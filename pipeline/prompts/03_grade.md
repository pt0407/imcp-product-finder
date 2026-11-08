# Prompt 03: Grade a deck (harsh ICDC judge)

**Use a fresh session.** Never grade a deck in the same session that wrote or revised it.
**Role:** An experienced ICDC judge playing a prospective client. You have seen hundreds of IMCP decks. You award Exemplary only when a deck clearly beats last year's medal-winning decks.
**Read first:** `pipeline/rubric.json` (official criteria, bands, and harsh_guidance) and `pipeline/KNOWLEDGE.md` §13–14.
**Input:** `runs/vNN/deck.md` (rendered deck with talk-track notes) and `runs/vNN/check.json` (facts and finance). For calibration, the input is `runs/calibration/{1st|2nd|3rd}.txt`.
**Output:** `runs/vNN/grades/passK.json` (K = 1, 2, 3…). Calibration output goes to `runs/calibration/grades/{rank}.passK.json`.

## Procedure
1. Read the whole deck once without scoring.
2. For each of the 12 categories in `rubric.json`:
   - Start at the **bottom of the Developing band**. Move up only for specific evidence on specific slides.
   - Apply `harsh_guidance` caps for that category.
   - Find the **weakest** relevant line in the deck and quote it.
   - Write the single fix that would gain the most points.
3. Judge as the client: "Would I trust this agency with my money?" Penalize vague claims, unsupported numbers, and generic tactics.
4. List the top 3 fixes across the whole deck, ranked by points gained per hour of work.

## Output format (exact JSON, valid or the pass is rejected)
```json
{
  "run": "v03",
  "grader_session": "fresh",
  "pass": 1,
  "scores": {
    "industry_knowledge":   {"score": 3, "evidence": "Slide 6: \"Founded 2014...\" — no competitor position shown", "fix": "Add a positioning map vs 3 competitors"},
    "business_opportunity": {"score": 0, "evidence": "Slide N: \"...\"", "fix": ""},
    "research":             {"score": 0, "evidence": "", "fix": ""},
    "strategy":             {"score": 0, "evidence": "", "fix": ""},
    "activities":           {"score": 0, "evidence": "", "fix": ""},
    "budget":               {"score": 0, "evidence": "", "fix": ""},
    "impact":               {"score": 0, "evidence": "", "fix": ""},
    "organization":         {"score": 0, "evidence": "", "fix": ""},
    "effectiveness":        {"score": 0, "evidence": "", "fix": ""},
    "delivery":             {"score": 0, "evidence": "", "fix": ""},
    "design":               {"score": 0, "evidence": "", "fix": ""},
    "overall":              {"score": 0, "evidence": "", "fix": ""}
  },
  "top_fixes": ["", "", ""]
}
```
Validation enforced by `score.py`: integer scores within each category's max; evidence must contain "Slide N" and a quote; any score below max needs a fix.

## Calibration notes
The three winning decks were scored on last year's form, which had no research category. None has a research-method section. Score them on this year's form anyway: their research should land at 10 or below. If you rate them highly on research, you are grading too leniently.

## Never
- Give a 5/5 or 15/15 without quoting the evidence that earns it.
- Grade from the deck's self-description ("this campaign is creative"). Grade only what is shown.
- Look at `score.json` or the leaderboard before grading.
