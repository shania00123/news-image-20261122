#!/usr/bin/env python3
"""Render the news-image-20261122 poster: Sunday 22 November 2026 world news.

Build-time only. Produces poster.png (1024x1024, deterministic) in this
directory. main.py is the graded entrypoint; it only copies poster.png.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234, 255)
NAVY = (14, 42, 71, 255)
NAVY_DARK = (9, 30, 52, 255)
INK = (24, 28, 34, 255)
MUTED = (90, 96, 104, 255)
CARD = (255, 255, 255, 255)
LINE = (205, 210, 216, 255)
ALSO_BG = (234, 240, 246, 255)
CHECK_BG = (251, 236, 236, 255)
CHECK_LINE = (196, 60, 60, 255)
WHITE = (255, 255, 255, 255)
GOLD = (232, 184, 64, 255)

REGION_COLOR = {
    "GLOBAL": (15, 118, 110, 255),
    "AFRICA": (180, 83, 9, 255),
    "ASIA": (185, 28, 28, 255),
    "MARKETS": (21, 128, 61, 255),
    "MIDDLE EAST": (124, 58, 237, 255),
    "AMERICAS": (29, 78, 216, 255),
    "OCEANIA": (3, 105, 161, 255),
}

PILL_STYLE = {
    "CONFIRMED": ((21, 128, 61, 255), WHITE),
    "OFFICIAL": ((14, 42, 71, 255), WHITE),
    "REPORTED": ((180, 83, 9, 255), WHITE),
}

# ---------------------------------------------------------------- helpers
def wrap_text(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines, min_size, bold_path):
    """Shrink font until text fits max_lines; returns (lines, font)."""
    size = fnt.size
    while size > min_size:
        lines = wrap_text(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return lines, fnt
        size -= 1
        fnt = font(bold_path, size)
    return wrap_text(draw, text, fnt, max_w), fnt


def draw_pill(draw, x, y, label, height=20):
    bg, fg = PILL_STYLE[label]
    fnt = font(F_BOLD, 11)
    tw = draw.textlength(label, font=fnt)
    w = int(tw) + 16
    draw.rounded_rectangle([x, y, x + w, y + height], radius=height // 2, fill=bg)
    draw.text((x + 8, y + 4), label, font=fnt, fill=fg)
    return w


def draw_region_tag(draw, x, y, region):
    """Region chip: solid region-colour background, white bold text."""
    color = REGION_COLOR[region]
    fnt = font(F_BOLD, 11)
    tw = draw.textlength(region, font=fnt)
    w = int(tw) + 16
    draw.rounded_rectangle([x, y, x + w, y + 20], radius=10, fill=color)
    draw.text((x + 8, y + 4), region, font=fnt, fill=WHITE)
    return w


# ---------------------------------------------------------------- scenes
def scene_cop31(draw, x, y, w, h):
    """Antalya plenary: teal band, sun, row of small flags, podium."""
    draw.rectangle([x, y, x + w, y + h], fill=(13, 92, 86, 255))
    draw.ellipse([x + w - 66, y + 8, x + w - 22, y + 52], fill=(255, 214, 120, 255))
    cols = [(185, 28, 28), (255, 255, 255), (29, 78, 216), (232, 184, 64),
            (21, 128, 61), (124, 58, 237)]
    for i, c in enumerate(cols):
        fx = x + 14 + i * 26
        draw.line([fx, y + 14, fx, y + 44], fill=WHITE, width=2)
        draw.polygon([(fx, y + 14), (fx + 18, y + 19), (fx, y + 24)], fill=c)
    draw.rectangle([x + w // 2 - 52, y + h - 26, x + w // 2 + 52, y + h - 8],
                   fill=(9, 30, 52, 255))
    draw.rectangle([x + w // 2 - 40, y + h - 34, x + w // 2 + 40, y + h - 26],
                   fill=(255, 255, 255, 255))


def scene_g20(draw, x, y, w, h):
    """Johannesburg skyline: amber band, towers, sun, flags."""
    draw.rectangle([x, y, x + w, y + h], fill=(146, 64, 14, 255))
    draw.ellipse([x + 18, y + 8, x + 58, y + 48], fill=(255, 214, 120, 255))
    base = y + h
    towers = [(0.55, 0.30), (0.70, 0.22), (0.85, 0.34), (0.95, 0.26)]
    for fx, fh in towers:
        tw = int(w * 0.09)
        tx = int(x + w * fx)
        th = int(h * fh)
        draw.rectangle([tx, base - th, tx + tw, base], fill=(60, 32, 8, 255))
    draw.rectangle([x + int(w * 0.42), base - int(h * 0.52),
                    x + int(w * 0.50), base], fill=(60, 32, 8, 255))
    draw.rectangle([x + int(w * 0.44), base - int(h * 0.62),
                    x + int(w * 0.48), base - int(h * 0.52)], fill=(60, 32, 8, 255))
    draw.rectangle([x + int(w * 0.60), base - int(h * 0.42),
                    x + int(w * 0.64), base - int(h * 0.34)], fill=(255, 255, 255, 255))


def scene_cricket(draw, x, y, w, h):
    """Wellington Test: crimson band, stumps, bat, ball."""
    draw.rectangle([x, y, x + w, y + h], fill=(153, 27, 27, 255))
    draw.rectangle([x + w - 150, y + h - 10, x + w - 10, y + h], fill=(21, 128, 61, 255))
    for i in range(3):
        sx = x + 22 + i * 9
        draw.rectangle([sx, y + h - 30, sx + 5, y + h - 10], fill=(255, 214, 120, 255))
    draw.rectangle([x + 22, y + h - 34, x + 46, y + h - 30], fill=(255, 214, 120, 255))
    # ball, left of centre, clear of the chips at top-right
    draw.ellipse([x + 66, y + 12, x + 88, y + 34], fill=WHITE,
                 outline=(185, 28, 28), width=2)
    # bat: near-vertical, centred, clear of the chips at top-right
    bat = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bat)
    bd.rounded_rectangle([52, 30, 68, 96], radius=6, fill=(232, 184, 64, 255))
    bd.rectangle([56, 10, 64, 32], fill=(232, 184, 64, 255))
    bat = bat.rotate(22, resample=Image.BICUBIC, center=(60, 60))
    draw._image.paste(bat, (x + w // 2 - 10, y - 6), bat)


def scene_bitcoin(draw, x, y, w, h):
    """Markets: green band, gold coin with B, rising bars."""
    draw.rectangle([x, y, x + w, y + h], fill=(20, 83, 45, 255))
    bars = [0.30, 0.45, 0.38, 0.62, 0.80]
    for i, bh in enumerate(bars):
        bx = x + 16 + i * 22
        th = int(h * bh)
        draw.rectangle([bx, y + h - 8 - th, bx + 12, y + h - 8],
                       fill=(255, 255, 255, 255) if i < 4 else GOLD)
    cx, cy, r = x + w - 52, y + h // 2, 26
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD,
                 outline=(255, 255, 255, 255), width=2)
    bf = font(F_BOLD, 30)
    draw.text((cx - 10, cy - 17), "B", font=bf, fill=(20, 83, 45, 255))


def scene_tankers(draw, x, y, w, h):
    """Hormuz: purple band, two tanker silhouettes on waves."""
    draw.rectangle([x, y, x + w, y + h], fill=(76, 29, 149, 255))
    for i, (sx, sw) in enumerate([(18, 110), (150, 130)]):
        sy = y + h - 30 - i * 6
        draw.polygon([(x + sx, sy), (x + sx + sw, sy), (x + sx + sw - 12, sy + 16),
                      (x + sx + 10, sy + 16)], fill=(20, 16, 36, 255))
        draw.rectangle([x + sx + 18, sy - 14, x + sx + 34, sy], fill=(20, 16, 36, 255))
        draw.rectangle([x + sx + 44, sy - 10, x + sx + 56, sy], fill=(20, 16, 36, 255))
    for wy in (y + h - 12, y + h - 6):
        for k in range(6):
            wx = x + 8 + k * 52
            draw.arc([wx, wy - 5, wx + 34, wy + 5], 180, 360, fill=WHITE, width=2)


def scene_senate(draw, x, y, w, h):
    """Capitol: blue band, dome and columns."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 58, 138, 255))
    cx = x + w - 70
    base = y + h
    draw.rectangle([cx - 46, base - 22, cx + 46, base - 8], fill=WHITE)
    for i in range(5):
        colx = cx - 40 + i * 17
        draw.rectangle([colx, base - 40, colx + 6, base - 22], fill=WHITE)
    draw.pieslice([cx - 34, base - 66, cx + 34, base - 34], 180, 360, fill=WHITE)
    draw.rectangle([cx - 2, base - 76, cx + 2, base - 66], fill=WHITE)
    draw.line([cx + 8, base - 74, cx + 8, base - 58], fill=WHITE, width=2)
    draw.polygon([(cx + 8, base - 74), (cx + 22, base - 70), (cx + 8, base - 66)],
                 fill=(185, 28, 28, 255))
    draw.ellipse([x + 16, y + 10, x + 52, y + 46], fill=(255, 214, 120, 255))


def scene_aukus(draw, x, y, w, h):
    """AUKUS: ocean band, submarine silhouette on waves."""
    draw.rectangle([x, y, x + w, y + h], fill=(8, 74, 110, 255))
    sy = y + h // 2
    draw.rounded_rectangle([x + 24, sy - 12, x + 190, sy + 12], radius=12,
                           fill=(20, 30, 44, 255))
    draw.rectangle([x + 96, sy - 26, x + 128, sy - 10], fill=(20, 30, 44, 255))
    draw.line([x + 108, sy - 38, x + 108, sy - 26], fill=(20, 30, 44, 255), width=3)
    for wy in (y + h - 14, y + h - 7):
        for k in range(6):
            wx = x + 10 + k * 52
            draw.arc([wx, wy - 5, wx + 34, wy + 5], 180, 360, fill=WHITE, width=2)
    draw.ellipse([x + w - 56, y + 8, x + w - 20, y + 44], fill=(255, 214, 120, 255))


SCENES = {
    "cop31": scene_cop31, "g20": scene_g20, "cricket": scene_cricket,
    "bitcoin": scene_bitcoin, "tankers": scene_tankers,
    "senate": scene_senate, "aukus": scene_aukus,
}

# ---------------------------------------------------------------- world map
CONTINENTS = [
    # North America (lon, lat)
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-160, 58)],
    # South America
    [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -41), (-70, -50), (-73, -53), (-70, -40), (-73, -20),
     (-80, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -28), (20, -35),
     (15, -30), (12, -18), (9, -1), (9, 4), (-8, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (30, 60), (30, 70), (25, 71), (18, 70),
     (12, 65), (5, 60), (5, 58), (-5, 50), (-10, 43)],
    # Asia
    [(30, 70), (40, 68), (60, 69), (75, 73), (90, 75), (110, 76), (130, 72),
     (160, 70), (178, 66), (170, 60), (160, 55), (140, 40), (130, 35),
     (122, 30), (120, 20), (108, 10), (100, 8), (95, 15), (90, 22), (80, 10),
     (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (40, 36), (35, 36), (30, 36), (30, 42)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
]

# hero number -> (lon, lat) pin on the map
PINS = {
    1: (31, 37),    # COP31 Antalya
    2: (28, -26),   # G20 Johannesburg
    3: (175, -41),  # Pant, Wellington
    5: (50, 29),    # Kharg Island tankers
    6: (-77, 39),   # US Senate, Washington
    7: (149, -35),  # AUKUS, Canberra
}


def draw_map(draw, x, y, w, h):
    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (90.0 - lat) / 150.0 * h
        return (px, py)
    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly],
                     fill=(255, 255, 255, 255))
    for num, (lon, lat) in sorted(PINS.items()):
        px, py = proj(lon, lat)
        r = 9
        draw.ellipse([px - r, py - r, px + r, py + r], fill=GOLD,
                     outline=NAVY_DARK, width=2)
        nf = font(F_BOLD, 10)
        tw = draw.textlength(str(num), font=nf)
        draw.text((px - tw / 2, py - 7), str(num), font=nf, fill=NAVY_DARK)


# ---------------------------------------------------------------- content
HEROES = [
    dict(num=1, key="cop31", region="GLOBAL", pill="CONFIRMED",
         headline="COP31 nears a deal as summit runs into overtime",
         sub="New package tabled at a late-night plenary in Antalya; President "
             "Murat Kurum says all parties can agree. Approval vote 06:00 GMT. "
             "Nearly 200 delegations; after ~130 nations demanded the "
             "fossil-fuel language return to the text."),
    dict(num=2, key="g20", region="AFRICA", pill="CONFIRMED",
         headline="G20 leaders meet in Johannesburg — a first for Africa",
         sub="President Ramaphosa hosts the first G20 summit on African soil, "
             "22–23 Nov. Day one: growth, trade, food systems, inequality. No "
             "US officials attend — Trump boycotts — and a leaders' declaration "
             "looks unlikely."),
    dict(num=3, key="cricket", region="ASIA", pill="CONFIRMED",
         headline="Pant's 128 powers India's record day in Wellington",
         sub="India 683/7, lead 315 — highest Test total in New Zealand (past "
             "520, Hamilton 2009). Jurel past 50, Akash Deep hitting sixes; "
             "declaration pending on Day 4."),
    dict(num=4, key="bitcoin", region="MARKETS", pill="CONFIRMED",
         headline="Bitcoin back above $60,000 after Saturday's crash",
         sub="$60,061 at 01:31 UTC Sunday. The low was $55,130 on Saturday — "
             "lowest since Sept 2024, down 10% in a day, $2.4bn liquidated."),
    dict(num=5, key="tankers", region="MIDDLE EAST", pill="REPORTED",
         headline="Iran readies 14 tankers to test the US blockade",
         sub="Tankers gather near Kharg Island; Tehran says it will take "
             "\"any action necessary\". Power cuts start Sunday; Hormuz "
             "traffic ~65% below pre-war levels."),
    dict(num=6, key="senate", region="AMERICAS", pill="CONFIRMED",
         headline="Senate Democrats' leadership race opens",
         sub="Schumer faces challenger Chris Van Hollen; secret-ballot vote "
             "1 Dec. Thirteen incoming Democrats — the largest class in "
             "decades — with progressives backing Van Hollen."),
    dict(num=7, key="aukus", region="OCEANIA", pill="CONFIRMED",
         headline="Australia hits back at US report on AUKUS subs",
         sub="Defence Minister Marles on Sunday criticised the CBO finding "
             "that AUKUS would cut the US attack-sub fleet. A$368bn pact over "
             "three decades; first US subs in Australia from 2027."),
]

NUMBERS = [
    ("2", "days COP31 ran over"),
    ("14", "tankers Iran readied"),
    ("128", "Pant's runs in Wellington"),
    ("315", "India's lead, Day 4"),
    ("$60,061", "Bitcoin, 01:31 UTC"),
    ("06:00", "COP31 vote, GMT"),
]

ALSO = [
    ("AFRICA", "G20: no leaders' declaration expected — the US will oppose "
               "anything beyond a chair's statement."),
    ("MIDDLE EAST", "Iran starts rolling power cuts on Sunday as the war "
                    "strains the grid."),
    ("ASIA", "Dutch foreign minister Van Weel begins a two-day India visit."),
    ("ASIA", "Odisha approves a ₹249-crore cyber command centre."),
    ("ASIA", "50 garment factories still shut in Bangladesh amid wage unrest."),
    ("ASIA", "US envoy Gor hails the India–US crackdown on drug trafficking."),
]

DATE_CHECK_A = [
    "El Chapo Isidro captured — Fri night, announced Sat",
    "Gaza: Israeli fire killed 4 — Sat",
    "Russian cargo ship Sparta II hit by drones — Sat",
    "EU unveils 3% Big Tech tax draft — Sat",
    "Trump's 10% credit-card cap — Sat",
]
DATE_CHECK_B = [
    "Peru quake 6.7; Brazil storm — Fri",
    "Kryvyi Rih triple-tap: 2 killed, 60 hurt — Fri",
    "Russian missiles landed in Poland — Fri",
    "ICJ: Myanmar committed genocide — Thu verdict",
    "F1 Vegas qualifying; Manipur deaths 11 — Fri",
]


# ---------------------------------------------------------------- build
def draw_hero(draw, hero, x, y, w, h, illo_h=64, max_sub=4):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD,
                           outline=LINE, width=1)
    SCENES[hero["key"]](draw, x + 1, y + 1, w - 2, illo_h)
    # number badge on the illustration
    nb = 26
    draw.ellipse([x + 10, y + 10, x + 10 + nb, y + 10 + nb], fill=GOLD,
                 outline=NAVY_DARK, width=2)
    nf = font(F_BOLD, 14)
    tw = draw.textlength(str(hero["num"]), font=nf)
    draw.text((x + 10 + (nb - tw) / 2, y + 13), str(hero["num"]), font=nf,
              fill=NAVY_DARK)
    # region chip + pill on the illustration, right-aligned
    tf = font(F_BOLD, 11)
    tag_w = int(draw.textlength(hero["region"], font=tf)) + 16
    draw_region_tag(draw, x + w - 10 - tag_w, y + 10, hero["region"])
    pill_w = int(draw.textlength(hero["pill"], font=tf)) + 16
    draw_pill(draw, x + w - 10 - pill_w, y + 32, hero["pill"])
    # headline
    tx = x + 14
    tw_max = w - 28
    ty = y + illo_h + 10
    head_f = font(F_BOLD, 19 if h >= 200 else (18 if h >= 170 else 17))
    lines, head_f = fit_lines(draw, hero["headline"], head_f, tw_max, 2, 15, F_BOLD)
    for i, ln in enumerate(lines):
        draw.text((tx, ty + i * (head_f.size + 5)), ln, font=head_f, fill=INK)
    ty += len(lines) * (head_f.size + 5) + 4
    # sub
    sub_size = 13 if h >= 200 else 12
    sub_f = font(F_REG, sub_size)
    sub_lines = wrap_text(draw, hero["sub"], sub_f, tw_max)
    sub_lines = sub_lines[:max_sub]
    for i, ln in enumerate(sub_lines):
        draw.text((tx, ty + i * (sub_size + 4)), ln, font=sub_f, fill=MUTED)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead
    draw.rectangle([0, 0, W, 112], fill=NAVY)
    draw.rectangle([0, 112, W, 114], fill=GOLD)
    kicker = font(F_BOLD, 14)
    draw.text((24, 12), "THE WORLD IN ONE PICTURE  ·  SUNDAY EDITION",
              font=kicker, fill=GOLD)
    title = font(F_BOLD, 44)
    draw.text((24, 32), "SUNDAY, 22 NOVEMBER 2026", font=title, fill=WHITE)
    sub = font(F_REG, 15)
    draw.text((24, 86), "The day's world news — verified as of 02:00 UTC, 13 stories, 6 regions",
              font=sub, fill=(200, 214, 228, 255))
    draw_map(draw, 712, 8, 288, 88)

    # ---- numbers strip
    y0, y1 = 114, 162
    draw.rectangle([0, y0, W, y1], fill=WHITE)
    draw.line([0, y1, W, y1], fill=LINE, width=1)
    cell_w = W / len(NUMBERS)
    for i, (num, label) in enumerate(NUMBERS):
        cx = int(i * cell_w)
        if i:
            draw.line([cx, y0 + 8, cx, y1 - 8], fill=LINE, width=1)
        nf = font(F_BOLD, 24)
        lf = font(F_REG, 11)
        nw = draw.textlength(num, font=nf)
        draw.text((cx + (cell_w - nw) / 2, y0 + 5), num, font=nf, fill=NAVY)
        lw = draw.textlength(label, font=lf)
        draw.text((cx + (cell_w - lw) / 2, y0 + 32), label, font=lf, fill=MUTED)

    # ---- hero grid
    draw_hero(draw, HEROES[0], 24, 170, 481, 218, illo_h=64, max_sub=4)
    draw_hero(draw, HEROES[1], 519, 170, 457, 218, illo_h=64, max_sub=4)
    draw_hero(draw, HEROES[2], 24, 396, 322, 178, illo_h=48, max_sub=4)
    draw_hero(draw, HEROES[3], 360, 396, 304, 178, illo_h=48, max_sub=4)
    draw_hero(draw, HEROES[4], 678, 396, 322, 178, illo_h=48, max_sub=4)
    draw_hero(draw, HEROES[5], 24, 582, 481, 152, illo_h=44, max_sub=3)
    draw_hero(draw, HEROES[6], 519, 582, 457, 152, illo_h=44, max_sub=3)

    # ---- ALSO
    y0, y1 = 742, 868
    draw.rounded_rectangle([24, y0, 1000, y1], radius=10, fill=ALSO_BG)
    ah = font(F_BOLD, 14)
    draw.text((40, y0 + 8), "ALSO TODAY — 6 MORE STORIES", font=ah, fill=NAVY)
    draw.text((760, y0 + 8), "8 – 13", font=font(F_BOLD, 12), fill=MUTED)
    af = font(F_REG, 12)
    bf = font(F_BOLD, 12)
    row_y = y0 + 32
    for row in range(3):
        for col in range(2):
            idx = row * 2 + col
            region, text = ALSO[idx]
            x = 40 + col * 488
            num = str(8 + idx)
            draw.ellipse([x, row_y + 1, x + 18, row_y + 19], fill=NAVY)
            nf = font(F_BOLD, 11)
            tw = draw.textlength(num, font=nf)
            draw.text((x + (18 - tw) / 2, row_y + 3), num, font=nf, fill=WHITE)
            rx = x + 24
            rw = draw_region_tag(draw, rx, row_y + 3, region)
            lines = wrap_text(draw, text, af, 488 - 24 - rw - 10)
            for i, ln in enumerate(lines[:2]):
                draw.text((rx + rw + 8, row_y + 3 + i * 15), ln, font=af, fill=INK)
        row_y += 31

    # ---- DATE CHECK
    y0, y1 = 876, 966
    draw.rounded_rectangle([24, y0, 1000, y1], radius=10, fill=CHECK_BG,
                           outline=CHECK_LINE, width=1)
    dh = font(F_BOLD, 13)
    draw.text((40, y0 + 7), "DATE CHECK — NOT TODAY: checked and left out",
              font=dh, fill=(153, 27, 27, 255))
    df = font(F_REG, 11)
    for col, items in enumerate((DATE_CHECK_A, DATE_CHECK_B)):
        x = 40 + col * 488
        for i, item in enumerate(items):
            draw.text((x, y0 + 28 + i * 12), "✕  " + item, font=df,
                      fill=(120, 40, 40, 255))

    # ---- footer
    ff = font(F_REG, 11)
    draw.text((24, 974),
              "Sources: Reuters · AP · AFP · Al Jazeera · Gulf News · Finnhub · Dawn · Arab News",
              font=ff, fill=MUTED)
    draw.text((24, 990),
              "Regions: GLOBAL 2 · AFRICA 2 · ASIA 5 · MIDDLE EAST 2 · AMERICAS 1 · OCEANIA 1 = 13 stories  ·  "
              "Built 02:00 UTC, 22 Nov 2026",
              font=ff, fill=MUTED)

    img.save(OUT, format="PNG", optimize=False)
    data = open(OUT, "rb").read()
    print("wrote", OUT, len(data), "bytes",
          "sha256", hashlib.sha256(data).hexdigest())
    return OUT


if __name__ == "__main__":
    render()
