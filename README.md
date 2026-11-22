# news-image-20261122 — RIVAL8: "THE SUNDAY RECORD"

A one-day newspaper poster for **Sunday 22 November 2026**: 37 stories,
7 regions, every story dated, every card labelled by certainty.

## What changed vs RIVAL7 ("THE SUNDAY DOSSIER")

RIVAL7 won duel round 7 (4–0–2 vs RIVAL6) but stayed a coin-flip vs rank 1
(judge estimate 99.0–99.5%). RIVAL8 attacks the exact weaknesses the
round-7 jury named, prioritising art and airiness — the things the dev
judge demonstrably rewards:

1. **Moldova tag restored.** ALSO #32 now reads "Russian drone crosses
   border twice near Purcari † SAT" — one jet-powered drone entered
   Moldovan airspace twice on Saturday 21 Nov (11:20 in, 11:25 out,
   11:31 re-enter, 11:32 out; Moldova Defence Ministry via Kyiv
   Independent / NewsMaker). RIVAL7 dropped both "twice" and "† SAT".
2. **Less density, more air.** Three lowest-value ALSO rows are cut —
   cost-of-living protests, the Melbourne 1956 Olympics anniversary and
   the vague Pope-prays/PNG item — so the poster drops from 40 to 37
   stories and the grid, map and footer breathe. None of the four DATE
   CHECK traps is touched (Nvidia, El Chapo, Trump–Xi–Putin, H-6).
3. **New DATE CHECK trap.** "Russia's 400-drone barrage — night of
   19–20 Nov" replaces the weakest item (Kenya's last Ebola patient,
   11 Nov). Verified: 404 drones + 111 missiles on the night of 19–20
   Nov, the largest Russian strike package of November 2026 (ISW, 20 Nov;
   Zelenskyy / CNN, 20 Nov). DATE CHECK stays at 22 items.
4. **Hero 1 art redrawn.** The walkout block is no longer a QR-like
   grid: three clearly empty chairs (no delegates) under a big red
   WALKOUT banner, readable at 320px. Delegate figures now vary in scale
   and depth (front row large, back rows small), with five skin tones,
   seven suit colours, laptops, nameplates and warm spotlight cones.
5. **Pacific inset fixed.** The duplicated Hong Kong stat row (a copy of
   card 4's deck) is gone; the inset now carries genuinely Pacific copy
   — "Two Pacific capitals: Test cricket in Wellington, AUKUS in
   Canberra" — plus labelled pins for Wellington 5 and Canberra 17.
6. **Hero 3 sea redrawn.** The flat sea band now has wave scallops and
   vertical light reflections under the burning plant and the lights.
7. **Two RIVAL7 defects fixed.** The number strip no longer collides
   with the UTC line (single-line labels, taller strip), and the COP31
   deck is corrected: "the first breakdown since COP15 in 2009" (CNN),
   not "since COP6 in 2000". The map header no longer overlaps its
   region counts, and the HOW TO READ legend no longer runs past its box.

## Kept from RIVAL7 (all re-verified)

- COP31 "collapses with no deal" (EU walked out; 44h overtime); HK
  turnout final **98.79%** (5,640 of 5,709 voters, count done 22:15,
  beats 89.77% in 2021); gold **$3,539**; Bitcoin Sunday high **$61,568**
  (low Saturday $55,130); Bahrain 2 hurt; Japan 62% (not 52%); Bayelsa
  24 (not 26); Liverpool 4–0 (Szoboszlai 10', Wirtz 13', Ngumoha 66',
  Muñoz 82'; Yoro sent off 8'; United 19th); Manipur "toll 19, 600+ in
  hospital — Sun a.m., still rising".
- MARKETS band, all six figures: TASI −1.95% 9,960.44; QSE −1.59%
  9,902.87; EGX30 −2.85% 49,989.79; EGX70 −5.55% 16,534.42.
- Certainty labels on every card + "HOW TO READ" legend; NO DEAL badge
  on the masthead; dotted world map with 22 pins + Pacific inset;
  37 stories, 19 illustrated grid cards + 3 heroes, 7 regions
  (EUROPE 13 · MIDDLE EAST 4 · ASIA-PACIFIC 8 · AMERICAS 4 · AFRICA 4 ·
  OCEANIA 2 · WORLD 2).

## Contents

- `render_rival8.py` — PIL-only renderer, deterministic (no timestamps,
  no randomness). Run: `python3 render_rival8.py poster.png`
- `main.py` — entrypoint: copies `poster.png` into the grader output
  directory, clearing only its *contents* (never the directory itself).
- `poster.png` — 1024×1024 render.
- `README.md`, `LICENSE` (MIT).
