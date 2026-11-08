#!/usr/bin/env python3
"""Render deck.json to a 16:9 HTML deck, a PDF (headless Chrome), and Markdown.

Usage: python3 render.py runs/v01/deck.json
Outputs: deck.html, deck.pdf, deck.md next to deck.json.
Visuals: if slide.visual.file exists (path relative to the run dir), it is embedded;
otherwise a labeled mockup placeholder is drawn so the gap is obvious.
"""
import html
import subprocess
import sys
from pathlib import Path

from common import SECTION_LABELS, load_json

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, Helvetica, Arial, sans-serif; color: #1d1d1f; }
.slide { width: 13.333in; height: 7.5in; padding: 0.55in 0.7in; position: relative;
         page-break-after: always; overflow: hidden; background: #fff; }
.slide.cover { background: var(--brand); color: #fff; display: flex; flex-direction: column; justify-content: center; }
.cover h1 { font-size: 64px; margin: 0 0 12px; }
.cover p { font-size: 26px; margin: 4px 0; opacity: .95; }
.kicker { font-size: 13px; letter-spacing: .12em; text-transform: uppercase; color: var(--brand); font-weight: 700; }
h2 { font-size: 38px; margin: 6px 0 18px; }
.cols { display: flex; gap: 0.45in; height: 5.2in; }
.text { flex: 1.15; font-size: 19px; line-height: 1.4; }
.text ul { margin: 0; padding-left: 22px; } .text li { margin-bottom: 9px; }
.visual { flex: 1; display: flex; align-items: center; justify-content: center; }
.visual img { max-width: 100%; max-height: 5in; border-radius: 10px; }
.placeholder { width: 100%; height: 4.6in; border: 3px dashed #c7c7cc; border-radius: 14px; display: flex;
               align-items: center; justify-content: center; text-align: center; padding: 24px;
               color: #8e8e93; font-size: 17px; }
.num { position: absolute; right: 0.5in; bottom: 0.35in; font-weight: 700; font-size: 18px; color: var(--brand); }
.theme { position: absolute; left: 0.7in; bottom: 0.35in; font-size: 13px; color: #8e8e93; }
.tag { color: #8e8e93; font-size: 0.75em; }
.ai { font-size: 11px; color: #8e8e93; margin-top: 6px; }
"""


def esc_with_tags(text):
    import re
    return re.sub(r"(\[[SARO]\d+(?:\s*,\s*[SARO]\d+)*\])", r'<span class="tag">\1</span>', html.escape(text))


def bibliography_bullets(deck):
    out = []
    for s in deck.get("sources", []):
        parts = [s.get("publisher", ""), f"\"{s.get('title', '')}\"" if s.get("title") else "", s.get("date", ""), s.get("url", "")]
        out.append(f"[{s['id']}] " + ". ".join(p for p in parts if p))
    return out


def render_html(deck, run_dir):
    meta = deck.get("meta", {})
    brand = meta.get("brand_color", "#0a66c2")
    parts = [f"<html><head><meta charset='utf-8'><style>:root{{--brand:{brand};}}{CSS}</style></head><body>"]
    for s in deck["slides"]:
        bullets = s.get("bullets", [])
        if s["section"] == "bibliography" and not bullets:
            bullets = bibliography_bullets(deck)
        if s["section"] == "cover":
            parts.append(f"<section class='slide cover'><h1>{html.escape(s.get('title', ''))}</h1>"
                         + "".join(f"<p>{html.escape(b)}</p>" for b in bullets) + "</section>")
            continue
        v = s.get("visual") or {}
        vis = ""
        if v.get("type", "none") != "none":
            f = v.get("file")
            if f and (run_dir / f).exists():
                vis = f"<img src='{(run_dir / f).resolve().as_uri()}'>"
            else:
                vis = f"<div class='placeholder'>MOCKUP NEEDED ({html.escape(v.get('type', ''))}):<br>{html.escape(v.get('desc', ''))}</div>"
            if v.get("ai_generated"):
                vis += "<div class='ai'>Image is AI-generated + human-edited for illustration.</div>"
        label = SECTION_LABELS.get(s["section"], "")
        size = " style='font-size:14px'" if s["section"] == "bibliography" else ""
        parts.append(
            f"<section class='slide'><div class='kicker'>{html.escape(label)}</div>"
            f"<h2>{html.escape(s.get('title', ''))}</h2><div class='cols'>"
            f"<div class='text'{size}><ul>" + "".join(f"<li>{esc_with_tags(b)}</li>" for b in bullets) + "</ul></div>"
            + (f"<div class='visual'>{vis}</div>" if vis else "") + "</div>"
            + (f"<div class='theme'>{html.escape(meta.get('theme', ''))}</div>" if s["n"] > 3 else "")
            + f"<div class='num'>{s['n']}</div></section>")
    parts.append("</body></html>")
    return "".join(parts)


def render_md(deck):
    lines = [f"# {deck.get('meta', {}).get('campaign_name', 'Deck')}\n"]
    for s in deck["slides"]:
        bullets = s.get("bullets") or (bibliography_bullets(deck) if s["section"] == "bibliography" else [])
        lines.append(f"## Slide {s['n']} — {SECTION_LABELS.get(s['section'], s['section'])}: {s.get('title', '')}")
        lines += [f"- {b}" for b in bullets]
        v = s.get("visual") or {}
        if v.get("type", "none") != "none":
            lines.append(f"\n*Visual ({v.get('type')}):* {v.get('desc', '')}")
        if s.get("notes"):
            lines.append(f"\n> Talk track: {s['notes']}")
        lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1]).resolve()
    run_dir = path.parent
    deck = load_json(path)
    (run_dir / "deck.html").write_text(render_html(deck, run_dir))
    (run_dir / "deck.md").write_text(render_md(deck))
    pdf = run_dir / "deck.pdf"
    if Path(CHROME).exists():
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", (run_dir / "deck.html").as_uri()],
                       capture_output=True, timeout=120)
    print(f"Wrote {run_dir / 'deck.html'}, {run_dir / 'deck.md'}" + (f", {pdf}" if pdf.exists() else " (PDF skipped: Chrome not found)"))


if __name__ == "__main__":
    main()
