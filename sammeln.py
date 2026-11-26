"""Sammel-Items in der Welt (Seitenansicht): Pflanze/Fundstück + Inventar-Icon.
Aufruf: python3 sammeln.py
Ausgabe: welt/sammeln/<item>.png   Zeilen: idle 6 · ernten 6 · leer 1 · nachwachsen 5   (Zelle 20x32, Boden y=31)
         welt/sammeln/icons_sammeln.png (16x16, Reihenfolge in sammeln.json), welt/sammeln/sammeln.json,
         preview_sammeln.gif
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'welt', 'sammeln')
W, H, GY, MX = 20, 32, 31, 10
INK, WHITE = C('#2b1e33'), C('#ffffff')
LEAF, LEAF_D, LEAF_L = g.LEAF, g.LEAF_D, g.LEAF_L
WOOD, WOOD_D = g.WOOD, g.WOOD_D
DIRT, DIRT_D = C('#7a5a3e'), C('#5a4030')
STONE, STONE_L, STONE_D = C('#7a7488'), C('#9a94a8'), C('#5a5468')
GOLD = C('#e8c050')

def cv(w=W, h=H): im = Image.new('RGBA', (w, h)); return im, ImageDraw.Draw(im)
def dots(d, pts, col, hi=None):
    for x, y in pts:
        d.rectangle([x, y, x + 1, y + 1], fill=col)
        if hi: d.point((x, y), fill=hi)
def busch(d):
    d.ellipse([3, 19, 17, 31], fill=LEAF_D); d.ellipse([4, 17, 15, 28], fill=LEAF); d.ellipse([6, 18, 11, 22], fill=LEAF_L)
def erdhuegel(d): d.ellipse([5, 28, 15, 33], fill=DIRT); d.line([(7, 29), (12, 29)], fill=shade(DIRT, 1.15))

# ---------------------------------------------------------------- Weltobjekte: f(d, voll) ; Icons: i(d)
def beeren(col, hi):
    def obj(d, voll):
        busch(d)
        if voll: dots(d, [(5, 21), (9, 24), (13, 20), (11, 27), (6, 26), (14, 25)], col, hi)
    def icon(d):
        d.line([(8, 1), (8, 5)], fill=WOOD_D); d.ellipse([5, 1, 11, 5], fill=LEAF)
        for x, y in ((3, 6), (8, 6), (5, 10), (10, 10), (7, 13) if False else (8, 11)): d.ellipse([x, y, x + 4, y + 4], fill=col); d.point((x + 1, y + 1), fill=hi)
    return obj, icon
def erdbeeren():
    red = C('#e0443a')
    def obj(d, voll):
        for x in (4, 9, 14): d.polygon([(x, 31), (x - 3, 25), (x + 1, 23), (x + 3, 28)], fill=LEAF)
        d.ellipse([6, 22, 12, 28], fill=LEAF_D)
        if voll:
            for x, y in ((3, 27), (13, 26)):
                d.polygon([(x, y), (x + 4, y), (x + 2, y + 4)], fill=red); d.point((x + 1, y + 1), fill=C('#ffe08a')); d.line([(x, y - 1), (x + 4, y - 1)], fill=LEAF_L)
    def icon(d):
        d.polygon([(2, 4), (13, 4), (11, 10), (7.5, 15), (4, 10)], fill=red); d.polygon([(3, 2), (7, 4), (12, 2), (10, 5), (5, 5)], fill=LEAF)
        for p in ((5, 7), (9, 7), (7, 10), (10, 10)): d.point(p, fill=C('#ffe08a'))
    return obj, icon
def weizen():
    def obj(d, voll):
        for i, x in enumerate((5, 8, 11, 14)):
            top = 12 + (i % 2) * 2
            if voll:
                d.line([(x, 31), (x, top + 4)], fill=C('#c8a040'))
                for k in range(4): d.point((x - 1, top + k), fill=GOLD); d.point((x + 1, top + k + 1), fill=GOLD)
                d.line([(x, top - 1), (x, top + 3)], fill=C('#f0d070'))
                d.line([(x, top - 1), (x + 1, top - 3)], fill=C('#f0d070'))
            else: d.line([(x, 31), (x, 28)], fill=C('#a8883a'))
        d.line([(3, 31), (16, 31)], fill=LEAF_D)
    def icon(d):
        for x, dx in ((5, -2), (8, 0), (11, 2)):
            d.line([(8, 15), (x, 6)], fill=C('#c8a040'))
            for k in range(4): d.point((x - 1 + dx * 0, 2 + k), fill=GOLD); d.point((x + 1, 3 + k), fill=GOLD)
            d.line([(x, 1), (x, 5)], fill=C('#f0d070'))
        d.line([(5, 11), (11, 11)], fill=C('#a83a3a'))
    return obj, icon
def karotte():
    org = C('#ec8a3a')
    def obj(d, voll):
        erdhuegel(d)
        if voll:
            for a in (-25, 0, 25): d.line([(10, 29), (10 + math.sin(math.radians(a)) * 6, 29 - 9)], fill=LEAF)
            d.ellipse([8, 18, 12, 22], fill=LEAF_L); d.rectangle([8, 28, 12, 30], fill=org)
    def icon(d):
        d.polygon([(4, 5), (11, 5), (8, 15)], fill=org); d.line([(5, 8), (7, 8)], fill=shade(org, .8)); d.line([(7, 11), (9, 11)], fill=shade(org, .8))
        for a in (-30, 0, 30): d.line([(7.5, 5), (7.5 + math.sin(math.radians(a)) * 4, 0)], fill=LEAF)
    return obj, icon
def pilz(cap, stem, glow=None):
    def obj(d, voll):
        if voll:
            for x0, s in ((4, 1.0), (11, .75)):
                w = int(8 * s); hh = int(9 * s)
                d.rectangle([x0 + w // 2 - 1, 31 - hh + 2, x0 + w // 2 + 1, 31], fill=stem)
                d.chord([x0, 31 - hh - 2, x0 + w, 31 - hh + 5], 180, 360, fill=cap); d.point((x0 + 2, 31 - hh), fill=WHITE)
        else: d.rectangle([7, 30, 8, 31], fill=stem)
        d.line([(2, 31), (17, 31)], fill=LEAF_D)
    def icon(d):
        d.rectangle([6, 8, 9, 14], fill=stem); d.chord([1, 1, 14, 13], 180, 360, fill=cap); d.point((4, 4), fill=WHITE); d.point((9, 3), fill=WHITE)
    return obj, icon, glow
def kraut(flower, glow=None, petals=5):
    def obj(d, voll):
        d.line([(10, 31), (10, 18)], fill=LEAF_D)
        for y, s in ((28, -1), (25, 1), (22, -1)): d.ellipse([10 + s * 4 - 2, y - 1, 10 + s * 4 + 2, y + 2], fill=LEAF)
        if voll:
            for a in range(petals):
                ang = a / petals * 2 * math.pi; d.ellipse([10 + math.cos(ang) * 2.5 - 1.5, 15 + math.sin(ang) * 2.5 - 1.5, 10 + math.cos(ang) * 2.5 + 1.5, 15 + math.sin(ang) * 2.5 + 1.5], fill=flower)
            d.point((10, 15), fill=C('#ffe08a'))
    def icon(d):
        d.line([(8, 15), (8, 6)], fill=LEAF_D); d.ellipse([3, 9, 7, 12], fill=LEAF); d.ellipse([9, 11, 13, 14], fill=LEAF)
        for a in range(petals):
            ang = a / petals * 2 * math.pi; d.ellipse([8 + math.cos(ang) * 3 - 2, 4 + math.sin(ang) * 3 - 2, 8 + math.cos(ang) * 3 + 2, 4 + math.sin(ang) * 3 + 2], fill=flower)
        d.point((8, 4), fill=C('#ffe08a'))
    return obj, icon, glow
def salbei():
    sage = C('#8aaa8a')
    def obj(d, voll):
        tips = [(3, 22), (6, 17), (10, 15), (14, 17), (17, 22)] if voll else [(7, 26), (13, 26)]
        for x, y in tips: d.line([(10, 31), (x, y + 3)], fill=LEAF_D)
        for x, y in tips: d.ellipse([x - 1, y - 2, x + 1, y + 3], fill=sage); d.point((x, y - 1), fill=mix(sage, WHITE, .3))
    def icon(d):
        for i, (x, y) in enumerate(((4, 3), (8, 1), (11, 4))): d.line([(8, 15), (x, y + 4)], fill=LEAF_D); d.ellipse([x - 3, y, x + 2, y + 7], fill=sage); d.line([(x - 1, y + 2), (x - 1, y + 5)], fill=mix(sage, WHITE, .3))
    return obj, icon
def apfel():
    red = C('#d8403a')
    def obj(d, voll):
        d.rectangle([9, 18, 11, 31], fill=WOOD); d.ellipse([2, 3, 18, 21], fill=LEAF_D); d.ellipse([3, 3, 15, 17], fill=LEAF); d.ellipse([5, 5, 10, 9], fill=LEAF_L)
        if voll: dots(d, [(5, 12), (12, 9), (13, 15), (8, 16)], red, C('#ff9a8a'))
    def icon(d):
        d.ellipse([2, 4, 13, 14], fill=red); d.point((5, 7), fill=WHITE); d.line([(8, 1), (8, 4)], fill=WOOD_D); d.ellipse([8, 1, 12, 4], fill=LEAF)
    return obj, icon
def baumwolle():
    def obj(d, voll):
        for x, top in ((6, 16), (10, 13), (14, 17)):
            d.line([(x, 31), (x, top)], fill=C('#6a8a4a'))
            if voll: d.ellipse([x - 2, top - 3, x + 2, top + 1], fill=C('#f4f0e8')); d.point((x - 1, top - 2), fill=WHITE)
            else: d.point((x, top - 1), fill=C('#8a6a3a'))
    def icon(d):
        for x, y in ((3, 5), (8, 3), (8, 8), (12, 6)): d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=C('#f4f0e8'))
        d.line([(8, 11), (8, 15)], fill=C('#6a8a4a'))
    return obj, icon
def ast():
    def obj(d, voll):
        if voll: d.line([(3, 30), (16, 28)], fill=WOOD, width=2); d.line([(11, 29), (14, 25)], fill=WOOD); d.point((13, 25), fill=LEAF)
    def icon(d): d.line([(2, 13), (13, 3)], fill=WOOD, width=2); d.line([(8, 8), (11, 10)], fill=WOOD); d.ellipse([11, 9, 14, 12], fill=LEAF)
    return obj, icon
def stein():
    def obj(d, voll):
        if voll: d.polygon([(5, 31), (6, 27), (10, 25), (14, 27), (15, 31)], fill=STONE); d.line([(7, 27), (10, 26)], fill=STONE_L)
    def icon(d): d.polygon([(2, 13), (3, 6), (8, 3), (13, 6), (14, 13)], fill=STONE); d.line([(4, 6), (8, 4)], fill=STONE_L); d.line([(9, 8), (11, 11)], fill=STONE_D)
    return obj, icon
def erzader(col, name):
    def obj(d, voll):
        d.polygon([(1, 31), (2, 22), (7, 16), (13, 15), (18, 21), (19, 31)], fill=STONE); d.line([(3, 22), (7, 17)], fill=STONE_L); d.line([(12, 22), (16, 27)], fill=STONE_D)
        if voll:
            for x, y in ((6, 21), (11, 19), (14, 25), (8, 27)): d.rectangle([x, y, x + 1, y + 1], fill=col); d.point((x, y), fill=mix(col, WHITE, .5))
        else:
            for x, y in ((6, 21), (11, 19)): d.point((x, y), fill=STONE_D)
    def icon(d):
        d.polygon([(2, 12), (3, 6), (7, 3), (12, 4), (14, 9), (12, 14), (5, 14)], fill=STONE)
        for x, y in ((5, 7), (9, 10), (10, 5)): d.rectangle([x, y, x + 1, y + 1], fill=col); d.point((x, y), fill=mix(col, WHITE, .5))
    return obj, icon
def kristall():
    c1, c2 = C('#8a6ae0'), C('#c8b0ff')
    def obj(d, voll):
        d.ellipse([3, 28, 17, 33], fill=STONE_D)
        parts = ((6, 9, c1), (10, 15, c2), (14, 8, c1)) if voll else ((10, 3, c1),)
        for x0, hh, c in parts:
            d.polygon([(x0 - 2, 31), (x0 + 2, 31), (x0 + 1, 31 - hh), (x0 - 1, 31 - hh)], fill=c); d.line([(x0 - 1, 30), (x0 - 1, 32 - hh)], fill=WHITE)
    def icon(d):
        for x0, hh, c in ((4, 9, c1), (8, 13, c2), (12, 8, c1)):
            d.polygon([(x0 - 2, 15), (x0 + 2, 15), (x0 + 1, 15 - hh), (x0 - 1, 15 - hh)], fill=c); d.line([(x0 - 1, 14), (x0 - 1, 16 - hh)], fill=WHITE)
    return obj, icon, C('#d8c8ff')
def muschel():
    sh = C('#f0c8b0')
    def obj(d, voll):
        d.ellipse([1, 29, 19, 33], fill=C('#e8d8a8'))
        if voll:
            d.chord([6, 23, 15, 33], 180, 360, fill=sh); d.rectangle([9, 27, 12, 29], fill=sh)
            for x in (8, 10, 12): d.line([(10, 28), (x, 24)], fill=shade(sh, .8))
    def icon(d):
        d.chord([1, 2, 14, 18], 180, 360, fill=sh); d.rectangle([5, 9, 10, 12], fill=sh)
        for x in (3, 6, 9, 12): d.line([(7.5, 10), (x, 3)], fill=shade(sh, .8))
    return obj, icon
def feder():
    fc = C('#e8e0f0')
    def obj(d, voll):
        if voll: d.line([(5, 30), (15, 25)], fill=C('#a89aa8')); d.polygon([(7, 28), (14, 23), (16, 25), (9, 30)], fill=fc); d.point((15, 24), fill=C('#8ad0ff'))
    def icon(d):
        d.line([(2, 14), (13, 2)], fill=C('#a89aa8')); d.polygon([(4, 11), (12, 2), (14, 4), (6, 13)], fill=fc); d.polygon([(11, 3), (13, 2), (14, 4)], fill=C('#8ad0ff'))
    return obj, icon
def nest():
    egg = C('#f0ead8')
    def obj(d, voll):
        if voll:
            for x in (7, 11): d.ellipse([x - 2, 23, x + 2, 29], fill=egg); d.point((x - 1, 25), fill=WHITE)
            d.point((12, 26), fill=C('#a8c8e8'))
        d.chord([2, 24, 18, 34], 0, 180, fill=C('#a8804a'))
        for x in range(3, 17, 3): d.line([(x, 29), (x + 2, 31)], fill=C('#7a5a3a'))
    def icon(d):
        d.ellipse([4, 1, 12, 13], fill=egg); d.point((6, 4), fill=WHITE); d.point((9, 8), fill=C('#a8c8e8')); d.point((7, 10), fill=C('#a8c8e8'))
    return obj, icon
def honig():
    def obj(d, voll):
        d.rectangle([8, 22, 12, 31], fill=WOOD_D)  # Pfahl
        d.ellipse([4, 9, 16, 23], fill=C('#d8a850'));
        for y in (12, 15, 18): d.line([(5, y), (15, y)], fill=C('#b8883a'))
        d.ellipse([9, 18, 11, 20], fill=INK)
        if voll: d.ellipse([12, 20, 14, 23], fill=C('#f0b830'))  # Honigtropfen
    def icon(d):
        d.rectangle([3, 5, 12, 14], fill=C('#c8a060')); d.rectangle([3, 7, 12, 12], fill=C('#f0b830')); d.rectangle([2, 3, 13, 5], fill=C('#a83a3a')); d.point((5, 8), fill=WHITE)
    return obj, icon

def mk(o):
    return (o[0], o[1], o[2] if len(o) > 2 else None)
ITEMS = {
    'beeren_rot': (mk(beeren(C('#d8403a'), C('#ff9a8a'))), 'busch'), 'blaubeeren': (mk(beeren(C('#4a5ac8'), C('#a8b8ff'))), 'busch'),
    'erdbeeren': (mk(erdbeeren()), 'pflanze'), 'weizen': (mk(weizen()), 'feld'), 'karotte': (mk(karotte()), 'ausgraben'),
    'pilz': (mk(pilz(C('#c84a4a'), C('#e8dcc0'))), 'pflanze'), 'leuchtpilz': (mk(pilz(C('#6ab8e8'), C('#d8d0e0'), C('#bfe8ff'))), 'pflanze'),
    'heilkraut': (mk(kraut(C('#e888a8'))), 'pflanze'), 'manablume': (mk(kraut(C('#6a9aff'), C('#bfe0ff'), 6)), 'pflanze'),
    'mondblume': (mk(kraut(C('#f4f0ff'), C('#fff8d0'), 8)), 'pflanze_nacht'), 'salbei': (mk(salbei()), 'pflanze'),
    'apfel': (mk(apfel()), 'baum'), 'baumwolle': (mk(baumwolle()), 'feld'), 'ast': (mk(ast()), 'aufheben'), 'feuerstein': (mk(stein()), 'aufheben'),
    'eisenerz': (mk(erzader(C('#c8a890'), 'eisen')), 'abbauen'), 'golderz': (mk(erzader(C('#f0c850'), 'gold')), 'abbauen'),
    'kristall': (mk(kristall()), 'abbauen'), 'muschel': (mk(muschel()), 'aufheben'), 'feder': (mk(feder()), 'aufheben'),
    'eier': (mk(nest()), 'nest'), 'honig': (mk(honig()), 'bienenstock'),
}
SWAY = {'busch': .6, 'pflanze': 1.0, 'pflanze_nacht': 1.0, 'feld': 1.6, 'baum': .5, 'ausgraben': .8}

# ---------------------------------------------------------------- Rendern
def raw(obj, voll):
    im, d = cv(); obj(d, voll); return im
def sway(im, t, amp):
    if not amp: return im
    out = Image.new('RGBA', im.size); src = im.load(); px = out.load()
    for y in range(H):
        k = max(0, (GY - y) / 18); off = int(round(math.sin(t / 6 * 2 * math.pi) * amp * k))
        for x in range(W):
            if src[x, y][3] and 0 <= x + off < W: px[x + off, y] = src[x, y]
    return out
def glowify(im, col, strength):
    if not col: return im
    a = im.getchannel('A'); halo = Image.new('RGBA', im.size)
    hp = halo.load(); ap = a.load()
    for y in range(H):
        for x in range(W):
            if ap[x, y]: continue
            n1 = any(0 <= x + dx < W and 0 <= y + dy < H and ap[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            n2 = any(0 <= x + dx < W and 0 <= y + dy < H and ap[x + dx, y + dy] for dx in (-2, 0, 2) for dy in (-2, 0, 2))
            if n1: hp[x, y] = col[:3] + (int(110 * strength),)
            elif n2 and (x + y) % 2 == 0: hp[x, y] = col[:3] + (int(70 * strength),)
    halo.alpha_composite(im); return halo
def icon_img(icon):
    im = Image.new('RGBA', (16, 16)); icon(ImageDraw.Draw(im)); return g.outline(im)
def sparkle(im, x, y, k, col=WHITE):
    d = ImageDraw.Draw(im); r = 1 + k
    d.point((x, y), fill=col); d.point((x - r, y), fill=col); d.point((x + r, y), fill=col); d.point((x, y - r), fill=col); d.point((x, y + r), fill=col)

def item_frames(name):
    (obj, icon, glow), kind = ITEMS[name]; amp = SWAY.get(kind, 0)
    full, empty = g.outline(raw(obj, True)), g.outline(raw(obj, False))
    ic = icon_img(icon)
    idle = []
    for t in range(6):
        f = sway(full, t, amp)
        if glow: f = glowify(f, glow, .6 + .4 * math.sin(t / 6 * 2 * math.pi))
        if kind in ('aufheben', 'abbauen') and t == 3: sparkle(f, 14, 24 if kind == 'aufheben' else 17, 0)  # Glitzern zum Finden
        idle.append(f)
    harvest = []
    for t in range(6):
        base = (full if t == 0 else empty).copy()
        if kind == 'abbauen' and t < 2: base = Image.new('RGBA', (W, H)); base.alpha_composite(full, ((-1) ** t, 0))
        f = base
        if t >= 1:
            s = [12, 11, 10, 9, 7][t - 1]; it = ic.resize((s, s), Image.NEAREST)
            y = [16, 9, 5, 3, 2][t - 1]
            layer = Image.new('RGBA', (W, H)); layer.alpha_composite(it, (MX - s // 2, y))
            if t == 5: layer.putalpha(layer.getchannel('A').point(lambda v: v // 2))
            f = base.copy(); f.alpha_composite(layer)
            if t in (1, 3): sparkle(f, MX + 6, y + 2, 1, C('#fff0a0'))
        if t == 1 and kind in ('abbauen',):
            d = ImageDraw.Draw(f)
            for k in range(4): d.point((MX - 6 + k * 4, 18 - k % 2 * 3), fill=STONE_L)
        if t == 1 and kind in ('busch', 'feld', 'pflanze', 'pflanze_nacht', 'baum'):
            d = ImageDraw.Draw(f)
            for k in range(3): d.point((MX - 5 + k * 5, 18 + k), fill=LEAF_L)
        harvest.append(f)
    leer = [empty]
    regrow = []
    for t in range(5):
        k = (t + 1) / 5; f = empty.copy()
        cut = int(GY - (GY - 2) * k)
        part = full.crop((0, cut, W, H)); f.alpha_composite(part, (0, cut))
        if t == 4: sparkle(f, MX, 14, 0, C('#fff0a0'))
        regrow.append(f)
    return {'idle': idle, 'ernten': harvest, 'leer': leer, 'nachwachsen': regrow}, ic

ORDER = [('idle', 6), ('ernten', 6), ('leer', 1), ('nachwachsen', 5)]

def main():
    os.makedirs(OUT, exist_ok=True); allf = {}; icons = []; meta = {}
    for name in ITEMS:
        F, ic = item_frames(name); allf[name] = F; icons.append(ic)
        s = Image.new('RGBA', (W * 6, H * len(ORDER)))
        for r, (a, n) in enumerate(ORDER):
            for c, f in enumerate(F[a]): s.alpha_composite(f, (c * W, r * H))
        s.save(os.path.join(OUT, f'{name}.png'))
        meta[name] = {'art': ITEMS[name][1], 'icon_index': len(icons) - 1, 'leuchtet': ITEMS[name][0][2] is not None}
    sh = Image.new('RGBA', (16 * len(icons), 16))
    for i, ic in enumerate(icons): sh.alpha_composite(ic, (i * 16, 0))
    sh.save(os.path.join(OUT, 'icons_sammeln.png'))
    json.dump({'zelle': [W, H], 'boden_y': GY, 'zeilen': {a: n for a, n in ORDER}, 'fps': 8, 'icon_groesse': 16,
               'hinweis': 'idle loopen → bei Interaktion ernten einmal → leer bleibt bis zum Nachwachsen (Zeit im Spiel festlegen) → nachwachsen einmal → idle. '
                          'art: busch/pflanze/feld/baum = pflücken, ausgraben, aufheben, abbauen (Werkzeug), nest, bienenstock; pflanze_nacht nur nachts sichtbar/leuchtend.',
               'items': meta}, open(os.path.join(OUT, 'sammeln.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(allf, icons)

def preview(allf, icons):
    names = list(allf); Z = 3; cols = 11; cw, chh = W * Z + 6, H * Z + 16 * 2 + 18
    rows = math.ceil(len(names) / cols); seq = [('idle', i) for i in range(6)] * 2 + [('ernten', i) for i in range(6)] + [('leer', 0)] * 4 + [('nachwachsen', i) for i in range(5)]
    out = []
    for a, i in seq:
        im = Image.new('RGB', (cols * cw + 6, rows * chh + 6), (42, 36, 69)); d = ImageDraw.Draw(im)
        for k, n in enumerate(names):
            x, y = 6 + (k % cols) * cw, 6 + (k // cols) * chh
            d.rectangle([x, y, x + W * Z - 1, y + H * Z - 1], fill=(74, 62, 88)); d.rectangle([x, y + GY * Z + 2, x + W * Z - 1, y + H * Z - 1], fill=(58, 80, 58))
            f = allf[n][a][min(i, len(allf[n][a]) - 1)].resize((W * Z, H * Z), Image.NEAREST); im.paste(f, (x, y), f)
            ic = icons[k].resize((32, 32), Image.NEAREST); im.paste(ic, (x + 14, y + H * Z + 2), ic)
            d.text((x, y + H * Z + 36), n.replace('_', ' ')[:11], fill=(230, 220, 200), font=g.font(10))
        out.append(im)
    out[0].save(os.path.join(g.BASE, 'preview_sammeln.gif'), save_all=True, append_images=out[1:], duration=140, loop=0)

if __name__ == '__main__':
    main()
