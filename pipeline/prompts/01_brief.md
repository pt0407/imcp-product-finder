# Prompt 01: Brief and research instruments

**Role:** Strategist at a marketing agency preparing a client brief.
**Read first:** `pipeline/KNOWLEDGE.md` sections 0, 1, 3, 4.
**Inputs:** product name from the human; public web sources.
**Outputs:** `pipeline/brief.json`, `pipeline/research/survey.md`, `pipeline/research/interview_guide.md`

## Steps
1. Research the product and company from public sources. Record each fact with its source.
2. Identify the **structural business problem** (KNOWLEDGE §1). Write 2–3 candidate problems, each with evidence. If you can only find "low awareness," say so explicitly. That is a signal to consider a different product.
3. Write `pipeline/brief.json`:
```json
{
  "product": "", "company": "", "category": "", "brand_color": "#hex from the brand's site",
  "facts": [{"fact": "", "source": "S1"}],
  "problem_candidates": [{"problem": "", "evidence": ["S2"]}],
  "competitors": [{"name": "", "price": "", "channel": "", "positioning": "", "source": "S5"}],
  "sources": [{"id": "S1", "publisher": "", "title": "", "date": "YYYY-MM or YYYY-MM-DD", "url": "", "type": "secondary|vendor|company"}],
  "assumptions": [{"id": "A1", "text": "AOV is $45 (no public figure; confirm with company)"}],
  "research": {"methods": [/* copy the 4 methods from templates/deck.template.json, status pending */], "findings": []},
  "open_questions": [""]
}
```
4. Write `research/survey.md`: 6–10 questions following KNOWLEDGE §4 survey rules (a screener first; awareness, purchase drivers, discovery channels, price sensitivity, and one open-ended question). Format it so the human can paste it into Google Forms.
5. Write `research/interview_guide.md`: 6 open questions, 10–15 minutes.

## Rules
- Every fact needs a source with publisher, date, and URL. Mark vendor-commissioned data `"type": "vendor"`.
- Never invent numbers. Unknown values become assumptions (A#) with a note on how to confirm them.
- Never write survey results. Results come only from the human's real data (prompt 01b below).

---

# Prompt 01b: Load real research results

**When:** the human has exported survey responses or interview notes.
1. Save the survey CSV to `pipeline/research/survey_results.csv`. Run:
   `python3 pipeline/scripts/summarize_survey.py pipeline/research/survey_results.csv`
2. Every survey finding must use **only** numbers printed in `research/survey_summary.md`. Do not compute or estimate other numbers.
3. Interview notes go in `research/interviews.md`. Quotes must be verbatim from the notes.
4. Update `brief.json` → `research.methods` (n, dates, recruitment, `"status": "complete"`) and add findings:
```json
{"id": "R1", "method": "M1", "finding": "62% of respondents discover snacks on TikTok (n=58)", "therefore": "TikTok gets the largest share of paid media"}
```
5. Add the survey and interviews to `sources` as `"type": "primary"`, with the publisher set to the team's agency name and the collection dates.

---

# Prompt 01c: No-survey primary research (when the team cannot run a survey)

Use when the human says the survey/interviews won't happen. These methods are **real primary-ish research** but weaker than a survey. Two or more completed ones lift the Research cap from 5 to 10. They never reach 11–15; say so honestly in the deck and to graders.

**Method A — Customer review analysis** (`review_analysis`, needs n ≥ 100):
1. Find the store's `<shop>.myshopify.com` domain: fetch the product site's homepage HTML and grep for `myshopify.com`. Judge.me is the most common review app.
2. `python3 pipeline/tools/fetch_reviews_judgeme.py <shop>.myshopify.com pipeline/research/reviews_<slug>.csv`
   - If the shop doesn't use Judge.me, look for Loox/Okendo/Stamped widget endpoints, or use the store's `/products/<handle>.json` + reviews page. Save whatever you get as CSV with columns: `review_id, rating, date, title, body`.
3. `python3 pipeline/tools/analyze_reviews.py pipeline/research/reviews_<slug>.csv`
   - It writes `review_summary.md`. **Only numbers printed there may appear in findings.**
4. Record as method `{"type": "review_analysis", "n": <n>, "dates": "collection date", "status": "complete", "results_file": "research/reviews_<slug>/review_summary.md"}`.
5. Findings example: `"64% of 2,140 public reviews mention taste/flavor unprompted (review analysis, collected 2026-11-07) -> therefore demo sampling, not awareness ads, is the conversion lever"`.
6. Always state the limitation on slide 9: reviewers are self-selected buyers and skew positive.

**Method B — Store/digital shelf audit** (`store_observation` or `digital_shelf_audit`, needs n ≥ 3):
- If the human can visit stores, generate `research/shelf_audit_<slug>.md` (checklist: shelf placement, facings, price tags, competitor adjacency, out-of-stocks; photos welcome). Each completed store visit = n. Human supplies the observations; you never invent them.
- If the human can't visit, do a **digital shelf audit**: screenshot/record the product's placement on the retailer's site (e.g., H-E-B, Amazon, Walmart), category page position, review counts, price vs. competitors. n = number of retailer pages audited.
- Only use observations the human or the fetched pages actually show.

**Method C — Social listening** (`social_listening`, needs n ≥ 100):
- Collect public posts/comments mentioning the brand or category (TikTok/Instagram/Reddit search results the human or you can actually see). Save raw items to `research/social_<slug>.csv` (`date, platform, text, url`). Hand-code themes like analyze_reviews does. Only use counts you can reproduce from the file.

After running methods: update `brief.json` research.methods — set skipped methods (survey, interview) to `"status": "not_applicable"` so `--final` doesn't block, keep at least 2 lite methods `complete`, and add R# findings with honest `method` links. Add each dataset as a source `"type": "primary"` with the collection dates and a note that it is customer-voice/review data, not a survey.
