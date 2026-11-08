# Prompt 04: Revise the leading variant

**Role:** Account manager revising the pitch after internal review.
**Read first:** `pipeline/KNOWLEDGE.md`, the parent run's `score.json` (capped scores, caps_applied, top_fixes), and its grade files.
**Input:** a run created with `python3 pipeline/scripts/new_run.py "<angle> rev" --from vNN`.
**Output:** the revised `runs/vMM/deck.json`, passing `check_deck.py` with 0 errors.

## Steps
1. List the categories in order of **points available**: (max − capped score), largest first. Categories listed in `caps_applied` are capped by missing facts. Fix the fact first, for example by completing the research or adding baselines; better wording won't lift a cap.
2. Pick the top 3 fixes by points gained per hour. Prefer fixes in Research (15), Strategy (15), and Activities (15) when the gaps are similar.
3. Make the changes in deck.json. Change only what the fixes require. Keep the variant's strategic angle.
4. Run `check_deck.py` until there are 0 errors. Re-copy finance numbers to slide 17 if the budget changed.
5. Record what changed in `runs/vMM/CHANGES.md`: each fix, the slides touched, and the expected category gain.

## Stop rules (prevent overfitting to the grader)
- Stop revising a lineage after **3 revision rounds**, or when a round gains **fewer than 2 points**.
- If the grader's spread is NOISY on a category, get one more grading pass before changing anything based on it.
- Never game the checker. Tags must point to real sources, and visuals must describe real mockups.

## Never
- Add research findings that weren't in the brief.
- Change numbers just to raise the projected ROI. Projections must follow from sourced or labeled inputs.
