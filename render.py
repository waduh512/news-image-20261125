#!/usr/bin/env python3
"""Render the news-image entry v5: a one-page summary of the world news of
Wednesday 25 November 2026, as a 1024x1024 PNG.

v4 rebuild of the v3 renderer (news-image-20261125). v3 was a clean
typographic front page (hero Huawei "10/12" numeral + verdict bar, 30
stories, light dotted map, numbers as a strip). The user asked for it to
be better, more interesting and more different, based on top-10
references from the 23 Nov edition (13,031 entries) and the 24 Nov
edition (9,063 entries) — see TOP10_NOTES.md section 5 ("What v4
should steal"). Our 24 Nov entry ranked 1296/7302 (round 1) and
1146/9063 (round 2): top 18%, outside the 50 prize places.

What v4 steals, in priority order:
1. STORY COUNT 30 -> 36. Six one-liners from NEWS_NOTES.md are
   promoted to numbered stories 31-36 (all dated 24-25 Nov, named
   sources; the single-source Bolsonaro ICU item was NOT promoted, and
   yesterday's Indonesia factory fire was NOT re-run as a fresh story).
   Region counts are now WORLD 3, EUROPE 7, MID EAST 5, AFRICA 6,
   ASIA 6, AMERICAS 7, OCEANIA 2.
2. NUMBERS RIGHT RAIL: the Day in Numbers strip becomes a dark navy
   RIGHT RAIL (gold numbers, coral story refs, 6 numbers) running down
   the right side of the page. This frees the top for a bigger hero.
3. PRESS-TIME STAMP + DECK LINE: "EDITION TO 02:10 UTC" beside
   "Edition No. 2" (hardcoded string, so the render stays
   deterministic), and the red italic deck line naming the 3 top
   stories is restored under the masthead (v1 had it, v3 dropped it).
4. VISUALS AS DIAGRAMS (no cartoon scenes — the user circled every
   literal drawing in v2 and they must NOT come back): the hero keeps
   its giant "10/12" numeral + 12-segment verdict bar, and the Gulf of
   Finland lead card gets a simple map diagram (coastlines, sea, a
   marked ship position, a dashed drone route, labelled). No faces, no
   people, no literal scenes anywhere.
5. DARK MAP: "WHERE IT HAPPENED" is now dark navy with coral
   numbered pins (like 23 Nov #3).
6. NAMED MEDIUM SECTION: the medium cards sit under "THE DAY IN
   TWELVE MORE", each with a one-word coloured topic banner
   (SANCTIONS, COURT, CRASH, STRIKE, EPIDEMIC, ...).
7. SOURCES PER STORY: a small source tag on the hero deck, every lead
   deck and every medium card (outlet names from NEWS_NOTES.md).
8. KEPT: cream paper, ink-navy serif masthead, coral accent, chill
   tagline "take a breath — here's the day", the honest Date Check
   footer (Hera image date unverified, Sudan drone count disputed;
   Merkury/COP31/Huang are not today's news), the CLAIM tag on story
   15, the UTC strip, the HOW SURE legend. Serious news stays serious.

v5 (this version): the user reviewed v4 (clean typographic front page,
no illustrations) and asked for the illustrations BACK — the page felt
lacking without them — but better than v2's crude drawings (a faceless
judge blob, grey-block refinery, flat ship, cartoon trophy; the user
circled all of those in green). v5 keeps v4's structure and every fact
exactly, and adds RICH drawn scenes: a detailed courtroom in the hero
(wood panelling, columns, judge bench with gavel and scales, the gold
"10/12" verdict board in the scene, no judge figure), a dusk refinery,
a Gulf of Finland sea strike, a stadium with a proper trophy, and a
small specific scene on every medium card. The lesson from the top 10s
(see TOP10_NOTES.md sections 2-3: 24 Nov #2 @lialie, 23 Nov #1 @kevin)
is that winning scenes are rich, detailed and specific — layered, with
gradient skies and small details — so every scene here has depth
(background / midground / foreground) and no flat solid squares.
One presentation trim: lead card 14's deck drops "and sets aside CAF's
forfeit" (the headline "title restored" already says it) so the deck
fits under the new scene strip.

Facts, dates and numbers are unchanged from NEWS_NOTES.md.

Everything is set in type and drawn with code (PIL + DejaVu fonts):
no photos, no logos, no network. Deterministic: same bytes every run
(the press time is a fixed string, not the clock).

Build-time tool only. The entry program (main.ts) copies the PNG this
script writes into /output/entry.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
NOTO_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size, base=None):
    return ImageFont.truetype(
        os.path.join(base or FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SERIF_I = lambda s: font("NotoSerif-Italic.ttf", s, base=NOTO_DIR)
F_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_R = lambda s: font("DejaVuSans.ttf", s)

# Palette — warm newspaper: cream paper, ink-navy type, one coral accent
INK_NAVY = (24, 36, 56)
INK_NAVY_D = (16, 24, 40)
CORAL = (198, 64, 44)
CORAL_D = (170, 48, 34)
NAVY = (18, 82, 76)
INK = (32, 30, 26)
GREY = (112, 102, 88)
PAPER = (253, 246, 233)
CARD = (255, 255, 255)
GOLD = (224, 164, 60)
GREEN = (74, 138, 90)
BLUE = (74, 110, 160)
RED = (196, 88, 56)
ORANGE = (210, 110, 50)
TEAL = (30, 130, 125)
LINE = (226, 216, 200)
PURPLE = (130, 95, 150)
BROWN = (160, 120, 60)
RAIL_LINE = (42, 56, 84)

PRESS_TIME = "EDITION TO 02:10 UTC"


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, lines, fnt, fill, leading):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def tag(draw, x, y, text, color):
    """Verification tag, e.g. REPORTED / CLAIM / OFFICIAL / ONGOING."""
    fnt = F_B(10)
    w = draw.textlength(text, font=fnt) + 10
    draw.rounded_rectangle([x, y, x + w, y + 15], radius=3, fill=color)
    draw.text((x + 5, y + 2), text, font=fnt, fill=(255, 255, 255))
    return w


TAG_COLORS = {"REPORTED": (120, 110, 95), "CLAIM": (200, 150, 40),
              "OFFICIAL": GREEN, "ONGOING": (210, 110, 50)}


def vgrad(draw, box, top, bottom):
    """Vertical gradient fill inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def dots(draw, box, n, colors, seed=0):
    """Deterministic scatter of 2px dots inside box (crowd / confetti)."""
    x0, y0, x1, y1 = box
    for i in range(n):
        px = x0 + ((i * 53 + seed * 17 + 11) % max(1, x1 - x0 - 2))
        py = y0 + ((i * 29 + seed * 7 + 5) % max(1, y1 - y0 - 2))
        draw.ellipse([px, py, px + 2, py + 2], fill=colors[i % len(colors)])


def courtroom_scene(draw, px, py, pw, ph):
    """Detailed courtroom inside the hero's left panel (300x138).

    Wood-panelled walls, fluted columns, a judge bench with a gavel
    and scales of justice, warm light. The gold "10/12" verdict board
    sits in the scene and the 12-segment bar + label below it stay
    prominent. No judge figure: an empty bench reads better than a
    bad figure (v2's faceless blob is what the user circled).
    """
    # wood wall: warm gradient + vertical panel seams
    vgrad(draw, (px, py, px + pw, py + ph), (150, 104, 60), (84, 56, 32))
    for sx in range(px + 58, px + pw, 58):
        draw.line([(sx, py), (sx, py + ph)], fill=(62, 40, 22), width=2)
        draw.line([(sx + 2, py), (sx + 2, py + ph)], fill=(176, 128, 74),
                  width=1)
    # warm light wash in the centre
    vgrad(draw, (px + 46, py, px + pw - 46, py + 96), (180, 130, 76),
          (134, 90, 50))
    # fluted columns at both edges
    for cx in (px + 4, px + pw - 26):
        draw.rectangle([cx, py + 4, cx + 22, py + ph - 4], fill=(203, 166, 94))
        for fx in (cx + 5, cx + 11, cx + 17):
            draw.line([(fx, py + 10), (fx, py + ph - 10)], fill=(172, 134, 68),
                      width=1)
        draw.rectangle([cx - 2, py + 4, cx + 24, py + 12], fill=(226, 192, 116))
        draw.rectangle([cx - 2, py + ph - 12, cx + 24, py + ph - 4],
                       fill=(226, 192, 116))
    # verdict plaque: gold frame, navy fill, coral numeral
    bx0, by0, bx1, by1 = px + 56, py + 10, px + pw - 56, py + 66
    draw.rectangle([bx0, by0, bx1, by1], fill=(24, 36, 56),
                   outline=(203, 164, 92), width=3)
    numeral = "10/12"
    nfnt = F_B(46)
    nw = draw.textlength(numeral, font=nfnt)
    draw.text((bx0 + (bx1 - bx0 - nw) / 2, by0 + 8), numeral, font=nfnt,
              fill=CORAL)
    # 12-segment verdict bar: 10 filled coral, 2 empty (outlined only)
    seg_w, seg_h, gap = 16, 11, 2
    bar_w = 12 * seg_w + 11 * gap
    bx = px + (pw - bar_w) / 2
    by = py + 74
    for i in range(12):
        sx0 = bx + i * (seg_w + gap)
        if i < 10:
            draw.rectangle([sx0, by, sx0 + seg_w, by + seg_h], fill=CORAL)
        else:
            draw.rectangle([sx0, by, sx0 + seg_w, by + seg_h],
                           outline=(150, 160, 180), width=1)
    lab = "GUILTY ON 10 OF 12 COUNTS"
    lfnt = F_B(9)
    lw = draw.textlength(lab, font=lfnt)
    draw.text((px + (pw - lw) / 2, by + 17), lab, font=lfnt,
              fill=(215, 220, 228))
    # judge bench: dark wood band with a light top edge
    bench_y = py + ph - 34
    draw.rectangle([px, bench_y, px + pw, py + ph], fill=(58, 38, 22))
    draw.line([(px, bench_y), (px + pw, bench_y)], fill=(190, 140, 84), width=2)
    # gavel on the bench, left (handle, banded head, sound block)
    gx, gy = px + 44, bench_y + 8
    draw.ellipse([gx - 2, gy + 16, gx + 26, gy + 22], fill=(40, 26, 14))
    draw.line([(gx + 4, gy + 14), (gx + 24, gy + 2)], fill=(140, 96, 52), width=4)
    draw.rounded_rectangle([gx + 18, gy - 2, gx + 40, gy + 8], radius=3,
                           fill=(96, 62, 34))
    draw.line([(gx + 22, gy - 2), (gx + 22, gy + 8)], fill=(203, 164, 92),
              width=2)
    draw.line([(gx + 32, gy - 2), (gx + 32, gy + 8)], fill=(203, 164, 92),
              width=2)
    # scales of justice on the bench, right (post, beam, two pans, base)
    sx = px + pw - 74
    sy = bench_y + 4
    draw.line([(sx + 16, sy), (sx + 16, sy + 24)], fill=(203, 164, 92), width=2)
    draw.line([(sx + 2, sy + 2), (sx + 30, sy + 2)], fill=(203, 164, 92), width=2)
    draw.ellipse([sx + 13, sy - 3, sx + 19, sy + 3], fill=(226, 192, 116))
    for ex in (sx + 2, sx + 30):
        draw.line([(ex, sy + 2), (ex - 5, sy + 12)], fill=(203, 164, 92), width=1)
        draw.line([(ex, sy + 2), (ex + 5, sy + 12)], fill=(203, 164, 92), width=1)
        draw.polygon([(ex - 6, sy + 12), (ex + 6, sy + 12), (ex, sy + 19)],
                     fill=(226, 192, 116))
    draw.polygon([(sx + 8, sy + 24), (sx + 24, sy + 24), (sx + 20, sy + 30),
                  (sx + 12, sy + 30)], fill=(203, 164, 92))


def refinery_scene(draw, x, y, w, h):
    """Refinery at dusk: gradient sky, sun low on the horizon, towers
    with lit windows and flare flames, smoke plumes, dark foreground."""
    vgrad(draw, (x, y, x + w, y + h), (28, 38, 78), (232, 138, 58))
    # stars in the upper sky
    for sx, sy in [(12, 4), (40, 8), (90, 3), (150, 7), (200, 4), (120, 10),
                   (170, 12), (60, 12)]:
        draw.ellipse([x + sx, y + sy, x + sx + 1, y + sy + 1],
                     fill=(235, 235, 240))
    # sun low on the horizon
    draw.ellipse([x + w - 52, y + h - 22, x + w - 38, y + h - 8],
                 fill=(250, 210, 120))
    # smoke plumes above the towers
    for sx, sy, r in [(60, 2, 7), (140, 0, 8), (190, 4, 6)]:
        draw.ellipse([x + sx - r, y + sy, x + sx + r, y + sy + 6],
                     fill=(150, 138, 128))
    # towers: dark silhouettes, lit windows, flare flames
    towers = [(8, 24, 22), (36, 30, 18), (62, 20, 24), (96, 28, 20),
              (170, 22, 22), (210, 26, 20)]
    for tx, th, tw in towers:
        draw.rectangle([x + tx, y + h - th, x + tx + tw, y + h],
                       fill=(22, 20, 30))
        for wy in range(y + h - th + 4, y + h - 3, 6):
            for wx in (x + tx + 4, x + tx + tw - 6):
                draw.rectangle([wx, wy, wx + 2, wy + 2], fill=(240, 190, 90))
        fx = x + tx + tw // 2
        draw.polygon([(fx - 4, y + h - th), (fx + 4, y + h - th),
                      (fx, y + h - th - 8)], fill=(240, 140, 40))
        draw.polygon([(fx - 2, y + h - th), (fx + 2, y + h - th),
                      (fx, y + h - th - 5)], fill=(250, 210, 100))
    # foreground ground + a pipe silhouette
    draw.rectangle([x, y + h - 6, x + w, y + h], fill=(14, 14, 20))
    draw.line([(x + 120, y + h - 6), (x + 120, y + h - 14)],
              fill=(14, 14, 20), width=4)


def gulf_scene(draw, x, y, w, h):
    """Gulf of Finland at sunset: land strips labelled FINLAND /
    ESTONIA, sunset sky, layered sea, a detailed cargo ship with
    containers, a dashed drone route and drone silhouettes."""
    # land strips top (Finland) and bottom (Estonia)
    draw.rectangle([x, y, x + w, y + 6], fill=(74, 110, 70))
    draw.rectangle([x, y + h - 6, x + w, y + h], fill=(74, 110, 70))
    draw.text((x + 4, y), "FINLAND", font=F_B(6), fill=(230, 235, 225))
    draw.text((x + 4, y + h - 6), "ESTONIA", font=F_B(6), fill=(230, 235, 225))
    # sunset sky, then layered sea
    vgrad(draw, (x, y + 6, x + w, y + 16), (252, 196, 130), (240, 150, 90))
    vgrad(draw, (x, y + 16, x + w, y + h - 6), (84, 128, 168), (34, 68, 108))
    # sun disc
    draw.ellipse([x + w - 46, y + 8, x + w - 34, y + 20], fill=(252, 220, 140))
    # wave lines
    for wy, wl in [(22, 40), (26, 120), (30, 200)]:
        draw.line([(x + wl, y + wy), (x + wl + 26, y + wy)],
                  fill=(160, 190, 220), width=1)
    # cargo ship: hull, container stacks, bridge
    hx0, hy0 = x + 96, y + 22
    draw.polygon([(hx0, hy0), (hx0 + 64, hy0), (hx0 + 58, hy0 + 8),
                  (hx0 + 6, hy0 + 8)], fill=(18, 22, 34))
    for cx, cy, col in [(hx0 + 8, hy0 - 7, (196, 64, 44)),
                        (hx0 + 20, hy0 - 7, (30, 130, 125)),
                        (hx0 + 32, hy0 - 7, (224, 164, 60)),
                        (hx0 + 44, hy0 - 7, (74, 110, 160))]:
        draw.rectangle([cx, cy, cx + 11, cy + 7], fill=col,
                       outline=(20, 24, 30), width=1)
    draw.rectangle([hx0 + 56, hy0 - 12, hx0 + 63, hy0], fill=(220, 225, 230))
    # dashed drone route from the west, two drone silhouettes
    rx0, ry0, rx1, ry1 = x + 12, y + 9, x + 92, y + 14
    steps = 10
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 0.55) / steps
        draw.line([(rx0 + (rx1 - rx0) * t0, ry0 + (ry1 - ry0) * t0),
                   (rx0 + (rx1 - rx0) * t1, ry0 + (ry1 - ry0) * t1)],
                  fill=CORAL, width=2)
    for dx, dy in [(34, 10), (62, 12)]:
        draw.ellipse([x + dx - 3, y + dy - 2, x + dx + 3, y + dy + 2],
                     fill=(16, 18, 26))
        draw.line([(x + dx - 5, y + dy - 3), (x + dx + 5, y + dy - 3)],
                  fill=(16, 18, 26), width=1)
    draw.text((x + w - 42, y + h - 14), "REUTERS", font=F_B(6),
              fill=(225, 235, 245))


def stadium_scene(draw, x, y, w, h):
    """AFCON final at night: floodlit stands with a crowd, green pitch,
    a trophy on a podium with confetti. The trophy is a real cup:
    bowl, handles, stem and base."""
    # night stands with a crowd
    vgrad(draw, (x, y, x + w, y + 24), (16, 34, 52), (24, 52, 66))
    dots(draw, (x + 2, y + 2, x + w - 2, y + 22), 90,
         [(240, 240, 235), (224, 164, 60), (198, 64, 44), (150, 190, 220),
          (255, 255, 255)], seed=3)
    # floodlight cones + heads
    draw.polygon([(x + 8, y), (x + 30, y), (x + 70, y + 24), (x + 40, y + 24)],
                 fill=(240, 232, 190))
    draw.polygon([(x + w - 8, y), (x + w - 30, y), (x + w - 70, y + 24),
                  (x + w - 40, y + 24)], fill=(240, 232, 190))
    draw.rectangle([x + 6, y, x + 32, y + 4], fill=(250, 248, 235))
    draw.rectangle([x + w - 32, y, x + w - 6, y + 4], fill=(250, 248, 235))
    # pitch with a centre circle
    vgrad(draw, (x, y + 24, x + w, y + h), (46, 130, 66), (28, 96, 48))
    draw.line([(x, y + 24), (x + w, y + 24)], fill=(240, 240, 235), width=1)
    draw.ellipse([x + w // 2 - 14, y + 26, x + w // 2 + 14, y + 34],
                 outline=(240, 240, 235), width=1)
    # confetti in the air (behind the trophy)
    dots(draw, (x + 4, y + 2, x + w - 4, y + 22), 26,
         [(224, 164, 60), (198, 64, 44), (255, 255, 255), (74, 138, 90)],
         seed=9)
    # podium, centre
    px0 = x + w // 2 - 16
    draw.rectangle([px0, y + h - 10, px0 + 32, y + h], fill=(40, 30, 22))
    draw.rectangle([px0, y + h - 10, px0 + 32, y + h - 8], fill=(120, 90, 50))
    # trophy: stem + base first, then bowl, highlight, handles
    tx = x + w // 2
    ty = y + h - 10  # podium top
    draw.rectangle([tx - 2, ty - 12, tx + 2, ty], fill=(224, 164, 60))
    draw.rectangle([tx - 7, ty - 3, tx + 7, ty], fill=(201, 142, 46))
    draw.pieslice([tx - 9, ty - 24, tx + 9, ty - 6], 0, 180,
                  fill=(224, 164, 60))
    draw.pieslice([tx - 9, ty - 24, tx - 1, ty - 6], 0, 180,
                  fill=(244, 204, 110))
    draw.arc([tx - 15, ty - 24, tx - 3, ty - 10], 90, 270,
             fill=(224, 164, 60), width=2)
    draw.arc([tx + 3, ty - 24, tx + 15, ty - 10], 270, 90,
             fill=(224, 164, 60), width=2)


def lead_scene(draw, x, y, w, h, key):
    """Dispatch to a lead-card scene strip (248x36)."""
    if key == "refinery":
        refinery_scene(draw, x, y, w, h)
    elif key == "gulf":
        gulf_scene(draw, x, y, w, h)
    elif key == "stadium":
        stadium_scene(draw, x, y, w, h)


def hero_card(draw, x, y, w, h):
    """Full-width hero (main column): the Huawei verdict, typographic.

    Coral band on top; left ink-navy panel with a giant coral "10/12"
    numeral and a 12-segment verdict bar (10 filled); big serif
    headline + deck + source line on the right.
    """
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK_NAVY, width=2)
    # coral band
    draw.rectangle([x + 2, y + 2, x + w - 2, y + 26], fill=CORAL)
    d_band = "THE VERDICT  —  BROOKLYN, TUESDAY"
    draw.text((x + 14, y + 6), d_band, font=F_B(12), fill=(255, 255, 255))
    tag(draw, x + w - 74, y + 6, "OFFICIAL", TAG_COLORS["OFFICIAL"])
    # left panel: detailed courtroom scene (v5) — wood panelling,
    # columns, judge bench with gavel and scales, and the gold "10/12"
    # verdict board with its 12-segment bar in the scene. No judge
    # figure: an empty bench reads better than a bad figure.
    px, py, pw, ph = x + 2, y + 26, 300, h - 28
    courtroom_scene(draw, px, py, pw, ph)
    # text, right
    tx = x + 2 + pw + 20
    tw = x + w - 2 - tx - 14
    ty = y + 28
    # story number badge + kicker
    draw.ellipse([tx, ty, tx + 24, ty + 24], fill=CORAL)
    tw1 = draw.textlength("1", font=F_B(13))
    draw.text((tx + 12 - tw1 / 2, ty + 4), "1", font=F_B(13),
              fill=(255, 255, 255))
    draw.text((tx + 32, ty + 4), "WORLD  •  TECH", font=F_B(13), fill=CORAL)
    ty += 26
    # headline with a fixed, balanced break (no dangling "counts")
    hl = ["Huawei convicted on 10", "of 12 counts"]
    ty = text_block(draw, (tx, ty), hl, F_SERIF_B(26), INK_NAVY, 29)
    ty += 4
    d1 = wrap(draw, "Bank fraud, sanctions breaches, trade-secrets theft. "
                     "Sentencing Sep 2027. Acquitted of racketeering and "
                     "obstruction.", F_R(13), tw)
    ty = text_block(draw, (tx, ty), d1, F_R(13), (60, 58, 52), 16)
    draw.text((tx, ty + 4), "Sources: Reuters  •  AP  •  CNN",
              font=F_R(10), fill=GREY)


def lead_card(draw, x, y, w, h, color, kicker, num, headline, deck, tagname,
              scene=None):
    """Lead card (v5): a drawn scene strip on top (like 24 Nov #8's
    small scene strips), then a large number chip, kicker, headline
    and deck with source. The scene strip is 36px; the deck is set
    at 11pt/12 leading so two lines fit under a two-line headline."""
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    # coloured top border
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 7], fill=color)
    # scene strip on top (under the border)
    ty0 = y + 52
    if scene:
        lead_scene(draw, x + 2, y + 8, w - 4, 36, scene)
        draw.rectangle([x + 2, y + 8, x + w - 2, y + 44], outline=LINE, width=1)
    else:
        ty0 = y + 14
    # large number chip
    draw.ellipse([x + 12, ty0, x + 42, ty0 + 30], fill=color)
    tw = draw.textlength(num, font=F_B(15))
    draw.text((x + 27 - tw / 2, ty0 + 6), num, font=F_B(15),
              fill=(255, 255, 255))
    # kicker beside the chip, status tag top-right
    draw.text((x + 52, ty0 + 8), kicker, font=F_B(12), fill=color)
    tag(draw, x + w - 78, ty0 + 4, tagname, TAG_COLORS[tagname])
    # headline
    ty = ty0 + 36
    hl = wrap(draw, headline, F_B(16), w - 24)
    ty = text_block(draw, (x + 12, ty), hl, F_B(16), INK_NAVY, 19)
    # deck, 11pt/12 leading
    cap = wrap(draw, deck, F_R(11), w - 24)
    text_block(draw, (x + 12, ty + 4), cap, F_R(11), (60, 60, 60), 12)


def medium_scene(draw, x, y, w, h, key):
    """One small (52x50) but specific scene: gradient background +
    midground shape + foreground detail. Every painter stays inside
    its rect. Deterministic (no randomness)."""
    if key == "eclipse":
        # deep space, cratered asteroid, moon shadow with a bright rim
        vgrad(draw, (x, y, x + w, y + h), (8, 10, 26), (38, 48, 88))
        for sx, sy in [(6, 6), (20, 4), (38, 8), (46, 14), (12, 18), (30, 12)]:
            draw.ellipse([x + sx, y + sy, x + sx + 1, y + sy + 1],
                         fill=(235, 235, 240))
        draw.ellipse([x + 14, y + 18, x + w - 2, y + h - 2],
                     fill=(150, 132, 112))
        draw.ellipse([x + 14, y + 18, x + w - 2, y + h - 2],
                     outline=(110, 94, 76), width=1)
        for cx, cy, r in [(30, 32, 4), (40, 42, 3), (24, 44, 2)]:
            draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                         fill=(120, 104, 86))
        draw.ellipse([x + 2, y + 2, x + 34, y + 34], fill=(12, 12, 22))
        draw.arc([x + 2, y + 2, x + 34, y + 34], 200, 340,
                 fill=(250, 220, 140), width=2)
    elif key == "radio":
        # sky, signal arcs, tapering radio mast with a red tip light
        vgrad(draw, (x, y, x + w, y + h), (110, 160, 200), (214, 230, 238))
        for r in (8, 12, 16):
            draw.arc([x + 26 - r, y + 16 - r, x + 26 + r, y + 16 + r],
                     200, 340, fill=(255, 255, 255), width=2)
        draw.polygon([(x + 22, y + h - 4), (x + 30, y + h - 4), (x + 28, y + 8),
                      (x + 24, y + 8)], fill=(40, 48, 60))
        for by in (18, 28, 38):
            draw.line([(x + 20, y + by), (x + 32, y + by)], fill=(40, 48, 60),
                      width=2)
        draw.ellipse([x + 24, y + 4, x + 28, y + 8], fill=(198, 64, 44))
        draw.rectangle([x, y + h - 5, x + w, y + h], fill=(60, 90, 70))
    elif key == "sanctions":
        # bank facade (pediment + columns) with a red falling chart
        vgrad(draw, (x, y, x + w, y + h), (232, 226, 212), (200, 190, 170))
        draw.polygon([(x + 6, y + 12), (x + w - 6, y + 12), (x + w // 2, y + 4)],
                     fill=(120, 110, 95))
        for cx in (10, 22, 34):
            draw.rectangle([x + cx, y + 14, x + cx + 6, y + h - 8],
                           fill=(245, 240, 228))
        draw.rectangle([x + 4, y + 14, x + w - 4, y + 17], fill=(120, 110, 95))
        draw.rectangle([x + 4, y + h - 10, x + w - 4, y + h - 7],
                       fill=(120, 110, 95))
        pts = [(x + 4, y + 20), (x + 14, y + 26), (x + 24, y + 22),
               (x + 34, y + 32), (x + 46, y + 40)]
        draw.line(pts, fill=(198, 64, 44), width=2)
        draw.polygon([(x + 46, y + 40), (x + 40, y + 40), (x + 46, y + 34)],
                     fill=(198, 64, 44))
    elif key == "budget":
        # bar chart with a flag on the tallest bar
        vgrad(draw, (x, y, x + w, y + h), (206, 224, 232), (242, 242, 236))
        for bx, bh, col in [(6, 12, (24, 36, 56)), (17, 18, (74, 110, 160)),
                            (28, 24, (30, 130, 125)), (39, 30, (224, 164, 60))]:
            draw.rectangle([x + bx, y + h - 6 - bh, x + bx + 9, y + h - 6],
                           fill=col)
        draw.line([(x + 2, y + h - 6), (x + w - 2, y + h - 6)], fill=(60, 60, 60),
                  width=1)
        draw.line([(x + 43, y + h - 6 - 30), (x + 43, y + h - 6 - 38)],
                  fill=(60, 60, 60), width=1)
        draw.polygon([(x + 43, y + h - 6 - 38), (x + 51, y + h - 6 - 35),
                      (x + 43, y + h - 6 - 32)], fill=(198, 64, 44))
    elif key == "court":
        # warm courtroom wall, two columns, a gavel between them
        vgrad(draw, (x, y, x + w, y + h), (224, 204, 172), (186, 156, 116))
        for cx in (6, 40):
            draw.rectangle([x + cx, y + 8, x + cx + 6, y + h - 8],
                           fill=(245, 238, 222))
            draw.rectangle([x + cx - 2, y + 6, x + cx + 8, y + 10],
                           fill=(220, 208, 186))
            draw.rectangle([x + cx - 2, y + h - 12, x + cx + 8, y + h - 8],
                           fill=(220, 208, 186))
        draw.line([(x + 20, y + 30), (x + 30, y + 22)], fill=(120, 82, 44),
                  width=3)
        draw.rounded_rectangle([x + 26, y + 16, x + 38, y + 26], radius=3,
                               fill=(96, 62, 34))
        draw.ellipse([x + 18, y + 32, x + 30, y + 36], fill=(70, 46, 24))
    elif key == "crash":
        # sky, hills, a helicopter silhouette in flight
        vgrad(draw, (x, y, x + w, y + h), (150, 180, 210), (232, 222, 200))
        draw.polygon([(x, y + h), (x, y + 34), (x + 26, y + 26), (x + w, y + 38),
                      (x + w, y + h)], fill=(90, 110, 90))
        draw.polygon([(x, y + h), (x, y + 42), (x + 30, y + 34), (x + w, y + 44),
                      (x + w, y + h)], fill=(60, 84, 66))
        hx, hy = x + 26, y + 12
        draw.ellipse([hx - 8, hy - 3, hx + 8, hy + 3], fill=(30, 30, 38))
        draw.line([(hx + 8, hy), (hx + 18, hy - 3)], fill=(30, 30, 38), width=2)
        draw.line([(hx - 10, hy - 6), (hx + 10, hy - 6)], fill=(30, 30, 38),
                  width=2)
        draw.line([(hx - 4, hy + 3), (hx - 6, hy + 8)], fill=(30, 30, 38), width=1)
        draw.line([(hx + 4, hy + 3), (hx + 6, hy + 8)], fill=(30, 30, 38), width=1)
        for my in (8, 14, 20):
            draw.line([(x + 2, y + my), (x + 10, y + my)], fill=(255, 255, 255),
                      width=1)
    elif key == "strike":
        # night sky, lit skyline, flames and smoke
        vgrad(draw, (x, y, x + w, y + h), (14, 18, 38), (62, 42, 62))
        for sx, sy in [(6, 6), (24, 4), (40, 8), (14, 12)]:
            draw.ellipse([x + sx, y + sy, x + sx + 1, y + sy + 1],
                         fill=(235, 235, 240))
        for bx, bh, bw in [(2, 22, 10), (14, 30, 12), (28, 18, 10), (40, 26, 10)]:
            draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                           fill=(24, 22, 32))
            for wy in range(y + h - bh + 4, y + h - 3, 6):
                draw.rectangle([x + bx + 3, wy, x + bx + 5, wy + 2],
                               fill=(240, 190, 90))
        for fx, fy in [(x + 19, y + h - 30), (x + 45, y + h - 26)]:
            draw.polygon([(fx - 4, fy), (fx + 4, fy), (fx, fy - 9)],
                         fill=(240, 140, 40))
            draw.polygon([(fx - 2, fy), (fx + 2, fy), (fx, fy - 5)],
                         fill=(250, 210, 100))
        draw.ellipse([x + 14, y + 6, x + 30, y + 14], fill=(120, 110, 115))
    elif key == "epidemic":
        # hospital building with a cross sign on top
        vgrad(draw, (x, y, x + w, y + h), (214, 228, 236), (190, 205, 215))
        draw.rectangle([x + 8, y + 14, x + w - 8, y + h - 6],
                       fill=(245, 246, 248))
        draw.rectangle([x + 8, y + 14, x + w - 8, y + 17], fill=(120, 140, 160))
        for wy in range(y + 22, y + h - 8, 8):
            for wx in range(x + 12, x + w - 12, 8):
                draw.rectangle([wx, wy, wx + 4, wy + 4], fill=(140, 170, 200))
        draw.rectangle([x + w // 2 - 8, y + 1, x + w // 2 + 8, y + 13],
                       fill=(30, 130, 125))
        draw.rectangle([x + w // 2 - 2, y + 2, x + w // 2 + 2, y + 12],
                       fill=(255, 255, 255))
        draw.rectangle([x + w // 2 - 7, y + 5, x + w // 2 + 7, y + 9],
                       fill=(255, 255, 255))
    elif key == "tower":
        # dusk sky, low sun, a tall tower with lit windows and antenna
        vgrad(draw, (x, y, x + w, y + h), (44, 54, 96), (224, 122, 62))
        draw.ellipse([x + 36, y + 26, x + 46, y + 36], fill=(252, 214, 130))
        draw.polygon([(x + 22, y + h), (x + 24, y + 8), (x + 28, y + 8),
                      (x + 30, y + h)], fill=(18, 18, 26))
        for wy in range(y + 12, y + h - 4, 5):
            draw.rectangle([x + 25, wy, x + 27, wy + 2], fill=(240, 190, 90))
        draw.line([(x + 26, y + 8), (x + 26, y + 2)], fill=(18, 18, 26), width=1)
        draw.ellipse([x + 25, y + 1, x + 27, y + 3], fill=(240, 80, 60))
        draw.rectangle([x, y + h - 5, x + w, y + h], fill=(12, 12, 18))
    elif key == "oil":
        # desert sun, a lattice derrick and a pumpjack silhouette
        vgrad(draw, (x, y, x + w, y + h), (240, 220, 180), (206, 170, 118))
        draw.ellipse([x + 38, y + 6, x + 48, y + 16], fill=(252, 214, 130))
        draw.polygon([(x + 10, y + h - 6), (x + 16, y + 10), (x + 22, y + 10),
                      (x + 28, y + h - 6)], fill=(52, 40, 28))
        for ly in (16, 24, 32):
            draw.line([(x + 13, y + ly), (x + 25, y + ly + 6)],
                      fill=(120, 96, 64), width=1)
            draw.line([(x + 25, y + ly), (x + 13, y + ly + 6)],
                      fill=(120, 96, 64), width=1)
        draw.line([(x + 36, y + h - 6), (x + 36, y + h - 22)], fill=(40, 32, 22),
                  width=2)
        draw.line([(x + 36, y + h - 22), (x + 48, y + h - 26)],
                  fill=(40, 32, 22), width=2)
        draw.polygon([(x + 48, y + h - 26), (x + 50, y + h - 22),
                      (x + 46, y + h - 22)], fill=(40, 32, 22))
        draw.rectangle([x, y + h - 6, x + w, y + h], fill=(140, 108, 70))
    elif key == "drones":
        # dark sky, radar circles with a sweep and blips, drone silhouettes
        vgrad(draw, (x, y, x + w, y + h), (14, 24, 44), (36, 56, 86))
        cx, cy = x + 16, y + h - 16
        for r in (5, 9, 13):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         outline=(90, 200, 120), width=1)
        draw.line([(cx, cy), (cx + 12, cy - 9)], fill=(140, 230, 160), width=2)
        for bx, by in [(cx + 8, cy - 6), (cx - 8, cy + 4), (cx + 4, cy - 12)]:
            draw.ellipse([bx - 1, by - 1, bx + 1, by + 1], fill=(140, 230, 160))
        for dx, dy in [(36, 10), (44, 18)]:
            draw.ellipse([x + dx - 3, y + dy - 2, x + dx + 3, y + dy + 2],
                         fill=(16, 18, 26))
            draw.line([(x + dx - 5, y + dy - 3), (x + dx + 5, y + dy - 3)],
                      fill=(16, 18, 26), width=1)
            draw.line([(x + dx - 5, y + dy + 3), (x + dx + 5, y + dy + 3)],
                      fill=(16, 18, 26), width=1)
    elif key == "exodus":
        # tent, aid boxes with a red cross, a crowd along the bottom
        vgrad(draw, (x, y, x + w, y + h), (224, 204, 164), (192, 162, 122))
        draw.polygon([(x + 6, y + h - 8), (x + 20, y + 14), (x + 34, y + h - 8)],
                     fill=(200, 180, 140))
        draw.line([(x + 6, y + h - 8), (x + 20, y + 14), (x + 34, y + h - 8)],
                  fill=(140, 120, 90), width=1)
        draw.rectangle([x + 30, y + h - 20, x + 46, y + h - 8],
                       fill=(178, 138, 84))
        draw.rectangle([x + 30, y + h - 20, x + 46, y + h - 17],
                       fill=(150, 112, 62))
        draw.rectangle([x + 36, y + h - 17, x + 40, y + h - 11],
                       fill=(198, 64, 44))
        draw.rectangle([x + 33, y + h - 15, x + 43, y + h - 13],
                       fill=(198, 64, 44))
        dots(draw, (x + 2, y + h - 7, x + w - 2, y + h - 1), 14,
             [(240, 240, 235), (60, 60, 70), (198, 64, 44), (30, 90, 60)],
             seed=5)


def medium_card(draw, x, y, w, h, color, num, topic, headline, caption,
                source, tagname, scene=None):
    """Medium card (v5): coloured header strip with one-word topic
    banner; text on the left, a small drawn scene on the right.
    Headline/caption sizes step down until the text fits the 50px
    body (headline up to 2 lines, caption up to 2 lines incl. source)."""
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 18], fill=color)
    draw.text((x + 8, y + 4), f"{num}  •  {topic}", font=F_B(10),
              fill=(255, 255, 255))
    tw_tag = draw.textlength(tagname, font=F_B(10)) + 10
    tag(draw, x + w - 8 - tw_tag, y + 3, tagname, TAG_COLORS[tagname])
    # scene panel, right
    sw, sh = 52, 50
    sx, sy = x + w - 8 - sw, y + 21
    if scene:
        medium_scene(draw, sx, sy, sw, sh, scene)
        draw.rectangle([sx, sy, sx + sw, sy + sh], outline=LINE, width=1)
    # text, left: headline + caption (with source) must fit 50px
    tw = w - 16 - sw - 8
    cap_text = caption + " — " + source
    for hf, hlead, cf, clead in [(12, 13, 9, 11), (11, 12, 9, 10),
                                 (11, 12, 8, 10), (10, 11, 8, 10)]:
        hl = wrap(draw, headline, F_B(hf), tw)
        cap = wrap(draw, cap_text, F_R(cf), tw)
        if len(hl) * hlead + 2 + len(cap) * clead <= 50:
            break
    ty = text_block(draw, (x + 8, y + 21), hl, F_B(hf), INK_NAVY, hlead)
    text_block(draw, (x + 8, ty + 2), cap, F_R(cf), (60, 60, 60), clead)


def right_rail(draw, x, y, w, h, numbers):
    """Dark navy right rail: 'THE DAY IN NUMBERS' with 6 gold numbers,
    each with its story ref (the most premium element seen in the
    winners' top 10s)."""
    draw.rectangle([x, y, x + w, y + h], fill=INK_NAVY_D,
                   outline=(52, 68, 95), width=1)
    cx = x + w // 2
    d = draw
    d.text((cx, y + 14), "THE DAY IN", font=F_B(13), fill=GOLD, anchor="ma")
    d.text((cx, y + 32), "NUMBERS", font=F_B(13), fill=GOLD, anchor="ma")
    d.line([(x + 20, y + 54), (x + w - 20, y + 54)], fill=GOLD, width=2)
    by = y + 64
    bh = 118
    for i, (big, label, ref) in enumerate(numbers):
        d.text((cx, by + 4), big, font=F_B(25), fill=GOLD, anchor="ma")
        lab = wrap(d, label, F_R(10), w - 20)
        ly = by + 38
        for ln in lab:
            d.text((cx, ly), ln, font=F_R(10), fill=(235, 235, 230),
                   anchor="ma")
            ly += 12
        d.text((cx, by + 92), ref, font=F_B(9), fill=CORAL, anchor="ma")
        if i < len(numbers) - 1:
            d.line([(x + 16, by + bh - 8), (x + w - 16, by + bh - 8)],
                   fill=RAIL_LINE, width=1)
        by += bh


def draw_map(draw, x, y, w, h, pins):
    """Dark navy schematic world map with coral numbered pins."""
    draw.rectangle([x, y, x + w, y + h], fill=INK_NAVY_D,
                   outline=LINE, width=1)
    # dotted grid over the whole map
    for gx in range(x + 8, x + w - 4, 9):
        for gy in range(y + 8, y + h - 4, 9):
            draw.ellipse([gx, gy, gx + 2, gy + 2], fill=(38, 52, 78))
    # continent blobs (schematic, scaled to the map height)
    blobs = [
        [(10, 26), (55, 16), (85, 28), (70, 58), (40, 62), (15, 45)],
        [(55, 70), (80, 66), (88, 96), (72, 122), (58, 100)],
        [(118, 18), (140, 12), (150, 28), (135, 40), (120, 34)],
        [(122, 48), (152, 46), (162, 70), (148, 102), (128, 86), (118, 60)],
        [(152, 12), (225, 10), (248, 32), (230, 62), (195, 70), (165, 50),
         (152, 28)],
        [(225, 108), (248, 105), (252, 120), (230, 124)],
    ]
    for poly in blobs:
        pts = [(x + px, y + py) for px, py in poly]
        draw.polygon(pts, fill=(52, 70, 98), outline=(70, 90, 120))
    # coral pins with white numbers
    for (px, py, num) in pins:
        draw.ellipse([x + px - 6, y + py - 6, x + px + 6, y + py + 6],
                     fill=CORAL, outline=(255, 255, 255), width=1)
        tw = draw.textlength(num, font=F_B(7))
        draw.text((x + px - tw / 2, y + py - 4), num, font=F_B(7),
                  fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 24            # main column left
    MC = 838           # main column right (rail starts at 846)
    RX = 846           # right rail left
    RW = 154           # right rail width

    # ---- Masthead: newspaper nameplate on cream ----
    d.text((24, 6), "The World in One Day", font=F_SERIF_B(28), fill=INK_NAVY)
    right = "36 STORIES  •  7 REGIONS  •  ALL FROM THIS ONE DAY"
    d.text((W - 24 - d.textlength(right, font=F_B(11)), 14), right,
           font=F_B(11), fill=INK_NAVY)
    d.text((24, 38), "Wednesday 25 November 2026", font=F_SERIF_B(26),
           fill=INK_NAVY)
    tagline = "take a breath — here's the day"
    d.text((W - 24 - d.textlength(tagline, font=F_SERIF(14)), 44), tagline,
           font=F_SERIF(14), fill=(120, 100, 80))
    d.text((24, 66), f"Edition No. 2  •  {PRESS_TIME}", font=F_B(11),
           fill=CORAL)
    # double rule, newspaper style
    d.line([(24, 79), (W - 24, 79)], fill=INK_NAVY, width=2)
    d.line([(24, 83), (W - 24, 83)], fill=INK_NAVY, width=1)

    # ---- Red italic deck line naming the 3 top stories (restored) ----
    deck = ("Putin vows retaliation   •   Huawei convicted on 10 of 12 "
            "counts   •   Senegal's AFCON title restored")
    d.text((24, 88), deck, font=F_SERIF_I(13), fill=CORAL)

    # ---- Region bar, slimmer (36 stories) ----
    ry = 108
    regions = [("WORLD", 3, NAVY), ("EUROPE", 7, BLUE),
               ("MID EAST", 5, RED), ("AFRICA", 6, BROWN),
               ("ASIA", 6, GREEN), ("AMERICAS", 7, TEAL),
               ("OCEANIA", 2, PURPLE)]
    total = 36
    rx = 24
    for name, n, col in regions:
        wseg = (W - 48) * n // total
        d.rounded_rectangle([rx, ry, rx + wseg - 2, ry + 15], radius=8,
                            fill=col)
        lab = f"{name} {n}"
        lfnt = F_B(9)
        if d.textlength(lab, font=lfnt) > wseg - 6:
            lfnt = F_B(8)
        d.text((rx + (wseg - 2) // 2, ry + 3), lab, font=lfnt,
               fill=(255, 255, 255), anchor="ma")
        rx += wseg

    # ---- Hero: the Huawei verdict, typographic (main column) ----
    hero_card(d, MX, 128, MC - MX, 166)

    # ---- Right rail: the day in numbers (dark navy, gold numbers) ----
    numbers = [("720,000", "Russian war dead (leaked)", "LEAKED RECORDS"),
               ("10/12", "Huawei counts guilty", "STORY 1"),
               ("~175", "migrants missing off Senegal", "STORY 18"),
               ("23", "injured, Colombia car bomb", "STORY 26"),
               ("5", "killed, Türkiye heli crash", "STORY 9"),
               ("12", "coral species 'resurrected'", "STORY 29")]
    right_rail(d, RX, 128, RW, 784, numbers)

    # ---- Three lead cards, text-only (one carries the Gulf diagram) ----
    ly, lh = 302, 156
    lw = (MC - MX - 2 * 10) // 3
    lead_card(d, MX, ly, lw, lh, CORAL_D, "EUROPE  •  WAR", "4",
              "Putin vows retaliation",
              "Putin tells oil chiefs retaliation is 'inevitable' as Kyiv "
              "keeps hitting refineries. — Independent",
              "REPORTED", scene="refinery")
    lead_card(d, MX + lw + 10, ly, lw, lh, BLUE, "EUROPE  •  WAR", "5",
              "Ukraine confirms Gulf of Finland ship strike",
              "Zelensky confirms it; Norway urges caution.",
              "REPORTED", scene="gulf")
    lead_card(d, MX + 2 * (lw + 10), ly, lw, lh, GREEN, "AFRICA  •  SPORT",
              "14", "Senegal's AFCON title restored",
              "CAS upholds Senegal's appeal; Morocco vows to appeal. "
              "— Reuters · AP",
              "OFFICIAL", scene="stadium")

    # ---- The day in UTC (main column) ----
    uy = 466
    d.rectangle([MX, uy, MC, uy + 19], fill=INK_NAVY_D)
    d.text((MX + 10, uy + 3), "THE DAY IN UTC", font=F_B(12), fill=GOLD)
    utc = ("23:18  Migrants missing, Senegal   •   00:23  DR Congo "
           "pullback   •   00:45  Türkiye crash   •   "
           "01:01  Cartagena held")
    d.text((MX + 10 + d.textlength("THE DAY IN UTC   ", font=F_B(12)), uy + 4),
           utc, font=F_R(11), fill=(255, 255, 255))

    # ---- Named medium section: THE DAY IN TWELVE MORE ----
    d.text((MX, 492), "THE DAY IN TWELVE MORE", font=F_B(15), fill=INK_NAVY)
    d.line([(MX, 510), (MX + 250, 510)], fill=CORAL, width=2)

    # ---- Twelve medium stories, 4 x 3, with topic banners + sources ----
    med = [
        ("2", "SPACE", "Asteroid eclipse photographed",
         "Hera catches Dimorphos' shadow.", "ESA", "REPORTED", "eclipse"),
        ("3", "MEDIA", "RFE/RL returns to shortwave",
         "New radio school for Afghan girls.", "RFE/RL", "REPORTED", "radio"),
        ("6", "SANCTIONS", "EU's 22nd sanctions package",
         "~60 banks off SWIFT; 70+ ships.", "UKRAINE MONITOR", "REPORTED",
         "sanctions"),
        ("7", "BUDGET", "Germany ties EU budget to Ukraine",
         "No budget deal till all 27 pay.", "REUTERS", "REPORTED", "budget"),
        ("8", "COURT", "Sarkozy, Bruni sent to trial",
         "First hearing 1 Apr 2027.", "REUTERS", "REPORTED", "court"),
        ("9", "CRASH", "Turkish heli crash kills 5",
         "Training flight in western Türkiye.", "WIREMINUTE", "REPORTED",
         "crash"),
        ("10", "STRIKE", "Strike kills Hamas official",
         "Abu Nahel killed in Gaza City.", "REUTERS", "REPORTED", "strike"),
        ("11", "EPIDEMIC", "Gaza meningitis epidemic alert",
         "Ministry warns after steep rise.", "ONE TURN", "REPORTED", "epidemic"),
        ("12", "TOWER", "Houthis hit Riyadh tower",
         "11 wounded; push toward Aden.", "REUTERS", "REPORTED", "tower"),
        ("13", "OIL", "Iraq to seize Kurdish oilfields",
         "Forces to take fields, crossings.", "STARLIT DAILY", "REPORTED",
         "oil"),
        ("15", "DRONES", "Sudan downs Blue Nile drones",
         "Count disputed: 4 vs 1.", "DEFENCEMENA", "CLAIM", "drones"),
        ("16", "EXODUS", "15,000 flee Blue Nile fighting",
         "Food aid cut to ~900,000 people.", "DABANGA · WFP", "REPORTED",
         "exodus"),
    ]
    colors = {"2": NAVY, "3": NAVY, "6": BLUE, "7": BLUE, "8": BLUE,
              "9": BLUE, "10": RED, "11": RED, "12": RED, "13": RED,
              "15": BROWN, "16": BROWN}
    mw = (MC - MX - 3 * 8) // 4
    mh = 74
    my0 = 516
    for i, (num, topic, head, cap, src, tg, scene) in enumerate(med):
        col = colors[num]
        mx = MX + (i % 4) * (mw + 8)
        my = my0 + (i // 4) * (mh + 4)
        medium_card(d, mx, my, mw, mh, col, num, topic, head, cap, src, tg,
                    scene=scene)

    # ---- Dark map + ALSO list (stories 17-36) ----
    by = 754
    d.text((MX, by), "WHERE IT HAPPENED", font=F_B(15), fill=INK_NAVY)
    d.text((MX + d.textlength("WHERE IT HAPPENED  ", font=F_B(15)), by + 2),
           "pins approximate", font=F_R(11), fill=GREY)
    map_x, map_y, map_w, map_h = MX, by + 22, 260, 136
    pins = [(84, 30, "1"), (158, 18, "4"), (144, 12, "5"),
            (122, 32, "6"), (134, 24, "31"), (155, 56, "10"),
            (168, 66, "12"), (180, 48, "32"), (112, 70, "14"),
            (100, 78, "18"), (126, 78, "33"), (148, 80, "15"),
            (198, 56, "19"), (230, 32, "21"), (242, 42, "34"),
            (212, 92, "22"), (242, 118, "29"), (64, 42, "24"),
            (60, 76, "26"), (72, 96, "35"), (42, 54, "36")]
    draw_map(d, map_x, map_y, map_w, map_h, pins)
    ax = 300
    d.text((ax, by), "ALSO ON WEDNESDAY 25 NOVEMBER", font=F_B(15),
           fill=INK_NAVY)
    also = [
        ("17", "DR Congo rebels pull back from Bunia"),
        ("18", "~175 migrants missing off Senegal"),
        ("19", "India 3rd in Asia Power Index 2026"),
        ("20", "Japan–India first live-fire missile drills"),
        ("21", "S. Korea scrambles jets over Russian planes"),
        ("22", "Indonesia VP successor names due today"),
        ("23", "China, Singapore expand yuan financing"),
        ("24", "Trump pardons turkeys Freedom & Feathers"),
        ("25", "Trump gives Medal of Freedom to Giuliani"),
        ("26", "Colombia car bomb injures 23"),
        ("27", "~20 hostages held in Cartagena store"),
        ("28", "Pentagon weighs $15bn Trump Jr.-linked loan"),
        ("29", "12 coral species 'resurrected' on the Reef"),
        ("30", "England beat Australia by 8 wickets, 2nd T20I"),
        ("31", "Poland blames Russia for drone incursion"),
        ("32", "Iran pharmacies shut amid drug shortages"),
        ("33", "Nigerian emir suspended after assault claim"),
        ("34", "Japan launches Asian oil task force"),
        ("35", "Supercell storm devastates Brazil town"),
        ("36", "Mexico to try 'El Chapo Isidro' anyway"),
    ]
    ay = by + 22
    col_w = 269
    for i, (num, txt) in enumerate(also):
        cx = ax + (i // 10) * col_w
        cy = ay + (i % 10) * 13
        d.text((cx, cy), num, font=F_B(11), fill=CORAL)
        d.text((cx + 22, cy), txt, font=F_R(10), fill=INK)

    # ---- Date check ----
    dy = 918
    d.rectangle([24, dy, W - 24, dy + 52], fill=(255, 255, 255),
                outline=CORAL, width=2)
    d.text((36, dy + 6), "DATE CHECK", font=F_B(14), fill=CORAL)
    dc = ("Every story here happened, or was first reported, Tue 24 – "
          "Wed 25 Nov 2026 (UTC) — except story 2 (Hera image: reported "
          "25 Nov, image date not firmly verified) and story 15 (Sudan "
          "drone count: 4 vs 1, disputed). Not today's news: Gibran "
          "resigned 12 Nov; Merkury, COP31 and Huang belong to the "
          "24 Nov edition.")
    lines = wrap(d, dc, F_R(11), W - 48 - 24)
    text_block(d, (36, dy + 24), lines, F_R(11), INK, 13)

    # ---- Footer ----
    d.text((W // 2, 976),
           "HOW SURE:  REPORTED = carried by the day's wires   •   CLAIM = one "
           "side's account, labelled as such   •   OFFICIAL = an official "
           "result or statement   •   ONGOING = still unfolding",
           font=F_R(10), fill=GREY, anchor="ma")
    d.text((W // 2, 988),
           "Sources: Reuters  •  AP  •  CNN  •  The Times  •  BBC  •  AFP  •  "
           "Al Jazeera  •  Euronews  •  SCMP  •  ProPublica  •  ScienceAlert  •  "
           "Lowy Institute  •  Independent  •  RFE/RL  •  WireMinute  •  "
           "Starlit Daily  •  DefenceMENA  •  Dabanga",
           font=F_R(8), fill=GREY, anchor="ma")
    d.text((W // 2, 1000),
           "Set in type and drawn in code, not photographs  •  The day, "
           "summed up gently — Wednesday 25 November 2026",
           font=F_R(10), fill=GREY, anchor="ma")

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
