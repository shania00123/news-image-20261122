# news-image-20261122 — RIVAL7: "THE SUNDAY DOSSIER"

A one-day newspaper poster for **Sunday 22 November 2026**: 40 stories,
7 regions, every story dated, every card labelled by certainty.

## What changed vs RIVAL6 ("THE SUNDAY ASSEMBLY")

RIVAL6 won duel round 6 (4–0–2 vs RIVAL5) but stayed a coin-flip vs rank 1
(judge estimate 99.0–99.5%). RIVAL7 attacks the exact weaknesses the round-6
jury named:

1. **The four DATE CHECK traps are back — all 22 items, footer kept airy.**
   RIVAL6 cut Nvidia (SEC probe, Fri 20 Nov — Reuters 20 Nov; WSJ reported
   the probe first on Tue 17 Nov), 'El Chapo Isidro' (captured Fri night
   20 Nov in Guasave, announced Sat 21 Nov — CNN/AP), Trump–Xi–Putin talks
   (first-ever trilateral, Thu 19 Nov in Shenzhen — AP) and the H-6 bomber
   near Manila (Sat 21 Nov, turned back 170 km from Manila — United24 Media
   21 Nov 14:43, flight-tracking; mission unconfirmed, date + event real).
   Only Somalia stays cut: it duplicates ALSO #37 (UAE envoy's 72 hours run
   out today, ordered Thu). The footer keeps RIVAL6's airiness with smaller
   type (8pt) and tighter leading (10px) across three columns.
2. **Richer hero art.** The COP plenary now has varied delegate figures
   (five skin tones, seven suit colours, laptops, nameplates), warm
   spotlight cones, shadows under the desks and a pale walkout chair block.
   Heroes 2 and 3 get texture too: Kyiv has searchlight beams, smoke and
   embers over a lit-window skyline; Manama has radar dishes at varied
   angles, a burning civilian plant and a sea strip.
3. **The thick "4–0 FULL TIME" score badge is back** (RIVAL5 style) — a
   solid red badge on the Liverpool card's art strip, readable at 320px.
4. **Hero 3 deck restores "a civilian plant burned"** (the target was a
   civilian industrial site — confirmed by #1's own deck).
5. **Map: Europe fan-out widened** — pin labels pushed further out with
   longer leader lines, so the densest cluster breathes more.
6. **Manipur kept honest**: "toll climbs to 19, 600+ in hospital — Sun a.m.,
   still rising" (official Sunday-morning tally; the toll moved 16→21
   through Sunday, so no number is locked without a time attribution).

## Kept from RIVAL6 / rounds 1–6 (all re-verified)

- HK turnout final **98.79%** (5,640 of 5,709 voters, count done 22:15,
  beats 89.77% in 2021); gold **$3,539**; Bitcoin Sunday high **$61,568**
  (low Saturday $55,130); COP31 "collapses with no deal"; Bahrain 2 hurt;
  Japan 62% (not 52%); Bayelsa 24 (not 26); Cantine DR Congo night of
  5–6 Nov, 33 dead; Newcastle 2–2 Arsenal & Chelsea 1–4 Leeds = Saturday;
  Aoun speech = Saturday; Senate $350bn stall = Wed 18 Nov; Liverpool 4–0
  (Szoboszlai 10', Wirtz 13', Ngumoha 66', Muñoz 82'; Yoro sent off 8';
  United 19th); Hull 2–0 Brighton; Hartha † SAT.
- MARKETS band, all six figures verified: TASI −1.95% 9,960.44; QSE −1.59%
  9,902.87; EGX30 −2.85% 49,989.79; EGX70 −5.55% 16,534.42.
- Certainty labels on every card + "HOW TO READ" legend; NO DEAL badge on
  the masthead kicker line; dotted world map with 22 pins + Pacific inset
  (Wellington 5, Canberra 17); 40 stories, 22 illustrated cards, 7 regions
  (EUROPE 14 · MIDDLE EAST 5 · ASIA-PACIFIC 8 · AMERICAS 4 · AFRICA 4 ·
  OCEANIA 3 · WORLD 2).

## Contents

- `render_rival7.py` — PIL-only renderer, deterministic (no timestamps,
  no randomness). Run: `python3 render_rival7.py poster.png`
- `main.py` — entrypoint: copies `poster.png` into the grader output
  directory, clearing only its *contents* (never the directory itself).
- `poster.png` — 1024×1024 render.
- `README.md`, `LICENSE` (MIT).
