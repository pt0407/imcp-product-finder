# IMCP Winner Formula (Hypothesis v1)

**Read this first:** the winner formula below is built from **3 winning decks**. That is too few to prove a formula. Treat the weights as a working hypothesis to test as more decks come in. The judgment-coded features are my reading of the decks, with evidence in `deck_codebook.csv`.

---

## 1. Data inventory

| Dataset | Size | Source | Status |
|---|---|---|---|
| Winning IMCP pitch decks | **3** (1st, 2nd, 3rd place) | Your files | Coded: `imcp_pitch_decks_measured.csv`, `deck_codebook.csv` |
| Score sheet (13 criteria, 3rd place) | 1 team | Your image | Used for criteria weights |
| DECA written-format reference (2021) | 1 (not a pitch deck) | Your file | Excluded, different format |
| Public winning decks | 0 found | Web search | DECA does not publish them |
| Business dataset (Shopify stores) | **1,005,954** active stores with traffic and ≥3 products | Shopify master list | `business_categories.csv`, `business_sample_by_category.csv` |
| Business sample for shortlists | 152 emerging brands across 19 categories | Derived | Stratified, 8 per category |

**What would make this real:** non-winning decks (for contrast), state-level placements, and your chapter's past entries. A formula needs losers as well as winners.

---

## 2. What the winners have in common (coded)

| Feature | 1st (StixFresh) | 2nd (MarkSetBot) | 3rd (Misfits) | Pattern |
|---|---|---|---|---|
| Unifying theme, mentions in deck | 13 | 8 | 11 | All three have one repeated theme |
| Named programs | 6 | 3 | 5 | Branded activations, not generic tactics |
| Named personas | 2 (Alice, Jason) | 0 (behavioral tiers) | 0 (named segments) | Named or segmented audience |
| Objective → metric → source table | yes | partial | yes | Metrics mapped to objectives |
| Itemized budget with revenue and ROI | summary only | **yes** | % split only | Only the 2nd place itemized |
| Audience-specific copy (SMS, email, posts) | partial | **yes** | partial | Only the 2nd place wrote scripts |
| Closing "why" slide | **yes** | not coded | no | Only the 1st place closed on mission |
| Visual creative (images) | 91 | 117 | 77 | All three show visuals |
| Named partner or executive target | partner | **exec + partner** | influencers | Partners add credibility |
| Projected ROI | 266% | 604% | 152% | Highest ROI did not win |

**Key observations (from the coding, not from any scoring model):**
1. **The theme is the strongest single signal.** All three decks repeat one phrase across every activity, which maps to criterion #6 (unifying theme).
2. **Higher projected ROI did not decide placement.** The 2nd-place deck had the most detailed budget and the highest ROI (604%) but placed below the 1st. Exam scores and presentation delivery also count, and we don't have those for the other teams. So deck features are one part of the score.
3. **Personas help, but segments can substitute.** The 1st place used named personas. The 2nd and 3rd used behavioral or named segments with demographic tables.
4. **Closing matters.** Only the 1st place ended on a "why" slide with the mission and projected results.

---

## 3. Creativity and uniqueness: the business side

Uniqueness is measured two ways:

**Category whitespace index** (computed on 1.0M active Shopify stores): demand per store, minus competitor saturation, z-scored across 19 categories. Higher = more demand with fewer competitors.

| Rank | Category | Stores | Median monthly visits | Whitespace index |
|---|---|---|---|---|
| 1 | Snacks / jerky | 1,607 | 423 | **4.10** |
| 2 | Functional beverages | 2,885 | 340 | 2.54 |
| 3 | Bakery / dessert | 3,469 | 328 | 2.19 |
| 4 | Toys / games / puzzles | 7,023 | 298 | 0.99 |
| 5 | Chocolate / candy | 5,373 | 256 | 0.93 |
| ... | Coffee / tea | 12,577 | 274 | 0.02 |
| ... | Apparel | 17,494 | 107 | -2.04 |
| 19 | Skincare / beauty | 26,807 | 113 | -2.52 |

**Limits of this index:** traffic numbers are third-party estimates, and keyword category matching is rough (for example, "bag" catches some unrelated stores). Treat it as a directional filter, not a measurement.

**What it says for our candidates:**
- **Snacks/jerky** (People's Choice, Snack Hawaii) sits at the top of the whitespace index.
- **Functional beverages** (Boba Tea Protein) is #2.
- **Chocolate/candy** (tinyB) is above average but not top.

**Originality (judgment):** Each deck needs one idea a competitor couldn't copy. The winners' examples were a branded challenge (#SaveWhatMatters, #BeAMisfit), a named event (Race for our Oceans), and a named trial program (Earth Day Trial Fleet).

---

## 4. The formula (100 points, hypothesis weights)

Weights follow the 13-criteria score sheet, where the largest swings between prelim and final were in originality (#11), key metrics (#10), and overview (#1). Each feature is scored 0–1 and multiplied by its weight.

| Component | Weight | Winner evidence | Scoring rule |
|---|---|---|---|
| Unifying theme (criterion #6) | 12 | 8–13 mentions in all 3 | 1.0 if one named theme appears in ≥ every activity slide |
| Named programs (criterion #3, #5) | 8 | 3–6 named | 1.0 at ≥5 named programs, linear below |
| Named personas or segments w/ demographics (criterion #4) | 10 | 3 of 3 | 1.0 if ≥2 segments, each with demographic and psychographic data |
| Objective → metric → source table (criterion #10) | 12 | 2 of 3 full, 1 partial | 1.0 if every objective maps to metric, target, and source |
| Itemized budget with revenue and ROI (criterion #9) | 12 | 2nd place | 1.0 if line items sum to total and revenue projection is given |
| Audience-specific copy (criterion #7) | 10 | 2nd place | 1.0 if SMS, email, or post copy is written out |
| Closing "why" slide (criterion #13) | 5 | 1st place | 1.0 if a mission slide with projected results is present |
| Visual creative samples (criterion #7) | 10 | 3 of 3 | 1.0 if ≥5 slides include mockup visuals |
| Named partner or executive target (criterion #2) | 6 | 1st and 2nd | 1.0 if a real partner or named decision-maker appears |
| Uniqueness (criterion #11) | 15 | All 3 | 50% from category whitespace index, 50% from judge-style originality rating (1–5) |

**Interpretation bands** (adapted from our rubric):
- 90–100: contender for a medal
- 80–89: strong finalist
- 70–79: viable, needs fixes
- < 70: below the winner pattern

---

## 5. Applying the formula to the tinyB deck

Scoring `decks/tinyb-borogodo-deck.md` against this formula:

| Component | Weight | tinyB draft | Points |
|---|---|---|---|
| Unifying theme | 12 | "Borogodó" on every activity slide | 12 |
| Named programs | 8 | 4 named (Borogodó Hour, #MyMomsBorogodó, creator seeding, Borogodó Letters) | 6.4 |
| Named segments w/ demographics | 10 | 2 named segments; primary has demographics table | 6 |
| Metrics table | 12 | Objective → metric → target → source | 12 |
| Itemized budget + revenue + ROI | 12 | Itemized; AOV and margin assumed, not verified | 8 |
| Audience copy | 10 | TikTok shot list, carousel copy, email subjects | 8 |
| Closing "why" slide | 5 | Slide 18 | 5 |
| Visual creative | 10 | Text and shot lists only | 3 |
| Named partner or exec | 6 | No named partner | 0 |
| Uniqueness | 15 | Chocolate category index 0.93 (mid); originality rated moderate | 7 |
| **Total** | **100** | | **~67.4** |

**What this says:** the tinyB draft is viable but below the winner pattern. The biggest gaps are:
1. **No visual mockups** (3/10). Build real mockups.
2. **No named partner or executive** (0/6). Get a real partner or decision-maker who could be named.
3. **Originality** (7/15). The challenge mechanic is good but not unusual enough. Also, chocolate sits mid-pack on whitespace, while snacks and beverages score higher.

---

## 6. Next data to collect (in priority order)

1. **Non-winning decks.** Even 5–10 would show what separates winners from losers.
2. **State-level and district winners** with their decks. This gives a second tier.
3. **Your chapter's past entries** and any feedback sheets. Feedback sheets show the judges' written comments.
4. **tinyB's actual sales data** (AOV, margin, order volume) to replace the assumptions in the budget.

---

## Files

- `code_decks.py`: measures slides, words, images, dollar figures, and theme repetition from the PDFs
- `imcp_pitch_decks_measured.csv`: measured features for the 3 winning decks
- `deck_codebook.csv`: judgment-coded features with evidence notes
- `business_whitespace.py`: category whitespace index on 1.0M Shopify stores
- `business_categories.csv`: 19 categories ranked by whitespace index
- `business_sample_by_category.csv`: 152 emerging brands, 8 per category
