# IMCP Pipeline Runbook (for SWE-2 Flash)

You are running an automated loop that generates IMCP pitch-deck variants, checks them against DECA rules, grades them like a harsh ICDC judge, and revises the best one. Scripts handle everything mechanical. You handle writing and grading by following the prompt files exactly.

All paths are relative to `/Users/pranav/Desktop/DevinProjects/imcp-product-finder/`.

## Files
| File | Purpose |
|---|---|
| `pipeline/KNOWLEDGE.md` | Marketing knowledge + winner patterns. **Read before every task.** |
| `pipeline/rubric.json` | Official 2026–27 evaluation form, bands, harsh guidance, auto-caps |
| `pipeline/prompts/00_screen.md` | Score a candidate business before building decks |
| `pipeline/prompts/01_brief.md` | Build the brief, survey, and interview guide; load real research |
| `pipeline/prompts/02_generate.md` | Write a full deck variant |
| `pipeline/prompts/03_grade.md` | Grade a deck (fresh session only) |
| `pipeline/prompts/04_revise.md` | Revise the leading variant |
| `pipeline/scripts/*.py` | check_deck, score, render, new_run, calibrate, extract_pdf, summarize_survey, make_visuals |
| `pipeline/tools/*.py` | fetch_reviews_judgeme, fetch_reviews_stamped, analyze_reviews (no-survey primary research) |
| `pipeline/team.json` | School, address, participants, date (the human fills this in) |
| `pipeline/leaderboard.csv` | Ranked results across all runs |

## Golden rules
1. **Never invent data:** no research results, quotes, company numbers, prices, or partner agreements. Unknowns become `[A#]` assumptions.
2. **Never grade in the session that wrote the deck.** Open a new Devin session for every grading pass.
3. **Scripts are the source of truth** for penalties, finance math, caps, and totals. Don't compute these yourself.
4. **Stop rules beat score-chasing:** max 3 revision rounds per lineage, and stop when a round gains fewer than 2 points.

---

## Step 0: Setup (once)
```
cd pipeline/scripts
python3 check_deck.py ../tests/fixture/deck.json   # should print 0 errors
```
Ask the human to fill in `pipeline/team.json`.

## Step 0.5: Screen candidates (when asked to find new businesses)
For each candidate name the human gives (or one you discover in `data/shortlist.csv` / the Shopify dataset), follow `prompts/00_screen.md` and write `pipeline/candidates/<slug>.md`. Only run Steps 2–5 on candidates that get a **Build it** verdict. Rank all screened candidates in `data/shortlist.csv` by score.

## Step 1: Calibrate the grader (once)
```
python3 extract_pdf.py
```
Then, in **three separate fresh sessions**, grade `runs/calibration/1st.txt`, `2nd.txt`, and `3rd.txt` with `prompts/03_grade.md`. Save the results as `runs/calibration/grades/{rank}.pass1.json`. Then run:
```
python3 calibrate.py
```
If it fails, re-read `rubric.json` → `harsh_guidance` and regrade the failing deck (max 2 retries). If it still fails, tell the human: the grader is unreliable, and the scores should be treated as rough.

## Step 2: Brief and research instruments
Follow `prompts/01_brief.md`. Output: `pipeline/brief.json`, `research/survey.md`, `research/interview_guide.md`.
**Hand the survey to the human immediately.** Real responses take the longest, so start them first.

**If the human says the survey won't happen:** follow `prompts/01_brief.md` → Prompt 01c. Run the no-survey methods yourself where possible (review fetch + analysis is fully automatable). You need **at least 2 completed lite methods** (`review_analysis` n≥100, `social_listening` n≥100, `digital_shelf_audit`/`store_observation` n≥3) to lift the Research cap from 5 to 10. Set skipped methods to `"not_applicable"`. Never present review analysis as a survey — label it customer-voice analysis and state the self-selection limitation on slide 9.

## Step 3: Generate variants (research pending)
Create 4 variants with different strategic angles. Pick from:

| Angle | Pattern source |
|---|---|
| **Channel gap:** convert an underused channel (B2B→consumer, retail→DTC) | 1st place (StixFresh) |
| **Mission metric:** build the campaign around one measurable impact number | 1st and 2nd place |
| **Trial program:** a named trial/sampling program with scripted follow-up and a conversion target | 2nd place (Earth Day Trial Fleet) |
| **Community challenge:** a UGC challenge with an ownable twist the brand alone can run | 3rd place (#BeAMisfit) |
| **Partner-led:** a proposed co-branded program with an audience-aligned partner | 1st place (HelloFresh kit) |
| **Occasion-led:** anchor on a seasonal moment inside the 45-day window | Category seasonality |

For each angle:
```
python3 new_run.py "Trial program"          # creates runs/vNN/
# follow prompts/02_generate.md in this session
python3 scripts/make_visuals.py ../runs/vNN/deck.json  # generates PNG visuals from deck.json data
python3 check_deck.py ../runs/vNN/deck.json # loop until 0 errors
python3 render.py ../runs/vNN/deck.json     # creates deck.md, deck.html, deck.pdf
python3 render_pptx.py ../runs/vNN/deck.json  # creates deck.pptx - polished editable slides w/ native charts, images, speaker notes
```

## Step 4: Grade and score each variant
For each run: open **2 fresh sessions** and grade `runs/vNN/deck.md` using `prompts/03_grade.md`. Save the grades as `grades/pass1.json` and `grades/pass2.json`. Then run:
```
python3 score.py ../runs/vNN
```
If the output says NOISY, run a 3rd fresh grading pass and score again.
While research is pending, the Research category is auto-capped at 5. That's expected: variants are compared on strategy, activities, budget, and impact for now.

## Step 5: Revise the leader
```
cat ../leaderboard.csv
python3 new_run.py "<angle> rev1" --from vNN     # vNN = top run
# follow prompts/04_revise.md
python3 check_deck.py ../runs/vMM/deck.json && python3 render.py ../runs/vMM/deck.json
# 2 fresh grading passes → score.py
```
Repeat until a stop rule triggers.

## Step 6: Load real research and finalize
When the human provides survey results, interview notes, or confirms the no-survey methods from Step 2:
1. Follow `prompts/01_brief.md` → Prompt 01b (survey/interviews) or 01c (no-survey methods). Use `summarize_survey.py` / `analyze_reviews.py`. Only use numbers they print.
2. Create a revision of the top run: `new_run.py "<angle> final" --from vNN`. Replace the research slides (9–10) with real findings, and cite ≥3 [R#] on strategy slides.
3. Run `python3 check_deck.py ../runs/vMM/deck.json --final`. This blocks on placeholders, pending research, missing title info, and unsigned assurances.
4. Render, then grade 2 fresh passes, then score.
5. Report the result to the human (see Handoff).

## Handoff to the human (end of every working session)
Report:
- The leaderboard top 3 (run, angle, final score, noisy categories)
- For the top run: capped scores by category, caps applied, and the top 3 fixes
- Open items: any [A#] assumptions on budget slides, mockups still needed (placeholders in deck.pdf), and research status
- **Recommendation:** one sentence

## Schedule for a Tue Nov 10 deadline
| When | Pipeline work | Human work |
|---|---|---|
| Sat | Steps 0–2 · Step 3 (4 variants) | Fill team.json · send survey widely · book 3 interviews |
| Sun | Steps 4–5 (grade, revise ×2) | Interviews · keep pushing the survey |
| Mon AM | Step 6 once survey closes at noon | Export CSV · type up interview notes |
| Mon PM | Final checks, render | Make/approve mockups · collect signatures · review the deck |
| Tue | — | Submit the PDF |

## Optional: one premium review
Before submission, the human may run one Opus review of the final deck using `prompts/03_grade.md`. A single strong-model pass is the cheapest way to catch what a smaller grader misses.
