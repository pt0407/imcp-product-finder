# Anti-AI-Slop Detection — 30 Presentation Patterns

These are the patterns that signal "an AI made this deck." Detect and fix before shipping.

## Visual Slop

| # | Pattern | Fix |
|---|---------|-----|
| 1 | **Purple-to-blue gradient background** | Use solid color or subtle texture |
| 2 | **Accent line under every title** | Remove all accent lines — use whitespace |
| 3 | **Generic stock photo descriptions** ("diverse team collaborating") | Use specific, relevant imagery or no image |
| 4 | **Perfect bilateral symmetry on every slide** | Break symmetry intentionally — asymmetric layouts feel human |
| 5 | **Identical icon style but random icon choices** | Icons should be semantically meaningful, not decorative |
| 6 | **Drop shadows on everything** | Remove all shadows, or use on one element type only |
| 7 | **Rounded rectangles at exactly 12px radius** | Vary: 4px for data elements, 8px for cards, 0px for sharp/editorial |
| 8 | **Same layout on every content slide** | Vary layouts: split, full, grid, center-stage |
| 9 | **Gradient text** | Never. Solid color only. |
| 10 | **Abstract geometric decorations** in corners | Remove decorative geometry that carries no information |

## Content Slop

| # | Pattern | Fix |
|---|---------|-----|
| 11 | **Topic-label titles** ("Revenue", "Market Analysis") | Rewrite as assertion: "Revenue grew 34% driven by enterprise" |
| 12 | **"In conclusion" slide** | Replace with specific CTA or next step |
| 13 | **"Thank you" as the final slide** | Final slide = specific ask or next action |
| 14 | **Bullet points that are full paragraphs** | Each bullet: 1 line, 8-12 words max |
| 15 | **5+ bullet points per slide** | Maximum 3-5. If more, split into 2 slides |
| 16 | **Buzzwords without specifics** ("leverage", "synergy", "innovative") | Replace with concrete facts and numbers |
| 17 | **Identical sentence structure across bullets** | Vary: start some with verbs, some with nouns, some with numbers |
| 18 | **"Overview" or "Agenda" slide with 10+ items** | Max 5 agenda items. Group if needed. |
| 19 | **Every slide has exactly 3 bullets** | Vary: 2 on some, 4 on others, data on some, image on some |
| 20 | **Filler slides** that restate the previous slide differently | Cut. Every slide must add new information. |

## Structural Slop

| # | Pattern | Fix |
|---|---------|-----|
| 21 | **Linear monotone pacing** (same density, same tempo throughout) | Vary: sparse → dense → sparse. Create rhythm. |
| 22 | **No breathing slides** (every slide is content-heavy) | Add a stat callout, quote, or full-bleed image between sections |
| 23 | **Section dividers with no clear purpose** | Each section divider earns its place by signaling a topic shift |
| 24 | **25+ slides for a 15-minute talk** | 1 slide per minute is the maximum for live presentations |
| 25 | **Appendix longer than the main deck** | Appendix: 5-10 slides max. Move deep data to a separate document |

## Data Slop

| # | Pattern | Fix |
|---|---------|-----|
| 26 | **Pie charts** | Replace with donut, horizontal bar, or stat callout |
| 27 | **Charts with 10+ data series** | Highlight 1-2, grey the rest |
| 28 | **Charts without annotations** | Add a callout pointing to the key insight |
| 29 | **Data tables with 20+ rows** | Summarize. Show top 5 with "full data in appendix" |
| 30 | **Charts with a legend far from the data** | Use direct labels on the data instead of legends |

## Detection Process

1. Scan every slide against this list
2. Count matches
3. 0 matches = clean
4. 1-3 matches = fix them
5. 5+ matches = significant rework needed
6. 10+ matches = start over with audience profile and narrative framework
