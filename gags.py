"""Gag-Animationen, viele davon direkt aus den Lachnummern der Bibel der Welt.
Aufruf: python3 gags.py
Ausgabe: welt/gags/<name>.png (Bilder nebeneinander), Einträge in welt/welt.json, preview_gags.gif
"""
import os, sys, math, random, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
import combat as cb, races as rc
from dungeon import F, chest, preview, strip

sys.path.insert(0, os.path.join(g.BASE, 'monster'))
from classify import OVR, build_spec
from render import render_all

OUT = os.path.join(g.BASE, 'welt', 'gags')
WHITE, INK = (255, 255, 255, 255), C('#2b1e33')

# ---------------------------------------------------------------- Mini-Schrift 3x5
FONT = {
    'A': ['010', '101', '111', '101', '101'], 'C': ['011', '100', '100', '100', '011'], 'E': ['111', '100', '110', '100', '111'],
    'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
    'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'], 'N': ['1001', '1101', '1011', '1001', '1001'],
    'O': ['010', '101', '101', '101', '010'], 'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'],
    'V': ['101', '101', '101', '101', '010'], 'W': ['101', '101', '111', '111', '101'], 'Z': ['111', '001', '010', '100', '111'],
    'D': ['110', '101', '101', '101', '110'], 'R': ['110', '101', '110', '101', '101'], 'U': ['101', '101', '101', '101', '111'],
    'F': ['111', '100', '110', '100', '100'], 'M': ['10001', '11011', '10101', '10001', '10001'], 'P': ['110', '101', '110', '100', '100'],
    '?': ['110', '001', '010', '000', '010'], '!': ['010', '010', '010', '000', '010'], '.': ['000', '000', '000', '000', '010'],
    ' ': ['000', '000', '000', '000', '000'],
}
def twidth(s): return sum(len(FONT[ch][0]) + 1 for ch in s) - 1
def text(img, x, y, s, col=INK):
    p = img.load(); cx = x
    for ch in s:
        for r, row in enumerate(FONT[ch]):
            for c, b in enumerate(row):
                X, Y = cx + c, y + r
                if b == '1' and 0 <= X < img.width and 0 <= Y < img.height: p[X, Y] = col
        cx += len(FONT[ch][0]) + 1
def bubble(img, x, y, s, tail='left'):
    w = twidth(s) + 4
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + 8], fill=WHITE, outline=INK)
    tx = x + 3 if tail == 'left' else x + w - 4
    d.polygon([(tx, y + 8), (tx + 3, y + 8), (tx + (-1 if tail == 'left' else 4), y + 11)], fill=WHITE)
    d.line([(tx, y + 9), (tx + (-1 if tail == 'left' else 4), y + 11)], fill=INK)
    text(img, x + 2, y + 2, s)

def place(dst, src, x, y): dst.alpha_composite(src, (int(x), int(y)))
def canvas(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def door(img, x, y, open_=0):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 1, y - 1, x + 12, y + 22], fill=g.WOOD_D)
    if open_:
        d.rectangle([x, y, x + 11, y + 22], fill=C('#140e18'))
        w = 12 - open_ * 4
        d.rectangle([x, y, x + w - 1, y + 22], fill=g.DOORWOOD)
        if open_ >= 1:
            for k in range(3): d.point((x + 12 - 2 * k, y + 10 + k), fill=C('#8a8098'))
    else:
        d.rectangle([x, y, x + 11, y + 22], fill=g.DOORWOOD)
        for xx in range(x + 2, x + 11, 3): d.line([(xx, y), (xx, y + 22)], fill=shade(g.DOORWOOD, .75))
        d.point((x + 2, y + 12), fill=g.GOLD)

# ---------------------------------------------------------------- 1) Adliger klopft an die eigene Tür
NOBLE = dict(rc.RACES[0], tunic=C('#6a3a8a'), hair=('kurz', C('#d8b070')))
def adliger(t):
    im = canvas(56, 40)
    door(im, 38, 14, open_=[0, 0, 0, 0, 0, 1, 2, 2, 1, 0][t])
    arm = 'vorne' if t in (1, 3) else 'brust' if t in (0, 2, 4) else 'mid'
    fig, _ = cb.compose(NOBLE, 'tunika', 'side', arm=arm, blink=t in (6, 7))
    p = fig.load()
    for x, y in ((7, 4), (8, 3), (9, 4), (10, 3), (11, 4)): p[x, y] = g.GOLD
    dx = 0 if t < 6 else -2 if t < 8 else -1
    shiver = (t in (6, 7)) * (1 if t % 2 else -1)
    place(im, fig, 16 + dx + shiver, 12)
    d = ImageDraw.Draw(im)
    if t in (1, 3):
        for k, (a, b) in enumerate(((36, 22), (35, 20))): d.point((a, b - k), fill=WHITE)
        text(im, 26, 2, 'KNOCK'[:0] or '')
    if t in (6, 7):
        for k in range(3): d.point((14 + k * 2, 10 - (k % 2)), fill=C('#8ac4ee'))
    if t == 8: bubble(im, 4, 0, '...')
    return im

# ---------------------------------------------------------------- 2) Goblin-Schamane wedelt mit Rauch
_GOB = None
def goblin_schamane(t):
    global _GOB
    if _GOB is None:
        sp = build_spec({'name': 'Goblin-Schamane', 'rang': 'D', 'merkmal': '', 'lebensraum': '', 'schwaeche': ''})
        sp['px'] = 32; _GOB = render_all(sp)[0]
    im = canvas(56, 44)
    seq = _GOB['attack'] + _GOB['attack'][:2] + [_GOB['idle'][0]] * 4
    fr = seq[t]
    place(im, fr, 4, im.height - fr.height - 2)
    d = ImageDraw.Draw(im)
    r = min(7, 2 + t * .8)
    if t < 8:
        cx, cy = 34 + t * .5, 22 - t
        for k in range(4):
            d.ellipse([cx + k * 3 - r * .6, cy - (k % 2) * 3 - r * .6, cx + k * 3 + r * .6, cy - (k % 2) * 3 + r * .6], fill=(170, 164, 180, 200))
        if t in (3, 5):
            for k in range(3): d.point((30 + k * 5, 12 + k), fill=(240, 240, 255, 255))
    else:
        for k in range(3): d.ellipse([38 + k * 4, 6 + (t - 8) * -1 + k, 40 + k * 4, 8 + (t - 8) * -1 + k], fill=(170, 164, 180, 90))
        bubble(im, 22, 0, '...' if t < 10 else '?')
        d.point((24, 22), fill=C('#8ac4ee')); d.point((24, 23 + (t % 2)), fill=C('#8ac4ee'))
    return im

# ---------------------------------------------------------------- 3) Brief aus Nebelhain
DARKELF = next(r for r in rc.RACES if r['name'] == 'dunkelelf')
def brief(t):
    im = canvas(56, 40)
    door(im, 36, 14)
    d = ImageDraw.Draw(im)
    if 1 <= t <= 4:
        fig, _ = cb.compose(DARKELF, 'tunika', 'side', legs='contact', arm='vorne' if t == 3 else 'mid')
        x = [0, -2, 12, 22, 40][t]
        ghost = fig.copy(); gp = ghost.load()
        for y in range(26):
            for xx in range(18):
                c = gp[xx, y]
                if c[3]: gp[xx, y] = c[:3] + (200 if t == 3 else 110,)
        place(im, ghost, x, 13)
        for k in range(4): d.line([(x - 4 - k * 3, 20 + k * 3), (x - 1 - k * 3, 20 + k * 3)], fill=(120, 110, 150, 140))
    if t >= 3:
        lx, ly = 28, 34
        d.rectangle([lx, ly, lx + 6, ly + 4], fill=C('#f0e4cc')); d.line([(lx, ly), (lx + 3, ly + 2), (lx + 6, ly)], fill=C('#c8b898'))
        d.point((lx + 3, ly + 2), fill=C('#a83a3a'))
        if t >= 5 and t % 2: d.point((lx + 7, ly - 1), fill=WHITE); d.point((lx - 1, ly - 2), fill=C('#fff4c8'))
    if t >= 6: bubble(im, 2, 2, '?', tail='right')
    return im

# ---------------------------------------------------------------- 4) Vakanter Lehrstuhl wird abgestaubt
def vakant(t):
    f = F(48, 44, seed=t)
    gold, red = C('#c89a3a'), C('#7a2a3a')
    f.rect(12, 6, 15, 38, gold); f.rect(32, 6, 35, 38, gold)
    f.rect(12, 6, 35, 9, gold); f.ell(18, 0, 29, 8, gold)
    f.rect(15, 10, 32, 24, red); f.rect(12, 24, 35, 28, gold); f.rect(13, 25, 34, 27, red)
    f.rect(13, 29, 15, 40, gold); f.rect(32, 29, 34, 40, gold)
    f.rect(17, 14, 30, 20, C('#f0e4cc'))
    img = g.outline(f.im); text(img, 17, 15, 'VAKANT', INK) if False else None
    sign = canvas(48, 44); ds = ImageDraw.Draw(sign)
    ds.rectangle([9, 13, 38, 21], fill=C('#f0e4cc'), outline=INK); text(sign, 11, 15, 'VAKANT')
    img.alpha_composite(sign)
    d = ImageDraw.Draw(img)
    sw = math.sin(t / 6 * 2*math.pi)
    hx, hy = 24 + sw * 12, 6 + abs(sw) * 3
    d.line([(hx, hy), (hx + 6, hy - 8)], fill=g.WOOD, width=2)
    for k in range(5): d.line([(hx, hy), (hx - 3 + k * 1.5, hy + 4)], fill=[C('#e8e0f0'), C('#c84a4a'), C('#e0b048')][k % 3])
    for k in range(3):
        y = hy + 6 + ((t + k) % 4) * 2
        d.point((hx - 2 + k * 2, y), fill=(220, 210, 190, 180))
    return img

# ---------------------------------------------------------------- 5) Skelett niest und zerfällt
_SK = None
def skelett(t):
    global _SK
    if _SK is None:
        sp = build_spec({'name': 'Skelettkrieger', 'rang': 'D', 'merkmal': '', 'lebensraum': '', 'schwaeche': ''})
        sp['px'] = 30; _SK = render_all(sp)[0]['idle'][0]
    base = _SK; w, h = base.size
    im = canvas(56, 44); oy = im.height - h - 2; ox = 18
    pieces = []
    rows = [(0, int(h * .32)), (int(h * .32), int(h * .62)), (int(h * .62), h)]
    for i, (a, b) in enumerate(rows): pieces.append((base.crop((0, a, w, b)), a))
    if t < 2:
        place(im, base, ox, oy + (1 if t == 1 else 0))
        if t == 1: bubble(im, 30, 2, 'HA..')
    elif t == 2:
        place(im, base, ox - 1, oy); bubble(im, 26, 0, 'TSCHI!')
    elif t <= 7:
        k = min(1, (t - 2) / 3)
        for i, (pc, a) in enumerate(pieces):
            fall = (h - pc.height - a) * k
            dx = [10, -6, 3][i] * k
            place(im, pc, ox + dx, oy + a + fall)
        if t >= 6: bubble(im, 2, 0, '...')
    else:
        k = max(0, 1 - (t - 7) / 3)
        for i, (pc, a) in enumerate(pieces):
            fall = (h - pc.height - a) * k; dx = [10, -6, 3][i] * k
            place(im, pc, ox + dx, oy + a + fall)
        if t == 10:
            d = ImageDraw.Draw(im)
            for k_ in range(3): d.point((ox + w + 2, oy + 4 + k_ * 3), fill=WHITE)
    return im

# ---------------------------------------------------------------- 6) Mimik-Truhe niest Münzen
def mimik_niest(t):
    im = canvas(64, 48)
    anim, k = [('zu', 0), ('oeffnen', 1), ('oeffnen', 1), ('zu', 0), ('oeffnen', 3), ('oeffnen', 3), ('offen', 0), ('zu', 0)][t]
    ch = chest('holz', anim, k if anim != 'zu' else 0)
    place(im, ch, 8, 6 + (1 if t == 3 else 0))
    d = ImageDraw.Draw(im)
    for x in (18, 27): d.rectangle([x, 31, x + 1, 32], fill=C('#ffd27a') if t not in (3,) else INK)
    if t in (1, 2): bubble(im, 30, 0, 'HA..', tail='left')
    if t in (4, 5):
        bubble(im, 30, 0, 'TSCHI!', tail='left')
        rng = random.Random(t)
        for i in range(10):
            x = 24 + rng.uniform(-14, 14) * (t - 3); y = 14 - rng.uniform(0, 10) + (t - 4) * 6
            d.rectangle([x, y, x + 1, y + 1], fill=g.GOLD if i % 2 else C('#fff0a0'))
    if t >= 6:
        for i in range(6): d.rectangle([10 + i * 5, 44, 11 + i * 5, 45], fill=g.GOLD)
        d.point((16, 33), fill=C('#e8897a')); d.point((30, 33), fill=C('#e8897a'))
    return im

# ---------------------------------------------------------------- 7) Baum auf dem Holzweg
_TREE = None
def holzweg(t):
    global _TREE
    if _TREE is None:
        sp = build_spec({'name': 'Wanderbaum', 'rang': 'C', 'merkmal': '', 'lebensraum': '', 'schwaeche': ''})
        sp['px'] = 30; _TREE = render_all(sp)[0]
    im = canvas(84, 48)
    d = ImageDraw.Draw(im)
    d.rectangle([56, 22, 57, 46], fill=g.WOOD_D)
    d.polygon([(46, 14), (77, 14), (81, 18), (77, 22), (46, 22)], fill=g.WOOD); d.line([(46, 14), (77, 14)], fill=g.WOOD_L)
    text(im, 48, 16, 'HOLZWEG', C('#f0e4cc'))
    if t < 6:
        fr = _TREE['move'][t % 6]; x = 2 + t * 3
    else:
        fr = _TREE['idle'][t % 4]; x = 2 + 5 * 3
    place(im, fr, x, im.height - fr.height - 1)
    if 7 <= t <= 9: bubble(im, x + 8, 0, '?')
    if t >= 10:
        bubble(im, x + 4, 0, 'OH...')
    return im

# ---------------------------------------------------------------- 8) Hyänenmensch wird „Gnoll“ genannt
HY = next(r for r in rc.RACES if r['name'] == 'hyaene')
def gnoll(t):
    im = canvas(48, 44)
    arm = 'brust' if t >= 3 else 'unten'
    fig, _ = cb.compose(HY, 'tunika', 'front', arm=arm, blink=t in (3, 4))
    if t >= 3:
        red = min(.45, (t - 2) * .12)
        fig = cb.tint(fig, C('#e03a3a'), red)
    stomp = 1 if t in (5, 7, 9) else 0
    place(im, fig, 16, 16 + stomp)
    if t in (0, 1, 2): bubble(im, 0, 2, 'GNOLL?', tail='right')
    d = ImageDraw.Draw(im)
    if t >= 4:
        for k in range(2):
            y = 14 - ((t * 2 + k * 3) % 8); x = 20 + k * 8
            d.ellipse([x - 1, y - 1, x + 2, y + 2], fill=(235, 235, 245, 200))
    if t >= 6:
        ax, ay = 34, 6 + (t % 2)
        for a_, b_ in (((ax, ay), (ax + 3, ay + 3)), ((ax + 5, ay), (ax + 2, ay + 3)), ((ax, ay + 6), (ax + 3, ay + 3)), ((ax + 5, ay + 6), (ax + 2, ay + 3))):
            d.line([a_, b_], fill=C('#e03a3a'))
    if t >= 8: bubble(im, 0, 0, 'HYAENE!', tail='right') if False else bubble(im, 2, 0, 'NEIN!', tail='right')
    return im

# ---------------------------------------------------------------- 9) Drachenmensch bekommt einen Fangauftrag auf seinen Namen
DRAKE = next(r for r in rc.RACES if r['name'] == 'drache')
def fangauftrag(t):
    im = canvas(56, 44)
    holding = t >= 3
    fig, hands = cb.compose(DRAKE, 'tunika', 'front', arm='brust' if holding else 'unten', blink=t in (6,))
    place(im, fig, 19, 16 + (1 if t == 6 else 0))
    d = ImageDraw.Draw(im)
    if t < 3:
        x = 2 + t * 9; y = 20 - math.sin(t / 3 * math.pi) * 8
        d.rectangle([x, y, x + 6, y + 4], fill=C('#f0e4cc')); d.line([(x, y), (x + 3, y + 2), (x + 6, y)], fill=C('#c8b898'))
    else:
        d.rectangle([24, 26, 33, 33], fill=C('#f0e4cc'), outline=C('#c8b898'))
        for k in range(3): d.line([(26, 28 + k * 2), (31, 28 + k * 2)], fill=C('#8a7a6a'))
        d.point((32, 32), fill=C('#c83a3a'))
    if t in (4, 5): bubble(im, 24, 2, 'FANG?')
    if t in (6, 7): bubble(im, 26, 2, 'ICH?!')
    if t >= 8:
        bubble(im, 22, 2, 'DRACHE...')
        for k in range(2):
            y = 22 - ((t + k) % 3) * 2
            d.ellipse([25 + k * 4, y - 1, 27 + k * 4, y + 1], fill=(150, 144, 160, 200))
    if t in (6, 7, 8): d.point((20, 18), fill=C('#8ac4ee')); d.point((20, 19 + t % 2), fill=C('#8ac4ee'))
    return im

# ---------------------------------------------------------------- 10) Der Zwergenkönig regiert den Schnee
DWARF = dict(next(r for r in rc.RACES if r['name'] == 'zwerg'), tunic=C('#6a3a8a'))
def zwergenkoenig(t):
    im = canvas(56, 48)
    arm = 'hoch_r' if 2 <= t <= 6 else 'unten'
    fig, _ = cb.compose(DWARF, 'tunika', 'front', arm=arm, blink=t >= 8)
    p = fig.load()
    for x, y in ((6, 4), (7, 3), (8, 4), (9, 3), (10, 4), (11, 3)):
        if 0 <= y < 26: p[x + 1, y + 2] = g.GOLD
    place(im, fig, 19, 20)
    d = ImageDraw.Draw(im)
    rng = random.Random(1)
    for i in range(26):
        x0, y0 = rng.uniform(0, 56), rng.uniform(0, 48)
        d.point(((x0 + math.sin(t + i) * 1.5) % 56, (y0 + t * 3) % 48), fill=WHITE)
    pile = min(4, max(0, t - 3))
    if pile: d.ellipse([23, 26 - pile, 34, 27], fill=WHITE)
    if 2 <= t <= 4: bubble(im, 30, 2, 'HALT!')
    if t == 5 or t == 6: bubble(im, 30, 2, 'HALT!!')
    if t >= 8: bubble(im, 4, 2, '...', tail='right')
    d.rectangle([0, 46, 55, 47], fill=WHITE)
    return im

# ---------------------------------------------------------------- 11) Die Elfen-Batterie geht mitten im Kampf aus
FIGHTER = rc.RACES[0]; ELF = next(r for r in rc.RACES if r['name'] == 'elf')
def batterie(t):
    im = canvas(72, 44)
    elf, _ = cb.compose(ELF, 'tunika', 'front', arm='brust', blink=t in (4,))
    place(im, elf, 52, 16)
    d = ImageDraw.Draw(im)
    d.ellipse([57, 33, 65, 37], fill=C('#c83a3a')); d.ellipse([58, 31, 64, 34], fill=WHITE)
    if t % 3 == 1: d.point((62, 26 - (t % 2)), fill=WHITE)
    arm = 'vorne' if t >= 2 else 'brust'
    fig, hands = cb.compose(FIGHTER, 'ruestung', 'side', legs='contact' if t >= 2 else 'stand', arm=arm)
    place(im, fig, 8, 16)
    bx, by = 4, 26
    d.rectangle([bx, by, bx + 4, by + 9], fill=C('#5a5468'), outline=INK)
    charge = [3, 3, 2, 1, 1, 0, 0, 0, 0, 0][t]
    for k in range(3):
        d.rectangle([bx + 1, by + 7 - k * 3, bx + 3, by + 8 - k * 3], fill=C('#8ad8ff') if k < charge else C('#2a2430'))
    hx, hy = hands[0][0] + 8, hands[0][1] + 16
    if t in (2, 3):
        r = 2 + t
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=C('#8ad8ff')); d.ellipse([hx - 1, hy - 1, hx + 1, hy + 1], fill=WHITE)
    if t == 4:
        d.ellipse([hx - 2, hy - 2, hx + 2, hy + 2], fill=C('#5a8ab0'))
    if t in (5, 6):
        for k in range(3): d.ellipse([hx + k * 3, hy - 2 - k * 2, hx + 3 + k * 3, hy + 1 - k * 2], fill=(150, 144, 160, 200))
        d.point((hx + 2, hy + 2), fill=C('#8ad8ff'))
    if 5 <= t <= 7: bubble(im, 14, 2, '...')
    if t >= 7:
        d.point((60, 22), fill=INK); d.line([(57, 25), (62, 25)], fill=INK) if False else None
        bubble(im, 40, 2, 'HI HI', tail='right')
    return im

GAGS = [('adliger_klopft', 'Adliger klopft an die eigene Tür', adliger, 10),
        ('goblin_schamane_rauch', 'Goblin-Schamane wedelt mit Rauch', goblin_schamane, 11),
        ('brief_aus_nebelhain', 'Brief aus Nebelhain', brief, 8),
        ('vakanter_lehrstuhl', 'Vakanter Lehrstuhl wird abgestaubt', vakant, 6),
        ('skelett_niest', 'Skelett niest und zerfällt', skelett, 11),
        ('mimik_niest', 'Mimik niest Münzen', mimik_niest, 8),
        ('holzweg', 'Baum auf dem Holzweg', holzweg, 12),
        ('nicht_gnoll', '"Gnoll?" – beleidigter Hyänenmensch', gnoll, 10),
        ('fangauftrag', 'Drachenmensch: Fangauftrag auf eigenen Namen', fangauftrag, 10),
        ('zwergenkoenig_schnee', 'Der Zwergenkönig regiert den Schnee', zwergenkoenig, 10),
        ('elfen_batterie', 'Elfen-Batterie geht im Kampf aus', batterie, 10)]

def main():
    os.makedirs(OUT, exist_ok=True)
    meta_path = os.path.join(g.BASE, 'welt', 'welt.json')
    meta = json.load(open(meta_path, encoding='utf-8'))
    meta['gags'] = {}
    prev = []
    for key, title, fn, n in GAGS:
        fr = [fn(t) for t in range(n)]
        strip(fr).save(os.path.join(OUT, f'{key}.png'))
        meta['gags'][key] = {'titel': title, 'bilder': n, 'bild': list(fr[0].size), 'schleife': key in ('vakanter_lehrstuhl',)}
        prev.append((title, fr))
    json.dump(meta, open(meta_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(prev, os.path.join(g.BASE, 'preview_gags.gif'), S=4, cols=4, n_frames=12, title='Gags')

if __name__ == '__main__':
    main()
