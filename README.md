# news-image-20261122 — RIVAL9: "THE SUNDAY RECORD" (round 9)

A one-page Sunday newspaper front page for 22 November 2026: 37 stories
across 7 regions, every date checked. Built from scratch with PIL only.

## Opponent

RIVAL8 (commit `5ced8477`, branch `rival8`) — won duel round 8 4–0–2
vs RIVAL7. This build keeps RIVAL8's verified facts and applies the
round-8 jury's levers:

1. **COP31 overtime 44h → 48h** — stat band, hero 1 kicker and deck.
   Verified: thegist (citing Politico Europe) "closed on Sunday 22
   November 48 hours past its scheduled finish"; AP "running nearly
   48 hours overtime"; Reuters "spilled two days into overtime";
   The Times "running two days past the finish date". Scheduled close
   was Friday 20 Nov 18:00 local (UNFCCC); the closing plenary ran to
   late Sunday afternoon. COP25's 44h record is beaten, so COP31 > 44h.
2. **DATE CHECK trap** — "148-drone night / Kryvyi Rih double-tap —
   Fri 20–Sat 21 Nov" replaces the weakest item (Senate $350bn defence
   push). Verified: Ukraine Air Force — 3 ballistic missiles + 148
   drones (87 jet-powered) between 18:00 20 Nov and the morning of
   21 Nov; Kryvyi Rih double-tap killed a 7-year-old boy and a
   20-year-old paramedic, 58 injured.
3. **Disambiguation** — hero 2 deck now reads "Tonight: 186 drones,
   not 400." The 400-drone barrage (404 drones + 111 missiles) was the
   night of 19–20 Nov; tonight's raid (night of 21–22 Nov) is 186
   drones, 161 downed or jammed (Ukraine Air Force).
4. **Hero 2 (Kyiv) art redrawn with depth** — layered skyline, haze,
   smoke column, searchlight beams, moon halo, drone silhouettes.
5. **Footer** — map band ~12px shorter; the room goes to DATE CHECK
   line-height. Story count unchanged (37).
6. **Varied mini illustrations** on the top grid cards (ballot box,
   cricket stumps, chequered flag, exam paper, ship + flame) and more.

## Inherited (verified in rounds 1–8)

- COP31 collapses with no deal — first breakdown since COP15 in 2009;
  the EU walked out (CNN, NPR).
- Bahrain: two hurt; a civilian plant burned.
- Hong Kong turnout final 98.79% (5,640 of 5,709).
- Japan poll 62% feel affinity to Korea (not 52%).
- Bayelsa boat toll 24 (not 26).
- Liverpool rout Man Utd 4–0 on Pochettino debut (Szoboszlai 10',
  Wirtz 13', Ngumoha 66', Muñoz 82'; Yoro off 8').
- MARKETS: gold $3,539; Bitcoin $61,568; TASI 9,960.44 −1.95%;
  QSE 9,902.87 −1.59%; EGX30 49,989.79 −2.85%; EGX70 16,534.42 −5.55%.
- Moldova: ONE Russian jet drone crossed the border twice near Purcari
  on Sat 21 Nov († SAT).
- Manipur liquor toll 19, 600+ in hospital — Sun a.m., still rising.
- Certainty labels + HOW TO READ legend; 22 pinned stories on the
  world map with a Pacific inset (Wellington 5 · Canberra 17).

## Files

- `render_rival9.py` — the renderer (PIL only, deterministic).
- `main.py` — entrypoint: renders, then copies `poster.png` into
  `$MAKEFUN_OUTPUT_DIR` (clears only the directory's contents).
- `poster.png` — the rendered 1024×1024 front page.
- `README.md` — this file.
- `LICENSE` — MIT.

## Build

```sh
python3 render_rival9.py poster.png
```

Render twice and compare hashes to confirm determinism.
