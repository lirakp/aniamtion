"""Tilesets (16x16) mit Ecken-Autotiling (Wang-Ecken, 16 Kacheln je Übergang).
Aufruf: python3 tiles.py
Ausgabe: tiles/<set>.png, tiles/tiles.json, tiles/beispielkarte.png/.gif, preview_tiles.png

Index einer Übergangs-Kachel = NW*1 + NE*2 + SW*4 + SE*8  (Bit = 1, wenn an dieser Ecke das obere Terrain liegt).
Die Kacheln liegen im Sheet 4x4 in Index-Reihenfolge (Index 0 = nur unteres Terrain, 15 = nur oberes).
Animierte Sets (Wasser) haben pro Bild ein eigenes 4x4-Feld nebeneinander.
"""
import os, math, random, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

T = 16
OUT = os.path.join(g.BASE, 'tiles')

def h(x, y, s=0):
    """deterministischer Hash 0..1 je Pixel (nahtlos, da nur innerhalb der Kachel)"""
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535

# ---------------------------------------------------------------- Terrain-Texturen
def tex(kind, x, y, t=0):
    if kind == 'gras':
        v = h(x, y, 1)
        if v < .08: return C('#4a7a3e')
        if v > .93: return C('#6e9e58')
        if h(x, y, 9) > .985: return C('#e8d870') if h(x, y, 3) > .5 else C('#e888a8')
        return C('#5a8a4a')
    if kind == 'weg':
        v = h(x, y, 2)
        if v < .1: return C('#8a6440')
        if v > .92: return C('#b88a5e')
        if h(x, y, 7) > .985: return C('#9a9488')
        return C('#a07850')
    if kind == 'sand':
        v = h(x, y, 3)
        if v < .08: return C('#c8ae80')
        if v > .94: return C('#f0dcb0')
        return C('#e0c898')
    if kind == 'wasser':
        wv = (x + y * 2 + t * 4) % 16
        if wv in (0, 1) and h(x // 3, y, 5) > .55: return C('#a8d4f4')
        if h(x, y, 4) < .07: return C('#3a78b8')
        return C('#4a8ac8')
    if kind == 'pflaster':
        bx, by = (x + (2 if (y // 4) % 2 else 0)) % 4, y % 4
        if bx == 3 or by == 3: return C('#6a6276')
        base = C('#9a94a8') if h((x + (2 if (y // 4) % 2 else 0)) // 4, y // 4, 6) > .5 else C('#8a8498')
        return mix(base, C('#ffffff'), .15) if bx == 0 and by == 0 else base
    if kind in ('d_physisch', 'd_dorn', 'd_blut', 'd_erinnerung'):
        pal = DUNGEON[kind[2:]]
        bx, by = (x + (4 if (y // 8) % 2 else 0)) % 8, y % 8
        if bx == 7 or by == 7: return pal['fuge']
        c = pal['boden'] if h((x + (4 if (y // 8) % 2 else 0)) // 8, y // 8, 8) > .5 else shade(pal['boden'], .92)
        if bx == 0 or by == 0: c = mix(c, C('#ffffff'), .08)
        if kind == 'd_dorn' and h(x, y, 11) > .97: c = pal['akzent']
        if kind == 'd_blut' and h(x // 2, y // 2, 12) > .93: c = pal['akzent']
        if kind == 'd_erinnerung' and (x + y + t) % 11 == 0 and h(x, y, 13) > .6: c = pal['akzent']
        return c
    if kind in ('w_physisch', 'w_dorn', 'w_blut', 'w_erinnerung'):
        pal = DUNGEON[kind[2:]]
        return pal['decke'] if h(x, y, 14) > .1 else shade(pal['decke'], 1.2)
    if kind == 'holz':
        if y % 4 == 3: return C('#5a3a28')
        off = (y // 4) * 5
        if (x + off) % 16 == 0: return C('#5a3a28')
        return C('#9c6c46') if h(x // 4, y // 4, 15) > .5 else C('#8e6040')
    if kind == 'teppich':
        return C('#8a2a3a') if (x + y) % 6 else C('#9a3a4a')
    return C('#ff00ff')

DUNGEON = {
    'physisch': dict(boden=C('#5a5468'), fuge=C('#3e384c'), decke=C('#241e2c'), wand=C('#4e4860'), wand_d=C('#36304a'), akzent=C('#7a7488')),
    'dorn': dict(boden=C('#3e3a3a'), fuge=C('#262222'), decke=C('#141210'), wand=C('#36302e'), wand_d=C('#221e1c'), akzent=C('#5a6e3a')),
    'blut': dict(boden=C('#5a3438'), fuge=C('#3a1e22'), decke=C('#1e0c10'), wand=C('#4e2a2e'), wand_d=C('#361a1e'), akzent=C('#8a1e2a')),
    'erinnerung': dict(boden=C('#4a4a78'), fuge=C('#30305a'), decke=C('#14142e'), wand=C('#3e3e6a'), wand_d=C('#2a2a50'), akzent=C('#a8b8ff')),
}

# Rand zwischen oberem (A) und unterem (B) Terrain
EDGE = {
    ('weg', 'gras'): dict(a=C('#8a6440'), b=C('#4a7a3e')),
    ('sand', 'gras'): dict(a=C('#c8ae80'), b=C('#4a7a3e')),
    ('pflaster', 'gras'): dict(a=C('#6a6276'), b=C('#3e6a36')),
    ('wasser', 'gras'): dict(a=C('#e8f8ff'), b=C('#3e6a36'), b2=C('#7a6a48')),
    ('wasser', 'sand'): dict(a=C('#e8f8ff'), b=C('#b89a6a')),
    ('teppich', 'holz'): dict(a=C('#e0b048'), b=C('#4a3020')),
}

def mask(bits, x, y, rough=.18, seed=0):
    nw, ne, sw, se = bits & 1, (bits >> 1) & 1, (bits >> 2) & 1, (bits >> 3) & 1
    u, v = (x + .5) / T, (y + .5) / T
    val = nw * (1 - u) * (1 - v) + ne * u * (1 - v) + sw * (1 - u) * v + se * u * v
    val += (h(x, y, 20 + seed) - .5) * rough
    return val > .5

def transition(a, b, t=0, rough=.18):
    """16 Kacheln: oberes Terrain a über unterem Terrain b"""
    sheet = Image.new('RGBA', (T * 4, T * 4))
    e = EDGE.get((a, b), dict(a=shade(tex(a, 0, 0), .75), b=shade(tex(b, 0, 0), .75)))
    for idx in range(16):
        tile = Image.new('RGBA', (T, T)); p = tile.load()
        m = [[mask(idx, x, y, rough) for x in range(T)] for y in range(T)]
        for y in range(T):
            for x in range(T):
                inside = m[y][x]
                near_out = any(0 <= x + dx < T and 0 <= y + dy < T and m[y + dy][x + dx] != inside
                               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if inside: c = e['a'] if near_out else tex(a, x, y, t)
                else:
                    c = tex(b, x, y, t)
                    if near_out: c = e['b']
                    elif 'b2' in e and any(0 <= x + dx < T and 0 <= y + dy < T and m[y + dy][x + dx]
                                           for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))): c = e['b2']
                if a == 'wasser' and inside and not near_out and any(0 <= x + dx < T and 0 <= y + dy < T and not m[y + dy][x + dx]
                                                                   for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))) and (x + y + t) % 3 == 0:
                    c = C('#a8d4f4')
                p[x, y] = c
        sheet.paste(tile, ((idx % 4) * T, (idx // 4) * T))
    return sheet

def wall_set(kind):
    """Dungeon: Wand-Oberseite (A) über Boden (B) + Schattenkante auf dem Boden."""
    sheet = Image.new('RGBA', (T * 4, T * 4)); pal = DUNGEON[kind]
    for idx in range(16):
        tile = Image.new('RGBA', (T, T)); p = tile.load()
        m = [[mask(idx, x, y, .06) for x in range(T)] for y in range(T)]
        for y in range(T):
            for x in range(T):
                if m[y][x]:
                    edge = any(0 <= x + dx < T and 0 <= y + dy < T and not m[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    c = pal['wand_d'] if edge else tex('w_' + kind, x, y)
                else:
                    c = tex('d_' + kind, x, y)
                    if any(0 <= y - k < T and m[y - k][x] for k in (1, 2)): c = shade(c, .7)
                p[x, y] = c
        sheet.paste(tile, ((idx % 4) * T, (idx // 4) * T))
    return sheet

def wall_front(kind):
    """Wandfront-Kacheln (unter Wand-Oberseiten, wo darunter Boden liegt): 6 Varianten."""
    pal = DUNGEON[kind]; sheet = Image.new('RGBA', (T * 6, T))
    for v in range(6):
        tile = Image.new('RGBA', (T, T)); d = ImageDraw.Draw(tile); p = tile.load()
        d.rectangle([0, 0, T - 1, T - 1], fill=pal['wand_d'])
        for row in range(4):
            off = (row % 2) * 4
            for col in range(-1, 3):
                x0 = col * 8 + off; y0 = row * 4
                c = shade(pal['wand'], .9 + .2 * h(col + v * 3, row, 30))
                xa, xb = max(0, x0 + 1), min(T - 1, x0 + 7)
                if xa > xb: continue
                d.rectangle([xa, y0 + 1, xb, y0 + 3], fill=c)
                d.line([(xa, y0 + 1), (min(xb, x0 + 6), y0 + 1)], fill=mix(c, C('#ffffff'), .12))
        d.line([(0, T - 1), (T - 1, T - 1)], fill=shade(pal['wand_d'], .7))
        if v == 1:   # Fackelhalter
            d.rectangle([7, 7, 8, 11], fill=g.WOOD_D); d.point((7, 6), fill=C('#ff9a3c')); d.point((8, 5), fill=C('#ffd27a'))
        if v == 2:   # Riss
            d.line([(4, 2), (7, 7), (5, 11)], fill=pal['wand_d'])
        if v == 3:   # typischer Akzent
            if kind == 'dorn':
                for k in range(3): d.line([(3 + k * 5, 15), (4 + k * 5, 8 + k)], fill=pal['akzent'])
            elif kind == 'blut':
                for x in (5, 10): d.line([(x, 0), (x, 6 + x % 4)], fill=pal['akzent'])
            elif kind == 'erinnerung':
                for k in range(4): p[4 + k * 2, 7] = pal['akzent']; p[5 + k * 2, 8] = pal['akzent']
            else:
                d.rectangle([5, 9, 10, 13], fill=C('#3a3446')); d.point((7, 11), fill=C('#e8e0d0'))
        if v == 4:   # Gitterfenster
            d.rectangle([4, 4, 11, 10], fill=C('#140e18'))
            for x in (6, 9): d.line([(x, 4), (x, 10)], fill=C('#5a5e6e'))
        if v == 5:   # Moos/Spinnweben
            for k in range(5): p[k, k] = (230, 230, 240, 255); p[0, k] = (230, 230, 240, 255); p[k, 0] = (230, 230, 240, 255)
        sheet.paste(tile, (v * T, 0))
    return sheet

def interior_wall():
    sheet = Image.new('RGBA', (T * 4, T))
    for v in range(4):
        tile = Image.new('RGBA', (T, T)); d = ImageDraw.Draw(tile)
        d.rectangle([0, 0, T - 1, 9], fill=C('#ded2be'))
        for k in range(6): d.point((int(h(k, v, 40) * 15), int(h(v, k, 41) * 9)), fill=C('#cbbfa8'))
        d.rectangle([0, 10, T - 1, T - 1], fill=g.WOOD); d.line([(0, 10), (T - 1, 10)], fill=g.WOOD_L)
        for x in range(0, T, 4): d.line([(x, 11), (x, T - 1)], fill=g.WOOD_D)
        if v == 1:
            d.rectangle([4, 1, 11, 8], fill=g.WOOD_D); d.rectangle([5, 2, 10, 7], fill=C('#b4d2ea')); d.line([(7, 2), (7, 7)], fill=g.WOOD_D); d.line([(5, 4), (10, 4)], fill=g.WOOD_D)
        if v == 2:
            d.rectangle([5, 2, 10, 7], fill=C('#c89a3a')); d.rectangle([6, 3, 9, 6], fill=C('#6a8ab0'))
        if v == 3:
            d.rectangle([3, 2, 12, 3], fill=g.WOOD_D)
            for k, c in enumerate((C('#c84a4a'), C('#4a6aa0'), C('#e0b048'))): d.rectangle([4 + k * 3, 0, 5 + k * 3, 1], fill=c)
        sheet.paste(tile, (v * T, 0))
    return sheet

def cliff():
    sheet = Image.new('RGBA', (T * 3, T * 2))
    for v in range(3):
        for row in range(2):
            tile = Image.new('RGBA', (T, T)); d = ImageDraw.Draw(tile)
            if row == 0:
                for y in range(T):
                    for x in range(T): tile.load()[x, y] = tex('gras', x, y)
                d.rectangle([0, 12, T - 1, T - 1], fill=C('#7a6a5a')); d.line([(0, 12), (T - 1, 12)], fill=C('#4a7a3e'))
                for x in range(0, T, 3): d.point((x, 13), fill=C('#3e6a36'))
            else:
                d.rectangle([0, 0, T - 1, T - 1], fill=C('#7a6a5a'))
                for k in range(5): d.line([(int(h(k, v, 50) * 15), 0), (int(h(k, v, 51) * 15), T - 1)], fill=C('#5a4a3e'))
                d.rectangle([0, 13, T - 1, T - 1], fill=C('#4a3e34'))
            if v == 0: d.rectangle([0, 0, 1, T - 1], fill=(0, 0, 0, 0)) if row == 1 else None
            if v == 0: d.line([(1, 12 if row == 0 else 0), (1, T - 1)], fill=C('#4a3e34'))
            if v == 2: d.line([(T - 2, 12 if row == 0 else 0), (T - 2, T - 1)], fill=C('#4a3e34'))
            sheet.paste(tile, (v * T, row * T))
    return sheet

def deko():
    """Einzelne Deko-Kacheln (transparent) zum Darüberlegen."""
    sheet = Image.new('RGBA', (T * 8, T))
    for v in range(8):
        tile = Image.new('RGBA', (T, T)); d = ImageDraw.Draw(tile)
        if v == 0:
            for x, hh in ((5, 4), (7, 6), (9, 5), (11, 3)): d.line([(x, 13), (x + 1, 13 - hh)], fill=C('#6e9e58'))
        elif v == 1:
            for x, y, c in ((4, 8, C('#e888a8')), (10, 6, C('#e8d870')), (7, 11, C('#f0f0f8'))):
                d.line([(x, y + 1), (x, y + 4)], fill=C('#4a7a3e')); d.point((x, y), fill=c); d.point((x - 1, y), fill=c); d.point((x + 1, y), fill=c); d.point((x, y - 1), fill=c)
        elif v == 2:
            d.ellipse([4, 9, 9, 13], fill=C('#8a8296')); d.ellipse([9, 10, 12, 13], fill=C('#7a7280')); d.point((5, 10), fill=C('#a8a0b4'))
        elif v == 3:
            d.rectangle([7, 9, 8, 13], fill=C('#e8dcc0')); d.ellipse([4, 6, 11, 10], fill=C('#c84a4a')); d.point((6, 7), fill=WHITE); d.point((9, 8), fill=WHITE)
        elif v == 4:
            for k in range(3): d.line([(5 + k * 3, 14), (6 + k * 3, 4 + k)], fill=C('#8a8a4a'))
            d.ellipse([10, 2, 12, 6], fill=C('#6a4a30'))
        elif v == 5:
            d.ellipse([3, 6, 13, 13], fill=g.LEAF_D); d.ellipse([4, 5, 11, 11], fill=g.LEAF); d.point((6, 7), fill=g.LEAF_L)
        elif v == 6:
            d.line([(3, 12), (12, 10)], fill=g.WOOD, width=2); d.ellipse([11, 9, 13, 11], fill=C('#c8a070'))
        else:
            d.ellipse([5, 10, 11, 13], fill=C('#e8e0d0')); d.line([(3, 12), (13, 9)], fill=C('#e8e0d0'))
        tile = g.outline(tile) if v in (2, 3, 5, 6, 7) else tile
        sheet.paste(tile, (v * T, 0))
    return sheet

WHITE = (255, 255, 255, 255)

SETS = [  # (name, titel, erzeuger, bilder)
    ('gras_weg', 'Weg auf Gras', lambda t: transition('weg', 'gras'), 1),
    ('gras_sand', 'Sand auf Gras', lambda t: transition('sand', 'gras'), 1),
    ('gras_pflaster', 'Pflaster auf Gras', lambda t: transition('pflaster', 'gras', rough=.04), 1),
    ('gras_wasser', 'Wasser auf Gras (animiert)', lambda t: transition('wasser', 'gras', t), 4),
    ('sand_wasser', 'Wasser auf Sand (animiert)', lambda t: transition('wasser', 'sand', t), 4),
    ('holz_teppich', 'Teppich auf Holzboden', lambda t: transition('teppich', 'holz', rough=0), 1),
] + [(f'dungeon_{k}_wand', f'Dungeon {k}: Wand über Boden', (lambda k: lambda t: wall_set(k))(k), 1) for k in DUNGEON]

def frames_strip(frames):
    w, hgt = frames[0].size; s = Image.new('RGBA', (w * len(frames), hgt))
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    return s

# ---------------------------------------------------------------- Beispielkarte
def autotile(grid, terrain, sheet, under=None):
    """grid: Eckpunkte (H+1)x(W+1) mit Terrain-Namen. Liefert Liste (x, y, index) für Kacheln mit terrain."""
    out = []
    for ty in range(len(grid) - 1):
        for tx in range(len(grid[0]) - 1):
            c = [grid[ty][tx], grid[ty][tx + 1], grid[ty + 1][tx], grid[ty + 1][tx + 1]]
            bits = sum((1 << i) for i, v in enumerate(c) if v in terrain)
            if bits: out.append((tx, ty, bits))
    return out

def demo_map(t):
    W, H = 26, 17
    grid = [['gras'] * (W + 1) for _ in range(H + 1)]
    for x in range(W + 1):
        for y in (9, 10): grid[y][x] = 'weg'
    for y in range(H + 1):
        for x in (14, 15): grid[y][x] = 'weg'
    for y in range(3, 9):
        for x in range(17, 24): grid[y][x] = 'pflaster'
    for y in range(11, H + 1):
        for x in range(1, 11):
            if ((x - 5.5) / 5.2) ** 2 + ((y - 14.5) / 3.6) ** 2 < 1: grid[y][x] = 'sand'
            if ((x - 5.5) / 3.8) ** 2 + ((y - 14.8) / 2.4) ** 2 < 1: grid[y][x] = 'wasser'
    img = Image.new('RGBA', (W * T, H * T))
    gras = Image.new('RGBA', (T, T))
    for y in range(T):
        for x in range(T): gras.load()[x, y] = tex('gras', x, y)
    for ty in range(H):
        for tx in range(W): img.paste(gras, (tx * T, ty * T))
    sheets = {k: transition(*k.split('|'), t if 'wasser' in k else 0, rough=.04 if 'pflaster' in k else .18) for k in
              ('pflaster|gras', 'weg|gras', 'sand|gras', 'wasser|sand')}
    for key, terr in (('pflaster|gras', ('pflaster',)), ('weg|gras', ('weg',)), ('sand|gras', ('sand', 'wasser')), ('wasser|sand', ('wasser',))):
        sh = sheets[key]
        for tx, ty, idx in autotile(grid, terr, sh):
            tile = sh.crop(((idx % 4) * T, (idx // 4) * T, (idx % 4 + 1) * T, (idx // 4 + 1) * T))
            img.alpha_composite(tile, (tx * T, ty * T))
    dk = deko()
    rng = random.Random(4)
    for _ in range(26):
        tx, ty = rng.randrange(W), rng.randrange(H)
        c = [grid[ty][tx], grid[ty][tx + 1], grid[ty + 1][tx], grid[ty + 1][tx + 1]]
        if all(v == 'gras' for v in c):
            v = rng.choice((0, 0, 1, 1, 2, 3, 5))
            img.alpha_composite(dk.crop((v * T, 0, (v + 1) * T, T)), (tx * T, ty * T))
    def put(path, x, y, frame=None, fw=None):
        im = Image.open(os.path.join(g.BASE, path))
        if fw: im = im.crop((frame * fw, 0, (frame + 1) * fw, im.height))
        img.alpha_composite(im, (x, y - im.height))
    put('buildings/cottage_tag.png', 10, 140)
    put('buildings/baeckerei_tag.png', 286, 54) if False else None
    put('buildings/taverne_tag.png', 92, 140)
    put('buildings/laden_alchemie_tag.png', 284, 132)
    put('props/baum_tag.png', 340, 120); put('props/baum_tag.png', 380, 200); put('props/tanne_tag.png', 230, 60)
    put('props/laterne_tag.png', 250, 160); put('props/zaun_tag.png', 380, 140)
    well = Image.open(os.path.join(g.BASE, 'welt', 'dorf', 'brunnen_eimer.png'))
    img.alpha_composite(well.crop(((t % 8) * 36, 0, (t % 8 + 1) * 36, 44)), (296, 168))
    for name, x, y in (('abenteurer', 236, 170), ('baeckerin', 196, 140), ('kind', 268, 168)):
        sh = Image.open(os.path.join(g.BASE, 'characters', 'idle', f'{name}_idle.png'))
        img.alpha_composite(sh.crop(((t % 6) * 18, 0, (t % 6 + 1) * 18, 26)), (x, y))
    fox = Image.open(os.path.join(g.BASE, 'characters', 'voelker', 'fuchs_ruestung_walk.png'))
    img.alpha_composite(fox.crop((((t % 4) + 1) * 18, 2 * 26, ((t % 4) + 2) * 18, 3 * 26)), (60 + t * 3, 148))
    return img

def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'kachelgroesse': T, 'autotiling': 'Wang-Ecken: Index = NW*1 + NE*2 + SW*4 + SE*8 (Bit = oberes Terrain an dieser Ecke); 4x4-Feld in Index-Reihenfolge',
            'uebergaenge': {}, 'einzeln': {}}
    prev = []
    for name, title, fn, n in SETS:
        frames = [fn(t) for t in range(n)]
        frames_strip(frames).save(os.path.join(OUT, f'{name}.png'))
        meta['uebergaenge'][name] = {'titel': title, 'bilder': n, 'feld': [4, 4]}
        prev.append((title, frames[0]))
    for k in DUNGEON:
        wall_front(k).save(os.path.join(OUT, f'dungeon_{k}_wandfront.png'))
        meta['einzeln'][f'dungeon_{k}_wandfront'] = {'titel': f'Dungeon {k}: Wandfront', 'varianten': ['normal', 'fackelhalter', 'riss', 'typisch', 'gitterfenster', 'spinnweben'],
                                                    'hinweis': 'unter eine Wand-Oberseite legen, wenn darunter Boden liegt'}
        prev.append((f'Wandfront {k}', wall_front(k)))
    interior_wall().save(os.path.join(OUT, 'innenwand.png'))
    meta['einzeln']['innenwand'] = {'titel': 'Innenwand', 'varianten': ['normal', 'fenster', 'bild', 'regal']}
    cliff().save(os.path.join(OUT, 'klippe.png'))
    meta['einzeln']['klippe'] = {'titel': 'Klippe', 'layout': '3 Spalten (links, mitte, rechts) x 2 Zeilen (Oberkante mit Gras, Felswand)'}
    deko().save(os.path.join(OUT, 'deko.png'))
    meta['einzeln']['deko'] = {'titel': 'Deko', 'varianten': ['grasbuschel', 'blumen', 'steine', 'pilz', 'schilf', 'busch', 'ast', 'knochen']}
    prev += [('Innenwand', interior_wall()), ('Klippe', cliff()), ('Deko', deko())]
    json.dump(meta, open(os.path.join(OUT, 'tiles.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau aller Sets
    S = 3; cols = 4
    cw, ch = 96 * S // 1 + 20, 64 * S + 26
    rows = (len(prev) + cols - 1) // cols
    im = Image.new('RGB', (cols * (64 * S + 24), rows * ch + 30), (30, 26, 42)); d = ImageDraw.Draw(im)
    d.text((8, 6), 'Tilesets (16x16, Ecken-Autotiling)', fill=(255, 240, 200), font=g.font(15))
    for i, (title, f) in enumerate(prev):
        x, y = (i % cols) * (64 * S + 24) + 8, 30 + (i // cols) * ch
        big = f.resize((f.width * S, f.height * S), Image.NEAREST)
        im.paste(big, (x, y + 18), big); d.text((x, y + 2), title, fill=(235, 225, 205), font=g.font(11))
    im.save(os.path.join(g.BASE, 'preview_tiles.png'))
    # Beispielkarte
    frames = [demo_map(t) for t in range(8)]
    frames[0].save(os.path.join(OUT, 'beispielkarte.png'))
    big = [f.resize((f.width * 2, f.height * 2), Image.NEAREST).convert('RGB') for f in frames]
    big[0].save(os.path.join(g.BASE, 'preview_beispielkarte.gif'), save_all=True, append_images=big[1:], duration=160, loop=0)

if __name__ == '__main__':
    main()
