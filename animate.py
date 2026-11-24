"""Gebäude-Animationen (8 Bilder, empfohlen 120-150 ms pro Bild).
Aufruf: python3 animate.py
Ausgabe: buildings/anim/<name>_<tag>_anim.png   (8 Bilder nebeneinander)
         buildings/anim/<name>_<tag>.gif
         preview_gebaeude_anim_<tag>.gif
Jedes Bild ist 16 px höher als das statische Gebäude (Platz für Rauch) -> unten ausrichten.
"""
import os, math
from PIL import Image
import generate as g, shops as sh
from generate import C, mix

N, PAD = 8, 16
OUT = os.path.join(g.BASE, 'buildings', 'anim')
FIRE, FIRE_L, FIRE_D = C('#ff9a3c'), C('#ffd27a'), C('#e8603a')
INTERIOR = C('#241a22')
WHITE = (255, 255, 255, 255)

def P(px, img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height: px[x, y] = c

# ---------------------------------------------------------------- Effekte
def smoke(img, ox, oy, t, col, night, puffs=3, rise=18):
    px = img.load()
    if night: col = mix(col, g.SKY_NIGHT, .35)
    light = mix(col, WHITE, .3)
    for i in range(puffs):
        p = ((t + i*N/puffs) % N) / N
        cx = ox + p*5 + math.sin(p*7)*1.0
        cy = oy + PAD - 1 - p*rise
        r = 1.6 + p*2.4
        for y in range(int(cy-r)-1, int(cy+r)+2):
            for x in range(int(cx-r)-1, int(cx+r)+2):
                if (x-cx)**2 + (y-cy)**2 <= r*r:
                    if p > .8 and (x+y) % 2: continue
                    P(px, img, x, y, light if (x < cx and y < cy) else col)

def fire(img, x0, x1, ybase, maxh, t, bg=INTERIOR):
    px = img.load(); yb = ybase + PAD
    for y in range(yb-maxh-2, yb+1):
        for x in range(x0, x1+1): P(px, img, x, y, bg)
    for x in range(x0, x1+1):
        v = math.sin(x*1.7 + t*N/4*1.3) + math.sin(x*0.9 - t*2*math.pi/N*2)
        h = max(1, min(maxh, int(1.5 + (v+2)/4*maxh)))
        for k in range(h):
            P(px, img, x, yb-k, FIRE_L if k == 0 else FIRE if k < h-1 else FIRE_D)
    w = x1-x0+1
    for i in range(2):
        sx = x0 + (t*3 + i*5) % w; sy = yb - maxh - 1 - ((t + i*4) % 3)
        P(px, img, sx, sy, FIRE_L)

TORCH_SHAPES = [{(0, 0): FIRE, (0, -1): FIRE_L},
                {(0, 0): FIRE, (0, -1): FIRE_L, (0, -2): FIRE_D},
                {(0, 0): FIRE_L, (0, -1): FIRE, (-1, -1): FIRE_D},
                {(0, 0): FIRE, (0, -1): FIRE_L, (1, -2): FIRE}]
def torch(img, x, y, t, i=0):
    px = img.load()
    for (dx, dy), c in TORCH_SHAPES[(t + i) % 4].items(): P(px, img, x+dx, y+dy+PAD, c)

def hot_metal(img, x0, x1, y, t):
    px = img.load()
    for x in range(x0, x1+1): P(px, img, x, y+PAD, FIRE_L if (x + t) % 3 == 0 else FIRE)

def pennant(img, t, col):
    px = img.load()
    for y in range(0, 8):
        for x in range(55, 64): P(px, img, x, y+PAD, (0, 0, 0, 0))
    lay = Image.new('RGBA', (12, 10), (0, 0, 0, 0)); lp = lay.load()
    lens = [3, 5, 6, 5, 3]
    for r, ln in enumerate(lens):
        for k in range(ln):
            dy = round(math.sin(k*0.9 - t*2*math.pi/N) * (k/ln))
            yy = 2 + r + dy
            if 0 <= yy < 10: lp[1+k, yy] = col if r < 4 else g.shade(col, .8)
    lay = g.outline(lay, g.B_OUTLINE)
    for y in range(10):
        for x in range(12):
            if lp[x, y][3] or lay.load()[x, y][3]:
                c = lay.load()[x, y]
                if c[3]: P(px, img, 54+x, y-1+PAD, c)
    for y in range(0, 10): P(px, img, 54, y+PAD, C('#3a3446'))
    P(px, img, 54, PAD, g.GOLD)

def bell(img, t):
    px = img.load()
    for y in range(45, 57):
        for x in range(18, 30): P(px, img, x, y+PAD, INTERIOR)
    dx = [0, 1, 1, 0, 0, -1, -1, 0][t]
    for y in (45, 46):
        for x in (23, 24): P(px, img, x, y+PAD, g.WOOD_D)
    for x in range(21+dx, 27+dx): P(px, img, x, 47+PAD, g.GOLD)
    for y in range(48, 53):
        for x in range(20+dx, 28+dx): P(px, img, x, y+PAD, g.GOLD)
    for x in range(19+dx, 29+dx): P(px, img, x, 53+PAD, g.GOLD)
    for y in range(48, 52): P(px, img, 21+dx, y+PAD, g.GOLD_L)
    for x in (23, 24): P(px, img, x - dx, 54+PAD, C('#b08030'))

SPARKS = [(6, 22), (70, 30), (67, 14), (9, 42), (72, 52), (64, 66)]
def sparkles(img, t):
    px = img.load()
    for i, (x, y) in enumerate(SPARKS):
        for yy in range(y-2, y+3):
            for xx in range(x-2, x+3): P(px, img, xx, yy+PAD, (0, 0, 0, 0))
        s = (t + i*3) % N
        if s in (0, 1):
            P(px, img, x, y+PAD, C('#ffffff'))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): P(px, img, x+dx, y+dy+PAD, sh.MAGIC_LIT[0])
        elif s in (2, 3, 7):
            P(px, img, x, y+PAD, C('#e0f0ff'))
    # aufsteigende Funken über dem Turmdach
    for i in range(3):
        p = ((t + i*N/3) % N) / N
        P(px, img, 30 + i*8 + round(math.sin(p*6)), round(34 - p*20) + PAD, sh.MAGIC_LIT[1] if p < .6 else sh.MAGIC_LIT[0])

GREY, DARKSMOKE, GREEN = C('#cfc9d8'), C('#8a8296'), C('#a8d8a0')
SPECS = {
    'cottage':   lambda im, t, n: smoke(im, 53, 5, t, GREY, n),
    'baeckerei': lambda im, t, n: smoke(im, 60, 1, t, GREY, n),
    'schmiede':  lambda im, t, n: (smoke(im, 66, 1, t, DARKSMOKE, n), fire(im, 19, 32, 51, 4, t)),
    'taverne':   lambda im, t, n: (smoke(im, 19, 1, t, GREY, n), smoke(im, 77, -1, (t+3) % N, GREY, n)),
    'windmuehle': None,  # wird pro Bild neu gezeichnet
    'kirche':    lambda im, t, n: bell(im, t),
    'gilde_abenteuer': lambda im, t, n: (pennant(im, t, C('#a8383e')), torch(im, 44, 91, t), torch(im, 65, 91, t, 2)),
    'gilde_handel':    lambda im, t, n: (pennant(im, t, C('#3f7a52')), torch(im, 44, 91, t), torch(im, 65, 91, t, 2)),
    'laden_alchemie':  lambda im, t, n: smoke(im, 47, 11, t, GREEN, n, puffs=4),
    'laden_dungeon':   lambda im, t, n: (torch(im, 47, 56, t), torch(im, 65, 56, t, 1)),
    'laden_magie':     lambda im, t, n: sparkles(im, t),
    'schmiede_ruestung': lambda im, t, n: (smoke(im, 67, 1, t, DARKSMOKE, n), fire(im, 16, 23, 73, 3, t), hot_metal(im, 27, 31, 79, t)),
    'schmiede_waffen':   lambda im, t, n: (smoke(im, 26, 1, t, DARKSMOKE, n), fire(im, 70, 77, 75, 3, t), hot_metal(im, 61, 65, 79, t)),
}

def builders():
    allb = {n: fn for n, _, fn in g.BUILDINGS}
    allb.update({n: fn for n, _, fn in sh.SHOPS})
    titles = {n: tt for n, tt, _ in g.BUILDINGS + sh.SHOPS}
    return allb, titles

def frames_for(name, fn, night):
    out = []
    base = None if name == 'windmuehle' else fn(night)
    for t in range(N):
        if name == 'windmuehle':
            g.MILL_ANGLE = t * 90 / N; b = fn(night); g.MILL_ANGLE = 0
        else:
            b = base
        im = Image.new('RGBA', (b.width, b.height + PAD), (0, 0, 0, 0)); im.alpha_composite(b, (0, PAD))
        if SPECS[name]: SPECS[name](im, t, night)
        out.append(im)
    return out

def main():
    g.ANIMATING = True
    os.makedirs(OUT, exist_ok=True)
    allb, titles = builders()
    for night, tag in ((False, 'tag'), (True, 'nacht')):
        per_frame = [[] for _ in range(N)]
        for name in SPECS:
            fr = frames_for(name, allb[name], night)
            w, h = fr[0].size
            sheet = Image.new('RGBA', (w*N, h), (0, 0, 0, 0))
            for i, f in enumerate(fr): sheet.alpha_composite(f, (i*w, 0))
            sheet.save(os.path.join(OUT, f'{name}_{tag}_anim.png'))
            bg = g.SKY_NIGHT if night else g.SKY_DAY
            gif = []
            for f in fr:
                b = Image.new('RGBA', (w*4, h*4), bg); b.alpha_composite(f.resize((w*4, h*4), Image.NEAREST)); gif.append(b.convert('RGB'))
            gif[0].save(os.path.join(OUT, f'{name}_{tag}.gif'), save_all=True, append_images=gif[1:], duration=130, loop=0)
            for t in range(N): per_frame[t].append((titles[name], fr[t]))
        prev = [g.sheet(items, 3, night, f"Cosy - animierte Gebäude ({'Nacht' if night else 'Tag'})", 5).convert('RGB') for items in per_frame]
        prev[0].save(os.path.join(g.BASE, f'preview_gebaeude_anim_{tag}.gif'), save_all=True, append_images=prev[1:], duration=130, loop=0)

if __name__ == '__main__':
    main()
