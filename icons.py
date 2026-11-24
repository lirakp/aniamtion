"""Gegenstands-Icons (16x16) für Inventar und Beute.
Aufruf: python3 icons.py
Ausgabe: icons/<gruppe>.png (Icons nebeneinander, Reihenfolge in icons/icons.json), preview_icons.png
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'icons')
WHITE, INK = (255, 255, 255, 255), C('#2b1e33')
WOOD, WOOD_D, WOOD_L = g.WOOD, g.WOOD_D, g.WOOD_L
RANKS = ['D', 'C', 'B', 'A', 'S', 'SS']
METAL = {  # Klinge, Klinge hell, Klinge dunkel, Beschlag, Glanz/Leuchten
    'D': (C('#8a7e74'), C('#b0a496'), C('#5a4e46'), C('#6a5a4a'), None),
    'C': (C('#b8bccc'), C('#eceef4'), C('#6e7284'), C('#8a6a4a'), None),
    'B': (C('#7aa8d8'), C('#d8ecff'), C('#3e6a9a'), C('#5a5e7a'), None),
    'A': (C('#d8dce8'), WHITE, C('#8a8ea0'), C('#e0b048'), None),
    'S': (C('#b89aff'), C('#f0e8ff'), C('#6a4aa8'), C('#e0b048'), C('#d8c8ff')),
    'SS': (C('#e0443a'), C('#ffc8c0'), C('#6a1420'), C('#2b1e33'), C('#ff8a7a')),
}
GEM = {'D': C('#8a7a6a'), 'C': C('#6ab06a'), 'B': C('#5a9ad8'), 'A': C('#b880ff'), 'S': C('#e0b048'), 'SS': C('#e0443a')}

def new(): im = Image.new('RGBA', (16, 16)); return im, ImageDraw.Draw(im)
def fin(im, glow=None):
    im = g.outline(im)
    if glow:
        p = im.load()
        for y in range(16):
            for x in range(16):
                if not p[x, y][3] and any(0 <= x + dx < 16 and 0 <= y + dy < 16 and p[x + dx, y + dy][3] == 255 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and (x + y) % 2:
                    p[x, y] = glow[:3] + (170,)
    return im

# ---------------------------------------------------------------- Waffen
def schwert(r, short=False):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    tip = (13, 2) if not short else (10, 5)
    d.line([(5, 10), tip], fill=b, width=2); d.line([(5, 9), (tip[0] - 1, tip[1])], fill=bl)
    d.line([(3, 8), (7, 12)], fill=acc, width=2)
    d.line([(2, 13), (4, 11)], fill=WOOD_D, width=2); d.point((1, 14), fill=acc)
    return fin(im, gl)
def axt(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.line([(3, 14), (11, 3)], fill=WOOD, width=2); d.line([(4, 14), (12, 3)], fill=WOOD_D)
    d.polygon([(9, 2), (14, 3), (15, 8), (12, 8), (10, 5)], fill=b); d.line([(14, 3), (15, 8)], fill=bl); d.point((11, 4), fill=acc)
    return fin(im, gl)
def speer(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.line([(1, 15), (11, 5)], fill=WOOD, width=1); d.line([(2, 15), (12, 5)], fill=WOOD_D)
    d.polygon([(10, 4), (15, 0), (12, 6)], fill=b); d.line([(11, 4), (15, 0)], fill=bl); d.line([(9, 6), (11, 8)], fill=acc)
    return fin(im, gl)
def bogen(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.arc([1, 1, 13, 14], 280, 80, fill=WOOD, width=2); d.line([(8, 1), (8, 14)], fill=C('#e8e0d0'))
    d.point((12, 7), fill=acc); d.point((12, 8), fill=acc)
    return fin(im, gl)
def stab(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.line([(3, 15), (11, 5)], fill=WOOD, width=2)
    gem = GEM[r]; d.ellipse([9, 0, 15, 6], fill=gem); d.point((11, 2), fill=WHITE); d.arc([8, 0, 15, 7], 90, 270, fill=acc)
    return fin(im, gl or mix(gem, WHITE, .4))
def hammer(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.line([(3, 14), (10, 5)], fill=WOOD, width=2)
    d.polygon([(7, 2), (12, 0), (15, 5), (10, 7)], fill=b); d.line([(12, 0), (15, 5)], fill=bl); d.line([(7, 2), (10, 7)], fill=bd)
    return fin(im, gl)
def schild(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.polygon([(2, 2), (13, 2), (13, 8), (7.5, 14), (2, 8)], fill=b); d.polygon([(4, 4), (11, 4), (11, 8), (7.5, 12), (4, 8)], fill=GEM[r] if r != 'D' else bd)
    d.line([(2, 2), (13, 2)], fill=bl); d.line([(7, 5), (7, 10)], fill=acc); d.line([(5, 7), (10, 7)], fill=acc)
    return fin(im, gl)

# ---------------------------------------------------------------- Rüstung & Schmuck
def helm(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.chord([2, 2, 13, 14], 180, 360, fill=b); d.rectangle([2, 8, 13, 13], fill=b)
    d.rectangle([4, 8, 11, 9], fill=INK); d.line([(7, 10), (7, 13)], fill=bd); d.line([(3, 4), (6, 2)], fill=bl)
    d.line([(7, 1), (8, 1)], fill=acc)
    return fin(im, gl)
def brust(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.polygon([(2, 3), (5, 2), (8, 4), (11, 2), (14, 3), (13, 8), (12, 14), (4, 14), (3, 8)], fill=b)
    d.line([(8, 5), (8, 13)], fill=bd); d.line([(4, 4), (5, 9)], fill=bl); d.line([(4, 11), (12, 11)], fill=acc)
    return fin(im, gl)
def stiefel(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    for x0 in (2, 8):
        d.rectangle([x0, 3, x0 + 4, 11], fill=b); d.rectangle([x0, 11, x0 + 6, 14], fill=bd if r != 'D' else WOOD_D); d.line([(x0, 5), (x0 + 4, 5)], fill=acc)
    return fin(im, gl)
def handschuh(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.rectangle([4, 7, 11, 14], fill=b); d.rectangle([4, 12, 11, 13], fill=acc)
    for k in range(4): d.rectangle([4 + k * 2, 3, 5 + k * 2, 7], fill=b)
    d.rectangle([11, 6, 13, 9], fill=b); d.line([(5, 8), (10, 8)], fill=bl)
    return fin(im, gl)
def ring(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.ellipse([3, 5, 12, 14], outline=C('#e0b048') if r != 'D' else C('#a89a8a'), width=2)
    d.ellipse([5, 1, 10, 6], fill=GEM[r]); d.point((6, 2), fill=WHITE)
    return fin(im, gl)
def amulett(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.arc([2, 0, 13, 9], 0, 180, fill=C('#c8ccd8'))
    d.polygon([(7.5, 7), (12, 10), (7.5, 15), (3, 10)], fill=C('#e0b048')); d.polygon([(7.5, 9), (10, 10.5), (7.5, 13), (5, 10.5)], fill=GEM[r])
    return fin(im, gl)

# ---------------------------------------------------------------- Tränke
POT = {'heil': C('#e0443a'), 'mana': C('#4a8ae0'), 'ausdauer': C('#6ac84a'), 'gegengift': C('#e8d040'), 'feuerschutz': C('#ff8a3a'), 'unsichtbar': C('#d8e8f0')}
def trank(col, gross):
    im, d = new()
    if gross:
        d.ellipse([2, 5, 13, 15], fill=C('#c8e0ee')); d.ellipse([3, 7, 12, 14], fill=col); d.rectangle([6, 1, 9, 6], fill=C('#c8e0ee')); d.rectangle([5, 0, 10, 1], fill=WOOD)
        d.point((4, 9), fill=WHITE); d.point((4, 10), fill=WHITE)
    else:
        d.ellipse([4, 7, 11, 14], fill=C('#c8e0ee')); d.ellipse([5, 9, 10, 13], fill=col); d.rectangle([6, 3, 9, 8], fill=C('#c8e0ee')); d.rectangle([6, 2, 9, 3], fill=WOOD)
        d.point((6, 10), fill=WHITE)
    return fin(im)

# ---------------------------------------------------------------- Beute aus der Welt
ELEM = {'feuer': C('#d8452e'), 'eis': C('#7ab8e8'), 'wasser': C('#2a6ab8'), 'erde': C('#8a6a4a'), 'dendro': C('#4a8a3a'),
        'wind': C('#9ac8c0'), 'elektro': C('#b880ff'), 'schatten': C('#3a2a5a'), 'licht': C('#f0d070')}
def monsterkern(r):
    im, d = new(); c = GEM[r]
    d.polygon([(8, 1), (14, 6), (11, 14), (5, 14), (2, 6)], fill=c); d.polygon([(8, 1), (8, 14), (5, 14), (2, 6)], fill=mix(c, WHITE, .3))
    d.line([(2, 6), (14, 6)], fill=shade(c, .7)); d.point((6, 4), fill=WHITE)
    return fin(im, mix(c, WHITE, .5) if r in ('A', 'S', 'SS') else None)
def rohling(r):
    b, bl, bd, acc, gl = METAL[r]; im, d = new()
    d.polygon([(1, 10), (11, 4), (15, 7), (5, 13)], fill=b); d.line([(1, 10), (11, 4)], fill=bl); d.line([(5, 13), (15, 7)], fill=bd)
    d.point((8, 8), fill=GEM[r])
    return fin(im, gl)
def grimoire(el):
    im, d = new(); c = ELEM[el]
    d.rectangle([2, 2, 13, 14], fill=c); d.rectangle([2, 2, 3, 14], fill=shade(c, .65)); d.rectangle([12, 3, 13, 13], fill=C('#f0e4cc'))
    d.rectangle([5, 5, 10, 10], outline=C('#e0b048')); d.point((7, 7), fill=WHITE); d.point((8, 8), fill=C('#e0b048'))
    return fin(im)
def erz(col, spots):
    im, d = new()
    d.polygon([(2, 12), (3, 6), (7, 3), (12, 4), (14, 9), (12, 14), (5, 14)], fill=C('#6e687a')); d.line([(3, 6), (7, 3)], fill=C('#8a8296'))
    for x, y in spots: d.rectangle([x, y, x + 1, y + 1], fill=col); d.point((x, y), fill=mix(col, WHITE, .5))
    return fin(im)
def kristall():
    im, d = new()
    for x0, h_, c in ((3, 9, C('#7a5ad0')), (7, 13, C('#b8a0ff')), (11, 8, C('#8a6ae0'))):
        d.polygon([(x0 - 2, 15), (x0 + 2, 15), (x0 + 1, 15 - h_), (x0 - 1, 15 - h_)], fill=c); d.line([(x0 - 1, 14), (x0 - 1, 16 - h_)], fill=WHITE)
    return fin(im, C('#e0d0ff'))
def muenzen(col):
    im, d = new()
    for i in range(4): d.ellipse([3, 10 - i * 2, 12, 14 - i * 2], fill=shade(col, .75)); d.ellipse([3, 9 - i * 2, 12, 13 - i * 2], fill=col)
    d.ellipse([6, 3, 13, 9], fill=col); d.point((8, 5), fill=mix(col, WHITE, .5))
    return fin(im)
def schluessel(kind):
    im, d = new(); col = {'eisen': C('#a8acbc'), 'gold': C('#e0b048'), 'dungeon': C('#8a6ae0'), 'boss': C('#e8e0d0')}[kind]
    if kind == 'boss':
        d.ellipse([1, 1, 8, 7], fill=col); d.point((3, 3), fill=INK); d.point((6, 3), fill=INK); d.rectangle([3, 6, 6, 8], fill=col)
    else:
        d.ellipse([1, 1, 7, 7], outline=col, width=2)
    d.line([(6, 6), (14, 14)], fill=col, width=2); d.line([(11, 11), (13, 9)], fill=col, width=2); d.line([(13, 13), (15, 11)], fill=col)
    return fin(im, C('#d8c8ff') if kind == 'dungeon' else None)
def essen(kind):
    im, d = new()
    if kind == 'brot':
        d.ellipse([1, 5, 14, 13], fill=C('#c8903a')); d.ellipse([2, 5, 13, 10], fill=C('#e0b060'))
        for x in (5, 8, 11): d.line([(x, 6), (x - 1, 9)], fill=C('#a8703a'))
    elif kind == 'apfel':
        d.ellipse([2, 4, 13, 14], fill=C('#d8403a')); d.point((5, 7), fill=WHITE); d.line([(8, 1), (8, 4)], fill=WOOD_D); d.ellipse([8, 1, 12, 4], fill=g.LEAF)
    elif kind == 'fleisch':
        d.ellipse([1, 3, 11, 12], fill=C('#c85a4a')); d.ellipse([3, 5, 8, 9], fill=C('#e88a7a')); d.line([(10, 10), (14, 14)], fill=C('#e8e0d0'), width=2); d.ellipse([13, 12, 15, 15], fill=C('#e8e0d0'))
    elif kind == 'kaese':
        d.polygon([(1, 12), (14, 6), (14, 12)], fill=C('#f0c850')); d.polygon([(1, 12), (14, 12), (14, 14), (1, 14)], fill=C('#d8a830')); d.point((10, 10), fill=C('#c8982a'))
    elif kind == 'fisch':
        d.ellipse([1, 5, 12, 11], fill=C('#8aa8c8')); d.polygon([(11, 8), (15, 4), (15, 12)], fill=C('#6a8ab0')); d.point((3, 7), fill=INK)
    return fin(im)
def kraut(kind):
    im, d = new()
    if kind == 'heilkraut':
        d.line([(8, 15), (8, 4)], fill=g.LEAF_D)
        for y, s in ((5, -1), (8, 1), (11, -1)): d.ellipse([8 + s * 5 - 2, y - 2, 8 + s * 5 + 2, y + 2], fill=g.LEAF)
        d.ellipse([6, 1, 10, 5], fill=C('#e888a8'))
    elif kind == 'pilz':
        d.rectangle([6, 8, 9, 14], fill=C('#e8dcc0')); d.ellipse([2, 3, 13, 10], fill=C('#c84a4a')); d.point((5, 5), fill=WHITE); d.point((9, 6), fill=WHITE)
    elif kind == 'leuchtpilz':
        d.rectangle([6, 8, 9, 14], fill=C('#d8d0e0')); d.ellipse([2, 3, 13, 10], fill=C('#6ab8e8')); d.point((5, 5), fill=WHITE)
        return fin(im, C('#bfe8ff'))
    elif kind == 'blume':
        d.line([(8, 15), (8, 7)], fill=g.LEAF_D)
        for a in range(5): d.ellipse([8 + math.cos(a * 1.26) * 3 - 2, 5 + math.sin(a * 1.26) * 3 - 2, 8 + math.cos(a * 1.26) * 3 + 2, 5 + math.sin(a * 1.26) * 3 + 2], fill=C('#f0e8f8'))
        d.ellipse([6, 3, 10, 7], fill=C('#e8c050'))
    return fin(im)
def sonst(kind):
    im, d = new()
    if kind == 'brief':
        d.rectangle([1, 4, 14, 12], fill=C('#f0e4cc')); d.line([(1, 4), (7, 9), (14, 4)], fill=C('#c8b898')); d.ellipse([6, 7, 9, 10], fill=C('#a83a3a'))
    elif kind == 'karte':
        d.polygon([(1, 3), (5, 2), (10, 3), (14, 2), (14, 13), (10, 14), (5, 13), (1, 14)], fill=C('#e8d8b0'))
        for x in (5, 10): d.line([(x, 2), (x, 13)], fill=C('#c8b088'))
        d.line([(3, 10), (7, 7), (12, 9)], fill=C('#a83a3a')); d.point((12, 9), fill=C('#a83a3a'))
    elif kind == 'fackel':
        d.line([(5, 15), (10, 6)], fill=WOOD, width=2); d.ellipse([8, 1, 14, 7], fill=C('#ff9a3c')); d.ellipse([10, 2, 13, 5], fill=C('#ffd27a'))
    elif kind == 'seil':
        for k in range(3): d.ellipse([2 + k, 3 + k, 13 - k, 13 - k], outline=C('#c8a870'))
        d.line([(12, 10), (15, 14)], fill=C('#c8a870'))
    elif kind == 'laterne':
        d.rectangle([4, 4, 11, 13], fill=C('#3a3446')); d.rectangle([5, 5, 10, 12], fill=C('#ffd27a')); d.line([(7, 5), (7, 12)], fill=C('#3a3446')); d.arc([5, 0, 10, 6], 180, 360, fill=C('#3a3446'))
    elif kind == 'mana_batterie':
        d.rectangle([4, 2, 11, 14], fill=C('#5a5468')); d.rectangle([6, 0, 9, 2], fill=C('#8a8ea0'))
        for k in range(3): d.rectangle([5, 11 - k * 4, 10, 13 - k * 4], fill=C('#8ad8ff'))
        return fin(im, C('#bfe8ff'))
    elif kind == 'siegelring':
        d.ellipse([3, 5, 12, 14], outline=C('#c8ccd8'), width=2); d.rectangle([4, 1, 11, 6], fill=C('#c8ccd8')); d.rectangle([5, 2, 10, 5], fill=C('#6a4aa8')); d.point((7, 3), fill=C('#e0d0ff'))
        return fin(im, C('#d8c8ff'))
    elif kind == 'seelenvase':
        d.ellipse([3, 5, 12, 14], fill=C('#3a3446')); d.rectangle([5, 2, 10, 6], fill=C('#3a3446')); d.rectangle([4, 1, 11, 2], fill=C('#5a5468'))
        d.ellipse([6, 8, 9, 11], fill=C('#8ad0ff'))
        return fin(im, C('#8ad0ff'))
    return fin(im)

GROUPS = {
    'waffen': [(f'{n}_{r}', fn(r)) for n, fn in (('schwert', schwert), ('dolch', lambda r: schwert(r, True)), ('axt', axt), ('speer', speer),
                                                   ('bogen', bogen), ('stab', stab), ('hammer', hammer), ('schild', schild)) for r in RANKS],
    'ruestung': [(f'{n}_{r}', fn(r)) for n, fn in (('helm', helm), ('brustplatte', brust), ('stiefel', stiefel), ('handschuhe', handschuh),
                                                     ('ring', ring), ('amulett', amulett)) for r in RANKS],
    'traenke': [(f'{k}_{"gross" if gr else "klein"}', trank(c, gr)) for k, c in POT.items() for gr in (False, True)],
    'beute': [(f'monsterkern_{r}', monsterkern(r)) for r in RANKS] + [(f'rohling_{r}', rohling(r)) for r in RANKS]
             + [(f'grimoire_{e}', grimoire(e)) for e in ELEM],
    'rohstoffe': [('erz_eisen', erz(C('#c8a890'), [(5, 7), (9, 10), (10, 5)])), ('erz_kupfer', erz(C('#d8804a'), [(5, 7), (9, 10), (10, 5)])),
                  ('erz_silber', erz(C('#e8ecf4'), [(5, 7), (9, 10), (10, 5)])), ('erz_gold', erz(C('#f0c850'), [(5, 7), (9, 10), (10, 5)])),
                  ('mana_kristall', kristall()), ('muenzen_kupfer', muenzen(C('#c87a4a'))), ('muenzen_silber', muenzen(C('#c8ccd8'))),
                  ('muenzen_gold', muenzen(C('#e0b048')))],
    'schluessel': [(f'schluessel_{k}', schluessel(k)) for k in ('eisen', 'gold', 'dungeon', 'boss')],
    'essen_kraeuter': [(k, essen(k)) for k in ('brot', 'apfel', 'fleisch', 'kaese', 'fisch')] + [(k, kraut(k)) for k in ('heilkraut', 'pilz', 'leuchtpilz', 'blume')],
    'sonstiges': [(k, sonst(k)) for k in ('brief', 'karte', 'fackel', 'seil', 'laterne', 'mana_batterie', 'siegelring', 'seelenvase')],
}

def main():
    os.makedirs(OUT, exist_ok=True); meta = {'groesse': 16, 'gruppen': {}}
    for grp, items in GROUPS.items():
        s = Image.new('RGBA', (16 * len(items), 16))
        for i, (n, im) in enumerate(items): s.alpha_composite(im, (i * 16, 0))
        s.save(os.path.join(OUT, f'{grp}.png')); meta['gruppen'][grp] = [n for n, _ in items]
    json.dump(meta, open(os.path.join(OUT, 'icons.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    S = 3; cell = 16 * S + 6
    rows = []
    for grp, items in GROUPS.items():
        per = 12 if grp in ('waffen', 'ruestung') else 16
        for k in range(0, len(items), per): rows.append((grp if k == 0 else '', items[k:k + per]))
    im = Image.new('RGB', (130 + 16 * cell, 30 + len(rows) * (cell + 4)), (42, 36, 69)); d = ImageDraw.Draw(im)
    d.text((8, 6), 'Gegenstands-Icons (16x16); Waffen & Rüstung je Rang D · C · B · A · S · SS', fill=(255, 240, 200), font=g.font(14))
    for r, (title, items) in enumerate(rows):
        y = 30 + r * (cell + 4)
        d.text((8, y + cell // 2 - 6), title, fill=(230, 220, 200), font=g.font(12))
        for i, (n, ic) in enumerate(items):
            x = 130 + i * cell
            d.rectangle([x, y, x + cell - 4, y + cell - 4], fill=(58, 52, 70))
            big = ic.resize((16 * S, 16 * S), Image.NEAREST); im.paste(big, (x + 1, y + 1), big)
    im.save(os.path.join(g.BASE, 'preview_icons.png'))

if __name__ == '__main__':
    main()
