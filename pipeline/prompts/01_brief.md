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
