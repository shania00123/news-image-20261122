#!/usr/bin/env python3
"""news-image-20261122 RIVAL10 — 'THE SUNDAY CHRONICLE'.
Built from scratch with PIL only. No code, text or layout was copied from
any earlier rival: the RIVAL9 poster was studied only as a rendered image,
and every line below was authored here.

Content: 36 stories (3 hero + 19 grid + 14 ALSO), 22 pinned on the map,
DATE CHECK 21 items, MARKETS 6 figures, certainty labels + HOW TO READ.
All facts re-verified against the web on 23 Nov 2026 (see README.md).
Deterministic render: same bytes every run.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (176, 30, 36)
RED_DK = (140, 20, 26)
NAVY = (28, 52, 88)
NAVY_DK = (18, 38, 66)
GOLD = (176, 132, 32)
GREY = (110, 104, 92)
RULE = (190, 182, 166)
CREAM = (252, 249, 240)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"


def F(size, bold=False, serif=True, italic=False):
    path = (SERIF if serif else SANS) % (
        "BoldItalic" if (bold and italic) else
        "Bold" if bold else
        "Italic" if italic else "Regular")
    return ImageFont.truetype(path, size)


def tw(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, maxw):
    """Greedy word wrap; returns list of lines that fit maxw."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(draw, trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, font, maxw, fill=INK, leading=None,
                 max_lines=None):
    lines = wrap(draw, text, font, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    lh = leading if leading is not None else int(font.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def hline(draw, x0, x1, y, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, fill=RULE, width=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


# ---------------------------------------------------------------- data
MASTHEAD_NAME = "THE SUNDAY CHRONICLE"
KICKER = ("COP31 collapses with no deal \u00b7 Russia fires 186 drones \u00b7 "
          "Iran claims two US radars hit")
STATS = [
    ("48h", "COP31 OVERTIME"),
    ("186", "DRONES AT UKRAINE"),
    ("161", "DOWNED OR JAMMED"),
    ("720/9", "INDIA'S TEST TOTAL"),
    ("$61,568", "BITCOIN SUNDAY HIGH"),
    ("98.79%", "HK TURNOUT, RECORD"),
]
TIMELINE = ("THE DAY IN UTC \u2014 03:00 COP31 objections close \u00b7 "
            "05:30 Verstappen wins Vegas \u00b7 06:00 COP31 approval due \u00b7 "
            "09:29 Hamas seeks talks \u00b7 14:15 HK count done")
MARKETS = [
    ("GOLD", "PER OZ", "$3,539", None),
    ("BITCOIN", "SUNDAY HIGH", "$61,568", None),
    ("TASI", "RIYADH", "9,960.44", "\u22121.95%"),
    ("QATAR", "DOHA", "9,902.87", "\u22121.59%"),
    ("EGX30", "CAIRO", "49,989.79", "\u22122.85%"),
    ("EGX70", "CAIRO", "16,534.42", "\u22125.55%"),
]

HEROES = [
    dict(num=1, place="ANTALYA", tag="48 HOURS OVERTIME", cert="REPORTED",
         head="COP31 collapses with no deal",
         deck=("The EU, UK and Panama rejected a final text that omitted "
               "fossil fuels \u2014 the first breakdown since COP15 in "
               "2009. The EU walked out."),
         red=None),
    dict(num=2, place="KYIV REGION", tag="186 DRONES", cert="REPORTED",
         head="Russia fires 186 drones; Dymer block destroyed",
         deck=("161 downed or jammed; 72 jet-powered. One destroyed a "
               "five-storey block in Dymer; 2 dead, 14 missing."),
         red="Tonight: 186 drones, not 400."),
    dict(num=3, place="MANAMA", tag="CLAIM", cert="CLAIM",
         head="Iran claims two US radars hit; Bahrain denies it",
         deck=("IRGC media claimed Saturday-night strikes hit two US "
               "Patriot radars; Bahrain says it intercepted them. "
               "Two hurt; a civilian plant burned."),
         red=None),
]

# grid cards 4..22: (num, place, cert, headline, deck, strip colour, motif)
GRID = [
    (4, "HONG KONG", "REPORTED", "Hong Kong turnout hits record 98.79%",
     "5,640 of 5,709 voted; count done 22:15. Beats 89.77% in 2021.",
     (31, 58, 95), "ballot"),
    (5, "WELLINGTON", "REPORTED", "India declare 720/9 \u2014 a record in NZ",
     "Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.",
     (96, 74, 28), "stumps"),
    (6, "LAS VEGAS", "REPORTED", "Verstappen wins Vegas by 0.639s",
     "75th career win; Norris 2nd, Piastri 3rd from 17th.",
     (120, 28, 28), "flag"),
    (7, "SEOUL", "REPORTED", "Seoul minister quits over AI exam scandal",
     "Choi Kyo-jin resigned; Lee accepted in an hour. 111 cheating cases probed.",
     (88, 44, 120), "paper"),
    (8, "FINLAND", "REPORTED", "Sparta II still burning off Finland",
     "Struck Sat; fire smouldered Sun. Helo breached Finnish airspace by 4.1 km.",
     (28, 96, 110), "ship"),
    (9, "KRYVYI RIH", "REPORTED", "Missile kills boy, 7, and medic, 20; 73 hurt",
     "Hometown double-tap: four fires, ~23 blocks hit; 73 hurt by Sat evening, incl. 9 children.",
     (150, 30, 30), "flame"),
    (10, "SAN ANTONIO", "REPORTED", "Wembanyama drops 50 as Spurs rout Pelicans",
     "San Antonio's star scores 50 in a 114-91 rout of New Orleans.",
     (24, 64, 110), "ball"),
    (11, "CIKANDE", "REPORTED", "Candy-factory fire: 3 dead, 36 missing",
     "Blaze broke out Saturday 17:00; search went on Sunday; 300 workers inside.",
     (140, 60, 20), "warn"),
    (12, "GAZA", "REPORTED", "Hamas seeks urgent talks after aid-van strike",
     "Aid-van strike killed workers Sat; Hamas seeks talks on aid access.",
     (60, 90, 50), "bubble"),
    (13, "BAYELSA", "REPORTED", "Nigeria boat toll reaches 24",
     "Capsized Friday; Ayama-Ukubie; 24 dead, 24 rescued. Manager held.",
     (20, 80, 110), "waves"),
    (14, "VATICAN", "REPORTED", "Pope Leo XIV hosts 1,300 for lunch",
     "10th World Day of the Poor; lunch in Paul VI Hall, a week of events.",
     (120, 90, 30), "dome"),
    (15, "FUKUSHIMA", "REPORTED", "1,500 still cut off by Japan landslide",
     "Stranded in Kitashiobara since Saturday; heavy rain hampered rescue.",
     (70, 90, 110), "mount"),
    (16, "MINDANAO", "REPORTED", "M6.0 quake off Mindanao; no damage",
     "Off southern Mindanao, 15:54 local, depth 10 km. No tsunami.",
     (40, 110, 90), "pulse"),
    (17, "CANBERRA", "REPORTED", "Albanese: US report \u2018wrong\u2019 on AUKUS",
     "Defence minister rejects CBO warning on subs cost; US $368bn programme.",
     (90, 60, 110), "sub"),
    (18, "TURIN", "FORECAST", "Zverev v Alcaraz in Turin final today",
     "ATP Finals title match closes the season in Turin.",
     (150, 110, 20), "tennis"),
    (19, "WARSAW", "FORECAST", "NATO to meet Monday over Poland incursion",
     "Drone debris confirmed in Nowy Lipowiec. Council meets Monday.",
     (30, 70, 130), "star"),
    (20, "TALLINN", "REPORTED", "Moscow vows retaliation as Estonia seals border",
     "Estonia seals crossings for months; Moscow calls it a new Iron Curtain.",
     (110, 40, 60), "fence"),
    (21, "DELHI", "REPORTED", "Nepal PM Shah lands in Delhi",
     "First foreign trip; talks with Modi on Monday.",
     (60, 60, 60), "plane"),
    (22, "LIVERPOOL", "REPORTED", "Liverpool rout Man Utd 4\u20130 on Pochettino debut",
     "Szoboszlai 10\u2032, Wirtz 13\u2032, Ngumoha 66\u2032, Mu\u00f1oz 82\u2032. Yoro off 8\u2032; United 19th.",
     (150, 30, 30), "score"),
]

HOWTO = [
    ("\u25cf", "REPORTED", "confirmed by 2+ sources"),
    ("\u25cb", "CLAIM", "asserted by one side"),
    ("\u25f7", "FORECAST", "not yet happened"),
    ("", "FULL TIME", "score final"),
    ("", "\u2020 in ALSO", "dated Fri / Sat"),
]

# ALSO 23..36 — (num, region, text, dateline, mark)
ALSO = [
    (23, "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv", ""),
    (24, "WORLD", "Russia says it downed 170 Ukrainian drones overnight", "Moscow", "\u25cb CLAIM"),
    (25, "WORLD", "Bitcoin back above $60,000 after Saturday\u2019s $55,130 low", "Coinbase", ""),
    (26, "AMERICAS", "San Francisco braces for record-long tides", "NWS", "\u25f7 FORECAST"),
    (27, "MIDDLE EAST", "US denies Iran claim it downed two US radars", "CENTCOM", "\u25cb CLAIM"),
    (28, "EUROPE", "Lebanon marks 83rd Independence Day", "Beirut", ""),
    (29, "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children, in W. Kordofan", "", ""),
    (30, "MIDDLE EAST", "Iraq: fire at Hartha power station kills 4, injures 35", "Basra", "\u2020 SAT"),
    (31, "EUROPE", "Moldova: Russian drone crosses border twice near Purcari", "Chisinau", "\u2020 SAT"),
    (32, "AFRICA", "Somalia: UAE envoy\u2019s 72 hours run out today (ordered Thu)", "Mogadishu", ""),
    (33, "ASIA-PACIFIC", "Manipur liquor toll 19, 600+ in hospital \u2014 (Sun a.m., still rising)", "Imphal", ""),
    (34, "ASIA-PACIFIC", "M5.3 Celebes Sea, 61 km, 07:54 UTC", "EMSC", ""),
    (35, "AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "Brasilia", ""),
    (36, "EUROPE", "Hull 2\u20130 Brighton", "MKM", ""),
]

DATECHECK = [
    "Peru quake \u2014 Fri 20 Nov",
    "Gaza aid-van strike \u2014 Sat 21 Nov",
    "Japan poll: 62% feel affinity to Korea \u2014 Fri 20 Nov",
    "Mlambo-Ngcuka dies \u2014 Fri 20 Nov",
    "Denmark expels Russian attach\u00e9 \u2014 Fri 20 Nov",
    "Qatar talks in Tehran \u2014 Fri 20 Nov",
    "Russia\u2019s 400-drone barrage \u2014 night of 19\u201320 Nov",
    "BepiColombo at Mercury \u2014 Sat 21 Nov",
    "Sparta II struck \u2014 Sat 21 Nov",
    "Newcastle 2\u20132 Arsenal; Chelsea 1\u20134 Leeds \u2014 Sat 21 Nov",
    "DR Congo Cantine attack \u2014 night of 5\u20136 Nov",
    "Estonia closes border \u2014 decided Fri 20 Nov",
    "UK\u2013EU food deal agreed \u2014 Fri 20 Nov",
    "148-drone night / Kryvyi Rih double-tap \u2014 Fri 20\u2013Sat 21 Nov",
    "ICJ Myanmar ruling \u2014 Thu 19 Nov",
    "Bayelsa boat capsizes \u2014 Fri 20 Nov",
    "Aoun\u2019s Israel-withdrawal speech \u2014 Sat 21 Nov",
    "Nvidia SEC probe \u2014 Fri 20 Nov",
    "\u2018El Chapo\u2019 Isidro captured \u2014 Fri 20 Nov",
    "Trump\u2013Xi\u2013Putin talks \u2014 Thu 19 Nov",
    "H-6 bomber nears Manila \u2014 Sat 21 Nov",
]

SOURCES = ("Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 BBC \u00b7 "
           "The Times \u00b7 Formula 1 \u00b7 Cricinfo \u00b7 PHIVOLCS \u00b7 "
           "Vatican News \u00b7 QNA \u00b7 Saudi Exchange \u00b7 EGX \u2014 "
           "verified vs Sunday 22 Nov 2026.")

# ---------------------------------------------------------------- motifs
def motif(draw, kind, x, y, w, h, fg):
    """Tiny pictogram inside a card's coloured strip (strip is h px tall)."""
    cy = y + h // 2
    if kind == "ballot":
        draw.rectangle([x + 2, cy - 3, x + 9, cy + 3], outline=fg, width=1)
        draw.line([(x + 3, cy - 5), (x + 6, cy - 2), (x + 10, cy - 6)],
                  fill=fg, width=1)
        draw.rectangle([x + 11, cy - 1, x + 14, cy + 2], fill=fg)
    elif kind == "stumps":
        for dx in (0, 3, 6):
            draw.line([(x + 2 + dx, cy - 4), (x + 2 + dx, cy + 4)],
                      fill=fg, width=1)
        draw.line([(x + 1, cy - 4), (x + 9, cy - 4)], fill=fg, width=1)
        draw.ellipse([x + 12, cy - 2, x + 15, cy + 1], fill=fg)
    elif kind == "flag":
        for i in range(4):
            for j in range(2):
                if (i + j) % 2 == 0:
                    draw.rectangle([x + 2 + i * 3, cy - 4 + j * 4,
                                    x + 4 + i * 3, cy - 1 + j * 4], fill=fg)
    elif kind == "paper":
        draw.rectangle([x + 3, cy - 5, x + 11, cy + 5], outline=fg, width=1)
        for dy in (-2, 0, 2):
            draw.line([(x + 5, cy + dy), (x + 9, cy + dy)], fill=fg, width=1)
    elif kind == "ship":
        draw.polygon([(x + 2, cy + 2), (x + 13, cy + 2), (x + 11, cy + 5),
                      (x + 4, cy + 5)], fill=fg)
        draw.line([(x + 8, cy + 2), (x + 8, cy - 4)], fill=fg, width=1)
        draw.polygon([(x + 8, cy - 4), (x + 8, cy), (x + 12, cy)],
                     fill=(255, 150, 60))
    elif kind == "flame":
        draw.polygon([(x + 8, cy - 5), (x + 11, cy), (x + 9, cy + 4),
                      (x + 5, cy + 4), (x + 3, cy)], fill=(255, 150, 60))
        draw.ellipse([x + 6, cy - 1, x + 10, cy + 3], fill=(255, 220, 90))
    elif kind == "ball":
        draw.ellipse([x + 3, cy - 4, x + 11, cy + 4], outline=fg, width=1)
        draw.arc([x + 3, cy - 4, x + 11, cy + 4], 200, 340, fill=fg, width=1)
        draw.line([(x + 7, cy - 4), (x + 7, cy + 4)], fill=fg, width=1)
    elif kind == "warn":
        draw.polygon([(x + 8, cy - 5), (x + 13, cy + 4), (x + 3, cy + 4)],
                     outline=fg, width=1)
        draw.text((x + 7, cy - 2), "!", font=F(7, bold=True, serif=False),
                  fill=fg)
    elif kind == "bubble":
        draw.ellipse([x + 2, cy - 4, x + 13, cy + 3], outline=fg, width=1)
        draw.polygon([(x + 5, cy + 3), (x + 7, cy + 6), (x + 8, cy + 3)],
                     fill=fg)
    elif kind == "waves":
        for dy in (-2, 1):
            for k in range(3):
                draw.arc([x + 1 + k * 4, cy + dy - 2, x + 5 + k * 4,
                          cy + dy + 2], 180, 360, fill=fg, width=1)
    elif kind == "dome":
        draw.arc([x + 2, cy - 4, x + 13, cy + 4], 180, 360, fill=fg, width=1)
        draw.line([(x + 2, cy + 4), (x + 13, cy + 4)], fill=fg, width=1)
        draw.line([(x + 8, cy - 6), (x + 8, cy - 4)], fill=fg, width=1)
    elif kind == "mount":
        draw.polygon([(x + 1, cy + 4), (x + 6, cy - 5), (x + 9, cy),
                      (x + 12, cy - 3), (x + 15, cy + 4)], outline=fg,
                     width=1)
        draw.polygon([(x + 5, cy - 3), (x + 6, cy - 5), (x + 8, cy - 2),
                      (x + 6, cy - 1)], fill=fg)
    elif kind == "pulse":
        draw.line([(x + 1, cy), (x + 4, cy), (x + 6, cy - 4), (x + 8, cy + 3),
                   (x + 10, cy - 2), (x + 12, cy), (x + 15, cy)],
                  fill=fg, width=1)
    elif kind == "sub":
        draw.ellipse([x + 2, cy - 2, x + 13, cy + 3], fill=fg)
        draw.rectangle([x + 6, cy - 4, x + 9, cy - 2], fill=fg)
        draw.line([(x + 2, cy + 1), (x + 0, cy + 1)], fill=fg, width=1)
    elif kind == "tennis":
        draw.ellipse([x + 3, cy - 4, x + 11, cy + 4], outline=fg, width=1)
        draw.arc([x + 3, cy - 4, x + 11, cy + 4], 300, 60, fill=fg, width=1)
        draw.arc([x + 3, cy - 4, x + 11, cy + 4], 120, 240, fill=fg, width=1)
    elif kind == "star":
        cx, cyy, r1, r2 = x + 8, cy, 5, 2
        pts = []
        for i in range(10):
            import math
            ang = -math.pi / 2 + i * math.pi / 5
            r = r1 if i % 2 == 0 else r2
            pts.append((cx + r * math.cos(ang), cyy + r * math.sin(ang)))
        draw.polygon(pts, fill=fg)
    elif kind == "fence":
        for dx in (1, 5, 9, 13):
            draw.line([(x + dx, cy - 4), (x + dx, cy + 4)], fill=fg, width=1)
        draw.line([(x + 1, cy - 1), (x + 14, cy - 1)], fill=fg, width=1)
        draw.line([(x + 1, cy + 2), (x + 14, cy + 2)], fill=fg, width=1)
    elif kind == "plane":
        draw.polygon([(x + 1, cy), (x + 6, cy - 2), (x + 13, cy - 4),
                      (x + 11, cy), (x + 13, cy + 4), (x + 6, cy + 2)],
                     fill=fg)
    elif kind == "score":
        draw.text((x + 1, cy - 5), "4\u20130", font=F(8, bold=True,
                  serif=False), fill=fg)


# ---------------------------------------------------------------- hero art
SKINS = [(232, 196, 160), (198, 152, 112), (160, 110, 78), (238, 210, 180),
         (120, 82, 58)]
SUITS = [(38, 52, 80), (90, 30, 30), (40, 70, 50), (60, 60, 64),
         (110, 80, 30), (70, 40, 90), (30, 80, 90)]


def delegate(draw, cx, base_y, s, skin, suit, laptop=False):
    """One seated delegate at scale s: head, shoulders, nameplate."""
    r = 4.5 * s
    draw.ellipse([cx - r, base_y - 2 * r - 6 * s, cx + r,
                  base_y - 6 * s], fill=skin)
    draw.polygon([(cx - 8 * s, base_y), (cx - 6 * s, base_y - 7 * s),
                  (cx + 6 * s, base_y - 7 * s), (cx + 8 * s, base_y)],
                 fill=suit)
    draw.rectangle([cx - 7 * s, base_y + 1, cx + 7 * s, base_y + 4 * s],
                   fill=(240, 236, 222), outline=(150, 140, 120))
    if laptop:
        draw.rectangle([cx - 5 * s, base_y - 9 * s, cx + 5 * s,
                        base_y - 6 * s], fill=(200, 210, 220),
                       outline=(120, 130, 140))


def hero1_art(d, x0, y0, w, h):
    """COP31 final plenary, drawn with perspective: warm spotlight cone,
    a small back row, a larger front row, foreground presidium desk and
    three empty walkout chairs under a red WALKOUT banner."""
    # wall: warm brown gradient
    for i in range(h):
        t = i / max(1, h - 1)
        d.rectangle([x0, y0 + i, x0 + w, y0 + i + 1],
                    fill=(int(96 - 34 * t), int(66 - 22 * t),
                          int(42 - 14 * t)))
    # warm spotlight cone from top centre
    cone = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cone)
    cd.polygon([(w * 0.42, 0), (w * 0.58, 0), (w * 0.86, h),
                (w * 0.14, h)], fill=(255, 205, 130, 82))
    cd.polygon([(w * 0.46, 0), (w * 0.54, 0), (w * 0.68, h),
                (w * 0.32, h)], fill=(255, 220, 150, 72))
    d._image.paste(Image.alpha_composite(d._image.convert("RGBA"), cone)
                   .convert("RGB"), (0, 0))
    # ceiling light bar
    d.rectangle([x0 + w * 0.30, y0 + 3, x0 + w * 0.70, y0 + 6],
                fill=(255, 225, 160))
    # screen
    sx0, sy0, sx1, sy1 = x0 + 14, y0 + 8, x0 + w - 118, y0 + 30
    d.rectangle([sx0, sy0, sx1, sy1], fill=(16, 44, 66),
                outline=(200, 210, 220))
    d.text((sx0 + 6, sy0 + 3), "COP31 \u00b7 ANTALYA",
           font=F(11, bold=True, serif=False), fill=(255, 255, 255))
    d.text((sx0 + 6, sy0 + 13), "FINAL PLENARY",
           font=F(9, bold=True, serif=False), fill=(255, 205, 120))
    # side flags on the screen wall
    for fx, fc in ((x0 + w - 104, (176, 30, 36)),
                   (x0 + w - 88, (28, 52, 88)),
                   (x0 + w - 72, (40, 110, 60))):
        d.rectangle([fx, y0 + 10, fx + 11, y0 + 26], fill=fc,
                    outline=(220, 220, 220))
    # back row of delegates (smaller, higher, dimmer)
    back_y = y0 + h - 46
    for i, cx in enumerate([x0 + 22 + k * 34 for k in range(8)]):
        delegate(d, cx, back_y, 0.62, SKINS[i % 5], SUITS[i % 7],
                 laptop=(i % 3 == 0))
    d.rectangle([x0 + 6, back_y + 5, x0 + w - 6, back_y + 9],
                fill=(70, 48, 30))
    # front row of delegates (larger, closer)
    front_y = y0 + h - 24
    for i, cx in enumerate([x0 + 16 + k * 40 for k in range(6)]):
        delegate(d, cx, front_y, 1.0, SKINS[(i + 2) % 5], SUITS[(i + 1) % 7],
                 laptop=(i % 2 == 0))
    # shadows under the front row
    for cx in [x0 + 16 + k * 40 for k in range(6)]:
        d.ellipse([cx - 12, front_y + 5, cx + 12, front_y + 9],
                  fill=(40, 26, 16))
    # foreground presidium desk (bottom band, closest to viewer)
    d.rectangle([x0, y0 + h - 12, x0 + w, y0 + h], fill=(52, 34, 20))
    d.rectangle([x0 + w // 2 - 34, y0 + h - 11, x0 + w // 2 + 34,
                 y0 + h - 4], fill=(240, 236, 222), outline=(150, 140, 120))
    d.text((x0 + w // 2 - 26, y0 + h - 11), "PRESIDENCY",
           font=F(6, bold=True, serif=False), fill=(40, 30, 20))
    # walkout: three empty chairs, right side, under a red banner
    wx0 = x0 + w - 96
    d.rectangle([wx0, y0 + 34, x0 + w - 8, y0 + 50], fill=RED)
    d.text((wx0 + 8, y0 + 37), "WALKOUT", font=F(11, bold=True,
           serif=False), fill=(255, 255, 255))
    for k in range(3):
        cx = wx0 + 14 + k * 28
        cy = y0 + h - 30
        d.rectangle([cx - 9, cy, cx + 9, cy + 16], fill=(214, 204, 186),
                    outline=(120, 108, 90))
        d.rectangle([cx - 9, cy - 8, cx + 9, cy], fill=(228, 220, 204),
                    outline=(120, 108, 90))


def hero2_art(d, x0, y0, w, h):
    """Kyiv at night: three skyline layers + haze, moon halo, smoke
    columns, searchlight, drone silhouettes, fire glow behind a block."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(14, 18, 40))
    # stars
    import random
    rnd = random.Random(20261122)
    for _ in range(26):
        sx, sy = x0 + rnd.randint(2, w - 2), y0 + rnd.randint(2, h // 2)
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=(220, 220, 240))
    # moon + halo
    mx, my = x0 + w - 42, y0 + 16
    d.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=(240, 235, 210))
    d.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(250, 246, 226))
    # far skyline (hazy, small)
    for i, bx in enumerate(range(0, w, 26)):
        bh = 26 + (i * 7) % 18
        d.rectangle([x0 + bx + 2, y0 + h - 52 - bh, x0 + bx + 22,
                     y0 + h - 52], fill=(38, 44, 74))
    # mid skyline with lit windows
    for i, bx in enumerate(range(4, w, 34)):
        bh = 34 + (i * 11) % 22
        d.rectangle([x0 + bx, y0 + h - 34 - bh, x0 + bx + 28,
                     y0 + h - 34], fill=(24, 28, 56))
        for wy in range(y0 + h - 30 - bh, y0 + h - 36, 8):
            for wx in range(x0 + bx + 4, x0 + bx + 26, 7):
                if (wx + wy) % 3 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 3],
                                fill=(255, 200, 90))
    # fire glow behind one mid block + smoke (kept low, behind near skyline)
    fx = x0 + w // 3
    d.ellipse([fx - 15, y0 + h - 58, fx + 15, y0 + h - 30],
              fill=(200, 90, 20))
    d.ellipse([fx - 8, y0 + h - 50, fx + 8, y0 + h - 36],
              fill=(255, 160, 50))
    for k, (sx, sy, sr) in enumerate([(fx + 6, y0 + 16, 5),
                                      (fx + 13, y0 + 9, 6),
                                      (fx + 21, y0 + 3, 4)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(120, 120, 130))
    # searchlight beam (narrow)
    d.polygon([(x0 + w - 88, y0 + h - 34), (x0 + w - 76, y0 + h - 34),
               (x0 + w - 44, y0 + 8), (x0 + w - 56, y0 + 8)],
              fill=(255, 240, 190))
    # near skyline (dark, tall, closest)
    for i, bx in enumerate(range(0, w, 44)):
        bh = 18 + (i * 13) % 14
        d.rectangle([x0 + bx, y0 + h - bh, x0 + bx + 38, y0 + h],
                    fill=(10, 12, 28))
        for wy in range(y0 + h - bh + 4, y0 + h - 4, 7):
            for wx in range(x0 + bx + 5, x0 + bx + 34, 8):
                if (wx * 2 + wy) % 5 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 3],
                                fill=(255, 190, 80))
    # drone silhouettes
    for dx, dy in ((x0 + 52, y0 + 18), (x0 + 96, y0 + 10)):
        d.polygon([(dx, dy), (dx + 12, dy + 3), (dx, dy + 6),
                   (dx - 12, dy + 3)], fill=(8, 8, 14))
        d.ellipse([dx + 9, dy + 1, dx + 12, dy + 4], fill=(255, 60, 40))


def hero3_art(d, x0, y0, w, h):
    """Manama at dusk, with depth: hazy far skyline, mid industrial plant
    with fire + smoke, near sea with wave reflections, a large foreground
    radar dish and an interceptor arc."""
    # dusk sky gradient: deep navy -> burnt orange horizon
    for i in range(h):
        t = i / max(1, h - 1)
        d.rectangle([x0, y0 + i, x0 + w, y0 + i + 1],
                    fill=(int(16 + 120 * t * t), int(22 + 60 * t),
                          int(52 - 10 * t)))
    # far skyline (small, hazy)
    for i, bx in enumerate(range(6, w, 30)):
        bh = 14 + (i * 5) % 10
        d.rectangle([x0 + bx, y0 + h - 46 - bh, x0 + bx + 24,
                     y0 + h - 46], fill=(70, 62, 80))
        for wx in range(x0 + bx + 4, x0 + bx + 22, 6):
            if (wx + i) % 4 == 0:
                d.rectangle([wx, y0 + h - 44 - bh, wx + 2,
                             y0 + h - 41 - bh], fill=(255, 210, 130))
    # moon
    d.ellipse([x0 + w - 34, y0 + 6, x0 + w - 16, y0 + 24],
              fill=(245, 240, 220))
    # mid plant: tanks + chimneys, one burning
    px0 = x0 + w // 2 - 10
    d.rectangle([px0, y0 + h - 58, px0 + 96, y0 + h - 40],
                fill=(150, 150, 158))
    for tx in (px0 + 6, px0 + 34, px0 + 62):
        d.rectangle([tx, y0 + h - 66, tx + 20, y0 + h - 40],
                    fill=(120, 120, 128), outline=(90, 90, 96))
        d.ellipse([tx + 2, y0 + h - 66, tx + 18, y0 + h - 58],
                  fill=(170, 170, 178))
    d.rectangle([px0 + 88, y0 + h - 72, px0 + 94, y0 + h - 40],
                fill=(100, 100, 108))
    # fire + glow on the plant (tucked behind the tank tops)
    d.ellipse([px0 + 36, y0 + h - 70, px0 + 60, y0 + h - 50],
              fill=(220, 100, 20))
    d.ellipse([px0 + 42, y0 + h - 64, px0 + 56, y0 + h - 52],
              fill=(255, 180, 60))
    # smoke column
    for k, (sx, sy, sr) in enumerate([(px0 + 48, y0 + 16, 8),
                                      (px0 + 58, y0 + 8, 10),
                                      (px0 + 70, y0 + 2, 7)]):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(105, 105, 115))
    # interceptor trail: short diagonal streak from the plant, bright head
    d.line([(px0 + 92, y0 + h - 68), (px0 + 148, y0 + 14)],
           fill=(240, 240, 250), width=2)
    d.ellipse([px0 + 142, y0 + 8, px0 + 154, y0 + 20],
              fill=(255, 220, 120))
    d.ellipse([px0 + 145, y0 + 11, px0 + 151, y0 + 17],
              fill=(255, 255, 255))
    # sea: dark band with scallop waves + vertical reflections
    sy0 = y0 + h - 40
    d.rectangle([x0, sy0, x0 + w, y0 + h], fill=(18, 42, 74))
    for row in range(3):
        yy = sy0 + 5 + row * 9
        for wx in range(x0 + 4, x0 + w - 8, 22):
            d.arc([wx, yy, wx + 16, yy + 7], 180, 360,
                  fill=(90, 140, 190), width=1)
    for rx in (px0 + 44, px0 + 52, x0 + w - 70):
        d.rectangle([rx, sy0 + 2, rx + 3, y0 + h - 4], fill=(255, 170, 70))
    # foreground radar dish (large, closest) at left
    dx, dy = x0 + 34, sy0 - 30
    d.line([(dx, dy + 14), (dx, dy + 40)], fill=(200, 200, 210), width=3)
    d.arc([dx - 17, dy - 14, dx + 17, dy + 14], 180, 360,
          fill=(235, 235, 240), width=3)
    d.line([(dx - 17, dy), (dx + 17, dy)], fill=(235, 235, 240), width=2)
    d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(200, 200, 210))
    d.ellipse([dx - 20, dy + 38, dx + 20, dy + 42], fill=(10, 24, 44))
    # second smaller dish, right side
    dx2 = x0 + w - 30
    d.line([(dx2, sy0 - 8), (dx2, sy0 + 12)], fill=(200, 200, 210),
           width=2)
    d.arc([dx2 - 14, sy0 - 22, dx2 + 14, sy0 + 6], 180, 360,
          fill=(225, 225, 232), width=3)

# ---------------------------------------------------------------- map
# Coarse land polygons in (lon, lat), authored from general geography.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-80, 73), (-75, 72), (-65, 60), (-55, 47), (-60, 45), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 29), (-97, 26),
     (-97, 16), (-94, 17), (-90, 14), (-83, 9), (-79, 9), (-83, 15),
     (-90, 21), (-105, 20), (-110, 23), (-114, 28), (-120, 34),
     (-125, 40), (-124, 48), (-130, 55), (-145, 60), (-155, 58),
     (-165, 60)],  # North America
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76),
     (-55, 76), (-60, 74)],  # Greenland
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-70, -52),
     (-66, -55), (-68, -52), (-65, -45), (-62, -40), (-58, -34),
     (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9),
     (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6),
     (-62, 9), (-70, 11), (-75, 10)],  # South America
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, 0),
     (12, -4), (13, -10), (12, -17), (14, -22), (16, -28), (19, -34),
     (26, -34), (32, -28), (35, -24), (40, -16), (40, -10), (42, -4),
     (46, -1), (51, 2), (51, 11), (48, 11), (44, 11), (40, 15),
     (38, 18), (37, 22), (34, 27), (32, 31), (30, 31), (22, 33),
     (19, 32), (11, 34), (10, 37), (4, 37), (-1, 35)],  # Africa
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (-5, 48),
     (-1, 50), (0, 51), (3, 53), (5, 53), (8, 57), (8, 59), (10, 59),
     (12, 56), (18, 56), (21, 55), (24, 58), (24, 60), (28, 59),
     (30, 60), (28, 62), (25, 65), (21, 65), (18, 69), (25, 71),
     (30, 70), (32, 68), (40, 68), (44, 67), (42, 65), (40, 60),
     (38, 56), (36, 54), (35, 51), (33, 46), (30, 46), (28, 44),
     (28, 41), (23, 40), (22, 38), (19, 40), (15, 44), (12, 44),
     (8, 44), (3, 43), (-1, 38), (-6, 36), (-9, 37)],  # Europe
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73),
     (90, 75), (100, 76), (110, 74), (120, 73), (130, 72), (140, 72),
     (150, 70), (160, 69), (170, 66), (178, 65), (178, 62), (170, 60),
     (162, 56), (158, 52), (150, 59), (142, 50), (140, 45), (135, 43),
     (130, 42), (127, 40), (126, 38), (122, 38), (120, 34), (122, 30),
     (120, 27), (116, 23), (110, 20), (108, 18), (105, 10), (104, 8),
     (100, 8), (98, 10), (97, 15), (94, 17), (92, 21), (90, 22),
     (88, 22), (86, 20), (84, 19), (80, 16), (80, 13), (77, 8),
     (75, 12), (72, 20), (70, 22), (68, 23), (66, 25), (62, 25),
     (58, 25), (56, 26), (54, 26), (52, 28), (50, 29), (48, 30),
     (50, 26), (54, 24), (57, 24), (59, 22), (56, 22), (52, 20),
     (48, 18), (45, 17), (43, 15), (42, 13), (40, 15), (38, 18),
     (37, 22), (35, 24), (35, 28), (34, 31), (35, 36), (36, 36),
     (33, 42), (30, 42), (28, 41), (26, 40), (23, 40), (26, 44),
     (28, 46), (30, 46), (33, 48), (35, 50), (38, 54), (40, 58),
     (40, 62), (38, 66), (35, 68)],  # Asia
    [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    # Australia
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (142, 42), (143, 44), (145, 44), (142, 42), (140, 39),
     (138, 37), (136, 35), (133, 34), (130, 32)],  # Japan
    [(109, 1), (111, 3), (113, 4), (116, 6), (118, 2), (117, -2),
     (115, -4), (112, -3), (110, -1)],  # Borneo
    [(95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (104, -6),
     (102, -4), (100, -1), (97, 3)],  # Sumatra
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
     (107, -8)],  # Java
    [(131, -1), (134, -2), (137, -3), (140, -3), (143, -4), (146, -6),
     (148, -8), (150, -9), (147, -8), (144, -6), (141, -5), (138, -4),
     (135, -3), (132, -2)],  # New Guinea
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (175, -40), (172, -43), (169, -46)],  # New Zealand
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50)],  # Britain
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -24), (44, -25),
     (43, -21)],  # Madagascar
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xin = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xin:
                inside = not inside
        j = i
    return inside


def _on_land(lon, lat):
    return any(_in_poly(lon, lat, p) for p in LAND)


# story number -> (lon, lat)
PINS = {
    1: (30.7, 36.9), 2: (30.5, 50.4), 3: (50.6, 26.2), 4: (114.2, 22.3),
    5: (174.8, -41.3), 6: (-115.1, 36.2), 7: (127.0, 37.5),
    8: (24.0, 59.5), 9: (33.4, 47.9), 10: (-98.5, 29.4),
    11: (106.3, -6.2), 12: (34.5, 31.5), 13: (6.3, 4.9),
    14: (12.45, 41.9), 15: (140.0, 37.7), 16: (126.0, 7.0),
    17: (149.1, -35.3), 18: (7.7, 45.1), 19: (21.0, 52.2),
    20: (24.7, 59.4), 21: (77.2, 28.6), 22: (-3.0, 53.4),
}
# Fan-out nudges (px) for the tight Europe / Near-East cluster, so pins
# stop stacking on top of each other. Leader lines join pin to true spot.
NUDGE = {
    1: (18, 12), 2: (24, -2), 3: (20, 14), 8: (16, -14), 9: (28, 8),
    12: (14, 16), 14: (-10, 14), 18: (-22, -6), 19: (-10, -16),
    20: (2, -20), 22: (-26, -10),
}


def draw_map(d, x0, y0, x1, y1):
    """Dotted world map with 22 numbered pins, fan-out in Europe."""
    lon0, lon1, lat0, lat1 = -168.0, 192.0, 72.0, -56.0

    def proj(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0),
                y0 + (lat0 - lat) / (lat0 - lat1) * (y1 - y0))

    step = 6
    yy = y0 + 3
    while yy < y1 - 2:
        xx = x0 + 3
        while xx < x1 - 2:
            lon = lon0 + (xx - x0) / (x1 - x0) * (lon1 - lon0)
            lat = lat0 - (yy - y0) / (y1 - y0) * (lat0 - lat1)
            if _on_land(lon, lat):
                d.ellipse([xx - 1.5, yy - 1.5, xx + 1.5, yy + 1.5],
                          fill=(168, 158, 132))
            xx += step
        yy += step
    # pins
    for num in sorted(PINS):
        lon, lat = PINS[num]
        px, py = proj(lon, lat)
        dx, dy = NUDGE.get(num, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=GREY)
            d.line([(px, py), (qx, qy)], fill=(150, 140, 120), width=1)
        d.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], fill=RED,
                  outline=(255, 255, 255))
        tf = F(7, bold=True, serif=False)
        twd = d.textlength(str(num), font=tf)
        d.text((qx - twd / 2, qy - 5), str(num), font=tf,
               fill=(255, 255, 255))


def draw_inset(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], outline=INK, width=1, fill=CREAM)
    d.text((x0 + 6, y0 + 4), "PACIFIC \u2014 INSET",
           font=F(9, bold=True, serif=False), fill=INK)
    d.text((x0 + 6, y0 + 17), "WELLINGTON 5 \u00b7 CANBERRA 17",
           font=F(10, bold=True, serif=False), fill=INK)
    draw_wrapped(d, x0 + 6, y0 + 31,
                 "Two Pacific capitals: Test cricket in Wellington, "
                 "AUKUS in Canberra.",
                 F(9, serif=False), x1 - x0 - 12, leading=11)
    for num, lx, ly, label in ((5, x0 + 26, y1 - 26, "Wellington"),
                               (17, x0 + 130, y1 - 26, "Canberra")):
        d.ellipse([lx - 8, ly - 8, lx + 8, ly + 8], fill=RED,
                  outline=(255, 255, 255))
        tf = F(8, bold=True, serif=False)
        twd = d.textlength(str(num), font=tf)
        d.text((lx - twd / 2, ly - 6), str(num), font=tf,
               fill=(255, 255, 255))
        d.text((lx + 12, ly - 5), label, font=F(9, serif=False), fill=INK)

# ---------------------------------------------------------------- layout
ML, MR = 12, 1012
CW = MR - ML


def cert_badge(d, x, y, cert):
    """Small right-aligned certainty badge; returns its left edge."""
    f = F(8, bold=True, serif=False)
    label = cert
    wdt = d.textlength(label, font=f) + 8
    fill = RED if cert == "REPORTED" else GOLD if cert == "CLAIM" else (90, 90, 90)
    d.rectangle([x - wdt, y, x, y + 11], fill=fill)
    d.text((x - wdt + 4, y + 1), label, font=f, fill=(255, 255, 255))
    return x - wdt


def draw_top(d):
    y = 6
    f_small = F(9, bold=True, serif=False)
    d.text((ML, y), MASTHEAD_NAME + " \u2014 THE WORLD IN ONE DAY",
           font=f_small, fill=INK)
    right = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY DATE CHECKED \u00b7 SUNDAY 22 NOVEMBER 2026"
    d.text((MR - d.textlength(right, font=f_small), y), right,
           font=f_small, fill=INK)
    y = 20
    d.text((ML, y), "Sunday 22 November 2026",
           font=F(47, bold=True), fill=INK)
    y = 72
    d.text((ML, y), KICKER, font=F(13, italic=True), fill=RED)
    bf = F(10, bold=True, serif=False)
    bw = d.textlength("NO DEAL", font=bf) + 12
    d.rectangle([MR - bw, y - 1, MR, y + 13], fill=RED)
    d.text((MR - bw + 6, y + 1), "NO DEAL", font=bf, fill=(255, 255, 255))
    # stat band
    y = 90
    hline(d, ML, MR, y - 4, fill=INK, width=1)
    colw = CW / 6
    for i, (num, lab) in enumerate(STATS):
        cx = ML + i * colw
        nf = F(23, bold=True)
        d.text((cx + 4, y), num, font=nf, fill=INK)
        d.text((cx + 4, y + 25), lab, font=F(8, bold=True, serif=False),
               fill=INK)
        if i:
            vline(d, cx, y - 2, y + 35, fill=RULE, width=1)
    hline(d, ML, MR, y + 38, fill=INK, width=1)
    # timeline
    y = 132
    d.text((ML, y), TIMELINE, font=F(9, serif=False), fill=INK)
    # markets bar
    y = 146
    d.rectangle([ML, y, MR, y + 19], fill=NAVY_DK)
    d.text((ML + 6, y + 4), "MARKETS", font=F(11, bold=True, serif=False),
           fill=(255, 255, 255))
    mx = ML + 92
    cellw = (MR - mx) / 6
    for i, (name, sub, val, chg) in enumerate(MARKETS):
        cx = mx + i * cellw
        d.text((cx + 4, y + 2), name + " \u00b7 " + sub,
               font=F(7, bold=True, serif=False), fill=(180, 195, 215))
        d.text((cx + 4, y + 10), val, font=F(12, bold=True, serif=False),
               fill=(255, 255, 255))
        if chg:
            d.text((cx + 4 + d.textlength(val, font=F(12, bold=True,
                    serif=False)) + 5, y + 11), chg,
                   font=F(9, bold=True, serif=False), fill=(255, 120, 110))
        if i:
            vline(d, cx, y + 2, y + 17, fill=(70, 95, 130), width=1)
    return y + 19


def draw_heroes(d, y0):
    gap = 8
    hw = (CW - 2 * gap) // 3
    art_h = 90
    art_fns = (hero1_art, hero2_art, hero3_art)
    bottom = y0
    for i, hero in enumerate(HEROES):
        x0 = ML + i * (hw + gap)
        art = Image.new("RGB", (hw, art_h), PAPER)
        ad = ImageDraw.Draw(art)
        art_fns[i](ad, 0, 0, hw, art_h)
        d._image.paste(art, (x0, y0))
        d.rectangle([x0, y0, x0 + hw, y0 + art_h], outline=RULE, width=1)
        y = y0 + art_h + 6
        d.text((x0, y), "%d %s \u00b7 %s" % (hero["num"], hero["place"],
               hero["tag"]), font=F(10, bold=True, serif=False), fill=RED)
        cert_badge(d, x0 + hw, y, hero["cert"])
        y += 15
        y = draw_wrapped(d, x0, y, hero["head"], F(17, bold=True), hw,
                         leading=19, max_lines=3)
        y += 1
        y = draw_wrapped(d, x0, y, hero["deck"], F(9, serif=False), hw,
                         leading=10.5, max_lines=3)
        if hero["red"]:
            y += 1
            d.text((x0, y), hero["red"], font=F(10, bold=True,
                   serif=False), fill=RED)
            y += 13
        bottom = max(bottom, y)
    return bottom


def draw_grid(d, y0):
    cols, rows = 5, 4
    gap = 6
    cw = (CW - (cols - 1) * gap) // cols
    rh = 76
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            x0 = ML + c * (cw + gap)
            yy = y0 + r * rh
            if idx == len(GRID):
                # HOW TO READ box in the last slot
                d.rectangle([x0, yy, x0 + cw, yy + rh - 6], outline=INK,
                            width=1, fill=CREAM)
                d.text((x0 + 6, yy + 4), "HOW TO READ",
                       font=F(10, bold=True, serif=False), fill=INK)
                ly = yy + 18
                for mark, tag, desc in HOWTO:
                    f = F(9, serif=False)
                    if mark:
                        d.text((x0 + 6, ly), mark, font=f, fill=INK)
                    d.text((x0 + 20, ly), tag,
                           font=F(9, bold=True, serif=False), fill=INK)
                    d.text((x0 + 20 + d.textlength(tag + " ", font=F(9, bold=True, serif=False)),
                            ly), desc, font=f, fill=GREY)
                    ly += 11
                continue
            if idx > len(GRID):
                continue
            num, place, cert, head, deck, colour, kind = GRID[idx]
            # coloured strip with motif
            d.rectangle([x0, yy, x0 + cw, yy + 11], fill=colour)
            motif(d, kind, x0 + cw - 20, yy, 18, 11, (255, 255, 255))
            y = yy + 14
            d.text((x0, y), "%d %s" % (num, place),
                   font=F(10, bold=True, serif=False), fill=RED)
            cert_badge(d, x0 + cw, y, cert)
            y += 13
            y = draw_wrapped(d, x0, y, head, F(13, bold=True), cw,
                             leading=13.5, max_lines=2)
            y += 1
            draw_wrapped(d, x0, y, deck, F(9, serif=False), cw,
                         leading=10, max_lines=2)
    return y0 + rows * rh


def draw_map_section(d, y0):
    y = y0
    d.text((ML, y), "THE WORLD ON SUNDAY \u2014 22 PINNED",
           font=F(11, bold=True, serif=False), fill=INK)
    counts = ("EUROPE 13 \u00b7 M. EAST 4 \u00b7 ASIA-PAC. 8 \u00b7 "
              "AMERICAS 4 \u00b7 AFRICA 3 \u00b7 OCEANIA 2 \u00b7 WORLD 2")
    d.text((MR - d.textlength(counts, font=F(9, serif=False)), y + 1),
           counts, font=F(9, serif=False), fill=INK)
    map_y0, map_y1 = y + 16, y + 100
    inset_x0 = MR - 208
    draw_map(d, ML, map_y0, inset_x0 - 10, map_y1)
    draw_inset(d, inset_x0, map_y0 - 2, MR, map_y1 + 2)
    return map_y1 + 6


def draw_also(d, y0):
    y = y0
    d.text((ML, y), "ALSO ON SUNDAY 22 NOVEMBER \u2014 14 MORE STORIES",
           font=F(11, bold=True, serif=False), fill=INK)
    hline(d, ML, MR, y + 14, fill=INK, width=1)
    y += 17
    colw = CW // 2
    rows = 7
    f_num = F(10, bold=True, serif=False)
    f_reg = F(8, bold=True, serif=False)
    f_txt = F(10, serif=False)
    f_mark = F(8, bold=True, serif=False)
    f_dl = F(8, serif=False)
    for col in range(2):
        items = ALSO[col * rows:(col + 1) * rows]
        for k, (num, region, text, dl, mark) in enumerate(items):
            yy = y + k * 14
            xx = ML + col * colw
            d.text((xx, yy), str(num), font=f_num, fill=RED)
            rx = xx + 20
            d.text((rx, yy + 1), region, font=f_reg, fill=GREY)
            tx = rx + d.textlength(region + " ", font=f_reg)
            maxw = colw - (tx - xx) - 66
            lines = wrap(d, text, f_txt, maxw)
            d.text((tx, yy), lines[0] if lines else "", font=f_txt,
                   fill=INK)
            if mark:
                d.text((xx + colw - 62, yy + 1), mark, font=f_mark,
                       fill=RED)
            if dl:
                d.text((xx + colw - 62, yy + 1) if not mark else
                       (xx + colw - 62, yy + 9), dl, font=f_dl, fill=GREY)
                if mark:
                    pass
    return y + rows * 14


def draw_datecheck(d, y0):
    y = y0
    d.text((ML, y), "DATE CHECK \u2014 NOT SUNDAY, however listed elsewhere:",
           font=F(11, bold=True, serif=False), fill=INK)
    hline(d, ML, MR, y + 14, fill=INK, width=1)
    y += 17
    colw = CW // 3
    f = F(9, serif=False)
    rows = 7
    for col in range(3):
        items = DATECHECK[col * rows:(col + 1) * rows]
        for k, item in enumerate(items):
            yy = y + k * 10
            xx = ML + col * colw
            d.text((xx, yy), "\u25aa", font=F(8, serif=False), fill=RED)
            d.text((xx + 10, yy), item, font=f, fill=INK)
    return y + rows * 10


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = draw_top(d)
    y = draw_heroes(d, y + 6)
    y = draw_grid(d, y + 4)
    y = draw_map_section(d, y + 2)
    y = draw_also(d, y + 2)
    y = draw_datecheck(d, y + 8)
    y += 4
    d.text((ML, y), SOURCES, font=F(8, serif=False), fill=GREY)
    assert y + 10 <= H, "layout overflow: sources end at %d" % (y + 10)
    return img


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(outdir, exist_ok=True)
    img = render()
    img.save(os.path.join(outdir, "poster.png"), "PNG")


if __name__ == "__main__":
    main()
