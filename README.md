# news-image-20261122 — RIVAL10: "THE SUNDAY CHRONICLE"

One-page newspaper front page for Sunday 22 November 2026: 36 stories
(3 hero + 19 grid + 14 ALSO), 22 pinned on a dotted world map with a
Pacific inset, DATE CHECK 21 items, MARKETS 6 figures, certainty labels
(REPORTED / CLAIM / FORECAST) + HOW TO READ legend.

## What changed vs RIVAL9 (round-10 levers)

1. **Hero 1 art rebuilt with perspective** — COP31 final plenary now has a
   warm spotlight cone, a small back row of delegates, a larger front row
   with varied skin tones / suits / laptops, shadows, a foreground
   presidium desk, and three empty walkout chairs under the red WALKOUT
   banner. Hero 3 (Manama) rebuilt the same way: hazy far skyline, burning
   industrial plant mid-ground, scalloped sea with fire reflections, a
   large foreground radar dish and an interceptor arc.
2. **Kryvyi Rih toll updated**: card 9 now reads "73 hurt" — the toll rose
   through Saturday (58 by Sat a.m., 73 by Sat evening incl. 9 children,
   Ukrinform / Vilkul).
3. **Duplication removed**: ALSO #30 (Mlambo-Ngcuka service) dropped — it
   duplicated the DATE CHECK item "Mlambo-Ngcuka dies — Fri 20 Nov".
   37 → 36 stories (now exactly #1's count); the freed space is footer
   whitespace, no story added.
4. **Footer lightened**: DATE CHECK 22 → 21 (weakest item, the EU–Indonesia
   deal, cut; all six strong traps kept: 148-drone, 400-drone, Nvidia,
   El Chapo, Trump–Xi–Putin, H-6) with slightly roomier leading.
5. **48h overtime re-verified, kept**: scheduled close Fri 18:00 local;
   decisive plenary Sun late afternoon (~47h past close per live blogs;
   Politico Europe: "48 hours past its scheduled finish"). The AP variant
   "more than 50 hours" conflicts with the gavel timeline (plenary set
   09:00 → 11:00 local, Kurum's no-adoption announcement in the morning
   session, conference ending ~17:00 local) and with three outlets
   reporting ~44h from an earlier baseline — 48h remains the best-supported
   single figure.
6. **Europe pins fanned out further**: numbered pins around the cluster now
   carry larger nudges with leader lines to their true spots.

## Heritage facts (all kept, re-verified 23 Nov 2026)

COP31 no-deal, "first breakdown since COP15 in 2009", "48 HOURS OVERTIME",
EU walked out; Bahrain 2 hurt + civilian plant burned; HK final 98.79%
(5,640/5,709, count done 22:15 — info.gov.hk); Japan 62%; Bayelsa 24;
Liverpool 4–0 (Szoboszlai 10', Wirtz 13', Ngumoha 66', Muñoz 82';
Yoro sent off 8'; United 19th); Moldova — one drone jet crossed twice
near Purcari † SAT (21 Nov 11:20/11:25/11:31/11:32); 400-drone barrage
19–20 Nov (404 drones + 111 missiles); 148-drone night / Kryvyi Rih
double-tap Fri 20–Sat 21 Nov; "Tonight: 186 drones, not 400." (raid
21–22 Nov = 186 drones, 161 downed/jammed; barrage 400 = night 19–20 Nov);
Manipur "19, 600+ — Sun a.m., still rising"; MARKETS — gold $3,539
(spot $3,539.00 Sun 22 Nov), BTC $61,568, TASI 9,960.44 −1.95%,
QSE 9,902.87 −1.59%, EGX30 49,989.79 −2.85%, EGX70 16,534.42 −5.55%.

## Build

`python3 render_rival10.py [outdir]` renders `poster.png` (1024×1024,
deterministic — identical bytes every run). `python3 main.py` renders to a
temp dir and copies the poster into `$MAKEFUN_OUTPUT_DIR`.
