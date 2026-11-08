#!/usr/bin/env python3
"""Generate dense creative-board visuals (grid of mockups) for program/creative slides.
Usage: python3 gen_boards.py ../runs/vNN/deck.json
Writes visuals/board_sNN.png for strategy slides 12+ and points visual.file at them (keeps real photo on cover/product slides)."""
import html, json, re, subprocess, sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TAG = re.compile(r"\s*\[(?:[SARO]\d+)(?:\]\[|,\s*|[SARO]\d+)*\]")
def e(t): return html.escape(TAG.sub("", str(t)))

CSS = """*{box-sizing:border-box;margin:0;padding:0}
body{width:1560px;height:880px;font-family:-apple-system,Helvetica,Arial,sans-serif;background:#0f1420;color:#fff;padding:34px;overflow:hidden}
.h{font-size:34px;font-weight:800;margin-bottom:4px} .sub{font-size:17px;color:#9fb3c8;margin-bottom:22px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.tile{background:#1a2332;border-radius:18px;padding:14px;display:flex;flex-direction:column;gap:8px}
.cap{font-size:12px;letter-spacing:2px;color:__BRAND__;font-weight:800}
.tt{background:#111;border-radius:14px;height:170px;position:relative;display:flex;align-items:center;justify-content:center}
.ttv{font-size:52px;color:#fff} .ttc{position:absolute;top:8px;left:10px;font-size:13px;font-weight:700}
.ttx{position:absolute;bottom:10px;left:10px;right:10px;font-size:14px;line-height:1.3} .ttx span{color:#bbb;font-size:12px}
.em{background:#fff;color:#222;border-radius:12px;padding:14px} .emh{font-weight:800;font-size:16px;margin-bottom:6px} .emb{font-size:13px;color:#555;line-height:1.4;margin-bottom:8px} .embtn{background:__BRAND__;color:#fff;text-align:center;border-radius:8px;padding:7px;font-size:13px;font-weight:700}
.ph{background:#f4f6fb;border-radius:16px;padding:12px;display:flex;flex-direction:column;gap:8px} .bub{background:#fff;border:1px solid #ddd;border-radius:14px;padding:9px 12px;font-size:13px;max-width:80%} .bub.me{background:__BRAND__;color:#fff;border:none;align-self:flex-end}
.st{background:linear-gradient(160deg,#2b1055,#7597de);border-radius:14px;height:170px;padding:16px;display:flex;flex-direction:column;justify-content:space-between} .stt{font-size:20px;font-weight:800} .stb{font-size:13px;color:#dfe6ff} .stswipe{font-size:12px;color:#fff;background:rgba(255,255,255,.2);align-self:flex-start;padding:4px 10px;border-radius:999px}
.sh{background:#fff;color:#222;border-radius:12px;padding:12px} .sht{font-size:15px;font-weight:800;color:__BRAND__} .shb{font-size:12px;color:#555;margin:4px 0} .shp{background:#eee;border-radius:8px;height:44px;display:flex;align-items:center;justify-content:center;font-size:11px;color:#999;letter-spacing:1px}
.ev{background:linear-gradient(160deg,#0f3d2e,#1f6f8b);border-radius:14px;padding:14px;display:flex;flex-direction:column;justify-content:space-between;min-height:170px} .evh{font-size:18px;font-weight:800} .evb{font-size:12px;color:#cfe8f0} .evd{font-size:12px;color:#fff}"""

def board_html(brand, theme, title, tiles, photo_uri=""):
    """tiles: list of (kind, headline, body) -> 3x2 grid of mockups."""
    cells = ""
    kinds = ["tiktok","email","sms","story","shelf","event"]
    pbg = f"background:url({photo_uri}) center/cover;box-shadow:inset 0 -110px 60px -20px rgba(0,0,0,.88);" if photo_uri else ""
    pimg = f"<img src='{photo_uri}' style='width:100%;height:100%;object-fit:contain'>" if photo_uri else "PRODUCT"
    for i,(kind,h,b) in enumerate(tiles):
        k = kinds[i % len(kinds)]
        if k=="tiktok":
            inner=f"<div class='tt' style='{pbg}'><div class='ttv'>▶</div><div class='ttc'>@brand</div><div class='ttx'>{e(h)}<br><span>{e(b)}</span></div></div>"
        elif k=="email":
            inner=f"<div class='em'><div class='emh'>{e(h)}</div><div class='emb'>{e(b)}</div><div class='embtn'>Shop now →</div></div>"
        elif k=="sms":
            inner=f"<div class='ph'><div class='bub'>{e(h)}</div><div class='bub me'>{e(b)}</div></div>"
        elif k=="story":
            inner=f"<div class='st' style='{pbg}'><div class='stt'>{e(h)}</div><div class='stb'>{e(b)}</div><div class='stswipe'>Swipe up</div></div>"
        elif k=="shelf":
            inner=f"<div class='sh'><div class='sht'>{e(h)}</div><div class='shb'>{e(b)}</div><div class='shp' style='padding:6px'>{pimg}</div></div>"
        else:
            inner=f"<div class='ev'><div class='evh'>{e(h)}</div><div class='evb'>{e(b)}</div><div class='evd'>📍 Event</div></div>"
        cells += f"<div class='tile'>{inner}<div class='cap'>{k.upper()}</div></div>"
    doc = ("<!doctype html><html><head><meta charset='utf-8'><style>" + CSS.replace("__BRAND__", brand) +
           "</style></head><body><div class='h'>" + e(title) + "</div><div class='sub'>" + e(theme) +
           " — creative board (channel mockups)</div><div class='grid'>" + cells + "</div></body></html>")
    return doc

def main(deck_path):
    deck = json.load(open(deck_path)); run = Path(deck_path).parent
    cj = run / "creative.json"
    if cj.exists(): deck["_creative"] = json.loads(cj.read_text())
    out = run / "visuals"; out.mkdir(exist_ok=True)
    meta = deck["meta"]; brand = meta.get("brand_color","#1f6f8b"); theme = meta.get("theme") or meta.get("campaign_name","")
    progs = {p["id"]:p for p in deck.get("programs",[])}
    # program -> 6 channel tiles derived from mechanic
    def tiles_for(prog):
        mech = prog["mechanic"]
        short = mech.split(".")[0][:90]
        return [
          ("tiktok","POV: "+prog["name"][:30], short[:70]),
          ("email","You're invited: "+prog["name"][:28], short[:60]),
          ("sms",prog["name"][:24]+" — act now", "Reply YES to join. T&Cs apply."),
          ("story","New: "+prog["name"][:26], short[:60]),
          ("shelf","In-store: "+prog["name"][:24], short[:60]),
          ("event","Live: "+prog["name"][:26], short[:60]),
        ]
    changed=[]
    for s in deck["slides"]:
        n=s["n"]
        if s["section"]!="strategy" or n<12 or n>16: continue
        # find program ids referenced in bullets or map by order
        ids=[g for g in progs if g in " ".join(s["bullets"])]
        prog = progs.get(ids[0]) if ids else (list(progs.values())[min(n-12,len(progs)-1)] if progs else None)
        if not prog: continue
        # bespoke copy wins: creative.json boards {pid: [[kind,headline,body],...]}
        copy = ((deck.get("_creative") or {}).get("boards") or {}).get(prog["id"])
        tiles = [(t[0],t[1],t[2]) for t in copy] if copy else tiles_for(prog)
        title = s.get("title","")
        # first usable product/photo for mockup backgrounds
        photo = ""
        for d in ("photos","webimg"):
            pd_ = run/d
            if pd_.exists():
                pics = sorted(x for x in pd_.iterdir() if x.suffix.lower() in (".jpg",".jpeg",".png",".webp"))
                if pics: photo = pics[0].resolve().as_uri(); break
        html_doc = board_html(brand, theme, title, tiles, photo)
        hf = (out/f"board_s{n:02d}.html").resolve(); hf.write_text(html_doc)
        png = out/f"board_s{n:02d}.png"
        subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars",f"--screenshot={png}",
                        "--window-size=1560,880",hf.as_uri()],capture_output=True,timeout=90)
        s["visual"]={"type":"image","desc":f"Creative board: {prog['name']} channel mockups","file":f"visuals/board_s{n:02d}.png"}
        changed.append(n)
    json.dump(deck,open(deck_path,"w"),indent=2)
    print("boards:",changed)

if __name__=="__main__":
    main(sys.argv[1])
