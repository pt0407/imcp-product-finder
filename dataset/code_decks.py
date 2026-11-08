#!/usr/bin/env python3
"""Code measurable features from IMCP pitch-deck PDFs (pdftotext + pdfimages).

Judgment-based features (named programs, personas, theme) are coded by hand in
deck_codebook.csv with an evidence note per row, not computed here.
"""
import csv, re, subprocess, sys
from pathlib import Path

ROOT = Path("/Users/pranav/Desktop")
DECKS = [
    ("1st", "StixFresh - Save What Matters", ROOT / "6a6d217994519ae1182e9c0a_IMCP 1st 900170284.pdf",
     ["Save What Matters", "SaveWhatMatters", "SAVE"]),
    ("2nd", "MarkSetBot - Race for our Oceans", ROOT / "6a6d217c492d1215468c14c6_IMCP 2nd 900187267.pdf",
     ["Racing Toward", "Greener Future", "Race for our Oceans", "Trial Fleet", "something green"]),
    ("3rd", "Misfits Health - #BeAMisfit", ROOT / "6a6d217ff24f4f0466c7cad1_IMCP 3rd 900183931.pdf",
     ["Misfits", "BeAMisfit", "#BEAMISFIT", "Fuel the Future", "Fuel Club"]),
]
OUT = Path(__file__).parent / "imcp_pitch_decks_measured.csv"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def page_text(pdf, page):
    return run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"])


def image_pages(pdf):
    counts = {}
    for line in run(["pdfimages", "-list", str(pdf)]).splitlines()[2:]:
        parts = line.split()
        if parts and parts[0].isdigit():
            counts[int(parts[0])] = counts.get(int(parts[0]), 0) + 1
    return counts


def main():
    rows = []
    for rank, name, pdf, themes in DECKS:
        pages = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(pdf)])).group(1))
        imgs = image_pages(pdf)
        full = run(["pdftotext", "-layout", str(pdf), "-"])
        words = [len(page_text(pdf, p).split()) for p in range(1, pages + 1)]
        theme_hits = {t: len(re.findall(re.escape(t), full, re.I)) for t in themes}
        dollars = re.findall(r"\$\s?[\d,]+(?:\.\d+)?", full)
        pct = re.findall(r"\d+(?:\.\d+)?\s?%", full)
        bib = full.split("BIBLIOGRAPHY")[-1] if "BIBLIOGRAPHY" in full else ""
        rows.append({
            "placement": rank,
            "deck": name,
            "slides": pages,
            "total_words": sum(words),
            "words_per_slide_avg": round(sum(words) / pages, 1),
            "slides_with_images": len([p for p in imgs if p <= pages]),
            "images_total": sum(imgs.values()),
            "dollar_figures": len(dollars),
            "percent_figures": len(pct),
            "theme_mentions": max(theme_hits.values()) if theme_hits else 0,
            "has_total_budget": int(bool(re.search(r"total", full, re.I))),
            "has_cac_or_roi": int(bool(re.search(r"\bCAC\b|\bROI\b", full))),
            "week_or_day_refs": len(re.findall(r"\b(Week|Weeks|Day|Days)\b", full)),
            "bibliography_lines": len([l for l in bib.splitlines() if l.strip()]),
        })
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    print(f"\nWrote {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
