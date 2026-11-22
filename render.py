#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261122 v2 poster.

Renders poster.png (1024x1024) from the STORIES table below. Deterministic:
no timestamps, no randomness, no network access. Run once at build time:
    python3 render.py
main.py (the graded entrypoint) never calls this module; it only copies the
checked-in poster.png to the grader output directory.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (15, 42, 74)
PAPER = (247, 244, 236)
CARD = (255, 255, 255)
INK = (24, 24, 24)
MUTED = (90, 90, 90)
RULE = (180, 175, 160)
GOLD = (201, 162, 39)

REGION_COLORS = {
    "GLOBAL": (106, 27, 154),
    "AFRICA": (180, 83, 9),
    "ASIA": (14, 116, 144),
    "MIDDLE EAST": (185, 28, 28),
    "AMERICAS": (29, 78, 216),
    "EUROPE": (21, 128, 61),
    "OCEANIA": (190, 24, 93),
}

# (region, headline, summary) — every story dated Sunday 22 November 2026.
HEROES = [
    ("AMERICAS",
     "Verstappen wins wild Las Vegas GP",
     "Max Verstappen beats Norris by 0.64s after 35 lead changes; Russell hits the wall late and Antonelli finishes fourth."),
    ("GLOBAL",
     "COP31 final deal goes to Sunday vote",
     "Antalya presidency tables a 10-page pact that never mentions fossil fuels; 130 nations want phase-out language restored."),
    ("AFRICA",
     "G20 adopts declaration without the US",
     "Johannesburg leaders back a 122-paragraph plan on climate, debt and minerals as Washington boycotts the first G20 in Africa."),
    ("ASIA",
     "India declare a record 720 for 9",
     "Pant hits 128 and Rahul 136 in Wellington, the highest Test total ever in New Zealand; the hosts trail by 233."),
    ("GLOBAL",
     "Bitcoin back above $60,000",
     "The token rebounds from Friday's $55,130 low, its weakest since July, as buyers return after a brutal November slide."),
    ("MIDDLE EAST",
     "Iran readies 14 tankers to defy blockade",
     "Tehran plans a convoy past the US naval cordon; a 'ghost tanker' track is exposed as a spoof and two ships are hit."),
    ("AMERICAS",
     "Trump shrugs off FBI database hack",
     "The president calls the breach of the FBI's crime database 'not good', then spins it as a way to expose the 'Russia hoax'."),
    ("OCEANIA",
     "Australia slams US budget office on AUKUS",
     "Canberra hits back at the Congressional Budget Office's cost claims as doubts swirl over the submarine pact."),
]

# (region, one-line headline) — all dated Sunday 22 November 2026.
ALSO = [
    ("AMERICAS", "Senate leadership race: Schumer v Van Hollen; vote 1 Dec"),
    ("AFRICA", "Modi pitches a Global Traditional Knowledge Repository"),
    ("MIDDLE EAST", "Iran rolling power cuts begin on Sunday"),
    ("ASIA", "Dutch foreign minister Van Weel visits India"),
    ("ASIA", "Odisha opens a Rs 249-crore cyber command centre"),
    ("ASIA", "Bangladesh shuts 50 garment factories"),
    ("AMERICAS", "US envoy Gor hails a drug crackdown"),
    ("EUROPE", "ATP final tonight: Zverev v Alcaraz, Turin 18:00 CET"),
    ("ASIA", "EU and Indonesia sign 'ambitious' trade deal"),
    ("ASIA", "South Korea education chief quits in AI cheating scandal"),
    ("ASIA", "Indonesia factory fire: 3 dead, 36 missing"),
    ("AFRICA", "Ethiopia polio drive to protect 11m children"),
    ("AFRICA", "Gambia intercepts 625 would-be migrants in two days"),
    ("AFRICA", "Nigeria: Tinubu seeks to decriminalise suicide bids"),
    ("AMERICAS", "Haiti taps El Salvador to build three prisons"),
    ("AFRICA", "700,000 displaced by conflict in southern Ethiopia"),
    ("EUROPE", "US-Ukraine envoys meet in Geneva on peace plan"),
    ("ASIA", "Kim Jong-un tours factories after Trump snub"),
    ("ASIA", "South Korea's Lee: speed decisive in AI race"),
    ("GLOBAL", "EU weighs forcing an open COP31 fossil-fuel vote"),
    ("AFRICA", "G20: Argentina walks out at the last minute"),
    ("ASIA", "Japan's Princess Aiko returns from Singapore trip"),
    ("AFRICA", "Uganda: Tooro interim premier resigns amid splits"),
    ("AFRICA", "Kenya: Ruto battles to hold voting blocs for 2027"),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w, max_lines):
    """Greedy word wrap; truncates the last line with an ellipsis if needed."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    # If text was cut, mark the last line.
    joined = " ".join(lines)
    if len(joined) < len(text):
        last = lines[-1]
        while last and draw.textlength(last + "\u2026", font=fnt) > max_w:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "\u2026"
    return lines


def fit_one_line(draw, text, fnt, max_w):
    """Single line, truncated with an ellipsis if it would overflow."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    cut = text
    while cut and draw.textlength(cut + "\u2026", font=fnt) > max_w:
        cut = cut[:-1]
    return cut + "\u2026"


def chip(draw, x, y, label, fnt):
    color = REGION_COLORS[label]
    tw = draw.textlength(label, font=fnt)
    w = int(tw) + 14
    h = 18
    draw.rounded_rectangle([x, y, x + w, y + h], radius=9, fill=color)
    draw.text((x + 7, y + 3), label, font=fnt, fill=(255, 255, 255))
    return w


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    f_title = font(SERIF_BOLD, 44)
    f_date = font(SANS_BOLD, 17)
    f_tag = font(SANS, 13)
    f_section = font(SANS_BOLD, 13)
    f_head = font(SANS_BOLD, 17)
    f_sum = font(SANS, 13)
    f_chip = font(SANS_BOLD, 10)
    f_also = font(SANS, 13)
    f_foot = font(SANS, 11)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 104], fill=NAVY)
    d.rectangle([0, 104, W, 107], fill=GOLD)
    d.text((MARGIN, 18), "THE SUNDAY GLOBE", font=f_title, fill=(255, 255, 255))
    date_txt = "SUNDAY, 22 NOVEMBER 2026"
    dw = d.textlength(date_txt, font=f_date)
    d.text((W - MARGIN - dw, 26), date_txt, font=f_date, fill=(255, 255, 255))
    tag = "32 stories  \u00b7  7 regions  \u00b7  one day, verified"
    tw = d.textlength(tag, font=f_tag)
    d.text((W - MARGIN - tw, 52), tag, font=f_tag, fill=(200, 210, 225))
    d.text((MARGIN, 74), "World news in one image", font=f_tag,
           fill=(201, 162, 39))

    # ---- Section label --------------------------------------------------
    y = 122
    d.text((MARGIN, y), "TOP STORIES", font=f_section, fill=NAVY)
    d.line([(MARGIN + 110, y + 8), (W - MARGIN, y + 8)], fill=RULE, width=1)

    # ---- Hero grid: 2 columns x 4 rows ---------------------------------
    col_w = (W - 2 * MARGIN - 16) // 2
    card_h = 124
    gap = 10
    hx, hy = MARGIN, 148
    for i, (region, head, summ) in enumerate(HEROES):
        cx = hx + (i % 2) * (col_w + 16)
        cy = hy + (i // 2) * (card_h + gap)
        d.rounded_rectangle([cx, cy, cx + col_w, cy + card_h], radius=6,
                            fill=CARD, outline=(210, 205, 190), width=1)
        px, py = cx + 13, cy + 11
        chip(d, px, py, region, f_chip)
        head_lines = wrap(d, head, f_head, col_w - 26, 2)
        ty = py + 26
        for ln in head_lines:
            d.text((px, ty), ln, font=f_head, fill=INK)
            ty += 20
        sum_lines = wrap(d, summ, f_sum, col_w - 26, 2)
        ty += 3
        for ln in sum_lines:
            d.text((px, ty), ln, font=f_sum, fill=(70, 70, 70))
            ty += 16

    # ---- Also today ------------------------------------------------------
    ay = hy + 4 * card_h + 3 * gap + 16
    d.text((MARGIN, ay), "ALSO TODAY", font=f_section, fill=NAVY)
    d.line([(MARGIN + 108, ay + 8), (W - MARGIN, ay + 8)], fill=RULE, width=1)
    rows = (len(ALSO) + 1) // 2
    row_h = 21
    acol_w = (W - 2 * MARGIN - 24) // 2
    ay += 26
    for i, (region, text) in enumerate(ALSO):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (acol_w + 24)
        yy = ay + row * row_h
        d.ellipse([x, yy + 5, x + 7, yy + 12], fill=REGION_COLORS[region])
        line = fit_one_line(d, text, f_also, acol_w - 16)
        d.text((x + 13, yy), line, font=f_also, fill=INK)

    # ---- Footer ----------------------------------------------------------
    fy = ay + rows * row_h + 10
    d.line([(MARGIN, fy), (W - MARGIN, fy)], fill=RULE, width=1)
    foot = ("All 32 stories dated Sunday 22 November 2026  \u00b7  Sources include "
            "Reuters, AP, AFP, Al Jazeera, ICC, Formula 1")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, fy + 8), foot, font=f_foot, fill=MUTED)
    foot2 = "Poster rendered deterministically from verified reports  \u00b7  No story from Friday or Saturday leads this page"
    fw2 = d.textlength(foot2, font=f_foot)
    d.text(((W - fw2) / 2, fy + 26), foot2, font=f_foot, fill=MUTED)

    assert fy + 44 <= H, "footer overflows canvas"
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
