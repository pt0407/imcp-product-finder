import json, subprocess
from pathlib import Path

RUN = Path("/Users/pranav/Desktop/DevinProjects/imcp-product-finder/pipeline/runs/v07")
OUT = RUN / "visuals"
OUT.mkdir(exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
O, D, C = "#e2711d", "#2b2118", "#fff6ec"

CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1000px; height: 760px; font-family: -apple-system, Helvetica, Arial, sans-serif; color: {D};
        background: {C}; padding: 28px; overflow: hidden; }}
.h {{ font-size: 26px; font-weight: 800; margin-bottom: 14px; }}
.sub {{ font-size: 15px; color: #7a6a5a; margin-bottom: 16px; }}
.grid {{ display: grid; gap: 16px; }}
.card {{ background: #fff; border-radius: 16px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
.tag {{ display: inline-block; background: {O}; color: #fff; border-radius: 999px; padding: 4px 12px; font-size: 13px; font-weight: 700; }}
.big {{ font-size: 44px; font-weight: 900; color: {O}; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; font-size: 15px; }}
th {{ background: {D}; color: #fff; text-align: left; padding: 10px; }}
td {{ padding: 9px 10px; border-bottom: 1px solid #eee; }}
tr:nth-child(even) td {{ background: #fdf3e8; }}
.foot {{ position: absolute; bottom: 14px; right: 24px; font-size: 12px; color: #9a8a7a; }}
.phone {{ width: 260px; height: 520px; background: #111; border-radius: 36px; padding: 14px; }}
.screen {{ background: #fff; height: 100%; border-radius: 24px; padding: 14px; font-size: 14px; overflow: hidden; }}
.bubble {{ background: #e9e9eb; border-radius: 16px; padding: 10px 12px; margin: 8px 0; }}
.bag {{ width: 90px; height: 130px; background: {O}; border-radius: 10px 10px 4px 4px; color: #fff; font-weight: 900;
        display: flex; align-items: center; justify-content: center; text-align: center; font-size: 15px; line-height: 1.1; }}
"""

def shot(name, body, foot="Mockup created by the agency team; illustrative."):
    html = f"<html><head><style>{CSS}</style></head><body>{body}<div class='foot'>{foot}</div></body></html>"
    f = OUT / f"{name}.html"
    f.write_text(html)
    png = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
                    "--window-size=1000,760", f.as_uri()], capture_output=True, timeout=60)
    return f"visuals/{name}.png"

def bar(n, v):
    w = int(abs(v) * 5 + 4)
    neg = f"<div style='height:22px;width:{w}px;background:#999;border-radius:4px'></div>" if v < 0 else ""
    pos = f"<div style='height:22px;width:{w}px;background:{O};border-radius:4px'></div>" if v > 0 else ""
    sign = "+" if v > 0 else ""
    return (f"<div style='display:flex;align-items:center;gap:8px;margin:6px 0'><div style='width:190px'>{n}</div>"
            f"<div style='width:60px;display:flex;justify-content:flex-end'>{neg}</div><div style='width:2px;height:26px;background:#333'></div>"
            f"{pos}<b>{sign}{v}%</b></div>")

V = {}
V[1] = shot("cover", f"""<div style='height:100%;display:flex;align-items:center;gap:40px;background:{O};margin:-28px;padding:60px;color:#fff'>
<div><div style='font-size:22px;letter-spacing:.2em'>PAN'S MUSHROOM JERKY</div><div style='font-size:72px;font-weight:900;line-height:1'>Switch to<br>Mushroom Mode</div>
<div style='font-size:22px;margin-top:18px'>A 45-day H-E-B velocity campaign</div></div>
<div style='display:flex;gap:14px'><div class='bag' style='background:#fff;color:{O}'>PAN'S<br>Original</div><div class='bag' style='background:{D}'>PAN'S<br>Zesty Thai</div></div></div>""", "Illustrative cover concept.")
V[4] = shot("overview", f"""<div class='h'>Campaign at a glance</div><div class='grid' style='grid-template-columns:1fr 1fr'>
<div class='card'><span class='tag'>PROBLEM</span><p style='font-size:20px;margin-top:10px'>Stores up from ~750 to 2,500+.<br>Revenue down from $3.15M.<br><b>&le; ~6 bags per store per week.</b></p></div>
<div class='card'><span class='tag'>OPPORTUNITY</span><p style='font-size:20px;margin-top:10px'>Meat snacks <b>+11.3%</b> ($6.4B)<br>Plant-based meat <b>-10%</b><br>Pan's is in the wrong mental aisle.</p></div>
<div class='card'><span class='tag'>SOLUTION</span><p style='font-size:20px;margin-top:10px'><b>Switch to Mushroom Mode</b><br>Demos + clip strip + app coupon at H-E-B, honest taste-offs online.</p></div>
<div class='card'><span class='tag'>45-DAY GOAL</span><p class='big'>1,500</p><p style='font-size:18px'>attributed purchases + 25% units/store lift vs. control</p></div></div>""", "Sources: SEC filing, GFI/SPINS, Circana (see bibliography).")
V[5] = shot("product", f"""<div class='h'>Pan's Mushroom Jerky</div><div style='display:flex;gap:22px;align-items:flex-end;margin:30px 0'>
{''.join(f"<div class='bag' style='width:150px;height:210px;font-size:20px;background:{c}'>PAN'S<br>{n}</div>" for n,c in [('Original',O),('Zesty Thai','#b5451b'),('Applewood BBQ',D),('Salt &amp; Pepper','#7a5c3e')])}</div>
<div class='grid' style='grid-template-columns:repeat(4,1fr)'>{''.join(f"<div class='card' style='text-align:center;font-weight:800'>{t}</div>" for t in ['Shiitake','Vegan','Gluten-free','No allergens'])}</div>
<p class='sub' style='margin-top:16px'>$7.99-$8.99 per 2.2 oz bag &middot; family recipe from Malaysia</p>""", "Illustrative packaging concept.")
V[6] = shot("company", f"""<div class='h'>More stores, fewer bags per store</div><div style='display:flex;gap:24px'>
<div class='card' style='flex:1'><div class='sub'>Revenue (SEC filing) vs. store count</div><div style='font-weight:800;color:#2b2118;margin-bottom:6px'>Stores: ~750 (2020) &rarr; 2,500+ (2026) &uarr;</div><div style='display:flex;align-items:flex-end;gap:22px;height:300px'>
{''.join(f"<div style='text-align:center'><div style='font-weight:800'>${v}M</div><div style='width:70px;height:{int(v*85)}px;background:{O};border-radius:8px 8px 0 0'></div><div>{y}</div></div>" for y,v in [('FY22',3.15),('FY23',2.88),('FY24*',2.78)])}
</div><div class='sub' style='margin-top:8px'>*11 months. Stores: ~750 (2020) &rarr; 2,500+ today</div></div>
<div class='card' style='flex:1;position:relative;height:430px'><div class='sub'>Positioning map</div>
<div style='position:absolute;left:50%;top:50px;bottom:20px;border-left:2px solid #ccc'></div><div style='position:absolute;top:55%;left:20px;right:20px;border-top:2px solid #ccc'></div>
<div style='position:absolute;top:42px;left:52%;font-size:12px'>Honest snack</div><div style='position:absolute;bottom:22px;left:52%;font-size:12px'>Imitates meat</div>
<div style='position:absolute;top:57%;left:22px;font-size:12px'>Meat-based</div><div style='position:absolute;top:57%;right:22px;font-size:12px'>Plant-based</div>
<div style='position:absolute;top:110px;left:70px' class='tag'>Chomps</div><div style='position:absolute;top:170px;left:40px;background:#888' class='tag'>Old Trapper</div>
<div style='position:absolute;top:290px;left:60px;background:#888' class='tag'>Jack Link's</div><div style='position:absolute;bottom:50px;right:40px;background:#888' class='tag'>Plant-based meat</div>
<div style='position:absolute;top:100px;right:40px;background:{D};font-size:16px' class='tag'>PAN'S</div></div></div>""", "Source: SEC Reg CF filing; positions are agency judgment from brand claims.")
V[7] = shot("objectives", f"""<div class='h'>Objectives</div><table><tr><th>ID</th><th>Funnel stage</th><th>Objective</th><th>Target</th></tr>
<tr><td><b>O1</b></td><td>Conversion</td><td>Attributed purchases (coupon + online)</td><td><b>1,500</b></td></tr>
<tr><td><b>O1</b></td><td>Conversion</td><td>Units/store/week, demo vs. control</td><td><b>+25%</b></td></tr>
<tr><td><b>O2</b></td><td>Consideration</td><td>In-store samples / coupon claims</td><td><b>2,400 / 6,000</b></td></tr>
<tr><td><b>O3</b></td><td>Awareness</td><td>Impressions / aided awareness</td><td><b>1.0M / +10 pts</b></td></tr></table>
<div class='card' style='margin-top:20px;font-size:18px'>Baseline: <b>&le; ~6 bags per store per week</b> (SEC revenue / 2,500 stores / ~$4 wholesale)</div>""", "Baseline is an upper-bound estimate; confirm with company sell-through.")
V[8] = shot("personas", f"""<div class='h'>Who we're talking to</div><div class='grid' style='grid-template-columns:1fr 1fr'>
<div class='card'><span class='tag'>P1 PRIMARY</span><h3 style='margin:10px 0'>Young Snack Explorers, 18-29</h3><p>College students + early-career, Central Texas</p>
<p style='margin-top:8px'><b>Wants:</b> new flavors, no fake-meat hype</p><p><b>Buys:</b> weekly snacks, tries what friends &amp; TikTok show</p><p><b>Media:</b> TikTok, Reels, group chats</p></div>
<div class='card'><span class='tag' style='background:{D}'>P2 SECONDARY</span><h3 style='margin:10px 0'>Flexitarian H-E-B Parents, 30-50</h3><p>Household income $60K+, Central Texas suburbs</p>
<p style='margin-top:8px'><b>Wants:</b> clean, allergen-free snacks for the family</p><p><b>Buys:</b> weekly at H-E-B, uses app coupons</p><p><b>Media:</b> H-E-B app, Facebook, email</p></div></div>""", "Personas to be validated with the team's survey and interviews.")
V[9] = shot("research", f"""<div class='h'>Research methods &amp; key results</div><table style='margin-bottom:18px'><tr><th>Method</th><th>Status</th></tr>
<tr><td>Secondary: SEC filing, GFI/SPINS, Circana, company pages (11 sources)</td><td>Complete</td></tr>
<tr><td>Survey: Central Texas snack buyers, 10 questions</td><td>In field</td></tr><tr><td>Interviews + taste test (3-5)</td><td>In field</td></tr><tr><td>H-E-B shelf audit (3 stores)</td><td>In field</td></tr></table>
<div class='card'><div class='sub'>Category growth, 2025</div>{''.join(bar(n,v) for n,v in [('Chomps',61.5),('Dried meat snacks',11.5),('Meat snacks (total)',11.3),('Jerky subcategory',-0.5),('Plant-based meat',-10)])}</div>""", "Sources: Circana via trade press; GFI/SPINS.")
V[10] = shot("insights", f"""<div class='h'>Finding &rarr; therefore</div><table><tr><th>Finding</th><th>Therefore we will...</th></tr>
<tr><td>Stores up, revenue down</td><td>Fund trial at the shelf, not more distribution</td></tr>
<tr><td>Meat snacks +11.3%, plant-based meat -10%</td><td>Place and message Pan's next to jerky</td></tr>
<tr><td>Brand: "not trying to imitate beef"</td><td>Run honest taste-offs, no "tastes like beef" claims</td></tr>
<tr><td>Net loss every year</td><td>Make every dollar trackable: coupons, QR, test vs. control</td></tr></table>""", "Survey findings (R1-R3) will be added when fieldwork closes.")
V[11] = shot("keyvisual", f"""<div style='display:flex;height:100%;margin:-28px'><div style='flex:1;background:#8a6a50;color:#fff;padding:40px;display:flex;flex-direction:column;justify-content:center'>
<div style='font-size:22px;opacity:.8'>Regular jerky aisle</div><div style='display:flex;gap:10px;margin-top:20px'>{''.join("<div class='bag' style='background:#5a4030;width:70px;height:100px'>JERKY</div>" for _ in range(3))}</div></div>
<div style='flex:1;background:{O};color:#fff;padding:40px;display:flex;flex-direction:column;justify-content:center'><div style='font-size:20px'>Love jerky?</div>
<div style='font-size:58px;font-weight:900;line-height:1'>Switch to<br>Mushroom Mode</div><div class='bag' style='background:#fff;color:{O};margin-top:24px'>PAN'S</div></div></div>""", "Key visual concept; illustrative.")
V[12] = shot("demo", f"""<div class='h'>Mushroom Mode Demo Day</div><div style='background:{O};color:#fff;border-radius:16px;padding:16px;font-size:34px;font-weight:900;text-align:center'>SWITCH TO MUSHROOM MODE</div>
<div style='display:flex;gap:16px;justify-content:center;margin:26px 0'>{''.join("<div style='width:60px;height:70px;background:#fff;border:3px solid "+O+";border-radius:0 0 18px 18px'></div>" for _ in range(6))}</div>
<div style='background:{D};height:150px;border-radius:12px;display:flex;align-items:center;justify-content:space-around;color:#fff'>
<div style='font-size:22px'>Free taste &rarr;</div><div style='background:#fff;color:{D};padding:16px;border-radius:10px;text-align:center'><div style='width:90px;height:90px;background:repeating-linear-gradient(45deg,#000 0 6px,#fff 6px 12px)'></div><b>$2 off 2 bags</b></div></div>
<p class='sub' style='margin-top:14px'>12 weekend shifts &middot; 6 test stores &middot; 200 samples per shift</p>""")
V[13] = shot("shelf", f"""<div class='h'>The Aisle Switch (proposed)</div><div style='background:#d9cfc4;border-radius:12px;padding:20px'>
{''.join(f"<div style='display:flex;gap:10px;border-bottom:8px solid #8a7a6a;padding:10px 0;align-items:flex-end'>{row}</div>" for row in [
"".join("<div class='bag' style='background:#5a4030;width:70px;height:95px;font-size:11px'>JACK LINK'S</div>" for _ in range(4)) + "<div class='bag' style='width:70px;height:95px'>PAN'S</div><div class='bag' style='width:70px;height:95px'>PAN'S</div>",
"".join("<div class='bag' style='background:#3d5a3a;width:70px;height:95px;font-size:12px'>CHOMPS</div>" for _ in range(5))])}
<div style='background:{O};color:#fff;padding:12px 16px;border-radius:8px;margin-top:10px;font-size:20px;font-weight:800'>Love jerky? Switch to Mushroom Mode. Scan: $2 off 2 bags</div></div>
<p class='sub' style='margin-top:12px'>Clip strip inside the meat-snack set at 6 test stores + shelf talker</p>""")
V[14] = shot("tiktok", f"""<div style='display:flex;gap:40px;align-items:center'><div class='phone'><div class='screen' style='background:#000;color:#fff;position:relative'>
<div style='display:flex;height:60%;gap:4px'><div style='flex:1;background:#5a4030;border-radius:10px;display:flex;align-items:center;justify-content:center'>A</div><div style='flex:1;background:{O};border-radius:10px;display:flex;align-items:center;justify-content:center'>B</div></div>
<p style='margin-top:12px;font-weight:800'>Blind taste-off: beef jerky vs. mushroom jerky</p><p style='margin-top:6px'>I did not expect this. #MushroomMode #ad</p><p style='margin-top:10px;color:{O}'>Find it at H-E-B &rarr;</p></div></div>
<div><div class='h'>Taste-Off + Founder's Table</div><div class='card' style='width:520px'><b>From: Michael Pan</b><p style='margin-top:6px'>Subject: I put my family recipe on Shark Tank. Now it's at H-E-B.</p><p class='sub' style='margin-top:6px'>Save $2 - Michael</p></div>
<p class='sub' style='margin-top:14px'>3 Texas creators &middot; store finder + code MUSHROOMMODE</p></div></div>""")
V[15] = shot("creative", f"""<div style='display:flex;gap:28px;align-items:center'><div class='phone'><div class='screen'><b>Pan's</b>
<div class='bubble'>Pan's: Mushroom Mode is at your H-E-B. Save $2 on 2 bags this week: pans.co/tx  Reply STOP to opt out.</div></div></div>
<div class='phone'><div class='screen'><b>Inbox</b><div class='bubble' style='background:#fdf3e8'><b>Michael Pan</b><br>I put my family recipe on Shark Tank. Now it's at H-E-B.<br><span style='color:#888'>Save $2 - Michael</span></div></div></div>
<div style='background:{O};color:#fff;border-radius:14px;padding:22px;width:300px'><div style='font-size:16px'>SHELF TALKER</div><div style='font-size:30px;font-weight:900;line-height:1.1;margin-top:8px'>Love jerky? Switch to Mushroom Mode.</div><div style='margin-top:12px;font-size:18px'>Scan: $2 off 2 bags</div></div></div>""")
V[16] = shot("gantt", f"""<div class='h'>45-day schedule</div><table><tr><th>Program</th>{''.join(f'<th>{w}</th>' for w in ['Oct-Nov','W1','W2','W3','W4','W5','W6','W7'])}</tr>
{''.join("<tr><td><b>"+n+"</b><br><span style='font-size:12px'>"+m+"</span></td>"+''.join(f"<td style='background:{O if i in on else '#fff'}'></td>" for i in range(8))+"</tr>" for n,m,on in [
('H-E-B sell-in','trade lead',[0]),('Aisle Switch + coupon','P2 · retail · O1/O2 · trade lead',[1,2,3,4,5,6,7]),('Demo Days','P2 · sampling · O1/O2 · field lead',[2,3,4,5,6]),
('Taste-Off','P1 · TikTok · O1/O3 · social lead',[2,3,4,5]),("Founder&#39;s Table",'P1 · email/SMS · O1/O3 · CRM lead',[1,3,5,7]),('Retargeting + last chance','P1/P2 · paid/SMS · O1 · paid lead',[4,5,6,7])])}</table>""")
V[17] = shot("budget", f"""<div class='h'>Budget: $10,000</div><div style='display:flex;gap:20px'><table style='flex:1'><tr><th>Line</th><th>$</th></tr>
{''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a,b in [('Paid social','4,000'),('Creators (3 x $750)','2,250'),('Demo Days (12 x $200)','2,400'),('Production','700'),('Tools','300'),('Contingency','350'),('<b>Total</b>','<b>10,000</b>')])}</table>
<div style='flex:1'><table><tr><th>Case</th><th>Purchases</th><th>Gross profit</th><th>ROI</th></tr><tr><td>Base</td><td>1,500</td><td>$15.1K</td><td><b>+51%</b></td></tr><tr><td>Conservative</td><td>750</td><td>$7.6K</td><td>-24%</td></tr></table>
<div class='card' style='margin-top:14px'>Break-even: <b>993 purchases</b><br>ROAS: <b>4.6x</b><br>Upside: ~480 demo-day purchases</div></div></div>""", "Costs are labeled agency estimates; see notes.")
V[18] = shot("kpi", f"""<div class='h'>KPI dashboard</div><table><tr><th>Obj</th><th>KPI</th><th>Baseline</th><th>Target</th><th>Tool</th><th>Cadence</th></tr>
<tr><td>O1</td><td>Attributed purchases</td><td>0</td><td>1,500</td><td>Coupon + Shopify codes</td><td>Weekly</td></tr>
<tr><td>O1</td><td>Units/store/week vs. control</td><td>&le; ~6</td><td>+25%</td><td>Retailer data</td><td>Weekly</td></tr>
<tr><td>O2</td><td>Samples / claims</td><td>0</td><td>2,400 / 6,000</td><td>Tally + coupon platform</td><td>Weekly</td></tr>
<tr><td>O3</td><td>Impressions / aided awareness</td><td>Week-0 survey</td><td>1.0M / +10 pts</td><td>Ads Manager + brand-lift survey</td><td>Weekly / pre-post</td></tr></table>
<div class='card' style='margin-top:16px'><b>Trigger:</b> under 20 QR scans per shift by week 3 &rarr; move demos to top 3 stores</div>""")
V[19] = shot("why", f"""<div style='margin:-28px;height:760px;background:{D};color:#fff;padding:50px'><div style='font-size:20px;color:{O}'>WHY IT MATTERS</div>
<div style='font-size:40px;font-weight:900;line-height:1.15;margin:14px 0 30px'>Pan's doesn't need more stores.<br>It needs more bags sold per store.</div>
<div style='display:flex;gap:20px'>{''.join(f"<div style='background:#fff;color:{D};border-radius:14px;padding:18px;flex:1'><div class='big'>{a}</div><div>{b}</div></div>" for a,b in [('1,500','attributed purchases'),('+51%','profit ROI'),('+25%','units/store vs. control')])}</div>
<p style='margin-top:26px;font-size:18px'>A family recipe from Malaysia, honest about what it is - kept on Texas shelves because Texans tried it.</p></div>""")

p = RUN / "deck.json"
d = json.load(open(p))
for s in d["slides"]:
    if s["n"] in V:
        s.setdefault("visual", {})["file"] = V[s["n"]]
        if s["visual"].get("type") == "none":
            s["visual"]["type"] = "image"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
print(len(V), "visuals")
