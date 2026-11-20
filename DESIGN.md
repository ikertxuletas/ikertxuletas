# Design · GitHub profile README

## Brief
For whom: recruiters and potential clients opening the GitHub profile · Goal: inform and invite contact · Tone: sober finance, warm, quietly alive · Platform: GitHub README made of SVG cards (no JS, no external CSS)
User decisions: keep the existing design and the portfolio recording (`assets/live.webp`) as they are; the profile follows real repository activity; private repositories appear only through an allowlist kept outside this repo.

## Direction
Design Read: a finance person who automates, shown with numbers that move on their own: calm, precise, a little gold.
Mode: Experience · Dials: variance 3 / motion 4 / density 4
Palette (from `scripts/svgkit.py` THEMES, the only source of colour):
- light: ink #1f2328, muted #4b535d, line #d1d9e0, surface #f2eee7, accent #7A6034, accent2 #A99D88, faint #8c959f, dim #b7bfc8
- dark: ink #f0f6fc, muted #b1bac4, line #3d444d, surface #1c232e, accent #C9B48A, accent2 #8C7748, faint #6e7681, dim #545d68
- Text uses ink or muted on the GitHub background or on surface; both pass 4.5:1. Accent is for one highlighted word, line or number per card.
Typography: Geist embedded as woff2 (400-700). Card titles 24/700 (-0.8 tracking), row labels 14/500 muted, row lines 19/600 ink, footers 14 muted, hero 42/700.
Layout: width 860 (`W`), cards left-aligned, rows of 80 px with 12 px radius, `<br><br>` between cards.
Motifs: thin gold wave lines (hero), a highlight that walks row by row (enc / edge / spot / nudge, 3 s per row), slow breathing on one figure. Every card respects `prefers-reduced-motion`.
Rules: one bold thing per card; no new tokens or fonts; light and dark variants on one line inside `<picture>` so GitHub serves the dark one; numbers are measured, never invented; dates are absolute.
Why it is not the generic answer: gold on GitHub greys instead of a stats widget, motion that reads like a ticker, and copy about outcomes, not tools.

## Technical
Stack: Python stdlib writes the SVGs (`scripts/build_svgs.py` for static cards, `scripts/update_langs.py` + `scripts/activity.py` for daily data cards), GitHub CLI for data, a daily Windows task pushes changes; GitHub Action `arcade.yml` builds the snake on the `output` branch.

## Audit
Date: 2026-11-20 · Activity card checked rendered at 1900 px in light and dark: no overlap between the longest line and the activity line, text tokens unchanged from existing cards · Banned list: no new devices · Accessory removed: the activity line has no fill or end dots.
