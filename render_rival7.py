#!/usr/bin/env python3
"""news-image-20261122 RIVAL7 — "THE SUNDAY DOSSIER".
PIL-only, deterministic (no timestamps, no randomness, no network).
Run: python3 render_rival7.py poster.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (244, 239, 227)
INK = (24, 24, 24)
RED = (163, 31, 31)
NAVY = (31, 45, 80)
GREY = (110, 108, 100)
LINE = (180, 175, 162)
CREAM = (250, 246, 236)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

_cache = {}


def F(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]


def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, font, maxw, leading, fill=INK, max_lines=None):
    lines = wrap(draw, text, font, maxw)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def rule(draw, x, y, w, fill=INK, width=1):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


def label_chip(draw, x, y, text, fill, fg=(255, 255, 255)):
    f = F(SANSB, 8)
    tw = draw.textlength(text, font=f)
    draw.rounded_rectangle([x, y, x + tw + 10, y + 12], radius=2, fill=fill)
    draw.text((x + 5, y + 2), text, font=f, fill=fg)
    return tw + 10


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "poster.png"
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    MX = 14
    CW = W - 2 * MX  # 996

    # ---------- masthead ----------
    d.text((MX, 8), "THE SUNDAY DOSSIER \u2014 THE WORLD IN ONE DAY",
           font=F(SANSB, 10), fill=INK)
    r = "40 STORIES \u00b7 7 REGIONS \u00b7 EVERY DATE CHECKED \u00b7 SUNDAY 22 NOVEMBER 2026"
    d.text((W - MX - d.textlength(r, font=F(SANSB, 9)), 9), r,
           font=F(SANSB, 9), fill=GREY)
    d.text((MX, 22), "Sunday 22 November 2026", font=F(SERIFB, 56), fill=INK)
    # kicker line + NO DEAL badge
    ky = 90
    d.text((MX, ky), "COP31 collapses with no deal  \u00b7  Russia fires 186 drones  \u00b7  "
           "Iran claims two US radars hit", font=F(SANSB, 13), fill=RED)
    bw = 92
    d.rectangle([W - MX - bw, ky - 2, W - MX, ky + 18], fill=RED)
    d.text((W - MX - bw + 12, ky + 1), "NO DEAL", font=F(SANSB, 13), fill=(255, 255, 255))

    # ---------- big numbers band ----------
    ny = 110
    nums = [
        ("44h", "COP31 OVERTIME\nTO COLLAPSE"),
        ("186", "DRONES OR MISSILES\nAT UKRAINE"),
        ("161", "DOWNED OR\nJAMMED"),
        ("720/9", "INDIA'S RECORD\nTEST TOTAL"),
        ("$61,568", "BITCOIN'S SUNDAY\nHIGH"),
        ("98.79%", "HONG KONG TURNOUT,\nRECORD"),
    ]
    cellw = CW / 6
    for i, (big, small) in enumerate(nums):
        x = MX + i * cellw
        if i:
            d.line([(x - 4, ny + 2), (x - 4, ny + 34)], fill=LINE, width=1)
        d.text((x, ny), big, font=F(SERIFB, 22), fill=INK)
        yy = ny + 26
        for ln in small.split("\n"):
            d.text((x, yy), ln, font=F(SANSB, 7), fill=GREY)
            yy += 9
    rule(d, MX, 148, CW, width=1)

    # ---------- timeline strip ----------
    d.text((MX, 152), "THE DAY IN UTC \u2014  03:00 COP31 objections close  \u00b7  "
           "05:30 Verstappen wins Vegas  \u00b7  06:00 COP31 approval due  \u00b7  "
           "09:29 Hamas seeks talks  \u00b7  14:15 HK count done",
           font=F(SANSB, 9), fill=INK)

    # ---------- MARKETS band ----------
    my = 166
    d.rectangle([MX, my, W - MX, my + 26], fill=NAVY)
    d.text((MX + 8, my + 7), "MARKETS", font=F(SANSB, 11), fill=(255, 255, 255))
    d.text((MX + 92, my + 7), "SUNDAY 22 NOV", font=F(SANS, 8), fill=(190, 200, 225))
    mk = [
        ("GOLD \u00b7 PER OZ", "$3,539"),
        ("BITCOIN \u00b7 SUNDAY HIGH", "$61,568"),
        ("TASI \u00b7 RIYADH", "9,960.44  \u22121.95%"),
        ("QATAR \u00b7 DOHA", "9,902.87  \u22121.59%"),
        ("EGX30 \u00b7 CAIRO", "49,989.79  \u22122.85%"),
        ("EGX70 \u00b7 CAIRO", "16,534.42  \u22125.55%"),
    ]
    mw = (CW - 170) / 6
    for i, (lab, val) in enumerate(mk):
        x = MX + 170 + i * mw
        d.text((x, my + 3), lab, font=F(SANS, 7), fill=(190, 200, 225))
        d.text((x, my + 13), val, font=F(SANSB, 10), fill=(255, 255, 255))

    draw_heroes(d, MX, CW)
    draw_grid(d, MX, CW)
    draw_map(d, MX, CW)
    draw_also(d, MX, CW)
    draw_datecheck(d, MX, CW)
    # ---------- footer ----------
    d.text((MX, 1014), "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 Al Jazeera \u00b7 BBC \u00b7 "
           "The Times \u00b7 Formula 1 \u00b7 Cricinfo \u00b7 PHIVOLCS \u00b7 Vatican News \u00b7 "
           "QNA \u00b7 Saudi Exchange \u00b7 EGX \u2014 all stories verified vs Sunday 22 Nov 2026; "
           "dated items flagged in the list below.",
           font=F(SANS, 7), fill=GREY)
    im.save(out, "PNG")
    print("wrote", out)


# =====================================================================
# HEROES
# =====================================================================
def hero_frame(d, x, y, w, kicker, label, label_fill):
    d.text((x, y), kicker, font=F(SANSB, 9), fill=RED)
    f = F(SANSB, 8)
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([x + w - tw - 10, y - 1, x + w, y + 11], radius=2, fill=label_fill)
    d.text((x + w - tw - 5, y + 1), label, font=f, fill=(255, 255, 255))


def hero1_cop(d, x, y, w, h):
    # warm assembly hall, ceiling spotlights, screen, presidium, varied delegates
    for i in range(h):
        t = i / h
        r = int(58 + 30 * t)
        g = int(44 + 22 * t)
        b = int(30 + 16 * t)
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    # spotlight cones from ceiling
    for cx in (x + 60, x + w // 2, x + w - 60):
        d.polygon([(cx - 14, y), (cx + 14, y), (cx + 46, y + 78), (cx - 46, y + 78)],
                  fill=(255, 214, 130, 38))
    # projection screen
    sx, sy, sw, sh = x + w // 2 - 78, y + 6, 156, 34
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=(238, 232, 214), outline=(20, 20, 20), width=2)
    d.text((sx + 12, sy + 4), "COP31 \u00b7 ANTALYA", font=F(SANSB, 12), fill=(90, 20, 20))
    d.text((sx + 34, sy + 20), "FINAL PLENARY", font=F(SANSB, 9), fill=(60, 60, 60))
    # presidium table + flags (flags sit on the table front)
    d.rectangle([x + 18, y + 44, x + w - 18, y + 56], fill=(72, 52, 34))
    flag_cols = [(163, 31, 31), (31, 45, 80), (30, 110, 60), (200, 160, 40),
                 (120, 40, 90), (40, 90, 130), (180, 90, 30)]
    for i, c in enumerate(flag_cols):
        fx = x + 34 + i * 38
        d.rectangle([fx, y + 44, fx + 16, y + 54], fill=c, outline=(220, 210, 190))
    # podium + speaker (left)
    d.rectangle([x + 26, y + 60, x + 52, y + 94], fill=(40, 28, 20))
    d.ellipse([x + 32, y + 48, x + 46, y + 62], fill=(214, 164, 120))  # head
    d.rectangle([x + 30, y + 62, x + 48, y + 72], fill=(30, 30, 40))   # shoulders
    d.line([(x + 46, y + 50), (x + 56, y + 60)], fill=(200, 200, 200), width=2)
    # delegate rows: 2 rows of larger, varied figures
    skins = [(214, 164, 120), (170, 120, 85), (235, 200, 160), (150, 105, 75), (225, 185, 145)]
    suits = [(31, 45, 80), (70, 70, 70), (20, 90, 80), (110, 30, 40), (90, 80, 30),
             (50, 60, 110), (120, 70, 20)]
    rows = [(y + 74, 10), (y + 96, 12)]
    for ri, (ry, n) in enumerate(rows):
        for i in range(n):
            dx = x + 16 + i * ((w - 32) / max(n - 1, 1))
            # shadow + desk
            d.ellipse([dx - 11, ry + 14, dx + 11, ry + 19], fill=(0, 0, 0, 60))
            d.rectangle([dx - 13, ry + 10, dx + 13, ry + 17], fill=(88, 64, 42))
            d.rectangle([dx - 9, ry + 11, dx - 2, ry + 15], fill=(240, 235, 220))  # nameplate
            d.ellipse([dx - 6, ry - 2, dx + 6, ry + 10], fill=skins[(i + ri * 3) % 5])
            d.rectangle([dx - 8, ry + 10, dx + 8, ry + 11], fill=suits[(i * 2 + ri) % 7])
            if (i + ri) % 4 == 0:
                d.rectangle([dx + 4, ry + 3, dx + 11, ry + 9], fill=(200, 210, 220))  # laptop
    # empty-chair walkout block (right, pale, dashed outline, 3 x 2 chairs)
    ex, ey, ew, eh = x + w - 82, y + 70, 68, 42
    d.rectangle([ex, ey, ex + ew, ey + eh], outline=(230, 220, 200), width=1)
    for r in range(2):
        for c in range(3):
            cx = ex + 12 + c * 22
            cy = ey + 7 + r * 19
            d.rectangle([cx - 7, cy, cx + 7, cy + 11], outline=(235, 228, 210), width=1)
            d.rectangle([cx - 7, cy - 5, cx + 7, cy], outline=(235, 228, 210), width=1)
    d.text((ex + 6, ey + eh - 10), "WALKOUT", font=F(SANSB, 7), fill=(235, 228, 210))


def hero2_kyiv(d, x, y, w, h):
    for i in range(h):
        t = i / h
        d.line([(x, y + i), (x + w, y + i)],
               fill=(int(14 + 10 * t), int(16 + 12 * t), int(44 + 18 * t)))
    # stars + moon
    for sx, sy in [(28, 12), (90, 22), (150, 10), (210, 26), (260, 14), (300, 30), (60, 34), (180, 36)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(230, 230, 200))
    d.ellipse([x + w - 52, y + 10, x + w - 22, y + 40], fill=(235, 228, 200))
    d.ellipse([x + w - 46, y + 16, x + w - 30, y + 32], fill=(200, 195, 170))
    # drone trails (kept inside the art box)
    d.arc([x + 20, y + 8, x + 180, y + 95], 200, 330, fill=(255, 180, 80), width=2)
    d.arc([x + 90, y + 12, x + 300, y + 105], 210, 320, fill=(255, 200, 120), width=2)
    for tx, ty in [(96, 44), (150, 30), (236, 52)]:
        d.ellipse([x + tx - 3, y + ty - 3, x + tx + 3, y + ty + 3], fill=(255, 190, 90))
    # skyline, varied heights + lit windows
    heights = [58, 74, 48, 88, 66, 96, 54, 80, 62, 92, 70, 44]
    bw = w // len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        by = y + h - bh
        d.rectangle([bx + 1, by, bx + bw - 1, y + h], fill=(8, 8, 18))
        for wy in range(by + 8, y + h - 6, 12):
            for wx in range(bx + 4, bx + bw - 4, 9):
                if (wx + wy * 3) % 17 < 6:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 200, 90))
    # burning block + smoke + searchlights
    fx = x + w - 96
    d.polygon([(fx - 30, y + 8), (fx + 10, y + 8), (fx - 8, y + 52)], fill=(255, 240, 180, 40))
    d.polygon([(fx + 40, y + 12), (fx + 70, y + 12), (fx + 58, y + 56)], fill=(255, 240, 180, 40))
    for sx, sy, r in [(fx + 8, y + 30, 16), (fx + 26, y + 16, 20), (fx + 44, y + 34, 13)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(90, 85, 85, 120))
    for fx2, fw, fh in [(fx - 6, 8, 18), (fx + 6, 10, 26), (fx + 20, 8, 16), (fx + 32, 9, 22)]:
        d.polygon([(x + fx2, y + h - 30), (x + fx2 + fw // 2, y + h - 30 - fh),
                   (x + fx2 + fw, y + h - 30)], fill=(255, 120, 20))
        d.ellipse([x + fx2 + 2, y + h - 34, x + fx2 + 6, y + h - 30], fill=(255, 200, 60))
    for ex2, ey2 in [(fx - 14, y + h - 44), (fx + 40, y + h - 52), (fx + 18, y + h - 60)]:
        d.ellipse([x + ex2, y + ey2, x + ex2 + 3, y + ey2 + 3], fill=(255, 150, 40))


def hero3_manama(d, x, y, w, h):
    for i in range(h):
        t = i / h
        d.line([(x, y + i), (x + w, y + i)],
               fill=(int(52 + 30 * t), int(30 + 14 * t), int(26 + 10 * t)))
    d.ellipse([x + 22, y + 12, x + 48, y + 38], fill=(240, 210, 160))
    # interceptor streak: straight diagonal trail + bright head
    d.line([(x + 70, y + 52), (x + 252, y + 18)], fill=(255, 255, 255), width=3)
    d.line([(x + 70, y + 52), (x + 252, y + 18)], fill=(200, 200, 200, 120), width=7)
    d.ellipse([x + 248, y + 14, x + 258, y + 24], fill=(255, 220, 120))
    # rooftops, domes, minaret
    d.rectangle([x, y + h - 46, x + w, y + h], fill=(24, 16, 14))
    for bx, bw2, bh in [(10, 60, 30), (80, 46, 40), (140, 70, 26), (220, 54, 36), (286, 40, 24)]:
        d.rectangle([x + bx, y + h - 46 - bh, x + bx + bw2, y + h - 46], fill=(40, 28, 24))
        for wx in range(bx + 6, bx + bw2 - 4, 12):
            d.rectangle([x + wx, y + h - 46 - bh + 6, x + wx + 4, y + h - 46 - bh + 10],
                        fill=(255, 200, 100))
    d.ellipse([x + 96, y + h - 46 - 52, x + 128, y + h - 46 - 20], fill=(70, 55, 40))
    d.rectangle([x + 250, y + h - 46 - 58, x + 258, y + h - 46], fill=(50, 38, 30))
    d.polygon([(x + 246, y + h - 46 - 58), (x + 262, y + h - 46 - 58), (x + 254, y + h - 46 - 72)],
              fill=(90, 70, 50))
    # radar dishes, varied angles (small dish + mast)
    for rx, tilt in [(40, -8), (170, -16), (300, -4)]:
        d.line([(x + rx, y + h - 46), (x + rx, y + h - 46 - 22)], fill=(200, 200, 200), width=2)
        d.ellipse([x + rx - 9, y + h - 46 - 34 + tilt, x + rx + 9, y + h - 46 - 20 + tilt],
                  outline=(220, 220, 220), width=2)
        d.line([(x + rx - 9, y + h - 46 - 27 + tilt), (x + rx + 9, y + h - 46 - 27 + tilt)],
               fill=(220, 220, 220), width=1)
    # burning civilian plant (right) + smoke
    px = x + w - 78
    for sx, sy, r in [(px + 10, y + 34, 14), (px + 30, y + 20, 18), (px + 48, y + 38, 11)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r], fill=(80, 75, 75, 130))
    d.rectangle([x + px, y + h - 46 - 18, x + px + 56, y + h - 46], fill=(60, 40, 30))
    d.rectangle([x + px + 6, y + h - 46 - 30, x + px + 12, y + h - 46 - 18], fill=(60, 40, 30))
    for fx2, fw, fh in [(px + 2, 8, 16), (px + 16, 10, 24), (px + 32, 8, 14)]:
        d.polygon([(x + fx2, y + h - 46 - 18), (x + fx2 + fw // 2, y + h - 46 - 18 - fh),
                   (x + fx2 + fw, y + h - 46 - 18)], fill=(255, 130, 25))
    # sea strip
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(30, 50, 70))
    for wx in range(6, w, 26):
        d.line([(x + wx, y + h - 4), (x + wx + 12, y + h - 4)], fill=(120, 160, 200), width=1)


def draw_heroes(d, MX, CW):
    hy = 196
    hw = (CW - 16) // 3
    arts = [hero1_cop, hero2_kyiv, hero3_manama]
    heroes = [
        ("1 ANTALYA \u00b7 44 HOURS OVERTIME", "REPORTED", RED,
         "COP31 collapses with no deal",
         "The EU, UK and Panama rejected a final text that omitted fossil fuels \u2014 "
         "the first no-deal COP since COP6 in 2000."),
        ("2 KYIV REGION \u00b7 186 DRONES", "REPORTED", RED,
         "Russia fires 186 drones; Dymer block destroyed",
         "161 downed or jammed; 72 jet-powered. One destroyed a five-storey block in "
         "Dymer; 2 dead, 14 missing."),
        ("3 MANAMA \u00b7 CLAIM", "CLAIM", (200, 140, 20),
         "Iran claims two US radars hit; Bahrain denies it",
         "IRGC media claimed Saturday-night strikes hit two US Patriot radars; Bahrain "
         "says it intercepted them. Two hurt; a civilian plant burned."),
    ]
    for i, (kick, lab, labfill, head, deck) in enumerate(heroes):
        x = MX + i * (hw + 8)
        arts[i](d, x, hy, hw, 112)
        hero_frame(d, x, hy + 118, hw, kick, lab, labfill)
        yy = para(d, x, hy + 132, head, F(SERIFB, 19), hw, 22, max_lines=2)
        para(d, x, yy + 2, deck, F(SANS, 10), hw, 13, fill=(60, 60, 60), max_lines=3)
        rule(d, x, hy + 220, hw, fill=LINE, width=1)

# =====================================================================
# GRID (cards 4-22 + HOW TO READ)
# =====================================================================
GRID = [
    ("4 HONG KONG", "REPORTED", (31, 45, 80),
     "Hong Kong turnout hits record 98.79%",
     "5,640 of 5,709 voters cast ballots; count done 22:15. Beats 89.77% in 2021."),
    ("5 WELLINGTON", "REPORTED", (31, 45, 80),
     "India declare 720/9 \u2014 a record in NZ",
     "Rahul 136, Pant 128, Gill 98; NZ 119/2, trailing by 233."),
    ("6 LAS VEGAS", "REPORTED", (31, 45, 80),
     "Verstappen wins Vegas by 0.639s",
     "75th career win; Norris 2nd, Piastri 3rd from 17th."),
    ("7 SEOUL", "REPORTED", (31, 45, 80),
     "Seoul minister quits over AI exam scandal",
     "Choi Kyo-jin resigned; Lee accepted in an hour. 111 device-cheating cases probed."),
    ("8 FINLAND", "REPORTED", (31, 45, 80),
     "Sparta II still burning off Finland",
     "Struck Sat; fire smouldered Sun. Helo suspected of violating Finnish airspace by 4.1 km."),
    ("9 KRYVYI RIH", "REPORTED", (31, 45, 80),
     "Missile kills boy, 7, and medic, 20; 58 hurt",
     "Strike on Zelenskyy's hometown; four fires, ~23 blocks hit, hospital and schools damaged."),
    ("10 SAN ANTONIO", "REPORTED", (31, 45, 80),
     "Wembanyama drops 50 as Spurs rout Pelicans",
     "San Antonio's star scores 50 in a 114\u201391 rout of New Orleans."),
    ("11 CIKANDE", "REPORTED", (31, 45, 80),
     "Candy-factory fire: 3 dead, 36 missing",
     "Blaze broke out Saturday 17:00; search went on Sunday; 300 workers inside."),
    ("12 GAZA", "REPORTED", (31, 45, 80),
     "Hamas seeks urgent talks after aid-van strike",
     "Aid-van strike killed aid workers on Saturday; Hamas called for urgent talks on aid access."),
    ("13 BAYELSA", "REPORTED", (31, 45, 80),
     "Nigeria boat toll reaches 24",
     "Capsized Friday; Ayama\u2013Ukubie; 24 dead, 24 rescued. Manager held."),
    ("14 VATICAN", "REPORTED", (31, 45, 80),
     "Pope Leo XIV hosts 1,300 for lunch",
     "10th World Day of the Poor; lunch in Paul VI Hall, a week of events."),
    ("15 FUKUSHIMA", "REPORTED", (31, 45, 80),
     "1,500 still cut off by Japan landslide",
     "Travellers stranded in Kitashiobara since Saturday; heavy rain hampered rescue."),
    ("16 MINDANAO", "REPORTED", (31, 45, 80),
     "M6.0 quake off Mindanao; no damage",
     "Off southern Mindanao, 15:54 local, depth 10 km. No tsunami."),
    ("17 CANBERRA", "REPORTED", (31, 45, 80),
     "Albanese: US report \u2018wrong\u2019 on AUKUS",
     "Defence minister rejects CBO warning on subs cost; US $368bn programme."),
    ("18 TURIN", "FORECAST", (90, 90, 90),
     "Zverev v Alcaraz in Turin final today",
     "ATP Finals title match closes the season in Turin."),
    ("19 WARSAW", "FORECAST", (90, 90, 90),
     "NATO to meet Monday over Poland incursion",
     "Drone debris confirmed in Nowy Lipowiec. Council meets Monday."),
    ("20 TALLINN", "REPORTED", (31, 45, 80),
     "Moscow vows retaliation as Estonia seals border",
     "Estonia seals crossings for months; Moscow calls it a new Iron Curtain."),
    ("21 DELHI", "REPORTED", (31, 45, 80),
     "Nepal PM Shah lands in Delhi",
     "First foreign trip; talks with Modi on Monday."),
    ("22 LIVERPOOL", "REPORTED", (31, 45, 80),
     "Liverpool 4\u20130 Man Utd: Pochettino routed on debut",
     "Szoboszlai 10\u2032, Wirtz 13\u2032, Ngumoha 66\u2032, Mu\u00f1oz 82\u2032; Yoro sent off 8\u2032. United 19th."),
]

MINI_COLS = [(31, 45, 80), (60, 90, 40), (120, 60, 20), (90, 30, 60),
             (20, 80, 90), (140, 90, 20), (70, 70, 70)]


def mini_art(d, x, y, w, h, variant, col):
    d.rectangle([x, y, x + w, y + h], fill=col)
    if variant == 0:  # skyline
        for i, bh in enumerate([8, 13, 6, 11, 9]):
            bx = x + 4 + i * (w // 5)
            d.rectangle([bx, y + h - bh, bx + w // 5 - 3, y + h], fill=(255, 255, 255, 90))
    elif variant == 1:  # sun + horizon
        d.ellipse([x + w - 22, y + 2, x + w - 6, y + 18], fill=(255, 210, 90))
        d.line([(x, y + h - 5), (x + w, y + h - 5)], fill=(255, 255, 255, 140), width=2)
    elif variant == 2:  # waves
        for wy in (y + 5, y + 11):
            for wx in range(x + 2, x + w - 8, 12):
                d.arc([wx, wy, wx + 10, wy + 8], 180, 360, fill=(255, 255, 255, 160), width=1)
    elif variant == 3:  # flag stripes
        for i, c in enumerate([(255, 255, 255), (255, 210, 90), (255, 255, 255)]):
            d.rectangle([x, y + i * (h // 3), x + w, y + (i + 1) * (h // 3)], fill=c + (110,))
    elif variant == 4:  # dots / radar
        d.ellipse([x + w // 2 - 3, y + h // 2 - 3, x + w // 2 + 3, y + h // 2 + 3],
                  fill=(255, 255, 255))
        d.ellipse([x + w // 2 - 8, y + h // 2 - 8, x + w // 2 + 8, y + h // 2 + 8],
                  outline=(255, 255, 255), width=1)
    elif variant == 5:  # flame
        d.polygon([(x + w // 2 - 6, y + h), (x + w // 2, y + 2), (x + w // 2 + 6, y + h)],
                  fill=(255, 160, 40))
    else:  # bars / chart
        for i, bh in enumerate([5, 9, 7, 12]):
            bx = x + 6 + i * 10
            d.rectangle([bx, y + h - bh, bx + 5, y + h], fill=(255, 255, 255, 150))


def draw_grid(d, MX, CW):
    gy = 422
    gw = (CW - 4 * 8) // 5
    gh = 68
    for idx, (kick, lab, labfill, head, deck) in enumerate(GRID):
        r, c = divmod(idx, 5)
        x = MX + c * (gw + 8)
        y = gy + r * (gh + 3)
        mini_art(d, x, y, gw, 13, idx % 7, MINI_COLS[idx % 7])
        if idx == 18:  # Liverpool: thick FULL TIME score badge over the art strip
            d.rectangle([x + gw - 74, y + 1, x + gw - 2, y + 12], fill=RED)
            d.text((x + gw - 70, y + 2), "4\u20130  FULL TIME", font=F(SANSB, 8),
                   fill=(255, 255, 255))
        d.text((x, y + 16), kick, font=F(SANSB, 8), fill=RED)
        f = F(SANSB, 7)
        tw = d.textlength(lab, font=f)
        d.text((x + gw - tw, y + 16), lab, font=f, fill=labfill)
        yy = para(d, x, y + 26, head, F(SANSB, 11), gw, 12, max_lines=2)
        para(d, x, yy, deck, F(SANS, 8), gw, 9, fill=(70, 70, 70), max_lines=2)
    # HOW TO READ box (last cell, row 4 col 5)
    x = MX + 4 * (gw + 8)
    y = gy + 3 * (gh + 3)
    d.rectangle([x, y, x + gw, y + gh], outline=INK, width=1)
    d.text((x + 6, y + 3), "HOW TO READ", font=F(SANSB, 9), fill=INK)
    legend = [
        ("\u25cf REPORTED", "confirmed by 2+ sources"),
        ("\u25cb CLAIM", "one side asserts, other denies"),
        ("\u25f7 FORECAST", "still to happen when drawn"),
        ("FULL TIME", "score final in"),
        ("\u2020 in ALSO", "dated Fri / Sat"),
    ]
    yy = y + 15
    for a, b in legend:
        d.text((x + 6, yy), a, font=F(SANSB, 7), fill=INK)
        d.text((x + 62, yy), b, font=F(SANS, 7), fill=(70, 70, 70))
        yy += 9


# =====================================================================
# MAP
# =====================================================================
# continents as ellipses in a 100 x 40 virtual grid
LAND = [
    (12, 10, 11, 7), (20, 18, 6, 4),      # N America + Central America
    (26, 28, 6, 8),                        # S America
    (48, 8, 6, 4),                         # Europe
    (50, 20, 7, 9),                        # Africa
    (68, 10, 16, 8), (78, 20, 8, 6),      # Asia + SE Asia
    (84, 30, 6, 4),                        # Australia
]
# (story, vx, vy, label offset dx, dy)
PINS = [
    (1, 52, 12, 6, -8), (2, 50, 8, 10, -4), (3, 57, 15, 6, 2),
    (4, 82, 14, 6, -8), (5, 95, 36, -16, -4), (6, 8, 12, -14, -4),
    (7, 84, 11, 6, -8), (8, 50, 5, 10, -10), (9, 49, 9, -4, 10),
    (10, 11, 15, -16, 2), (11, 80, 22, 6, 2), (12, 53, 14, 6, 8),
    (13, 47, 20, -16, 2), (14, 47, 11, -18, -4), (15, 86, 10, 6, -8),
    (16, 83, 20, 6, 2), (17, 90, 33, -14, 6), (18, 46, 10, -18, 6),
    (19, 49, 7, -14, -10), (20, 50, 4, 4, -12), (21, 70, 14, 6, -8),
    (22, 44, 7, -18, -8),
]


def draw_map(d, MX, CW):
    my = 708
    d.text((MX, my), "THE WORLD ON SUNDAY \u2014 22 STORIES PINNED",
           font=F(SANSB, 10), fill=INK)
    d.text((W - MX - d.textlength("EUROPE 14 \u00b7 MIDDLE EAST 5 \u00b7 ASIA-PACIFIC 8 \u00b7 "
           "AMERICAS 4 \u00b7 AFRICA 4 \u00b7 OCEANIA 3 \u00b7 WORLD 2", font=F(SANSB, 8)), my + 1),
           "EUROPE 14 \u00b7 MIDDLE EAST 5 \u00b7 ASIA-PACIFIC 8 \u00b7 "
           "AMERICAS 4 \u00b7 AFRICA 4 \u00b7 OCEANIA 3 \u00b7 WORLD 2",
           font=F(SANSB, 8), fill=GREY)
    mapx, mapy, mapw, maph = MX, my + 14, 746, 80
    # dotted land
    for gx in range(0, 101, 2):
        for gy in range(0, 41, 2):
            inside = False
            for (cx, cy, rx, ry) in LAND:
                if ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1:
                    inside = True
                    break
            if inside:
                px = mapx + gx / 100 * mapw
                py = mapy + gy / 40 * maph
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(150, 140, 120))
    # pins with fanned leader lines
    for (n, vx, vy, dx, dy) in PINS:
        px = mapx + vx / 100 * mapw
        py = mapy + vy / 40 * maph
        lx, ly = px + dx, py + dy
        d.line([(px, py), (lx, ly)], fill=RED, width=1)
        d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=RED)
        d.text((lx - 3 if n < 10 else lx - 6, ly - 5), str(n), font=F(SANSB, 8),
               fill=(255, 255, 255))
    # Pacific inset
    ix, iy, iw, ih = W - MX - 236, mapy, 236, 80
    d.rectangle([ix, iy, ix + iw, iy + ih], outline=INK, width=1)
    d.text((ix + 6, iy + 3), "PACIFIC \u2014 INSET", font=F(SANSB, 9), fill=INK)
    d.text((ix + 6, iy + 16), "WELLINGTON 5  \u00b7  CANBERRA 17", font=F(SANSB, 9), fill=INK)
    d.text((ix + 6, iy + 30), "5,640 voters \u00b7 98.79% \u2014 the record",
           font=F(SANS, 8), fill=(70, 70, 70))
    d.text((ix + 6, iy + 42), "that beat 89.77% in 2021.", font=F(SANS, 8), fill=(70, 70, 70))
    for n, px, py in [(5, ix + 40, iy + 66), (17, ix + 150, iy + 66)]:
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED)
        d.text((px - 3 if n < 10 else px - 6, py - 5), str(n), font=F(SANSB, 8),
               fill=(255, 255, 255))
    d.text((ix + 58, iy + 60), "Wellington", font=F(SANS, 8), fill=INK)
    d.text((ix + 168, iy + 60), "Canberra", font=F(SANS, 8), fill=INK)


# =====================================================================
# ALSO + DATE CHECK
# =====================================================================
ALSO_L = [
    ("23", "EUROPE", "Zelenskyy: 2,700 drones fired at Ukraine this week", "Kyiv"),
    ("24", "WORLD", "Russia says it downed 170 Ukrainian drones overnight \u25cb CLAIM", "Moscow"),
    ("25", "WORLD", "Bitcoin back above $60,000 after Saturday's $55,130 low", "Coinbase"),
    ("26", "AMERICAS", "San Francisco braces for record king tides \u25f7 FORECAST", "NWS"),
    ("27", "MIDDLE EAST", "US denies Iran claim it downed two US radars \u25cb CLAIM", "CENTCOM"),
    ("28", "EUROPE", "Lebanon marks 83rd Independence Day", "Beirut"),
    ("29", "EUROPE", "Cost-of-living protests across Europe, third day running", "Paris"),
    ("30", "AFRICA", "Sudan: RSF accused of killing civilians, incl. 3 children", "W. Kordofan"),
    ("31", "AFRICA", "S. Africa holds service for Mlambo-Ngcuka, 71 (died Fri)", "SABC"),
]
ALSO_R = [
    ("32", "OCEANIA", "Melbourne: 70 years since the 1956 Olympics opened", "Melbourne"),
    ("33", "EUROPE", "Hull 2\u20130 Brighton", "MKM"),
    ("34", "WORLD", "Pope prays for war victims; drought-hit PNG", "Vatican"),
    ("35", "MIDDLE EAST", "Iraq: fire at Hartha power station kills 4, injures 35 \u2020 SAT", "Basra"),
    ("36", "EUROPE", "Moldova: Russian drone crosses border near Purcari", "Chisinau"),
    ("37", "AFRICA", "Somalia: UAE envoy's 72 hours run out today (ordered Thu)", "Mogadishu"),
    ("38", "ASIA-PACIFIC", "Manipur liquor toll climbs to 19, 600+ in hospital \u2014 Sun a.m., still rising", "Imphal"),
    ("39", "ASIA-PACIFIC", "M5.3 Celebes Sea, 61 km, 07:54 UTC", "EMSC"),
    ("40", "AMERICAS", "Bolsonaro in ICU after bowel obstruction, admitted Friday", "Brasilia"),
]

DC_COLS = [
    ["Peru quake \u2014 Fri 20 Nov",
     "Kenya's last Ebola patient out \u2014 11 Nov",
     "Gaza aid-van strike \u2014 Sat 21 Nov",
     "Japan poll: 62% feel affinity to Korea \u2014 Fri 20 Nov",
     "Mlambo-Ngcuka dies \u2014 Fri 20 Nov",
     "EU\u2013Indonesia deal \u2014 Sat 21 Nov",
     "Denmark expels Russian attach\u00e9 \u2014 Fri 20 Nov",
     "Qatar talks in Tehran \u2014 Fri 20 Nov"],
    ["BepiColombo at Mercury \u2014 Sat 21 Nov",
     "Sparta II struck \u2014 Sat 21 Nov",
     "Newcastle 2\u20132 Arsenal; Chelsea 1\u20134 Leeds \u2014 Sat 21 Nov",
     "DR Congo Cantine attack \u2014 night of 5\u20136 Nov",
     "Estonia closes border \u2014 decided Fri 20 Nov",
     "UK\u2013EU food deal agreed \u2014 Fri 20 Nov",
     "Senate $350bn defence push stalls \u2014 Wed 18 Nov"],
    ["ICJ Myanmar ruling \u2014 Thu 19 Nov",
     "Bayelsa boat capsizes \u2014 Fri 20 Nov",
     "Aoun's Israel-withdrawal speech \u2014 Sat 21 Nov",
     "Nvidia SEC probe \u2014 Fri 20 Nov",
     "\u2018El Chapo Isidro\u2019 captured \u2014 Fri 20 Nov",
     "Trump\u2013Xi\u2013Putin talks \u2014 Thu 19 Nov",
     "H-6 bomber nears Manila \u2014 Sat 21 Nov"],
]


def draw_also(d, MX, CW):
    ay = 808
    d.text((MX, ay), "ALSO ON SUNDAY 22 NOVEMBER \u2014 18 MORE STORIES",
           font=F(SANSB, 10), fill=INK)
    rule(d, MX, ay + 13, CW, width=1)
    f = F(SANS, 9)
    fb = F(SANSB, 9)
    colw = CW // 2
    for col, items in enumerate((ALSO_L, ALSO_R)):
        x = MX + col * colw
        yy = ay + 18
        for (n, reg, txt, src) in items:
            d.text((x, yy), n, font=fb, fill=RED)
            d.text((x + 20, yy), reg, font=fb, fill=GREY)
            d.text((x + 96, yy), txt, font=f, fill=INK)
            sw = d.textlength(src, font=F(SANS, 8))
            d.text((MX + (col + 1) * colw - sw - 2, yy), src, font=F(SANS, 8), fill=GREY)
            yy += 10


def draw_datecheck(d, MX, CW):
    dy = 921
    d.text((MX, dy), "DATE CHECK \u2014 NOT SUNDAY, however listed elsewhere:",
           font=F(SANSB, 10), fill=INK)
    rule(d, MX, dy + 13, CW, width=1)
    f = F(SANS, 8)
    colw = CW // 3
    for ci, items in enumerate(DC_COLS):
        x = MX + ci * colw
        yy = dy + 18
        for it in items:
            d.text((x, yy), "\u2022", font=f, fill=RED)
            d.text((x + 8, yy), it, font=f, fill=INK)
            yy += 9


if __name__ == "__main__":
    main()
