# IMCP Product Shortlist — Top 20 Candidates

**Method:** Scored 1.9M Shopify stores (`shopify_master_list.csv`, exported 2026-07-20) through a 5-part rubric mapped to the official IMCP judging form, filtered to emerging consumer-product brands (2k–400k monthly visits), deduplicated, then manually researched the top candidates.

**Important caveat:** the dataset's social/sales fields are ~95% empty, so "marketing whitespace" was verified manually for Tier 1–2 picks rather than algorithmically. Tier 3 candidates are algorithmic picks that still need verification.

## Rubric (what IMCP judges reward → dataset proxy)

| IMCP judging category | Dataset proxy |
|---|---|
| Business opportunity / real product | Active store, ≥3 products, real traffic |
| Target market fit | Consumer category keywords (food, beauty, pet, stationery…) |
| Research-able problem | Traffic band 15k–250k = established but not saturated |
| Creative samples possible | Visually demo-able consumer goods |
| Financial viability | Traffic + catalog size signals |

## Tier 1 — Verified, strongest angles

| # | Brand | Why it could win |
|---|---|---|
| 1 | **tinyB chocolate** (tinybchocolate.com) | Artisan Brazilian brigadeiro bars, handmade small-batch, gluten-free. Founder story is genuinely moving (mother's survival kitchen → Bay Area). ~15k monthly visits = near-zero awareness = pure whitespace. Campaign: "the candy that crossed an ocean" sampling + immigrant-story content. Risk: very small company. |
| 2 | **Candycopia** (candycopia.com) | Oak Park/Elmhurst IL candy store + DTC. Killer experiential hook: customers **build their own gummy mix** from 200+ candies, plus curated small-batch/different-owned makers. 296k visits on a tiny team = demand > marketing. Campaign: UGC "candy bar" challenge, custom-mix subscriptions, local discovery angle. |
| 3 | **Snack Hawaii** (snackhawaii.com) | Family biz (6 employees) selling authentic Hawaiian snacks — Li Hing Mui, Ahi jerky they *invented*. ~230k monthly visits but ~88 LinkedIn followers = glaring whitespace. Campaign: "taste of Hawaii" tourism + foodie angle, airport/travel retail push. Risk: niche/regional product. |
| 4 | **People's Choice Beef Jerky** (peopleschoicebeefjerky.com) | 96-year-old family recipe, 4 generations, handmade in LA. Heritage-craft story vs. mass-market jerky. 214k visits, tiny team. Campaign: "since 1929" authenticity, big-slab format differentiation. Risk: jerky is a crowded category. |
| 5 | **Boba Tea Protein** (bobateaprotein.com) | Functional bubble tea — protein + fun drink for Gen Z. 133k visits, 2–10 employees. If marketing is weak (needs verification), this is a perfect "attention gap" pick: inherently TikTok-able product, functional trend, low sophistication. |

## Tier 2 — Solid, needs verification

| # | Brand | Notes |
|---|---|---|
| 6 | **Cha Cha Matcha** | 7 matcha cafes expanding into DTC kits + international. Matcha wellness wave. But they're already executing a growth plan — whitespace is moderate. |
| 7 | **Stellar Snacks** | Vegan pretzel braids, mother-daughter brand, artist-collab bags, ~18k retail doors. Great brand — but already doing Sprouts launches and PR; less whitespace. |
| 8 | **The Penny Candy Store** | Vintage penny candy, 1,211 products, 246k visits, 1 employee bucket — nostalgia + discovery play. Verify brand quality. |
| 9 | **Sweet Candy Company** | 231k visits, candy. Unverified — needs research. |
| 10 | **Pan's Mushroom Jerky** | Mushroom-based jerky = functional snacking trend. 49k visits = whitespace. Small catalog (23 products). |
| 11 | **Torrone Candy** | Italian torrone confections, 530 products, literally 1 employee. Novel import angle; verify it's a real operating brand. |
| 12 | **Matchaful** | Matcha brand, 97k visits. Matcha trend tailwind; unverified marketing state. |

## Tier 3 — Backups (algorithmic picks, verify before committing)

| # | Brand | Notes |
|---|---|---|
| 13 | **Liberty Puzzles** | Heirloom wooden jigsaw puzzles ($85–225), great story, but demo skews older/affluent — weaker Gen Z fit. |
| 14 | **Ujicha Matcha** | Uji, Japan matcha; 344 products; small. |
| 15 | **Kringle Candle Company** | Candles, 850 products, 194k visits; crowded category. |
| 16 | **Blooms Candy & Soda Pop Shop** | Vintage candy/soda, 855 products, 137k visits. |
| 17 | **Dayton Homemade Chocolates** | Local Ohio chocolate + gifts, micro team, 24k visits. |
| 18 | **Savannah's Candy Kitchen** | Candy kitchen, 156k visits, 51–200 emp — verify size/marketing. |
| 19 | **Kultura Filipino** | Filipino food products, 1,016 products, 220k visits; ethnic niche. |
| 20 | **Verve Coffee Roasters** | SF roaster, 244k visits — probably too established/known; included as benchmark. |

## Benchmark: Mid-Day Squares (user's original pick)

Would likely score Tier 2 — strong brand/story but already marketing-sophisticated (founder-led social IS their strategy), making whitespace harder. The shortlist above optimizes for the "fixable marketing problem" criterion that separates exemplary campaigns.

## Recommended next steps

1. **Deep-verify Tier 1 (#1–5)**: check their Instagram/TikTok activity, existing campaigns, retail presence — confirm the whitespace is real
2. **Check DECA rules**: confirm product must be a *retail* product and whether international brands qualify
3. **Pick one, then build the campaign** — the product matters less than the angle; all Tier 1 picks have a defensible "problem → campaign" story

## Files

- `score.py` — scoring pipeline (rerunnable on updated datasets)
- `data/shopify_master_list.csv` — 1.9M-store dataset (367MB)
- `data/stage1_scored.csv` — top 2,000 stage-1 scores
- `data/emerging_pool.csv` — 950 emerging-brand candidates
- `data/shortlist.csv` — this shortlist in table form
