"""Statuseffekte: 9x9-Icons für die Statusleiste + animierte Overlays (32x32), die über jede Figur gelegt werden.
Aufruf: python3 status.py
Ausgabe: status/icons.png, status/overlay_<effekt>.png (6 Frames nebeneinander), status/status.json,
         preview_status.gif
Overlay-Zelle 32x32: Figur (18x26) liegt bei (7, 6), Füße auf y=31, Kopfmitte ca. (16, 11).
Zusätzlich hat jeder Effekt eine Tönung (Farbe + Stärke) in status.json, die das Spiel auf die Figur legt.
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
import combat as cb, races as rc

OUT = os.path.join(g.BASE, 'status')
N, S = 6, 32
HEAD, FEET = (16, 11), 31
WHITE = (255, 255, 255, 255)

def P(px, x, y, c):
    if 0 <= x < S and 0 <= y < S: px[int(x), int(y)] = c

# ---------------------------------------------------------------- Overlays (Frame t = 0..5)
def brennen(t, px, d):
    for i, (x, by) in enumerate(((9, 27), (22, 24), (12, 17), (21, 14), (16, 30))):
        h = 4 + (i * 5 + t * 3) % 3; sway = (1 if (t + i) % 2 else -1)
        d.polygon([(x - 2, by), (x + 2, by), (x + 1, by - h + 2), (x + sway, by - h)], fill=C('#d8452e'))
        d.polygon([(x - 1, by), (x + 1, by), (x + sway * .5, by - h + 2)], fill=C('#ff9a3c'))
        P(px, x, by - 1, C('#ffe08a'))
    for i in range(3):
        y = 9 - (t * 2 + i * 4) % 10; P(px, 11 + i * 5 + (t % 2), y, C('#7a6a6a'))
def vergiftet(t, px, d):
    for i in range(4):
        ph = (t + i * 1.5) % N; y = 18 - ph * 2.2; x = 9 + i * 4.5 + math.sin(ph) * 1
        r = 1 if ph < 3 else 0
        col = C('#7ad84a') if ph < 4 else C('#4a8a3a')
        d.ellipse([x - r, y - r, x + r, y + r], fill=col) if r else P(px, x, y, col)
    for i in range(2): P(px, 12 + i * 8, 29 + (t + i) % 2, C('#7ad84a'))
def gelaehmt(t, px, d):
    rnd = [(5, 10, 9, 15, 6, 19), (25, 9, 22, 14, 26, 18), (8, 22, 12, 25, 7, 28), (24, 22, 20, 25, 25, 29)]
    for i, (a, b, c, e, f, h) in enumerate(rnd):
        if (t + i) % 3 == 0: continue
        col = C('#f0e8ff') if (t + i) % 2 else C('#b880ff')
        d.line([(a, b), (c, e), (f, h)], fill=col)
    if t % 3 == 0: P(px, 16, 3, C('#f0e8ff')); d.line([(15, 2), (17, 4)], fill=C('#b880ff'))
def gefroren(t, px, d):
    ice = C('#bfe8ff') + ()
    for x0, h in ((7, 7), (11, 5), (21, 6), (24, 8)):
        d.polygon([(x0 - 2, FEET), (x0 + 2, FEET), (x0, FEET - h)], fill=C('#bfe8ff')); d.line([(x0, FEET - h + 1), (x0, FEET - 1)], fill=WHITE)
    for i in range(3):
        a = t * .5 + i * 2.1; x = 16 + math.cos(a) * 11; y = 12 + math.sin(a) * 4 + i * 5
        P(px, x, y, WHITE); P(px, x - 1, y, C('#bfe8ff')); P(px, x + 1, y, C('#bfe8ff')); P(px, x, y - 1, C('#bfe8ff')); P(px, x, y + 1, C('#bfe8ff'))
def blutung(t, px, d):
    blood = C('#b8283a')
    for i, (x, y0) in enumerate(((11, 14), (19, 16), (14, 20))):
        ph = (t + i * 2) % N
        if ph < 4: P(px, x, y0 + ph * 2, blood); P(px, x, y0 + ph * 2 - 1, shade(blood, .8))
    for x in range(10, 22, 3):
        if (x + t) % 2: P(px, x, FEET, blood)
def verflucht(t, px, d):
    col, dk = C('#a070e0'), C('#3a2a5a')
    for i in range(4):
        a = t / N * 2 * math.pi + i * math.pi / 2; x = 16 + math.cos(a) * 10; y = 18 + math.sin(a) * 3
        P(px, x, y, col); P(px, x, y - 1, dk); P(px, x, y + 1, dk)
    y = 1 + (t % 2)  # kleiner Totenkopf über dem Kopf
    d.ellipse([13, y, 19, y + 5], fill=col); P(px, 15, y + 2, dk); P(px, 17, y + 2, dk); d.line([(15, y + 5), (17, y + 5)], fill=col)
def geblendet(t, px, d):
    for i, (x, y) in enumerate(((9, 5), (23, 6), (16, 2), (6, 12), (26, 13))):
        if (t + i) % 3 == 2: continue
        big = (t + i) % 3 == 0; col = C('#fff0a0')
        P(px, x, y, WHITE); P(px, x - 1, y, col); P(px, x + 1, y, col); P(px, x, y - 1, col); P(px, x, y + 1, col)
        if big: P(px, x - 2, y, col); P(px, x + 2, y, col); P(px, x, y - 2, col); P(px, x, y + 2, col)
def stille(t, px, d):
    y = 0 + (t // 3)
    d.rounded_rectangle([10, y, 22, y + 7], 2, fill=C('#f0e4cc')); d.polygon([(13, y + 7), (15, y + 7), (13, y + 9)], fill=C('#f0e4cc'))
    for k in range(3): P(px, 13 + k * 3, y + 3, C('#6a5a6a'))
    d.line([(10, y + 8), (22, y - 1)], fill=C('#d8403a')); d.line([(10, y + 7), (21, y - 1)], fill=C('#d8403a'))
def verlangsamt(t, px, d):
    y = 0
    d.ellipse([11, y, 21, y + 9], fill=C('#e8e0d0')); d.ellipse([12, y + 1, 20, y + 8], fill=C('#f8f4ea'))
    P(px, 16, y + 4, C('#2b1e33'))
    a = t / N * 2 * math.pi - math.pi / 2; d.line([(16, y + 4), (16 + math.cos(a) * 3, y + 4 + math.sin(a) * 3)], fill=C('#2b1e33'))
    d.line([(16, y + 4), (16, y + 2)], fill=C('#d8403a'))
    for i in range(3):
        x = 4 + ((t + i * 2) % N); P(px, x, 22 + i * 3, C('#9ac8c0'))
def schlaf(t, px, d):
    for i in range(3):
        ph = (t + i * 2) % N; x = 20 + ph + i; y = 8 - ph * 1.3
        s = 1 if i < 2 else 2
        col = C('#d8e8ff') if ph < 4 else C('#8a9ab8')
        d.line([(x, y), (x + 2 * s, y)], fill=col); d.line([(x + 2 * s, y), (x, y + 2 * s)], fill=col); d.line([(x, y + 2 * s), (x + 2 * s, y + 2 * s)], fill=col)
def manastau(t, px, d):
    for i in range(6):
        a = t / N * 2 * math.pi * (1 if i % 2 else -1) + i; r = 7 + (i % 3)
        P(px, HEAD[0] + math.cos(a) * r, HEAD[1] + math.sin(a) * r * .7, C('#8ad8ff') if i % 2 else C('#4a8ae0'))
    if t % 2 == 0:
        x = 16 + (t - 2) * 2; d.line([(x, 1), (x + 1, 3), (x - 1, 4), (x, 6)], fill=C('#f0e8ff'))
    for x, y in ((6, 6), (26, 7)):
        if (t + x) % 3 == 0: P(px, x, y, C('#ff8a7a'))
def staerkung(t, px, d):
    col = C('#e84a3a')
    for i in range(3):
        ph = (t + i * 2) % N; x = 7 + i * 9; y = 24 - ph * 3
        d.polygon([(x, y), (x - 2, y + 2), (x + 2, y + 2)], fill=col); d.line([(x, y + 2), (x, y + 4)], fill=col)
def schutz(t, px, d):
    col = C('#8ad0ff'); rim = C('#d8f0ff')
    p = [(x, y) for x in range(S) for y in range(S)]
    for x, y in p:
        r = ((x - 16) / 13) ** 2 + ((y - 17.5) / 15) ** 2
        if .86 < r <= 1.0 and (x + y + t) % 3: P(px, x, y, rim if (x * 3 + y + t * 2) % 7 == 0 else col[:3] + (200,))
    a = t / N * 2 * math.pi; P(px, 16 + math.cos(a) * 12, 17 + math.sin(a) * 14, WHITE)
def tempo(t, px, d):
    for i, y in enumerate((10, 15, 20, 25)):
        x = 4 - ((t * 3 + i * 5) % 8); L = 4 + i % 2 * 2
        d.line([(x, y), (x + L, y)], fill=C('#d8f0e8')); P(px, x + L + 1, y, C('#9ac8c0'))
    if t % 2: P(px, 26, FEET - 1, C('#c8b8a0')); P(px, 28, FEET - 2, C('#c8b8a0'))
def regeneration(t, px, d):
    col = C('#7ad84a')
    for i in range(3):
        ph = (t + i * 2) % N; x = 8 + i * 8; y = 26 - ph * 3.5
        c = col if ph < 4 else C('#c8f0a8')
        d.line([(x - 1, y), (x + 1, y)], fill=c); d.line([(x, y - 1), (x, y + 1)], fill=c)

EFFECTS = {  # Name: (Overlay, Tönung (Farbe, Stärke), Icon-Farbe, debuff?)
    'brennen': (brennen, ('#ff8a3a', .25), '#ff8a3a', True), 'vergiftet': (vergiftet, ('#6ac84a', .2), '#6ac84a', True),
    'gelaehmt': (gelaehmt, ('#e0d0ff', .2), '#b880ff', True), 'gefroren': (gefroren, ('#8ad0ff', .55), '#8ad0ff', True),
    'blutung': (blutung, ('#b8283a', .15), '#b8283a', True), 'verflucht': (verflucht, ('#3a2a5a', .4), '#a070e0', True),
    'geblendet': (geblendet, ('#fff0a0', .3), '#f0d070', True), 'stille': (stille, (None, 0), '#e8e0d0', True),
    'verlangsamt': (verlangsamt, ('#7a8a9a', .25), '#9ac8c0', True), 'schlaf': (schlaf, ('#2a2a4a', .15), '#a8b8e8', True),
    'manastau': (manastau, ('#4a8ae0', .2), '#4a8ae0', True), 'staerkung': (staerkung, ('#e84a3a', .12), '#e84a3a', False),
    'schutz': (schutz, (None, 0), '#8ad0ff', False), 'tempo': (tempo, (None, 0), '#9ac8c0', False),
    'regeneration': (regeneration, ('#7ad84a', .12), '#7ad84a', False),
}

def overlay(name, t):
    im = Image.new('RGBA', (S, S)); EFFECTS[name][0](t, im.load(), ImageDraw.Draw(im)); return im

# ---------------------------------------------------------------- Icons 9x9
def icon(name):
    _, _, col, debuff = EFFECTS[name]; col = C(col)
    im = Image.new('RGBA', (9, 9)); d = ImageDraw.Draw(im); px = im.load()
    frame = C('#6a2a3a') if debuff else C('#2a5a3a')
    d.rectangle([0, 0, 8, 8], fill=frame); d.rectangle([1, 1, 7, 7], fill=C('#2b1e33'))
    k = C('#2b1e33'); W = WHITE
    def pts(lst, c=col):
        for x, y in lst: px[x, y] = c
    if name == 'brennen': pts([(4, 2), (3, 3), (4, 3), (3, 4), (4, 4), (5, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (3, 6), (4, 6), (5, 6)]); pts([(4, 5), (4, 6)], C('#ffe08a'))
    elif name == 'vergiftet': pts([(4, 2), (3, 3), (4, 3), (5, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (3, 5), (4, 5), (5, 5)]); pts([(3, 4), (5, 4)], k); pts([(4, 6)])
    elif name == 'gelaehmt': pts([(5, 1), (4, 2), (3, 3), (4, 3), (5, 3), (4, 4), (3, 5), (2, 6), (3, 7)]) if False else pts([(5, 2), (4, 3), (3, 4), (4, 4), (5, 4), (4, 5), (3, 6)])
    elif name == 'gefroren': pts([(4, 2), (4, 3), (4, 5), (4, 6), (2, 4), (3, 4), (5, 4), (6, 4), (3, 3), (5, 5), (3, 5), (5, 3)]); pts([(4, 4)], W)
    elif name == 'blutung': pts([(4, 2), (4, 3), (3, 4), (4, 4), (5, 4), (3, 5), (4, 5), (5, 5), (4, 6)]); pts([(3, 4)], C('#ff8a8a'))
    elif name == 'verflucht': pts([(3, 2), (4, 2), (5, 2), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (2, 4), (4, 4), (6, 4), (3, 5), (4, 5), (5, 5), (3, 6), (5, 6)])
    elif name == 'geblendet': pts([(4, 2), (4, 3), (2, 4), (3, 4), (5, 4), (6, 4), (4, 5), (4, 6), (3, 3), (5, 5), (5, 3), (3, 5)]); pts([(4, 4)], W)
    elif name == 'stille': pts([(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (2, 3), (6, 3), (2, 4), (6, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (3, 6)]); pts([(2, 6), (3, 5), (4, 4), (5, 3), (6, 2)], C('#d8403a'))
    elif name == 'verlangsamt': pts([(3, 2), (4, 2), (5, 2), (2, 3), (6, 3), (2, 4), (6, 4), (2, 5), (6, 5), (3, 6), (4, 6), (5, 6)]); pts([(4, 3), (4, 4), (5, 4)], W)
    elif name == 'schlaf': pts([(2, 2), (3, 2), (4, 2), (4, 3), (3, 4), (2, 5), (3, 5), (4, 5)]); pts([(5, 5), (6, 5), (6, 6), (5, 7) if False else (5, 6)], C('#d8e8ff'))
    elif name == 'manastau': pts([(3, 2), (4, 2), (5, 2), (2, 3), (6, 3), (2, 4), (4, 4), (6, 4), (2, 5), (5, 5), (3, 6), (4, 6)]); pts([(4, 4)], W)
    elif name == 'staerkung': pts([(4, 2), (3, 3), (4, 3), (5, 3), (2, 4), (4, 4), (6, 4), (4, 5), (4, 6)])
    elif name == 'schutz': pts([(2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (3, 5), (4, 5), (5, 5), (4, 6)]); pts([(4, 3), (4, 4)], W)
    elif name == 'tempo': pts([(2, 3), (3, 3), (4, 3), (3, 5), (4, 5), (5, 5), (6, 5)]); pts([(5, 2), (6, 3), (5, 4) if False else (5, 3)], col); pts([(6, 4)], col)
    elif name == 'regeneration': pts([(4, 2), (4, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (4, 5), (4, 6)])
    return im

# ---------------------------------------------------------------- Ausgabe + Vorschau
def on_char(base, name, t):
    tc, k = EFFECTS[name][1]
    fig = cb.tint(base, C(tc), k * (0.8 + 0.2 * math.sin(t))) if tc else base
    if name == 'gefroren': fig = base if False else fig
    if name == 'schlaf': fig = cb.kneel(fig)
    c = Image.new('RGBA', (S, S)); dy = 1 if name == 'gelaehmt' and t % 2 else 0
    c.alpha_composite(fig, (7 + (t % 2 if name == 'gelaehmt' else 0), 6 - dy * 0)); c.alpha_composite(overlay(name, t))
    return c

def main():
    os.makedirs(OUT, exist_ok=True); names = list(EFFECTS)
    ic = Image.new('RGBA', (9 * len(names), 9))
    for i, n in enumerate(names): ic.alpha_composite(icon(n), (i * 9, 0))
    ic.save(os.path.join(OUT, 'icons.png'))
    meta = {'zelle': S, 'frames': N, 'figur_offset': [7, 6], 'icon_groesse': 9, 'effekte': {}}
    for i, n in enumerate(names):
        sh = Image.new('RGBA', (S * N, S))
        for t in range(N): sh.alpha_composite(overlay(n, t), (t * S, 0))
        sh.save(os.path.join(OUT, f'overlay_{n}.png'))
        tc, k = EFFECTS[n][1]
        meta['effekte'][n] = {'icon_index': i, 'art': 'schwaechung' if EFFECTS[n][3] else 'staerkung', 'toenung': tc, 'toenung_staerke': k,
                              'fps': 8, 'hinweis': 'Figur knien lassen' if n == 'schlaf' else 'Figur zittern lassen (±1 px)' if n == 'gelaehmt' else ''}
    json.dump(meta, open(os.path.join(OUT, 'status.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau: Mensch (Tunika) von der Seite, jeder Effekt
    base, _ = cb.compose(rc.RACES[0], 'tunika', 'side', arm='mid')
    Z, cols = 3, 5; cw, chh = S * Z + 8, S * Z + 26; rows = math.ceil(len(names) / cols)
    frames = []
    for t in range(N):
        im = Image.new('RGB', (cols * cw + 8, rows * chh + 8), (42, 36, 69)); d = ImageDraw.Draw(im)
        for i, n in enumerate(names):
            x, y = 8 + (i % cols) * cw, 8 + (i // cols) * chh
            d.rectangle([x, y, x + S * Z - 1, y + S * Z - 1], fill=(58, 52, 70))
            c = on_char(base, n, t).resize((S * Z, S * Z), Image.NEAREST); im.paste(c, (x, y), c)
            ib = icon(n).resize((18, 18), Image.NEAREST); im.paste(ib, (x, y + S * Z + 3), ib)
            d.text((x + 22, y + S * Z + 5), n, fill=(230, 220, 200), font=g.font(11))
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_status.gif'), save_all=True, append_images=frames[1:], duration=140, loop=0)

if __name__ == '__main__':
    main()
