#!/usr/bin/env python3
"""Generate slide visuals (PNG) for any deck straight from deck.json + check.json.

Usage: python3 make_visuals.py runs/vNN/deck.json
Writes runs/vNN/visuals/sNN.png and sets slide.visual.file. Then run render.py.

What it builds (all data-driven, so numbers always match the deck):
  cover, overview cards, objectives table, persona cards, research methods + findings,
  finding->therefore table, key visual, program mockups, phone creative samples,
  Gantt from programs[].weeks, budget table + finance cases, KPI table, closing callouts.
Visuals are clean vector-style mockups. Replace product/persona art with real photos before submission
(set visual.file to your photo path; this script skips slides whose visual.file points to a non-generated file).
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TAG = re.compile(r"\s*\[(?:[SARO]\d+)(?:\]\[|,\s*|[SARO]\d+)*\]")


def e(t):
    return html.escape(TAG.sub("", str(t)))


def css(brand, dark="#1f1f24", cream="#fbf7f2"):
    return f"""*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1000px;height:760px;font-family:-apple-system,Helvetica,Arial,sans-serif;color:{dark};background:{cream};padding:30px;overflow:hidden}}
.h{{font-size:28px;font-weight:800;margin-bottom:16px}} .sub{{font-size:15px;color:#777;margin-bottom:12px}}
.grid{{display:grid;gap:16px}} .card{{background:#fff;border-radius:16px;padding:18px;box-shadow:0 2px 8px rgba(0,0,0,.08);font-size:17px;line-height:1.35}}
.tag{{display:inline-block;background:{brand};color:#fff;border-radius:999px;padding:4px 12px;font-size:13px;font-weight:700;margin-bottom:8px}}
.big{{font-size:46px;font-weight:900;color:{brand}}} .brand{{background:{brand};color:#fff}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:15px}}
th{{background:{dark};color:#fff;text-align:left;padding:10px}} td{{padding:9px 10px;border-bottom:1px solid #eee;vertical-align:top}}
tr:nth-child(even) td{{background:#f7f1ea}} .on{{background:{brand} !important}}
.phone{{width:270px;height:540px;background:#111;border-radius:38px;padding:14px;flex:none}}
.screen{{background:#fff;height:100%;border-radius:26px;padding:16px;font-size:15px;overflow:hidden}}
.bubble{{background:#ececef;border-radius:16px;padding:10px 12px;margin:10px 0;line-height:1.3}}
.foot{{position:absolute;bottom:12px;right:22px;font-size:12px;color:#999}}"""


class Builder:
    def __init__(self, deck_path):
        self.path = Path(deck_path).resolve()
        self.run = self.path.parent
        self.deck = json.load(open(self.path))
        chk = self.run / "check.json"
        self.fin = json.load(open(chk)).get("finance") if chk.exists() else None
        self.out = self.run / "visuals"
        self.out.mkdir(exist_ok=True)
        m = self.deck["meta"]
        self.brand = m.get("brand_color") or "#0a66c2"
        self.theme = m.get("theme") or m.get("campaign_name", "")
        self.css = css(self.brand)

    def shot(self, n, body, foot="Agency mockup; illustrative."):
        f = self.out / f"s{n:02d}.html"
        f.write_text(f"<html><head><meta charset='utf-8'><style>{self.css}</style></head><body>{body}<div class='foot'>{e(foot)}</div></body></html>")
        png = self.out / f"s{n:02d}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
                        "--window-size=1000,760", f.as_uri()], capture_output=True, timeout=90)
        return f"visuals/s{n:02d}.png"

    # ---- builders -------------------------------------------------------------------
    def cover(self, s):
        m = self.deck["meta"]
        return (f"<div class='brand' style='margin:-30px;height:760px;padding:70px;display:flex;flex-direction:column;justify-content:center'>"
                f"<div style='font-size:22px;letter-spacing:.2em;opacity:.9'>{e(m.get('product','')).upper()}</div>"
                f"<div style='font-size:76px;font-weight:900;line-height:1.02;margin:14px 0'>{e(m.get('campaign_name',''))}</div>"
                f"<div style='font-size:24px;opacity:.95'>{e(m.get('thesis',''))}</div></div>")

    def overview(self, s):
        cards = []
        for b in s["bullets"]:
            label, _, rest = TAG.sub("", b).partition(":")
            if rest and len(label) < 22:
                cards.append(f"<div class='card'><span class='tag'>{e(label.upper())}</span><div>{e(rest)}</div></div>")
        return f"<div class='h'>{e(s['title'])}</div><div class='grid' style='grid-template-columns:1fr 1fr'>{''.join(cards[:6])}</div>"

    def objectives(self, s):
        rows = "".join(f"<tr><td><b>{e(o['id'])}</b></td><td>{e(o.get('funnel_stage','')).title()}</td><td>{e(o['text'])}</td></tr>"
                       for o in self.deck["objectives"])
        return f"<div class='h'>Campaign objectives</div><table><tr><th>ID</th><th>Funnel stage</th><th>Objective</th></tr>{rows}</table>"

    def personas(self, s):
        cards = "".join(
            f"<div class='card'><span class='tag'>{e(p['id'])} {e(p.get('role','')).upper()}</span><h3 style='margin:4px 0 10px'>{e(p['name'])}</h3>"
            f"<p><b>Who:</b> {e(p.get('demographic',''))}</p><p><b>Where:</b> {e(p.get('geographic',''))}</p>"
            f"<p><b>Values:</b> {e(p.get('psychographic',''))}</p><p><b>Behavior:</b> {e(p.get('behavioral',''))}</p>"
            f"<p><b>Media:</b> {e(p.get('media',''))}</p></div>" for p in self.deck["segments"])
        return f"<div class='h'>Target market</div><div class='grid' style='grid-template-columns:1fr 1fr;font-size:14px'>{cards}</div>"

    def research(self, s):
        r = self.deck.get("research", {})
        rows = "".join(f"<tr><td>{e(m.get('type','')).replace('_',' ').title()}</td><td>{e(m.get('n') or '')}</td><td>{e(m.get('dates',''))}</td><td>{e(m.get('status',''))}</td></tr>"
                       for m in r.get("methods", []))
        finds = "".join(f"<div class='card' style='margin-top:10px'><b>{e(f['id'])}</b> {e(f['finding'])}</div>" for f in r.get("findings", [])[:4])
        return f"<div class='h'>Research methods &amp; results</div><table><tr><th>Method</th><th>n</th><th>Dates</th><th>Status</th></tr>{rows}</table>{finds}"

    def insights(self, s):
        rows = []
        for b in s["bullets"]:
            if "->" in b or "→" in b:
                left, right = re.split(r"->|→", TAG.sub("", b), maxsplit=1)
                rows.append(f"<tr><td>{e(left.replace('Finding:','').strip())}</td><td><b>{e(right.replace('therefore','').strip())}</b></td></tr>")
        return f"<div class='h'>Insight &rarr; decision</div><table><tr><th>Finding</th><th>Therefore we will</th></tr>{''.join(rows)}</table>"

    def key_visual(self, s):
        return (f"<div class='brand' style='margin:-30px;height:760px;padding:70px;display:flex;flex-direction:column;justify-content:center'>"
                f"<div style='font-size:24px;opacity:.9'>{e(self.deck['meta'].get('product',''))}</div>"
                f"<div style='font-size:92px;font-weight:900;line-height:1'>{e(self.theme)}</div>"
                f"<div style='font-size:24px;margin-top:22px;max-width:760px'>{e(s['bullets'][0] if s['bullets'] else '')}</div></div>")

    def program(self, s):
        desc = (s.get("visual") or {}).get("desc", "")
        bullets = "".join(f"<li style='margin:8px 0'>{e(b)}</li>" for b in s["bullets"][1:4])
        phone = any(k in desc.lower() for k in ("tiktok", "phone", "email", "sms", "instagram"))
        art = (f"<div class='phone'><div class='screen'><div class='tag'>{e(self.theme)}</div><div class='bubble'>{e(s['bullets'][0] if s['bullets'] else '')}</div></div></div>"
               if phone else f"<div class='brand' style='width:330px;height:420px;border-radius:20px;padding:28px;display:flex;flex-direction:column;justify-content:space-between;flex:none'>"
               f"<div style='font-size:16px;opacity:.9'>{e(self.deck['meta'].get('product',''))}</div><div style='font-size:44px;font-weight:900;line-height:1.05'>{e(self.theme)}</div>"
               f"<div style='font-size:15px'>{e(desc[:120])}</div></div>")
        return (f"<div class='h'>{e(s['title'])}</div><div style='display:flex;gap:30px;align-items:flex-start'>{art}"
                f"<ul style='font-size:18px;line-height:1.35;padding-left:20px'>{bullets}</ul></div>")

    def creative(self, s):
        phones = []
        for b in s["bullets"][:3]:
            label, _, copy = TAG.sub("", b).partition(":")
            phones.append(f"<div class='phone' style='width:290px'><div class='screen'><b>{e(label)}</b><div class='bubble'>{e(copy.strip().strip(chr(39)))}</div></div></div>")
        return f"<div style='display:flex;gap:22px;justify-content:center'>{''.join(phones)}</div>"

    def gantt(self, s):
        progs = self.deck.get("programs", [])
        weeks = max([w for g in progs for w in g.get("weeks", [])] or [7])
        head = "".join(f"<th>W{w}</th>" for w in range(1, weeks + 1))
        rows = "".join(f"<tr><td><b>{e(g['name'])}</b><br><span style='font-size:12px'>{e(g.get('segment',''))} · {e(', '.join(g.get('channels',[])[:2]))} · {e('/'.join(g.get('objectives',[])))} · {e(g.get('owner',''))}</span></td>"
                       + "".join(f"<td class='{'on' if w in g.get('weeks', []) else ''}'></td>" for w in range(1, weeks + 1)) + "</tr>" for g in progs)
        return f"<div class='h'>Schedule</div><table><tr><th style='width:42%'>Program</th>{head}</tr>{rows}</table>"

    def budget(self, s):
        b = self.deck["budget"]
        rows = "".join(f"<tr><td>{e(l['item'])}</td><td style='text-align:right'>${l['usd']:,.0f}</td></tr>" for l in b["lines"])
        rows += f"<tr><td><b>Total</b></td><td style='text-align:right'><b>${b['total_usd']:,.0f}</b></td></tr>"
        cases = ""
        if self.fin:
            f = self.fin
            cases = "".join(f"<tr><td>{n}</td><td>{c['orders']:,}</td><td>${c['revenue_usd']:,}</td><td>${c['gross_profit_usd']:,}</td><td><b>{c['roi_profit_based']:+.0%}</b></td></tr>"
                            for n, c in (("Base", f["base_case"]), ("Conservative", f["conservative_case"])))
            cases = (f"<table style='margin-top:0'><tr><th>Case</th><th>Orders</th><th>Revenue</th><th>Gross profit</th><th>ROI</th></tr>{cases}</table>"
                     f"<div class='card' style='margin-top:12px'>Break-even: <b>{f['break_even_orders']:,} orders</b> &middot; ROAS {f['base_case']['roas']}x &middot; CAC ${f['base_case']['cac_usd']}</div>")
        return f"<div class='h'>Budget &amp; financial viability</div><div style='display:flex;gap:18px'><table style='flex:1;font-size:14px'><tr><th>Line</th><th>$</th></tr>{rows}</table><div style='flex:1.1'>{cases}</div></div>"

    def kpis(self, s):
        rows = "".join(f"<tr><td><b>{e(k['objective'])}</b></td><td>{e(k['kpi'])}</td><td>{e(k.get('baseline',''))}</td><td>{e(k.get('target',''))}</td><td>{e(k.get('tool',''))}</td><td>{e(k.get('cadence',''))}</td></tr>"
                       for k in self.deck.get("kpis", []))
        return f"<div class='h'>Impact &amp; measurement</div><table style='font-size:13px'><tr><th>Obj</th><th>KPI</th><th>Baseline</th><th>Target</th><th>Tool</th><th>Cadence</th></tr>{rows}</table>"

    def why(self, s):
        calls = []
        if self.fin:
            calls = [(f"{self.fin['base_case']['orders']:,}", "projected orders"), (f"{self.fin['base_case']['roi_profit_based']:+.0%}", "profit-based ROI"),
                     (f"{self.fin['break_even_orders']:,}", "break-even orders")]
        boxes = "".join(f"<div style='background:#fff;color:#222;border-radius:14px;padding:18px;flex:1'><div class='big'>{a}</div><div>{b}</div></div>" for a, b in calls)
        return (f"<div style='margin:-30px;height:760px;background:#1f1f24;color:#fff;padding:56px'><div class='tag'>WHY IT MATTERS</div>"
                f"<div style='font-size:40px;font-weight:900;line-height:1.15;margin:16px 0 30px'>{e(self.deck['meta'].get('thesis',''))}</div>"
                f"<div style='display:flex;gap:18px'>{boxes}</div></div>")

    def pick(self, s, first_strategy):
        sec, title, vtype = s.get("section"), s.get("title", "").lower(), (s.get("visual") or {}).get("type", "none")
        if sec == "cover": return self.cover
        if sec == "overview": return self.overview
        if sec == "objectives": return self.objectives
        if sec == "target_market": return self.personas
        if sec == "research": return self.insights if any("->" in b or "→" in b for b in s["bullets"]) else self.research
        if sec == "strategy":
            if "schedule" in title: return self.gantt
            if "creative" in title: return self.creative
            return self.key_visual if s["n"] == first_strategy else self.program
        if sec == "budget": return self.budget
        if sec == "impact": return self.kpis if "measure" in title or "impact" in title else self.why
        return None if vtype == "none" else self.program

    def build(self):
        first_strategy = min((s["n"] for s in self.deck["slides"] if s.get("section") == "strategy"), default=0)
        made = 0
        for s in self.deck["slides"]:
            cur = (s.get("visual") or {}).get("file", "")
            if cur and not cur.startswith("visuals/s"):
                continue  # human-provided photo: keep it
            fn = self.pick(s, first_strategy)
            if not fn:
                continue
            s.setdefault("visual", {"type": "image"})["file"] = self.shot(s["n"], fn(s))
            if s["visual"].get("type") == "none":
                s["visual"]["type"] = "image"
            made += 1
        json.dump(self.deck, open(self.path, "w"), indent=2, ensure_ascii=False)
        print(f"generated {made} visuals in {self.out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    Builder(sys.argv[1]).build()
