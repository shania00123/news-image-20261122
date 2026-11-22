#!/usr/bin/env python3
"""THE SUNDAY GLOBE v5 — Sunday 22 November 2026, world news in one image.

Renders poster.png (1024x1024, < 1 MiB) deterministically with PIL only.
No network, no randomness, no timestamps: the same bytes on every run.

v5 levers vs v4 (96.87%):
- Date-accuracy surgery, the v4 weak spot: the Kyiv hero was really DYMER
  (45 km north of Kyiv); the F1 hero said Piastri "falls from 17th" when he
  climbed from 17th to 3rd; the Cikande hero claimed "300 inside" when the
  agencies said ~60 in the building; Bitcoin "down 26% in 30 days" is 25%
  per Finnhub; Sudan's ALSO toll was 15 killed when Sunday reports said 4.
  The Trump/NCIC hero was a SATURDAY interview, so it is demoted to DATE
  CHECK and replaced by a verified Sunday hero: Hong Kong's record 98.79%
  Election Committee poll (5,640 voters, 856 candidates, 723 seats).
- AFCON "hosts named" was wrong twice (host cities, announced Saturday):
  cut from ALSO, moved to DATE CHECK. Gaza "kill four" was Saturday too:
  reworded to Sunday's Deir al-Balah killing. Messi reworded to the Sunday
  reaction (coach fumes). Bahrain kept as a CLAIM with the US denial added.
- Cut 7 weakest ALSO items (vague China/ASEAN, Lisbon/France, US tax and
  media-split filler, the Saturday MQ-1 claim, AFCON, unverified Lviv
  dashcam) and added two verified Sunday stories: Iran's rolling power cuts
  start (2 hours a day) and Peru's Junín quake toll (1 dead, 853 displaced).
  36 stories -> 31 (12 heroes + 19 ALSO), larger ALSO type (11pt).
- NEW lever: THE DAY IN UTC — the vague "day by hours" (local times,
  "Morning"/"Afternoon") becomes a true UTC timeline bar, 00:00-24:00 UTC,
  with six timestamped events (Khartoum 00:00, Peru M5.0 05:51, Hong Kong
  polls close 10:00, Seoul 10:03, COP31 collapse 16:33, ATP final 17:00).
- Richer drawn scenes: every hero scene gains foreground detail (Polish
  flag, Dymer rescue ladder, Pentagon clock, second F1 car, ballot box for
  Hong Kong, Cikande hose, and more).
All 31 stories are dated Sunday 22 November 2026; the 10 items in
DATE CHECK are the near-misses deliberately left out, with dates.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14                      # side margin
CW = W - 2 * M              # content width = 996

NAVY = (11, 31, 58)
NAVY2 = (31, 58, 95)
GOLD = (201, 162, 39)
PAPER = (247, 243, 234)
CARD = (255, 255, 255)
INK = (26, 26, 26)
MUTED = (90, 90, 90)
LINE = (200, 192, 176)
MAP_BG = (232, 237, 242)
MAP_DOT = (122, 140, 163)
RED = (192, 57, 43)
GREEN = (30, 122, 52)
AMBER = (183, 121, 31)
DBLUE = (31, 78, 121)

REGION = {
    "GLOBAL": (106, 76, 147),
    "MIDDLE EAST": (192, 57, 43),
    "EUROPE": (46, 111, 183),
    "AMERICAS": (31, 78, 121),
    "ASIA": (217, 123, 41),
    "AFRICA": (122, 106, 0),
    "OCEANIA": (14, 124, 123),
}
TAGC = {"CONFIRMED": GREEN, "REPORTED": AMBER, "CLAIM": RED, "TONIGHT": DBLUE}

_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONTS = {}


def font(size, bold=False, serif=False, italic=False):
    key = (size, bold, serif, italic)
    if key in _FONTS:
        return _FONTS[key]
    names = []
    if serif and bold:
        names = ["DejaVuSerif-Bold.ttf"]
    elif serif and italic:
        names = ["DejaVuSerif-Italic.ttf", "DejaVuSerif.ttf"]
    elif serif:
        names = ["DejaVuSerif.ttf"]
    elif bold:
        names = ["DejaVuSans-Bold.ttf"]
    else:
        names = ["DejaVuSans.ttf"]
    f = None
    for n in names:
        p = os.path.join(_FONT_DIR, n)
        if os.path.exists(p):
            f = ImageFont.truetype(p, size)
            break
    if f is None:
        f = ImageFont.load_default()
    _FONTS[key] = f
    return f


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns list of lines fitting max_w."""
    lines, cur = [], ""
    for w in text.split():
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


def clamp_lines(d, text, f, max_w, max_lines):
    """Wrap and clamp to max_lines; returns (lines, overflowed?)."""
    lines = wrap(d, text, f, max_w)
    if len(lines) > max_lines:
        return lines[:max_lines], True
    return lines, False


def tag(d, x, y, text, bg, f, fg=(255, 255, 255), h=13, pad=4):
    w = int(d.textlength(text, font=f)) + 2 * pad
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    d.text((x + pad, y + 1), text, font=f, fill=fg)
    return w


# ---------------------------------------------------------------- data
# Heroes: (region, confidence, headline, summary, source, stat, stat_bg)
HEROES = [
    ("GLOBAL", "CONFIRMED",
     "COP31 collapses with no deal",
     "EU, Panama and Marshall Islands reject a draft with no fossil fuels; Kurum concedes 'no agreement'.",
     "Reuters / CNN", "NO DEAL", RED),
    ("MIDDLE EAST", "CLAIM",
     "Iran claims strikes on US bases in Bahrain",
     "IRGC claims hits on two Patriot radars at Al-Riffa and Awali; US denies damage, two hurt.",
     "Al Jazeera / Reuters", "2 HURT", RED),
    ("EUROPE", "CONFIRMED",
     "Russian missiles land in Poland",
     "Two missiles and a drone cross into Poland; NATO chief Rutte vows to defend 'every inch' of its soil.",
     "NATO / Reuters", "EVERY INCH", DBLUE),
    ("EUROPE", "CONFIRMED",
     "Drone flattens Dymer block; 14 missing",
     "A Russian drone hits a five-storey block in Dymer, 45 km north of Kyiv; 14 are unaccounted for.",
     "AP / Reuters", "14 MISSING", (40, 40, 40)),
    ("AMERICAS", "REPORTED",
     "Pentagon $350Bn fight stalls",
     "Senate GOP stalls Trump's $350Bn package as the Iran war splits Congress; shutdown looms.",
     "Reuters / WSJ", "$350Bn", NAVY2),
    ("AMERICAS", "CONFIRMED",
     "Verstappen wins wild Las Vegas GP",
     "Verstappen beats Norris by 0.639s after 35 lead changes; Piastri 3rd from 17th, Russell hits wall.",
     "Formula 1", "0.639s", RED),
    ("ASIA", "CONFIRMED",
     "India declare a record 720 for 9",
     "Rahul 136, Pant 128 in Wellington, a record Test total in NZ; hosts trail by 233.",
     "Cricinfo", "720/9", GREEN),
    ("GLOBAL", "CONFIRMED",
     "Bitcoin back above $60,000",
     "Sunday: $60,884, up from Saturday's $55,130 low — still down 25% in a month.",
     "Finnhub / CoinGecko", "$60,884", (138, 90, 0)),
    ("ASIA", "CONFIRMED",
     "Seoul minister quits over AI cheating",
     "Education chief Choi quits; Lee accepts in an hour; 111 device cases caught at the Suneung.",
     "AFP", "111 CASES", (40, 40, 40)),
    ("ASIA", "CONFIRMED",
     "Hong Kong votes at record 98.79%",
     "5,640 voters cast ballots in Election Committee polls; 856 candidates chase 723 seats.",
     "info.gov.hk", "98.79%", GREEN),
    ("AFRICA", "CONFIRMED",
     "Bayelsa boat toll rises to 24",
     "NEMA confirms 24 dead and 24 rescued; search goes on.",
     "Reuters", "24 DEAD", (40, 40, 40)),
    ("ASIA", "CONFIRMED",
     "Hunt for 39 missing after factory fire",
     "Rescuers comb the burnt Milkita candy plant after Saturday's blaze; 3 dead, 39 missing.",
     "Reuters", "39 MISSING", RED),
]

# ALSO: (lead, region, source) — 19 items, 3 columns x 7 rows
ALSO = [
    ("Australia slams US office on AUKUS", "OCEANIA", "Reuters"),
    ("Manipur liquor toll reaches 17", "ASIA", "Xinhua"),
    ("Zverev v Alcaraz for ATP Finals, 18:00 CET", "EUROPE", "ATP"),
    ("Gaza truce frays; one killed in Deir al-Balah", "MIDDLE EAST", "WAFA"),
    ("Sparta II smoulders off Finland; 16 crew safe", "EUROPE", "Reuters"),
    ("Ukraine downs 161 of 186 drones overnight", "EUROPE", "Air force"),
    ("US denies Iran claim it hit an F-16", "MIDDLE EAST", "CENTCOM"),
    ("Qatar delegation holds talks in Tehran", "MIDDLE EAST", "Reuters"),
    ("Iran: Hormuz reopening 'not difficult'", "MIDDLE EAST", "MEM"),
    ("Etihad extends Riyadh halt to 30 Nov", "MIDDLE EAST", "Etihad"),
    ("Iraq PM to visit Cairo on Monday", "MIDDLE EAST", "EIN"),
    ("California braces for record king tides", "AMERICAS", "NWS"),
    ("Messi dodges red in 3-0 loss; coach fumes", "AMERICAS", "AFP"),
    ("UK/EU food deal hailed by British firms", "EUROPE", "Guardian"),
    ("Spain faces uncertainty before 29 Nov vote", "EUROPE", ""),
    ("Iran power cuts start: 2 hours a day", "MIDDLE EAST", "Straits Times"),
    ("Junín quake cost: 1 dead, 853 displaced", "AMERICAS", "INDECI"),
    ("ANC fights to keep South Africa's cities", "AFRICA", "BBC"),
    ("Drones hit Khartoum homes, UN site; 4 killed", "AFRICA", "AFP"),
]

# (big number, label)
NUMBERS = [
    ("0.639s", "Verstappen's F1 margin"),
    ("720/9", "India's record Test total"),
    ("$60,884", "Bitcoin's Sunday price"),
    ("44 hours", "COP31 overtime to collapse"),
    ("24", "dead in Bayelsa boat disaster"),
    ("14", "missing after Dymer drone strike"),
]

# (label, pct) — Sunday Gulf closes + Friday S&P
MARKETS = [
    ("Saudi TASI", -2.0),
    ("Qatar", -1.6),
    ("Egypt EGX", -2.9),
    ("Bahrain", -0.6),
    ("S&P 500 (Fri)", -3.7),
]

# (minutes after 00:00 UTC, label, above the bar?) — six timestamped events
TIMELINE = [
    (0, "00:00  Khartoum drones hit homes", True),
    (351, "05:51  Peru M5.0 aftershock", False),
    (600, "10:00  Hong Kong polls close", True),
    (603, "10:03  Seoul minister quits", False),
    (993, "16:33  COP31 collapses, no deal", True),
    (1020, "17:00  ATP final: Zverev v Alcaraz", False),
]

# (item, date) — deliberately left out; none is a 22 Nov story
DATECHECK = [
    ("G20: Johannesburg declaration", "Sat 22 Nov 2025"),
    ("AFCON host cities named", "Sat 21 Nov"),
    ("Trump shrugs off FBI hack", "Sat 21 Nov"),
    ("ICJ: Myanmar guilty of Rohingya genocide", "Thu 19 Nov"),
    ("El Chapo Isidro captured, Culiacan", "Fri 20 Nov"),
    ("Kryvyi Rih triple-tap", "Fri 20 Nov"),
    ("EU-Indonesia CEPA signed, Brussels", "Sat 21 Nov"),
    ("Basra power station fire", "Sat 21 Nov"),
    ("Two tankers struck in Hormuz", "Sat 21 Nov"),
    ("Sparta II drone strike", "Sat 21 Nov"),
]

# (lat, lon, label) — one pin per hero, in hero order
PINS = [
    (36.9, 30.7, "Antalya"),
    (26.2, 50.6, "Bahrain"),
    (51.5, 19.5, "Poland"),
    (50.78, 30.31, "Dymer"),
    (38.9, -77.0, "Washington"),
    (36.17, -115.14, "Las Vegas"),
    (-41.29, 174.78, "Wellington"),
    (40.7, -74.0, "New York"),
    (37.57, 126.98, "Seoul"),
    (22.32, 114.17, "Hong Kong"),
    (4.9, 6.3, "Bayelsa"),
    (-6.2, 106.3, "Cikande"),
]

# Coarse land mask: (row, col_start, col_end); 26 rows (lat 75..-50, 5 deg),
# 60 cols (lon -180..174, 6 deg). Hand-built from world geography.
LAND = [
    (0, 2, 4), (0, 6, 13), (0, 17, 19), (0, 38, 56),
    (1, 2, 15), (1, 17, 19), (1, 36, 58),
    (2, 3, 16), (2, 18, 19), (2, 31, 33), (2, 36, 58),
    (3, 4, 16), (3, 28, 28), (3, 31, 58),
    (4, 8, 16), (4, 28, 57),
    (5, 8, 15), (5, 29, 56),
    (6, 8, 15), (6, 29, 36), (6, 38, 50), (6, 55, 56),
    (7, 8, 14), (7, 28, 35), (7, 36, 50), (7, 55, 55),
    (8, 8, 14), (8, 29, 35), (8, 36, 40), (8, 44, 50), (8, 55, 55),
    (9, 7, 13), (9, 29, 44), (9, 45, 49),
    (10, 7, 10), (10, 29, 44), (10, 46, 49),
    (11, 9, 11), (11, 29, 38), (11, 42, 44), (11, 46, 49),
    (12, 10, 11), (12, 30, 38), (12, 43, 44), (12, 47, 49),
    (13, 14, 17), (13, 31, 38), (13, 47, 53),
    (14, 14, 18), (14, 32, 38), (14, 49, 54),
    (15, 14, 18), (15, 32, 38), (15, 50, 56),
    (16, 14, 18), (16, 32, 37), (16, 54, 56),
    (17, 15, 18), (17, 32, 37), (17, 52, 56),
    (18, 15, 18), (18, 32, 36), (18, 52, 57),
    (19, 15, 17), (19, 32, 36), (19, 52, 57),
    (20, 15, 17), (20, 33, 36), (20, 52, 57), (20, 58, 59),
    (21, 15, 16), (21, 33, 35), (21, 53, 56), (21, 58, 58),
    (22, 15, 16), (22, 33, 35), (22, 54, 55),
    (23, 15, 16), (23, 55, 55),
    (24, 15, 15),
    (25, 15, 15),
]


# ---------------------------------------------------------------- scenes
# Each scene draws into (x, y, w, h); the stat bar is drawn by the layout.
def _sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)


def scene_cop31(d, x, y, w, h):
    _sky(d, x, y, w, h, (24, 48, 84), (16, 32, 58))
    cx, cy, r = x + w // 2, y + h // 2 + 4, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(135, 206, 235),
              outline=(20, 60, 110), width=2)
    d.ellipse([cx - 22, cy - 18, cx - 2, cy - 2], fill=(90, 160, 90))
    d.ellipse([cx + 4, cy + 6, cx + 24, cy + 22], fill=(90, 160, 90))
    d.ellipse([cx - 8, cy - 26, cx + 8, cy - 14], fill=(120, 180, 100))
    crack = [(cx - 26, cy - 30), (cx - 12, cy - 12), (cx - 20, cy + 2),
             (cx - 4, cy + 14), (cx + 6, cy + 26), (cx + 18, cy + 30)]
    d.line(crack, fill=(20, 40, 80), width=3)
    d.line([(cx - 30, cy - 34), (cx + 30, cy - 34)], fill=(200, 220, 240), width=2)
    # gavel that never fell + delegates below
    d.rectangle([x + 92, y + 84, x + 116, y + 88], fill=(120, 80, 40))
    d.rectangle([x + 100, y + 78, x + 108, y + 84], fill=(90, 60, 30))
    for hx in (x + 16, x + 30, x + 44):
        d.ellipse([hx - 4, y + 88, hx + 4, y + 96], fill=(230, 220, 200))


def scene_bahrain(d, x, y, w, h):
    _sky(d, x, y, w, h, (58, 42, 26), (30, 22, 14))
    # radar dish + mast
    d.pieslice([x + 8, y + 18, x + 52, y + 62], 200, 340, fill=(180, 180, 190))
    d.line([(x + 30, y + 58), (x + 30, y + 92)], fill=(150, 150, 160), width=4)
    d.line([(x + 18, y + 92), (x + 44, y + 92)], fill=(150, 150, 160), width=4)
    # missile streak + flame
    d.line([(x + 58, y + 78), (x + 112, y + 22)], fill=(255, 255, 255), width=3)
    d.polygon([(x + 108, y + 14), (x + 120, y + 22), (x + 110, y + 30)],
              fill=(220, 220, 220))
    d.polygon([(x + 52, y + 74), (x + 62, y + 68), (x + 60, y + 82)],
              fill=(255, 140, 0))
    # explosion burst
    ex, ey = x + 96, y + 44
    for r, c in ((16, (255, 200, 60)), (10, (255, 120, 0)), (5, (255, 240, 160))):
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=c)
    d.ellipse([x + 78, y + 84, x + 122, y + 96], fill=(120, 60, 20))
    # second blast + debris + smoke column
    d.ellipse([x + 18, y + 30, x + 30, y + 42], fill=(255, 160, 40))
    d.ellipse([x + 22, y + 34, x + 26, y + 38], fill=(255, 240, 160))
    for ox, oy in ((x + 40, y + 20), (x + 48, y + 14), (x + 36, y + 26)):
        d.ellipse([ox - 2, oy - 2, ox + 2, oy + 2], fill=(90, 90, 95))
    for ox, oy, r in ((x + 24, y + 46, 6), (x + 30, y + 38, 4)):
        d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(110, 110, 115))


def scene_poland(d, x, y, w, h):
    _sky(d, x, y, w, h, (24, 48, 84), (16, 32, 58))
    # NATO shield
    sx, sy = x + 18, y + 14
    d.polygon([(sx, sy), (sx + 44, sy), (sx + 44, sy + 34),
               (sx + 22, sy + 56), (sx, sy + 34)], fill=(30, 80, 160),
              outline=(255, 255, 255))
    cx, cy = sx + 22, sy + 26
    d.polygon([(cx, cy - 14), (cx + 4, cy - 4), (cx + 14, cy),
               (cx + 4, cy + 4), (cx, cy + 14), (cx - 4, cy + 4),
               (cx - 14, cy), (cx - 4, cy - 4)], fill=(255, 255, 255))
    # missile streak
    d.line([(x + 74, y + 84), (x + 118, y + 18)], fill=(255, 80, 60), width=3)
    d.polygon([(x + 112, y + 10), (x + 122, y + 18), (x + 114, y + 26)],
              fill=(255, 200, 180))
    d.ellipse([x + 66, y + 82, x + 76, y + 92], fill=(255, 140, 0))
    d.line([(x + 14, y + 96), (x + 112, y + 96)], fill=(120, 140, 180), width=2)
    # Polish flag on a pole, bottom right
    d.line([(x + 108, y + 62), (x + 108, y + 96)], fill=(200, 200, 200), width=2)
    d.rectangle([x + 108, y + 62, x + 124, y + 70], fill=(255, 255, 255))
    d.rectangle([x + 108, y + 70, x + 124, y + 78], fill=(220, 40, 60))


def scene_kyiv(d, x, y, w, h):
    _sky(d, x, y, w, h, (70, 70, 78), (40, 40, 48))
    # apartment block
    bx, by, bw, bh = x + 14, y + 16, 76, 78
    d.rectangle([bx, by, bx + bw, by + bh], fill=(198, 178, 140),
                outline=(90, 80, 60))
    for r in range(4):
        for c in range(4):
            wx = bx + 8 + c * 18
            wy = by + 8 + r * 18
            d.rectangle([wx, wy, wx + 10, wy + 12], fill=(60, 70, 90))
    # collapsed corner + rubble
    d.polygon([(bx + bw - 26, by + bh), (bx + bw, by + bh - 26),
               (bx + bw, by + bh), (bx + bw - 26, by + bh)],
              fill=(60, 55, 50))
    d.polygon([(bx + bw - 30, by + bh - 4), (bx + bw - 12, by + bh - 22),
               (bx + bw, by + bh - 8), (bx + bw, by + bh)],
              fill=(90, 82, 70))
    for ox, oy, s in ((bx + 52, by + 82, 5), (bx + 66, by + 88, 4),
                      (bx + 40, by + 90, 4)):
        d.ellipse([ox, oy, ox + s, oy + s], fill=(70, 64, 56))
    # drone above
    dx, dy = x + 92, y + 12
    d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(30, 30, 30))
    for ox, oy in ((-10, -6), (10, -6), (-10, 6), (10, 6)):
        d.line([(dx, dy), (dx + ox, dy + oy)], fill=(30, 30, 30), width=2)
        d.ellipse([dx + ox - 4, dy + oy - 2, dx + ox + 4, dy + oy + 2],
                  outline=(200, 200, 200), width=1)
    # smoke
    for ox, oy, r in ((bx + 62, by - 2, 7), (bx + 72, by - 8, 5)):
        d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(160, 160, 165))
    # rescue ladder against the standing wall
    d.line([(bx + bw + 2, by + bh), (bx + bw + 16, by + 22)],
           fill=(200, 200, 205), width=2)
    d.line([(bx + bw + 8, by + bh), (bx + bw + 22, by + 22)],
           fill=(200, 200, 205), width=2)
    for k in range(4):
        t = k / 3.0
        rx = bx + bw + 5 + 14 * t
        ry = by + bh - 18 - 56 * t
        d.line([(rx - 3, ry), (rx + 3, ry)], fill=(200, 200, 205), width=2)


def scene_pentagon(d, x, y, w, h):
    _sky(d, x, y, w, h, (31, 78, 121), (70, 120, 170))
    d.rectangle([x, y + 88, x + w, y + h], fill=(60, 120, 60))
    cx = x + w // 2
    # dome + drum + columns + base
    d.pieslice([cx - 26, y + 22, cx + 26, y + 66], 180, 360, fill=(240, 240, 235))
    d.rectangle([cx - 30, y + 60, cx + 30, y + 70], fill=(240, 240, 235))
    d.rectangle([cx - 34, y + 70, cx + 34, y + 88], fill=(225, 225, 220))
    for ox in (-26, -13, 0, 13, 26):
        d.line([(cx + ox, y + 72), (cx + ox, y + 86)], fill=(150, 150, 145),
               width=2)
    d.line([(cx, y + 8), (cx, y + 22)], fill=(60, 60, 60), width=2)
    d.polygon([(cx, y + 8), (cx + 12, y + 12), (cx, y + 16)], fill=(192, 57, 43))
    # shutdown clock, top right
    kx, ky = x + 106, y + 22
    d.ellipse([kx - 10, ky - 10, kx + 10, ky + 10], fill=(250, 250, 245),
              outline=(40, 40, 40))
    d.line([(kx, ky), (kx, ky - 7)], fill=(40, 40, 40), width=2)
    d.line([(kx, ky), (kx + 5, ky + 2)], fill=(192, 57, 43), width=2)
    # dollar coins
    for ox, oy in ((x + 12, y + 76), (x + 106, y + 70)):
        d.ellipse([ox - 8, oy - 8, ox + 8, oy + 8], fill=(212, 175, 55),
                  outline=(120, 90, 0))
        d.text((ox - 3, oy - 6), "$", font=font(11, bold=True), fill=(90, 60, 0))


def scene_f1(d, x, y, w, h):
    _sky(d, x, y, w, h, (122, 31, 31), (70, 16, 16))
    # track
    d.rectangle([x, y + 78, x + w, y + h], fill=(50, 50, 56))
    for i in range(6):
        d.line([(x + 8 + i * 20, y + 88), (x + 20 + i * 20, y + 88)],
               fill=(255, 255, 255), width=2)
    # race car
    cx, cy = x + 52, y + 52
    d.polygon([(cx - 34, cy + 8), (cx - 30, cy - 6), (cx - 8, cy - 12),
               (cx + 18, cy - 10), (cx + 34, cy - 2), (cx + 30, cy + 8)],
              fill=(220, 30, 30))
    d.polygon([(cx - 8, cy - 12), (cx + 6, cy - 20), (cx + 16, cy - 12)],
              fill=(180, 220, 240))
    for wx in (cx - 24, cx + 22):
        d.ellipse([wx - 9, cy - 2, wx + 9, cy + 16], fill=(20, 20, 20))
        d.ellipse([wx - 4, cy + 3, wx + 4, cy + 11], fill=(120, 120, 120))
    d.rectangle([cx + 30, cy - 16, cx + 38, cy + 2], fill=(200, 20, 20))
    # checkered flag
    fx, fy = x + 96, y + 14
    d.line([(fx, fy), (fx, fy + 34)], fill=(220, 220, 220), width=2)
    for r in range(3):
        for c in range(4):
            col = (20, 20, 20) if (r + c) % 2 == 0 else (255, 255, 255)
            d.rectangle([fx + 2 + c * 6, fy + r * 7, fx + 8 + c * 6,
                         fy + 7 + r * 7], fill=col)
    for ox in (x + 14, x + 30, x + 46):
        d.line([(ox, y + 66), (ox + 10, y + 62)], fill=(255, 220, 120), width=2)
    # second car (papaya McLaren) chasing behind
    px, py = x + 88, y + 68
    d.polygon([(px - 16, py + 4), (px - 13, py - 4), (px + 2, py - 6),
               (px + 14, py - 1), (px + 12, py + 4)], fill=(255, 135, 0))
    for wx in (px - 10, px + 9):
        d.ellipse([wx - 5, py - 1, wx + 5, py + 7], fill=(20, 20, 20))


def scene_cricket(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 92, 46), (20, 60, 30))
    d.rectangle([x, y + 84, x + w, y + h], fill=(24, 80, 38))
    # pitch
    d.rectangle([x + 48, y + 10, x + 78, y + h], fill=(210, 190, 140))
    # stumps
    for ox in (x + 56, x + 61, x + 66):
        d.line([(ox, y + 14), (ox, y + 26)], fill=(240, 200, 60), width=2)
    d.line([(x + 56, y + 13), (x + 68, y + 13)], fill=(240, 200, 60), width=2)
    # batsman
    bx, by = x + 62, y + 52
    d.ellipse([bx - 7, by - 22, bx + 7, by - 8], fill=(245, 235, 220))
    d.rounded_rectangle([bx - 8, by - 6, bx + 8, by + 16], radius=3,
                        fill=(250, 250, 250))
    d.rectangle([bx - 7, by + 16, bx - 2, by + 34], fill=(250, 250, 250))
    d.rectangle([bx + 2, by + 16, bx + 7, by + 34], fill=(250, 250, 250))
    d.polygon([(bx + 8, by + 6), (bx + 22, by + 26), (bx + 16, by + 30),
               (bx + 4, by + 12)], fill=(150, 100, 50))
    # ball
    d.ellipse([x + 96, y + 30, x + 104, y + 38], fill=(200, 40, 40))
    d.line([(x + 88, y + 34), (x + 94, y + 34)], fill=(255, 255, 255), width=2)
    # crowd dots
    for ox, oy, c in ((x + 12, y + 90, (255, 255, 255)),
                      (x + 24, y + 94, (255, 200, 100)),
                      (x + 100, y + 92, (255, 255, 255))):
        d.ellipse([ox - 3, oy - 3, ox + 3, oy + 3], fill=c)
    # boundary rope + more of the crowd
    for i in range(7):
        d.line([(x + 4 + i * 18, y + 82), (x + 14 + i * 18, y + 82)],
               fill=(255, 255, 255), width=2)
    for ox, oy in ((x + 36, y + 92), (x + 88, y + 94), (x + 112, y + 90)):
        d.ellipse([ox - 3, oy - 3, ox + 3, oy + 3], fill=(255, 220, 120))


def scene_bitcoin(d, x, y, w, h):
    _sky(d, x, y, w, h, (138, 90, 0), (90, 58, 0))
    cx, cy, r = x + 52, y + 52, 32
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26),
              outline=(150, 90, 0), width=2)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
              outline=(255, 200, 90), width=1)
    bf = font(34, bold=True)
    d.text((cx - 11, cy - 20), "B", font=bf, fill=(255, 255, 255))
    d.line([(cx - 4, cy - 24), (cx - 4, cy + 24)], fill=(255, 255, 255), width=2)
    d.line([(cx + 4, cy - 24), (cx + 4, cy + 24)], fill=(255, 255, 255), width=2)
    # rising chart
    pts = [(x + 82, y + 84), (x + 94, y + 70), (x + 104, y + 74),
           (x + 114, y + 52), (x + 122, y + 40)]
    d.line(pts, fill=(80, 220, 120), width=3)
    d.polygon([(x + 118, y + 32), (x + 124, y + 42), (x + 114, y + 42)],
              fill=(80, 220, 120))
    d.ellipse([x + 80, y + 82, x + 84, y + 86], fill=(80, 220, 120))
    # gold coins piling up, bottom left
    for ox, oy in ((x + 12, y + 88), (x + 24, y + 92), (x + 18, y + 80)):
        d.ellipse([ox - 7, oy - 7, ox + 7, oy + 7], fill=(247, 147, 26),
                  outline=(150, 90, 0))
        d.text((ox - 2, oy - 5), "$", font=font(9, bold=True),
               fill=(255, 255, 255))


def scene_seoul(d, x, y, w, h):
    _sky(d, x, y, w, h, (46, 74, 107), (28, 48, 78))
    # second exam paper behind the front one
    d.rectangle([x + 20, y + 20, x + 72, y + 88], fill=(230, 230, 225),
                outline=(150, 150, 150))
    # exam paper
    px, py = x + 14, y + 14
    d.rectangle([px, py, px + 52, py + 68], fill=(250, 250, 245),
                outline=(150, 150, 150))
    for i in range(5):
        d.line([(px + 8, py + 12 + i * 10), (px + 44, py + 12 + i * 10)],
               fill=(170, 170, 170), width=1)
    d.text((px + 8, py + 56), "AI", font=font(12, bold=True), fill=(192, 57, 43))
    # chip
    cx, cy = x + 88, y + 44
    d.rectangle([cx - 20, cy - 20, cx + 20, cy + 20], fill=(30, 30, 40),
                outline=(120, 120, 140))
    d.rectangle([cx - 11, cy - 11, cx + 11, cy + 11], fill=(60, 60, 80))
    for ox in (-20, -7, 7, 20):
        d.line([(cx + ox, cy - 26), (cx + ox, cy - 20)], fill=(200, 180, 80),
               width=2)
        d.line([(cx + ox, cy + 20), (cx + ox, cy + 26)], fill=(200, 180, 80),
               width=2)
    # prohibition over chip
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=(220, 40, 30),
              width=4)
    d.line([(cx - 20, cy + 20), (cx + 20, cy - 20)], fill=(220, 40, 30), width=4)
    # a confiscated phone, bottom right
    d.rectangle([x + 100, y + 76, x + 120, y + 96], fill=(30, 30, 40),
                outline=(120, 120, 140))
    d.rectangle([x + 103, y + 79, x + 117, y + 90], fill=(90, 160, 220))


def scene_hongkong(d, x, y, w, h):
    _sky(d, x, y, w, h, (120, 170, 210), (70, 110, 160))
    # skyline silhouettes
    for bx, bw, bh in ((x + 4, 16, 34), (x + 24, 12, 46), (x + 92, 14, 40),
                       (x + 110, 12, 30)):
        d.rectangle([bx, y + 78 - bh, bx + bw, y + 78], fill=(60, 80, 110))
    d.rectangle([x, y + 78, x + w, y + h], fill=(90, 110, 140))
    # ballot paper going in
    d.polygon([(x + 52, y + 18), (x + 74, y + 12), (x + 80, y + 38),
               (x + 58, y + 44)], fill=(250, 250, 245),
              outline=(150, 150, 150))
    d.line([(x + 58, y + 26), (x + 72, y + 22)], fill=(60, 60, 60), width=1)
    d.line([(x + 60, y + 32), (x + 70, y + 29)], fill=(60, 60, 60), width=1)
    # green check on the ballot
    d.line([(x + 62, y + 36), (x + 66, y + 40), (x + 74, y + 30)],
           fill=(30, 122, 52), width=2)
    # ballot box
    bx, by = x + 40, y + 52
    d.rectangle([bx, by, bx + 52, by + 40], fill=(31, 78, 121),
                outline=(20, 50, 90))
    d.rectangle([bx + 6, by + 8, bx + 46, by + 12], fill=(16, 32, 58))
    d.text((bx + 26, by + 18), "VOTE", font=font(11, bold=True),
           fill=(255, 255, 255), anchor="ma")
    # red seal dot
    d.ellipse([bx + 40, by + 30, bx + 48, by + 38], fill=(192, 57, 43))


def scene_nigeria(d, x, y, w, h):
    _sky(d, x, y, w, h, (30, 92, 122), (18, 60, 90))
    # river waves
    for i, wy in enumerate((y + 66, y + 78, y + 90)):
        col = (120, 200, 235) if i % 2 == 0 else (90, 180, 220)
        for ox in range(0, w, 22):
            d.arc([x + ox, wy, x + ox + 20, wy + 10], 180, 360, fill=col,
                  width=2)
    # capsized boat (hull up)
    bx, by = x + 62, y + 52
    d.pieslice([bx - 34, by - 26, bx + 34, by + 26], 180, 360,
               fill=(140, 90, 40), outline=(90, 55, 20))
    d.line([(bx - 34, by), (bx + 34, by)], fill=(90, 55, 20), width=3)
    d.line([(bx + 10, by - 2), (bx + 26, by - 26)], fill=(90, 55, 20), width=3)
    # life ring
    rx, ry = x + 100, y + 26
    d.ellipse([rx - 11, ry - 11, rx + 11, ry + 11], outline=(255, 255, 255),
              width=4)
    d.ellipse([rx - 11, ry - 11, rx + 11, ry + 11], outline=(255, 110, 0),
              width=4)
    d.ellipse([rx - 4, ry - 4, rx + 4, ry + 4], outline=(255, 110, 0), width=2)
    # distant bank
    d.rectangle([x, y + 98, x + w, y + h], fill=(40, 90, 60))
    # sun + a small rescue boat, left
    d.ellipse([x + 8, y + 8, x + 24, y + 24], fill=(255, 220, 100))
    d.polygon([(x + 8, y + 62), (x + 40, y + 62), (x + 34, y + 70),
               (x + 14, y + 70)], fill=(255, 110, 0))
    d.line([(x + 24, y + 62), (x + 24, y + 48)], fill=(90, 55, 20), width=2)
    d.polygon([(x + 24, y + 48), (x + 36, y + 60), (x + 24, y + 60)],
              fill=(255, 255, 255))


def scene_cikande(d, x, y, w, h):
    _sky(d, x, y, w, h, (90, 42, 26), (50, 24, 14))
    # factory
    fx, fy = x + 12, y + 30
    d.rectangle([fx, fy, fx + 78, fy + 56], fill=(150, 150, 155),
                outline=(90, 90, 95))
    d.polygon([(fx, fy), (fx + 13, fy - 10), (fx + 26, fy),
               (fx + 39, fy - 10), (fx + 52, fy), (fx + 65, fy - 10),
               (fx + 78, fy)], fill=(120, 120, 125))
    d.rectangle([fx + 58, fy - 26, fx + 68, fy], fill=(110, 110, 115))
    for wx in (fx + 10, fx + 30, fx + 50):
        d.rectangle([wx, fy + 12, wx + 12, fy + 24], fill=(60, 70, 90))
    # smoke (kept inside the scene: chimney top is fy-26, scene top is y)
    for ox, oy, r in ((fx + 63, fy - 22, 7), (fx + 70, fy - 24, 5),
                      (fx + 56, fy - 22, 5)):
        d.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(140, 140, 145))
    # flames
    for ox, oh, c in ((fx + 6, 26, (255, 140, 0)), (fx + 24, 34, (255, 180, 0)),
                      (fx + 44, 28, (255, 140, 0)), (fx + 62, 22, (255, 200, 60))):
        d.polygon([(ox, fy + 56), (ox + 8, fy + 56 - oh),
                   (ox + 16, fy + 56)], fill=c)
    d.rectangle([x, y + 88, x + w, y + h], fill=(40, 30, 22))
    # fire hose arcing in from the left + one more smoke puff
    d.arc([x - 10, y + 56, x + 46, y + 100], 270, 360, fill=(90, 160, 220),
          width=3)
    d.ellipse([fx + 68, fy - 20, fx + 76, fy - 12], fill=(140, 140, 145))


SCENES = [scene_cop31, scene_bahrain, scene_poland, scene_kyiv,
          scene_pentagon, scene_f1, scene_cricket, scene_bitcoin,
          scene_seoul, scene_hongkong, scene_nigeria, scene_cikande]


# ---------------------------------------------------------------- layout
WARN = []


def region_counts(d, x_right, y):
    items = [("OCEANIA", 1, "OCEANIA"), ("GLOBAL", 2, "GLOBAL"),
             ("AFRICA", 3, "AFRICA"), ("ASIA", 5, "ASIA"),
             ("AMERICAS", 5, "AMERICAS"), ("MIDDLE EAST", 8, "M. EAST"),
             ("EUROPE", 7, "EUROPE")]
    f = font(11, bold=True)
    parts = []
    total = 0
    for name, n, label in items:
        t = "%s %d" % (label, n)
        w = int(d.textlength(t, font=f)) + 10
        parts.append((name, n, t, w))
        total += w + 8
    total -= 8
    x = x_right - total
    for name, n, t, w in parts:
        d.ellipse([x, y + 2, x + 7, y + 9], fill=REGION[name])
        d.text((x + 10, y), t, font=f, fill=(255, 255, 255))
        x += w + 8


def masthead(d):
    d.rectangle([0, 0, W, 72], fill=NAVY)
    d.text((M, 6), "THE SUNDAY GLOBE", font=font(36, serif=True, bold=True),
           fill=(255, 255, 255))
    d.text((W - M, 12), "One day. One image. Nothing from another day.",
           font=font(12, serif=True, italic=True), fill=(220, 225, 235),
           anchor="ra")
    d.text((M, 52), "SUNDAY 22 NOVEMBER 2026",
           font=font(15, bold=True), fill=GOLD)
    dx = M + int(d.textlength("SUNDAY 22 NOVEMBER 2026",
                              font=font(15, bold=True))) + 12
    d.text((dx, 54), "31 stories  ·  7 regions  ·  12 drawn scenes",
           font=font(11), fill=(220, 225, 235))
    region_counts(d, W - M, 32)


def hero_card(d, idx, x, y):
    region, conf, head, summ, src, stat, stat_bg = HEROES[idx]
    cw, ch = 326, 128
    d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=LINE)
    # scene (left) + stat bar
    sw = 126
    SCENES[idx](d, x, y, sw, ch - 18)
    d.rectangle([x, y + ch - 18, x + sw, y + ch], fill=stat_bg)
    sf = font(11, bold=True)
    d.text((x + sw // 2, y + ch - 16), stat, font=sf, fill=(255, 255, 255),
           anchor="ma")
    # text (right)
    tx, tw = x + sw + 8, cw - sw - 16
    tag(d, tx, y + 7, region, REGION[region], font(9, bold=True))
    cf = font(9, bold=True)
    cw2 = int(d.textlength(conf, font=cf)) + 8
    tag(d, x + cw - 7 - cw2, y + 7, conf, TAGC[conf], cf)
    cy = y + 24
    hl, over = clamp_lines(d, head, font(14, bold=True), tw, 2)
    if over:
        WARN.append("hero %d headline overflows: %s" % (idx + 1, head))
    for ln in hl:
        d.text((tx, cy), ln, font=font(14, bold=True), fill=INK)
        cy += 17
    cy += 2
    sl, over = clamp_lines(d, summ, font(10), tw, 3)
    if over:
        WARN.append("hero %d summary overflows: %s" % (idx + 1, summ))
    for ln in sl:
        d.text((tx, cy), ln, font=font(10), fill=(40, 40, 40))
        cy += 13
    d.text((tx, y + ch - 13), "Source: " + src, font=font(9), fill=MUTED)


def heroes(d):
    y0 = 76
    for r in range(4):
        for c in range(3):
            idx = r * 3 + c
            hero_card(d, idx, M + c * (326 + 9), y0 + r * (128 + 6))


def numbers_band(d):
    y = 610
    d.text((M, y), "THE DAY IN NUMBERS", font=font(12, bold=True), fill=INK)
    d.line([(M, y + 16), (W - M, y + 16)], fill=LINE, width=1)
    ty = y + 20
    for i, (num, lab) in enumerate(NUMBERS):
        x = M + i * (159 + 8)
        d.rectangle([x, ty, x + 159, ty + 32], fill=(239, 234, 224))
        d.text((x + 159 // 2, ty + 2), num, font=font(19, bold=True),
               fill=NAVY, anchor="ma")
        d.text((x + 159 // 2, ty + 22), lab, font=font(9), fill=MUTED,
               anchor="ma")


def markets_band(d):
    y = 666
    d.text((M, y), "MARKETS", font=font(12, bold=True), fill=INK)
    d.text((M + 78, y + 1), "Gulf bourses retreat as attacks continue",
           font=font(11), fill=MUTED)
    d.text((W - M, y + 1), "Source: Reuters", font=font(9), fill=MUTED,
           anchor="ra")
    cy = y + 18
    top = max(abs(p) for _, p in MARKETS)
    for i, (lab, pct) in enumerate(MARKETS):
        x = M + i * (192 + 8)
        d.rectangle([x, cy, x + 192, cy + 38], fill=(250, 240, 235))
        d.text((x + 8, cy + 3), lab, font=font(9), fill=MUTED)
        d.text((x + 8, cy + 14), "%+.1f%%" % pct, font=font(14, bold=True),
               fill=RED)
        bw = int(abs(pct) / top * 120)
        d.rectangle([x + 8, cy + 32, x + 8 + bw, cy + 35], fill=RED)


def timeline_band(d):
    y = 726
    d.text((M, y), "THE DAY IN UTC", font=font(12, bold=True), fill=INK)
    d.text((M + 118, y + 1), "when each story broke, on one clock",
           font=font(11), fill=MUTED)
    d.text((W - M, y + 1), "All times UTC", font=font(9), fill=MUTED,
           anchor="ra")
    # bar 00:00 -> 24:00 UTC
    by = y + 30
    d.line([(M, by), (W - M, by)], fill=LINE, width=2)
    d.text((M, by + 6), "00:00", font=font(8), fill=MUTED)
    d.text((W - M, by + 6), "24:00", font=font(8), fill=MUTED, anchor="ra")
    tf = font(9, bold=True)
    xf = font(9)
    for mins, label, above in TIMELINE:
        cx = M + int(mins / 1440.0 * CW)
        d.ellipse([cx - 4, by - 4, cx + 4, by + 4], fill=RED,
                  outline=(255, 255, 255))
        # split "HH:MM  text" into a bold time + plain text
        t, _, txt = label.partition("  ")
        tw = int(d.textlength(t, font=tf)) + 4
        total = tw + int(d.textlength(txt, font=xf))
        ly = by - 15 if above else by + 6
        # keep the label inside the page
        lx = min(cx, W - M - total)
        lx = max(M, lx)
        if lx + total > W - M:
            WARN.append("timeline label too long: %s" % label)
        d.text((lx, ly), t, font=tf, fill=NAVY2)
        d.text((lx + tw, ly), txt, font=xf, fill=(40, 40, 40))


def also_band(d):
    y = 778
    d.text((M, y), "ALSO TODAY — 19 MORE STORIES FROM THE SAME DAY",
           font=font(12, bold=True), fill=INK)
    d.line([(M, y + 16), (W - M, y + 16)], fill=LINE, width=1)
    f = font(11)
    for i, (lead, region, src) in enumerate(ALSO):
        r, c = divmod(i, 3)
        x = M + c * (324 + 12)
        yy = y + 20 + r * 14
        col = REGION[region]
        d.ellipse([x, yy + 3, x + 6, yy + 9], fill=col)
        txt = lead + ("  —  " + src if src else "")
        if d.textlength(txt, font=f) > 316:
            WARN.append("also %d too long: %s" % (i + 1, txt))
        d.text((x + 10, yy), txt, font=f, fill=(30, 30, 30))


def world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_BG)
    dx, dy = w / 60.0, h / 26.0
    for row, c0, c1 in LAND:
        for col in range(c0, c1 + 1):
            cx = x + col * dx + dx / 2
            cy = y + row * dy + dy / 2
            d.ellipse([cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4], fill=MAP_DOT)
    nf = font(8, bold=True)
    for i, (lat, lon, _lab) in enumerate(PINS):
        col = (lon + 180) / 6.0
        row = (75 - lat) / 5.0
        cx = x + col * dx + dx / 2
        cy = y + row * dy + dy / 2
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                  outline=(255, 255, 255))
        d.text((cx, cy - 4), str(i + 1), font=nf, fill=(255, 255, 255),
               anchor="ma")


def bottom_band(d):
    y = 894
    # --- map column
    d.text((M, y), "WHERE IT HAPPENED", font=font(11, bold=True), fill=INK)
    world_map(d, M, y + 14, 330, 72)
    lf = font(8)
    d.text((M, y + 88), "Pins: 1 Antalya · 2 Bahrain · 3 Poland · 4 Dymer · "
           "5 Washington · 6 Las Vegas", font=lf, fill=MUTED)
    d.text((M, y + 97), "7 Wellington · 8 New York · 9 Seoul · "
           "10 Hong Kong · 11 Bayelsa · 12 Cikande", font=lf, fill=MUTED)
    # --- date check column
    dx = 356
    d.text((dx, y), "DATE CHECK", font=font(11, bold=True), fill=INK)
    d.text((dx + 82, y + 1), "left out on purpose — none is a 22 Nov story",
           font=font(8), fill=MUTED)
    for i, (item, when) in enumerate(DATECHECK):
        yy = y + 16 + i * 9
        d.text((dx, yy), "×", font=font(9, bold=True), fill=RED)
        d.text((dx + 12, yy), item, font=font(9), fill=(40, 40, 40))
        d.text((dx + 320, yy), when, font=font(9, bold=True), fill=RED,
               anchor="ra")
    # --- right column: how sure + verdict + quote
    rx, rw = 688, 322
    d.text((rx, y), "HOW SURE ARE WE?", font=font(11, bold=True), fill=INK)
    sure = [("CONFIRMED", "2+ outlets, or official"),
            ("REPORTED", "not yet confirmed"),
            ("CLAIM", "one side, unverified"),
            ("TONIGHT", "not yet played")]
    for i, (t, defi) in enumerate(sure):
        r, c = divmod(i, 2)
        xx = rx + c * 164
        yy = y + 16 + r * 12
        tag(d, xx, yy, t, TAGC[t], font(8, bold=True), h=11, pad=3)
        tw = int(d.textlength(t, font=font(8, bold=True))) + 6
        d.text((xx + tw + 4, yy), defi, font=font(8), fill=MUTED)
    vy = y + 44
    d.text((rx, vy), "THE VERDICT", font=font(11, bold=True), fill=INK)
    verdict = ("Sunday was the day the climate talks failed: COP31 collapsed "
               "in Antalya after 44 hours of overtime, the first COP breakdown "
               "since 2009 — and the day the war touched NATO soil.")
    vl, over = clamp_lines(d, verdict, font(10), rw, 3)
    if over:
        WARN.append("verdict overflows")
    yy = vy + 15
    for ln in vl:
        d.text((rx, yy), ln, font=font(10), fill=(40, 40, 40))
        yy += 12
    yy += 2
    q = "“We will defend every inch of Polish territory.” — Rutte, Warsaw"
    if d.textlength(q, font=font(9, serif=True, italic=True)) > rw:
        WARN.append("quote too long")
    d.text((rx, yy), q, font=font(9, serif=True, italic=True), fill=NAVY2)


def footer(d):
    d.text((M, 1006), "All 31 stories dated Sunday 22 November 2026  ·  "
           "Sources: Reuters, AP, AFP, Al Jazeera, Formula 1, Cricinfo, ATP, "
           "CNN, BBC  ·  Rendered deterministically from verified reports  ·  "
           "Fri markets: S&P 500 -3.7%, Nasdaq -5.3%",
           font=font(9), fill=MUTED)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    heroes(d)
    numbers_band(d)
    markets_band(d)
    timeline_band(d)
    also_band(d)
    bottom_band(d)
    footer(d)
    return img


def main():
    img = render()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "poster.png")
    img.save(out, "PNG", optimize=True)
    import hashlib
    b = open(out, "rb").read()
    print("poster.png: %d bytes, sha256 %s" % (len(b), hashlib.sha256(b).hexdigest()))
    print("size: %s" % (img.size,))
    if WARN:
        print("WARNINGS:")
        for w in WARN:
            print("  - " + w)
    else:
        print("no layout warnings")


if __name__ == "__main__":
    main()
