"""Kampf- und Zauber-Animationen für alle Völker (4 Richtungen).
Aufruf: python3 combat.py
Ausgabe: characters/voelker/kampf/<volk>_<kleidung>_<animation>.png
         Zellen 26x26 (Figur mittig, Füße unten), Zeilen: unten, links, rechts, oben.
Animationen: angriff 5 · treffer 3 · tod 5 · zauber_geschoss 6 · zauber_flaeche 6 · zauber_selbst 6
             kanalisieren 4 (Schleife) · bruchklang 6 · ueberlastung 6
Das Leuchten an den Händen ist neutrales Mana. Die Element-Effekte liegen in effects/magie (magic.py).
"""
import os, math
from PIL import Image, ImageDraw
import generate as g, walk as w, races as rc
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'characters', 'voelker', 'kampf')
CELL = 26
MANA, MANA_CORE = C('#8ad8ff'), C('#f0fcff')
BRUCH_A, BRUCH_B = C('#ff9a3c'), C('#7ab8ff')
BLOOD = C('#b8283a')
STEEL_W, HILT = C('#e0e4ee'), C('#e0b048')

def strip_arms(rows):
    out = []
    for i, r in enumerate(rows):
        if 14 <= i <= 17: r = r[:3] + '.' + r[4:12] + '.' + r[13:]
        out.append(r)
    return out
FRONT_NA, BACK_NA = strip_arms(w.FRONT_TOP), strip_arms(w.BACK_TOP)

_L = [(3, 14, 'C'), (3, 15, 'C'), (3, 16, 'C'), (3, 17, 's')]
_R = [(12, 14, 'C'), (12, 15, 'C'), (12, 16, 'C'), (12, 17, 's')]
_RUP = [(12, 14, 'C'), (12, 13, 'C'), (13, 12, 'C'), (13, 11, 'C'), (13, 10, 's')]
_LUP = [(3, 14, 'C'), (3, 13, 'C'), (2, 12, 'C'), (2, 11, 'C'), (2, 10, 's')]
FA = {  # Arme vorne/hinten: Pixel + Handpositionen
    'unten': (_L + _R, [(3, 17), (12, 17)]),
    'hoch_r': (_L + _RUP, [(13, 10)]),
    'hoch_b': (_LUP + _RUP, [(2, 10), (13, 10)]),
    'brust': ([(3, 14, 'C'), (4, 15, 'C'), (5, 15, 'C'), (6, 15, 's'), (12, 14, 'C'), (11, 15, 'C'), (10, 15, 'C'), (9, 15, 's')], [(7.5, 15)]),
    'vor_r': (_L + [(12, 14, 'C'), (12, 15, 'C'), (11, 16, 's')], [(11, 16)]),
}
SA = {  # Arm in der Seitenansicht (Blick nach rechts)
    'mid': ([(x, y, 'C') for y in range(13, 17) for x in (7, 8)] + [(7, 17, 's'), (8, 17, 's')], [(8, 17)]),
    'vorne': ([(7, 13, 'C'), (8, 13, 'C'), (9, 14, 'C'), (10, 14, 'C'), (11, 14, 's')], [(11, 14)]),
    'hoch': ([(7, 13, 'C'), (8, 13, 'C'), (8, 12, 'C'), (9, 11, 'C'), (10, 10, 's')], [(10, 10)]),
    'brust': ([(7, 13, 'C'), (8, 13, 'C'), (8, 14, 'C'), (9, 14, 's')], [(9, 14)]),
    'hinten_oben': ([(7, 13, 'C'), (8, 13, 'C'), (7, 12, 'C'), (6, 11, 'C'), (6, 10, 'C'), (5, 9, 's')], [(5, 9)]),
    'fwd': ([(7, 13, 'C'), (8, 13, 'C'), (8, 14, 'C'), (8, 15, 'C'), (9, 16, 's')], [(9, 16)]),
}
BLADES = {  # Klingenpixel je Pose (Reihenfolge ab Hand)
    ('side', 'hinten_oben'): [(5, 8), (4, 7), (4, 6), (3, 5), (3, 4)],
    ('side', 'vorne'): [(12, 14), (13, 14), (14, 14), (15, 14), (16, 14)],
    ('side', 'fwd'): [(10, 17), (11, 18), (12, 19), (13, 20), (14, 21)],
    ('fb', 'hoch_r'): [(13, 9), (13, 8), (13, 7), (13, 6), (13, 5)],
    ('fb', 'vor_r'): [(10, 17), (9, 18), (8, 19), (7, 20), (6, 21)],
}

def paint_pts(px, pts, pal, dy=0):
    for x, y, ch in pts:
        c = pal.get(ch)
        if c is not None and 0 <= x+1 < 18 and 0 <= y+1+dy < 26: px[x+1, y+1+dy] = c

def compose(race, outfit, view, legs='stand', arm='unten', dy=0, blink=False, near_front=True, blade=0):
    """view: 'front' | 'back' | 'side'. Gibt (Bild 18x26, Handpositionen im Bild) zurück."""
    img, px = g.new(18, 26); pal = rc.pal_for(race, outfit); o = rc.OUTFITS[outfit]; fp = rc.feature_pal(race)
    side = view == 'side'; back = view == 'back'
    if side:
        lp = pal['p']; lpal = dict(pal, F=lp if near_front else shade(lp, .72), B=shade(lp, .72) if near_front else lp)
        if race.get('tail'): s, rows = rc.TAILS[race['tail']][1]; w.paint(px, s, rows, rc.tail_pal(race), dy)
        w.paint(px, 17, w.SIDE_LEGS[legs], lpal)
        w.paint(px, 0, w._blink(w.SIDE_TOP) if blink else w.SIDE_TOP, pal, dy)
        s, rows = rc.HEM['side']; w.paint(px, s, rows, {'a': o.get('hem', pal['c'])}, dy)
    else:
        if race.get('tail') and not back: s, rows = rc.TAILS[race['tail']][0]; w.paint(px, s, rows, rc.tail_pal(race), dy)
        w.paint(px, 17, w.FB_LEGS[legs], pal)
        top = BACK_NA if back else (w._blink(FRONT_NA) if blink else FRONT_NA)
        w.paint(px, 0, top, pal, dy)
        s, rows = rc.HEM['fb']; w.paint(px, s, rows, {'a': o.get('hem', pal['c'])}, dy)
    # Arme
    pts, hands = (SA if side else FA)[arm]
    if blade:
        key = ('side' if side else 'fb', arm)
        if key in BLADES:
            bl = BLADES[key][:blade]
            paint_pts(px, [(x, y, 'W') for x, y in bl], {'W': STEEL_W}, dy)
            hx, hy = hands[0]; paint_pts(px, [(int(hx), int(hy), 'H')], {'H': HILT}, dy)
    paint_pts(px, [p for p in pts if not (blade and p[2] == 's' and (int(hands[0][0]), int(hands[0][1])) == (p[0], p[1]))], pal, dy)
    if 'pauldron' in o: s, rows = rc.PAULDRON['side' if side else 'fb']; w.paint(px, s, rows, {'P': o['pauldron']}, dy)
    # Kopf-Merkmale
    if race.get('animal'):
        if race.get('spots'): s, rows = rc.SPOTS[1 if side else 0]; w.paint(px, s, rows, fp, dy)
        if race.get('muzzle') and not back:
            s, rows = rc.MUZZLE[race['muzzle']][1 if side else 0]
            if blink and race['muzzle'] in ('frosch', 'eule'): rows = [r.replace('E', 'g').replace('e', 'w') for r in rows]
            w.paint(px, s, rows, fp, dy)
    else:
        hs, hc = race['hair']
        if side: s, rows = w.SIDE_HAIR[hs]; w.paint(px, s, rows, {'h': hc}, dy)
        else:
            s, rows = g.HAIR[hs]; w.paint(px, s, rows, {'h': hc}, dy)
            if back and hs in w.BACK_HAIR_FILL: s, rows = w.BACK_HAIR_FILL[hs]; w.paint(px, s, rows, {'h': hc}, dy)
        if race.get('dwarf') and not back:
            s, rows = rc.DWARF_BEARD[1 if side else 0]; w.paint(px, s, rows, {'f': hc}, dy)
    if race.get('ears'): s, rows = rc.EARS[race['ears']][1 if side else 0]; w.paint(px, s, rows, fp, dy)
    if race.get('tail') and back: s, rows = rc.TAILS[race['tail']][2]; w.paint(px, s, rows, rc.tail_pal(race), dy)
    img = rc.finish(img, race.get('dwarf'))
    off = 2 if race.get('dwarf') else 0
    return img, [(hx + 1, hy + 1 + dy + off) for hx, hy in hands]

# ---------------------------------------------------------------- Effekte auf der Figur
def glow(img, pts, size, cols=(MANA, MANA_CORE)):
    px = img.load()
    for (x, y) in pts:
        x, y = int(round(x)), int(round(y))
        ring = [(0, 0)]
        if size >= 1: ring += [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if size >= 2: ring += [(1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (-2, 0), (0, -2)]
        if size >= 3: ring += [(0, -3), (2, -2), (-2, -2), (3, 0), (-3, 0), (0, 2)]
        for dx, dy in ring:
            if 0 <= x+dx < img.width and 0 <= y+dy < img.height:
                d = abs(dx) + abs(dy)
                px[x+dx, y+dy] = cols[1] if d == 0 else cols[0] if d <= 1 or (x+dx+y+dy) % 2 == 0 else px[x+dx, y+dy]

def aura(img, t, strength=1.0):
    """Mana-Aura: Pixel direkt um die Silhouette, wandern nach oben."""
    src = img.copy().load(); px = img.load(); W, H = img.size
    for y in range(H):
        for x in range(W):
            if src[x, y][3]: continue
            near = any(0 <= x+dx < W and 0 <= y+dy < H and src[x+dx, y+dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if near and (y + t*2 + x) % 4 == 0 and (H - y) / H < .4 + .6*strength:
                px[x, y] = MANA if (y + t) % 3 else MANA_CORE

def tint(img, col, k):
    out = img.copy(); px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = px[x, y]
            if c[3]: px[x, y] = mix(c, col, k)[:3] + (c[3],)
    return out

def blood(img, view, level, dy=0, dwarf=False):
    px = img.load(); o = (2 if dwarf else 0) + dy
    pts = []
    if view == 'side': pts = [(11, 10 + o)] + ([(11, 11 + o), (13, 12 + o)] if level >= 2 else [])
    elif view == 'front': pts = [(7, 10 + o), (10, 10 + o)] + ([(7, 11 + o), (10, 11 + o), (8, 12 + o), (9, 12 + o)] if level >= 2 else [])
    for x, y in pts:
        if 0 <= x < img.width and 0 <= y < img.height: px[x, y] = BLOOD

def sparks(img, center, t, n=6, cols=(BRUCH_A, BRUCH_B), r=4):
    px = img.load()
    for i in range(n):
        a = i / n * 2*math.pi + t*.9
        x = int(center[0] + math.cos(a) * (r - (i + t) % 2)); y = int(center[1] + math.sin(a) * (r - (i + t) % 2))
        if 0 <= x < img.width and 0 <= y < img.height: px[x, y] = cols[i % 2]

def kneel(img):
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img.crop((0, 0, 18, 20)), (0, 3)); out.paste(img.crop((0, 23, 18, 26)), (0, 23))
    return out

def cell(img, dx=0, dy=0):
    c = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0)); c.alpha_composite(img, (4 + dx, dy)); return c

def lying(img, rot):
    r = img.rotate(rot, expand=True); b = r.getbbox(); r = r.crop(b)
    c = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0)); c.alpha_composite(r, ((CELL - r.width) // 2, CELL - r.height - 1)); return c

def flip(c): return c.transpose(Image.FLIP_LEFT_RIGHT)

# ---------------------------------------------------------------- Animationen
ARMS = {'front': {'release': 'vor_r', 'up1': 'hoch_r', 'up2': 'hoch_b', 'chest': 'brust', 'rest': 'unten'},
        'back': {'release': 'hoch_r', 'up1': 'hoch_r', 'up2': 'hoch_b', 'chest': 'brust', 'rest': 'unten'},
        'side': {'release': 'vorne', 'up1': 'hoch', 'up2': 'hoch', 'chest': 'brust', 'rest': 'mid'}}
FWD = {'front': (0, 1), 'back': (0, -1), 'side': (1, 0)}

def anim_frames(race, outfit, anim, view):
    A = ARMS[view]; fx, fy = FWD[view]; side = view == 'side'
    legs_step = 'contact' if side else 'a'
    blade_len = 3 if outfit == 'tunika' else 5
    dw = race.get('dwarf', False)
    def C_(arm, legs='stand', dy=0, blink=False, near=True, blade=0):
        return compose(race, outfit, view, legs=legs, arm=arm, dy=dy, blink=blink, near_front=near, blade=blade)
    out = []
    if anim == 'angriff':
        wind = 'hinten_oben' if side else 'hoch_r'
        hit = 'vorne' if side else 'vor_r'
        foll = 'fwd' if side else 'vor_r'
        for i, (arm, legs, step) in enumerate([(wind, 'stand', 0), (wind, 'stand', 0), (hit, legs_step, 1), (foll, legs_step, 1), (A['rest'], 'stand', 0)]):
            im, _ = C_(arm, legs, dy=1 if i == 1 else 0, blade=blade_len if i < 4 else 0)
            out.append(cell(im, fx*step, fy*step))
    elif anim == 'treffer':
        for i in range(3):
            im, _ = C_(A['rest'], blink=True)
            if i == 0: im = tint(im, (255, 255, 255, 255), .75)
            elif i == 1: im = tint(im, C('#ff4a4a'), .35)
            out.append(cell(im, -fx*(1 if i < 2 else 0), -fy*(1 if i < 2 else 0)))
    elif anim == 'tod':
        im, _ = C_(A['rest'], blink=True)
        rot = 90 if view != 'back' else -90
        out = [cell(tint(im, (255, 255, 255, 255), .6), -fx, -fy), cell(kneel(im)), cell(kneel(kneel(im)))]
        lie = lying(im, rot); out += [lie, tint(lie, C('#2b1e33'), .15)]
    elif anim == 'zauber_geschoss':
        seq = [(A['chest'], 0), (A['chest'], 1), (A['release'], 2), (A['release'], 3), (A['release'], 1), (A['rest'], 0)]
        for i, (arm, gs) in enumerate(seq):
            im, hands = C_(arm, legs_step if i in (2, 3) else 'stand')
            if gs: glow(im, hands, gs)
            out.append(cell(im, fx if i == 3 else 0, fy if i == 3 else 0))
    elif anim == 'zauber_flaeche':
        seq = [(A['chest'], 1, 0), (A['up2'], 1, 0), (A['up2'], 2, -1), (A['up2'], 3, -1), (A['chest'], 2, 1), (A['rest'], 0, 0)]
        for i, (arm, gs, d) in enumerate(seq):
            im, hands = C_(arm, dy=max(0, d))
            if gs: glow(im, hands, gs)
            if i in (2, 3): sparks(im, (hands[0][0], hands[0][1] - 3), i, n=4, cols=(MANA, MANA_CORE), r=3)
            out.append(cell(im, 0, min(0, d)))
    elif anim == 'zauber_selbst':
        seq = [(A['chest'], 1, 0), (A['chest'], 2, .4), (A['chest'], 2, .7), (A['chest'], 1, 1.0), (A['rest'], 0, .6), (A['rest'], 0, .2)]
        for i, (arm, gs, au) in enumerate(seq):
            im, hands = C_(arm, dy=1 if i == 2 else 0)
            if gs: glow(im, hands, gs)
            c = cell(im)
            if au: aura(c, i, au)
            out.append(c)
    elif anim == 'kanalisieren':
        for i in range(4):
            im, hands = C_(A['release'], legs_step)
            glow(im, hands, 2 + (i % 2))
            c = cell(im)
            hx, hy = hands[0][0] + 4, hands[0][1]
            px = c.load()
            for k in range(1, 5):
                x, y = int(hx + fx*(k+1)), int(hy + fy*(k+1))
                if 0 <= x < CELL and 0 <= y < CELL and (k + i) % 4 != 0: px[x, y] = MANA_CORE if k < 2 else MANA
            out.append(c)
    elif anim == 'bruchklang':
        for i in range(6):
            if i < 3:
                im, hands = C_(A['chest'] if i < 2 else A['up2'], dy=0)
                glow(im, hands, 1 + i, cols=(BRUCH_A if i % 2 else BRUCH_B, (255, 255, 255, 255)))
                sparks(im, hands[0], i, n=4 + 2*i, r=2 + i)
                out.append(cell(im))
            elif i == 3:
                im, hands = C_(A['up2'], blink=True)
                c = cell(tint(im, (255, 255, 255, 255), .8)); sparks(c, (hands[0][0] + 4, hands[0][1]), i, n=12, r=7)
                out.append(c)
            elif i == 4:
                im, _ = C_(A['rest'], blink=True)
                c = cell(tint(im, C('#5a4a4a'), .3), -2*fx, -2*fy)
                sparks(c, (13, 8), i, n=6, cols=(C('#6a6070'), C('#8a8090')), r=5)
                out.append(c)
            else:
                im, _ = C_(A['rest'], blink=True)
                out.append(cell(kneel(tint(im, C('#5a4a4a'), .15)), -fx, -fy))
    elif anim == 'ueberlastung':
        for i in range(6):
            if i < 3:
                im, hands = C_(A['chest'], blink=(i == 2), dy=1 if i == 2 else 0)
                glow(im, hands, [2, 1, 0][i])
                if i: blood(im, view, i, dy=1 if i == 2 else 0, dwarf=dw)
                out.append(cell(im, -fx if i == 2 else 0, 0))
            elif i == 3:
                im, _ = C_(A['rest'], blink=True); blood(im, view, 2, dwarf=dw); out.append(cell(kneel(im)))
            else:
                im, _ = C_(A['rest'], blink=True); blood(im, view, 2, dwarf=dw)
                lie = lying(im, 90 if view != 'back' else -90); out.append(lie if i == 4 else tint(lie, C('#2b1e33'), .1))
    return out

ANIMS = [('angriff', 5), ('treffer', 3), ('tod', 5), ('zauber_geschoss', 6), ('zauber_flaeche', 6), ('zauber_selbst', 6),
         ('kanalisieren', 4), ('bruchklang', 6), ('ueberlastung', 6)]

def directions(race, outfit, anim):
    down = anim_frames(race, outfit, anim, 'front')
    right = anim_frames(race, outfit, anim, 'side')
    up = anim_frames(race, outfit, anim, 'back')
    return {'unten': down, 'links': [flip(c) for c in right], 'rechts': right, 'oben': up}

def main():
    os.makedirs(OUT, exist_ok=True)
    preview = {}
    for race in rc.RACES:
        for outfit in rc.OUTFITS:
            for anim, n in ANIMS:
                d = directions(race, outfit, anim)
                sh = Image.new('RGBA', (CELL*n, CELL*4), (0, 0, 0, 0))
                for r, k in enumerate(w.ORDER):
                    for c, f in enumerate(d[k]): sh.alpha_composite(f, (c*CELL, r*CELL))
                sh.save(os.path.join(OUT, f"{race['name']}_{outfit}_{anim}.png"))
                if race['name'] in ('mensch', 'zwerg', 'elf', 'fuchs', 'drache', 'eule'):
                    preview[(race['name'], outfit, anim)] = d
    # Vorschau-GIF: Zeilen = Animationen, Spalten = Beispiel-Völker (Seitenansicht + vorne)
    S = 4
    cols = [('mensch', 'tunika'), ('zwerg', 'ruestung'), ('elf', 'tunika'), ('fuchs', 'ruestung'), ('drache', 'ruestung'), ('eule', 'tunika')]
    W_ = 160 + len(cols) * 2 * CELL * S; H_ = 30 + len(ANIMS) * (CELL * S + 4)
    frames = []
    for t in range(6):
        im = Image.new('RGB', (W_, H_), (42, 36, 69)); dr = ImageDraw.Draw(im)
        dr.text((10, 6), 'Kampf & Magie (rechts / unten)', fill=(255, 240, 200), font=g.font(16))
        for r, (anim, n) in enumerate(ANIMS):
            y = 30 + r * (CELL*S + 4)
            dr.text((10, y + CELL*S//2 - 8), anim, fill=(230, 220, 200), font=g.font(13))
            for c, (rn, of) in enumerate(cols):
                d = preview[(rn, of, anim)]
                for j, view in enumerate(('rechts', 'unten')):
                    f = d[view][min(t, n-1) if anim not in ('kanalisieren',) else t % n]
                    im.paste(f.resize((CELL*S, CELL*S), Image.NEAREST), (160 + (c*2 + j) * CELL*S, y), f.resize((CELL*S, CELL*S), Image.NEAREST))
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_kampf_magie.gif'), save_all=True, append_images=frames[1:], duration=[160, 160, 160, 160, 160, 500], loop=0)
    frames[3].save(os.path.join(g.BASE, 'preview_kampf_magie.png'))

if __name__ == '__main__':
    main()
