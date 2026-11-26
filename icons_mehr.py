"""Weitere Inventar-Icons (16x16): mehr Tränke, Werkzeuge, Monsterteile, Magisches, Edelsteine, Gekochtes, Getränke, Taschen, Quest-Items.
Aufruf: python3 icons_mehr.py
Ausgabe: icons/<gruppe>.png (Reihenfolge in icons/icons_mehr.json), preview_icons_mehr.png
Stil und Kontur wie icons.py.
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
from icons import new, fin, ELEM, WOOD, WOOD_D, WOOD_L, INK, WHITE

OUT = os.path.join(g.BASE, 'icons')
GLASS = C('#c8e0ee')
STEEL, STEEL_L = C('#a8acbc'), C('#e0e4ee')

# ---------------------------------------------------------------- Tränke
def flasche(col, form='rund', glow=None, kork=WOOD):
    im, d = new()
    if form == 'rund':
        d.ellipse([2, 5, 13, 15], fill=GLASS); d.ellipse([3, 7, 12, 14], fill=col); d.rectangle([6, 1, 9, 6], fill=GLASS); d.rectangle([5, 0, 10, 1], fill=kork)
        d.point((4, 9), fill=WHITE); d.point((4, 10), fill=WHITE)
    elif form == 'hoch':
        d.rectangle([4, 4, 11, 15], fill=GLASS); d.rectangle([5, 7, 10, 14], fill=col); d.rectangle([6, 1, 9, 4], fill=GLASS); d.rectangle([5, 0, 10, 1], fill=kork)
        d.line([(5, 8), (5, 12)], fill=WHITE)
    elif form == 'kegel':
        d.polygon([(6, 4), (9, 4), (14, 15), (1, 15)], fill=GLASS); d.polygon([(5, 8), (10, 8), (13, 14), (2, 14)], fill=col); d.rectangle([6, 1, 9, 4], fill=GLASS); d.rectangle([5, 0, 10, 1], fill=kork)
        d.line([(4, 11), (5, 9)], fill=WHITE)
    elif form == 'herz':
        d.ellipse([1, 4, 8, 11], fill=GLASS); d.ellipse([7, 4, 14, 11], fill=GLASS); d.polygon([(1, 8), (14, 8), (7.5, 15)], fill=GLASS)
        d.ellipse([2, 6, 7, 10], fill=col); d.ellipse([8, 6, 13, 10], fill=col); d.polygon([(2, 9), (13, 9), (7.5, 14)], fill=col)
        d.rectangle([6, 1, 9, 5], fill=GLASS); d.rectangle([5, 0, 10, 1], fill=kork); d.point((3, 7), fill=WHITE)
    elif form == 'riesig':
        d.ellipse([0, 4, 15, 16], fill=GLASS); d.ellipse([1, 6, 14, 15], fill=col); d.rectangle([5, 0, 10, 5], fill=GLASS); d.rectangle([4, 0, 11, 1], fill=kork)
        d.line([(3, 8), (3, 11)], fill=WHITE); d.rectangle([6, 9, 9, 12], fill=mix(col, WHITE, .4))
    elif form == 'bombe':
        d.ellipse([1, 4, 14, 16], fill=GLASS); d.ellipse([2, 6, 13, 15], fill=col); d.rectangle([6, 2, 9, 5], fill=C('#5a5468'))
        d.line([(8, 2), (11, 0)], fill=C('#c8a870')); d.point((12, 0), fill=C('#ffd27a')); d.point((4, 8), fill=WHITE)
    elif form == 'leer':
        d.ellipse([3, 6, 12, 15], fill=GLASS); d.rectangle([6, 2, 9, 7], fill=GLASS); d.point((5, 9), fill=WHITE)
    return fin(im, glow)
def gift():
    im = flasche(C('#3a6a2a'), 'rund').copy(); d = ImageDraw.Draw(im)
    d.rectangle([6, 9, 9, 11], fill=C('#e8e0d0')); d.point((6, 10), fill=INK); d.point((9, 10), fill=INK); d.line([(7, 12), (8, 12)], fill=C('#e8e0d0'))
    return im
def elixier(el): return flasche(ELEM[el], 'kegel', glow=mix(ELEM[el], WHITE, .5))

# ---------------------------------------------------------------- Werkzeuge
def werkzeug(kind):
    im, d = new()
    if kind == 'spitzhacke':
        d.line([(3, 14), (11, 4)], fill=WOOD, width=2); d.arc([2, 0, 16, 10], 200, 340, fill=STEEL, width=2)
    elif kind == 'holzaxt':
        d.line([(3, 14), (10, 3)], fill=WOOD, width=2); d.polygon([(8, 1), (13, 2), (14, 7), (11, 7), (9, 4)], fill=STEEL); d.line([(13, 2), (14, 7)], fill=STEEL_L)
    elif kind == 'angel':
        d.line([(2, 15), (12, 1)], fill=WOOD); d.line([(12, 1), (14, 9)], fill=C('#e8e0d0')); d.arc([12, 9, 15, 13], 0, 200, fill=STEEL); d.ellipse([3, 11, 6, 14], fill=C('#8a8296'))
    elif kind == 'sichel':
        d.line([(3, 14), (6, 10)], fill=WOOD, width=2); d.arc([4, 1, 15, 13], 160, 330, fill=STEEL_L, width=2)
    elif kind == 'schaufel':
        d.line([(3, 1), (9, 9)], fill=WOOD, width=2); d.line([(2, 1), (5, 1)], fill=WOOD); d.polygon([(8, 8), (13, 9), (14, 14), (10, 15), (7, 12)], fill=STEEL); d.line([(13, 9), (14, 14)], fill=STEEL_L)
    elif kind == 'giesskanne':
        d.rectangle([3, 6, 10, 13], fill=C('#7a9ab0')); d.line([(10, 8), (14, 4)], fill=C('#7a9ab0'), width=2); d.arc([2, 2, 9, 10], 180, 360, fill=C('#5a7a90')); d.point((15, 3), fill=C('#8ad0ff'))
    elif kind == 'hammer':
        d.line([(3, 14), (9, 6)], fill=WOOD, width=2); d.rectangle([6, 2, 14, 6], fill=STEEL); d.line([(6, 2), (14, 2)], fill=STEEL_L)
    elif kind == 'saege':
        d.polygon([(4, 4), (15, 8), (15, 11), (4, 8)], fill=STEEL); [d.point((x, 9 + (x - 4) // 3), fill=STEEL_L) for x in range(5, 15, 2)]; d.rounded_rectangle([0, 3, 5, 10], 1, fill=WOOD)
    elif kind == 'pinzette_alchemie':
        d.ellipse([2, 8, 9, 15], fill=C('#c8ccd8')); d.ellipse([4, 10, 7, 13], fill=C('#5a5468')); d.line([(7, 9), (13, 2)], fill=WOOD, width=2)  # Mörser
    return fin(im)

# ---------------------------------------------------------------- Monsterteile
def teil(kind):
    im, d = new()
    if kind == 'zahn': d.polygon([(5, 1), (11, 1), (10, 8), (8, 15), (6, 8)], fill=C('#f0ead8')); d.line([(6, 2), (7, 9)], fill=WHITE)
    elif kind == 'klaue':
        d.ellipse([1, 8, 13, 15], fill=C('#8a6a4a')); d.ellipse([3, 9, 8, 12], fill=C('#a8845a'))
        for i in range(3):
            x = 3 + i * 4; d.polygon([(x, 9), (x + 3, 9), (x + 4, 4), (x + 3, 1), (x + 2, 5)], fill=C('#f0ead8')); d.point((x + 3, 2), fill=C('#c8b898'))
    elif kind == 'horn': d.polygon([(2, 15), (7, 15), (11, 8), (14, 1), (8, 6)], fill=C('#e8dcc0')); d.line([(4, 13), (9, 7)], fill=C('#c8b898')); d.line([(3, 15), (7, 15)], fill=C('#a89878'))
    elif kind == 'schuppe': d.polygon([(8, 1), (14, 6), (12, 13), (8, 15), (4, 13), (2, 6)], fill=C('#4a9a6a')); d.polygon([(8, 3), (11, 7), (8, 12), (5, 7)], fill=C('#7ad09a')); d.point((7, 5), fill=WHITE)
    elif kind == 'fell': d.polygon([(1, 4), (6, 2), (10, 3), (15, 2), (14, 9), (15, 14), (9, 13), (3, 15), (2, 9)], fill=C('#8a6a4a')); [d.line([(x, 5), (x + 1, 11)], fill=C('#6a4e34')) for x in (4, 8, 12)]
    elif kind == 'knochen': d.line([(4, 12), (12, 4)], fill=C('#f0ead8'), width=3); [d.ellipse([x - 2, y - 2, x + 1, y + 1], fill=C('#f0ead8')) for x, y in ((3, 11), (5, 14), (11, 3), (14, 5))]
    elif kind == 'schleimkugel': d.ellipse([2, 4, 14, 15], fill=C('#6ac84a')); d.ellipse([4, 6, 8, 9], fill=C('#c8f0a8')); d.point((10, 11), fill=C('#3a8a2a'))
    elif kind == 'fluegel': d.polygon([(2, 14), (3, 3), (9, 1), (15, 4), (12, 7), (14, 10), (8, 11)], fill=C('#5a4a6a')); [d.line([(3, 13), p], fill=C('#3a2a4a')) for p in ((9, 2), (13, 6), (12, 10))]
    elif kind == 'auge': d.ellipse([2, 3, 14, 13], fill=C('#f0ead8')); d.ellipse([5, 5, 11, 11], fill=C('#c83a3a')); d.ellipse([7, 7, 9, 9], fill=INK); d.point((6, 6), fill=WHITE); d.line([(1, 14), (4, 11)], fill=C('#c83a3a'))
    elif kind == 'giftdruese': d.ellipse([3, 3, 13, 14], fill=C('#8a4a8a')); d.ellipse([5, 5, 9, 9], fill=C('#c88ac8')); d.point((12, 14), fill=C('#7ad84a')); d.point((12, 15), fill=C('#7ad84a'))
    elif kind == 'ektoplasma': d.polygon([(4, 3), (12, 3), (14, 9), (12, 15), (10, 12), (8, 15), (6, 12), (3, 14), (2, 8)], fill=C('#bfe8ff')); d.point((6, 7), fill=INK); d.point((10, 7), fill=INK); return fin(im, C('#bfe8ff'))
    elif kind == 'drachenschuppe': d.polygon([(8, 1), (14, 6), (12, 13), (8, 15), (4, 13), (2, 6)], fill=C('#b84a4a')); d.polygon([(8, 3), (11, 7), (8, 12), (5, 7)], fill=C('#e8c070')); return fin(im, C('#ff9a7a'))
    return fin(im)

# ---------------------------------------------------------------- Magisches & Edelsteine
def rolle(el):
    im, d = new(); c = ELEM[el]
    d.rectangle([3, 3, 12, 12], fill=C('#f0e4cc')); d.ellipse([1, 1, 5, 5], fill=C('#d8c8a8')); d.ellipse([10, 10, 14, 14], fill=C('#d8c8a8'))
    for y in (5, 7, 9): d.line([(5, y), (10, y)], fill=C('#a89878'))
    d.ellipse([8, 8, 12, 12], fill=c); d.point((9, 9), fill=mix(c, WHITE, .5))
    return fin(im)
def runenstein(col):
    im, d = new(); d.polygon([(3, 2), (12, 1), (14, 8), (11, 15), (4, 14), (2, 8)], fill=C('#6e687a')); d.line([(4, 3), (11, 2)], fill=C('#8a8296'))
    d.line([(8, 4), (8, 12)], fill=col); d.line([(8, 6), (11, 4)], fill=col); d.line([(8, 9), (5, 7)], fill=col)
    return fin(im, mix(col, WHITE, .4))
def edelstein(col):
    im, d = new()
    d.polygon([(4, 3), (11, 3), (14, 7), (7.5, 15), (1, 7)], fill=col); d.polygon([(4, 3), (11, 3), (12, 7), (3, 7)], fill=mix(col, WHITE, .35))
    d.line([(1, 7), (14, 7)], fill=shade(col, .7)); d.line([(7.5, 7), (7.5, 14)], fill=shade(col, .8)); d.point((5, 4), fill=WHITE)
    return fin(im, mix(col, WHITE, .5))
def sternsplitter():
    im, d = new(); pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; r = 7 if i % 2 == 0 else 3; pts.append((7.5 + math.cos(a) * r, 8 + math.sin(a) * r))
    d.polygon(pts, fill=C('#fff0a0')); d.point((7, 7), fill=WHITE)
    return fin(im, C('#fff8d0'))

# ---------------------------------------------------------------- Essen & Getränke
def gericht(kind):
    im, d = new()
    if kind in ('suppe', 'eintopf'):
        d.chord([1, 3, 14, 15], 0, 180, fill=C('#a8784a')); d.ellipse([1, 6, 14, 10], fill=C('#e0a050') if kind == 'suppe' else C('#a8583a'))
        if kind == 'eintopf': [d.point(p, fill=c) for p, c in (((4, 8), C('#ec8a3a')), ((8, 7), C('#6e9e58')), ((11, 8), C('#e8dcc0')))]
        for x in (5, 9): d.line([(x, 1), (x + 1, 4)], fill=(230, 230, 240, 255))
    elif kind == 'kuchen':
        d.polygon([(1, 9), (14, 6), (14, 13), (1, 15)], fill=C('#e8c890')); d.polygon([(1, 9), (14, 6), (14, 8), (1, 11)], fill=C('#f4ecf0'))
        d.ellipse([9, 2, 12, 6], fill=C('#d8403a')); d.line([(1, 12), (14, 10)], fill=C('#c89868'))
    elif kind == 'beerentorte':
        d.chord([1, 4, 14, 16], 0, 180, fill=C('#d8a860')); d.ellipse([1, 6, 14, 12], fill=C('#d8a860')); d.ellipse([2, 7, 13, 11], fill=C('#4a5ac8'))
        [d.point(p, fill=C('#a8b8ff')) for p in ((4, 8), (7, 9), (10, 8))]
    elif kind == 'gebratener_fisch':
        d.ellipse([1, 5, 12, 11], fill=C('#c8884a')); d.polygon([(11, 8), (15, 4), (15, 12)], fill=C('#a8683a')); [d.line([(x, 6), (x, 10)], fill=C('#8a4a2a')) for x in (4, 7)]
        d.line([(0, 14), (15, 14)], fill=C('#e8e0d0'))
    elif kind == 'honigbrot':
        d.rectangle([2, 4, 13, 14], fill=C('#d8a860')); d.rectangle([3, 5, 12, 13], fill=C('#f0d8a8')); d.rectangle([3, 5, 12, 8], fill=C('#f0b830')); d.point((6, 9), fill=C('#f0b830'))
    elif kind == 'spiess':
        d.line([(1, 14), (14, 1)], fill=WOOD); [d.ellipse([x - 2, 14 - x - 2, x + 2, 14 - x + 2], fill=c) for x, c in ((4, C('#c85a4a')), (8, C('#6e9e58')), (12, C('#c85a4a')))]
    elif kind == 'kekse':
        for x, y in ((1, 6), (6, 2), (7, 8)): d.ellipse([x, y, x + 7, y + 7], fill=C('#d8a860')); d.point((x + 2, y + 3), fill=C('#5a3a2a')); d.point((x + 5, y + 4), fill=C('#5a3a2a'))
    elif kind == 'bier':
        d.rectangle([3, 4, 11, 15], fill=C('#e8a830')); d.rectangle([3, 1, 11, 5], fill=WHITE); d.rectangle([11, 6, 14, 12], outline=C('#c8a060')); d.line([(5, 7), (5, 13)], fill=C('#f8d070'))
    elif kind == 'milch':
        d.rectangle([4, 5, 11, 15], fill=C('#f4f0e8')); d.polygon([(4, 5), (11, 5), (9, 1), (6, 1)], fill=C('#e0d8c8')); d.rectangle([4, 9, 11, 12], fill=C('#4a8ae0'))
    elif kind == 'tee':
        d.chord([2, 5, 12, 15], 0, 180, fill=C('#e8e0f0')); d.rectangle([2, 7, 12, 10], fill=C('#e8e0f0')); d.ellipse([3, 6, 11, 9], fill=C('#a8683a')); d.arc([10, 7, 15, 12], 270, 90, fill=C('#e8e0f0'))
        d.line([(6, 1), (7, 4)], fill=(230, 230, 240, 255))
    elif kind == 'saft':
        d.polygon([(3, 3), (12, 3), (11, 15), (4, 15)], fill=GLASS); d.polygon([(4, 6), (11, 6), (10, 14), (5, 14)], fill=C('#d8403a')); d.line([(9, 0), (11, 6)], fill=C('#6ab06a'))
    return fin(im)

# ---------------------------------------------------------------- Taschen & Quest
def behaelter(kind):
    im, d = new()
    if kind == 'beutel': d.ellipse([2, 4, 13, 15], fill=C('#a8804a')); d.rectangle([5, 2, 10, 5], fill=C('#a8804a')); d.line([(4, 5), (11, 5)], fill=C('#6a4a2a')); d.point((7, 10), fill=C('#c8a070'))
    elif kind == 'tasche': d.rectangle([2, 5, 13, 14], fill=C('#8a5a3a')); d.arc([4, 0, 11, 9], 180, 360, fill=C('#5a3a2a'), width=2); d.rectangle([2, 5, 13, 8], fill=C('#6a4a2a')); d.rectangle([7, 7, 8, 9], fill=g.GOLD)
    elif kind == 'rucksack':
        d.rounded_rectangle([2, 2, 13, 15], 3, fill=C('#6a7a4a')); d.rounded_rectangle([2, 2, 13, 7], 3, fill=C('#5a6a3a')); d.rectangle([4, 9, 11, 13], outline=C('#4a5a2a')); d.point((7, 7), fill=g.GOLD)
    elif kind == 'flaschenguertel':
        d.rectangle([0, 9, 15, 12], fill=C('#6a4a2a'))
        for x, c in ((2, C('#e0443a')), (7, C('#4a8ae0')), (12, C('#6ac84a'))): d.rectangle([x - 1, 4, x + 1, 9], fill=GLASS); d.rectangle([x - 1, 6, x + 1, 9], fill=c)
    elif kind == 'kistchen': d.rectangle([2, 6, 13, 14], fill=WOOD); d.rectangle([1, 4, 14, 7], fill=WOOD_L); d.rectangle([7, 7, 8, 9], fill=g.GOLD)
    return fin(im)
def quest(kind):
    im, d = new()
    if kind == 'altes_amulett': d.arc([3, 0, 12, 8], 0, 180, fill=C('#8a8296')); d.ellipse([3, 6, 12, 15], fill=C('#8a6a3a')); d.ellipse([5, 8, 10, 13], fill=C('#4a8a6a')); d.point((10, 7), fill=C('#5a4a3a'))
    elif kind == 'kartenfragment': d.polygon([(2, 3), (13, 2), (11, 8), (14, 14), (3, 13), (5, 8)], fill=C('#e8d8b0')); d.line([(4, 10), (9, 6)], fill=C('#a83a3a')); d.point((9, 6), fill=C('#a83a3a')); d.point((10, 5), fill=C('#a83a3a'))
    elif kind == 'tagebuch': d.rectangle([3, 2, 13, 14], fill=C('#5a3a5a')); d.rectangle([3, 2, 4, 14], fill=C('#3a2a3a')); d.rectangle([11, 7, 14, 9], fill=g.GOLD); d.rectangle([12, 3, 13, 13], fill=C('#f0e4cc'))
    elif kind == 'kompass': d.ellipse([2, 2, 13, 13], fill=g.GOLD); d.ellipse([3, 3, 12, 12], fill=C('#f0e4cc')); d.polygon([(7.5, 4), (9, 7.5), (7.5, 11), (6, 7.5)], fill=C('#c83a3a')); d.polygon([(7.5, 7.5), (9, 7.5), (7.5, 11), (6, 7.5)], fill=C('#5a5468'))
    elif kind == 'sanduhr': d.rectangle([3, 1, 12, 2], fill=WOOD); d.rectangle([3, 13, 12, 14], fill=WOOD); d.polygon([(4, 3), (11, 3), (8, 8), (11, 12), (4, 12), (7, 8)], fill=GLASS); d.polygon([(5, 10), (10, 10), (11, 12), (4, 12)], fill=C('#e8c070')); d.point((7, 8), fill=C('#e8c070'))
    elif kind == 'alter_schluessel': d.ellipse([1, 1, 7, 7], outline=C('#8a6a4a'), width=2); d.line([(6, 6), (14, 14)], fill=C('#8a6a4a'), width=2); d.line([(11, 11), (13, 9)], fill=C('#8a6a4a')); d.point((10, 8), fill=C('#6a8a5a'))
    elif kind == 'versiegelte_truhe': d.rectangle([1, 5, 14, 14], fill=C('#3a3446')); d.rectangle([1, 4, 14, 7], fill=C('#5a5468')); d.ellipse([5, 7, 10, 12], fill=C('#8a6ae0')); return fin(im, C('#d8c8ff'))
    elif kind == 'kronenjuwel': d.polygon([(1, 13), (1, 5), (4, 8), (7.5, 2), (11, 8), (14, 5), (14, 13)], fill=g.GOLD); d.ellipse([6, 8, 9, 11], fill=C('#c83a3a')); d.line([(1, 13), (14, 13)], fill=shade(g.GOLD, .7)); return fin(im, C('#fff0a0'))
    return fin(im)

GROUPS = {
    'traenke_mehr': [(n, flasche(C(c), f)) for n, c, f in (('staerke', '#e8603a', 'hoch'), ('schutz', '#a8acbc', 'hoch'), ('tempo', '#4ad8c8', 'kegel'),
                     ('regeneration', '#8ae06a', 'herz'), ('nachtsicht', '#8a6ad0', 'hoch'), ('wasseratmung', '#3ab0c8', 'rund'),
                     ('liebestrank', '#f088b0', 'herz'), ('glueck', '#e8d040', 'kegel'), ('heil_riesig', '#e0443a', 'riesig'),
                     ('mana_riesig', '#4a8ae0', 'riesig'), ('wurf_feuer', '#ff8a3a', 'bombe'), ('wurf_eis', '#8ad0ff', 'bombe'),
                     ('wurf_gift', '#6ac84a', 'bombe'), ('wurf_blitz', '#b880ff', 'bombe'))]
                    + [('gift', gift()), ('leere_flasche', flasche(GLASS, 'leer'))] + [(f'elixier_{e}', elixier(e)) for e in ELEM],
    'werkzeuge': [(k, werkzeug(k)) for k in ('spitzhacke', 'holzaxt', 'angel', 'sichel', 'schaufel', 'giesskanne', 'hammer', 'saege', 'pinzette_alchemie')],
    'monsterteile': [(k, teil(k)) for k in ('zahn', 'klaue', 'horn', 'schuppe', 'fell', 'knochen', 'schleimkugel', 'fluegel', 'auge', 'giftdruese', 'ektoplasma', 'drachenschuppe')],
    'magisch': [(f'schriftrolle_{e}', rolle(e)) for e in ELEM] + [('runenstein_feuer', runenstein(C('#ff8a3a'))), ('runenstein_eis', runenstein(C('#8ad0ff'))),
                ('runenstein_arkan', runenstein(C('#b880ff'))), ('sternsplitter', sternsplitter())],
    'edelsteine': [(n, edelstein(C(c))) for n, c in (('rubin', '#d8303a'), ('saphir', '#3a6ae0'), ('smaragd', '#3ab05a'), ('amethyst', '#9a5ad8'),
                   ('topas', '#e8b030'), ('diamant', '#e0f0ff'), ('onyx', '#3a3446'), ('mondstein', '#c8d8f0'))],
    'gekocht_getraenke': [(k, gericht(k)) for k in ('suppe', 'eintopf', 'kuchen', 'beerentorte', 'gebratener_fisch', 'honigbrot', 'spiess', 'kekse',
                                                    'bier', 'milch', 'tee', 'saft')],
    'taschen_quest': [(k, behaelter(k)) for k in ('beutel', 'tasche', 'rucksack', 'flaschenguertel', 'kistchen')]
                     + [(k, quest(k)) for k in ('altes_amulett', 'kartenfragment', 'tagebuch', 'kompass', 'sanduhr', 'alter_schluessel', 'versiegelte_truhe', 'kronenjuwel')],
}

def main():
    meta = {'groesse': 16, 'gruppen': {}}
    for grp, items in GROUPS.items():
        s = Image.new('RGBA', (16 * len(items), 16))
        for i, (n, im) in enumerate(items): s.alpha_composite(im, (i * 16, 0))
        s.save(os.path.join(OUT, f'{grp}.png')); meta['gruppen'][grp] = [n for n, _ in items]
    json.dump(meta, open(os.path.join(OUT, 'icons_mehr.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    S = 3; cell = 16 * S + 6; rows = []
    for grp, items in GROUPS.items():
        for k in range(0, len(items), 13): rows.append((grp if k == 0 else '', items[k:k + 13]))
    im = Image.new('RGB', (150 + 13 * cell, 30 + len(rows) * (cell + 16)), (42, 36, 69)); d = ImageDraw.Draw(im)
    d.text((8, 6), 'Weitere Inventar-Icons (16x16)', fill=(255, 240, 200), font=g.font(14))
    for r, (title, items) in enumerate(rows):
        y = 30 + r * (cell + 16); d.text((8, y + cell // 2 - 6), title, fill=(230, 220, 200), font=g.font(12))
        for i, (n, ic) in enumerate(items):
            x = 150 + i * cell; d.rectangle([x, y, x + cell - 4, y + cell - 4], fill=(58, 52, 70))
            big = ic.resize((16 * S, 16 * S), Image.NEAREST); im.paste(big, (x + 1, y + 1), big)
            d.text((x, y + cell - 2), n.replace('_', ' ')[:9], fill=(200, 190, 180), font=g.font(9))
    im.save(os.path.join(g.BASE, 'preview_icons_mehr.png'))

if __name__ == '__main__':
    main()
