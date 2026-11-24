"""Benutzeroberfläche für den Plattformer.
Aufruf: python3 ui.py
Ausgabe: ui/<element>.png, ui/schrift_*.png, ui/ui.json, preview_ui.gif
"""
import os, json, math, random
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'ui')
WHITE, INK = (255, 255, 255, 255), C('#2b1e33')
GOLD, GOLD_L, GOLD_D = C('#e0b048'), C('#fff0a0'), C('#a87a2a')
RANKS = ['D', 'C', 'B', 'A', 'S', 'SS']
RANK_COL = {'D': C('#9a94a8'), 'C': C('#6ab06a'), 'B': C('#5a9ad8'), 'A': C('#b880ff'), 'S': C('#e0b048'), 'SS': C('#e0443a')}

# ---------------------------------------------------------------- Pixel-Schrift 3x5 (M, N, W, Q breiter)
GLYPHS = {
    'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
    'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
    'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
    'J': ['001', '001', '001', '101', '010'], 'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'],
    'M': ['10001', '11011', '10101', '10001', '10001'], 'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'],
    'P': ['110', '101', '110', '100', '100'], 'Q': ['0110', '1001', '1001', '1011', '0111'], 'R': ['110', '101', '110', '101', '101'],
    'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'], 'U': ['101', '101', '101', '101', '111'],
    'V': ['101', '101', '101', '101', '010'], 'W': ['10001', '10001', '10101', '11011', '10001'], 'X': ['101', '101', '010', '101', '101'],
    'Y': ['101', '101', '010', '010', '010'], 'Z': ['111', '001', '010', '100', '111'],
    'Ä': ['101', '010', '101', '111', '101'], 'Ö': ['101', '000', '111', '101', '111'], 'Ü': ['101', '000', '101', '101', '111'],
    '0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'], '2': ['110', '001', '010', '100', '111'],
    '3': ['111', '001', '011', '001', '111'], '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '110', '001', '110'],
    '6': ['011', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'], '8': ['111', '101', '111', '101', '111'],
    '9': ['111', '101', '111', '001', '110'], '+': ['000', '010', '111', '010', '000'], '-': ['000', '000', '111', '000', '000'],
    '!': ['1', '1', '1', '0', '1'], '?': ['110', '001', '010', '000', '010'], '.': ['0', '0', '0', '0', '1'], ',': ['0', '0', '0', '1', '1'], ':': ['0', '1', '0', '1', '0'],
    ' ': ['00', '00', '00', '00', '00'], '/': ['001', '001', '010', '100', '100'],
}
def twidth(s, scale=1): return (sum(len(GLYPHS[c][0]) + 1 for c in s) - 1) * scale
def text(img, x, y, s, col=INK, scale=1, shadow=None):
    p = img.load()
    for pass_, (ox, oy, cc) in enumerate(((1, 1, shadow), (0, 0, col)) if shadow else ((0, 0, col),)):
        cx = x
        for ch in s:
            gl = GLYPHS[ch]
            for r, row in enumerate(gl):
                for c, b in enumerate(row):
                    if b != '1': continue
                    for sy in range(scale):
                        for sx in range(scale):
                            X, Y = cx + c * scale + sx + ox, y + r * scale + sy + oy
                            if 0 <= X < img.width and 0 <= Y < img.height: p[X, Y] = cc
            cx += (len(gl[0]) + 1) * scale

def font_sheet():
    chars = ''.join(GLYPHS.keys())
    im = Image.new('RGBA', (len(chars) * 6, 5)); x = 0; meta = {}
    for ch in chars:
        text(im, x, 0, ch, WHITE); meta[ch] = [x, len(GLYPHS[ch][0])]; x += 6
    return im, meta

# ---------------------------------------------------------------- Leben (Herzen)
def heart(fill=1.0, col=C('#e0443a'), crack=0, glow=0):
    im = Image.new('RGBA', (13, 12)); d = ImageDraw.Draw(im)
    shape = ['0110001100000', '1111011110000', '1111111111000', '1111111111000', '0111111110000', '0011111100000', '0001111000000', '0000110000000']
    shape = ['01100110', '11111111', '11111111', '11111111', '01111110', '00111100', '00011000']
    p = im.load()
    for y, row in enumerate(shape):
        for x, b in enumerate(row):
            if b != '1': continue
            X, Y = x * 1 + 2, y + 2
            lvl = (len(shape) - y) / len(shape)
            c = col if lvl <= fill + 1e-6 else C('#3a2a3a')
            if c == col and (x, y) in ((1, 1), (2, 1), (1, 2)): c = mix(col, WHITE, .5)
            p[X, Y] = c
    if crack:
        for k, (x, y) in enumerate(((5, 2), (6, 3), (5, 4), (6, 5), (5, 6))):
            if k < crack: p[x, y] = INK
    im = g.outline(im)
    if glow:
        q = im.load()
        for y in range(12):
            for x in range(13):
                if not q[x, y][3] and any(0 <= x + dx < 13 and 0 <= y + dy < 12 and q[x + dx, y + dy][3] == 255 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and (x + y + glow) % 2:
                    q[x, y] = (255, 240, 160, 200)
    return im

# ---------------------------------------------------------------- Mana-Gefäß
def mana_vessel(level, t=0, col=C('#5ab0f0'), colL=C('#bfe8ff')):
    im = Image.new('RGBA', (22, 24)); d = ImageDraw.Draw(im)
    d.ellipse([2, 6, 19, 23], fill=C('#2a2438')); d.rectangle([7, 1, 14, 7], fill=C('#2a2438'))
    top = 22 - int(level * 16)
    for y in range(max(top, 7), 23):
        for x in range(3, 19):
            if (x - 10.5) ** 2 / 64 + (y - 14.5) ** 2 / 72 <= 1:
                wv = math.sin((x + t * 2) * .9) if y == top else 0
                if y + wv >= top: im.load()[x, y] = colL if y <= top + 1 else col
    for k in range(2):
        by = 22 - ((t * 3 + k * 5) % max(2, int(level * 16)))
        if level > .1 and by > top: im.load()[7 + k * 6, by] = colL
    d.ellipse([2, 6, 19, 23], outline=C('#c8ccd8')); d.rectangle([7, 1, 14, 6], outline=C('#c8ccd8'))
    d.rectangle([6, 0, 15, 2], fill=C('#8a6a4a')); d.point((5, 10), fill=WHITE); d.point((5, 11), fill=WHITE)
    return g.outline(im)

def rank_badge(r):
    im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im); c = RANK_COL[r]
    d.polygon([(8, 0), (15, 4), (15, 11), (8, 15), (1, 11), (1, 4)], fill=shade(c, .6))
    d.polygon([(8, 2), (13, 5), (13, 10), (8, 13), (3, 10), (3, 5)], fill=c)
    tw = twidth(r); text(im, 8 - tw // 2, 5, r, WHITE, shadow=shade(c, .4))
    return g.outline(im)

# ---------------------------------------------------------------- Schadenszahlen
NUM_STYLES = {'normal': (WHITE, INK), 'kritisch': (C('#ffd27a'), C('#8a2a1a')), 'heilung': (C('#8ae06a'), C('#1e4a1e')),
              'mana': (C('#8ad8ff'), C('#1e3a6a')), 'gift': (C('#c8f07a'), C('#3a5a1a')), 'block': (C('#b8bccc'), C('#3a3446'))}
def digits(style):
    col, sh = NUM_STYLES[style]; sc = 2 if style == 'kritisch' else 1
    chars = '0123456789+-!'
    cw = 4 * sc + 1
    im = Image.new('RGBA', (len(chars) * cw, 6 * sc + 1))
    for i, ch in enumerate(chars): text(im, i * cw, 0, ch, col, sc, shadow=sh)
    return im

def number_popup(value, style, t):
    """Beispiel-Animation einer aufsteigenden Zahl (8 Bilder)."""
    col, sh = NUM_STYLES[style]; sc = 2 if style == 'kritisch' else 1
    s = ('+' if style in ('heilung', 'mana') else '') + str(value) + ('!' if style == 'kritisch' else '')
    im = Image.new('RGBA', (40, 30))
    y = 18 - t * 2 + (0 if t > 1 else -t)
    bounce = 1 if t == 1 else 0
    if t < 7:
        tmp = Image.new('RGBA', (40, 30)); text(tmp, 20 - twidth(s, sc) // 2, y - bounce, s, col, sc, shadow=sh)
        if t >= 5:
            p = tmp.load()
            for yy in range(30):
                for xx in range(40):
                    c = p[xx, yy]
                    if c[3] and (xx + yy) % (2 if t == 5 else 1) == 0 and t == 6: p[xx, yy] = (0, 0, 0, 0)
                    elif c[3] and t == 5 and (xx + yy) % 2 == 0: p[xx, yy] = c[:3] + (150,)
        im.alpha_composite(tmp)
    return im

# ---------------------------------------------------------------- Rahmen (9-Slice)
def frame9(style):
    """24x24, Ecken 8 px: holz, pergament, dungeon, magie"""
    im = Image.new('RGBA', (24, 24)); d = ImageDraw.Draw(im)
    if style == 'holz':
        d.rectangle([0, 0, 23, 23], fill=g.WOOD_D); d.rectangle([2, 2, 21, 21], fill=g.WOOD); d.rectangle([4, 4, 19, 19], fill=C('#3a2a32'))
        d.line([(2, 2), (21, 2)], fill=g.WOOD_L)
        for x, y in ((3, 3), (20, 3), (3, 20), (20, 20)): d.point((x, y), fill=GOLD)
    elif style == 'pergament':
        d.rectangle([0, 0, 23, 23], fill=C('#a8885a')); d.rectangle([1, 1, 22, 22], fill=C('#f0e4cc')); d.rectangle([3, 3, 20, 20], fill=C('#f4ecd8'))
        for k in range(0, 24, 3): d.point((k, 1), fill=C('#d8c8a8')); d.point((1, k), fill=C('#d8c8a8'))
    elif style == 'dungeon':
        d.rectangle([0, 0, 23, 23], fill=C('#16121c')); d.rectangle([1, 1, 22, 22], fill=C('#3e384c')); d.rectangle([3, 3, 20, 20], fill=C('#1e1a26'))
        for x, y in ((1, 1), (22, 1), (1, 22), (22, 22)): d.point((x, y), fill=C('#7a7488'))
        d.line([(3, 3), (20, 3)], fill=C('#2a2432'))
    elif style == 'magie':
        d.rectangle([0, 0, 23, 23], fill=C('#2a1e48')); d.rectangle([1, 1, 22, 22], fill=C('#6a4aa8')); d.rectangle([3, 3, 20, 20], fill=C('#1e1a3a'))
        for x, y in ((2, 2), (21, 2), (2, 21), (21, 21)): d.point((x, y), fill=C('#e0d0ff'))
        for k in range(4, 20, 4): d.point((k, 2), fill=C('#b8a0ff')); d.point((k, 21), fill=C('#b8a0ff'))
    return im

def button(state, w=24, h=12):
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    base = {'normal': C('#5a4a6a'), 'hover': C('#7a5a8a'), 'gedrueckt': C('#3e3248'), 'aus': C('#3a3640')}[state]
    off = 1 if state == 'gedrueckt' else 0
    d.rectangle([0, 0, w - 1, h - 1], fill=INK); d.rectangle([1, 1 + off, w - 2, h - 2], fill=base)
    if state != 'gedrueckt': d.line([(1, 1), (w - 2, 1)], fill=mix(base, WHITE, .3)); d.line([(1, h - 2), (w - 2, h - 2)], fill=shade(base, .7))
    if state == 'hover':
        for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): d.point((x, y), fill=GOLD)
    return im

def cursor(kind, t=0):
    im = Image.new('RGBA', (12, 12)); d = ImageDraw.Draw(im)
    if kind == 'pfeil':
        d.polygon([(1, 1), (1, 10), (4, 7), (6, 11), (8, 10), (6, 6), (10, 6)], fill=WHITE)
    elif kind == 'hand':
        d.rectangle([4, 1, 5, 6], fill=C('#f2c69b')); d.rectangle([2, 5, 9, 10], fill=C('#f2c69b'))
        for x in (6, 8): d.rectangle([x, 4, x + 1, 6], fill=C('#f2c69b'))
    elif kind == 'auswahl':
        o = t % 2
        for x, y, dx, dy in ((0, 0, 1, 1), (11, 0, -1, 1), (0, 11, 1, -1), (11, 11, -1, -1)):
            d.line([(x + dx * o, y + dy * o), (x + dx * (3 + o), y + dy * o)], fill=GOLD_L); d.line([(x + dx * o, y + dy * o), (x + dx * o, y + dy * (3 + o))], fill=GOLD_L)
        return im
    return g.outline(im)

def slot(rank=None, selected=False, t=0):
    im = Image.new('RGBA', (20, 20)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 19, 19], fill=INK); d.rectangle([1, 1, 18, 18], fill=C('#3a3446')); d.rectangle([2, 2, 17, 17], fill=C('#2a2432'))
    if rank:
        c = RANK_COL[rank]; d.rectangle([1, 1, 18, 18], outline=c)
        if rank in ('S', 'SS'):
            for k in range(4): d.point(((t * 3 + k * 5) % 18 + 1, 1), fill=mix(c, WHITE, .6))
    if selected:
        o = t % 2
        d.rectangle([0 - o + o, 0, 19, 19], outline=GOLD_L if t % 2 else GOLD)
    return im

def weiter_pfeil(t):
    im = Image.new('RGBA', (8, 8)); y = [0, 1, 2, 1][t]
    ImageDraw.Draw(im).polygon([(1, 2 + y), (6, 2 + y), (3.5, 5 + y)], fill=GOLD_L)
    return g.outline(im)

def muenze(t):
    im = Image.new('RGBA', (10, 10)); d = ImageDraw.Draw(im)
    w_ = [4, 3, 1, 0, 1, 3][t]
    d.ellipse([5 - w_, 1, 5 + w_, 8], fill=GOLD) if w_ else d.line([(5, 1), (5, 8)], fill=GOLD_D)
    if w_ >= 3: d.line([(5, 3), (5, 6)], fill=GOLD_D); d.point((5 - w_ + 1, 3), fill=GOLD_L)
    return g.outline(im)

def banner(title, col, t, w=112, h=36):
    """Stufenaufstieg / Auftrag erledigt (10 Bilder)."""
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    k = min(1, (t + 1) / 3)
    bw = int(w * k)
    if t < 9:
        x0 = (w - bw) // 2
        d.rectangle([x0, 10, x0 + bw - 1, 25], fill=shade(col, .45)); d.rectangle([x0, 11, x0 + bw - 1, 24], fill=shade(col, .7))
        d.polygon([(x0, 10), (x0 - 4, 17.5), (x0, 25)], fill=shade(col, .45)); d.polygon([(x0 + bw - 1, 10), (x0 + bw + 3, 17.5), (x0 + bw - 1, 25)], fill=shade(col, .45))
        if t >= 2:
            tmp = Image.new('RGBA', (w, h)); text(tmp, w // 2 - twidth(title) // 2, 15, title, WHITE, shadow=shade(col, .3))
            if t == 8:
                p = tmp.load()
                for y in range(h):
                    for x in range(w):
                        if p[x, y][3] and (x + y) % 2: p[x, y] = (0, 0, 0, 0)
            im.alpha_composite(tmp)
        if 2 <= t <= 6:
            for i in range(10):
                a = i / 10 * 2*math.pi + t * .3; r = 18 + t * 4
                x, y = w / 2 + math.cos(a) * r, 17 + math.sin(a) * r * .35
                if 0 <= x < w and 0 <= y < h: im.load()[int(x), int(y)] = GOLD_L if i % 2 else WHITE
    return im

def nine(src, w, h, c=8):
    """9-Slice: Ecken bleiben, Kanten und Mitte werden gekachelt."""
    W, H = src.size; out = Image.new('RGBA', (w, h))
    parts = lambda x0, y0, x1, y1: src.crop((x0, y0, x1, y1))
    mid = parts(c, c, W - c, H - c); top = parts(c, 0, W - c, c); bot = parts(c, H - c, W - c, H); lef = parts(0, c, c, H - c); rig = parts(W - c, c, W, H - c)
    for y in range(c, h - c, mid.height):
        for x in range(c, w - c, mid.width): out.paste(mid, (x, y))
    for x in range(c, w - c, top.width): out.paste(top, (x, 0)); out.paste(bot, (x, h - c))
    for y in range(c, h - c, lef.height): out.paste(lef, (0, y)); out.paste(rig, (w - c, y))
    out.paste(parts(0, 0, c, c), (0, 0)); out.paste(parts(W - c, 0, W, c), (w - c, 0)); out.paste(parts(0, H - c, c, H), (0, h - c)); out.paste(parts(W - c, H - c, W, H), (w - c, h - c))
    return out

# ---------------------------------------------------------------- Export
def save(im, name):
    im.save(os.path.join(OUT, name + '.png'))

def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w * len(frames), h))
    for i, f in enumerate(frames): s.alpha_composite(f, (i * w, 0))
    return s

def main():
    os.makedirs(OUT, exist_ok=True); meta = {}
    fs, fmeta = font_sheet(); save(fs, 'schrift_3x5'); meta['schrift_3x5'] = {'hoehe': 5, 'zeichen': fmeta, 'hinweis': '[x, breite] je Zeichen, 1 px Abstand'}
    hearts = {'voll': heart(1), 'halb': heart(.5), 'leer': heart(0)}
    save(strip(list(hearts.values())), 'herz_zustaende'); meta['herz_zustaende'] = ['voll', 'halb', 'leer']
    save(strip([heart(1, crack=k) for k in range(5)] + [heart(0)]), 'herz_verlust'); meta['herz_verlust'] = {'bilder': 6}
    save(strip([heart(k / 4, glow=k) for k in range(5)]), 'herz_heilen'); meta['herz_heilen'] = {'bilder': 5}
    save(strip([mana_vessel(k / 8) for k in range(9)]), 'mana_fuellstand'); meta['mana_fuellstand'] = {'stufen': 9, 'hinweis': '0/8 bis 8/8'}
    save(strip([mana_vessel(.75, t) for t in range(4)]), 'mana_blubbern'); meta['mana_blubbern'] = {'bilder': 4, 'schleife': True}
    save(strip([rank_badge(r) for r in RANKS]), 'mana_rang'); meta['mana_rang'] = RANKS
    for st in NUM_STYLES:
        save(digits(st), f'zahlen_{st}')
        save(strip([number_popup(127 if st != 'kritisch' else 348, st, t) for t in range(8)]), f'zahl_aufsteigen_{st}')
    meta['zahlen'] = {'zeichen': '0123456789+-!', 'stile': list(NUM_STYLES), 'hinweis': 'zahl_aufsteigen_* = Beispiel-Ablauf (8 Bilder)'}
    for st in ('holz', 'pergament', 'dungeon', 'magie'): save(frame9(st), f'rahmen_{st}')
    meta['rahmen'] = {'groesse': 24, 'ecken': 8, 'stile': ['holz', 'pergament', 'dungeon', 'magie'], 'hinweis': '9-Slice: Ecken 8 px, Mitte dehnen'}
    save(strip([button(s) for s in ('normal', 'hover', 'gedrueckt', 'aus')]), 'knopf'); meta['knopf'] = {'zustaende': ['normal', 'hover', 'gedrueckt', 'aus'], 'hinweis': '9-Slice, Ecken 3 px'}
    save(strip([cursor('pfeil'), cursor('hand')]), 'zeiger'); save(strip([cursor('auswahl', t) for t in range(2)]), 'auswahlrahmen')
    save(strip([slot()] + [slot(r) for r in RANKS] + [slot(selected=True)]), 'inventar_slot')
    meta['inventar_slot'] = ['leer'] + [f'rang_{r}' for r in RANKS] + ['ausgewaehlt']
    save(strip([weiter_pfeil(t) for t in range(4)]), 'dialog_weiter'); save(strip([muenze(t) for t in range(6)]), 'muenze_dreht')
    lvl = [banner('STUFE AUF!', C('#e0b048'), t) for t in range(10)]
    quest = [banner('AUFTRAG ERLEDIGT', C('#5a9a6a'), t) for t in range(10)]
    death = [banner('BESIEGT', C('#a83a3a'), t) for t in range(10)]
    dung = [banner('DUNGEON GELÖST', C('#6a4aa8'), t) for t in range(10)]
    for n, fr in (('banner_stufe_auf', lvl), ('banner_auftrag_erledigt', quest), ('banner_besiegt', death), ('banner_dungeon_geloest', dung)):
        save(strip(fr), n); meta[n] = {'bilder': 10}
    json.dump(meta, open(os.path.join(OUT, 'ui.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau: eine HUD-Szene
    frames = []
    for t in range(10):
        im = Image.new('RGBA', (240, 160), C('#2a2445'))
        mv = mana_vessel(.75, t % 4); im.alpha_composite(mv, (6, 6))
        for i in range(5):
            hrt = heart(1) if i < 3 else heart(.5) if i == 3 else heart(0)
            if i == 2 and t >= 4: hrt = heart(1, crack=min(4, t - 4)) if t < 9 else heart(0)
            im.alpha_composite(hrt, (30 + i * 12, 8))
        im.alpha_composite(rank_badge('B'), (30, 20))
        cn = muenze(t % 6); im.alpha_composite(cn, (196, 8)); tt = Image.new('RGBA', (30, 8)); text(tt, 0, 1, '429', GOLD_L, shadow=INK); im.alpha_composite(tt, (208, 8))
        for i, st in enumerate(('normal', 'kritisch', 'heilung', 'mana')):
            im.alpha_composite(number_popup([12, 348, 25, 10][i], st, t % 8), (20 + i * 50, 40))
        box = Image.new('RGBA', (180, 34)); f9 = frame9('holz')
        box.alpha_composite(nine(f9, 180, 34))
        text(box, 10, 9, 'WILLKOMMEN IN COSY!', WHITE, shadow=INK); text(box, 10, 18, 'DRÜCKE E ZUM SPRECHEN.', C('#e8dcc0'))
        box.alpha_composite(weiter_pfeil(t % 4), (164, 22))
        im.alpha_composite(box, (30, 80))
        for i, r in enumerate([None] + RANKS):
            im.alpha_composite(slot(r, selected=(i == 3), t=t), (14 + i * 22, 122))
        im.alpha_composite(lvl[t], (120, 118 - 70)) if False else None
        frames.append(im.resize((480, 320), Image.NEAREST).convert('RGB'))
    frames[0].save(os.path.join(g.BASE, 'preview_ui.gif'), save_all=True, append_images=frames[1:], duration=140, loop=0)
    bn = []
    for t in range(10):
        im = Image.new('RGBA', (240, 170), C('#2a2445'))
        for i, fr in enumerate((lvl, quest, death, dung)): im.alpha_composite(fr[t], (64, 4 + i * 40))
        bn.append(im.resize((480, 340), Image.NEAREST).convert('RGB'))
    bn[0].save(os.path.join(g.BASE, 'preview_ui_banner.gif'), save_all=True, append_images=bn[1:], duration=140, loop=0)
    frames[4].save('/tmp/claude-0/-home-user/12f6a153-289c-51b2-bfa7-11e2d78969f5/scratchpad/ui.png'); bn[5].save('/tmp/claude-0/-home-user/12f6a153-289c-51b2-bfa7-11e2d78969f5/scratchpad/bn.png')

if __name__ == '__main__':
    main()
