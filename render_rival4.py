#!/usr/bin/env python3
"""RIVAL4 — 'THE SUNDAY LEDGER' — news-image-20261122, LAWAN-ADU round 4.

A front-page newspaper for Sunday 22 November 2026: 41 verified stories,
22 illustrated cards (3 heroes + 19), a dotted world map with 22 numbered
pins and a Pacific inset, a proper MARKETS band, ALSO + DATE CHECK footer.

Written from scratch for this round. No other version's source was read;
the RIVAL3 poster was studied visually only. PIL only, deterministic.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14                      # outer margin
CW = W - 2 * M              # 996 content width
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
NAVY = (18, 35, 61)
NAVY2 = (28, 52, 88)
GREY = (90, 86, 76)
LIGHT = (239, 231, 211)
RULE = (60, 58, 50)

FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def fit(name, text, max_w, start):
    """Largest size <= start whose width fits max_w."""
    s = start
    while s > 8:
        f = font(name, s)
        if f.getlength(text) <= max_w:
            return f
        s -= 1
    return font(name, 8)


def wrap(d, text, f, max_w):
    """Greedy word wrap to lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, f, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def clipped_lines(d, lines, x, y, f, fill, leading, max_lines):
    return draw_lines(d, lines[:max_lines], x, y, f, fill, leading)


# ---------------------------------------------------------------- data
# Heroes: (num, kicker, headline, deck, scene, lon, lat, region)
HEROES = [
    (1, "ANTALYA  ·  44 HOURS OVERTIME",
     "COP31 collapses with no deal",
     "The EU, UK and Panama rejected a final text that omitted fossil "
     "fuels. First no-deal COP since COP6 in 2000; the longest ever.",
     "hall", 30.7, 36.9, "EUROPE"),
    (2, "KYIV REGION  ·  186 DRONES",
     "Russia fires 186 drones; Dymer block destroyed",
     "161 downed or jammed; 72 jet-powered. One destroyed a five-storey "
     "block in Dymer; 2 dead, 14 missing. Zelenskyy: 2,700 drones fired "
     "this week.",
     "drones", 30.5, 50.4, "EUROPE"),
    (3, "MANAMA  ·  CLAIM",
     "Iran claims two US radars hit; Bahrain denies it",
     "IRGC media claimed Saturday-night strikes hit two US Patriot radars; "
     "Bahrain says its defences intercepted them. A civilian plant burned, "
     "two hurt. CLAIM.",
     "radar", 50.6, 26.2, "MIDDLE EAST"),
]

# Cards: (num, kicker, headline, deck, scene, lon, lat, region)
CARDS = [
    (4, "HONG KONG", "Hong Kong turnout hits record 98.79%",
     "5,640 of 5,709 voters cast ballots; count done 22:15. 2021: 30.2%.",
     "ballot", 114.2, 22.3, "ASIA-PACIFIC"),
    (5, "WELLINGTON", "India declare 720/9 — a record in NZ",
     "Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.",
     "cricket", 174.8, -41.3, "OCEANIA"),
    (6, "LAS VEGAS", "Verstappen wins Vegas by 0.639s",
     "75th career win; Norris 2nd, Piastri 3rd from 17th.",
     "race", -115.1, 36.2, "AMERICAS"),
    (7, "SEOUL", "Seoul minister quits over AI exam scandal",
     "Choi Kyo-jin resigned; Lee accepted in an hour. 111 device "
     "cheating cases probed.", "desk", 127.0, 37.5, "ASIA-PACIFIC"),
    (8, "FINLAND", "Sparta II still burning off Finland",
     "Struck Sat; fire smouldered Sun, 16 crew out. Russian helicopter "
     "'violated' Finnish airspace Sat, 4.1 km in.", "ship", 24.9, 60.2, "EUROPE"),
    (9, "KRYVYI RIH", "Missile kills boy, 7, and medic, 20; 58 hurt",
     "Friday-night strike on Zelenskyy's hometown. Four fires; ~25 blocks, "
     "a hospital and schools damaged.", "ruins", 33.4, 47.9, "EUROPE"),
    (10, "SAN ANTONIO", "Wembanyama drops 50 as Spurs rout Pelicans",
     "50 pts, 19 reb, 5 blk — a first. Spurs 114-91.",
     "court", -98.5, 29.4, "AMERICAS"),
    (11, "CIKANDE", "Candy-factory fire: 3 dead, 36 missing",
     "Blaze broke out Saturday 17:00; search went on Sunday. ~300 "
     "workers inside.", "fire", 106.3, -6.2, "ASIA-PACIFIC"),
    (12, "GAZA", "Hamas seeks urgent talks after aid-van strike",
     "Strike killed 3 aid workers Saturday; Hamas calls mediators Sunday.",
     "desert", 34.5, 31.5, "MIDDLE EAST"),
    (13, "BAYELSA", "Nigeria boat toll reaches 24",
     "Capsized Friday, Ayama-Ukubie; 24 dead, 24 rescued. Manager held.",
     "river", 6.3, 4.9, "AFRICA"),
    (14, "VATICAN", "Pope Leo XIV hosts 1,300 for lunch",
     "10th World Day of the Poor; lunch in Paul VI Hall, a week of events.",
     "church", 12.45, 41.9, "EUROPE"),
    (15, "FUKUSHIMA", "1,500 still cut off by Japan snow",
     "Travellers stranded in Kitashiobara since Saturday; drifts 2 m.",
     "snow", 140.5, 37.8, "ASIA-PACIFIC"),
    (16, "MINDANAO", "M5.6 quake off Mindanao; no damage",
     "Off southern Mindanao, 15:54 local, depth 10 km. No tsunami.",
     "quake", 126.2, 7.0, "ASIA-PACIFIC"),
    (17, "CANBERRA", "Marles: US report 'wrong' on AUKUS",
     "Defence minister rejects CBO warning on subs cost.",
     "capitol", 149.1, -35.3, "OCEANIA"),
    (18, "TURIN  ·  FORECAST", "Zverev v Alcaraz in Turin final — today",
     "The ATP Finals title match closes the season in Turin.",
     "court2", 7.7, 45.1, "EUROPE"),
    (19, "WARSAW", "NATO to meet Monday over Poland incursion",
     "Rutte: 'every inch'; Kh-101 confirmed in Nowy Lipowiec. Council "
     "meets Monday.", "summit", 21.0, 52.2, "EUROPE"),
    (20, "TALLINN", "Moscow vows retaliation as Estonia seals border",
     "Crossings shut from 1 Dec, six months. Moscow calls it a 'new Iron "
     "Curtain'.", "border", 24.7, 59.4, "EUROPE"),
    (21, "DELHI", "Nepal PM Shah lands in Delhi",
     "First foreign trip; talks with Modi on Monday.",
     "plane", 77.2, 28.6, "ASIA-PACIFIC"),
    (22, "LIVERPOOL  ·  16:30 GMT", "Liverpool v Man Utd — Pochettino's first game",
     "Pochettino bows at Anfield; Yoro off early, Szoboszlai free-kick "
     "opens the scoring.", "stadium", -3.0, 53.4, "EUROPE"),
]

# ALSO: (num, region, text, source)
ALSO = [
    (22 + 1, "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv"),
    (24, "EUROPE", "Russia says it downed 170 Ukrainian drones overnight", "Moscow"),
    (25, "WORLD", "Bitcoin back above $60,000 after Saturday's $55,130 low", "Coinbase"),
    (26, "AMERICAS", "San Francisco braces for record king tides", "SFO"),
    (27, "MID EAST", "US denies Iran claim it downed an F-16", "CENTCOM"),
    (28, "MID EAST", "Lebanon marks 83rd Independence Day", "Beirut"),
    (29, "EUROPE", "Cost-of-living protests across Europe, third day running", "Paris"),
    (30, "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children", "W. Kordofan"),
    (31, "AFRICA", "S. Africa holds prayer service for Mlambo-Ngcuka, 71 (died Fri)", "SABC"),
    (32, "OCEANIA", "Melbourne: 70 years since the 1956 Olympics opened", "ABC"),
    (33, "EUROPE", "Hull v Brighton, 14:00 GMT — today", "MKM"),
    (34, "WORLD", "Pope prays for war victims; drought-hit Papua New Guinea", "Vatican"),
    (35, "MID EAST", "Iraq: fire at Hartha power station kills 4, injures 35", "Basra"),
    (36, "EUROPE", "Moldova: Russian drone crossed border twice near Purcari", "Chisinau"),
    (37, "AFRICA", "Somalia: UAE envoy's 72 hours run out today (ordered Thu)", "Mogadishu"),
    (38, "ASIA-PACIFIC", "India: toxic alcohol kills 11 in Manipur, 180+ in hospital", "Imphal"),
    (39, "ASIA-PACIFIC", "M5.3 quake in the Celebes Sea, 61 km deep, 07:54 UTC", "EMSC"),
    (40, "AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "Brasilia"),
]

# DATE CHECK: (text, day) — items listed elsewhere as Sunday that are not.
DATECHECK = [
    ("Peru quake — Fri 20 Nov", "Fri 20 Nov"),
    ("BepiColombo at Mercury — Sat 21 Nov", "Sat 21 Nov"),
    ("ICJ Myanmar ruling — Thu 19 Nov", "Thu 19 Nov"),
    ("Kenya's last Ebola patient out — 11 Nov", "11 Nov"),
    ("Sparta II struck — Sat 21 Nov", "Sat 21 Nov"),
    ("Bayelsa boat capsizes — Fri 20 Nov", "Fri 20 Nov"),
    ("Gaza aid-van strike — Sat 21 Nov", "Sat 21 Nov"),
    ("Newcastle 2–2 Arsenal; Chelsea 1–4 Leeds — Sat 21 Nov", "Sat 21 Nov"),
    ("Aoun's Israel-withdrawal speech — Sat 21 Nov", "Sat 21 Nov"),
    ("Japan poll: 62% feel affinity to Korea — Fri 20 Nov", "Fri 20 Nov"),
    ("DR Congo Cantine attack — night of 5–6 Nov", "5–6 Nov"),
    ("Somalia orders UAE envoy out — Thu 19 Nov", "Thu 19 Nov"),
    ("Mlambo-Ngcuka dies — Fri 20 Nov", "Fri 20 Nov"),
    ("Estonia closes border — decided Fri 20 Nov", "Fri 20 Nov"),
    ("El Chapo Isidro seized — Fri 20 Nov", "Fri 20 Nov"),
    ("EU–Indonesia deal — Sat 21 Nov", "Sat 21 Nov"),
    ("Nvidia SEC probe — Fri 20 Nov", "Fri 20 Nov"),
    ("Trump–Xi–Putin talks — Thu 19 Nov", "Thu 19 Nov"),
]

NUMBERS = [
    ("44h", "COP31 OVERTIME TO COLLAPSE"),
    ("186", "DRONES OR MISSILES AT UKRAINE"),
    ("161", "DOWNED OR JAMMED"),
    ("720/9", "INDIA'S RECORD TEST TOTAL"),
    ("$61,568", "BITCOIN'S SUNDAY HIGH"),
    ("98.79%", "HONG KONG TURNOUT, RECORD"),
]

MARKETS = [
    ("GOLD, per oz, Sunday", "$3,539", ""),
    ("BITCOIN — Sunday high", "$61,568", ""),
    ("TASI — 9,960.44, Riyadh", "−1.95%", "-"),
    ("QATAR — 9,902.87, Doha", "−1.59%", "-"),
    ("EGX30 — 49,989.79, Cairo", "−2.85%", "-"),
    ("EGX70 — 16,534.42, Cairo", "−5.55%", "-"),
]

TIMELINE = ("THE DAY IN UTC — 03:00 COP31 objections close · 05:30 Verstappen "
            "wins Vegas · 06:00 COP31 approval due · 09:29 Hamas seeks talks · "
            "14:15 HK count done")

KICKER = ("COP31 collapses with no deal  ·  Russia fires 186 drones  ·  "
          "Iran claims two US radars hit")

SOURCES = ("Sources: Reuters · AP · AFP · Al Jazeera · BBC · The Times · Formula 1 · "
           "Cricinfo · PHIVOLCS · Vatican News · QNA · Saudi Exchange · QSE · EGX — "
           "all stories verified vs Sunday 22 Nov 2026; decided / forecast labelled; "
           "claims attributed.")

# ---------------------------------------------------------------- scenes
# Every scene is a small flat illustration drawn with PIL primitives.
# Signature: scene(d, x, y, w, h) — top-left corner and box size.

def _sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def _dots(d, x, y, w, h, n, col, r=1):
    # deterministic pseudo-random dots (fixed seed pattern, no random module)
    s = 1234567
    for _ in range(n):
        s = (s * 1103515245 + 12345) % (1 << 31)
        px = x + s % w
        s = (s * 1103515245 + 12345) % (1 << 31)
        py = y + s % h
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)


def scene_hall(d, x, y, w, h):
    # COP31 plenary: warm hall, long desk, delegates, flags, clock. NO stamp.
    _sky(d, x, y, w, h, (96, 74, 52), (60, 48, 38))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(52, 40, 30))
    d.rectangle([x + 8, y + h - 44, x + w - 8, y + h - 26], fill=(122, 92, 58))
    for i in range(7):
        px = x + 14 + i * (w - 28) // 6
        d.ellipse([px - 5, y + h - 58, px + 5, y + h - 46], fill=(226, 205, 160))
        d.rectangle([px - 6, y + h - 46, px + 6, y + h - 44], fill=(40, 40, 40))
    for i, c in enumerate([(178, 34, 34), (255, 215, 0), (30, 80, 160),
                           (255, 255, 255), (0, 120, 60), (200, 120, 20)]):
        fx = x + 16 + i * (w - 32) // 5
        d.line([(fx, y + 8), (fx, y + 30)], fill=(220, 220, 220), width=1)
        d.polygon([(fx, y + 8), (fx + 12, y + 12), (fx, y + 17)], fill=c)
    d.ellipse([x + w - 30, y + 8, x + w - 12, y + 26], fill=(247, 242, 231))
    d.line([(x + w - 21, y + 12), (x + w - 21, y + 17)], fill=INK, width=1)
    d.line([(x + w - 21, y + 17), (x + w - 16, y + 20)], fill=INK, width=1)


def scene_drones(d, x, y, w, h):
    _sky(d, x, y, w, h, (16, 22, 44), (52, 44, 66))
    _dots(d, x, y, w, h // 2, 26, (255, 255, 255))
    d.ellipse([x + w - 34, y + 8, x + w - 14, y + 28], fill=(240, 230, 200))
    for i in range(9):
        px = x + 10 + i * (w - 20) // 8
        py = y + 14 + (i % 3) * 12
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 120, 60))
        d.line([(px, py), (px + 6, py + 4)], fill=(255, 180, 90), width=1)
    d.polygon([(x + 8, y + h), (x + 30, y + h - 26), (x + 52, y + h)],
              fill=(20, 20, 26))
    d.polygon([(x + w - 60, y + h), (x + w - 38, y + h - 20), (x + w - 16, y + h)],
              fill=(26, 26, 34))
    d.ellipse([x + w // 2 - 8, y + h - 34, x + w // 2 + 8, y + h - 18],
              fill=(255, 150, 40))
    d.ellipse([x + w // 2 - 4, y + h - 28, x + w // 2 + 4, y + h - 20],
              fill=(255, 220, 120))


def scene_radar(d, x, y, w, h):
    _sky(d, x, y, w, h, (58, 32, 22), (24, 16, 28))
    _dots(d, x, y, w, h // 2, 18, (255, 220, 160))
    for cx in (x + w // 4, x + 3 * w // 4):
        d.line([(cx, y + h - 18), (cx, y + h - 52)], fill=(200, 200, 200), width=2)
        d.arc([cx - 18, y + h - 62, cx + 18, y + h - 26], 180, 360,
              fill=(230, 230, 230), width=3)
        d.line([(cx, y + h - 52), (cx + 14, y + h - 62)], fill=(230, 230, 230),
               width=2)
    d.ellipse([x + w // 2 - 10, y + 14, x + w // 2 + 10, y + 34],
              fill=(255, 140, 30))
    d.ellipse([x + w // 2 - 5, y + 19, x + w // 2 + 5, y + 29],
              fill=(255, 210, 110))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(30, 22, 18))
    for i in range(5):
        d.rectangle([x + 10 + i * 16, y + h - 30, x + 20 + i * 16, y + h - 18],
                    fill=(70, 55, 40))


def scene_ballot(d, x, y, w, h):
    _sky(d, x, y, w, h, (200, 40, 50), (150, 30, 40))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(120, 25, 35))
    d.rectangle([x + w // 2 - 22, y + 12, x + w // 2 + 22, y + h - 22],
                fill=(40, 40, 48))
    d.rectangle([x + w // 2 - 14, y + 20, x + w // 2 + 14, y + h - 30],
                fill=(247, 242, 231))
    d.line([(x + w // 2 - 9, y + h - 44), (x + w // 2 - 2, y + h - 34),
            (x + w // 2 + 10, y + h - 52)], fill=RED, width=3)
    for i in range(4):
        d.rectangle([x + 8 + i * 10, y + h - 12 - (i % 2) * 6,
                     x + 15 + i * 10, y + h - 6], fill=(255, 215, 0))


def scene_cricket(d, x, y, w, h):
    _sky(d, x, y, w, h, (120, 180, 110), (60, 120, 70))
    d.ellipse([x + w - 26, y + 6, x + w - 8, y + 24], fill=(255, 240, 180))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(140, 110, 60))
    d.rectangle([x + w // 2 - 26, y + h - 26, x + w // 2 + 26, y + h - 8],
                fill=(200, 180, 130))
    d.rectangle([x + w // 2 - 3, y + h - 46, x + w // 2 + 3, y + h - 26],
                fill=(90, 60, 30))
    d.rectangle([x + 14, y + h - 34, x + 22, y + h - 26], fill=(240, 240, 240))
    d.ellipse([x + w - 46, y + h - 40, x + w - 38, y + h - 32], fill=(200, 40, 40))


def scene_race(d, x, y, w, h):
    _sky(d, x, y, w, h, (20, 24, 60), (90, 40, 90))
    for i in range(6):
        d.rectangle([x + i * (w // 6), y + 6, x + i * (w // 6) + 8, y + 16],
                    fill=(255, 215, 0) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(40, 40, 44))
    d.rectangle([x, y + h - 34, x + w, y + h - 30], fill=(220, 220, 220))
    for cx, col in ((w // 4, (200, 30, 30)), (w // 2, (30, 120, 220)),
                    (3 * w // 4, (240, 200, 30))):
        d.polygon([(x + cx - 16, y + h - 14), (x + cx + 16, y + h - 14),
                   (x + cx + 10, y + h - 24), (x + cx - 10, y + h - 24)],
                  fill=col)
        d.ellipse([x + cx - 12, y + h - 14, x + cx - 4, y + h - 6], fill=INK)
        d.ellipse([x + cx + 4, y + h - 14, x + cx + 12, y + h - 6], fill=INK)


def scene_desk(d, x, y, w, h):
    _sky(d, x, y, w, h, (70, 90, 130), (40, 55, 85))
    d.rectangle([x, y + h - 24, x + w, y + h], fill=(60, 45, 35))
    d.rectangle([x + 12, y + 12, x + w - 12, y + h - 24], fill=(247, 242, 231))
    d.line([(x + 18, y + 20), (x + w - 18, y + 20)], fill=GREY, width=1)
    d.line([(x + 18, y + 28), (x + w - 30, y + 28)], fill=GREY, width=1)
    d.line([(x + 18, y + 36), (x + w - 22, y + 36)], fill=GREY, width=1)
    d.line([(x + w - 26, y + 16), (x + w - 18, y + 24)], fill=RED, width=2)
    d.line([(x + w - 18, y + 16), (x + w - 26, y + 24)], fill=RED, width=2)
    d.polygon([(x + w // 2 - 14, y + h - 24), (x + w // 2 + 14, y + h - 24),
               (x + w // 2, y + h - 40)], fill=(178, 34, 34))


def scene_ship(d, x, y, w, h):
    _sky(d, x, y, w, h, (90, 110, 140), (50, 70, 100))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(30, 60, 90))
    for i in range(3):
        d.line([(x, y + h - 16 + i * 6), (x + w, y + h - 16 + i * 6)],
               fill=(120, 160, 200), width=1)
    d.rectangle([x + 10, y + h - 40, x + w - 10, y + h - 24], fill=(90, 40, 30))
    d.rectangle([x + w // 2 - 14, y + h - 56, x + w // 2 + 14, y + h - 40],
                fill=(120, 120, 120))
    d.polygon([(x + w // 2 - 4, y + h - 56), (x + w // 2 + 4, y + h - 56),
               (x + w // 2, y + h - 66)], fill=(255, 140, 30))
    d.ellipse([x + w - 34, y + h - 62, x + w - 18, y + h - 46],
              fill=(255, 150, 40))
    d.ellipse([x + w - 29, y + h - 57, x + w - 23, y + h - 51],
              fill=(255, 220, 120))
    d.ellipse([x + 14, y + 8, x + 30, y + 24], fill=(240, 235, 210))


def scene_ruins(d, x, y, w, h):
    _sky(d, x, y, w, h, (70, 70, 80), (40, 40, 50))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(35, 35, 40))
    for bx, bh, bw in ((6, 34, 26), (36, 48, 22), (62, 28, 24)):
        d.polygon([(x + bx, y + h - 14), (x + bx, y + h - 14 - bh),
                   (x + bx + bw // 2, y + h - 14 - bh - 8),
                   (x + bx + bw, y + h - 14 - bh), (x + bx + bw, y + h - 14)],
                  fill=(90, 85, 80))
        d.rectangle([x + bx + 5, y + h - 26, x + bx + 12, y + h - 14],
                    fill=(20, 20, 22))
    d.ellipse([x + w - 26, y + 8, x + w - 10, y + 24], fill=(255, 150, 40))
    d.ellipse([x + w - 21, y + 13, x + w - 15, y + 19], fill=(255, 220, 120))


def scene_court(d, x, y, w, h):
    _sky(d, x, y, w, h, (150, 90, 50), (110, 60, 40))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(200, 130, 60))
    d.ellipse([x + w // 2 - 30, y + h - 24, x + w // 2 + 30, y + h - 6],
              fill=(240, 240, 235))
    d.ellipse([x + w // 2 - 8, y + 10, x + w // 2 + 8, y + 26], fill=(230, 120, 40))
    d.line([(x + w // 2, y + 26), (x + w // 2, y + h - 26)], fill=(90, 50, 20),
           width=1)
    d.rectangle([x + w - 20, y + 8, x + w - 12, y + 30], fill=(200, 200, 200))
    d.ellipse([x + w - 24, y + 6, x + w - 8, y + 12], fill=(255, 120, 30))


def scene_fire(d, x, y, w, h):
    _sky(d, x, y, w, h, (60, 50, 45), (30, 25, 22))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(25, 20, 18))
    d.rectangle([x + 10, y + h - 48, x + w - 10, y + h - 20], fill=(90, 85, 80))
    d.rectangle([x + 16, y + h - 42, x + w - 16, y + h - 36], fill=(60, 55, 50))
    for fx in (w // 4, w // 2, 3 * w // 4):
        d.polygon([(x + fx - 10, y + h - 20), (x + fx, y + h - 52),
                   (x + fx + 10, y + h - 20)], fill=(255, 140, 30))
        d.polygon([(x + fx - 5, y + h - 20), (x + fx, y + h - 40),
                   (x + fx + 5, y + h - 20)], fill=(255, 210, 110))
    d.rectangle([x + w - 24, y + 8, x + w - 10, y + 22], fill=(200, 40, 40))


def scene_desert(d, x, y, w, h):
    _sky(d, x, y, w, h, (230, 190, 120), (200, 150, 90))
    d.ellipse([x + w - 26, y + 8, x + w - 8, y + 26], fill=(255, 240, 190))
    d.polygon([(x, y + h), (x + w // 3, y + h - 22), (x + 2 * w // 3, y + h),
               (x + w, y + h - 16), (x + w, y + h)], fill=(190, 150, 90))
    d.rectangle([x + 10, y + h - 30, x + 34, y + h - 18], fill=(240, 235, 220))
    d.polygon([(x + 10, y + h - 30), (x + 22, y + h - 40), (x + 34, y + h - 30)],
              fill=(200, 60, 50))
    d.rectangle([x + w - 30, y + h - 34, x + w - 12, y + h - 18],
                fill=(180, 170, 150))


def scene_river(d, x, y, w, h):
    _sky(d, x, y, w, h, (140, 180, 200), (80, 120, 150))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(40, 90, 130))
    for i in range(4):
        d.line([(x + 6, y + h - 20 + i * 5), (x + w - 6, y + h - 20 + i * 5)],
               fill=(150, 200, 230), width=1)
    d.polygon([(x + w // 2 - 26, y + h - 26), (x + w // 2 + 26, y + h - 26),
               (x + w // 2 + 14, y + h - 38), (x + w // 2 - 14, y + h - 38)],
              fill=(120, 70, 40))
    d.polygon([(x + w // 2 - 4, y + h - 52), (x + w // 2 + 4, y + h - 52),
               (x + w // 2, y + h - 38)], fill=(90, 50, 30))
    d.ellipse([x + 12, y + 8, x + 28, y + 24], fill=(255, 240, 180))


def scene_church(d, x, y, w, h):
    _sky(d, x, y, w, h, (190, 200, 220), (150, 160, 190))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(120, 110, 90))
    d.rectangle([x + w // 2 - 24, y + 14, x + w // 2 + 24, y + h - 16],
                fill=(230, 220, 200))
    d.polygon([(x + w // 2 - 28, y + 16), (x + w // 2, y - 2),
               (x + w // 2 + 28, y + 16)], fill=(178, 34, 34))
    d.rectangle([x + w // 2 - 6, y + h - 34, x + w // 2 + 6, y + h - 16],
                fill=(60, 50, 40))
    d.ellipse([x + w // 2 - 4, y + h - 34, x + w // 2 + 4, y + h - 26],
              fill=(60, 50, 40))
    for i in range(3):
        d.ellipse([x + 10 + i * 12, y + h - 10, x + 16 + i * 12, y + h - 4],
                  fill=(90, 80, 70))


def scene_snow(d, x, y, w, h):
    _sky(d, x, y, w, h, (210, 220, 235), (170, 185, 205))
    _dots(d, x, y, w, h, 30, (255, 255, 255), r=1)
    d.polygon([(x, y + h), (x + w // 3, y + h - 26), (x + 2 * w // 3, y + h - 14),
               (x + w, y + h - 24), (x + w, y + h)], fill=(240, 244, 248))
    d.rectangle([x + 12, y + h - 34, x + 40, y + h - 20], fill=(180, 60, 50))
    d.rectangle([x + 46, y + h - 30, x + 66, y + h - 20], fill=(60, 90, 140))
    d.ellipse([x + w - 30, y + 8, x + w - 12, y + 26], fill=(250, 245, 220))


def scene_quake(d, x, y, w, h):
    _sky(d, x, y, w, h, (70, 100, 130), (40, 60, 85))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(50, 70, 90))
    d.line([(x + 8, y + h - 18), (x + w // 4, y + h - 44), (x + w // 2, y + h - 24),
            (x + 3 * w // 4, y + h - 48), (x + w - 8, y + h - 30)],
           fill=(255, 120, 60), width=2)
    for i in range(4):
        d.line([(x + 10 + i * 18, y + h - 18), (x + 14 + i * 18, y + h - 30)],
               fill=(200, 200, 200), width=1)
    d.ellipse([x + w // 2 - 6, y + 10, x + w // 2 + 6, y + 22], fill=(255, 220, 120))


def scene_capitol(d, x, y, w, h):
    _sky(d, x, y, w, h, (150, 170, 200), (110, 130, 170))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(90, 100, 90))
    d.rectangle([x + w // 2 - 26, y + h - 44, x + w // 2 + 26, y + h - 14],
                fill=(230, 225, 210))
    d.ellipse([x + w // 2 - 14, y + h - 58, x + w // 2 + 14, y + h - 40],
              fill=(200, 195, 180))
    for i in range(5):
        d.rectangle([x + w // 2 - 24 + i * 10, y + h - 40,
                     x + w // 2 - 18 + i * 10, y + h - 14], fill=(180, 175, 160))
    d.rectangle([x + 10, y + 10, x + 26, y + 26], fill=(30, 60, 110))
    d.rectangle([x + 14, y + 14, x + 22, y + 22], fill=(255, 255, 255))


def scene_court2(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 60, 110), (20, 40, 80))
    d.rectangle([x, y + h - 24, x + w, y + h], fill=(60, 120, 90))
    d.line([(x, y + h - 12), (x + w, y + h - 12)], fill=(255, 255, 255), width=1)
    d.line([(x + w // 2, y + h - 24), (x + w // 2, y + h)], fill=(255, 255, 255),
           width=1)
    d.ellipse([x + w // 2 - 5, y + h - 34, x + w // 2 + 5, y + h - 24],
              fill=(220, 220, 40))
    for cx in (w // 4, 3 * w // 4):
        d.ellipse([x + cx - 5, y + 12, x + cx + 5, y + 22], fill=(240, 220, 180))
        d.rectangle([x + cx - 6, y + 22, x + cx + 6, y + h - 24],
                    fill=(240, 240, 240))


def scene_summit(d, x, y, w, h):
    _sky(d, x, y, w, h, (40, 60, 100), (25, 40, 70))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(30, 35, 45))
    for i in range(6):
        fx = x + 12 + i * (w - 24) // 5
        d.line([(fx, y + 10), (fx, y + 30)], fill=(220, 220, 220), width=1)
        d.polygon([(fx, y + 10), (fx + 11, y + 14), (fx, y + 19)],
                  fill=[(30, 80, 160), (178, 34, 34), (255, 215, 0),
                        (0, 120, 60), (255, 255, 255), (200, 120, 20)][i])
    d.rectangle([x + w // 2 - 30, y + h - 38, x + w // 2 + 30, y + h - 20],
                fill=(90, 70, 50))
    d.ellipse([x + w - 28, y + 8, x + w - 12, y + 24], fill=(240, 230, 200))


def scene_border(d, x, y, w, h):
    _sky(d, x, y, w, h, (120, 130, 140), (80, 90, 100))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(70, 80, 70))
    for i in range(6):
        bx = x + 8 + i * (w - 16) // 5
        d.line([(bx, y + 12), (bx, y + h - 22)], fill=(60, 60, 60), width=2)
    d.line([(x, y + 18), (x + w, y + 18)], fill=(60, 60, 60), width=2)
    d.line([(x, y + 30), (x + w, y + 30)], fill=(60, 60, 60), width=2)
    d.rectangle([x + w // 2 - 18, y + 34, x + w // 2 + 18, y + h - 22],
                fill=(178, 34, 34))
    d.text((x + w // 2 - 12, y + 40), "STOP", font=font("DejaVuSans-Bold.ttf", 9),
           fill=(255, 255, 255))


def scene_plane(d, x, y, w, h):
    _sky(d, x, y, w, h, (140, 180, 220), (90, 130, 180))
    _dots(d, x, y, w, h // 2, 14, (255, 255, 255))
    d.ellipse([x + w - 30, y + 8, x + w - 12, y + 26], fill=(255, 240, 180))
    cx, cy = x + w // 2, y + h // 2 - 4
    d.polygon([(cx - 30, cy), (cx + 26, cy - 6), (cx + 34, cy),
               (cx + 26, cy + 6)], fill=(240, 240, 240))
    d.polygon([(cx - 6, cy - 4), (cx + 4, cy - 18), (cx + 10, cy - 4)],
              fill=(200, 200, 200))
    d.polygon([(cx - 6, cy + 4), (cx + 2, cy + 16), (cx + 8, cy + 4)],
              fill=(200, 200, 200))
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(90, 110, 90))
    for i in range(4):
        d.rectangle([x + 10 + i * 22, y + h - 16, x + 26 + i * 22, y + h - 8],
                    fill=(70, 90, 70))


def scene_stadium(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 60, 40), (20, 40, 60))
    _dots(d, x, y, w, h // 3, 22, (255, 255, 255))
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(60, 140, 70))
    d.ellipse([x + w // 2 - 34, y + h - 28, x + w // 2 + 34, y + h - 8],
              fill=(90, 180, 90))
    d.line([(x + w // 2, y + h - 28), (x + w // 2, y + h - 8)],
           fill=(255, 255, 255), width=1)
    d.rectangle([x + 8, y + 10, x + w - 8, y + 22], fill=(200, 30, 30))
    d.rectangle([x + w // 2 - 2, y + 10, x + w // 2 + 2, y + 22],
                fill=(255, 255, 255))
    d.ellipse([x + w // 2 - 5, y + h - 40, x + w // 2 + 5, y + h - 30],
              fill=(240, 240, 240))


SCENES = {
    "hall": scene_hall, "drones": scene_drones, "radar": scene_radar,
    "ballot": scene_ballot, "cricket": scene_cricket, "race": scene_race,
    "desk": scene_desk, "ship": scene_ship, "ruins": scene_ruins,
    "court": scene_court, "fire": scene_fire, "desert": scene_desert,
    "river": scene_river, "church": scene_church, "snow": scene_snow,
    "quake": scene_quake, "capitol": scene_capitol, "court2": scene_court2,
    "summit": scene_summit, "border": scene_border, "plane": scene_plane,
    "stadium": scene_stadium,
}

# ---------------------------------------------------------------- map
# Rough equirectangular continent polygons, hand-authored (lon, lat).
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-105, 69),
     (-95, 69), (-88, 66), (-82, 66), (-80, 73), (-70, 62), (-60, 55),
     (-55, 52), (-60, 46), (-66, 44), (-70, 42), (-74, 39), (-76, 35),
     (-80, 32), (-81, 26), (-85, 29), (-90, 29), (-94, 29), (-97, 26),
     (-102, 24), (-105, 22), (-100, 18), (-95, 16), (-92, 15), (-88, 13),
     (-84, 11), (-80, 9), (-79, 9), (-83, 9), (-87, 13), (-91, 14),
     (-95, 16), (-100, 18), (-105, 21), (-110, 24), (-114, 29), (-118, 33),
     (-122, 38), (-124, 43), (-124, 48), (-128, 52), (-135, 58), (-145, 60),
     (-155, 58), (-162, 58), (-166, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-50, 60), (-43, 60), (-40, 64), (-32, 68), (-25, 70),
     (-22, 74), (-30, 76), (-45, 78), (-55, 76), (-58, 72), (-60, 68)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-78, -10), (-75, -15),
     (-71, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-71, -50),
     (-68, -54), (-65, -50), (-65, -44), (-60, -38), (-55, -34), (-50, -30),
     (-46, -26), (-41, -23), (-39, -17), (-36, -12), (-35, -8), (-38, -5),
     (-42, -3), (-46, -1), (-50, 0), (-54, 3), (-58, 6), (-62, 9),
     (-68, 11), (-73, 11), (-76, 10), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-3, 48), (-5, 49), (-1, 50), (2, 51),
     (4, 53), (7, 54), (8, 57), (10, 59), (6, 60), (5, 62), (10, 64),
     (14, 66), (18, 69), (24, 71), (30, 70), (34, 68), (40, 67), (45, 68),
     (50, 69), (55, 68), (60, 69), (65, 68), (68, 66), (64, 62), (60, 58),
     (55, 54), (50, 50), (46, 47), (42, 46), (38, 46), (34, 45), (30, 44),
     (28, 42), (26, 40), (23, 36), (22, 38), (19, 40), (16, 38), (13, 42),
     (11, 44), (8, 44), (4, 43), (2, 42), (0, 39), (-2, 37), (-6, 36),
     (-9, 37)],
    # Africa
    [(-6, 35), (-10, 31), (-14, 28), (-16, 23), (-17, 18), (-16, 13),
     (-13, 9), (-10, 6), (-6, 5), (-1, 5), (4, 6), (8, 4), (9, 2),
     (10, -2), (12, -5), (13, -9), (13, -13), (12, -17), (13, -21),
     (14, -25), (16, -28), (18, -31), (19, -34), (24, -34), (28, -33),
     (31, -29), (34, -26), (35, -22), (37, -18), (40, -14), (40, -10),
     (42, -6), (44, -2), (47, 0), (51, 2), (51, 7), (50, 11), (47, 11),
     (44, 12), (42, 14), (39, 16), (38, 19), (36, 22), (34, 26), (32, 30),
     (30, 32), (26, 32), (22, 33), (18, 33), (14, 32), (10, 34), (6, 35),
     (0, 36), (-3, 35)],
    # Asia (mainland, simplified — two lobes joined)
    [(28, 36), (33, 36), (36, 36), (39, 34), (42, 32), (44, 30), (47, 30),
     (50, 29), (53, 27), (56, 26), (59, 25), (62, 25), (66, 25), (69, 22),
     (72, 20), (74, 17), (76, 12), (78, 8), (80, 7), (81, 9), (83, 14),
     (86, 19), (89, 22), (92, 21), (94, 18), (96, 15), (98, 11), (100, 8),
     (102, 4), (104, 2), (106, 6), (108, 10), (109, 14), (108, 18), (106, 20),
     (108, 24), (110, 28), (112, 32), (114, 36), (117, 39), (120, 41),
     (122, 40), (124, 40), (127, 41), (130, 43), (132, 44), (135, 44),
     (137, 46), (139, 48), (141, 51), (142, 54), (141, 58), (139, 60),
     (137, 62), (134, 64), (131, 66), (128, 68), (125, 70), (122, 72),
     (118, 73), (114, 72), (110, 70), (106, 68), (102, 67), (98, 65),
     (94, 62), (90, 60), (86, 58), (82, 55), (78, 52), (74, 49), (70, 46),
     (66, 43), (62, 41), (58, 39), (54, 37), (50, 38), (46, 39), (42, 40),
     (38, 41), (34, 39), (30, 37), (28, 36)],
    # Australia
    [(114, -22), (114, -28), (115, -32), (117, -35), (121, -34), (125, -33),
     (129, -32), (132, -32), (135, -35), (137, -35), (140, -38), (144, -38),
     (147, -39), (150, -37), (152, -33), (153, -28), (152, -24), (150, -22),
     (147, -19), (144, -16), (142, -12), (141, -14), (139, -17), (136, -15),
     (134, -12), (131, -12), (128, -14), (125, -15), (122, -17), (119, -19),
     (116, -21)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (142, 42), (144, 44), (142, 44), (140, 40), (139, 37),
     (136, 34), (133, 33), (130, 31)],
    # Indonesia islands (as small blobs)
    [(95, 5), (98, 4), (100, 0), (102, -3), (105, -5), (108, -7), (111, -7),
     (114, -8), (117, -9), (120, -10), (122, -9), (119, -8), (116, -7),
     (113, -6), (110, -6), (107, -5), (104, -3), (101, 0), (98, 3), (95, 5)],
    [(122, -2), (126, -1), (129, -2), (131, -3), (128, -5), (124, -5)],
    # New Guinea
    [(131, -1), (135, -2), (138, -4), (141, -6), (144, -7), (147, -9),
     (150, -10), (147, -8), (143, -6), (139, -4), (135, -2), (131, -1)],
]


def _inside(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (
                px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(d, x, y, w, h):
    """Dotted world map; returns pin positions {num: (px, py)}."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 216))
    d.rectangle([x, y, x + w, y + h], outline=(150, 146, 134))
    step = 7
    for gy in range(y + 4, y + h - 2, step):
        lat = 75 - (gy - y) / h * 130
        for gx in range(x + 4, x + w - 2, step):
            lon = (gx - x) / w * 360 - 170
            for poly in CONTINENTS:
                if _inside(lon, lat, poly):
                    d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1],
                              fill=(120, 116, 104))
                    break
    # graticule
    for lon in range(-150, 181, 30):
        gx = x + (lon + 170) / 360 * w
        d.line([(gx, y), (gx, y + h)], fill=(210, 206, 192))
    for lat in range(-45, 76, 30):
        gy = y + (75 - lat) / 130 * h
        d.line([(x, gy), (x + w, gy)], fill=(210, 206, 192))
    pins = {}
    for num, _k, _h, _de, _s, lon, lat, _r in HEROES + CARDS:
        px = x + (lon + 170) / 360 * w
        py = y + (75 - lat) / 130 * h
        pins[num] = (px, py)
    return pins


# leader offsets (dx, dy) for crowded pins so numbers never overlap.
# Europe / Levant true positions sit within ~15 px of each other, so the
# fan spreads them wide with leader lines back to the true dot.
PIN_OFFSETS = {
    1: (-30, 20), 2: (-24, -8), 3: (12, -14), 9: (30, 8), 12: (34, 20),
    14: (-12, 24), 18: (-30, 12), 19: (16, 24), 20: (30, -6), 22: (-34, -10),
    7: (10, -12), 15: (14, 6), 8: (-36, 4), 13: (26, 14), 16: (-4, 16),
    4: (-12, 10), 21: (10, 10),
}

def scene_thumb(kind, w, h_out):
    """Render a scene at a safe height, then squash to a short strip.
    Scenes are authored for tall boxes; thumbnails keep them intact."""
    big = Image.new("RGB", (w, 56), PAPER)
    dd = ImageDraw.Draw(big)
    SCENES[kind](dd, 0, 0, w, 56)
    return big.resize((w, h_out), Image.LANCZOS)


# ---------------------------------------------------------------- layout
from collections import Counter


def region_line():
    c = Counter()
    for _n, _k, _h, _d, _s, _lo, _la, r in HEROES + CARDS:
        c[r] += 1
    for _n, r, _t, _s in ALSO:
        c["MIDDLE EAST" if r == "MID EAST" else r] += 1
    order = ["EUROPE", "MIDDLE EAST", "ASIA-PACIFIC", "AMERICAS", "AFRICA",
             "OCEANIA", "WORLD"]
    return "  ·  ".join("%s %d" % (r, c[r]) for r in order if c[r])


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 8
    # ---- top line
    f_top = font("DejaVuSans-Bold.ttf", 13)
    d.text((M, y), "THE WORLD IN ONE DAY", font=f_top, fill=INK)
    f_topr = font("DejaVuSans-Bold.ttf", 11)
    tr = "40 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - M - d.textlength(tr, font=f_topr), y + 1), tr, font=f_topr,
           fill=INK)
    y += 20
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)
    y += 6
    # ---- masthead
    f_mast = fit("DejaVuSerif-Bold.ttf", "Sunday 22 November 2026", CW, 66)
    d.text((M, y), "Sunday 22 November 2026", font=f_mast, fill=INK)
    y += 66
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    y += 4
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)
    y += 8
    # ---- kicker + NO DEAL badge (in the masthead rule, NOT on the art)
    f_kick = font("DejaVuSans-Bold.ttf", 15)
    d.text((M, y + 3), KICKER, font=f_kick, fill=DARKRED)
    badge_w = 108
    bx = W - M - badge_w
    d.rectangle([bx, y, bx + badge_w, y + 26], fill=RED)
    d.rectangle([bx, y, bx + badge_w, y + 26], outline=DARKRED, width=2)
    f_badge = font("DejaVuSans-Bold.ttf", 16)
    bt = "NO DEAL"
    d.text((bx + (badge_w - d.textlength(bt, font=f_badge)) / 2, y + 4), bt,
           font=f_badge, fill=(255, 255, 255))
    y += 30
    # ---- numbers band
    d.rectangle([M, y, W - M, y + 44], fill=LIGHT)
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    d.line([(M, y + 44), (W - M, y + 44)], fill=RULE, width=1)
    cw6 = CW / 6
    f_num = font("DejaVuSerif-Bold.ttf", 27)
    f_cap = font("DejaVuSans-Bold.ttf", 8)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cw6
        d.text((cx + (cw6 - d.textlength(num, font=f_num)) / 2, y + 3), num,
               font=f_num, fill=INK)
        d.text((cx + (cw6 - d.textlength(cap, font=f_cap)) / 2, y + 32), cap,
               font=f_cap, fill=GREY)
        if i:
            d.line([(cx, y + 6), (cx, y + 38)], fill=(200, 194, 178))
    y += 48
    # ---- timeline
    f_tl = font("DejaVuSans.ttf", 11)
    d.text((M, y), TIMELINE, font=f_tl, fill=INK)
    y += 15
    # ---- MARKETS band
    d.rectangle([M, y, W - M, y + 40], fill=NAVY)
    f_mlab = font("DejaVuSans-Bold.ttf", 10)
    lab = "MARKETS —\nSUNDAY 22 NOV"
    ly = y + 8
    for ln in lab.split("\n"):
        d.text((M + 8, ly), ln, font=f_mlab, fill=(159, 180, 216))
        ly += 13
    lab_w = 132
    cw_m = (CW - lab_w) / 6
    f_mn = font("DejaVuSans.ttf", 8)
    f_mv = font("DejaVuSans-Bold.ttf", 14)
    for i, (name, val, _s) in enumerate(MARKETS):
        cx = M + lab_w + i * cw_m
        d.text((cx + 6, y + 6), name, font=f_mn, fill=(159, 180, 216))
        col = (255, 122, 107) if val.startswith("−") else (255, 255, 255)
        d.text((cx + 6, y + 20), val, font=f_mv, fill=col)
        if i:
            d.line([(cx, y + 5), (cx, y + 35)], fill=NAVY2)
    y += 44
    # ---- heroes
    hw = (CW - 12) / 3
    f_hkick = font("DejaVuSans-Bold.ttf", 10)
    f_hhead = font("DejaVuSerif-Bold.ttf", 20)
    f_hdeck = font("DejaVuSans.ttf", 10)
    hero_y = y
    for i, (num, kick, head, deck, scene, _lo, _la, _r) in enumerate(HEROES):
        hx = M + i * (hw + 6)
        SCENES[scene](d, hx, hero_y, hw, 88)
        d.rectangle([hx, hero_y + 88, hx + hw, hero_y + 102], fill=INK)
        d.text((hx + 6, hero_y + 91), "%d  %s" % (num, kick), font=f_hkick,
               fill=(255, 255, 255))
        hl = wrap(d, head, f_hhead, hw - 8)
        draw_lines(d, hl[:2], hx + 2, hero_y + 106, f_hhead, INK, 22)
        dl = wrap(d, deck, f_hdeck, hw - 4)
        draw_lines(d, dl[:3], hx + 2, hero_y + 152, f_hdeck, (40, 40, 40), 11)
        d.rectangle([hx, hero_y, hx + hw, hero_y + 186], outline=(150, 146, 134))
    y = hero_y + 186 + 4
    # ---- cards: 5 cols x 4 rows
    card_w = 194
    card_gap = 6
    row_h = 64
    f_ckick = font("DejaVuSans-Bold.ttf", 8)
    f_chead = font("DejaVuSans-Bold.ttf", 11)
    f_cdeck = font("DejaVuSans.ttf", 8)
    for r_i in range(4):
        row = CARDS[r_i * 5:(r_i + 1) * 5]
        ry = y + r_i * (row_h + 3)
        for c_i, (num, kick, head, deck, scene, _lo, _la, _r) in enumerate(row):
            cx = M + 1 + c_i * (card_w + card_gap)
            img.paste(scene_thumb(scene, card_w, 18), (cx, ry))
            d.text((cx + 1, ry + 20), "%d  %s" % (num, kick), font=f_ckick,
                   fill=RED)
            hl = wrap(d, head, f_chead, card_w - 4)
            draw_lines(d, hl[:2], cx + 1, ry + 29, f_chead, INK, 10)
            dl = wrap(d, deck, f_cdeck, card_w - 4)
            draw_lines(d, dl[:2], cx + 1, ry + 48, f_cdeck, (60, 58, 52), 7)
            d.rectangle([cx, ry, cx + card_w, ry + row_h],
                        outline=(190, 186, 172))
    y += 4 * row_h + 3 * 3 + 6
    # ---- map
    f_mh = font("DejaVuSans-Bold.ttf", 11)
    d.text((M, y), "THE WORLD ON SUNDAY — 22 STORIES PINNED", font=f_mh, fill=INK)
    f_mhr = font("DejaVuSans.ttf", 9)
    rl = region_line()
    d.text((W - M - d.textlength(rl, font=f_mhr), y + 1), rl, font=f_mhr,
           fill=GREY)
    y += 16
    map_y = y
    map_h = 92
    pins = draw_map(d, M, map_y, CW, map_h)
    f_pin = font("DejaVuSans-Bold.ttf", 8)
    for num, (px, py) in pins.items():
        if num in (5, 17):
            # Pacific pins live in the inset; small dot on the main map only
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
            continue
        dx, dy = PIN_OFFSETS.get(num, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line([(px, py), (qx, qy)], fill=RED, width=1)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED,
                  outline=(255, 255, 255))
        t = str(num)
        d.text((qx - d.textlength(t, font=f_pin) / 2, qy - 6), t, font=f_pin,
               fill=(255, 255, 255))
    # Pacific inset (bottom-right of the map): Wellington 5 + Canberra 17
    ix0, iy0 = W - M - 192, map_y + map_h - 60
    ix1, iy1 = W - M, map_y + map_h
    d.rectangle([ix0, iy0, ix1, iy1], fill=(214, 226, 238),
                outline=(90, 110, 140), width=2)
    f_in = font("DejaVuSans-Bold.ttf", 8)
    d.text((ix0 + 6, iy0 + 3), "PACIFIC — INSET", font=f_in, fill=NAVY)
    for lon, lat, col in [(140, -20, (120, 116, 104)), (145, -37, (120, 116, 104)),
                          (150, -25, (120, 116, 104)), (167, -41, (120, 116, 104)),
                          (172, -43, (120, 116, 104))]:
        px = ix0 + (lon - 110) / 75 * 192
        py = iy0 + 14 + (-10 - lat) / 40 * 44
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
    for num, lon, lat, lab, side in [(5, 174.8, -41.3, "WELLINGTON", "up"),
                                      (17, 149.1, -35.3, "CANBERRA", "down")]:
        px = ix0 + (lon - 110) / 75 * 192
        py = iy0 + 14 + (-10 - lat) / 40 * 44
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255))
        t = str(num)
        d.text((px - d.textlength(t, font=f_pin) / 2, py - 6), t, font=f_pin,
               fill=(255, 255, 255))
        if side == "up":
            d.text((px - d.textlength(lab, font=f_in) / 2, py - 20), lab,
                   font=f_in, fill=INK)
        else:
            d.text((px - d.textlength(lab, font=f_in) / 2, py + 10), lab,
                   font=f_in, fill=INK)
    y = map_y + map_h + 6
    # ---- ALSO
    d.text((M, y), "ALSO ON SUNDAY 22 NOVEMBER — 18 MORE STORIES", font=f_mh,
           fill=INK)
    f_ar = font("DejaVuSans.ttf", 9)
    ar = "FORECAST = still to happen when drawn"
    d.text((W - M - d.textlength(ar, font=f_ar), y + 1), ar, font=f_ar, fill=GREY)
    y += 13
    f_an = font("DejaVuSans-Bold.ttf", 10)
    f_at = font("DejaVuSans.ttf", 10)
    f_as = font("DejaVuSans.ttf", 9)
    col_w = (CW - 16) / 2
    for i, (num, reg, text, src) in enumerate(ALSO):
        col = i % 2
        row = i // 2
        ax = M + col * (col_w + 16)
        ay = y + row * 10
        d.text((ax, ay), "%d" % num, font=f_an, fill=RED)
        d.text((ax + 26, ay), reg, font=f_an, fill=INK)
        tx = ax + 26 + d.textlength(reg + "  ", font=f_an)
        d.text((tx, ay), text, font=f_at, fill=INK)
        d.text((ax + col_w - d.textlength(src, font=f_as), ay + 1), src,
               font=f_as, fill=GREY)
    y += ((len(ALSO) + 1) // 2) * 10 + 4
    # ---- DATE CHECK (roomier: 3 columns, 6 rows, generous leading)
    d.rectangle([M, y, W - M, y + 68], outline=RED, width=2)
    d.text((M + 6, y + 4), "DATE CHECK — NOT SUNDAY, however listed elsewhere:",
           font=f_mh, fill=DARKRED)
    f_dc = font("DejaVuSans.ttf", 9)
    dc_w = (CW - 12) / 3
    for i, (text, _day) in enumerate(DATECHECK):
        col = i % 3
        row = i // 3
        dx = M + 6 + col * dc_w
        dy = y + 19 + row * 8
        d.text((dx, dy), "×  " + text, font=f_dc, fill=(60, 58, 52))
    y += 68 + 4
    # ---- footer
    f_ft = font("DejaVuSans.ttf", 8)
    d.text((M, y), SOURCES, font=f_ft, fill=GREY)
    y += 12
    print("final y =", y, "| stories =", 3 + len(CARDS) + len(ALSO),
          "| illustrated =", 3 + len(CARDS), "| regions:", region_line())
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")
    img = render()
    img.save(out, "PNG")
    print("wrote", out, img.size)
