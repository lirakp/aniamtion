"""Effekt-Animationen für alle 270 Zauber + 9 Element-Grundzauber.
Aufruf: python3 spells.py
Ausgabe: zauber/sprites/<kapitel>/<zauber>.png   (10 Bilder nebeneinander)
         zauber/sprites/grund/<element>_<teil>.png  (entstehen 4, flug 4, einschlag 6)
         zauber/sprites/zauber.json, zauber/preview_<kapitel>.gif, zauber/preview_grundzauber.gif
"""
import os, sys, math, random, json, re, unicodedata
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from formen import lade

def C(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
def mix(a, b, t): return tuple(int(a[i]*(1-t) + b[i]*t) for i in range(3)) + (255,)
def shade(c, f): return tuple(max(0, min(255, int(v*f))) for v in c[:3]) + (255,)
WHITE, OUTL = (255, 255, 255, 255), C('#2b1e33')
ELEM = {
    'feuer': [C('#ffe9a0'), C('#ff9a3c'), C('#d8452e')], 'eis': [C('#ffffff'), C('#a8e0ff'), C('#5a9ad8')],
    'wasser': [C('#e8f8ff'), C('#5ab0f0'), C('#2a6ab8')], 'erde': [C('#e0c898'), C('#a8804e'), C('#6a4a30')],
    'dendro': [C('#e0f8a0'), C('#7ac84a'), C('#3a7a3a')], 'wind': [C('#ffffff'), C('#d8f0e8'), C('#9ac8c0')],
    'elektro': [C('#ffffff'), C('#fff07a'), C('#b880ff')], 'schatten': [C('#b8a0e8'), C('#6a4aa8'), C('#2a1e48')],
    'licht': [C('#ffffff'), C('#fff4c8'), C('#ffd27a')],
}
OPP = {'feuer': 'eis', 'eis': 'feuer', 'licht': 'schatten', 'schatten': 'licht', 'erde': 'wind', 'wind': 'erde',
       'wasser': 'elektro', 'elektro': 'wasser'}
N = 10
SIZES = {'Zweiklang': (64, 48), 'Dreiklang': (80, 56), 'Vierklang': (96, 64)}

class F:
    """Ein Bild + Zeichenhilfen in Pixeln."""
    def __init__(self, W, H, P, rng):
        self.im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); self.px = self.im.load(); self.d = ImageDraw.Draw(self.im)
        self.W, self.H, self.P, self.rng = W, H, P, rng
        self.gy = H - 5; self.sc = W / 64
    def c(self, i, s): return self.P[i % len(self.P)][s]
    def s(self, x, y, col):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.W and 0 <= y < self.H: self.px[x, y] = col
    def disc(self, cx, cy, r, col):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if (x + .5 - cx)**2 + (y + .5 - cy)**2 <= r*r: self.s(x, y, col)
    def ell(self, cx, cy, rx, ry, col, fill=True):
        if rx < .5 or ry < .5: self.s(cx, cy, col); return
        if fill: self.d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
        else: self.d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col)
    def ring(self, cx, cy, rx, ry, col, dots=1):
        n = max(8, int((rx + ry) * 2))
        for i in range(n):
            if i % dots: continue
            a = i / n * 2*math.pi; self.s(cx + math.cos(a)*rx, cy + math.sin(a)*ry, col)
    def line(self, a, b, col, w=1): self.d.line([a, b], fill=col, width=w)
    def poly(self, pts, col): self.d.polygon(pts, fill=col)
    def bolt(self, x0, y0, x1, y1, col, core=None, segs=6, jit=3):
        pts = [(x0, y0)]
        for i in range(1, segs):
            t = i / segs
            pts.append((x0 + (x1 - x0)*t + self.rng.uniform(-jit, jit) * .5, y0 + (y1 - y0)*t + self.rng.uniform(-jit, jit)))
        pts.append((x1, y1))
        for a, b in zip(pts, pts[1:]): self.line(a, b, col, 2 if self.sc > 1.2 else 1)
        if core:
            for a, b in zip(pts, pts[1:]): self.line(a, b, core)
    def sparks(self, cx, cy, r, n, k=0, rise=0.0):
        for i in range(n):
            a = self.rng.random() * 2*math.pi; rr = self.rng.random() * r
            self.s(cx + math.cos(a)*rr, cy + math.sin(a)*rr*.7 - rise, self.c(i, i % 3))
    def cloud(self, cx, cy, r):
        tint = self.P[-1][1]
        cols = [mix(C('#d8d4e2'), tint, .25), mix(C('#8a8498'), tint, .25), mix(C('#4a4458'), tint, .3)]
        self.disc(cx, cy, r, cols[2]); self.disc(cx - r*.2, cy - r*.25, r*.8, cols[1]); self.disc(cx - r*.35, cy - r*.45, r*.4, cols[0])
    def puff(self, cx, cy, r, i=0):
        self.disc(cx, cy, r, self.c(i, 2)); self.disc(cx - r*.25, cy - r*.25, r*.75, self.c(i, 1)); self.disc(cx - r*.4, cy - r*.45, r*.35, self.c(i, 0))

def env(t, a=2, b=7):
    """0..1 an- und abschwellend über 10 Bilder"""
    if t < a: return (t + 1) / (a + 1)
    if t > b: return max(0, 1 - (t - b) / (N - b))
    return 1.0

# ================================================================ Formen
def f_geschoss(f, t, var):
    y = f.H * .55; x0, x1 = 10 * f.sc, f.W - 12 * f.sc
    if t <= 1:
        f.sparks(x0, y, 8 * f.sc * (1 - t*.4), 10); proj(f, x0, y, var, .4 + t*.3, t)
    elif t <= 6:
        k = (t - 1) / 5; x = x0 + (x1 - x0) * k
        for j in range(1, 5): f.s(x - j*3*f.sc, y + math.sin(t + j)*1.5, f.c(1, j % 3))
        proj(f, x, y, var, 1.0, t)
    else:
        k = (t - 6) / 3; r = (4 + 10*k) * f.sc
        if t == 7: f.disc(x1, y, 5*f.sc, f.c(0, 0))
        f.ring(x1, y, r, r*.8, f.c(0, 1 if t < 9 else 2), dots=1 if t < 9 else 2)
        f.sparks(x1, y, r, 12, rise=k*4)
        if var == 'samen':
            for i in range(6): a = i/6*6.28; f.s(x1 + math.cos(a)*r*.6, y + math.sin(a)*r*.6, f.c(i, 1))
        if var == 'kugel': f.ring(x1, y, r*1.3, r, f.c(1, 0), dots=2)

def proj(f, x, y, var, s, t):
    s *= f.sc
    if var in ('', 'orb', 'flamme', 'wisp', 'kugel'):
        r = (4.5 if var == 'kugel' else 3.5) * s
        if var == 'flamme':
            for j in range(4): f.disc(x - j*2*s, y + math.sin(t + j)*.6, r - j*.7*s, f.c(0, min(2, j)))
        f.disc(x, y, r, f.c(0, 2)); f.disc(x - r*.15, y - r*.15, r*.7, f.c(0, 1)); f.disc(x - r*.3, y - r*.3, r*.35, f.c(0, 0))
        if var == 'kugel':
            for j in range(4): a = j*1.57 + t; f.s(x + math.cos(a)*r*1.4, y + math.sin(a)*r*1.4, f.c(1, 0))
        if var == 'wisp':
            for j in range(6): a = j + t; f.s(x - j*2*s, y + math.sin(a)*3*s, f.c(0, 1))
    elif var in ('lanze', 'pfeil'):
        L = (14 if var == 'lanze' else 10) * s
        f.poly([(x + 4*s, y), (x - L*.3, y - 2*s), (x - L, y), (x - L*.3, y + 2*s)], f.c(0, 1))
        f.line((x - L, y), (x + 3*s, y), f.c(0, 0))
        if var == 'pfeil': f.line((x - L, y - 2*s), (x - L - 2*s, y), f.c(1, 1)); f.line((x - L, y + 2*s), (x - L - 2*s, y), f.c(1, 1))
    elif var in ('faust', 'stein'):
        r = 4 * s
        f.poly([(x - r, y - r*.6), (x + r*.6, y - r), (x + r, y + r*.2), (x + r*.2, y + r), (x - r*.8, y + r*.7)], f.c(0, 2))
        f.disc(x, y - r*.2, r*.55, f.c(0, 1))
        for j in range(3): f.s(x - r*.3 + j*r*.4, y + r*.3, f.c(1, 0))
        if var == 'faust':
            for j in range(3): f.disc(x + r*.8, y - r*.6 + j*r*.6, r*.3, f.c(0, 1))
    elif var in ('dorn', 'nadeln'):
        for j in (-1, 0, 1) if var == 'nadeln' else (0,):
            yy = y + j*3*s
            f.poly([(x + 3*s, yy), (x - 6*s, yy - 1.3*s), (x - 6*s, yy + 1.3*s)], f.c(0, 1)); f.s(x + 2*s, yy, f.c(0, 0))
    elif var == 'samen':
        f.ell(x, y, 3.5*s, 2.5*s, f.c(0, 1)); f.line((x - 3*s, y), (x + 3*s, y), f.c(1, 2)); f.s(x + 3*s, y - 2*s, f.c(1, 0))
    elif var == 'klinge':
        for j in range(12):
            a = -1.2 + j * .2; f.s(x + math.cos(a)*5*s, y + math.sin(a)*5*s, f.c(0, j % 2))
            f.s(x + math.cos(a)*4*s, y + math.sin(a)*4*s, f.c(1, 1))

def f_strahl(f, t, var):
    y = f.H * .55; x0 = 8 * f.sc
    L = (f.W - 6*f.sc - x0) * min(1, (t + 1) / 3)
    th = (3.5 + math.sin(t * 1.7)) * f.sc * env(t)
    for x in range(int(x0), int(x0 + L)):
        wv = math.sin((x + t*5) * .35) * .8
        for dy in range(-int(th) - 1, int(th) + 2):
            d = abs(dy - wv) / max(1, th)
            if d < .35: f.s(x, y + dy, f.c(0, 0))
            elif d < .75: f.s(x, y + dy, f.c(0, 1))
            elif d < 1.05 and (x + dy + t) % 2 == 0: f.s(x, y + dy, f.c(1, 1))
    if var == 'dampf':
        for i in range(6): f.puff(x0 + L*(i + .5)/6, y - th - 2 - ((t + i) % 4), 2*f.sc, 0)
    if var == 'lanze' and t >= 2:
        f.disc(x0 + L, y, 4*f.sc, f.c(0, 0))
    f.disc(x0, y, 3*f.sc*env(t), f.c(0, 0))

def f_kegel(f, t, var):
    y = f.H * .5; x0 = 8 * f.sc; L = (f.W - 10*f.sc) * min(1, (t + 1) / 4) * (1 if t < 8 else 1 - (t - 7) * .25)
    for i in range(int(90 * f.sc * env(t))):
        d = f.rng.random() * L; spread = d * .45
        yy = y + f.rng.uniform(-spread, spread)
        col = f.c(0, 0) if d < L*.25 else f.c(i, 1) if d < L*.65 else f.c(i, 2)
        f.s(x0 + d, yy, col)
        if f.sc > 1.2: f.s(x0 + d + 1, yy, col)

def f_welle(f, t, var):
    x = 30*f.sc + (f.W - 32*f.sc) * t / (N - 1)
    h = f.H * (.75 if var in ('gross', 'lawine') else .55) * env(t, 1, 8)
    WL = 28*f.sc
    for xx in range(int(x - WL), int(x)):
        k = max(0.0, (xx - (x - WL)) / WL)
        top = f.gy - h * (k ** 1.4 if k < .92 else (1 - (k - .92) / .08 * .5)) + math.sin(xx*.6 + t)*.8
        for yy in range(int(top), f.gy + 1):
            col = f.c(0, 0) if yy < top + 2 else f.c(0, 1) if (yy - top) < h*.45 else f.c(0, 2)
            if k > .9 and yy < top + 4: col = WHITE
            if var == 'hitze': col = f.c(0, 1) if (xx + yy + t) % 3 == 0 else (0, 0, 0, 0) if (xx + yy) % 2 else f.c(0, 2)
            if col[3]: f.s(xx, yy, col)
    for i in range(6): f.s(x + f.rng.uniform(-2, 3), f.gy - h*f.rng.random(), f.c(1, 0))
    if var == 'blitz' and t % 2 == 0: f.bolt(x - 10*f.sc, f.gy - h*.8, x, f.gy - h*.2, f.c(1, 1), f.c(1, 0), 4)
    if var == 'gefriert' and t >= 6:
            for xx in range(int(x - 28*f.sc), int(x), 3): f.line((xx, f.gy), (xx + 1, f.gy - h*.5), f.c(1, 0))
    if var == 'wind':
        for i in range(5): yy = f.gy - h*(i + 1)/6; f.line((x - 28*f.sc, yy), (x - 4*f.sc, yy), f.c(0, i % 2))

def f_ring(f, t, var):
    cx, cy = f.W/2, f.gy - 2
    for k in range(3):
        r = (t - k*2) * f.W / 22
        if r <= 0: continue
        col = f.c(k, 0 if k == 0 else 1)
        if var in ('stille', 'sog'): r = f.W/2.2 - r * .8
        if r > 0: f.ring(cx, cy, r, r*.35, col, dots=1 if var != 'stille' else 2)
        if var == 'druck' and r > 0: f.ring(cx, cy - r*.3, r*.8, r*.5, f.c(k, 1), dots=2)
    if var == 'sog':
        for i in range(10): a = i/10*6.28 + t*.5; rr = (10 - t) * f.sc * 2; f.s(cx + math.cos(a)*rr, cy - 8*f.sc + math.sin(a)*rr*.4, f.c(i, 1))
        f.disc(cx, cy - 8*f.sc, 2*f.sc, f.c(0, 2))
    if var == 'bann':
        for i in range(8): a = i/8*6.28; f.line((cx, cy - 10*f.sc), (cx + math.cos(a)*14*f.sc*env(t), cy - 10*f.sc + math.sin(a)*14*f.sc*env(t)), f.c(i, 0))
    if var == 'stille':
        for i in range(4): f.s(cx - 6*f.sc + i*4*f.sc, cy - 12*f.sc - (t % 3), f.c(0, 0))

def f_wolke(f, t, var):
    cx, cy = f.W/2, f.H * (.45 if var != 'nebel' else .6)
    n = 14 if var != 'glitzer' else 8
    for i in range(n):
        a = i / n * 6.28 + t * .15
        r = (7 + (i % 3) * 1.5) * f.sc * env(t, 3, 8)
        f.puff(cx + math.cos(a) * f.W*.28, cy + math.sin(a) * f.H*.15, r, i)
    f.puff(cx, cy, 8 * f.sc * env(t, 3, 8), 0)
    m = {'sporen': 18, 'glitzer': 30, 'sturm': 20}.get(var, 8)
    for i in range(m):
        x = f.rng.uniform(f.W*.1, f.W*.9); y = cy + f.rng.uniform(-f.H*.3, f.H*.3) + ((t + i) % 5) * (1 if var != 'sporen' else -1)
        f.s(x, y, f.c(i, 0 if var == 'glitzer' else 1))
    if var == 'sturm' and t % 3 == 1: f.bolt(cx, cy, cx + f.rng.uniform(-10, 10)*f.sc, f.gy, f.c(-1, 1), f.c(-1, 0), 4)

def f_regen(f, t, var):
    top = 6 * f.sc
    for i in range(11): f.cloud(f.W*(i + .5)/11, top + (i % 2)*2, 5*f.sc*env(t, 2, 9))
    if t < 2: return
    n = int(16 * f.sc)
    for i in range(n):
        x = f.rng.uniform(4, f.W - 4); speed = f.H * .14
        y = top + 4 + ((t * speed + i * 7) % (f.gy - top - 4))
        col = f.c(i, 1 if i % 3 else 0)
        if var in ('', 'traenen', 'heilung', 'sintflut'): f.line((x, y), (x - 1, y - 3*f.sc), col)
        elif var in ('hagel', 'steine', 'asche'): f.disc(x, y, 1.2*f.sc, col)
        elif var == 'funken': f.s(x, y, f.c(i, 0)); f.s(x + 1, y - 1, col)
        elif var in ('dornen',): f.line((x, y), (x, y - 4*f.sc), col)
        elif var in ('blueten',): f.s(x, y, f.c(i, 1)); f.s(x + 1, y, f.c(i, 0))
        elif var == 'licht': f.line((x, y - 6*f.sc), (x, y), f.c(0, 0))
        elif var == 'blitze':
            if (i + t) % 6 == 0: f.bolt(x, top + 4, x + f.rng.uniform(-4, 4), f.gy, f.c(i, 1), f.c(i, 0), 4)
            else: f.disc(x, y, 1, col)
        elif var == 'ranken': f.line((x, y), (x - 2, y - 3*f.sc), col); f.s(x, f.gy - (t % 3), f.c(1, 1))
        else: f.s(x, y, col)
        if y > f.gy - 3: f.ring(x, f.gy, 2*f.sc, 1, f.c(i, 0))
    if var == 'sintflut': f.d.rectangle([0, f.gy - 2 - t*.6*f.sc, f.W, f.gy], fill=f.c(0, 2))
    if var == 'heilung':
        for i in range(4): x = f.W*(i + .5)/4; f.line((x - 2, f.gy - 6), (x + 2, f.gy - 6), f.c(1, 0)); f.line((x, f.gy - 8), (x, f.gy - 4), f.c(1, 0))

def f_saeule(f, t, var):
    cx = f.W * .5
    if t < 2:
        f.line((cx, 0), (cx, f.gy), f.c(0, 1 if t else 2)); f.ring(cx, f.gy, 6*f.sc, 2*f.sc, f.c(0, 1))
        if var == 'stern': f.disc(cx + (2 - t)*12*f.sc, 6*f.sc + t*6, 3*f.sc, f.c(0, 0))
        return
    w = (7 if t < 7 else 7 - (t - 6) * 2) * f.sc * (1.3 if var == 'lanze' else 1)
    if var == 'blitz' or var == 'stern':
        f.bolt(cx, 0, cx, f.gy, f.c(0, 1), f.c(0, 0), 7, 5*f.sc)
        if t % 2: f.bolt(cx + 3, 0, cx - 2, f.gy, f.c(1, 1), None, 6, 6*f.sc)
    else:
        for x in range(int(cx - w), int(cx + w) + 1):
            d = abs(x - cx) / max(1, w)
            for y in range(0, f.gy):
                if d < .3: f.s(x, y, f.c(0, 0))
                elif d < .7: f.s(x, y, f.c(0, 1))
                elif (x + y + t) % 2 == 0: f.s(x, y, f.c(1, 1))
    r = (t - 1) * 3 * f.sc
    f.ring(cx, f.gy, r, r*.35, f.c(0, 0)); f.ring(cx, f.gy, r*.7, r*.25, f.c(1, 1))
    f.sparks(cx, f.gy - 4, r*.8, 12, rise=t)

def f_boden(f, t, var):
    cx, cy = f.W/2, f.gy - 3; e = env(t, 3, 9)
    rx, ry = f.W*.42*e, f.H*.14*e
    base = {'lava': 0, 'schlamm': 0, 'sumpf': 0, 'see': 0, 'eis': 0, 'faeulnis': 0, 'quelle': 0}
    if var == 'riss':
        pts = [(f.W*.1, cy)] + [(f.W*(.1 + .8*i/8), cy + f.rng.uniform(-3, 3)) for i in range(1, 9)]
        k = min(len(pts), 2 + t)
        for a, b in zip(pts[:k], pts[1:k]): f.line(a, b, f.c(0, 1), 3); f.line(a, b, f.c(0, 0))
        f.sparks(cx, cy - 3, f.W*.35, 14, rise=t)
        return
    f.ell(cx, cy, rx, ry, f.c(0, 2)); f.ell(cx, cy - 1, rx*.85, ry*.75, f.c(0, 1))
    if var == 'treibsand':
        for i in range(24): a = i*.5 + t*.4; rr = i/24*rx; f.s(cx + math.cos(a)*rr, cy + math.sin(a)*rr*ry/max(1, rx), f.c(0, 2))
    elif var == 'eis':
        for i in range(5):
            x = cx - rx*.7 + i*rx*.35; h = (4 + (i % 2)*4) * f.sc * e
            f.poly([(x - 2*f.sc, cy), (x + 2*f.sc, cy), (x, cy - h)], f.c(0, 0))
        if 'elektro' in [k for k in []]: pass
    elif var == 'geysir' or var == 'quelle':
        for i in range(3 if var == 'geysir' else 1):
            x = cx - rx*.5 + i*rx*.5; h = f.H*.6*abs(math.sin((t + i*2) * .7)) * e
            for y in range(int(cy - h), int(cy)): f.s(x + math.sin(y*.5)*1, y, f.c(0, 0 if y < cy - h + 3 else 1))
            f.puff(x, cy - h, 3*f.sc*e, 1)
    elif var == 'haende':
        for i in range(3):
            x = cx - rx*.5 + i*rx*.5; h = 10*f.sc*abs(math.sin(t*.6 + i))
            f.line((x, cy), (x, cy - h), f.c(-1, 2), 2)
            for j in (-2, 0, 2): f.line((x, cy - h), (x + j, cy - h - 3), f.c(-1, 2))
    for i in range(int(6*f.sc)):
        x = cx + f.rng.uniform(-rx*.8, rx*.8); y = cy + f.rng.uniform(-ry*.5, ry*.5)
        if (t + i) % 3 == 0: f.disc(x, y - 1, 1.5*f.sc, f.c(i, 0))
    if var == 'sumpf':
        for i in range(4): x = cx - rx*.6 + i*rx*.4; f.line((x, cy), (x + 1, cy - 6*f.sc), f.c(-1, 2))

def f_wall(f, t, var):
    h = f.H * .7 * min(1, (t + 1) / 5)
    x0, x1 = f.W * .3, f.W * .75
    if var == 'wolke':
        for i in range(8): f.puff(f.W*(.1 + .1*i), f.gy - 10*f.sc - i*1.5*f.sc*min(1, t/4), 4*f.sc, 0)
        return
    n = 6
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1); hh = h * (.8 + .2 * ((i * 7) % 3) / 2)
        if var in ('eis', 'spiegel', 'fels', '', 'labyrinth'):
            f.poly([(x - 5*f.sc, f.gy), (x + 5*f.sc, f.gy), (x + 3*f.sc, f.gy - hh), (x - 2*f.sc, f.gy - hh - 3*f.sc)], f.c(i, 2 if i % 2 else 1))
            f.line((x - 1, f.gy - 2), (x, f.gy - hh + 2), f.c(0, 0))
        elif var in ('dornen', 'baeume'):
            f.line((x, f.gy), (x + math.sin(i)*2, f.gy - hh), f.c(i, 2), 3)
            for j in range(4): f.line((x, f.gy - hh*j/4), (x + 3*f.sc*(1 if j % 2 else -1), f.gy - hh*j/4 - 2), f.c(1, 1))
            if var == 'baeume': f.puff(x, f.gy - hh, 4*f.sc, 0)
        elif var == 'wind':
            for y in range(int(f.gy - hh), f.gy, 3): f.s(x + math.sin(y*.3 + t)*3, y, f.c(i, 1))
    if var == 'spiegel':
        for i in range(3): f.line((x0 + i*8*f.sc, f.gy - h*.8), (x0 + i*8*f.sc + 3, f.gy - h*.6), WHITE)

def f_kuppel(f, t, var):
    cx = f.W/2; e = min(1, (t + 1)/4)
    if var == 'schild':
        x = f.W*.6; h = f.H*.7*e
        f.ell(x, f.gy - h/2, 4*f.sc, h/2, f.c(0, 2)); f.ell(x, f.gy - h/2, 3*f.sc, h/2 - 2, f.c(0, 1))
        f.line((x - 1, f.gy - h*.8), (x - 1, f.gy - h*.3), f.c(0, 0))
        for i in range(4): f.s(x + 3*f.sc, f.gy - h*f.rng.random(), f.c(1, 0))
        return
    rx = f.W*.42*e; ry = f.H*(.85 if var == 'gross' else .7)*e
    for k in range(48):
        a = math.pi + k/47*math.pi
        x, y = cx + math.cos(a)*rx, f.gy + math.sin(a)*ry
        f.s(x, y, f.c(k, 1)); f.s(x, y + 1, f.c(k, 2))
    for k in range(int(20*f.sc)):
        a = math.pi + f.rng.random()*math.pi; r = f.rng.random()
        if (k + t) % 3 == 0: f.s(cx + math.cos(a)*rx*r, f.gy + math.sin(a)*ry*r, f.c(k, 0))
    f.ring(cx, f.gy, rx, 3*f.sc, f.c(0, 1))
    if var == 'gross':
        for k in range(3): f.line((cx - rx*.5 + k*rx*.5, f.gy), (cx - rx*.5 + k*rx*.5, f.gy - ry*.7), f.c(k, 0))

def f_wirbel(f, t, var):
    cx = f.W/2; e = env(t, 2, 8)
    if var == 'umkreis':
        for i in range(14):
            a = i/14*6.28 + t*.6; x = cx + math.cos(a)*f.W*.3; y = f.gy - 12*f.sc + math.sin(a)*5*f.sc
            f.disc(x, y, 2*f.sc*e, f.c(i, 1 if math.sin(a) > 0 else 2)); f.s(x, y - 2, f.c(i, 0))
        return
    H = f.H * (.9 if var == 'gross' else .75)
    for j in range(22):
        k = j / 21; y = f.gy - k*H; r = (3 + k * f.W*.28) * e
        for i in range(22):
            a = i/22*6.28 + t*.9 + j*.5
            col = f.c(i + j, 1 if math.sin(a) > 0 else 2)
            if var == 'strudel': col = f.c(i, 2 if k < .5 else 1)
            f.s(cx + math.cos(a)*r + math.sin(k*4 + t)*2, y + math.sin(a)*r*.25, col)
    for i in range(10):
        a = f.rng.random()*6.28; k = f.rng.random()
        x = cx + math.cos(a + t)*(k*f.W*.3); y = f.gy - k*H
        if var == 'blaetter': f.s(x, y, f.c(1, 1)); f.s(x + 1, y, f.c(1, 2))
        elif var == 'klingen': f.line((x, y), (x + 3, y - 1), f.c(0, 0))
        else: f.s(x, y, f.c(i, 0))

def f_ranke(f, t, var):
    tx = f.W * .62; e = min(1, (t + 1) / 5)
    if var == 'peitsche':
        pts = []
        for i in range(16):
            k = i/15; x = 8*f.sc + (f.W*.75)*k*e; y = f.H*.5 + math.sin(k*6 - t*1.3)*6*f.sc*(1 - k*.3)
            pts.append((x, y))
        for a, b in zip(pts, pts[1:]): f.line(a, b, f.c(0, 1), 2); f.line(a, b, f.c(0, 0))
        return
    if var == 'hand':
        h = 18*f.sc*e
        f.line((tx, f.gy), (tx, f.gy - h), f.c(0, 2), int(4*f.sc))
        for j in (-3, -1, 1, 3): f.line((tx, f.gy - h), (tx + j*f.sc, f.gy - h - 5*f.sc + abs(j)), f.c(0, 2), 2)
        f.ell(tx, f.gy, 6*f.sc, 2*f.sc, f.c(0, 2)); return
    if var == 'netz':
        for i in range(5):
            f.line((tx - 12*f.sc + i*6*f.sc, f.gy - 20*f.sc*e), (tx - 12*f.sc + i*6*f.sc, f.gy), f.c(i, 1))
            f.line((tx - 12*f.sc, f.gy - i*5*f.sc*e), (tx + 12*f.sc, f.gy - i*5*f.sc*e), f.c(i, 1))
        if t % 2: f.bolt(tx - 12*f.sc, f.gy - 10*f.sc, tx + 12*f.sc, f.gy - 12*f.sc, f.c(0, 0), None, 4)
        return
    n = 4 if var != 'baeume' else 3
    for i in range(n):
        bx = tx - 12*f.sc + i*8*f.sc
        pts = [(bx, f.gy)]
        for j in range(10):
            k = j/9; a = -math.pi/2 + math.sin(k*5 + t*.8 + i)*.7
            pts.append((pts[-1][0] + math.cos(a)*2.4*f.sc*e, pts[-1][1] + math.sin(a)*2.4*f.sc*e))
        for a, b in zip(pts, pts[1:]): f.line(a, b, f.c(i, 2 if var == 'baeume' else 1), 3 if var == 'baeume' else 2)
        if var == 'blitz' and (t + i) % 2: f.s(pts[-1][0], pts[-1][1], f.c(1, 0))
        if var == 'baeume': f.puff(pts[-1][0], pts[-1][1], 4*f.sc, 0)
    f.ell(tx, f.gy, 14*f.sc*e, 2*f.sc, f.c(0, 2))

def f_blitz(f, t, var):
    x0, y0 = 8*f.sc, f.H*.5
    if t in (0, 1): f.disc(x0, y0, (2 + t*2)*f.sc, f.c(0, 0)); return
    if t > 7: f.sparks(f.W*.8, f.H*.55, 6*f.sc, 8); return
    targets = [(f.W*.85, f.H*.55)] if var not in ('kette',) else [(f.W*.45, f.H*.6), (f.W*.7, f.H*.4), (f.W*.9, f.H*.65)]
    if var == 'boden':
        for i in range(8): f.line((x0 + i*f.W*.1, f.gy - (i % 2)*2), (x0 + (i + 1)*f.W*.1, f.gy - ((i + 1) % 2)*2), f.c(1, 2), 2)
        f.bolt(f.W*.8, f.gy, f.W*.8, f.gy - 18*f.sc, f.c(0, 1), f.c(0, 0), 4); return
    prev = (x0, y0)
    for i, tg in enumerate(targets):
        f.bolt(prev[0], prev[1], tg[0], tg[1], f.c(i, 1), f.c(0, 0), 6, 4*f.sc)
        f.disc(tg[0], tg[1], 2*f.sc, f.c(0, 0)); f.sparks(tg[0], tg[1], 5*f.sc, 6)
        prev = tg
    if var == 'kurz': pass

def f_heilung(f, t, var):
    cx = f.W/2; e = env(t, 2, 8)
    f.ell(cx, f.gy, f.W*.3*e, 3*f.sc, f.c(0, 1), fill=False)
    for i in range(int(14*f.sc)):
        x = cx + f.rng.uniform(-f.W*.28, f.W*.28); y = f.gy - ((t*4 + i*5) % int(f.H*.8))
        if var == 'regenbogen': col = [C('#ff6a6a'), C('#ffd27a'), C('#8ae06a'), C('#6ab8ff'), C('#b88aff')][i % 5]
        else: col = f.c(i, 0 if i % 2 else 1)
        if i % 3 == 0: f.line((x - 1, y), (x + 1, y), col); f.line((x, y - 1), (x, y + 1), col)
        else: f.s(x, y, col)
    if var == 'herz' and 3 <= t <= 7:
        hx, hy = cx, f.H*.45; s = 2*f.sc
        f.disc(hx - s, hy, s*1.2, f.c(0, 1)); f.disc(hx + s, hy, s*1.2, f.c(0, 1)); f.poly([(hx - 2.4*s, hy + .5*s), (hx + 2.4*s, hy + .5*s), (hx, hy + 3*s)], f.c(0, 1))
        if t % 2: f.bolt(hx - 3*s, hy, hx + 3*s, hy - s, f.c(1, 0), None, 3)
    if var in ('gross', 'regenbogen') and 3 <= t <= 7:
        f.line((cx, f.H*.2), (cx, f.H*.5), f.c(0, 0), 2); f.line((cx - 5*f.sc, f.H*.33), (cx + 5*f.sc, f.H*.33), f.c(0, 0), 2)
    if var == 'boden': f.ell(cx, f.gy, f.W*.35*e, 2*f.sc, f.c(-1, 1))

def f_aura(f, t, var):
    cx = f.W/2; top = f.gy - 26*f.sc; e = env(t, 2, 8)
    if var in ('teleport', 'sprint'):
        if var == 'teleport':
            x = cx - 10*f.sc if t < 5 else cx + 12*f.sc
            k = abs(t - 4.5) / 4.5
            for i in range(int(20*k*f.sc)): f.s(x + f.rng.uniform(-4, 4)*f.sc, f.gy - f.rng.random()*24*f.sc, f.c(i, 1))
            f.ell(x, f.gy, 6*f.sc, 2*f.sc, f.c(0, 2))
        else:
            for i in range(6):
                y = f.gy - 4*f.sc - i*3*f.sc; L = f.W*.6*e
                f.line((cx - L/2 + (t*3) % 8, y), (cx + L/2, y), f.c(i, 1 if i % 2 else 0))
        return
    if var == 'fluegel':
        for s in (-1, 1):
            for k in range(8):
                a = .3 + k*.15; L = 14*f.sc*e
                f.line((cx, top + 10*f.sc), (cx + s*math.cos(a)*L, top + 10*f.sc - math.sin(a)*L + k), f.c(k, 0 if k % 2 else 1))
    if var == 'unsichtbar':
        for y in range(int(top), f.gy):
            for x in range(int(cx - 8*f.sc), int(cx + 8*f.sc)):
                if (x + y + t) % 5 == 0: f.s(x, y, f.c(0, 1))
        return
    if var in ('nebel', 'schatten', 'flimmern'):
        for i in range(10):
            f.puff(cx + f.rng.uniform(-8, 8)*f.sc, f.gy - f.rng.uniform(2, 24)*f.sc - t, 3*f.sc*e, i)
        return
    for i in range(int(16*f.sc)):
        x = cx + f.rng.uniform(-10, 10)*f.sc; y = f.gy - ((t*3 + i*4) % int(28*f.sc))
        if abs(x - cx) < 5*f.sc and y > top + 4: x += 6*f.sc * (1 if x > cx else -1)
        f.s(x, y, f.c(i, i % 2)); f.s(x, y + 1, f.c(i, 2))
    if var == 'tempo':
        for i in range(4): f.line((cx - 16*f.sc, f.gy - 6*f.sc - i*5*f.sc), (cx - 9*f.sc, f.gy - 6*f.sc - i*5*f.sc), f.c(0, 0))
    if var in ('schweben', 'federn'):
        f.ell(cx, f.gy, 10*f.sc*e, 2*f.sc, f.c(0, 1))
        if var == 'federn':
            for i in range(5): x = cx + f.rng.uniform(-12, 12)*f.sc; y = top + ((t*2 + i*7) % 24)*f.sc; f.line((x, y), (x + 2, y + 1), WHITE)
    if var == 'stark': f.ring(cx, f.gy, 12*f.sc*e, 3*f.sc*e, f.c(0, 0))

def f_beschwoerung(f, t, var):
    cx = f.W/2
    rx = f.W*.4*min(1, (t + 1)/3)
    for i in range(40):
        a = i/40*6.28 + t*.15; f.s(cx + math.cos(a)*rx, f.gy + math.sin(a)*rx*.25, f.c(i // 10, 1 if i % 3 else 0))
    for i in range(6):
        a = i/6*6.28 + t*.15; b = (i + 2)/6*6.28 + t*.15
        f.line((cx + math.cos(a)*rx*.8, f.gy + math.sin(a)*rx*.2), (cx + math.cos(b)*rx*.8, f.gy + math.sin(b)*rx*.2), f.c(i, 2))
    if t < 3: return
    k = min(1, (t - 2) / 4); hmax = f.H*.82
    h = hmax * k
    body, lite = f.c(0, 2), f.c(0, 1)
    if var in ('golem', 'titan'):
        w = (10 if var == 'golem' else 14) * f.sc
        f.d.rectangle([cx - w*.6, f.gy - h, cx + w*.6, f.gy - h*.35], fill=body)
        f.d.rectangle([cx - w*.3, f.gy - h*.35, cx - w*.1, f.gy], fill=body); f.d.rectangle([cx + w*.1, f.gy - h*.35, cx + w*.3, f.gy], fill=body)
        f.d.rectangle([cx - w, f.gy - h*.95, cx - w*.6, f.gy - h*.45], fill=lite); f.d.rectangle([cx + w*.6, f.gy - h*.95, cx + w, f.gy - h*.45], fill=lite)
        f.d.rectangle([cx - w*.3, f.gy - h - w*.5, cx + w*.3, f.gy - h], fill=lite)
        if t >= 7: f.s(cx + w*.1, f.gy - h - w*.25, f.c(1, 0)); f.s(cx - w*.1, f.gy - h - w*.25, f.c(1, 0))
    elif var in ('geist', 'gestalten', 'untote'):
        n = 1 if var == 'geist' else 3
        for i in range(n):
            x = cx + (i - (n - 1)/2) * 12*f.sc; hh = h * (1 if n == 1 else .7)
            f.poly([(x - 5*f.sc, f.gy - hh*.6), (x + 5*f.sc, f.gy - hh*.6), (x + 2*f.sc, f.gy - 2), (x - 4*f.sc + math.sin(t + i)*2, f.gy - 4)], body)
            f.disc(x, f.gy - hh*.65, 5*f.sc, lite)
            if t >= 6: f.s(x + 2*f.sc, f.gy - hh*.67, f.c(1, 0)); f.s(x - 1*f.sc, f.gy - hh*.67, f.c(1, 0))
    elif var == 'baum':
        f.line((cx, f.gy), (cx, f.gy - h*.6), body, int(4*f.sc))
        f.puff(cx, f.gy - h*.7, 10*f.sc*k, 0)
        if t >= 7: f.s(cx + 2*f.sc, f.gy - h*.4, f.c(1, 0))
    elif var in ('drache', 'ungeheuer'):
        f.ell(cx, f.gy - h*.35, 14*f.sc*k, 7*f.sc*k, body)
        f.line((cx + 10*f.sc*k, f.gy - h*.4), (cx + 16*f.sc*k, f.gy - h*.8), body, int(3*f.sc))
        f.disc(cx + 17*f.sc*k, f.gy - h*.85, 3*f.sc*k, lite)
        if var == 'drache':
            f.poly([(cx - 2*f.sc, f.gy - h*.45), (cx - 16*f.sc*k, f.gy - h), (cx - 6*f.sc, f.gy - h*.4)], lite)
        else:
            for i in range(4): f.line((cx - 10*f.sc + i*6*f.sc, f.gy - h*.3), (cx - 12*f.sc + i*6*f.sc + math.sin(t + i)*3, f.gy), body, 2)
    elif var == 'armee':
        for i in range(5):
            x = cx - 20*f.sc + i*10*f.sc; hh = h*.6
            f.d.rectangle([x - 2*f.sc, f.gy - hh, x + 2*f.sc, f.gy], fill=body); f.disc(x, f.gy - hh - 2*f.sc, 2*f.sc, lite)
            f.line((x + 3*f.sc, f.gy - hh - 4*f.sc), (x + 3*f.sc, f.gy - 2), f.c(1, 0))
    f.sparks(cx, f.gy - h*.5, f.W*.3, 8, rise=t)

def f_gefaengnis(f, t, var):
    cx = f.W*.6; e = min(1, (t + 1)/5); h = f.H*.65
    if var == 'sarg':
        hh = h * e
        f.d.rectangle([cx - 9*f.sc, f.gy - hh, cx + 9*f.sc, f.gy], fill=f.c(0, 2)); f.d.rectangle([cx - 7*f.sc, f.gy - hh + 2, cx + 7*f.sc, f.gy - 2], fill=f.c(0, 1))
        f.line((cx - 5*f.sc, f.gy - hh + 3), (cx - 2*f.sc, f.gy - hh*.5), f.c(0, 0))
    elif var == 'kaefig':
        for i in range(6):
            x = cx - 10*f.sc + i*4*f.sc
            if (i + t) % 2 or t < 3: f.bolt(x, f.gy - h*e, x, f.gy, f.c(0, 1), f.c(0, 0), 4, 2)
        f.line((cx - 11*f.sc, f.gy - h*e), (cx + 11*f.sc, f.gy - h*e), f.c(0, 0))
    elif var == 'kristall':
        for i in range(7):
            a = -math.pi/2 + (i - 3)*.35; L = h*e*(.7 + .3*(i % 2))
            f.poly([(cx + (i - 3)*3*f.sc, f.gy), (cx + (i - 3)*3*f.sc + 3*f.sc, f.gy), (cx + (i - 3)*1.2*f.sc + math.cos(a)*L*.3, f.gy - L)], f.c(i, 1 if i % 2 else 0))
    elif var == 'kerker':
        f.ell(cx, f.gy, 12*f.sc, 4*f.sc, f.c(0, 2))
        for i in range(5): f.line((cx - 10*f.sc + i*5*f.sc, f.gy - h*e), (cx - 10*f.sc + i*5*f.sc, f.gy), f.c(i, 2), 2)
    elif var == 'druck':
        for i in range(5):
            x = cx - 12*f.sc + i*6*f.sc; y = (t * 5 + i*7) % int(h)
            f.line((x, f.gy - h + y), (x, f.gy - h + y + 6), f.c(i, 1)); f.poly([(x - 2, f.gy - h + y + 6), (x + 2, f.gy - h + y + 6), (x, f.gy - h + y + 9)], f.c(i, 1))
        f.ell(cx, f.gy, 14*f.sc*e, 3*f.sc, f.c(0, 2))
    f.sparks(cx, f.gy - h*.5, 12*f.sc, 6)

def f_fluch(f, t, var):
    cx, cy = f.W*.6, f.H*.35; e = env(t, 2, 8)
    r = 8*f.sc*e
    for i in range(12):
        a = i/12*6.28 + t*.4; f.s(cx + math.cos(a)*r, cy + math.sin(a)*r*.5, f.c(i, 1))
    for i in range(3):
        a = i/3*6.28 - t*.6; b = (i + 1)/3*6.28 - t*.6
        f.line((cx + math.cos(a)*r*.7, cy + math.sin(a)*r*.35), (cx + math.cos(b)*r*.7, cy + math.sin(b)*r*.35), f.c(i, 2))
    for i in range(8):
        k = ((t + i) % 6) / 6
        a = i/8*6.28
        x = cx + math.cos(a)*14*f.sc*(1 - k); y = f.gy - 12*f.sc + math.sin(a)*6*f.sc*(1 - k)
        f.s(x, y, f.c(i, 0 if var in ('sog', 'blut') else 1))
    if var == 'faeden':
        for i in range(3): f.line((cx - 6*f.sc + i*6*f.sc, cy), (cx - 6*f.sc + i*6*f.sc + math.sin(t + i)*2, f.gy - 10*f.sc), f.c(i, 0))
    if var == 'kette':
        for i in range(8): f.ring(f.W*.2 + i*f.W*.08, f.H*.5 + math.sin(i + t)*2, 2*f.sc, 1.5*f.sc, f.c(i, 1))
    if var == 'blase': f.ring(cx, f.gy - 18*f.sc, 7*f.sc*e, 6*f.sc*e, f.c(0, 0))
    if var == 'blut':
        for i in range(5): f.s(cx - 4 + i*2, f.gy - 8*f.sc + (t + i) % 4, C('#c83a3a'))
    if var == 'biss':
        for i in range(4): f.poly([(cx - 8*f.sc + i*5*f.sc, f.gy - 14*f.sc), (cx - 5*f.sc + i*5*f.sc, f.gy - 14*f.sc), (cx - 6.5*f.sc + i*5*f.sc, f.gy - 14*f.sc + 5*f.sc*e)], f.c(0, 0))

def f_explosion(f, t, var):
    els = [el for el in f.els]
    a = els[0]; b = OPP.get(a, els[-1])
    for el in els:
        if OPP.get(el) in els: a, b = el, OPP[el]; break
    A, B = ELEM[a], ELEM[b]
    cx = f.W * (.25 if var == 'selbst' else .5); cy = f.H * .55
    if t < 4:
        r = (3 + t*2) * f.sc
        for i in range(int(40*f.sc)):
            ang = f.rng.random()*6.28; rr = f.rng.random()*r
            f.s(cx + math.cos(ang)*rr, cy + math.sin(ang)*rr, (A if math.cos(ang + t) > 0 else B)[i % 3])
        for _ in range(t + 1):
            f.bolt(cx, cy, cx + f.rng.uniform(-r, r)*1.5, cy + f.rng.uniform(-r, r)*1.5, WHITE, None, 3, 3)
    elif t == 4:
        f.disc(cx, cy, f.H*.45, WHITE); f.disc(cx, cy, f.H*.3, A[0])
    else:
        r = (t - 3) * f.H * .13 * (1.4 if var == 'gross' else 1)
        f.ring(cx, cy, r, r*.85, A[1]); f.ring(cx, cy, r*.8, r*.7, B[1], dots=2)
        for i in range(int(20*f.sc)):
            ang = i/(20*f.sc)*6.28; rr = r*(.5 + f.rng.random()*.4)
            if (i + t) % 2: f.s(cx + math.cos(ang)*rr, cy + math.sin(ang)*rr, (A if i % 2 else B)[min(2, t - 5)])
        for i in range(6): f.puff(cx + f.rng.uniform(-r, r)*.6, cy + f.rng.uniform(-r, r)*.5, 2*f.sc, -1) if t > 6 else None
    if var == 'licht' and t in (3, 4, 5):
        for i in range(12): ang = i/12*6.28; f.line((cx, cy), (cx + math.cos(ang)*f.W*.45, cy + math.sin(ang)*f.H*.45), WHITE)

def f_portal(f, t, var):
    cx, cy = f.W/2, f.gy - f.H*.35; e = min(1, (t + 1)/5)
    if var == 'riss':
        pts = [(cx, cy - f.H*.35*e)]
        for i in range(1, 8): pts.append((cx + f.rng.uniform(-3, 3)*f.sc, cy - f.H*.35*e + i*f.H*.1*e))
        for a, b in zip(pts, pts[1:]): f.line(a, b, f.c(0, 0), 3); f.line(a, b, f.c(1, 2))
        f.sparks(cx, cy, 10*f.sc, 10)
        return
    if var == 'schlund':
        f.ell(cx, f.gy - 2, f.W*.35*e, 6*f.sc*e, C('#0c0810')); f.ring(cx, f.gy - 2, f.W*.35*e, 6*f.sc*e, f.c(0, 1))
        f.sparks(cx, f.gy - 8*f.sc, f.W*.3, 10, rise=t); return
    rx, ry = 10*f.sc*e, f.H*.38*e
    f.ell(cx, cy, rx + 2, ry + 2, f.c(0, 2)); f.ell(cx, cy, rx, ry, C('#140c1c'))
    for i in range(20):
        a = i/20*6.28 + t*.5; rr = (i % 5)/5
        f.s(cx + math.cos(a)*rx*rr, cy + math.sin(a)*ry*rr, f.c(i, 1))
    f.ring(cx, cy, rx + 2, ry + 2, f.c(1, 1))

def f_feld(f, t, var):
    cx = f.W/2; e = min(1, (t + 1)/3)
    rx, ry = f.W*.38*e, f.H*.13*e
    f.ring(cx, f.gy - 2, rx, ry, f.c(0, 1)); f.ring(cx, f.gy - 2, rx*.75, ry*.75, f.c(1 if len(f.P) > 1 else 0, 2))
    nr = 4 + len(f.P)
    for i in range(nr):
        a = i/nr*6.28 + t*.2; x, y = cx + math.cos(a)*rx*.87, f.gy - 2 + math.sin(a)*ry*.87
        f.s(x, y, f.c(i, 0)); f.s(x + 1, y, f.c(i, 0))
    pulse = (t % 5) / 5
    if var in ('puls', 'magnet', 'adern'):
        f.ring(cx, f.gy - 2, rx*pulse, ry*pulse, f.c(0, 0), dots=2)
    if var == 'adern':
        for i in range(5): f.line((cx, f.gy - 2), (cx + math.cos(i*1.3)*rx, f.gy - 2 + math.sin(i*1.3)*ry), f.c(i, 1))
    if var in ('flamme',):
        for i in range(5): x = cx - rx*.5 + i*rx*.25; f.disc(x, f.gy - 5 - (t + i) % 3, 1.5*f.sc, f.c(0, i % 2))
    if var in ('spiegel', 'auge'):
        f.ell(cx, f.H*.35, 8*f.sc*e, (5 if var == 'auge' else 8)*f.sc*e, f.c(0, 1)); f.ell(cx, f.H*.35, 3*f.sc*e, 3*f.sc*e, f.c(1, 2) if var == 'auge' else WHITE)
    if var == 'moos':
        for i in range(int(14*f.sc)): x = cx + f.rng.uniform(-rx, rx); f.s(x, f.gy - 2 + f.rng.uniform(-ry, ry)*.6, f.c(i, 1 if (i + t) % 3 else 0))
    if var == 'siegel':
        for i in range(5):
            a = i/5*6.28 - math.pi/2; b = (i + 2)/5*6.28 - math.pi/2
            f.line((cx + math.cos(a)*rx*.7, f.gy - 2 + math.sin(a)*ry*.7), (cx + math.cos(b)*rx*.7, f.gy - 2 + math.sin(b)*ry*.7), f.c(i, 0))
    if var == 'blitz' and t % 2: f.bolt(cx - rx*.6, f.gy - 2, cx + rx*.6, f.gy - 3, f.c(-1, 1), f.c(-1, 0), 5, 2)
    for i in range(6): f.s(cx + f.rng.uniform(-rx, rx)*.8, f.gy - 4 - ((t*2 + i*5) % int(14*f.sc)), f.c(i, 0))

def f_wachstum(f, t, var):
    e = min(1, (t + 1)/7)
    if var in ('baum', 'blitzbaum'):
        cx = f.W/2; h = f.H*.8*e
        f.line((cx, f.gy), (cx, f.gy - h*.65), f.c(-1, 2) if var == 'baum' else C('#6a4a32'), int(4*f.sc))
        for s in (-1, 1): f.line((cx, f.gy - h*.45), (cx + s*8*f.sc*e, f.gy - h*.7), C('#6a4a32'), 2)
        f.puff(cx, f.gy - h*.8, 11*f.sc*e, 0); f.puff(cx - 8*f.sc*e, f.gy - h*.65, 7*f.sc*e, 1 if len(f.P) > 1 else 0)
        if var == 'blitzbaum' and t >= 6 and t % 2 == 0: f.bolt(cx, 0, cx, f.gy - h*.9, f.c(0, 1), f.c(0, 0), 4)
        return
    if var == 'maul':
        cx = f.W*.6; h = f.H*.6*e
        f.line((cx, f.gy), (cx - 3, f.gy - h), f.c(0, 2), int(3*f.sc))
        o = 3*f.sc*(1 + math.sin(t))
        f.ell(cx - 3, f.gy - h, 8*f.sc*e, (4*f.sc + o)*e, f.c(1, 1)); f.ell(cx - 1, f.gy - h, 5*f.sc*e, o*e, C('#5a1e2a'))
        return
    n = {'wald': 7, 'kristall': 6, 'dornen': 9}.get(var, 7)
    for i in range(n):
        x = f.W*(i + .5)/n + f.rng.uniform(-2, 2); h = (f.H*.35 + f.rng.random()*f.H*.35) * e
        if var in ('kristall', 'eis'):
            f.poly([(x - 3*f.sc, f.gy), (x + 3*f.sc, f.gy), (x + 1*f.sc, f.gy - h), (x - 1*f.sc, f.gy - h - 2*f.sc)], f.c(i, 1 if i % 2 else 0))
            f.line((x - 1, f.gy - 2), (x - 1, f.gy - h + 2), WHITE)
        elif var == 'dornen':
            f.line((x, f.gy), (x + 2, f.gy - h*.7), f.c(i, 2), 2)
            for j in range(3): f.s(x + 1 + (1 if j % 2 else -1)*2, f.gy - h*.2*(j + 1), f.c(0, 0))
        elif var == 'wald':
            f.line((x, f.gy), (x, f.gy - h*.6), C('#5a3a2a'), 2); f.puff(x, f.gy - h*.7, 5*f.sc*e, i)
        else:
            f.line((x, f.gy), (x + math.sin(i + t*.3), f.gy - h*.6), f.c(-1, 2) if len(f.P) > 1 else C('#4a7d4a'))
            if t >= 4: f.disc(x, f.gy - h*.6, 1.8*f.sc, f.c(i, 0 if var == 'blumen' else 1))
    f.sparks(f.W/2, f.gy - 6, f.W*.4, 8, rise=t)

def f_himmel(f, t, var):
    e = env(t, 3, 8)
    if var == 'polarlicht':
        for b in range(len(f.P) + 1):
            for x in range(f.W):
                y = 6*f.sc + b*4*f.sc + math.sin(x*.12 + t*.6 + b)*4*f.sc
                for k in range(int(5*f.sc*e)):
                    if (x + k) % 2 == 0: f.s(x, y + k, f.c(b, 1))
        return
    if var in ('nacht', 'finsternis'):
        hgt = f.H * .9 * e
        for y in range(int(hgt)):
            for x in range(f.W):
                if (x + y) % (2 if y < hgt*.6 else 3) == 0: f.s(x, y, f.c(0, 2))
        if var == 'finsternis':
            f.disc(f.W/2, f.H*.3, 9*f.sc, f.c(-1, 0)); f.disc(f.W/2 + 4*f.sc*e, f.H*.3, 9*f.sc, C('#0c0810'))
        return
    if var in ('stern', 'sonne'):
        cx, cy = f.W/2, f.H*.25 if var == 'stern' else f.gy - 4*f.sc*e
        f.disc(cx, cy, (3 if var == 'stern' else 10)*f.sc*e, f.c(0, 0))
        for i in range(8 if var == 'stern' else 12):
            a = i/(8 if var == 'stern' else 12)*6.28 + t*.1; L = (10 if var == 'stern' else 18)*f.sc*e*(1 if i % 2 else .6)
            f.line((cx, cy), (cx + math.cos(a)*L, cy + math.sin(a)*L), f.c(i, 1))
        return
    for i in range(12): f.cloud(f.W*(i + .5)/12, 8*f.sc + (i % 2)*3, 6*f.sc*e)
    if var in ('gewitter',) and t % 3 != 1:
        x = f.rng.uniform(f.W*.2, f.W*.8); f.bolt(x, 12*f.sc, x + f.rng.uniform(-6, 6), f.gy, f.c(1, 1), WHITE, 6, 5)
    if var == 'winter':
        for i in range(int(20*f.sc)): f.s(f.rng.uniform(0, f.W), (t*3 + i*7) % f.H, WHITE)

def f_beben(f, t, var):
    cx = f.W/2; sh = (1 if t % 2 else -1) * f.sc
    for i in range(6):
        a = i/6*math.pi; L = f.W*.42*min(1, (t + 1)/5)
        x1 = cx + math.cos(a)*L; y1 = f.gy - 2 + math.sin(a)*4*f.sc
        f.line((cx + sh, f.gy - 2), (x1 + sh, y1), f.c(0, 2), 2); f.line((cx + sh, f.gy - 2), (x1 + sh, y1), f.c(0, 1))
    for i in range(int(8*f.sc)):
        x = f.rng.uniform(f.W*.1, f.W*.9); y = f.gy - abs(math.sin(t + i))*10*f.sc
        f.disc(x, y, 1.3*f.sc, f.c(i, 2))
    if var in ('staub', ''):
        for i in range(5): f.puff(f.W*(i + .5)/5, f.gy - 6*f.sc - (t % 3), 4*f.sc*env(t), 0)
    if var == 'blitz' and t % 2: f.bolt(f.rng.uniform(5, f.W - 5), 0, f.rng.uniform(5, f.W - 5), f.gy, f.c(1, 1), WHITE, 6, 5)
    if var == 'feuer':
        for i in range(8): f.disc(f.rng.uniform(4, f.W - 4), f.gy - 2, 1.5*f.sc, f.c(0, 0))

def f_waffe(f, t, var):
    cx, cy = f.W/2, f.H*.5; e = env(t, 3, 8)
    if var == 'pfeil':
        f.line((cx - 16*f.sc, cy), (cx + 14*f.sc, cy), C('#c8b898'), 2); f.poly([(cx + 14*f.sc, cy - 3*f.sc), (cx + 20*f.sc, cy), (cx + 14*f.sc, cy + 3*f.sc)], f.c(0, 0))
    else:
        f.line((cx - 2*f.sc, cy + 14*f.sc), (cx - 2*f.sc, cy - 16*f.sc), f.c(0, 0) if var != 'schmelze' else C('#c8ccd8'), int(3*f.sc))
        f.line((cx - 7*f.sc, cy + 8*f.sc), (cx + 3*f.sc, cy + 8*f.sc), C('#e0b048'), 2)
        f.line((cx - 2*f.sc, cy + 9*f.sc), (cx - 2*f.sc, cy + 15*f.sc), C('#6a4a32'), 2)
        if var == 'schmelze':
            for i in range(int(4*e*f.sc)): f.disc(cx - 2*f.sc + f.rng.uniform(-1, 1), cy - 10*f.sc + i*4, 1.5*f.sc, f.c(0, 1))
    for i in range(int(16*f.sc*e)):
        a = f.rng.random()*6.28; r = f.rng.uniform(4, 16)*f.sc
        f.s(cx + math.cos(a + t*.3)*r, cy + math.sin(a + t*.3)*r*.8, f.c(i, i % 3))
    if 3 <= t <= 6: f.ring(cx, cy, 14*f.sc*e, 14*f.sc*e*.8, f.c(1 if len(f.P) > 1 else 0, 0), dots=2)

FORMS = dict(geschoss=f_geschoss, strahl=f_strahl, kegel=f_kegel, welle=f_welle, ring=f_ring, wolke=f_wolke, regen=f_regen,
             saeule=f_saeule, boden=f_boden, wall=f_wall, kuppel=f_kuppel, wirbel=f_wirbel, ranke=f_ranke, blitz=f_blitz,
             heilung=f_heilung, aura=f_aura, beschwoerung=f_beschwoerung, gefaengnis=f_gefaengnis, fluch=f_fluch,
             explosion=f_explosion, portal=f_portal, feld=f_feld, wachstum=f_wachstum, himmel=f_himmel, beben=f_beben, waffe=f_waffe)
ANKER = dict(geschoss='linie', strahl='linie', kegel='linie', welle='linie', blitz='linie', ranke='ziel', wolke='flaeche',
             regen='flaeche', saeule='ziel', boden='flaeche', wall='ziel', kuppel='zaubernder', wirbel='flaeche', heilung='ziel',
             aura='zaubernder', beschwoerung='ziel', gefaengnis='ziel', fluch='ziel', explosion='flaeche', portal='ziel',
             feld='flaeche', wachstum='flaeche', himmel='flaeche', beben='flaeche', waffe='zaubernder', ring='zaubernder')
SCHLEIFE = {'wolke': 4, 'feld': 3, 'wall': 5, 'kuppel': 4, 'wirbel': 3, 'himmel': 4, 'boden': 4, 'aura': 3, 'wachstum': 7}

def slug(s):
    s = s.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')

def elemente(txt):
    m = {'dendro': 'dendro', 'elektro': 'elektro'}
    return [w.strip().lower() for w in txt.split('+')]

def render_spell(sp, form, var):
    W, H = SIZES[sp['stufe'].split(' ·')[0]]
    els = elemente(sp['elemente'])
    P = [ELEM[e] for e in els]
    bruch = 'Bruchklang' in sp['stufe']
    frames = []
    for t in range(N):
        rng = random.Random(sum(map(ord, sp['name'])) * 31 + t)
        f = F(W, H, P, rng); f.els = els
        FORMS[form](f, t, var)
        if bruch and form != 'explosion':
            a = els[0]; b = OPP.get(a)
            for e in els:
                if OPP.get(e) in els: a, b = e, OPP[e]; break
            for i in range(int(10 * f.sc)):
                x, y = rng.uniform(0, W), rng.uniform(0, H)
                if f.px[int(x), int(y)][3]: f.s(x, y, (ELEM[a] if (i + t) % 2 else ELEM[b])[0])
            if t == N - 2:
                for i in range(int(30*f.sc)): f.s(rng.uniform(0, W), rng.uniform(H*.3, H), WHITE if i % 2 else ELEM[b][1])
        frames.append(f.im)
    return frames

# ================================================================ Element-Grundzauber
GRUND = {'feuer': 'Feuerball', 'eis': 'Eissplitter', 'wasser': 'Wasserkugel', 'erde': 'Felsbrocken', 'dendro': 'Dornensaat',
         'wind': 'Windsichel', 'elektro': 'Blitzkugel', 'schatten': 'Schattenkugel', 'licht': 'Lichtkugel'}
GVAR = {'feuer': 'flamme', 'eis': 'lanze', 'wasser': '', 'erde': 'stein', 'dendro': 'samen', 'wind': 'klinge',
        'elektro': 'kugel', 'schatten': '', 'licht': 'wisp'}

def grund(el):
    P = [ELEM[el], ELEM[el]]
    parts = {}
    def fr(sz, fn):
        out = []
        for t in range(fn[1]):
            f = F(sz, sz, P, random.Random(t + len(el))); f.sc = sz / 24; f.els = [el]
            fn[0](f, t); out.append(f.im)
        return out
    def entstehen(f, t):
        c = f.W / 2
        for i in range(14):
            a = i/14*6.28 + t; r = (4 - t) * 3 * f.sc
            f.s(c + math.cos(a)*r, c + math.sin(a)*r, f.c(0, i % 3))
        proj(f, c, c, GVAR[el], .3 + t*.25, t)
    def flug(f, t):
        c = f.W / 2
        for j in range(1, 6): f.s(c - j*2.5*f.sc, c + math.sin(t*1.5 + j)*1.5, f.c(0, j % 3))
        proj(f, c + 2*f.sc, c, GVAR[el], 1.15, t)
        if el == 'elektro' and t % 2: f.bolt(c, c, c + 8*f.sc, c - 4, f.c(0, 1), None, 3, 2)
        if el == 'wasser':
            for j in range(3): f.s(c - 7*f.sc - j*2, c + (t + j) % 3 - 1, f.c(0, 0))
    def einschlag(f, t):
        c = f.W / 2; r = (2 + t * 2.4) * f.sc
        if t < 2: f.disc(c, c, (4 + t*3)*f.sc, f.c(0, t))
        f.ring(c, c, r, r*.85, f.c(0, 1 if t < 4 else 2), dots=1 if t < 4 else 2)
        f.sparks(c, c, r, 14, rise=t)
        if el in ('erde',):
            for i in range(6): a = i*1.05; f.disc(c + math.cos(a)*r*.8, c + math.sin(a)*r*.8 + t, 1.4*f.sc, f.c(0, 2))
        if el == 'dendro':
            for i in range(6): a = i*1.05 + t*.3; f.s(c + math.cos(a)*r*.7, c + math.sin(a)*r*.7, f.c(0, 1)); f.s(c + math.cos(a)*r*.7 + 1, c + math.sin(a)*r*.7, f.c(0, 0))
    parts['entstehen'] = fr(32, (entstehen, 4)); parts['flug'] = fr(32, (flug, 4)); parts['einschlag'] = fr(40, (einschlag, 6))
    return parts

# ================================================================ Export
def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w*len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(f, (i*w, 0))
    return s

def font(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', sz)
    except Exception: return ImageFont.load_default()

def main():
    out = os.path.join(HERE, 'sprites'); os.makedirs(out, exist_ok=True)
    book = json.load(open(os.path.join(HERE, 'zauberbuch.json'), encoding='utf-8'))
    mp = lade(); meta = {}
    per_chapter = {}
    for sp in book:
        form, var = mp[sp['name']]
        frames = render_spell(sp, form, var)
        d = os.path.join(out, slug(sp['kapitel'])); os.makedirs(d, exist_ok=True)
        fn = slug(sp['name']) + '.png'; strip(frames).save(os.path.join(d, fn))
        W, H = frames[0].size
        meta[sp['name']] = dict(datei=f"{slug(sp['kapitel'])}/{fn}", kapitel=sp['kapitel'], stufe=sp['stufe'], elemente=sp['elemente'],
                                wirkung=sp['wirkung'], form=form, variante=var, bilder=N, bild=[W, H], anker=ANKER[form],
                                schleife_ab=SCHLEIFE.get(form))
        per_chapter.setdefault(sp['kapitel'], []).append((sp['name'], sp['stufe'], frames))
    gd = os.path.join(out, 'grund'); os.makedirs(gd, exist_ok=True)
    grund_frames = {}
    for el, name in GRUND.items():
        parts = grund(el); grund_frames[el] = parts
        for p, fr in parts.items(): strip(fr).save(os.path.join(gd, f'{el}_{p}.png'))
        meta['Grundzauber: ' + name] = dict(element=el, teile={p: dict(datei=f'grund/{el}_{p}.png', bilder=len(fr), bild=list(fr[0].size)) for p, fr in parts.items()})
    meta['_hinweis'] = {'anker': {'linie': 'Bildmitte links = Hand des Zaubernden, Effekt läuft nach rechts (für links spiegeln)',
                                  'ziel': 'unten Mitte auf den Zielpunkt legen', 'flaeche': 'unten Mitte auf die Mitte der Fläche',
                                  'zaubernder': 'unten Mitte auf die Füße des Zaubernden'},
                        'schleife_ab': 'Dauerzauber: ab diesem Bild bis zum Ende in Schleife abspielen, solange der Zauber wirkt'}
    json.dump(meta, open(os.path.join(out, 'zauber.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau je Kapitel
    S = 2
    for kap, items in per_chapter.items():
        cols = 6; cw, ch = 96*S + 10, 64*S + 22
        rows = (len(items) + cols - 1) // cols
        imgs = []
        for t in range(N):
            im = Image.new('RGB', (cols*cw, rows*ch + 30), (30, 26, 48)); d = ImageDraw.Draw(im)
            d.text((8, 6), f'Zauberbuch – {kap}', fill=(255, 240, 200), font=font(16))
            for i, (name, st, fr) in enumerate(items):
                x, y = (i % cols)*cw, 30 + (i // cols)*ch
                f = fr[t]; big = f.resize((f.width*S, f.height*S), Image.NEAREST)
                d.rectangle([x + 2, y + 16, x + cw - 4, y + ch - 2], fill=(42, 36, 69))
                im.paste(big, (x + 4 + (96*S - big.width)//2, y + 18 + (64*S - big.height)), big)
                d.text((x + 4, y + 2), f"{name} · {st.replace('klang', '').replace(' · Bruch', '!')}", fill=(235, 225, 205), font=font(11))
            imgs.append(im)
        imgs[0].save(os.path.join(HERE, f'preview_{slug(kap)}.gif'), save_all=True, append_images=imgs[1:], duration=110, loop=0)
    # Grundzauber-Vorschau
    S = 4; imgs = []
    for t in range(14):
        im = Image.new('RGB', (9*44*S//2 + 20, 140), (30, 26, 48)); d = ImageDraw.Draw(im)
        for i, (el, parts) in enumerate(grund_frames.items()):
            x = 10 + i * 44*S//2
            seq = parts['entstehen'] + parts['flug'] + parts['einschlag']
            f = seq[t]; big = f.resize((f.width*S//2 + f.width//2, f.height*S//2 + f.height//2), Image.NEAREST)
            im.paste(big, (x, 30), big); d.text((x, 8), GRUND[el], fill=(255, 240, 200), font=font(12))
        imgs.append(im)
    imgs[0].save(os.path.join(HERE, 'preview_grundzauber.gif'), save_all=True, append_images=imgs[1:], duration=110, loop=0)
    print(len(book), 'Zauber + 9 Grundzauber')

if __name__ == '__main__':
    main()
