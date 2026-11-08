#!/usr/bin/env python3
"""Review content analysis: code customer reviews into themes and print citable numbers.

Usage: python3 analyze_reviews.py <reviews.csv> [themes.json]
Input CSV needs a text column (body/text/review) and optionally rating, date, title.
Output: research/review_summary.md next to the CSV's parent 'research' folder (or beside the CSV).

Rules for the deck (enforced by the runbook, not this script):
- Only numbers printed here may appear in R# findings about reviews.
- State the method honestly: "content analysis of N public reviews, collected <date>, keyword-coded".
- Reviews skew positive (self-selected buyers). Say so as a limitation.
"""
import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

DEFAULT_THEMES = {
    "taste_flavor": ["taste", "flavor", "flavour", "delicious", "yummy", "tasty", "savory", "umami", "seasoning"],
    "texture_chew": ["texture", "chewy", "chew", "meaty", "tender", "crunchy", "mouthfeel", "mouth feel"],
    "health_clean": ["healthy", "clean", "ingredients", "guilt", "natural", "organic", "nutritious", "fiber"],
    "diet_vegan_veg": ["vegan", "vegetarian", "plant", "meatless", "dairy", "gluten"],
    "compared_to_meat": ["beef", "meat jerky", "real jerky", "like jerky", "regular jerky"],
    "price_value": ["price", "expensive", "pricey", "cost", "value", "worth", "cheap"],
    "found_in_store": ["store", "costco", "whole foods", "walmart", "h-e-b", "heb", "kroger", "sprouts", "target", "found it"],
    "repeat_bulk": ["again", "reorder", "re-order", "every month", "subscribe", "subscription", "stock up", "bags", "bulk", "favorite"],
    "gift_share": ["gift", "share", "family", "kids", "husband", "wife", "daughter", "son", "friend"],
    "complaint": ["too salty", "too sweet", "hard", "dry", "stale", "small bag", "disappoint", "didn't like", "not good", "bland"],
}


def text_col(row):
    for k in ("body", "text", "review", "content", "Review"):
        if row.get(k):
            return (row.get("title", "") + " " + row[k]).strip()
    return ""


def main():
    src = Path(sys.argv[1])
    themes = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else DEFAULT_THEMES
    rows = [r for r in csv.DictReader(open(src)) if text_col(r)]
    n = len(rows)
    if not n:
        sys.exit("no review text found")
    hits, quotes = Counter(), {t: [] for t in themes}
    ratings = Counter(r.get("rating", "") for r in rows if r.get("rating"))
    for r in rows:
        t = text_col(r).lower()
        for theme, kws in themes.items():
            if any(re.search(r"\b" + re.escape(k) + r"\b", t) for k in kws):
                hits[theme] += 1
                if len(quotes[theme]) < 3 and 40 < len(text_col(r)) < 220:
                    quotes[theme].append(text_col(r))
    rated = sum(ratings.values())
    avg = sum(int(k) * v for k, v in ratings.items() if k.isdigit()) / rated if rated else None

    out = src.parent / "review_summary.md"
    L = [f"# Review content analysis: {src.name}", "",
         f"- Method: keyword-coded content analysis of **n = {n}** public customer reviews",
         f"- Collected: {date.today().isoformat()} (record this date in deck.json research.methods)",
         f"- Average rating: {avg:.2f} / 5 (n = {rated})" if avg else "- Average rating: n/a",
         f"- Rating mix: " + ", ".join(f"{k}★ {v} ({v / rated:.0%})" for k, v in sorted(ratings.items(), reverse=True)) if rated else "",
         "- Limitation: reviewers are self-selected buyers; results skew positive and do not represent non-buyers.", "",
         "| Theme | Reviews mentioning | % of n |", "|---|---|---|"]
    for theme, c in hits.most_common():
        L.append(f"| {theme} | {c} | {c / n:.0%} |")
    L += ["", "## Verbatim quotes (use exactly as written)"]
    for theme, qs in quotes.items():
        for q in qs:
            L.append(f"- [{theme}] \"{q}\"")
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L[:14 + len(hits)]))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
