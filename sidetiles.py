"""Tilesets & Hintergründe für ein Seitenansicht-Spiel (Plattformer, 16x16).
Aufruf: python3 sidetiles.py
Ausgabe: level/terrain_<gebiet>.png   – fester Block, Ecken-Autotiling (4x4, Index = NW*1 + NE*2 + SW*4 + SE*8, Bit = fest)
         level/rueckwand_<gebiet>.png – Hintergrund-Wand ohne Kollision (4 Varianten)
         level/schraege_<gebiet>.png  – 45°-Schrägen: aufwärts, abwärts, Füll-Kachel darunter
         level/plattformen.png, level/leiter.png, level/stacheln.png
         level/parallax/<szene>_<ebene>.png (320x180, waagrecht kachelbar)
         level/level.json, preview_level_tiles.png, preview_level_szene.gif
"""
import os, math, random, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

T = 16
OUT = os.path.join(g.BASE, 'level')
WHITE = (255, 255, 255, 255)

def h(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535

# ---------------------------------------------------------------- Gebiete
BIOMES = {
    'wiese': dict(fill=C('#6a4a32'), fill_d=C('#54382a'), fill_l=C('#7e5a3e'), top=C('#5a8a4a'), top_l=C('#7aae5a'), top_d=C('#3e6a36'),
                  under=C('#3e2a20'), rim=C('#4a3426'), deco='steine', topkind='gras', back=C('#3a2c26')),
    'fels': dict(fill=C('#5a5466'), fill_d=C('#46404f'), fill_l=C('#6e687a'), top=C('#5a7a4a'), top_l=C('#7a9a5a'), top_d=C('#3e5a36'),
                 under=C('#2e2a36'), rim=C('#3a3446'), deco='risse', topkind='moos', back=C('#2a2632')),
    'schnee': dict(fill=C('#6a7a90'), fill_d=C('#56647a'), fill_l=C('#8494aa'), top=C('#f0f4fa'), top_l=WHITE, top_d=C('#c8d8e8'),
                   under=C('#3e4a5e'), rim=C('#4a5870'), deco='eis', topkind='schnee', back=C('#2e3646')),
    'dungeon_physisch': dict(fill=C('#5a5468'), fill_d=C('#3e384c'), fill_l=C('#6e687c'), top=C('#7a7488'), top_l=C('#948ea2'), top_d=C('#5a5468'),
                             under=C('#2a2432'), rim=C('#36304a'), deco='ziegel', topkind='kante', back=C('#26222e')),
    'dungeon_dorn': dict(fill=C('#3e3a3a'), fill_d=C('#262222'), fill_l=C('#504a48'), top=C('#3a4a2a'), top_l=C('#5a6e3a'), top_d=C('#22301c'),
                         under=C('#1a1616'), rim=C('#262222'), deco='ziegel', topkind='dornen', back=C('#1c1a1a')),
    'dungeon_blut': dict(fill=C('#5a3438'), fill_d=C('#3a1e22'), fill_l=C('#6e4448'), top=C('#8a1e2a'), top_l=C('#b8283a'), top_d=C('#5a1420'),
                         under=C('#2a0e14'), rim=C('#3a1e22'), deco='ziegel', topkind='blut', back=C('#241014')),
    'dungeon_erinnerung': dict(fill=C('#4a4a78'), fill_d=C('#30305a'), fill_l=C('#5e5e8e'), top=C('#a8b8ff'), top_l=C('#e0e8ff'), top_d=C('#6a6ab0'),
                               under=C('#1a1a3a'), rim=C('#30305a'), deco='ziegel', topkind='glyphen', back=C('#1c1c3a')),
}

def fill_px(b, x, y, kind):
    """Innenfüllung eines festen Blocks (nahtlos kachelbar)."""
    B = BIOMES[b]
    if B['deco'] == 'ziegel':
        bx, by = (x + (4 if (y // 8) % 2 else 0)) % 8, y % 8
        if bx == 7 or by == 7: return B['fill_d']
        c = B['fill'] if h((x + (4 if (y // 8) % 2 else 0)) // 8, y // 8, 3) > .5 else shade(B['fill'], .92)
        if bx == 0 or by == 0: c = B['fill_l']
        return c
    v = h(x, y, 1)
    if B['deco'] == 'steine' and h(x // 3, y // 3, 2) > .93: return C('#8a8296') if v > .4 else C('#6a6276')
    if B['deco'] == 'risse' and (x * 3 + y * 5) % 17 == 0: return B['fill_d']
    if B['deco'] == 'eis' and (x - y) % 9 == 0 and h(x, y, 4) > .5: return B['fill_l']
    if v < .1: return B['fill_d']
    if v > .9: return B['fill_l']
    return B['fill']

def solid_mask(bits, x, y, rough=.1):
    nw, ne, sw, se = bits & 1, (bits >> 1) & 1, (bits >> 2) & 1, (bits >> 3) & 1
    u, v = (x + .5) / T, (y + .5) / T
    val = nw * (1 - u) * (1 - v) + ne * u * (1 - v) + sw * (1 - u) * v + se * u * v
    return val + (h(x, y, 21) - .5) * rough > .5

def terrain_tile(b, bits, t=0):
    B = BIOMES[b]
    tile = Image.new('RGBA', (T, T)); p = tile.load()
    m = [[solid_mask(bits, x, y) for x in range(T)] for y in range(T)]
    S = lambda x, y: m[y][x] if 0 <= x < T and 0 <= y < T else None
    for y in range(T):
        for x in range(T):
            if not m[y][x]: continue
            # Abstand zur Luft nach oben / unten / seitlich
            up = next((k for k in range(1, 5) if S(x, y - k) is False), None)
            down = next((k for k in range(1, 3) if S(x, y + k) is False), None)
            side = any(S(x + dx, y) is False for dx in (-1, 1))
            c = fill_px(b, x, y, B)
            if side: c = B['rim']
            if down == 1: c = B['under']
            if up is not None:
                if up == 1: c = B['top_l']
                elif up <= 3: c = B['top'] if B['topkind'] != 'kante' else B['top_d']
                elif up == 4 and B['topkind'] in ('gras', 'moos', 'schnee'): c = B['top_d'] if (x + y) % 2 else c
            p[x, y] = c
    # Oberflächen-Details in die Luft hinein (Grashalme, Dornen, Schnee, Glyphen) und Wurzeln/Tropfen unten
    for x in range(T):
        tops = [y for y in range(T) if m[y][x] and (y == 0 or not m[y - 1][x])]
        for y in tops:
            if y == 0: continue
            kind = B['topkind']
            if kind == 'gras' and h(x, y, 5) > .55:
                hh = 1 + int(h(x, y, 6) * 3)
                for k in range(1, hh + 1):
                    if y - k >= 0: p[x, y - k] = B['top_l'] if k == hh else B['top']
            elif kind == 'moos' and h(x, y, 5) > .7 and y >= 1: p[x, y - 1] = B['top']
            elif kind == 'schnee' and h(x, y, 5) > .6 and y >= 1: p[x, y - 1] = WHITE
            elif kind == 'dornen' and x % 4 == 1 and y >= 3:
                p[x, y - 1] = B['top']; p[x, y - 2] = B['top_l'] if h(x, y, 7) > .5 else B['top']; p[x, y - 3] = C('#c8b898')
            elif kind == 'blut' and h(x, y, 8) > .8 and y >= 1: p[x, y - 1] = B['top']
            elif kind == 'glyphen' and (x + t) % 6 == 0: p[x, y] = WHITE
        bottoms = [y for y in range(T) if m[y][x] and (y == T - 1 or not m[y + 1][x])]
        for y in bottoms:
            if y == T - 1: continue
            if B['topkind'] in ('gras', 'moos') and h(x, y, 9) > .82:
                for k in range(1, 3 + int(h(x, y, 10) * 3)):
                    if y + k < T: p[x, y + k] = B['under'] if k % 2 else B['rim']
            elif B['topkind'] == 'blut' and h(x, y, 11) > .85 and y + 2 < T:
                p[x, y + 1] = B['top']; p[x, y + 2] = B['top_l']
            elif B['topkind'] == 'schnee' and h(x, y, 12) > .85 and y + 2 < T:
                p[x, y + 1] = C('#c8e4f8'); p[x, y + 2] = C('#e8f6ff')
    return tile

def terrain_sheet(b, t=0):
    sh = Image.new('RGBA', (T * 4, T * 4))
    for idx in range(16): sh.paste(terrain_tile(b, idx, t), ((idx % 4) * T, (idx // 4) * T))
    return sh

def rueckwand(b):
    B = BIOMES[b]; sh = Image.new('RGBA', (T * 4, T))
    for v in range(4):
        tile = Image.new('RGBA', (T, T)); p = tile.load()
        for y in range(T):
            for x in range(T):
                c = mix(fill_px(b, x, y, B), B['back'], .62)
                if v == 1 and (x * 7 + y * 3) % 23 == 0: c = shade(c, .7)
                if v == 2 and 5 <= x <= 10 and 4 <= y <= 11: c = shade(B['back'], .7) if not (x in (5, 10) or y in (4, 11)) else mix(B['fill_l'], B['back'], .5)
                if v == 3 and x in (7, 8) and h(x, y, 33) > .3: c = mix(C('#5a5e6e'), B['back'], .4)
                p[x, y] = c
        sh.paste(tile, (v * T, 0))
    return sh

def schraege(b):
    """[aufwärts (links unten -> rechts oben), abwärts, Füllkachel]"""
    sh = Image.new('RGBA', (T * 3, T))
    full = terrain_tile(b, 15)
    for v in range(2):
        tile = Image.new('RGBA', (T, T)); p = tile.load(); B = BIOMES[b]
        for y in range(T):
            for x in range(T):
                edge = (T - 1 - x) if v == 0 else x
                if y > edge:
                    d = y - edge
                    c = fill_px(b, x, y, B)
                    if d == 1: c = B['top_l']
                    elif d <= 3: c = B['top'] if B['topkind'] != 'kante' else B['top_d']
                    p[x, y] = c
                elif y == edge and B['topkind'] == 'gras' and h(x, y, 5) > .6 and y >= 1:
                    p[x, y - 1] = B['top']
        sh.paste(tile, (v * T, 0))
    sh.paste(full, (2 * T, 0))
    return sh

def plattformen():
    """Durchspringbare Plattformen: Holz (links, mitte, rechts), Stein (links, mitte, rechts), Wolke, Ast."""
    sh = Image.new('RGBA', (T * 8, T))
    d = ImageDraw.Draw(sh)
    for i in range(3):
        x0 = i * T
        d.rectangle([x0, 0, x0 + 15, 3], fill=g.WOOD); d.line([(x0, 0), (x0 + 15, 0)], fill=g.WOOD_L); d.line([(x0, 4), (x0 + 15, 4)], fill=g.WOOD_D)
        for k in (4, 11): d.point((x0 + k, 1), fill=C('#5a5e6e'))
        if i == 0: d.line([(x0 + 2, 5), (x0 + 6, 12)], fill=g.WOOD_D, width=2)
        if i == 2: d.line([(x0 + 13, 5), (x0 + 9, 12)], fill=g.WOOD_D, width=2)
    for i in range(3):
        x0 = (3 + i) * T
        d.rectangle([x0, 0, x0 + 15, 5], fill=C('#6e687a')); d.line([(x0, 0), (x0 + 15, 0)], fill=C('#948ea2')); d.line([(x0, 5), (x0 + 15, 5)], fill=C('#46404f'))
        d.line([(x0 + 8, 1), (x0 + 8, 4)], fill=C('#46404f'))
        if i == 0: d.polygon([(x0, 6), (x0 + 8, 6), (x0, 12)], fill=C('#5a5466'))
        if i == 2: d.polygon([(x0 + 15, 6), (x0 + 7, 6), (x0 + 15, 12)], fill=C('#5a5466'))
    x0 = 6 * T
    for k in range(4): d.ellipse([x0 + k * 3, 1 + (k % 2), x0 + k * 3 + 7, 7 + (k % 2)], fill=C('#e8eef8'))
    d.line([(x0 + 1, 7), (x0 + 14, 7)], fill=C('#b8c8e0'))
    x0 = 7 * T
    d.line([(x0, 3), (x0 + 15, 2)], fill=g.WOOD, width=3); d.line([(x0, 5), (x0 + 15, 4)], fill=g.WOOD_D)
    for k in (3, 9, 13): d.ellipse([x0 + k - 2, 0, x0 + k + 2, 2], fill=g.LEAF)
    return g.outline(sh)

def leiter():
    sh = Image.new('RGBA', (T * 3, T)); d = ImageDraw.Draw(sh)
    d.line([(3, 0), (3, 15)], fill=g.WOOD, width=2); d.line([(12, 0), (12, 15)], fill=g.WOOD, width=2)
    for y in (3, 11): d.line([(3, y), (12, y)], fill=g.WOOD_L, width=2)
    for y in range(T): d.point((7 + int(math.sin(y * .8) * 1), y), fill=C('#c8a870')); d.point((8 + int(math.sin(y * .8) * 1), y), fill=C('#a8885a'))
    for y in range(0, T, 4): d.ellipse([T * 2 + 5, y, T * 2 + 10, y + 3], outline=C('#7a7e8e'))
    return g.outline(sh)

def stacheln():
    """Stacheln: Stahl, Knochen, Dornen, Kristall (je eine Kachel, Spitzen nach oben)."""
    sh = Image.new('RGBA', (T * 4, T)); d = ImageDraw.Draw(sh)
    kinds = [(C('#b8bccc'), C('#eceef4'), C('#5a5e6e')), (C('#e8e0d0'), WHITE, C('#a89a8a')),
             (C('#3a4a2a'), C('#5a6e3a'), C('#22301c')), (C('#8ad0e8'), C('#e0f8ff'), C('#4a7aa8'))]
    for i, (c, l, b) in enumerate(kinds):
        x0 = i * T
        d.rectangle([x0, 12, x0 + 15, 15], fill=b)
        for k in range(4):
            sx = x0 + k * 4
            d.polygon([(sx, 12), (sx + 3, 12), (sx + 1.5, 3 + (k % 2) * 2)], fill=c); d.line([(sx + 1, 11), (sx + 1, 5 + (k % 2) * 2)], fill=l)
    return g.outline(sh)

# ---------------------------------------------------------------- Parallax-Hintergründe (320x180)
PW, PH = 320, 180
def ridge(seed, base, amp, freq):
    rng = random.Random(seed); ph = [rng.random() * 6.28 for _ in range(3)]
    def f(x):
        return base + amp * (math.sin(x * freq * 2*math.pi / PW + ph[0]) * .5 + math.sin(x * freq * 2 * 2*math.pi / PW + ph[1]) * .3
                              + math.sin(x * freq * 5 * 2*math.pi / PW + ph[2]) * .2)
    return f

def layer_fill(f, col, dither_top=None):
    im = Image.new('RGBA', (PW, PH)); p = im.load()
    for x in range(PW):
        top = int(f(x))
        for y in range(max(0, top), PH):
            p[x, y] = col
        if dither_top:
            for y in range(max(0, top - 3), max(0, top)):
                if (x + y) % 2 == 0: p[x, y] = dither_top
    return im

def sky(top, bottom, stars=False, moon=None):
    im = Image.new('RGBA', (PW, PH)); p = im.load()
    for y in range(PH):
        c = mix(top, bottom, y / PH)
        for x in range(PW):
            cc = c
            if 0 < y % 12 < 2 and (x + y) % 2 == 0: cc = mix(c, bottom, .3)
            p[x, y] = cc
    if stars:
        rng = random.Random(3)
        for _ in range(60): p[rng.randrange(PW), rng.randrange(PH // 2)] = (255, 255, 255, 255) if rng.random() > .3 else (200, 200, 230, 255)
    if moon:
        d = ImageDraw.Draw(im); d.ellipse([230, 20, 254, 44], fill=moon); d.ellipse([236, 26, 241, 31], fill=shade(moon, .85))
    return im

def trees(seed, y0, col, dark, n=14, h_=(28, 46)):
    im = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(im); rng = random.Random(seed)
    for i in range(n):
        x = (i * PW / n + rng.uniform(-6, 6)) % PW; hh = rng.uniform(*h_)
        for dx in (-PW, 0, PW):
            if rng.random() < .5:
                d.polygon([(x + dx - 7, y0), (x + dx + 7, y0), (x + dx, y0 - hh)], fill=col); d.line([(x + dx, y0 - hh), (x + dx + 6, y0)], fill=dark)
            else:
                d.ellipse([x + dx - 11, y0 - hh, x + dx + 11, y0 - hh + 22], fill=col); d.rectangle([x + dx - 1, y0 - hh + 18, x + dx + 1, y0], fill=dark)
    d.rectangle([0, y0, PW, PH], fill=col)
    return im

def scenes():
    S = {}
    # Dorf (Tag + Nacht, angelehnt an den Screenshot)
    S['dorf_tag'] = [('himmel', sky(C('#7ab0e0'), C('#c8e0f0'))),
                     ('berge', layer_fill(ridge(1, 95, 22, 1.5), C('#8a9ac0'), C('#a8b8d8'))),
                     ('huegel', layer_fill(ridge(2, 125, 12, 2), C('#6a9a7a'))),
                     ('wald', trees(5, 150, C('#4a7a4a'), C('#3a6a3a')))]
    S['dorf_nacht'] = [('himmel', sky(C('#1e1a3a'), C('#3a3058'), stars=True, moon=C('#f4e6b0'))),
                       ('berge', layer_fill(ridge(1, 95, 22, 1.5), C('#5a3d6b'), C('#6a4a7a'))),
                       ('huegel', layer_fill(ridge(2, 125, 12, 2), C('#3a3558'))),
                       ('wald', trees(5, 150, C('#2a3a3a'), C('#1e2a2a')))]
    # Höhle
    cave = [('fern', sky(C('#16121e'), C('#241e2e'))),
            ('felsen', layer_fill(ridge(7, 120, 25, 2.5), C('#2e2a36'))),
            ('stalaktiten', None), ('kristalle', None)]
    st = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(st); rng = random.Random(8)
    d.rectangle([0, 0, PW, 14], fill=C('#3a3446'))
    for i in range(22):
        x = i * PW / 22 + rng.uniform(-4, 4); L = rng.uniform(14, 50)
        d.polygon([(x - 5, 14), (x + 5, 14), (x, 14 + L)], fill=C('#3a3446')); d.line([(x, 14), (x, 14 + L - 2)], fill=C('#4a4458'))
    cave[2] = ('stalaktiten', st)
    kr = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(kr)
    d.rectangle([0, 160, PW, PH], fill=C('#2a2632'))
    for i in range(9):
        x = i * PW / 9 + 15
        d.polygon([(x - 5, 160), (x + 5, 160), (x + 1, 140), (x - 2, 136)], fill=C('#5a4aa8')); d.line([(x - 1, 158), (x - 2, 140)], fill=C('#b8a0ff'))
    cave[3] = ('kristalle', kr)
    S['hoehle'] = cave
    # Dungeons
    def dungeon_scene(base, accent, arch):
        bg = sky(shade(base, .5), shade(base, .8))
        arches = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(arches)
        for i in range(5):
            x = i * 64
            d.rectangle([x, 30, x + 63, PH], fill=shade(base, .9))
            d.ellipse([x + 12, 40, x + 52, 80], fill=shade(base, .6)); d.rectangle([x + 12, 60, x + 52, PH], fill=shade(base, .6))
        pillars = Image.new('RGBA', (PW, PH)); d = ImageDraw.Draw(pillars)
        for i in range(4):
            x = i * 80 + 30
            d.rectangle([x, 0, x + 14, PH], fill=shade(base, 1.1)); d.rectangle([x - 3, 0, x + 17, 8], fill=shade(base, 1.25)); d.rectangle([x - 3, PH - 10, x + 17, PH], fill=shade(base, 1.25))
            if arch == 'dorn':
                for k in range(6): d.line([(x + 14, 20 + k * 25), (x + 24, 14 + k * 25)], fill=accent, width=2)
            elif arch == 'blut':
                for k in range(3): d.line([(x + 4 + k * 4, 8), (x + 4 + k * 4, 30 + k * 12)], fill=accent, width=1)
            elif arch == 'erinnerung':
                for k in range(5): d.rectangle([x + 40 + k * 7, 40 + (k * 17) % 60, x + 44 + k * 7, 44 + (k * 17) % 60], fill=accent)
            else:
                d.line([(x + 7, 8), (x + 7, 50)], fill=C('#5a5e6e')); d.ellipse([x + 3, 48, x + 11, 56], outline=C('#5a5e6e'))
        return [('hintergrund', bg), ('boegen', arches), ('saeulen', pillars)]
    S['dungeon_physisch'] = dungeon_scene(C('#3e384c'), C('#7a7488'), 'physisch')
    S['dungeon_dorn'] = dungeon_scene(C('#2a2626'), C('#5a6e3a'), 'dorn')
    S['dungeon_blut'] = dungeon_scene(C('#3a1e22'), C('#8a1e2a'), 'blut')
    S['dungeon_erinnerung'] = dungeon_scene(C('#2a2a50'), C('#a8b8ff'), 'erinnerung')
    return S

# ---------------------------------------------------------------- Testszene
LEVEL = [
    '..................................................',
    '..................................................',
    '..................................................',
    '..................................................',
    '...........................====...................',
    '..................................................',
    '.................####.................=====.......',
    '.......====......####.............................',
    '................######...........#######..........',
    '..........H.....######.........../#######\\........',
    '..........H..../#######.........###########.......',
    '#########^^^^##########\\.......##############.....',
    '#######################################.....######',
]
def tile_of(sheet, idx): return sheet.crop(((idx % 4) * T, (idx // 4) * T, (idx % 4 + 1) * T, (idx // 4 + 1) * T))

def render_level(t, biome, scene_layers, cam):
    rows = [r.ljust(50, '.') for r in LEVEL]
    H, W = len(rows), len(rows[0])
    def solid(x, y):
        if x < 0 or x >= W: return True if 0 <= y < H and rows[y][max(0, min(W - 1, x))] in '#' else False
        if y < 0: return False
        if y >= H: return True
        return rows[y][x] == '#'
    view = Image.new('RGBA', (PW, PH))
    speeds = [0, .2, .4, .65] if len(scene_layers) == 4 else [0, .3, .6]
    for (name, layer), sp in zip(scene_layers, speeds):
        off = int(cam * sp) % PW
        view.alpha_composite(layer, (-off, 0)); view.alpha_composite(layer, (PW - off, 0))
    lvl = Image.new('RGBA', (W * T, H * T))
    sheet = terrain_sheet(biome); sl = schraege(biome); pl = plattformen(); la = leiter(); sp_ = stacheln()
    # Ecken-Autotiling: Eckpunkt fest, wenn alle 4 umliegenden Kacheln fest sind -> hier: Ecke fest, wenn mind. eine angrenzende Kachel fest
    for ty in range(H):
        for tx in range(W):
            ch = rows[ty][tx]
            if ch == '#':
                def corner(cx, cy):
                    return all(solid(cx - dx, cy - dy) or rows[min(H - 1, max(0, cy - dy))][min(W - 1, max(0, cx - dx))] in '/\\'
                               for dx in (0, 1) for dy in (0, 1))
                bits = corner(tx, ty) * 1 + corner(tx + 1, ty) * 2 + corner(tx, ty + 1) * 4 + corner(tx + 1, ty + 1) * 8
                lvl.alpha_composite(tile_of(sheet, bits if bits else 15), (tx * T, ty * T))
            elif ch == '/': lvl.alpha_composite(sl.crop((0, 0, T, T)), (tx * T, ty * T))
            elif ch == '\\': lvl.alpha_composite(sl.crop((T, 0, 2 * T, T)), (tx * T, ty * T))
            elif ch == '=':
                k = 0 if tx == 0 or rows[ty][tx - 1] != '=' else 2 if tx == W - 1 or rows[ty][tx + 1] != '=' else 1
                lvl.alpha_composite(pl.crop((k * T, 0, (k + 1) * T, T)), (tx * T, ty * T))
            elif ch == 'H': lvl.alpha_composite(la.crop((0, 0, T, T)), (tx * T, ty * T))
            elif ch == '^': lvl.alpha_composite(sp_.crop((0, 0, T, T)), (tx * T, ty * T))
    # Figuren
    fox = Image.open(os.path.join(g.BASE, 'characters', 'voelker', 'fuchs_ruestung_walk.png'))
    px = 40 + t * 4
    lvl.alpha_composite(fox.crop(((1 + t % 4) * 18, 2 * 26, (2 + t % 4) * 18, 3 * 26)), (px, 11 * T - 26 + 2))
    wolf = Image.open(os.path.join(g.BASE, 'monster', 'sprites', 'D', 'graswolf.png'))
    meta = json.load(open(os.path.join(g.BASE, 'monster', 'sprites', 'monster.json'), encoding='utf-8'))['Graswolf']
    ww, wh = meta['bild']
    wf = wolf.crop(((t % 6) * ww, wh, (t % 6 + 1) * ww, 2 * wh)).transpose(Image.FLIP_LEFT_RIGHT)
    lvl.alpha_composite(wf, (34 * T - t * 3, 8 * T - meta['bodenpunkt'][1] + 1))
    view.alpha_composite(lvl.crop((cam, 0, cam + PW, H * T)), (0, PH - H * T))
    return view

def main():
    os.makedirs(os.path.join(OUT, 'parallax'), exist_ok=True)
    meta = {'kachelgroesse': T, 'terrain_autotiling': 'Wang-Ecken, Index = NW*1 + NE*2 + SW*4 + SE*8, Bit = fest; 4x4-Feld in Index-Reihenfolge. '
            'Oberkante (Gras/Moos/Schnee/Dornen/Blut/Glyphen), Seitenrand und Unterseite ergeben sich automatisch.',
            'gebiete': list(BIOMES), 'einzeln': {}, 'parallax': {}}
    prev = []
    for b in BIOMES:
        terrain_sheet(b).save(os.path.join(OUT, f'terrain_{b}.png'))
        rueckwand(b).save(os.path.join(OUT, f'rueckwand_{b}.png'))
        schraege(b).save(os.path.join(OUT, f'schraege_{b}.png'))
        prev.append((f'Terrain {b}', terrain_sheet(b))); prev.append((f'Rückwand + Schräge {b}', None))
    plattformen().save(os.path.join(OUT, 'plattformen.png')); leiter().save(os.path.join(OUT, 'leiter.png')); stacheln().save(os.path.join(OUT, 'stacheln.png'))
    meta['einzeln'] = {'rueckwand_<gebiet>': ['normal', 'risse', 'nische', 'kette'], 'schraege_<gebiet>': ['aufwaerts', 'abwaerts', 'fuellung'],
                       'plattformen': ['holz_links', 'holz_mitte', 'holz_rechts', 'stein_links', 'stein_mitte', 'stein_rechts', 'wolke', 'ast'],
                       'leiter': ['leiter', 'seil', 'kette'], 'stacheln': ['stahl', 'knochen', 'dornen', 'kristall']}
    S = scenes()
    for name, layers in S.items():
        meta['parallax'][name] = []
        for i, (ln, im) in enumerate(layers):
            im.save(os.path.join(OUT, 'parallax', f'{name}_{i}_{ln}.png')); meta['parallax'][name].append(f'{i}_{ln}')
    meta['parallax_hinweis'] = 'Ebenen von hinten (0) nach vorn; empfohlene Scroll-Faktoren: 0, 0.2, 0.4, 0.65 (bzw. 0, 0.3, 0.6 bei drei Ebenen). 320x180, waagrecht kachelbar.'
    json.dump(meta, open(os.path.join(OUT, 'level.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau Kacheln
    Sc = 3; cell = 64 * Sc + 16
    biomes = list(BIOMES)
    im = Image.new('RGB', (len(biomes) * (cell) + 16, 64 * Sc + 16 * Sc + 120 + 60), (30, 26, 42)); d = ImageDraw.Draw(im)
    d.text((8, 6), 'Seitenansicht-Tilesets: Terrain (Autotiling), Rückwände, Schrägen, Plattformen, Leitern, Stacheln', fill=(255, 240, 200), font=g.font(14))
    for i, b in enumerate(biomes):
        x = 8 + i * cell
        d.text((x, 26), b, fill=(235, 225, 205), font=g.font(12))
        bg = Image.new('RGBA', (64, 64), BIOMES[b]['back'][:3] + (255,)); bg.alpha_composite(terrain_sheet(b))
        im.paste(bg.resize((64 * Sc, 64 * Sc), Image.NEAREST), (x, 44))
        rw = rueckwand(b); im.paste(rw.resize((64 * Sc, 16 * Sc), Image.NEAREST), (x, 44 + 64 * Sc + 6))
        sl = schraege(b); bg2 = Image.new('RGBA', sl.size, BIOMES[b]['back'][:3] + (255,)); bg2.alpha_composite(sl)
        im.paste(bg2.resize((48 * Sc, 16 * Sc), Image.NEAREST), (x, 44 + 80 * Sc + 12))
    y = 44 + 96 * Sc + 24
    for j, (title, sh) in enumerate((('Plattformen', plattformen()), ('Leiter/Seil/Kette', leiter()), ('Stacheln', stacheln()))):
        x = 8 + j * 420
        d.text((x, y), title, fill=(235, 225, 205), font=g.font(12))
        im.paste(sh.resize((sh.width * Sc, sh.height * Sc), Image.NEAREST), (x, y + 16), sh.resize((sh.width * Sc, sh.height * Sc), Image.NEAREST))
    im.save(os.path.join(g.BASE, 'preview_level_tiles.png'))
    # Testszenen: Dorf-Nacht mit Wiese, Höhle mit Fels, Blut-Dungeon
    frames = []
    for scene, biome in (('dorf_nacht', 'wiese'), ('hoehle', 'fels'), ('dungeon_blut', 'dungeon_blut')):
        for t in range(16):
            v = render_level(t, biome, S[scene], cam=t * 6)
            frames.append(v.resize((PW * 3, PH * 3), Image.NEAREST).convert('RGB'))
    frames[0].save(os.path.join(g.BASE, 'preview_level_szene.gif'), save_all=True, append_images=frames[1:], duration=110, loop=0)
    frames[4].save('/tmp/claude-0/-home-user/12f6a153-289c-51b2-bfa7-11e2d78969f5/scratchpad/szene1.png')
    frames[20].save('/tmp/claude-0/-home-user/12f6a153-289c-51b2-bfa7-11e2d78969f5/scratchpad/szene2.png')
    frames[36].save('/tmp/claude-0/-home-user/12f6a153-289c-51b2-bfa7-11e2d78969f5/scratchpad/szene3.png')

if __name__ == '__main__':
    main()
