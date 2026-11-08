# Prompt 00: Screen a candidate business (before building any deck)

**Role:** IMCP strategist deciding whether a business is worth a 20-slide deck.
**Read first:** `pipeline/KNOWLEDGE.md` §1 (business problem) and §13 (winner patterns).
**Input:** a business name (from `data/shortlist.csv` or fresh discovery).
**Output:** `pipeline/candidates/<slug>.md` with the scorecard below, plus a verdict.

Do NOT write a deck for a candidate that fails screening. Decks cost grading passes; screening is cheap.

## Scorecard (score each 1–5, cite evidence for every point above 3)

| # | Criterion | What a 5 looks like |
|---|---|---|
| 1 | **Structural problem** | One specific, evidenced problem: channel concentration, falling revenue, distribution-without-velocity, pricing gap, seasonal cliff. Public numbers prove it (filings, investor briefs, store counts vs. revenue). |
| 2 | **Product clarity** | A judge understands the product in 5 seconds and wants to try it. |
| 3 | **Public evidence** | ≥5 citable sources with publisher+date: revenue, growth, distribution, founder story, reviews. |
| 4 | **Research feasibility** | The team can collect real data in ≤1 week without company permission: reachable customers, a store to visit, public reviews, community access. |
| 5 | **Campaign measurability** | A 45-day campaign with a countable outcome (sell-through, trial signups, redemption rate) and a plausible test/control or promo-code measurement. |
| 6 | **Budget realism** | A credible campaign budget exists at $5K–$75K with identifiable line items. |
| 7 | **Whitespace** | Competitors are not already running this exact campaign. The brand's own assets (existing audience, retail relationships) make the idea ownable. |
| 8 | **Judge appeal** | Texas/District-5 relevance or a broadly relatable product. Avoid luxury/niche B2B unless the story is exceptional. |

## Verdict rules
- **Build it** if total ≥ 30/40 AND criterion 1 ≥ 4 AND criterion 4 ≥ 3.
- **Maybe** if 26–29: only proceed if no better candidate exists.
- **Skip** if < 26, or if the only problem you can name is "low awareness," or if every fact requires the company to reply before research can start.

## Required sections in candidates/<slug>.md
1. Scorecard table with evidence URLs.
2. The one-sentence business problem.
3. The campaign angle you would test first (name it; don't write the deck).
4. Top 3 open questions for the company or the team.
5. Verdict + reasoning in 3 sentences.

## Hard rules
- Verify every number on the public web before scoring. Search summaries are not sources; open the page.
- Prefer businesses where the problem is provable *without* the company: SEC/regulatory filings, investor briefs, press coverage, review counts, store locators.
- Flag any candidate whose claims look inflated (e.g., "10,000+ five-star reviews" — check the actual review page).
