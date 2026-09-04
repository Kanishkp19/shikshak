# 04 — UI/UX Design System — Shikshak AI

Adapted from the supplied Notion-style design reference (`design.md`). Same token system and component chrome, re-purposed for a teaching product: warm, document-like calm for reading-heavy screens (lesson transcripts, reports), one confident accent color, and a decorative sticker palette repurposed as subject-category color-coding (math, science, history, programming) rather than pure decoration.

## Design philosophy

Shikshak AI should feel like a well-made notebook, not a dashboard. The student is here to read, watch, and think — not to navigate chrome. The interface stays quiet (warm off-white canvas, near-black ink, one blue accent) so the lesson content and generated video are what a student's eyes land on. Where Notion uses its sticker palette purely for marketing decoration, we repurpose the same palette functionally: each subject area (math, science, history, programming, language) gets one fixed accent color from the palette, used consistently for that subject's badges, timeline dots, and card headers — so a student builds a visual association between color and subject across sessions, without ever letting color carry a second, competing meaning (never use it for status/error, which stays semantic-neutral per the "no dedicated semantic ramp" note below).

## Colors

### Brand & accent
- **Primary** `{colors.primary}` — `#0075de` — the one structural accent: primary CTA fill, active nav state, focus rings, links inside transcripts.
- **Primary pressed** `{colors.primary-active}` — `#005bab`
- **Secondary / hero** `{colors.secondary}` — `#213183` — reserved for a single "session complete" or hero moment (e.g. the report screen's top band), not repeated chrome.

### Subject color-coding (repurposed sticker palette — functional, not decorative)
- Mathematics: `{colors.accent-sky}` — `#62aef0`
- Science: `{colors.accent-green}` — `#1aae39`
- History/Social Studies: `{colors.accent-orange}` — `#dd5b00`
- Programming/CS: `{colors.accent-purple}` — `#d6b6f6` (fill) / `{colors.accent-purple-deep}` — `#391c57` (text on fill)
- Language/Literature: `{colors.accent-pink}` — `#ff64c8`
- General/Uncategorized: `{colors.accent-teal}` — `#2a9d99`

Rule: a subject color paints a `badge-pill`, a `SegmentTimeline` dot, or a `feature-card` header band — never a primary CTA and never a status signal (correct/incorrect answers use semantic green/red defined below, not subject colors, so the two systems never collide).

### Semantic (added for this product — the source design system has none, so we define our own, kept separate from the sticker/subject palette)
- Success / correct answer: `{colors.accent-green}` `#1aae39` at 800-equivalent darkness for text-on-fill
- Error / incorrect answer: a new token, `{colors.danger}` — `#c0392b` (not present in the source palette; added because the teaching product needs an unambiguous "wrong answer" signal distinct from any subject color)
- Warning / fallback engaged (e.g. video provider fallback toast): `{colors.accent-orange}` `#dd5b00`, reused since orange is not assigned to a semantic elsewhere in the neutral chrome

### Surface
- `{colors.canvas-soft}` `#f6f5f4` — page background everywhere except the lesson player (which goes full-bleed dark for video contrast — see Lesson Player exception below)
- `{colors.canvas}` / `{colors.surface}` `#ffffff` — cards, panels, form fields
- `{colors.hairline}` `#e6e6e6` — borders/dividers

### Text
- `{colors.ink}` `#000000` (~95% alpha) — headings, body
- `{colors.ink-secondary}` `#31302e` — secondary copy, transcript text
- `{colors.ink-muted}` `#615d59` — supporting copy
- `{colors.ink-faint}` `#a39e98` — captions, timestamps, metadata

### Lesson Player exception
The session player screen (`/session/[sessionId]`) inverts to a dark chrome around the video — the same treatment as Notion's `hero-band`, using `{colors.secondary}` `#213183` as the surrounding frame — so the generated video has visual contrast and isn't fighting a bright warm-paper background. This is the only screen besides the report's top band that uses the dark inversion.

## Typography

Same family and scale as the source system — `NotionInter`, substitute **Inter** directly with explicit negative tracking applied per the table below (do not rely on default Inter tracking).

| Token | Size | Weight | Line height | Tracking | Use in Shikshak AI |
|---|---|---|---|---|---|
| `{typography.display-1}` | 64px | 700 | 1.0 | −2.125px | Marketing hero only |
| `{typography.display-2}` | 54px | 700 | 1.04 | −1.875px | Report score numeral |
| `{typography.heading-1}` | 40px | 700 | 1.1 | −1px | Dashboard section titles |
| `{typography.heading-2}` | 26px | 700 | 1.23 | −0.625px | Lesson segment titles |
| `{typography.heading-3}` | 22px | 700 | 1.27 | −0.25px | Card titles (session cards, report sections) |
| `{typography.title}` | 20px | 600 | 1.4 | −0.125px | Question card prompts |
| `{typography.body-md}` | 16px | 400 | 1.5 | 0 | Transcript text, default body |
| `{typography.body-sm}` | 15px | 400 | 1.33 | 0 | Timeline labels, table rows |
| `{typography.button}` | 16px | 500 | 1.5 | 0 | All button labels |
| `{typography.caption}` | 14px | 400 | 1.43 | 0 | Timestamps, metadata |
| `{typography.eyebrow}` | 12px | 600 | 1.33 | +0.125px | Subject badges, level badges |

## Layout

- Base spacing unit: 8px, same scale as source (`{spacing.xxs}` 4px through `{spacing.xxl}` 32px).
- Container: centered, max-width ~1100px for reading-heavy screens (dashboard, report); the lesson player goes full-bleed within the app shell for video presence.
- Whitespace-first grouping, hairlines over rules, exactly as source system — this matters more for us than for Notion, since dense agent-generated text (transcripts, reports) needs generous spacing to stay readable.

### Breakpoints (unchanged from source)
| Name | Width | Key change |
|---|---|---|
| Wide | 1440px+ | Full sidebar + widest player |
| Desktop | 1080–1300px | Standard container |
| Tablet | 768–840px | Transcript panel moves below player instead of beside it |
| Mobile | ≤600px | Single column, hamburger nav, sticky "answer" bar for QuestionCard |

## Elevation

Unchanged from source — flat + hairline for default cards, soft Level-1 layered shadow for the lesson player frame and floating QuestionCard, Level-2 for the sign-out confirm modal. No heavy drop shadows anywhere in the product.

## Shapes

Unchanged token values from source:
- `{rounded.xs}` 4px — form fields
- `{rounded.sm}` 5px — list rows, status pills
- `{rounded.md}` 8px — utility buttons, subject badges
- `{rounded.lg}` 12px — feature cards, session cards, report card
- `{rounded.xl}` 16px — video player frame
- `{rounded.full}` — marketing CTAs, "Start lesson" pill, all `badge-pill` chips

## Components

### Navigation
**`app-shell-nav`** (maps to source `ex-app-shell-row`) — left sidebar, `{colors.canvas}` surface, active item shows `{colors.primary}` as a left `activeIndicator` bar plus `{colors.primary}`-tinted text.

### Buttons
**`button-primary`** — `{colors.primary}` fill, pill `{rounded.full}` — "Start lesson", "Get started free", "Submit answer".
**`button-primary-pressed`** — `{colors.primary-active}` fill.
**`button-secondary`** — white surface, `{colors.ink}` text, pill, soft shadow — "See how it works", "Start related lesson".
**`button-utility`** — white surface, `{rounded.md}`, hairline border, tight padding — nav actions, language switcher, "Retry" actions.
**`button-icon-circular`** — video player transport controls (play/pause/skip), `rgba(0,0,0,0.05)` fill per source spec.

### Cards
**`feature-card`** — session list items, dashboard feature cards, learning-path stepper rows. Optional colored header band using the subject color-coding above.
**`feature-card-elevated`** — the report card, the floating QuestionCard.
**`session-card`** (new, extends `feature-card`) — adds a subject `badge-pill`, a score `badge-pill` (green fill if score ≥ 70, orange if below — semantic, not subject color), and a `{typography.caption}` date.

### Inputs
**`text-input`** — unchanged from source: `{rounded.xs}` 4px, tight square corners, `{colors.hairline}`-adjacent border, focus adds Level-1 shadow.
**`select`** (new, extends `text-input` chrome) — same border/radius/padding, chevron icon from `lucide-react`.
**`file-dropzone`** (new) — dashed `{colors.hairline}` border at `{rounded.lg}`, `{colors.canvas-soft}` fill, centered upload icon + `{typography.body-sm}` instructions; on drag-over, border becomes `{colors.primary}` solid.

### Signature components (new, specific to Shikshak AI)
**`QuestionCard`** — `feature-card-elevated` chrome, appears inline within the lesson player (never a blocking overlay modal). Contains `{typography.title}` prompt, MCQ options as selectable `button-utility`-style rows or a `text-input` for short answer, `button-primary` "Submit answer". On grading: correct shows a `{colors.accent-green}` top border flash; incorrect shows `{colors.danger}` top border flash, then transitions into the misconception re-explanation segment.
**`SegmentTimeline`** — horizontal strip of dots (`{rounded.full}`, 8px), current segment dot filled `{colors.primary}`, completed dots filled `{colors.ink-faint}`, upcoming dots are hollow with a hairline border. Checkpoint segments show a small question-mark glyph above their dot.
**`ScoreBadge`** — `badge-pill` chrome, `{colors.accent-green}` fill + dark green text if score ≥ 70, `{colors.accent-orange}` fill + dark orange text otherwise.
**`ReportBand`** — top band of the report screen, `{colors.secondary}` dark fill (the one other place besides the marketing hero and lesson player that uses the dark inversion), white `{typography.display-2}` score numeral centered.

### Toast/alert
**`toast`** — `feature-card` shape + medium shadow (source `ex-toast` pattern), `{typography.body-sm}`, colored left border only (4px, no full-surface tint) using semantic `{colors.primary}` (info), `{colors.accent-green}` (success), `{colors.danger}` (error), `{colors.accent-orange}` (warning/fallback-engaged).

### Loading skeletons
Session cards, video frame, and report card all use a shimmering `{colors.hairline}`-toned rectangle matching the real component's exact `{rounded}` value and dimensions — never a generic gray box that doesn't match final layout, to avoid layout shift.

## Accessibility

- WCAG AA minimum contrast for all text-on-surface pairings; `{colors.ink-faint}` (#a39e98) is reserved for captions/metadata only, never body copy, since it sits close to the AA threshold on `{colors.canvas-soft}`.
- All interactive elements (buttons, timeline dots, QuestionCard options) carry visible focus rings using `{colors.primary}`.
- Video player includes captions (the narration transcript, already generated) toggleable via a `button-icon-circular` control — this doubles as an accessibility feature and a literal on-screen-text requirement from the assessment brief.
- Language switcher and level indicators use both color and text label (never color alone) to convey subject/level, satisfying color-blind accessibility.

## CSS variables (paste into `globals.css`)

```css
:root {
  --color-primary: #0075de;
  --color-primary-active: #005bab;
  --color-secondary: #213183;
  --color-danger: #c0392b;
  --color-accent-sky: #62aef0;
  --color-accent-green: #1aae39;
  --color-accent-orange: #dd5b00;
  --color-accent-purple: #d6b6f6;
  --color-accent-purple-deep: #391c57;
  --color-accent-pink: #ff64c8;
  --color-accent-teal: #2a9d99;
  --color-canvas: #ffffff;
  --color-canvas-soft: #f6f5f4;
  --color-hairline: #e6e6e6;
  --color-ink: rgba(0,0,0,0.95);
  --color-ink-secondary: #31302e;
  --color-ink-muted: #615d59;
  --color-ink-faint: #a39e98;
  --radius-xs: 4px;
  --radius-sm: 5px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  --spacing-xxs: 4px;
  --spacing-xs: 8px;
  --spacing-sm: 12px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 28px;
  --spacing-xxl: 32px;
  --shadow-level-1: 0 0.175px 1.041px rgba(0,0,0,0.01), 0 0.8px 2.925px rgba(0,0,0,0.02), 0 2.025px 7.847px rgba(0,0,0,0.027), 0 4px 18px rgba(0,0,0,0.04);
  --shadow-level-2: 0 23px 52px rgba(0,0,0,0.05);
}
```
