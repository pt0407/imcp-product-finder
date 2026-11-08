#!/usr/bin/env python3
"""Render deck.json -> IMCP-format designed slides (matches It's-Not-Jerky.pdf style) -> deck_imcp.pdf
Section-specific layouts driven by deck.json structured data. Usage: render_imcp.py ../runs/vNN/deck.json"""
import html, json, re, subprocess, sys
from pathlib import Path
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHART_DIR = None
def brand_rgb(hexstr, default=(0.24,0.36,0.55)):
    h = (hexstr or "#3d5a80").lstrip("#")
    try: return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
    except Exception: return default

def make_charts(deck, run):
    """Generate data-driven PNG charts into run/imcp/charts/. Returns {key: path}."""
    global CHART_DIR
    CHART_DIR = run / "imcp" / "charts"; CHART_DIR.mkdir(parents=True, exist_ok=True)
    brand = deck["meta"].get("brand_color","#3d5a80"); c = brand_rgb(brand)
    out = {}
    plt.rcParams.update({"font.family":"Helvetica","font.size":13,"axes.edgecolor":"#ddd","axes.labelcolor":"#444"})
    # 1) budget horizontal bars
    lines = deck.get("budget",{}).get("lines",[])
    if lines:
        fig,ax = plt.subplots(figsize=(6.8,1.9),dpi=200)
        items=[l["item"][:34] for l in lines][::-1]; vals=[l["usd"] for l in lines][::-1]
        ax.barh(items,vals,color=c,height=.62)
        for i,v in enumerate(vals): ax.text(v+max(vals)*.01,i,f"${v:,}",va="center",fontsize=12,fontweight="bold")
        ax.set_xlim(0,max(vals)*1.22); ax.set_xticks([]); ax.spines[["top","right","bottom"]].set_visible(False)
        ax.set_title("Campaign Budget Allocation",fontsize=15,fontweight="bold",loc="left")
        fig.tight_layout(); p=CHART_DIR/"budget.png"; fig.savefig(p,bbox_inches="tight",facecolor="white"); plt.close(fig); out["budget"]=p
    # 2) review theme frequency (real coded data)
    repo = run.parents[2]
    for m in deck.get("research",{}).get("methods",[]):
        if m.get("type")=="review_analysis" and m.get("results_file"):
            summ = repo/m["results_file"]/"review_summary.md"
            if summ.exists():
                themes=[]
                for line in summ.read_text().splitlines():
                    mm=re.match(r"\|\s*([a-z_]+)\s*\|\s*(\d+)\s*\|\s*(\d+)%",line)
                    if mm and mm.group(1) not in ("theme",): themes.append((mm.group(1).replace("_"," "),int(mm.group(3))))
                if themes:
                    fig,ax=plt.subplots(figsize=(6.4,3.4),dpi=200)
                    themes=themes[::-1]
                    ax.barh([t[0] for t in themes],[t[1] for t in themes],color=c,height=.6)
                    for i,(_,v) in enumerate(themes): ax.text(v+.3,i,f"{v}%",va="center",fontsize=11,fontweight="bold")
                    ax.set_xlim(0,max(t[1] for t in themes)*1.3); ax.set_xticks([]); ax.spines[["top","right","bottom"]].set_visible(False)
                    ax.set_title("What 500 Verified Reviews Mention",fontsize=15,fontweight="bold",loc="left")
                    fig.tight_layout(); p=CHART_DIR/"themes.png"; fig.savefig(p,bbox_inches="tight",facecolor="white"); plt.close(fig); out["themes"]=p
            break
    return out

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TAG = re.compile(r"\s*\[(?:[SAROMG]\d+)(?:\]\[|,\s*|[SARO]\d+)*\]")
W, H = 1600, 900
def e(t): return html.escape(TAG.sub("", str(t)).strip())
def clean(b): return TAG.sub("", str(b)).strip()

def bullets_html(bs, cls=""):
    out = ""
    for b in bs:
        t = clean(b); m = re.match(r"^(.*?[.:—–-])\s+(.*)$", t, re.S)
        inner = f"<b>{html.escape(m.group(1))}</b> {html.escape(m.group(2))}" if m and len(m.group(1))<70 else html.escape(t)
        out += f'<li class="{cls}">{inner}</li>'
    return out

def b64(p):
    import base64
    return base64.b64encode(p.read_bytes()).decode()

def photo_strip(run, n=5):
    imgs = []
    for d in ("webimg","photos"):
        p = run/d
        if p.exists(): imgs += sorted(x for x in p.iterdir() if x.suffix.lower() in (".jpg",".jpeg",".png",".webp"))
    if not imgs: return ""
    imgs = imgs[:n]
    cells = "".join(f'<img src="{x.resolve().as_uri()}">' for x in imgs)
    return f'<div class="strip">{cells}</div>'

def visual_uri(run, s):
    v = s.get("visual") or {}; f = v.get("file")
    cands = []
    if f: cands.append(run / f)
    cands += [run/"visuals"/f"s{s['n']:02d}.png", run/"visuals"/f"board_s{s['n']:02d}.png"]
    for p in cands:
        if p.exists(): return p.resolve().as_uri()
    # real business imagery harvested from the brand's own site
    web = sorted((run/"webimg").glob("*")) if (run/"webimg").exists() else []
    if web:
        return web[(s["n"]-1) % len(web)].resolve().as_uri()
    return ""

def kicker(txt): return f'<div class="kick">{html.escape(txt)}</div>'
def h1(txt): return f'<div class="h1">{html.escape(txt)}</div><div class="tbar"></div>'

def fonts(meta):
    d = meta.get("display_font","Archivo").replace(" ","+")
    b = meta.get("body_font","Inter").replace(" ","+")
    fams = f"family={d}:wght@600;700;800;900" if d==b else f"family={d}:wght@600;700;800;900&family={b}:wght@400;500;600;700"
    return (f"""<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fams}&display=swap" rel="stylesheet">""")

NAV_SECTIONS = ["Product","Objectives","Target Market","Proposed Plan","Expenses","Key Metrics"]
NAV_MAP = {"description":"Product","objectives":"Objectives","target":"Target Market",
           "programs":"Proposed Plan","schedule":"Proposed Plan","strategy":"Proposed Plan",
           "insights":"Proposed Plan","budget":"Expenses","impact":"Key Metrics"}
def nav_html(meta, idx, sec):
    cur = NAV_MAP.get(sec)
    pills = "".join(f'<span class="navp{" on" if l==cur else ""}">{l}</span>' for l in NAV_SECTIONS)
    return (f'<div class="navbar"><div class="navpills">{pills}</div>'
            f'<div class="pgcirc">{idx+1}</div></div>')

def page(meta, idx, total, body, bg="#ffffff", sec=""):
    css = (CSS.replace('__BRAND__',meta.get('brand_color','#1f4e79'))
              .replace('__ACC__',meta.get('accent_color') or meta.get('brand_color','#1f4e79'))
              .replace('__DISP__',meta.get('display_font','Archivo'))
              .replace('__BODY__',meta.get('body_font','Inter')))
    chrome = "" if sec in ("cover","title") else nav_html(meta, idx, sec)
    frame  = "" if sec in ("cover","title") else '<div class="frame"></div>'
    return f"""<!doctype html><html><head><meta charset='utf-8'>{fonts(meta)}<style>{css}</style></head>
<body><div class="page" style="background:{bg}">{frame}{body}{chrome}</div></body></html>"""

CSS = """
:root{--brand:__BRAND__;--acc:__ACC__}
*{box-sizing:border-box;margin:0;padding:0}
.page{width:1600px;height:900px;font-family:'__BODY__','Helvetica Neue',Helvetica,Arial,sans-serif;color:#1c1c1e;position:relative;padding:70px 96px 150px;display:flex;flex-direction:column}
.frame{position:absolute;left:26px;top:26px;right:26px;bottom:26px;border:5px solid var(--acc);border-radius:34px;pointer-events:none}
.navbar{position:absolute;left:64px;right:64px;bottom:40px;display:flex;align-items:center;justify-content:space-between}
.navpills{display:flex;gap:12px}
.navp{font-size:16px;font-weight:700;padding:9px 20px;border-radius:999px;background:#eceadf;color:#57534a}
.navp.on{background:var(--acc);color:#fff}
.pgcirc{width:54px;height:54px;border-radius:50%;background:var(--brand);color:#fff;font-size:21px;font-weight:800;display:flex;align-items:center;justify-content:center}
.statp{display:inline-block;background:var(--brand);color:#fff;font-size:28px;font-weight:800;padding:13px 28px;border-radius:999px;margin:6px 12px 6px 0}
.themep{display:inline-block;background:var(--acc);color:#fff;font-size:26px;font-weight:800;padding:14px 38px;border-radius:999px;margin:8px 0 18px}
.tbar{width:88px;height:10px;background:var(--acc);border-radius:6px;margin:4px 0 20px}
.catband{background:var(--acc);color:#fff;font-weight:800;font-size:19px;padding:10px 18px;letter-spacing:.04em}
.strip{position:absolute;left:0;right:0;bottom:0;height:230px;display:flex;overflow:hidden;gap:4px}
.strip img{flex:1;object-fit:cover;min-width:0;height:230px}
.kick{font-family:'__DISP__','__BODY__',sans-serif;font-size:19px;letter-spacing:.32em;font-weight:800;color:var(--brand);text-transform:uppercase;margin-bottom:14px}
.kick.grey{color:#9a917f}
.h1{font-family:'__DISP__','__BODY__',sans-serif;font-size:54px;font-weight:900;letter-spacing:-1.5px;line-height:1.03;margin-bottom:8px}
.sub{font-size:21px;color:#6d675e;margin-bottom:26px}
.pfoot{position:absolute;bottom:30px;left:76px;right:76px;display:flex;justify-content:space-between;font-size:15px;color:#b3aa99;border-top:1px solid #ece5d8;padding-top:14px}
.card{background:#fff;border:1px solid #e8e1d4;border-radius:18px;padding:26px 28px;box-shadow:0 6px 20px rgba(60,50,30,.05)}
.card .cl{font-size:15px;letter-spacing:.22em;font-weight:800;color:var(--brand);margin-bottom:12px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.statn{font-size:64px;font-weight:900;color:var(--brand);line-height:1}
.statl{font-size:16px;color:#6d675e;margin-top:10px;line-height:1.35}
.body{font-size:23px;line-height:1.5;color:#33302a}
.body li{margin-bottom:16px}
.body li::marker{color:var(--brand)}
ul.body{list-style:disc;padding-left:26px}
.arrow{color:var(--brand);font-weight:900;font-size:30px}
table.tb{width:100%;border-collapse:collapse;font-size:20px}
.tb th{background:#211d18;color:#fff;text-align:left;padding:14px 16px;font-size:16px;letter-spacing:.08em}
.tb td{padding:14px 16px;border-bottom:1px solid #ece5d8;vertical-align:top;line-height:1.35}
.tb tr:nth-child(even) td{background:#faf7f1}
.ph{border:2px dashed #d8cfbf;border-radius:16px;display:flex;align-items:center;justify-content:center;color:#a2977f;font-size:18px;text-align:center;padding:20px}
img.vis{max-width:100%;max-height:560px;border-radius:16px;object-fit:contain;box-shadow:0 14px 40px rgba(0,0,0,.14)}
.cols2{display:flex;gap:40px}
.col{flex:1}
.q{border-left:6px solid var(--brand);background:#fff;padding:18px 22px;border-radius:0 14px 14px 0;font-size:21px;line-height:1.4;margin-bottom:16px;box-shadow:0 4px 14px rgba(60,50,30,.06)}
.q small{display:block;color:#a2977f;font-size:14px;margin-top:8px;letter-spacing:.08em;text-transform:uppercase}
.tag{display:inline-block;background:var(--brand);color:#fff;border-radius:999px;padding:5px 14px;font-size:14px;font-weight:800;letter-spacing:.06em}
.mono{font-family:'SF Mono',Menlo,monospace}
"""

def find(deck, sid): return next((p for p in deck.get("programs",[]) if p["id"]==sid), None)

def slide_html(deck, s, run, idx, total, charts=None):
    charts = charts or {}
    meta = deck["meta"]; sec = s["section"]; n = s["n"]
    slides = {x["n"]: x for x in deck["slides"]}
    B = lambda x: bullets_html(x.get("bullets",[]))
    uri = visual_uri(run, s)

    # ---------- cover ----------
    if sec == "cover":
        logo = ""
        lf = run / meta.get("logo_file","")
        if meta.get("logo_file") and lf.exists() and lf.suffix != ".svg":
            logo = f'<img src="data:image/png;base64,{b64(lf)}" style="height:64px;filter:brightness(0) invert(1);margin-bottom:60px">'
        kicker_txt = html.escape(meta.get("product","Integrated Marketing Campaign")).upper()
        body = f"""
<div style="margin-top:96px">{logo}
<div style="font-size:24px;letter-spacing:.4em;font-weight:800;color:#fff;opacity:.85">{kicker_txt}</div>
<div style="font-size:110px;font-family:'{meta.get('display_font','Archivo')}',sans-serif;font-weight:900;color:#fff;letter-spacing:-3px;line-height:1.02;margin:10px 0">{html.escape(meta.get('campaign_name',''))}</div>
<div style="font-size:30px;color:#fff;opacity:.95;font-weight:600;max-width:1250px">{html.escape(meta.get('thesis',''))}</div>
<div style="margin-top:40px;font-size:24px;color:#fff;opacity:.8">{html.escape(meta.get('company','').split('(')[0].strip())} · Integrated Marketing Campaign · {html.escape(meta.get('date',''))}</div>
</div>
{photo_strip(run)}"""
        return page(meta, idx, total, body, bg=meta.get("cover_bg") or meta.get("brand_color","#8a2f2f"), sec=sec)

    # ---------- title ----------
    if sec == "title":
        body = f"""<div style="margin:auto;text-align:center">
<div class="kick" style="font-size:26px">INTEGRATED MARKETING CAMPAIGN — PRODUCT</div>
<div style="font-size:88px;font-weight:900;letter-spacing:-2px">{html.escape(meta.get('campaign_name',''))}</div>
<div style="font-size:30px;color:#6d675e;margin-top:18px">{html.escape(meta.get('product',''))}</div>
<div style="margin-top:44px;font-size:24px;color:#6d675e">{html.escape(meta.get('school',''))} · {html.escape(meta.get('school_address',''))}</div>
<div style="font-size:22px;color:#6d675e;margin-top:8px">{html.escape(' · '.join(meta.get('participants',[])))}</div>
<div style="font-size:22px;color:#6d675e;margin-top:8px">{html.escape(meta.get('date',''))}</div></div>"""
        return page(meta, idx, total, body, sec=sec)

    # ---------- TOC ----------
    if sec == "toc":
        items = [clean(b) for b in s.get("bullets",[])]
        rows = "".join(f'<div style="display:flex;gap:26px;align-items:baseline;padding:13px 0;border-bottom:1px solid #ece5d8"><span class="mono" style="font-size:26px;color:var(--brand);font-weight:800">{i+1}</span><span style="font-size:28px;font-weight:700">{html.escape(t)}</span></div>' for i,t in enumerate(items))
        body = kicker("AGENDA") + h1(s.get("title","")) + f'<div class="card" style="padding:14px 34px;margin-top:20px">{rows}</div>'
        return page(meta, idx, total, body, sec=sec)

    # ---------- overview / exec summary ----------
    if sec == "overview":
        prob = next((x["text"] for x in deck.get("objectives",[]) if x.get("primary")), "")
        bp = deck.get("business_problem","")
        sol = meta.get("thesis","")
        goal = prob or ""
        body = kicker("EXECUTIVE SUMMARY") + h1(s.get("title","Campaign Overview")) + f"""
<div class="grid4" style="margin-top:24px">
<div class="card"><div class="cl">PROBLEM</div><div class="body" style="font-size:19px">{html.escape(bp[:220])}</div></div>
<div class="card"><div class="cl">OPPORTUNITY</div><div class="body" style="font-size:19px">{html.escape((deck.get('segments',[{}])[0].get('name','')+' segment: '+deck.get('segments',[{}])[0].get('psychographic',''))[:220])}</div></div>
<div class="card"><div class="cl">SOLUTION</div><div class="body" style="font-size:19px">{html.escape(sol[:220])}</div></div>
<div class="card"><div class="cl">45-DAY GOAL</div><div class="body" style="font-size:19px">{html.escape(goal[:220])}</div></div>
</div>
<div class="card" style="margin-top:24px;background:var(--brand);border:none"><div style="font-size:21px;color:#fff;font-weight:600">Core Thesis: {html.escape(sol)}</div></div>"""
        return page(meta, idx, total, body, sec=sec)

    # ---------- description: product then company (alternate by title) ----------
    if sec == "description":
        if "Product" in s.get("title","") or n <= 5:
            attrs = s.get("bullets",[])
            cards = ""
            for b in attrs[:4]:
                t = clean(b); lab,_,rest = t.partition(":")
                lab = lab if len(lab)<30 else t[:28]
                cards += f'<div class="card"><div class="cl">{html.escape(lab.upper())}</div><div class="body" style="font-size:19px">{html.escape(rest or t)}</div></div>'
            pics = []
            for d in ("photos","webimg"):
                pdir = run/d
                if pdir.exists(): pics += sorted(pdir.glob("*"))
            pics = pics[:6]
            picrow = ""
            if pics:
                picrow = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:22px">' + "".join(f'<img src="{p.resolve().as_uri()}" style="width:100%;height:190px;object-fit:cover;border-radius:14px">' for p in pics) + '</div>'
            body = kicker("PRODUCT PROFILE") + h1(s.get("title","The Product")) + f'<div class="body" style="font-size:24px;max-width:1100px">{B(s)}</div>' + f'<div class="grid4" style="margin-top:22px">{cards}</div>' + picrow
        else:
            right = f'<img class="vis" src="{uri}">' if uri else ""
            body = kicker("COMPANY & POSITION") + h1(s.get("title","")) + f'<div class="cols2"><div class="col"><div class="body">{B(s)}</div></div><div class="col">{right}</div></div>'
        return page(meta, idx, total, body, sec=sec)

    # ---------- objectives ----------
    if sec == "objectives":
        rows = ""
        for o in deck.get("objectives",[]):
            rows += f'<tr><td><span class="tag">{o["id"]}{" · PRIMARY" if o.get("primary") else ""}</span></td><td style="font-weight:700">{html.escape(o["funnel_stage"].title())}</td><td>{html.escape(o["text"])}</td></tr>'
        body = kicker("MEASURABLE GOALS") + h1(s.get("title","Campaign Objectives")) + f"""
<table class="tb" style="margin-top:20px"><tr><th style="width:120px">OBJECTIVE</th><th style="width:180px">FUNNEL STAGE</th><th>TARGET</th></tr>{rows}</table>
<div class="body" style="margin-top:22px;font-size:20px">{B(s)}</div>"""
        return page(meta, idx, total, body, sec=sec)

    # ---------- target market ----------
    if sec == "target_market":
        cards = ""
        for sg in deck.get("segments",[]):
            cards += f"""<div class="card"><div class="cl">{html.escape(sg['id'])} · {html.escape(sg['name'].upper())} {"(PRIMARY)" if sg.get('role')=='primary' else ""}</div>
<div class="body" style="font-size:20px"><b>Who:</b> {html.escape(sg.get('demographic',''))}<br><b>Where:</b> {html.escape(sg.get('geographic',''))}<br><b>Mindset:</b> {html.escape(sg.get('psychographic',''))}<br><b>Behavior:</b> {html.escape(sg.get('behavioral',''))}<br><b>Media:</b> {html.escape(sg.get('media',''))}</div></div>"""
        seg_imgs = ""
        imgs = []
        for d in ("webimg","photos"):
            p = run/d
            if p.exists(): imgs += sorted(x for x in p.iterdir() if x.suffix.lower() in (".jpg",".jpeg",".png",".webp"))
        if imgs:
            cells = "".join(f'<img src="{x.resolve().as_uri()}" style="flex:1;height:140px;object-fit:cover;border-radius:14px;min-width:0">' for x in imgs[:4])
            seg_imgs = f'<div style="display:flex;gap:16px;margin-top:26px">{cells}</div>'
        body = kicker("AUDIENCE SEGMENTS") + h1(s.get("title","Target Market")) + f'<div class="grid2" style="margin-top:22px">{cards}</div>{seg_imgs}'
        return page(meta, idx, total, body, sec=sec)

    # ---------- research slides ----------
    if sec == "research":
        if "Method" in s.get("title","") or "Results" in s.get("title",""):
            meth = "".join(f'<div class="q"><div class="body" style="font-size:20px">{html.escape(m["type"].replace("_"," ").title())} (n={m.get("n") or "—"}): {html.escape(m.get("recruitment","")[:180])} — {html.escape(m.get("status",""))}</div></div>' for m in deck.get("research",{}).get("methods",[]) if m.get("status")=="complete")
            finds = "".join(f'<div class="q" style="margin-bottom:10px;padding:14px 18px"><div class="body" style="font-size:18px">{html.escape(f["finding"][:190])}</div></div>' for f in deck.get("research",{}).get("findings",[])[:5])
            body = kicker("METHODOLOGY & FINDINGS") + h1(s.get("title","Research")) + f'<div class="cols2"><div class="col"><div class="kick grey" style="font-size:16px">METHODS</div>{meth}</div><div class="col"><div class="kick grey" style="font-size:16px">KEY RESULTS</div>{finds}</div></div>'
        else:
            rows = ""
            for f in deck.get("research",{}).get("findings",[]):
                dec = next((clean(b) for b in slides.get(11,{}).get("bullets",[]) if f["id"] in b), "→ campaign decision")
                rows += f'<div class="card" style="margin-bottom:18px;display:flex;gap:24px;align-items:center"><div class="body" style="flex:1.4;font-size:20px"><b>[{f["id"]}]</b> {html.escape(f["finding"][:200])}</div><div class="arrow">→</div><div class="body" style="flex:1;font-size:19px;color:var(--brand);font-weight:700">{html.escape(dec[:140])}</div></div>'
            if not rows:
                for b_ in slides.get(11,{}).get("bullets",[])[:5]:
                    rows += f'<div class="card" style="margin-bottom:14px"><div class="body" style="font-size:20px">{html.escape(clean(b_))}</div></div>'
            body = kicker("STRATEGIC LOGIC") + h1(s.get("title","")) + f'<div style="margin-top:18px">{rows}</div>'
        return page(meta, idx, total, body, sec=sec)

    # ---------- strategy + programs ----------
    if sec == "strategy" and "Program" in s.get("title",""):
        ids = [g for g in [p["id"] for p in deck.get("programs",[])] if g in " ".join(s.get("bullets",[]))]
        prog = find(deck, ids[0]) if ids else None
        if not prog:
            pm = re.search(r"Program\s+(\d+)", s.get("title",""))
            if pm:
                i = int(pm.group(1)) - 1
                progs = deck.get("programs",[])
                prog = progs[i] if 0 <= i < len(progs) else None
        if prog:
            body = kicker(f"PROGRAM {prog['id'][1:]} · {prog['name'].upper()}") + h1(prog["name"]) + f"""
<div class="cols2" style="margin-top:16px"><div class="col" style="flex:1.15">
<div class="card"><div class="body" style="font-size:21px">{html.escape(prog['mechanic'])}</div></div>
<div class="grid2" style="margin-top:18px;gap:14px">
<div class="card" style="padding:16px 18px"><div class="cl">SEGMENT</div><div class="body" style="font-size:17px">{html.escape(prog.get('segment',''))}</div></div>
<div class="card" style="padding:16px 18px"><div class="cl">CHANNELS</div><div class="body" style="font-size:17px">{html.escape(' · '.join(prog.get('channels',[])))}</div></div>
<div class="card" style="padding:16px 18px"><div class="cl">OBJECTIVES</div><div class="body" style="font-size:17px">{html.escape(' · '.join(prog.get('objectives',[])))}</div></div>
<div class="card" style="padding:16px 18px"><div class="cl">WEEKS / OWNER</div><div class="body" style="font-size:17px">Wks {html.escape(str(prog.get('weeks',[])))} · {html.escape(prog.get('owner',''))}</div></div>
</div></div>
<div class="col">{"" if not uri else f'<img class="vis" src="{uri}" style="max-height:560px;width:100%;object-fit:contain">'}</div></div>"""
            return page(meta, idx, total, body, sec=sec)

    if sec == "strategy" and ("Schedule" in s.get("title","") or "Week" in s.get("title","")):
        # Gantt-ish table from programs[].weeks
        rows = ""
        for p in deck.get("programs",[]):
            wks = "".join(f'<span style="display:inline-block;width:52px;height:26px;line-height:26px;text-align:center;border-radius:6px;background:var(--brand);color:#fff;font-size:14px;font-weight:700;margin-right:4px">{w}</span>' if w in p.get("weeks",[]) else '<span style="display:inline-block;width:52px;height:26px;line-height:26px;text-align:center;border-radius:6px;background:#efe9dd;color:#b3aa99;font-size:14px;margin-right:4px">{w}</span>' for w in range(1,8))
            rows += f'<tr><td style="font-weight:700">{html.escape(p["name"])}</td><td>{wks}</td><td style="font-size:17px">{html.escape(p.get("owner",""))}</td></tr>'
        body = kicker("45-DAY SCHEDULE") + h1(s.get("title","")) + f'<table class="tb" style="margin-top:20px"><tr><th>PROGRAM</th><th>WEEKS 1-7</th><th>OWNER</th></tr>{rows}</table><div class="body" style="margin-top:20px;font-size:20px">{B(s)}</div>'
        return page(meta, idx, total, body, sec=sec)

    # ---------- budget ----------
    if sec == "budget":
        b = deck.get("budget",{}); lines = b.get("lines",[])
        rows = "".join(f'<tr><td>{html.escape(l["item"])}</td><td style="text-align:right;font-weight:800">${l["usd"]:,}</td></tr>' for l in lines)
        proj = b.get("projection",{})
        fin = ""
        try:
            chk = run/"check.json"
            if chk.exists():
                f = json.load(open(chk)).get("finance",{})
                bc, cc = f.get("base_case",{}), f.get("conservative_case",{})
                fin = (f'<div style="margin-top:14px">'
                       f'<span class="statp">${b.get("total_usd",0):,}</span>'
                       f'<span class="statp">ROI: {bc.get("roi_profit_based",0)*100:.0f}%</span>'
                       f'<span class="statp">CAC: ${bc.get("cac_usd",0):.2f}</span><br>'
                       f'<span class="statp" style="background:#57534a">BE: {f.get("break_even_orders",0)} orders</span>'
                       f'<span class="statp" style="background:#57534a">Cons: {cc.get("roi_profit_based",0)*100:.0f}%</span></div>')
        except Exception: pass
        bchart = f'<img src="{charts["budget"].resolve().as_uri()}" style="width:100%;max-height:330px;object-fit:contain;border-radius:12px;margin-top:14px">' if "budget" in charts else ""
        body = kicker("BUDGET & FINANCIAL VIABILITY") + h1(s.get("title","")) + f'<div class="cols2"><div class="col"><table class="tb"><tr><th>LINE ITEM</th><th style="text-align:right">COST</th></tr>{rows}<tr><td style="font-weight:900">TOTAL</td><td style="text-align:right;font-weight:900">${b.get("total_usd",0):,}</td></tr></table>{bchart}</div><div class="col">{fin}<div class="body" style="margin-top:16px;font-size:19px">{B(s)}</div></div></div>'
        return page(meta, idx, total, body, sec=sec)

    # ---------- impact ----------
    if sec == "impact":
        if "Measurement" in s.get("title","") or "Metric" in s.get("title",""):
            rows = ""
            for k in deck.get("kpis",[]):
                rows += f'<tr><td><span class="tag">{k["objective"]}</span></td><td style="font-weight:700">{html.escape(k["kpi"][:80])}</td><td>{html.escape(str(k.get("baseline",""))[:60])}</td><td style="font-weight:800;color:var(--brand)">{html.escape(str(k.get("target",""))[:60])}</td><td style="font-size:16px">{html.escape(k.get("tool",""))} · {html.escape(k.get("cadence",""))}</td></tr>'
            body = kicker("IMPACT & MEASUREMENT") + h1(s.get("title","")) + f'<table class="tb" style="margin-top:20px;font-size:18px"><tr><th style="width:80px">OBJ</th><th>KPI</th><th>BASELINE</th><th>TARGET</th><th>TOOL · CADENCE</th></tr>{rows}</table><div class="body" style="margin-top:18px;font-size:19px">{B(s)}</div>'
        else:
            # breathing slide: dark full-bleed, big-number hero (UUPM pattern break)
            big = ""
            try:
                f_ = json.load(open(run/"check.json")).get("finance",{})
                bc = f_.get("base_case",{})
                if bc.get("orders"): big = f'<div style="font-size:150px;font-family:{chr(39)}{meta.get("display_font","Archivo")}{chr(39)},sans-serif;font-weight:900;color:#fff;line-height:1">{bc["orders"]:,}</div><div style="font-size:28px;color:#fff;opacity:.85;font-weight:600">attributed purchases in 45 days · ROI {bc.get("roi_profit_based",0)*100:.0f}%</div>'
            except Exception: pass
            bl = "".join(f'<div style="font-size:22px;color:#fff;opacity:.92;line-height:1.5;margin-bottom:14px">{html.escape(clean(b_))}</div>' for b_ in s.get("bullets",[])[:3])
            body = f"""<div style="margin-top:40px">
<div style="font-size:19px;letter-spacing:.32em;font-weight:800;color:#fff;opacity:.7;margin-bottom:16px">WHY IT MATTERS</div>
<div class="themep" style="opacity:.95">{html.escape(meta.get('theme',''))}</div>
<div class="h1" style="color:#fff;font-size:52px">{html.escape(s.get("title","Why This Campaign"))}</div>
{big}<div style="margin-top:34px;max-width:1150px">{bl}</div></div>"""
            return page(meta, idx, total, body, bg=meta.get("cover_bg") or meta.get("brand_color","#222"), sec=sec)
        return page(meta, idx, total, body, sec=sec)

    # ---------- bibliography ----------
    if sec == "bibliography":
        srcs = deck.get("sources",[])
        items = "".join(f'<div class="body" style="font-size:19px;margin-bottom:14px"><b>[S{i+1}]</b> {html.escape(x["publisher"])}. {html.escape(x["title"])} ({html.escape(x.get("date",""))}). <span class="mono" style="color:#8a8172;font-size:16px">{html.escape(x.get("url",""))}</span></div>' for i,x in enumerate(srcs))
        body = kicker("BIBLIOGRAPHY & SOURCES") + h1(s.get("title","Bibliography")) + f'<div style="margin-top:20px;columns:2;column-gap:50px">{items}</div>'
        return page(meta, idx, total, body, sec=sec)

    # ---------- strategy overview: theme pill (winner motif) ----------
    if sec == "strategy":
        chans = sorted({c for p in deck.get("programs",[]) for c in p.get("channels",[])})
        chips = "".join(f'<span class="navp" style="background:var(--brand);color:#fff;font-size:18px;padding:12px 24px">{html.escape(c)}</span>' for c in chans[:7])
        body = (kicker("CAMPAIGN STRATEGY") + h1(s.get("title","Campaign Strategy"))
                + f'<div class="themep">Theme: {html.escape(meta.get("theme",""))}</div>'
                + f'<div class="body" style="font-size:23px;max-width:1250px">{B(s)}</div>'
                + f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:26px">{chips}</div>')
        return page(meta, idx, total, body, sec=sec)

    # ---------- fallback: creative / anything else ----------
    uri_img = f'<img class="vis" src="{uri}" style="max-height:480px">' if uri else ""
    body = kicker(sec.upper().replace("_"," ")) + h1(s.get("title","")) + f'<div class="cols2"><div class="col"><ul class="body">{bullets_html(s.get("bullets",[]))}</ul></div><div class="col">{uri_img}</div></div>'
    return page(meta, idx, total, body, sec=sec)

def main(deck_path):
    deck = json.load(open(deck_path)); run = Path(deck_path).parent
    # per-brand identity: real palette/fonts/logo scraped by brandkit.py
    bj = run / "brand.json"
    if bj.exists():
        b = json.loads(bj.read_text()); m = deck["meta"]
        m["brand_color"] = b.get("primary") or m.get("brand_color")
        m["accent_color"] = b.get("accent") or m.get("brand_color")
        if b.get("display_font"): m["display_font"] = b["display_font"]
        if b.get("body_font"):    m["body_font"]    = b["body_font"]
        # dark cover bg: if primary is light (e.g. PUCKIPUPPY gold), use darkest palette color
        def lum(c):
            r,g,bl = int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)
            return (0.299*r+0.587*g+0.114*bl)/255
        m["cover_bg"] = min(b.get("palette",[]) or [m["brand_color"]], key=lum)
        if b.get("logo_file"): m["logo_file"] = b["logo_file"]
    outdir = run / "imcp"; outdir.mkdir(exist_ok=True)
    slides = deck["slides"]; total = len(slides); pngs = []
    charts = make_charts(deck, run)
    for i, s in enumerate(slides):
        doc = slide_html(deck, s, run, i, total, charts)
        hf = outdir / f"p{i+1:02d}.html"; hf.write_text(doc)
        png = outdir / f"p{i+1:02d}.png"
        if not (png.exists() and png.stat().st_size > 10000):
            subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars",f"--screenshot={png}",
                            f"--window-size={W},{H}",hf.resolve().as_uri()],capture_output=True,timeout=120)
        pngs.append(png)
    pdf = run / "deck_imcp.pdf"
    imgs = [Image.open(p).convert("RGB") for p in pngs]
    imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=144.0)
    print("Wrote", pdf, f"({len(pngs)} slides)")

if __name__ == "__main__":
    main(sys.argv[1])
