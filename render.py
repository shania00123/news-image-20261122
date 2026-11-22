# render.py — news-image-20261122 v3: "The Sunday Globe"
# Draws the 1024x1024 poster for Sunday 22 November 2026 from verified reports.
# Written fresh in this session. Deterministic: no network, no clock, no random.
# Run: python3 render.py  -> writes poster.png next to this file.
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "poster.png")

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

# ---------- palette ----------
PAPER = (248, 244, 233)
INK = (25, 25, 25)
MUTED = (90, 86, 76)
NAVY = (21, 34, 56)
GOLD = (201, 162, 39)
CARD = (255, 253, 246)
CARDBD = (216, 208, 189)
RULE = (180, 170, 145)
REGION = {
    "GLOBAL": (106, 63, 160),
    "MIDDLE EAST": (176, 48, 48),
    "AMERICAS": (26, 95, 180),
    "ASIA": (199, 116, 0),
    "OCEANIA": (14, 122, 107),
    "EUROPE": (46, 107, 48),
    "AFRICA": (138, 90, 0),
}
TAGC = {
    "CONFIRMED": (30, 125, 50),
    "CLAIM": (178, 106, 0),
    "REPORTED": (21, 101, 192),
    "TONIGHT": (106, 27, 154),
}

# ---------- data: 12 hero stories (all verified 22 Nov 2026) ----------
# scene keys: cop31, iran, f1, cricket, btc, korea, fbi, aukus, gaza, manipur, atp, fire
HEROES = [
    dict(n=1, region="GLOBAL", tag="CONFIRMED", scene="cop31",
         head="COP31 collapses with no deal",
         sub="The EU, Panama and the Marshall Islands reject a fourth draft that never names fossil fuels; Kurum concedes 'no agreement' after 44 hours of overtime.",
         src="Reuters / CNN"),
    dict(n=2, region="MIDDLE EAST", tag="CLAIM", scene="iran",
         head="Iran strikes US bases in Bahrain",
         sub="The IRGC claims two Patriot radars destroyed at Al Rifa and Awali; Bahrain says a plant burned and two were hurt as two tankers are hit in Hormuz on day 130.",
         src="Al Jazeera / Reuters"),
    dict(n=3, region="AMERICAS", tag="CONFIRMED", scene="f1",
         head="Verstappen wins wild Las Vegas GP",
         sub="The Red Bull star beats Norris by 0.639s after 35 lead changes and 352 overtakes; Piastri takes third from 17th, Russell hits the wall and ends ninth.",
         src="Formula 1"),
    dict(n=4, region="ASIA", tag="CONFIRMED", scene="cricket",
         head="India declare a record 720 for 9",
         sub="Rahul hits 136 and Pant 128 in Wellington, the highest Test total ever in New Zealand; the first seven partnerships all pass 50 as the hosts trail by 233.",
         src="Cricinfo"),
    dict(n=5, region="GLOBAL", tag="CONFIRMED", scene="btc",
         head="Bitcoin back above $60,000",
         sub="The token closes Sunday at $60,884, up from a $55,130 low on Saturday — its lowest since September 2024 — but still down 26% in 30 days.",
         src="Finnhub / CoinGecko"),
    dict(n=6, region="ASIA", tag="CONFIRMED", scene="korea",
         head="Seoul minister quits over AI cheating",
         sub="Education chief Choi Kyo-jin resigns and President Lee accepts within the hour; 111 device cases were caught at the Suneung, taken by 550,000 students.",
         src="AFP"),
    dict(n=7, region="AMERICAS", tag="REPORTED", scene="fbi",
         head="Trump shrugs off FBI database hack",
         sub="“It’s not good,” the president says of the NCIC breach first reported by CNN on Friday — then spins it as a way to expose the ‘Russia, Russia, Russia hoax’.",
         src="CNN / Fox News"),
    dict(n=8, region="OCEANIA", tag="CONFIRMED", scene="aukus",
         head="Australia slams US office on AUKUS",
         sub="Defence chief Marles calls the CBO ‘wrong’ for warning Virginia-class sales could shrink the US attack-sub fleet through 2060; Canberra has pledged A$368bn.",
         src="Reuters"),
    dict(n=9, region="MIDDLE EAST", tag="CONFIRMED", scene="gaza",
         head="Two killed in Gaza as truce frays",
         sub="An Israeli strike in Khan Younis kills two on Sunday, taking the toll since the October 2025 ceasefire to 1,675; Hamas demands emergency talks.",
         src="WAFA / AFP"),
    dict(n=10, region="ASIA", tag="REPORTED", scene="manipur",
         head="Manipur liquor toll reaches 17",
         sub="Deaths since Wednesday climb as 230 stay in hospital, 38 on dialysis; six arrested and 4,600 litres seized after the toxic batch spread through Chandel district.",
         src="Xinhua / Reuters"),
    dict(n=11, region="EUROPE", tag="TONIGHT", scene="atp",
         head="Zverev v Alcaraz for ATP Finals",
         sub="The world No. 1 meets Alcaraz in Turin at 18:00 CET for the season’s last title and $5,171,000; Alcaraz leads their series 7–6 and chases a first Finals crown.",
         src="ATP"),
    dict(n=12, region="ASIA", tag="CONFIRMED", scene="fire",
         head="Hunt for 36 missing after factory fire",
         sub="Rescuers comb the burnt Fonusa Agung Mulia candy plant in Cikande after Saturday’s blaze; 300 were inside, 15 rescued, 3 dead, and police put the missing near 50.",
         src="Reuters"),
]

# ---------- data: 28 more stories, one readable line each ----------
ALSO = [
    ("EUROPE", "Kyiv drone collapses block; 14 missing", "The Hindu"),
    ("EUROPE", "ATP doubles final at 15:00 CET, Turin", "ATP"),
    ("AMERICAS", "CISA: VMware flaw exploited; patch by Mon", "CISA"),
    ("AMERICAS", "US blocks China AI-chip remote access", ""),
    ("MIDDLE EAST", "Iraq PM to visit Cairo on Monday", "EIN"),
    ("MIDDLE EAST", "Eisenkot tasked to form Israeli govt", ""),
    ("AMERICAS", "St. Johns River breaks 73-year record", ""),
    ("AMERICAS", "California braces for record king tides", "NWS"),
    ("AMERICAS", "Messi avoids red as Inter Miami lose", "Al Jazeera"),
    ("EUROPE", "UK-EU food deal hailed by British firms", "Guardian"),
    ("EUROPE", "Spain faces uncertainty before 29 Nov vote", ""),
    ("ASIA", "China, ASEAN struggle over sea code", ""),
    ("EUROPE", "Jewellery icon Paolo Bulgari dies at 89", ""),
    ("EUROPE", "Europe sees new protests over costs", ""),
    ("AMERICAS", "Democrats seek to unwind Trump tax rules", "FT"),
    ("AMERICAS", "Conservative media split in Trump camp", "Guardian"),
    ("MIDDLE EAST", "Iran claims 20th US MQ-1 drone downed", "IRGC"),
    ("MIDDLE EAST", "Hormuz transits 263/week, 65% below norm", "UKMTO"),
    ("AFRICA", "Bayelsa boat tragedy: NEMA team deployed", "Vanguard"),
    ("AFRICA", "Kenya awards minerals deal to US group", "Africanews"),
    ("AFRICA", "Chopper, drones hunt missing Aberdare hiker", "Standard"),
    ("AFRICA", "AFCON 2027 hosts named; Nairobi sole in Kenya", "CAF"),
    ("AFRICA", "Nigeria moves to end jail for suicide bids", "BBC"),
    ("AFRICA", "ANC fights to keep South Africa’s cities", "BBC"),
    ("AFRICA", "Sudan: Khartoum homes hit; 15 killed", "News Central"),
    ("GLOBAL", "Super El Nino to worsen global hunger", ""),
    ("GLOBAL", "WHO warns on antibiotic resistance", ""),
    ("EUROPE", "Dashcam shows missile strike on Lviv", ""),
]

# ---------- data: day in numbers / day by hours / date check ----------
NUMBERS = [
    ("0.639s", "Verstappen’s F1 margin"),
    ("720/9", "India’s record Test total"),
    ("$60,884", "Bitcoin’s Sunday close"),
    ("44 hours", "COP31 overtime to collapse"),
    ("25", "tankers hit in 7 days"),
    ("111", "Suneung cheating cases"),
]
HOURS = [
    ("10:04", "Seoul", "Education minister resigns over AI cheating"),
    ("15:40", "Wellington", "India declare 720/9, a record in New Zealand"),
    ("Afternoon", "Antalya", "COP31 collapses; Kurum concedes no deal"),
    ("18:00", "Turin", "ATP singles final: Zverev v Alcaraz"),
]
DATECHECK = [
    ("G20 Johannesburg declaration", "Sat 22 Nov 2025"),
    ("G20: Argentina walks out", "Sat 22 Nov 2025"),
    ("Trump–Xi–Putin summit, Shenzhen", "Thu 19–Fri 20 Nov"),
    ("ICJ: Myanmar guilty of Rohingya genocide", "Thu 19 Nov"),
    ("El Chapo Isidro captured, Guasave", "Fri 20 Nov"),
    ("Kryvyi Rih double-tap strike", "Fri 20 Nov"),
    ("Russia missiles enter Polish airspace", "Fri 20 Nov"),
    ("EU–Indonesia CEPA signed, Brussels", "Sat 21 Nov"),
    ("Basra power station fire", "Sat 21 Nov"),
    ("Sparta II cargo ship on fire, Baltic", "Sat 21 Nov"),
]
VERDICT = ("Sunday was the day the climate talks failed: COP31 collapsed in Antalya "
           "after 44 hours of overtime — the first COP breakdown since 2009.")

# ---------- text helpers ----------
def wrap(draw, text, font, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_h(draw, lines, font):
    return sum(draw.textbbox((0, 0), l, font=font)[3] for l in lines)

# ---------- dot-matrix world map ----------
# Land mask: (row, col0, col1) ranges on a 28-row x 60-col grid.
# Row 0 = lat 79-84N, row 27 = lat 51-56S; col 0 = lon 180-174W.
LAND = [
    (0, [(15, 16), (20, 25), (31, 32)]),
    (1, [(2, 6), (10, 16), (20, 25), (31, 33), (46, 49), (52, 54)]),
    (2, [(2, 6), (7, 19), (20, 26), (33, 34), (40, 59)]),
    (3, [(2, 7), (7, 20), (30, 35), (36, 59)]),
    (4, [(3, 8), (8, 20), (27, 27), (30, 35), (36, 59), (55, 56)]),
    (5, [(8, 21), (29, 58)]),
    (6, [(9, 21), (28, 57)]),
    (7, [(10, 19), (28, 53)]),
    (8, [(10, 19), (28, 54)]),
    (9, [(10, 19), (27, 53)]),
    (10, [(11, 18), (27, 50)]),
    (11, [(11, 16), (27, 50)]),
    (12, [(12, 15), (27, 48)]),
    (13, [(14, 16), (27, 31), (36, 39), (41, 43), (45, 48)]),
    (14, [(15, 17), (27, 31), (35, 37), (45, 47), (49, 50)]),
    (15, [(17, 20), (27, 33), (35, 38), (45, 50)]),
    (16, [(17, 22), (31, 35), (36, 38), (47, 52)]),
    (17, [(17, 23), (31, 36), (48, 53)]),
    (18, [(17, 23), (32, 36), (51, 54)]),
    (19, [(17, 23), (32, 36), (36, 38), (48, 53)]),
    (20, [(17, 23), (31, 35), (36, 37), (48, 54)]),
    (21, [(17, 22), (31, 35), (48, 54)]),
    (22, [(17, 21), (31, 34), (48, 54)]),
    (23, [(17, 20), (31, 33), (49, 53), (57, 58)]),
    (24, [(17, 19), (53, 54), (57, 58)]),
    (25, [(17, 18), (57, 58)]),
    (26, [(17, 18)]),
    (27, [(17, 18)]),
]
# Numbered pins (row, col) for the 12 heroes. 5 = Bitcoin (global; shown London).
PINS = {
    1: (9, 35), 2: (11, 38), 3: (9, 10), 4: (25, 59), 5: (6, 30),
    6: (9, 51), 7: (9, 17), 8: (23, 54), 9: (11, 36), 10: (11, 45),
    11: (8, 31), 12: (18, 47),
}

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 238, 244), outline=RULE)
    cw, ch = w / 60.0, h / 28.0
    for row, spans in LAND:
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = x + (c + 0.5) * cw
                cy = y + (row + 0.5) * ch
                d.ellipse([cx - 1.3, cy - 1.3, cx + 1.3, cy + 1.3], fill=(120, 130, 145))
    fpin = F(SANSB, 6)
    for n, (row, col) in PINS.items():
        cx = x + (col + 0.5) * cw
        cy = y + (row + 0.5) * ch
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(176, 48, 48), outline=(255, 255, 255))
        t = str(n)
        tw = d.textlength(t, font=fpin)
        d.text((cx - tw / 2, cy - 3), t, font=fpin, fill=(255, 255, 255))

# ---------- drawn scenes (each fills a w x h panel at x, y) ----------
def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(15, 76, 92))
    cx, cy, r = x + w // 2, y + h // 2 - 8, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(127, 200, 232))
    d.ellipse([cx - 22, cy - 18, cx - 2, cy - 4], fill=(46, 139, 87))
    d.ellipse([cx + 4, cy + 6, cx + 24, cy + 20], fill=(46, 139, 87))
    d.ellipse([cx + 8, cy - 24, cx + 26, cy - 10], fill=(46, 139, 87))
    # jagged crack
    d.line([(cx - 20, cy - 34), (cx - 8, cy - 12), (cx - 16, cy + 2),
            (cx + 2, cy + 18), (cx - 4, cy + 34)], fill=(25, 25, 25), width=3)
    d.rectangle([x + 8, y + h - 26, x + w - 8, y + h - 8], fill=(176, 48, 48))
    f = F(SANSB, 12)
    t = "NO DEAL"
    d.text((x + w // 2 - d.textlength(t, font=f) // 2, y + h - 24), t, font=f, fill=(255, 255, 255))

def scene_iran(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 58))
    # radar dish
    cx, cy = x + 34, y + h - 34
    d.pieslice([cx - 26, cy - 26, cx + 26, cy + 26], 180, 360, fill=(200, 205, 215))
    d.line([(cx, cy), (cx + 24, cy - 24)], fill=(255, 200, 60), width=3)
    d.ellipse([cx + 20, cy - 28, cx + 28, cy - 20], fill=(255, 200, 60))
    d.ellipse([cx - 6, cy - 26, cx + 2, cy - 18], fill=(255, 200, 60))
    # missile arc + explosion
    d.line([(x + 52, y + h - 20), (x + 66, y + 44), (x + 82, y + 22)], fill=(255, 255, 255), width=2)
    d.polygon([(x + 78, y + 12), (x + 88, y + 26), (x + 82, y + 30), (x + 74, y + 20)], fill=(220, 220, 220))
    for dx, dy, rr in [(0, 0, 7), (-9, 5, 5), (9, 5, 5), (0, -9, 5)]:
        d.ellipse([x + 88 + dx - rr, y + 12 + dy - rr, x + 88 + dx + rr, y + 12 + dy + rr],
                  fill=(255, 120, 40))
    d.rectangle([x + 6, y + 6, x + 46, y + 22], fill=(176, 48, 48))
    f = F(SANSB, 10)
    d.text((x + 10, y + 8), "DAY 130", font=f, fill=(255, 255, 255))

def scene_f1(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 26, 46))
    # checkered strip
    seg = w // 8
    for i in range(8):
        c = (255, 255, 255) if i % 2 == 0 else (20, 20, 20)
        d.rectangle([x + i * seg, y + 6, x + (i + 1) * seg, y + 18], fill=c)
    # speed lines
    for yy in (44, 54, 64):
        d.line([(x + 4, y + yy), (x + 30, y + yy)], fill=(255, 255, 255), width=2)
    # car body
    bx, by = x + 30, y + 52
    d.polygon([(bx, by + 18), (bx + 8, by + 2), (bx + 34, by), (bx + 52, by + 6),
               (bx + 64, by + 12), (bx + 64, by + 18)], fill=(200, 30, 30))
    d.polygon([(bx + 14, by + 2), (bx + 20, by - 10), (bx + 38, by - 10), (bx + 40, by)],
              fill=(20, 20, 30))
    d.polygon([(bx + 62, by + 6), (bx + 72, by + 8), (bx + 72, by + 16), (bx + 62, by + 16)],
              fill=(200, 30, 30))
    for wx in (bx + 12, bx + 52):
        d.ellipse([wx - 8, by + 14, wx + 8, by + 30], fill=(15, 15, 15))
        d.ellipse([wx - 3, by + 19, wx + 3, by + 25], fill=(180, 180, 180))
    f = F(SANSB, 11)
    t = "0.639s"
    d.text((x + w - d.textlength(t, font=f) - 6, y + h - 20), t, font=f, fill=(255, 200, 60))

def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 107, 52))
    # pitch
    d.rectangle([x + 14, y + 18, x + w - 14, y + h - 30], fill=(210, 180, 120))
    # stumps
    for sx in (x + 26, x + 32, x + 38):
        d.line([(sx, y + 26), (sx, y + 48)], fill=(255, 220, 80), width=3)
    # batsman
    d.ellipse([x + 58, y + 30, x + 70, y + 42], fill=(240, 200, 160))
    d.polygon([(x + 56, y + 44), (x + 72, y + 44), (x + 76, y + 66), (x + 54, y + 66)],
              fill=(255, 255, 255))
    d.line([(x + 58, y + 66), (x + 54, y + 88)], fill=(20, 20, 20), width=4)
    d.line([(x + 70, y + 66), (x + 76, y + 88)], fill=(20, 20, 20), width=4)
    # bat
    d.line([(x + 72, y + 48), (x + 84, y + 70)], fill=(160, 110, 50), width=5)
    # ball
    d.ellipse([x + 84, y + 74, x + 92, y + 82], fill=(200, 30, 30))
    f = F(SANSB, 14)
    t = "720/9"
    d.text((x + w // 2 - d.textlength(t, font=f) // 2, y + h - 26), t, font=f, fill=(255, 255, 255))

def scene_btc(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 26, 8))
    # rising chart
    pts = [(x + 8, y + 78), (x + 24, y + 66), (x + 40, y + 70), (x + 56, y + 48),
           (x + 72, y + 52), (x + 88, y + 30)]
    d.line(pts, fill=(60, 200, 110), width=3)
    d.polygon([(x + 82, y + 24), (x + 90, y + 30), (x + 84, y + 38)], fill=(60, 200, 110))
    # coin
    cx, cy, r = x + w // 2, y + 44, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(247, 147, 26), outline=(255, 210, 120), width=2)
    f = F(SANSB, 15)
    t = "BTC"
    d.text((cx - d.textlength(t, font=f) // 2, cy - 9), t, font=f, fill=(255, 255, 255))
    f2 = F(SANSB, 11)
    t2 = "$60,884"
    d.text((x + w // 2 - d.textlength(t2, font=f2) // 2, y + h - 20), t2, font=f2, fill=(255, 200, 60))

def scene_korea(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 230, 210))
    # exam paper
    d.rectangle([x + 14, y + 10, x + w - 30, y + h - 26], fill=(255, 255, 255), outline=(150, 140, 120))
    for i, yy in enumerate((26, 38, 50, 62)):
        d.line([(x + 22, y + yy), (x + w - 38, y + yy)], fill=(180, 175, 160), width=2)
    d.rectangle([x + 22, y + 16, x + 44, y + 22], fill=(200, 60, 60))
    # pencil
    d.polygon([(x + 72, y + 24), (x + 92, y + 24), (x + 92, y + 84), (x + 82, y + 96),
               (x + 72, y + 84)], fill=(255, 200, 60))
    d.polygon([(x + 82, y + 96), (x + 76, y + 86), (x + 88, y + 86)], fill=(230, 190, 150))
    # AI chip with red ban
    d.rectangle([x + 16, y + h - 34, x + 52, y + h - 10], fill=(40, 40, 60))
    f = F(SANSB, 11)
    d.text((x + 24, y + h - 29), "AI", font=f, fill=(255, 255, 255))
    d.ellipse([x + 56, y + h - 32, x + 74, y + h - 14], outline=(200, 30, 30), width=3)
    d.line([(x + 58, y + h - 30), (x + 72, y + h - 16)], fill=(200, 30, 30), width=3)

def scene_fbi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 24, 36))
    # laptop
    d.rectangle([x + 16, y + 22, x + w - 16, y + 74], fill=(60, 70, 95), outline=(150, 160, 190))
    d.rectangle([x + 10, y + 74, x + w - 10, y + 82], fill=(120, 130, 155))
    f = F(SANSB, 13)
    t = "NCIC"
    d.text((x + w // 2 - d.textlength(t, font=f) // 2, y + 40), t, font=f, fill=(255, 255, 255))
    # padlock
    lx, ly = x + w - 34, y + h - 34
    d.arc([lx - 7, ly - 12, lx + 7, ly + 2], 180, 360, fill=(255, 200, 60), width=3)
    d.rectangle([lx - 9, ly - 2, lx + 9, ly + 12], fill=(255, 200, 60))
    # warning triangle
    tx, ty = x + 12, y + h - 36
    d.polygon([(tx, ty), (tx + 22, ty), (tx + 11, ty - 18)], fill=(230, 180, 0))
    f2 = F(SANSB, 12)
    d.text((tx + 8, ty - 15), "!", font=f2, fill=(20, 20, 20))

def scene_aukus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 90, 140))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(14, 60, 100))
    # waves
    for wx in range(0, w, 16):
        d.arc([x + wx - 4, y + h - 30, x + wx + 12, y + h - 16], 180, 360,
              fill=(255, 255, 255), width=2)
    # submarine
    sx, sy = x + 12, y + 44
    d.rounded_rectangle([sx, sy, sx + 78, sy + 24], radius=12, fill=(50, 55, 65))
    d.rectangle([sx + 30, sy - 12, sx + 48, sy], fill=(50, 55, 65))
    d.line([(sx + 38, sy - 12), (sx + 38, sy - 20)], fill=(180, 180, 180), width=2)
    d.ellipse([sx + 62, sy + 8, sx + 70, sy + 16], fill=(255, 200, 60))
    for bx, by, br in [(sx + 20, sy - 24, 3), (sx + 30, sy - 32, 2), (sx + 44, sy - 28, 2)]:
        d.ellipse([bx - br, by - br, bx + br, by + br], outline=(255, 255, 255), width=1)
    f = F(SANSB, 10)
    d.text((x + 8, y + 8), "A$368bn", font=f, fill=(255, 255, 255))

def scene_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(138, 122, 106))
    # buildings
    d.rectangle([x + 10, y + 40, x + 40, y + h - 14], fill=(70, 66, 62))
    d.rectangle([x + 46, y + 24, x + 78, y + h - 14], fill=(90, 84, 78))
    d.rectangle([x + 82, y + 52, x + w - 8, y + h - 14], fill=(70, 66, 62))
    for wx in (18, 30, 54, 66, 88):
        for wy in (48, 62, 76):
            d.rectangle([x + wx, y + wy, x + wx + 5, y + wy + 6], fill=(255, 220, 120))
    # smoke plume
    for sx, sy, sr in [(62, 16, 7), (70, 8, 9), (58, 4, 6)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(200, 195, 185))
    # dove
    dx, dy = x + 16, y + 14
    d.ellipse([dx, dy, dx + 16, dy + 8], fill=(255, 255, 255))
    d.arc([dx + 2, dy - 6, dx + 16, dy + 6], 180, 360, fill=(255, 255, 255), width=2)

def scene_manipur(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 230, 230))
    # bottle
    bx, by = x + 26, y + 18
    d.rectangle([bx + 8, by, bx + 20, by + 14], fill=(60, 40, 20))
    d.polygon([(bx, by + 14), (bx + 28, by + 14), (bx + 34, by + 30), (bx + 34, by + 70),
               (bx, by + 70)], fill=(90, 60, 30))
    d.rectangle([bx + 6, by + 44, bx + 28, by + 62], fill=(240, 230, 200))
    # red X over bottle
    d.line([(bx - 4, by + 8), (bx + 40, by + 76)], fill=(200, 30, 30), width=5)
    d.line([(bx + 40, by + 8), (bx - 4, by + 76)], fill=(200, 30, 30), width=5)
    # medical cross
    cx, cy = x + w - 30, y + h - 30
    d.rectangle([cx - 4, cy - 12, cx + 4, cy + 12], fill=(30, 125, 50))
    d.rectangle([cx - 12, cy - 4, cx + 12, cy + 4], fill=(30, 125, 50))

def scene_atp(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 74, 143))
    # tennis ball
    cx, cy, r = x + 34, y + 44, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 230, 60))
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(255, 255, 255), width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 120, 240, fill=(255, 255, 255), width=3)
    # trophy
    tx, ty = x + 58, y + 26
    d.polygon([(tx, ty), (tx + 26, ty), (tx + 22, ty + 22), (tx + 4, ty + 22)], fill=(255, 200, 60))
    d.arc([tx - 6, ty + 2, tx + 6, ty + 16], 90, 270, fill=(255, 200, 60), width=3)
    d.arc([tx + 20, ty + 2, tx + 32, ty + 16], 270, 90, fill=(255, 200, 60), width=3)
    d.rectangle([tx + 10, ty + 22, tx + 16, ty + 34], fill=(255, 200, 60))
    d.rectangle([tx + 2, ty + 34, tx + 24, ty + 40], fill=(255, 200, 60))
    f = F(SANSB, 11)
    t = "18:00 CET"
    d.text((x + w // 2 - d.textlength(t, font=f) // 2, y + h - 20), t, font=f, fill=(255, 255, 255))

def scene_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 58, 56))
    # factory
    d.rectangle([x + 10, y + 52, x + w - 10, y + h - 12], fill=(40, 40, 42))
    for i in range(4):
        sx = x + 12 + i * 22
        d.polygon([(sx, y + 52), (sx + 11, y + 40), (sx + 22, y + 52)], fill=(40, 40, 42))
    d.rectangle([x + w - 26, y + 22, x + w - 16, y + 52], fill=(70, 66, 62))
    # flames
    for fx, fh in [(22, 26), (44, 34), (66, 28), (84, 22)]:
        d.polygon([(x + fx - 8, y + 52), (x + fx, y + 52 - fh), (x + fx + 8, y + 52)],
                  fill=(255, 140, 20))
        d.polygon([(x + fx - 4, y + 52), (x + fx, y + 52 - fh + 12), (x + fx + 4, y + 52)],
                  fill=(255, 210, 60))
    # smoke
    for sx, sy, sr in [(30, 14, 7), (46, 8, 9), (64, 14, 6)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(180, 175, 165))
    f = F(SANSB, 11)
    t = "36 MISSING"
    d.text((x + w // 2 - d.textlength(t, font=f) // 2, y + h - 20), t, font=f, fill=(255, 200, 60))

SCENES = {
    "cop31": scene_cop31, "iran": scene_iran, "f1": scene_f1, "cricket": scene_cricket,
    "btc": scene_btc, "korea": scene_korea, "fbi": scene_fbi, "aukus": scene_aukus,
    "gaza": scene_gaza, "manipur": scene_manipur, "atp": scene_atp, "fire": scene_fire,
}

# ---------- layout ----------
W, H = 1024, 1024
M = 14  # outer margin

def section_head(d, x, y, w, title, right=None):
    f = F(SANSB, 12)
    d.text((x, y), title, font=f, fill=NAVY)
    d.line([(x, y + 17), (x + w, y + 17)], fill=GOLD, width=2)
    if right:
        fr = F(SANS, 9)
        d.text((x + w - d.textlength(right, font=fr), y + 2), right, font=fr, fill=MUTED)

def draw_hero(d, h, x, y, w, hh):
    d.rectangle([x, y, x + w, y + hh], fill=CARD, outline=CARDBD)
    sw = 96
    SCENES[h["scene"]](d, x + 1, y + 1, sw, hh - 2)
    tx = x + sw + 8
    tw = w - sw - 14
    # number badge + region + tag
    rc = REGION[h["region"]]
    d.ellipse([tx, y + 7, tx + 15, y + 22], fill=rc)
    fn = F(SANSB, 9)
    t = str(h["n"])
    d.text((tx + 8 - d.textlength(t, font=fn) / 2, y + 9), t, font=fn, fill=(255, 255, 255))
    fr = F(SANSB, 8)
    d.text((tx + 20, y + 9), h["region"], font=fr, fill=rc)
    tc = TAGC[h["tag"]]
    tagw = d.textlength(h["tag"], font=fr) + 8
    d.rounded_rectangle([tx + tw - tagw, y + 6, tx + tw, y + 20], radius=3, fill=tc)
    d.text((tx + tw - tagw + 4, y + 9), h["tag"], font=fr, fill=(255, 255, 255))
    # headline (max 2 lines)
    fh = F(SANSB, 12)
    lines = wrap(d, h["head"], fh, tw)
    yy = y + 26
    for ln in lines[:2]:
        d.text((tx, yy), ln, font=fh, fill=INK)
        yy += 15
    # sub (max 4 lines)
    fs = F(SANS, 9)
    slines = wrap(d, h["sub"], fs, tw)
    yy += 2
    for ln in slines[:4]:
        d.text((tx, yy), ln, font=fs, fill=(50, 48, 44))
        yy += 12
    # source
    fsrc = F(SANS, 8)
    d.text((tx, y + hh - 11), "Source: " + h["src"], font=fsrc, fill=MUTED)

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # ---- masthead: 0-84 ----
    d.rectangle([0, 0, W, 84], fill=NAVY)
    d.rectangle([0, 81, W, 84], fill=GOLD)
    fm = F(SERIFB, 38)
    d.text((M, 6), "THE SUNDAY GLOBE", font=fm, fill=(255, 255, 255))
    fmd = F(SANSB, 13)
    d.text((M, 50), "SUNDAY 22 NOVEMBER 2026", font=fmd, fill=(255, 210, 90))
    fr = F(SANS, 11)
    d.text((M, 68), "40 stories  ·  7 regions  ·  12 drawn scenes  ·  every story checked against its date",
           font=fr, fill=(200, 205, 220))
    counts = [("AMERICAS 9", "AMERICAS"), ("EUROPE 8", "EUROPE"), ("AFRICA 7", "AFRICA"),
              ("M. EAST 6", "MIDDLE EAST"), ("ASIA 5", "ASIA"), ("GLOBAL 4", "GLOBAL"),
              ("OCEANIA 1", "OCEANIA")]
    fx = W - M
    fs2 = F(SANSB, 10)
    for label, reg in counts:
        tw = d.textlength(label, font=fs2)
        fx -= tw + 18
        d.ellipse([fx, 12, fx + 9, 21], fill=REGION[reg])
        d.text((fx + 12, 11), label, font=fs2, fill=(255, 255, 255))
    d.text((W - M - d.textlength("STORIES BY REGION", font=F(SANS, 9)), 48),
           "STORIES BY REGION", font=F(SANS, 9), fill=(180, 185, 200))
    d.text((W - M - d.textlength("One day. One image. Nothing from another day.",
                                 font=F(SANS, 10)), 64),
           "One day. One image. Nothing from another day.", font=F(SANS, 10),
           fill=(200, 205, 220))
    # ---- heroes: 3 cols x 4 rows, 92-574 ----
    hy, hh, gap = 92, 116, 6
    cw = (W - 2 * M - 2 * gap) // 3
    for i, h in enumerate(HEROES):
        r, c = divmod(i, 3)
        draw_hero(d, h, M + c * (cw + gap), hy + r * (hh + gap), cw, hh)
    # ---- day in numbers: 580-636 ----
    ny = 580
    section_head(d, M, ny, W - 2 * M, "THE DAY IN NUMBERS")
    nbox = 6
    bw = (W - 2 * M - (nbox - 1) * gap) // nbox
    for i, (big, small) in enumerate(NUMBERS):
        bx = M + i * (bw + gap)
        d.rectangle([bx, ny + 22, bx + bw, ny + 56], fill=CARD, outline=CARDBD)
        fb = F(SANSB, 16)
        d.text((bx + bw // 2 - d.textlength(big, font=fb) // 2, ny + 24), big, font=fb, fill=NAVY)
        fsl = F(SANS, 8)
        d.text((bx + bw // 2 - d.textlength(small, font=fsl) // 2, ny + 44), small, font=fsl, fill=MUTED)
    # ---- day by hours: 642-714 ----
    hy2 = 642
    section_head(d, M, hy2, W - 2 * M, "THE DAY BY HOURS", right="All times local")
    fht = F(SANSB, 10)
    fhc = F(SANS, 10)
    yy = hy2 + 24
    for tm, city, what in HOURS:
        d.text((M, yy), tm, font=fht, fill=NAVY)
        d.text((M + 74, yy), city, font=fht, fill=REGION["GLOBAL"])
        d.text((M + 150, yy), what, font=fhc, fill=INK)
        yy += 12
    # ---- also today: 720-864, 3 cols x 10 rows ----
    ay = 720
    section_head(d, M, ay, W - 2 * M, "ALSO TODAY — 28 MORE STORIES FROM THE SAME DAY")
    colw = (W - 2 * M - 2 * gap) // 3
    fa = F(SANS, 9)
    for i, (reg, txt, src) in enumerate(ALSO):
        c, r = divmod(i, 10)
        ax = M + c * (colw + gap)
        ayy = ay + 24 + r * 12
        d.ellipse([ax, ayy + 1, ax + 8, ayy + 9], fill=REGION[reg])
        line = txt + ("  — " + src if src else "")
        d.text((ax + 12, ayy), line, font=fa, fill=INK)
    # ---- bottom band: 870-1012 ----
    by = 870
    # map (left)
    mw = 348
    section_head(d, M, by, mw, "WHERE IT HAPPENED")
    draw_map(d, M, by + 22, mw, 76)
    fleg = F(SANS, 7)
    d.text((M, by + 102), "Pins: 1 COP31 · 2 Bahrain · 3 F1 · 4 Cricket · 5 Bitcoin · 6 Seoul",
           font=fleg, fill=MUTED)
    d.text((M, by + 112), "7 FBI · 8 AUKUS · 9 Gaza · 10 Manipur · 11 ATP · 12 Cikande",
           font=fleg, fill=MUTED)
    # date check (middle)
    dx = M + mw + 12
    dw = 330
    section_head(d, dx, by, dw, "DATE CHECK",
                 right="Left out on purpose — none is a 22 Nov story")
    fdc = F(SANS, 9)
    fdcb = F(SANSB, 9)
    yy = by + 24
    for what, when in DATECHECK:
        d.text((dx, yy), "✕  " + what, font=fdc, fill=INK)
        d.text((dx + dw - d.textlength(when, font=fdcb), yy), when, font=fdcb, fill=(176, 48, 48))
        yy += 11
    # right stack: how sure + verdict
    rx = dx + dw + 12
    rw = W - M - rx
    section_head(d, rx, by, rw, "HOW SURE ARE WE?")
    fhs = F(SANS, 9)
    yy = by + 24
    for tag, expl in [("CONFIRMED", "2+ major outlets, or an official source"),
                      ("REPORTED", "reported, not yet confirmed"),
                      ("CLAIM", "one side’s claim, not verified"),
                      ("TONIGHT", "scheduled, not yet played")]:
        tc = TAGC[tag]
        d.rounded_rectangle([rx, yy, rx + 74, yy + 13], radius=3, fill=tc)
        d.text((rx + 4, yy + 2), tag, font=F(SANSB, 8), fill=(255, 255, 255))
        d.text((rx + 78, yy + 1), expl, font=fhs, fill=INK)
        yy += 15
    vy = by + 84
    section_head(d, rx, vy, rw, "THE VERDICT")
    fv = F(SANS, 9)
    yy = vy + 22
    for ln in wrap(d, VERDICT, fv, rw):
        d.text((rx, yy), ln, font=fv, fill=INK)
        yy += 11
    # ---- footer ----
    d.line([(M, 1012), (W - M, 1012)], fill=RULE)
    ff = F(SANS, 8)
    d.text((M, 1014), "All 40 stories dated Sunday 22 November 2026 · Sources: Reuters, AP, AFP, "
           "Al Jazeera, Formula 1, Cricinfo, ATP, CNN, BBC · Rendered deterministically from verified "
           "reports · Fri markets: S&P 500 –3.7%, Nasdaq –5.3%",
           font=ff, fill=MUTED)
    img.save(OUT, "PNG")
    return OUT

if __name__ == "__main__":
    print(render())
