#!/usr/bin/env python3
"""Generate a Gamma deck from deck.json via the Gamma Public API.
Free/Plus plans cap at 10 cards per generation, so slides are chunked into
multi-card gammas and the exported PDFs are merged into one deck.
Usage: GAMMA_API_KEY=sk-... python3 gamma_api.py ../runs/vNN/deck.json [--theme ID] [--images pexels|aiGenerated|noImages] [--export pdf|pptx|png] [--per 9]"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

BASE = "https://public-api.gamma.app/v1.0"
import re
TAG = re.compile(r"\s*\[(?:[SAROMG]\d+)(?:\]\[|,\s*|[SARO]\d+)*\]")
def clean(t): return TAG.sub("", str(t)).strip()

def build_input(deck, slides, header=True):
    m = deck["meta"]
    parts = []
    if header:
        title_slide = next((s for s in deck["slides"] if s["section"]=="title"), {})
        tbul = " | ".join(clean(b) for b in title_slide.get("bullets",[]))
        parts.append(f"# {m.get('campaign_name','')} — Integrated Marketing Campaign (Product)\n"
             f"{m.get('product','')} by {m.get('company','')}\n"
             f"{m.get('school','')} · {m.get('school_address','')} · {', '.join(m.get('participants',[]))} · {m.get('date','')}\n"
             f"{tbul}\nThesis: {m.get('thesis','')}")
    for s in slides:
        sec = s["section"].replace("_"," ").title()
        body = f"## {sec}: {s.get('title','')}\n" + "\n".join(f"- {clean(b)}" for b in s.get("bullets",[]))
        if s.get("notes"): body += f"\n(Speaker note: {s['notes']})"
        parts.append(body)
    return "\n---\n".join(parts)

def req(method, path, key, payload=None):
    r = urllib.request.Request(BASE + path, method=method,
        headers={"X-API-KEY": key, "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"},
        data=json.dumps(payload).encode() if payload else None)
    try:
        return json.load(urllib.request.urlopen(r, timeout=60))
    except urllib.error.HTTPError as ex:
        print(f"HTTP {ex.code} {path}: {ex.read().decode()[:500]}", file=sys.stderr)
        raise

def generate(key, payload, label):
    res = req("POST", "/generations", key, payload)
    gid = res.get("generationId") or res.get("id") or (res.get("generation") or {}).get("id")
    print(f"[{label}] generationId: {gid}", flush=True)
    if not gid:
        print(json.dumps(res)[:600]); return None
    g = {}
    for _ in range(90):
        time.sleep(10)
        st = req("GET", f"/generations/{gid}", key)
        g = st.get("generation", st)
        status = g.get("status")
        print(f"[{label}] status: {status}", flush=True)
        if status in ("succeeded","failed","error","completed","cancelled"):
            if g.get("exportUrl") or g.get("export_url") or status in ("failed","error","cancelled"):
                break
    print(f"[{label}] gammaUrl: {g.get('gammaUrl') or g.get('gamma_url')}", flush=True)
    print(f"[{label}] exportUrl: {g.get('exportUrl') or g.get('export_url')}", flush=True)
    return g

def main():
    deck_path = Path(sys.argv[1]).resolve(); deck = json.load(open(deck_path))
    run = deck_path.parent
    key = os.environ.get("GAMMA_API_KEY") or os.environ.get("GAMMA_KEY")
    if not key: sys.exit("Set GAMMA_API_KEY")
    theme, images, export, per = None, "pexels", "pdf", 9
    args = sys.argv[2:]
    for i,a in enumerate(args):
        if a == "--theme" and i+1 < len(args): theme = args[i+1]
        if a == "--images" and i+1 < len(args): images = args[i+1]
        if a == "--export" and i+1 < len(args): export = args[i+1]
        if a == "--per" and i+1 < len(args): per = int(args[i+1])

    slides = deck["slides"]
    # compact mode: cover+title slides are folded into the header card (Gamma makes its own title card)
    compact = "--compact" in args
    if compact:
        slides = [s for s in slides if s["section"] not in ("cover","title")]
    chunks = [slides[i:i+per] for i in range(0, len(slides), per)]
    print(f"{len(slides)} slides -> {len(chunks)} gamma generations ({per}/gen max)")
    pdfs, urls = [], []
    for ci, chunk in enumerate(chunks):
        existing = run / f"deck_gamma_part{ci+1}.{export}"
        if existing.exists() and existing.stat().st_size > 10000:
            print(f"[part{ci+1}] exists, skipping generation", flush=True)
            if export == "pdf": pdfs.append(existing)
            continue
        payload = {
            "title": f"{deck['meta'].get('campaign_name','')} — IMCP part {ci+1} ({deck['meta'].get('product','')})",
            "inputText": build_input(deck, chunk, header=(ci == 0)),
            "format": "presentation",
            "textMode": "preserve",
            "cardSplit": "inputTextBreaks",
            "cardOptions": {"dimensions": "16x9"},
            "imageOptions": {"source": images},
            "exportAs": export,
            "additionalInstructions": ("Professional DECA IMCP marketing pitch deck. Clean modern design, "
                "strong visual hierarchy, one idea per card, generous whitespace. Avoid clip-art; use images where they add value."),
        }
        if theme and theme != "none": payload["themeId"] = theme
        g = generate(key, payload, f"part{ci+1}")
        if not g: continue
        urls.append(g.get("gammaUrl") or g.get("gamma_url"))
        exp = g.get("exportUrl") or g.get("export_url")
        if exp:
            out = run / f"deck_gamma_part{ci+1}.{export}"
            rq = urllib.request.Request(exp, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
                "X-API-KEY": key})
            try:
                data = urllib.request.urlopen(rq, timeout=120).read()
                out.write_bytes(data)
                print(f"[part{ci+1}] downloaded {out} ({len(data)} bytes)", flush=True)
                if export == "pdf": pdfs.append(out)
            except Exception as ex:
                print(f"[part{ci+1}] export download failed: {ex}", flush=True)
        else:
            print(f"[part{ci+1}] no exportUrl in response: {json.dumps(g)[:400]}", flush=True)
    if export == "pdf" and pdfs:
        merged = run / "deck_gamma.pdf"
        import subprocess
        r = subprocess.run(["pdfunite"] + [str(p) for p in pdfs] + [str(merged)], capture_output=True)
        if r.returncode == 0:
            print("Merged ->", merged)
        else:
            print("PDF merge failed:", r.stderr.decode()[:300], "- parts are in run dir")
    print("GAMMA URLS:", urls)

if __name__ == "__main__":
    main()
