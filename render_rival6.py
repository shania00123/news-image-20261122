#!/usr/bin/env python3
"""Render RIVAL6 poster for news-image-20261122: "THE SUNDAY ASSEMBLY".

One-day newspaper poster for Sunday 22 November 2026. 40 stories, 7 regions,
every story dated, every card labelled by certainty. PIL only, deterministic
(no timestamps, no randomness, no network). Run: python3 render_rival6.py
(or: python3 render_rival6.py poster.png) -> writes poster.png 1024x1024.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14                      # side margin
CW = W - 2 * M              # content width = 996

PAPER = (246, 241, 229)
INK = (26, 26, 26)
RED = (164, 31, 31)
NAVY = (28, 47, 77)
NAVY_DK = (20, 34, 56)
GOLD = (176, 132, 30)
GREY = (110, 105, 95)
LIGHT_LINE = (190, 182, 165)
CARD_BG = (252, 250, 244)
GREEN = (46, 110, 58)
AMBER = (176, 110, 16)
BLUE = (52, 96, 158)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "liberation/LiberationSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "liberation/LiberationSerif-Regular.ttf")
SERIF_I = os.path.join(FONT_DIR, "liberation/LiberationSerif-Italic.ttf")
SANS_B = os.path.join(FONT_DIR, "liberation/LiberationSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "liberation/LiberationSans-Regular.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- text utils
def wrap(text, font, width, max_lines=None):
    """Greedy word wrap; returns list of lines (never exceeds max_lines)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            if max_lines and len(lines) == max_lines:
                break
    if cur and (not max_lines or len(lines) < max_lines):
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    return lines


def draw_wrapped(d, x, y, text, font, width, fill, leading=None, max_lines=None):
    lines = wrap(text, font, width, max_lines)
    lh = leading or int(font.size * 1.12)
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def text_w(font, s):
    return font.getlength(s)


# ---------------------------------------------------------------- data
# certainty: R = reported, C = claim, F = forecast
HEROES = [
    dict(n=1, place="ANTALYA", tag="44 HOURS OVERTIME", cert="R",
         head="COP31 collapses with no deal",
         deck="The EU, UK and Panama rejected a final text that omitted fossil "
              "fuels \u2014 the first no-deal COP since COP6 in 2000.",
         art="plenary"),
    dict(n=2, place="KYIV REGION", tag="186 DRONES", cert="R",
         head="Russia fires 186 drones; Dymer block destroyed",
         deck="161 downed or jammed; 72 jet-powered. One destroyed a five-storey "
              "block in Dymer; 2 dead, 14 missing.",
         art="kyiv"),
    dict(n=3, place="MANAMA", tag="CLAIM", cert="C",
         head="Iran claims two US radars hit; Bahrain denies it",
         deck="IRGC media claimed Saturday-night strikes hit two US Patriot "
              "radars; Bahrain says it intercepted them. Two hurt.",
         art="manama"),
]

GRID = [
    dict(n=4, place="HONG KONG", region="ASIA-PACIFIC", cert="R",
         head="Hong Kong turnout hits record 98.79%",
         deck="5,640 of 5,709 voters cast ballots; count done 22:15. Beats 89.77% in 2021.",
         art="skyline", pal=("sunset",)),
    dict(n=5, place="WELLINGTON", region="OCEANIA", cert="R",
         head="India declare 720/9 \u2014 a record in NZ",
         deck="Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.",
         art="stadium", pal=("green",)),
    dict(n=6, place="LAS VEGAS", region="AMERICAS", cert="R",
         head="Verstappen wins Vegas by 0.639s",
         deck="75th career win; Norris 2nd, Piastri 3rd from 17th.",
         art="track", pal=("night",)),
    dict(n=7, place="SEOUL", region="ASIA-PACIFIC", cert="R",
         head="Seoul minister quits over AI exam scandal",
         deck="Choi Kyo-jin resigned; Lee accepted in an hour. 111 device-cheating cases probed.",
         art="papers", pal=("blue",)),
    dict(n=8, place="FINLAND", region="EUROPE", cert="R",
         head="Sparta II still burning off Finland",
         deck="Struck Sat; fire smouldered Sun. Helicopter suspected of violating "
              "Finnish airspace by 4.1 km.",
         art="ship", pal=("sea",)),
    dict(n=9, place="KRYVYI RIH", region="EUROPE", cert="R",
         head="Missile kills boy, 7, and medic, 20; 58 hurt",
         deck="Strike on Zelenskyy's hometown; four fires, ~23 blocks hit, "
              "hospital and schools damaged.",
         art="flame", pal=("night",)),
    dict(n=10, place="SAN ANTONIO", region="AMERICAS", cert="R",
         head="Wembanyama drops 50 as Spurs rout Pelicans",
         deck="San Antonio's star scores 50 in a 114\u201391 rout of New Orleans.",
         art="court", pal=("orange",)),
    dict(n=11, place="CIKANDE", region="ASIA-PACIFIC", cert="R",
         head="Candy-factory fire: 3 dead, 36 missing",
         deck="Blaze broke out Saturday 17:00; search went on Sunday; 300 workers inside.",
         art="flame", pal=("dusk",)),
    dict(n=12, place="GAZA", region="MIDDLE EAST", cert="R",
         head="Hamas seeks urgent talks after aid-van strike",
         deck="Aid-van strike killed aid workers on Saturday; Hamas called for "
              "urgent talks on aid access.",
         art="skyline", pal=("dusk",)),
    dict(n=13, place="BAYELSA", region="AFRICA", cert="R",
         head="Nigeria boat toll reaches 24",
         deck="Capsized Friday; Ayama-Ukubie; 24 dead, 24 rescued. Manager held.",
         art="waves", pal=("sea",)),
    dict(n=14, place="VATICAN", region="EUROPE", cert="R",
         head="Pope Leo XIV hosts 1,300 for lunch",
         deck="10th World Day of the Poor; lunch in Paul VI Hall, a week of events.",
         art="dome", pal=("gold",)),
    dict(n=15, place="FUKUSHIMA", region="ASIA-PACIFIC", cert="R",
         head="1,500 still cut off by Japan landslide",
         deck="Travellers stranded in Kitashiobara since Saturday; heavy rain hampered rescue.",
         art="peaks", pal=("green",)),
    dict(n=16, place="MINDANAO", region="ASIA-PACIFIC", cert="R",
         head="M6.0 quake off Mindanao; no damage",
         deck="Off southern Mindanao, 15:54 local, depth 10 km. No tsunami.",
         art="quake", pal=("sea",)),
    dict(n=17, place="CANBERRA", region="ASIA-PACIFIC", cert="R",
         head="Albanese: US report \u2018wrong\u2019 on AUKUS",
         deck="Defence minister rejects CBO warning on subs cost; US $368bn programme.",
         art="skyline", pal=("blue",)),
    dict(n=18, place="TURIN", region="EUROPE", cert="F",
         head="Zverev v Alcaraz in Turin final today",
         deck="ATP Finals title match closes the season in Turin.",
         art="court", pal=("green",)),
    dict(n=19, place="WARSAW", region="EUROPE", cert="F",
         head="NATO to meet Monday over Poland incursion",
         deck="Drone debris confirmed in Nowy Lipowiec. Council meets Monday.",
         art="flag", pal=("blue",)),
    dict(n=20, place="TALLINN", region="EUROPE", cert="R",
         head="Moscow vows retaliation as Estonia seals border",
         deck="Estonia seals crossings for months; Moscow calls it a new Iron Curtain.",
         art="fence", pal=("grey",)),
    dict(n=21, place="DELHI", region="ASIA-PACIFIC", cert="R",
         head="Nepal PM Shah lands in Delhi",
         deck="First foreign trip; talks with Modi on Monday.",
         art="dome", pal=("sunset",)),
    dict(n=22, place="LIVERPOOL", region="EUROPE", cert="R",
         head="Liverpool 4\u20130 Man Utd: Pochettino routed on debut",
         deck="Szoboszlai 10', Wirtz 13', Ngumoha 66', Mu\u00f1oz 82'; Yoro sent off 8'. United 19th.",
         art="stadium", pal=("red",)),
]

ALSO = [
    (23, "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "", "Kyiv"),
    (24, "EUROPE", "Russia says it downed 170 Ukrainian drones overnight", "C", "Moscow"),
    (25, "WORLD", "Bitcoin back above $60,000 after Saturday's $55,130 low", "", "Coinbase"),
    (26, "AMERICAS", "San Francisco braces for record king tides", "F", "SF"),
    (27, "MID EAST", "US denies Iran claim it downed an F-16", "C", "CENTCOM"),
    (28, "MID EAST", "Lebanon marks 83rd Independence Day", "", "Beirut"),
    (29, "EUROPE", "Cost-of-living protests across Europe, third day running", "", "Paris"),
    (30, "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children", "", "W. Kordofan"),
    (31, "AFRICA", "S. Africa holds prayer service for Mlambo-Ngcuka, 71 (died Fri)", "", "SABC"),
    (32, "OCEANIA", "Melbourne: 70 years since the 1956 Olympics opened", "", "Melbourne"),
    (33, "EUROPE", "Hull stun Brighton 2\u20130 \u2014 McBurnie late brace", "", "MKM"),
    (34, "WORLD", "Pope prays for war victims; drought-hit Papua New Guinea", "", "Vatican"),
    (35, "MID EAST", "Iraq: fire at Hartha power station kills 4, injures 35 \u2020 SAT", "", "Basra"),
    (36, "EUROPE", "Moldova: Russian drones cross border twice near Purcari \u2020 SAT", "", "Chisinau"),
    (37, "AFRICA", "Somalia: UAE envoy's 72 hours run out today (ordered Thu)", "", "Mogadishu"),
    (38, "ASIA-PACIFIC", "India: Manipur liquor toll climbs to 19, 600+ in hospital \u2014 Sun a.m., still rising", "", "Imphal"),
    (39, "ASIA-PACIFIC", "M5.3 quake in the Celebes Sea, 61 km deep, 07:54 UTC", "", "EMSC"),
    (40, "AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "", "Brasilia"),
]

DATE_CHECK = [
    ["Peru quake \u2014 Fri 20 Nov",
     "Kenya's last Ebola patient out \u2014 11 Nov",
     "Gaza aid-van strike \u2014 Sat 21 Nov",
     "Japan poll: 62% feel affinity to Korea \u2014 Fri 20 Nov",
     "Mlambo-Ngcuka dies \u2014 Fri 20 Nov",
     "EU\u2013Indonesia deal \u2014 Sat 21 Nov"],
    ["Denmark expels Russian attach\u00e9 \u2014 Fri 20 Nov",
     "Qatar talks in Tehran \u2014 Fri 20 Nov",
     "BepiColombo at Mercury \u2014 Sat 21 Nov",
     "Sparta II struck \u2014 Sat 21 Nov",
     "Newcastle 2\u20132 Arsenal; Chelsea 1\u20134 Leeds \u2014 Sat 21 Nov",
     "DR Congo Cantine attack \u2014 night of 5\u20136 Nov"],
    ["Estonia closes border \u2014 decided Fri 20 Nov",
     "UK\u2013EU food deal agreed \u2014 Fri 20 Nov",
     "Senate $350bn defence push stalls \u2014 Wed 18 Nov",
     "ICJ Myanmar ruling \u2014 Thu 19 Nov",
     "Bayelsa boat capsizes \u2014 Fri 20 Nov",
     "Aoun's Israel-withdrawal speech \u2014 Sat 21 Nov"],
]

BAND = [
    ("44h", "COP31 OVERTIME\nTO COLLAPSE"),
    ("186", "DRONES OR MISSILES\nAT UKRAINE"),
    ("161", "DOWNED OR\nJAMMED"),
    ("720/9", "INDIA'S RECORD\nTEST TOTAL"),
    ("$61,568", "BITCOIN'S SUNDAY\nHIGH"),
    ("98.79%", "HONG KONG TURNOUT,\nRECORD"),
]

MARKETS = [
    ("GOLD", "per oz., Sunday", "$3,539", ""),
    ("BITCOIN", "Sunday high", "$61,568", ""),
    ("TASI", "9,960.44, Riyadh", "\u22121.95%", "red"),
    ("QATAR", "9,902.87, Doha", "\u22121.59%", "red"),
    ("EGX30", "49,989.79, Cairo", "\u22122.85%", "red"),
    ("EGX70", "16,534.42, Cairo", "\u22125.55%", "red"),
]

TIMELINE = ("THE DAY IN UTC \u2014  03:00 COP31 objections close  \u00b7  05:30 "
            "Verstappen wins Vegas  \u00b7  06:00 COP31 approval due  \u00b7  "
            "09:29 Hamas seeks talks  \u00b7  14:15 HK count done")

CERT = {"R": ("REPORTED", GREEN), "C": ("CLAIM", AMBER), "F": ("FORECAST", BLUE)}

REGION_COLOR = {
    "EUROPE": (138, 47, 47),
    "MIDDLE EAST": (122, 90, 31),
    "ASIA-PACIFIC": (47, 93, 58),
    "AMERICAS": (47, 77, 110),
    "AFRICA": (110, 74, 47),
    "OCEANIA": (63, 110, 110),
    "WORLD": (68, 68, 68),
}

# ---------------------------------------------------------------- art
def _sky(d, box, top, bottom):
    """Vertical gradient sky inside box."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def _stars(d, box, pts):
    for (fx, fy, r) in pts:
        x = box[0] + int(fx * (box[2] - box[0]))
        y = box[1] + int(fy * (box[3] - box[1]))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 230, 210))


def _person(d, x, y, s, suit, skin=(214, 178, 140), hair=(40, 30, 22)):
    """Small seated/standing delegate: head + shoulders."""
    d.ellipse([x - 3 * s, y - 6 * s, x + 3 * s, y], fill=skin)
    d.pieslice([x - 3 * s, y - 6 * s, x + 3 * s, y + 1], 180, 360, fill=hair)
    d.polygon([(x - 6 * s, y + 9 * s), (x - 4 * s, y + 1 * s),
               (x + 4 * s, y + 1 * s), (x + 6 * s, y + 9 * s)], fill=suit)


def draw_plenary(d, box):
    """Hero 1: the COP31 final plenary in Antalya -- a real assembly hall.
    Warm wood wall, projection screen, presidium table, curved rows of
    delegate desks, and a block of EMPTY chairs where delegations walked out.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    _sky(d, box, (96, 66, 38), (52, 34, 18))
    # ceiling light strip
    d.rectangle([x0, y0, x1, y0 + 7], fill=(214, 178, 110))
    for lx in (x0 + 30, x0 + w // 2, x1 - 30):
        d.polygon([(lx - 26, y0 + 7), (lx + 26, y0 + 7),
                   (lx + 14, y0 + 26), (lx - 14, y0 + 26)],
                  fill=(196, 158, 96))
    # projection screen
    sx0, sy0 = x0 + w // 2 - 78, y0 + 10
    sx1, sy1 = x0 + w // 2 + 78, y0 + 40
    d.rectangle([sx0 - 3, sy0 - 3, sx1 + 3, sy1 + 3], fill=(30, 26, 20))
    d.rectangle([sx0, sy0, sx1, sy1], fill=(238, 230, 210))
    d.text((sx0 + 10, sy0 + 3), "COP31", font=F(SANS_B, 15), fill=(28, 47, 77))
    d.text((sx0 + 62, sy0 + 7), "ANTALYA", font=F(SANS_B, 9), fill=(120, 40, 40))
    d.text((sx0 + 62, sy0 + 19), "FINAL PLENARY", font=F(SANS_B, 8), fill=(90, 84, 72))
    # presidium table
    py = y0 + 52
    d.rectangle([x0 + 8, py, x1 - 8, py + 12], fill=(38, 24, 14))
    d.rectangle([x0 + 8, py, x1 - 8, py + 3], fill=(74, 50, 28))
    # tiny flags on the presidium table
    flag_cols = [(164, 31, 31), (226, 178, 40), (52, 96, 158), (240, 240, 240),
                 (46, 110, 58), (220, 120, 30), (140, 60, 140)]
    for i, fc in enumerate(flag_cols):
        fx = x0 + 26 + i * 16
        d.line([(fx, py - 9), (fx, py)], fill=(210, 200, 180), width=1)
        d.polygon([(fx, py - 9), (fx + 9, py - 6), (fx, py - 3)], fill=fc)
    # podium at left of the table
    px = x0 + 34
    d.polygon([(px - 2, py + 12), (px + 16, py + 12), (px + 12, y1 - 6),
               (px + 2, y1 - 6)], fill=(58, 38, 20))
    d.line([(px + 8, py - 2), (px + 12, py - 10)], fill=(200, 190, 170), width=2)
    _person(d, px + 9, py - 12, 1.0, (30, 30, 34))
    # delegate rows: three curved bands of desks; some chairs EMPTY
    suits = [(36, 40, 52), (74, 60, 44), (52, 52, 52), (90, 40, 36),
             (44, 74, 60), (60, 60, 90), (30, 30, 30)]
    rows = [(y0 + 66, 7, 1.2), (y0 + 82, 9, 1.4), (y0 + 97, 11, 1.6)]
    # empty-chair seats: (row, index) -- the walkout block, centre-front
    empty = {(0, 3), (1, 3), (1, 4), (1, 5), (2, 4), (2, 5), (2, 6)}
    for ri, (ry, count, s) in enumerate(rows):
        d.rectangle([x0 + 4, ry, x1 - 4, ry + 5], fill=(66, 44, 24))
        for i in range(count):
            cx = x0 + 16 + i * ((w - 32) // max(1, count - 1))
            if (ri, i) in empty:
                # empty chair: pale back rest only, no delegate -- the walkout
                d.rectangle([cx - 5, ry + 5, cx + 5, ry + 12],
                            fill=(168, 134, 88), outline=(120, 90, 50))
                d.rectangle([cx - 5, ry + 5, cx + 5, ry + 7], fill=(196, 162, 110))
            else:
                _person(d, cx, ry - 1, s, suits[(ri * 3 + i) % len(suits)])
                # white nameplate on the desk front + dark chair back
                d.rectangle([cx - 4, ry + 1, cx + 4, ry + 3], fill=(238, 232, 214))
                d.rectangle([cx - 6, ry + 5, cx + 6, ry + 11], fill=(70, 48, 28))
    # one delegate walking out, aisle right
    wx, wy = x1 - 26, y0 + 88
    d.line([(wx, wy - 14), (wx + 3, wy - 4)], fill=(30, 30, 34), width=3)
    d.ellipse([wx - 3, wy - 22, wx + 3, wy - 16], fill=(214, 178, 140))
    d.polygon([(wx - 4, wy - 4), (wx + 7, wy - 4), (wx + 9, wy + 6),
               (wx - 2, wy + 6)], fill=(36, 40, 52))


def draw_kyiv(d, box):
    """Hero 2: night sky over Kyiv -- drone trails, burning block."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    _sky(d, box, (24, 26, 58), (52, 44, 78))
    _stars(d, box, [(0.08, 0.15, 1), (0.22, 0.08, 1), (0.38, 0.2, 2),
                    (0.55, 0.1, 1), (0.7, 0.22, 1), (0.85, 0.12, 2),
                    (0.93, 0.3, 1), (0.3, 0.35, 1), (0.62, 0.32, 1)])
    # moon
    d.ellipse([x0 + w - 52, y0 + 12, x0 + w - 20, y0 + 44], fill=(226, 216, 188))
    d.ellipse([x0 + w - 46, y0 + 18, x0 + w - 36, y0 + 28], fill=(206, 196, 168))
    # drones: orange dots with motion trails
    drones = [(0.12, 0.28, 34), (0.3, 0.42, 26), (0.48, 0.24, 30),
              (0.62, 0.5, 22), (0.78, 0.36, 28), (0.88, 0.55, 20)]
    for fx, fy, tl in drones:
        dx, dy = x0 + int(fx * w), y0 + int(fy * h)
        d.line([(dx - tl, dy + 8), (dx, dy)], fill=(232, 140, 40), width=2)
        d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(240, 150, 44))
        d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 210, 120))
    # skyline silhouette
    base = y1 - 4
    heights = [26, 40, 30, 52, 34, 44, 28, 48, 36, 24]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 1, base - hh, bx + bw - 1, base], fill=(16, 14, 26))
        for wy in range(base - hh + 6, base - 4, 9):
            d.rectangle([bx + 4, wy, bx + 7, wy + 3], fill=(232, 180, 80))
    # one block burning: orange glow + smoke
    bx = x0 + int(0.58 * w)
    d.ellipse([bx - 16, base - 62, bx + 16, base - 30], fill=(226, 96, 28))
    d.ellipse([bx - 9, base - 54, bx + 9, base - 36], fill=(255, 190, 60))
    d.ellipse([bx - 12, base - 78, bx + 2, base - 64], fill=(120, 112, 104))
    d.ellipse([bx + 2, base - 88, bx + 16, base - 74], fill=(96, 90, 84))


def draw_manama(d, box):
    """Hero 3: night over Manama -- radar dishes, interceptor, burning plant."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    _sky(d, box, (52, 24, 26), (88, 52, 40))
    _stars(d, box, [(0.1, 0.14, 1), (0.28, 0.08, 1), (0.5, 0.16, 1),
                    (0.68, 0.1, 2), (0.9, 0.18, 1), (0.4, 0.3, 1)])
    # big low sun / glow
    d.ellipse([x0 + int(0.62 * w), y0 + 8, x0 + int(0.62 * w) + 44,
               y0 + 52], fill=(240, 150, 44))
    d.ellipse([x0 + int(0.62 * w) + 12, y0 + 20, x0 + int(0.62 * w) + 32,
               y0 + 40], fill=(255, 210, 120))
    # interceptor streak
    d.line([(x0 + 20, y0 + int(0.72 * h)), (x0 + int(0.42 * w), y0 + 14)],
           fill=(240, 236, 220), width=3)
    d.line([(x0 + 20, y0 + int(0.72 * h)), (x0 + int(0.3 * w), y0 + 30)],
           fill=(200, 196, 180), width=1)
    # rooftops with radar dishes
    base = y1 - 4
    for rx, rw, rh in [(0.06, 0.24, 30), (0.34, 0.2, 22), (0.72, 0.22, 26)]:
        bx = x0 + int(rx * w)
        d.rectangle([bx, base - rh, bx + int(rw * w), base], fill=(22, 18, 20))
    # dish 1 (left roof): white arc + feed arm
    dx, dy = x0 + int(0.16 * w), base - 30
    d.arc([dx - 22, dy - 22, dx + 22, dy + 22], 200, 340, fill=(232, 228, 214), width=4)
    d.line([(dx, dy), (dx + 14, dy - 16)], fill=(232, 228, 214), width=3)
    # dish 2 (right roof)
    dx2, dy2 = x0 + int(0.82 * w), base - 26
    d.arc([dx2 - 20, dy2 - 20, dx2 + 20, dy2 + 20], 200, 340,
          fill=(232, 228, 214), width=4)
    d.line([(dx2, dy2), (dx2 - 12, dy2 - 15)], fill=(232, 228, 214), width=3)
    # burning plant, centre-right: glow + smoke column
    px = x0 + int(0.52 * w)
    d.rectangle([px - 18, base - 14, px + 18, base], fill=(26, 20, 18))
    d.ellipse([px - 12, base - 30, px + 12, base - 10], fill=(232, 110, 30))
    d.ellipse([px - 6, base - 26, px + 6, base - 14], fill=(255, 196, 80))
    d.ellipse([px - 8, base - 52, px + 6, base - 38], fill=(110, 100, 92))
    d.ellipse([px + 2, base - 66, px + 16, base - 52], fill=(88, 80, 74))

# ------------------------------------------------------- mini card scenes
PALETTES = {
    "sunset": ((196, 120, 60), (60, 44, 52), (240, 190, 110)),
    "green": ((52, 110, 62), (30, 60, 34), (220, 230, 200)),
    "night": ((30, 32, 66), (14, 14, 26), (240, 150, 44)),
    "blue": ((70, 100, 150), (30, 46, 74), (220, 228, 240)),
    "sea": ((60, 110, 150), (24, 52, 80), (220, 235, 245)),
    "dusk": ((150, 80, 60), (52, 36, 40), (255, 190, 90)),
    "orange": ((200, 110, 40), (90, 44, 20), (255, 210, 120)),
    "gold": ((176, 132, 30), (80, 60, 22), (245, 220, 150)),
    "grey": ((110, 110, 116), (52, 52, 56), (220, 220, 224)),
    "red": ((150, 40, 40), (70, 22, 22), (245, 220, 200)),
}


def mini_scene(d, box, kind, pal):
    """Small 20px-high illustrative strip for a grid card."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky, dark, lite = PALETTES[pal]
    _sky(d, box, sky, dark)
    if kind == "skyline":
        base = y1
        hs = [10, 16, 12, 18, 11, 15, 9]
        bw = w // len(hs)
        for i, hh in enumerate(hs):
            bx = x0 + i * bw
            d.rectangle([bx + 1, base - hh, bx + bw - 1, base], fill=dark)
            d.rectangle([bx + 3, base - hh + 3, bx + 5, base - hh + 5], fill=lite)
    elif kind == "stadium":
        d.ellipse([x0 + w - 16, y0 + 2, x0 + w - 4, y0 + 14], fill=lite)
        d.rectangle([x0, y1 - 7, x1, y1], fill=(46, 120, 58))
        d.line([(x0, y1 - 7), (x1, y1 - 7)], fill=(240, 240, 240), width=1)
        d.ellipse([x0 + w // 2 - 8, y1 - 12, x0 + w // 2 + 8, y1 - 2],
                  outline=(240, 240, 240), width=1)
    elif kind == "track":
        d.line([(x0, y1 - 4), (x1, y0 + 6)], fill=(30, 30, 34), width=5)
        for i in range(6):
            cx = x0 + 8 + i * 12
            d.rectangle([cx, y0 + 2, cx + 6, y0 + 8],
                        fill=(240, 240, 240) if i % 2 == 0 else (20, 20, 20))
        d.ellipse([x0 + w // 2 - 4, y0 + 8, x0 + w // 2 + 4, y0 + 16],
                  fill=(240, 150, 44))
    elif kind == "papers":
        for i in range(3):
            px = x0 + 10 + i * 22
            d.rectangle([px, y0 + 4, px + 16, y1 - 4], fill=(245, 242, 232))
            d.line([(px + 3, y0 + 8), (px + 13, y0 + 8)], fill=(90, 90, 90), width=1)
            d.line([(px + 3, y0 + 12), (px + 13, y0 + 12)], fill=(90, 90, 90), width=1)
        d.line([(x0 + w - 22, y0 + 3), (x0 + w - 8, y1 - 5)], fill=RED, width=2)
    elif kind == "ship":
        d.rectangle([x0, y1 - 5, x1, y1], fill=(24, 52, 80))
        d.polygon([(x0 + w // 2 - 26, y1 - 6), (x0 + w // 2 + 26, y1 - 6),
                   (x0 + w // 2 + 18, y1 - 12), (x0 + w // 2 - 18, y1 - 12)],
                  fill=(40, 36, 32))
        d.rectangle([x0 + w // 2 - 4, y1 - 20, x0 + w // 2 + 4, y1 - 12],
                    fill=(60, 56, 50))
        d.ellipse([x0 + w // 2 + 22, y1 - 18, x0 + w // 2 + 32, y1 - 8],
                  fill=(240, 150, 44))
        d.ellipse([x0 + w // 2 + 25, y1 - 15, x0 + w // 2 + 29, y1 - 11],
                  fill=(255, 210, 120))
    elif kind == "flame":
        d.rectangle([x0, y1 - 6, x1, y1], fill=dark)
        fx, fy = x0 + w // 2, y1 - 6
        d.polygon([(fx - 9, fy), (fx - 5, fy - 12), (fx, fy - 6),
                   (fx + 5, fy - 14), (fx + 9, fy)], fill=(232, 110, 30))
        d.polygon([(fx - 4, fy), (fx - 2, fy - 7), (fx + 2, fy - 8),
                   (fx + 4, fy)], fill=(255, 210, 120))
    elif kind == "court":
        d.rectangle([x0, y1 - 8, x1, y1], fill=(190, 120, 60))
        d.line([(x0, y1 - 8), (x1, y1 - 8)], fill=(240, 240, 240), width=1)
        d.ellipse([x0 + w // 2 - 9, y1 - 14, x0 + w // 2 + 9, y1 - 2],
                  outline=(240, 240, 240), width=1)
        d.ellipse([x0 + 8, y0 + 4, x0 + 16, y0 + 12], fill=(230, 120, 40))
    elif kind == "waves":
        for i, yy in enumerate(range(y0 + 4, y1 - 2, 5)):
            d.arc([x0 + 4 + (i % 2) * 8, yy, x0 + 30 + (i % 2) * 8, yy + 8],
                  180, 360, fill=lite, width=1)
            d.arc([x0 + w - 34 + (i % 2) * 8, yy, x0 + w - 8 + (i % 2) * 8,
                   yy + 8], 180, 360, fill=lite, width=1)
        d.ellipse([x0 + w // 2 - 5, y0 + 3, x0 + w // 2 + 5, y0 + 13],
                  fill=(240, 220, 160))
    elif kind == "dome":
        base = y1
        d.rectangle([x0 + 10, base - 8, x1 - 10, base], fill=dark)
        d.pieslice([x0 + w // 2 - 12, base - 20, x0 + w // 2 + 12, base - 2],
                   180, 360, fill=dark)
        d.rectangle([x0 + w // 2 - 1, base - 24, x0 + w // 2 + 1, base - 18],
                    fill=dark)
        d.ellipse([x0 + 8, y0 + 3, x0 + 16, y0 + 11], fill=lite)
    elif kind == "peaks":
        d.polygon([(x0, y1), (x0 + 22, y0 + 4), (x0 + 44, y1)], fill=dark)
        d.polygon([(x0 + 30, y1), (x0 + 62, y0 + 2), (x0 + 94, y1)], fill=(40, 60, 44))
        d.polygon([(x0 + 22, y0 + 4), (x0 + 27, y0 + 9), (x0 + 17, y0 + 9)],
                  fill=(245, 245, 245))
        d.polygon([(x0 + 62, y0 + 2), (x0 + 68, y0 + 8), (x0 + 56, y0 + 8)],
                  fill=(245, 245, 245))
    elif kind == "quake":
        d.line([(x0 + 6, y1 - 4), (x0 + w // 3, y1 - 12), (x0 + w // 2, y1 - 5),
                (x0 + 2 * w // 3, y1 - 13), (x1 - 6, y1 - 4)],
               fill=(40, 36, 32), width=2)
        d.ellipse([x0 + w - 18, y0 + 3, x0 + w - 6, y0 + 15], fill=lite)
    elif kind == "flag":
        d.rectangle([x0, y0, x1, y0 + 7], fill=(240, 240, 240))
        d.rectangle([x0, y0 + 7, x1, y0 + 13], fill=(52, 96, 158))
        for sx in (x0 + 12, x0 + 26, x0 + 40):
            d.ellipse([sx, y0 + 8, sx + 3, y0 + 11], fill=(255, 215, 80))
        d.rectangle([x0, y0 + 13, x1, y1], fill=dark)
    elif kind == "fence":
        for i in range(7):
            fx = x0 + 6 + i * 14
            d.line([(fx, y0 + 3), (fx, y1 - 3)], fill=(220, 220, 220), width=2)
        d.line([(x0, y0 + 6), (x1, y0 + 6)], fill=(220, 220, 220), width=1)
        d.line([(x0, y1 - 7), (x1, y1 - 7)], fill=(220, 220, 220), width=1)


# ------------------------------------------------------------- dotted map
LAND_BLOBS = [
    # (cx, cy, rx, ry) in map-box fractions
    (0.10, 0.34, 0.075, 0.20),   # Alaska / W Canada
    (0.17, 0.30, 0.085, 0.22),   # N America
    (0.235, 0.52, 0.045, 0.20),  # Mexico / C America
    (0.295, 0.16, 0.028, 0.10),  # Greenland
    (0.305, 0.72, 0.035, 0.20),  # S America (north)
    (0.545, 0.30, 0.038, 0.16),  # Europe
    (0.555, 0.62, 0.045, 0.24),  # Africa
    (0.66, 0.30, 0.075, 0.20),   # W/C Asia
    (0.775, 0.32, 0.085, 0.20),  # E Asia
    (0.72, 0.58, 0.028, 0.14),   # India
    (0.80, 0.58, 0.035, 0.14),   # SE Asia
    (0.885, 0.72, 0.035, 0.14),  # Australia (north edge)
]


def draw_dotted_map(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    step = 5
    for gy in range(y0 + 2, y1 - 1, step):
        for gx in range(x0 + 2, x1 - 1, step):
            fx = (gx - x0) / w
            fy = (gy - y0) / h
            for (cx, cy, rx, ry) in LAND_BLOBS:
                if ((fx - cx) / rx) ** 2 + ((fy - cy) / ry) ** 2 <= 1:
                    d.ellipse([gx - 1, gy - 1, gx + 2, gy + 2],
                              fill=(128, 116, 92))
                    break


def draw_pin(d, x, y, n):
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED,
              outline=(255, 255, 255), width=1)
    f = F(SANS_B, 8)
    tw = f.getlength(str(n))
    d.text((x - tw / 2, y - 5), str(n), font=f, fill=(255, 255, 255))


def chip(d, x, y, cert):
    """Certainty chip: coloured dot + label; returns width used."""
    label, col = CERT[cert]
    f = F(SANS_B, 8)
    d.ellipse([x, y, x + 7, y + 7], fill=col)
    d.text((x + 10, y - 1), label, font=f, fill=col)
    return 10 + f.getlength(label)


# ------------------------------------------------------------------ render
def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead eyebrow
    f_eye = F(SANS_B, 9)
    d.text((M, 8), "THE SUNDAY ASSEMBLY \u2014 THE WORLD IN ONE DAY",
           font=f_eye, fill=INK)
    right = "40 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - M - text_w(f_eye, right), 8), right, font=f_eye, fill=GREY)
    d.line([(M, 24), (W - M, 24)], fill=INK, width=1)

    # ---- title
    d.text((M, 28), "Sunday 22 November 2026", font=F(SERIF_B, 50), fill=INK)
    d.line([(M, 84), (W - M, 84)], fill=INK, width=2)

    # ---- kicker + NO DEAL badge
    f_kick = F(SANS_B, 13)
    kick = ("COP31 collapses with no deal  \u00b7  Russia fires 186 drones  "
            "\u00b7  Iran claims two US radars hit")
    d.text((M, 88), kick, font=f_kick, fill=RED)
    badge = "NO DEAL"
    f_badge = F(SANS_B, 13)
    bw = f_badge.getlength(badge) + 18
    d.rectangle([W - M - bw, 86, W - M, 105], fill=RED)
    d.text((W - M - bw + 9, 88), badge, font=f_badge, fill=(255, 255, 255))

    # ---- big-numbers band
    y = 108
    cell_w = CW / 6
    f_num = F(SERIF_B, 26)
    f_lab = F(SANS_B, 7)
    for i, (num, lab) in enumerate(BAND):
        cx = M + i * cell_w
        d.text((cx + 4, y), num, font=f_num, fill=INK)
        ly = y + 30
        for j, ln in enumerate(lab.split("\n")):
            d.text((cx + 4, ly + j * 9), ln, font=f_lab, fill=GREY)
        if i:
            d.line([(cx, y + 2), (cx, y + 46)], fill=LIGHT_LINE, width=1)
    d.line([(M, 158), (W - M, 158)], fill=INK, width=1)

    # ---- timeline
    d.text((M, 162), TIMELINE, font=F(SANS, 9), fill=INK)
    d.line([(M, 176), (W - M, 176)], fill=INK, width=1)

    # ---- MARKETS band
    my0, my1 = 180, 216
    d.rectangle([M, my0, W - M, my1], fill=NAVY)
    d.text((M + 8, my0 + 5), "MARKETS \u2014", font=F(SANS_B, 10),
           fill=(255, 255, 255))
    d.text((M + 8, my0 + 19), "SUNDAY 22 NOV", font=F(SANS_B, 8),
           fill=(180, 190, 210))
    cell_w = (CW - 120) / 6
    f_mv = F(SERIF_B, 17)
    f_ml = F(SANS, 8)
    for i, (name, sub, val, kind) in enumerate(MARKETS):
        cx = M + 120 + i * cell_w
        d.text((cx + 6, my0 + 4), name, font=F(SANS_B, 8), fill=(180, 190, 210))
        d.text((cx + 6, my0 + 15), sub, font=f_ml, fill=(180, 190, 210))
        d.text((cx + 6, my0 + 20), val,
               font=F(SERIF_B, 15) if kind else f_mv,
               fill=(255, 120, 110) if kind else (255, 255, 255))
        if i:
            d.line([(cx, my0 + 4), (cx, my1 - 4)], fill=(70, 88, 120), width=1)

    # ---- heroes
    hy0 = 222
    h_art = 96
    gap = 8
    hw = (CW - 2 * gap) / 3
    f_hkick = F(SANS_B, 10)
    f_hhead = F(SERIF_B, 20)
    f_hdeck = F(SERIF, 11)
    art_fns = {"plenary": draw_plenary, "kyiv": draw_kyiv, "manama": draw_manama}
    for i, h in enumerate(HEROES):
        x0 = M + i * (hw + gap)
        x1 = x0 + hw
        art_fns[h["art"]](d, (x0, hy0, x1, hy0 + h_art))
        d.rectangle([x0, hy0 + h_art, x1, hy0 + h_art + 17], fill=INK)
        d.text((x0 + 6, hy0 + h_art + 3),
               "%d  %s  \u00b7  %s" % (h["n"], h["place"], h["tag"]),
               font=f_hkick, fill=(255, 255, 255))
        label, col = CERT[h["cert"]]
        f_chip = F(SANS_B, 8)
        cw = 10 + f_chip.getlength(label)
        d.ellipse([x1 - cw - 4, hy0 + h_art + 5, x1 - cw + 3, hy0 + h_art + 12],
                  fill=col)
        d.text((x1 - cw + 6, hy0 + h_art + 4), label, font=f_chip, fill=col)
        draw_wrapped(d, x0 + 2, hy0 + h_art + 20, h["head"], f_hhead, hw - 4,
                     INK, leading=20, max_lines=2)
        draw_wrapped(d, x0 + 2, hy0 + h_art + 62, h["deck"], f_hdeck, hw - 4,
                     (60, 56, 48), leading=13, max_lines=2)
        d.rectangle([x0, hy0, x1, hy0 + h_art + 90], outline=INK, width=1)

    # ---- grid: 5 cols x 4 rows; last cell = HOW TO READ
    gy0 = 412
    gh = 79
    gw = (CW - 4 * 6) / 5
    f_gkick = F(SANS_B, 9)
    f_ghead = F(SERIF_B, 14)
    f_gdeck = F(SERIF, 8)
    for idx, g in enumerate(GRID):
        row, col = divmod(idx, 5)
        x0 = M + col * (gw + 6)
        y0 = gy0 + row * gh
        x1, y1 = x0 + gw, y0 + gh - 4
        mini_scene(d, (x0, y0, x1, y0 + 17), g["art"], g["pal"][0])
        d.text((x0 + 2, y0 + 19), "%d %s" % (g["n"], g["place"]),
               font=f_gkick, fill=RED)
        label, ccol = CERT[g["cert"]]
        f_c = F(SANS_B, 7)
        cw = 9 + f_c.getlength(label)
        d.ellipse([x1 - cw - 2, y0 + 20, x1 - cw + 4, y0 + 26], fill=ccol)
        d.text((x1 - cw + 7, y0 + 19), label, font=f_c, fill=ccol)
        draw_wrapped(d, x0 + 2, y0 + 31, g["head"], f_ghead, gw - 4,
                     INK, leading=13, max_lines=2)
        draw_wrapped(d, x0 + 2, y0 + 58, g["deck"], f_gdeck, gw - 4,
                     (70, 66, 58), leading=9, max_lines=2)
        d.rectangle([x0, y0, x1, y1], outline=LIGHT_LINE, width=1)
    # Liverpool FULL TIME score bug on card 22 (row 3, col 3)
    lx0 = M + 3 * (gw + 6)
    ly0 = gy0 + 3 * gh
    d.rectangle([lx0 + gw - 52, ly0 + 1, lx0 + gw - 2, ly0 + 13], fill=RED)
    d.text((lx0 + gw - 47, ly0 + 2), "4 \u2013 0", font=F(SANS_B, 9),
           fill=(255, 255, 255))
    d.text((lx0 + gw - 52, ly0 + 14), "FULL TIME", font=F(SANS_B, 6),
           fill=RED)
    # HOW TO READ box (row 3, col 4)
    hx0 = M + 4 * (gw + 6)
    hyy0 = gy0 + 3 * gh
    hx1, hyy1 = hx0 + gw, hyy0 + gh - 4
    d.rectangle([hx0, hyy0, hx1, hyy1], fill=(238, 232, 214),
                outline=INK, width=1)
    d.text((hx0 + 6, hyy0 + 4), "HOW TO READ", font=F(SANS_B, 10), fill=INK)
    legend = [
        (GREEN, "REPORTED \u2014 confirmed by 2+ sources"),
        (AMBER, "CLAIM \u2014 one side asserts, other denies"),
        (BLUE, "FORECAST \u2014 still to happen when drawn"),
        (RED, "FULL TIME \u2014 final score in"),
        (INK, "\u2020 in ALSO \u2014 dated Fri/Sat, see below"),
    ]
    f_leg = F(SANS, 8)
    for i, (col, txt) in enumerate(legend):
        yy = hyy0 + 20 + i * 11
        d.ellipse([hx0 + 6, yy + 1, hx0 + 12, yy + 7], fill=col)
        d.text((hx0 + 15, yy), txt, font=f_leg, fill=INK)

    # ---- map
    myy0 = 732
    d.text((M, myy0), "THE WORLD ON SUNDAY \u2014 22 STORIES PINNED",
           font=F(SANS_B, 10), fill=INK)
    counts = ("EUROPE 14  \u00b7  MIDDLE EAST 5  \u00b7  ASIA-PACIFIC 8  \u00b7  "
              "AMERICAS 4  \u00b7  AFRICA 4  \u00b7  OCEANIA 3  \u00b7  WORLD 2")
    d.text((W - M - text_w(F(SANS, 9), counts), myy0 + 1), counts,
           font=F(SANS, 9), fill=GREY)
    map_box = (M, myy0 + 16, 826, myy0 + 64)
    draw_dotted_map(d, map_box)
    # pins: (n, dot_fx, dot_fy, label_fx, label_fy) in map-box fractions
    pins = [
        (6, 0.150, 0.45, 0.150, 0.45),
        (10, 0.180, 0.65, 0.180, 0.65),
        (22, 0.505, 0.34, 0.470, 0.12),
        (19, 0.552, 0.26, 0.500, 0.12),
        (20, 0.560, 0.16, 0.530, 0.12),
        (8, 0.575, 0.10, 0.560, 0.12),
        (2, 0.595, 0.30, 0.590, 0.12),
        (9, 0.600, 0.38, 0.620, 0.12),
        (1, 0.608, 0.52, 0.650, 0.12),
        (18, 0.525, 0.46, 0.500, 0.88),
        (14, 0.538, 0.56, 0.530, 0.88),
        (13, 0.548, 0.78, 0.560, 0.88),
        (12, 0.612, 0.62, 0.595, 0.88),
        (3, 0.645, 0.66, 0.628, 0.88),
        (21, 0.740, 0.55, 0.740, 0.55),
        (4, 0.845, 0.50, 0.845, 0.50),
        (7, 0.868, 0.30, 0.868, 0.30),
        (15, 0.888, 0.22, 0.888, 0.22),
        (11, 0.815, 0.72, 0.815, 0.72),
        (16, 0.858, 0.74, 0.858, 0.74),
    ]
    mw, mh = map_box[2] - map_box[0], map_box[3] - map_box[1]
    for (n, dfx, dfy, lfx, lfy) in pins:
        dx = map_box[0] + int(dfx * mw)
        dy = map_box[1] + int(dfy * mh)
        lx = map_box[0] + int(lfx * mw)
        ly = map_box[1] + int(lfy * mh)
        if (dx, dy) != (lx, ly):
            d.line([(lx, ly), (dx, dy)], fill=(150, 140, 120), width=1)
            d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=RED)
        draw_pin(d, lx, ly, n)
    # Pacific inset
    ix0, iy0, ix1, iy1 = 836, myy0 + 16, W - M, myy0 + 64
    d.rectangle([ix0, iy0, ix1, iy1], fill=(226, 236, 242), outline=NAVY, width=1)
    d.text((ix0 + 6, iy0 + 4), "PACIFIC \u2014 INSET", font=F(SANS_B, 9), fill=NAVY)
    d.text((ix0 + 6, iy0 + 20), "WELLINGTON 5  \u00b7  CANBERRA 17",
           font=F(SANS_B, 9), fill=INK)
    draw_pin(d, ix1 - 16, iy0 + 38, 5)
    draw_pin(d, ix0 + 26, iy0 + 38, 17)
    d.text((ix0 + 6, iy1 - 11), "FORECAST = still to happen when drawn",
           font=F(SERIF_I, 8), fill=GREY)

    # ---- ALSO
    ay0 = 800
    d.text((M, ay0), "ALSO ON SUNDAY 22 NOVEMBER \u2014 18 MORE STORIES",
           font=F(SANS_B, 10), fill=INK)
    d.line([(M, ay0 + 13), (W - M, ay0 + 13)], fill=INK, width=1)
    f_a = F(SERIF, 9)
    f_ab = F(SANS_B, 8)
    f_an = F(SANS_B, 9)
    col_w = CW / 2
    for i, (n, region, txt, cert, city) in enumerate(ALSO):
        col, row = divmod(i, 9)
        x0 = M + col * col_w
        y = ay0 + 17 + row * 12
        d.text((x0, y), str(n), font=f_an, fill=RED)
        rx = x0 + 18
        rw = f_ab.getlength(region)
        d.text((rx, y), region, font=f_ab, fill=GREY)
        tx = rx + rw + 5
        cw = f_ab.getlength(city)
        max_tw = (x0 + col_w - 8 - cw - 6) - tx
        lines = wrap(txt, f_a, max_tw, max_lines=1)
        shown = lines[0] if lines else txt
        d.text((tx, y), shown, font=f_a, fill=INK)
        if cert:
            label, ccol = CERT[cert]
            d.text((tx + text_w(f_a, shown) + 4, y),
                   "\u25cb " + label, font=F(SANS_B, 7), fill=ccol)
        d.text((x0 + col_w - 8 - cw, y), city, font=f_ab, fill=GREY)

    # ---- DATE CHECK
    dy0 = 928
    d.text((M, dy0), "DATE CHECK \u2014 NOT SUNDAY, however listed elsewhere:",
           font=F(SANS_B, 10), fill=RED)
    d.line([(M, dy0 + 13), (W - M, dy0 + 13)], fill=RED, width=1)
    f_dc = F(SERIF, 8)
    dc_w = CW / 3
    for ci, col_items in enumerate(DATE_CHECK):
        x0 = M + ci * dc_w
        for ri, item in enumerate(col_items):
            y = dy0 + 17 + ri * 9
            d.text((x0, y), "\u00d7", font=F(SANS_B, 8), fill=RED)
            d.text((x0 + 10, y), item, font=f_dc, fill=INK)

    # ---- footer
    d.line([(M, 1002), (W - M, 1002)], fill=INK, width=1)
    d.text((M, 1006),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 BBC \u00b7 The Times \u00b7 "
           "Formula 1 \u00b7 Cricinfo \u00b7 PHIVOLCS \u00b7 Vatican News \u00b7 QNA \u00b7 Saudi "
           "Exchange \u00b7 QSE \u00b7 EGX \u2014 all stories verified vs Sunday 22 Nov 2026; "
           "dated items flagged; claims attributed.",
           font=F(SANS, 7), fill=GREY)

    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    render(out)
    print("wrote", out)
