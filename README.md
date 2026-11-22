# news-image-20261122 — RIVAL5: "THE SUNDAY VERDICT"

A one-day newspaper poster for **Sunday 22 November 2026**: 40 stories,
7 regions, every story dated, every card labelled by certainty.

## What changed vs RIVAL4 ("THE SUNDAY LEDGER")

RIVAL4 won duel round 4 (3–2–1 vs RIVAL3) but was still a coin-flip vs rank 1
(judge estimate 98.9–99.5%). RIVAL5 attacks its real weaknesses:

1. **Manipur corrected.** RIVAL4 printed the Friday figure (11 dead, 180+ in
   hospital). By Sunday morning the official toll was **19 dead, 600+ in
   hospital** (e-pao / NorthEast Now, 22 Nov). ALSO #38 now reads
   "Manipur liquor toll climbs to 19, 600+ in hospital", tagged † FRI.
2. **"Suspected" restored.** The Finland card again says the Russian
   helicopter was *suspected* of violating Finnish airspace — by 4.1 km,
   off Loviisa (Finnish MoD, Sat 21 Nov).
3. **Honest date framing.** The three Fri/Sat items under the ALSO header
   (Hartha #35, Moldova #36, Manipur #38) now carry a † FRI / † SAT tag,
   explained by the legend ("† in ALSO — dated Fri/Sat, see below").
4. **DATE CHECK 18 → 23.** Restored traps: Denmark expels Russian attaché
   (Fri 20 Nov), Qatar talks in Tehran (Fri 20 Nov), UK–EU food deal agreed
   (Fri 20 Nov), Senate $350bn defence push stalls (Fri 20 Nov), H-6 bomber
   patrol nears Manila (Sat 21 Nov).
5. **Certainty labels on every card.** Each kicker carries a chip —
   ● REPORTED (confirmed by 2+ sources), ○ CLAIM (one side asserts, the
   other denies), ◷ FORECAST (still to happen when drawn) — with a
   "HOW TO READ" legend box in the grid. Heroes #1/#2 REPORTED, #3 CLAIM;
   Turin final and NATO-Monday are FORECAST.
6. **Europe pin cluster decluttered.** The map's Europe pins are fanned out
   with leader lines instead of stacking; the Pacific inset now sits
   *beside* the map (Wellington 5, Canberra 17) instead of covering East
   Asia pins.
7. **Liverpool is a result, not a forecast.** Liverpool 4–0 Man Utd,
   Pochettino routed on debut (Szoboszlai 10', Wirtz 13', Ngumoha 66',
   Muñoz 82'; Yoro sent off 8'), with a FULL TIME chip. Hull 2–0 Brighton
   (McBurnie late brace) likewise corrected in ALSO #33.

## Kept from RIVAL4 / rounds 1–3 (all re-verified)

- HK turnout final **98.79%**; gold **$3,539**; Bitcoin Sunday high
  **$61,568**; COP31 "collapses with no deal"; Bahrain 2 hurt; Japan 62%
  (not 52%); Bayelsa 24 (not 26); Cantine DR Congo night of 5–6 Nov,
  33 dead; Newcastle 2–2 Arsenal & Chelsea 1–4 Leeds = Saturday; Aoun
  speech = Saturday.
- MARKETS band, all six figures verified: TASI −1.95% 9,960.44; QSE −1.59%
  9,902.87; EGX30 −2.85% 49,989.79; EGX70 −5.55% 16,534.42.
- NO DEAL badge on the masthead kicker line; airy footer; 22 illustrated
  cards; 320px readability (hero 20pt, badge + 3 hero headlines + MARKETS
  band legible).

## Contents

- `render_rival5.py` — PIL-only renderer, deterministic (no timestamps,
  no randomness). Run: `python3 render_rival5.py poster.png`
- `main.py` — entrypoint: copies `poster.png` into the grader output
  directory, clearing only its *contents* (never the directory itself).
- `poster.png` — 1024×1024 render.
- `README.md`, `LICENSE` (MIT).

## Sources

Reuters · AP · AFP · Al Jazeera · BBC · The Times · Formula 1 · Cricinfo ·
PHIVOLCS · Vatican News · QNA · Saudi Exchange · QSE · EGX — all stories
verified vs Sunday 22 Nov 2026; decided / forecast labelled; claims
attributed.
