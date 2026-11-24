"""Zauber-Effekte für die neun Elemente der Welt (Feuer, Eis, Wasser, Erde, Dendro, Wind, Elektro, Schatten, Licht),
Bruchklang-Explosionen für die vier Gegensatzpaare und Zauberkreise für Mehrklänge.
Aufruf: python3 magic.py
Ausgabe: effects/magie/<element>_<effekt>.png (Bilder nebeneinander), effects/magie/bruchklang_<paar>.png,
         effects/magie/kreis_<zauber>.png, effects/magie/effekte.json, preview_magie.gif
Effekte (Blick/Flug nach rechts; für andere Richtungen drehen/spiegeln):
  geschoss 4 (Schleife) · einschlag 6 · kreis 8 (Schleife, am Boden) · aura 6 (Schleife, um die Figur)
  strahl 4 (Schleife, kachelbar) · saeule 6 (Flächenzauber von oben)
"""
import os, math, random, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'effects', 'magie')
WHITE = (255, 255, 255, 255)

ELEMENTS = {  # hell, mittel, dunkel
    'feuer':   [C('#ffe9a0'), C('#ff9a3c'), C('#d8452e')],
    'eis':     [C('#ffffff'), C('#a8e0ff'), C('#5a9ad8')],
    'wasser':  [C('#e8f8ff'), C('#5ab0f0'), C('#2a6ab8')],
    'erde':    [C('#e0c898'), C('#a8804e'), C('#6a4a30')],
    'dendro':  [C('#e0f8a0'), C('#7ac84a'), C('#3a7a3a')],
    'wind':    [C('#ffffff'), C('#d8f0e8'), C('#9ac8c0')],
    'elektro': [C('#ffffff'), C('#fff07a'), C('#b880ff')],
    'schatten': [C('#b8a0e8'), C('#6a4aa8'), C('#2a1e48')],
    'licht':   [C('#ffffff'), C('#fff4c8'), C('#ffd27a')],
}
PAIRS = [('feuer', 'eis'), ('licht', 'schatten'), ('erde', 'wind'), ('wasser', 'elektro')]

def canvas(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))
def S(img, x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < img.width and 0 <= y < img.height: img.load()[x, y] = c
def disc(img, cx, cy, r, c):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x + .5 - cx)**2 + (y + .5 - cy)**2 <= r*r: S(img, x, y, c)
def outline(img, col=g.OUTLINE):
    return g.outline(img, col)

# ---------------------------------------------------------------- Geschoss
def projectile(el, t):
    L, M, D = ELEMENTS[el]; im = canvas(18, 14); cx, cy = 11, 7
    rng = random.Random(t)
    if el == 'feuer':
        for k in range(6): disc(im, cx - k*1.3, cy + math.sin(t + k)*.8, 3.2 - k*.45, [L, M, M, D, D, D][k])
        disc(im, cx + .5, cy, 2, L)
    elif el == 'eis':
        pts = [(cx + 5, cy), (cx, cy - 2.5), (cx - 4, cy), (cx, cy + 2.5)]
        ImageDraw.Draw(im).polygon(pts, fill=M); ImageDraw.Draw(im).line([(cx - 3, cy), (cx + 4, cy)], fill=L)
        for k in range(3): S(im, cx - 6 - k*2, cy + (k - 1) * ((t % 2)*2 - 1), L)
    elif el == 'wasser':
        disc(im, cx, cy, 3, M); disc(im, cx - 3, cy, 2, M); disc(im, cx - 5, cy, 1.2, D); S(im, cx + 1, cy - 1, L); S(im, cx + 1, cy - 2, L)
        for k in range(2): S(im, cx - 7 - k*2, cy + (t + k) % 3 - 1, L)
    elif el == 'erde':
        ImageDraw.Draw(im).polygon([(cx - 3, cy - 3), (cx + 3, cy - 2), (cx + 4, cy + 2), (cx - 2, cy + 3), (cx - 4, cy)], fill=M)
        S(im, cx - 1, cy - 2, L); S(im, cx, cy - 1, L); S(im, cx + 2, cy + 1, D)
        for k in range(3): S(im, cx - 6 - k*2, cy + 2 - (t + k) % 3, D)
    elif el == 'dendro':
        ImageDraw.Draw(im).ellipse([cx - 4, cy - 2, cx + 3, cy + 2], fill=M); ImageDraw.Draw(im).line([(cx - 4, cy), (cx + 3, cy)], fill=D)
        for k in range(3): S(im, cx - 6 - k*2, cy + math.sin(t + k)*2, L if k % 2 else M)
    elif el == 'wind':
        for k in range(3):
            for a in range(0, 180, 20):
                ang = math.radians(a + t*45 + k*60)
                S(im, cx - k*3 + math.cos(ang)*3, cy + math.sin(ang)*2.5, [L, M, D][k])
    elif el == 'elektro':
        disc(im, cx, cy, 2.2, L)
        x, y = cx, cy
        for k in range(4):
            nx, ny = x - 2, y + rng.choice((-2, -1, 1, 2))
            ImageDraw.Draw(im).line([(x, y), (nx, ny)], fill=M); x, y = nx, ny
        for a in range(4): S(im, cx + math.cos(a*1.6 + t)*3.5, cy + math.sin(a*1.6 + t)*3.5, D)
    elif el == 'schatten':
        disc(im, cx, cy, 3.2, D); disc(im, cx, cy, 2, M); S(im, cx, cy, L)
        for k in range(4): S(im, cx - 4 - k*1.5, cy + math.sin(t*1.5 + k)*2, D if k % 2 else M)
    elif el == 'licht':
        disc(im, cx, cy, 2.5, M); disc(im, cx, cy, 1.4, L)
        for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4)):
            if (t + dx + dy) % 2 == 0: S(im, cx + dx, cy + dy, D)
        for k in range(3): S(im, cx - 6 - k*2, cy, [M, D, D][k])
    return im

# ---------------------------------------------------------------- Einschlag
def impact(el, t):
    L, M, D = ELEMENTS[el]; im = canvas(28, 28); cx, cy = 14, 14
    r = 2 + t * 2.2
    rng = random.Random(el)
    if t < 2: disc(im, cx, cy, 3 + t*2, L if t == 0 else M)
    for k in range(18):
        a = k / 18 * 2*math.pi + rng.random()*.3
        rr = r * (.8 + rng.random()*.4)
        if t < 5 and (k + t) % 2 == 0: S(im, cx + math.cos(a)*rr, cy + math.sin(a)*rr, [L, M, D][min(2, t // 2)])
    if el in ('erde', 'dendro') and t >= 2:
        for k in range(5):
            a = k * 1.3; S(im, cx + math.cos(a)*(r*.7), cy + math.sin(a)*(r*.7) + t*.6, D)
    if el == 'elektro' and t in (1, 3):
        for k in range(3):
            x, y = cx, cy
            for _ in range(4):
                nx, ny = x + rng.choice((-3, -2, 2, 3)), y + rng.choice((-3, -2, 2, 3))
                ImageDraw.Draw(im).line([(x, y), (nx, ny)], fill=M); x, y = nx, ny
    if el == 'schatten' and t >= 1:
        disc(im, cx, cy, max(0, 4 - t*.7), D)
    return im

# ---------------------------------------------------------------- Zauberkreis (am Boden, perspektivisch)
def circle(elements, t, w=44, h=20):
    im = canvas(w, h); cx, cy = w/2, h/2; rx, ry = w/2 - 2, h/2 - 2
    cols = [ELEMENTS[e] for e in elements]
    n = 72
    for i in range(n):
        a = i / n * 2*math.pi
        seg = int((a / (2*math.pi)) * len(cols)) % len(cols)
        c = cols[seg]
        S(im, cx + math.cos(a)*rx, cy + math.sin(a)*ry, c[1])
        if i % 2 == 0: S(im, cx + math.cos(a)*(rx - 3), cy + math.sin(a)*(ry - 1.5), c[2])
    # Runen = Anzahl Elemente x 2, drehen sich
    k_ = len(cols) * 2
    for i in range(k_):
        a = i / k_ * 2*math.pi + t * (2*math.pi / 8 / k_ * 2)
        c = cols[i % len(cols)]
        x, y = cx + math.cos(a)*(rx - 1.5), cy + math.sin(a)*(ry - .8)
        S(im, x, y, c[0]); S(im, x + 1, y, c[0]); S(im, x, y - 1, c[1])
    # Innenstern
    pts = 4 + len(cols)
    for i in range(pts):
        a = i / pts * 2*math.pi - t * .2
        b = (i + 2) / pts * 2*math.pi - t * .2
        ImageDraw.Draw(im).line([(cx + math.cos(a)*(rx - 5), cy + math.sin(a)*(ry - 3)),
                                 (cx + math.cos(b)*(rx - 5), cy + math.sin(b)*(ry - 3))], fill=cols[i % len(cols)][1] if (i + t) % 3 else cols[0][0])
    return im

# ---------------------------------------------------------------- Aura (um eine 18x26-Figur, Zelle 26x30)
def aura_fx(el, t):
    L, M, D = ELEMENTS[el]; im = canvas(26, 30); rng = random.Random(el)
    for k in range(16):
        x = rng.randint(2, 23); base = rng.randint(14, 29)
        y = base - ((t * 3 + k * 5) % 16)
        if abs(x - 13) < 5 and 8 < y < 27: continue
        S(im, x, y, [L, M, D][(k + t) % 3])
        if el in ('feuer', 'licht', 'elektro'): S(im, x, y + 1, D)
    for x in range(4, 23):
        if (x + t) % 3 == 0: S(im, x, 28, M)
    return im

# ---------------------------------------------------------------- Strahl (kachelbar 16x10)
def beam(el, t):
    L, M, D = ELEMENTS[el]; im = canvas(16, 10)
    for x in range(16):
        wv = math.sin((x + t*4) / 16 * 2*math.pi * 2)
        for y in range(2, 8):
            d = abs(y - 4.5 - wv*.8)
            if d < 1: S(im, x, y, L)
            elif d < 2: S(im, x, y, M)
            elif d < 3 and (x + t) % 2 == 0: S(im, x, y, D)
    return im

# ---------------------------------------------------------------- Säule / Flächenzauber von oben
def column(el, t):
    L, M, D = ELEMENTS[el]; im = canvas(28, 56); cx = 14
    reach = min(56, 10 + t * 14)
    wdt = [3, 6, 8, 8, 6, 3][t]
    for y in range(reach):
        for x in range(int(cx - wdt), int(cx + wdt) + 1):
            d = abs(x - cx) / max(1, wdt)
            if el in ('erde', 'dendro'):
                yy = 55 - y
                if (x * 7 + yy * 3) % 5 == 0 or d < .3: S(im, x, yy, M if d < .5 else D)
            else:
                if d < .35: S(im, x, y, L)
                elif d < .7: S(im, x, y, M)
                elif (x + y + t) % 2 == 0: S(im, x, y, D)
    if t >= 2:
        for k in range(10):
            a = k / 10 * math.pi
            S(im, cx + math.cos(a) * (wdt + 3), 54 - math.sin(a) * 3, M)
    return im

# ---------------------------------------------------------------- Bruchklang
def bruch(a, b, t):
    A, B = ELEMENTS[a], ELEMENTS[b]; im = canvas(48, 48); cx, cy = 24, 24
    rng = random.Random(t * 7)
    if t < 3:
        r = 4 + t * 2
        for k in range(40):
            ang = rng.random() * 2*math.pi; rr = rng.random() * r
            S(im, cx + math.cos(ang)*rr, cy + math.sin(ang)*rr, (A if math.cos(ang) > 0 else B)[k % 3])
        for k in range(t + 2):
            x, y = cx, cy
            for _ in range(4):
                nx, ny = x + rng.choice((-3, 3)), y + rng.choice((-3, -2, 2, 3))
                ImageDraw.Draw(im).line([(x, y), (nx, ny)], fill=WHITE); x, y = nx, ny
    elif t == 3:
        disc(im, cx, cy, 14, WHITE); disc(im, cx, cy, 10, A[0])
    else:
        r = 10 + (t - 3) * 5
        for k in range(60):
            ang = k / 60 * 2*math.pi; rr = r * (.75 + rng.random() * .35)
            if (k + t) % 2: S(im, cx + math.cos(ang)*rr, cy + math.sin(ang)*rr, (A if k % 2 else B)[min(2, t - 3)])
        if t < 7:
            for k in range(12):
                S(im, cx + rng.randint(-r//2, r//2), cy + rng.randint(-r//2, r//2), C('#6a6070'))
    return im

# ---------------------------------------------------------------- Mehrklang-Zauber aus der Bibel der Welt
SPELLS = {
    'heilung': ['licht', 'wasser'], 'dampfstoss': ['feuer', 'wasser'], 'stille': ['wind', 'schatten'],
    'dornenwall': ['erde', 'dendro'], 'kettenblitz': ['wind', 'elektro'],
    'sumpfgrab': ['wasser', 'erde', 'dendro'], 'bannlicht': ['licht', 'wind', 'feuer'], 'frostgewitter': ['eis', 'wind', 'elektro'],
    'laeuterung': ['licht', 'wasser', 'erde', 'dendro'], 'aschesturm': ['feuer', 'wind', 'erde', 'schatten'],
    'seelenmagie': ['licht', 'schatten'], 'teleport': ['licht', 'elektro'],
}

EFFECTS = [('geschoss', 4, projectile), ('einschlag', 6, impact), ('kreis', 8, lambda el, t: circle([el], t)),
           ('aura', 6, aura_fx), ('strahl', 4, beam), ('saeule', 6, column)]

def strip(frames):
    w, h = frames[0].size; s = canvas(w * len(frames), h)
    for i, f in enumerate(frames): s.alpha_composite(f, (i * w, 0))
    return s

def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'elemente': list(ELEMENTS), 'effekte': {}, 'bruchklang': [], 'kreise': {}}
    store = {}
    for el in ELEMENTS:
        for name, n, fn in EFFECTS:
            fr = [fn(el, t) for t in range(n)]
            if name in ('geschoss',): fr = [outline(f, shade(ELEMENTS[el][2], .55)) for f in fr]
            strip(fr).save(os.path.join(OUT, f'{el}_{name}.png'))
            meta['effekte'][name] = {'bilder': n, 'groesse': list(fr[0].size)}
            store[(el, name)] = fr
    for a, b in PAIRS:
        fr = [bruch(a, b, t) for t in range(8)]
        strip(fr).save(os.path.join(OUT, f'bruchklang_{a}_{b}.png')); meta['bruchklang'].append(f'{a}_{b}')
        store[('bruch', a)] = fr
    for sp, els in SPELLS.items():
        fr = [circle(els, t) for t in range(8)]
        strip(fr).save(os.path.join(OUT, f'kreis_{sp}.png')); meta['kreise'][sp] = els
        store[('kreis', sp)] = fr
    meta['hinweis'] = ('Geschoss/Strahl fliegen nach rechts. Kreis liegt unter den Füßen. Aura-Zelle 26x30 passt mittig '
                       'über eine Figur (Füße unten). Säule fällt von oben auf den Zielpunkt (unten Mitte).')
    json.dump(meta, open(os.path.join(OUT, 'effekte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau
    Sc = 3; els = list(ELEMENTS)
    colw = 60 * Sc
    W_ = 120 + len(els) * colw; rows = ['geschoss', 'einschlag', 'kreis', 'aura', 'strahl', 'saeule']
    rh = [16, 28, 20, 30, 10, 56]
    H_ = 40 + sum(h * Sc + 10 for h in rh) + 60 * Sc
    frames = []
    for t in range(8):
        im = Image.new('RGB', (W_, H_), (42, 36, 69)); d = ImageDraw.Draw(im)
        for i, el in enumerate(els): d.text((120 + i * colw, 10), el.capitalize(), fill=(255, 240, 200), font=g.font(14))
        y = 40
        for rname, h in zip(rows, rh):
            d.text((8, y + h*Sc//2 - 8), rname, fill=(230, 220, 200), font=g.font(13))
            for i, el in enumerate(els):
                fr = store[(el, rname)]; f = fr[t % len(fr)]
                if rname == 'strahl': f = strip([f, f, f])
                big = f.resize((f.width * Sc, f.height * Sc), Image.NEAREST)
                im.paste(big, (120 + i * colw, y), big)
            y += h * Sc + 10
        d.text((8, y + 20), 'Bruchklang', fill=(230, 220, 200), font=g.font(13))
        for i, (a, b) in enumerate(PAIRS):
            f = store[('bruch', a)][t]; big = f.resize((48 * Sc, 48 * Sc), Image.NEAREST)
            im.paste(big, (120 + i * 2 * colw, y), big)
            d.text((120 + i * 2 * colw + 150, y + 60), f'{a} + {b}', fill=(230, 220, 200), font=g.font(12))
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_magie.gif'), save_all=True, append_images=frames[1:], duration=120, loop=0)
    # Kreise der Mehrklänge
    kf = []
    for t in range(8):
        im = Image.new('RGB', (6 * 150 + 20, 2 * 110 + 20), (42, 36, 69)); d = ImageDraw.Draw(im)
        for i, sp in enumerate(SPELLS):
            x, y = 10 + (i % 6) * 150, 10 + (i // 6) * 110
            f = store[('kreis', sp)][t]; big = f.resize((44 * 3, 20 * 3), Image.NEAREST)
            im.paste(big, (x, y + 20), big)
            d.text((x, y), sp, fill=(255, 240, 200), font=g.font(12))
            d.text((x, y + 84), ' + '.join(SPELLS[sp]), fill=(200, 190, 175), font=g.font(10))
        kf.append(im)
    kf[0].save(os.path.join(g.BASE, 'preview_zauberkreise.gif'), save_all=True, append_images=kf[1:], duration=120, loop=0)
    frames[2].save(os.path.join(g.BASE, 'preview_magie.png'))

if __name__ == '__main__':
    main()
