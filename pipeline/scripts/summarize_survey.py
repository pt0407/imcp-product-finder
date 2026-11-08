#!/usr/bin/env python3
"""Tabulate a Google Forms CSV export so deck findings use computed numbers only.

Usage: python3 summarize_survey.py pipeline/research/survey_results.csv
Writes survey_summary.md and survey_summary.json next to the CSV.
Columns with <= 15 distinct answers are tabulated as % of respondents.
Checkbox questions (answers separated by ';' or ', ') are split per option.
Free-text columns are listed verbatim for quote selection.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path


def split_multi(v):
    for sep in (";", ", "):
        if sep in v:
            return [x.strip() for x in v.split(sep) if x.strip()]
    return [v.strip()] if v.strip() else []


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    n = len(rows)
    summary = {"n": n, "questions": {}}
    md = [f"# Survey summary\n\n**n = {n}** respondents · source file `{path.name}`\n"]
    for col in rows[0].keys() if rows else []:
        if col.lower() in ("timestamp", "email address"):
            continue
        answers = [r[col] for r in rows if r.get(col, "").strip()]
        split = [x for a in answers for x in split_multi(a)]
        distinct = set(split)
        md.append(f"## {col}\n*answered by {len(answers)} of {n}*\n")
        if 0 < len(distinct) <= 15:
            counts = Counter(split)
            table = {k: {"count": c, "pct_of_respondents": round(100 * c / n, 1)} for k, c in counts.most_common()}
            summary["questions"][col] = {"type": "choice", "answered": len(answers), "options": table}
            md += [f"- {k}: {v['count']} ({v['pct_of_respondents']}%)" for k, v in table.items()]
        else:
            summary["questions"][col] = {"type": "text", "answered": len(answers), "responses": answers}
            md += [f"> {a}" for a in answers[:40]]
        md.append("")
    (path.parent / "survey_summary.md").write_text("\n".join(md))
    (path.parent / "survey_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"n={n}. Wrote {path.parent / 'survey_summary.md'}")


if __name__ == "__main__":
    main()
