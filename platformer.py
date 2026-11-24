"""Plattformer-Animationen (Seitenansicht, Blick nach rechts – für links im Spiel spiegeln) für alle Völker.
Aufruf: python3 platformer.py
Ausgabe: characters/voelker/plattformer/<volk>_<kleidung>_<animation>.png  (Zellen 26x26, Füße unten, eine Zeile)
         characters/voelker/plattformer/plattformer.json, preview_plattformer.gif
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g, walk as w, races as rc, combat as cb
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'characters', 'voelker', 'plattformer')
WHITE = (255, 255, 255, 255)

def R(spec):
    s = ['.'] * 16
    for start, chars in spec:
        for i, c in enumerate(chars): s[start + i] = c
    return ''.join(s)
HIP = R([(5, 'pppppp')]); E = '.' * 16
w.SIDE_LEGS.update({
    'renn_a': [HIP, R([(5, 'BB'), (9, 'FF')]), R([(4, 'BB'), (10, 'FF')]), R([(3, 'BB'), (11, 'FF')]), R([(2, 'bbb'), (11, 'bbb')]), E],
    'renn_b': [HIP, R([(6, 'BB'), (9, 'FFF')]), R([(6, 'BB'), (11, 'FF')]), R([(6, 'BB'), (11, 'bb')]), R([(6, 'bbb')]), E],
    'sprung': [HIP, R([(5, 'BB'), (8, 'FFFF')]), R([(4, 'BB'), (11, 'FF')]), R([(3, 'bb'), (10, 'bb')]), E, E],
    'scheitel': [HIP, R([(5, 'BBFFF')]), R([(4, 'bb'), (9, 'bbb')]), E, E, E],
    'fall': [HIP, R([(5, 'BB'), (9, 'FF')]), R([(5, 'BB'), (9, 'FF')]), R([(4, 'BB'), (10, 'FF')]), R([(4, 'bb'), (10, 'bbb')]), E],
    'hocke': [HIP, R([(4, 'BBB'), (8, 'FFFF')]), R([(3, 'bbb'), (9, 'bbbb')]), E, E, E],
    'wand': [HIP, R([(5, 'BB'), (9, 'FFF')]), R([(5, 'BB'), (11, 'FF')]), R([(5, 'BB'), (12, 'b')]), R([(5, 'bbb'), (12, 'b')]), E],
})
cb.SA.update({
    'oben': ([(7, 13, 'C'), (8, 13, 'C'), (8, 12, 'C'), (8, 11, 'C'), (8, 10, 's')], [(8, 10)]),
    'abwaerts': ([(7, 13, 'C'), (8, 13, 'C'), (8, 14, 'C'), (9, 15, 'C'), (9, 16, 's')], [(9, 16)]),
    'zurueck': ([(7, 13, 'C'), (7, 14, 'C'), (6, 15, 'C'), (5, 16, 's')], [(5, 16)]),
    'wandgriff': ([(7, 13, 'C'), (8, 13, 'C'), (9, 12, 'C'), (10, 11, 'C'), (11, 10, 's')], [(11, 10)]),
})
cb.BLADES.update({
    ('side', 'oben'): [(8, 9), (8, 8), (8, 7), (8, 6), (8, 5)],
    ('side', 'abwaerts'): [(9, 17), (9, 18), (9, 19), (9, 20), (9, 21)],
})
cb.FA['hoch_l'] = (cb._LUP + cb._R, [(2, 10)])

def F(race, outfit, legs='stand', arm='mid', dy=0, blink=False, near=True, blade=0, view='side'):
    im, hands = cb.compose(race, outfit, view, legs=legs, arm=arm, dy=dy, blink=blink, near_front=near, blade=blade)
    return im, hands

def cell(im, dx=0, dy=0, sx=1.0, sy=1.0):
    if sx == 1.0 and sy == 1.0: return cb.cell(im, dx, dy)
    nw, nh = max(1, round(18 * sx)), max(1, round(26 * sy))
    r = im.resize((nw, nh), Image.NEAREST)
    c = Image.new('RGBA', (26, 26), (0, 0, 0, 0))
    c.alpha_composite(r, (4 + (18 - nw) // 2 + dx, 26 - nh + dy)) if 26 - nh + dy >= 0 else c.alpha_composite(r.crop((0, nh - 26 - dy, nw, nh)), (4 + (18 - nw) // 2 + dx, 0))
    return c

def lines(c, xs, y0, y1, col=(220, 230, 255, 170)):
    d = ImageDraw.Draw(c)
    for x in xs: d.line([(x, y0), (x, y1)], fill=col)

def arc(c, cx, cy, r, a0, a1, col=WHITE, col2=C('#c8e0ff')):
    p = c.load()
    for k in range(24):
        a = a0 + (a1 - a0) * k / 23
        for rr, cc in ((r, col), (r - 1, col2)):
            x, y = int(round(cx + math.cos(a) * rr)), int(round(cy - math.sin(a) * rr))
            if 0 <= x < c.width and 0 <= y < c.height: p[x, y] = cc

def ghost(img, a):
    out = img.copy(); p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = p[x, y]
            if c[3]: p[x, y] = mix(c, C('#c8e0ff'), .5)[:3] + (a,)
    return out

def dust(c, x, y, t, n=3):
    p = c.load()
    for k in range(n):
        xx, yy = x - k * 2 - t, y - (k % 2)
        if 0 <= xx < c.width and 0 <= yy < c.height: p[xx, yy] = (200, 192, 180, 200)

def anims(race, outfit):
    blade = 3 if outfit == 'tunika' else 5
    A = {}
    A['stehen'] = [cell(F(race, outfit, dy=d, blink=b)[0]) for d, b in zip([0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 1])]
    run = []
    for i in range(8):
        legs = 'renn_a' if i % 2 == 0 else 'renn_b'
        near = i < 4
        arm = 'fwd' if (i // 2) % 2 == 0 else 'zurueck'
        run.append(cell(F(race, outfit, legs=legs, arm=arm, near=near, dy=0 if i % 2 == 0 else -0)[0], 0, -1 if i % 2 else 0))
    A['rennen'] = run
    A['sprung_start'] = [cell(F(race, outfit, legs='hocke', arm='mid', dy=3)[0], sx=1.15, sy=.85),
                         cell(F(race, outfit, legs='sprung', arm='hoch')[0], 0, -1, sx=.9, sy=1.1)]
    dust(A['sprung_start'][0], 9, 25, 0, 3); dust(A['sprung_start'][0], 21, 25, 0, 3)
    su = [cell(F(race, outfit, legs='sprung', arm='hoch')[0], 0, -2, sx=.92, sy=1.08), cell(F(race, outfit, legs='sprung', arm='oben')[0], 0, -2, sx=.92, sy=1.08)]
    for i, c in enumerate(su): lines(c, (10 + i, 15 + i), 22, 25)
    A['sprung_auf'] = su
    A['scheitel'] = [cell(F(race, outfit, legs='scheitel', arm='vorne')[0], 0, -3)]
    fa = [cell(F(race, outfit, legs='fall', arm='hoch')[0], 0, -1, sx=.95, sy=1.05), cell(F(race, outfit, legs='fall', arm='vorne')[0], 0, -1, sx=.95, sy=1.05)]
    for i, c in enumerate(fa): lines(c, (9 + i, 16 - i), 0, 3)
    A['fallen'] = fa
    land = [cell(F(race, outfit, legs='hocke', arm='mid', dy=3)[0], sx=1.2, sy=.8), cell(F(race, outfit, legs='hocke', arm='mid', dy=2)[0], sx=1.08, sy=.92), cell(F(race, outfit)[0])]
    for k, c in enumerate(land[:2]): dust(c, 8, 25, k, 3); dust(c, 22, 25, -k, 3)
    A['landen'] = land
    dash = []
    for i in range(4):
        base = F(race, outfit, legs='sprung', arm='zurueck')[0].resize((21, 24), Image.NEAREST)
        c = Image.new('RGBA', (26, 26), (0, 0, 0, 0))
        if i < 3:
            for k, a in ((3, 60), (2, 110)): c.alpha_composite(ghost(base, a), (3 - k * 3 - i, 1))
        c.alpha_composite(base, (3 + (1 if i < 3 else 0), 1))
        d = ImageDraw.Draw(c)
        for k in range(3): d.line([(0, 10 + k * 4), (5 - i, 10 + k * 4)], fill=(220, 230, 255, 180))
        dash.append(c)
    A['dash'] = dash
    wall = []
    for i in range(2):
        c = cell(F(race, outfit, legs='wand', arm='wandgriff', blink=i == 1)[0], 1)
        p = c.load()
        for k in range(3):
            y = 12 + ((i * 3 + k * 5) % 14)
            if y < 26: p[18, y] = (200, 192, 180, 220)
        wall.append(c)
    A['wand_rutschen'] = wall
    wj = [cell(F(race, outfit, legs='hocke', arm='wandgriff', dy=2)[0], 1),
          cell(F(race, outfit, legs='sprung', arm='hoch')[0], -1, -1),
          cell(F(race, outfit, legs='scheitel', arm='vorne')[0], -2, -2)]
    A['wandsprung'] = wj
    climb = []
    for i in range(4):
        arm = 'hoch_r' if i % 2 == 0 else 'hoch_l'
        im, _ = F(race, outfit, legs='a' if i % 2 == 0 else 'b', arm=arm, view='back')
        climb.append(cell(im, 0, -1 if i % 2 else 0))
    A['klettern'] = climb
    A['ducken'] = [cell(F(race, outfit, legs='hocke', arm='mid', dy=3, blink=b)[0]) for b in (0, 1)]
    up = []
    for i, (arm, bl) in enumerate((('hinten_oben', 0), ('oben', blade), ('oben', blade), ('mid', 0))):
        c = cell(F(race, outfit, arm=arm, blade=bl)[0])
        if i in (1, 2): arc(c, 13, 8, 9 - i, math.radians(160), math.radians(20) if i == 1 else math.radians(60))
        up.append(c)
    A['angriff_oben'] = up
    down = []
    for i, (arm, bl) in enumerate((('hoch', 0), ('abwaerts', blade), ('abwaerts', blade), ('vorne', 0))):
        c = cell(F(race, outfit, legs='scheitel', arm=arm, blade=bl)[0], 0, -2)
        if i in (1, 2): arc(c, 13, 20, 8 - i, math.radians(200), math.radians(340) if i == 1 else math.radians(300))
        down.append(c)
    A['angriff_unten'] = down
    fw = []
    for i, (arm, bl, legs) in enumerate((('hinten_oben', blade, 'stand'), ('vorne', blade, 'contact'), ('fwd', blade, 'contact'), ('mid', 0, 'stand'))):
        c = cell(F(race, outfit, legs=legs, arm=arm, blade=bl)[0], 1 if i in (1, 2) else 0)
        if i == 1: arc(c, 14, 14, 10, math.radians(100), math.radians(-40))
        fw.append(c)
    A['angriff_vorne'] = fw
    kb = []
    for i in range(3):
        im = F(race, outfit, legs='fall', arm='hoch', blink=True)[0]
        if i == 0: im = cb.tint(im, WHITE, .75)
        elif i == 1: im = cb.tint(im, C('#ff4a4a'), .35)
        kb.append(cell(im, -2 + i, -1))
    A['rueckstoss'] = kb
    return A

SCHLEIFE = {'stehen': True, 'rennen': True, 'sprung_auf': True, 'fallen': True, 'wand_rutschen': True, 'klettern': True, 'ducken': True}

def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'zelle': [26, 26], 'blick': 'rechts (für links horizontal spiegeln)', 'animationen': {}}
    sample = {}
    for race in rc.RACES:
        for outfit in rc.OUTFITS:
            A = anims(race, outfit)
            for name, fr in A.items():
                s = Image.new('RGBA', (26 * len(fr), 26), (0, 0, 0, 0))
                for i, f in enumerate(fr): s.alpha_composite(f, (i * 26, 0))
                s.save(os.path.join(OUT, f"{race['name']}_{outfit}_{name}.png"))
                meta['animationen'][name] = {'bilder': len(fr), 'schleife': SCHLEIFE.get(name, False)}
            if race['name'] in ('mensch', 'zwerg', 'elf', 'fuchs', 'echse', 'eule'): sample[(race['title'], outfit)] = A
    meta['ablauf'] = ('Sprung: sprung_start -> sprung_auf (Schleife, solange steigend) -> scheitel -> fallen (Schleife) -> landen. '
                      'Wand: wand_rutschen (Schleife) -> wandsprung (Bild ist vom Wand weg gedreht: beim Abspringen Blickrichtung umkehren). '
                      'angriff_unten = Pogo-Schlag in der Luft.')
    json.dump(meta, open(os.path.join(OUT, 'plattformer.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau: Zeilen = Animationen, Spalten = Beispiel-Völker
    names = list(next(iter(sample.values())).keys())
    keys = [('Mensch', 'tunika'), ('Zwerg', 'ruestung'), ('Elf', 'tunika'), ('Fuchs', 'ruestung'), ('Echse', 'ruestung'), ('Eule', 'tunika')]
    S = 3; cw = 26 * S + 6; rh = 26 * S + 4
    frames = []
    for t in range(8):
        im = Image.new('RGB', (150 + len(keys) * cw, 30 + len(names) * rh), (42, 36, 69)); d = ImageDraw.Draw(im)
        d.text((10, 6), 'Plattformer-Bewegungen (Blick rechts)', fill=(255, 240, 200), font=g.font(15))
        for r, n in enumerate(names):
            y = 30 + r * rh
            d.text((10, y + rh // 2 - 8), n, fill=(230, 220, 200), font=g.font(12))
            for c_, k in enumerate(keys):
                fr = sample[k][n]; f = fr[t % len(fr)] if SCHLEIFE.get(n) else fr[min(t, len(fr) - 1)]
                big = f.resize((26 * S, 26 * S), Image.NEAREST); im.paste(big, (150 + c_ * cw, y), big)
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_plattformer.gif'), save_all=True, append_images=frames[1:], duration=120, loop=0)
    frames[1].save('/tmp/claude-0/-home-user/12f6a153-289c-51b2-bfa7-11e2d78969f5/scratchpad/plat.png')

if __name__ == '__main__':
    main()
