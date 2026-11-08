# The 3-Second Glance Test

## The Test

Look at a slide for exactly 3 seconds. Then look away.

Can you answer: **"What is the point of this slide?"**

- YES → slide passes
- NO → slide fails. Fix it.

## Why 3 Seconds

During a live presentation, the audience splits attention between the speaker and
the slide. They glance at the slide for 2-4 seconds, then return to the speaker.
If the slide's point isn't clear in that glance, the slide is noise.

## The 5 Failure Modes

### 1. No Hierarchy
Everything is the same size and weight. The eye has nowhere to land.
**Fix:** Make the headline 2x the size of body text. One element dominates.

### 2. Too Much Content
More than 50 words on a live presentation slide.
**Fix:** Cut to 25-35 words. Move detail to speaker notes.

### 3. Topic Label Instead of Assertion
Headline says "Q3 Revenue" instead of "Q3 revenue exceeded target by 12%."
**Fix:** Rewrite headline as a complete sentence stating the takeaway.

### 4. Competing Visuals
Two charts, an image, and text all fighting for attention.
**Fix:** One primary visual per slide. Support with text, not more visuals.

### 5. No Focal Point
The slide is visually balanced but nothing draws the eye first.
**Fix:** Create asymmetry. Bigger number, brighter color, more whitespace on one side.

## How to Run the Glance Test

For each slide:
1. Display the slide
2. Start a 3-second mental timer
3. Look away
4. State the point in one sentence
5. If you can → pass
6. If you hesitate → fail → apply the fix for the matching failure mode

## Testing in Claude Code

When generating slides, mentally simulate the glance test on each slide:
- Is the headline an assertion? (If topic label → fail)
- Is there one dominant visual element? (If competing → fail)
- Is word count under the audience profile limit? (If over → fail)
- Is there clear size hierarchy? (If everything same size → fail)
