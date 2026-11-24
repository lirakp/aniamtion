"""Animierte Lichtquellen: Lagerfeuer, Laternen, Fackeln, Feuerschale + Lichtkreise.
Aufruf: python3 lights.py
Ausgabe in objects/licht/ (+ preview_licht.gif); Lichtpunkte in objects/licht/licht.json
Alle Animationen: 8 Bilder, ca. 110 ms pro Bild.
"""
import os, math, json, random
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
from objects import strip, gif

OUT = os.path.join(g.BASE, 'objects', 'licht')
N = 8
FIRE_W, FIRE_L, FIRE, FIRE_D = C('#fff4c8'), C('#ffd27a'), C('#ff9a3c'), C('#e8603a')
EMBER = C('#c84a2a')
IRON, IRON_L, IRON_D = C('#3a3446'), C('#5a5468'), C('#241e2c')
STONE, STONE_L, STONE_D = C('#7a7690'), C('#9a96ae'), C('#56526a')
LOG, LOG_D, LOG_END = C('#7a5236'), C('#4d3324'), C('#c8a070')
GLASS_OFF = C('#8aa4bc')

def S(img, x, y, c):
    x, y = int(x), int(y)
    if 0 <= x < img.width and 0 <= y < img.height: img.load()[x, y] = c

def flame(img, cx, base_y, halfw, H, t, seed=0.0):
    for x in range(int(math.floor(cx-halfw)), int(math.ceil(cx+halfw))+1):
        d = abs(x-cx) / halfw
        if d > 1: continue
        h = (1 - d**1.6) * H + math.sin(x*1.3 + seed + t*math.pi/2) * H*.15 + math.sin(x*.7 - t*math.pi/4 + seed) * H*.1
        h = max(1, int(round(h)))
        for k in range(h):
            rel = k / h
            c = FIRE_W if rel < .3 and d < .35 else FIRE_L if rel < .45 else FIRE if rel < .78 else FIRE_D
            S(img, x, base_y-k, c)
    # loses Flämmchen
    tx = cx + ((t*3 + int(seed*7)) % 5) - 2
    if t % 3 != 2: S(img, tx, base_y - H - 1 - (t % 2), FIRE_D)

def sparks(img, cx, top, t, n=3, spread=3):
    for i in range(n):
        p = ((t + i*N/n) % N) / N
        if p > .85: continue
        S(img, cx + math.sin(p*6 + i)*spread*.7 + (i-1)*spread*.6, top - p*9, FIRE_L if p < .5 else FIRE_D)

def blob(img, cx, cy, rx, ry, c, cl, cd):
    for y in range(int(cy-ry)-1, int(cy+ry)+2):
        for x in range(int(cx-rx)-1, int(cx+rx)+2):
            e = ((x-cx)/rx)**2 + ((y-cy)/ry)**2
            if e <= 1: S(img, x, y, cl if (x < cx and y < cy) else cd if y > cy+ry*.3 else c)

def thick_line(img, p0, p1, w, col, dark):
    d = ImageDraw.Draw(img)
    d.line([p0, p1], fill=col, width=w)
    d.line([(p0[0], p0[1]+w//2), (p1[0], p1[1]+w//2)], fill=dark, width=1)

# ---------------------------------------------------------------- Lagerfeuer
CF_W, CF_H, CF_CX, CF_BASE = 34, 38, 17, 29
def campfire_layers(lit=True):
    back = Image.new('RGBA', (CF_W, CF_H), (0, 0, 0, 0)); front = back.copy()
    for i in range(12):
        a = i/12 * 2*math.pi
        x, y = CF_CX + 13*math.cos(a), 31 + 4.5*math.sin(a)
        blob(back if math.sin(a) < 0 else front, x, y, 2.4, 1.7, STONE, STONE_L, STONE_D)
    rng = random.Random(5)
    if lit:
        for _ in range(40):
            S(back, rng.randint(10, 24), rng.randint(28, 31), rng.choice([FIRE, EMBER, FIRE_D, C('#5a2a22')]))
    else:
        for _ in range(40):
            S(back, rng.randint(10, 24), rng.randint(28, 31), rng.choice([C('#8a8494'), C('#6a6476'), C('#4a4452')]))
    lc, ld = (LOG, LOG_D) if lit else (C('#3a2a26'), C('#221818'))
    thick_line(back, (8, 32), (26, 26), 3, lc, ld); thick_line(back, (8, 26), (26, 32), 3, lc, ld)
    for (x, y) in ((8, 32), (26, 26), (8, 26), (26, 32)):
        blob(back, x, y, 1.6, 1.6, LOG_END if lit else C('#5a4a40'), LOG_END, shade(LOG_END, .8))
    return g.outline(back), g.outline(front)

def campfire(t, layers):
    back, front = layers
    im = back.copy()
    flame(im, CF_CX, CF_BASE, 7.5, 15, t, 0.3)
    flame(im, CF_CX-4, CF_BASE, 3.5, 8, (t+3) % N, 1.7)
    flame(im, CF_CX+4, CF_BASE, 3.5, 9, (t+5) % N, 2.9)
    im.alpha_composite(front)
    sparks(im, CF_CX, CF_BASE-16, t)
    return im

# ---------------------------------------------------------------- Laternen
def candle(img, x, y, t):
    S(img, x, y, FIRE_L); S(img, x, y-1, FIRE_W if t % 2 else FIRE_L)
    if t % 4 == 1: S(img, x, y-2, FIRE)
    elif t % 4 == 3: S(img, x+1, y-1, FIRE)

def lantern_body(img, x0, y0, t, lit):
    """Laternengehäuse 8 breit, 14 hoch, ab (x0,y0)"""
    S(img, x0+3, y0, IRON); S(img, x0+4, y0, IRON)                     # Knauf
    for i, (a, b) in enumerate(((2, 5), (1, 6), (0, 7))):              # Dach
        for x in range(a, b+1): S(img, x0+x, y0+1+i, IRON_L if x == a else IRON)
    for y in range(y0+4, y0+12):
        for x in range(x0, x0+8):
            edge = x in (x0, x0+7) or y in (y0+4, y0+11)
            if edge: c = IRON
            elif lit:
                pulse = .5 + .5*math.sin(t*math.pi/4)
                c = mix(FIRE_L, FIRE_W, pulse*.6) if (x-x0)+(y-y0-4) < 6 else mix(FIRE, FIRE_L, .5+pulse*.3)
            else: c = GLASS_OFF if (x-x0)-(y-y0) != -3 else mix(GLASS_OFF, (255,)*4, .4)
            S(img, x, y, c)
    for y in range(y0+4, y0+12): S(img, x0+4, y, IRON)                 # Steg
    if lit: candle(img, x0+3, y0+9, t)
    for x in range(x0+1, x0+7): S(img, x, y0+12, IRON)
    for x in range(x0+2, x0+6): S(img, x, y0+13, IRON_D)

def street_lantern(t, lit=True):
    im = Image.new('RGBA', (14, 40), (0, 0, 0, 0))
    lantern_body(im, 3, 1, t, lit)
    for y in range(15, 37):
        S(im, 6, y, IRON); S(im, 7, y, IRON_D)
    for x in range(4, 10): S(im, x, 20, IRON_L)
    S(im, 5, 21, IRON); S(im, 8, 21, IRON)
    for y, (a, b) in ((35, (4, 9)), (36, (3, 10)), (37, (3, 10))):
        for x in range(a, b+1): S(im, x, y, IRON_L if y == 35 else IRON)
    return g.outline(im)

def hanging_lantern(t, lit=True):
    im = Image.new('RGBA', (20, 30), (0, 0, 0, 0))
    for y in range(1, 9):                                              # Wandplatte
        for x in range(0, 3): S(im, x, y, IRON if x else IRON_L)
    for x in range(2, 15): S(im, x, 3, IRON)                           # Arm
    for (x, y) in ((4, 4), (5, 5), (6, 6), (5, 7)): S(im, x, y, IRON_L) # Zierbogen
    S(im, 14, 2, IRON_L)
    dx = round(math.sin(t*2*math.pi/N) * 1.2)
    for k in range(4):
        S(im, 13 + round(dx*k/4), 4+k, IRON_L if k % 2 else IRON)
    lantern_body(im, 9+dx, 7, t, lit)
    return g.outline(im)

# ---------------------------------------------------------------- Fackeln
def standing_torch(t, lit=True):
    im = Image.new('RGBA', (12, 36), (0, 0, 0, 0))
    for y in range(14, 34): S(im, 5, y, LOG); S(im, 6, y, LOG_D)
    S(im, 5, 34, LOG_D)
    for y in (18, 26): S(im, 4, y, IRON); S(im, 7, y, IRON)
    for x in range(3, 9): S(im, x, 13, IRON); S(im, x, 12, IRON_L if x in (3, 8) else IRON)
    for x in range(4, 8): S(im, x, 11, C('#8a6a4a') if lit else C('#3a2a26'))
    base = g.outline(im)
    if lit:
        flame(base, 5.5, 10, 3.2, 9, t, .8)
        sparks(base, 5.5, 0, t, n=2, spread=2)
    return base

def wall_torch(t, lit=True):
    im = Image.new('RGBA', (12, 26), (0, 0, 0, 0))
    for y in range(14, 23):
        for x in range(2, 5): S(im, x, y, IRON_L if x == 2 else IRON)
    S(im, 3, 16, IRON_D); S(im, 3, 20, IRON_D)
    for i in range(4): S(im, 5+i//2, 18-i, IRON)                       # Halter
    for y in range(9, 18): S(im, 6, y, LOG); S(im, 7, y, LOG_D)
    for x in range(5, 9): S(im, x, 12, IRON)
    for x in range(5, 9): S(im, x, 9, C('#8a6a4a') if lit else C('#3a2a26'))
    base = g.outline(im)
    if lit: flame(base, 6.5, 8, 2.6, 7, t, 2.2)
    return base

def brazier(t, lit=True):
    im = Image.new('RGBA', (20, 34), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line([(4, 33), (8, 22)], fill=IRON); d.line([(15, 33), (11, 22)], fill=IRON); d.line([(9, 33), (9, 22)], fill=IRON_D)
    for x in range(5, 15): S(im, x, 28, IRON)
    for i, y in enumerate(range(17, 23)):
        for x in range(2+i//2, 18-i//2): S(im, x, y, IRON_L if y == 17 else IRON if x < 13 else IRON_D)
    rng = random.Random(9)
    for x in range(3, 17):
        S(im, x, 16, rng.choice([FIRE, EMBER, FIRE_D]) if lit else rng.choice([C('#4a4452'), C('#6a6476')]))
    base = g.outline(im)
    if lit:
        flame(base, 9.5, 15, 6.5, 12, t, .4)
        sparks(base, 9.5, 2, t, n=3, spread=3)
    return base

# ---------------------------------------------------------------- Lichtkreise
def light_circle(R, t, col=(255, 176, 84)):
    s = R*2 + 4
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); px = im.load()
    r = R * (1 + .04*math.sin(t*2*math.pi/N) + .02*math.sin(t*math.pi))
    c = s / 2
    for y in range(s):
        for x in range(s):
            d = math.hypot(x+.5-c, y+.5-c) / r + ((x+y) % 2) * .06
            a = 96 if d < .4 else 64 if d < .65 else 36 if d < .85 else 16 if d < 1 else 0
            if a: px[x, y] = col + (a,)
    return im

OBJECTS = {
    # name: (funktion, Lichtpunkt (x,y) im Bild, Lichtradius)
    'lagerfeuer':     (None, (CF_CX, CF_BASE-6), 34),
    'strassenlaterne': (street_lantern, (7, 9), 26),
    'haengelaterne':  (hanging_lantern, (13, 15), 22),
    'standfackel':    (standing_torch, (5, 6), 24),
    'wandfackel':     (wall_torch, (6, 5), 20),
    'feuerschale':    (brazier, (9, 10), 30),
}

def main():
    os.makedirs(OUT, exist_ok=True)
    meta, anims = {}, {}
    lit_layers, off_layers = campfire_layers(True), campfire_layers(False)
    for name, (fn, (lx, ly), R) in OBJECTS.items():
        if name == 'lagerfeuer':
            fr = [campfire(t, lit_layers) for t in range(N)]
            aus = off_layers[0].copy(); aus.alpha_composite(off_layers[1])
        else:
            fr = [fn(t) for t in range(N)]; aus = fn(0, lit=False)
        strip(fr).save(os.path.join(OUT, f'{name}_anim.png'))
        aus.save(os.path.join(OUT, f'{name}_aus.png'))
        gif(fr, os.path.join(OUT, f'{name}.gif'), 110, scale=6)
        lc = [light_circle(R, t) for t in range(N)]
        strip(lc).save(os.path.join(OUT, f'{name}_lichtkreis.png'))
        meta[name] = {'bild': list(fr[0].size), 'bilder': N, 'ms_pro_bild': 110,
                      'lichtpunkt': [lx, ly], 'lichtkreis_groesse': list(lc[0].size),
                      'hinweis': 'Lichtkreis mittig auf den Lichtpunkt legen, additiv oder normal mischen'}
        anims[name] = (fr, lc, (lx, ly))
    with open(os.path.join(OUT, 'licht.json'), 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    # Vorschau-Szene bei Nacht
    Sx = 4; Wv, Hv = 520, 70; ground = 58
    pos = {'lagerfeuer': 14, 'strassenlaterne': 96, 'haengelaterne': 160, 'standfackel': 236,
           'wandfackel': 300, 'feuerschale': 360}
    frames = []
    for t in range(N):
        sc = Image.new('RGBA', (Wv, Hv), g.SKY_NIGHT)
        ImageDraw.Draw(sc).rectangle([0, ground, Wv, Hv], fill=g.GROUND_NIGHT)
        # Mauerstück für Wandfackel/Hängelaterne
        ImageDraw.Draw(sc).rectangle([148, 12, 152, ground], fill=C('#4a4458'))
        ImageDraw.Draw(sc).rectangle([288, 20, 294, ground], fill=C('#4a4458'))
        for name, (fr, lc, (lx, ly)) in anims.items():
            f = fr[t]; x = pos[name]
            if name == 'haengelaterne': y = 12
            elif name == 'wandfackel': y = 22; x = 291
            else: y = ground - f.height + 2
            if name == 'haengelaterne': x = 150
            l = lc[t]; sc.alpha_composite(l, (x+lx-l.width//2, y+ly-l.height//2))
        for name, (fr, lc, (lx, ly)) in anims.items():
            f = fr[t]; x = pos[name]
            if name == 'haengelaterne': x, y = 150, 12
            elif name == 'wandfackel': x, y = 291, 22
            else: y = ground - f.height + 2
            sc.alpha_composite(f, (x, y))
        big = sc.resize((Wv*Sx, Hv*Sx), Image.NEAREST)
        ImageDraw.Draw(big).text((12, 8), 'Lagerfeuer, Laternen, Fackeln, Feuerschale (mit Lichtkreisen)', fill=(255, 240, 200), font=g.font(18))
        frames.append(big.convert('RGB'))
    frames[0].save(os.path.join(g.BASE, 'preview_licht.gif'), save_all=True, append_images=frames[1:], duration=110, loop=0)

if __name__ == '__main__':
    main()
