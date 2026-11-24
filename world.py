"""Details für die Welt außerhalb der Dungeons.
Aufruf: python3 world.py
Ausgabe: welt/<gruppe>/<name>.png (Bilder nebeneinander), welt/welt.json,
         preview_welt_lore.gif, preview_welt_dorf.gif, preview_welt_natur.gif, preview_welt_hilfen.gif
Gruppen: lore (Welt-Lore aus der Bibel), dorf (Dorfleben), natur (Natur & Wetter), hilfen (Spielhilfen)
"""
import os, math, random, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
from dungeon import F, preview, strip
import combat as cb, races as rc

OUT = os.path.join(g.BASE, 'welt')
WHITE = (255, 255, 255, 255)
MANA, MANA_L = C('#8ad8ff'), C('#f0fcff')
BLOOD_MOON = [C('#ffb0a0'), C('#e0443a'), C('#8a1e2a')]
LEAF, LEAF_D, LEAF_L = g.LEAF, g.LEAF_D, g.LEAF_L
HUMAN = rc.RACES[0]

def fig(arm='unten', blink=False, race=None, outfit='tunika', view='front'):
    im, hands = cb.compose(race or HUMAN, outfit, view, arm=arm, blink=blink); return im, hands

def place(dst, src, x, y):
    dst.alpha_composite(src, (int(x), int(y)))

def alpha(c, a): return c[:3] + (int(max(0, min(255, a))),)

# ================================================================ LORE
def huelle(stage):
    """Dungeon-Außenhülle in der Welt. stage: ruhig, unruhig, kritisch, ausbruch"""
    speed = {'ruhig': 1, 'unruhig': 2, 'kritisch': 3, 'ausbruch': 3}[stage]
    col = {'ruhig': [C('#e0f4ff'), C('#7ab8ff'), C('#3a4a9a')], 'unruhig': [C('#f0e0ff'), C('#b88aff'), C('#5a3a9a')],
           'kritisch': BLOOD_MOON, 'ausbruch': BLOOD_MOON}[stage]
    def fn(t):
        f = F(48, 56, seed=t)
        cx, cy = 24, 30
        pulse = .5 + .5 * math.sin(t / 8 * 2*math.pi * speed)
        f.ell(6, 46, 42, 54, C('#3a3446'))
        rx, ry = 14 + pulse * 2, 21 + pulse * 2
        for k in range(3, 0, -1):
            f.ell(cx - rx - k, cy - ry - k, cx + rx + k, cy + ry + k, alpha(col[1], int((60 + 80 * pulse) / k)))
        f.ell(cx - rx, cy - ry, cx + rx, cy + ry, col[2])
        f.ell(cx - rx + 2, cy - ry + 2, cx + rx - 2, cy + ry - 2, C('#0c0810'))
        for arm in range(3):
            for k in range(26):
                p = k / 26
                a = arm * 2.09 + p * 5 + t * .3 * speed
                f.s(cx + math.cos(a) * (rx - 3) * p, cy + math.sin(a) * (ry - 3) * p, col[0] if k > 20 else col[1] if k > 8 else col[2])
        for k in range(10):
            a = k / 10 * 2*math.pi + t * .2 * speed
            f.s(cx + math.cos(a) * (rx + 4 + pulse * 2), cy + math.sin(a) * (ry + 4 + pulse * 2), alpha(col[0], 200))
        if stage in ('kritisch', 'ausbruch'):
            for a_, b_ in (((10, 20), (4, 14)), ((38, 28), (45, 22)), ((14, 46), (8, 52))): f.line(a_, b_, col[1])
        if stage == 'ausbruch' and t >= 3:
            r = (t - 2) * 6
            for k in range(40):
                a = k / 40 * 2*math.pi; f.s(cx + math.cos(a) * r, cy + math.sin(a) * r * .8, col[(k + t) % 3])
            for k in range(3):
                x = cx + (k - 1) * 10 + (t - 3) * (k - 1) * 3; y = cy - 4 - (t - 3)
                f.ell(x - 3, y - 4, x + 3, y + 4, C('#140810')); f.s(x + 1, y - 1, C('#ff3a3a'))
        return f.im
    return fn

def fristhalter(t):
    """Fristhalter geht in die Hülle und verschwindet."""
    base = huelle('ruhig')(t)
    walk = Image.open(os.path.join(g.BASE, 'characters', 'walk', 'abenteurer_walk.png'))
    fr = walk.crop(((1 + t % 4) * 18, 3 * 26, (2 + t % 4) * 18, 4 * 26))
    k = t / 7
    fade = Image.new('RGBA', fr.size, (0, 0, 0, 0)); p = fade.load(); s = fr.load()
    for y in range(26):
        for x in range(18):
            c = s[x, y]
            if c[3] and random.Random(x * 7 + y * 13 + t).random() > k * 1.1:
                p[x, y] = mix(c, MANA_L, k * .7)[:3] + (c[3],)
    place(base, fade, 15, 52 - 26 - t * 2)
    return base

def teleport(mode):
    def fn(t):
        f = F(32, 40, seed=t)
        k = t if mode == 'senden' else 7 - t
        box_vis = k < 5
        if box_vis:
            f.rect(9, 26, 22, 36, g.WOOD); f.rect(9, 26, 22, 27, g.WOOD_L); f.rect(15, 26, 16, 36, C('#c8a878'))
            if k >= 2:
                for y in range(26, 37):
                    for x in range(9, 23):
                        if (x + y + k) % (6 - k) == 0: f.s(x, y, C('#fff4c8'))
        if 2 <= k <= 6:
            h = (k - 1) * 6
            for y in range(36 - h, 37):
                for x in range(13, 19):
                    if (x + y) % 2 == 0: f.s(x, y, C('#fff4c8'))
            f.line((16, 36 - h), (13, 30 - h), C('#fff07a')); f.line((16, 30 - h), (20, 24 - h), C('#fff07a'))
        for i in range(6):
            a = i / 6 * 2*math.pi + t * .5; r = 10 - abs(k - 4) * 1.5
            f.s(16 + math.cos(a) * r, 31 + math.sin(a) * r * .5, C('#ffd27a') if i % 2 else C('#fff07a'))
        f.d.ellipse([5, 34, 27, 39], outline=C('#ffd27a'))
        return f.im
    return fn

def waesche(mana):
    def fn(t):
        f = F(56, 36, seed=t)
        for x in (3, 52): f.rect(x - 1, 6, x, 35, g.WOOD_D)
        sag = lambda x: 8 + math.sin((x - 3) / 49 * math.pi) * 4
        for x in range(3, 52): f.s(x, sag(x), C('#e8e0d0'))
        cols = [C('#c84a4a'), C('#e8e0f0'), C('#4a6aa0'), C('#e0b048')]
        for i, x0 in enumerate((8, 20, 32, 42)):
            w_ = 8; y0 = sag(x0 + 4)
            wind = math.sin(t / 8 * 2*math.pi + i) * 2
            pts = [(x0, y0), (x0 + w_, y0), (x0 + w_ + wind, y0 + 11), (x0 + wind * .6, y0 + 12)]
            f.poly(pts, cols[i]); f.line((x0, y0), (x0 + w_, y0), shade(cols[i], .7))
            f.s(x0 + 1, y0, C('#8a6a4a')); f.s(x0 + w_ - 1, y0, C('#8a6a4a'))
            if mana and (t + i) % 2 == 0:
                for k in range(3): f.s(x0 + 2 + k * 2 + wind, y0 + 13 + ((t + k) % 4), MANA if k % 2 else MANA_L)
            elif not mana and (t + i) % 4 == 0:
                f.s(x0 + 4, y0 + 13, C('#8ac4ee'))
        return f.im
    return fn

def kind_aura(t):
    im = g.make_character(next(c for c in g.CHARACTERS if c['name'] == 'kind'), 'idle')
    c = cb.cell(im); cb.aura(c, t, .6 + .4 * math.sin(t / 6 * 2*math.pi))
    return c

def ritual(t):
    f = F(48, 40, seed=t)
    priest, _ = fig('brust', race=HUMAN)
    pal = priest.load()
    robe = Image.new('RGBA', priest.size, (0, 0, 0, 0)); rp = robe.load()
    for y in range(26):
        for x in range(18):
            c = pal[x, y]
            if not c[3]: continue
            if y > 13 and c[:3] not in (g.OUTLINE[:3],): c = mix(C('#f0ecf4'), c, .2)
            rp[x, y] = c
    place(f.im, robe, 6, 12)
    f.ell(12, 25, 19, 29, C('#e8e0d0')); f.ell(13, 24, 16, 27, g.SKIN)
    f.rect(38, 30, 42, 34, C('#e0b048')); f.ell(36, 27, 44, 31, C('#e0b048')); f.rect(39, 34, 41, 38, C('#c89a3a')); f.rect(37, 38, 43, 39, C('#c89a3a'))
    k = t / 7
    for i in range(6):
        p = ((t + i * 1.3) % 8) / 8
        x = 17 + (40 - 17) * p; y = 26 - math.sin(p * math.pi) * 10
        f.s(x, y, MANA_L if i % 2 else MANA)
    if t in (5, 6, 7): f.ell(36, 25, 44, 29, MANA)
    if t % 4 == 1: f.s(14, 22, MANA_L)
    return f.im

def manastau(stage):
    n = {'druck': 4, 'schwaeche': 6, 'manafieber': 6, 'entladung': 8}[stage]
    def fn(t):
        c = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        if stage == 'druck':
            im, _ = fig('hoch_b', blink=t % 2 == 1); place(c, im, 11 + (t % 2), 12)
            for k in range(3): c.load()[18 + k * 2, 11 - (t + k) % 2] = MANA + ()
        elif stage == 'schwaeche':
            im, _ = fig('unten', blink=True)
            if t >= 3: im = cb.kneel(im)
            place(c, im, 11 + [0, -1, 1, -1, 0, 0][t], 12)
            for k in range(2): c.load()[14 + k * 8, 14 + (t % 3)] = (220, 220, 240, 255)
        elif stage == 'manafieber':
            im, _ = fig('brust', blink=t % 3 == 0)
            p = im.load()
            pulse = .5 + .5 * math.sin(t / 6 * 2*math.pi)
            for y in range(26):
                for x in range(18):
                    col = p[x, y]
                    if col[3] and col[:3] in (g.SKIN[:3], shade(g.SKIN, .85)[:3], g.SKIN_S[:3], mix(g.SKIN, WHITE, .12)[:3]) and (x * 3 + y * 5 + t) % 4 == 0:
                        p[x, y] = mix(col, MANA, .4 + .5 * pulse)[:3] + (255,)
                    elif col[3] and col[:3] not in (g.OUTLINE[:3],):
                        p[x, y] = mix(col, C('#ff7a5a'), .12 * pulse)[:3] + (255,)
            place(c, im, 11, 12)
            for k in range(2): c.load()[13 + k * 12, 10 + (t % 3)] = (255, 160, 120, 255)
        else:
            im, _ = fig('hoch_b' if t >= 2 else 'brust', blink=True)
            if t >= 3: im = cb.tint(im, WHITE, .6 if t == 3 else .2)
            place(c, im, 11, 12)
            d = ImageDraw.Draw(c)
            if t >= 2:
                r = (t - 1) * 3.2
                d.ellipse([20 - r, 24 - r, 20 + r, 24 + r], outline=MANA_L if t < 5 else MANA)
                for k in range(12):
                    a = k / 12 * 2*math.pi + t
                    x, y = 20 + math.cos(a) * r * 1.2, 24 + math.sin(a) * r * 1.2
                    if 0 <= x < 40 and 0 <= y < 40: c.load()[int(x), int(y)] = MANA_L
            if t in (3, 4):
                for k in range(5): d.line([(20, 24), (20 + math.cos(k * 1.3) * 18, 24 + math.sin(k * 1.3) * 18)], fill=MANA)
        return c
    return fn, n

def blutmond(t):
    f = F(64, 48, seed=t)
    pulse = .5 + .5 * math.sin(t / 8 * 2*math.pi)
    for r in range(18, 10, -2):
        a = int(30 + (18 - r) * 12 * (.6 + .4 * pulse))
        f.disc(32, 24, r, alpha(BLOOD_MOON[1], a))
    f.disc(32, 24, 10, mix(BLOOD_MOON[1], BLOOD_MOON[0], .2 * pulse)); f.disc(29, 21, 3, BLOOD_MOON[2]); f.disc(35, 27, 2, BLOOD_MOON[2])
    f.disc(28, 20, 1.5, BLOOD_MOON[0])
    for i in range(3):
        x = (i * 26 + t * 2) % 80 - 12; y = 14 + i * 12
        for k in range(5): f.disc(x + k * 3, y + (k % 2), 3, alpha(C('#2a1a2e'), 200))
    return f.im

def oedland(t):
    f = F(80, 32, seed=1)
    cx = 66
    f.ell(56, 6, 78, 30, C('#0c0810')); f.d.ellipse([56, 6, 78, 30], outline=C('#7a5a9a'))
    rng = random.Random(3)
    for i in range(24):
        x = rng.uniform(2, 52); k = x / 52
        col = mix(C('#4a7d4a'), C('#8a7a5a'), k)
        h = 5 * (1 - k * .8)
        droop = k * 3
        f.line((x, 30), (x + droop, 30 - h), col)
        if rng.random() < .4 and k < .5: f.s(x + droop, 30 - h - 1, C('#e888a8'))
    f.rect(0, 30, 54, 31, mix(C('#5a8a4a'), C('#6a5a4a'), .5))
    for i in range(10):
        p = ((t + i * 0.8) % 8) / 8
        sx = 4 + (i * 13) % 48; sy = 10 + (i * 7) % 18
        x = sx + (cx - sx) * p; y = sy + (18 - sy) * p
        f.s(x, y, C('#b8a0ff') if i % 2 else C('#8ae06a'))
    return f.im

def himmelswal(t):
    f = F(128, 52, seed=t)
    x = 64; y = 24 + math.sin(t / 8 * 2*math.pi) * 2
    body, belly = C('#8aa0c8'), C('#e8eef8')
    fin = math.sin(t / 8 * 2*math.pi) * 6
    f.poly([(x - 44, y), (x - 60, y - 10 + fin), (x - 56, y), (x - 60, y + 10 + fin)], shade(body, .85))
    f.ell(x - 48, y - 12, x + 46, y + 13, body)
    f.ell(x - 38, y + 1, x + 40, y + 13, belly)
    for k in range(5): f.line((x + 10, y + 6 + k * 1.5), (x + 38, y + 6 + k * 1.5 - 2), shade(belly, .85))
    f.poly([(x - 4, y + 6), (x + 10, y + 6), (x + 2, y + 18 + fin * .5)], shade(body, .8))
    f.s(x + 32, y - 3, C('#2b1e33')); f.s(x + 33, y - 3, C('#2b1e33'))
    for k in range(4): f.ell(x - 30 + k * 16, y - 16 - (k % 2) * 2, x - 22 + k * 16, y - 12 - (k % 2) * 2, (255, 255, 255, 200))
    return g.outline(f.im)

def himmelswal_schatten(t):
    f = F(128, 24)
    x = 64 + math.sin(t / 8 * 2*math.pi) * 1
    for y in range(24):
        for xx in range(128):
            d = ((xx - x) / 58) ** 2 + ((y - 12) / 9) ** 2
            if d <= 1 and (xx + y) % 2 == 0: f.s(xx, y, (20, 14, 30, 90))
    return f.im

def dornen_tattoo(t):
    im, _ = fig('hoch_r', race=next(r for r in rc.RACES if r['name'] == 'elf'))
    p = im.load()
    glow = [0, .4, 1, 1, .6, .2][t]
    pts = [(14, 11), (14, 12), (14, 13), (13, 14), (13, 15), (14, 12), (15, 13)]
    for x, y in pts:
        if 0 <= x < 18 and p[x, y][3]: p[x, y] = mix(C('#3a5a2a'), C('#c8ff7a'), glow)[:3] + (255,)
    c = cb.cell(im)
    if glow > .5:
        cp = c.load()
        for k in range(6):
            a = k * 1.05 + t; x, y = int(18 + math.cos(a) * 4), int(12 + math.sin(a) * 4)
            if 0 <= x < 26 and 0 <= y < 26 and not cp[x, y][3]: cp[x, y] = C('#c8ff7a')
    return c

# ================================================================ DORFLEBEN
def haendler(t):
    im, _ = fig('hoch_r' if t % 2 else 'unten', race=next(r for r in rc.RACES if r['name'] == 'hund'))
    c = Image.new('RGBA', (32, 34), (0, 0, 0, 0)); place(c, im, 7, 8)
    d = ImageDraw.Draw(c)
    if t in (1, 2):
        d.rectangle([20, 0, 30, 8], fill=WHITE); d.polygon([(22, 8), (25, 8), (21, 11)], fill=WHITE)
        d.rectangle([24, 2, 25, 4], fill=C('#c83a3a')); d.point((24, 6), fill=C('#c83a3a')); d.point((25, 6), fill=C('#c83a3a'))
    for i in range(2):
        y = 30 - ((t * 3 + i * 5) % 12)
        d.point((4 + i * 3, y), fill=g.GOLD); d.point((5 + i * 3, y), fill=C('#fff0a0'))
    return c

def brunnen(t):
    base = g.brunnen(False); p = base.load()
    for y in range(17, 31):
        for x in range(13, 22): p[x, y] = (0, 0, 0, 0)
    d = ImageDraw.Draw(base)
    rope = 2 + abs(4 - t) * 2
    d.line([(17, 18), (17, 18 + rope)], fill=C('#c8b898'))
    by = 18 + rope
    d.rectangle([15, by, 19, by + 4], fill=g.WOOD); d.rectangle([15, by, 19, by], fill=g.WOOD_D)
    if t in (4, 5): d.point((15, by + 5), fill=C('#8ac4ee')); d.point((19, by + 6), fill=C('#8ac4ee'))
    ang = t / 8 * 2*math.pi
    d.line([(28, 16), (28 + math.cos(ang) * 4, 16 + math.sin(ang) * 4)], fill=g.WOOD_D, width=2)
    return base

def schmiede_funken(t):
    f = F(40, 28, seed=t)
    f.rect(12, 18, 27, 19, C('#8a8ea0')); f.rect(16, 20, 23, 22, C('#5a5e6e')); f.rect(13, 23, 26, 25, C('#3e4050'))
    f.rect(16, 17, 22, 17, C('#ff9a3c')); f.s(21, 17, C('#ffd27a'))
    a = [-.9, -.4, .5, .9, .2, -.6][t]
    hx, hy = 30 + math.cos(a) * 2, 8 + math.sin(a) * 6
    f.line((34, 14), (hx - 6, hy + 6), g.WOOD, 2)
    f.rect(hx - 9, hy + 3, hx - 4, hy + 8, C('#6a6e80'))
    if t in (2, 3):
        for k in range(10):
            ang = -math.pi * (k / 9); r = 3 + (t - 1) * 4 + (k % 3)
            f.s(19 + math.cos(ang) * r, 16 + math.sin(ang) * r * .8, C('#ffd27a') if k % 2 else C('#ff9a3c'))
    return g.outline(f.im)

def ofen(t):
    f = F(36, 36, seed=t)
    f.ell(2, 6, 33, 34, C('#9a6a4a')); f.rect(2, 20, 33, 34, C('#9a6a4a'))
    for y in range(8, 34, 4):
        for x in range(2 + (y // 4 % 2) * 3, 33, 6): f.s(x, y, C('#7a4e36'))
    f.ell(10, 16, 25, 31, C('#2a1a1a')); f.rect(10, 24, 25, 31, C('#2a1a1a'))
    for k in range(5): f.s(12 + k * 3, 29 - (k + t) % 2, C('#ff9a3c'))
    slide = [0, 0, 2, 5, 8, 8, 4, 0][t]
    if slide:
        f.ell(12 + slide, 24, 23 + slide, 29, C('#d8a050')); f.ell(13 + slide, 24, 21 + slide, 26, C('#f0c878'))
        f.line((14 + slide, 25), (16 + slide, 27), C('#a8703a')); f.line((18 + slide, 25), (20 + slide, 27), C('#a8703a'))
    for i in range(3):
        y = 12 - ((t * 2 + i * 4) % 12); x = 18 + math.sin(t * .8 + i) * 2 + (i - 1) * 3
        f.disc(x, y, 1.5 + i * .3, (240, 240, 250, 170))
    return g.outline(f.im)

def rauch_wind(t):
    f = F(40, 40, seed=t)
    f.rect(4, 30, 11, 39, C('#8a4a44')); f.rect(3, 29, 12, 30, C('#5a3030'))
    for i in range(6):
        p = ((t + i * 8 / 6) % 8) / 8
        x = 8 + p * 28 + math.sin(p * 6) * 1.5; y = 27 - p * 16 + p * p * 8
        r = 1.5 + p * 3.5
        if p < .85 or (i + t) % 2:
            f.disc(x, y, r, (200, 196, 210, int(220 - p * 150))); f.disc(x - r * .3, y - r * .3, r * .5, (235, 232, 245, int(220 - p * 150)))
    return f.im

def fensterladen(mode):
    def fn(t):
        f = F(28, 22, seed=t)
        k = t if mode == 'auf' else 3 - t
        f.rect(8, 3, 19, 18, g.WOOD_D); f.rect(9, 4, 18, 17, C('#b4d2ea')); f.rect(13, 4, 14, 17, g.WOOD_D); f.rect(9, 10, 18, 11, g.WOOD_D)
        w_ = [5, 4, 2, 1][k]
        for side in (-1, 1):
            if side < 0: x0, x1 = 8 - (5 - w_) * 1.6 if k else 8, 8 - (5 - w_) * 1.6 + w_ if k else 13
            else: x1, x0 = 19 + (5 - w_) * 1.6 if k else 19, 19 + (5 - w_) * 1.6 - w_ if k else 14
            if k == 0:
                x0, x1 = (8, 13) if side < 0 else (14, 19)
            elif k == 3:
                x0, x1 = (2, 7) if side < 0 else (20, 25)
            f.rect(min(x0, x1), 3, max(x0, x1), 18, g.WOOD)
            for y in range(5, 18, 3): f.line((min(x0, x1), y), (max(x0, x1), y), g.WOOD_D)
        f.rect(7, 19, 20, 19, g.WOOD_L)
        return g.outline(f.im)
    return fn

def gildenbrett(t):
    f = F(36, 36, seed=1)
    f.rect(6, 22, 7, 35, g.WOOD_D); f.rect(28, 22, 29, 35, g.WOOD_D)
    f.rect(2, 2, 33, 24, g.WOOD); f.rect(2, 2, 33, 3, g.WOOD_L); f.rect(4, 5, 31, 22, C('#8a6a4a'))
    papers = [(6, 7, C('#f0e4cc')), (14, 6, C('#e8dcc0')), (23, 8, C('#f4ecd8')), (8, 15, C('#e0d4b8'))]
    for i, (x, y, c) in enumerate(papers):
        wv = 1 if (t + i) % 4 == 0 else 0
        f.rect(x, y, x + 6, y + 6 + wv, c); f.s(x + 3, y, C('#c83a3a'))
        for k in range(2): f.line((x + 1, y + 2 + k * 2), (x + 5, y + 2 + k * 2), C('#8a7a6a'))
    if t >= 4:
        y = 14 - max(0, 6 - t) * 3
        f.rect(19, y, 25, y + 6, WHITE); f.s(22, y, C('#e0b048'))
        f.line((20, y + 2), (24, y + 2), C('#c83a3a'))
        if t == 6: f.s(26, y - 1, C('#fff0a0')); f.s(18, y - 1, C('#fff0a0'))
    return g.outline(f.im)

# ================================================================ NATUR & WETTER
def regen(t):
    f = F(64, 64)
    rng = random.Random(1)
    for i in range(40):
        x0, y0 = rng.uniform(0, 72), rng.uniform(0, 64)
        y = (y0 + t * 8) % 64; x = (x0 - t * 2) % 64
        f.line((x, y), (x + 1, y - 4), (170, 200, 235, 170))
    return f.im

def pfuetze(t):
    f = F(24, 10)
    f.ell(1, 1, 22, 9, (90, 120, 170, 200)); f.ell(4, 2, 12, 4, (170, 200, 235, 160))
    for k, x in enumerate((8, 16)):
        r = ((t + k * 3) % 6) * 1.3
        if r: f.d.ellipse([x - r, 5 - r * .4, x + r, 5 + r * .4], outline=(210, 230, 250, 220))
    return f.im

def schnee(t):
    f = F(64, 64)
    rng = random.Random(2)
    for i in range(36):
        x0, y0 = rng.uniform(0, 64), rng.uniform(0, 64)
        y = (y0 + t * 3) % 64; x = (x0 + math.sin(t * .5 + i) * 2) % 64
        f.s(x, y, (255, 255, 255, 230))
        if i % 3 == 0: f.s(x + 1, y, (255, 255, 255, 160))
    return f.im

def gewitter(t):
    f = F(64, 64, seed=t)
    if t in (2, 3):
        for y in range(64):
            for x in range(64):
                if (x + y) % (2 if t == 2 else 4) == 0: f.s(x, y, (255, 255, 255, 70 if t == 2 else 35))
    if t in (2, 3, 4):
        x = 36; pts = [(x, 0)]
        rng = random.Random(5)
        for k in range(8): pts.append((pts[-1][0] + rng.uniform(-5, 5), pts[-1][1] + 8))
        for a, b in zip(pts, pts[1:]):
            f.line(a, b, C('#fff07a') if t < 4 else C('#b8a0ff'), 2 if t == 2 else 1); f.line(a, b, WHITE)
    return f.im

def gras_wind(t):
    f = F(20, 14)
    for i, (x, h, c) in enumerate(((3, 9, LEAF_D), (6, 12, LEAF), (9, 10, LEAF_L), (12, 13, LEAF), (15, 9, LEAF_D), (17, 11, LEAF_L))):
        bend = math.sin(t / 8 * 2*math.pi + i * .4) * 2 + 1.5
        f.line((x, 13), (x + bend * .5, 13 - h * .5), c); f.line((x + bend * .5, 13 - h * .5), (x + bend, 13 - h), c)
    return f.im

def baum_wind(t):
    tree = g.baum(False)
    w, h = tree.size
    out = Image.new('RGBA', (w + 8, h), (0, 0, 0, 0)); p = out.load(); s = tree.load()
    sway = math.sin(t / 8 * 2*math.pi) * 2.5
    for y in range(h):
        k = max(0, (h * .62 - y) / (h * .62))
        dx = round(sway * k * k + sway * .3 * k)
        for x in range(w):
            if s[x, y][3]: p[x + 4 + dx, y] = s[x, y]
    return out

def gluehwuermchen(t):
    f = F(40, 32)
    rng = random.Random(4)
    for i in range(7):
        x0, y0 = rng.uniform(4, 36), rng.uniform(4, 28)
        x = x0 + math.sin(t / 8 * 2*math.pi + i) * 3; y = y0 + math.cos(t / 8 * 2*math.pi * 1.3 + i) * 2
        on = (t + i * 3) % 8 < 5
        if on:
            f.s(x, y, C('#f8ffb0')); f.s(x + 1, y, (200, 255, 120, 160)); f.s(x - 1, y, (200, 255, 120, 160)); f.s(x, y - 1, (200, 255, 120, 120))
        else: f.s(x, y, (120, 160, 80, 140))
    return f.im

def sternschnuppe(t):
    f = F(64, 32)
    x = 56 - t * 9; y = 4 + t * 4
    for k in range(10):
        a = int(255 * (1 - k / 10))
        f.s(x + k * 1.5, y - k * .7, (255, 255, 230, a))
    f.s(x, y, WHITE); f.s(x - 1, y, (255, 240, 200, 200))
    return f.im

def voegel(t):
    f = F(48, 32)
    for i, (x0, y0) in enumerate(((8, 26), (16, 28), (24, 27))):
        if t < 2:
            f.s(x0, y0, C('#5a4a4a')); f.s(x0 + 1, y0, C('#5a4a4a')); f.s(x0 + 2, y0 - 1, C('#5a4a4a'))
        else:
            x = x0 + (t - 1) * (3 + i); y = y0 - (t - 1) * (4 + i)
            up = (t + i) % 2
            f.s(x, y, C('#5a4a4a')); f.s(x - 1, y - (1 if up else -1), C('#5a4a4a')); f.s(x + 1, y - (1 if up else -1), C('#5a4a4a'))
            f.s(x - 2, y - (2 if up else 0), C('#5a4a4a')); f.s(x + 2, y - (2 if up else 0), C('#5a4a4a'))
    return f.im

def fisch(t):
    f = F(28, 24)
    f.d.ellipse([3, 18, 25, 22], outline=(120, 170, 220, 200) if t > 0 else (0, 0, 0, 0))
    if 1 <= t <= 6:
        p = (t - 1) / 5
        x = 6 + p * 16; y = 19 - math.sin(p * math.pi) * 14
        ang = math.cos(p * math.pi) * .8
        for k in range(-3, 4):
            f.s(x + k * math.cos(ang), y - k * math.sin(ang), C('#c8a050') if abs(k) < 3 else C('#a87a3a'))
        f.s(x + 3 * math.cos(ang), y - 3 * math.sin(ang) - 1, C('#2b1e33'))
        if t in (1, 6):
            for k in range(4): f.s(x - 3 + k * 2, 17 - (k % 2), (220, 240, 255, 230))
    return f.im

def schmetterling(t):
    f = F(12, 12)
    up = t % 2
    y = 6 + (t % 4 == 2)
    col, col2 = C('#e888a8'), C('#f8c8d8')
    f.s(6, y, C('#3a2a2a')); f.s(6, y + 1, C('#3a2a2a'))
    if up:
        f.rect(3, y - 3, 5, y, col); f.rect(7, y - 3, 9, y, col); f.s(4, y - 2, col2); f.s(8, y - 2, col2)
    else:
        f.rect(2, y, 5, y + 2, col); f.rect(7, y, 10, y + 2, col)
    return f.im

def ufer(t):
    f = F(40, 14)
    f.rect(0, 0, 39, 13, (74, 138, 200, 255))
    for x in range(40):
        y = 6 + math.sin((x + t * 3) * .35) * 1.5
        f.s(x, y, C('#e8f8ff'))
        if (x + t) % 5 == 0: f.s(x, y + 1, C('#b4d2ea'))
    f.rect(0, 10, 39, 13, C('#d8c098'))
    for x in range(0, 40, 2):
        if math.sin((x + t * 3) * .35) > .6: f.s(x, 10, C('#e8f8ff'))
    return f.im

def bach(t):
    f = F(40, 16)
    f.rect(0, 2, 39, 13, C('#4a8ac8')); f.rect(0, 0, 39, 1, C('#5a8a4a')); f.rect(0, 14, 39, 15, C('#5a8a4a'))
    rng = random.Random(6)
    for i in range(10):
        x0 = rng.uniform(0, 40); y = rng.randint(4, 11)
        x = (x0 + t * 3) % 40
        f.line((x, y), (x + 3, y), C('#b4d2ea') if i % 3 else WHITE)
    return f.im


# ================================================================ Brunnen-Münze & Bäume
def muenze_brunnen(t):
    base = g.brunnen(False)
    out = Image.new('RGBA', (52, 48), (0, 0, 0, 0)); out.alpha_composite(base, (16, 4)); p = out.load()
    d = ImageDraw.Draw(out)
    if t <= 4:
        k = t / 4
        x = 4 + k * 30; y = 26 - math.sin(k * math.pi) * 18 + k * 6
        c = g.GOLD if t % 2 else C('#fff0a0')
        d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=c); d.point((x - 1, y - 1), fill=C('#fff8d0'))
        if t > 0:
            for j in range(1, 3): d.point((x - j * 3, y + j), fill=(255, 240, 160, 120))
    if t in (5, 6):
        for k, (dx, dy) in enumerate(((-4, -4), (-1, -7), (2, -6), (5, -3), (0, -9))):
            if t == 6: dy -= 2
            d.point((34 + dx, 33 + dy), fill=C('#b4d2ea') if k % 2 else C('#e8f8ff'))
    if t >= 6:
        for k in range(5):
            a = k / 5 * 2*math.pi + t; r = 3 + (t - 6) * 3
            d.point((34 + math.cos(a) * r, 26 + math.sin(a) * r * .6), fill=C('#fff4c8'))
        d.point((34, 22 - (t - 6) * 2), fill=WHITE)
    return out

LEAF_GREEN = [C('#6e9e58'), C('#4a7d4a'), C('#8ab868')]
LEAF_AUTUMN = [C('#e0a040'), C('#c8603a'), C('#e8c060')]
def recolor(img, pal):
    out = img.copy(); p = out.load()
    src = {g.LEAF[:3]: pal[1], g.LEAF_D[:3]: shade(pal[1], .75), g.LEAF_L[:3]: pal[0], C('#8ab868')[:3]: pal[2]}
    for y in range(out.height):
        for x in range(out.width):
            c = p[x, y]
            if c[3] and c[:3] in src: p[x, y] = src[c[:3]][:3] + (255,)
    return out

def blaetter(autumn):
    def fn(t):
        tree = g.baum(False)
        if autumn: tree = recolor(tree, LEAF_AUTUMN)
        out = Image.new('RGBA', (56, 60), (0, 0, 0, 0)); out.alpha_composite(tree, (7, 6)); p = out.load()
        pal = LEAF_AUTUMN if autumn else LEAF_GREEN
        rng = random.Random(2)
        for i in range(7 if autumn else 4):
            x0 = rng.uniform(10, 44); y0 = rng.uniform(14, 30); sp = rng.uniform(3, 4.5)
            prog = (t + i * 8 / (7 if autumn else 4)) % 8
            y = y0 + prog * sp; x = x0 + math.sin(prog * .9 + i) * 3
            if y < 58:
                c = pal[i % 3]
                if 0 <= x < 56 and 0 <= y < 60: p[int(x), int(y)] = c
                if 0 <= x + 1 < 56 and 0 <= y < 60 and (int(prog) + i) % 2: p[int(x) + 1, int(y)] = shade(c, .8)
        if autumn:
            for x in range(8, 50, 3): p[x, 57] = pal[(x // 3) % 3]
        return out
    return fn

def blitzbaum(t):
    tree = g.baum(False)
    out = Image.new('RGBA', (56, 72), (0, 0, 0, 0))
    if t <= 1:
        out.alpha_composite(tree, (7, 18))
        if t == 1:
            pp = out.load()
            for y in range(72):
                for x in range(56):
                    if (x + y) % 3 == 0 and not pp[x, y][3]: pp[x, y] = (255, 255, 255, 60)
        return out
    if t == 2:
        out.alpha_composite(cb.tint(tree, WHITE, .8), (7, 18))
    else:
        burnt = tree.copy(); bp = burnt.load()
        for y in range(burnt.height):
            for x in range(burnt.width):
                c = bp[x, y]
                if not c[3]: continue
                if c[:3] in (g.LEAF[:3], g.LEAF_D[:3], g.LEAF_L[:3], C('#8ab868')[:3]):
                    if random.Random(x * 7 + y * 3).random() < .5 + (t - 3) * .05: bp[x, y] = (0, 0, 0, 0)
                    else: bp[x, y] = mix(c, C('#3a2a22'), .6)[:3] + (255,)
                elif c[:3] != g.OUTLINE[:3]:
                    bp[x, y] = mix(c, C('#2a1e1a'), .55)[:3] + (255,)
        burnt = g.outline(burnt)
        out.alpha_composite(burnt, (7, 18))
    d = ImageDraw.Draw(out)
    if t in (2, 3):
        pts = [(30, 0), (25, 8), (31, 14), (26, 22), (28, 30)]
        for a, b in zip(pts, pts[1:]): d.line([a, b], fill=C('#fff07a'), width=3 if t == 2 else 2); d.line([a, b], fill=WHITE)
    if t >= 3:
        fl = [C('#fff4c8'), C('#ffd27a'), C('#ff9a3c'), C('#d8452e')]
        for i, (x, y) in enumerate(((27, 30), (22, 34), (33, 33), (28, 44))):
            if t > 7 and i > 1: continue
            h = 3 + ((t + i) % 3)
            for k in range(h): d.point((x + (k % 2) * ((t + i) % 2), y - k), fill=fl[min(3, k)])
        for i in range(3):
            y = 26 - ((t * 3 + i * 5) % 22); x = 27 + math.sin(t + i) * 3 + i * 2
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(110, 104, 118, 160))
        d.line([(28, 40), (28, 58)], fill=C('#ff9a3c') if t < 6 else C('#5a3a2a'))
    return out

def wuetender_baum(mode):
    """Verkohlter Baum erwacht nach dem Blitz und droht dem Himmel."""
    def fn(t):
        f = F(56, 64, seed=t)
        bark, bark_d, char = C('#5a4030'), C('#3a2a22'), C('#2a1e1a')
        shake = (1 if t % 2 else -1) if mode == 'wuetend' else 0
        # Wurzeln + Stamm
        for s in (-1, 1): f.line((28, 58), (28 + s * 9, 62), bark_d, 3)
        f.poly([(21, 62), (35, 62), (33 + shake, 26), (23 + shake, 26)], bark)
        f.poly([(30, 62), (35, 62), (33 + shake, 26), (31 + shake, 26)], bark_d)
        for y in (34, 44, 52): f.line((23, y), (26, y + 2), char)
        # Äste: Winkel je nach Pose
        if mode == 'erwachen': up = [0, 0, .2, .5, .8, 1][t]
        else: up = 1
        for s in (-1, 1):
            wob = math.sin(t * 2.1 + s) * .25 if mode == 'wuetend' else 0
            a = math.radians(200 if s < 0 else -20) * (1 - up) + math.radians(110 if s < 0 else 70) * up + wob * s
            sx, sy = 28 + s * 3 + shake, 30
            ex, ey = sx + math.cos(a) * 14 * s * (-1 if s < 0 else 1) if False else sx + math.cos(a) * 14, sy - math.sin(a) * 14
            f.line((sx, sy), (ex, ey), bark, 4); f.line((sx, sy), (ex, ey), bark_d)
            for k, da in enumerate((-.5, 0, .5)):
                aa = a + da + (math.sin(t * 3 + k) * .3 if mode == 'wuetend' else 0)
                f.line((ex, ey), (ex + math.cos(aa) * 6, ey - math.sin(aa) * 6), bark, 2)
            if mode == 'wuetend' and t % 3 == 0:
                f.s(ex + math.cos(a) * 8, ey - math.sin(a) * 8 - 1, C('#ff9a3c'))
        # wenige verbrannte Blätter
        for x, y in ((18, 20), (38, 18), (28, 16)):
            if mode == 'erwachen' or (t + x) % 4: f.disc(x + shake, y + (2 if up < .5 else 0), 2.5, C('#4a4a2a'))
        # Gesicht
        awake = mode == 'wuetend' or t >= 2
        ey_ = 36
        if awake:
            for ex_ in (25, 31):
                f.ell(ex_ - 2 + shake, ey_ - 1, ex_ + 2 + shake, ey_ + 2, C('#fff4c8'))
                f.s(ex_ + shake, ey_ + 1, C('#c83a3a'))
            f.line((22 + shake, ey_ - 4), (27 + shake, ey_ - 2), char, 2); f.line((34 + shake, ey_ - 4), (29 + shake, ey_ - 2), char, 2)
            mo = 2 + (t % 2) * 2 if mode == 'wuetend' else 1
            f.ell(24 + shake, 41, 32 + shake, 41 + mo, C('#140c0c'))
            if mo > 2:
                for x in (25, 28, 31): f.s(x + shake, 41, C('#e8e0d0'))
        else:
            for ex_ in (25, 31): f.line((ex_ - 2, ey_ + 1), (ex_ + 2, ey_ + 1), char)
        img = g.outline(f.im)
        d = ImageDraw.Draw(img)
        if mode == 'wuetend':
            ax, ay = 44, 10 + (t % 2)
            for a_, b_ in (((ax, ay), (ax + 3, ay + 3)), ((ax + 5, ay), (ax + 2, ay + 3)), ((ax, ay + 6), (ax + 3, ay + 3)), ((ax + 5, ay + 6), (ax + 2, ay + 3))):
                d.line([a_, b_], fill=C('#e03a3a'), width=1)
            for i in range(2):
                y = 24 - ((t * 2 + i * 3) % 8); x = 20 + i * 16
                d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(160, 150, 170, 180))
        if mode == 'erwachen' and t in (0, 1):
            for i in range(3): d.point((26 + i * 3, 22 - t * 2), fill=(140, 134, 150, 200))
        return img
    return fn

# ================================================================ SPIELHILFEN
def funkeln(t):
    f = F(12, 12)
    s = [0, 1, 3, 4, 3, 1][t]
    c = 6
    f.s(c, c, WHITE)
    for k in range(1, s + 1):
        a = 255 - k * 45
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): f.s(c + dx, c + dy, (255, 244, 200, a))
    if s >= 3:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)): f.s(c + dx, c + dy, (255, 240, 180, 200))
    return f.im

def ausrufezeichen(t):
    f = F(10, 18)
    y = [4, 2, 1, 2, 4, 4][t]
    f.rect(3, y, 6, y + 7, C('#e0b048')); f.rect(4, y, 5, y + 6, C('#fff0a0'))
    f.rect(3, y + 9, 6, y + 11, C('#e0b048'))
    return g.outline(f.im)

def sprechblase(t):
    f = F(20, 16)
    f.ell(1, 1, 18, 11, WHITE); f.poly([(5, 10), (9, 10), (4, 14)], WHITE)
    for k in range(3):
        if t % 4 >= k + 1 or t % 4 == 0 and False: f.rect(5 + k * 4, 6, 6 + k * 4, 7, C('#5a5468'))
    return g.outline(f.im)

def zzz(t):
    f = F(16, 20)
    for k in range(3):
        p = ((t + k * 2) % 6) / 6
        x = 3 + k * 3 + p * 3; y = 16 - k * 4 - p * 6
        s = 1 + k
        a = int(255 * (1 - p * .7))
        col = (230, 230, 255, a)
        f.line((x, y), (x + s + 1, y), col); f.line((x + s + 1, y), (x, y + s + 1), col); f.line((x, y + s + 1), (x + s + 1, y + s + 1), col)
    return f.im

# ================================================================ Registrierung
def entries():
    E = {'lore': [], 'dorf': [], 'natur': [], 'hilfen': []}
    L = E['lore']
    for st, n in (('ruhig', 8), ('unruhig', 8), ('kritisch', 8), ('ausbruch', 8)):
        L.append((f'dungeon_huelle_{st}', f'Dungeon-Hülle: {st}', huelle(st), n))
    L += [('fristhalter_eintritt', 'Fristhalter tritt ein', fristhalter, 8),
          ('teleportpost_senden', 'Teleport-Post: senden', teleport('senden'), 8),
          ('teleportpost_empfangen', 'Teleport-Post: empfangen', teleport('empfangen'), 8),
          ('mana_waesche', 'Wäsche mit Mana trocknen', waesche(True), 8),
          ('kind_mana_aura', 'Kind mit Mana-Aura', kind_aura, 6),
          ('kirchen_ritual', 'Kirchenritual (Mana-Entzug)', ritual, 8)]
    for st in ('druck', 'schwaeche', 'manafieber', 'entladung'):
        fn, n = manastau(st); L.append((f'manastau_{st}', f'Manastau: {st}', fn, n))
    L += [('blutmond', 'Blutmond am Himmel', blutmond, 8), ('voellerei_oedland', 'Ödland der Völlerei', oedland, 8),
          ('himmelswal', 'Himmelswal', himmelswal, 8), ('himmelswal_schatten', 'Himmelswal-Schatten', himmelswal_schatten, 8),
          ('dornen_tattoo', 'Dornen-Tattoo leuchtet', dornen_tattoo, 6)]
    E['dorf'] = [('haendler_ruft', 'Händler ruft', haendler, 4), ('brunnen_eimer', 'Brunnen mit Eimer', brunnen, 8),
                 ('schmiede_funken', 'Schmiede: Hammer & Funken', schmiede_funken, 6), ('backofen', 'Backofen', ofen, 8),
                 ('rauch_wind', 'Rauch im Wind', rauch_wind, 8), ('waesche_wind', 'Wäsche im Wind', waesche(False), 8),
                 ('fensterladen_auf', 'Fensterläden: auf', fensterladen('auf'), 4), ('fensterladen_zu', 'Fensterläden: zu', fensterladen('zu'), 4),
                 ('gildenbrett', 'Gildenbrett', gildenbrett, 8)]
    E['natur'] = [('regen', 'Regen (Overlay)', regen, 8), ('pfuetze', 'Pfütze im Regen', pfuetze, 6), ('schnee', 'Schnee (Overlay)', schnee, 8),
                  ('gewitter', 'Gewitter (Overlay)', gewitter, 8), ('gras_wind', 'Gras im Wind', gras_wind, 8), ('baum_wind', 'Baum im Wind', baum_wind, 8),
                  ('gluehwuermchen', 'Glühwürmchen', gluehwuermchen, 8), ('sternschnuppe', 'Sternschnuppe', sternschnuppe, 6),
                  ('voegel_auffliegen', 'Vögel fliegen auf', voegel, 8), ('fisch_springt', 'Fisch springt', fisch, 8),
                  ('schmetterling', 'Schmetterling', schmetterling, 4),
                  ('muenze_brunnen', 'Münze in den Brunnen', muenze_brunnen, 8),
                  ('baum_blaetter', 'Baum verliert Blätter', blaetter(False), 8),
                  ('herbstbaum_blaetter', 'Herbstbaum verliert Blätter', blaetter(True), 8),
                  ('baum_blitzschlag', 'Blitz schlägt in Baum', blitzbaum, 10),
                  ('wuetender_baum_erwachen', 'Wütender Baum: erwacht', wuetender_baum('erwachen'), 6),
                  ('wuetender_baum_droht', 'Wütender Baum: droht dem Himmel', wuetender_baum('wuetend'), 6), ('ufer_wellen', 'Wellen am Ufer', ufer, 8), ('bach', 'Bach', bach, 6)]
    E['hilfen'] = [('funkeln', 'Funkeln (Sammelobjekt)', funkeln, 6), ('ausrufezeichen', 'Ausrufezeichen', ausrufezeichen, 6),
                   ('sprechblase', 'Sprechblase', sprechblase, 4), ('zzz', 'Schlafen (Zzz)', zzz, 6)]
    return E

def main():
    meta = {}
    titles = {'lore': 'Welt-Lore', 'dorf': 'Dorfleben', 'natur': 'Natur & Wetter', 'hilfen': 'Spielhilfen'}
    for grp, items in entries().items():
        os.makedirs(os.path.join(OUT, grp), exist_ok=True)
        prev = []
        meta[grp] = {}
        for key, title, fn, n in items:
            fr = [fn(t) for t in range(n)]
            strip(fr).save(os.path.join(OUT, grp, f'{key}.png'))
            meta[grp][key] = {'titel': title, 'bilder': n, 'bild': list(fr[0].size)}
            prev.append((title, fr))
        S = {'lore': 3, 'dorf': 3, 'natur': 3, 'hilfen': 5}[grp]
        cols = {'lore': 4, 'dorf': 5, 'natur': 5, 'hilfen': 4}[grp]
        preview(prev, os.path.join(g.BASE, f'preview_welt_{grp}.gif'), S=S, cols=cols, n_frames=8, title=titles[grp])
    meta['hinweis'] = ('Alle Animationen laufen in Schleife, außer: dungeon_huelle_ausbruch, fristhalter_eintritt, teleportpost_*, '
                       'manastau_entladung, fensterladen_*, voegel_auffliegen, sternschnuppe (einmal abspielen). '
                       'Regen/Schnee/Gewitter sind kachelbare Overlays (64x64). Empfohlen: 110-150 ms pro Bild.')
    json.dump(meta, open(os.path.join(OUT, 'welt.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
