#!/usr/bin/env python3
"""Harvest real brand imagery from the company's own website into run/webimg/.
Usage: python3 harvest_images.py <domain> <run_dir> [product_handles...]
Pulls CDN product/lifestyle images (Shopify products.js + homepage HTML)."""
import json, re, subprocess, sys, urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read()

def main(domain, run_dir, handles):
    out = Path(run_dir) / "webimg"; out.mkdir(exist_ok=True)
    urls = []
    # 1) Shopify products.js for given handles
    for h in handles:
        try:
            d = json.loads(get(f"https://{domain}/products/{h}.js"))
            for u in d.get("images", [])[:4]:
                urls.append(u if u.startswith("http") else "https:" + u)
        except Exception as ex:
            print("product fail", h, ex)
    # 2) homepage + collections HTML for cdn images
    for page in ["", "/collections/all"]:
        try:
            html = get(f"https://{domain}{page}").decode("utf-8", "ignore")
            for u in re.findall(r'https?://cdn\.shopify\.com/s/files/[^"\'\\\s]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"\'\\\s]*)?', html):
                urls.append(u.split("\\")[0])
        except Exception as ex:
            print("page fail", page, ex)
    seen, n = set(), 0
    for u in urls:
        if any(k in u.lower() for k in ("logo","icon","favicon","badge","payment","sprite","pixel","blank")): continue
        base = u.split("?")[0]
        if base in seen: continue
        seen.add(base)
        ext = base.rsplit(".",1)[-1].split("?")[0][:4]
        dest = out / f"web{n:02d}.{ext if ext in ('jpg','png','webp') else 'jpg'}"
        try:
            data = get(u)
            if len(data) < 20000: continue
            dest.write_bytes(data); n += 1
            if n >= 10: break
        except Exception: pass
    print(f"harvested {n} images -> {out}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
