#!/usr/bin/env python3
"""Check that the grader ranks the known winning decks sensibly before trusting it.

Usage: python3 calibrate.py
Reads runs/calibration/grades/{1st,2nd,3rd}.pass*.json (same schema as deck grades).

Gates (from what we know about the 2026 ICDC decks):
  C1 (hard): 1st-place total > 3rd-place total.
  C2 (hard): no winning deck gets research > 10/15 (none had a research method section).
  C3 (soft): 1st >= 2nd >= 3rd.
"""
import sys

from common import CATEGORY_KEYS, RUNS, load_json
from score import aggregate, validate_grade


def main():
    gdir = RUNS / "calibration" / "grades"
    totals, research = {}, {}
    for rank in ("1st", "2nd", "3rd"):
        grades = []
        for f in sorted(gdir.glob(f"{rank}.pass*.json")):
            g = load_json(f)
            probs = validate_grade(g)
            if probs:
                print(f"REJECTED {f.name}: {probs[:3]}")
            else:
                grades.append(g)
        if not grades:
            sys.exit(f"No valid grades for {rank}. Grade runs/calibration/{rank}.txt with prompts/03_grade.md.")
        agg, _ = aggregate(grades)
        totals[rank], research[rank] = sum(agg.values()), agg["research"]
        print(f"{rank}: total {totals[rank]}/100, research {research[rank]}/15  " +
              " ".join(f"{k[:6]}={agg[k]}" for k in CATEGORY_KEYS))
    c1 = totals["1st"] > totals["3rd"]
    c2 = all(v <= 10 for v in research.values())
    c3 = totals["1st"] >= totals["2nd"] >= totals["3rd"]
    print(f"\nC1 1st > 3rd: {'PASS' if c1 else 'FAIL'}")
    print(f"C2 research <= 10 for all winners: {'PASS' if c2 else 'FAIL'}")
    print(f"C3 1st >= 2nd >= 3rd (soft): {'PASS' if c3 else 'WARN'}")
    if not (c1 and c2):
        print("\nCALIBRATION FAILED. Re-read rubric.json harsh_guidance, then regrade the failing decks.")
        sys.exit(1)
    print("\nCALIBRATION PASSED. The grader may now score campaign variants.")


if __name__ == "__main__":
    main()
