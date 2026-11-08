#!/usr/bin/env python3
"""Fetch all public Judge.me reviews for a Shopify store into a CSV (for review content analysis).

Usage: python3 fetch_reviews_judgeme.py <shop>.myshopify.com <out.csv> [max_pages=40]
Find <shop>.myshopify.com by searching the store's homepage HTML for "myshopify.com".
Uses the same public endpoint the store's own review widget calls. Polite: 1 request/sec.
"""
import csv
import html
import json
import re
import sys
import time
import urllib.request

API = "https://api.judge.me/reviews/all_reviews_js_based"
REV_RE = re.compile(r"<div class='jdgm-rev jdgm-divider-top'(.*?)(?=<div class='jdgm-rev jdgm-divider-top'|\Z)", re.S)


def field(pattern, text):
    m = re.search(pattern, text, re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip() if m else ""


def fetch(shop, page):
    url = f"{API}?url={shop}&shop_domain={shop}&platform=shopify&page={page}&per_page=50&review_type=all-reviews"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    shop, out = sys.argv[1], sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    rows, seen, page = [], set(), 1
    while page <= max_pages:
        data = fetch(shop, page)
        blocks = REV_RE.findall(data.get("html", ""))
        ids = {field(r"data-review-id='([^']+)'", b) for b in blocks}
        if not blocks or ids <= seen:
            break
        seen |= ids
        for b in blocks:
            rows.append({
                "review_id": field(r"data-review-id='([^']+)'", b),
                "rating": field(r"data-score='(\d)'", b),
                "date": field(r"data-content='([^']+)'", b) or field(r"jdgm-rev__timestamp[^>]*>(.*?)</span>", b),
                "verified": field(r"data-verified-buyer='(\w+)'", b),
                "title": field(r"jdgm-rev__title'?[^>]*>(.*?)</b>", b),
                "body": field(r"jdgm-rev__body'?[^>]*>(.*?)</div>\s*</div>", b),
                "product": field(r"jdgm-rev__prod-link[^>]*>(.*?)</a>", b),
            })
        print(f"page {page}: {len(blocks)} reviews (total {len(rows)})", file=sys.stderr)
        page += 1
        time.sleep(1)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} reviews to {out}")


if __name__ == "__main__":
    main()
