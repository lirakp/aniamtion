"""Bosse in großer Ausführung (ca. 4x so hoch wie der Held) mit erweiterten Animationen.
Aufruf: python3 boss.py           (aus dem Ordner monster/)
Ausgabe: sprites/bosse/<name>.png (Zeile = Animation), sprites/bosse/bosse.json,
         ../preview_bosse.gif, ../preview_boss_<name>.gif (erste drei)
Animationen: idle 6 · bewegen 8 · angriff_nah 8 · angriff_spezial 10 · bruellen (Phasenwechsel) 8 ·
             benommen 6 · treffer 3 · tod 12
"""
import os, json, math, re, unicodedata
from PIL import Image, ImageDraw
from multiprocessing import Pool
from engine import pose, tint, death_frame, WHITE, C, ELEMENT_COLS, mix, shade
from render import draw, EXT
from classify import all_specs

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'sprites', 'bosse')
BOSSES = ['Glutvater', 'Frostmutter', 'Der Erste Tote', 'Hydrenkönig', 'Geisterkaiser', 'Krakenkönig', 'Schattenschleim-Mutter',
          'Höllentitan', 'Weltenbaum-Wächter', 'Ur-Phönix', 'Gletschertitan', 'Erinnerungsschlund']
TARGET_H = 168
PAD = 28
ANIMS = [('idle', 6), ('bewegen', 8), ('angriff_nah', 8), ('angriff_spezial', 10), ('bruellen', 8), ('benommen', 6), ('treffer', 3), ('tod', 12)]
ENRAGE = C('#e0443a')

def slug(name):
    s = name.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')
def lerp(seq, k):
    k = max(0, min(1, k)) * (len(seq) - 1); i = min(int(k), len(seq) - 2); f = k - i
    return seq[i] * (1 - f) + seq[i + 1] * f

# ---------------------------------------------------------------- Posen (bauen auf engine.pose auf)
def P(anim, t, n):
    k = t / n
    if anim == 'idle':
        p = pose('idle', 0); ph = k * 2 * math.pi; p.update(bob=math.sin(ph) * .015, flap=math.sin(ph), phase=ph); return p
    if anim == 'bewegen':
        p = pose('move', 0); ph = k * 2 * math.pi; p.update(walk=ph, bob=abs(math.sin(ph)) * .03, flap=math.sin(ph * 2), phase=ph); return p
    if anim == 'angriff_nah':
        k = t / (n - 1); p = pose('attack', 0)
        p.update(lunge=lerp([-.04, -.09, -.1, .16, .2, .12, .04, 0], k), open=lerp([0, .3, .5, 1, 1, .6, .2, 0], k),
                 swing=lerp([0, -.8, -1, .8, 1, .6, .2, 0], k), flap=lerp([0, .6, 1, -1, -.8, -.3, 0, 0], k), phase=k * 2 * math.pi); return p
    if anim == 'angriff_spezial':
        k = t / (n - 1); p = pose('attack', 0)
        p.update(lunge=lerp([0, -.05, -.07, .06, .08, .08, .08, .06, .02, 0], k), open=lerp([0, .4, .6, 1, 1, 1, 1, .8, .3, 0], k),
                 cast=lerp([0, .5, .8, 1, 1, 1, 1, .8, .3, 0], k), swing=lerp([0, -.5, -.8, .2, .3, .3, .3, .2, 0, 0], k),
                 flap=lerp([0, .8, 1, .2, -.2, .2, -.2, 0, 0, 0], k), phase=k * 2 * math.pi); return p
    if anim == 'bruellen':
        p = pose('attack', 0); k = t / (n - 1)
        p.update(open=lerp([0, .6, 1, 1, 1, 1, .6, 0], k), lunge=lerp([0, -.06, .02, .02, .02, .02, 0, 0], k), flap=math.sin(t * 2.2), cast=.7, swing=-.3); return p
    if anim == 'benommen':
        p = pose('hurt', 0); p.update(recoil=-.05, open=.4, bob=-.03 + math.sin(t) * .006, flap=-.5); return p
    p = pose('hurt', min(t, 2)); return p

# ---------------------------------------------------------------- Effekte auf dem fertigen Bild
def pad(im): c = Image.new('RGBA', (im.width + 2 * PAD + 60, im.height + PAD)); c.alpha_composite(im, (PAD, PAD)); return c
def silhouette_ring(im, col, k, t, dens=3):
    src = im.load(); out = im.copy(); px = out.load(); W, H = im.size
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if src[x, y][3]: continue
            if any(src[x + dx, y + dy][3] == 255 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and (x + y * 2 + t) % dens == 0:
                px[x, y] = col[:3] + (int(220 * k),)
    return out
def particles(im, cols, t, n, box, rise=True, seed=0):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = box
    for i in range(n):
        h = ((i * 7919 + seed * 104729) % 1000) / 1000; h2 = ((i * 3571 + seed * 7) % 1000) / 1000
        x = x0 + h * (x1 - x0); y = y1 - ((h2 * (y1 - y0) + t * 6 * (1 if rise else -1)) % (y1 - y0))
        r = 1 + (i % 3 == 0)
        x, y = int(x), int(y); d.rectangle([x, y, x + r - 1, y + r - 1], fill=cols[i % len(cols)])
    return im
def shake(im, dx):
    c = Image.new('RGBA', im.size); c.alpha_composite(im, (dx, 0)); return c
def shockwave(im, cx, cy, r, col):
    d = ImageDraw.Draw(im); d.ellipse([cx - r, cy - r * .35, cx + r, cy + r * .35], outline=col[:3] + (200,), width=2); return im
def stars(im, cx, cy, t):
    d = ImageDraw.Draw(im)
    for i in range(3):
        a = t / 6 * 2 * math.pi + i * 2.1; x, y = cx + math.cos(a) * 18, cy + math.sin(a) * 5
        col = C('#fff07a')
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            d.point((x + dx, y + dy), fill=WHITE if (dx, dy) == (0, 0) else col if abs(dx) + abs(dy) < 3 or abs(dx) == 1 else C('#e0b048'))
    return im
def cast_orb(im, c, r, cols, t):
    d = ImageDraw.Draw(im); x, y = c
    for k, col in enumerate(cols[::-1]):
        rr = r * (1 - k * .3); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col[:3] + (230,))
    for i in range(6):
        a = i / 6 * 2 * math.pi + t * .7; d.point((x + math.cos(a) * (r + 4), y + math.sin(a) * (r + 4)), fill=cols[0])
    return im
def beam(im, c, length, cols, t):
    d = ImageDraw.Draw(im); x, y = c
    for k, (w, col) in enumerate(((9, cols[2]), (5, cols[1]), (2, cols[0]))):
        d.line([(x, y), (x + length, y + (t % 2))], fill=col[:3] + (235,), width=w)
    for i in range(5): d.point((x + (i * 13 + t * 7) % max(1, int(length)), y - 6 + (i * 5) % 12), fill=cols[0])
    return im

OUTL = C('#2b1e33')[:3]
def pixelify(im):
    """Pixel-Schattierung für große Flächen: Glanzkante oben, gerasterter Schatten unten, leichte Struktur."""
    src = im.load(); out = im.copy(); px = out.load(); W, H = im.size
    def solid(x, y): return 0 <= x < W and 0 <= y < H and src[x, y][3] == 255 and src[x, y][:3] != OUTL
    for x in range(W):
        run_top = None
        for y in range(H):
            c = src[x, y]
            if not solid(x, y): run_top = None; continue
            if run_top is None: run_top = y
            up = y - run_top
            down = 0
            while down < 9 and solid(x, y + down + 1): down += 1
            n = None
            if up == 0 or not solid(x - 1, y) and up < 4: n = mix(c, WHITE, .28)
            elif down <= 1: n = shade(c, .66)
            elif down <= 4: n = shade(c, .78)
            elif down <= 7 and (x + y) % 2 == 0: n = shade(c, .86)
            elif not solid(x + 1, y) or not solid(x + 2, y): n = shade(c, .84)
            h = ((x * 73856093) ^ (y * 19349663)) % 1000
            if n is None and h < 45: n = shade(c, .9)
            elif n is None and h > 985: n = mix(c, WHITE, .18)
            if n: px[x, y] = n[:3] + (255,)
    return out

def element_of(spec): return spec.get('breath') or spec.get('element') or 'arkan'

def render_boss(spec):
    el = element_of(spec); cols = ELEMENT_COLS.get(el, ELEMENT_COLS['arkan'])
    l, rt, top = EXT[spec['typ']]
    spec = dict(spec); spec['px'] = int(TARGET_H / top)
    frames = {}
    for anim, n in ANIMS:
        out = []
        for t in range(n):
            if anim in ('treffer', 'tod'):
                base, origin = draw(spec, P('treffer', 0 if anim == 'tod' else t, n)); base = pixelify(base); img = pad(base)
                if anim == 'treffer':
                    img = tint(img, WHITE, .75) if t == 0 else tint(img, C('#ff4a4a'), .35) if t == 1 else img
                else:
                    if t < 4:  # Aufbäumen: Blitzen + Zittern
                        img = shake(tint(img, WHITE, .6 if t % 2 == 0 else .15), [-3, 3, -2, 2][t])
                        img = particles(img, cols, t, 14, (PAD, PAD, img.width - PAD, img.height - 4), seed=t)
                    else:
                        k = (t - 4) / 7; img = death_frame(img, k, seed=t, col=spec.get('death_col', cols[0]))
                        img = particles(img, cols, t, 30, (PAD, PAD, img.width - PAD, img.height - 4), seed=t)
                        if t == 4: shockwave(img, img.width // 2, img.height - 6, img.width // 3, cols[0])
            else:
                kb = 0
                p = P(anim, t, n)
                if anim == 'angriff_spezial' and spec.get('breath'): kb = lerp([0, 0, .3, .8, 1, 1, 1, .8, .4, 0], t / (n - 1))
                base, origin = draw(spec, p, kb); base = pixelify(base); img = pad(base)
                W_, H_ = img.size
                if anim == 'angriff_spezial' and not spec.get('breath'):
                    bb = base.getbbox(); cx, cy = PAD + bb[2] + 4, PAD + bb[1] + int((bb[3] - bb[1]) * .35)
                    if 1 <= t <= 4: cast_orb(img, (cx, cy), 3 + t * 3, cols, t)
                    elif 5 <= t <= 8: cast_orb(img, (cx, cy), 12, cols, t); beam(img, (cx + 8, cy), 56, cols, t)
                    img = particles(img, cols, t, 10, (cx - 30, cy - 30, cx + 30, cy + 30), seed=t)
                if anim == 'angriff_nah' and t in (3, 4):
                    shockwave(img, int(W_ * .75), H_ - 6, 14 + (t - 3) * 10, WHITE)
                if anim == 'bruellen':
                    k = [0, .4, 1, 1, 1, 1, .6, .2][t]
                    img = silhouette_ring(tint(img, ENRAGE, .38 * k), ENRAGE, k, t, dens=2)
                    if 2 <= t <= 5: img = shake(img, [-2, 2, -1, 1][t - 2]); shockwave(img, W_ // 2, H_ - 6, 20 + (t - 2) * 14, ENRAGE)
                    img = particles(img, [ENRAGE, C('#ff9a7a')], t, int(12 * k), (PAD, PAD, W_ - PAD, H_ - 4), seed=t + 50)
                if anim == 'benommen':
                    bb = base.getbbox(); stars(img, PAD + (bb[0] + bb[2]) // 2, PAD + bb[1] - 4, t)
            out.append(img)
        frames[anim] = out
    box = None
    for fl in frames.values():
        for f in fl:
            b = f.getbbox()
            if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    x0, y0, x1, y1 = box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1
    for k in frames: frames[k] = [f.crop((x0, y0, x1, y1)) for f in frames[k]]
    return frames, (origin[0] + PAD - x0, origin[1] + PAD - y0)

def job(args):
    entry, spec = args
    fr, origin = render_boss(spec); w, h = fr['idle'][0].size
    cols = max(n for _, n in ANIMS); s = Image.new('RGBA', (w * cols, h * len(ANIMS)))
    for r, (a, n) in enumerate(ANIMS):
        for c, f in enumerate(fr[a]): s.alpha_composite(f, (c * w, r * h))
    fn = slug(entry['name']) + '.png'; s.save(os.path.join(OUT, fn))
    return entry['name'], dict(datei=fn, bild=[w, h], bodenpunkt=list(origin), animationen={a: n for a, n in ANIMS},
                               element=element_of(spec), lebensraum=entry['lebensraum'], merkmal=entry['merkmal'], schwaeche=entry['schwaeche'])

def main():
    os.makedirs(OUT, exist_ok=True)
    specs, _ = all_specs(); todo = [(e, s) for e, s in specs if e['name'] in BOSSES]
    todo.sort(key=lambda x: BOSSES.index(x[0]['name']))
    with Pool(4) as pool: res = pool.map(job, todo)
    meta = dict(res)
    json.dump({'hinweis': 'Blick nach rechts. "bruellen" = Phasenwechsel (Boss wird wütend, rote Aura). "benommen" = Schwachstelle nach genug Treffern. Bodenpunkt = Füße/Mitte.',
               'bosse': meta}, open(os.path.join(OUT, 'bosse.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(meta)

def load(meta, name, anim, i):
    m = meta[name]; s = Image.open(os.path.join(OUT, m['datei'])); w, h = m['bild']; r = [a for a, _ in ANIMS].index(anim)
    return s.crop((i * w, r * h, (i + 1) * w, (r + 1) * h))

def preview(meta):
    import sys; sys.path.insert(0, os.path.dirname(HERE)); import generate as g
    names = list(meta)
    # Übersicht: alle Bosse idle, mit Held zum Größenvergleich
    hero = Image.open(os.path.join(os.path.dirname(HERE), 'characters', 'held', 'mensch_tunika.png')).crop((0, 0, 48, 48))
    cols = 4; cw = max(meta[n]['bild'][0] for n in names) + 16; ch = max(meta[n]['bild'][1] for n in names) + 24
    rows = math.ceil(len(names) / cols); frames = []
    for t in range(6):
        im = Image.new('RGB', (cols * cw, rows * ch), (42, 36, 69)); d = ImageDraw.Draw(im)
        for i, n in enumerate(names):
            x, y = (i % cols) * cw, (i // cols) * ch; m = meta[n]; w, h = m['bild']
            gy = y + ch - 20; d.line([(x + 4, gy), (x + cw - 4, gy)], fill=(110, 96, 120))
            f = load(meta, n, 'idle', t % 6); ox = x + 50; im.paste(f, (ox, gy - m['bodenpunkt'][1]), f)
            im.paste(hero, (x + 2, gy - 46), hero)
            d.text((x + 6, gy + 3), n, fill=(240, 230, 210), font=g.font(12))
        frames.append(im)
    frames[0].save(os.path.join(os.path.dirname(HERE), 'preview_bosse.gif'), save_all=True, append_images=frames[1:], duration=160, loop=0)
    # Detail: jeder Boss alle Animationen nacheinander
    for n in names[:3]:
        m = meta[n]; w, h = m['bild']; out = []
        for a, cnt in ANIMS:
            for i in range(cnt):
                im = Image.new('RGB', (w + 20, h + 26), (42, 36, 69)); d = ImageDraw.Draw(im)
                f = load(meta, n, a, i); im.paste(f, (10, 6), f); d.text((8, h + 8), f'{n} – {a}', fill=(240, 230, 210), font=g.font(12))
                out.append(im)
        out = [o.resize((o.width * 2, o.height * 2), Image.NEAREST) for o in out]
        out[0].save(os.path.join(os.path.dirname(HERE), f'preview_boss_{slug(n)}.gif'), save_all=True, append_images=out[1:], duration=130, loop=0)

if __name__ == '__main__':
    main()
