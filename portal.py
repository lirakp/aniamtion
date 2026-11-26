"""Portal: stehendes Oval, leicht durchsichtig, mit wirbelndem Inneren und funkelndem Rand.
Aufruf: python3 portal.py
Ausgabe: objects/portal/portal_<farbe>.png  (Zeilen: oeffnen 8 · offen 12 (Schleife) · durchgang 6 · schliessen 8; Zelle 56x72)
         objects/portal/portal.json, preview_portal.gif
Das Innere hat ca. 45–65 % Deckkraft, der Hintergrund scheint also durch. Bodenpunkt = unten Mitte (28, 70).
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, mix

OUT = os.path.join(g.BASE, 'objects', 'portal')
CW, CH = 56, 72
CX, CY = 28, 38          # Mitte des Ovals
RX, RY = 19, 29          # Halbachsen
N_OPEN, N_LOOP, N_PASS, N_CLOSE = 8, 12, 6, 8
FARBEN = {  # dunkel, mittel, hell, Rand/Funken
    'violett': (C('#3a2a6a'), C('#7a5ad0'), C('#b8a0ff'), C('#f0e8ff')),
    'blau':    (C('#1e3a6a'), C('#3a7ac8'), C('#8ad0ff'), C('#e8f8ff')),
    'gruen':   (C('#1e4a3a'), C('#3a9a6a'), C('#8ae0a8'), C('#eaffe8')),
    'rot':     (C('#5a1a2a'), C('#c83a3a'), C('#ff8a6a'), C('#fff0d8')),
}

def h(i, s):
    x = (i * 374761393 + s * 668265263) & 0xffffffff
    x = ((x ^ (x >> 13)) * 1274126177) & 0xffffffff
    return ((x ^ (x >> 16)) & 0xffffff) / 0x1000000

def portal(col, scale, phase, glow=0.0, flash=0.0):
    """scale 0..1 = Öffnungsgrad, phase 0..1 = Wirbel-Phase (Schleife), glow = Durchgang-Aufleuchten."""
    dk, md, lt, rim = col
    im = Image.new('RGBA', (CW, CH)); px = im.load()
    if scale <= 0.02: return im
    rx, ry = max(1.0, RX * scale), RY * min(1.0, .35 + scale * .65)
    ph = phase * 2 * math.pi
    for y in range(CH):
        for x in range(CW):
            dx, dy = (x + .5 - CX) / rx, (y + .5 - CY) / ry
            r = math.hypot(dx, dy)
            if r > 1.0: continue
            a = math.atan2(dy, dx)
            if r > .86:  # Rand: hell, fast deckend, leicht pulsierend
                k = (math.sin(a * 6 - ph * 2) + 1) / 2
                c = mix(lt, rim, k * .7)
                px[x, y] = c[:3] + (235,)
                continue
            # Spiralwirbel: 3 Arme, die sich nach innen drehen
            v = math.sin(a * 3 + r * 9 - ph) * .5 + .5
            v2 = math.sin(a * 2 - r * 6 + ph * 2) * .5 + .5
            band = v * .7 + v2 * .3
            c = dk if band < .35 else md if band < .7 else lt
            if r < .22: c = mix(c, rim, (1 - r / .22) * .6)   # heller Kern
            c = mix(c, rim, glow * (1 - r) * .9)
            # Pixel-Raster: dunkle Stellen etwas durchsichtiger
            alpha = int(115 + 50 * band + 40 * (1 - r) + glow * 60)
            if (x + y) % 2 and band < .35: alpha -= 25
            px[x, y] = c[:3] + (min(230, alpha),)
    d = ImageDraw.Draw(im)
    # Außenkontur (dünn, halbdeckend, damit der Pixel-Stil erhalten bleibt)
    d.ellipse([CX - rx - 1, CY - ry - 1, CX + rx, CY + ry], outline=dk[:3] + (200,))
    # Funken, die um den Rand kreisen und nach innen gezogen werden
    for i in range(10):
        a = h(i, 1) * 2 * math.pi + ph * (1 if i % 2 else -1)
        rr = 1.08 - ((phase + h(i, 2)) % 1.0) * .9
        x, y = CX + math.cos(a) * rx * rr, CY + math.sin(a) * ry * rr
        if 0 <= x < CW and 0 <= y < CH:
            d.point((x, y), fill=rim[:3] + (255,))
            if i % 3 == 0: d.point((x + 1, y), fill=lt[:3] + (200,)); d.point((x, y + 1), fill=lt[:3] + (200,))
    # Bodenschein
    gy = CY + ry + 2
    if gy < CH:
        for k, aa in ((rx + 4, 50), (rx, 90)):
            d.ellipse([CX - k, gy - 1.5, CX + k, gy + 1.5], fill=md[:3] + (int(aa * scale),))
    if flash:
        ov = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.ellipse([CX - rx - 3, CY - ry - 3, CX + rx + 3, CY + ry + 3], fill=rim[:3] + (int(170 * flash),))
        im = Image.alpha_composite(im, ov)
    return im

def frames(col):
    ease = lambda k: 1 - (1 - k) ** 3
    op = [portal(col, ease((i + 1) / N_OPEN), i / N_OPEN, flash=.8 if i == N_OPEN - 2 else 0) for i in range(N_OPEN)]
    lp = [portal(col, 1, i / N_LOOP) for i in range(N_LOOP)]
    ps = [portal(col, 1 + .05 * math.sin(i / (N_PASS - 1) * math.pi), i / N_PASS, glow=math.sin(i / (N_PASS - 1) * math.pi), flash=.5 if i == 2 else 0) for i in range(N_PASS)]
    cl = [portal(col, 1 - ease((i + 1) / N_CLOSE) * .98, i / N_CLOSE, flash=.7 if i == 0 else 0) for i in range(N_CLOSE)]
    return {'oeffnen': op, 'offen': lp, 'durchgang': ps, 'schliessen': cl}

ORDER = ['oeffnen', 'offen', 'durchgang', 'schliessen']

def main():
    os.makedirs(OUT, exist_ok=True); meta = {}
    allf = {}
    for name, col in FARBEN.items():
        F = frames(col); allf[name] = F
        cols = max(len(v) for v in F.values()); s = Image.new('RGBA', (CW * cols, CH * len(ORDER)))
        for r, a in enumerate(ORDER):
            for c, f in enumerate(F[a]): s.alpha_composite(f, (c * CW, r * CH))
        s.save(os.path.join(OUT, f'portal_{name}.png')); meta[name] = f'portal_{name}.png'
    json.dump({'zelle': [CW, CH], 'bodenpunkt': [CX, CH - 2], 'zeilen': ORDER,
               'frames': {'oeffnen': N_OPEN, 'offen': N_LOOP, 'durchgang': N_PASS, 'schliessen': N_CLOSE},
               'fps': {'oeffnen': 12, 'offen': 10, 'durchgang': 14, 'schliessen': 12},
               'hinweis': 'oeffnen einmal → offen in Schleife → beim Betreten durchgang → schliessen einmal. Inneres ist halbtransparent.',
               'farben': meta}, open(os.path.join(OUT, 'portal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(allf)

def preview(allf):
    bg = Image.new('RGBA', (320, 180), (30, 24, 40, 255))
    par = os.path.join(g.BASE, 'level', 'parallax')
    for k, n in enumerate(['himmel', 'berge', 'huegel', 'wald']):
        p = os.path.join(par, f'dorf_nacht_{k}_{n}.png')
        if os.path.exists(p): bg.alpha_composite(Image.open(p).convert('RGBA'))
    hero = None
    hp = os.path.join(g.BASE, 'characters', 'held', 'mensch_tunika.png')
    if os.path.exists(hp): hero = Image.open(hp).crop((0, 0, 48, 48))
    seq = []
    for a in ORDER:
        n = len(allf['violett'][a]); reps = 2 if a == 'offen' else 1
        for _ in range(reps):
            for i in range(n): seq.append((a, i))
    out = []
    for a, i in seq:
        im = bg.copy()
        for k, name in enumerate(FARBEN):
            x = 60 + k * 64; y = 180 - 14 - CH
            im.alpha_composite(allf[name][a][i], (x, y))
        if hero: im.alpha_composite(hero, (2, 180 - 14 - 46))
        out.append(im.resize((960, 540), Image.NEAREST).convert('RGB'))
    out[0].save(os.path.join(g.BASE, 'preview_portal.gif'), save_all=True, append_images=out[1:], duration=90, loop=0)

if __name__ == '__main__':
    main()
