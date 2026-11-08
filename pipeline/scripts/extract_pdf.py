#!/usr/bin/env python3
"""Extract per-slide text (+ image counts) from the winning PDFs for calibration grading.

Usage: python3 extract_pdf.py
Writes runs/calibration/{1st,2nd,3rd}.txt
"""
import subprocess
from pathlib import Path

from common import RUNS

DESKTOP = Path.home() / "Desktop"
WINNERS = {
    "1st": DESKTOP / "6a6d217994519ae1182e9c0a_IMCP 1st 900170284.pdf",
    "2nd": DESKTOP / "6a6d217c492d1215468c14c6_IMCP 2nd 900187267.pdf",
    "3rd": DESKTOP / "6a6d217ff24f4f0466c7cad1_IMCP 3rd 900183931.pdf",
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def main():
    out_dir = RUNS / "calibration"
    (out_dir / "grades").mkdir(parents=True, exist_ok=True)
    for rank, pdf in WINNERS.items():
        if not pdf.exists():
            print(f"missing {pdf}")
            continue
        pages = int(next(l for l in run(["pdfinfo", str(pdf)]).splitlines() if l.startswith("Pages")).split()[1])
        imgs = {}
        for line in run(["pdfimages", "-list", str(pdf)]).splitlines()[2:]:
            p = line.split()
            if p and p[0].isdigit():
                imgs[int(p[0])] = imgs.get(int(p[0]), 0) + 1
        chunks = []
        for n in range(1, pages + 1):
            text = run(["pdftotext", "-f", str(n), "-l", str(n), "-layout", str(pdf), "-"]).strip()
            chunks.append(f"=== SLIDE {n} === (images on slide: {imgs.get(n, 0)})\n{text}\n")
        (out_dir / f"{rank}.txt").write_text("\n".join(chunks))
        print(f"wrote {out_dir / (rank + '.txt')} ({pages} slides)")


if __name__ == "__main__":
    main()
