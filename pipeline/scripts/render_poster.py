#!/usr/bin/env python3
"""Render deck.json -> full-slide designed PNGs -> deck_poster.pdf (and optional .pptx of full-slide images).
Each slide is a 1600x900 designed poster: brand header band, real typography, embedded visuals/photos.
Usage: python3 render_poster.py ../runs/vNN/deck.json"""
import html, json, re, subprocess, sys
from pathlib import Path
from PIL import Image

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TAG = re.compile(r"\s*\[(?:[SAROMG]\d+)(?:\]\[|,\s*|[SARO]\d+)*\]")
W, H = 1600, 900

def e(t): return html.escape(TAG.sub("", str(t)).strip())

def clean(b): return TAG.sub("", str(b)).strip()

def esc(b):
    """escape + bold lead-in before first colon/dash."""
    t = html.escape(clean(b))
    m = re.match(r"^(.*?[.:—–-])\s+(.*)$", clean(b), re.S)
    if m and len(m.group(1)) < 60:
        return f"<b>{html.escape(m.group(1))}</b> {html.escape(m.group(2))}"
    return t

def visual_path(run, s):
    v = s.get("visual") or {}
    f = v.get("file")
    if f:
        p = run / f
        if p.exists(): return p
    # fallback: generated sNN.png
    p = run / "visuals" / f"s{s['n']:02d}.png"
    if p.exists(): return p
    p = run / "visuals" / f"board_s{s['n']:02d}.png"
    if p.exists(): return p
    return None

def slide_html(deck, s, run, idx, total):
    meta = deck["meta"]; brand = meta.get("brand_color","#1f4e79")
    sec = s["section"]; n = s["n"]
    theme = meta.get("theme") or meta.get("campaign_name","")
    foot = f"{theme}  •  {meta.get('school','')}  •  {idx+1}/{total}"
    bullets = s.get("bullets", [])
    if sec == "bibliography" and not bullets:
        bullets = [f"{x['publisher']}. {x['title']} ({x.get('date','')})" for x in deck.get("sources",[])]
    img = visual_path(run, s)
    img_uri = img.resolve().as_uri() if img else ""
    vdesc = (s.get("visual") or {}).get("desc","")

    head = f"""<div class="topbar" style="background:{brand}"></div>
<div class="head"><div class="kicker">{html.escape(sec.upper())}</div>
<div class="title">{html.escape(s.get('title',''))}</div></div>"""

    if sec == "cover":
        return f"""<div class="slide cover" style="background:{brand}">
<div class="ctitle">{html.escape(meta.get('campaign_name',''))}</div>
<div class="csub">{html.escape(meta.get('product',''))} — Integrated Marketing Campaign</div>
<div class="cthesis">{html.escape(meta.get('thesis',''))}</div>
<div class="cmeta">{html.escape(meta.get('school',''))} • {html.escape(', '.join(meta.get('participants',[])))}</div>
{f'<img class="cphoto" src="{img_uri}">' if img_uri else ''}
<div class="footw">{html.escape(foot)}</div></div>"""

    if sec == "toc":
        rows = "".join(f'<div class="tocrow"><span class="tocn">{i+1}</span><span class="toct">{html.escape(clean(b))}</span></div>'
                       for i,b in enumerate(bullets))
        return f"""<div class="slide"><div class="pad">{head}
<div class="toctitle">{html.escape(s.get('title',''))}</div>{rows}
<div class="footw dark">{html.escape(foot)}</div></div></div>"""

    # standard slide
    bl = "".join(f"<li>{esc(b)}</li>" for b in bullets)
    right = ""
    if img_uri:
        right = f'<div class="vis"><img src="{img_uri}"></div>'
    elif vdesc and (s.get("visual") or {}).get("type") not in (None,"none"):
        right = f'<div class="vis ph" style="border-color:{brand}"><div class="phcap">{html.escape(vdesc)}</div></div>'
    if sec == "bibliography":
        return f"""<div class="slide"><div class="pad bib">{head}
<div class="biblist">{''.join(f'<div class="bib">{html.escape(clean(b))}</div>' for b in bullets)}</div>
<div class="footw dark">{html.escape(foot)}</div></div></div>"""
    return f"""<div class="slide"><div class="pad">{head}
<div class="cols"><div class="blist"><ul>{bl}</ul></div>{right}</div>
<div class="footw dark">{html.escape(foot)}</div></div></div>"""

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
.slide{width:1600px;height:900px;font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;background:#fbf8f4;color:#1d1d1f;position:relative;overflow:hidden}
.pad{padding:70px 80px;height:100%;display:flex;flex-direction:column}
.topbar{height:14px;width:100%}
.head{margin-top:26px}
.kicker{font-size:20px;letter-spacing:.35em;font-weight:800;color:#8a8378;text-transform:uppercase}
.title{font-size:52px;font-weight:900;letter-spacing:-.5px;margin-top:6px;line-height:1.05}
.cols{display:flex;gap:56px;margin-top:34px;flex:1;min-height:0}
.blist{flex:1.15;font-size:27px;line-height:1.42}
.blist ul{list-style:none}
.blist li{margin-bottom:26px;padding-left:34px;position:relative}
.blist li::before{content:"";position:absolute;left:0;top:.62em;width:14px;height:14px;border-radius:4px;background:var(--brand);transform:rotate(45deg)}
.blist b{color:var(--brand)}
.vis{flex:1;display:flex;align-items:center;justify-content:center}
.vis img{max-width:100%;max-height:640px;border-radius:24px;box-shadow:0 18px 50px rgba(0,0,0,.18);object-fit:contain}
.vis.ph{border:3px dashed #c9c0b4;border-radius:24px;align-items:center;justify-content:center}
.phcap{font-size:20px;color:#8a8378;text-align:center;padding:30px;line-height:1.5}
.footw{position:absolute;bottom:26px;right:44px;font-size:16px;color:rgba(255,255,255,.75)}
.footw.dark{color:#a89f92}
/* cover */
.cover{color:#fff;display:flex;flex-direction:column;justify-content:center;padding:0 110px}
.ctitle{font-size:110px;font-weight:900;letter-spacing:-2px;line-height:1}
.csub{font-size:34px;opacity:.92;margin-top:18px;font-weight:600}
.cthesis{font-size:30px;opacity:.85;margin-top:44px;max-width:900px;line-height:1.35;font-weight:400}
.cmeta{font-size:22px;opacity:.75;margin-top:60px}
.cphoto{position:absolute;right:80px;top:110px;width:520px;height:680px;object-fit:cover;border-radius:28px;box-shadow:0 24px 60px rgba(0,0,0,.35);transform:rotate(2deg)}
/* toc */
.toctitle{font-size:64px;font-weight:900;margin:20px 0 40px}
.tocrow{display:flex;align-items:center;gap:30px;padding:26px 0;border-bottom:2px solid #e7e0d6;font-size:34px}
.tocn{width:64px;height:64px;border-radius:50%;background:var(--brand);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:28px;flex:none}
/* bib */
.biblist{margin-top:30px;columns:2;column-gap:60px}
.bib{font-size:21px;line-height:1.45;color:#3a3a3a;margin-bottom:18px;break-inside:avoid}
"""

def main(deck_path):
    deck = json.load(open(deck_path)); run = Path(deck_path).parent
    meta = deck["meta"]; brand = meta.get("brand_color","#1f4e79")
    outdir = run / "posters"; outdir.mkdir(exist_ok=True)
    slides = deck["slides"]; total = len(slides)
    pngs = []
    for i, s in enumerate(slides):
        doc = f"<!doctype html><html><head><meta charset='utf-8'><style>:root{{--brand:{brand};}}{CSS}</style></head><body>{slide_html(deck,s,run,i,total)}</body></html>"
        hf = (outdir / f"p{i+1:02d}.html"); hf.write_text(doc)
        png = outdir / f"p{i+1:02d}.png"
        if png.exists() and png.stat().st_size > 10000:
            pngs.append(png); continue
        subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars",f"--screenshot={png}",
                        f"--window-size={W},{H}",hf.resolve().as_uri()],capture_output=True,timeout=120)
        pngs.append(png)
    # combine to PDF via PIL
    pdf_path = run / "deck_poster.pdf"
    imgs = [Image.open(p).convert("RGB") for p in pngs]
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:], resolution=144.0)
    print("Wrote", pdf_path, f"({len(pngs)} slides)")

if __name__ == "__main__":
    main(sys.argv[1])
