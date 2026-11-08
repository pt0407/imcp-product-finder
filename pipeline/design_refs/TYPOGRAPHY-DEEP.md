# Typography Deep Dive

## Font Pairing Matrix

### The Rule
One font for headings, one for body. Same font for both is also fine.
Never three fonts. The heading font carries personality. The body font
carries readability. They must contrast in category but harmonize in quality.

### Proven Pairs by Feel

| Feel | Heading | Body | Where |
|------|---------|------|-------|
| Tech / Modern | **Inter** | Inter | SaaS, developer tools |
| Tech / Editorial | **Space Grotesk** | Inter | Tech keynotes, product |
| Premium / Luxury | **Instrument Serif** | Libre Franklin | Finance, fashion |
| Premium / Warm | **Playfair Display** | Source Sans 3 | Editorial, lifestyle |
| Academic / Serious | **Source Serif 4** | Source Sans 3 | Research, policy |
| Friendly / Startup | **Plus Jakarta Sans** | Plus Jakarta Sans | Consumer apps, startup |
| Clean / Corporate | **Calibri** | Calibri | Enterprise, internal |
| Bold / Impact | **Archivo Black** | Archivo | Events, announcements |
| Developer | **Geist Sans** | Geist Sans | Dev tools, CLIs |
| Classic | **Georgia** | Arial or Calibri | Traditional, government |
| Organic / Natural | **DM Sans** | DM Sans | Wellness, sustainability |
| Monospace accent | **JetBrains Mono** (code only) | Inter | Tech with code samples |

### Weight Usage

| Purpose | Weight | When |
|---------|--------|------|
| Slide title | **700** (Bold) | Always |
| Subtitle / kicker | **500** (Medium) | Context line above or below title |
| Body text | **400** (Regular) | Always |
| Data callout number | **700** (Bold) | Big stat numbers |
| Data labels | **400** (Regular) | Chart labels, table cells |
| Emphasis in body | **600** (Semibold) | Inline emphasis, not bold |
| Caption / source | **400** (Regular) | Footer text, data sources |

### Never Use
- **300 (Light)** on any projected slide — disappears
- **900 (Black)** for body text — overwhelming
- Multiple weights in the same line (creates visual noise)
- All caps for body text (30% harder to read)

## Fallback Font Stacks

Always specify fallbacks for when your chosen font isn't available:

```
/* Sans-serif presentations */
font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;

/* Serif presentations */
font-family: 'Source Serif 4', 'Georgia', 'Palatino Linotype', serif;

/* Monospace (code samples) */
font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
```

## Number Typography

| Context | Rule | Example |
|---------|------|---------|
| Tabular data | Use tabular (monospaced) figures | `font-variant-numeric: tabular-nums` |
| Body text numbers | Use proportional figures | Default in most fonts |
| Financial data | Right-align, tabular figures | Columns of $1,234.56 |
| Percentages | Include the % sign, no space | 34.2% not 34.2 % |
| Large numbers | Use separator | 1,234,567 not 1234567 |
| Year | No separator | 2026 not 2,026 |

## Hierarchy System

For any slide, these 4 levels should be visually distinct:

| Level | Size | Weight | Color | Usage |
|-------|------|--------|-------|-------|
| L1 — Primary | 36-44pt | 700 | Text primary | Slide title |
| L2 — Secondary | 20-24pt | 500 | Text primary | Subtitles, section labels |
| L3 — Body | 18-22pt | 400 | Text primary | Content, bullets |
| L4 — Meta | 12-14pt | 400 | Text secondary | Sources, page numbers, captions |

**The ratio between L1 and L3 should be at least 1.7:1.** If your title is 36pt and your body is 22pt, the ratio is 1.64:1 — close but acceptable. If your title is 28pt and your body is 22pt, the ratio is 1.27:1 — too close, no hierarchy.
