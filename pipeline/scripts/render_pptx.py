#!/usr/bin/env python3
"""Render deck.json -> polished .pptx (16:9) with branded layouts, native charts, images, speaker notes."""
import json, sys, re
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

SECTION_LABELS = {
    "cover":"","title":"","toc":"Agenda","overview":"Overview","description":"The Business",
    "objectives":"Objectives","target_market":"Target Market","research":"Research",
    "strategy":"Strategy","budget":"Budget","impact":"Impact","bibliography":"Sources",
}

def rgb(hexstr):
    h = hexstr.lstrip('#')
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def add_textbox(slide, x, y, w, h, runs, size=18, color=None, bold=False, align=PP_ALIGN.LEFT, font="Calibri"):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.02)
    first = True
    for item in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.alignment = align
        text, b, sz, c = item if isinstance(item, tuple) else (item, bold, size, color)
        r = p.add_run(); r.text = text
        r.font.size = Pt(sz); r.font.bold = b; r.font.name = font
        if c: r.font.color.rgb = c
    return tb

def add_bullets(slide, x, y, w, h, bullets, size=16, color=None, gap_after=6):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    clean = lambda b: re.sub(r'\[(S|A|R|O|M|G)\d+\]', '', b).strip()
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap_after)
        # bold lead-in before first colon/dash
        m = re.match(r'^(.*?[.:—-])\s+(.*)$', clean(b), re.S)
        if m:
            r1 = p.add_run(); r1.text = "▪ " + m.group(1) + " "; r1.font.bold = True
            r1.font.size = Pt(size); r1.font.name = "Calibri"
            r2 = p.add_run(); r2.text = m.group(2); r2.font.size = Pt(size); r2.font.name = "Calibri"
        else:
            r = p.add_run(); r.text = "▪ " + clean(b); r.font.size = Pt(size); r.font.name = "Calibri"
        for r in p.runs:
            if color: r.font.color.rgb = color
    return tb

def add_image(slide, path, x, y, w, h):
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))

def placeholder_box(slide, x, y, w, h, desc, brand):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(brand + "22") if len(brand)==7 else RGBColor(0xEE,0xEE,0xEE)
    sh.line.color.rgb = rgb(brand)
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "VISUAL\n" + desc[:120]; r.font.size = Pt(13); r.font.color.rgb = rgb(brand)
    return sh

def add_chart(slide, x, y, w, h, deck):
    b = deck.get("budget", {})
    lines = b.get("lines", [])
    if not lines: return
    cd = CategoryChartData()
    cd.categories = [l["item"][:28] for l in lines]
    cd.add_series("USD", [l["usd"] for l in lines])
    gf = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.has_legend = False
    ch.font.size = Pt(11)
    plot = ch.plots[0]; plot.gap_width = 60
    ser = plot.series[0]
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = rgb(deck["meta"].get("brand_color","#333333"))

def render(deck_path):
    deck = json.load(open(deck_path))
    run_dir = Path(deck_path).parent
    meta = deck["meta"]; brand = meta.get("brand_color","#1f4e79")
    prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    dark, light = rgb(brand), RGBColor(0x1d,0x1d,0x1f)
    WHITE = RGBColor(0xFF,0xFF,0xFF)

    for s in deck["slides"]:
        sl = prs.slides.add_slide(blank)
        sec, n = s["section"], s["n"]
        bullets = s.get("bullets", [])
        if sec == "bibliography" and not bullets:
            bullets = [f"{src['publisher']}. '{src['title']}' {src.get('date','')}. {src.get('url','')}" for src in deck.get("sources",[])]
        v = s.get("visual") or {}
        img = run_dir / v["file"] if v.get("file") else None
        has_img = img and img.exists()

        if sec == "cover":
            bg = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid(); bg.fill.fore_color.rgb = dark; bg.line.fill.background()
            bg.shadow.inherit = False
            add_textbox(sl, 0.8, 2.2, 8.5, 1.2, [(s.get("title",""), True, 54, WHITE)])
            add_textbox(sl, 0.8, 3.5, 8.5, 2.0, [(b, False, 24, WHITE) for b in bullets])
            add_textbox(sl, 0.8, 6.6, 8.5, 0.5, [(f"{meta.get('school','')}  •  {meta.get('campaign_name','')}", False, 16, WHITE)])
            if has_img: add_image(sl, img, 9.3, 1.4, 3.4, 4.7)
            if s.get("notes"): sl.notes_slide.notes_text_frame.text = s["notes"]
            continue

        if sec in ("toc","title"):
            add_textbox(sl, 0.7, 0.5, 10, 0.5, [(SECTION_LABELS.get(sec,"Overview"), False, 14, dark)], bold=True)
            add_textbox(sl, 0.7, 1.0, 11.9, 0.9, [(s.get("title",""), True, 40, light)])
            if bullets:
                add_bullets(sl, 0.9, 2.0, 11.5, 4.8, bullets, size=20)
            if s.get("notes"): sl.notes_slide.notes_text_frame.text = s["notes"]
            continue

        # standard content slide: kicker + title, bullets left, visual/chart right
        add_textbox(sl, 0.6, 0.35, 10, 0.35, [(SECTION_LABELS.get(sec,""), False, 13, dark)], bold=True)
        add_textbox(sl, 0.6, 0.68, 12.1, 0.75, [(s.get("title",""), True, 30, light)])
        line = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.38), Inches(12.1), Pt(2.5))
        line.fill.solid(); line.fill.fore_color.rgb = dark; line.line.fill.background(); line.shadow.inherit = False

        if sec == "budget" and deck.get("budget",{}).get("lines"):
            add_bullets(sl, 0.6, 1.6, 6.6, 5.3, bullets, size=15)
            add_chart(sl, 7.5, 1.8, 5.3, 4.6, deck)
        elif sec == "bibliography":
            add_bullets(sl, 0.6, 1.6, 12.1, 5.3, bullets, size=13, gap_after=4)
        else:
            bw = 6.4 if (v.get("type") != "none" or has_img) else 11.9
            add_bullets(sl, 0.6, 1.6, bw, 5.3, bullets, size=15)
            rx = 7.3 if bw < 8 else 12.1
            rw = 5.4 if bw < 8 else 0
            if v.get("type") == "chart" or (sec == "impact" and v.get("type") != "none"):
                if sec == "budget": add_chart(sl, rx, 1.8, rw, 4.6, deck)
                else: placeholder_box(sl, rx, 1.7, rw, 4.6, v.get("desc","chart"), brand)
            elif has_img:
                add_image(sl, img, rx, 1.6, rw, 4.9)
            elif v.get("type") != "none":
                placeholder_box(sl, rx, 1.7, rw, 4.6, v.get("desc","visual needed"), brand)
        if s.get("notes"): sl.notes_slide.notes_text_frame.text = s["notes"]

    out = run_dir / "deck.pptx"
    prs.save(out)
    print("Wrote", out)

if __name__ == "__main__":
    render(sys.argv[1])
