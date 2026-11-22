#!/usr/bin/env python3
"""RIVAL5 — "THE SUNDAY VERDICT" — news-image-20261122.

A one-day newspaper poster for Sunday 22 November 2026: 40 stories,
7 regions, every story dated, every card labelled by certainty
(REPORTED / CLAIM / FORECAST) with a legend. Built from scratch with
PIL only; deterministic output (no timestamps, no randomness).

Layout (1024x1024):
  strap / masthead / kicker + NO DEAL / 6-number band / UTC ticker /
  MARKETS band / 3 heroes / 5x4 grid (22 cards + legend) /
  pinned world map + Pacific inset / ALSO 18 / DATE CHECK 24 / sources.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (244, 239, 228)
INK = (26, 26, 26)
RED = (178, 35, 27)
DARKRED = (140, 22, 18)
NAVY = (28, 47, 74)
NAVY2 = (22, 38, 60)
GREY = (110, 105, 95)
LIGHT = (232, 226, 212)
GOLD = (176, 132, 40)

FDIR = "/usr/share/fonts/truetype"
SERIF_B = f"{FDIR}/liberation/LiberationSerif-Bold.ttf"
SERIF = f"{FDIR}/liberation/LiberationSerif-Regular.ttf"
SERIF_I = f"{FDIR}/liberation/LiberationSerif-Italic.ttf"
SANS_B = f"{FDIR}/liberation/LiberationSans-Bold.ttf"
SANS = f"{FDIR}/liberation/LiberationSans-Regular.ttf"
DSANS_B = f"{FDIR}/dejavu/DejaVuSans-Bold.ttf"
DSANS = f"{FDIR}/dejavu/DejaVuSans.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, text, font, x, y, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(d, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=fill)
    return len(lines)


def fit_lines(d, text, font, max_w, max_lines):
    """True if text wraps within max_lines at this font."""
    return len(wrap(d, text, font, max_w)) <= max_lines


# ---------------------------------------------------------------- landmask
# Coarse equirectangular landmask, 72 cols (lon -180..180, 5 deg/col) x
# 24 rows (lat 75..-52). Hand-drawn approximation for a dotted strip map.
LAND = [
    "........##########..........###.......###################.......",
    "......###############......###...###..#######################..",
    "......##################........#############################.",
    "..........###############...#.##############################...",
    "...........##############..###############################....",
    "............#############..##############################.....",
    ".............############...############################......",
    ".............###########....#########################.........",
    "..............##########....########################..........",
    "..............###..#####.....#######################..........",
    "................###.........#######################...........",
    "..................###.......######################............",
    "....................#####....#####################............",
    "....................######....###################.............",
    "....................######.....##################.............",
    "....................######.....##################.............",
    "....................#####......##################.............",
    "....................#####......##################.............",
    "....................####.......################...............",
    "....................###........###############................",
    "....................###..................................##...",
    "....................##...................................##...",
    "....................##........................................",
    "....................##........................................",
]

# ------------------------------------------------------------------ content
# label: R = REPORTED (confirmed by 2+ sources)
#        C = CLAIM (one side asserts, the other denies)
#        F = FORECAST (still to happen when drawn)
HEROES = [
    dict(num=1, place="ANTALYA", tag="44 HOURS OVERTIME", label="R",
         head="COP31 collapses with no deal",
         body=("The EU, UK and Panama rejected a final text that omitted fossil "
               "fuels. First no-deal COP since COP6 in 2000; the longest ever."),
         art="table"),
    dict(num=2, place="KYIV REGION", tag="186 DRONES", label="R",
         head="Russia fires 186 drones; Dymer block destroyed",
         body=("161 downed or jammed; 72 jet-powered. One destroyed a five-storey "
               "block in Dymer; 2 dead, 14 missing. Zelenskyy: 2,700 drones "
               "fired this week."),
         art="drones"),
    dict(num=3, place="MANAMA", tag="CLAIM", label="C",
         head="Iran claims two US radars hit; Bahrain denies it",
         body=("IRGC media claimed Saturday-night strikes hit two US Patriot "
               "radars; Bahrain says its defences intercepted them. A civilian "
               "plant burned, two hurt."),
         art="radar"),
]

CARDS = [
    dict(num=4, place="HONG KONG", label="R",
         head="Hong Kong turnout hits record 98.79%",
         body="5,640 of 5,709 voters cast ballots; count done 22:15. 2021: 30.2%.",
         art="ballot"),
    dict(num=5, place="WELLINGTON", label="R",
         head="India declare 720/9 \u2014 a record in NZ",
         body="Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.",
         art="cricket"),
    dict(num=6, place="LAS VEGAS", label="R",
         head="Verstappen wins Vegas by 0.639s",
         body="75th career win; Norris 2nd, Piastri 3rd from 17th.",
         art="race"),
    dict(num=7, place="SEOUL", label="R",
         head="Seoul minister quits over AI exam scandal",
         body="Choi Kyo-jin resigned; Lee accepted in an hour. 111 device cheating cases probed.",
         art="exam"),
    dict(num=8, place="FINLAND", label="R",
         head="Sparta II still burning off Finland",
         body=("Struck Sat; fire smouldered Sun, 16 crew out. Russian helicopter "
               "suspected of violating Finnish airspace by 4.1 km."),
         art="ship"),
    dict(num=9, place="KRYVYI RIH", label="R",
         head="Missile kills boy, 7, and medic, 20; 58 hurt",
         body="Russian strike on Zelenskyy\u2019s hometown; four fires, ~23 blocks hit, a hospital and schools damaged.",
         art="fire"),
    dict(num=10, place="SAN ANTONIO", label="R",
         head="Wembanyama drops 50 as Spurs rout Pelicans",
         body="San Antonio\u2019s star scores 50 in a 114\u201391 rout of New Orleans.",
         art="hoops"),
    dict(num=11, place="CIKANDE", label="R",
         head="Candy-factory fire: 3 dead, 36 missing",
         body="Blaze broke out Saturday 17:00; search went on Sunday; 300 workers inside.",
         art="factory"),
    dict(num=12, place="GAZA", label="R",
         head="Hamas seeks urgent talks after aid-van strike",
         body="An aid-van strike killed aid workers on Saturday; Hamas called for urgent talks on aid access.",
         art="tent"),
    dict(num=13, place="BAYELSA", label="R",
         head="Nigeria boat toll reaches 24",
         body="Capsized Friday, Ayama-Ukubie; 24 dead, 24 rescued. Manager held.",
         art="boat"),
    dict(num=14, place="VATICAN", label="R",
         head="Pope Leo XIV hosts 1,300 for lunch",
         body="10th World Day of the Poor; lunch in Paul VI Hall, a week of events.",
         art="dome"),
    dict(num=15, place="FUKUSHIMA", label="R",
         head="1,500 still cut off by Japan landslide",
         body="Travellers stranded in Kitashiobara since Saturday; heavy rain hampered rescue.",
         art="rain"),
    dict(num=16, place="MINDANAO", label="R",
         head="M6.6 quake off Mindanao; no damage",
         body="Off southern Mindanao, 15:54 local, depth 10 km. No tsunami.",
         art="quake"),
    dict(num=17, place="CANBERRA", label="R",
         head="Albanese: US report \u2018wrong\u2019 on AUKUS",
         body="Defence minister rejects CBO warning on subs cost; US $368bn programme.",
         art="parl"),
    dict(num=18, place="TURIN", label="F",
         head="Zverev v Alcaraz in Turin final today",
         body="ATP Finals title match closes the season in Turin.",
         art="tennis"),
    dict(num=19, place="WARSAW", label="F",
         head="NATO to meet Monday over Poland incursion",
         body="Drone debris confirmed in Nowy Lipowiec. Council meets Monday.",
         art="flags"),
    dict(num=20, place="TALLINN", label="R",
         head="Moscow vows retaliation as Estonia seals border",
         body="Estonia seals crossings for months; Moscow calls it a new Iron Curtain.",
         art="fence"),
    dict(num=21, place="DELHI", label="R",
         head="Nepal PM Shah lands in Delhi",
         body="First foreign trip; talks with Modi on Monday.",
         art="plane"),
    dict(num=22, place="LIVERPOOL", label="R", ft=True,
         head="Liverpool 4\u20130 Man Utd: Pochettino routed on debut",
         body="Szoboszlai 10\u2019, Wirtz 13\u2019, Ngumoha 66\u2019, Mu\u00f1oz 82\u2019; Yoro sent off 8\u2019. United 18th.",
         art="score"),
]

# ALSO list: (num, region, text, source, label, dagger)
# dagger: "FRI" / "SAT" = happened Fri/Sat, updated Sunday.
ALSO = [
    (23, "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv", "R", ""),
    (24, "EUROPE", "Russia says it downed 170 Ukrainian drones overnight", "Moscow", "C", ""),
    (25, "WORLD", "Bitcoin back above $60,000 after Saturday\u2019s $55,130 low", "Coinbase", "R", ""),
    (26, "AMERICAS", "San Francisco braces for record king tides", "SF", "F", ""),
    (27, "MID EAST", "US denies Iran claim it downed an F-16", "CENTCOM", "C", ""),
    (28, "MID EAST", "Lebanon marks 83rd Independence Day", "Beirut", "R", ""),
    (29, "EUROPE", "Cost-of-living protests across Europe, third day running", "Paris", "R", ""),
    (30, "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children", "W. Kordofan", "R", ""),
    (31, "AFRICA", "S. Africa holds prayer service for Mlambo-Ngcuka, 71 (died Fri)", "SABC", "R", ""),
    (32, "OCEANIA", "Melbourne: 70 years since the 1956 Olympics opened", "Melbourne", "R", ""),
    (33, "EUROPE", "Hull stun Brighton 2\u20130 \u2014 McBurnie late brace", "MKM", "R", ""),
    (34, "WORLD", "Pope prays for war victims; drought-hit Papua New Guinea", "Vatican", "R", ""),
    (35, "MID EAST", "Iraq: fire at Hartha power station kills 4, injures 35", "Basra", "R", "FRI"),
    (36, "EUROPE", "Moldova: Russian drone crossed border twice near Purcari", "Chisinau", "R", "SAT"),
    (37, "AFRICA", "Somalia: UAE envoy\u2019s 72 hours run out today (ordered Thu)", "Mogadishu", "R", ""),
    (38, "ASIA-PACIFIC", "India: Manipur liquor toll climbs to 19, 600+ in hospital", "Imphal", "R", "FRI"),
    (39, "ASIA-PACIFIC", "M5.3 quake in the Celebes Sea, 61 km deep, 07:54 UTC", "EMSC", "R", ""),
    (40, "AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "Brasilia", "R", ""),
]

# DATE CHECK: not Sunday, however listed elsewhere. 3 columns.
DATECHECK = [
    ["Peru quake \u2014 Fri 20 Nov",
     "Kenya\u2019s last Ebola patient out \u2014 11 Nov",
     "Gaza aid-van strike \u2014 Sat 21 Nov",
     "Japan poll: 62% feel affinity to Korea \u2014 Fri 20 Nov",
     "Mlambo-Ngcuka dies \u2014 Fri 20 Nov",
     "EU-Indonesia deal \u2014 Sat 21 Nov",
     "Denmark expels Russian attach\u00e9 \u2014 Fri 20 Nov",
     "Qatar talks in Tehran \u2014 Fri 20 Nov"],
    ["BepiColombo at Mercury \u2014 Sat 21 Nov",
     "Sparta II struck \u2014 Sat 21 Nov",
     "Newcastle 2\u20132 Arsenal; Chelsea 1\u20134 Leeds \u2014 Sat 21 Nov",
     "DR Congo Cantine attack \u2014 night of 5\u20136 Nov",
     "Estonia closes border \u2014 decided Fri 20 Nov",
     "Nvidia SEC probe \u2014 Fri 20 Nov",
     "UK\u2013EU food deal agreed \u2014 Fri 20 Nov",
     "Senate $350bn defence push stalls \u2014 Fri 20 Nov"],
    ["ICJ Myanmar ruling \u2014 Thu 19 Nov",
     "Bayelsa boat capsizes \u2014 Fri 20 Nov",
     "Aoun\u2019s Israel-withdrawal speech \u2014 Sat 21 Nov",
     "Somalia orders UAE envoy out \u2014 Thu 19 Nov",
     "El Chapo Isidro seized \u2014 Fri 20 Nov",
     "Trump\u2013Xi\u2013Putin talks \u2014 Thu 19 Nov",
     "H-6 bomber patrol nears Manila \u2014 Sat 21 Nov"],
]

# Map pins: (num, lon, lat, label dx, label dy) — offsets fan the Europe cluster.
PINS = [
    (1, 30.7, 36.9, -8, 14), (2, 30.5, 50.4, 30, -4), (3, 50.6, 26.2, 0, 0),
    (4, 114.2, 22.3, 0, 0), (5, 174.8, -41.3, 0, 0), (6, -115.1, 36.2, 0, 0),
    (7, 127.0, 37.5, 0, 0), (8, 24.0, 60.0, -16, -20), (9, 33.4, 47.9, 24, 10),
    (10, -98.5, 29.4, 0, 0), (11, 106.3, -6.3, 0, 0), (12, 34.5, 31.5, 16, 20),
    (13, 6.3, 4.8, 0, -14), (14, 12.45, 41.9, -6, 16), (15, 140.5, 37.8, 0, 0),
    (16, 126.0, 7.0, 0, 12), (17, 149.1, -35.3, 0, 0), (18, 7.7, 45.1, -22, 12),
    (19, 21.0, 52.2, 8, -18), (20, 24.7, 59.4, 24, -12), (21, 77.2, 28.6, 0, 0),
    (22, -3.0, 53.4, -24, -6),
]

# ------------------------------------------------------------------ labels
LABEL_TEXT = {"R": "REPORTED", "C": "CLAIM", "F": "FORECAST"}
LABEL_FILL = {"R": (46, 110, 60), "C": (176, 110, 20), "F": (40, 90, 140)}


def label_chip(d, x, y, label, font):
    """Small certainty chip: coloured disc + word. Returns width used."""
    col = LABEL_FILL[label]
    d.ellipse([x, y + 1, x + 7, y + 8], fill=col)
    d.text((x + 10, y), LABEL_TEXT[label], font=font, fill=col)
    return 10 + d.textlength(LABEL_TEXT[label], font=font)


# ------------------------------------------------------------------ art
def art_strip(d, x0, y0, w, h, kind):
    """Flat mini illustration strip; drawn at 22px then scaled to h."""
    tmp = Image.new("RGB", (w, 22), (120, 120, 120))
    td = ImageDraw.Draw(tmp)
    _art_strip_inner(td, 0, 0, w, 22, kind)
    tmp = tmp.resize((w, h), Image.LANCZOS)
    d._image.paste(tmp, (x0, y0))


def _art_strip_inner(d, x0, y0, w, h, kind):
    """Flat mini illustration strip, 22px tall (heroes get their own)."""
    x1, y1 = x0 + w, y0 + h
    sky = {
        "ballot": (178, 34, 34), "cricket": (96, 140, 80), "race": (30, 30, 46),
        "exam": (70, 90, 120), "ship": (40, 80, 110), "fire": (60, 50, 55),
        "hoops": (200, 120, 50), "factory": (90, 90, 95), "tent": (190, 160, 110),
        "boat": (40, 100, 140), "dome": (210, 190, 150), "rain": (90, 110, 130),
        "quake": (120, 100, 80), "parl": (60, 70, 100), "tennis": (80, 140, 90),
        "flags": (40, 60, 100), "fence": (110, 100, 85), "plane": (140, 170, 200),
        "score": (150, 20, 20),
    }.get(kind, (120, 120, 120))
    d.rectangle([x0, y0, x1, y1], fill=sky)
    cx, cy = x0 + w // 2, y0 + h // 2
    if kind == "ballot":  # ballot box + red bars
        d.rectangle([x0 + 8, y0 + 14, x0 + w - 8, y1 - 3], fill=(240, 235, 220))
        for i, bh in enumerate((6, 10, 8, 12)):
            bx = x0 + 14 + i * 16
            d.rectangle([bx, y1 - 4 - bh, bx + 10, y1 - 4], fill=(178, 35, 27))
        d.rectangle([x0 + w - 34, y0 + 4, x0 + w - 10, y0 + 9], fill=(26, 26, 26))
    elif kind == "cricket":  # pitch + stumps
        d.rectangle([x0, y0 + 15, x1, y1], fill=(190, 170, 120))
        for sx in (x0 + 20, x0 + w - 26):
            for k in range(3):
                d.rectangle([sx + k * 4, y0 + 6, sx + k * 4 + 2, y0 + 14], fill=(240, 230, 200))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(178, 35, 27))
    elif kind == "race":  # chequered band
        for i in range(12):
            c = (240, 240, 240) if i % 2 == 0 else (20, 20, 20)
            d.rectangle([x0 + i * (w // 12), y0 + 4, x0 + (i + 1) * (w // 12), y0 + 12], fill=c)
        d.rectangle([x0, y0 + 15, x1, y1 - 2], fill=(60, 60, 70))
        d.ellipse([cx - 5, y0 + 15, cx + 5, y1 - 3], fill=(255, 200, 40))
    elif kind == "exam":  # paper + magnifier
        d.rectangle([x0 + 12, y0 + 3, x0 + w - 40, y1 - 3], fill=(245, 242, 235))
        for i in range(3):
            d.rectangle([x0 + 17, y0 + 7 + i * 5, x0 + w - 50, y0 + 9 + i * 5], fill=(120, 120, 120))
        d.ellipse([x0 + w - 30, y0 + 4, x0 + w - 12, y1 - 6], outline=(255, 220, 80), width=2)
    elif kind == "ship":  # hull + smoke
        d.polygon([(x0 + 20, y0 + 14), (x0 + w - 20, y0 + 14), (x0 + w - 32, y1 - 3), (x0 + 32, y1 - 3)], fill=(40, 40, 45))
        d.rectangle([x0 + w // 2 - 4, y0 + 4, x0 + w // 2 + 4, y0 + 14], fill=(200, 200, 200))
        for i, r in enumerate((4, 6, 8)):
            d.ellipse([x0 + w // 2 - 14 + i * 10, y0 + 1 - i, x0 + w // 2 - 6 + i * 10, y0 + 9 - i], fill=(230, 230, 230))
    elif kind == "fire":  # building + flame
        d.rectangle([x0 + 14, y0 + 8, x0 + w - 14, y1 - 3], fill=(70, 60, 65))
        for i in range(3):
            d.rectangle([x0 + 22 + i * 18, y0 + 12, x0 + 30 + i * 18, y0 + 18], fill=(255, 210, 90))
        d.polygon([(cx - 6, y0 + 12), (cx, y0 + 1), (cx + 6, y0 + 12)], fill=(255, 120, 30))
    elif kind == "hoops":  # court + ball
        d.rectangle([x0, y0 + 14, x1, y1], fill=(220, 180, 120))
        d.ellipse([cx - 16, y0 + 2, cx + 16, y1 - 2], outline=(255, 255, 255), width=2)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(220, 90, 30))
    elif kind == "factory":  # factory + chimney smoke
        d.rectangle([x0 + 12, y0 + 10, x0 + w - 12, y1 - 3], fill=(60, 60, 66))
        d.polygon([(x0 + 12, y0 + 10), (x0 + 30, y0 + 2), (x0 + 48, y0 + 10)], fill=(80, 80, 88))
        d.rectangle([x0 + w - 30, y0 + 2, x0 + w - 22, y0 + 12], fill=(50, 50, 55))
        d.ellipse([x0 + w - 34, y0 - 1, x0 + w - 26, y0 + 7], fill=(230, 230, 230))
    elif kind == "tent":  # tent + sun
        d.polygon([(x0 + 20, y1 - 3), (cx, y0 + 4), (x0 + w - 20, y1 - 3)], fill=(200, 120, 60))
        d.ellipse([x0 + w - 26, y0 + 2, x0 + w - 12, y0 + 16], fill=(255, 210, 90))
    elif kind == "boat":  # hull + waves
        d.polygon([(x0 + 30, y0 + 12), (x0 + w - 30, y0 + 12), (x0 + w - 44, y1 - 4), (x0 + 44, y1 - 4)], fill=(120, 70, 40))
        for i in range(3):
            d.arc([x0 + 10 + i * 30, y1 - 8, x0 + 34 + i * 30, y1 + 2], 180, 360, fill=(255, 255, 255), width=2)
    elif kind == "dome":  # dome + colonnade
        d.pieslice([cx - 16, y0, cx + 16, y0 + 22], 180, 360, fill=(240, 230, 200))
        d.rectangle([x0 + 16, y1 - 8, x1 - 16, y1 - 3], fill=(200, 180, 140))
        for i in range(5):
            d.rectangle([x0 + 22 + i * 14, y1 - 14, x0 + 26 + i * 14, y1 - 8], fill=(240, 230, 200))
    elif kind == "rain":  # mountain + rain
        d.polygon([(x0 + 10, y1 - 3), (cx - 10, y0 + 6), (cx + 20, y1 - 3)], fill=(80, 90, 100))
        d.polygon([(cx + 10, y1 - 3), (x0 + w - 30, y0 + 10), (x0 + w - 6, y1 - 3)], fill=(100, 110, 120))
        for i in range(4):
            d.line([x0 + 20 + i * 16, y0 + 2, x0 + 16 + i * 16, y0 + 9], fill=(220, 230, 240), width=2)
    elif kind == "quake":  # seismograph line
        pts = [(x0 + 6, cy), (x0 + 30, cy), (x0 + 40, cy - 7), (x0 + 50, cy + 7),
               (x0 + 60, cy - 4), (x0 + 72, cy + 3), (x0 + 90, cy), (x1 - 8, cy)]
        d.line(pts, fill=(255, 255, 255), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 120, 30))
    elif kind == "parl":  # parliament flagpole
        d.rectangle([x0 + 14, y1 - 6, x1 - 14, y1 - 3], fill=(200, 190, 160))
        d.rectangle([cx - 2, y0 + 4, cx + 2, y1 - 6], fill=(240, 240, 240))
        d.polygon([(cx + 2, y0 + 4), (cx + 26, y0 + 8), (cx + 2, y0 + 12)], fill=(0, 90, 160))
    elif kind == "tennis":  # court + ball
        d.rectangle([x0 + 10, y0 + 4, x1 - 10, y1 - 4], fill=(60, 110, 200))
        d.line([cx, y0 + 4, cx, y1 - 4], fill=(255, 255, 255), width=2)
        d.ellipse([x0 + w - 30, y0 + 5, x0 + w - 18, y0 + 17], fill=(200, 230, 60))
    elif kind == "flags":  # two flags
        for i, col in enumerate(((255, 255, 255), (220, 40, 40))):
            fx = x0 + 30 + i * 60
            d.rectangle([fx, y0 + 3, fx + 3, y1 - 3], fill=(240, 240, 240))
            d.polygon([(fx + 3, y0 + 3), (fx + 30, y0 + 7), (fx + 3, y0 + 11)], fill=col)
    elif kind == "fence":  # border fence
        for i in range(9):
            fx = x0 + 12 + i * 20
            d.rectangle([fx, y0 + 3, fx + 3, y1 - 3], fill=(220, 220, 220))
        d.rectangle([x0 + 8, y0 + 6, x1 - 8, y0 + 9], fill=(220, 220, 220))
        d.rectangle([x0 + 8, y1 - 7, x1 - 8, y1 - 4], fill=(220, 220, 220))
    elif kind == "plane":  # plane silhouette
        d.polygon([(x0 + 20, cy), (x0 + w - 40, cy - 6), (x0 + w - 20, cy), (x0 + w - 40, cy + 6)], fill=(255, 255, 255))
        d.polygon([(cx - 6, cy - 2), (cx + 14, cy - 12), (cx + 20, cy - 12), (cx + 6, cy - 2)], fill=(255, 255, 255))
    elif kind == "score":  # scoreboard 4-0
        d.rectangle([x0 + w // 2 - 34, y0 + 3, x0 + w // 2 + 34, y1 - 3], fill=(20, 20, 20))
        d.text((x0 + w // 2 - 24, y0 + 4), "4 \u2013 0", font=F(DSANS_B, 13), fill=(255, 255, 255))


def hero_art(d, x0, y0, w, h, kind):
    """Hero illustration, ~98px tall, flat shapes."""
    x1, y1 = x0 + w, y0 + h
    if kind == "table":  # COP31 negotiation table, flags, clock
        d.rectangle([x0, y0, x1, y1], fill=(96, 72, 48))
        d.rectangle([x0, y0 + h - 34, x1, y1], fill=(52, 36, 22))
        d.rectangle([x0 + 10, y0 + h - 62, x1 - 10, y0 + h - 34], fill=(140, 100, 60))
        cols = [(200, 40, 40), (240, 200, 40), (40, 90, 200), (240, 240, 240),
                (40, 160, 80), (240, 140, 40), (160, 60, 160)]
        n = 7
        for i, col in enumerate(cols):
            px = x0 + 18 + i * ((w - 36) // (n - 1))
            d.rectangle([px, y0 + 26, px + 2, y0 + 62], fill=(230, 230, 230))
            d.polygon([(px + 2, y0 + 26), (px + 22, y0 + 31), (px + 2, y0 + 36)], fill=col)
            d.ellipse([px - 9, y0 + 62, px + 11, y0 + 82], fill=(230, 200, 160))
            d.rectangle([px - 11, y0 + 82, px + 13, y0 + 86], fill=(30, 30, 30))
        # wall clock: overtime
        ccx, ccy = x1 - 34, y0 + 34
        d.ellipse([ccx - 20, ccy - 20, ccx + 20, ccy + 20], fill=(245, 242, 235))
        d.ellipse([ccx - 20, ccy - 20, ccx + 20, ccy + 20], outline=(30, 30, 30), width=2)
        d.line([ccx, ccy, ccx, ccy - 13], fill=(30, 30, 30), width=2)
        d.line([ccx, ccy, ccx + 10, ccy + 4], fill=(30, 30, 30), width=2)
    elif kind == "drones":  # night sky, drones, moon, rooftops
        d.rectangle([x0, y0, x1, y1], fill=(38, 34, 66))
        d.ellipse([x1 - 62, y0 + 14, x1 - 26, y0 + 50], fill=(235, 225, 190))
        for sx, sy in [(x0 + 20, y0 + 12), (x0 + 90, y0 + 30), (x0 + 160, y0 + 10),
                       (x0 + 230, y0 + 26), (x0 + 280, y0 + 8), (x0 + 60, y0 + 48)]:
            d.text((sx, sy), "\u2726", font=F(DSANS, 9), fill=(255, 255, 255))
        for dx, dy in [(x0 + 40, y0 + 34), (x0 + 110, y0 + 20), (x0 + 180, y0 + 44),
                       (x0 + 250, y0 + 18), (x0 + 300, y0 + 52), (x0 + 150, y0 + 62)]:
            d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(255, 140, 50))
            d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 220, 140))
            d.line([dx + 5, dy + 5, dx + 12, dy + 12], fill=(255, 140, 50), width=2)
        d.polygon([(x0, y1), (x0 + 60, y0 + h - 34), (x0 + 130, y1)], fill=(22, 20, 40))
        d.polygon([(x1 - 130, y1), (x1 - 60, y0 + h - 28), (x1, y1)], fill=(22, 20, 40))
        mcx = x0 + w // 2
        d.ellipse([mcx - 12, y0 + h - 46, mcx + 12, y0 + h - 22],
                  fill=(255, 150, 60))
    elif kind == "radar":  # night, two Patriot-style radar dishes, blast
        d.rectangle([x0, y0, x1, y1], fill=(52, 34, 36))
        for sx, sy in [(x0 + 16, y0 + 14), (x0 + 70, y0 + 30), (x0 + 140, y0 + 10),
                       (x0 + 210, y0 + 28), (x0 + 280, y0 + 12), (x0 + 250, y0 + 44)]:
            d.text((sx, sy), "\u2726", font=F(DSANS, 9), fill=(255, 240, 200))
        for rx in (x0 + 70, x0 + w - 110):
            d.arc([rx - 34, y0 + 34, rx + 34, y0 + 102], 180, 360, fill=(235, 235, 235), width=4)
            d.line([rx, y0 + 68, rx, y1 - 8], fill=(235, 235, 235), width=4)
            d.line([rx, y0 + 68, rx + 22, y0 + 46], fill=(235, 235, 235), width=3)
        d.rectangle([x0 + 12, y1 - 22, x0 + 90, y1 - 8], fill=(30, 22, 24))
        for i in range(4):
            d.rectangle([x0 + 18 + i * 18, y1 - 34, x0 + 30 + i * 18, y1 - 22], fill=(40, 30, 32))
        bx, by = x0 + w // 2, y0 + 44
        d.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(255, 140, 40))
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(255, 220, 120))

# ------------------------------------------------------------------ render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    f_mast = F(SERIF_B, 58)
    f_kick = F(SERIF_B, 15)
    f_num = F(SERIF_B, 27)
    f_cap = F(SANS_B, 8)
    f_cap2 = F(SANS, 8)
    f_tick = F(SANS, 10)
    f_mkt_big = F(SANS_B, 17)
    f_mkt_mid = F(SANS_B, 13)
    f_mkt_sm = F(SANS, 8)
    f_hero_head = F(SERIF_B, 20)
    f_hero_body = F(SERIF, 11)
    f_kick_sm = F(SANS_B, 9)
    f_card_head = F(SERIF_B, 13)
    f_card_body = F(SERIF, 8)
    f_sec = F(SANS_B, 11)
    f_also = F(SERIF, 8)
    f_also_b = F(SANS_B, 8)
    f_dc = F(SERIF, 8)
    f_src = F(SANS, 8)

    # --- top strap
    d.text((12, 6), "THE SUNDAY VERDICT \u2014 THE WORLD IN ONE DAY",
           font=F(SANS_B, 11), fill=INK)
    right = "40 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - 12 - d.textlength(right, font=F(SANS_B, 10)), 7), right,
           font=F(SANS_B, 10), fill=INK)
    d.line([12, 26, W - 12, 26], fill=INK, width=2)

    # --- masthead
    d.text((12, 26), "Sunday 22 November 2026", font=f_mast, fill=INK)
    d.line([12, 88, W - 12, 88], fill=INK, width=2)
    d.line([12, 91, W - 12, 91], fill=INK, width=1)

    # --- kicker line + NO DEAL badge
    d.text((12, 96), "COP31 collapses with no deal  \u00b7  Russia fires 186 drones  \u00b7  "
                      "Iran claims two US radars hit", font=f_kick, fill=RED)
    badge = "NO DEAL"
    bw = d.textlength(badge, font=F(SANS_B, 14)) + 18
    d.rectangle([W - 12 - bw, 95, W - 12, 115], fill=RED)
    d.text((W - 12 - bw + 9, 98), badge, font=F(SANS_B, 14), fill=(255, 255, 255))

    # --- 6-number band
    nums = [("44h", "COP31 OVERTIME", "TO COLLAPSE"),
            ("186", "DRONES OR MISSILES", "AT UKRAINE"),
            ("161", "DOWNED OR", "JAMMED"),
            ("720/9", "INDIA\u2019S RECORD", "TEST TOTAL"),
            ("$61,568", "BITCOIN\u2019S SUNDAY", "HIGH"),
            ("98.79%", "HONG KONG TURNOUT,", "RECORD")]
    cw = (W - 24) / 6
    y0 = 116
    for i, (n, c1, c2) in enumerate(nums):
        x = 12 + i * cw
        d.text((x + 4, y0), n, font=f_num, fill=INK)
        d.text((x + 4, y0 + 29), c1, font=f_cap, fill=GREY)
        d.text((x + 4, y0 + 39), c2, font=f_cap, fill=GREY)
        if i:
            d.line([x, y0 + 2, x, y0 + 46], fill=(200, 192, 175), width=1)
    d.line([12, 164, W - 12, 164], fill=INK, width=1)

    # --- UTC ticker
    d.text((12, 168), "THE DAY IN UTC \u2014  03:00 COP31 objections close  \u00b7  05:30 Verstappen "
                      "wins Vegas  \u00b7  06:00 COP31 approval due  \u00b7  09:29 Hamas seeks "
                      "talks  \u00b7  14:15 HK count done",
           font=f_tick, fill=INK)
    d.line([12, 184, W - 12, 184], fill=INK, width=1)

    # --- MARKETS band
    d.rectangle([12, 188, W - 12, 232], fill=NAVY)
    d.text((20, 194), "MARKETS \u2014", font=F(SANS_B, 11), fill=(255, 255, 255))
    d.text((20, 210), "SUNDAY 22 NOV", font=F(SANS_B, 11), fill=(255, 255, 255))
    mkts = [("GOLD, per oz, Sunday", "$3,539", None),
            ("BITCOIN \u2014 Sunday high", "$61,568", None),
            ("TASI \u2014 9,960.44, Riyadh", "\u22121.95%", (255, 120, 110)),
            ("QATAR \u2014 9,902.87, Doha", "\u22121.59%", (255, 120, 110)),
            ("EGX30 \u2014 49,989.79, Cairo", "\u22122.85%", (255, 120, 110)),
            ("EGX70 \u2014 16,534.42, Cairo", "\u22125.55%", (255, 120, 110))]
    mw = (W - 24 - 150) / 6
    for i, (lab, val, col) in enumerate(mkts):
        x = 12 + 150 + i * mw
        d.text((x + 6, 193), lab, font=f_mkt_sm, fill=(180, 190, 205))
        d.text((x + 6, 205), val, font=f_mkt_big if i < 2 else f_mkt_mid,
               fill=col or (255, 255, 255))
        d.line([x, 192, x, 228], fill=(60, 80, 110), width=1)

    # --- heroes
    hx = [12, 342, 672]
    hw = [324, 324, 326]
    hy, hh = 238, 180
    for h, x0, w in zip(HEROES, hx, hw):
        x1 = x0 + w
        hero_art(d, x0, hy, w, 90, h["art"])
        d.rectangle([x0, hy + 90, x1, hy + 105], fill=INK)
        d.text((x0 + 6, hy + 93), f"{h['num']}  {h['place']}  \u00b7  {h['tag']}",
               font=f_kick_sm, fill=(255, 255, 255))
        label_chip(d, x1 - 78, hy + 93, h["label"], F(SANS_B, 8))
        d.rectangle([x0, hy + 105, x1, hy + hh], fill=PAPER)
        d.rectangle([x0, hy, x1, hy + hh], outline=(120, 112, 95), width=1)
        draw_wrapped(d, h["head"], f_hero_head, x0 + 6, hy + 107, w - 12, 20,
                     max_lines=2)
        draw_wrapped(d, h["body"], f_hero_body, x0 + 6, hy + 147, w - 12,
                     11, max_lines=3)

    # --- grid 5 x 4 (22 cards + legend)
    gx = [12, 213, 414, 615, 816]
    gw = 196
    gy = [424, 504, 584, 664]
    gh = 80
    for idx, c in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x0, y0 = gx[col], gy[row]
        x1 = x0 + gw
        art_strip(d, x0, y0, gw, 16, c["art"])
        d.rectangle([x0, y0 + 16, x1, y0 + 27], fill=PAPER)
        d.text((x0 + 4, y0 + 18), f"{c['num']}  {c['place']}", font=f_kick_sm, fill=RED)
        chip_x = x1 - 4 - (10 + d.textlength(LABEL_TEXT[c["label"]], font=F(SANS_B, 7)))
        label_chip(d, chip_x, y0 + 18, c["label"], F(SANS_B, 7))
        d.rectangle([x0, y0, x1, y0 + gh], outline=(120, 112, 95), width=1)
        head_lines = draw_wrapped(d, c["head"], f_card_head, x0 + 4, y0 + 28,
                                  gw - 8, 13, max_lines=2)
        by = y0 + 28 + head_lines * 13 + 1
        draw_wrapped(d, c["body"], f_card_body, x0 + 4, by, gw - 8, 8,
                     max_lines=3)
        if c.get("ft"):
            tw = d.textlength("FULL TIME", font=F(SANS_B, 7)) + 8
            d.rectangle([x1 - tw - 2, y0 + 2, x1 - 2, y0 + 12], fill=RED)
            d.text((x1 - tw + 2, y0 + 3), "FULL TIME", font=F(SANS_B, 7),
                   fill=(255, 255, 255))
    # legend cell: row 4, col 5
    lx, ly = gx[4], gy[3]
    d.rectangle([lx, ly, lx + gw, ly + gh], fill=LIGHT)
    d.rectangle([lx, ly, lx + gw, ly + gh], outline=(120, 112, 95), width=1)
    d.text((lx + 6, ly + 4), "HOW TO READ", font=F(SANS_B, 9), fill=INK)
    legend = [
        ((46, 110, 60), "REPORTED \u2014 confirmed by 2+ sources"),
        ((176, 110, 20), "CLAIM \u2014 one side asserts, other denies"),
        ((40, 90, 140), "FORECAST \u2014 still to happen when drawn"),
        (RED, "FULL TIME \u2014 final score in"),
        (INK, "\u2020 in ALSO \u2014 dated Fri/Sat, see below"),
    ]
    for i, (col, txt) in enumerate(legend):
        yy = ly + 19 + i * 12
        d.ellipse([lx + 7, yy + 1, lx + 14, yy + 8], fill=col)
        d.text((lx + 18, yy), txt, font=F(SANS, 8), fill=INK)

    # --- map
    my = 750
    d.text((12, my), "THE WORLD ON SUNDAY \u2014 22 STORIES PINNED",
           font=f_sec, fill=INK)
    rc = "EUROPE 14  \u00b7  MIDDLE EAST 5  \u00b7  ASIA-PACIFIC 8  \u00b7  AMERICAS 4  \u00b7  AFRICA 4  \u00b7  OCEANIA 3  \u00b7  WORLD 2"
    d.text((W - 12 - d.textlength(rc, font=F(SANS_B, 9)), my + 1), rc,
           font=F(SANS_B, 9), fill=GREY)
    map_x0, map_x1 = 12, 780
    map_y0, map_y1 = my + 18, 824
    def lonlat(lon, lat):
        x = map_x0 + (lon + 170) / 320 * (map_x1 - map_x0)
        y = map_y0 + (75 - lat) / 130 * (map_y1 - map_y0)
        return x, y
    for r, row in enumerate(LAND):
        if r % 2:
            continue
        for cix, ch in enumerate(row):
            if ch == "#":
                lon = -180 + cix * 5 + 2.5
                if lon < -170 or lon > 150:
                    continue
                lat = 75 - r * (130 / 24) - 2.7
                x, y = lonlat(lon, lat)
                d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(150, 142, 125))
    f_pin = F(DSANS_B, 7)
    for num, lon, lat, dx, dy in PINS:
        if num in (5, 17):
            continue  # drawn in the Pacific inset
        x, y = lonlat(lon, lat)
        lx2, ly2 = x + dx, y + dy
        if dx or dy:
            d.line([x, y, lx2, ly2], fill=RED, width=1)
        d.ellipse([lx2 - 7, ly2 - 7, lx2 + 7, ly2 + 7], fill=RED)
        tw = d.textlength(str(num), font=f_pin)
        d.text((lx2 - tw / 2, ly2 - 5), str(num), font=f_pin, fill=(255, 255, 255))
    # Pacific inset (beside the map, not on top of it)
    ix0, iy0, ix1, iy1 = 790, map_y0, W - 12, map_y1
    d.rectangle([ix0, iy0, ix1, iy1], fill=(225, 232, 240))
    d.rectangle([ix0, iy0, ix1, iy1], outline=NAVY, width=1)
    d.text((ix0 + 5, iy0 + 2), "PACIFIC \u2014 INSET", font=F(SANS_B, 8), fill=NAVY)
    def inset_xy(lon, lat):
        x = ix0 + 8 + (lon - 135) / 45 * (ix1 - ix0 - 16)
        y = iy0 + 14 + (-20 - lat) / 30 * (iy1 - iy0 - 18)
        return x, y
    for num, lon, lat, _, _ in PINS:
        if num not in (5, 17):
            continue
        x, y = inset_xy(lon, lat)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED)
        tw = d.textlength(str(num), font=f_pin)
        d.text((x - tw / 2, y - 5), str(num), font=f_pin, fill=(255, 255, 255))
    d.text((ix0 + 6, iy1 - 12), "WELLINGTON 5  \u00b7  CANBERRA 17",
           font=F(SANS_B, 8), fill=NAVY)

    # --- ALSO
    ay = 828
    d.text((12, ay), "ALSO ON SUNDAY 22 NOVEMBER \u2014 18 MORE STORIES",
           font=f_sec, fill=INK)
    d.text((W - 12 - d.textlength("FORECAST = still to happen when drawn", font=F(SANS, 9)), ay + 1),
           "FORECAST = still to happen when drawn", font=F(SANS, 9), fill=GREY)
    d.line([12, ay + 15, W - 12, ay + 15], fill=INK, width=1)
    left_items = ALSO[0::2]
    right_items = ALSO[1::2]
    for col_i, items in enumerate((left_items, right_items)):
        x0 = 12 if col_i == 0 else 516
        for ri, (num, region, text, src, lab, dag) in enumerate(items):
            yy = ay + 19 + ri * 8.4
            d.text((x0, yy), str(num), font=F(SANS_B, 9), fill=RED)
            nx = x0 + 18
            d.text((nx, yy), region, font=f_also_b, fill=INK)
            tx = nx + d.textlength(region + "  ", font=f_also_b)
            label = ""
            if lab == "C":
                label = " \u25cb CLAIM"
            elif lab == "F":
                label = " \u25f7 FORECAST"
            if dag:
                label += f"  \u2020 {dag}"
            full = text + label
            # shrink text if it would collide with the source at right
            src_w = d.textlength(src, font=F(SANS, 8))
            max_w = (W - 12 - src_w - 8) - tx if col_i == 1 else (508 - src_w - 8) - tx
            lines = wrap(d, full, f_also, max_w)
            if len(lines) > 1:
                print(f"ALSO OVERFLOW {num}: {full}", file=sys.stderr)
            d.text((tx, yy), lines[0], font=f_also, fill=INK)
            sx = (W - 12 - src_w) if col_i == 1 else (508 - src_w)
            d.text((sx, yy), src, font=F(SANS, 8), fill=GREY)

    # --- DATE CHECK
    dy = 926
    d.text((12, dy), "DATE CHECK \u2014 NOT SUNDAY, however listed elsewhere:",
           font=F(SANS_B, 11), fill=RED)
    d.line([12, dy + 14, W - 12, dy + 14], fill=RED, width=1)
    col_w = (W - 24) / 3
    for ci, items in enumerate(DATECHECK):
        x0 = 12 + ci * col_w
        for ri, item in enumerate(items):
            yy = dy + 18 + ri * 8.3
            d.text((x0, yy), "\u00d7  " + item, font=f_dc, fill=INK)
    # --- sources
    d.line([12, 1013, W - 12, 1013], fill=INK, width=1)
    d.text((12, 1015),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 BBC \u00b7 The Times \u00b7 Formula 1 \u00b7 "
           "Cricinfo \u00b7 PHIVOLCS \u00b7 Vatican News \u00b7 QNA \u00b7 Saudi Exchange \u00b7 QSE \u00b7 EGX \u2014 all stories "
           "verified vs Sunday 22 Nov 2026; decided / forecast labelled; claims attributed.",
           font=f_src, fill=GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    img = render()
    img.save(out, format="PNG")
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
