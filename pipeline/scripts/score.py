#!/usr/bin/env python3
"""Aggregate grader passes for a run, apply auto-caps and DECA penalties, update leaderboard.

Usage: python3 score.py runs/v01 [--no-leaderboard]
Reads: runs/v01/deck.json, runs/v01/check.json, runs/v01/grades/*.json
Writes: runs/v01/score.json, pipeline/leaderboard.csv
"""
import csv
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path

from common import CATEGORY_KEYS, CATEGORY_MAX, PIPELINE, RUBRIC, load_json, save_json

EVIDENCE_RE = re.compile(r"slide\s*\d+", re.I)
QUOTE_RE = re.compile(r"[\"“”']")


def validate_grade(g):
    """Return list of problems; empty list = valid."""
    problems = []
    scores = g.get("scores", {})
    for k in CATEGORY_KEYS:
        s = scores.get(k)
        if not isinstance(s, dict):
            problems.append(f"missing category {k}")
            continue
        v = s.get("score")
        if not isinstance(v, int) or not 0 <= v <= CATEGORY_MAX[k]:
            problems.append(f"{k}: score {v!r} not an integer in 0..{CATEGORY_MAX[k]}")
        ev = s.get("evidence", "")
        if not (EVIDENCE_RE.search(ev) and QUOTE_RE.search(ev)):
            problems.append(f"{k}: evidence must cite 'Slide N' and quote text")
        if v is not None and isinstance(v, int) and v < CATEGORY_MAX[k] and not s.get("fix"):
            problems.append(f"{k}: below max but no 'fix' given")
    return problems


def aggregate(grades):
    """Median per category across valid passes, plus spread for noise detection."""
    out, spread = {}, {}
    for k in CATEGORY_KEYS:
        vals = [g["scores"][k]["score"] for g in grades]
        out[k] = int(round(statistics.median(vals)))
        spread[k] = max(vals) - min(vals)
    return out, spread


def caps_from_facts(facts):
    rules = RUBRIC["auto_caps"]
    caps = {}

    def cap(rule_key):
        r = rules[rule_key]
        caps[r["category"]] = min(caps.get(r["category"], 99), r["cap"])

    if not facts.get("primary_research_ok"):
        cap("research_primary_lite" if facts.get("primary_lite_ok") else "research_no_primary")
    if facts.get("findings_cited_on_strategy", 0) < 3:
        cap("research_unlinked")
    if facts.get("budget_lines", 0) < 5 or not facts.get("has_projection"):
        cap("budget_thin")
    if facts.get("kpis_missing_target", 1) > 0:
        cap("impact_no_targets")
    if facts.get("kpis_with_baseline", 0) == 0:
        cap("impact_no_baselines")
    if facts.get("body_slides_with_visual", 0) < 8:
        cap("design_no_visuals")
    if facts.get("body_slides_with_notes", 0) == 0:
        cap("delivery_no_talk_track")
    return caps


def score_run(run_dir, leaderboard=True):
    run_dir = Path(run_dir)
    check = load_json(run_dir / "check.json")
    if any(not e["code"].startswith("P_") for e in check["errors"]):
        sys.exit("check.json has blocking errors. Fix them and re-run check_deck.py before scoring.")
    valid, rejected = [], []
    for f in sorted((run_dir / "grades").glob("*.json")):
        g = load_json(f)
        probs = validate_grade(g)
        (rejected if probs else valid).append((f.name, probs, g))
    if not valid:
        for name, probs, _ in rejected:
            print(f"REJECTED {name}: {probs[:5]}")
        sys.exit("No valid grade files. Re-grade following prompts/03_grade.md.")
    raw, spread = aggregate([g for _, _, g in valid])
    caps = caps_from_facts(check["facts"])
    capped = {k: min(v, caps.get(k, v)) for k, v in raw.items()}
    noisy = [k for k in CATEGORY_KEYS if spread[k] >= (4 if CATEGORY_MAX[k] >= 10 else 2)]
    result = {
        "run": run_dir.name,
        "passes_valid": len(valid),
        "passes_rejected": [{"file": n, "problems": p} for n, p, _ in rejected],
        "raw": raw,
        "caps_applied": {k: c for k, c in caps.items() if raw[k] > c},
        "capped": capped,
        "spread": spread,
        "noisy_categories": noisy,
        "raw_total": sum(raw.values()),
        "capped_total": sum(capped.values()),
        "penalty_points": check["penalty_points"],
        "final": sum(capped.values()) - check["penalty_points"],
        "top_fixes": [fx for _, _, g in valid for fx in g.get("top_fixes", [])][:6],
        "scored_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_json(run_dir / "score.json", result)
    if leaderboard:
        update_leaderboard(run_dir, result)
    return result


def update_leaderboard(run_dir, r):
    path = PIPELINE / "leaderboard.csv"
    deck = load_json(run_dir / "deck.json")
    rows = []
    if path.exists():
        rows = [row for row in csv.DictReader(path.open()) if row["run"] != r["run"]]
    rows.append({
        "run": r["run"], "angle": deck.get("meta", {}).get("variant_angle", ""),
        "campaign": deck.get("meta", {}).get("campaign_name", ""),
        "passes": r["passes_valid"], "raw_total": r["raw_total"], "capped_total": r["capped_total"],
        "penalties": r["penalty_points"], "final": r["final"],
        "noisy": ";".join(r["noisy_categories"]), "scored_at": r["scored_at"],
    })
    rows.sort(key=lambda x: -float(x["final"]))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    r = score_run(sys.argv[1], leaderboard="--no-leaderboard" not in sys.argv)
    print(f"{r['run']}: final {r['final']}/100 (raw {r['raw_total']}, capped {r['capped_total']}, "
          f"penalties -{r['penalty_points']}, {r['passes_valid']} valid passes)")
    for k in CATEGORY_KEYS:
        flag = " CAPPED" if k in r["caps_applied"] else ""
        flag += " NOISY" if k in r["noisy_categories"] else ""
        print(f"  {k:22} {r['capped'][k]:>2}/{CATEGORY_MAX[k]}{flag}")
    if r["passes_rejected"]:
        print(f"Rejected passes: {[p['file'] for p in r['passes_rejected']]}")
    if r["noisy_categories"]:
        print("Noisy grading: run one more independent grading pass before trusting this score.")
    if "--no-leaderboard" not in sys.argv:
        print(f"Leaderboard: {PIPELINE / 'leaderboard.csv'}")


if __name__ == "__main__":
    main()
