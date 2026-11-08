# Field Kit — Stryve / Braav Biltong ("It's Not Jerky")

Everything the team needs to collect REAL primary research in ~1 week. Every item maps to a rubric research method. Target: n≥30 survey + 3 interviews + shelf audit + photos. That moves Research from 10/15 → 13–15/15.

---

## 1. Intercept Survey (target n=30–50, ~2 hrs at a DFW H-E-B or gym)

**Script:** "Hi — quick 60-second snack survey for a class project. Mind if I ask 5 questions?"

Ask only shoppers near the meat-snack/jerky set or fitness aisle:

1. How often do you buy jerky/meat snacks? (weekly / monthly / rarely / never)
2. What's the #1 reason you buy them? (protein / taste / convenience / curiosity / other)
3. Have you ever tried biltong? (yes / no / what's that?)
4. Would you try an air-dried beef snack if samples were free? (yes / maybe / no)
5. What would make you buy it again? (open-ended — record verbatim)

**Record:** date, store, approximate age range, exact quotes for Q5.
**Deliverable:** `pipeline/research/survey_results.csv` (one row per respondent) → I run `summarize_survey.py` and wire findings into deck.json as [R#].

## 2. Customer Interviews (3 × 20 min)

Find jerky/meat-snack buyers at H-E-B, gym, or via the Stryve website's review contacts. Record notes (no recording needed, but get verbatim quotes).

- "Walk me through the last time you bought a meat snack — where, why, how did it taste?"
- "What's your go-to brand and what keeps you loyal / what frustrates you?"
- "If you saw 'biltong — air-dried, never cooked' on a shelf tag, would you try it? Why/why not?"
- "What would make you switch from your usual jerky?"

## 3. Shelf Audit (30 min at 2–3 H-E-B stores)

At each store, photograph + note:
- [ ] Braav/Stryve pack facing, price, shelf position (eye-level? bottom?)
- [ ] Adjacent jerky brands + prices (competitive set)
- [ ] Any shelf talkers/clip strips/demos present
- [ ] Store locator confirms Braav stocked here? (Y/N)

Deliverable: photos + `pipeline/research/shelf_audit_<store>.md`.

## 4. Photo Shot List (for design score)

Take real photos — these replace generated visuals:
- [ ] Braav bag front + back (buy one ~$8 at H-E-B/Walmart/Sprouts)
- [ ] Biltong slices close-up (texture shot)
- [ ] H-E-B shelf set wide shot (context)
- [ ] Any existing shelf talker/clip strip
- [ ] Team at the demo table (delivery slide optional)

## 5. What to send me

Drop into the repo: survey CSV, interview notes (verbatim quotes), shelf audit notes, photos in `pipeline/runs/vNN/photos/`. I'll validate, wire findings → decisions on Slide 10, re-render, re-grade. Expected gain: +4–5 research points → ~92–93.
