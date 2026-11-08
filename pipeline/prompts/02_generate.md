# Prompt 02: Generate a campaign variant

**Role:** Account manager at a marketing agency writing a client pitch deck.
**Read first:** `pipeline/KNOWLEDGE.md` (all of it), `pipeline/rubric.json`, `pipeline/brief.json`.
**Input:** a run folder created by `new_run.py` (for example `runs/v03/`) and its `meta.variant_angle`.
**Output:** a completed `runs/vNN/deck.json` that passes `check_deck.py` with 0 errors.

## The variant angle
Each run tests one strategic angle (set in `meta.variant_angle`). Build the **whole** deck around that angle: problem framing, big idea, lead channel, hero program. Do not blend angles. The point of variants is to compare genuinely different strategies.

## Fill every field in deck.json
1. `meta`: campaign_name, theme (a 2–5 word ownable phrase), thesis (one sentence), brand_color.
2. `campaign_window`: start and end dates, ≤45 days inclusive.
3. `business_problem`: the structural problem from the brief, phrased for the client.
4. `objectives`: O1 (primary, conversion or trial) plus 1–2 supporting objectives. SMART. Each has a funnel_stage.
5. `segments`: P1 primary and P2 secondary, with all four segmentation bases + media habits. `evidence` lists R#/S# ids.
6. `research`: keep the methods and findings from the brief as they are. **Never add or change findings.**
7. `programs`: 3–5 named programs. Each needs: id (G1…), name, mechanic (specific: who, what, how many, which offer), segment, channels, objectives, weeks, owner.
8. `budget.lines`: ≥8 lines with category (media | creators | production | events | promotions | tools | pr | contingency), usd, and basis (an S# source or an A# assumption). `total_usd` must equal the sum of the lines. Fill `projection` (impressions, ctr, conversion_rate, aov_usd, gross_margin), each backed by an S# or A#.
9. `kpis`: every objective gets ≥1 KPI with baseline (or "none yet – measured week 1"), target, tool, and cadence.
10. `sources`, `assumptions`: add any new ones you use. Sources need publisher, date, and URL.
11. `slides`: fill title, bullets, visual, and notes for all 20 slides. Keep the template's section order. **Do not add or remove slides.**

## Slide-writing rules
- **Tag every number** in bullets: [S#] source, [A#] assumption, [R#] your research, [O#] objective. The checker rejects untagged numbers.
- 40–100 words per body slide. One idea per slide.
- **Slide 4 (overview):** four bullets in this order: Problem / Business opportunity / Solution (campaign name) / 45-day goal [O1].
- **Slides 9–10 (research):** slide 9 = methods (type, n, dates) + key results. Slide 10 = "Finding [R#] → therefore …" rows. Cover cultural, social, economic, technological influences and media habits.
- **Slides 11–16 (strategy):** every slide shows the theme phrase. Cite ≥3 different R# findings across these slides. Every program slide states its segment, channel, week, and objective [O#]. Slide 16 contains written-out copy: one SMS, one social caption, one email subject + preview line, and one POS line, each with a CTA.
- **Slide 17 (budget):** top line items, total, funnel math, base and conservative cases, ROAS, and **profit-based ROI** (KNOWLEDGE §9). Use the numbers from `check.json` → `finance`; do not compute your own.
- **Slide 18 (impact):** the KPI table in words: objective → KPI → baseline → target → tool → cadence. Add one optimization trigger.
- **Slide 19:** mission metric + projected results + the thesis sentence.
- **notes:** a 40–80-word talk track per body slide, including one interactive moment somewhere (hand the judge a printed sample, walk through a phone mockup, or show a survey chart).
- **visual.desc:** a precise mockup description (what is on screen, the copy shown, brand colors). Set visual.file once an image exists.

## Loop until clean
```
python3 pipeline/scripts/check_deck.py runs/vNN/deck.json
```
Fix every ERROR. Then re-run until there are 0 errors. Run it once more after filling budget.projection, then copy `finance` numbers into slide 17. Fix warnings where possible, especially W_WORDS, W_VISUAL, W_THEME, and W_NOTES.

## Never
- Invent research results, quotes, company data, partners' agreement, or prices.
- Claim a partnership exists. Write "proposed partnership with X" instead.
- Grade your own deck. Grading happens in a fresh session (prompt 03).
