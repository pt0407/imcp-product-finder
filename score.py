#!/usr/bin/env python3
"""
IMCP product scorer — stage 1 (dataset-level).

Scores Shopify stores on "chance of doing well in DECA IMCP" using proxy
signals available in the dataset. Stage 2 = manual research on top candidates.

Rubric (0-100), mapped to what IMCP judges reward:
  A. Business viability        25  - real product company, big enough to matter
  B. Marketing whitespace      30  - traction but weak social presence = fixable gap
  C. Target-demo fit           20  - Gen Z / millennial consumer categories
  D. Creative-sample ease      15  - visually demo-able consumer products
  E. Size sweet spot           10  - emerging brand, not saturated, not too small
"""

import pandas as pd
import numpy as np
import re
import sys

DATA = "data/shopify_master_list.csv"
OUT = "data/stage1_scored.csv"
TOP_N = 2000

# --- Category keyword scoring (demo fit + creative ease) ---------------------
# name/tags keyword -> (demo_fit 0-20, creative 0-15)
CATEGORY_KEYWORDS = {
    # high demo fit: Gen Z / millennial purchase categories
    "snack|candy|chocolate|protein bar|granola|jerky|coffee|matcha|tea ": (18, 14),
    "skincare|beauty|cosmetic|serum|moisturizer|lip|nail|fragrance|perfume|candle": (18, 13),
    "supplement|vitamin|collagen|protein|wellness|gut health|mushroom": (17, 11),
    "fitness|gym|yoga|activewear|athleisure|sportswear|workout": (16, 12),
    "apparel|clothing|streetwear|hoodie|sneaker|shoe|jewelry|accessor": (15, 12),
    "pet|dog|cat food|treat": (15, 13),
    "stationery|planner|journal|notebook|scrapbook|stickers": (15, 13),
    "toys|game|puzzle|collectible|figure|plush": (16, 14),
    "phone case|tech accessory|charger|earbud|gadget": (14, 13),
    "home|kitchen|cookware|bedding|decor|candle|soap": (13, 11),
    "sustainable|eco|vegan|zero waste|reusable|bamboo": (16, 10),
    "kids|baby|toddler": (14, 12),
    "food|sauce|spice|hot sauce|honey|syrup|drink|soda|kombucha|wine|beer": (16, 12),
    "book|author|magazine": (10, 9),
    "wedding|event|party": (12, 10),
    # lower fit: industrial/B2B-ish or weak demo
    "industrial|machinery|equipment|wholesale|b2b|bulk|parts|supplies": (4, 4),
    "fabric|textile|leather hide|raw material": (3, 4),
    "software|saas|digital|course|ebook|download|template": (2, 2),
    "real estate|property|insurance|finance|legal": (2, 3),
}
CATEGORY_RES = [(re.compile(p, re.I), v) for p, v in CATEGORY_KEYWORDS.items()]


def category_scores(text):
    """Return (demo_fit, creative) best-match scores."""
    best_demo, best_creative = 6, 6  # neutral baseline
    for rx, (d, c) in CATEGORY_RES:
        if rx.search(text):
            if d > best_demo:
                best_demo, best_creative = d, c
    return best_demo, best_creative


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def inum(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return 0


def score_chunk(df):
    # text for category match
    text = (df["merchant_name"].fillna("") + " " + df["tags"].fillna("")).str.lower()
    cat = text.map(category_scores)
    df["demo_fit"] = [c[0] for c in cat]
    df["creative"] = [c[1] for c in cat]

    monthly_sales = df["estimated_monthly_sales"].map(fnum)
    yearly_sales = df["estimated_yearly_sales"].map(fnum)
    visits = df["estimated_monthly_visits"].map(fnum)
    ig = df["instagram_followers"].map(lambda x: fnum(x) or 0)
    tt = df["tiktok_followers"].map(lambda x: fnum(x) or 0)
    social = ig.fillna(0) + tt.fillna(0)
    products = df["products_sold"].map(inum)
    avg_price = df["average_product_price"].map(fnum)

    # ---- A. Business viability (25) ----
    # proxy: monthly visits or sales present; sweet revenue band
    has_signal = visits.notna() | monthly_sales.notna() | yearly_sales.notna()
    sales_proxy = monthly_sales.fillna(0) + visits.fillna(0) / 50  # rough $/visit
    viability = np.select(
        [
            sales_proxy >= 500_000,          # too big? still viable but saturated
            sales_proxy >= 100_000,
            sales_proxy >= 25_000,
            sales_proxy >= 5_000,
            sales_proxy > 0,
        ],
        [22, 25, 20, 14, 8],
        default=0,
    )
    viability = pd.Series(viability, index=df.index)
    viability = viability.where(has_signal, 0)
    # product catalog depth bonus
    viability += np.select([products >= 20, products >= 5], [3, 1.5], default=0)

    # ---- B. Marketing whitespace (30) ----
    # high business signal + LOW social following = gap a campaign can fix.
    # some social presence = channel viability.
    whitespace = np.zeros(len(df))
    biz = sales_proxy.fillna(0)
    # normalize social: log scale; brands with <5k followers have whitespace
    social_log = np.log10(social + 1)
    biz_log = np.log10(biz + 1)
    # whitespace peaks when biz is decent but social is small
    whitespace = np.clip((biz_log - 3.5) * 12 - np.clip(social_log - 3.5, 0, 6) * 4, 0, 30)
    # note: social==0 usually means missing data, not zero presence -> neutral, no bonus
    whitespace = pd.Series(whitespace, index=df.index)

    # ---- E. Size sweet spot (10) ----
    # emerging: monthly sales roughly $10k-$500k, or visits 5k-200k
    sweet = np.select(
        [
            (monthly_sales >= 10_000) & (monthly_sales <= 500_000),
            (monthly_sales > 500_000),
            (monthly_sales > 0) & (monthly_sales < 10_000),
            visits >= 5_000,
        ],
        [10, 6, 4, 7],
        default=0,
    )
    sweet = pd.Series(sweet, index=df.index)

    df["score_viability"] = viability.clip(0, 25)
    df["score_whitespace"] = whitespace.clip(0, 30)
    df["score_demo"] = df["demo_fit"] * 1.0  # already ~0-20 scaled? rescale below
    df["score_creative"] = df["creative"] * 1.0
    df["score_sweetspot"] = sweet.clip(0, 10)

    # rescale demo (0-20 max ~18) and creative (0-15 max ~14) to their caps
    df["score_demo"] = (df["demo_fit"] / 18 * 20).clip(0, 20)
    df["score_creative"] = (df["creative"] / 14 * 15).clip(0, 15)

    df["stage1_score"] = (
        df["score_viability"] + df["score_whitespace"] + df["score_demo"]
        + df["score_creative"] + df["score_sweetspot"]
    ).round(1)
    return df


def main():
    keep_cols = [
        "domain", "merchant_name", "status", "estimated_monthly_sales",
        "estimated_yearly_sales", "estimated_monthly_visits", "average_product_price",
        "products_sold", "employee_count_bucket", "instagram_followers",
        "tiktok_followers", "tags",
    ]
    chunks = []
    scored_chunks = []
    total = 0
    for chunk in pd.read_csv(DATA, chunksize=200_000, low_memory=False):
        total += len(chunk)
        chunk = chunk[keep_cols].copy()
        # ---- eligibility tightened: emerging DTC brands only ----
        # cap traffic so mega-brands (already saturated, agency-saturated) are excluded
        chunk = chunk[
            (chunk["status"].str.lower() == "active")
            & (chunk["products_sold"].map(inum) >= 3)
            & (chunk["estimated_monthly_visits"].map(fnum) >= 2_000)
            & (chunk["estimated_monthly_visits"].map(fnum) <= 400_000)
        ]
        chunk = score_chunk(chunk)
        scored_chunks.append(chunk.nlargest(min(500, len(chunk)), "stage1_score"))
        if total % 400_000 < 200_000:
            print(f"processed {total:,} rows...", file=sys.stderr)

    all_scored = pd.concat(scored_chunks).nlargest(TOP_N, "stage1_score")
    all_scored.to_csv(OUT, index=False)
    print(f"\nDone. Scored pool -> top {len(all_scored)} written to {OUT}")
    print(all_scored.head(20)[["merchant_name", "domain", "stage1_score",
                               "estimated_monthly_sales", "estimated_monthly_visits",
                               "instagram_followers", "tiktok_followers"]].to_string())


if __name__ == "__main__":
    main()
