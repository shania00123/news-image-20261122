#!/usr/bin/env python3
"""RIVAL3 — news-image-20261122, LAWAN-ADU round 3.

A front-page newspaper for Sunday 22 November 2026: 40 verified Sunday
stories, 21 illustrated cards, a proper MARKETS band, a journalistic COP31
plenary hero, a neater dotted world map with 21 numbered pins, and a DATE
CHECK box catching wrong-day items other entries list as Sunday.

Deterministic, PIL only, no network. Written from scratch for this round:
the poster was studied visually (rival2 + top-3 leaderboard posters);
no other version's source code was read.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER   = (247, 243, 232)
PAPER2  = (238, 232, 216)
INK     = (17, 17, 17)
MUTED   = (90, 86, 76)
NAVY    = (18, 35, 63)
NAVY2   = (28, 52, 88)
RED     = (176, 30, 36)
RED_DK  = (140, 20, 26)
GOLD    = (201, 162, 39)
GOLD_LT = (232, 200, 110)
TEAL    = (18, 74, 74)
RULE    = (17, 17, 17)
HAIR    = (150, 144, 128)
CARD_BG = (255, 255, 255)
MAP_DOT = (138, 143, 152)
GREEN   = (27, 94, 52)
ORANGE  = (214, 90, 20)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF   = lambda s: font("DejaVuSerif.ttf", s)
F_SANS_B  = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS    = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines fitting width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, width, fill=INK, leading=None, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def hline(draw, x0, x1, y, fill=INK, w=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


def vline(draw, x, y0, y1, fill=INK, w=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=w)


def chip(draw, x, y, text, fnt, fg, bg):
    tw = draw.textlength(text, font=fnt)
    pad = 5
    draw.rounded_rectangle([x, y, x + tw + pad * 2, y + fnt.size + 7],
                           radius=2, fill=bg)
    draw.text((x + pad, y + 3), text, font=fnt, fill=fg)
    return x + tw + pad * 2


# ---------------------------------------------------------------- dot map
# Simplified continent polygons (lon, lat). Union rasterised into dots.
POLYS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 69), (-85, 66), (-75, 62),
     (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35), (-80, 26),
     (-90, 21), (-97, 16), (-105, 20), (-110, 23), (-117, 33), (-125, 40),
     (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-20, 70), (-35, 76), (-55, 76),
     (-60, 70)],
    # South America
    [(-79, 9), (-62, 10), (-52, 5), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-57, -38), (-65, -45), (-70, -54), (-73, -40), (-72, -20),
     (-77, -12), (-81, -5), (-80, 2)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 66), (20, 70),
     (15, 70), (12, 65), (5, 60), (-5, 58), (-10, 52), (-10, 43)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -28),
     (26, -34), (19, -35), (15, -27), (12, -18), (13, -10), (9, 4),
     (-8, 5), (-15, 11)],
    # Asia
    [(30, 62), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (160, 70), (178, 66), (170, 60), (162, 55), (156, 50), (142, 45),
     (140, 38), (130, 33), (127, 35), (122, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (98, 15), (95, 16), (92, 21), (88, 22), (80, 15),
     (77, 8), (75, 12), (72, 20), (66, 25), (60, 25), (56, 27), (52, 28),
     (48, 30), (44, 29), (40, 31), (36, 36), (30, 36), (27, 40), (28, 45),
     (30, 50), (32, 55), (30, 60)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -11), (126, -14), (122, -17), (118, -20)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -3), (135, -2), (140, -4), (141, -8), (138, -9),
     (130, -8), (122, -11), (115, -10), (108, -8), (102, -4), (97, 2)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (143, 43), (145, 44), (142, 45), (140, 42), (138, 38),
     (136, 35), (133, 34), (131, 32)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (176, -37), (178, -38), (175, -40),
     (172, -43), (168, -46)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (46, -24), (44, -22),
     (43, -18)],
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(_in_poly(lon, lat, p) for p in POLYS)


# lon/lat of the 21 pinned stories (+ manual de-conflict offsets in px)
PINS = [
    (1, 30.7, 36.9, 0, 0),      # Antalya — COP31
    (2, 30.0, 50.8, 0, -11),    # Dymer / Kyiv — drones
    (3, 50.6, 26.2, 5, 5),      # Manama — Bahrain
    (4, 114.2, 22.3, 0, 9),     # Hong Kong
    (5, 174.8, -41.3, -7, 0),   # Wellington
    (6, -115.1, 36.2, 0, 0),    # Las Vegas
    (7, 127.0, 37.5, 7, -7),    # Seoul
    (8, 24.5, 59.5, -15, -11),  # Gulf of Finland — Sparta II
    (9, -47.9, -15.8, 0, 0),    # Brasilia
    (10, -98.5, 29.4, 7, 5),    # San Antonio
    (11, 106.3, -6.2, 9, 10),   # Cikande / Serang
    (12, 34.5, 31.5, -11, -6),  # Gaza
    (13, 6.3, 4.9, 0, 7),       # Bayelsa
    (14, 12.45, 41.9, -15, 10), # Vatican
    (15, 140.5, 37.8, 11, -2),  # Fukushima
    (16, 125.5, 6.0, -11, 8),   # Mindanao
    (17, 149.1, -35.3, 0, -5),  # Canberra
    (18, 7.7, 45.1, -17, -3),   # Turin
    (19, 21.0, 52.2, 11, 5),    # Warsaw
    (20, 24.7, 59.4, 13, -13),  # Tallinn
    (21, 77.2, 28.6, 0, -7),    # Delhi
]


def draw_map(draw, x0, y0, w, h):
    """Dotted world map + 21 numbered pins, all inside the frame."""
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 72.0, -55.0
    step_x, step_y = 8.0, 5.0
    r = 2
    lon = lon0 + step_x / 2
    while lon < lon1:
        lat = lat0 - step_y / 2
        while lat > lat1:
            if on_land(lon, lat):
                px = x0 + (lon - lon0) / (lon1 - lon0) * w
                py = y0 + (lat0 - lat) / (lat0 - lat1) * h
                draw.ellipse([px - r, py - r, px + r, py + r], fill=MAP_DOT)
            lat -= step_y
        lon += step_x
    fnum = F_SANS_B(8)
    for num, plon, plat, dx, dy in PINS:
        px = x0 + (plon - lon0) / (lon1 - lon0) * w
        py = y0 + (lat0 - plat) / (lat0 - lat1) * h
        px = min(max(px, x0 + 9), x0 + w - 9)
        py = min(max(py, y0 + 9), y0 + h - 9)
        # true-position dot
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        qx, qy = px + dx, py + dy
        qx = min(max(qx, x0 + 8), x0 + w - 8)
        qy = min(max(qy, y0 + 8), y0 + h - 8)
        if abs(dx) + abs(dy) > 3:
            draw.line([(px, py), (qx, qy)], fill=RED, width=1)
        draw.ellipse([qx - 8, qy - 8, qx + 8, qy + 8], fill=RED,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(num), font=fnum)
        draw.text((qx - tw / 2, qy - 5), str(num), font=fnum,
                  fill=(255, 255, 255))


# ---------------------------------------------------------------- scenes
def _flame(draw, cx, base, s, cols=((255, 200, 40), (240, 110, 20), (200, 40, 10))):
    for i, c in enumerate(cols):
        w = s * (1 - i * 0.28)
        h = s * (1.35 - i * 0.3)
        draw.polygon([(cx - w / 2, base), (cx - w / 4, base - h * 0.7),
                      (cx, base - h), (cx + w / 4, base - h * 0.7),
                      (cx + w / 2, base)], fill=c)


def _smoke(draw, cx, cy, s, col=(120, 120, 125)):
    for dx, dy, r in ((-s, 0, s * 0.55), (0, -s * 0.7, s * 0.7),
                     (s, -s * 0.2, s * 0.5), (s * 0.4, -s * 1.4, s * 0.6)):
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                     fill=col)


def hero_cop31(draw, x, y, w, h):
    """Antalya plenary: delegates at a long table, clock, NO DEAL stamp."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 48, 66))
    draw.rectangle([x, y, x + w, y + 26], fill=(32, 64, 84))
    # windows / hall lights
    for i in range(6):
        wx = x + 14 + i * 52
        draw.rectangle([wx, y + 8, wx + 34, y + 20], fill=(214, 186, 110))
    # wall panel
    draw.rectangle([x, y + 26, x + w, y + 52], fill=(20, 40, 56))
    # clock: 44h overtime (top-left, clear of the delegates)
    cx, cy = x + 30, y + 30
    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(247, 243, 232),
                 outline=(201, 162, 39), width=2)
    draw.line([(cx, cy), (cx, cy - 9)], fill=INK, width=2)
    draw.line([(cx, cy), (cx + 7, cy + 3)], fill=INK, width=2)
    fclock = F_SANS_B(9)
    draw.text((cx - 13, cy + 18), "44h", font=fclock, fill=(232, 200, 110))
    # delegates behind the table
    shirts = [(90, 60, 110), (176, 30, 36), (40, 90, 140), (201, 162, 39),
              (60, 120, 90), (140, 60, 60), (70, 70, 120), (180, 130, 60)]
    for i, c in enumerate(shirts):
        dx = x + 22 + i * 38
        draw.ellipse([dx - 7, y + 58, dx + 7, y + 72], fill=(232, 200, 170))
        draw.pieslice([dx - 11, y + 70, dx + 11, y + 92], 180, 360, fill=c)
    # long table
    draw.polygon([(x + 6, y + 88), (x + w - 6, y + 88), (x + w - 14, y + h - 14),
                  (x + 14, y + h - 14)], fill=(96, 62, 32))
    draw.polygon([(x + 6, y + 88), (x + w - 6, y + 88), (x + w - 10, y + 96),
                  (x + 10, y + 96)], fill=(120, 78, 40))
    # flags on the table
    for i, c in enumerate([(30, 60, 160), (200, 40, 50), (40, 110, 70)]):
        fx = x + 40 + i * 96
        draw.line([(fx, y + 96), (fx, y + 78)], fill=(220, 220, 220), width=1)
        draw.rectangle([fx, y + 78, fx + 22, y + 88], fill=c)
    # papers
    for i in range(4):
        px = x + 70 + i * 70
        draw.rectangle([px, y + 92, px + 26, y + 100], fill=(247, 243, 232))
    # NO DEAL stamp (small, top-right, inside the picture)
    stamp = Image.new("RGBA", (110, 36), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([3, 3, 107, 33], outline=(200, 30, 36, 255), width=3)
    sd.text((10, 7), "NO DEAL", font=F_SANS_B(19), fill=(200, 30, 36, 255))
    stamp = stamp.rotate(-12, expand=True, resample=Image.BICUBIC)
    draw._image.paste(stamp, (x + w - 126, y + 24), stamp)


def hero_kyiv(draw, x, y, w, h):
    """Night over Kyiv region: skyline, drones, fire at the Dymer block."""
    draw.rectangle([x, y, x + w, y + h], fill=(10, 16, 34))
    # stars (fixed)
    for sx, sy in [(18, 12), (60, 26), (120, 10), (180, 22), (240, 12),
                   (290, 28), (40, 44), (150, 34), (215, 40), (270, 14)]:
        draw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                     fill=(240, 240, 220))
    # moon
    draw.ellipse([x + w - 42, y + 8, x + w - 18, y + 32], fill=(235, 228, 200))
    # skyline
    base = y + h - 18
    heights = [46, 30, 58, 38, 66, 34, 50, 42, 60, 28]
    bx = x + 4
    for i, hh in enumerate(heights):
        bw = 28
        draw.rectangle([bx, base - hh, bx + bw, base], fill=(22, 30, 52))
        for wy in range(base - hh + 6, base - 6, 12):
            for wx in range(bx + 5, bx + bw - 4, 9):
                if (wx + wy) % 3 == 0:
                    draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 205, 90))
        bx += bw + 3
    # burning block (Dymer): shorter building, flame + smoke stay in frame
    fx = x + 150
    draw.rectangle([fx, base - 40, fx + 34, base], fill=(40, 34, 44))
    _flame(draw, fx + 17, base - 34, 16)
    _smoke(draw, fx + 17, base - 52, 5, (90, 90, 96))
    # searchlight beam (narrow)
    draw.polygon([(x + 30, base), (x + 38, base), (x + 100, y + 20),
                  (x + 88, y + 20)], fill=(190, 190, 165))
    # drones
    for dx, dy in [(90, 26), (205, 44), (255, 30)]:
        draw.line([(x + dx - 8, y + dy), (x + dx + 8, y + dy)], fill=(200, 200, 200),
                  width=2)
        draw.line([(x + dx, y + dy - 5), (x + dx, y + dy + 5)], fill=(200, 200, 200),
                  width=2)
        draw.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2],
                     fill=(255, 60, 50))


def hero_bahrain(draw, x, y, w, h):
    """Manama at dusk: Patriot radar left, burning plant right, sea below."""
    for i in range(h - 30):
        t = i / max(1, h - 30)
        r = int(70 + (180 - 70) * t)
        g = int(60 + (110 - 60) * t)
        b = int(110 + (60 - 110) * t)
        draw.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    # sun low
    draw.ellipse([x + w - 70, y + 18, x + w - 40, y + 48], fill=(240, 180, 90))
    # radar dish + launcher (left)
    draw.rectangle([x + 26, y + 78, x + 34, y + 104], fill=(60, 60, 66))
    draw.pieslice([x + 14, y + 52, x + 46, y + 84], 180, 360, fill=(225, 225, 225))
    draw.line([(x + 30, y + 62), (x + 30, y + 78)], fill=(225, 225, 225), width=3)
    draw.rectangle([x + 52, y + 94, x + 96, y + 106], fill=(80, 84, 70))
    for wx in range(58, 92, 10):
        draw.ellipse([wx, y + 90, wx + 5, y + 95], fill=(20, 20, 20))
    # missile trails
    draw.arc([x + 90, y + 10, x + 190, y + 70], 200, 330, fill=(255, 255, 255),
             width=2)
    draw.arc([x + 120, y + 4, x + 220, y + 64], 200, 330, fill=(255, 220, 150),
             width=2)
    # burning plant (right)
    px = x + w - 78
    draw.rectangle([px, y + 66, px + 58, y + 104], fill=(52, 48, 54))
    draw.rectangle([px + 8, y + 56, px + 14, y + 66], fill=(52, 48, 54))
    _flame(draw, px + 29, y + 62, 24)
    _smoke(draw, px + 29, y + 34, 11, (70, 70, 78))
    # sea
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(16, 42, 66))
    draw.line([(x, y + h - 16), (x + w, y + h - 16)], fill=(90, 140, 180), width=1)


def scene(draw, x, y, w, h, kind):
    """Small illustrated strip for a story card."""
    if kind == "ballot":
        draw.rectangle([x, y, x + w, y + h], fill=(150, 30, 36))
        draw.rectangle([x + w // 2 - 26, y + 12, x + w // 2 + 26, y + h - 6],
                       fill=(247, 243, 232))
        draw.rectangle([x + w // 2 - 14, y + 15, x + w // 2 + 14, y + 19],
                       fill=(17, 17, 17))
        draw.rectangle([x + 12, y + 4, x + 34, y + 16], fill=(255, 255, 255))
        draw.text((x + 16, y + 5), "✓", font=F_SANS_B(10), fill=RED)
    elif kind == "cricket":
        draw.rectangle([x, y, x + w, y + h], fill=(46, 125, 60))
        draw.rectangle([x, y + h - 12, x + w, y + h], fill=(120, 90, 50))
        draw.line([(x + 40, y + 8), (x + 78, y + h - 12)], fill=(222, 184, 120),
                  width=6)
        draw.ellipse([x + w - 34, y + 8, x + w - 22, y + 20], fill=RED)
    elif kind == "race":
        draw.rectangle([x, y, x + w, y + h], fill=(24, 24, 32))
        draw.rectangle([x, y + h - 14, x + w, y + h - 6], fill=(70, 70, 78))
        draw.polygon([(x + 30, y + h - 18), (x + 58, y + h - 18),
                      (x + 66, y + h - 8), (x + 24, y + h - 8)], fill=(200, 30, 36))
        draw.ellipse([x + 34, y + h - 8, x + 42, y + h - 1], fill=(10, 10, 10))
        draw.ellipse([x + 54, y + h - 8, x + 62, y + h - 1], fill=(10, 10, 10))
        for i in range(4):
            draw.rectangle([x + w - 40 + i * 9, y + 4, x + w - 32 + i * 9, y + 12],
                           fill=(255, 255, 255) if i % 2 == 0 else (17, 17, 17))
    elif kind == "phone":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 34, 48))
        draw.rectangle([x + w // 2 - 16, y + 4, x + w // 2 + 16, y + h - 4],
                       fill=(220, 225, 235))
        draw.rectangle([x + w // 2 - 11, y + 9, x + w // 2 + 11, y + h - 10],
                       fill=(90, 140, 220))
        draw.text((x + w - 30, y + 8), "✕", font=F_SANS_B(18), fill=RED)
    elif kind == "ship":
        draw.rectangle([x, y, x + w, y + h], fill=(16, 42, 66))
        draw.rectangle([x, y + h - 12, x + w, y + h], fill=(30, 80, 120))
        draw.polygon([(x + 30, y + h - 14), (x + 120, y + h - 14),
                      (x + 108, y + h - 4), (x + 42, y + h - 4)],
                     fill=(90, 70, 50))
        draw.rectangle([x + 58, y + h - 30, x + 96, y + h - 14], fill=(120, 90, 60))
        _flame(draw, x + 76, y + h - 28, 20)
        _smoke(draw, x + 76, y + 6, 8, (80, 80, 88))
    elif kind == "hospital":
        draw.rectangle([x, y, x + w, y + h], fill=(240, 240, 238))
        draw.rectangle([x + w // 2 - 8, y + 6, x + w // 2 + 8, y + h - 6],
                       fill=RED)
        draw.rectangle([x + w // 2 - 20, y + 14, x + w // 2 + 20, y + 26],
                       fill=RED)
        draw.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)], fill=RED, width=2)
    elif kind == "basket":
        draw.rectangle([x, y, x + w, y + h], fill=(214, 90, 20))
        draw.ellipse([x + 18, y + 6, x + 44, y + 32], fill=(240, 130, 40),
                     outline=(120, 50, 10), width=2)
        draw.arc([x + 18, y + 6, x + 44, y + 32], 0, 180, fill=(120, 50, 10),
                 width=1)
        draw.rectangle([x + w - 44, y + 8, x + w - 16, y + 14], fill=(200, 40, 30))
        draw.line([(x + w - 40, y + 14), (x + w - 36, y + 26)], fill=(255, 255, 255),
                  width=1)
        draw.line([(x + w - 20, y + 14), (x + w - 24, y + 26)], fill=(255, 255, 255),
                  width=1)
    elif kind == "fire":
        draw.rectangle([x, y, x + w, y + h], fill=(40, 34, 40))
        draw.rectangle([x + 24, y + 14, x + w - 24, y + h - 4], fill=(70, 60, 66))
        for wy in range(y + 18, y + h - 8, 8):
            draw.rectangle([x + 30, wy, x + 36, wy + 4], fill=(255, 205, 90))
            draw.rectangle([x + w - 36, wy, x + w - 30, wy + 4], fill=(255, 205, 90))
        _flame(draw, x + w // 2, y + 16, 22)
    elif kind == "van":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 190, 170))
        draw.rectangle([x, y + h - 12, x + w, y + h], fill=(90, 90, 96))
        draw.rectangle([x + 26, y + 10, x + 96, y + h - 12], fill=(250, 250, 250))
        draw.rectangle([x + 96, y + 16, x + 122, y + h - 12], fill=(220, 220, 220))
        draw.ellipse([x + 38, y + h - 12, x + 50, y + h - 2], fill=(17, 17, 17))
        draw.ellipse([x + 100, y + h - 12, x + 112, y + h - 2], fill=(17, 17, 17))
    elif kind == "boat":
        draw.rectangle([x, y, x + w, y + h], fill=(120, 180, 220))
        draw.rectangle([x, y + h - 16, x + w, y + h], fill=(30, 90, 140))
        draw.polygon([(x + 34, y + h - 18), (x + 124, y + h - 18),
                      (x + 112, y + h - 6), (x + 46, y + h - 6)],
                     fill=(120, 82, 40))
        draw.line([(x + 76, y + h - 18), (x + 76, y + 6)], fill=(60, 40, 20),
                  width=2)
        draw.polygon([(x + 78, y + 8), (x + 78, y + h - 20), (x + 104, y + h - 20)],
                     fill=(247, 243, 232))
    elif kind == "table":
        draw.rectangle([x, y, x + w, y + h], fill=(240, 230, 210))
        draw.rectangle([x + 14, y + 18, x + w - 14, y + 26], fill=(150, 100, 50))
        for px in (30, 70, 110):
            draw.ellipse([x + px, y + h - 14, x + px + 18, y + h - 2],
                         fill=(255, 255, 255), outline=(150, 150, 150))
    elif kind == "snow":
        draw.rectangle([x, y, x + w, y + h], fill=(210, 225, 240))
        draw.rectangle([x, y + h - 10, x + w, y + h], fill=(255, 255, 255))
        draw.rectangle([x + 30, y + 14, x + 120, y + h - 10], fill=(40, 80, 140))
        for wx in range(38, 116, 14):
            draw.rectangle([wx, y + 18, wx + 8, y + 24], fill=(180, 220, 255))
        for sx, sy in [(14, 8), (140, 6), (130, 24), (20, 26)]:
            draw.text((x + sx, y + sy), "*", font=F_SANS_B(12), fill=(255, 255, 255))
    elif kind == "quake":
        draw.rectangle([x, y, x + w, y + h], fill=(250, 245, 235))
        pts = [(x + 6, y + h // 2), (x + 30, y + h // 2), (x + 40, y + 8),
               (x + 52, y + h - 8), (x + 64, y + h // 2), (x + 90, y + h // 2),
               (x + 100, y + 12), (x + 112, y + h - 10), (x + 124, y + h // 2),
               (x + w - 6, y + h // 2)]
        draw.line(pts, fill=RED, width=2)
        draw.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(200, 200, 200),
                  width=1)
    elif kind == "parliament":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 205, 215))
        draw.polygon([(x + 20, y + 8), (x + w // 2, y + 2), (x + w - 20, y + 8)],
                     fill=(120, 110, 100))
        for cx in (34, 62, 90, 118):
            draw.rectangle([x + cx, y + 12, x + cx + 8, y + h - 6],
                           fill=(240, 240, 235))
        draw.rectangle([x + 14, y + h - 8, x + w - 14, y + h - 4],
                       fill=(120, 110, 100))
    elif kind == "trophy":
        draw.rectangle([x, y, x + w, y + h], fill=(20, 40, 60))
        draw.ellipse([x + w // 2 - 14, y + 6, x + w // 2 + 14, y + 26],
                     fill=GOLD_LT)
        draw.rectangle([x + w // 2 - 4, y + 26, x + w // 2 + 4, y + 34],
                       fill=GOLD_LT)
        draw.rectangle([x + w // 2 - 12, y + 34, x + w // 2 + 12, y + 38],
                       fill=GOLD_LT)
        draw.arc([x + w // 2 - 24, y + 8, x + w // 2 - 6, y + 24], 90, 270,
                 fill=GOLD_LT, width=2)
        draw.arc([x + w // 2 + 6, y + 8, x + w // 2 + 24, y + 24], 270, 90,
                 fill=GOLD_LT, width=2)
    elif kind == "nato":
        draw.rectangle([x, y, x + w, y + h], fill=(20, 50, 110))
        cx, cy = x + w // 2, y + h // 2
        draw.polygon([(cx, cy - 16), (cx + 4, cy - 4), (cx + 16, cy),
                      (cx + 4, cy + 4), (cx, cy + 16), (cx - 4, cy + 4),
                      (cx - 16, cy), (cx - 4, cy - 4)], fill=(255, 255, 255))
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(20, 50, 110))
    elif kind == "gate":
        draw.rectangle([x, y, x + w, y + h], fill=(180, 190, 200))
        draw.rectangle([x + 12, y + 6, x + 18, y + h - 6], fill=(60, 60, 66))
        draw.rectangle([x + w - 18, y + 6, x + w - 12, y + h - 6],
                       fill=(60, 60, 66))
        for i in range(5):
            draw.rectangle([x + 20 + i * 24, y + 10, x + 34 + i * 24, y + 16],
                           fill=(176, 30, 36) if i % 2 == 0 else (255, 255, 255))
        draw.line([(x + 12, y + 20), (x + w - 12, y + 20)], fill=(60, 60, 66),
                  width=2)
    elif kind == "flags":
        draw.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
        draw.line([(x + 34, y + 6), (x + 34, y + h - 6)], fill=(120, 120, 120),
                  width=2)
        draw.rectangle([x + 36, y + 6, x + 72, y + 20], fill=(255, 153, 51))
        draw.rectangle([x + 36, y + 20, x + 72, y + 27], fill=(255, 255, 255))
        draw.rectangle([x + 36, y + 27, x + 72, y + 38], fill=(19, 136, 8))
        draw.line([(x + w - 34, y + 6), (x + w - 34, y + h - 6)],
                  fill=(120, 120, 120), width=2)
        draw.rectangle([x + w - 72, y + 6, x + w - 36, y + 20], fill=(220, 20, 60))
        draw.rectangle([x + w - 72, y + 20, x + w - 36, y + 38],
                       fill=(0, 0, 130))
        draw.ellipse([x + w // 2 - 10, y + h - 14, x + w // 2 + 10, y + h - 2],
                     fill=(232, 200, 170))
    else:  # fallback: plain skyline
        draw.rectangle([x, y, x + w, y + h], fill=(90, 110, 140))


# ---------------------------------------------------------------- content
# (num, region, place, kind, headline, deck, source)
HEROES = [
    (1, "CLIMATE · ANTALYA", "COP31",
     "COP31 collapses with no deal",
     "The EU, UK and Panama rejected a text omitting fossil fuels. Kurum: "
     "\u201cnot adopted\u201d. 44 hours overtime \u2014 the longest COP ever, "
     "first no-deal since COP6 in 2000. Draft kept a 35% clean-electricity "
     "goal; 1.5\u00b0C will be overshot.",
     "Reuters \u00b7 BBC \u00b7 The Guardian"),
    (2, "WAR · UKRAINE", "KYIV",
     "Russia fires 186 drones; Dymer block destroyed, 14 missing",
     "Russia launched 186 drones overnight \u2014 161 downed or jammed, 72 of "
     "them jet-powered. One destroyed a five-storey block in Dymer: 14 "
     "people unaccounted for, 2 dead. Zelenskyy: 2,700 drones fired this "
     "week.",
     "Ukrainian Air Force \u00b7 Reuters"),
    (3, "CLAIM · GULF", "MANAMA",
     "Iran claims two US radars hit; Bahrain denies it",
     "IRGC media claimed Saturday-night strikes hit two US Patriot radars at "
     "al-Riffa and Awali. Bahrain says its defences intercepted the attack; "
     "a civilian plant burned, two hurt. CLAIM \u2014 unverified by "
     "independent sources.",
     "Khaleej Times \u00b7 Al Jazeera \u00b7 CENTCOM"),
]

# (num, region, place, kind, headline, deck, source)
CARDS = [
    (4, "HONG KONG", "ballot",
     "Hong Kong turnout hits record 98.79%",
     "5,640 of 5,709 voters cast ballots; count done 22:15. 2021: 89.77%.",
     "SCMP"),
    (5, "WELLINGTON", "cricket",
     "India declare 720/9 \u2014 a record in NZ",
     "Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233.",
     "ESPNcricinfo"),
    (6, "LAS VEGAS", "race",
     "Verstappen wins Vegas by 0.639s",
     "75th career win; Norris 2nd, Piastri 3rd from 17th.",
     "Formula 1"),
    (7, "SEOUL", "phone",
     "Seoul minister quits over AI exam scandal",
     "Choi Kyo-jin resigned; Lee accepted in an hour. 111 device cases.",
     "AFP"),
    (8, "FINLAND", "ship",
     "Sparta II still burning off Finland",
     "Struck Saturday; fire smouldered Sunday, 16 crew out, 1 slightly hurt.",
     "Reuters"),
    (9, "BRAS\u00cdLIA", "hospital",
     "Bolsonaro in ICU after bowel obstruction",
     "Admitted Friday, in ICU Saturday, stable. Serving 27-year sentence.",
     "Reuters"),
    (10, "SAN ANTONIO", "basket",
     "Wembanyama drops 50 as Spurs rout Pelicans",
     "50 pts, 19 reb, 5 blk \u2014 a first. Spurs 114\u201391.",
     "AP \u00b7 Reuters"),
    (11, "CIKANDE", "fire",
     "Candy-factory fire: 3 dead, 36 missing",
     "Blaze broke out Saturday 17:00; search went on Sunday, ~300 inside.",
     "Detiknews"),
    (12, "GAZA", "van",
     "Hamas seeks urgent talks after aid-van strike",
     "Strike killed 3 aid workers Saturday; Hamas calls mediators Sunday.",
     "Anadolu \u00b7 Wafa"),
    (13, "BAYELSA", "boat",
     "Nigeria boat toll reaches 24",
     "Capsized Friday, Ayama-Ukubie; 24 dead, 24 rescued. Manager held.",
     "Reuters"),
    (14, "VATICAN", "table",
     "Pope Leo XIV hosts 1,300 for lunch",
     "10th World Day of the Poor; lunch in Paul VI Hall, a week late.",
     "Vatican News"),
    (15, "FUKUSHIMA", "snow",
     "1,500 still cut off by Japan snow",
     "Travellers stranded in Kitashiobara since Saturday; train derailed.",
     "NHK"),
    (16, "MINDANAO", "quake",
     "M5.6 quake off Mindanao; no damage",
     "Off southern Mindanao, 15:54 local, depth 10 km. No damage expected.",
     "PHIVOLCS"),
    (17, "CANBERRA", "parliament",
     "Marles: US report \u2018wrong\u2019 on AUKUS",
     "Defence minister rejects CBO warning on subs cost.",
     "Reuters"),
    (18, "TURIN · FORECAST", "trophy",
     "Zverev v Alcaraz in Turin final \u2014 today",
     "The ATP Finals title match closes the season in Turin.",
     "ATP"),
    (19, "WARSAW", "nato",
     "NATO to meet Monday over Poland incursion",
     "Rutte: \u2018every inch\u2019; Kh-101 confirmed; council meets Mon 23 Nov.",
     "dpa \u00b7 PAP"),
    (20, "TALLINN", "gate",
     "Moscow vows retaliation as Estonia seals border",
     "Crossings shut from 1 Dec; Moscow calls it a \u2018new Iron Curtain\u2019.",
     "Reuters"),
    (21, "DELHI", "flags",
     "Nepal PM Shah lands in Delhi",
     "First foreign trip; talks with Modi on Monday.",
     "MEA \u00b7 PTI"),
]

# (num, region, text, source)
ALSO = [
    (22, "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv"),
    (23, "EUROPE", "Russia says it downed 170 Ukrainian drones overnight", "Moscow"),
    (24, "WORLD", "Bitcoin back above $60,000 after Saturday\u2019s $55,106 low", "Coinbase"),
    (25, "AMERICAS", "San Francisco braces for record king tides", "NWS"),
    (26, "AMERICAS", "Crew stun Messi\u2019s 10-man Inter Miami 3\u20130", "MLS"),
    (27, "MID EAST", "Iran begins rolling power cuts, up to 2 hours a day", "Tavanir"),
    (28, "MID EAST", "US denies Iran claim it downed an F-16 \u2014 CENTCOM", "US"),
    (29, "MID EAST", "Iraq PM to visit Cairo on Monday \u2014 oil, arms talks", "Baghdad"),
    (30, "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children, in W. Kordofan", "Wires"),
    (31, "AFRICA", "S. Africa holds prayer service for Mlambo-Ngcuka, 71 (died Fri)", "SABC"),
    (32, "OCEANIA", "Melbourne: 70 years since the 1956 Olympics opened", "ABC"),
    (33, "EUROPE", "Football later today: Liverpool v Man Utd, 16:30 GMT", "FORECAST"),
    (34, "WORLD", "Pope prays for war victims, drought-hit Papua New Guinea", "Vatican"),
    (35, "EUROPE", "Russian helicopter suspected of breaching Finnish airspace", "Helsinki"),
    (36, "MID EAST", "Lebanon marks 83rd Independence Day", "Beirut"),
    (37, "EUROPE", "Hull v Brighton, 14:00 GMT \u2014 today", "FORECAST"),
    (38, "EUROPE", "Poland: Swedish Gripen pilot held fire on the Kh-101 in bad weather", "PAP"),
    (39, "ASIA-PACIFIC", "M5.3 quake in the Celebes Sea, 61 km deep, Sun 07:54 UTC", "EMSC"),
    (40, "AFRICA", "Somalia: UAE envoy\u2019s 72 hours to leave run out today (ordered Thu)", "Mogadishu"),
]

# wrong-day items other entries list as Sunday
DATE_CHECK = [
    ("Peru quake", "Fri 20 Nov"),
    ("BepiColombo at Mercury", "Sat 21 Nov"),
    ("ICJ Myanmar ruling", "Thu 19 Nov"),
    ("Kenya\u2019s last Ebola patient out", "11 Nov"),
    ("Denmark expels attach\u00e9", "Fri 20 Nov"),
    ("Senate $350bn bill stalls", "18\u201319 Nov"),
    ("Qatar talks in Tehran", "Fri night"),
    ("Trump\u2013Xi\u2013Putin talks", "Thu 19 Nov"),
    ("EU\u2013Indonesia deal", "Sat 21 Nov"),
    ("UK\u2013EU food deal", "Fri 20 Nov"),
    ("El Chapo Isidro seized", "Fri 20 Nov"),
    ("Nvidia SEC probe", "Fri 20 Nov"),
    ("China H-6 bomber turns", "Sat 21 Nov"),
    ("Sparta II struck", "Sat 21 Nov"),
    ("Bayelsa boat capsizes", "Fri 20 Nov"),
    ("Gaza aid-van strike", "Sat 21 Nov"),
    ("Newcastle 2\u20132 Arsenal; Chelsea 1\u20134 Leeds", "Sat 21 Nov"),
    ("Aoun\u2019s Israel-withdrawal speech", "Sat 21 Nov"),
    ("Japan poll: 62% feel affinity to Korea", "Fri 20 Nov"),
    ("DR Congo Cantine attack", "5\u20136 Nov"),
    ("Somalia orders UAE envoy out", "Thu 19 Nov"),
    ("Mlambo-Ngcuka dies", "Fri 20 Nov"),
    ("Estonia closes border", "decided Fri 20 Nov"),
]

NUMBERS = [
    ("44h", "COP31 OVERTIME TO COLLAPSE"),
    ("186", "DRONES FIRED AT UKRAINE"),
    ("161", "DOWNED OR JAMMED"),
    ("720/9", "INDIA\u2019S RECORD TEST TOTAL"),
    ("$61,568", "BITCOIN\u2019S SUNDAY HIGH"),
    ("98.79%", "HONG KONG TURNOUT, RECORD"),
]

MARKETS = [
    ("GOLD \u2014 per oz, Sunday", "$3,539"),
    ("BITCOIN \u2014 Sunday high", "$61,568"),
    ("TASI \u2014 9,960.44, Riyadh", "\u22121.95%"),
    ("QATAR \u2014 9,902.87, Doha", "\u22121.59%"),
    ("EGX30 \u2014 49,989.79, Cairo", "\u22122.85%"),
    ("EGX70 \u2014 16,534.42, Cairo", "\u22125.55%"),
]

TIMELINE = ("THE DAY IN UTC \u2014 03:00 COP31 objections close \u00b7 "
            "05:30 Verstappen wins Vegas \u00b7 06:00 COP31 approval due \u00b7 "
            "09:29 Hamas seeks talks \u00b7 12:15 Bitcoin tops $61,568 \u00b7 "
            "14:15 HK count done")

REGIONS = ("7 REGIONS \u2014 EUROPE 12 \u00b7 MIDDLE EAST 6 \u00b7 "
           "ASIA-PACIFIC 7 \u00b7 AMERICAS 5 \u00b7 AFRICA 4 \u00b7 "
           "OCEANIA 3 \u00b7 WORLD 3")


# ---------------------------------------------------------------- build
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 24                      # side margin
    X1 = W - M

    # --- top strip
    d.rectangle([0, 0, W, 20], fill=NAVY)
    d.text((M, 4), "THE WORLD IN ONE DAY", font=F_SANS_B(10),
           fill=(255, 255, 255))
    rt = "40 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((X1 - d.textlength(rt, font=F_SANS_B(10)), 4), rt,
           font=F_SANS_B(10), fill=GOLD_LT)

    # --- masthead
    title = "Sunday 22 November 2026"
    tf = F_SERIF_B(56)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 24), title, font=tf, fill=INK)
    sub = ("COP31 collapses with no deal  \u00b7  Russia fires 186 drones  "
           "\u00b7  Iran claims two US radars hit")
    sf = F_SANS_B(16)
    sw = d.textlength(sub, font=sf)
    d.text(((W - sw) / 2, 86), sub, font=sf, fill=RED)
    hline(d, M, X1, 106, w=2)

    # --- numbers band
    y0, y1 = 110, 150
    cw = (X1 - M) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx0 = M + i * cw
        nf = F_SANS_B(30)
        nw = d.textlength(num, font=nf)
        d.text((cx0 + (cw - nw) / 2, y0), num, font=nf, fill=INK)
        lf = F_SANS_B(8)
        lw = d.textlength(lab, font=lf)
        d.text((cx0 + (cw - lw) / 2, y0 + 30), lab, font=lf, fill=MUTED)
        if i:
            vline(d, cx0, y0 + 2, y1 - 4, fill=HAIR, w=1)
    hline(d, M, X1, y1, w=1)

    # --- UTC timeline
    d.text((M, 154), TIMELINE, font=F_SANS_B(9), fill=MUTED)
    hline(d, M, X1, 168, w=1)

    # --- MARKETS band (proper band, all Sunday closes)
    my0, my1 = 172, 214
    d.rectangle([M, my0, X1, my1], fill=NAVY)
    d.text((M + 8, my0 + 3), "MARKETS \u2014 SUNDAY 22 NOV \u00b7 GULF BOURSES RETREAT",
           font=F_SANS_B(10), fill=GOLD_LT)
    mcw = (X1 - M) / 6
    for i, (name, val) in enumerate(MARKETS):
        cx0 = M + i * mcw
        d.text((cx0 + 8, my0 + 16), name, font=F_SANS_B(8),
               fill=(180, 190, 205))
        d.text((cx0 + 8, my0 + 25), val, font=F_SANS_B(16),
               fill=(255, 255, 255))
        if i:
            vline(d, cx0, my0 + 15, my1 - 4, fill=(70, 90, 125), w=1)

    # --- regions strip
    d.text((M, 218), REGIONS, font=F_SANS_B(10), fill=INK)
    hline(d, M, X1, 230, w=2)

    # --- heroes (journalistic scenes, not abstract)
    hw = (X1 - M - 16) // 3
    hy0 = 234
    img_h = 84
    for i, (num, region, place, head, deck, src) in enumerate(HEROES):
        hx = M + i * (hw + 8)
        if i == 0:
            hero_cop31(d, hx, hy0, hw, img_h)
        elif i == 1:
            hero_kyiv(d, hx, hy0, hw, img_h)
        else:
            hero_bahrain(d, hx, hy0, hw, img_h)
        cap = {"COP31": "ANTALYA \u2014 44 HOURS OVERTIME",
               "KYIV": "KYIV REGION \u2014 186 DRONES",
               "MANAMA": "MANAMA \u2014 CLAIM: IRGC SAYS TWO RADARS HIT"}[place]
        d.rectangle([hx, hy0 + img_h - 15, hx + hw, hy0 + img_h], fill=(0, 0, 0))
        d.text((hx + 5, hy0 + img_h - 12), cap, font=F_SANS_B(8),
               fill=(255, 255, 255))
        ty = hy0 + img_h + 5
        chip(d, hx, ty, str(num), F_SANS_B(9), (255, 255, 255), RED)
        d.text((hx + 24, ty + 1), region, font=F_SANS_B(9), fill=RED)
        hy = draw_wrapped(d, (hx, ty + 15), head, F_SERIF_B(19), hw,
                          leading=21, max_lines=2)
        draw_wrapped(d, (hx, hy + 2), deck, F_SANS(10), hw, leading=11,
                     max_lines=4)
    hline(d, M, X1, 429, w=1)

    # --- cards grid 6 x 3 (number + place overlaid on the scene strip)
    gy0 = 435
    ch, cgap = 88, 6
    cw2 = (X1 - M - 5 * cgap) // 6
    for idx, (num, place, kind, head, deck, src) in enumerate(CARDS):
        r, c = divmod(idx, 6)
        cx = M + c * (cw2 + cgap)
        cy = gy0 + r * (ch + cgap)
        d.rectangle([cx, cy, cx + cw2, cy + ch], fill=CARD_BG,
                    outline=HAIR, width=1)
        scene(d, cx + 1, cy + 1, cw2 - 2, 38, kind)
        # overlay bar: number + place on the scene
        d.rectangle([cx + 1, cy + 27, cx + cw2 - 1, cy + 39], fill=(0, 0, 0))
        d.text((cx + 5, cy + 30), str(num), font=F_SANS_B(9), fill=RED)
        d.text((cx + 18, cy + 30), place, font=F_SANS_B(8),
               fill=(255, 255, 255))
        hy = draw_wrapped(d, (cx + 4, cy + 43), head, F_SANS_B(11),
                          cw2 - 8, leading=12, max_lines=2)
        draw_wrapped(d, (cx + 4, hy + 1), deck, F_SANS(9), cw2 - 8,
                     leading=10, max_lines=2)
    hline(d, M, X1, gy0 + 3 * ch + 2 * cgap + 4, w=1)

    # --- map strip
    map_y0 = 715
    d.text((M, map_y0), "THE WORLD ON SUNDAY \u2014 21 STORIES PINNED",
           font=F_SANS_B(10), fill=INK)
    d.text((X1 - d.textlength("pins match story numbers",
                               font=F_SANS(9)), map_y0 + 1),
           "pins match story numbers", font=F_SANS(9), fill=MUTED)
    draw_map(d, M, map_y0 + 14, X1 - M, 60)
    hline(d, M, X1, map_y0 + 80, w=1)

    # --- ALSO
    ay0 = 805
    d.text((M, ay0), "ALSO ON SUNDAY 22 NOVEMBER \u2014 19 MORE STORIES",
           font=F_SANS_B(11), fill=INK)
    d.text((X1 - d.textlength("FORECAST = still to happen when drawn",
                               font=F_SANS(9)), ay0 + 1),
           "FORECAST = still to happen when drawn", font=F_SANS(9),
           fill=MUTED)
    col_w = (X1 - M) / 2
    for i, (num, region, text, src) in enumerate(ALSO):
        col = 0 if i < 10 else 1
        row = i if i < 10 else i - 10
        ax = M + col * col_w
        ay = ay0 + 16 + row * 10
        d.text((ax, ay), f"{num}", font=F_SANS_B(9), fill=RED)
        d.text((ax + 18, ay), region, font=F_SANS_B(9), fill=INK)
        rx = ax + 18 + d.textlength(region, font=F_SANS_B(9)) + 5
        d.text((rx, ay), text, font=F_SANS(9), fill=INK)
        send = (X1 if col == 1 else ax + col_w) - 8
        d.text((send - d.textlength(src, font=F_SANS(8)), ay),
               src, font=F_SANS(8), fill=MUTED)
    hline(d, M, X1, ay0 + 16 + 10 * 10 + 2, w=1)

    # --- DATE CHECK (3 columns)
    dy0 = 923
    d.rectangle([M, dy0, X1, dy0 + 84], outline=RED, width=2)
    d.text((M + 6, dy0 + 3), "DATE CHECK", font=F_SANS_B(10), fill=RED)
    d.text((M + 82, dy0 + 3),
           "NOT SUNDAY \u2014 listed as Sunday elsewhere, left out on purpose:",
           font=F_SANS_B(9), fill=INK)
    items = [f"\u2715 {name} \u2014 {when}" for name, when in DATE_CHECK]
    ncols, per = 3, 8
    colw = (X1 - M) / ncols
    for col in range(ncols):
        chunk = items[col * per:(col + 1) * per]
        ax = M + 6 + col * colw
        for j, it in enumerate(chunk):
            d.text((ax, dy0 + 17 + j * 8.5), it, font=F_SANS(8), fill=INK)

    # --- footer
    d.text((M, 1012),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 BBC \u00b7 The Times \u00b7 "
           "Formula 1 \u00b7 Cricinfo \u00b7 PHIVOLCS \u00b7 Vatican News \u00b7 QNA \u00b7 "
           "Saudi Exchange \u00b7 QSE \u00b7 EGX \u2014 all stories verified vs Sunday "
           "22 Nov 2026; forecasts labelled; claims attributed.",
           font=F_SANS(8), fill=MUTED)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    img = render()
    img.save(out, format="PNG")
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
