"""Dungeon-Fallen in Seitenansicht (für den Plattformer).
Aufruf: python3 sidetraps.py
Ausgabe: dungeon/fallen_seite/<falle>_<animation>.png (Bilder nebeneinander), dungeon/fallen_seite/fallen_seite.json,
         preview_fallen_seite.gif
Alle Fallen stehen auf einer Bodenkante (unterste 16 px = Boden aus dem Tileset dungeon_physisch).
Pendelklinge, Pfeilfalle, Felsbrocken, Fallgatter und Einsturz waren schon seitlich -> aus dungeon/fallen übernehmen.
"""
import os, json, math, random
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
from dungeon import F, preview, strip, STEEL, STEEL_L, STEEL_D, BLOOD, BLOOD_D, BLOOD_L, FIRE, POISON, ARCANE, THORN, THORN_D, THORN_L
import sidetiles as st

OUT = os.path.join(g.BASE, 'dungeon', 'fallen_seite')
WHITE = (255, 255, 255, 255)
BLOCK = st.terrain_tile('dungeon_physisch', 15)

def ground(f, gaps=()):
    """Boden: zwei Blöcke à 16 px, oberste Kante bei y = H-16."""
    y0 = f.H - 16
    for i in range(f.W // 16):
        if i in gaps: continue
        f.im.alpha_composite(BLOCK, (i * 16, y0))
    return y0

def stacheln(t, mode):
    f = F(32, 40); y0 = ground(f)
    for x in range(3, 30, 6): f.rect(x, y0, x + 3, y0 + 1, C('#140e18'))
    hs = [0, 0, 4, 12, 12, 12, 6, 0][t] if mode == 'ausloesen' else 0
    if mode == 'ausloesen' and t == 1:
        for x in range(4, 30, 6): f.s(x + 1, y0 - 1, WHITE)
    for x in range(3, 30, 6):
        if hs:
            f.poly([(x, y0), (x + 3, y0), (x + 1.5, y0 - hs)], STEEL); f.line((x + 1, y0 - 1), (x + 1, y0 - hs + 2), STEEL_L)
    return f.im

def druckplatte(t, mode):
    f = F(32, 24); y0 = ground(f)
    d = [0, 2, 2, 1][t] if mode == 'ausloesen' else 0
    f.rect(8, y0 - 3 + d, 23, y0, C('#7a7488')); f.rect(8, y0 - 3 + d, 23, y0 - 3 + d, C('#948ea2'))
    if mode == 'ausloesen' and t == 2:
        for x in (6, 25): f.s(x, y0 - 4, WHITE)
    return f.im

def einbruch(t, mode):
    """Boden bricht ein (Fallgrube von der Seite)."""
    f = F(48, 48)
    k = t if mode == 'einbrechen' else 0
    y0 = f.H - 32
    for i in range(3):
        if i == 1 and k >= 3:
            fall = (k - 2) ** 2 * 3
            if y0 + fall < f.H: f.im.alpha_composite(BLOCK, (16, int(y0 + fall)))
            for j in range(3): f.disc(14 + j * 10, y0 + fall - 3 - j, 1.5, C('#8a8098'))
        else:
            f.im.alpha_composite(BLOCK, (i * 16, y0)); f.im.alpha_composite(BLOCK, (i * 16, y0 + 16)) if i != 1 else None
    if k >= 1 and k < 3:
        f.line((18, y0), (22, y0 + 6), C('#140e18')); f.line((22, y0 + 6), (28, y0 + 3), C('#140e18'))
        if k == 2: f.line((26, y0 + 2), (30, y0 + 10), C('#140e18'))
    if k >= 3: f.rect(16, y0 + 16, 31, f.H - 1, C('#0c0810'))
    return f.im

def saege(t, mode):
    f = F(40, 32); y0 = ground(f)
    f.rect(2, y0, 37, y0 + 2, C('#140e18'))
    x = 8 + (math.sin(t / 8 * 2*math.pi) + 1) * 12
    for k in range(20):
        a = k / 20 * 2*math.pi + t * .7
        r = 9 if k % 2 else 7.5
        yy = y0 + math.sin(a) * r
        if yy <= y0: f.s(x + math.cos(a) * r, yy, STEEL if k % 2 else STEEL_D)
    for yy in range(int(y0 - 7), y0):
        for xx in range(int(x - 7), int(x + 8)):
            if (xx - x) ** 2 + (yy - y0) ** 2 <= 49: f.s(xx, yy, STEEL if (xx + yy) % 5 else STEEL_L)
    f.disc(x, y0 - 1, 1.5, STEEL_D)
    for k in range(3): f.s(x + 6 + k, y0 - 1 - (t + k) % 3, C('#fff07a'))
    return f.im

def baerenfalle(t, mode):
    f = F(32, 28); y0 = ground(f)
    k = [0, 1, 2, 2][t] if mode == 'zuschnappen' else 0
    cx = 16
    if k == 0:
        f.line((cx - 12, y0 - 1), (cx + 12, y0 - 1), STEEL)
        for i in range(6): f.poly([(cx - 11 + i * 4, y0 - 1), (cx - 9 + i * 4, y0 - 1), (cx - 10 + i * 4, y0 - 4)], STEEL_L)
        f.rect(cx - 2, y0 - 2, cx + 2, y0 - 1, STEEL_D)
    else:
        ang = [0, .7, 1.45][k]
        for s in (-1, 1):
            ex = cx + s * 12 * math.cos(ang); ey = y0 - 1 - 12 * math.sin(ang)
            f.line((cx, y0 - 1), (ex, ey), STEEL, 2)
            for j in range(3):
                px_, py_ = cx + s * (4 + j * 3) * math.cos(ang), y0 - 1 - (4 + j * 3) * math.sin(ang)
                f.poly([(px_, py_), (px_ - s * 2, py_ - 1), (px_ - s * 1, py_ + 2)], STEEL_L)
        if k == 2:
            for p_ in ((cx - 4, y0 - 16), (cx + 4, y0 - 16), (cx, y0 - 18)): f.s(*p_, WHITE)
    return g.outline(f.im)

def gas(t, mode):
    f = F(32, 48); y0 = ground(f)
    f.rect(11, y0, 20, y0 + 2, C('#2a2430'))
    for k in range(3): f.line((12 + k * 3, y0), (13 + k * 3, y0 + 2), POISON[2])
    for i in range(7):
        p = ((t + i * 8 / 7) % 8) / 8
        x = 16 + math.sin(i * 1.7 + p * 3) * (3 + p * 9); y = y0 - 2 - p * 26
        r = 2 + p * 4
        if p < .9:
            f.disc(x, y, r, POISON[2] if p > .6 else POISON[1]); f.disc(x - r * .3, y - r * .3, r * .5, POISON[0] if p < .5 else POISON[1])
    return f.im

def feuer(t, mode):
    f = F(32, 56); y0 = ground(f)
    f.rect(11, y0, 20, y0 + 2, C('#2a2430'))
    for k in range(4): f.rect(12 + k * 2, y0, 12 + k * 2, y0 + 2, STEEL_D)
    h = [0, 0, 10, 26, 36, 36, 20, 6][t] if mode == 'ausloesen' else 0
    if mode == 'ausloesen' and t == 1:
        for k in range(5): f.s(13 + k * 2, y0 - 1 - (k % 2), FIRE[1])
    if mode == 'bereit': f.s(15, y0 - 1, FIRE[3]); f.s(17, y0 - 1, FIRE[2])
    if h:
        for y in range(int(y0 - h), y0):
            k = (y0 - y) / h; wd = (1 - k) * 6 + 2 + math.sin(y * .7 + t) * 1.2
            for x in range(int(16 - wd), int(16 + wd) + 1):
                d = abs(x - 16) / max(1, wd)
                f.s(x, y, FIRE[0] if d < .3 and k < .7 else FIRE[1] if d < .6 else FIRE[2] if k < .8 else FIRE[3])
    return f.im

def dornen(t, mode):
    f = F(32, 48); y0 = ground(f)
    k = [0, 1, 3, 6, 10, 10, 5, 2][t] if mode == 'ausloesen' else 0
    if mode == 'ausloesen' and 1 <= t <= 6:
        f.line((6, y0), (10, y0 + 4), C('#140e18')); f.line((18, y0), (16, y0 + 5), C('#140e18')); f.line((26, y0), (24, y0 + 3), C('#140e18'))
    for i in range(5):
        pts = [(4 + i * 6, y0)]
        for j in range(k):
            a = -math.pi / 2 + math.sin(j * .9 + i * 2 + t * .4) * .5
            pts.append((pts[-1][0] + math.cos(a) * 2.8, pts[-1][1] + math.sin(a) * 2.8))
        for a_, b_ in zip(pts, pts[1:]): f.line(a_, b_, THORN, 2)
        for j, (x, y) in enumerate(pts[1:]):
            if j % 2: f.s(x + 2, y, THORN_L); f.s(x - 2, y - 1, C('#c8b898'))
        if k >= 6: f.s(pts[-1][0], pts[-1][1] - 1, C('#c83a3a'))
    return f.im

def blut(t, mode):
    f = F(32, 48); y0 = ground(f)
    f.rect(2, y0 - 1, 29, y0, BLOOD); f.rect(4, y0 - 2, 27, y0 - 2, BLOOD_D)
    if mode == 'idle':
        for k in range(3): f.s(6 + ((t * 5 + k * 9) % 22), y0 - 2, BLOOD_L)
        return f.im
    h = [0, 2, 10, 22, 22, 14, 5, 0][t]
    if t in (1, 2):
        for k in range(4): f.disc(6 + k * 6, y0 - 3, 1.2, BLOOD_L)
    for i, x in enumerate((7, 13, 19, 25)):
        hh = h * (1 if i % 2 == 0 else .7)
        if hh: f.poly([(x - 2, y0 - 1), (x + 2, y0 - 1), (x, y0 - 1 - hh)], BLOOD); f.line((x - 1, y0 - 2), (x, y0 - hh), BLOOD_L)
    if t in (4, 5):
        rng = random.Random(t)
        for _ in range(8): f.s(16 + rng.uniform(-14, 14), y0 - 10 - rng.uniform(0, 14), BLOOD)
    return f.im

def rune(t, mode):
    f = F(32, 56); y0 = ground(f)
    glow = [0, .2, .4, .6, .8, 1, .6, .2][t] if mode == 'ausloesen' else .15 + .1 * math.sin(t / 4 * 2*math.pi)
    for i in range(6):
        lit = mode != 'ausloesen' or i <= t
        x = 4 + i * 5
        col = ARCANE[0] if lit and glow > .3 else mix(C('#5a4a7a'), ARCANE[1], glow)
        f.s(x, y0, col); f.s(x + 1, y0, col); f.s(x, y0 + 1, mix(C('#5a4a7a'), ARCANE[2], glow))
    if mode == 'ausloesen' and t in (5, 6):
        wd = 7 if t == 5 else 4
        for y in range(0, y0):
            for x in range(16 - wd, 16 + wd + 1):
                d = abs(x - 16) / wd
                if d < .4: f.s(x, y, ARCANE[0])
                elif d < .8: f.s(x, y, ARCANE[1])
                elif (x + y) % 2: f.s(x, y, ARCANE[2])
    if mode == 'ausloesen' and t >= 6:
        for i in range(8): a = i * .8 + t; f.s(16 + math.cos(a) * (t - 3) * 3, y0 - 6 + math.sin(a) * (t - 3) * 2, ARCANE[1])
    return f.im

def flut(t, mode):
    f = F(48, 56)
    for x0 in (0, 32): f.rect(x0, 0, x0 + 15, f.H - 1, C('#3e384c'))
    f.im.alpha_composite(BLOCK, (16, f.H - 16))
    for x0 in (0, 32):
        for y in range(0, f.H, 6): f.line((x0, y), (x0 + 15, y), C('#2e2a3a'))
    level = min(1, t / 7) if mode == 'fluten' else 1
    if mode == 'fluten' and t < 3:
        for i in range(3): f.s(18 + i * 6, f.H - 17 - ((t + i) % 3), C('#8ac4ee'))
    if level:
        top = int(f.H - 16 - level * 34)
        for y in range(top, f.H - 16):
            for x in range(16, 32):
                wv = math.sin((x + t * 3) * .6) if y < top + 2 else 0
                if y + wv >= top:
                    c = C('#e8f8ff') if y < top + 1 else C('#5ab0f0') if y < top + 6 else C('#3a80c8')
                    f.s(x, y, c[:3] + (220 if y > top + 1 else 255,))
    return f.im

def mimik(t, mode):
    f = F(32, 40); y0 = ground(f)
    if mode == 'atmen':
        if t in (1, 2): f.rect(4, y0 - 1, 27, y0 - 1, C('#7a5a6a'))
        return f.im
    o = [0, 1, 4, 9, 12, 4, 0, 0][t]
    if o:
        f.rect(4, y0 - o - 2, 27, y0 + 2, C('#2a0c14'))
        f.ell(4, y0 - o - 2, 27, y0 + 4, C('#5a1e2a'))
        f.ell(6, y0 - o, 25, y0 + 2, C('#2a0c14'))
        for k in range(6):
            x = 6 + k * 4
            f.poly([(x, y0 - o), (x + 3, y0 - o), (x + 1.5, y0 - o + 4)], C('#f4f0e0'))
            f.poly([(x, y0 + 1), (x + 3, y0 + 1), (x + 1.5, y0 - 3)], C('#f4f0e0'))
        if o >= 9: f.ell(10, y0 - 4, 22, y0, C('#c84a6a'))
        f.im.alpha_composite(BLOCK.crop((0, 0, 16, 6)), (2, int(y0 - o - 8)))
        f.im.alpha_composite(BLOCK.crop((0, 0, 16, 6)), (16, int(y0 - o - 8)))
    if t == 5:
        for p_ in ((3, y0 - 14), (28, y0 - 14), (16, y0 - 18)): f.s(*p_, WHITE)
    return f.im

TRAPS = [('stachelfalle', 'Stachelfalle', stacheln, [('idle', 1), ('ausloesen', 8)]),
         ('druckplatte', 'Druckplatte', druckplatte, [('idle', 1), ('ausloesen', 4)]),
         ('einbruch', 'Einbrechender Boden', einbruch, [('idle', 1), ('einbrechen', 8)]),
         ('saegeblatt', 'Sägeblatt im Boden', saege, [('laufen', 8)]),
         ('baerenfalle', 'Bärenfalle', baerenfalle, [('offen', 1), ('zuschnappen', 4)]),
         ('giftgas', 'Giftgas', gas, [('stroemen', 8)]),
         ('feuerduese', 'Feuerdüse', feuer, [('bereit', 1), ('ausloesen', 8)]),
         ('dornenfalle', 'Dornenfalle (Dorn-Dungeon)', dornen, [('idle', 1), ('ausloesen', 8)]),
         ('blutfalle', 'Blutfalle (Blut-Dungeon)', blut, [('idle', 4), ('ausloesen', 8)]),
         ('runenfalle', 'Runenfalle (Erinnerungs-Dungeon)', rune, [('idle', 4), ('ausloesen', 8)]),
         ('flutraum', 'Flutraum', flut, [('fluten', 8), ('voll', 4)]),
         ('mimikboden', 'Mimik-Boden', mimik, [('atmen', 4), ('zuschnappen', 8)])]

def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'hinweis': 'Seitenansicht; unterste 16 px = Bodenblock. Pendelklinge, Pfeilfalle, Felsbrocken, Fallgatter und Einsturz liegen in dungeon/fallen.', 'fallen': {}}
    prev = []
    for key, title, fn, anims in TRAPS:
        meta['fallen'][key] = {'titel': title, 'animationen': {}}
        seq = []
        for anim, n in anims:
            fr = [fn(t, anim) for t in range(n)]
            strip(fr).save(os.path.join(OUT, f'{key}_{anim}.png'))
            meta['fallen'][key]['animationen'][anim] = {'bilder': n, 'bild': list(fr[0].size)}
            seq += fr if n > 1 else fr * 2
        prev.append((title, seq))
    json.dump(meta, open(os.path.join(OUT, 'fallen_seite.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(prev, os.path.join(g.BASE, 'preview_fallen_seite.gif'), S=3, cols=6, n_frames=12, title='Fallen in Seitenansicht')

if __name__ == '__main__':
    main()
