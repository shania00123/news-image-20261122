#!/usr/bin/env python3
"""news-image-20261122 — RIVAL8: "THE SUNDAY RECORD".

A one-day newspaper poster for Sunday 22 November 2026, drawn from scratch
with PIL only. Deterministic: no timestamps, no randomness, no network.
Run:  python3 render_rival8.py poster.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (245, 240, 227)
INK = (25, 25, 25)
RED = (164, 22, 26)
RED_DK = (127, 15, 19)
NAVY = (30, 42, 82)
GOLD = (166, 124, 0)
GREY = (107, 101, 88)
LINE = (201, 192, 168)
FAINT = (233, 227, 210)
WHITE = (255, 255, 255)
CREAM = (250, 246, 235)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, font, width):
    """Greedy word wrap; raises if a single word cannot fit."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if font.getlength(word) > width:
                raise ValueError("word too wide: %r" % word)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, font, fill, leading):
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=fill)
    return y + len(lines) * leading


def fit(text, font, width, max_lines):
    """Wrap and assert it fits in max_lines; return lines."""
    lines = wrap(text, font, width)
    if len(lines) > max_lines:
        raise ValueError("overflow %d lines: %r" % (len(lines), text))
    return lines


def badge(d, x_right, y, label, bg, fg, font):
    """Right-aligned small badge; returns left x."""
    w = int(font.getlength(label)) + 8
    d.rectangle([x_right - w, y, x_right, y + 11], fill=bg)
    d.text((x_right - w + 4, y + 1), label, font=font, fill=fg)
    return x_right - w


# ---------------------------------------------------------------- data
# (region, place, headline, deck, certainty, strip colour, strip motif)
GRID = [
    ("HONG KONG", "Hong Kong turnout hits record 98.79%",
     "5,640 of 5,709 voted; count done 22:15. Beats 89.77% in 2021.",
     "REPORTED", (30, 42, 82), "ballot"),
    ("WELLINGTON", "India declare 720/9 — a record in NZ",
     "Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.",
     "REPORTED", (46, 110, 60), "ball"),
    ("LAS VEGAS", "Verstappen wins Vegas by 0.639s",
     "75th career win; Norris 2nd, Piastri 3rd from 17th.",
     "REPORTED", (122, 84, 32), "flag"),
    ("SEOUL", "Seoul minister quits over AI exam scandal",
     "Choi Kyo-jin resigned; Lee accepted in an hour. 111 cheating cases probed.",
     "REPORTED", (96, 84, 130), "screen"),
    ("FINLAND", "Sparta II still burning off Finland",
     "Struck Sat; fire smouldered Sun. Helo breached Finnish airspace by 4.1 km.",
     "REPORTED", (20, 101, 94), "flame"),
    ("KRYVYI RIH", "Missile kills boy, 7, and medic, 20; 58 hurt",
     "Hometown strike; four fires, ~23 blocks hit, hospital and schools damaged.",
     "REPORTED", (150, 110, 40), "warn"),
    ("SAN ANTONIO", "Wembanyama drops 50 as Spurs rout Pelicans",
     "San Antonio's star scores 50 in a 114–91 rout of New Orleans.",
     "REPORTED", (52, 58, 66), "bars"),
    ("CIKANDE", "Candy-factory fire: 3 dead, 36 missing",
     "Blaze broke out Saturday 17:00; search went on Sunday; 300 workers inside.",
     "REPORTED", (140, 80, 30), "flame"),
    ("GAZA", "Hamas seeks urgent talks after aid-van strike",
     "Aid-van strike killed workers Sat; Hamas seeks urgent talks on aid access.",
     "REPORTED", (58, 58, 58), "bars"),
    ("BAYELSA", "Nigeria boat toll reaches 24",
     "Capsized Friday; Ayama-Ukubie; 24 dead, 24 rescued. Manager held.",
     "REPORTED", (120, 86, 40), "wave"),
    ("VATICAN", "Pope Leo XIV hosts 1,300 for lunch",
     "10th World Day of the Poor; lunch in Paul VI Hall, a week of events.",
     "REPORTED", (110, 88, 140), "circle"),
    ("FUKUSHIMA", "1,500 still cut off by Japan landslide",
     "Stranded in Kitashiobara since Saturday; heavy rain hampered rescue.",
     "REPORTED", (20, 101, 94), "rain"),
    ("MINDANAO", "M6.0 quake off Mindanao; no damage",
     "Off southern Mindanao, 15:54 local, depth 10 km. No tsunami.",
     "REPORTED", (140, 80, 30), "warn"),
    ("CANBERRA", "Albanese: US report 'wrong' on AUKUS",
     "Defence minister rejects CBO warning on subs cost; US $368bn programme.",
     "REPORTED", (20, 101, 94), "circle"),
    ("TURIN", "Zverev v Alcaraz in Turin final today",
     "ATP Finals title match closes the season in Turin.",
     "FORECAST", (30, 42, 82), "bars"),
    ("WARSAW", "NATO to meet Monday over Poland incursion",
     "Drone debris confirmed in Nowy Lipowiec. Council meets Monday.",
     "FORECAST", (46, 110, 60), "ball"),
    ("TALLINN", "Moscow vows retaliation as Estonia seals border",
     "Estonia seals crossings for months; Moscow calls it a new Iron Curtain.",
     "REPORTED", (122, 84, 32), "flag"),
    ("DELHI", "Nepal PM Shah lands in Delhi",
     "First foreign trip; talks with Modi on Monday.",
     "REPORTED", (96, 84, 130), "circle"),
    ("LIVERPOOL", "Liverpool rout Man Utd 4–0 on Pochettino debut",
     "Szoboszlai 10', Wirtz 13', Ngumoha 66', Muñoz 82'. Yoro off 8'; United 19th.",
     "REPORTED", (164, 22, 26), "bars"),
]

# (number, region, text, place) — 15 items, renumbered 23..37
ALSO = [
    ("EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv"),
    ("WORLD", "Russia says it downed 170 Ukrainian drones overnight ○ CLAIM", "Moscow"),
    ("WORLD", "Bitcoin back above $60,000 after Saturday's $55,130 low", "Coinbase"),
    ("AMERICAS", "San Francisco braces for record king tides ○ FORECAST", "NWS"),
    ("MIDDLE EAST", "US denies Iran claim it downed two US radars ○ CLAIM", "CENTCOM"),
    ("EUROPE", "Lebanon marks 83rd Independence Day", "Beirut"),
    ("AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children", "W. Kordofan"),
    ("AFRICA", "S. Africa holds service for Mlambo-Ngcuka, 71 (died Fri)", "SABC"),
    ("MIDDLE EAST", "Iraq: fire at Hartha power station kills 4, injures 35 † SAT", "Basra"),
    ("EUROPE", "Moldova: Russian drone crosses border twice near Purcari † SAT", "Chisinau"),
    ("AFRICA", "Somalia: UAE envoy's 72 hours run out today (ordered Thu)", "Mogadishu"),
    ("ASIA-PACIFIC", "Manipur liquor toll 19, 600+ in hospital — Sun a.m., still rising", "Imphal"),
    ("ASIA-PACIFIC", "M5.3 Celebes Sea, 61 km, 07:54 UTC", "EMSC"),
    ("AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "Brasilia"),
    ("EUROPE", "Hull 2–0 Brighton", "MKM"),
]

DATE_CHECK = [
    ["Peru quake — Fri 20 Nov",
     "Gaza aid-van strike — Sat 21 Nov",
     "Japan poll: 62% feel affinity to Korea — Fri 20 Nov",
     "Mlambo-Ngcuka dies — Fri 20 Nov",
     "EU-Indonesia deal — Sat 21 Nov",
     "Denmark expels Russian attaché — Fri 20 Nov",
     "Qatar talks in Tehran — Fri 20 Nov",
     "Russia's 400-drone barrage — night of 19–20 Nov"],
    ["BepiColombo at Mercury — Sat 21 Nov",
     "Sparta II struck — Sat 21 Nov",
     "Newcastle 2–2 Arsenal; Chelsea 1–4 Leeds — Sat 21 Nov",
     "DR Congo Cantine attack — night of 5–6 Nov",
     "Estonia closes border — decided Fri 20 Nov",
     "UK-EU food deal agreed — Fri 20 Nov",
     "Senate $350bn defence push stalls — Wed 18 Nov"],
    ["ICJ Myanmar ruling — Thu 19 Nov",
     "Bayelsa boat capsizes — Fri 20 Nov",
     "Aoun's Israel-withdrawal speech — Sat 21 Nov",
     "Nvidia SEC probe — Fri 20 Nov",
     "'El Chapo Isidro' captured — Fri 20 Nov",
     "Trump–Xi–Putin talks — Thu 19 Nov",
     "H-6 bomber nears Manila — Sat 21 Nov"],
]

MARKETS = [
    ("GOLD · PER OZ", "$3,539"),
    ("BITCOIN · SUNDAY HIGH", "$61,568"),
    ("TASI · RIYADH", "9,960.44  −1.95%"),
    ("QATAR · DOHA", "9,902.87  −1.59%"),
    ("EGX30 · CAIRO", "49,989.79  −2.85%"),
    ("EGX70 · CAIRO", "16,534.42  −5.55%"),
]

# ---------------------------------------------------------------- art
SKINS = [(232, 197, 160), (198, 152, 112), (160, 110, 76), (240, 205, 170),
         (120, 82, 58)]
SUITS = [(38, 48, 74), (74, 74, 74), (96, 32, 32), (32, 74, 52),
         (110, 84, 30), (60, 40, 80), (30, 80, 90)]


def apply_overlay(im, ov):
    im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"),
             (0, 0))


def hero_cop(im, x, y, w, h):
    """COP31 final plenary: delegate rows with varied scale/depth, warm
    spotlights, and a clearly EMPTY walkout chair block with a big label."""
    d = ImageDraw.Draw(im)
    d.rectangle([x, y, x + w, y + h], fill=(122, 90, 56))
    d.rectangle([x, y, x + w, y + 46], fill=(96, 68, 40))
    # warm spotlight cones from the ceiling
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.polygon([(x + 30, y), (x + 70, y), (x + 150, y + h), (x + 60, y + h)],
               fill=(255, 220, 140, 26))
    od.polygon([(x + w - 70, y), (x + w - 30, y), (x + w - 60, y + h),
                (x + w - 150, y + h)], fill=(255, 220, 140, 26))
    apply_overlay(im, ov)
    # podium sign
    sx, sw = x + w // 2 - 78, 156
    d.rectangle([sx, y + 6, sx + sw, y + 30], fill=CREAM,
                outline=(60, 40, 20))
    d.text((sx + sw // 2, y + 8), "COP31 · ANTALYA", font=F(SERIF_B, 13),
           fill=RED, anchor="mt")
    d.text((sx + sw // 2, y + 21), "FINAL PLENARY", font=F(SANS_B, 9),
           fill=INK, anchor="mt")
    # flag chips under the sign
    chips = [(34, 120, 60), (30, 60, 130), (200, 170, 40), (130, 40, 120),
             (210, 110, 30), (170, 30, 30), (40, 130, 130)]
    for i, c in enumerate(chips):
        d.rectangle([sx + 8 + i * 21, y + 33, sx + 26 + i * 21, y + 39],
                    fill=c)
    # delegate rows: back row small, front row large (depth + scale)
    rows = [(y + 44, 4, 26, 0), (y + 58, 5, 30, 1), (y + 74, 7, 34, 2)]
    for ry, r, step, row_i in rows:
        n = (w - 90) // step
        for i in range(n):
            cx = x + 14 + i * step + (row_i * 7) % 11
            if cx > x + w - 96:  # keep the walkout block clear
                continue
            skin = SKINS[(i * 3 + row_i) % 5]
            suit = SUITS[(i + row_i * 2) % 7]
            d.ellipse([cx - r, ry - r, cx + r, ry + r], fill=skin)
            d.rounded_rectangle([cx - r - 2, ry + r - 1, cx + r + 2,
                                 ry + r + 9], radius=3, fill=suit)
            if (i + row_i) % 3 == 0:  # laptop glow
                d.rectangle([cx - r - 5, ry + r + 3, cx - r + 3, ry + r + 8],
                            fill=(210, 215, 220))
            if (i * 2 + row_i) % 4 == 0:  # nameplate
                d.rectangle([cx - 4, ry + r + 10, cx + 5, ry + r + 13],
                            fill=CREAM)
    # desks
    for ry in (y + 52, y + 67, y + 83):
        d.rectangle([x + 6, ry + 9, x + w - 96, ry + 12], fill=(70, 48, 26))
    # ---- WALKOUT: three clearly empty chairs, no delegates at all ----
    wx0, wx1 = x + w - 88, x + w - 6
    d.rectangle([wx0, y + 42, wx1, y + h - 4], fill=(146, 110, 68))
    d.rectangle([wx0, y + 42, wx1, y + 58], fill=RED)
    d.text(((wx0 + wx1) // 2, y + 45), "WALKOUT", font=F(SANS_B, 12),
           fill=WHITE, anchor="mt")
    for i in range(3):
        cx = wx0 + 14 + i * 26
        d.rounded_rectangle([cx - 8, y + 64, cx + 8, y + 82], radius=3,
                            fill=(52, 36, 20))          # chair back
        d.rectangle([cx - 8, y + 82, cx + 8, y + 86], fill=(52, 36, 20))
        d.rectangle([cx - 5, y + 87, cx + 5, y + 90], fill=CREAM)


def hero_kyiv(im, x, y, w, h):
    """Kyiv at night: skyline, lit windows, searchlight beams, smoke,
    embers and drone arcs."""
    d = ImageDraw.Draw(im)
    d.rectangle([x, y, x + w, y + h], fill=(13, 21, 48))
    for sx, sy in [(18, 8), (52, 16), (90, 6), (130, 14), (170, 7),
                   (205, 15), (245, 6), (285, 12), (70, 24), (150, 22),
                   (230, 24), (300, 20)]:
        d.ellipse([x + sx, y + sy, x + sx + 1, y + sy + 1], fill=(220, 225, 240))
    d.ellipse([x + 252, y + 10, x + 280, y + 38], fill=(235, 228, 200))
    d.ellipse([x + 260, y + 18, x + 266, y + 24], fill=(210, 200, 170))
    d.ellipse([x + 270, y + 26, x + 274, y + 30], fill=(210, 200, 170))
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.polygon([(x + 60, y + h), (x + 78, y + h), (x + 150, y + 4),
                (x + 128, y + 4)], fill=(255, 240, 180, 30))
    od.polygon([(x + 210, y + h), (x + 226, y + h), (x + 120, y + 10),
                (x + 104, y + 10)], fill=(255, 240, 180, 24))
    apply_overlay(im, ov)
    # drone arcs (gold, dotted)
    for cx0, cy0, r in [(40, 96, 70), (150, 96, 90), (250, 96, 60)]:
        for a in range(200, 341, 6):
            import math
            px = x + cx0 + r * math.cos(math.radians(a))
            py = y + cy0 - r * 0.55 * math.sin(math.radians(a))
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(230, 190, 90))
    # skyline
    heights = [34, 52, 44, 66, 40, 58, 48, 70, 38, 56, 46, 62, 36]
    bx = x
    for i, bh in enumerate(heights):
        bw = w // len(heights)
        d.rectangle([bx, y + h - bh, bx + bw - 2, y + h], fill=(5, 7, 15))
        for wy in range(y + h - bh + 5, y + h - 4, 9):
            for wx in range(bx + 3, bx + bw - 5, 7):
                if (wx + wy + i) % 3 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 205, 90))
        bx += bw
    # fire + smoke over one block (low glow at the roofline, small smoke)
    fx = x + 132
    d.ellipse([fx - 20, y + h - 62, fx + 20, y + h - 44], fill=(200, 90, 20))
    d.ellipse([fx - 13, y + h - 58, fx + 13, y + h - 44], fill=(240, 160, 40))
    d.ellipse([fx - 7, y + h - 54, fx + 7, y + h - 44], fill=(255, 220, 120))
    d.polygon([(fx - 10, y + h - 46), (fx - 4, y + h - 64),
               (fx + 2, y + h - 50), (fx + 8, y + h - 60),
               (fx + 12, y + h - 46)], fill=(245, 160, 40))
    for sx, sy, sr in [(fx - 6, y + h - 72, 6), (fx + 6, y + h - 82, 7),
                       (fx - 2, y + h - 90, 5)]:
        d.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2],
                  fill=(80, 80, 95))
    for ex, ey in [(fx - 16, y + h - 40), (fx + 14, y + h - 48),
                   (fx - 8, y + h - 56), (fx + 18, y + h - 36)]:
        d.ellipse([ex, ey, ex + 2, ey + 2], fill=(255, 150, 50))


def hero_manama(im, x, y, w, h):
    """Manama at dusk: radar dishes at varied angles, a burning civilian
    plant, and a sea strip with waves and light reflections."""
    d = ImageDraw.Draw(im)
    d.rectangle([x, y, x + w, y + h], fill=(74, 44, 51))
    d.ellipse([x + 250, y + 8, x + 292, y + 50], fill=(235, 210, 170))
    sea_y = y + h - 26
    d.rectangle([x, y + 52, x + w, sea_y], fill=(38, 30, 34))
    # buildings with lit windows
    for bx, bw, bh in [(6, 44, 34), (58, 36, 44), (104, 52, 30),
                       (170, 40, 40), (218, 46, 32), (272, 38, 38)]:
        d.rectangle([x + bx, y + 52 - bh + 18, x + bx + bw, sea_y],
                    fill=(24, 18, 22))
        for wy in range(y + 52 - bh + 24, sea_y - 4, 9):
            for wx in range(x + bx + 5, x + bx + bw - 5, 9):
                if (wx * 7 + wy) % 5 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 205, 90))
    # radar dishes, three different tilts, mounted on rooftops
    import math
    for dx, topy, tilt in [(28, 36, -25), (190, 30, 10), (290, 32, 30)]:
        d.line([x + dx, y + topy, x + dx, y + topy - 14],
               fill=(200, 200, 205), width=2)
        d.rectangle([x + dx - 5, y + topy - 1, x + dx + 5, y + topy + 2],
                    fill=(160, 160, 165))
        d.ellipse([x + dx - 10, y + topy - 20, x + dx + 10, y + topy - 8],
                  outline=(225, 225, 230), width=2, fill=(90, 80, 90))
        ex = dx + 8 * math.cos(math.radians(tilt - 90))
        ey = topy - 14 + 8 * math.sin(math.radians(tilt - 90))
        d.line([x + dx, y + topy - 14, x + ex, y + ey],
               fill=(225, 225, 230), width=2)
    # burning civilian plant: flames + glow + smoke
    px = x + 118
    d.ellipse([px - 34, sea_y - 26, px + 34, sea_y + 4], fill=(190, 80, 20))
    d.polygon([(px - 16, sea_y - 6), (px - 6, sea_y - 30), (px + 2, sea_y - 12),
               (px + 10, sea_y - 26), (px + 18, sea_y - 6)], fill=(245, 160, 40))
    d.polygon([(px - 8, sea_y - 6), (px - 2, sea_y - 20), (px + 6, sea_y - 6)],
              fill=(255, 225, 130))
    for sx, sy, sr in [(104, 18, 8), (112, 8, 10), (122, 2, 8)]:
        d.ellipse([x + sx - sr, y + sy - sr // 2, x + sx + sr,
                   y + sy + sr // 2], fill=(80, 70, 75))
    # sea: waves + reflections of the fire and the lights
    d.rectangle([x, sea_y, x + w, y + h], fill=(20, 38, 62))
    for row, yy in enumerate(range(sea_y + 4, y + h - 2, 7)):
        for wx in range(x + 4 + (row % 2) * 9, x + w - 8, 18):
            d.arc([wx, yy, wx + 14, yy + 6], 180, 360, fill=(120, 160, 200))
    for i, (rx, rl) in enumerate([(108, 16), (114, 10), (120, 18), (126, 8),
                                  (112, 12), (124, 14), (262, 12), (268, 8)]):
        d.line([x + rx, sea_y + 3 + (i % 3) * 5, x + rx,
                sea_y + 3 + (i % 3) * 5 + rl], fill=(245, 180, 80), width=2)


def strip(d, x, y, w, base, motif):
    """11px illustrated band for a grid card."""
    d.rectangle([x, y, x + w, y + 11], fill=base)
    d.rectangle([x, y + 8, x + w, y + 11], fill=tuple(max(0, c - 28) for c in base))
    if motif == "ball":
        d.ellipse([x + w - 16, y + 1, x + w - 6, y + 11], fill=(250, 246, 235))
        d.line([x + 6, y + 9, x + w - 20, y + 2], fill=(250, 246, 235), width=2)
    elif motif == "flag":
        for i in range(6):
            d.rectangle([x + 8 + i * 8, y + 2, x + 14 + i * 8, y + 8],
                        fill=WHITE if i % 2 == 0 else (20, 20, 20))
    elif motif == "flame":
        d.polygon([(x + w - 14, y + 10), (x + w - 9, y + 1), (x + w - 4, y + 10)],
                  fill=(255, 170, 40))
    elif motif == "wave":
        for wx in range(x + 6, x + w - 10, 12):
            d.arc([wx, y + 2, wx + 10, y + 9], 180, 360, fill=(200, 220, 240))
    elif motif == "bars":
        for i, bh in enumerate([4, 8, 5, 9, 6]):
            d.rectangle([x + 8 + i * 9, y + 10 - bh, x + 14 + i * 9, y + 10],
                        fill=(210, 215, 225))
    elif motif == "circle":
        d.ellipse([x + w - 17, y + 1, x + w - 7, y + 11],
                  outline=WHITE, width=2)
        d.ellipse([x + w - 13, y + 5, x + w - 11, y + 7], fill=WHITE)
    elif motif == "warn":
        d.polygon([(x + w - 14, y + 2), (x + w - 5, y + 10), (x + w - 22, y + 10)],
                  outline=(255, 220, 90), width=2)
    elif motif == "rain":
        for i in range(5):
            d.line([x + 10 + i * 12, y + 2, x + 6 + i * 12, y + 9],
                   fill=(180, 210, 230), width=2)
    elif motif == "screen":
        d.rectangle([x + w - 24, y + 2, x + w - 6, y + 9], outline=WHITE, width=1)
        d.line([x + w - 20, y + 5, x + w - 10, y + 5], fill=WHITE, width=1)
    elif motif == "ballot":
        for i in range(4):
            d.rectangle([x + 8 + i * 12, y + 3, x + 16 + i * 12, y + 9],
                        fill=(220, 225, 235))
        d.ellipse([x + w - 14, y + 2, x + w - 6, y + 10], fill=RED)

# ---------------------------------------------------------------- map
LAND = [(0.13, 0.30, 0.13, 0.20), (0.24, 0.20, 0.07, 0.09),
        (0.33, 0.10, 0.03, 0.06), (0.33, 0.68, 0.06, 0.16),
        (0.50, 0.22, 0.06, 0.10), (0.46, 0.15, 0.02, 0.04),
        (0.52, 0.58, 0.07, 0.17), (0.58, 0.40, 0.05, 0.06),
        (0.72, 0.25, 0.16, 0.14), (0.68, 0.45, 0.04, 0.08),
        (0.80, 0.52, 0.05, 0.07), (0.82, 0.62, 0.08, 0.03),
        (0.86, 0.78, 0.07, 0.06), (0.94, 0.86, 0.02, 0.05),
        (0.90, 0.32, 0.02, 0.05)]

# num -> (true nx, true ny, display nx, display ny); Europe pins fan out
PINS = {
    6: (0.08, 0.45, 0.08, 0.45), 10: (0.14, 0.55, 0.14, 0.55),
    22: (0.44, 0.28, 0.415, 0.30), 18: (0.47, 0.38, 0.435, 0.50),
    14: (0.48, 0.42, 0.465, 0.36), 19: (0.51, 0.30, 0.475, 0.20),
    20: (0.53, 0.20, 0.525, 0.12), 2: (0.56, 0.34, 0.55, 0.26),
    9: (0.55, 0.40, 0.575, 0.44), 1: (0.55, 0.46, 0.52, 0.56),
    12: (0.57, 0.50, 0.60, 0.56), 3: (0.60, 0.52, 0.635, 0.44),
    8: (0.52, 0.12, 0.485, 0.06), 21: (0.69, 0.48, 0.69, 0.48),
    4: (0.82, 0.50, 0.82, 0.50), 7: (0.86, 0.40, 0.86, 0.40),
    15: (0.90, 0.36, 0.90, 0.36), 16: (0.85, 0.62, 0.85, 0.62),
    11: (0.80, 0.64, 0.80, 0.64), 17: (0.87, 0.84, 0.87, 0.84),
    5: (0.94, 0.90, 0.94, 0.90),
}


def draw_map(d, x, y, w, h):
    for gy in range(y + 3, y + h - 2, 6):
        for gx in range(x + 3, x + w - 2, 6):
            nx, ny = (gx - x) / w, (gy - y) / h
            for cx, cy, rx, ry in LAND:
                if ((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 <= 1:
                    d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1],
                              fill=(150, 138, 110))
                    break
    fnum = F(SANS_B, 8)
    for num, (tx, ty, dx, dy) in sorted(PINS.items()):
        px, py = x + dx * w, y + dy * h
        txp, typ = x + tx * w, y + ty * h
        if abs(px - txp) > 2 or abs(py - typ) > 2:
            d.line([px, py, txp, typ], fill=(164, 22, 26), width=1)
            d.ellipse([txp - 2, typ - 2, txp + 2, typ + 2], fill=RED)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED)
        d.text((px, py), str(num), font=fnum, fill=WHITE, anchor="mm")


# ---------------------------------------------------------------- build
def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    M, CW = 28, 968
    R = M + CW  # 996

    # ---- masthead
    fk = F(SANS_B, 11)
    d.text((M, 8), "THE SUNDAY RECORD — THE WORLD IN ONE DAY", font=fk, fill=INK)
    rt = "37 STORIES · 7 REGIONS · EVERY DATE CHECKED · SUNDAY 22 NOVEMBER 2026"
    d.text((R, 8), rt, font=fk, fill=GREY, anchor="ra")
    d.text((M, 16), "Sunday 22 November 2026", font=F(SERIF_B, 56), fill=INK)
    d.text((M, 80), "COP31 collapses with no deal · Russia fires 186 drones · "
                    "Iran claims two US radars hit", font=F(SANS_B, 15), fill=RED)
    d.rectangle([R - 84, 78, R, 96], fill=RED)
    d.text((R - 42, 81), "NO DEAL", font=F(SANS_B, 13), fill=WHITE, anchor="ma")

    # ---- number strip (single-line labels: no wrap, no collision)
    d.line([M, 100, R, 100], fill=LINE, width=1)
    stats = [("44h", "COP31 OVERTIME"), ("186", "DRONES AT UKRAINE"),
             ("161", "DOWNED OR JAMMED"), ("720/9", "INDIA'S TEST TOTAL"),
             ("$61,568", "BITCOIN SUNDAY HIGH"), ("98.79%", "HK TURNOUT, RECORD")]
    cw = CW / 6
    fnum, flab = F(SERIF_B, 30), F(SANS_B, 9)
    for i, (num, lab) in enumerate(stats):
        cx = M + i * cw
        if i:
            d.line([cx, 104, cx, 146], fill=LINE, width=1)
        d.text((cx + 8, 104), num, font=fnum, fill=INK)
        d.text((cx + 8, 138), lab, font=flab, fill=GREY)
    d.line([M, 150, R, 150], fill=INK, width=1)

    # ---- UTC timeline
    utc = ("THE DAY IN UTC — 03:00 COP31 objections close · 05:30 Verstappen "
           "wins Vegas · 06:00 COP31 approval due · 09:29 Hamas seeks talks · "
           "14:15 HK count done")
    d.text((M, 154), utc, font=F(SANS_B, 11), fill=INK)

    # ---- MARKETS band
    d.rectangle([M, 172, R, 196], fill=NAVY)
    d.text((M + 8, 179), "MARKETS", font=F(SANS_B, 13), fill=WHITE)
    mcell = (R - 150) / 6
    for i, (lab, val) in enumerate(MARKETS):
        cx = 150 + i * mcell
        d.text((cx + 6, 175), lab, font=F(SANS_B, 8), fill=(170, 180, 210))
        d.text((cx + 6, 184), val, font=F(SANS_B, 12), fill=WHITE)

    # ---- heroes
    heroes = [
        ("1 ANTALYA · 44 HOURS OVERTIME", "REPORTED",
         "COP31 collapses with no deal",
         "The EU, UK and Panama rejected a final text that omitted fossil "
         "fuels — the first breakdown since COP15 in 2009. The EU walked out.",
         hero_cop),
        ("2 KYIV REGION · 186 DRONES", "REPORTED",
         "Russia fires 186 drones; Dymer block destroyed",
         "161 downed or jammed; 72 jet-powered. One destroyed a five-storey "
         "block in Dymer; 2 dead, 14 missing.",
         hero_kyiv),
        ("3 MANAMA · CLAIM", "CLAIM",
         "Iran claims two US radars hit; Bahrain denies it",
         "IRGC media claimed Saturday-night strikes hit two US Patriot "
         "radars; Bahrain says it intercepted them. Two hurt; a civilian "
         "plant burned.",
         hero_manama),
    ]
    for i, (kick, cert, head, deck, art) in enumerate(heroes):
        hx = M + i * (316 + 10)
        art(im, hx, 200, 316, 96)
        d.text((hx, 300), kick, font=F(SANS_B, 10), fill=RED)
        bg = RED if cert == "REPORTED" else GOLD
        fg = WHITE if cert == "REPORTED" else INK
        badge(d, hx + 316, 300, cert, bg, fg, F(SANS_B, 8))
        hl = fit(head, F(SERIF_B, 20), 316, 2)
        text_lines(d, hx, 314, hl, F(SERIF_B, 20), INK, 22)
        dl = fit(deck, F(SANS, 11), 316, 3)
        text_lines(d, hx, 360, dl, F(SANS, 11), (60, 58, 50), 12)

    d.line([M, 398, R, 398], fill=LINE, width=1)

    # ---- grid 4..22 (19 cards) + HOW TO READ box
    fgrid_k, fgrid_h, fgrid_d = F(SANS_B, 9), F(SERIF_B, 13), F(SANS, 9)
    for idx, (place, head, deck, cert, colour, motif) in enumerate(GRID):
        n = idx + 4
        row, col = divmod(idx, 5)
        gx = M + col * (187 + 8)
        gy = 404 + row * 78
        if n == 22:
            pass
        strip(d, gx, gy, 187, colour, motif)
        d.text((gx, gy + 14), "%d %s" % (n, place), font=fgrid_k, fill=RED)
        bg = RED if cert == "REPORTED" else GOLD
        fg = WHITE if cert == "REPORTED" else INK
        badge(d, gx + 187, gy + 14, cert, bg, fg, F(SANS_B, 8))
        hl = fit(head, fgrid_h, 187, 2)
        text_lines(d, gx, gy + 26, hl, fgrid_h, INK, 14)
        dl = fit(deck, fgrid_d, 187, 2)
        text_lines(d, gx, gy + 55, dl, fgrid_d, (60, 58, 50), 10.5)
        if n == 22:  # thick FULL TIME badge on the Liverpool art strip
            d.rectangle([gx + 187 - 92, gy + 1, gx + 187 - 2, gy + 10], fill=RED)
            d.text((gx + 187 - 47, gy + 1), "4–0 FULL TIME",
                   font=F(SANS_B, 8), fill=WHITE, anchor="ma")
    # HOW TO READ box (row 4, col 5)
    bx, by = M + 4 * (187 + 8), 404 + 3 * 78
    d.rectangle([bx, by, bx + 187, by + 78], outline=INK, width=1)
    d.text((bx + 6, by + 3), "HOW TO READ", font=F(SANS_B, 11), fill=INK)
    legend = [("● REPORTED", "confirmed by 2+ sources"),
              ("○ CLAIM", "asserted by one side"),
              ("◐ FORECAST", "not yet happened"),
              ("FULL TIME", "score final"),
              ("† in ALSO", "dated Fri / Sat")]
    for i, (a, b) in enumerate(legend):
        yy = by + 18 + i * 11
        d.text((bx + 6, yy), a, font=F(SANS_B, 9), fill=INK)
        d.text((bx + 74, yy), b, font=F(SANS, 9), fill=GREY)

    # ---- map
    d.line([M, 718, R, 718], fill=LINE, width=1)
    d.text((M, 722), "THE WORLD ON SUNDAY — 22 PINNED",
           font=F(SANS_B, 12), fill=INK)
    d.text((742, 724), "EUROPE 13 · M. EAST 4 · ASIA-PAC. 8 · AMERICAS 4 · "
                       "AFRICA 4 · OCEANIA 2 · WORLD 2",
           font=F(SANS_B, 9), fill=GREY, anchor="ra")
    draw_map(d, M, 736, 714, 80)
    # Pacific inset: genuinely Pacific copy (no duplicated HK stat)
    ix0, ix1 = 752, 996
    d.rectangle([ix0, 738, ix1, 816], outline=INK, width=1)
    d.text((ix0 + 8, 742), "PACIFIC — INSET", font=F(SANS_B, 10), fill=INK)
    d.text((ix0 + 8, 754), "WELLINGTON 5 · CANBERRA 17",
           font=F(SANS_B, 11), fill=INK)
    cap = fit("Two Pacific capitals: Test cricket in Wellington, AUKUS in "
              "Canberra.", F(SANS, 9), ix1 - ix0 - 16, 2)
    text_lines(d, ix0 + 8, 768, cap, F(SANS, 9), (60, 58, 50), 11)
    for px, num, lab in [(ix0 + 22, "5", "Wellington"), (ix0 + 130, "17", "Canberra")]:
        d.ellipse([px - 8, 792, px + 8, 808], fill=RED)
        d.text((px, 800), num, font=F(SANS_B, 9), fill=WHITE, anchor="mm")
        d.text((px + 12, 795), lab, font=F(SANS, 9), fill=INK)

    # ---- ALSO (15 items, 2 columns)
    d.line([M, 820, R, 820], fill=LINE, width=1)
    d.text((M, 824), "ALSO ON SUNDAY 22 NOVEMBER — 15 MORE STORIES",
           font=F(SANS_B, 12), fill=INK)
    fnum, freg, ftxt, fplc = (F(SANS_B, 9), F(SANS_B, 8), F(SANS, 9),
                              F(SANS, 8))
    for i, (region, txt, place) in enumerate(ALSO):
        col = 0 if i < 8 else 1
        ax = M + col * 500
        ay = 840 + (i % 8) * 10.5
        num = 23 + i
        d.text((ax, ay), str(num), font=fnum, fill=RED)
        d.text((ax + 20, ay + 0.5), region, font=freg, fill=GREY)
        tw = 468 - 20 - 78 - 66
        lines = fit(txt, ftxt, tw, 1)
        d.text((ax + 98, ay), lines[0], font=ftxt, fill=INK)
        d.text((ax + 468, ay + 0.5), place, font=fplc, fill=GREY, anchor="ra")

    # ---- DATE CHECK (22 items, 3 columns)
    d.line([M, 924, R, 924], fill=LINE, width=1)
    d.text((M, 928), "DATE CHECK — NOT SUNDAY, however listed elsewhere:",
           font=F(SANS_B, 11), fill=INK)
    fdc = F(SANS, 8.5)
    for c, items in enumerate(DATE_CHECK):
        dx = M + c * 316
        for j, item in enumerate(items):
            yy = 942 + j * 9.5
            d.text((dx, yy), "•", font=fdc, fill=RED)
            d.text((dx + 9, yy), item, font=fdc, fill=INK)

    # ---- footer
    d.text((M, 1016), "Sources: Reuters · AP · AFP · Al Jazeera · BBC · "
                      "The Times · Formula 1 · Cricinfo · PHIVOLCS · "
                      "Vatican News · QNA · Saudi Exchange · EGX — verified "
                      "vs Sunday 22 Nov 2026.", font=F(SANS, 8), fill=GREY)
    return im


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    build().save(out)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
