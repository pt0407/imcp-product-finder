"""Shared helpers for the IMCP pipeline."""
import json
import re
from datetime import date
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
RUNS = PIPELINE / "runs"
RUBRIC = json.loads((PIPELINE / "rubric.json").read_text())
CATEGORY_KEYS = [c["key"] for c in RUBRIC["categories"]]
CATEGORY_MAX = {c["key"]: c["max"] for c in RUBRIC["categories"]}

# Official 2026-27 outline order. "appendix" optional.
SECTION_ORDER = ["cover", "title", "toc", "overview", "description", "objectives",
                 "target_market", "research", "strategy", "budget", "impact",
                 "bibliography", "appendix"]
REQUIRED_SECTIONS = [s for s in SECTION_ORDER if s != "appendix"]
SECTION_LABELS = {
    "overview": "I. Overview", "description": "II. Product & Company",
    "objectives": "III. Campaign Objectives", "target_market": "IV. Target Market",
    "research": "V. Research, Insights & Connection", "strategy": "VI. Strategy, Activities & Schedule",
    "budget": "VII. Proposed Budget", "impact": "VIII. Impact & Measurement",
    "bibliography": "IX. Bibliography", "appendix": "X. Appendix",
}

TAG_RE = re.compile(r"\[((?:[SARO]\d+)(?:\s*,\s*[SARO]\d+)*)\]")
NUMBER_RE = re.compile(
    r"\$\s?\d"                          # dollar amounts
    r"|\d+(?:\.\d+)?\s?%"               # percentages
    r"|\b\d{1,3}(?:,\d{3})+\b"          # 1,000-style numbers
    r"|\b\d+(?:\.\d+)?\s?[KMB]\b"       # 10K, 2.4M
    r"|\b(?!19\d\d\b|20\d\d\b)\d{4,}\b"  # 4+ digit numbers that are not years
    r"|\b\d+(?:\.\d+)?x\b"              # 3x multipliers
)
PLACEHOLDER_RE = re.compile(r"\[VERIFY|\bTBD\b|\bTODO\b|\{\{|\bXX+\b|lorem ipsum", re.I)


def load_json(path):
    return json.loads(Path(path).read_text())


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def slide_text(slide):
    parts = [slide.get("title", "")] + list(slide.get("bullets", []))
    return " ".join(p for p in parts if p)


def word_count(text):
    return len(re.findall(r"\b\w[\w'’-]*\b", text))


def tags_in(text):
    ids = []
    for group in TAG_RE.findall(text):
        ids += [t.strip() for t in group.split(",")]
    return ids


def campaign_days(window):
    start = date.fromisoformat(window["start"])
    end = date.fromisoformat(window["end"])
    return (end - start).days + 1


def finance(deck):
    """Funnel math -> revenue, gross profit, ROI (profit-based), ROAS, CAC, break-even."""
    b = deck.get("budget", {})
    p = b.get("projection") or {}
    total = b.get("total_usd") or 0
    needed = ["impressions", "ctr", "conversion_rate", "aov_usd", "gross_margin"]
    if not total or any(p.get(k) in (None, "") for k in needed):
        return None
    ad_spend = sum(l["usd"] for l in b.get("lines", []) if l.get("category") in ("media", "creators"))

    def case(factor):
        clicks = p["impressions"] * p["ctr"]
        orders = clicks * p["conversion_rate"] * factor
        revenue = orders * p["aov_usd"]
        gross = revenue * p["gross_margin"]
        return {
            "orders": round(orders),
            "revenue_usd": round(revenue),
            "gross_profit_usd": round(gross),
            "roi_profit_based": round((gross - total) / total, 3),
            "roas": round(revenue / ad_spend, 2) if ad_spend else None,
            "cac_usd": round(total / orders, 2) if orders else None,
        }

    return {
        "campaign_cost_usd": total,
        "ad_spend_usd": ad_spend,
        "break_even_orders": round(total / (p["aov_usd"] * p["gross_margin"])),
        "base_case": case(1.0),
        "conservative_case": case(b.get("conservative_factor", 0.5)),
    }
