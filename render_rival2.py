#!/usr/bin/env python3
"""Render rival2 poster for make.fun news-image-20261122.

Front-page newspaper for Sunday 22 November 2026. 37 stories, 18
illustrated cards, accurate dotted world map with numbered pins, and a
DATE CHECK box catching wrong-day items that rival entries list as Sunday.

Authored from scratch in this session. PIL only, fully deterministic
(no randomness, no time, no network). Output: poster.png 1024x1024.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 24
CW = W - 2 * MX

PAPER = (248, 244, 234)
INK = (26, 26, 26)
INK2 = (70, 66, 58)
RED = (178, 34, 24)
RED_DK = (140, 22, 16)
BLUE = (30, 64, 120)
GREY = (120, 114, 102)
RULE = (190, 182, 168)
CARD_BG = (255, 252, 244)
TAG_BG = (26, 26, 26)
SKY = (214, 228, 238)
NIGHT = (18, 30, 54)

FD = "/usr/share/fonts/truetype"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF = f"{FD}/dejavu/DejaVuSerif.ttf"
SERIF_B = f"{FD}/dejavu/DejaVuSerif-Bold.ttf"
SANS = f"{FD}/dejavu/DejaVuSans.ttf"
SANS_B = f"{FD}/dejavu/DejaVuSans-Bold.ttf"
DISPLAY = f"{FD}/noto/NotoSerifDisplay-Black.ttf"
if not os.path.exists(DISPLAY):
    DISPLAY = SERIF_B
COND_B = f"{FD}/noto/NotoSans-CondensedBold.ttf"
if not os.path.exists(COND_B):
    COND_B = SANS_B


def wrap(d, text, fnt, width):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_center(d, cx, y, text, fnt, fill=INK):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def hline(d, x0, x1, y, fill=RULE, wdt=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=wdt)


def tag_chip(d, x, y, label, fill=TAG_BG, fg=(255, 255, 255), fnt=None):
    fnt = fnt or font(SANS_B, 8)
    tw = d.textlength(label, font=fnt)
    d.rounded_rectangle([x, y, x + tw + 10, y + 13], radius=2, fill=fill)
    d.text((x + 5, y + 2), label, font=fnt, fill=fg)
    return tw + 10


# ---------------------------------------------------------------- data
NUMBERS = [
    ("44h", "COP31 OVERTIME TO COLLAPSE"),
    ("186", "DRONES FIRED AT UKRAINE"),
    ("161", "DOWNED OR JAMMED"),
    ("720/9", "INDIA'S RECORD TEST TOTAL"),
    ("$61,568", "BITCOIN'S SUNDAY HIGH"),
    ("98.79%", "HONG KONG TURNOUT, RECORD"),
]

TIMELINE = ("THE DAY IN UTC  \u2014  01:00 HK polls open  \u00b7  03:00 COP31 objections close  \u00b7  "
            "05:30 Verstappen wins Vegas  \u00b7  06:00 COP31 approval due  \u00b7  "
            "12:15 Bitcoin tops $61,568  \u00b7  14:15 HK count done")

REGIONS = "7 REGIONS  —  EUROPE 9  ·  MIDDLE EAST 6  ·  ASIA-PACIFIC 6  ·  AMERICAS 5  ·  AFRICA 3  ·  OCEANIA 4  ·  WORLD 4"

HEROES = [
    dict(n=1, tag="CLIMATE · ANTALYA", scene="cop31",
         head="COP31 collapses with no deal",
         body=("The final text landed at dawn, but the EU, UK and Panama rejected it for "
               "omitting fossil fuels. Murat Kurum conceded it was \u201cnot adopted\u201d. "
               "44 hours overtime \u2014 the longest COP ever, and the first no-deal since COP6 in 2000. "
               "The draft kept a 35% clean-electricity goal, dropped the $120bn-a-year "
               "adaptation target, and admitted 1.5\u00b0C will be overshot. "
               "UN chief Ant\u00f3nio Guterres: \u201cdeeply disappointed\u201d.")),
    dict(n=2, tag="WAR · UKRAINE", scene="drones",
         head="Russia fires 186 drones; Dymer block destroyed, 14 missing",
         body=("Russia launched 186 drones overnight \u2014 161 downed or jammed \u2014 with hits at "
               "18 locations. In Dymer, Kyiv region, a five-storey block was destroyed; 14 people "
               "are unaccounted for and 2\u20133 are dead, Zelenskyy said. Russia said it downed 170 "
               "Ukrainian drones in return. Zelenskyy: 2,700 drones, 1,460 bombs and 165 missiles "
               "were fired at Ukraine this week; he renewed calls for interceptor missiles.")),
    dict(n=3, tag="CLAIM · GULF", scene="radar",
         head="Iran claims two US radars hit; Bahrain denies it",
         body=("IRGC media claimed Saturday-night missile and drone strikes hit two US Patriot "
               "radars at al-Riffa and Awali. Bahrain says its defences intercepted the attack; a "
               "civilian industrial plant burned and two people were hurt. A US official said no US "
               "forces were damaged; CENTCOM categorically denied Iran\u2019s separate claim of "
               "downing an F-16. CLAIM \u2014 unverified by independent sources.")),
]

# small cards: n, region, scene, headline, body
SMALL = [
    dict(n=4, tag="HONG KONG", scene="ballot",
         head="Hong Kong turnout hits record 98.79%",
         body="5,640 of 5,709 voters cast ballots; count done 22:15. 2021: 89.77%."),
    dict(n=5, tag="WELLINGTON", scene="cricket",
         head="India declare 720/9 \u2014 a record in NZ",
         body="Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233 on day four."),
    dict(n=6, tag="LAS VEGAS", scene="f1",
         head="Verstappen wins Vegas by 0.639s",
         body="75th career win; Norris 2nd, Piastri 3rd from 17th. 35 lead changes."),
    dict(n=7, tag="SEOUL", scene="minister",
         head="Seoul minister quits over exam scandal",
         body="Choi Kyo-jin resigned; Lee accepted in an hour. 111 AI-cheat cases."),
    dict(n=8, tag="FINLAND", scene="tanker",
         head="Sparta II still burning off Finland",
         body="Struck Saturday; fire smouldered Sunday. 16 crew out, 1 slightly hurt."),
    dict(n=9, tag="BRAS\u00cdLIA", scene="hospital",
         head="Bolsonaro in ICU after bowel obstruction",
         body="Admitted Friday, in ICU Saturday; stable, 71. Serving 27-year sentence."),
    dict(n=10, tag="SAN ANTONIO", scene="hoop",
         head="Wembanyama drops 50 as Spurs rout Pelicans",
         body="50 pts, 19 reb, 5 blk, 4 stl \u2014 a first. Spurs 114\u201391, Saturday US."),
    dict(n=11, tag="CIKANDE", scene="factory",
         head="Candy-factory fire: 3 dead, 36 missing",
         body="Blaze broke out Saturday 17:00; search went on Sunday. ~300 inside."),
    dict(n=12, tag="GAZA", scene="aid",
         head="Gaza: blocked supplies threaten surgeries",
         body="Health ministry: blocked medical stocks put operations at risk."),
    dict(n=13, tag="BAYELSA", scene="boat",
         head="Nigeria boat toll reaches 24",
         body="Capsized Friday, Ayama\u2013Ukubie; 24 dead, 24 rescued. Manager held."),
    dict(n=14, tag="VATICAN", scene="pope",
         head="Pope Leo XIV hosts 1,300 for lunch",
         body="10th World Day of the Poor: lunch in Paul VI Hall, a week late."),
    dict(n=15, tag="FUKUSHIMA", scene="snow",
         head="1,500 still cut off by Japan snow",
         body="Travellers stranded in Kitashiobara since Saturday; train derailed."),
    dict(n=16, tag="MINDANAO", scene="quake",
         head="M5.6 quake off Mindanao; no damage",
         body="Off Sarangani, 15:54 local, depth 10 km. No damage expected."),
    dict(n=17, tag="CANBERRA", scene="sub",
         head="Marles: US report \u2018wrong\u2019 on AUKUS",
         body="Defence minister rejects CBO warning on subs cost, Reuters reports."),
    dict(n=18, tag="TURIN · FORECAST", scene="tennis",
         head="Zverev v Alcaraz in Turin final \u2014 today",
         body="The ATP Finals title match closes the season in Turin."),
]

ALSO = [
    ("ASIA", "Nepal PM Shah lands in Delhi \u2014 first foreign trip; talks with Modi on Monday"),
    ("EUROPE", "Estonia seals Russia border from 1 Dec; Moscow vows a response"),
    ("AFRICA", "Sudan: RSF accused of killing civilians incl. 3 children in W. Kordofan"),
    ("AFRICA", "S. Africa mourns Mlambo-Ngcuka, 71 \u2014 prayer service held Sunday"),
    ("OCEANIA", "Melbourne: 70 years since the 1956 Olympics opened"),
    ("AMERICAS", "Crew stun Messi\u2019s 10-man Inter Miami 3\u20130"),
    ("MID EAST", "Iran begins rolling power cuts \u2014 up to 2h a day"),
    ("MID EAST", "US denies Iran claim it downed an F-16 \u2014 CENTCOM"),
    ("MID EAST", "Iraq PM to visit Cairo on Monday \u2014 oil, arms talks"),
    ("WORLD", "Gold $3,539 \u2014 14-month low after Friday\u2019s rout"),
    ("WORLD", "Bitcoin back above $60,000 after Saturday\u2019s $55,106 low"),
    ("AMERICAS", "San Francisco braces for record king tides"),
    ("EUROPE", "Russia says it downed 170 Ukrainian drones overnight"),
    ("EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week"),
    ("WORLD", "October 2026: warmest month on record, 1.8\u00b0C above pre-industrial"),
    ("MID EAST", "Hamas seeks urgent talks after Gaza aid-van strike"),
    ("EUROPE", "Liverpool host Man City, 16:30 GMT \u2014 later today"),
    ("OCEANIA", "Pope prays for war victims, drought-hit Papua New Guinea"),
    ("EUROPE", "Russian helicopter suspected of breaching Finnish airspace"),
]

DATECHECK = [
    "Peru quake \u2014 Fri 20 Nov",
    "BepiColombo at Mercury \u2014 Sat 21 Nov",
    "ICJ Myanmar ruling \u2014 Thu 19 Nov",
    "Kenya last Ebola case out \u2014 11 Nov",
    "Denmark expels attach\u00e9 \u2014 Fri 20 Nov",
    "Senate $350bn bill stalls \u2014 18\u201319 Nov",
    "Qatar talks in Tehran \u2014 Fri night",
    "Trump\u2013Xi\u2013Putin talks \u2014 Thu 19 Nov",
    "EU\u2013Indonesia deal signed \u2014 Sat 21 Nov",
    "UK\u2013EU food deal signed \u2014 Fri 20 Nov",
    "El Chapo Isidro seized \u2014 Fri 20 Nov",
    "Nvidia SEC probe \u2014 Fri 20 Nov",
    "China H-6 bomber turns \u2014 Sat 21 Nov",
    "Sparta II struck \u2014 Sat 21 Nov",
    "Bayelsa boat capsizes \u2014 Fri 20 Nov",
    "Gaza aid-van strike \u2014 Sat 21 Nov",
]

# (lon, lat) pins for the 18 illustrated stories
PINS = {
    1: (30.7, 36.9), 2: (30.5, 50.8), 3: (50.6, 26.2), 4: (114.2, 22.3),
    5: (174.8, -41.3), 6: (-115.1, 36.2), 7: (127.0, 37.6), 8: (26.2, 60.4),
    9: (-47.9, -15.8), 10: (-98.5, 29.4), 11: (106.3, -6.2), 12: (34.5, 31.5),
    13: (6.3, 4.9), 14: (12.45, 41.9), 15: (140.5, 37.7), 16: (125.5, 5.5),
    17: (149.1, -35.3), 18: (7.7, 45.1),
}
# nudge (dx, dy) px for pins that would overlap on the small map
NUDGE = {1: (-6, -5), 2: (6, 4), 8: (-8, -7), 12: (8, 7), 14: (8, 5), 18: (-8, -5)}

# landmask: row -> list of (col0, col1) inclusive; 72 cols x 30 rows,
# equirectangular, lon -180..180, lat 90..-90
LAND = {
    1: [(19, 21), (24, 32)],
    2: [(12, 24), (25, 31), (38, 41), (50, 71)],
    3: [(2, 24), (25, 30), (37, 71)],
    4: [(2, 25), (31, 32), (37, 71)],
    5: [(3, 25), (35, 36), (37, 71)],
    6: [(10, 25), (35, 65)],
    7: [(11, 23), (35, 64)],
    8: [(11, 22), (34, 48), (51, 64)],
    9: [(12, 21), (34, 60), (62, 64)],
    10: [(13, 19), (34, 47), (50, 60)],
    11: [(15, 18), (32, 47), (50, 53), (55, 57), (60, 60)],
    12: [(17, 19), (32, 38), (44, 47), (50, 52), (55, 57), (60, 60)],
    13: [(19, 20), (33, 38), (51, 51), (55, 60)],
    14: [(20, 26), (34, 39), (56, 60), (62, 65)],
    15: [(20, 28), (34, 40), (57, 61), (63, 65)],
    16: [(21, 29), (35, 41), (58, 62)],
    17: [(21, 28), (38, 42), (58, 62)],
    18: [(22, 28), (38, 42), (44, 46), (58, 65)],
    19: [(22, 27), (38, 42), (58, 66)],
    20: [(22, 26), (39, 41), (59, 66), (69, 71)],
    21: [(21, 25), (64, 66), (69, 71)],
    22: [(21, 24), (69, 70)],
    23: [(21, 23)],
    24: [(22, 22)],
}

# ---------------------------------------------------------------- scenes
def scene_cop31(d, x0, y0, w, h):
    """Antalya summit hall: empty chairs, long table, cracked globe."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY)
    d.rectangle([x0, y0, x0 + w, y0 + int(h * 0.42)], fill=(196, 214, 228))
    d.ellipse([x0 + w - 52, y0 + 8, x0 + w - 16, y0 + 44], fill=(240, 214, 130))
    # hall
    d.rectangle([x0 + 18, y0 + int(h * 0.30), x0 + w - 18, y0 + h - 26], fill=(58, 68, 84))
    d.rectangle([x0 + 26, y0 + int(h * 0.34), x0 + w - 26, y0 + int(h * 0.52)],
                fill=(120, 140, 165))
    for i in range(5):
        wx = x0 + 34 + i * 52
        d.rectangle([wx, y0 + int(h * 0.36), wx + 34, y0 + int(h * 0.50)],
                    fill=(220, 230, 240))
    # long table + empty chairs
    d.rectangle([x0 + 30, y0 + h - 44, x0 + w - 30, y0 + h - 34], fill=(38, 44, 58))
    for i in range(6):
        cx = x0 + 44 + i * 44
        d.rectangle([cx, y0 + h - 30, cx + 26, y0 + h - 26], fill=(90, 96, 110))
        d.rectangle([cx + 3, y0 + h - 26, cx + 23, y0 + h - 12], fill=(70, 76, 92))
    # cracked globe above the hall
    gx, gy, gr = x0 + w // 2, y0 + int(h * 0.30), 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(46, 110, 170))
    d.ellipse([gx - 18, gy - 22, gx - 2, gy - 6], fill=(84, 160, 90))
    d.ellipse([gx + 4, gy + 6, gx + 20, gy + 22], fill=(84, 160, 90))
    d.ellipse([gx + 8, gy - 20, gx + 20, gy - 8], fill=(84, 160, 90))
    d.line([(gx - 4, gy - 28), (gx + 2, gy - 12), (gx - 6, gy + 2), (gx + 4, gy + 16),
            (gx - 2, gy + 28)], fill=RED, width=3)
    d.rectangle([x0, y0 + h - 15, x0 + w, y0 + h], fill=(20, 20, 24))
    d.text((x0 + 8, y0 + h - 13), "ANTALYA \u2014 44 HOURS OVERTIME",
           font=font(SANS_B, 9), fill=(255, 255, 255))


def scene_drones(d, x0, y0, w, h):
    """Night sky over Kyiv: drones, interceptor arcs, burning block."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=NIGHT)
    for (sx, sy) in [(30, 12), (90, 24), (150, 10), (210, 30), (260, 14), (120, 40), (190, 8)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(220, 225, 240))
    # interceptor arcs
    for (ax, ay, bx, by) in [(40, 96, 150, 30), (90, 100, 210, 26), (160, 98, 270, 34)]:
        d.arc([x0 + ax, y0 + ay - 60, x0 + bx, y0 + by + 40], 180, 360,
              fill=(200, 210, 230), width=1)
    # drones: small quadcopters with lights
    for (dx, dy) in [(70, 34), (150, 22), (235, 40)]:
        d.line([(x0 + dx - 9, y0 + dy), (x0 + dx + 9, y0 + dy)], fill=(200, 205, 220), width=2)
        d.line([(x0 + dx, y0 + dy - 6), (x0 + dx, y0 + dy + 6)], fill=(200, 205, 220), width=2)
        d.ellipse([x0 + dx - 3, y0 + dy - 3, x0 + dx + 3, y0 + dy + 3], fill=RED)
    # burning block, bottom left
    d.rectangle([x0 + 14, y0 + h - 52, x0 + 86, y0 + h - 8], fill=(20, 20, 26))
    for wy in range(3):
        for wx in range(3):
            d.rectangle([x0 + 22 + wx * 22, y0 + h - 46 + wy * 14,
                         x0 + 32 + wx * 22, y0 + h - 36 + wy * 14], fill=(240, 200, 90))
    # flames licking from the roofline
    for (fx, fy, fr) in [(34, 54, 10), (50, 58, 13), (66, 54, 9)]:
        d.ellipse([x0 + fx - fr, y0 + h - fy - fr, x0 + fx + fr, y0 + h - fy + fr],
                  fill=(230, 120, 30))
    d.ellipse([x0 + 44, y0 + h - 62, x0 + 56, y0 + h - 50], fill=(250, 200, 60))
    # smoke rising from the roof, drifting right
    for (sx, sy, sr) in [(58, 78, 8), (70, 88, 11), (84, 96, 9)]:
        d.ellipse([x0 + sx - sr, y0 + h - sy - sr, x0 + sx + sr, y0 + h - sy + sr],
                  fill=(120, 124, 134))
    # skyline right
    d.rectangle([x0 + w - 110, y0 + h - 34, x0 + w - 20, y0 + h - 8], fill=(14, 20, 38))
    d.rectangle([x0 + w - 92, y0 + h - 46, x0 + w - 60, y0 + h - 8], fill=(14, 20, 38))
    d.rectangle([x0, y0 + h - 15, x0 + w, y0 + h], fill=(20, 20, 24))
    d.text((x0 + 8, y0 + h - 13), "KYIV REGION \u2014 186 DRONES",
           font=font(SANS_B, 9), fill=(255, 255, 255))


def scene_radar(d, x0, y0, w, h):
    """Gulf coast at dusk: two radar domes, one hit, missile arc."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 214, 178))
    d.rectangle([x0, y0, x0 + w, y0 + int(h * 0.45)], fill=(248, 226, 190))
    d.ellipse([x0 + 18, y0 + 10, x0 + 54, y0 + 46], fill=(244, 196, 120))
    # sea
    d.rectangle([x0, y0 + int(h * 0.62), x0 + w, y0 + h], fill=(64, 120, 140))
    for wy in range(3):
        yy = y0 + int(h * 0.66) + wy * 12
        d.line([(x0 + 10, yy), (x0 + w - 10, yy)], fill=(120, 170, 185), width=2)
    # land
    d.polygon([(x0, y0 + int(h * 0.62)), (x0 + w, y0 + int(h * 0.62)),
               (x0 + w, y0 + int(h * 0.45)), (x0 + int(w * 0.55), y0 + int(h * 0.52)),
               (x0 + int(w * 0.30), y0 + int(h * 0.46))], fill=(196, 172, 128))
    # missile arc (dashed)
    for i in range(9):
        t = i / 8
        px = x0 + 20 + t * 190
        py = y0 + 78 - (t * (1 - t)) * 130
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(90, 60, 50))
    # two radar domes
    for (rx, hit) in [(120, True), (225, False)]:
        d.rectangle([x0 + rx - 16, y0 + 66, x0 + rx + 16, y0 + 78], fill=(120, 116, 108))
        d.ellipse([x0 + rx - 20, y0 + 40, x0 + rx + 20, y0 + 76], fill=(240, 238, 230))
        d.line([(x0 + rx, y0 + 40), (x0 + rx + 12, y0 + 28)], fill=(90, 88, 80), width=2)
        if hit:
            d.ellipse([x0 + rx - 10, y0 + 30, x0 + rx + 10, y0 + 50], fill=(230, 90, 30))
            d.ellipse([x0 + rx - 4, y0 + 36, x0 + rx + 4, y0 + 44], fill=(250, 200, 60))
            for (sx, sy, sr) in [(rx + 4, 18, 7), (rx + 12, 10, 9)]:
                d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                          fill=(140, 136, 128))
    d.rectangle([x0, y0 + h - 15, x0 + w, y0 + h], fill=(20, 20, 24))
    d.text((x0 + 8, y0 + h - 13), "MANAMA \u2014 CLAIM: IRGC SAYS TWO RADARS HIT",
           font=font(SANS_B, 9), fill=(255, 255, 255))


def draw_mini(d, kind, x0, y0, w, h):
    """Small flat illustration for a card, 188x44 area."""
    bg = (238, 232, 216)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=bg)
    cx, cy = x0 + w // 2, y0 + h // 2
    if kind == "ballot":
        d.rectangle([x0 + w - 78, y0 + 12, x0 + w - 30, y0 + h - 8], fill=(178, 34, 24))
        d.rectangle([x0 + w - 72, y0 + 6, x0 + w - 36, y0 + 14], fill=(120, 20, 14))
        d.rectangle([x0 + w - 66, y0 - 2, x0 + w - 42, y0 + 8], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.text((x0 + 8, y0 + 12), "98.79%", font=font(SERIF_B, 20), fill=INK)
    elif kind == "cricket":
        # diagonal bat, ball, big total
        d.polygon([(x0 + 16, y0 + 40), (x0 + 26, y0 + 42), (x0 + 44, y0 + 10),
                   (x0 + 36, y0 + 6)], fill=(196, 164, 110))
        d.polygon([(x0 + 38, y0 + 8), (x0 + 44, y0 + 10), (x0 + 50, y0 + 2),
                   (x0 + 44, y0 + 0)], fill=(120, 90, 60))
        d.ellipse([x0 + 62, y0 + 12, x0 + 86, y0 + 36], fill=RED)
        d.text((x0 + 96, y0 + 10), "720/9", font=font(SERIF_B, 18), fill=INK)
    elif kind == "f1":
        d.rectangle([x0 + 8, y0 + 18, x0 + w - 40, y0 + 30], fill=(178, 34, 24))
        d.polygon([(x0 + w - 40, y0 + 18), (x0 + w - 22, y0 + 18), (x0 + w - 14, y0 + 30),
                   (x0 + w - 40, y0 + 30)], fill=(30, 30, 30))
        for wx in (26, 66):
            d.ellipse([x0 + wx, y0 + 28, x0 + wx + 14, y0 + 42], fill=INK)
        for i in range(4):
            d.rectangle([x0 + w - 34 + (i % 2) * 8, y0 + 4 + (i // 2) * 7,
                         x0 + w - 26 + (i % 2) * 8, y0 + 11 + (i // 2) * 7],
                        fill=INK if i % 2 == 0 else (255, 255, 255))
        d.text((x0 + 100, y0 + 4), "0.639s", font=font(SERIF_B, 13), fill=INK)
    elif kind == "minister":
        d.rectangle([x0 + 16, y0 + 10, x0 + 86, y0 + h - 6], fill=(120, 128, 140))
        d.polygon([(x0 + 10, y0 + 12), (x0 + 51, y0 + 2), (x0 + 92, y0 + 12)],
                  fill=(90, 98, 112))
        for i in range(3):
            d.rectangle([x0 + 26 + i * 20, y0 + 18, x0 + 32 + i * 20, y0 + h - 10],
                        fill=(240, 240, 235))
        d.rectangle([x0 + w - 70, y0 + 6, x0 + w - 14, y0 + h - 8], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.line([(x0 + w - 62, y0 + 14), (x0 + w - 22, y0 + 14)], fill=RED, width=2)
        d.line([(x0 + w - 62, y0 + 20), (x0 + w - 22, y0 + 20)], fill=INK, width=1)
        d.line([(x0 + w - 62, y0 + 26), (x0 + w - 34, y0 + 26)], fill=INK, width=1)
    elif kind == "tanker":
        d.rectangle([x0 + 14, y0 + 20, x0 + w - 60, y0 + 34], fill=(40, 50, 66))
        for i in range(3):
            d.rectangle([x0 + 20 + i * 26, y0 + 8, x0 + 40 + i * 26, y0 + 20],
                        fill=(178, 34, 24) if i != 1 else (30, 64, 120))
        d.ellipse([x0 + w - 52, y0 + 2, x0 + w - 36, y0 + 18], fill=(120, 124, 134))
        d.ellipse([x0 + w - 44, y0 - 6, x0 + w - 26, y0 + 12], fill=(140, 144, 154))
        d.ellipse([x0 + w - 34, y0 + 14, x0 + w - 20, y0 + 28], fill=(230, 120, 30))
        d.line([(x0 + 8, y0 + h - 6), (x0 + w - 8, y0 + h - 6)], fill=(64, 120, 140), width=2)
    elif kind == "hospital":
        d.rectangle([x0 + 12, y0 + 22, x0 + 96, y0 + 32], fill=(200, 200, 195))
        d.rectangle([x0 + 12, y0 + 32, x0 + 18, y0 + h - 6], fill=INK2)
        d.rectangle([x0 + 90, y0 + 32, x0 + 96, y0 + h - 6], fill=INK2)
        d.ellipse([x0 + 22, y0 + 12, x0 + 38, y0 + 24], fill=(232, 200, 170))
        d.rectangle([x0 + 38, y0 + 18, x0 + 84, y0 + 26], fill=(232, 200, 170))
        d.rectangle([x0 + w - 44, y0 + 6, x0 + w - 12, y0 + 38], fill=(255, 255, 255),
                    outline=RED, width=1)
        d.rectangle([x0 + w - 34, y0 + 12, x0 + w - 22, y0 + 32], fill=RED)
        d.rectangle([x0 + w - 40, y0 + 18, x0 + w - 16, y0 + 26], fill=RED)
    elif kind == "hoop":
        d.rectangle([x0 + w - 34, y0 + 6, x0 + w - 28, y0 + h - 6], fill=INK2)
        d.rectangle([x0 + w - 52, y0 + 6, x0 + w - 28, y0 + 14], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.ellipse([x0 + w - 46, y0 + 16, x0 + w - 32, y0 + 30], fill=RED)
        d.ellipse([x0 + 16, y0 + 6, x0 + 52, y0 + 42], fill=(230, 120, 30))
        d.arc([x0 + 16, y0 + 6, x0 + 52, y0 + 42], 300, 60, fill=INK, width=2)
        d.text((x0 + 62, y0 + 12), "50", font=font(SERIF_B, 22), fill=INK)
    elif kind == "factory":
        d.polygon([(x0 + 12, y0 + h - 8), (x0 + 12, y0 + 18), (x0 + 34, y0 + 8),
                   (x0 + 56, y0 + 18), (x0 + 78, y0 + 8), (x0 + 100, y0 + 18),
                   (x0 + 100, y0 + h - 8)], fill=(90, 96, 110))
        d.rectangle([x0 + w - 40, y0 + 4, x0 + w - 30, y0 + h - 8], fill=(120, 116, 108))
        for (fx, fy, fr) in [(w - 58, 16, 8), (w - 46, 10, 10), (w - 34, 18, 7)]:
            d.ellipse([x0 + fx - fr, y0 + fy - fr, x0 + fx + fr, y0 + fy + fr],
                      fill=(230, 120, 30))
        d.text((x0 + 108, y0 + 12), "3 / 36", font=font(SERIF_B, 15), fill=INK)
    elif kind == "aid":
        d.rectangle([x0 + 12, y0 + 16, x0 + 70, y0 + 32], fill=(240, 238, 230),
                    outline=INK, width=1)
        d.rectangle([x0 + 70, y0 + 20, x0 + 92, y0 + 32], fill=(178, 34, 24))
        for wx in (24, 76):
            d.ellipse([x0 + wx, y0 + 30, x0 + wx + 12, y0 + 42], fill=INK)
        d.rectangle([x0 + w - 44, y0 + 6, x0 + w - 12, y0 + 38], fill=(255, 255, 255),
                    outline=BLUE, width=1)
        d.rectangle([x0 + w - 34, y0 + 12, x0 + w - 22, y0 + 32], fill=BLUE)
        d.rectangle([x0 + w - 40, y0 + 18, x0 + w - 16, y0 + 26], fill=BLUE)
    elif kind == "boat":
        d.polygon([(x0 + 14, y0 + 22), (x0 + w - 60, y0 + 22), (x0 + w - 72, y0 + 34),
                   (x0 + 26, y0 + 34)], fill=(120, 80, 40))
        d.rectangle([x0 + 40, y0 + 10, x0 + 70, y0 + 22], fill=(160, 120, 70))
        for wy in (38, 42):
            d.line([(x0 + 8, y0 + wy), (x0 + w - 8, y0 + wy)], fill=(64, 120, 140), width=2)
        d.ellipse([x0 + w - 48, y0 + 8, x0 + w - 16, y0 + 40], fill=(255, 255, 255),
                  outline=RED, width=3)
        d.text((x0 + w - 108, y0 + 12), "24", font=font(SERIF_B, 18), fill=INK)
    elif kind == "pope":
        d.ellipse([x0 + 20, y0 + 4, x0 + 64, y0 + 30], fill=(178, 34, 24))
        d.rectangle([x0 + 16, y0 + 28, x0 + 68, y0 + h - 8], fill=(200, 190, 170))
        d.rectangle([x0 + 96, y0 + 26, x0 + w - 14, y0 + 32], fill=(120, 90, 60))
        for i in range(3):
            d.ellipse([x0 + 102 + i * 26, y0 + 16, x0 + 112 + i * 26, y0 + 26],
                      fill=(232, 200, 170))
        d.text((x0 + 96, y0 + 34), "1,300", font=font(SERIF_B, 12), fill=INK)
    elif kind == "snow":
        d.polygon([(x0 + 8, y0 + h - 6), (x0 + 46, y0 + 4), (x0 + 84, y0 + h - 6)],
                  fill=(240, 244, 248), outline=(180, 190, 200), width=1)
        d.polygon([(x0 + 60, y0 + h - 6), (x0 + 96, y0 + 12), (x0 + 130, y0 + h - 6)],
                  fill=(225, 232, 240))
        for (sx, sy) in [(20, 8), (50, 16), (90, 6), (130, 14), (160, 8)]:
            d.ellipse([x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3], fill=(255, 255, 255))
        d.rectangle([x0 + w - 62, y0 + 24, x0 + w - 10, y0 + 36], fill=(30, 64, 120))
        d.text((x0 + w - 108, y0 + 8), "1,500", font=font(SERIF_B, 15), fill=INK)
    elif kind == "quake":
        d.line([(x0 + 10, y0 + 22), (x0 + 40, y0 + 22), (x0 + 52, y0 + 8),
                (x0 + 64, y0 + 36), (x0 + 76, y0 + 14), (x0 + 88, y0 + 22),
                (x0 + w - 10, y0 + 22)], fill=RED, width=2)
        d.text((x0 + w - 78, y0 + 4), "M5.6", font=font(SERIF_B, 15), fill=INK)
        d.line([(x0 + 10, y0 + h - 8), (x0 + w - 10, y0 + h - 8)], fill=GREY, width=1)
    elif kind == "sub":
        d.ellipse([x0 + 14, y0 + 14, x0 + w - 50, y0 + 34], fill=(40, 50, 66))
        d.rectangle([x0 + 60, y0 + 6, x0 + 86, y0 + 16], fill=(40, 50, 66))
        d.polygon([(x0 + w - 50, y0 + 14), (x0 + w - 30, y0 + 24), (x0 + w - 50, y0 + 34)],
                  fill=(40, 50, 66))
        for wy in (38, 42):
            d.line([(x0 + 8, y0 + wy), (x0 + w - 8, y0 + wy)], fill=(64, 120, 140), width=2)
        d.text((x0 + w - 104, y0 + 4), "AUKUS", font=font(SERIF_B, 13), fill=INK)
    elif kind == "tennis":
        d.ellipse([x0 + 14, y0 + 6, x0 + 50, y0 + 42], fill=(200, 220, 60))
        d.arc([x0 + 14, y0 + 6, x0 + 50, y0 + 42], 250, 110, fill=(255, 255, 255), width=3)
        d.arc([x0 + 14, y0 + 6, x0 + 50, y0 + 42], 70, 290, fill=(255, 255, 255), width=3)
        d.polygon([(x0 + w - 52, y0 + 6), (x0 + w - 20, y0 + 6), (x0 + w - 26, y0 + 22),
                   (x0 + w - 46, y0 + 22)], fill=(220, 180, 60))
        d.rectangle([x0 + w - 44, y0 + 22, x0 + w - 28, y0 + 40], fill=(220, 180, 60))
        d.rectangle([x0 + w - 50, y0 + 40, x0 + w - 22, y0 + 44], fill=(220, 180, 60))
        d.text((x0 + 58, y0 + 12), "FINAL", font=font(SERIF_B, 14), fill=INK)

# ---------------------------------------------------------------- map
def draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(233, 238, 244))
    d.text((x0 + 8, y0 + 6), "THE WORLD ON SUNDAY  \u2014  18 STORIES PINNED",
           font=font(SANS_B, 10), fill=INK)
    cols, rows = 72, 30
    cw, ch = w / cols, (h - 22) / rows
    oy = y0 + 22
    dot = (110, 118, 128)
    for r, ranges in LAND.items():
        for (c0, c1) in ranges:
            for c in range(c0, c1 + 1):
                px = x0 + c * cw + cw / 2
                py = oy + r * ch + ch / 2
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=dot)
    # pins
    fnum = font(SANS_B, 8)
    pts = {}
    for n, (lon, lat) in PINS.items():
        px = x0 + (lon + 180) / 360 * w
        py = oy + (90 - lat) / 180 * (h - 22)
        pts[n] = (px, py)
    for n, (px, py) in pts.items():
        dx, dy = NUDGE.get(n, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line([(px, py), (qx, qy)], fill=RED, width=1)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED, outline=(255, 255, 255), width=1)
        t = str(n)
        d.text((qx - d.textlength(t, font=fnum) / 2, qy - 5.5), t, font=fnum,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 12

    # masthead
    f_mast = font(DISPLAY, 46)
    draw_center(d, W // 2, y, "Sunday 22 November 2026", f_mast)
    y += 50
    # red subline: the three top stories
    f_sub = font(SERIF_B, 15)
    draw_center(d, W // 2, y, "COP31 collapses with no deal  \u00b7  Russia fires 186 drones  \u00b7  "
                "Iran claims two US radars hit", f_sub, fill=RED)
    y += 22
    hline(d, MX, W - MX, y, fill=INK, wdt=2)
    y += 6

    # numbers strip
    bw = (CW - 5 * 4) / 6
    f_num = font(SERIF_B, 21)
    f_lab = font(SANS_B, 8)
    for i, (num, lab) in enumerate(NUMBERS):
        bx = MX + i * (bw + 4)
        d.rectangle([bx, y, bx + bw, y + 44], fill=CARD_BG, outline=RULE, width=1)
        draw_center(d, bx + bw / 2, y + 2, num, f_num)
        draw_center(d, bx + bw / 2, y + 27, lab, f_lab)
    y += 44 + 6

    # timeline
    f_tl = font(SANS, 9.5)
    draw_center(d, W // 2, y, TIMELINE, f_tl, fill=INK2)
    y += 13
    # region bar
    f_rg = font(SANS_B, 10)
    draw_center(d, W // 2, y, REGIONS, f_rg)
    y += 13
    hline(d, MX, W - MX, y, fill=RULE, wdt=1)
    y += 6

    # heroes: 3 columns, total 236
    hw = (CW - 2 * 12) / 3
    hy0 = y
    f_hhead = font(SERIF_B, 16)
    f_hbody = font(SANS, 10)
    for i, hero in enumerate(HEROES):
        hx = MX + i * (hw + 12)
        globals()["scene_" + hero["scene"]](d, hx, y, hw, 96)
        yy = y + 96 + 5
        tag_chip(d, hx, yy, str(hero["n"]) + "  \u00b7  " + hero["tag"])
        yy += 16
        for ln in wrap(d, hero["head"], f_hhead, hw)[:2]:
            d.text((hx, yy), ln, font=f_hhead, fill=INK)
            yy += 18
        yy += 2
        for ln in wrap(d, hero["body"], f_hbody, hw)[:8]:
            d.text((hx, yy), ln, font=f_hbody, fill=INK2)
            yy += 11
    y = hy0 + 236

    # small grid: 5 cols x 3 rows, card 106
    gw = (CW - 4 * 8) / 5
    gh = 106
    f_chead = font(SERIF_B, 11)
    f_cbody = font(SANS, 9)
    for i, card in enumerate(SMALL):
        r, c = divmod(i, 5)
        cx = MX + c * (gw + 8)
        cy = y + r * (gh + 5)
        d.rectangle([cx, cy, cx + gw, cy + gh], fill=CARD_BG, outline=RULE, width=1)
        draw_mini(d, card["scene"], cx + 1, cy + 1, gw - 2, 44)
        yy = cy + 47
        tag_chip(d, cx + 5, yy, str(card["n"]) + "  \u00b7  " + card["tag"])
        yy += 14
        for ln in wrap(d, card["head"], f_chead, gw - 10)[:2]:
            d.text((cx + 5, yy), ln, font=f_chead, fill=INK)
            yy += 12
        yy += 1
        for ln in wrap(d, card["body"], f_cbody, gw - 10)[:2]:
            d.text((cx + 5, yy), ln, font=f_cbody, fill=INK2)
            yy += 10
    y += 3 * gh + 2 * 5 + 8

    # map + date check row
    map_w = 596
    dc_x = MX + map_w + 12
    dc_w = CW - map_w - 12
    row_h = 132
    draw_map(d, MX, y, map_w, row_h)
    d.rectangle([dc_x, y, dc_x + dc_w, y + row_h], fill=CARD_BG, outline=RULE, width=1)
    d.text((dc_x + 8, y + 4), "DATE CHECK \u2014 NOT SUNDAY",
           font=font(SANS_B, 10), fill=RED)
    d.text((dc_x + 8, y + 17), "These were listed as Sunday news elsewhere;",
           font=font(SANS, 8.5), fill=INK2)
    d.text((dc_x + 8, y + 26), "they happened on other days.",
           font=font(SANS, 8.5), fill=INK2)
    f_dc = font(SANS, 8.5)
    col_w = (dc_w - 16) / 2
    for i, item in enumerate(DATECHECK):
        cc, rr = divmod(i, 8)
        ix = dc_x + 8 + cc * col_w
        iy = y + 40 + rr * 11.5
        d.text((ix, iy), "\u2022 " + item, font=f_dc, fill=INK2)
    y += row_h + 6

    # ALSO list
    f_ah = font(SANS_B, 10)
    d.text((MX, y), "ALSO ON SUNDAY", font=f_ah, fill=INK)
    hline(d, MX + 108, W - MX, y + 7, fill=RULE, wdt=1)
    y += 14
    f_al = font(SANS, 9.5)
    col_w = (CW - 20) / 2
    for i, (reg, item) in enumerate(ALSO):
        cc, rr = divmod(i, 10)
        ix = MX + cc * (col_w + 20)
        iy = y + rr * 10.8
        d.text((ix, iy), reg, font=font(SANS_B, 8.5), fill=RED)
        d.text((ix + 62, iy), item, font=f_al, fill=INK2)
    y += 10 * 10.8 + 3

    # footer: single line
    hline(d, MX, W - MX, y, fill=RULE, wdt=1)
    y += 4
    f_ft = font(SANS, 8.5)
    draw_center(d, W // 2, y,
                "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 BBC \u00b7 CNN \u00b7 The Times \u00b7 "
                "Formula 1 \u00b7 Cricinfo \u00b7 PHIVOLCS \u00b7 Vatican News \u00b7 QNA \u00b7 Saudi Exchange \u00b7 Yle "
                "\u2014 all stories verified vs Sunday 22 Nov 2026; forecasts labelled; claims attributed.",
                f_ft, fill=GREY)
    y += 10
    print("final y =", y, "of", H)
    img.save(out_path, "PNG", optimize=True)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    render(os.path.join(here, "poster.png"))
