"""Körpertypen (Seitenansicht, Blick nach rechts). Jede Funktion zeichnet in R (Welt-Einheiten,
Boden y=0, Höhe ~1) und gibt Ankerpunkte zurück (z.B. 'mund' für Atem-/Zauberangriffe)."""
import math, random
from engine import C, shade, mix, light, WHITE, breath, particles, ELEMENT_COLS

DARKMOUTH = C('#5a1e2a')
TOOTH = C('#f4f0e0')
CLAW = C('#e8e0d0')

def g(sp, k, d=None): return sp.get(k, d)

def eye(r, x, y, sp, big=False):
    ec = g(sp, 'eye', C('#2b1e33'))
    r.dot(x, y, ec, 1 if (big or r.S >= 70) else 0)
    if r.S >= 45 and ec != C('#2b1e33'): r.dot(x, y + 1/r.S, mix(ec, WHITE, .6))

def wing(r, sx, sy, span, ang, col, kind='fledermaus', far=False):
    """Flügel ab Schulter (sx,sy); ang = Winkel der Flügelspitze (rad, 0 = nach hinten waagrecht)."""
    c = shade(col, .7) if far else col
    tipx, tipy = sx - math.cos(ang) * span * .9, sy + math.sin(ang) * span
    if kind == 'vogel':
        mid = (sx - span*.55, sy + math.sin(ang) * span * .5)
        r.poly([(sx + .04, sy), (tipx, tipy), (mid[0] - .05, mid[1] - .12), (sx - span*.35, sy - .06)], c)
        for k in range(1, 4):
            fx = sx - span*(.25 + .2*k); r.line(fx, sy + math.sin(ang)*span*(.25 + .2*k) - .02, fx + .04, sy - .04, shade(c, .8))
    elif kind == 'insekt':
        r.ell((sx + tipx)/2, (sy + tipy)/2, span*.45, span*.18, mix(c, WHITE, .5), False,
              rot=math.atan2(tipy - sy, tipx - sx))
    elif kind == 'motte':
        r.ell((sx + tipx)/2, (sy + tipy)/2, span*.5, span*.32, c, True, rot=math.atan2(tipy - sy, tipx - sx))
        r.dot((sx + tipx)/2, (sy + tipy)/2, shade(c, .5), 1)
    else:  # Fledermaus / Drache / Dämon
        ex, ey = sx - span*.75, sy - span*.08          # hinteres Ende der Flughaut
        elbow = (sx - span*.35, sy + math.sin(ang) * span * .55 + .03)
        pts = [(sx + .03, sy + .02), elbow, (tipx, tipy)]
        n = 3
        for k in range(1, n+1):
            fx = tipx + (ex - tipx) * k / n
            fy = tipy + (ey - tipy) * k / n
            pts.append((fx + .03, fy + .07)); pts.append((fx, fy))
        pts.append((sx - span*.15, sy - .06))
        r.poly(pts, c)
        r.line(sx, sy, elbow[0], elbow[1], shade(c, .6)); r.line(elbow[0], elbow[1], tipx, tipy, shade(c, .6))
        for k in range(1, n+1):
            fx = tipx + (ex - tipx) * k / n; fy = tipy + (ey - tipy) * k / n
            r.line(elbow[0], elbow[1], fx, fy, shade(c, .75))

# ================================================================ VIERBEINER
def quadruped(r, sp, p):
    L, bh, leg = g(sp, 'L', 1.0), g(sp, 'bh', .36), g(sp, 'leg', .3)
    hs, sn, neck = g(sp, 'head', .17), g(sp, 'snout', .13), g(sp, 'neck', .08)
    col, col2, acc = sp['col'], g(sp, 'col2', light(sp['col'], .35)), g(sp, 'acc', CLAW)
    bulk = g(sp, 'bulk', 1.0)
    bx = p['lunge'] * .8 + p['recoil']
    by = leg + bh/2 + p['bob']
    stride = .11 * L if p['moving'] else 0
    lw = .085 * bulk
    hips = [(-L/2 + .14, 0.0), (L/2 - .14, math.pi/2)]
    def legs(far):
        for hx, off in hips:
            ph = p['walk'] + off + (math.pi if far else 0)
            fx = bx + hx + (math.sin(ph) * stride if p['moving'] else 0)
            lift = max(0, math.cos(ph)) * .06 if p['moving'] else 0
            if p['anim'] == 'attack' and hx > 0 and not far: fx += p['lunge'] * .6
            c = shade(col, .7) if far else col
            kx = (bx + hx + fx) / 2 + (.03 if hx > 0 else -.03)
            ky = lift + leg * .5
            r.capsule(bx + hx, by - bh*.15, kx, ky, lw*1.3, c, lw)
            r.capsule(kx, ky, fx, lift + lw/2, lw, c, lw*.9)
            r.ell(fx + .02, lift + lw*.35, lw*.75, lw*.4, shade(c, .8), False)
    # Flügel hinten
    if g(sp, 'wings'):
        wing(r, bx + L*.15, by + bh*.35, g(sp, 'wingspan', .8), .6 + .5*p['flap'], g(sp, 'wingcol', col), g(sp, 'wingkind', 'vogel'), far=True)
    legs(True)
    # Schwanz
    tail = g(sp, 'tail', 'duenn')
    tx, ty = bx - L/2 + .02, by + bh*.1
    wag = math.sin(p['phase'] * (2 if p['moving'] else 1)) * .08
    if tail == 'duenn':
        r.capsule(tx, ty, tx - .2, ty + .05 + wag, .05, col, .03); r.capsule(tx - .2, ty + .05 + wag, tx - .3, ty + .16 + wag, .03, col, .02)
    elif tail == 'buschig':
        r.ell(tx - .16, ty + .02 + wag, .17, .07, col, rot=.35 + wag); r.dot(tx - .3, ty + .08 + wag, col2, 1)
    elif tail == 'kurz':
        r.ell(tx - .04, ty + .05, .06, .05, col2 if g(sp, 'puschel') else col)
    elif tail == 'echse':
        r.capsule(tx + .05, ty - .05, tx - .45, .05 + wag*.5, bh*.55, col, .03, shaded=True)
    elif tail == 'loewe':
        r.capsule(tx, ty, tx - .25, ty - .1 + wag, .035, col, .025); r.ell(tx - .27, ty - .1 + wag, .05, .05, g(sp, 'mane_col', shade(col, .7)))
    elif tail == 'stachel':
        pts = [(tx, ty)]
        for k in range(1, 6):
            a = .9 + k * .45 + p['open'] * .5
            pts.append((pts[-1][0] - .09 * math.cos(a - 1.2), pts[-1][1] + .09 * math.sin(a - .4)))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]): r.capsule(x0, y0, x1, y1, .07, shade(col, .9), .06)
        r.tri(pts[-1][0] + .04, pts[-1][1], .05, .1, acc, lean=.05)
    # Körper
    r.ell(bx, by, L/2, bh/2, col)
    if not g(sp, 'nobelly'):
        r.ell(bx + .02, by - bh*.22, L*.36, bh*.22, col2, False)
    if g(sp, 'stripes'):
        for k in range(-2, 3):
            r.capsule(bx + k*L*.14, by + bh*.4, bx + k*L*.14 - .03, by - bh*.1, .03, g(sp, 'pattern', shade(col, .55)))
    if g(sp, 'spots'):
        rng = random.Random(len(sp['name']))
        for _ in range(7): r.dot(bx + (rng.random() - .5) * L*.8, by + (rng.random() - .3) * bh*.6, g(sp, 'pattern', shade(col, .55)), 1 if r.S > 40 else 0)
    if g(sp, 'shell'):
        sc = g(sp, 'shell_col', C('#6a7a4a'))
        r.ell(bx - .02, by + bh*.32, L*.5, bh*.55, sc)
        for k in range(-2, 3): r.line(bx + k*L*.16, by + bh*.05, bx + k*L*.12, by + bh*.8, shade(sc, .7))
        if g(sp, 'island'):
            for k, (ox, h) in enumerate(((-.15, .35), (.1, .28), (-.3, .22))):
                r.capsule(bx + ox, by + bh*.75, bx + ox, by + bh*.75 + h*.5, .04, C('#5a3a2a'))
                r.ell(bx + ox, by + bh*.75 + h*.55, .1, .08, C('#4a7d4a'))
            r.poly([(bx + .2, by + bh*.8), (bx + .32, by + bh*.8), (bx + .32, by + bh*.95), (bx + .26, by + bh*1.05), (bx + .2, by + bh*.95)], C('#ded2be'))
    if g(sp, 'spikes'):
        n = 5
        for k in range(n):
            x = bx - L*.35 + k * L*.7/(n-1)
            yy = by + bh*.45 * math.sqrt(max(0, 1 - ((x - bx)/(L/2))**2))
            r.tri(x, yy - .02, .07, .1 * g(sp, 'spike_h', 1), g(sp, 'spike_col', acc), lean=-.02)
    if g(sp, 'ore'):
        rng = random.Random(5)
        for _ in range(8): r.dot(bx + (rng.random() - .5)*L*.8, by + (rng.random() - .2)*bh*.6, g(sp, 'ore'), 1 if r.S > 40 else 0)
    if g(sp, 'flames'):
        particles(r, 'feuer', p['t'], bx, by + bh*.5, L*.4, n=8, seed=4)
    legs(False)
    if g(sp, 'rider'):
        rd = sp['rider']; rs = rd.get('skin', C('#6a9a55')); rc = rd.get('col', C('#6a5a4a'))
        rx_, ry_ = bx + .02, by + bh*.45
        r.capsule(rx_, ry_, rx_ + .06, ry_ - .12, .07, shade(rc, .8))
        r.ell(rx_, ry_ + .12, .07, .12, rc)
        r.ell(rx_ + .03, ry_ + .3, .065, .065, rs)
        r.dot(rx_ + .07, ry_ + .31, C('#2b1e33'))
        if rd.get('horns'): r.capsule(rx_, ry_ + .35, rx_ - .04, ry_ + .42, .025, C('#3a2a2a'))
        if rd.get('ears'): r.tri(rx_ - .04, ry_ + .32, .04, .06, rs, lean=-.05)
        wx = rx_ + .08 + max(0, p['lunge'])
        r.capsule(rx_ + .03, ry_ + .15, wx, ry_ + .12 + p['swing']*.06, .03, rs)
        r.capsule(wx - .02, ry_ - .05, wx + .12, ry_ + .35 + p['swing']*-.1, .02, rd.get('weapon_col', C('#c8ccd8')))
    # Hals + Kopf
    hx = bx + L/2 + hs*.35 + p['open']*.04
    hy = by + bh*.3 + neck - (p['open'] * .04 if p['anim'] == 'attack' else 0) + (g(sp, 'head_low', 0))
    if g(sp, 'mane'):
        r.ell(bx + L/2 - .05, by + bh*.3, hs*1.3, bh*.65, g(sp, 'mane_col', shade(col, .7)))
    r.capsule(bx + L/2 - .1, by + bh*.15, hx - hs*.3, hy, hs*1.2, col)
    r.ell(hx, hy, hs, hs*.85, col)
    snx, sny = hx + hs*.75, hy - hs*.3
    if p['open'] > .3:
        r.ell(snx + sn*.1, sny - hs*.15, sn*.9, hs*.35, DARKMOUTH, False)
        r.capsule(hx + hs*.2, sny - hs*.35, snx + sn*.6, sny - hs*.45 - p['open']*hs*.4, hs*.35, g(sp, 'snout_col', col))
        r.dot(snx + sn*.5, sny - hs*.25, TOOTH)
    if g(sp, 'beak'):
        bc = sp['beak']
        r.poly([(hx + hs*.5, hy + hs*.25), (hx + hs*1.6, hy - hs*.2), (hx + hs*1.25, hy - hs*.55), (hx + hs*.5, hy - hs*.45)], bc)
    else:
        r.ell(snx, sny, sn, hs*.42, g(sp, 'snout_col', col))
        r.dot(snx + sn*.85, sny + hs*.15, g(sp, 'nose', C('#2b1e33')))
    if g(sp, 'tusks'):
        r.capsule(snx + sn*.4, sny - hs*.3, snx + sn*.7, sny + hs*.15, .03, TOOTH, .015)
    eye(r, hx + hs*.35, hy + hs*.25, sp)
    ears = g(sp, 'ears', 'spitz')
    if ears == 'spitz': r.tri(hx - hs*.25, hy + hs*.55, hs*.55, hs*.7, col, lean=-.03)
    elif ears == 'rund': r.ell(hx - hs*.3, hy + hs*.75, hs*.3, hs*.28, col)
    elif ears == 'lang': r.ell(hx - hs*.4, hy + hs*1.1, hs*.2, hs*.65, col, rot=.3)
    elif ears == 'haengend': r.ell(hx - hs*.45, hy - hs*.05, hs*.25, hs*.5, shade(col, .8), rot=-.2)
    horns = g(sp, 'horns')
    hc = g(sp, 'horn_col', C('#e8dcc0'))
    if horns == 'gerade':
        r.tri(hx + hs*.1, hy + hs*.6, hs*.35, hs*1.1, hc, lean=.06)
    elif horns == 'gebogen':
        r.capsule(hx - hs*.1, hy + hs*.6, hx - hs*.7, hy + hs*1.2, hs*.35, hc, hs*.25)
        r.capsule(hx - hs*.7, hy + hs*1.2, hx - hs*.9, hy + hs*.7, hs*.25, hc, hs*.1)
    elif horns == 'bulle':
        r.capsule(hx - hs*.1, hy + hs*.5, hx + hs*.6, hy + hs*.9, hs*.3, hc, hs*.15)
        r.capsule(hx + hs*.6, hy + hs*.9, hx + hs*.7, hy + hs*1.3, hs*.15, hc, hs*.08)
    elif horns == 'geweih':
        bc = g(sp, 'horn_col', C('#8a6a4a'))
        r.capsule(hx - hs*.2, hy + hs*.6, hx - hs*.5, hy + hs*2.0, .035, bc)
        r.capsule(hx - hs*.35, hy + hs*1.3, hx + hs*.2, hy + hs*1.8, .03, bc)
        r.capsule(hx - hs*.45, hy + hs*1.75, hx - hs*.9, hy + hs*2.2, .03, bc)
        if g(sp, 'leaves'):
            r.ell(hx - hs*.5, hy + hs*2.1, hs*.4, hs*.25, C('#6e9e58'))
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], bx, by, L*.45, n=4, seed=2)
    return {'mund': (snx + sn, sny - hs*.1)}

# ================================================================ ZWEIBEINER
def biped(r, sp, p):
    build = g(sp, 'build', 'normal')
    wmul = {'schmal': .8, 'normal': 1.0, 'breit': 1.35, 'riesig': 1.6}[build]
    col, col2, acc = sp['col'], g(sp, 'col2', shade(sp['col'], .8)), g(sp, 'acc', C('#c8ccd8'))
    skin = g(sp, 'skin', col)
    hs = g(sp, 'head', .13) * (.85 if build == 'riesig' else 1)
    hunch = g(sp, 'hunch', 0)
    leg_len = g(sp, 'leglen', .42)
    bx = p['lunge'] * .5 + p['recoil']
    hipy = leg_len + p['bob']
    sh_y = hipy + .32 + p['bob']*.5
    torso_rx, torso_ry = .15 * wmul, .19
    lw = .075 * wmul
    float_ = g(sp, 'float')
    if float_:
        hipy = leg_len + .05 + math.sin(p['phase']) * .02
        sh_y = hipy + .32
    def leg(far):
        if float_ or g(sp, 'robe'): return
        sw = math.sin(p['walk'] + (math.pi if far else 0)) * .32 if p['moving'] else 0
        if p['anim'] == 'attack' and not far: sw = .25 * max(0, p['lunge']) * 5
        c = shade(col2, .7) if far else col2
        if g(sp, 'skeleton'): c = shade(skin, .7) if far else skin
        x0 = bx + (-.03 if far else .03)
        kx, ky = x0 + math.sin(sw) * leg_len * .5 + .02, hipy - leg_len*.5
        fx, fy = x0 + math.sin(sw) * leg_len, max(0, -math.cos(sw) * 0 + (.04 if (p['moving'] and math.cos(p['walk'] + (math.pi if far else 0)) > 0) else 0))
        lww = lw * (.55 if g(sp, 'skeleton') else 1)
        r.capsule(x0, hipy, kx, ky, lww*1.2, c, lww)
        r.capsule(kx, ky, fx, fy + lww/2, lww, c)
        r.ell(fx + lww*.6, fy + lww*.3, lww*.9, lww*.45, g(sp, 'boot', shade(c, .7)), False)
    def arm(far):
        if g(sp, 'noarms'): return None
        sx, sy = bx + (-.02 if far else .03), sh_y - .03
        alen = .3 * (1.15 if build == 'riesig' else 1)
        if far:
            th = math.radians(10 - (math.sin(p['walk']) * 25 if p['moving'] else 0))
        else:
            s = p['swing']
            if p['anim'] == 'attack':
                th = math.radians(15 + (-s * 155 if s < 0 else s * 45))
            else:
                th = math.radians(15 + (math.sin(p['walk']) * 25 if p['moving'] else 0) + p['bob'] * 100)
            if g(sp, 'weapon') in ('speer', 'dreizack'): th = math.radians(80)
            if g(sp, 'weapon') == 'bogen': th = math.radians(88)
            if g(sp, 'weapon') == 'stab' and p['anim'] == 'attack': th = math.radians(60 + p['cast'] * 50)
        hx, hy = sx + math.sin(th) * alen, sy - math.cos(th) * alen
        c = shade(col, .75) if far else col
        if g(sp, 'bare_arms') or g(sp, 'skeleton'): c = shade(skin, .75) if far else skin
        aw = lw * (.6 if g(sp, 'skeleton') else .9)
        r.capsule(sx, sy, hx, hy, aw*1.1, c, aw)
        r.ell(hx, hy, aw*.7, aw*.7, shade(skin, .75) if far else skin)
        if g(sp, 'claws') and not far:
            for k in (-1, 0, 1): r.capsule(hx, hy, hx + math.sin(th)*.07 + k*.02, hy - math.cos(th)*.07, .015, CLAW)
        return (hx, hy, th)
    # Flügel / Umhang hinten
    if g(sp, 'wings'):
        wing(r, bx - .02, sh_y, g(sp, 'wingspan', .6), .7 + .4*p['flap'], g(sp, 'wingcol', shade(col, .7)), g(sp, 'wings'), far=True)
    if g(sp, 'cape'):
        sway = math.sin(p['phase']) * .03 - (.06 if p['moving'] else 0)
        r.poly([(bx - .08, sh_y + .02), (bx + .02, sh_y + .02), (bx - .1 + sway, .08), (bx - .3 + sway*2, .1)], g(sp, 'cape'))
    if g(sp, 'tail'):
        t_ = sp['tail']; tc = g(sp, 'tail_col', skin)
        wag = math.sin(p['phase']) * .05
        if t_ == 'echse': r.capsule(bx - .08, hipy, bx - .42, .05 + wag, .1, tc, .03, shaded=True)
        elif t_ == 'buschig': r.ell(bx - .2, hipy - .05 + wag, .15, .06, tc, rot=.5)
        else: r.capsule(bx - .08, hipy, bx - .3, hipy - .1 + wag, .04, tc, .02)
    leg(True)
    farh = arm(True)
    # Körper
    tx = bx + hunch * .3
    if g(sp, 'robe'):
        sway = math.sin(p['walk'] if p['moving'] else p['phase']) * .03
        r.poly([(tx - torso_rx, sh_y - .05), (tx + torso_rx, sh_y - .05), (tx + torso_rx*1.6 + sway, 0), (tx - torso_rx*1.8 + sway, 0)], col2)
        r.line(tx - torso_rx*1.8 + sway, 0, tx + torso_rx*1.6 + sway, 0, shade(col2, .7))
    if float_:
        wav = math.sin(p['phase']*2) * .04
        r.poly([(tx - torso_rx, hipy + .05), (tx + torso_rx, hipy + .05), (tx - .02 + wav, hipy - .32), (tx - .2 + wav, hipy - .25)],
               g(sp, 'ghost_col', col))
    if g(sp, 'skeleton'):
        r.capsule(tx, hipy, tx + hunch*.1, sh_y, .03, skin)
        for k in range(4):
            yy = hipy + .1 + k * .055
            r.capsule(tx - torso_rx*.8, yy, tx + torso_rx*.9, yy + .01, .022, skin)
        r.ell(tx, hipy, torso_rx*.8, .04, skin)
        if g(sp, 'armor'):
            r.ell(tx, hipy + .2, torso_rx*1.05, torso_ry*.85, acc)
    else:
        r.ell(tx, hipy + .16, torso_rx, torso_ry, col)
        if g(sp, 'belly'): r.ell(tx + .03, hipy + .13, torso_rx*.7, torso_ry*.6, sp['belly'], False)
        if g(sp, 'armor'):
            r.ell(tx + .01, hipy + .19, torso_rx*.95, torso_ry*.8, acc)
            r.line(tx - torso_rx*.8, hipy + .05, tx + torso_rx*.8, hipy + .05, shade(acc, .6))
        if g(sp, 'wrap'):
            for k in range(5):
                yy = hipy + k*.07
                r.line(tx - torso_rx, yy, tx + torso_rx, yy + .03, shade(col, .8))
        if g(sp, 'belt'): r.capsule(tx - torso_rx*.9, hipy + .02, tx + torso_rx*.9, hipy + .02, .03, sp['belt'])
    leg(False)
    # Kopf
    hx, hy = tx + .02 + hunch*.12, sh_y + hs*.8 - hunch*.06
    if p['anim'] == 'attack': hx += p['lunge']*.2
    head = g(sp, 'headtype', 'normal')
    draw_head(r, sp, p, head, hx, hy, hs, skin)
    near = arm(False)
    weapon = g(sp, 'weapon')
    anchor = {'mund': (hx + hs, hy - hs*.2)}
    if near and weapon:
        anchor.update(draw_weapon(r, sp, p, weapon, *near))
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], tx, hipy + .2, .3, n=5, seed=3)
    return anchor

def draw_head(r, sp, p, head, hx, hy, hs, skin):
    hc = g(sp, 'hair')
    if head in ('normal', 'goblin', 'ork', 'troll', 'oger', 'zyklop', 'vampir', 'riese', 'zwerg', 'puppe'):
        r.ell(hx, hy, hs, hs, skin)
        if head == 'goblin':
            r.tri(hx - hs*.6, hy + hs*.1, hs*.6, hs*.9, skin, lean=-hs*1.0)
            r.ell(hx + hs*.95, hy - hs*.15, hs*.3, hs*.22, skin)
        if head in ('ork', 'troll', 'oger'):
            r.ell(hx + hs*.7, hy - hs*.35, hs*.45, hs*.35, skin)
            r.capsule(hx + hs*.75, hy - hs*.5, hx + hs*.8, hy - hs*.1, .025, TOOTH, .012)
        if head == 'troll': r.ell(hx + hs*1.05, hy, hs*.35, hs*.22, skin)
        if head == 'zyklop':
            r.ell(hx + hs*.5, hy + hs*.15, hs*.35, hs*.35, WHITE, False); r.dot(hx + hs*.62, hy + hs*.15, g(sp, 'eye', C('#a83a3a')), 1)
        else:
            eye(r, hx + hs*.55, hy + hs*.15, sp)
        if head == 'vampir':
            r.dot(hx + hs*.7, hy - hs*.55, TOOTH)
        if head == 'puppe':
            r.line(hx + hs*.3, hy - hs*.4, hx + hs*.8, hy - hs*.4, C('#3a2a2a'))
            r.dot(hx + hs*.6, hy + hs*.15, C('#2b1e33'), 1)
        if hc: r.ell(hx - hs*.3, hy + hs*.45, hs*.85, hs*.6, hc)
        if g(sp, 'beard'): r.ell(hx + hs*.4, hy - hs*.65, hs*.55, hs*.5, sp['beard'])
    elif head == 'schaedel':
        bone = g(sp, 'bone', C('#e8e0d0'))
        r.ell(hx, hy + hs*.1, hs, hs*.9, bone)
        r.ell(hx + hs*.45, hy - hs*.55, hs*.45, hs*.3, bone)
        r.ell(hx + hs*.45, hy + hs*.1, hs*.28, hs*.3, C('#2b1e33'), False)
        r.dot(hx + hs*.5, hy + hs*.1, g(sp, 'eye', C('#ff5a3a')))
        r.line(hx + hs*.2, hy - hs*.5, hx + hs*.8, hy - hs*.5, shade(bone, .6))
    elif head in ('kapuze', 'mumie', 'kuerbis', 'leer', 'helm'):
        if head == 'kapuze':
            hood = g(sp, 'hood_col', g(sp, 'col2', sp['col']))
            r.ell(hx - hs*.1, hy + hs*.1, hs*1.15, hs*1.15, hood)
            r.tri(hx - hs*.6, hy + hs*.6, hs*.8, hs*.9, hood, lean=-hs*.6)
            r.ell(hx + hs*.35, hy, hs*.55, hs*.65, C('#1a1420'), False)
            ec = g(sp, 'eye', C('#ff5a3a'))
            r.dot(hx + hs*.4, hy + hs*.1, ec); r.dot(hx + hs*.65, hy + hs*.1, ec)
        elif head == 'mumie':
            r.ell(hx, hy, hs, hs, C('#d8ccae'))
            for k in range(3): r.line(hx - hs, hy - hs*.5 + k*hs*.5, hx + hs, hy - hs*.3 + k*hs*.5, C('#a89a7a'))
            r.dot(hx + hs*.55, hy + hs*.1, g(sp, 'eye', C('#ffd27a')))
        elif head == 'kuerbis':
            r.ell(hx, hy, hs*1.2, hs, C('#e07a34'))
            r.line(hx, hy - hs, hx, hy + hs, shade(C('#e07a34'), .7))
            r.capsule(hx, hy + hs, hx - .02, hy + hs*1.3, .03, C('#4a7d4a'))
            r.tri(hx + hs*.5, hy + hs*.05, hs*.3, hs*.3, C('#ffd27a'))
            r.poly([(hx + hs*.2, hy - hs*.45), (hx + hs*1.0, hy - hs*.45), (hx + hs*.6, hy - hs*.2)], C('#ffd27a'))
        elif head in ('leer', 'helm'):
            hm = g(sp, 'acc', C('#a8acbc'))
            r.ell(hx, hy + hs*.05, hs, hs*1.05, hm)
            r.capsule(hx + hs*.1, hy + hs*.05, hx + hs*.95, hy + hs*.05, hs*.25, C('#1a1420'))
            if head == 'leer':
                r.dot(hx + hs*.6, hy + hs*.05, g(sp, 'eye', C('#8ad0ff')))
            if g(sp, 'plume'): r.ell(hx - hs*.3, hy + hs*1.1, hs*.6, hs*.25, sp['plume'], rot=.5)
    elif head in ('bulle', 'wolf', 'hyaene', 'echse', 'baer', 'affe', 'ratte', 'ziege', 'vogel'):
        r.ell(hx, hy, hs, hs*.9, skin)
        snout = {'bulle': .7, 'wolf': .8, 'hyaene': .75, 'echse': .9, 'baer': .55, 'affe': .4, 'ratte': .8, 'ziege': .6, 'vogel': .6}[head]
        sc = g(sp, 'snout_col', skin)
        if head == 'vogel':
            r.tri(hx + hs*.9, hy - hs*.1, hs*.5, hs*.9, g(sp, 'beak', C('#e0a040')), lean=0)
            r.poly([(hx + hs*.6, hy + hs*.1), (hx + hs*1.6, hy - hs*.15), (hx + hs*.6, hy - hs*.35)], g(sp, 'beak', C('#e0a040')))
        else:
            r.ell(hx + hs*.75, hy - hs*.3, hs*snout, hs*.45, sc)
            r.dot(hx + hs*(.7 + snout*.9), hy - hs*.15, C('#2b1e33'))
            if p['open'] > .3:
                r.capsule(hx + hs*.4, hy - hs*.65, hx + hs*(.5 + snout), hy - hs*.75 - p['open']*hs*.3, hs*.3, sc)
        eye(r, hx + hs*.35, hy + hs*.25, sp)
        if head in ('wolf', 'hyaene', 'ratte'):
            r.tri(hx - hs*.3, hy + hs*.6, hs*.5, hs*(.8 if head == 'wolf' else .5), skin, lean=-.02)
        if head in ('bulle', 'ziege'):
            hc2 = g(sp, 'horn_col', C('#e8dcc0'))
            r.capsule(hx - hs*.1, hy + hs*.6, hx + hs*.5, hy + hs*1.2, hs*.3, hc2, hs*.12)
        if head == 'echse': r.tri(hx - hs*.2, hy + hs*.75, hs*.5, hs*.4, g(sp, 'acc', shade(skin, .7)))
        if head == 'baer': r.ell(hx - hs*.3, hy + hs*.75, hs*.3, hs*.28, skin)
    elif head == 'baum':
        r.ell(hx, hy + hs*.6, hs*2.0, hs*1.5, g(sp, 'leaf', C('#4a7d4a')))
        r.ell(hx - hs*.6, hy + hs*1.2, hs*1.1, hs*.9, light(g(sp, 'leaf', C('#4a7d4a')), .15))
        r.ell(hx + hs*.4, hy - hs*.2, hs*.25, hs*.2, C('#2b1e33'), False); r.dot(hx + hs*.45, hy - hs*.2, g(sp, 'eye', C('#ffd27a')))
    elif head == 'pilz':
        r.ell(hx, hy - hs*.2, hs*.7, hs*.8, C('#e8dcc0'))
        cap = g(sp, 'cap', C('#c84a4a'))
        r.ell(hx, hy + hs*.5, hs*1.6, hs*.9, cap)
        for k in range(3): r.dot(hx - hs*.8 + k*hs*.8, hy + hs*.8, WHITE, 1 if r.S > 40 else 0)
        eye(r, hx + hs*.35, hy - hs*.2, sp)
    elif head == 'stroh':
        r.ell(hx, hy, hs, hs, C('#e8d8a0'))
        r.ell(hx, hy + hs*.6, hs*1.6, hs*.3, C('#c8a050'))
        r.ell(hx, hy + hs*.9, hs*.8, hs*.4, C('#c8a050'))
        r.dot(hx + hs*.5, hy + hs*.1, C('#2b1e33'), 1 if r.S > 40 else 0)
    if g(sp, 'horns'):
        hc2 = g(sp, 'horn_col', C('#3a2a2a'))
        r.capsule(hx - hs*.1, hy + hs*.7, hx - hs*.5, hy + hs*1.4, hs*.3, hc2, hs*.08)
    if g(sp, 'crown'):
        cc = g(sp, 'crown_col', C('#e0b048'))
        r.poly([(hx - hs*.7, hy + hs*.75), (hx + hs*.7, hy + hs*.75), (hx + hs*.7, hy + hs*1.2), (hx + hs*.35, hy + hs*.95),
                (hx, hy + hs*1.3), (hx - hs*.35, hy + hs*.95), (hx - hs*.7, hy + hs*1.2)], cc)

def draw_weapon(r, sp, p, weapon, hx, hy, th):
    wc = g(sp, 'weapon_col', C('#c8ccd8'))
    dx, dy = math.sin(th), -math.cos(th)
    out = {}
    if weapon in ('schwert', 'messer', 'sense'):
        ln = {'schwert': .32, 'messer': .14, 'sense': .45}[weapon]
        r.capsule(hx, hy, hx + dx*ln, hy + dy*ln, .035 if weapon != 'messer' else .025, wc, .015)
        r.capsule(hx - dy*.05, hy + dx*.05, hx + dy*.05, hy - dx*.05, .02, C('#8a6a4a'))
        if weapon == 'sense':
            ex, ey = hx + dx*ln, hy + dy*ln
            r.capsule(ex, ey, ex - dy*.2 - dx*.05, ey + dx*.2 - dy*.05, .04, C('#c8ccd8'), .01)
    elif weapon in ('axt', 'keule', 'hammer', 'baum'):
        ln = {'axt': .34, 'keule': .32, 'hammer': .36, 'baum': .55}[weapon]
        ex, ey = hx + dx*ln, hy + dy*ln
        if weapon == 'keule': r.capsule(hx, hy, ex, ey, .04, C('#7a5236'), .1)
        elif weapon == 'baum':
            r.capsule(hx, hy, ex, ey, .06, C('#5a3a2a'), .1); r.ell(ex, ey, .14, .12, C('#4a7d4a'))
        else:
            r.capsule(hx, hy, ex, ey, .03, C('#7a5236'))
            if weapon == 'axt': r.ell(ex - dx*.04 + dy*.06, ey - dy*.04 - dx*.06, .08, .06, wc, rot=th)
            else: r.ell(ex, ey, .08, .06, C('#7a7e8e'), rot=th)
    elif weapon in ('speer', 'dreizack'):
        x0 = hx - .25 + p['lunge']*1.2; x1 = hx + .35 + p['lunge']*1.2
        r.line(x0, hy, x1, hy, C('#7a5236')); r.line(x0, hy + 1/r.S, x1, hy + 1/r.S, C('#7a5236'))
        r.tri(x1 + .03, hy - .03, .06, .08, wc, lean=0) if False else r.poly([(x1, hy + .03), (x1 + .08, hy + .005), (x1, hy - .03)], wc)
        if weapon == 'dreizack':
            r.line(x1 - .02, hy + .05, x1 + .05, hy + .05, wc); r.line(x1 - .02, hy - .04, x1 + .05, hy - .04, wc)
    elif weapon == 'stab':
        r.capsule(hx - dx*.1, hy - dy*.1 - .25, hx + dx*.2, hy + dy*.2 + .2, .025, C('#6a4a32'))
        oc = ELEMENT_COLS.get(g(sp, 'element', 'arkan'), ELEMENT_COLS['arkan'])
        ox, oy = hx + dx*.2, hy + dy*.2 + .23
        r.ell(ox, oy, .045, .045, oc[1]); r.dot(ox - .01, oy + .01, oc[0])
        out['mund'] = (ox + .05, oy)
        if p['anim'] == 'attack' and p['cast'] > .5:
            k = (p['t'] - 2) / 3
            r.ell(ox + .1 + k*.5, oy - k*.1, .06, .06, oc[1]); r.dot(ox + .1 + k*.5, oy - k*.1, oc[0], 1)
    elif weapon == 'bogen':
        bx_, by_ = hx + .02, hy
        for k in range(-6, 7):
            a = k / 6
            r.dot(bx_ + .06 * (1 - a*a), by_ + a*.18, C('#7a5236'))
        r.line(bx_, by_ - .18, bx_, by_ + .18, C('#e8e0d0'))
        if p['anim'] == 'attack' and p['t'] >= 3:
            ax = bx_ + (p['t'] - 2) * .22
            r.line(ax, by_, ax + .16, by_, C('#c8b898')); r.dot(ax + .17, by_, wc)
    elif weapon == 'fackel':
        r.capsule(hx, hy, hx + dx*.18, hy + dy*.18 + .1, .03, C('#7a5236'))
        particles(r, 'feuer', p['t'], hx + dx*.18, hy + dy*.18 + .14, .04, n=5)
    return out

# ================================================================ FLIEGER
def flyer(r, sp, p):
    kind = g(sp, 'kind', 'vogel')
    col, col2 = sp['col'], g(sp, 'col2', light(sp['col'], .3))
    span = g(sp, 'span', .55)
    bl = g(sp, 'blen', .3)
    y = g(sp, 'alt', .45) + p['bob'] * 2 + math.sin(p['phase']) * .03
    x = p['lunge'] * 1.4 + p['recoil']
    if p['anim'] == 'attack': y -= max(0, p['lunge']) * 1.2
    r.shadow(x, bl * 1.6)
    flap = p['flap'] if p['anim'] != 'idle' else math.sin(p['phase'] * 2)
    ang = .5 + .7 * flap
    wk = {'vogel': 'vogel', 'fledermaus': 'fledermaus', 'insekt': 'insekt', 'motte': 'motte'}[kind]
    wing(r, x + .02, y + .05, span, ang + .25, g(sp, 'wingcol', col), wk, far=True)
    if kind == 'insekt':
        wing(r, x - .03, y + .06, span, ang - .2, g(sp, 'wingcol', col), wk)
    if kind == 'vogel':
        r.tri(x - bl*.85, y, .12, .12, shade(col, .8), lean=-.12) if False else r.poly([(x - bl*.7, y + .03), (x - bl*1.3, y + .08), (x - bl*1.25, y - .05)], shade(col, .85))
        r.ell(x, y, bl, bl*.55, col)
        r.ell(x + .03, y - bl*.2, bl*.6, bl*.3, col2, False)
        hx, hy = x + bl*.85, y + bl*.35
        r.ell(hx, hy, bl*.38, bl*.35, g(sp, 'head_col', col))
        bc = g(sp, 'beak', C('#e0a040'))
        r.poly([(hx + bl*.25, hy + bl*.1), (hx + bl*.75 + p['open']*.02, hy - bl*.05), (hx + bl*.25, hy - bl*.15)], bc)
        if g(sp, 'crest'): r.tri(hx - bl*.1, hy + bl*.3, bl*.25, bl*.35, g(sp, 'crest'), lean=-bl*.2)
        eye(r, hx + bl*.12, hy + bl*.1, sp)
        tal = .08 if p['anim'] != 'attack' else .02
        r.line(x + bl*.2, y - bl*.5, x + bl*.3 + (.08 if p['anim'] == 'attack' else 0), y - bl*.5 - tal, C('#e0a040'))
        mouth = (hx + bl*.8, hy - bl*.05)
    elif kind == 'fledermaus':
        r.ell(x, y, bl*.6, bl*.5, col)
        hx, hy = x + bl*.45, y + bl*.25
        r.ell(hx, hy, bl*.35, bl*.32, col)
        r.tri(hx - bl*.1, hy + bl*.2, bl*.2, bl*.35, col); r.tri(hx + bl*.15, hy + bl*.2, bl*.2, bl*.35, col)
        eye(r, hx + bl*.2, hy + bl*.05, sp)
        if p['open'] > .3: r.dot(hx + bl*.3, hy - bl*.2, TOOTH)
        mouth = (hx + bl*.35, hy - bl*.1)
    else:  # insekt / motte
        stripes = g(sp, 'stripes')
        r.ell(x - bl*.45, y - bl*.05, bl*.55, bl*.32, col)
        if stripes:
            for k in range(3): r.line(x - bl*.75 + k*bl*.22, y + bl*.25, x - bl*.7 + k*bl*.22, y - bl*.3, stripes)
        if g(sp, 'stinger'): r.tri(x - bl*1.0, y - bl*.05, bl*.15, bl*.25, C('#2b1e33'), lean=-bl*.2)
        r.ell(x + bl*.1, y, bl*.25, bl*.22, col2)
        hx, hy = x + bl*.38, y + bl*.02
        r.ell(hx, hy, bl*.2, bl*.2, shade(col, .8))
        eye(r, hx + bl*.08, hy + bl*.05, sp, big=True)
        r.line(hx, hy + bl*.15, hx + bl*.25, hy + bl*.45, shade(col, .6))
        for k in (-.15, .1):
            r.line(x + k*bl, y - bl*.15, x + k*bl + .03, y - bl*.45, shade(col, .6))
        mouth = (hx + bl*.2, hy)
    if kind not in ('insekt',):
        wing(r, x - .01, y + .05, span, ang, g(sp, 'wingcol', col), wk)
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], x, y, bl*1.2, n=5, seed=5)
    return {'mund': mouth}

TOOTH = C('#f4f0e0')

# ================================================================ INSEKTEN / SPINNEN / KRABBEN
def insect(r, sp, p):
    kind = g(sp, 'kind', 'kaefer')
    col, col2, acc = sp['col'], g(sp, 'col2', shade(sp['col'], .8)), g(sp, 'acc', shade(sp['col'], .6))
    x = p['lunge'] * .8 + p['recoil']
    y = .22 + p['bob']
    nlegs = 4 if kind in ('spinne', 'skorpion') else 3
    leg_h = .38 if kind == 'spinne' else .22
    def legs(far):
        for k in range(nlegs):
            base = x - .2 + k * (.4 / max(1, nlegs-1))
            ph = p['walk'] + k * math.pi/2 + (math.pi if far else 0)
            sw = math.sin(ph) * .06 if p['moving'] else 0
            lift = max(0, math.cos(ph)) * .04 if p['moving'] else 0
            c = shade(acc, .7) if far else acc
            dirx = -1 if k < nlegs/2 else 1
            spread = 1.7 if kind == 'spinne' else 1.0
            kx, ky = base + dirx * .12 * spread + sw*.5, y + leg_h*.6
            fx = base + dirx * .22 * spread + sw + (.04 if far else 0)
            r.line(base, y, kx, ky, c); r.line(kx, ky, fx, lift, c)
            if r.S > 50:
                r.line(base, y + 1/r.S, kx, ky + 1/r.S, c); r.line(kx + 1/r.S, ky, fx + 1/r.S, lift, c)
    legs(True)
    mouth = (x + .45, y)
    if kind == 'skorpion':
        cur = .8 + p['open'] * .9
        pts = [(x - .3, y + .02)]
        for k in range(5):
            a = math.pi/2 + k * cur/2.6
            pts.append((pts[-1][0] - .08 * math.cos(a) - .03, pts[-1][1] + .09 * math.sin(a) + .02))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]): r.capsule(x0, y0, x1, y1, .08, col, .065)
        sx, sy = pts[-1]
        r.poly([(sx, sy + .02), (sx + .09, sy - .05 - p['open']*.05), (sx + .01, sy - .04)], acc)
    if kind in ('spinne',):
        r.ell(x - .28, y + .1, .26, .2, col)
        if g(sp, 'pattern'): r.ell(x - .3, y + .17, .08, .06, sp['pattern'], False)
        r.ell(x + .02, y + .04, .14, .11, col2)
        r.ell(x + .17, y + .03, .08, .07, col2)
        for k in range(3): r.dot(x + .2 + (k % 2)*.02, y + .06 - k*.015, g(sp, 'eye', C('#c83a3a')))
        if p['open'] > .3: r.capsule(x + .22, y - .02, x + .27, y - .08, .025, acc)
        mouth = (x + .26, y)
    elif kind in ('kaefer', 'skorpion', 'assel', 'zecke', 'ameise', 'hirschkaefer', 'kakerlake'):
        ab_rx = {'zecke': .26, 'ameise': .16, 'assel': .32, 'kakerlake': .3}.get(kind, .26)
        if kind == 'ameise':
            r.ell(x - .22, y + .05, .16, .12, col); r.ell(x, y + .05, .09, .07, col2); r.ell(x + .15, y + .07, .09, .08, col)
        elif kind == 'assel':
            r.ell(x - .04, y + .06, .32, .16, col)
            for k in range(-3, 4): r.line(x + k*.07, y + .2, x + k*.075, y - .06, shade(col, .65))
        else:
            r.ell(x - .08, y + .07, ab_rx, .16 if kind != 'zecke' else .2, col)
            if kind in ('kaefer', 'hirschkaefer', 'kakerlake'): r.line(x - .08 - ab_rx*.9, y + .12, x - .08 + ab_rx*.9, y + .12, shade(col, .6))
            if g(sp, 'shine'): r.ell(x - .12, y + .15, ab_rx*.4, .04, light(col, .45), False)
            r.ell(x + .19, y + .05, .09, .08, col2)
        hx = x + (.26 if kind != 'ameise' else .22)
        eye(r, hx, y + .08, sp)
        if kind in ('hirschkaefer',):
            o = p['open'] * .05
            r.capsule(hx + .02, y + .08, hx + .2, y + .14 + o, .035, acc, .02); r.capsule(hx + .02, y + .02, hx + .2, y - .02 - o, .035, acc, .02)
        if kind == 'skorpion':
            for s in (1, -1):
                ex = hx + .14 + p['lunge']*.5
                r.capsule(hx, y + .03, ex, y + .1 + s*.02, .05, col)
                r.ell(ex + .05, y + .1 + s*.02, .07, .05, col)
                r.tri(ex + .1, y + .12, .04, .05 + p['open']*.03, acc, lean=.03)
        r.line(hx, y + .12, hx + .12, y + .25, acc)
        mouth = (hx + .1, y + .06)
    elif kind == 'krabbe':
        r.ell(x, y + .1, .32, .17, col)
        for s in (-.1, .1):
            r.capsule(x + s + .05, y + .2, x + s + .07, y + .3, .025, acc); r.dot(x + s + .07, y + .31, C('#2b1e33'), 1 if r.S > 40 else 0)
        up = .12 + p['open']*.1 + math.sin(p['phase'])*.02
        for side in (0, 1):
            cx_ = x + .3 + side*.05 + p['lunge']*.5
            r.capsule(x + .22, y + .1, cx_, y + up + .1, .06, col)
            r.ell(cx_ + .06, y + up + .14, .1, .07, col2)
            r.tri(cx_ + .12, y + up + .17, .05, .08 + p['open']*.05, col2, lean=.04)
        mouth = (x + .45, y + .1)
    elif kind == 'mantis':
        r.ell(x - .25, y + .08, .22, .08, col, rot=.2)
        r.capsule(x - .05, y + .1, x + .08, y + .42, .07, col2)
        hx, hy = x + .12, y + .5
        r.poly([(hx - .04, hy + .05), (hx + .1, hy), (hx - .02, hy - .06)], col2)
        eye(r, hx, hy + .01, sp)
        reach = .1 + p['lunge'] * 1.4
        r.capsule(x + .06, y + .35, x + .1 + reach, y + .4, .045, acc)
        r.capsule(x + .1 + reach, y + .4, x + .14 + reach, y + .22, .035, acc)
        mouth = (hx + .1, hy)
    legs(False)
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], x, y + .1, .3, n=4)
    return {'mund': mouth}

# ================================================================ SCHLANGEN / WÜRMER
def serpent(r, sp, p):
    kind = g(sp, 'kind', 'schlange')
    col, col2 = sp['col'], g(sp, 'col2', light(sp['col'], .3))
    L, th = g(sp, 'L', 1.3), g(sp, 'th', .14)
    rear = g(sp, 'rear', .25)
    x0 = p['lunge'] * .8 + p['recoil']
    if kind == 'sandwurm':
        return sandworm(r, sp, p)
    N = 26
    amp = (.06 if p['moving'] else .03) * (1 if kind != 'made' else .5)
    phase = p['walk'] if p['moving'] else p['phase'] * .5
    pts = []
    for i in range(N + 1):
        s = i / N
        x = x0 - L/2 + s * L * (.85 if s > .8 else 1)
        y = th/2 + amp * math.sin(2*math.pi*s*1.5 - phase) * (1 - s*.3)
        if s > .78: y += (s - .78)/.22 * rear + (p['open'] * .05 if p['anim'] == 'attack' else 0)
        if s > .78 and p['anim'] == 'attack': x += (s - .78)/.22 * p['lunge'] * 1.2
        w = th * (.35 + .65 * min(1, s*2.2)) if kind not in ('wurm', 'made', 'egel') else th * (.7 + .3*math.sin(math.pi*s))
        pts.append((x, y, w))
    if g(sp, 'naga'):
        pts = pts[:20]
    for i, (x, y, w) in enumerate(pts):
        c = col
        if g(sp, 'stripes') and (i // 2) % 2: c = sp['stripes']
        if kind in ('wurm', 'made') and i % 3 == 0: c = shade(col, .82)
        r.ell(x, y, w/2 + .01, w/2, c)
        if g(sp, 'spikes') and i % 3 == 0 and 3 < i < N-4: r.tri(x, y + w/2 - .01, .05, .07, g(sp, 'acc', shade(col, .6)))
        if g(sp, 'fin') and 4 < i < N - 6: r.dot(x, y + w/2 + .01, g(sp, 'fin'))
    hx, hy, hw = pts[-1]
    mouth = (hx + .1, hy)
    if g(sp, 'naga'):
        tx, ty, tw = pts[-1]
        bp = dict(sp); bp['float'] = False
        r.ell(tx + .02, ty + .18, .1, .17, g(sp, 'skin', col))
        r.ell(tx + .05, ty + .42, .09, .09, g(sp, 'skin', col))
        if g(sp, 'hair'): r.ell(tx - .01, ty + .47, .1, .08, sp['hair']); r.capsule(tx - .04, ty + .45, tx - .1, ty + .25, .06, sp['hair'])
        eye(r, tx + .1, ty + .44, sp)
        hx2 = tx + .12 + max(0, p['lunge'])
        r.capsule(tx + .04, ty + .3, hx2 + .08, ty + .28 + p['cast']*.1, .05, g(sp, 'skin', col))
        return {'mund': (tx + .15, ty + .42)}
    if kind in ('schlange', 'wyrm', 'aal', 'hydrakopf'):
        r.ell(hx + .06, hy + .01, th*.75, th*.5, col)
        if p['open'] > .3:
            r.ell(hx + .14, hy - .03, th*.4, th*.18, DARKMOUTH, False)
            r.capsule(hx + .04, hy - th*.35, hx + .18, hy - th*.55, th*.3, col)
            r.dot(hx + .16, hy - .02, TOOTH)
        eye(r, hx + .08, hy + th*.2, sp)
        if kind == 'schlange' and p['anim'] == 'idle' and p['t'] in (1, 2):
            r.line(hx + .14, hy - .01, hx + .22, hy - .01, C('#c83a3a'))
        if kind == 'wyrm':
            r.capsule(hx, hy + th*.35, hx - .12, hy + th*.9, .04, g(sp, 'horn_col', C('#e8dcc0')), .015)
        if kind == 'aal' and g(sp, 'element'):
            particles(r, sp['element'], p['t'], hx - L*.3, hy, .2, n=5)
        mouth = (hx + .16, hy)
    elif kind in ('wurm', 'made', 'egel'):
        o = .4 + p['open'] * .6
        r.ell(hx + .03, hy, hw*.25, hw*.4*o, DARKMOUTH, False)
        if kind == 'wurm' and r.S > 30:
            for k in range(-2, 3): r.dot(hx + .05, hy + k*hw*.15*o, TOOTH)
        if kind == 'made': r.dot(hx, hy + hw*.15, C('#2b1e33'))
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], x0, th, L*.4, n=5, seed=8)
    return {'mund': mouth}

def sandworm(r, sp, p):
    col = sp['col']; th = g(sp, 'th', .3)
    rise = .75 + (.1 if p['moving'] else 0) * math.sin(p['walk']) + p['open'] * .05
    lean = .15 + p['lunge'] * 1.5 + math.sin(p['phase']) * .03
    r.ell(0, .02, th*1.3, .06, g(sp, 'dirt', C('#c8a070')))
    N = 16
    top = None
    for i in range(N + 1):
        s = i / N
        x = lean * s*s + p['recoil']
        y = s * rise
        w = th * (1 - s*.15)
        r.ell(x, y, w/2, w*.32, shade(col, .85) if i % 2 else col)
        top = (x, y, w)
    x, y, w = top
    o = .35 + p['open'] * .65
    r.ell(x + .02, y + .02, w*.48, w*.3*o + .02, DARKMOUTH, False)
    for k in range(8):
        a = k / 8 * 2*math.pi
        r.dot(x + .02 + math.cos(a)*w*.42, y + .02 + math.sin(a)*w*.25*o, TOOTH, 1 if r.S > 60 else 0)
    r.ell(0, .02, th*1.2, .035, shade(g(sp, 'dirt', C('#c8a070')), .8), False)
    return {'mund': (x + w*.4, y)}

# ================================================================ FISCHE / WALE / QUALLEN
def fish(r, sp, p):
    kind = g(sp, 'kind', 'fisch')
    col, col2 = sp['col'], g(sp, 'col2', light(sp['col'], .35))
    L = g(sp, 'L', .9); h = g(sp, 'h', .32)
    x = p['lunge'] * 1.0 + p['recoil']
    y = g(sp, 'alt', .4) + math.sin(p['phase']) * .03 + p['bob']
    if kind == 'qualle':
        r.ell(x, y + .12, .24, .18, col, lo=shade(col, .8))
        r.ell(x, y + .08, .2, .08, col2, False)
        for k in range(6):
            tx = x - .18 + k * .07
            for j in range(6):
                r.dot(tx + math.sin(p['phase'] + j*.8 + k) * .03, y - j * .06, mix(col, WHITE, .3))
        particles(r, g(sp, 'element', 'blitz'), p['t'], x, y, .25, n=3)
        return {'mund': (x + .25, y)}
    wig = math.sin(p['phase'] * (2 if p['moving'] else 1)) * .06
    r.poly([(x - L*.45, y), (x - L*.72, y + h*.6 + wig), (x - L*.66, y + wig*.3), (x - L*.72, y - h*.55 + wig)], g(sp, 'fin', shade(col, .8)))
    r.ell(x, y, L/2, h/2, col)
    r.ell(x + .03, y - h*.18, L*.4, h*.25, col2, False)
    fin = g(sp, 'fin', shade(col, .8))
    if kind == 'hai':
        r.poly([(x - L*.1, y + h*.4), (x + L*.08, y + h*.4), (x - L*.12, y + h*1.15)], fin)
    else:
        r.poly([(x - L*.2, y + h*.4), (x + L*.1, y + h*.45), (x - L*.15, y + h*.75)], fin)
    r.poly([(x + L*.05, y - h*.2), (x - L*.12, y - h*.25), (x - L*.05, y - h*.6 - wig*.5)], fin)
    hx = x + L*.38
    if p['open'] > .3 or kind in ('hecht', 'hai'):
        o = p['open']
        r.poly([(hx + L*.12, y - h*.05), (hx - L*.06, y - h*.12 - o*h*.15), (hx + L*.12, y - h*.25 - o*h*.2)], DARKMOUTH)
        r.dot(hx + L*.05, y - h*.12, TOOTH)
    eye(r, hx - L*.05, y + h*.12, sp)
    if kind == 'wal':
        for k in range(4): r.line(x + L*.1, y - h*.3 - k*.02, x + L*.35, y - h*.25 - k*.02, shade(col2, .85))
        if g(sp, 'sky'):
            for k in range(3): r.ell(x - L*.3 + k*L*.25, y + h*.7, .08, .05, WHITE, False)
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], x, y, L*.4, n=5)
    return {'mund': (hx + L*.15, y - h*.1)}

# ================================================================ KRAKEN
def octopus(r, sp, p):
    col, col2 = sp['col'], g(sp, 'col2', light(sp['col'], .35))
    x = p['recoil'] + p['lunge'] * .3
    by = .38 + p['bob']
    for k in range(7):
        base = x - .22 + k * .07
        far = k % 2 == 0
        c = shade(col, .72) if far else col
        reach = .0
        if p['anim'] == 'attack' and k == 6: reach = p['lunge'] * 3.5 + .15 * p['open']
        pts = [(base, by)]
        for j in range(1, 7):
            a = -math.pi/2 + (k - 3) * .25 + math.sin(p['phase'] + j*.7 + k) * .35
            if reach: a = -.1 + j*.05
            seg = .075 + (reach * .12 if reach else 0)
            pts.append((pts[-1][0] + math.cos(a)*seg, max(.01, pts[-1][1] + math.sin(a)*seg)))
        for j, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
            w = .075 * (1 - j/7) + .015
            r.capsule(x0, y0, x1, y1, w, c)
            if j % 2 and not far and r.S > 40: r.dot(x1, y1 - w*.3, col2)
    r.ell(x, by + .25, .24, .3, col, rot=-.25)
    r.ell(x + .12, by + .12, .06, .06, WHITE, False); eye(r, x + .14, by + .12, sp, big=True)
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], x, by, .3, n=4)
    return {'mund': (x + .25, by)}

# ================================================================ SCHLEIME
def slime(r, sp, p):
    col = sp['col']
    kind = g(sp, 'kind', 'schleim')
    w, h = g(sp, 'w', .9), g(sp, 'h', .62)
    if kind == 'pfuetze': h = .28
    jump, sx, sy = 0.0, 1.0, 1.0
    if p['moving']:
        s = math.sin(p['walk'])
        jump = max(0, s) * .25
        sx, sy = (1.18, .82) if s < -.3 else (.9, 1.12) if s > .3 else (1, 1)
    elif p['anim'] == 'idle':
        sx, sy = 1 + math.sin(p['phase'])*.04, 1 - math.sin(p['phase'])*.04
    elif p['anim'] == 'attack':
        sx, sy = 1 + max(0, p['lunge'])*2.5, 1 - max(0, p['lunge'])*1.2
    x = p['lunge'] * .5 + p['recoil']
    if kind == 'blase': jump = .25 + math.sin(p['phase'])*.03
    if jump: r.shadow(x, w*.8)
    rx, ry = w/2*sx, h/2*sy
    cy = ry + jump
    lo = shade(col, .7)
    r.ell(x, cy, rx, ry, col, lo=lo)
    if kind != 'blase': r.poly([(x - rx, jump + .02), (x + rx, jump + .02), (x + rx*.9, jump), (x - rx*.9, jump)], shade(col, .8))
    rng = random.Random(len(sp['name']))
    if g(sp, 'inside'):
        for _ in range(3): r.dot(x + (rng.random()-.5)*rx, cy + (rng.random()-.6)*ry, sp['inside'], 1 if r.S > 40 else 0)
    r.ell(x - rx*.35, cy + ry*.45, rx*.2, ry*.13, mix(col, WHITE, .65), False)
    ex = x + rx*.35
    ec = g(sp, 'eye', C('#2b1e33'))
    r.dot(ex - rx*.18, cy + ry*.1, ec, 1 if r.S > 30 else 0); r.dot(ex + rx*.12, cy + ry*.1, ec, 1 if r.S > 30 else 0)
    if p['open'] > .3: r.ell(ex, cy - ry*.25, rx*.15, ry*.12*p['open'] + .01, DARKMOUTH, False)
    if g(sp, 'drip'):
        for k in range(3): r.capsule(x - rx*.5 + k*rx*.5, cy - ry*.5, x - rx*.5 + k*rx*.5, jump + .02 - (k % 2)*.03, .03, col)
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], x, cy, rx, n=5)
    return {'mund': (ex + rx*.3, cy)}

# ================================================================ GEISTER / ELEMENTARE
def spirit(r, sp, p):
    kind = g(sp, 'kind', 'geist')
    col = g(sp, 'col', C('#c8c4e0')); col2 = g(sp, 'col2', light(col, .4))
    x = p['lunge'] * 1.2 + p['recoil']
    y = g(sp, 'alt', .42) + math.sin(p['phase']) * .04 + p['bob']
    sz = g(sp, 'sz', 1.0)
    r.shadow(x, .35 * sz, 50)
    el = g(sp, 'element')
    if kind == 'irrlicht':
        for k in range(3):
            tx = x - .08*k - .05; ty = y - .04*k + math.sin(p['phase'] + k)*.03
            r.ell(tx, ty, .06*(1 - k*.25)*sz, .06*(1 - k*.25)*sz, mix(col, WHITE, .2*k), False)
        r.ell(x, y, .12*sz, .12*sz, col, False); r.ell(x - .02, y + .02, .06*sz, .06*sz, col2, False)
        return {'mund': (x + .12*sz, y)}
    if kind == 'flamme':
        fl = math.sin(p['phase']*2) * .04
        cols = ELEMENT_COLS.get(el or 'feuer')
        r.poly([(x - .2*sz, y - .15*sz), (x + .2*sz, y - .15*sz), (x + .12*sz, y + .2*sz), (x + fl, y + .45*sz), (x - .1*sz, y + .22*sz)], cols[2])
        r.poly([(x - .13*sz, y - .1*sz), (x + .13*sz, y - .1*sz), (x + .07*sz, y + .15*sz), (x + fl*.5, y + .32*sz), (x - .06*sz, y + .15*sz)], cols[1])
        r.ell(x, y - .02*sz, .1*sz, .1*sz, cols[0], False)
        r.dot(x + .03*sz, y + .02*sz, C('#2b1e33'), 1 if r.S > 40 else 0); r.dot(x + .09*sz, y + .02*sz, C('#2b1e33'), 1 if r.S > 40 else 0)
        if g(sp, 'candle'):
            r.capsule(x, y - .2*sz, x, y - .5*sz, .12*sz, C('#f0e4cc')); r.dot(x, y - .15*sz, C('#3a2a2a'))
        particles(r, el or 'feuer', p['t'], x, y + .3*sz, .12*sz, n=4)
        return {'mund': (x + .15*sz, y)}
    if kind in ('geist', 'kapuze'):
        wav = math.sin(p['phase']*2) * .05
        ghost = g(sp, 'ghost_col', col)
        r.poly([(x - .17*sz, y + .1*sz), (x + .17*sz, y + .1*sz), (x + .05*sz + wav, y - .35*sz), (x - .1*sz, y - .28*sz + wav),
                (x - .28*sz + wav, y - .32*sz)], ghost)
        r.ell(x, y + .15*sz, .18*sz, .2*sz, ghost)
        if kind == 'kapuze':
            hood = g(sp, 'hood_col', col)
            r.ell(x - .02*sz, y + .22*sz, .2*sz, .2*sz, hood)
            r.tri(x - .15*sz, y + .3*sz, .15*sz, .2*sz, hood, lean=-.1*sz)
            r.ell(x + .07*sz, y + .2*sz, .11*sz, .12*sz, C('#140e18'), False)
        ec = g(sp, 'eye', C('#2b1e33'))
        r.dot(x + .06*sz, y + .2*sz, ec, 1 if r.S > 40 else 0); r.dot(x + .14*sz, y + .2*sz, ec, 1 if r.S > 40 else 0)
        if p['open'] > .3: r.ell(x + .1*sz, y + .08*sz, .04*sz, .05*sz*p['open'] + .01, C('#140e18'), False)
        armx = x + .18*sz + max(0, p['lunge'])*1.5
        r.capsule(x + .08*sz, y + .05*sz, armx, y + .02*sz + p['cast']*.1, .06*sz, ghost, .04*sz)
        if g(sp, 'item'):
            it = sp['item']
            if it == 'sense':
                r.capsule(armx, y - .2*sz, armx + .02, y + .45*sz, .025, C('#5a3a2a'))
                r.capsule(armx + .02, y + .45*sz, armx + .25*sz, y + .35*sz, .04, C('#c8ccd8'), .01)
            elif it == 'glocke':
                r.ell(armx + .06, y - .02, .07*sz, .08*sz, C('#e0b048'))
            elif it == 'laterne':
                r.ell(armx + .04, y - .05, .05*sz, .07*sz, C('#ffd27a'))
        if el and p['anim'] != 'death': particles(r, el, p['t'], x, y, .25*sz, n=5)
        return {'mund': (x + .2*sz, y + .15*sz)}
    if kind in ('wicht', 'elementar'):
        big = kind == 'elementar'
        cols = ELEMENT_COLS.get(el or 'erde')
        body = g(sp, 'body_col', cols[1])
        bs = (.26 if big else .17) * sz
        rng = random.Random(len(sp['name']))
        for k in range(5 if big else 3):
            a = k / (5 if big else 3) * 2*math.pi + p['phase']*.5
            r.ell(x + math.cos(a)*bs*.4, y - bs*.6 - k*.04*sz, bs*.4, bs*.3, cols[2] if k % 2 else body)
        r.ell(x, y, bs, bs*1.05, body, lo=cols[2], hi=cols[0])
        if g(sp, 'chunks'):
            for k in range(4):
                a = rng.random()*6.28 + p['phase']*.3
                r.ell(x + math.cos(a)*bs*1.25, y + math.sin(a)*bs*1.1, bs*.18, bs*.15, cols[2])
        arm_r = max(0, p['lunge'])*1.2
        for side, s_ in ((-1, .7), (1, 1)):
            ax = x + side*bs*.95 + (arm_r if side > 0 else 0)
            r.ell(ax, y - bs*.05 + (p['cast']*.1 if side > 0 else 0), bs*.32*s_, bs*.28*s_, body if side > 0 else cols[2])
        ec = g(sp, 'eye', C('#2b1e33') if not big else WHITE)
        r.dot(x + bs*.3, y + bs*.25, ec, 1 if r.S > 30 else 0); r.dot(x + bs*.6, y + bs*.25, ec, 1 if r.S > 30 else 0)
        if p['anim'] != 'death': particles(r, el or 'erde', p['t'], x, y, bs*1.4, n=8 if big else 5)
        return {'mund': (x + bs, y)}
    return {'mund': (x, y)}

# ================================================================ WOLKEN / STÜRME / NEBEL
def cloud(r, sp, p):
    col = sp['col']; el = g(sp, 'element')
    x = p['lunge'] * .6 + p['recoil']
    y = g(sp, 'alt', .5) + math.sin(p['phase']) * .03
    rng = random.Random(len(sp['name']) * 3)
    n = g(sp, 'puffs', 9)
    for k in range(n):
        a = k / n * 2*math.pi + p['phase'] * (.25 if not g(sp, 'swirl') else .6)
        rr = .25 + rng.random() * .12
        px_, py_ = x + math.cos(a) * .3, y + math.sin(a) * .16
        c = col if k % 3 else shade(col, .85)
        r.ell(px_, py_, rr*.6, rr*.45, c, lo=shade(col, .75))
    r.ell(x, y, .34, .22, light(col, .1), lo=shade(col, .8))
    if g(sp, 'eyes'):
        ec = sp['eyes']
        r.dot(x + .12, y + .05, ec, 1); r.dot(x + .24, y + .05, ec, 1)
        if p['open'] > .3: r.ell(x + .18, y - .08, .06, .04*p['open'] + .01, C('#140e18'), False)
    if el and p['anim'] != 'death':
        particles(r, el, p['t'], x, y, .5, n=10, seed=9, rise=False)
        if el == 'blitz' and p['anim'] == 'attack' and p['t'] in (2, 3):
            bx_ = x + .3; by_ = y - .15
            pts = [(bx_, by_)]
            for k in range(5): pts.append((pts[-1][0] + .05 + (k % 2)*.04, pts[-1][1] - .1))
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]): r.capsule(x0, y0, x1, y1, .025, C('#fff07a'))
    if g(sp, 'rain'):
        for k in range(8):
            rx_ = x - .35 + k * .1; ry_ = y - .25 - ((p['t'] + k) % 4) * .07
            r.dot(rx_, ry_, sp['rain'])
    return {'mund': (x + .4, y)}

# ================================================================ PFLANZEN
def plant(r, sp, p):
    kind = g(sp, 'kind', 'bluete')
    col, col2 = sp['col'], g(sp, 'col2', C('#4a7d4a'))
    x = p['recoil']
    sway = math.sin(p['phase']) * .04 + (math.sin(p['walk']) * .05 if p['moving'] else 0)
    if kind == 'bluete':
        r.ell(x, .04, .25, .05, shade(col2, .7))
        for s in (-1, 1): r.ell(x + s*.12, .12, .14, .05, col2, rot=s*.5)
        hx = x + sway + p['lunge']*1.6
        hy = .62 + p['bob'] + (p['open']*.05)
        r.capsule(x, .02, x + sway*.5, .3, .06, col2)
        r.capsule(x + sway*.5, .3, hx - .05, hy - .1, .055, col2)
        o = .25 + p['open'] * .7
        for k in range(6):
            a = k / 6 * 2*math.pi
            r.ell(hx + math.cos(a)*.13, hy + math.sin(a)*.13, .09, .07, col, rot=a)
        r.ell(hx + .02, hy, .1, .1*o + .01, DARKMOUTH, False)
        if r.S > 35:
            for k in range(-1, 2): r.dot(hx + .03 + k*.03, hy + .1*o - .01, TOOTH); r.dot(hx + .03 + k*.03, hy - .1*o + .01, TOOTH)
        return {'mund': (hx + .12, hy)}
    if kind == 'ranke':
        n = 3
        for k in range(n):
            bx = x - .2 + k*.2
            pts = [(bx, 0)]
            for j in range(8):
                a = math.pi/2 + math.sin(p['phase'] + j*.7 + k*2) * .6 + (p['lunge']*-3 if k == n-1 and p['anim'] == 'attack' else 0)
                pts.append((pts[-1][0] + math.cos(a)*.08, pts[-1][1] + math.sin(a)*.08))
            for j, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
                r.capsule(x0, y0, x1, y1, .07*(1 - j/9), col)
                if j % 2: r.tri(x1 + .02, y1, .03, .05, g(sp, 'acc', C('#e8dcc0')), lean=.03)
        if g(sp, 'flower'): r.ell(pts[-1][0], pts[-1][1], .06, .05, sp['flower'])
        r.ell(x, .02, .32, .04, shade(col, .6), False)
        return {'mund': (x + .3, .5)}
    if kind == 'pilz':
        jump = max(0, math.sin(p['walk'])) * .1 if p['moving'] else 0
        sq = 1 - (.1 if p['anim'] == 'attack' and p['t'] in (1, 2) else 0)
        stem = g(sp, 'stem', C('#e8dcc0'))
        r.capsule(x - .05, .02 + jump, x + .05, .02 + jump, .06, shade(stem, .7))
        r.ell(x, .22*sq + jump, .14, .2*sq, stem)
        r.ell(x, .45*sq + jump, .3, .17, col)
        for k in range(3): r.dot(x - .15 + k*.13, .52*sq + jump, WHITE, 1 if r.S > 40 else 0)
        eye(r, x + .07, .25*sq + jump, sp); eye(r, x + .02, .25*sq + jump, sp)
        if p['anim'] == 'attack' and p['t'] >= 2:
            particles(r, g(sp, 'element', 'gift'), p['t'], x + .2, .5, .3, n=10)
        return {'mund': (x + .2, .3)}
    if kind == 'baum':
        trunk = g(sp, 'trunk', C('#6a4a32'))
        leaf = col
        step = math.sin(p['walk']) * .06 if p['moving'] else 0
        for s, c in ((-1, shade(trunk, .7)), (1, trunk)):
            r.capsule(x + s*.08, .25, x + s*.15 + step*s, .02, .07, c, .05)
        r.capsule(x, .2, x + sway*.3, .62, .22, trunk, .18)
        armx = x + .25 + max(0, p['lunge'])*1.5
        r.capsule(x + .05, .5, armx, .42 + p['swing']*.1, .07, trunk, .04)
        r.capsule(x - .05, .5, x - .25, .55, .06, shade(trunk, .75), .03)
        r.ell(x + sway*.4, .82, .36, .24, leaf)
        r.ell(x - .12 + sway*.4, .9, .2, .14, light(leaf, .15))
        if g(sp, 'flower'):
            rng = random.Random(4)
            for _ in range(5): r.dot(x + (rng.random()-.5)*.6, .75 + rng.random()*.2, sp['flower'], 1 if r.S > 40 else 0)
        r.ell(x + .08, .5, .05, .04, C('#2b1e33'), False); r.dot(x + .1, .5, g(sp, 'eye', C('#ffd27a')))
        r.capsule(x + .03, .4, x + .13, .4, .02, C('#2b1e33'))
        return {'mund': (armx, .42)}
    return {'mund': (x, .3)}

# ================================================================ SCHWÄRME
def swarm(r, sp, p):
    kind = g(sp, 'kind', 'insekt'); col = sp['col']
    n = g(sp, 'n', 22)
    cx = p['lunge'] * 2.0 + p['recoil']
    cy = g(sp, 'alt', .45) + p['bob']
    rng = random.Random(len(sp['name']))
    spread = .38 * (.7 if p['anim'] == 'attack' and p['t'] in (2, 3) else 1) * (1.6 if kind == 'goblin' else 1)
    for i in range(n):
        a0 = rng.random() * 2*math.pi; sp_ = .6 + rng.random()*.8; rad = .3 + rng.random()*.7
        a = a0 + p['phase'] * sp_ + (p['walk'] if p['moving'] else 0)
        x = cx + math.cos(a) * spread * rad
        y = cy + math.sin(a*1.3) * spread * .6 * rad + (0 if kind not in ('ratte', 'ameise', 'kaefer') else -cy + .03 + abs(math.sin(a))*.02)
        if kind == 'insekt':
            if r.S > 45:
                r.ell(x, y, .014, .011, col, False); r.ell(x - .004, y + .014, .01, .006, mix(col, WHITE, .6) if (i + p['t']) % 2 else col, False)
            else:
                r.dot(x, y, col); r.dot(x + 1/r.S, y, col); r.dot(x, y + 1/r.S, mix(col, WHITE, .6) if (i + p['t']) % 2 else col)
        elif kind == 'fledermaus':
            r.dot(x, y, col); r.dot(x - 1/r.S, y + 1/r.S*((i + p['t']) % 2), col); r.dot(x + 1/r.S, y + 1/r.S*((i + p['t']) % 2), col)
        elif kind in ('ratte', 'ameise', 'kaefer'):
            r.ell(x, y + .02, .035, .022, col); r.dot(x + .03, y + .02, shade(col, .6))
        elif kind == 'licht':
            r.dot(x, y, WHITE); r.dot(x + 1/r.S, y, col); r.dot(x - 1/r.S, y, col); r.dot(x, y + 1/r.S, col)
        elif kind == 'goblin':
            yy = .01 + abs(math.sin(a*2 + p['t'])) * .015
            r.capsule(x - .01, yy, x - .01, yy + .04, .018, C('#3a2a2a')); r.capsule(x + .015, yy, x + .015, yy + .04, .018, C('#3a2a2a'))
            r.ell(x, yy + .07, .03, .04, C('#6a5a4a')); r.ell(x + .01, yy + .13, .028, .028, C('#6a9a55'))
            r.tri(x - .02, yy + .13, .02, .03, C('#6a9a55'), lean=-.03)
            r.capsule(x + .03, yy + .06, x + .05, yy + .16, .008, C('#c8ccd8'))
        elif kind == 'vogel':
            r.dot(x, y, col); r.dot(x - 1/r.S, y + 1/r.S, col); r.dot(x + 1/r.S, y + 1/r.S, col); r.dot(x - 2/r.S, y + 2/r.S*((i + p['t']) % 2), col)
    if g(sp, 'core'):
        r.ell(cx, cy, .1, .1, sp['core'])
        eye(r, cx + .04, cy + .02, sp)
    return {'mund': (cx + .4, cy)}

# ================================================================ OBJEKTE / MIMIKS
def obj(r, sp, p):
    kind = g(sp, 'kind', 'truhe'); col, col2 = sp['col'], g(sp, 'col2', C('#c8a040'))
    x = p['lunge'] * .6 + p['recoil']
    jump = max(0, math.sin(p['walk'])) * .12 if p['moving'] else 0
    if kind in ('truhe', 'haus', 'burg'):
        W_ = {'truhe': .8, 'haus': .9, 'burg': 1.0}[kind]; H_ = {'truhe': .42, 'haus': .5, 'burg': .55}[kind]
        lid_a = .15 + (p['open'] * .9) + (math.sin(p['phase'])*.05 if p['anim'] == 'idle' else 0)
        y0 = jump
        if jump: r.shadow(x, W_)
        if kind == 'truhe':
            r.ell(x - W_*.15, y0 + H_*.4, W_*.1, H_*.25, DARKMOUTH, False)
            r.poly([(x - W_/2, y0), (x + W_/2, y0), (x + W_/2, y0 + H_), (x - W_/2, y0 + H_)], col)
            for k in (.25, .75): r.line(x - W_/2 + W_*k, y0, x - W_/2 + W_*k, y0 + H_, col2)
            r.line(x - W_/2, y0 + H_*.5, x + W_/2, y0 + H_*.5, shade(col, .7))
            hx, hy = x - W_/2, y0 + H_
            ca, sa = math.cos(lid_a), math.sin(lid_a)
            pts = [(0, 0), (W_, 0), (W_, H_*.45), (0, H_*.45)]
            r.poly([(hx + px_*ca - py_*sa, hy + px_*sa + py_*ca) for px_, py_ in pts], shade(col, 1.1))
            tx_ = hx + W_*ca; ty_ = hy + W_*sa
            if lid_a > .3:
                r.poly([(x - W_/2 + .02, y0 + H_), (x + W_/2 - .02, y0 + H_), (tx_, ty_)], DARKMOUTH)
                for k in range(5):
                    fx = x - W_/2 + .05 + k * (W_ - .1)/4
                    r.tri(fx, y0 + H_, .05, .06, TOOTH)
                r.capsule(x, y0 + H_ + .02, x + W_*.3 + p['lunge']*1.5, y0 + H_ + .05, .07, C('#c84a6a'), .05)
            r.ell(x + W_*.2, y0 + H_*.6, .03, .04, col2)
            ec = g(sp, 'eye', C('#ffd27a'))
            r.dot(x + W_*.32, y0 + H_*.8, ec, 1 if r.S > 40 else 0)
        else:
            body = col
            r.poly([(x - W_/2, y0), (x + W_/2, y0), (x + W_/2, y0 + H_), (x - W_/2, y0 + H_)], body)
            if kind == 'burg':
                for k in range(5):
                    if k % 2 == 0: r.poly([(x - W_/2 + k*W_/5, y0 + H_), (x - W_/2 + (k+1)*W_/5, y0 + H_), (x - W_/2 + (k+1)*W_/5, y0 + H_ + .08), (x - W_/2 + k*W_/5, y0 + H_ + .08)], body)
                r.poly([(x - W_/2 - .08, y0), (x - W_/2 + .12, y0), (x - W_/2 + .12, y0 + H_ + .3), (x - W_/2 - .08, y0 + H_ + .3)], shade(body, .9))
                r.tri(x - W_/2 + .02, y0 + H_ + .3, .26, .2, C('#525a7a'))
            else:
                r.poly([(x - W_/2 - .06, y0 + H_), (x + W_/2 + .06, y0 + H_), (x, y0 + H_ + .35)], C('#953a40'))
            o = .1 + p['open'] * .15
            r.ell(x + .1, y0 + .16, .16, o, DARKMOUTH, False)
            for k in range(4):
                r.tri(x + .0 + k*.07, y0 + .16 + o - .01, .04, -.05, TOOTH)
                r.tri(x + .0 + k*.07, y0 + .16 - o + .01, .04, .05, TOOTH)
            for wx in (-.25, .3):
                r.ell(x + wx, y0 + H_*.68, .07, .06, g(sp, 'eye', C('#ffd27a')), False)
        return {'mund': (x + W_/2, y0 + H_*.5)}
    if kind == 'buch':
        y = .4 + math.sin(p['phase'])*.04 + jump
        r.shadow(x, .5)
        o = .3 + p['open']*.6 + (math.sin(p['phase']*2)*.15 if p['moving'] else 0)
        r.poly([(x, y), (x - .3, y + .05 + o*.1), (x - .3, y - .25 + o*.1), (x, y - .2)], col)
        r.poly([(x, y), (x + .3*math.cos(o), y + .05 + .3*math.sin(o)), (x + .3*math.cos(o), y - .25 + .3*math.sin(o)), (x, y - .2)], shade(col, 1.1))
        r.poly([(x - .02, y - .01), (x - .26, y + .03 + o*.1), (x - .26, y - .21 + o*.1), (x - .02, y - .18)], C('#f0e4cc'))
        for k in range(3): r.tri(x + .05 + k*.07, y - .2, .04, .05, TOOTH)
        particles(r, g(sp, 'element', 'arkan'), p['t'], x, y, .3, n=6)
        r.dot(x - .15, y - .05, g(sp, 'eye', C('#c83a3a')), 1 if r.S > 40 else 0)
        return {'mund': (x + .3, y)}
    if kind == 'helm':
        y = .3 + math.sin(p['phase'])*.04 + jump
        r.shadow(x, .35)
        r.ell(x, y, .2, .2, col)
        r.capsule(x + .02, y, x + .18, y, .05, C('#140e18'))
        r.dot(x + .12, y, g(sp, 'eye', C('#8ad0ff')), 1 if r.S > 30 else 0)
        if g(sp, 'plume'): r.ell(x - .1, y + .22, .12, .05, sp['plume'], rot=.4)
        return {'mund': (x + .2, y)}
    if kind == 'klinge':
        n = g(sp, 'n', 1)
        rng = random.Random(len(sp['name']))
        for i in range(n):
            ox = (rng.random() - .5) * .9 if n > 1 else 0; oy = (rng.random() - .5) * .5 if n > 1 else 0
            a = math.radians(-60 + i*37 + (p['swing']*80 if p['anim'] == 'attack' else math.sin(p['phase'] + i)*15))
            cx_, cy_ = x + ox + p['lunge']*1.2, .45 + oy + math.sin(p['phase'] + i)*.04
            ln = .5 if n == 1 else .25
            dx, dy = math.cos(a), math.sin(a)
            r.capsule(cx_ - dx*ln*.3, cy_ - dy*ln*.3, cx_ + dx*ln*.7, cy_ + dy*ln*.7, .05 if n == 1 else .035, col, .015)
            r.capsule(cx_ - dx*ln*.3 - dy*.06, cy_ - dy*ln*.3 + dx*.06, cx_ - dx*ln*.3 + dy*.06, cy_ - dy*ln*.3 - dx*.06, .025, col2)
        if g(sp, 'core'): r.ell(x, .45, .07, .07, sp['core'])
        r.shadow(x, .4)
        return {'mund': (x + .4, .45)}
    if kind == 'glocke':
        y = .45 + math.sin(p['phase'])*.03
        sw = math.sin(p['phase']*2) * .2 + p['swing']*.3
        r.shadow(x, .4)
        r.poly([(x - .05 + sw*.1, y + .2), (x + .05 + sw*.1, y + .2), (x + .2 + sw*.3, y - .15), (x - .2 + sw*.3, y - .15)], col)
        r.ell(x + sw*.3, y - .16, .05, .05, shade(col, .6))
        ec = g(sp, 'eye', C('#8ad0ff'))
        r.dot(x + .02 + sw*.2, y + .05, ec, 1 if r.S > 30 else 0); r.dot(x + .09 + sw*.2, y + .05, ec, 1 if r.S > 30 else 0)
        particles(r, 'arkan', p['t'], x, y, .3, n=4)
        return {'mund': (x + .2, y)}
    if kind == 'spiegel':
        y = .05 + jump
        r.poly([(x - .2, y), (x + .2, y), (x + .2, y + .6), (x - .2, y + .6)], col2)
        r.poly([(x - .15, y + .05), (x + .15, y + .05), (x + .15, y + .55), (x - .15, y + .55)], mix(col, WHITE, .2 + .1*math.sin(p['phase'])))
        r.line(x - .1, y + .45, x - .02, y + .53, WHITE)
        r.dot(x + .04, y + .32, g(sp, 'eye', C('#c83a3a')), 1 if r.S > 30 else 0)
        return {'mund': (x + .2, y + .3)}
    if kind == 'schiff':
        y = .1 + math.sin(p['phase'])*.03
        hull = col
        r.poly([(x - .55, y + .2), (x + .55, y + .2), (x + .4, y), (x - .45, y)], hull)
        r.poly([(x + .4, y + .2), (x + .62, y + .3), (x + .55, y + .2)], hull)
        r.line(x - .5, y + .14, x + .5, y + .14, shade(hull, .7))
        for mx in (-.15, .2):
            r.capsule(x + mx, y + .2, x + mx, y + .85, .025, shade(hull, .7))
            sail = g(sp, 'sail', C('#c8c4d4'))
            r.poly([(x + mx + .02, y + .8), (x + mx + .25 + math.sin(p['phase'])*.03, y + .7), (x + mx + .22, y + .4), (x + mx + .02, y + .35)], sail)
            r.dot(x + mx + .12, y + .55, shade(sail, .6), 1)
        particles(r, g(sp, 'element', 'nebel'), p['t'], x, y + .4, .5, n=8)
        return {'mund': (x + .6, y + .3)}
    if kind == 'muschel':
        o = .1 + p['open']*.4 + (math.sin(p['phase'])*.04 if p['anim'] == 'idle' else 0)
        r.ell(x, .1, .3, .1, col)
        r.ell(x - .05, .14 + o*.3, .3, .1, light(col, .15), rot=o*.6)
        if o > .2:
            r.ell(x + .05, .16, .2, .05, C('#e8a0b0'), False); r.dot(x + .05, .16, WHITE, 1)
        return {'mund': (x + .3, .15)}
    if kind == 'stumpf':
        o = .05 + p['open']*.12
        r.poly([(x - .22, 0), (x + .22, 0), (x + .18, .45), (x - .18, .45)], col)
        r.ell(x, .45, .18, .05, C('#c8a878'))
        r.ell(x + .1, .22, .08, o, DARKMOUTH, False)
        for k in range(3): r.dot(x + .05 + k*.04, .22 + o - .01, TOOTH)
        r.dot(x + .05, .35, g(sp, 'eye', C('#ffd27a')), 1 if r.S > 30 else 0)
        for s in (-1, 1): r.capsule(x + s*.18, .05, x + s*.32, 0, .05, col)
        return {'mund': (x + .2, .22)}
    if kind == 'stein':
        r.ell(x, .2 + jump, .32, .2, col)
        r.ell(x - .05, .35 + jump, .25, .06, g(sp, 'moss', C('#6e9e58')), False)
        ec = g(sp, 'eye', C('#ffd27a'))
        if p['anim'] != 'idle' or p['t'] in (2, 3):
            r.dot(x + .12, .25 + jump, ec, 1 if r.S > 30 else 0); r.dot(x + .2, .25 + jump, ec, 1 if r.S > 30 else 0)
        return {'mund': (x + .3, .2)}
    if kind == 'kugel':
        rot = p['walk'] if p['moving'] else p['phase']*.2
        y = .25 + jump
        r.ell(x, y, .25, .25, col)
        for k in range(10):
            a = k/10 * 2*math.pi + rot
            r.tri(x + math.cos(a)*.24, y + math.sin(a)*.24, .04, .07, col2, lean=math.cos(a)*.05)
        return {'mund': (x + .3, y)}
    return {'mund': (x, .3)}

# ================================================================ DRACHEN / HYDREN
def dragon(r, sp, p):
    kind = g(sp, 'kind', 'drache')
    col, col2, acc = sp['col'], g(sp, 'col2', light(sp['col'], .35)), g(sp, 'acc', C('#e8dcc0'))
    bone = g(sp, 'bone')
    L, bh, leg = g(sp, 'L', 1.1), g(sp, 'bh', .34), g(sp, 'leg', .26)
    bx = p['lunge'] * .6 + p['recoil']
    by = leg + bh/2 + p['bob']
    wings = kind in ('drache', 'wyvern') and not g(sp, 'nowings')
    flap = p['flap'] if p['anim'] != 'idle' else math.sin(p['phase']) * .3
    if wings:
        wing(r, bx + .05, by + bh*.4, g(sp, 'span', .95), .8 + .6*flap, g(sp, 'wingcol', shade(col, .75)), 'fledermaus', far=True)
    stride = .1 if p['moving'] else 0
    legs_x = [(-L/2 + .18, 0), (L/2 - .2, math.pi/2)] if kind != 'wyvern' else [(-.05, 0)]
    def legs(far):
        for hx, off in legs_x:
            ph = p['walk'] + off + (math.pi if far else 0)
            fx = bx + hx + math.sin(ph) * stride
            lift = max(0, math.cos(ph)) * .05 if p['moving'] else 0
            c = shade(col, .7) if far else col
            r.capsule(bx + hx, by - bh*.1, fx + .03, leg*.45 + lift, .11, c, .08)
            r.capsule(fx + .03, leg*.45 + lift, fx, lift + .03, .08, c, .06)
            r.ell(fx + .04, lift + .02, .06, .03, acc, False)
    legs(True)
    # Schwanz
    wag = math.sin(p['phase']) * .05
    tpts = []
    for k in range(9):
        s = k / 8
        tpts.append((bx - L/2 + .05 - s * L*.75, by - s*bh*.6 + math.sin(s*3 + p['phase'])*.04 + wag*s, bh*.7*(1 - s*.85)))
    for (x0, y0, w0), (x1, y1, w1) in zip(tpts, tpts[1:]):
        r.capsule(x0, y0, x1, y1, w0, col, w1)
    ex, ey, _ = tpts[-1]
    r.poly([(ex, ey + .05), (ex - .1, ey), (ex, ey - .05)], acc)
    # Körper
    r.ell(bx, by, L/2, bh/2, col)
    if bone:
        for k in range(5): r.capsule(bx - L*.25 + k*L*.12, by + bh*.35, bx - L*.25 + k*L*.12 + .02, by - bh*.35, .03, bone)
    else:
        r.ell(bx + .05, by - bh*.2, L*.38, bh*.22, col2, False)
    for k in range(6):
        x = bx - L*.4 + k*L*.16
        r.tri(x, by + bh*.42 - abs(k - 2.5)*.01, .06, .09, acc, lean=-.02)
    # Hälse/Köpfe
    heads = g(sp, 'heads', 1)
    mouth = None
    hlist = []
    if heads == 1:
        hlist = [(0, 1.0)]
    else:
        nvis = min(heads, 9)
        hlist = [((i - (nvis-1)/2) / max(1, nvis-1), .7 + .3*((i*7) % 5)/4) for i in range(nvis)]
    for i, (spread, ln) in enumerate(hlist):
        nb = (bx + L/2 - .1, by + bh*.2)
        sway = math.sin(p['phase'] + i*1.3) * .04
        if heads == 1:
            nx = bx + L/2 + .2 * ln + p['open'] * .1 + sway
            ny = by + .35 * ln + bh*.3 - (p['open'] * .08 if p['anim'] == 'attack' else 0)
        else:
            nx = bx + L/2 + .0 + (spread + .5) * .6 + p['open'] * .1 + sway
            ny = by + bh*.3 + .12 + (1 - abs(spread)) * .45 * ln + (i % 3) * .07 - (p['open'] * .08 if p['anim'] == 'attack' else 0)
        midx, midy = (nb[0] + nx)/2 + .02, (nb[1] + ny)/2 + .08
        nw = .13 if heads == 1 else .08
        c = shade(col, .85) if (heads > 1 and i % 2) else col
        r.capsule(nb[0], nb[1], midx, midy, nw*1.4, c, nw*1.1)
        r.capsule(midx, midy, nx, ny, nw*1.1, c, nw)
        hs = .1 if heads == 1 else .07
        r.ell(nx + hs*.4, ny, hs*1.1, hs*.8, c)
        snx, sny = nx + hs*1.4, ny - hs*.2
        if p['open'] > .3:
            r.ell(snx, sny - hs*.25, hs*.8, hs*.35, DARKMOUTH, False)
            r.capsule(nx + hs*.6, sny - hs*.45, snx + hs*.6, sny - hs*.75 - p['open']*hs*.4, hs*.4, c)
            r.dot(snx + hs*.3, sny - hs*.2, TOOTH)
        r.ell(snx, sny, hs*.8, hs*.45, c)
        eye(r, nx + hs*.6, ny + hs*.3, sp)
        r.capsule(nx - hs*.1, ny + hs*.5, nx - hs*.9, ny + hs*1.3, hs*.35, acc, hs*.1)
        if mouth is None or (heads > 1 and abs(spread) < .2):
            mouth = (snx + hs*.8, sny - hs*.1)
    legs(False)
    if wings:
        wing(r, bx + .12, by + bh*.45, g(sp, 'span', .95), .6 + .6*flap, g(sp, 'wingcol', shade(col, .9)), 'fledermaus')
    if g(sp, 'element') and p['anim'] != 'death':
        particles(r, sp['element'], p['t'], bx, by, L*.5, n=5, seed=6)
    return {'mund': mouth}

# ================================================================ KRÖTEN / SCHNECKEN / SCHLUND
def frog(r, sp, p):
    col = g(sp, 'col', C('#c8c4e0')); col2 = g(sp, 'col2', light(col, .4))
    x = p['recoil']
    jump = max(0, math.sin(p['walk'])) * .3 if p['moving'] else 0
    sq = 1 + (math.sin(p['phase'])*.04 if p['anim'] == 'idle' else 0)
    if jump: r.shadow(x, .6)
    y = jump
    leg_ext = .2 if jump > .1 else 0
    r.capsule(x - .2, y + .12, x - .3 - leg_ext, y + .03 - leg_ext*.3, .1, shade(col, .85))
    r.ell(x, y + .25*sq, .34, .22*sq, col)
    r.ell(x + .08, y + .16, .22, .1, col2, False)
    if g(sp, 'warts'):
        rng = random.Random(3)
        for _ in range(6): r.dot(x + (rng.random()-.6)*.5, y + .25 + rng.random()*.15, shade(col, .7), 1 if r.S > 40 else 0)
    if g(sp, 'spots'):
        for k in range(4): r.dot(x - .2 + k*.12, y + .38, sp['spots'], 1 if r.S > 30 else 0)
    r.ell(x + .2, y + .45*sq, .09, .09, col); r.ell(x + .22, y + .46*sq, .05, .05, WHITE, False); r.dot(x + .24, y + .46*sq, C('#2b1e33'), 1 if r.S > 40 else 0)
    r.capsule(x + .15, y + .1, x + .25 + leg_ext*.3, y + .02, .07, col)
    r.line(x + .2, y + .2, x + .34, y + .22, shade(col, .55))
    if p['anim'] == 'attack' and p['open'] > .3:
        tl = p['lunge'] * 4 + .2
        r.capsule(x + .32, y + .22, x + .32 + tl, y + .22, .04, C('#e8708a'))
        r.ell(x + .32 + tl, y + .22, .05, .05, C('#e8708a'))
    if g(sp, 'element') and p['anim'] != 'death': particles(r, sp['element'], p['t'], x, y + .3, .3, n=4)
    return {'mund': (x + .34, y + .22)}

def snail(r, sp, p):
    col, shell = sp['col'], g(sp, 'col2', C('#a87a4a'))
    st = math.sin(p['walk']) * .05 if p['moving'] else 0
    x = p['recoil'] + p['lunge']*.6
    r.ell(x + .05 + st, .07, .4 + abs(st), .07, col)
    r.capsule(x + .3 + st, .08, x + .38 + st, .25, .08, col)
    for s in (-.02, .03):
        r.line(x + .36 + st, .25, x + .38 + st + s, .36, col); r.dot(x + .38 + st + s, .37, C('#2b1e33'))
    r.ell(x - .05, .3, .26, .24, shell)
    for k in range(3):
        rr = .2 - k*.06
        r.ell(x - .05 + k*.02, .3 + k*.01, rr, rr*.9, shade(shell, 1 - k*.1) if k % 2 else light(shell, .1), False)
    if g(sp, 'element'):
        particles(r, sp['element'], p['t'], x - .3, .05, .2, n=4)
        if sp['element'] == 'feuer': r.line(x - .5, .01, x - .2, .01, C('#ff9a3c'))
    return {'mund': (x + .4, .2)}

def maw(r, sp, p):
    col = sp['col']
    x = p['recoil'] + p['lunge']*.3
    y = g(sp, 'alt', .5)
    o = .6 + p['open']*.4 + math.sin(p['phase'])*.05
    for k in range(12):
        a = k/12 * 2*math.pi + p['phase']*.5
        r.ell(x + math.cos(a)*.38, y + math.sin(a)*.3, .1, .08, col if k % 2 else shade(col, .8))
    r.ell(x, y, .32*o, .26*o, C('#0c0810'), False)
    r.ell(x, y, .18*o, .14*o, g(sp, 'core', C('#3a2a5a')), False)
    for k in range(10):
        a = k/10 * 2*math.pi
        r.tri(x + math.cos(a)*.3*o, y + math.sin(a)*.24*o, .05, -.06, TOOTH)
    if g(sp, 'eyes'):
        r.dot(x, y, sp['eyes'], 1)
    particles(r, g(sp, 'element', 'schatten'), p['t'], x, y, .5, n=10, rise=False)
    return {'mund': (x + .3, y)}

ARCHETYPES = dict(vierbeiner=quadruped, zweibeiner=biped, flieger=flyer, insekt=insect, schlange=serpent,
                  fisch=fish, krake=octopus, schleim=slime, geist=spirit, wolke=cloud, pflanze=plant,
                  schwarm=swarm, objekt=obj, drache=dragon, kroete=frog, schnecke=snail, schlund=maw)
