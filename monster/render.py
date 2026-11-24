"""Rendert ein Monster (Spec) in alle Animationen und schneidet das Ergebnis zu."""
import math
from PIL import Image
from engine import R, ANIMS, pose, finalize, tint, death_frame, breath, WHITE, C
from archetypes import ARCHETYPES

EXT = {  # links, rechts, oben (Welteinheiten)
    'vierbeiner': (1.0, 1.2, 1.5), 'zweibeiner': (.8, 1.0, 1.4), 'flieger': (1.0, 1.2, 1.3), 'insekt': (.8, 1.0, 1.0),
    'schlange': (1.2, 1.4, 1.1), 'fisch': (1.0, 1.1, 1.1), 'krake': (.7, 1.6, 1.1), 'schleim': (.7, 1.0, 1.0),
    'geist': (.7, 1.0, 1.3), 'wolke': (1.0, 1.2, 1.1), 'pflanze': (.7, 1.2, 1.4), 'schwarm': (.9, 1.5, 1.1),
    'objekt': (.9, 1.3, 1.5), 'drache': (1.6, 1.3, 1.7), 'kroete': (.7, 1.5, 1.0), 'schnecke': (.8, 1.0, .9),
    'schlund': (.9, 1.1, 1.2),
}

MAT = {
    'stein': None, 'eisen': None, 'kristall': C('#c0f0ff'), 'lava': C('#ff9a3c'), 'eis': C('#ffffff'),
    'holz': None, 'runen': C('#7ae0ff'), 'koralle': C('#f08a8a'), 'dornen': C('#2e3a26'), 'salz': C('#ffffff'),
    'schlamm': None, 'erz': C('#d8a848'), 'sand': None, 'asche': C('#ff7a3a'), 'knochen': None, 'wrack': None,
}
def texture(r, spec):
    from engine import light, shade, mix
    base = spec.get('skin', spec['col'])
    cols = {base[:3], light(base)[:3], shade(base, .72)[:3]}
    kind = spec['material']; acc = MAT.get(kind)
    px = r.px
    for y in range(r.H):
        for x in range(r.W):
            c = px[x, y]
            if c[3] == 0 or c[:3] not in cols: continue
            n = None
            if kind in ('stein', 'runen', 'sand', 'schlamm', 'salz', 'wrack'):
                if y % 5 == 0 or (x + (y // 5) * 3) % 7 == 0: n = shade(c, .78)
                if kind == 'runen' and (x * 7 + y * 3) % 29 == 0: n = acc
                if kind == 'salz' and (x + y) % 9 == 0: n = acc
            elif kind == 'eisen':
                if y % 6 == 0: n = shade(c, .7)
                elif x % 5 == 2 and y % 6 == 3: n = light(c, .5)
            elif kind in ('kristall', 'eis'):
                if (x + y) % 6 == 0: n = mix(c, acc, .6)
                elif (x - y) % 7 == 0: n = shade(c, .82)
            elif kind in ('lava', 'asche'):
                if (x * 3 + y * 5) % 11 == 0 or (x - y * 2) % 13 == 0: n = acc
            elif kind == 'holz':
                if x % 3 == 0: n = shade(c, .8)
            elif kind in ('koralle', 'erz'):
                if (x * 5 + y * 3) % 9 == 0: n = acc
            elif kind == 'dornen':
                if (x * 3 + y * 7) % 8 == 0: n = acc
            if n: px[x, y] = n[:3] + (255,)

def draw(spec, p, k_breath=0.0):
    S = spec['px']
    l, rt, top = EXT[spec['typ']]
    if spec.get('typ') == 'schlange': l = rt = spec.get('L', 1.3)/2 + .5
    if spec.get('breath'): rt += .9
    W, H = int(S * (l + rt)) + 10, int(S * top) + 10
    r = R(W, H, S, l * S + 5, H - 4)
    anchors = ARCHETYPES[spec['typ']](r, spec, p) or {}
    if spec.get('material'): texture(r, spec)
    if k_breath and anchors.get('mund'):
        mx, my = anchors['mund']
        breath(r, mx, my, k_breath, spec.get('breath'), length=spec.get('breath_len', .8), seed=p['t'])
    return finalize(r.img), (int(l * S + 5), H - 4)

def render_all(spec):
    frames = {}
    origin = None
    for anim, n in ANIMS:
        out = []
        for t in range(n):
            if anim in ('idle', 'move', 'attack'):
                p = pose(anim, t)
                kb = [0, 0, .5, 1, .7, 0][t] if (anim == 'attack' and spec.get('breath')) else 0
                img, origin = draw(spec, p, kb)
            elif anim == 'hurt':
                img, origin = draw(spec, pose('hurt', t))
                if t == 0: img = tint(img, WHITE, .75)
                elif t == 1: img = tint(img, C('#ff4a4a'), .35)
            else:
                base, origin = draw(spec, pose('hurt', 0))
                img = tint(base, WHITE, .5) if t == 0 else death_frame(base, t / 5, seed=t,
                                                                      col=spec.get('death_col', C('#d8d0e8')))
            out.append(img)
        frames[anim] = out
    # gemeinsamer Zuschnitt
    box = None
    for fl in frames.values():
        for f in fl:
            b = f.getbbox()
            if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = max(0, x0 - 1), max(0, y0 - 1), x1 + 1, y1 + 1
    for k in frames: frames[k] = [f.crop((x0, y0, x1, y1)) for f in frames[k]]
    return frames, (origin[0] - x0, origin[1] - y0)

def sheet(frames):
    w, h = frames['idle'][0].size
    cols = max(n for _, n in ANIMS)
    s = Image.new('RGBA', (w * cols, h * len(ANIMS)), (0, 0, 0, 0))
    for row, (anim, n) in enumerate(ANIMS):
        for c, f in enumerate(frames[anim]): s.alpha_composite(f, (c * w, row * h))
    return s
