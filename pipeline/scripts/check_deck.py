#!/usr/bin/env python3
"""Validate a deck.json against DECA 2026-27 rules + pipeline quality rules.

Usage: python3 check_deck.py runs/v01/deck.json [--final]
Writes check.json next to the deck. Exit code 1 if any error.

Error codes starting with P_ are DECA penalty-checklist items (cost points).
Other E_ errors block grading. W_ warnings lower quality but don't block.
"""
import math
import sys
from pathlib import Path

from common import (PLACEHOLDER_RE, NUMBER_RE, REQUIRED_SECTIONS, SECTION_ORDER, TAG_RE,
                    campaign_days, finance, load_json, save_json, slide_text, tags_in, word_count)

NO_SOURCE_CHECK = {"cover", "title", "toc", "bibliography"}


def check(deck, final=False):
    errors, warnings = [], []
    err = lambda code, msg, pts=0: errors.append({"code": code, "msg": msg, "penalty_points": pts})
    warn = lambda code, msg: warnings.append({"code": code, "msg": msg})

    slides = deck.get("slides", [])
    ids = {k: {x["id"] for x in deck.get(coll, [])} for k, coll in
           [("S", "sources"), ("A", "assumptions"), ("O", "objectives")]}
    ids["R"] = {f["id"] for f in deck.get("research", {}).get("findings", [])}
    meta = deck.get("meta", {})

    # ---- DECA penalty items -------------------------------------------------
    if len(slides) > 20:
        err("P_SLIDES", f"{len(slides)} slides; limit is 20 incl. appendix", 5 * (len(slides) - 20))
    nums = [s.get("n") for s in slides]
    if nums != list(range(1, len(slides) + 1)):
        err("P_NUMBER", f"slide numbers not sequential from 1: {nums}", 5)
    sec = [s.get("section") for s in slides]
    if len(sec) < 3 or sec[1] != "title" or sec[2] != "toc":
        err("P_NUMBER", "title must be slide 2 and table of contents slide 3", 5)
    elif len(sec) > 3 and sec[3] != "overview":
        err("P_OUTLINE", "body must start with I. Overview on slide 4", 5)
    order = [SECTION_ORDER.index(s) if s in SECTION_ORDER else -1 for s in sec]
    if -1 in order:
        err("P_OUTLINE", f"unknown section names: {[s for s in sec if s not in SECTION_ORDER]}", 5)
    elif order != sorted(order):
        err("P_OUTLINE", f"sections out of official order: {sec}", 5)
    missing = [s for s in REQUIRED_SECTIONS if s not in sec]
    if missing:
        err("P_OUTLINE", f"missing required sections: {missing}", 5)
    if final and not meta.get("assurances_signed"):
        err("P_ASSURANCES", "Statement of Assurances not marked signed (meta.assurances_signed)", 15)

    # ---- Blocking errors -----------------------------------------------------
    win = deck.get("campaign_window")
    days = None
    if not win:
        err("E_WINDOW", "campaign_window missing")
    else:
        days = campaign_days(win)
        if days > 45:
            err("E_WINDOW", f"campaign is {days} days; max 45")
    title = slide_text(slides[1]) if len(slides) > 1 else ""
    if "integrated marketing campaign" not in title.lower():
        err("E_TITLE", "title slide must name the event: INTEGRATED MARKETING CAMPAIGN–PRODUCT")
    for key in ("school", "school_address", "participants", "date"):
        if not meta.get(key):
            (err if final else warn)("E_TITLE" if final else "W_TITLE", f"meta.{key} missing (needed on title slide)")

    if len(deck.get("sources", [])) < 5:
        err("E_SOURCES_MIN", f"{len(deck.get('sources', []))} sources; need >= 5")
    for s in deck.get("sources", []):
        if not (s.get("publisher") and s.get("date") and (s.get("url") or s.get("type") == "primary")):
            err("E_SOURCE_FIELDS", f"source {s.get('id')} needs publisher, date, and url (or type=primary)")

    for s in slides:
        if s.get("section") in NO_SOURCE_CHECK:
            continue
        for b in [s.get("title", "")] + s.get("bullets", []):
            stripped = TAG_RE.sub("", b)
            if NUMBER_RE.search(stripped) and not TAG_RE.search(b):
                err("E_UNSOURCED", f"slide {s['n']}: number without [S#]/[A#]/[R#]/[O#] tag: \"{b[:90]}\"")
            for t in tags_in(b):
                if t not in ids[t[0]]:
                    err("E_BAD_TAG", f"slide {s['n']}: tag {t} does not exist")

    b = deck.get("budget", {})
    lines = b.get("lines", [])
    if lines and abs(sum(l.get("usd", 0) for l in lines) - b.get("total_usd", 0)) > 1:
        err("E_BUDGET_SUM", f"budget lines sum to {sum(l['usd'] for l in lines)} but total_usd is {b.get('total_usd')}")
    for l in lines:
        basis = l.get("basis", "")
        if not basis or (basis[0] in "SA" and basis not in ids[basis[0]]) or basis[0] not in "SA":
            err("E_BUDGET_BASIS", f"budget line '{l.get('item')}' needs basis = existing S# (source) or A# (assumption)")

    obj_ids = ids["O"]
    kpi_objs = {k.get("objective") for k in deck.get("kpis", [])}
    for o in obj_ids - kpi_objs:
        err("E_KPI_OBJ", f"objective {o} has no KPI")
    for o in kpi_objs - obj_ids:
        err("E_KPI_OBJ", f"KPI references unknown objective {o}")

    seg_ids = {s["id"] for s in deck.get("segments", [])}
    max_week = math.ceil(days / 7) if days else 7
    for g in deck.get("programs", []):
        for f in ("name", "mechanic", "segment", "channels", "objectives", "weeks"):
            if not g.get(f):
                err("E_PROGRAM", f"program {g.get('id')} missing {f}")
        if g.get("segment") and g["segment"] not in seg_ids:
            err("E_PROGRAM", f"program {g.get('id')} segment {g['segment']} not defined")
        if any(o not in obj_ids for o in g.get("objectives", [])):
            err("E_PROGRAM", f"program {g.get('id')} references unknown objective")
        if any(w > max_week for w in g.get("weeks", [])):
            err("E_PROGRAM", f"program {g.get('id')} runs past week {max_week} of the campaign")

    methods = deck.get("research", {}).get("methods", [])
    if final:
        for s in slides:
            if PLACEHOLDER_RE.search(slide_text(s) + " " + s.get("notes", "")):
                err("E_PLACEHOLDER", f"slide {s['n']} contains a placeholder (VERIFY/TBD/TODO/{{{{)")
        for m in methods:
            if m.get("status") != "complete":
                err("E_RESEARCH_PENDING", f"research method {m.get('id')} is not complete; real data required")

    # ---- Warnings --------------------------------------------------------------
    theme = (meta.get("theme") or "").lower()
    for s in slides:
        body = 4 <= s["n"] <= 19 and s.get("section") not in ("bibliography", "appendix")
        wc = word_count(slide_text(s))
        if body and wc > 110:
            warn("W_WORDS", f"slide {s['n']}: {wc} words (winners averaged 62-92)")
        if body and wc < 25:
            warn("W_WORDS", f"slide {s['n']}: only {wc} words")
        if body and (s.get("visual") or {}).get("type", "none") == "none":
            warn("W_VISUAL", f"slide {s['n']}: no visual")
        if body and not s.get("notes"):
            warn("W_NOTES", f"slide {s['n']}: no talk-track notes")
        if s.get("section") == "strategy" and theme and theme not in slide_text(s).lower():
            warn("W_THEME", f"slide {s['n']}: theme '{meta.get('theme')}' not on strategy slide")
    referenced = set()
    for s in slides:
        if s.get("section") in ("strategy", "budget", "impact"):
            referenced |= set(tags_in(slide_text(s)))
    for o in obj_ids - referenced:
        warn("W_OBJ_REF", f"objective {o} never referenced on strategy/budget/impact slides")
    fin = finance(deck)
    if fin is None:
        warn("W_FINANCE", "budget.projection incomplete; cannot compute ROI/ROAS/CAC")
    elif fin["conservative_case"]["roi_profit_based"] < 0:
        warn("W_FINANCE", "conservative case loses money; address the risk on the budget slide")

    # ---- Facts used by score.py caps ------------------------------------------------
    complete = [m for m in methods if m.get("status") == "complete"]
    survey_ok = any(m.get("type") == "survey" and (m.get("n") or 0) >= 30 for m in complete)
    interviews_ok = sum(1 for m in complete if m.get("type") == "interview") >= 3 or \
        any(m.get("type") == "interview" and (m.get("n") or 0) >= 3 for m in complete)
    strategy_r = {t for s in slides if s.get("section") == "strategy"
                  for t in tags_in(slide_text(s)) if t.startswith("R")}
    kpis = deck.get("kpis", [])
    body = [s for s in slides if 4 <= s["n"] <= 19]
    facts = {
        "primary_research_ok": survey_ok or interviews_ok,
        "findings_cited_on_strategy": len(strategy_r),
        "budget_lines": len(lines),
        "has_projection": fin is not None,
        "kpis_missing_target": sum(1 for k in kpis if not k.get("target")),
        "kpis_with_baseline": sum(1 for k in kpis if k.get("baseline")),
        "body_slides_with_visual": sum(1 for s in body if (s.get("visual") or {}).get("type", "none") != "none"),
        "body_slides_with_notes": sum(1 for s in body if s.get("notes")),
        "campaign_days": days,
    }
    return {"final_mode": final, "errors": errors, "warnings": warnings, "facts": facts, "finance": fin,
            "penalty_points": sum(e["penalty_points"] for e in errors)}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    result = check(load_json(path), final="--final" in sys.argv)
    save_json(path.parent / "check.json", result)
    for e in result["errors"]:
        print(f"ERROR {e['code']}: {e['msg']}" + (f"  (-{e['penalty_points']} pts)" if e["penalty_points"] else ""))
    for w in result["warnings"]:
        print(f"warn  {w['code']}: {w['msg']}")
    print(f"\n{len(result['errors'])} errors, {len(result['warnings'])} warnings, "
          f"{result['penalty_points']} DECA penalty points. Facts: {result['facts']}")
    if result["finance"]:
        print(f"Finance: {result['finance']}")
    sys.exit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
