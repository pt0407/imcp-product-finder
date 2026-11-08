#!/usr/bin/env python3
"""Create a new variant run folder from the template.

Usage:
  python3 new_run.py "<variant angle>"               # fresh variant from template
  python3 new_run.py "<variant angle>" --from v03     # revision: copy deck from an existing run
Creates runs/vNN/{deck.json, grades/}. Copies team info from pipeline/team.json and
shared facts (product, company, sources, research) from pipeline/brief.json if present.
"""
import shutil
import sys

from common import PIPELINE, RUNS, load_json, save_json


def next_id():
    existing = [int(p.name[1:]) for p in RUNS.glob("v[0-9]*") if p.name[1:].isdigit()]
    return f"v{(max(existing) + 1 if existing else 1):02d}"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    angle = sys.argv[1]
    run = RUNS / next_id()
    (run / "grades").mkdir(parents=True)
    if "--from" in sys.argv:
        src = RUNS / sys.argv[sys.argv.index("--from") + 1] / "deck.json"
        deck = load_json(src)
        deck["meta"]["parent_run"] = src.parent.name
    else:
        deck = load_json(PIPELINE / "templates" / "deck.template.json")
        brief_path = PIPELINE / "brief.json"
        if brief_path.exists():
            brief = load_json(brief_path)
            deck["meta"].update({k: brief[k] for k in ("product", "company", "brand_color") if brief.get(k)})
            for k in ("sources", "assumptions"):
                deck[k] = brief.get(k, [])
            if brief.get("research"):
                deck["research"] = brief["research"]
    team_path = PIPELINE / "team.json"
    if team_path.exists():
        deck["meta"].update(load_json(team_path))
    deck["meta"]["variant_angle"] = angle
    save_json(run / "deck.json", deck)
    print(f"Created {run} (angle: {angle})")


if __name__ == "__main__":
    main()
