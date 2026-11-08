#!/usr/bin/env python3
"""brandkit.py -- extract a business's real visual identity from its website.

Fetches the site, finds the primary stylesheet, pulls the dominant brand
colors, declared font families and logo image, downloads the logo, and
writes brand.json into the run dir:

  python3 brandkit.py ../runs/vNN/deck.json

render_imcp.py reads brand.json to theme each deck per its actual brand.
"""
import json, re, sys, urllib.request
from collections import Counter
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# curated display/body font pairings for Google-Fonts equivalents
PAIRINGS = {
    "bold-tech":      ("Archivo", "Inter"),
    "playful-pet":    ("Poppins", "Poppins"),
    "rugged-outdoor": ("Barlow Condensed", "Barlow"),
    "premium-minimal":("Space Grotesk", "Inter"),
    "editorial":      ("Fraunces", "Inter"),
    "generic":        ("Archivo", "Inter"),
}

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read() if binary else r.read().decode("utf-8", errors="replace")

def hex_colors(text):
    # skip near-whites/near-grays noise, keep saturated/dark brand tones
    out = Counter(re.findall(r"#[0-9a-fA-F]{6}\b", text))
    scored = []
    for c, n in out.items():
        c2 = c.lower()
        r, g, b = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
        mx, mn = max(r,g,b), min(r,g,b)
        sat = 0 if mx == 0 else (mx-mn)/mx
        lum = (0.299*r+0.587*g+0.114*b)/255
        if sat > .25 or lum < .25:  # colored OR genuinely dark
            scored.append((n, c))
    return [c for _, c in sorted(scored, reverse=True)]

def font_families(text):
    fams = Counter()
    for m in re.findall(r"font-family\s*:\s*([^;}\"']+)", text):
        for f in re.split(r",", m):
            f = f.strip().strip('"').strip("'")
            if f and "\\" not in f and "!" not in f and not f.startswith("var(") and f.lower() not in (
                "inherit","system-ui","sans-serif","serif","-apple-system",
                "blinkmacsystemfont","segoe ui","roboto","oxygen","ubuntu",
                "cantarell","fira sans","droid sans","helvetica neue"):
                fams[f] += 1
    return [f for f,_ in fams.most_common(8)]

def logo_url(home_html, base):
    # prefer explicit logo-named images
    for m in re.findall(r"(?:src|data-src|srcset)\s*=\s*[\"']([^\"']*(?:logo|Logo)[^\"']*?\.(?:png|svg|jpe?g|webp)[^\"']*)[\"']", home_html):
        u = m.split(" ")[0].replace("&amp;","&")
        if "next/image" in u:  # unwrap next/image proxy
            inner = re.search(r"url=([^&]+)", u)
            if inner: u = urllib.parse.unquote(inner.group(1))
        if u.startswith("//"): u = "https:" + u
        if u.startswith("/"): u = base.rstrip("/") + u
        return u
    return None

import urllib.parse

def main():
    deck_path = Path(sys.argv[1]).resolve()
    deck = json.loads(deck_path.read_text())
    run_dir = deck_path.parent
    site = deck["meta"].get("company_website") or deck["meta"].get("website") or ""
    if not site:
        sys.exit("deck meta has no company_website")
    if not site.startswith("http"): site = "https://" + site

    html = fetch(site)
    # grab first linked css bundle for more colors/fonts
    css_text = ""
    for href in re.findall(r'href="([^"]+\.css[^"]*)"', html)[:3]:
        u = href
        if u.startswith("//"): u = "https:" + u
        if u.startswith("/"): u = site.rstrip("/") + u
        if not u.startswith("http"): continue
        try: css_text += fetch(u) + "\n"
        except Exception: pass

    colors = hex_colors(html + "\n" + css_text)
    fonts  = font_families(html + "\n" + css_text)
    logo   = logo_url(html, site)

    brand = {
        "site": site,
        "primary":   colors[0] if colors else deck["meta"].get("brand_color","#1f4e79"),
        "secondary": colors[1] if len(colors)>1 else None,
        "accent":    colors[2] if len(colors)>2 else None,
        "palette":   colors[:8],
        "site_fonts": fonts[:5],
        "logo_url": logo,
    }

    # pick a font pairing: use brand's own Google-hosted font if present
    gfonts = [f for f in fonts if re.fullmatch(r"[A-Za-z ]+", f)]
    if gfonts:
        brand["display_font"], brand["body_font"] = gfonts[0], (gfonts[1] if len(gfonts)>1 else gfonts[0])
    else:
        brand["display_font"], brand["body_font"] = PAIRINGS["generic"]

    # download logo
    if logo:
        try:
            data = fetch(logo, binary=True)
            ext = ".svg" if logo.lower().endswith(".svg") or data[:5].lower().startswith(b"<svg") else ".png"
            (run_dir/("brand"+ext)).write_bytes(data)
            brand["logo_file"] = "brand"+ext
        except Exception as e:
            print(f"logo download failed: {e}")

    (run_dir/"brand.json").write_text(json.dumps(brand, indent=2))
    print(json.dumps(brand, indent=2))

if __name__ == "__main__":
    main()
