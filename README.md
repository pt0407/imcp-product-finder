# IMCP Product Finder

Automated pipeline for DECA **Integrated Marketing Campaign–Product (IMCP)**: find real businesses, research them, generate judge-pleasing campaign decks, grade them harshly against the official rubric, and iterate.

Built for District 5 / ICDC-level prep. Everything runs locally with `python3` + `pandas`/`numpy` + Chrome (for PDF/screenshot rendering).

## Repo layout

```
data/
  shopify_master_list.csv      ~1.9M Shopify stores (domain, name, visits, followers, tags...)
  stage1_scored.csv            top 2,000 stores scored by stage-1 formula
  emerging_pool.csv            emerging-brand pool
  shortlist.csv                human-ranked candidates
  nonfood_pool.csv             non-food category filter output
dataset/
  business_sample_by_category.csv  153 curated emerging brands across 19 categories
  business_whitespace.py           re-sample the master list by category
  FORMULA.md                      how the master list was built
pipeline/
  RUNBOOK.md                  master instructions for the agent loop
  KNOWLEDGE.md                marketing knowledge + winner patterns (READ FIRST)
  rubric.json                 official 2026-27 evaluation form + harsh grading caps
  prompts/                    00_screen, 01_brief, 02_generate, 03_grade, 04_revise
  tools/                      review fetchers + analyzer (see below)
  scripts/                    check_deck, render, make_visuals, new_run, score, calibrate
  candidates/                 per-business scorecards
  research/                   review analyses, shelf audits
  runs/vNN/                   deck variants (deck.json/html/pdf/md + grades)
  leaderboard.csv             ranked results
  team.json                   school/participants/date (fill in before submitting)
decks/, campaigns/            earlier one-off research and decks
score.py                      stage-1 store scorer
```

## Part 1 — Finding businesses (the main job)

Goal: real product companies with a **structural marketing problem** — traction in one channel but weak in another — that a team can demo and research.

### Step A: start from the curated sample

`dataset/business_sample_by_category.csv` — 153 emerging brands (~130–250K monthly visits) across 19 categories: snacks, beverages, bakery, toys/games, chocolate, coffee/tea, sauces, supplements, skincare, fragrance, apparel, footwear/jewelry, pet, home/candle, outdoor/fitness, baby/kids, tech accessories, stationery, gifts.

### Step B: expand the pool

```bash
# Re-sample N stores per category from the 1.9M master list
python3 dataset/business_whitespace.py            # writes dataset/business_sample_by_category.csv

# Score the top of the master list (stage-1 formula: viability, whitespace, demo-fit)
python3 score.py                                  # writes data/stage1_scored.csv
```

### Step C: vet a candidate (30 min each)

For each promising domain:

1. **Check it has a review corpus** (this powers the Research rubric section — 15 pts):

```bash
# Judge.me (most common on Shopify)
python3 pipeline/tools/fetch_reviews_judgeme.py <shop>.myshopify.com out.csv
# Stamped
python3 pipeline/tools/fetch_reviews_stamped.py <domain> out.csv
# Analyze whatever you got
python3 pipeline/tools/analyze_reviews.py out.csv
```

Find `<shop>.myshopify.com` by grepping the store's homepage HTML for `myshopify.com`. n≥100 reviews = strong; n≥30 usable; <30 = weak research base.

2. **Check the business problem**: declining sales, distribution-without-velocity, new retail launch with no awareness, rating gaps (Amazon vs. own site), or a real founder story. Avoid brands already marketing-sophisticated — no whitespace = weak deck.

3. **Demo-ability**: can the product be sampled/shown physically? Food, candles, toys, beauty, tech accessories all work.

4. **Write a scorecard** following `pipeline/prompts/00_screen.md` → `pipeline/candidates/<slug>.md`. Only "Build it" verdicts proceed.

### What makes a good IMCP candidate (winner patterns)

- Real company, real structural gap (not generic "increase awareness")
- 3–6 named programs possible, real partners nameable, a mission metric judges can picture
- Review corpus or reachable retail for primary research
- Product a team can buy, demo, and photograph

## Part 2 — Building a deck

Follow `pipeline/RUNBOOK.md` exactly. Short version:

```bash
python3 pipeline/scripts/new_run.py            # creates runs/vNN/
# write deck.json per prompts/02_generate.md (read KNOWLEDGE.md first)
python3 pipeline/scripts/check_deck.py runs/vNN/deck.json   # 0 errors required
python3 pipeline/scripts/make_visuals.py runs/vNN/deck.json # generates slide PNGs
python3 pipeline/scripts/render.py runs/vNN/deck.json       # html/pdf/md
# grade in a FRESH session with prompts/03_grade.md — never grade your own deck
```

## Hard rules

1. **Never fabricate data** — no invented reviews, survey results, prices, or partnerships. Unknowns become `[A#]` assumptions. Getting caught = disqualification.
2. **Fresh grading sessions** — the deck author never grades their own work.
3. **Scripts are truth** — check_deck.py owns penalties/finance/caps; don't hand-compute.
4. Research caps: no survey/interviews → Research category caps ~10/15. A real n≥30 survey or 3 interviews unlocks 11–15.

## Current leaderboard

| Run | Business | Campaign | Score |
|---|---|---|---|
| v11 | Stryve / Braav Biltong | It's Not Jerky | 85 |
| v13 | BEEST Snacks | Crunch, Verified | 82 |
| v09 | Pan's Mushroom Jerky | Switch to Mushroom Mode | 81 |
| v10 | All Y'Alls Foods | The Smarter Switch | 78 |
