#!/usr/bin/env python3
"""Variety + uniqueness dataset from the 1.9M-store Shopify master list.

Uniqueness proxy (category level):
  demand_per_store = median monthly visits of active stores in the category
  saturation       = number of active stores in the category (log-scaled)
  whitespace_index = z(demand_per_store) - z(log10(saturation))
High index = proven demand with few competitors = room for a distinct campaign.

Store level: stratified sample (N per category) of emerging brands (15k-250k visits),
so the shortlist covers many categories rather than only coffee/tea.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent.parent / "data" / "shopify_master_list.csv"
OUT_DIR = Path(__file__).parent
PER_CATEGORY = 8

CATEGORIES = {
    "coffee_tea": r"coffee|tea\b|matcha|espresso|roast|chai",
    "chocolate_candy": r"chocolate|candy|candies|gummy|gummies|confection|sweet|truffle|brigadeiro",
    "snacks_jerky": r"snack|jerky|chips|crisp|pretzel|cracker|popcorn",
    "beverage_functional": r"drink|soda|kombucha|boba|juice|electrolyte|sparkling|seltzer",
    "supplements_wellness": r"supplement|vitamin|collagen|probiotic|wellness|protein|mushroom|adaptogen",
    "skincare_beauty": r"skin|beauty|cosmetic|serum|moisturi|lip|makeup|hair|nail",
    "fragrance": r"fragrance|perfume|cologne|parfum|scent",
    "apparel": r"apparel|clothing|shirt|hoodie|tee\b|streetwear|jacket|denim|sock",
    "footwear_accessories": r"shoe|sneaker|boot|sandal|jewel|bag|wallet|belt|hat\b|eyewear|sunglass",
    "pet": r"\bpet\b|dog|cat\b|kitten|puppy|treat",
    "home_decor_candle": r"candle|decor|home|kitchen|bedding|pillow|rug|lamp|vase",
    "toys_games_puzzles": r"toy|game|puzzle|plush|lego|board game|collectible",
    "stationery_hobby": r"stationery|planner|journal|notebook|sticker|craft|paint|art supplies|yarn|knit",
    "outdoor_fitness": r"outdoor|camp|hike|fitness|yoga|gym|bike|cycl|running|golf|surf|skate",
    "baby_kids": r"baby|kids|toddler|infant|nursery",
    "tech_accessories": r"phone case|charger|earbud|cable|tech|gadget|keyboard|speaker",
    "food_sauce_spice": r"sauce|spice|seasoning|honey|syrup|pantry|hot sauce|condiment|oil\b",
    "bakery_dessert": r"bakery|cookie|cake|brownie|pastry|dessert|ice cream",
    "gifts_novelty": r"gift|novelty|souvenir|keepsake|personalized",
}
ORDER = list(CATEGORIES)


def assign(text_series):
    out = pd.Series("other", index=text_series.index)
    for cat in reversed(ORDER):
        mask = text_series.str.contains(CATEGORIES[cat], regex=True, na=False)
        out[mask] = cat
    return out


def load():
    cols = ["domain", "merchant_name", "status", "estimated_monthly_visits", "products_sold", "tags"]
    frames = []
    for chunk in pd.read_csv(DATA, usecols=cols, chunksize=300_000, low_memory=False):
        chunk = chunk[(chunk["status"].astype(str).str.lower() == "active")
                      & chunk["estimated_monthly_visits"].notna()
                      & (chunk["products_sold"].fillna(0) >= 3)]
        if chunk.empty:
            continue
        text = (chunk["merchant_name"].fillna("") + " " + chunk["tags"].fillna("")
                + " " + chunk["domain"].fillna("")).str.lower()
        chunk = chunk.assign(category=assign(text))
        frames.append(chunk)
    return pd.concat(frames, ignore_index=True)


def category_table(df):
    g = df.groupby("category")
    t = pd.DataFrame({
        "stores": g.size(),
        "median_monthly_visits": g["estimated_monthly_visits"].median(),
        "share_emerging_15k_250k": g["estimated_monthly_visits"].apply(lambda s: s.between(15_000, 250_000).mean()),
    })
    t = t[t.index != "other"]
    z = lambda s: (s - s.mean()) / s.std()
    t["whitespace_index"] = (z(t["median_monthly_visits"]) - z(np.log10(t["stores"]))).round(2)
    return t.sort_values("whitespace_index", ascending=False).round(3)


def sample_stores(df):
    emerging = df[df["estimated_monthly_visits"].between(15_000, 250_000) & (df["category"] != "other")]
    return (emerging.sort_values("estimated_monthly_visits", ascending=False)
            .groupby("category", group_keys=False).head(PER_CATEGORY)
            .sort_values(["category", "estimated_monthly_visits"], ascending=[True, False]))


def main():
    df = load()
    print(f"active stores with traffic + >=3 products: {len(df):,}", file=sys.stderr)
    cats = category_table(df)
    cats.to_csv(OUT_DIR / "business_categories.csv")
    sample_stores(df)[["category", "domain", "merchant_name", "estimated_monthly_visits",
                       "products_sold", "tags"]].to_csv(OUT_DIR / "business_sample_by_category.csv", index=False)
    print(cats.to_string())


if __name__ == "__main__":
    main()
