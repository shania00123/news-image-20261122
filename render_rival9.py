#!/usr/bin/env python3
"""Render RIVAL9 — 'THE SUNDAY RECORD' for news-image-20261122.

Built from scratch (PIL only) for round 9 of the LAWAN-ADU loop.
Opponent: RIVAL8 (commit 5ced8477). Changes vs RIVAL8:
  1. COP31 overtime 44h -> 48h (stat band + hero 1 kicker + deck).
  2. DATE CHECK: new trap '148-drone night / Kryvyi Rih double-tap
     — Fri 20–Sat 21 Nov' replaces weakest item (Senate $350bn).
  3. Disambiguation in hero 2 deck: 'Tonight: 186 drones, not 400.'
  4. Hero 2 (Kyiv) art redrawn with depth: layered skyline, haze,
     smoke column, searchlight beams, moon halo.
  5. Map band ~12px shorter; DATE CHECK gets the room (line-height up).
  6. Varied mini illustrations on the top grid cards (4-8) + a few more.
Everything else inherits RIVAL8's verified facts (37 stories, 22 pins,
MARKETS 6 figures, labels + HOW TO READ legend).
Deterministic: no randomness, no network, no time dependence.
Usage: python3 render_rival9.py [output_path]   (default: poster.png)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 227)
INK = (26, 26, 26)
RED = (176, 30, 36)
RED_DK = (140, 22, 28)
NAVY = (30, 42, 82)
NAVY_DK = (22, 32, 64)
GOLD = (176, 138, 20)
GREY = (105, 100, 88)
GREY_LT = (150, 144, 128)
RULE = (120, 112, 96)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SYM_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns y just below last line."""
    if leading is None:
        leading = int(fnt.size * 1.18)
    lines = wrap(d, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def badge(d, x, y, text, fill=RED, fg=(255, 255, 255), fnt=None):
    """Small filled badge; returns its width."""
    fnt = fnt or font(F_SANS_B, 9)
    w = int(d.textlength(text, font=fnt)) + 10
    h = 13
    d.rectangle([x, y, x + w, y + h], fill=fill)
    d.text((x + 5, y + 2), text, font=fnt, fill=fg)
    return w


def kicker_row(d, x, y, width, left_text, badge_text, badge_fill=RED):
    """Red kicker left, badge right-aligned."""
    fnt = font(F_SANS_B, 11)
    d.text((x, y), left_text, font=fnt, fill=RED)
    bw = int(d.textlength(badge_text, font=font(F_SANS_B, 9))) + 10
    badge(d, x + width - bw, y - 1, badge_text, fill=badge_fill)


# ---------------------------------------------------------------- data
STAT_BAND = [
    ("48h", "COP31 OVERTIME"),
    ("186", "DRONES AT UKRAINE"),
    ("161", "DOWNED OR JAMMED"),
    ("720/9", "INDIA'S TEST TOTAL"),
    ("$61,568", "BITCOIN SUNDAY HIGH"),
    ("98.79%", "HK TURNOUT, RECORD"),
]

MARKETS = [
    ("GOLD · PER OZ", "$3,539", None),
    ("BITCOIN · SUNDAY HIGH", "$61,568", None),
    ("TASI · RIYADH", "9,960.44", "-1.95%"),
    ("QATAR · DOHA", "9,902.87", "-1.59%"),
    ("EGX30 · CAIRO", "49,989.79", "-2.85%"),
    ("EGX70 · CAIRO", "16,534.42", "-5.55%"),
]

TIMELINE = ("THE DAY IN UTC — 03:00 COP31 objections close · 05:30 Verstappen "
            "wins Vegas · 06:00 COP31 approval due · 09:29 Hamas seeks talks · "
            "14:15 HK count done")

HEROES = [
    dict(num=1, place="ANTALYA", kick="48 HOURS OVERTIME", badge="REPORTED",
         bf=RED,
         head="COP31 collapses with no deal",
         deck=("The EU, UK and Panama rejected a final text that omitted fossil "
               "fuels — the first breakdown since COP15 in 2009. The EU walked out.")),
    dict(num=2, place="KYIV REGION", kick="186 DRONES", badge="REPORTED",
         bf=RED,
         head="Russia fires 186 drones; Dymer block destroyed",
         deck=("161 downed or jammed; 72 jet-powered. One destroyed a "
               "five-storey block in Dymer; 2 dead, 14 missing."),
         extra="Tonight: 186 drones, not 400."),
    dict(num=3, place="MANAMA", kick="CLAIM", badge="CLAIM",
         bf=GOLD,
         head="Iran claims two US radars hit; Bahrain denies it",
         deck=("IRGC media claimed Saturday-night strikes hit two US Patriot "
               "radars; Bahrain says it intercepted them. Two hurt; a civilian "
               "plant burned.")),
]

# grid cards: (num, place, badge, badge_fill, headline, deck, strip motif)
GRID = [
    (4, "HONG KONG", "REPORTED", RED, "Hong Kong turnout hits record 98.79%",
     "5,640 of 5,709 voted; count done 22:15. Beats 89.77% in 2021.", "ballot"),
    (5, "WELLINGTON", "REPORTED", RED, "India declare 720/9 — a record in NZ",
     "Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.", "cricket"),
    (6, "LAS VEGAS", "REPORTED", RED, "Verstappen wins Vegas by 0.639s",
     "75th career win; Norris 2nd, Piastri 3rd from 17th.", "chequer"),
    (7, "SEOUL", "REPORTED", RED, "Seoul minister quits over AI exam scandal",
     "Choi Kyo-jin resigned; Lee accepted in an hour. 111 cheating cases probed.", "exam"),
    (8, "FINLAND", "REPORTED", RED, "Sparta II still burning off Finland",
     "Struck Sat; fire smouldered Sun. Helo breached Finnish airspace by 4.1 km.", "ship"),
    (9, "KRYVYI RIH", "REPORTED", RED, "Missile kills boy, 7, and medic, 20; 58 hurt",
     "Hometown strike; four fires, ~23 blocks hit, hospital and schools damaged.", "warn"),
    (10, "SAN ANTONIO", "REPORTED", RED, "Wembanyama drops 50 as Spurs rout Pelicans",
     "San Antonio's star scores 50 in a 114-91 rout of New Orleans.", "ball"),
    (11, "CIKANDE", "REPORTED", RED, "Candy-factory fire: 3 dead, 36 missing",
     "Blaze broke out Saturday 17:00; search went on Sunday; 300 workers inside.", "flame"),
    (12, "GAZA", "REPORTED", RED, "Hamas seeks urgent talks after aid-van strike",
     "Aid-van strike killed workers Sat; Hamas seeks urgent talks on aid access.", "talks"),
    (13, "BAYELSA", "REPORTED", RED, "Nigeria boat toll reaches 24",
     "Capsized Friday; Ayama-Ukubie; 24 dead, 24 rescued. Manager held.", "waves"),
    (14, "VATICAN", "REPORTED", RED, "Pope Leo XIV hosts 1,300 for lunch",
     "10th World Day of the Poor; lunch in Paul VI Hall, a week of events.", "dome"),
    (15, "FUKUSHIMA", "REPORTED", RED, "1,500 still cut off by Japan landslide",
     "Stranded in Kitashiobara since Saturday; heavy rain hampered rescue.", "mount"),
    (16, "MINDANAO", "REPORTED", RED, "M6.0 quake off Mindanao; no damage",
     "Off southern Mindanao, 15:54 local, depth 10 km. No tsunami.", "seismo"),
    (17, "CANBERRA", "REPORTED", RED, "Albanese: US report 'wrong' on AUKUS",
     "Defence minister rejects CBO warning on subs cost; US $368bn programme.", "sub"),
    (18, "TURIN", "FORECAST", GOLD, "Zverev v Alcaraz in Turin final today",
     "ATP Finals title match closes the season in Turin.", "tennis"),
    (19, "WARSAW", "FORECAST", GOLD, "NATO to meet Monday over Poland incursion",
     "Drone debris confirmed in Nowy Lipowiec. Council meets Monday.", "star"),
    (20, "TALLINN", "REPORTED", RED, "Moscow vows retaliation as Estonia seals border",
     "Estonia seals crossings for months; Moscow calls it a new Iron Curtain.", "fence"),
    (21, "DELHI", "REPORTED", RED, "Nepal PM Shah lands in Delhi",
     "First foreign trip; talks with Modi on Monday.", "plane"),
    (22, "LIVERPOOL", "REPORTED", RED, "Liverpool rout Man Utd 4–0 on Pochettino debut",
     "Szoboszlai 10', Wirtz 13', Ngumoha 66', Muñoz 82'. Yoro off 8'; United 19th.", "score"),
]

ALSO = [
    (23, "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv", ""),
    (24, "WORLD", "Russia says it downed 170 Ukrainian drones overnight", "Moscow", "○ CLAIM"),
    (25, "WORLD", "Bitcoin back above $60,000 after Saturday's $55,130 low", "Coinbase", ""),
    (26, "AMERICAS", "San Francisco braces for record king tides", "NWS", "○ FORECAST"),
    (27, "MIDDLE EAST", "US denies Iran claim it downed two US radars", "CENTCOM", "○ CLAIM"),
    (28, "EUROPE", "Lebanon marks 83rd Independence Day", "Beirut", ""),
    (29, "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children", "W. Kordofan", ""),
    (30, "AFRICA", "S. Africa holds service for Mlambo-Ngcuka, 71 (died Fri)", "SABC", ""),
    (31, "MIDDLE EAST", "Iraq: fire at Hartha power station kills 4, injures 35", "Basra", "† SAT"),
    (32, "EUROPE", "Moldova: Russian drone crosses border twice near Purcari", "Chisinau", "† SAT"),
    (33, "AFRICA", "Somalia: UAE envoy's 72 hours run out today (ordered Thu)", "Mogadishu", ""),
    (34, "ASIA-PACIFIC", "Manipur liquor toll 19, 600+ in hospital — Sun a.m., still rising", "Imphal", ""),
    (35, "ASIA-PACIFIC", "M5.3 Celebes Sea, 61 km, 07:54 UTC", "EMSC", ""),
    (36, "AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "Brasilia", ""),
    (37, "EUROPE", "Hull 2–0 Brighton", "MKM", ""),
]

DATE_CHECK = [
    # column 1 (8)
    ["Peru quake — Fri 20 Nov",
     "Gaza aid-van strike — Sat 21 Nov",
     "Japan poll: 62% feel affinity to Korea — Fri 20 Nov",
     "Mlambo-Ngcuka dies — Fri 20 Nov",
     "EU–Indonesia deal — Sat 21 Nov",
     "Denmark expels Russian attaché — Fri 20 Nov",
     "Qatar talks in Tehran — Fri 20 Nov",
     "Russia's 400-drone barrage — night of 19–20 Nov"],
    # column 2 (7) — NEW trap replaces 'Senate $350bn defence push stalls'
    ["BepiColombo at Mercury — Sat 21 Nov",
     "Sparta II struck — Sat 21 Nov",
     "Newcastle 2–2 Arsenal; Chelsea 1–4 Leeds — Sat 21 Nov",
     "DR Congo Cantine attack — night of 5–6 Nov",
     "Estonia closes border — decided Fri 20 Nov",
     "UK–EU food deal agreed — Fri 20 Nov",
     "148-drone night / Kryvyi Rih double-tap — Fri 20–Sat 21 Nov"],
    # column 3 (7)
    ["ICJ Myanmar ruling — Thu 19 Nov",
     "Bayelsa boat capsizes — Fri 20 Nov",
     "Aoun's Israel-withdrawal speech — Sat 21 Nov",
     "Nvidia SEC probe — Fri 20 Nov",
     "'El Chapo Isidro' captured — Fri 20 Nov",
     "Trump–Xi–Putin talks — Thu 19 Nov",
     "H-6 bomber nears Manila — Sat 21 Nov"],
]

FOOTER = ("Sources: Reuters · AP · AFP · Al Jazeera · BBC · The Times · Formula 1 · "
          "Cricinfo · PHIVOLCS · Vatican News · ONA · Saudi Exchange · EGX — "
          "verified vs Sunday 22 Nov 2026.")

# ---------------------------------------------------------------- mini strips
STRIP_COLORS = [
    (31, 56, 100), (36, 110, 70), (122, 84, 40), (88, 62, 130), (18, 110, 110),
    (122, 84, 40), (40, 44, 52), (122, 60, 40), (60, 60, 60), (122, 84, 40),
    (96, 62, 130), (18, 110, 110), (122, 84, 40), (60, 60, 60), (122, 84, 40),
    (122, 84, 40), (31, 56, 100), (31, 56, 100), (36, 110, 70), (122, 84, 40),
]

STRIP_FG = (240, 235, 220)


def draw_strip(d, x, y, w, h, motif, color, card_no):
    """12px illustrated mini-strip on top of a grid card."""
    d.rectangle([x, y, x + w, y + h], fill=color)
    fg = STRIP_FG
    if motif == "ballot":  # ballot boxes + ticks
        for i, bx in enumerate([x + 10, x + 34, x + 58]):
            d.rectangle([bx, y + 3, bx + 16, y + 9], outline=fg, width=1)
            d.line([bx + 3, y + 6, bx + 6, y + 8, bx + 13, y + 4], fill=fg, width=1)
        d.ellipse([x + w - 16, y + 2, x + w - 6, y + 10], fill=(176, 30, 36))
    elif motif == "cricket":  # stumps + ball
        for sx in (x + 14, x + 20, x + 26):
            d.rectangle([sx, y + 2, sx + 2, y + 10], fill=fg)
        d.rectangle([x + 13, y + 1, x + 29, y + 3], fill=fg)
        d.ellipse([x + w - 18, y + 2, x + w - 8, y + 10], fill=(176, 30, 36))
        d.line([x + 40, y + 10, x + w - 20, y + 3], fill=fg, width=1)
    elif motif == "chequer":  # checkered flag
        for r in range(2):
            for c in range(8):
                if (r + c) % 2 == 0:
                    d.rectangle([x + 8 + c * 5, y + 2 + r * 5,
                                 x + 12 + c * 5, y + 6 + r * 5], fill=fg)
        d.rectangle([x + 52, y + 2, x + 54, y + 10], fill=fg)
    elif motif == "exam":  # paper + pencil
        d.rectangle([x + 10, y + 2, x + 26, y + 10], outline=fg, width=1)
        for ly in (4, 6, 8):
            d.line([x + 13, y + ly, x + 23, y + ly], fill=fg, width=1)
        d.line([x + 34, y + 10, x + 46, y + 2], fill=(240, 200, 60), width=2)
    elif motif == "ship":  # ship + flame
        d.polygon([(x + 12, y + 9), (x + 40, y + 9), (x + 34, y + 4), (x + 18, y + 4)],
                  fill=fg)
        d.rectangle([x + 24, y + 1, x + 26, y + 4], fill=fg)
        d.polygon([(x + w - 18, y + 10), (x + w - 12, y + 2), (x + w - 6, y + 10)],
                  fill=(240, 140, 40))
    elif motif == "warn":  # warning triangle
        d.polygon([(x + 16, y + 1), (x + 28, y + 10), (x + 4, y + 10)],
                  outline=(240, 200, 60), width=2)
        d.text((x + 14, y + 4), "!", font=font(F_SANS_B, 7), fill=(240, 200, 60))
    elif motif == "ball":  # basketball
        d.ellipse([x + 10, y + 1, x + 22, y + 11], outline=fg, width=1)
        d.line([x + 16, y + 1, x + 16, y + 11], fill=fg, width=1)
        d.arc([x + 10, y + 1, x + 22, y + 11], 300, 60, fill=fg, width=1)
    elif motif == "flame":
        d.polygon([(x + 16, y + 11), (x + 10, y + 5), (x + 16, y + 7),
                   (x + 18, y + 1), (x + 24, y + 8), (x + 20, y + 11)],
                  fill=(240, 140, 40))
    elif motif == "talks":  # speech bubbles
        d.rounded_rectangle([x + 8, y + 2, x + 26, y + 8], radius=2, outline=fg, width=1)
        d.rounded_rectangle([x + 30, y + 4, x + 48, y + 10], radius=2, outline=fg, width=1)
    elif motif == "waves":
        for wy in (4, 8):
            for k in range(6):
                d.arc([x + 8 + k * 12, y + wy - 3, x + 18 + k * 12, y + wy + 3],
                      180, 360, fill=fg, width=1)
    elif motif == "dome":  # basilica dome + cross
        d.arc([x + 10, y + 3, x + 26, y + 11], 180, 360, fill=fg, width=2)
        d.line([x + 18, y - 0, x + 18, y + 3], fill=fg, width=1)
        d.line([x + 15, y + 1, x + 21, y + 1], fill=fg, width=1)
    elif motif == "mount":
        d.polygon([(x + 6, y + 11), (x + 20, y + 1), (x + 34, y + 11)], fill=fg)
        d.polygon([(x + 16, y + 5), (x + 20, y + 1), (x + 24, y + 5)], fill=color)
    elif motif == "seismo":
        pts = [(x + 6, y + 6), (x + 12, y + 6), (x + 16, y + 2), (x + 20, y + 10),
               (x + 24, y + 4), (x + 28, y + 6), (x + 40, y + 6)]
        d.line(pts, fill=fg, width=1)
    elif motif == "sub":  # submarine
        d.rounded_rectangle([x + 8, y + 4, x + 34, y + 9], radius=2, fill=fg)
        d.rectangle([x + 16, y + 1, x + 22, y + 4], fill=fg)
        d.line([x + 34, y + 6, x + 40, y + 6], fill=fg, width=1)
    elif motif == "tennis":
        d.ellipse([x + 10, y + 1, x + 22, y + 11], outline=fg, width=1)
        d.arc([x + 10, y + 1, x + 22, y + 11], 300, 60, fill=fg, width=1)
        d.arc([x + 10, y + 1, x + 22, y + 11], 120, 240, fill=fg, width=1)
    elif motif == "star":  # NATO compass star
        cx, cy = x + 16, y + 6
        d.polygon([(cx, cy - 5), (cx + 2, cy - 2), (cx + 5, cy), (cx + 2, cy + 2),
                   (cx, cy + 5), (cx - 2, cy + 2), (cx - 5, cy), (cx - 2, cy - 2)],
                  fill=fg)
    elif motif == "fence":
        for fx in range(x + 8, x + w - 8, 8):
            d.line([fx, y + 2, fx, y + 10], fill=fg, width=1)
        d.line([x + 6, y + 4, x + w - 6, y + 4], fill=fg, width=1)
        d.line([x + 6, y + 8, x + w - 6, y + 8], fill=fg, width=1)
    elif motif == "plane":
        d.polygon([(x + 8, y + 6), (x + 26, y + 2), (x + 26, y + 5), (x + 38, y + 5),
                   (x + 38, y + 7), (x + 26, y + 7), (x + 26, y + 10), (x + 8, y + 6)],
                  fill=fg)
    elif motif == "score":  # 4-0 full time strip
        d.rectangle([x, y, x + w, y + h], fill=RED)
        d.text((x + 6, y + 1), "4-0  FULL TIME", font=font(F_SANS_B, 9),
               fill=(255, 255, 255))
    else:  # generic: dotted line
        for dx in range(x + 8, x + w - 8, 10):
            d.ellipse([dx, y + 5, dx + 2, y + 7], fill=fg)


# ---------------------------------------------------------------- hero art
def hero_cop31(d, x, y, w, h):
    """COP31 final plenary: delegates, screen, WALKOUT banner, 3 empty chairs."""
    d.rectangle([x, y, x + w, y + h], fill=(146, 108, 66))
    d.rectangle([x, y, x + w, y + 26], fill=(122, 88, 52))
    # screen
    sx, sy, sw, sh = x + w // 2 - 78, y + 2, 156, 32
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=(245, 240, 228))
    d.rectangle([sx, sy, sx + sw, sy + sh], outline=(60, 40, 20), width=1)
    d.text((sx + 8, sy + 2), "COP31 · ANTALYA", font=font(F_SANS_B, 13),
           fill=(176, 30, 36))
    d.text((sx + 8, sy + 17), "FINAL PLENARY", font=font(F_SANS_B, 12), fill=INK)
    # delegate rows: heads + shoulders, varied skin tones / suits.
    # Left of the WALKOUT/chairs block only (cx <= x + w - 110).
    skins = [(232, 190, 150), (200, 150, 110), (160, 110, 75), (240, 205, 170),
             (180, 130, 95)]
    suits = [(40, 60, 100), (90, 40, 40), (50, 90, 60), (120, 90, 30),
             (70, 70, 70), (30, 100, 110), (130, 60, 90)]
    for row, ry in enumerate((38, 54, 70)):
        for col in range(6):
            cx = x + 16 + col * 32 + (10 if row % 2 else 0)
            ay = y + ry
            tone = skins[(row * 3 + col) % len(skins)]
            suit = suits[(row + col * 2) % len(suits)]
            d.ellipse([cx - 6, ay, cx + 6, ay + 11], fill=tone)
            d.rounded_rectangle([cx - 9, ay + 11, cx + 9, ay + 20], radius=3,
                                fill=suit)
            d.rectangle([cx - 6, ay + 13, cx + 6, ay + 16], fill=(245, 240, 228))
    # desks
    d.rectangle([x, y + 56, x + w, y + 60], fill=(90, 62, 36))
    d.rectangle([x, y + 76, x + w, y + 80], fill=(90, 62, 36))
    # WALKOUT banner (right)
    bx, by = x + w - 96, y + 40
    d.rectangle([bx, by, bx + 92, by + 20], fill=RED)
    d.text((bx + 6, by + 4), "WALKOUT", font=font(F_SANS_B, 12), fill=(255, 255, 255))
    # 3 empty chairs under banner
    for i in range(3):
        cx = bx + 10 + i * 30
        d.rectangle([cx, by + 30, cx + 20, by + 44], fill=(40, 28, 18))
        d.rectangle([cx + 2, by + 44, cx + 18, by + 46], fill=(40, 28, 18))
        d.rectangle([cx + 4, by + 26, cx + 16, by + 30], fill=(245, 240, 228))


def hero_kyiv(d, x, y, w, h):
    """Kyiv night, redrawn with depth: haze, 3 skyline layers, smoke,
    searchlight beams, moon halo, explosion glow."""
    # sky gradient (dark navy, lighter near horizon)
    for yy in range(h):
        t = yy / max(h - 1, 1)
        r = int(10 + 14 * t)
        g = int(14 + 16 * t)
        b = int(42 + 26 * t)
        d.line([(x, y + yy), (x + w, y + yy)], fill=(r, g, b))
    # stars
    for sx, sy in [(18, 8), (52, 20), (96, 6), (150, 14), (210, 8), (260, 18),
                   (300, 6), (120, 26), (240, 28), (70, 30)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(220, 220, 200))
    # moon + halo (top right)
    mx, my = x + w - 52, y + 12
    for rr, col in [(26, (60, 66, 100)), (20, (90, 96, 130)), (15, (200, 198, 180))]:
        d.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=col)
    d.ellipse([mx - 13, my - 13, mx + 13, my + 13], fill=(232, 228, 205))
    d.ellipse([mx - 5, my - 6, mx + 1, my + 0], fill=(205, 200, 175))
    d.ellipse([mx + 2, my + 3, mx + 7, my + 8], fill=(205, 200, 175))
    # searchlight beams (pale translucent triangles from ground)
    for bx0, bx1, top in [(30, 70, 8), (w - 90, w - 40, 4), (w // 2 + 40, w // 2 + 90, 12)]:
        d.polygon([(x + bx0, y + h), (x + bx1, y + h), (x + (bx0 + bx1) // 2, y + top)],
                  fill=(120, 128, 160))
    # explosion glow (centre-left, behind mid skyline)
    gx, gy = x + w // 2 - 30, y + h - 52
    for rr, col in [(44, (120, 60, 20)), (34, (200, 110, 30)), (24, (245, 170, 60)),
                    (15, (255, 210, 110))]:
        d.ellipse([gx - rr, gy - rr // 2, gx + rr, gy + rr // 2], fill=col)
    # smoke column rising from glow (kept inside the art rect)
    for i, (sx, sy, sr) in enumerate([(gx - 6, gy - 16, 8), (gx + 4, gy - 26, 10),
                                      (gx - 2, gy - 36, 10)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(70, 70, 78))
    # far skyline (hazy, lighter navy, sparse windows)
    far = [(0, 46, 34, 60), (40, 58, 30, 48), (78, 40, 44, 66), (130, 52, 36, 54),
           (176, 44, 30, 62), (214, 56, 40, 50), (262, 42, 34, 64), (300, 54, 12, 52)]
    for fx, fh, fw, _ in far:
        d.rectangle([x + fx, y + h - fh, x + fx + fw, y + h], fill=(52, 58, 92))
        for wy in range(y + h - fh + 6, y + h - 4, 10):
            for wx in range(x + fx + 4, x + fx + fw - 3, 9):
                if (wx + wy) % 23 < 6:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(150, 140, 100))
    # mid skyline (darker, more windows)
    mid = [(14, 66, 40), (62, 78, 36), (106, 70, 30), (144, 82, 44),
           (196, 72, 34), (238, 80, 40), (286, 68, 26)]
    for fx, fh, fw in mid:
        d.rectangle([x + fx, y + h - fh, x + fx + fw, y + h], fill=(28, 32, 58))
        for wy in range(y + h - fh + 6, y + h - 4, 9):
            for wx in range(x + fx + 4, x + fx + fw - 3, 8):
                if (wx * 3 + wy) % 17 < 7:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(245, 200, 90))
    # near skyline (near-black, bright windows)
    near = [(0, 52, 30), (44, 60, 26), (120, 56, 30), (200, 62, 28), (268, 54, 44)]
    for fx, fh, fw in near:
        d.rectangle([x + fx, y + h - fh, x + fx + fw, y + h], fill=(12, 14, 26))
        for wy in range(y + h - fh + 6, y + h - 4, 8):
            for wx in range(x + fx + 4, x + fx + fw - 3, 7):
                if (wx + wy * 2) % 13 < 6:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 214, 110))
    # drone silhouettes (small, with red dot)
    for dx, dy in [(x + 60, y + 22), (x + 230, y + 34)]:
        d.ellipse([dx - 4, dy - 1, dx + 4, dy + 1], fill=(8, 8, 12))
        d.ellipse([dx - 1, dy - 1, dx + 1, dy + 1], fill=(220, 40, 40))


def hero_manama(d, x, y, w, h):
    """Manama night: radar dishes, fire glow, sea with scallop waves."""
    for yy in range(h):
        t = yy / max(h - 1, 1)
        r = int(16 + 10 * t)
        g = int(14 + 8 * t)
        b = int(40 + 14 * t)
        d.line([(x, y + yy), (x + w, y + yy)], fill=(r, g, b))
    # moon
    mx, my = x + w - 46, y + 14
    d.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=(228, 222, 196))
    # skyline + radar dishes
    roofs = [(0, 48, 44), (52, 62, 40), (100, 54, 36), (144, 66, 44),
             (196, 58, 38), (242, 50, 40), (290, 60, 22)]
    for fx, fh, fw in roofs:
        d.rectangle([x + fx, y + h - 30 - fh, x + fx + fw, y + h - 30],
                    fill=(14, 16, 30))
        for wy in range(y + h - 30 - fh + 6, y + h - 32, 9):
            for wx in range(x + fx + 5, x + fx + fw - 4, 9):
                if (wx + wy) % 19 < 7:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(245, 200, 90))
    for dx, dy, dr in [(x + 22, y + 18, 12), (x + 168, y + 12, 13), (x + 268, y + 16, 12)]:
        d.line([dx, dy + dr, dx, dy + dr + 14], fill=(200, 200, 200), width=2)
        d.arc([dx - dr, dy - dr, dx + dr, dy + dr], 200, 340, fill=(220, 220, 220),
              width=3)
        d.line([dx - dr, dy, dx + dr, dy], fill=(220, 220, 220), width=2)
    # fire glow on horizon
    gx, gy = x + w // 2, y + h - 34
    for rr, col in [(40, (120, 55, 18)), (30, (205, 110, 30)), (20, (245, 165, 55)),
                    (12, (255, 205, 100))]:
        d.ellipse([gx - rr, gy - rr // 2, gx + rr, gy + rr // 2], fill=col)
    d.polygon([(gx - 14, gy + 2), (gx - 4, gy - 16), (gx + 6, gy + 2)],
              fill=(255, 220, 120))
    d.polygon([(gx + 2, gy + 2), (gx + 10, gy - 12), (gx + 18, gy + 2)],
              fill=(245, 170, 60))
    # sea: scallop waves + vertical reflections
    sea_y = y + h - 30
    d.rectangle([x, sea_y, x + w, y + h], fill=(18, 42, 78))
    for wy in (sea_y + 6, sea_y + 14, sea_y + 22):
        for k in range(0, w // 16 + 1):
            d.arc([x + k * 16, wy - 4, x + k * 16 + 16, wy + 4], 0, 180,
                  fill=(140, 170, 210), width=1)
    for rx in (gx - 10, gx + 4, gx + 16):
        d.line([(rx, sea_y + 2), (rx, sea_y + 24)], fill=(245, 190, 90), width=2)

# ---------------------------------------------------------------- page sections
def draw_masthead(d):
    d.text((26, 8), "THE SUNDAY RECORD — THE WORLD IN ONE DAY",
           font=font(F_SANS_B, 11), fill=INK)
    right = "37 STORIES · 7 REGIONS · EVERY DATE CHECKED · SUNDAY 22 NOVEMBER 2026"
    f = font(F_SANS, 10)
    d.text((W - 26 - d.textlength(right, font=f), 9), right, font=f, fill=GREY)
    d.text((26, 26), "Sunday 22 November 2026",
           font=font(F_SERIF, 54), fill=INK)
    # red kicker line + NO DEAL badge
    kick = ("COP31 collapses with no deal · Russia fires 186 drones · "
            "Iran claims two US radars hit")
    d.text((26, 90), kick, font=font(F_SANS_B, 13), fill=RED)
    bw = 74
    d.rectangle([W - 26 - bw, 88, W - 26, 106], fill=RED)
    d.text((W - 26 - bw + 8, 91), "NO DEAL", font=font(F_SANS_B, 12),
           fill=(255, 255, 255))
    d.line([(26, 112), (W - 26, 112)], fill=RULE, width=1)


def draw_stat_band(d):
    y0, y1 = 118, 150
    cell_w = (W - 52) / 6
    for i, (num, label) in enumerate(STAT_BAND):
        cx = 26 + i * cell_w
        d.text((cx + 4, y0), num, font=font(F_SERIF, 24), fill=INK)
        d.text((cx + 4, y0 + 26), label, font=font(F_SANS_B, 8), fill=GREY)
        if i:
            d.line([(cx, y0 + 2), (cx, y1 - 2)], fill=RULE, width=1)
    d.line([(26, y1 + 4), (W - 26, y1 + 4)], fill=RULE, width=1)


def draw_timeline(d):
    d.text((26, 160), TIMELINE, font=font(F_SANS, 10), fill=INK)


def draw_markets(d):
    y0, h = 172, 25
    d.rectangle([26, y0, W - 26, y0 + h], fill=NAVY)
    d.text((34, y0 + 7), "MARKETS", font=font(F_SANS_B, 11), fill=(255, 255, 255))
    cell_w = (W - 52 - 110) / 6
    for i, (label, value, pct) in enumerate(MARKETS):
        cx = 26 + 110 + i * cell_w
        d.text((cx + 6, y0 + 3), label, font=font(F_SANS_B, 7), fill=(170, 180, 210))
        val = value + (("  " + pct) if pct else "")
        d.text((cx + 6, y0 + 12), val, font=font(F_SANS_B, 11),
               fill=(255, 255, 255))


def draw_heroes(d, im):
    y_art, art_h = 202, 96
    col_w, gap = 312, 12
    art_fns = [hero_cop31, hero_kyiv, hero_manama]
    for i, hero in enumerate(HEROES):
        x = 26 + i * (col_w + gap)
        # render art on its own layer so nothing bleeds above the art rect
        layer = Image.new("RGB", (col_w, art_h), PAPER)
        ld = ImageDraw.Draw(layer)
        art_fns[i](ld, 0, 0, col_w, art_h)
        im.paste(layer, (x, y_art))
        ky = y_art + art_h + 6
        kicker_row(d, x, ky, col_w,
                   "%d %s · %s" % (hero["num"], hero["place"], hero["kick"]),
                   hero["badge"], badge_fill=hero["bf"])
        hy = ky + 16
        head_lines = wrap(d, hero["head"], font(F_SERIF, 20), col_w)
        assert len(head_lines) <= 2, "hero headline too long: %r" % hero["head"]
        yy = hy
        for ln in head_lines:
            d.text((x, yy), ln, font=font(F_SERIF, 20), fill=INK)
            yy += 22
        dy = hy + 44
        deck_lines = wrap(d, hero["deck"], font(F_SANS, 10), col_w)
        n_extra = 1 if "extra" in hero else 0
        assert len(deck_lines) + n_extra <= 3, "hero deck too long: %r" % hero["deck"]
        for ln in deck_lines:
            d.text((x, dy), ln, font=font(F_SANS, 10), fill=INK)
            dy += 12
        if "extra" in hero:
            d.text((x, dy), hero["extra"], font=font(F_SANS_B, 10), fill=RED_DK)


def draw_grid(d):
    col_w, gap, row_h, strip_h = 186, 9, 78, 11
    y_rows = [404, 482, 560, 638]
    for idx, (num, place, bdg, bf, head, deck, motif) in enumerate(GRID):
        row, col = divmod(idx, 5)
        x = 26 + col * (col_w + gap)
        y = y_rows[row]
        draw_strip(d, x, y, col_w, strip_h, motif,
                   STRIP_COLORS[idx % len(STRIP_COLORS)], num)
        ky = y + strip_h + 2
        kicker_row(d, x, ky, col_w, "%d %s" % (num, place), bdg, badge_fill=bf)
        hy = ky + 13
        head_lines = wrap(d, head, font(F_SERIF, 13), col_w)
        assert len(head_lines) <= 2, "card headline too long: %r" % head
        yy = hy
        for ln in head_lines:
            d.text((x, yy), ln, font=font(F_SERIF, 13), fill=INK)
            yy += 15
        dy = hy + 30
        deck_lines = wrap(d, deck, font(F_SANS, 9), col_w)
        assert len(deck_lines) <= 2, "card deck too long: %r" % deck
        for ln in deck_lines:
            d.text((x, dy), ln, font=font(F_SANS, 9), fill=INK)
            dy += 10.5
    # HOW TO READ box (5th cell of row 4)
    x = 26 + 4 * (col_w + gap)
    y = y_rows[3]
    d.rectangle([x, y, x + col_w, y + row_h - 2], outline=INK, width=1)
    d.text((x + 6, y + 3), "HOW TO READ", font=font(F_SANS_B, 11), fill=INK)
    sym = font(F_SYM, 9)
    rows = [
        ("●", "REPORTED", "confirmed by 2+ sources"),
        ("○", "CLAIM", "asserted by one side"),
        ("◐", "FORECAST", "not yet happened"),
        ("", "FULL TIME", "score final"),
        ("†", "in ALSO", "dated Fri / Sat"),
    ]
    yy = y + 19
    for s, tag, desc in rows:
        if s:
            d.text((x + 6, yy), s, font=sym, fill=INK)
        d.text((x + 18, yy), tag, font=font(F_SANS_B, 8), fill=INK)
        d.text((x + 76, yy), desc, font=font(F_SANS, 8), fill=GREY)
        yy += 11


# ---------------------------------------------------------------- world map
# Coarse land mask, 96 cols x 13 rows (hand-drawn equirectangular sketch).
LAND = [
    "  xxxxxxxxxxxxxxxx                          xxxxxxxx                  ",
    "  xxxxxxxxxxxxxxxxxx                      xxxxxxxxxx  xxxxxxxx       ",
    "   xxxxxxxxxxxxxxxxx      xxxx   xxxx   xxxxxxxxxxxxxxxxxxxxxxx     ",
    "    xxxxxxxxxxxxxxx      xxxxx xxxxxx  xxxxxxxxxxxxxxxxxxxxxxxxx    ",
    "     xxxxxxxxxxxxx       xxxxx  xxxx   xxxxxxxxxxxxxxxxxxxxxxx      ",
    "      xxxxxxxxxxxx        xxxx  xxx    xxxxxxxxxxxxxxxxxxxxx        ",
    "       xxxxxxxxxx         xxxx  xx      xxxxxxxxxx  xxxxxxx         ",
    "        xxxxxxxx           xxx  x        xxxxxxx    xxxxx           ",
    "         xxxxxx            xxx           xxxxx      xxx             ",
    "          xxxx             xx            xxx        xx    xx       ",
    "          xx               x             xx               xxx      ",
    "                           x              x                xx      ",
    "                                                              x     ",
]

# pin positions as fractions of the map rect (x 30..762, y 740..800)
PINS = {
    1: (0.600, 0.30), 2: (0.600, 0.16), 3: (0.648, 0.44), 4: (0.800, 0.48),
    5: (0.985, 0.74), 6: (0.100, 0.33), 7: (0.830, 0.30), 8: (0.585, 0.10),
    9: (0.608, 0.19), 10: (0.130, 0.40), 11: (0.782, 0.62), 12: (0.612, 0.38),
    13: (0.545, 0.56), 14: (0.566, 0.25), 15: (0.855, 0.30), 16: (0.826, 0.58),
    17: (0.930, 0.70), 18: (0.556, 0.21), 19: (0.586, 0.13), 20: (0.592, 0.08),
    21: (0.710, 0.41), 22: (0.530, 0.13),
}
# Europe cluster: numbered pins fanned out from their true spots (absolute
# px in the 1024 canvas), joined by leader lines to small true-position dots.
# Fan positions were checked pairwise: every pair is >= 12px apart.
FAN = {
    22: (405, 744), 19: (438, 740), 20: (464, 738), 8: (486, 744),
    2: (496, 754), 9: (492, 766), 1: (466, 772), 14: (446, 764),
    18: (424, 758),
}


def draw_map(d):
    mx0, my0, mx1, my1 = 30, 740, 762, 800
    d.line([(26, 720), (W - 26, 720)], fill=RULE, width=1)
    d.text((26, 724), "THE WORLD ON SUNDAY — 22 PINNED",
           font=font(F_SANS_B, 13), fill=INK)
    counts = "EUROPE 13 · M. EAST 4 · ASIA-PAC. 8 · AMERICAS 4 · AFRICA 4 · OCEANIA 2 · WORLD 2"
    f = font(F_SANS_B, 10)
    d.text((W - 26 - d.textlength(counts, font=f), 726), counts, font=f, fill=GREY)
    # dotted land
    cols, rows = 96, 13
    cw = (mx1 - mx0) / cols
    ch = (my1 - my0) / rows
    for r, line in enumerate(LAND):
        for c, ch2 in enumerate(line):
            if ch2 == "x":
                cx = mx0 + c * cw + cw / 2
                cy = my0 + r * ch + ch / 2
                d.ellipse([cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4], fill=(168, 156, 128))
    # pins: true positions, Europe cluster fanned out with leader lines
    pts = {}
    for num, (fx, fy) in PINS.items():
        pts[num] = (mx0 + fx * (mx1 - mx0), my0 + fy * (my1 - my0))
    for num, (px, py) in pts.items():
        if num in FAN:
            fx, fy = FAN[num]
            d.line([(px, py), (fx, fy)], fill=RED, width=1)
            d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=RED)
            px, py = fx, fy
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED)
        t = str(num)
        tf = font(F_SANS_B, 7 if num < 10 else 6)
        tw = d.textlength(t, font=tf)
        d.text((px - tw / 2, py - 4.5), t, font=tf, fill=(255, 255, 255))
    # Pacific inset (top below the counts line, so nothing overlaps it)
    ix0, iy0, ix1, iy1 = 776, 740, 998, 808
    d.rectangle([ix0, iy0, ix1, iy1], outline=INK, width=1)
    d.text((ix0 + 8, iy0 + 3), "PACIFIC — INSET", font=font(F_SANS_B, 11), fill=INK)
    d.text((ix0 + 8, iy0 + 16), "WELLINGTON 5 · CANBERRA 17",
           font=font(F_SANS_B, 12), fill=INK)
    draw_wrapped(d, ix0 + 8, iy0 + 29,
                 "Two Pacific capitals: Test cricket in Wellington, AUKUS in Canberra.",
                 font(F_SANS, 9), ix1 - ix0 - 16, leading=11)
    for num, label, lx in [(5, "Wellington", ix0 + 8), (17, "Canberra", ix0 + 116)]:
        cy = iy1 - 9
        d.ellipse([lx, cy - 8, lx + 16, cy + 8], fill=RED)
        t = str(num)
        tf = font(F_SANS_B, 8 if num < 10 else 7)
        d.text((lx + 8 - d.textlength(t, font=tf) / 2, cy - 5), t, font=tf,
               fill=(255, 255, 255))
        d.text((lx + 20, cy - 5), label, font=font(F_SANS, 10), fill=INK)


def draw_also(d):
    # two columns: items 23-30 (8 rows) left, 31-37 (7 rows) right
    d.line([(26, 814), (W - 26, 814)], fill=RULE, width=1)
    d.text((26, 818), "ALSO ON SUNDAY 22 NOVEMBER — 15 MORE STORIES",
           font=font(F_SANS_B, 12), fill=INK)
    cols_x = [26, 520]
    f_num = font(F_SANS_B, 10)
    f_reg = font(F_SANS, 9)
    f_txt = font(F_SANS, 9)
    f_src = font(F_SANS, 9)
    f_mark = font(F_SYM, 9)
    left, right = ALSO[:8], ALSO[8:]
    for col_idx, items in enumerate([left, right]):
        x0 = cols_x[col_idx]
        col_w = 472 if col_idx == 0 else 478
        for row, (num, region, text, src, mark) in enumerate(items):
            y = 831 + row * 10.5
            d.text((x0, y), str(num), font=f_num, fill=RED)
            d.text((x0 + 24, y + 1), region, font=f_reg, fill=GREY)
            tx = x0 + 24 + d.textlength(region + "  ", font=f_reg)
            src_w = d.textlength(src, font=f_src)
            avail = (x0 + col_w - 6 - src_w - 4) - tx
            if mark:
                avail -= d.textlength(mark + " ", font=f_mark)
            t = text
            while d.textlength(t, font=f_txt) > avail and len(t) > 8:
                t = t[:-1]
            assert len(t) > 8, "ALSO text truncated too far: %r" % text
            d.text((tx, y), t, font=f_txt, fill=INK)
            mx = x0 + col_w - 6 - src_w - 4
            if mark:
                d.text((mx - d.textlength(mark + " ", font=f_mark), y), mark,
                       font=f_mark, fill=GREY)
            d.text((x0 + col_w - 6 - src_w, y + 1), src, font=f_src, fill=GREY)


def draw_datecheck(d):
    d.line([(26, 914), (W - 26, 914)], fill=RULE, width=1)
    d.text((26, 918), "DATE CHECK — NOT SUNDAY, however listed elsewhere:",
           font=font(F_SANS_B, 12), fill=INK)
    col_w = (W - 52) / 3
    f = font(F_SANS, 9)
    for col, items in enumerate(DATE_CHECK):
        x = 26 + col * col_w
        y = 932
        for it in items:
            d.text((x, y), "•", font=font(F_SYM_B, 9), fill=RED)
            d.text((x + 10, y), it, font=f, fill=INK)
            y += 9.5


def draw_footer(d):
    d.text((26, 1010), FOOTER, font=font(F_SANS, 8), fill=GREY)


def render(path):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    draw_masthead(d)
    draw_stat_band(d)
    draw_timeline(d)
    draw_markets(d)
    draw_heroes(d, im)
    draw_grid(d)
    draw_map(d)
    draw_also(d)
    draw_datecheck(d)
    draw_footer(d)
    im.save(path, "PNG")
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    render(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
