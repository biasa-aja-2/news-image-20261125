"""The World in One Day - Wednesday, 25 November 2026.

A one-page newspaper front page drawn entirely with the Python
standard library. No images are loaded, no network is used, and the
output is fully deterministic: two runs write identical bytes.

The page sums up the day's world news in 35 stories across 8 regions:
a lead on the Chen Jining probe in China, six feature stories,
twenty-four items in "The Day in Brief", and four more in the footer
strip. Every column carries its own illustration.

Writes entry.png into $MAKEFUN_OUTPUT_DIR (default /output).
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 241, 224)
CARD = (255, 253, 246)
INK = (28, 28, 28)
NAVY = (18, 34, 58)
RED = (178, 34, 34)
BLUE = (30, 80, 130)
TEAL = (16, 120, 110)
GOLD = (198, 148, 28)
GREEN = (46, 130, 66)
ORANGE = (214, 104, 34)
SKY = (140, 190, 224)
SEA = (24, 100, 160)
SAND = (224, 200, 146)
GREY = (120, 116, 106)
LIGHT = (234, 226, 206)
WHITE = (255, 255, 255)
DARKRED = (120, 20, 20)

# A 5x7 pixel font, drawn cell by cell. '#' is ink, '.' is empty.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
}
FONT.update({
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "'": (".....", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.###", "#..##"),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", "..#..", ".#..."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "#": ("#.#.#", "#.#.#", "#####", "#.#.#", "#####", "#.#.#", "#.#.#"),
})


class Canvas:
    """An RGB canvas with small drawing helpers."""

    def __init__(self):
        self.px = bytearray(bytes(PAPER) * W * H)

    def put(self, x, y, colour):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, colour):
        self.rect(x, y, w, 1, colour)

    def vline(self, x, y, h, colour):
        self.rect(x, y, 1, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.put(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, colour, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.put(xx, yy, colour)
                elif not fill and abs(d - r * r) <= r:
                    self.put(xx, yy, colour)

    def tri(self, x0, y0, x1, y1, x2, y2, colour):
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y1 - y2) * (xx - x2) + (x2 - x1) * (yy - y2)) / d
                b = ((y2 - y0) * (xx - x2) + (x0 - x2) * (yy - y2)) / d
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.put(xx, yy, colour)

    def glyph(self, x, y, ch, scale, colour):
        g = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(g):
            for col_i, cell in enumerate(row):
                if cell == "#":
                    self.rect(x + col_i * scale, y + row_i * scale,
                              scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        cx = x
        for ch in s.upper():
            self.glyph(cx, y, ch, scale, colour)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines."""
        words, lines, cur = s.split(" "), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, colour, max_w, max_lines=None,
             line_gap=2):
        lines = self.wrap(s, scale, max_w)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * (7 * scale + line_gap), ln, scale, colour)
        return y + len(lines) * (7 * scale + line_gap)


def write_png(canvas, path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- small scene illustrations (one per column) ----

def art_gate(c, x, y, w, h):
    """Beijing gate under a red sky, with a magnifier over a star."""
    c.rect(x, y, w, h, DARKRED)
    # skyline silhouettes along the bottom
    for bx, bh in ((0, 26), (70, 40), (250, 34), (320, 22)):
        c.rect(x + bx, y + h - 18 - bh, 40, bh, (90, 10, 10))
    c.rect(x, y + h - 18, w, 18, (90, 10, 10))
    # the gate, big and centred
    gx = x + w // 2
    c.rect(gx - 80, y + 26, 160, 10, GOLD)
    c.rect(gx - 68, y + 36, 136, 66, (150, 30, 30))
    c.rect(gx - 68, y + 36, 136, 5, GOLD)
    for i in range(6):
        ax = gx - 58 + i * 20
        c.rect(ax, y + 50, 11, 52, (60, 8, 8))
    c.rect(gx - 80, y + 102, 160, 8, GOLD)
    c.rect(gx - 90, y + 110, 180, 6, GOLD)
    # flag pole at the left
    c.rect(x + 14, y + h - 40, 34, 22, GOLD)
    c.line(x + 31, y + h - 40, x + 31, y + 12, GOLD)
    c.tri(x + 31, y + 12, x + 31, y + 32, x + 52, y + 22, RED)
    # magnifier over a gold star, bottom right
    sx, sy = x + w - 56, y + h - 48
    c.circle(sx, sy, 17, WHITE, fill=False)
    c.circle(sx, sy, 14, (255, 240, 180))
    c.line(sx + 12, sy + 12, sx + 26, sy + 26, WHITE)
    c.text(sx - 5, sy - 4, "*", 1, RED)


def art_ship(c, x, y, w, h):
    """Container ship on a grey sea, tariff per cent above."""
    c.rect(x, y, w, h, SKY)
    c.rect(x, y + h - 8, w, 8, SEA)
    # two rows of containers, all inside the box
    for i in range(6):
        c.rect(x + 20 + i * 44, y + h - 24, 20, 10, (200 - i * 16, 60, 40))
    for i in range(5):
        c.rect(x + 42 + i * 44, y + h - 36, 20, 10, (40, 90, 140))
    c.rect(x + 6, y + h - 14, w - 12, 4, INK)
    c.line(x + 8, y + h - 4, x + w - 8, y + h - 4, WHITE)
    c.text(x + w - 30, y + 2, "%", 2, RED)


def art_rocket(c, x, y, w, h):
    """Rocket climbing past stars into a dark sky."""
    c.rect(x, y, w, h, NAVY)
    for sx, sy in ((10, 6), (w - 16, 8), (22, 26), (w - 28, 30)):
        c.text(x + sx, y + sy, "*", 1, GOLD)
    cx = x + w // 2
    c.tri(cx, y + 2, cx - 9, y + 20, cx + 9, y + 20, WHITE)
    c.rect(cx - 9, y + 20, 18, 10, RED)
    c.rect(cx - 9, y + 30, 18, 3, GOLD)
    c.tri(cx - 7, y + 33, cx + 7, y + 33, cx, y + h - 2, ORANGE)
    c.rect(cx - 16, y + 22, 6, 9, BLUE)
    c.rect(cx + 10, y + 22, 6, 9, BLUE)
    c.circle(cx, y + 12, 4, SKY)


def art_blast(c, x, y, w, h):
    """Night blast over city rooftops, kept inside the box."""
    c.rect(x, y, w, h, (30, 28, 40))
    cx, cy = x + w // 2, y + h // 2
    for r, col in ((13, ORANGE), (9, GOLD), (5, WHITE)):
        c.circle(cx, cy, r, col)
    for ang in range(0, 360, 45):
        import math
        ex = cx + int(17 * math.cos(math.radians(ang)))
        ey = cy + int(17 * math.sin(math.radians(ang)))
        c.line(cx, cy, ex, ey, GOLD)
    for i, bw in enumerate((30, 24, 36, 20)):
        bx = x + 6 + i * (w // 4)
        bh = 10 + (i % 2) * 5
        c.rect(bx, y + h - bh, bw, bh, INK)


def art_pact(c, x, y, w, h):
    """Two islands, a shield, and a rising sun over the Pacific."""
    c.rect(x, y, w, h, SKY)
    c.circle(x + w - 26, y + 10, 9, GOLD)
    c.rect(x, y + h - 8, w, 8, SEA)
    c.tri(x + 10, y + h - 8, x + 40, y + h - 8, x + 25, y + h - 24, GREEN)
    c.tri(x + w - 46, y + h - 8, x + w - 12, y + h - 8,
          x + w - 29, y + h - 20, (30, 110, 60))
    cx, cy = x + w // 2, y + 15
    c.rect(cx - 13, cy - 9, 26, 18, WHITE)
    c.tri(cx - 13, cy + 9, cx + 13, cy + 9, cx, cy + 20, WHITE)
    c.rect(cx - 8, cy - 5, 16, 12, BLUE)
    c.text(cx - 4, cy - 2, "+", 1, WHITE)


def art_rubble(c, x, y, w, h):
    """Broken wall and dust under a pale sky, kept inside the box."""
    c.rect(x, y, w, h, (214, 200, 170))
    c.rect(x, y + h - 8, w, 8, (150, 132, 104))
    blocks = [(8, 16), (44, 22), (76, 12), (108, 20), (140, 14),
              (172, 24), (204, 12), (236, 18), (268, 10)]
    for bx, bh in blocks:
        c.rect(x + bx, y + h - 8 - bh, 24, bh, (120, 104, 84))
    c.text(x + w - 26, y + 2, "!", 2, RED)
    for dx, dy in ((30, 8), (90, 6), (150, 10)):
        c.circle(x + dx, y + dy, 2, (170, 154, 128))


def art_chart(c, x, y, w, h):
    """A falling market line over bars, kept inside the box."""
    c.rect(x, y, w, h, CARD)
    c.rect(x + 6, y + h - 6, w - 12, 2, INK)
    c.rect(x + 6, y + 4, 2, h - 10, INK)
    pts = [(12, 8), (34, 13), (56, 11), (78, 19), (100, 24), (122, 31)]
    for i in range(len(pts) - 1):
        c.line(x + pts[i][0], y + pts[i][1],
               x + pts[i + 1][0], y + pts[i + 1][1], RED)
    for i, (px, py) in enumerate(pts):
        bh = max(2, (h - 8 - py) // 2)
        c.rect(x + px - 2, y + h - 8 - bh, 5, bh,
               (180, 60, 60) if i > 2 else GREEN)
    c.text(x + w - 32, y + 2, "-5%", 1, RED)


def icon_globe(c, x, y):
    c.circle(x + 8, y + 8, 8, BLUE, fill=False)
    c.line(x, y + 8, x + 16, y + 8, BLUE)
    c.line(x + 8, y, x + 8, y + 16, BLUE)


def icon_columns(c, x, y):
    for i in range(3):
        c.rect(x + 1 + i * 5, y + 4, 3, 9, NAVY)
    c.rect(x, y + 2, 16, 2, NAVY)
    c.rect(x, y + 13, 16, 2, NAVY)


def icon_sun(c, x, y):
    c.circle(x + 8, y + 8, 5, GOLD)
    for ang in range(0, 360, 45):
        import math
        c.line(x + 8, y + 8,
               x + 8 + int(9 * math.cos(math.radians(ang))),
               y + 8 + int(9 * math.sin(math.radians(ang))), GOLD)


def icon_tree(c, x, y):
    c.tri(x + 8, y + 1, x + 2, y + 10, x + 14, y + 10, GREEN)
    c.rect(x + 7, y + 10, 2, 5, (120, 80, 40))


def icon_star(c, x, y):
    c.text(x + 2, y + 2, "*", 2, RED)


def icon_flask(c, x, y):
    c.rect(x + 7, y + 1, 2, 5, TEAL)
    c.tri(x + 8, y + 5, x + 2, y + 15, x + 14, y + 15, TEAL)
    c.rect(x + 5, y + 11, 6, 3, WHITE)


def icon_coin(c, x, y):
    c.circle(x + 8, y + 8, 7, GOLD)
    c.text(x + 5, y + 5, "$", 1, NAVY)


# ---- page layout ----

FEATURES = [
    ("TARIFFS", "TRUMP READIES NEW TARIFFS",
     "USTR probe findings due; new duties loom on 16 partners.",
     art_ship, RED),
    ("SPACE", "SHENZHOU-24 LIFTS OFF",
     "First Pakistani astronaut heads for the Tiangong station.",
     art_rocket, BLUE),
    ("UKRAINE", "ODESA STRIKE KILLS TWO",
     "Russia hits Odesa; drones strike Kyiv flats, two hurt.",
     art_blast, NAVY),
    ("PACIFIC", "AUSTRALIA-SOLOMONS PACT",
     "Canberra becomes defence partner of choice.",
     art_pact, TEAL),
    ("GAZA", "STRIKES KILL SIX IN GAZA",
     "Israeli strikes kill six despite the ceasefire.",
     art_rubble, DARKRED),
    ("MARKETS", "ASIAN STOCKS TUMBLE",
     "AI rally fizzles; Kospi -5.3%, Taiwan -5.1%, Nvidia -5.9%.",
     art_chart, GREEN),
]

BRIEFS = [
    ("ASIA-PACIFIC", icon_globe, BLUE, [
        "Shanghai pledges loyalty to Beijing after the Chen probe.",
        "Japan service prices rise 4.2%, beating forecasts.",
        "Indonesia detains a ship carrying 405 tonnes of chemical.",
        "Australia inflation at 3.8% squeezes the Reserve Bank.",
    ]),
    ("EUROPE", icon_columns, NAVY, [
        "EU proposes its 22nd package of Russia sanctions.",
        "Seven states urge the EU to bar Russian athletes.",
        "UK abuse protection orders extend across England and Wales.",
        "Swiss panel backs a 90% capital rule for UBS units.",
    ]),
    ("MIDDLE EAST & AFRICA", icon_sun, ORANGE, [
        "Iran orders Hormuz shut again; Qatar seeks talks.",
        "Houthis threaten Saudi ports over the Hodeidah order.",
        "Sudan drones kill five children in Khartoum.",
        "Libya condemns a Ukraine drone hit on ships off Benghazi.",
    ]),
    ("AMERICAS", icon_star, RED, [
        "US pauses joint military operations with Ecuador.",
        "Trump open to a US stake in Nvidia and a Huang pardon.",
        "US measles cases hit a 30-year high; 1,600 in Pennsylvania.",
        "Shein to pay $100m to settle US deception claims.",
    ]),
    ("SCIENCE & TECH", icon_flask, TEAL, [
        "OpenAI's GPT-6.2 Astra praised for optimisation speed.",
        "Rockstar shuts Discord behind an AI bid to crack GTA 6.",
        "Cambridge begins an NHS trial of AI mammogram reading.",
        "Anthropic's $ANT fails at its $83 IPO price.",
    ]),
    ("MARKETS & LIFE", icon_coin, GOLD, [
        "Brent crude $91 as Hormuz attacks lift oil prices.",
        "Bitcoin $59,257 as crypto slips with the sell-off.",
        "Kate Middleton opens up on her cancer battle.",
        "FIFA names the 2031 Women's World Cup hosts.",
    ]),
]

FOOTER = [
    "Verstappen holds off Norris to win in Las Vegas.",
    "England draw Norway in the Nations League quarters.",
    "Australia win a last-over thriller at the MCG.",
    "GTA VI launches with a return to Vice City.",
]


def build():
    c = Canvas()
    # Masthead
    c.rect(0, 0, W, 92, NAVY)
    title = "THE WORLD IN ONE DAY"
    c.text((W - c.text_w(title, 4)) // 2, 12, title, 4, WHITE)
    c.rect(16, 52, W - 32, 2, GOLD)
    date = "WEDNESDAY, 25 NOVEMBER 2026"
    c.text((W - c.text_w(date, 2)) // 2, 60, date, 2, GOLD)
    sub = "THE DAY'S WORLD NEWS IN ONE IMAGE"
    c.text((W - c.text_w(sub, 1)) // 2, 80, sub, 1, (200, 205, 215))

    # Lead story: China probe
    ly, lh = 100, 196
    art_gate(c, 16, ly, 360, lh)
    tx = 392
    c.text(tx, ly + 6, "LEAD - CHINA", 2, RED)
    c.text(tx, ly + 30, "SHANGHAI CHIEF UNDER PROBE", 3, INK)
    c.text(tx, ly + 58, "POLITBURO MEMBER CHEN JINING INVESTIGATED", 2, NAVY)
    c.para(tx, ly + 88,
           "China's anti-graft watchdog is investigating Chen Jining, "
           "Shanghai's Communist Party chief and a member of the elite "
           "Politburo - the fourth top leader probed since 2025. "
           "Shanghai's leadership pledged loyalty to Beijing and vowed "
           "to see the probe through to the end.",
           1, INK, 600, max_lines=6)
    c.text(tx, ly + 168, "XINHUA / REUTERS - WEDNESDAY, 25 NOVEMBER", 1, GREY)

    # Feature cards: two rows of three
    c.text(16, 306, "THE BIG STORIES", 2, INK)
    c.hline(16, 326, W - 32, INK)
    for idx, (kick, head, body, art, col) in enumerate(FEATURES):
        col_i, row_i = idx % 3, idx // 3
        fx = 16 + col_i * (322 + 13)
        fy = 334 + row_i * 128
        c.rect(fx, fy, 322, 120, CARD)
        c.rect(fx, fy, 322, 3, col)
        art(c, fx + 4, fy + 8, 314, 40)
        c.text(fx + 8, fy + 52, kick, 1, col)
        c.text(fx + 8, fy + 64, head, 2, INK)
        c.para(fx + 8, fy + 88, body, 1, INK, 306, max_lines=2)

    # The Day in Brief: six region groups
    by = 604
    c.text(16, by, "THE DAY IN BRIEF", 2, INK)
    tag = "35 STORIES - 8 REGIONS"
    c.text(W - 16 - c.text_w(tag, 1), by + 4, tag, 1, GREY)
    c.hline(16, by + 22, W - 32, INK)
    for idx, (region, icon, col, items) in enumerate(BRIEFS):
        col_i, row_i = idx % 3, idx // 3
        gx = 16 + col_i * (322 + 13)
        gy = by + 30 + row_i * 160
        c.rect(gx, gy, 322, 152, CARD)
        c.rect(gx, gy, 322, 3, col)
        icon(c, gx + 8, gy + 10)
        c.text(gx + 28, gy + 12, region, 2, col)
        iy = gy + 34
        for it in items:
            iy = c.para(gx + 10, iy, "- " + it, 1, INK, 302,
                        max_lines=2, line_gap=1)
            iy += 5

    # Footer strip
    fy = 948
    c.hline(16, fy, W - 32, INK)
    for i, item in enumerate(FOOTER):
        fx = 16 + i * (242 + 13)
        c.para(fx, fy + 8, item, 1, INK, 236, max_lines=3, line_gap=1)
    c.text(16, 1002, "SOURCES: REUTERS - XINHUA - AP - BBC - NYT - FT",
           1, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
