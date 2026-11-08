#!/usr/bin/env python3
"""Fetch public Stamped.io reviews for a Shopify store into a CSV (for review content analysis).

Usage: python3 fetch_reviews_stamped.py <store-domain e.g. stryve.com> <out.csv> [max_pages=40]
Uses the same public endpoint the store's review widget calls: stamped.io/api/reviews?shop=<domain>.
NOTE: observed corpora can be heavily 5-star-skewed (verified-purchase review programs).
Record that limitation in the deck. Polite: 1 request/sec.
"""
import csv
import sys
import time
import json
import urllib.request

API = "https://stamped.io/api/reviews"


def fetch(shop, page):
    url = f"{API}?shop={shop}&limit=100&page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: fetch_reviews_stamped.py <store-domain> <out.csv> [max_pages=40]")
    shop = sys.argv[1].replace("https://", "").replace("http://", "").strip("/")
    out = sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    rows = []
    for page in range(1, max_pages + 1):
        try:
            data = fetch(shop, page)
        except Exception as e:
            print(f"page {page}: error {e}", file=sys.stderr)
            break
        if not data:
            break
        for r in data:
            rows.append({
                "review_id": r.get("id", ""),
                "rating": r.get("reviewRating", ""),
                "date": (r.get("reviewDate") or r.get("dateCreated") or "")[:10],
                "verified": "yes" if r.get("verifiedBuyer") or r.get("reviewType") == 1 else "",
                "title": r.get("reviewTitle") or "",
                "body": r.get("reviewMessage") or "",
                "product": r.get("productName") or "",
            })
        print(f"page {page}: +{len(data)} (total {len(rows)})")
        if len(data) < 100:
            break
        time.sleep(1)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["review_id", "rating", "date", "verified", "title", "body", "product"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} reviews to {out}")


if __name__ == "__main__":
    main()
