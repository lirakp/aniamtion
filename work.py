"""Arbeitsschleifen für Dorfbewohner (Seitenansicht, Blick nach rechts, 8 Frames, Schleife).
Aufruf: python3 work.py
Ausgabe: characters/arbeit/<job>.png (8 Frames à 48x34), characters/arbeit/arbeit.json, preview_arbeit.gif
Die Figur steht bei (12, 8) in der Zelle, Füße auf y=33. Requisiten (Amboss, Tisch …) sind mit im Bild.
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
import platformer  # registriert zusätzliche Arm-/Beinposen
import combat as cb, races as rc

OUT = os.path.join(g.BASE, 'characters', 'arbeit')
W, H, N = 48, 34, 8
CX, CY = 12, 8
INK, WHITE = C('#2b1e33'), C('#ffffff')
WOOD, WOOD_D = g.WOOD, g.WOOD_D
IRON, IRON_L, IRON_D = C('#6a6e80'), C('#a8acbc'), C('#3e4050')
R = {r['name']: r for r in rc.RACES}

def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1; return dx / L, dy / L
def add(p, v, k): return (p[0] + v[0] * k, p[1] + v[1] * k)

def figure(race, outfit, arm, legs='stand', dy=0, blink=False):
    img, hands = cb.compose(R[race], outfit, 'side', legs=legs, arm=arm, dy=dy, blink=blink)
    off = 2 if R[race].get('dwarf') else 0
    sh = (CX + 9, CY + 14 + dy + off); hand = (CX + hands[0][0], CY + hands[0][1])
    return img, hand, unit(sh, hand)

def frame(): im = Image.new('RGBA', (W, H)); return im, ImageDraw.Draw(im)
def put(im, fig): im.alpha_composite(fig, (CX, CY))
def perp(v): return (-v[1], v[0])

# ---------------------------------------------------------------- Requisiten
def amboss(d):
    d.polygon([(29, 27), (41, 27), (39, 29), (32, 29)], fill=IRON); d.line([(29, 27), (41, 27)], fill=IRON_L)
    d.polygon([(26, 27), (29, 27), (29, 28)], fill=IRON); d.rectangle([33, 29, 38, 31], fill=IRON_D); d.rectangle([31, 31, 40, 33], fill=WOOD_D)
def tisch(d, top=24):
    d.rectangle([24, top, 44, top + 2], fill=WOOD); d.line([(24, top), (44, top)], fill=g.WOOD_L); d.rectangle([26, top + 3, 27, 33], fill=WOOD_D); d.rectangle([41, top + 3, 42, 33], fill=WOOD_D)
def klotz(d):
    d.rectangle([28, 27, 38, 33], fill=WOOD); d.ellipse([28, 25, 38, 29], fill=C('#c8a070')); d.ellipse([31, 26, 35, 28], outline=WOOD)
def blumen(d, t):
    for x, c in ((34, C('#e888a8')), (38, C('#f0e070')), (42, C('#a8c8ff'))):
        d.line([(x, 33), (x, 28)], fill=g.LEAF_D); d.point((x - 1, 30), fill=g.LEAF); d.ellipse([x - 1, 26 - (t % 4 == 0 and x == 38), x + 1, 28], fill=c)
def wasser(d):
    d.rectangle([22, 31, 47, 33], fill=C('#3a6ab0')); d.line([(22, 31), (47, 31)], fill=C('#8ac0f0'))
def theke(d):
    d.rectangle([28, 22, 47, 33], fill=WOOD); d.rectangle([27, 21, 47, 22], fill=g.WOOD_L)
    for y in (26, 30): d.line([(29, y), (46, y)], fill=WOOD_D)

# ---------------------------------------------------------------- Werkzeuge an der Hand
def hammer(d, hand, v, big=False):
    end = add(hand, v, 5); d.line([hand, end], fill=WOOD, width=1)
    p = perp(v); a, b = add(end, p, -2), add(end, p, 2); d.line([a, b], fill=IRON, width=2); d.point(a, fill=IRON_L)
def axt(d, hand, v):
    end = add(hand, v, 7); d.line([add(hand, v, -1), end], fill=WOOD)
    p = perp(v); d.polygon([add(end, p, -1), add(add(end, p, -4), v, 1), add(add(end, p, -4), v, -3), add(end, v, -2)], fill=IRON_L)
def hacke(d, hand, v):
    a, end = add(hand, v, -4), add(hand, v, 9); d.line([a, end], fill=WOOD)
    p = perp(v); d.line([end, add(add(end, p, -3), v, -1)], fill=IRON_L, width=2)
def besen(d, hand, sweep):
    v = unit((0, 0), (.55 + sweep, 1)); k = (32 - hand[1]) / v[1]; end = add(hand, v, k)
    d.line([add(hand, v, -5), end], fill=WOOD); x, y = end
    d.polygon([(x - 2, y - 1), (x + 2, y - 1), (x + 4, 33), (x - 3, 33)], fill=C('#d8b860')); d.line([(x - 2, y - 1), (x + 2, y - 1)], fill=C('#a8302a'))
def kanne(d, hand, tilt):
    x, y = hand; body = C('#7a9ab0')
    d.rectangle([x, y - 1, x + 5, y + 3], fill=body); d.line([(x + 5, y), (x + 9, y - 2 + tilt * 3)], fill=body, width=1)
    d.arc([x - 2, y - 3, x + 3, y + 2], 180, 300, fill=shade(body, .7))
def schale(d, x, y, sq):
    d.ellipse([x - 4 - sq, y - 3 + sq, x + 4 + sq, y + 1], fill=C('#f0e0c0')); d.line([(x - 2, y - 2 + sq), (x + 1, y - 2 + sq)], fill=WHITE)
def krug(d, hand):
    x, y = hand; d.rectangle([x, y - 4, x + 3, y], fill=C('#c8a060')); d.rectangle([x, y - 5, x + 3, y - 4], fill=WHITE); d.point((x + 4, y - 2), fill=C('#c8a060'))
def speer(d, hand):
    x, y = hand; d.line([(x, y - 13), (x, 33)], fill=WOOD); d.polygon([(x - 1, y - 13), (x + 1, y - 13), (x, y - 17)], fill=IRON_L)
def angel(d, hand, t, catch):
    x, y = hand; tip = (x + 13, y - 10); d.line([hand, tip], fill=WOOD)
    by = 31 + (t % 2) if not catch else 26 - (t - 6) * 3
    d.line([tip, (tip[0] + 3, by)], fill=C('#e8e0d0'))
    if catch: d.polygon([(tip[0] + 1, by), (tip[0] + 5, by), (tip[0] + 3, by + 5)], fill=C('#8aa8c8'))
    else: d.point((tip[0] + 3, by), fill=C('#e84a3a'))
def funken(d, c, t):
    for i in range(4):
        a = -math.pi / 2 + (i - 1.5) * .6; r = 2 + t
        d.point(add(c, (math.cos(a), math.sin(a)), r), fill=C('#ffd27a') if i % 2 else C('#ff9a3c'))
def puenktchen(d, c, t, col):
    for i in range(3): d.point((c[0] - 2 + i * 2 + (i - 1) * t, c[1] - t - (i % 2)), fill=col)

# ---------------------------------------------------------------- Jobs: Liste von Frames
def schmied():
    seq = [('hinten_oben', 0), ('hinten_oben', 0), ('hoch', 0), ('vorne', 0), ('vorne', 1), ('vorne', 1), ('hoch', 0), ('hoch', 0)]
    out = []
    for i, (arm, dy) in enumerate(seq):
        im, d = frame(); amboss(d); d.rectangle([31, 25, 36, 26], fill=C('#ff8a3a') if i < 5 else C('#d8452e'))  # glühendes Eisen
        fig, hand, v = figure('zwerg', 'tunika', arm, dy=dy, blink=i == 6); put(im, fig); hammer(d, hand, v)
        if i in (4, 5): funken(d, (31, 25), i - 3)
        out.append(im)
    return out
def baecker():
    out = []
    for i in range(N):
        arm = ['vorne', 'fwd', 'fwd', 'vorne'][i % 4]; press = arm == 'fwd'
        im, d = frame(); tisch(d); schale(d, 31, 23, 1 if press else 0)
        if i == 5: puenktchen(d, (33, 18), 1, WHITE)
        fig, hand, v = figure('mensch', 'tunika', arm, dy=1 if press else 0, blink=i == 3); put(im, fig); out.append(im)
    return out
def holzfaeller():
    seq = ['hinten_oben', 'hinten_oben', 'hoch', 'vorne', 'fwd', 'fwd', 'mid', 'mid']
    out = []
    for i, arm in enumerate(seq):
        im, d = frame(); klotz(d)
        split = i in (4, 5, 6)
        if split: d.rectangle([29, 20, 31, 25], fill=C('#c8a070')); d.rectangle([35 + (i - 4), 20 + (i - 4), 37 + (i - 4), 25], fill=C('#c8a070'))
        else: d.rectangle([30, 19, 36, 25], fill=C('#c8a070')); d.line([(30, 19), (36, 19)], fill=WOOD)
        fig, hand, v = figure('wolf', 'tunika', arm, dy=1 if arm == 'fwd' else 0); put(im, fig); axt(d, hand, v)
        if i == 4: puenktchen(d, (33, 20), 2, C('#e0c090'))
        out.append(im)
    return out
def bauer():
    seq = ['hoch', 'hoch', 'vorne', 'fwd', 'fwd', 'mid', 'mid', 'vorne']
    out = []
    for i, arm in enumerate(seq):
        im, d = frame(); d.rectangle([20, 32, 47, 33], fill=C('#6a4a30'))
        for x in (30, 37, 44): d.line([(x, 31), (x, 29)], fill=g.LEAF); d.point((x - 1, 29), fill=g.LEAF_L)
        fig, hand, v = figure('hase', 'tunika', arm, dy=1 if arm == 'fwd' else 0, blink=i == 6); put(im, fig); hacke(d, hand, v)
        if i in (3, 4): puenktchen(d, (31, 31), i - 2, C('#8a6a4a'))
        out.append(im)
    return out
def kehrer():
    out = []
    for i in range(N):
        arm = ['fwd', 'fwd', 'mid', 'mid'][i % 4]
        im, d = frame(); fig, hand, v = figure('katze', 'tunika', arm, legs='pass' if i % 4 < 2 else 'stand', blink=i == 5); put(im, fig); besen(d, hand, .5 if arm == 'fwd' else -.1)
        if arm == 'mid': puenktchen(d, (30 + (i % 2) * 2, 32), 1 + i % 2, C('#c8b8a0'))
        out.append(im)
    return out
def wirt():
    out = []
    for i in range(N):
        im, d = frame(); theke(d)
        arm = 'vorne' if i % 4 < 2 else 'brust'
        fig, hand, v = figure('fuchs', 'tunika', arm, blink=i == 2); put(im, fig)
        x = 36 + int(math.cos(i / N * 4 * math.pi) * 2)
        d.rectangle([34, 16, 38, 20], fill=C('#c8d8e0')); d.rectangle([39, 17, 40, 19], outline=C('#c8d8e0'))
        d.rectangle([x - 2, 17, x + 1, 19], fill=C('#e8e0d0')); d.line([hand, (x - 2, 18)], fill=C('#e8e0d0'))  # Tuch
        if i in (3, 7): d.point((33, 15), fill=WHITE); d.point((32, 16), fill=WHITE) if False else None
        out.append(im)
    return out
def fischer():
    out = []
    for i in range(N):
        im, d = frame(); wasser(d); d.rectangle([0, 31, 21, 33], fill=WOOD); d.line([(0, 31), (21, 31)], fill=g.WOOD_L)
        catch = i >= 6
        fig, hand, v = figure('frosch', 'tunika', 'hoch' if catch else 'vorne', dy=-2 + 0 if False else -2, blink=i == 2); put(im, fig)
        angel(d, hand, i, catch)
        if catch: puenktchen(d, (39, 30), i - 5, C('#8ac0f0'))
        out.append(im)
    return out
def haendler():
    out = []
    for i in range(N):
        im, d = frame(); tisch(d, 25)
        for k, c in enumerate((C('#e0b048'), C('#c8ccd8'), C('#e0b048'))): d.ellipse([33 + k * 3, 23, 35 + k * 3, 24], fill=c)
        arm = 'vorne' if i < 4 else 'hoch' if i < 6 else 'vorne'
        fig, hand, v = figure('echse', 'tunika', arm, blink=i == 7); put(im, fig)
        if 3 <= i <= 6:
            y = [18, 10, 8, 14][i - 3]; x = hand[0] + 1
            d.ellipse([x, y, x + 2 - (i % 2), y + 2], fill=C('#e0b048')); d.point((x, y), fill=WHITE)
        out.append(im)
    return out
def wache():
    out = []
    for i in range(N):
        im, d = frame(); dy = 1 if i in (3, 4) else 0
        fig, hand, v = figure('hund', 'ruestung', 'mid', dy=dy, blink=i in (2, 6)); put(im, fig); speer(d, (hand[0] + 2, hand[1] - 1))
        if i in (4, 5): d.text((CX + 13, CY - 6 + (i - 4)), 'z', fill=C('#d8e8ff'))  # döst kurz ein
        out.append(im)
    return out
def gaertner():
    out = []
    for i in range(N):
        im, d = frame(); blumen(d, i); tilt = 1 if 2 <= i <= 5 else 0
        fig, hand, v = figure('elf', 'tunika', 'vorne', blink=i == 7); put(im, fig); kanne(d, hand, tilt)
        if tilt:
            for k in range(3): d.point((hand[0] + 9 + k % 2, hand[1] + 1 + k * 3 + (i % 2)), fill=C('#8ad0ff'))
        out.append(im)
    return out

JOBS = {'schmied': (schmied, 'Zwerg hämmert auf dem Amboss'), 'baecker': (baecker, 'Mensch knetet Teig'),
        'holzfaeller': (holzfaeller, 'Wolf spaltet Holz'), 'bauer': (bauer, 'Hase hackt das Feld'),
        'kehrer': (kehrer, 'Katze fegt'), 'wirt': (wirt, 'Fuchs poliert einen Krug'),
        'fischer': (fischer, 'Frosch angelt und fängt einen Fisch'), 'haendler': (haendler, 'Echse wirft eine Münze'),
        'wache': (wache, 'Hund in Rüstung hält Wache und döst'), 'gaertner': (gaertner, 'Elf gießt Blumen')}

def main():
    os.makedirs(OUT, exist_ok=True); meta = {'zelle': [W, H], 'frames': N, 'fps': 8, 'figur_offset': [CX, CY], 'jobs': {}}
    all_frames = {}
    for name, (fn, desc) in JOBS.items():
        fr = [g.outline(f) if False else f for f in fn()]; all_frames[name] = fr
        s = Image.new('RGBA', (W * N, H))
        for i, f in enumerate(fr): s.alpha_composite(f, (i * W, 0))
        s.save(os.path.join(OUT, f'{name}.png')); meta['jobs'][name] = desc
    json.dump(meta, open(os.path.join(OUT, 'arbeit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    Z, cols = 3, 5; cw, chh = W * Z + 8, H * Z + 22; names = list(JOBS); rows = math.ceil(len(names) / cols)
    frames = []
    for t in range(N):
        im = Image.new('RGB', (cols * cw + 8, rows * chh + 8), (42, 36, 69)); d = ImageDraw.Draw(im)
        for i, n in enumerate(names):
            x, y = 8 + (i % cols) * cw, 8 + (i // cols) * chh
            d.rectangle([x, y, x + W * Z - 1, y + H * Z - 1], fill=(74, 62, 88))
            c = all_frames[n][t].resize((W * Z, H * Z), Image.NEAREST); im.paste(c, (x, y), c)
            d.text((x + 2, y + H * Z + 4), n, fill=(230, 220, 200), font=g.font(12))
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_arbeit.gif'), save_all=True, append_images=frames[1:], duration=130, loop=0)

if __name__ == '__main__':
    main()
