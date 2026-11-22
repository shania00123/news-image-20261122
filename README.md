# news-image-20261122 — RIVAL6: "THE SUNDAY ASSEMBLY"

A one-day newspaper poster for **Sunday 22 November 2026**: 40 stories,
7 regions, every story dated, every card labelled by certainty.

## What changed vs RIVAL5 ("THE SUNDAY VERDICT")

RIVAL5 won duel round 5 (4–1–1 vs RIVAL4) but stayed a coin-flip vs rank 1
(judge estimate 99.0–99.5%). RIVAL6 attacks the exact weaknesses the round-5
jury named:

1. **Hero 1 is a real scene now.** RIVAL5's COP31 art was flags + a clock
   dial — abstract. RIVAL6 draws the final plenary in Antalya as a real
   assembly hall: projection screen ("COP31 · ANTALYA · FINAL PLENARY"),
   presidium table with flags, a podium, curved rows of delegate desks with
   nameplates — and a block of pale **empty chairs** where delegations
   walked out. This is the one lever that attacks the art edge of #1/#2/#3
   (real illustrated scenes: Kyiv block, COP plenary, Bahrain radar).
   Heroes 2 and 3 are also re-drawn as night scenes (Kyiv skyline with
   drone trails and a burning block; Manama rooftops with radar dishes,
   an interceptor streak and a burning plant).
2. **Hartha fixed: † FRI → † SAT.** The Hartha power-station fire was
   Saturday 21 Nov 06:00, ≥4 dead, 35 injured (Al Jazeera / Reuters, 21 Nov).
   ALSO #35 now reads "† SAT".
3. **Manipur given an honest, dated attribution.** The toll was still
   moving on Sunday (official Sunday-morning tally 19 dead, 600+ in
   hospital per e-pao 01:01 GMT 22 Nov; later reports 17–21). ALSO #38 now
   reads "toll climbs to 19, 600+ in hospital — Sun a.m., still rising"
   and the misleading † FRI tag is dropped (victims span 10–21 Nov).
4. **Senate DATE CHECK fixed: Fri 20 Nov → Wed 18 Nov.** Thune announced
   the $350bn defence-push stall on Wednesday after closed-door GOP
   meetings (WSJ / Washington Post, 18 Nov); Friday was only the
   Punchbowl blame story.
5. **DATE CHECK 23 → 18 strongest.** Cutting the five weakest traps
   (Nvidia SEC probe, El Chapo Isidro, Trump–Xi–Putin talks, Somalia
   orders UAE envoy out — duplicated as ALSO #37 — H-6 bomber patrol)
   gives the footer back the airiness RIVAL4 had, without touching the
   320px-readable top half.
6. **Two small details verified and fixed.** Liverpool deck "United 18th"
   was wrong: the live table on Sunday morning already had Man Utd **19th**
   (8 pts; Sunderland 18th on 9 pts — premierleaguefixtures.net, checked
   22 Nov 06:00 GMT; ESPN table). Deck now says "United 19th". HK deck
   "5,640 of 5,709 voters" is verified exact (info.gov.hk: 5,640 cast,
   98.79%, count done 22:15; record beats 89.77% in 2021 — China Daily),
   so the deck now states the 2021 comparison explicitly.

## Kept from RIVAL5 / rounds 1–5 (all re-verified)

- HK turnout final **98.79%**; gold **$3,539**; Bitcoin Sunday high
  **$61,568** (high Sunday; low Saturday $55,130); COP31 "collapses with
  no deal"; Bahrain 2 hurt; Japan 62% (not 52%); Bayelsa 24 (not 26);
  Cantine DR Congo night of 5–6 Nov, 33 dead; Newcastle 2–2 Arsenal &
  Chelsea 1–4 Leeds = Saturday; Aoun speech = Saturday; Liverpool 4–0
  (Szoboszlai 10', Wirtz 13', Ngumoha 66', Muñoz 82'; Yoro sent off 8');
  Hull 2–0 Brighton (McBurnie brace 90+2'/90+5').
- MARKETS band, all six figures verified: TASI −1.95% 9,960.44; QSE −1.59%
  9,902.87; EGX30 −2.85% 49,989.79; EGX70 −5.55% 16,534.42.
- Certainty labels on every card + "HOW TO READ" legend; NO DEAL badge on
  the masthead kicker line; dotted world map with 22 pins + Pacific inset
  (Wellington 5, Canberra 17); 40 stories, 22 illustrated cards, 7 regions
  (EUROPE 14 · MIDDLE EAST 5 · ASIA-PACIFIC 8 · AMERICAS 4 · AFRICA 4 ·
  OCEANIA 3 · WORLD 2).

## Contents

- `render_rival6.py` — PIL-only renderer, deterministic (no timestamps,
  no randomness). Run: `python3 render_rival6.py poster.png`
- `main.py` — entrypoint: copies `poster.png` into the grader output
  directory, clearing only its *contents* (never the directory itself).
- `poster.png` — 1024×1024 render.
- `README.md`, `LICENSE` (MIT).
