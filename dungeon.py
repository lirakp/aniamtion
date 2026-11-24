"""Dungeon-Animationen: Fallen, Truhen und kleine Detail-Animationen.
Aufruf: python3 dungeon.py
Ausgabe: dungeon/fallen/<falle>_<animation>.png, dungeon/truhen/<truhe>_<animation>.png,
         dungeon/details/<detail>.png, dungeon/dungeon.json, preview_fallen.gif, preview_truhen.gif, preview_details.gif
Bilder liegen nebeneinander. Fallen sind Bodenkacheln (32x32) bzw. Wandkacheln; Größen stehen in dungeon.json.
"""
import os, math, random, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'dungeon')
WHITE = (255, 255, 255, 255)
STONE, STONE_D, STONE_L, MORTAR = C('#4e4860'), C('#3e384c'), C('#625a76'), C('#2e2a3a')
STEEL, STEEL_L, STEEL_D = C('#b8bccc'), C('#eceef4'), C('#6a6e80')
WOOD, WOOD_D, WOOD_L = C('#7a5236'), C('#4d3324'), C('#9c6c46')
BLOOD, BLOOD_D, BLOOD_L = C('#a8283a'), C('#6a1424'), C('#e05a5a')
GOLD, GOLD_L = C('#e0b048'), C('#fff0a0')
FIRE = [C('#fff4c8'), C('#ffd27a'), C('#ff9a3c'), C('#d8452e')]
POISON = [C('#d8f07a'), C('#8ad04a'), C('#5a9a3a')]
ARCANE = [C('#f0e4ff'), C('#b8a0ff'), C('#7a5ad0')]
THORN, THORN_D, THORN_L = C('#3a4a2a'), C('#22301c'), C('#5a6e3a')

class F:
    def __init__(self, w, h, seed=0):
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); self.px = self.im.load(); self.d = ImageDraw.Draw(self.im)
        self.W, self.H = w, h; self.rng = random.Random(seed)
    def s(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.W and 0 <= y < self.H: self.px[x, y] = c
    def rect(self, x0, y0, x1, y1, c):
        if x1 >= x0 and y1 >= y0: self.d.rectangle([x0, y0, x1, y1], fill=c)
    def ell(self, x0, y0, x1, y1, c):
        if x1 >= x0 and y1 >= y0: self.d.ellipse([x0, y0, x1, y1], fill=c)
    def poly(self, pts, c): self.d.polygon(pts, fill=c)
    def line(self, a, b, c, w=1): self.d.line([a, b], fill=c, width=w)
    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if (x + .5 - cx)**2 + (y + .5 - cy)**2 <= r*r: self.s(x, y, c)
    def outlined(self): return g.outline(self.im)

def floor(f, oy=0):
    rng = random.Random(7)
    f.rect(0, oy, f.W - 1, oy + 31, MORTAR)
    for row in range(4):
        off = (row % 2) * 4
        for col in range(-1, 5):
            x0 = col * 8 + off; y0 = oy + row * 8
            c = shade(STONE, rng.uniform(.9, 1.1))
            f.rect(max(0, x0 + 1), y0 + 1, min(f.W - 1, x0 + 7), y0 + 7, c)
            if 0 <= x0 + 1 < f.W: f.rect(x0 + 1, y0 + 1, min(f.W - 1, x0 + 6), y0 + 1, mix(c, WHITE, .12))

def wall(f, oy=0, h=32):
    rng = random.Random(9)
    f.rect(0, oy, f.W - 1, oy + h - 1, MORTAR)
    for row in range(h // 6 + 1):
        off = (row % 2) * 5
        for col in range(-1, f.W // 10 + 2):
            x0 = col * 10 + off; y0 = oy + row * 6
            c = shade(C('#5a5468'), rng.uniform(.9, 1.1))
            f.rect(max(0, x0 + 1), y0 + 1, min(f.W - 1, x0 + 9), min(oy + h - 1, y0 + 5), c)

# ================================================================ FALLEN
HOLES = [(8, 12), (16, 12), (24, 12), (8, 21), (16, 21), (24, 21)]

def t_stachel(t, mode):
    f = F(32, 44); floor(f, 12)
    press = 1 if mode == 'ausloesen' and t == 1 else 0
    f.rect(4, 19 + press, 27, 38 + press, C('#5a5468')); f.rect(4, 19 + press, 27, 19 + press, STONE_L)
    hs = [0, 0, 3, 10, 10, 10, 5, 0][t] if mode == 'ausloesen' else 0
    for x, y in HOLES:
        f.ell(x - 2, y + 9, x + 2, y + 11, MORTAR)
    for x, y in HOLES:
        if hs:
            f.poly([(x - 2, y + 10), (x + 2, y + 10), (x, y + 10 - hs)], STEEL)
            f.line((x - 1, y + 9), (x - 1, y + 11 - hs), STEEL_L)
            if t == 4: f.s(x, y + 10 - hs, BLOOD_L)
    return f.im

def t_pfeil(t, mode):
    f = F(32, 32); wall(f)
    f.rect(6, 14, 25, 17, C('#140e18')); f.rect(6, 13, 25, 13, STONE_D)
    if mode == 'ausloesen':
        if t == 1: f.s(24, 15, STEEL_L); f.s(23, 15, STEEL)
        if t == 2: f.rect(20, 15, 27, 15, WOOD); f.poly([(27, 14), (30, 15), (27, 16)], STEEL)
        if t >= 3:
            for k in range(t - 2): f.disc(28 + k*1.5, 15 + (k % 2) * 2 - 1, 1.6, C('#8a8098'))
    return f.im

def t_pfeil_flug(t, mode):
    f = F(20, 7)
    f.rect(2, 3, 14, 3, WOOD); f.poly([(14, 1), (19, 3), (14, 5)], STEEL)
    f.line((2, 3), (0, 1 + t % 2), C('#e8e0d0')); f.line((3, 3), (1, 5 - t % 2), C('#e8e0d0'))
    return f.im

def t_druckplatte(t, mode):
    f = F(32, 32); floor(f)
    d = [0, 2, 2, 1][t] if mode == 'ausloesen' else 0
    f.rect(8, 9 + d, 23, 22 + d, C('#6a6276')); f.rect(8, 9 + d, 23, 9 + d, STONE_L if not d else STONE_D)
    f.rect(8, 22 + d, 23, 23, MORTAR)
    if mode == 'ausloesen' and t == 2:
        for x, y in ((6, 8), (25, 8), (6, 24), (25, 24)): f.s(x, y, WHITE)
    return f.im

def t_fallgrube(t, mode):
    f = F(32, 32); floor(f)
    k = t if mode == 'oeffnen' else (7 - t)
    if k >= 1:
        for a, b in (((6, 10), (14, 16)), ((14, 16), (24, 12)), ((14, 16), (16, 26))): f.line(a, b, MORTAR)
    if k >= 3:
        r = min(1, (k - 2) / 4)
        f.ell(16 - 13*r, 16 - 11*r, 16 + 13*r, 16 + 11*r, C('#0c0810'))
        f.ell(16 - 13*r, 16 - 11*r, 16 + 13*r, 16 - 11*r + 4, C('#241c2c'))
        for i in range(6 if k < 6 else 0):
            a = i * 1.05 + k; rr = 9 * r
            f.rect(16 + math.cos(a)*rr - 1, 16 + math.sin(a)*rr*.8 + (k - 3)*2, 16 + math.cos(a)*rr + 1, 16 + math.sin(a)*rr*.8 + (k - 3)*2 + 1, STONE)
    return f.im

def t_pendel(t, mode):
    f = F(40, 48)
    f.rect(16, 0, 23, 3, C('#3a3446')); f.rect(18, 4, 21, 5, STEEL_D)
    a = math.sin(t / 8 * 2*math.pi) * .9
    px_, py_ = 20, 4
    ex, ey = px_ + math.sin(a) * 30, py_ + math.cos(a) * 30
    f.line((px_, py_), (ex, ey), C('#5a5e6e'), 2)
    for k in range(-36, 37):
        aa = a + k * .011
        for r_ in range(30, 38):
            c = STEEL_L if r_ == 37 else STEEL if r_ > 32 else STEEL_D
            f.s(px_ + math.sin(aa) * r_, py_ + math.cos(aa) * r_, c)
    if abs(math.cos(t / 8 * 2*math.pi)) > .7:
        for k in range(4): f.s(px_ + math.sin(a - .35 * (1 if math.sin(a) > 0 else -1)) * (34 + k), py_ + math.cos(a) * (34 + k) - 1, C('#c8ccd8'))
    return g.outline(f.im)

def t_feuer(t, mode):
    f = F(32, 56); floor(f, 24)
    f.ell(10, 34, 21, 40, C('#2a2430')); f.ell(11, 35, 20, 39, C('#140e18'))
    for k in range(4): f.rect(11 + k*3, 34, 11 + k*3, 40, STEEL_D)
    h = [0, 0, 8, 22, 30, 30, 18, 6][t] if mode == 'ausloesen' else 0
    if mode == 'ausloesen' and t == 1:
        for k in range(5): f.s(13 + k*2, 33 - (k % 2), FIRE[1])
    if h:
        for y in range(int(37 - h), 37):
            k = (37 - y) / h
            w = (1 - k) * 6 + 2 + math.sin(y * .7 + t) * 1.2
            for x in range(int(16 - w), int(16 + w) + 1):
                d = abs(x - 16) / max(1, w)
                f.s(x, y, FIRE[0] if d < .3 and k < .7 else FIRE[1] if d < .6 else FIRE[2] if k < .8 else FIRE[3])
    elif mode == 'bereit':
        f.s(15, 37, FIRE[3]); f.s(17, 37, FIRE[2])
    return f.im

def t_gift(t, mode):
    f = F(32, 40); floor(f, 8)
    f.ell(11, 18, 21, 23, C('#2a2430'))
    for k in range(3): f.line((12 + k*3, 19), (13 + k*3, 22), POISON[2])
    rng = random.Random(3)
    for i in range(7):
        p = ((t + i * 8/7) % 8) / 8
        x = 16 + math.sin(i * 1.7 + p * 3) * (4 + p * 10); y = 20 - p * 18
        r = 2 + p * 4
        if p < .9:
            f.disc(x, y, r, POISON[2] if p > .6 else POISON[1]); f.disc(x - r*.3, y - r*.3, r*.5, POISON[0] if p < .5 else POISON[1])
    return f.im

def t_fels(t, mode):
    f = F(32, 32)
    f.ell(4, 27, 28, 31, (20, 14, 30, 90))
    f.disc(16, 16, 12, C('#7a7280')); f.disc(14, 13, 8, C('#8a8296')); f.disc(12, 10, 3, C('#a8a0b4'))
    a = t / 4 * math.pi / 2
    for k in range(3):
        aa = a + k * 2.1
        x0, y0 = 16 + math.cos(aa) * 4, 16 + math.sin(aa) * 4
        f.line((x0, y0), (16 + math.cos(aa) * 10, 16 + math.sin(aa) * 10), C('#5a5262'))
    for k in range(3): f.disc(4 - k*2 + (t % 2), 27 - k*2, 1.5, C('#a89a8a'))
    return g.outline(f.im)

def t_saege(t, mode):
    f = F(32, 32); floor(f)
    f.rect(3, 15, 28, 18, C('#140e18')); f.rect(3, 15, 28, 15, MORTAR)
    x = 8 + abs(((t / 8) * 2 % 2) - 1) * 16 if False else 8 + (math.sin(t / 8 * 2*math.pi) + 1) * 8
    for k in range(16):
        a = k / 16 * 2*math.pi + t * .7
        r = 8 if k % 2 else 6.5
        f.s(x + math.cos(a) * r, 13 + math.sin(a) * r * .9, STEEL if k % 2 else STEEL_D)
    f.disc(x, 13, 6, STEEL); f.disc(x - 1, 12, 3, STEEL_L); f.disc(x, 13, 1.5, STEEL_D)
    for k in range(3): f.s(x + 4 + k, 18 - (t + k) % 3, C('#fff07a'))
    return f.im

def t_dornen(t, mode):
    f = F(32, 44); floor(f, 12)
    k = [0, 1, 3, 6, 9, 9, 5, 2][t] if mode == 'ausloesen' else 0
    if mode == 'ausloesen' and t >= 1:
        for a, b in (((6, 26), (16, 30)), ((16, 30), (26, 25)), ((16, 30), (14, 40))): f.line(a, b, THORN_D)
    for i in range(5):
        bx = 6 + i * 5
        pts = [(bx, 32)]
        for j in range(k):
            a = -math.pi/2 + math.sin(j * .9 + i * 2 + t * .4) * .6
            pts.append((pts[-1][0] + math.cos(a) * 2.6, pts[-1][1] + math.sin(a) * 2.6))
        for a_, b_ in zip(pts, pts[1:]): f.line(a_, b_, THORN, 2)
        for j, (x, y) in enumerate(pts[1:]):
            if j % 2: f.s(x + 2, y, THORN_L); f.s(x - 2, y - 1, C('#c8b898'))
        if k >= 6: f.s(pts[-1][0], pts[-1][1] - 1, C('#c83a3a'))
    return f.im

def t_blut(t, mode):
    f = F(32, 44); floor(f, 12)
    f.ell(4, 22, 28, 36, BLOOD_D); f.ell(6, 23, 26, 34, BLOOD)
    rng = random.Random(t)
    if mode == 'idle':
        r = 3 + t * 2
        f.d.ellipse([16 - r, 28 - r*.45, 16 + r, 28 + r*.45], outline=BLOOD_L)
        return f.im
    h = [0, 2, 8, 16, 16, 10, 4, 0][t]
    if t in (1, 2):
        for k in range(4): f.disc(8 + k*5, 27 + (k % 2), 1.3, BLOOD_L)
    for i, (x, y) in enumerate(((10, 28), (16, 26), (22, 29), (13, 31), (19, 31))):
        hh = h * (1 if i < 3 else .6)
        if hh: f.poly([(x - 2, y), (x + 2, y), (x, y - hh)], BLOOD); f.line((x - 1, y - 1), (x, y - hh + 1), BLOOD_L)
    if t in (4, 5):
        for k in range(8): f.s(16 + rng.uniform(-12, 12), 10 + rng.uniform(0, 12), BLOOD)
    return f.im

def t_rune(t, mode):
    f = F(32, 44); floor(f, 12)
    cx, cy = 16, 28
    glow = [0, .2, .4, .6, .8, 1, .6, .2][t] if mode == 'ausloesen' else (.15 + .1 * math.sin(t / 4 * 2*math.pi))
    col = mix(C('#5a4a7a'), ARCANE[1], glow)
    f.d.ellipse([cx - 12, cy - 6, cx + 12, cy + 6], outline=col)
    f.d.ellipse([cx - 8, cy - 4, cx + 8, cy + 4], outline=mix(C('#4a3a6a'), ARCANE[2], glow))
    for i in range(6):
        lit = mode != 'ausloesen' or i <= t
        a = i / 6 * 2*math.pi
        f.s(cx + math.cos(a) * 10, cy + math.sin(a) * 5, ARCANE[0] if lit and glow > .3 else col)
    if mode == 'ausloesen' and t in (5, 6):
        w = 6 if t == 5 else 3
        for y in range(0, cy):
            for x in range(cx - w, cx + w + 1):
                d = abs(x - cx) / w
                if d < .4: f.s(x, y, ARCANE[0])
                elif d < .8: f.s(x, y, ARCANE[1])
                elif (x + y) % 2: f.s(x, y, ARCANE[2])
    if mode == 'ausloesen' and t >= 6:
        for i in range(8): a = i * .8 + t; f.s(cx + math.cos(a) * (t - 3) * 3, cy + math.sin(a) * (t - 3) * 1.5, ARCANE[1])
    return f.im

def t_baer(t, mode):
    f = F(32, 32); floor(f)
    cx, cy = 16, 18
    f.ell(cx - 3, cy - 2, cx + 3, cy + 2, STEEL_D)
    open_ = [1, .5, 0, 0][t] if mode == 'zuschnappen' else 1
    for s in (-1, 1):
        r = 9
        for k in range(15):
            a = math.pi * k / 14
            x = cx + math.cos(a) * r * s * (1 if open_ else 1)
            y = cy - math.sin(a) * r * (.35 + .65 * (1 - open_)) * (1 if s > 0 else -1) * (1 if open_ < 1 else .4) if False else None
        # vereinfachte Bügel
    if open_ > .5:
        for s in (-1, 1):
            f.d.arc([cx - 11, cy - 5 + s*3, cx + 11, cy + 5 + s*3], 0 if s > 0 else 180, 180 if s > 0 else 360, fill=STEEL)
            for k in range(6): f.s(cx - 8 + k * 3, cy + s * 4 - s * 2, STEEL_L)
    else:
        f.d.arc([cx - 9, cy - 8, cx + 9, cy + 4], 180, 360, fill=STEEL)
        f.d.arc([cx - 9, cy - 4, cx + 9, cy + 8], 0, 180, fill=STEEL_D)
        for k in range(6): f.poly([(cx - 8 + k*3, cy - 2), (cx - 6 + k*3, cy - 2), (cx - 7 + k*3, cy + 1)], STEEL_L)
        if t == 2:
            for p in ((cx - 12, cy - 6), (cx + 12, cy - 6), (cx, cy - 10)): f.s(*p, WHITE)
    f.line((cx, cy + 3), (cx + 10, cy + 10), C('#5a5e6e'))
    return f.im

def t_gatter(t, mode):
    f = F(32, 48); wall(f, 0, 48)
    f.rect(6, 6, 25, 47, C('#140e18')); f.rect(4, 4, 27, 6, STONE_D)
    drop = [0, 14, 30, 38, 38][t] if mode == 'fallen' else 0
    bottom = 6 + drop
    if drop:
        for x in range(8, 25, 4): f.rect(x, 6, x + 1, bottom, C('#5a5e6e'))
        for y in range(10, bottom, 8): f.rect(7, y, 24, y + 1, C('#4a4e5e'))
        for x in range(8, 25, 4): f.poly([(x - 1, bottom), (x + 2, bottom), (x + .5, bottom + 2)], STEEL)
    if mode == 'fallen' and t == 3:
        for k in range(8): f.disc(6 + k * 3, 46 - (k % 2), 1.5, C('#8a8098'))
    return f.im

def t_decke(t, mode):
    f = F(32, 64); floor(f, 32)
    f.rect(0, 0, 31, 5, STONE_D); f.rect(0, 5, 31, 5, MORTAR)
    rng = random.Random(5)
    if mode == 'warnung':
        for a, b in (((8, 5), (13, 9)), ((13, 9), (20, 6)), ((20, 6), (25, 10))): f.line(a, b, MORTAR)
        for i in range(3):
            y = 7 + ((t * 4 + i * 9) % 30); f.s(12 + i * 4, y, C('#a89a8a'))
        return f.im
    for a, b in (((8, 5), (13, 9)), ((13, 9), (20, 6)), ((20, 6), (25, 10))): f.line(a, b, MORTAR)
    rocks = [(10, 0, 4), (20, 1, 5), (15, 2, 3)]
    for x, delay, r in rocks:
        k = t - delay
        if k < 0: continue
        y = 8 + k * k * 4
        if y < 46:
            f.disc(x, y, r, C('#7a7280')); f.disc(x - 1, y - 1, r * .6, C('#8a8296')); f.s(x - 2, y - 2, C('#a8a0b4'))
        else:
            f.ell(x - r - 2, 44, x + r + 2, 49, C('#6a6276')); f.ell(x - r, 43, x + r, 47, C('#7a7280'))
            if k * k * 4 + 8 < 60:
                for i in range(6): f.disc(x + rng.uniform(-8, 8), 44 - rng.uniform(0, 6), 1.5, C('#a89a8a'))
    if t >= 5:
        for i in range(8): f.s(rng.uniform(2, 30), 10 + ((t * 3 + i * 5) % 30), C('#a89a8a'))
    return f.im

def t_flut(t, mode):
    f = F(32, 40); floor(f, 8)
    for gx in (8, 22):
        f.rect(gx - 4, 26, gx + 3, 31, C('#2a2430'))
        for k in range(4): f.rect(gx - 3 + k*2, 26, gx - 3 + k*2, 31, STEEL_D)
    level = {'fluten': min(1, t / 7), 'voll': 1}[mode]
    if mode == 'fluten' and t < 3:
        for gx in (8, 22):
            for i in range(3): f.s(gx - 2 + i * 2, 25 - ((t + i) % 3), C('#8ac4ee'))
    if level > 0:
        top = int(39 - level * 30)
        for y in range(top, 40):
            for x in range(32):
                wv = math.sin((x + t * 3) * .5) * (1 if y < top + 2 else 0)
                if y + wv >= top:
                    c = C('#e8f8ff') if y < top + 1 else C('#5ab0f0') if y < top + 6 else C('#3a80c8')
                    a = 210 if y > top + 1 else 255
                    f.s(x, y, c[:3] + (a,))
        for i in range(4): f.s((i * 9 + t * 2) % 32, top + 3 + i % 3, C('#e8f8ff'))
    return f.im

def t_mimikboden(t, mode):
    f = F(32, 40); floor(f, 8)
    if mode == 'atmen':
        if t in (1, 2): f.rect(8, 23, 23, 23, STONE_L); f.rect(9, 24, 22, 24, mix(STONE, C('#8a4a5a'), .25))
        return f.im
    o = [0, 1, 3, 6, 8, 3, 0, 0][t]
    cx, cy = 16, 24
    if t >= 1:
        f.line((6, cy), (26, cy), MORTAR)
    if o:
        f.ell(cx - 12, cy - o, cx + 12, cy + o, C('#5a1e2a'))
        f.ell(cx - 9, cy - o + 2, cx + 9, cy + o - 1, C('#2a0c14'))
        for k in range(7):
            x = cx - 10 + k * 3.3
            f.poly([(x - 1.2, cy - o + 1), (x + 1.2, cy - o + 1), (x, cy - o + 4)], C('#f4f0e0'))
            f.poly([(x - 1.2, cy + o - 1), (x + 1.2, cy + o - 1), (x, cy + o - 4)], C('#f4f0e0'))
        if o >= 6: f.ell(cx - 4, cy + 1, cx + 6, cy + 4, C('#c84a6a'))
        f.rect(cx - 13, cy - o - 1, cx + 13, cy - o - 1, STONE_L)
    if t == 5:
        for x, y in ((4, 16), (28, 16), (16, 10)): f.s(x, y, WHITE)
    if t >= 6:
        f.line((4, cy), (28, cy), MORTAR)
        for i in range(4): f.disc(6 + i * 7, cy - 6 - (t - 6) * 2, 1.4, C('#8a8098'))
    return f.im

TRAPS = [
    ('stachelfalle', 'Stachelfalle', t_stachel, [('idle', 1), ('ausloesen', 8)]),
    ('pfeilfalle', 'Pfeilfalle (Wand)', t_pfeil, [('idle', 1), ('ausloesen', 6)]),
    ('pfeil', 'Pfeil (Geschoss)', t_pfeil_flug, [('flug', 2)]),
    ('druckplatte', 'Druckplatte', t_druckplatte, [('idle', 1), ('ausloesen', 4)]),
    ('fallgrube', 'Fallgrube', t_fallgrube, [('oeffnen', 8), ('schliessen', 8)]),
    ('pendelklinge', 'Pendelklinge', t_pendel, [('schwingen', 8)]),
    ('feuerduese', 'Feuerdüse', t_feuer, [('bereit', 1), ('ausloesen', 8)]),
    ('giftgas', 'Giftgas', t_gift, [('stroemen', 8)]),
    ('felsbrocken', 'Rollender Felsbrocken', t_fels, [('rollen', 4)]),
    ('saegeblatt', 'Sägeblatt', t_saege, [('laufen', 8)]),
    ('baerenfalle', 'Bärenfalle', t_baer, [('offen', 1), ('zuschnappen', 4)]),
    ('fallgatter', 'Fallgatter', t_gatter, [('offen', 1), ('fallen', 5)]),
    ('dornenfalle', 'Dornenfalle (Dorn-Dungeon)', t_dornen, [('idle', 1), ('ausloesen', 8)]),
    ('blutfalle', 'Blutfalle (Blut-Dungeon)', t_blut, [('idle', 4), ('ausloesen', 8)]),
    ('runenfalle', 'Runenfalle (Erinnerungs-Dungeon)', t_rune, [('idle', 4), ('ausloesen', 8)]),
    ('einsturz', 'Einstürzende Decke', t_decke, [('warnung', 4), ('einsturz', 8)]),
    ('flutraum', 'Flutraum', t_flut, [('fluten', 8), ('voll', 4)]),
    ('mimikboden', 'Mimik-Boden', t_mimikboden, [('atmen', 4), ('zuschnappen', 8)]),
]

# ================================================================ TRUHEN
CHESTS = {
    'holz': dict(title='Holztruhe', body=WOOD, dark=WOOD_D, light=WOOD_L, band=C('#5a5e6e'), lock=C('#8a8e9e'), glow=GOLD),
    'eisen': dict(title='Eisentruhe', body=C('#6a6e80'), dark=C('#4a4e5e'), light=C('#8a8ea0'), band=C('#3a3e4a'), lock=GOLD, glow=GOLD),
    'gold': dict(title='Goldtruhe', body=C('#c89a3a'), dark=C('#8a6a2a'), light=C('#f0c860'), band=C('#5a3a8a'), lock=C('#e8e0ff'), glow=C('#fff4c8')),
    'dorn': dict(title='Dorntruhe', body=C('#2e2a2a'), dark=C('#1a1616'), light=C('#4a4040'), band=THORN, lock=C('#c83a3a'), glow=C('#ff5a5a'), thorns=True),
    'blut': dict(title='Bluttruhe', body=C('#6a1e2a'), dark=C('#3e1018'), light=C('#8a2e3a'), band=C('#2a1a1e'), lock=C('#e0b048'), glow=BLOOD_L, drip=True),
    'erinnerung': dict(title='Erinnerungstruhe', body=C('#5a6a9a'), dark=C('#3a4a7a'), light=C('#8aa0d0'), band=C('#c8d8ff'), lock=C('#ffffff'), glow=ARCANE[0], ghost=True),
}

def chest(kind, anim, t):
    k = CHESTS[kind]; f = F(32, 40, seed=t)
    oy = 8
    shake = (1 if t % 2 else -1) if anim == 'verschlossen' else 0
    x0, x1 = 5 + shake, 26 + shake
    f.ell(x0 - 1, oy + 27, x1 + 1, oy + 31, (20, 14, 30, 80))
    # Körper
    f.rect(x0, oy + 16, x1, oy + 28, k['body']); f.rect(x0, oy + 28, x1, oy + 28, k['dark'])
    for bx in (x0 + 3, x1 - 3): f.rect(bx - 1, oy + 16, bx, oy + 28, k['band'])
    if k.get('thorns'):
        for x in range(x0, x1, 4): f.poly([(x, oy + 28), (x + 2, oy + 28), (x + 1, oy + 31)], THORN_L)
    # Deckel
    ang = {'zu': 0, 'verschlossen': 0, 'oeffnen': [0, 1, 2, 3, 3, 3][t], 'offen': 3, 'leer': 3}[anim]
    glow = k['glow']
    if ang == 0:
        f.rect(x0, oy + 9, x1, oy + 16, k['light']); f.ell(x0, oy + 4, x1, oy + 14, k['light'])
        f.rect(x0, oy + 15, x1, oy + 16, k['dark'])
        for bx in (x0 + 3, x1 - 3): f.rect(bx - 1, oy + 6, bx, oy + 16, k['band'])
        f.rect(15 + shake, oy + 14, 17 + shake, oy + 19, k['lock']); f.s(16 + shake, oy + 17, k['dark'])
        if anim == 'verschlossen' and t in (1, 2):
            f.s(19 + shake, oy + 13, WHITE); f.s(13 + shake, oy + 13, WHITE)
    else:
        f.rect(x0 + 1, oy + 14, x1 - 1, oy + 17, C('#140e18'))
        if anim != 'leer':
            f.rect(x0 + 2, oy + 15, x1 - 2, oy + 17, glow)
            for i in range(6): f.s(x0 + 3 + i * 3, oy + 15 + (i % 2), GOLD_L if i % 2 else GOLD)
        if ang == 1:
            f.poly([(x0, oy + 14), (x1, oy + 14), (x1 + 1, oy + 7), (x0 - 1, oy + 7)], k['light'])
            f.rect(x0, oy + 12, x1, oy + 13, k['dark'])
        elif ang == 2:
            f.poly([(x0, oy + 14), (x1, oy + 14), (x1 - 1, oy + 2), (x0 + 1, oy + 2)], k['dark'])
            f.rect(x0 + 1, oy + 2, x1 - 1, oy + 4, k['light'])
        else:
            f.rect(x0 + 1, oy, x1 - 1, oy + 14, k['dark']); f.rect(x0 + 1, oy, x1 - 1, oy + 1, k['light'])
            for bx in (x0 + 3, x1 - 3): f.rect(bx - 1, oy, bx, oy + 14, k['band'])
    img = g.outline(f.im)
    p = img.load()
    def S(x, y, c):
        if 0 <= x < 32 and 0 <= y < 40: p[x, y] = c
    if anim == 'oeffnen' and t >= 2 or anim == 'offen':
        n = {2: 3, 3: 6, 4: 8, 5: 5}.get(t, 4) if anim == 'oeffnen' else 4
        for i in range(n):
            a = -math.pi/2 + (i - (n - 1) / 2) * .28
            L = (10 + (t % 3) * 3) if anim == 'oeffnen' else 6 + ((t + i) % 3) * 2
            for r_ in range(2, L):
                if (r_ + i) % 2 == 0: S(int(16 + math.cos(a) * r_), int(oy + 14 + math.sin(a) * r_), glow)
    if (anim == 'oeffnen' and t >= 3) or anim == 'offen':
        for i in range(5 if anim == 'oeffnen' else 3):
            S(8 + (i * 5 + t * 3) % 17, oy + 8 - ((t + i * 2) % 7), WHITE if i % 2 else GOLD_L)
    if anim == 'oeffnen' and t == 4:
        for x, y in ((11, oy + 6), (20, oy + 4), (14, oy + 2)):
            S(x, y, GOLD); S(x + 1, y, GOLD_L)
    if k.get('drip') and anim in ('zu', 'offen', 'leer', 'oeffnen'):
        y = oy + 29 + (t % 4)
        S(9, y, BLOOD); S(9, oy + 28, BLOOD)
    if k.get('ghost'):
        for y in range(40):
            for x in range(32):
                c = p[x, y]
                if c[3] == 255 and (x + y + t) % 5 == 0: p[x, y] = mix(c, ARCANE[1], .5)[:3] + (255,)
    return img

CHEST_ANIMS = [('zu', 1), ('verschlossen', 4), ('oeffnen', 6), ('offen', 4), ('leer', 1)]

# ================================================================ DETAILS
def d_tropfen(t, col, colL, colD, wall_=False):
    f = F(16, 40)
    f.rect(0, 0, 15, 3, STONE_D); f.rect(0, 3, 15, 3, MORTAR)
    f.ell(5, 2, 10, 5, colD)
    if wall_:
        for y in range(4, 4 + min(28, t * 4)): f.s(7 + (y // 6) % 2, y, col); f.s(8, y, colD if y % 3 else col)
    stage = t
    if stage < 3:
        r = 1 + stage * .6
        f.disc(7.5, 5 + stage, r, col); f.s(7, 4 + stage, colL)
    elif stage < 6:
        y = 8 + (stage - 3) ** 2 * 5
        f.ell(6.5, y - 2, 8.5, y + 1, col); f.s(7, y - 1, colL)
    elif stage == 6:
        f.ell(3, 35, 12, 38, col)
        for x, y in ((2, 32), (13, 33), (5, 31), (10, 31)): f.s(x, y, col)
    else:
        f.ell(4, 36, 11, 38, colD)
    if stage < 6: f.ell(4, 36, 11, 38, colD)
    return f.im

def d_blut_rinnt(t):
    f = F(16, 32); wall(f, 0, 32)
    L = min(30, 4 + t * 4)
    for y in range(0, L):
        x = 7 + int(math.sin(y * .4) * 1.2)
        f.s(x, y, BLOOD); f.s(x + 1, y, BLOOD_D)
        if y < L - 4 and y % 7 == 3: f.s(x - 1, y, BLOOD)
    f.ell(5, L - 1, 10, L + 2, BLOOD); f.s(7, L, BLOOD_L)
    return f.im

def d_blutlache(t):
    f = F(28, 14)
    f.ell(1, 2, 26, 12, BLOOD_D); f.ell(3, 3, 24, 11, BLOOD); f.ell(6, 4, 13, 6, mix(BLOOD, WHITE, .2))
    r = 2 + t * 2.5
    f.d.ellipse([15 - r, 7 - r*.4, 15 + r, 7 + r*.4], outline=BLOOD_L if t < 3 else BLOOD)
    return f.im

def d_kerzen(t):
    f = F(20, 20)
    for i, (x, h) in enumerate(((5, 8), (10, 12), (15, 6))):
        f.rect(x - 1, 19 - h, x + 1, 18, C('#f0e4cc')); f.s(x + 1, 19 - h + 1, C('#d8ccb4'))
        fl = (t + i) % 4
        f.s(x, 17 - h, FIRE[2]); f.s(x, 16 - h, FIRE[1] if fl % 2 else FIRE[0]);
        if fl in (1, 2): f.s(x + (1 if fl == 1 else -1), 15 - h, FIRE[2])
        if fl == 3: f.s(x, 15 - h, FIRE[1])
    f.ell(2, 17, 18, 19, C('#e8dcc4'))
    return g.outline(f.im)

def d_kette(t):
    f = F(20, 40)
    f.rect(6, 0, 13, 2, STONE_D)
    a = math.sin(t / 6 * 2*math.pi) * .25
    for k in range(9):
        x = 10 + math.sin(a) * k * 4; y = 3 + math.cos(a) * k * 4
        if k % 2: f.d.ellipse([x - 1, y - 2, x + 1, y + 2], outline=C('#7a7e8e'))
        else: f.d.ellipse([x - 2, y - 1, x + 2, y + 1], outline=C('#9a9eae'))
    x, y = 10 + math.sin(a) * 36, 3 + math.cos(a) * 36
    f.d.arc([x - 3, y - 3, x + 3, y + 3], 0, 300, fill=C('#9a9eae'))
    return g.outline(f.im)

def d_spinnweben(t):
    f = F(20, 20); col = (230, 230, 240, 200)
    sway = math.sin(t / 4 * 2*math.pi) * .8
    for k in range(5):
        a = k / 4 * math.pi / 2
        f.line((0, 0), (math.cos(a) * 18 + sway * (k / 4), math.sin(a) * 18), col)
    for r_ in (5, 9, 13, 17):
        pts = [(math.cos(k / 8 * math.pi / 2) * r_ + sway * k / 8, math.sin(k / 8 * math.pi / 2) * r_) for k in range(9)]
        for a_, b_ in zip(pts, pts[1:]): f.line(a_, b_, col)
    return f.im

def d_fliegen(t):
    f = F(24, 24)
    bone, bone_d = C('#e8e0d0'), C('#b8ac98')
    def bone_(x0, y0, x1, y1):
        f.line((x0, y0), (x1, y1), bone, 2)
        for x, y in ((x0, y0), (x1, y1)): f.disc(x, y, 1.6, bone); f.s(x, y + 1, bone_d)
    bone_(3, 21, 12, 19); bone_(11, 22, 20, 20); bone_(6, 18, 16, 21); bone_(14, 17, 21, 18)
    f.ell(7, 11, 15, 18, bone); f.rect(9, 16, 13, 19, bone)
    f.ell(8, 13, 10, 15, C('#2b1e33')); f.ell(12, 13, 14, 15, C('#2b1e33')); f.s(11, 16, C('#2b1e33'))
    for x in (10, 12): f.s(x, 18, bone_d)
    img = g.outline(f.im); p = img.load()
    for i in range(4):
        a = i * 1.6 + t * 1.3
        x, y = int(12 + math.cos(a) * 8), int(7 + math.sin(a * 1.3) * 4)
        if 0 <= x < 24 and 0 <= y < 24: p[x, y] = (30, 26, 34, 255)
        if 0 <= x < 24 and 0 <= y - 1 < 24 and (t + i) % 2: p[x, y - 1] = (200, 210, 230, 255)
    return img

def d_blutmond_strahl(t):
    f = F(48, 64)
    wall(f, 0, 20)
    f.ell(16, 3, 31, 17, C('#140e18'))
    pulse = .5 + .5 * math.sin(t / 8 * 2*math.pi)
    moon = mix(C('#a8283a'), C('#ff5a5a'), pulse)
    f.disc(26, 9, 4, moon); f.disc(25, 8, 2, mix(moon, WHITE, .3))
    for k in range(3): f.line((16 + k * 7, 4), (16 + k * 7, 16), C('#3a3446'), 2)
    for y in range(17, 64):
        k = (y - 17) / 47
        x0, x1 = 17 - k * 10, 30 + k * 14
        for x in range(int(x0), int(x1) + 1):
            if (x + y + t) % 3 == 0 or ((x + y) % 2 == 0 and k < .3):
                f.s(x, y, (255, 70, 80, int(60 + 70 * pulse * (1 - k))))
    for i in range(5):
        y = 20 + ((t * 3 + i * 9) % 44); x = 20 + i * 5 + math.sin(t + i) * 2
        f.s(x, y, (255, 160, 160, 200))
    return f.im

def d_blutmond_schimmer(t):
    f = F(64, 64)
    pulse = .5 + .5 * math.sin(t / 8 * 2*math.pi)
    for y in range(64):
        for x in range(64):
            d = math.hypot(x - 31.5, y - 31.5) / 45
            if d > .45 and (x + y) % 2 == 0:
                f.s(x, y, (180, 20, 40, int(min(1, (d - .45) * 2.2) * (70 + 60 * pulse))))
    return f.im

def d_pilze(t):
    f = F(20, 20)
    gl = .5 + .5 * math.sin(t / 6 * 2*math.pi)
    col = mix(C('#3a8ab8'), C('#9af0ff'), gl)
    for x, h, r in ((5, 7, 3), (11, 10, 4), (16, 5, 2.5)):
        f.rect(x - 1, 19 - h, x, 18, C('#d8d0e0'))
        f.ell(x - r - .5, 19 - h - r, x + r - .5, 19 - h + 1, col)
        f.s(x - 1, 19 - h - r + 1, mix(col, WHITE, .5))
    img = g.outline(f.im); p = img.load()
    for i in range(3):
        x, y = 3 + i * 6 + (t % 2), 6 - ((t + i * 2) % 6)
        if 0 <= y < 20: p[x, y] = mix(col, WHITE, .4)
    return img

def d_kristall(t):
    f = F(20, 28)
    gl = .5 + .5 * math.sin(t / 6 * 2*math.pi)
    base = mix(C('#5a3aa8'), C('#c8a8ff'), gl)
    f.poly([(10, 2), (15, 10), (13, 25), (7, 25), (5, 10)], base)
    f.poly([(10, 2), (10, 25), (7, 25), (5, 10)], mix(base, WHITE, .25))
    f.poly([(3, 16), (6, 14), (7, 25), (3, 25)], shade(base, .8)); f.poly([(16, 15), (18, 18), (17, 25), (13, 25)], shade(base, .85))
    f.line((8, 6), (7, 14), WHITE)
    img = g.outline(f.im); p = img.load()
    for i in range(4):
        a = i * 1.57 + t * .6; x, y = int(10 + math.cos(a) * 9), int(14 + math.sin(a) * 9)
        if 0 <= x < 20 and 0 <= y < 28 and gl > .3: p[x, y] = ARCANE[0]
    return img

def d_glut(t):
    f = F(20, 14)
    f.ell(1, 6, 18, 13, C('#3a3438'))
    rng = random.Random(1)
    for i in range(14):
        x, y = rng.randint(4, 15), rng.randint(8, 11)
        f.s(x, y, FIRE[(i + t) % 4] if (i + t) % 3 else C('#5a3a3a'))
    for i in range(2):
        y = 6 - ((t * 2 + i * 3) % 7)
        f.s(7 + i * 5 + (t % 2), y, FIRE[1])
    return f.im

def d_staub(t):
    f = F(32, 32)
    rng = random.Random(4)
    for i in range(12):
        x0, y0 = rng.uniform(0, 32), rng.uniform(0, 32)
        x = (x0 + t * .8 + math.sin(t * .4 + i) * 2) % 32; y = (y0 - t * .5) % 32
        f.s(x, y, (230, 220, 200, 150 if i % 2 else 90))
    return f.im

def d_nebel(t):
    f = F(48, 16)
    for i in range(7):
        x = (i * 9 + t * 2) % 56 - 4
        r = 5 + (i % 3)
        for y in range(16):
            for xx in range(int(x - r), int(x + r)):
                d = ((xx - x) / r) ** 2 + ((y - 11) / (r * .5)) ** 2
                if d <= 1 and 0 <= xx < 48 and (xx + y) % 2 == 0: f.s(xx, y, (220, 216, 236, 110))
    return f.im

def d_lava(t):
    f = F(28, 14)
    f.ell(1, 2, 26, 12, FIRE[3]); f.ell(3, 3, 24, 11, FIRE[2])
    for i in range(3):
        p = ((t + i * 2) % 6) / 6; x = 7 + i * 7
        if p < .7: f.disc(x, 7, 1 + p * 3, FIRE[1]); f.s(x - 1, 6, FIRE[0])
        else: f.s(x, 4, FIRE[1]); f.s(x + 2, 3, FIRE[2])
    return f.im

def ghostify(src, t, dark, light, glitch=1, seed=0, tears=None, eye=None, mouth=None):
    """Macht aus einer Figur ein Geisterbild: Palette, heller Rand, Rauchschweif, Schweben, Bildstörung."""
    W, H = 30, 34
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = out.load(); sp = src.load()
    bob = round(math.sin(t / 8 * 2*math.pi) * 1.2)
    rng = random.Random(seed * 100 + t)
    band = None
    if glitch and t in (2, 5, 6):
        y0 = rng.randint(6, 20); band = (y0, y0 + rng.randint(2, 4), rng.choice((-2, -1, 2)) * glitch)
    sw, sh = src.size
    top = next((y for y in range(sh) if any(sp[x, y][3] for x in range(sw))), 0)
    bot = max((y for y in range(sh) if any(sp[x, y][3] for x in range(sw))), default=sh - 1)
    for y in range(sh):
        k = (y - top) / max(1, bot - top)
        shift = 0
        if band and band[0] <= y <= band[1]: shift = band[2]
        if k > .68: shift += round(math.sin(y * .7 + t * .9) * (k - .68) * 6)
        for x in range(sw):
            c = sp[x, y]
            if not c[3]: continue
            if k > .72 and rng.random() < (k - .72) * 2.6: continue
            inner = all(0 <= x + dx < sw and 0 <= y + dy < sh and sp[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if c[:3] == g.OUTLINE[:3] and inner and 6 <= y - top <= 14: col = eye or dark; a = 255
            elif c[:3] == g.OUTLINE[:3]: col = light; a = 235
            elif c[:3] in ((224, 228, 238), (236, 238, 244)): col = WHITE; a = 255
            else:
                v = (c[0] * .3 + c[1] * .55 + c[2] * .15) / 255
                col = mix(dark, light, max(0, min(1, -.15 + v * 1.35))); a = 195
            if band and band[0] <= y <= band[1] and (x + t) % 3 == 0: col = WHITE
            if (y + t) % 7 == 0: a -= 45
            X, Y = x + (W - sw) // 2 + shift, y + bob + 3
            if 0 <= X < W and 0 <= Y < H: p[X, Y] = col[:3] + (max(40, a),)
    if mouth:
        for (mx, my) in mouth:
            X, Y = mx + (W - sw) // 2, my + bob + 3
            if 0 <= X < W and 0 <= Y < H: p[X, Y] = C('#140810')[:3] + (240,)
    if tears:
        for (tx, ty) in tears:
            for k in range(1 + (t % 4)):
                X, Y = tx + (W - sw) // 2, ty + bob + 3 + k
                if 0 <= X < W and 0 <= Y < H: p[X, Y] = C('#d8283a')[:3] + (230,)
    for i in range(3):
        y = H - 4 - ((t * 2 + i * 5) % 14); x = W // 2 - 6 + i * 6 + math.sin(t + i) * 2
        if 0 <= y < H: p[int(x), int(y)] = light[:3] + (150,)
    return out

_GHOST_CACHE = {}
def _ghost_src(kind, t):
    import combat as cb, races as rc
    if kind == 'mensch':
        if 'm' not in _GHOST_CACHE: _GHOST_CACHE['m'], _ = cb.compose(rc.RACES[0], 'tunika', 'front', arm='unten', blink=False)
        return _GHOST_CACHE['m']
    if kind == 'schrei':
        if 's' not in _GHOST_CACHE: _GHOST_CACHE['s'], _ = cb.compose(rc.RACES[2], 'tunika', 'front', arm='hoch_b', blink=True)
        return _GHOST_CACHE['s']
    if kind == 'schrei2':
        if 's2' not in _GHOST_CACHE:
            fox = next(r for r in rc.RACES if r['name'] == 'fuchs')
            _GHOST_CACHE['s2'], _ = cb.compose(fox, 'tunika', 'front', arm='hoch_b', blink=True)
        return _GHOST_CACHE['s2']
    if kind == 'krieger':
        if 'k' not in _GHOST_CACHE:
            _GHOST_CACHE['k'] = cb.anim_frames(rc.RACES[1], 'ruestung', 'angriff', 'side')
        seq = [0, 0, 1, 2, 3, 4, 4, 4]
        return _GHOST_CACHE['k'][seq[t]]

def d_geist(t):
    return ghostify(_ghost_src('mensch', t), t, C('#2a3a7a'), C('#c8e0ff'), glitch=1, seed=1, eye=C('#ffffff'))

def d_geist_schrei(t):
    src = _ghost_src('schrei', t)
    return ghostify(src, t, C('#5a1428'), C('#ffc8d0'), glitch=2, seed=2, tears=[(7, 11), (10, 11)], eye=C('#140810'),
                    mouth=[(8, 12), (9, 12), (8, 13), (9, 13)])

def d_geist_schrei2(t):
    return ghostify(_ghost_src('schrei2', t), t, C('#5a1428'), C('#ffc8d0'), glitch=2, seed=4, tears=[(7, 11), (10, 11)],
                    eye=C('#140810'), mouth=[(8, 13), (9, 13), (8, 14), (9, 14)])

def d_geist_krieger(t):
    return ghostify(_ghost_src('krieger', t), t, C('#1e4a3a'), C('#d8ffe8'), glitch=1, seed=3, eye=C('#ffffff'))

def d_kaefig(t):
    f = F(20, 40)
    a = math.sin(t / 6 * 2*math.pi) * .12
    f.line((10, 0), (10 + math.sin(a) * 10, 10), C('#7a7e8e'))
    cx = 10 + math.sin(a) * 14
    f.d.arc([cx - 7, 8, cx + 7, 18], 180, 360, fill=C('#6a6e7e'))
    for k in range(5): f.line((cx - 6 + k * 3, 13), (cx - 6 + k * 3 + math.sin(a) * 2, 34), C('#6a6e7e'))
    f.line((cx - 7, 34), (cx + 7, 34), C('#5a5e6e'), 2)
    for x, y in ((cx - 2, 31), (cx + 1, 32), (cx, 29)): f.s(x, y, C('#e8e0d0'))
    return g.outline(f.im)

def d_schaedel(t):
    f = F(16, 16)
    f.ell(2, 2, 13, 12, C('#e8e0d0')); f.rect(5, 10, 10, 14, C('#e8e0d0'))
    for x in (6, 8): f.line((x, 12), (x, 14), C('#a89a8a'))
    on = t not in (4,)
    ec = C('#ff3a3a') if on else C('#2b1e33')
    f.ell(4, 6, 7, 9, C('#2b1e33')); f.ell(9, 6, 12, 9, C('#2b1e33'))
    if on: f.s(5, 7, ec); f.s(10, 7, ec); f.s(6, 8, shade(ec, .7)); f.s(11, 8, shade(ec, .7))
    img = g.outline(f.im)
    if on and t in (1, 2):
        p = img.load()
        for x, y in ((4, 5), (12, 5)):
            p[x, y] = (255, 90, 90, 160)
    return img

DETAILS = [
    ('blut_tropfen', 'Tropfendes Blut', lambda t: d_tropfen(t, BLOOD, BLOOD_L, BLOOD_D), 8),
    ('wasser_tropfen', 'Tropfendes Wasser', lambda t: d_tropfen(t, C('#5ab0f0'), C('#e8f8ff'), C('#2a6ab8')), 8),
    ('blut_rinnt', 'Blut rinnt die Wand herab', d_blut_rinnt, 8),
    ('blutlache', 'Blutlache', d_blutlache, 4),
    ('kerzen', 'Kerzen', d_kerzen, 4),
    ('kette', 'Hängende Kette', d_kette, 6),
    ('kaefig', 'Hängender Käfig', d_kaefig, 6),
    ('spinnweben', 'Spinnweben', d_spinnweben, 4),
    ('fliegen', 'Fliegen über Knochen', d_fliegen, 4),
    ('pilze', 'Leuchtpilze', d_pilze, 6),
    ('mana_kristall', 'Mana-Kristall', d_kristall, 6),
    ('glut', 'Glut', d_glut, 4),
    ('staub', 'Schwebender Staub', d_staub, 8),
    ('bodennebel', 'Bodennebel', d_nebel, 8),
    ('lavablasen', 'Lava-Blasen', d_lava, 6),
    ('schaedel_augen', 'Schädel mit glühenden Augen', d_schaedel, 6),
    ('geisterbild', 'Geisterbild: Erinnerung', d_geist, 8),
    ('geisterbild_schrei', 'Geisterbild: schreiendes Opfer', d_geist_schrei, 8),
    ('geisterbild_schrei_2', 'Geisterbild: schreiendes Opfer 2 (Fuchs)', d_geist_schrei2, 8),
    ('geisterbild_krieger', 'Geisterbild: Krieger in der Schleife', d_geist_krieger, 8),
    ('blutmond_lichtstrahl', 'Blutmond-Licht (Fenster)', d_blutmond_strahl, 8),
    ('blutmond_schimmer', 'Blutmond-Schimmer (Overlay)', d_blutmond_schimmer, 8),
]

# ================================================================ Export
def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(f, (i * w, 0))
    return s

def preview(items, path, S=3, cols=5, n_frames=8, title=''):
    """items: [(titel, [frames])] -> GIF"""
    cw = max(f[0].width for _, f in items) * S + 16; ch = max(f[0].height for _, f in items) * S + 26
    rows = (len(items) + cols - 1) // cols
    out = []
    for t in range(n_frames):
        im = Image.new('RGB', (cols * cw, rows * ch + 30), (30, 26, 42)); d = ImageDraw.Draw(im)
        d.text((8, 6), title, fill=(255, 240, 200), font=g.font(15))
        for i, (name, fr) in enumerate(items):
            x, y = (i % cols) * cw, 30 + (i // cols) * ch
            d.rectangle([x + 3, y + 16, x + cw - 4, y + ch - 3], fill=(46, 40, 58))
            f = fr[t % len(fr)]; big = f.resize((f.width * S, f.height * S), Image.NEAREST)
            im.paste(big, (x + (cw - big.width) // 2, y + ch - 5 - big.height), big)
            d.text((x + 5, y + 2), name, fill=(235, 225, 205), font=g.font(11))
        out.append(im)
    out[0].save(path, save_all=True, append_images=out[1:], duration=130, loop=0)

def main():
    meta = {'fallen': {}, 'truhen': {}, 'details': {}}
    for sub in ('fallen', 'truhen', 'details'): os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    trap_prev = []
    for key, title, fn, anims in TRAPS:
        meta['fallen'][key] = {'titel': title, 'animationen': {}}
        seq = []
        for anim, n in anims:
            fr = [fn(t, anim) for t in range(n)]
            strip(fr).save(os.path.join(OUT, 'fallen', f'{key}_{anim}.png'))
            meta['fallen'][key]['animationen'][anim] = {'bilder': n, 'bild': list(fr[0].size)}
            seq += fr if n > 1 else fr * 2
        trap_prev.append((title, seq))
    chest_prev = []
    for kind, k in CHESTS.items():
        meta['truhen'][kind] = {'titel': k['title'], 'animationen': {}}
        seq = []
        for anim, n in CHEST_ANIMS:
            fr = [chest(kind, anim, t) for t in range(n)]
            strip(fr).save(os.path.join(OUT, 'truhen', f'{kind}_{anim}.png'))
            meta['truhen'][kind]['animationen'][anim] = {'bilder': n, 'bild': list(fr[0].size)}
            seq += fr if n > 1 else fr * 3
        chest_prev.append((k['title'], seq))
    det_prev = []
    for key, title, fn, n in DETAILS:
        fr = [fn(t) for t in range(n)]
        strip(fr).save(os.path.join(OUT, 'details', f'{key}.png'))
        meta['details'][key] = {'titel': title, 'bilder': n, 'bild': list(fr[0].size), 'schleife': True}
        det_prev.append((title, fr))
    meta['hinweis'] = ('Alle Bilder liegen nebeneinander. Fallen: idle/bereit/offen = Ruhezustand, ausloesen/zuschnappen/fallen = einmal '
                       'abspielen, schwingen/rollen/laufen/stroemen = Schleife. Truhen: zu -> oeffnen -> offen (Schleife) -> leer; '
                       'verschlossen = Rütteln bei verschlossener Truhe. Empfohlen: 100-130 ms pro Bild.')
    json.dump(meta, open(os.path.join(OUT, 'dungeon.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(trap_prev, os.path.join(g.BASE, 'preview_fallen.gif'), S=3, cols=5, n_frames=18, title='Dungeon-Fallen')
    preview(chest_prev, os.path.join(g.BASE, 'preview_truhen.gif'), S=4, cols=6, n_frames=18, title='Truhen: zu · rütteln · öffnen · offen · leer')
    preview(det_prev, os.path.join(g.BASE, 'preview_details.gif'), S=4, cols=6, n_frames=24, title='Dungeon-Details')

if __name__ == '__main__':
    main()
