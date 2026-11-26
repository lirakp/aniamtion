"""Großes Spieler-Sprite (ca. 40 px hoch, Zelle 48x48) mit Gelenk-Rig, Umhang und Schwert – für alle Völker.
Aufruf: python3 hero.py
Ausgabe: characters/held/<volk>_<kleidung>.png (Zeile = Animation, Spalte = Frame, Zelle 48x48),
         characters/held/held.json, preview_held.gif, preview_held_voelker.gif
Blick nach rechts; für links horizontal spiegeln. Füße stehen auf y=46, Körpermitte x=24.
"""
import os, json, math
from PIL import Image, ImageDraw
from multiprocessing import Pool
import generate as g
from generate import C, shade, mix
import races as rc

OUT = os.path.join(g.BASE, 'characters', 'held')
CS, GROUND, MIDX = 48, 46, 24
INK, WHITE = C('#2b1e33'), C('#ffffff')
STEEL, STEEL_L, STEEL_D = C('#a8acbc'), C('#e0e4ee'), C('#6a6e80')
SLASH = C('#f0f4ff')

def pt(o, a, L): r = math.radians(a); return (o[0] + math.sin(r) * L, o[1] + math.cos(r) * L)
def cap(d, a, b, r, col):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) * 2))
    for i in range(n + 1):
        x = a[0] + (b[0] - a[0]) * i / n; y = a[1] + (b[1] - a[1]) * i / n
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

# ---------------------------------------------------------------- Pose
def pose(**k):
    p = dict(lean=0, dy=0, fl=(0, 0), bl=(0, 0), fa=(10, 20), ba=(-10, 20), cape=0, sword=None, eye='auf', hip=None, flash=0, kneel=False)
    p.update(k); return p

def draw(race, outfit, P):
    im = Image.new('RGBA', (CS, CS)); d = ImageDraw.Draw(im)
    dwarf = race.get('dwarf'); animal = race.get('animal')
    th, sh, tor = (5, 5, 10) if dwarf else (7, 7, 11)
    pal = rc.pal_for(race, outfit); fp = rc.feature_pal(race)
    skin = race.get('s', g.SKIN); skin_s = race.get('S', shade(skin, .82))
    arm_c = skin if animal and outfit == 'tunika' and False else pal['c']
    armor = outfit == 'ruestung'
    body_c = STEEL if armor else race['tunic']; body_d = shade(body_c, .78)
    pants = pal['p']; boots = pal['b']; belt = pal['l']
    cape_c = shade(race['tunic'], .62) if armor else C('#a83a3a') if race['tunic'][0] < 140 else C('#3a4a7a')
    cape_d = shade(cape_c, .75)

    # Hüfte so, dass der tiefste Fuß auf dem Boden steht (außer in der Luft)
    def legpts(hip, leg):
        k = pt(hip, leg[0], th); f = pt(k, leg[0] + leg[1], sh); return k, f
    hip = (MIDX, 30.0)
    if P['hip'] is None:
        low = max(max(p[1] + (1.5 if p is legpts(hip, l)[0] else 0) for p in legpts(hip, l)) for l in (P['fl'], P['bl']))
        hip = (MIDX, hip[1] + (GROUND - 2 - low) + P['dy'])
    else: hip = (MIDX + P['hip'][0], P['hip'][1] + P['dy'])
    lean = P['lean']
    neck = pt(hip, 180 - lean, tor)  # nach oben
    sho = pt(hip, 180 - lean, tor - 2)
    head = pt(neck, 180 - lean * .6, 6 if not dwarf else 6)
    P['_head'] = head

    # Umhang (hinter allem)
    cv = P['cape']  # -1 = hängt / weht nach hinten unten, +1 = weht nach oben (Fall)
    c0 = (sho[0] - 1, sho[1]); bx = -6 - abs(lean) * .12 - max(0, cv) * 3
    tip_y = hip[1] + 6 - cv * 9; tip_x = c0[0] + bx - (3 if cv > .3 else 0)
    wave = P.get('wave', 0)
    d.polygon([(c0[0] + 3, c0[1] - 1), (c0[0] - 3, c0[1] + 1), (tip_x - 3 + wave, tip_y), (tip_x + 2, tip_y + 1 + wave % 2), (hip[0] - 1, hip[1] + 2)], fill=cape_c)
    d.line([(c0[0] - 1, c0[1] + 2), (tip_x + wave * .5, tip_y - 1)], fill=cape_d)

    # Schwanz
    if race.get('tail'):
        t = race['tail']; tc = race.get('T', race.get('s')); base = (hip[0] - 3, hip[1] - 1)
        sway = P.get('wave', 0) * .5
        if t in ('buschig', 'echse'):
            end = (base[0] - 8, base[1] + (2 if t == 'echse' else -3) + sway)
            cap(d, base, end, 2.5 if t == 'buschig' else 2, race['s']); cap(d, ((base[0] + end[0]) / 2, (base[1] + end[1]) / 2), end, 1.5, tc)
        elif t in ('duenn', 'hund', 'quaste'):
            mid = (base[0] - 4, base[1] - 1 + sway); end = (base[0] - 6, base[1] - 6 + sway)
            cap(d, base, mid, 1, race['s']); cap(d, mid, end, 1, race['s'])
            if t == 'quaste': d.ellipse([end[0] - 2, end[1] - 2, end[0] + 1, end[1] + 1], fill=tc)
        elif t == 'puschel': d.ellipse([base[0] - 4, base[1] - 3, base[0], base[1] + 1], fill=race.get('t', WHITE))

    # Hinteres Bein & Arm
    def leg(lg, front):
        k, f = legpts(hip, lg); pc = pants if front else shade(pants, .75); bc = boots if front else shade(boots, .75)
        if armor: pc = STEEL_D if not front else shade(STEEL, .85)
        if front: cap(d, hip, k, 2.6, INK); cap(d, k, f, 2.6, INK)
        cap(d, hip, k, 1.6, pc); cap(d, k, f, 1.5, pc)
        bt = pt(k, lg[0] + lg[1], sh - 3); cap(d, bt, f, 1.6, bc)
        foot = (f[0] + 3 * math.cos(math.radians(lg[0] + lg[1])), f[1] - .5 + 3 * math.sin(math.radians(lg[0] + lg[1])) * .3)
        cap(d, f, foot, 1.2, bc)
    def arm(a, front):
        el = pt(sho, a[0], 5 if not dwarf else 4); hd = pt(el, a[0] + a[1], 5 if not dwarf else 4)
        sc = (STEEL if armor else body_c) if front else shade(STEEL if armor else body_c, .72)
        if front: cap(d, sho, el, 2.3, INK); cap(d, el, hd, 2.1, INK)
        cap(d, sho, el, 1.4, sc); cap(d, el, hd, 1.2, sc if not animal else sc)
        d.ellipse([hd[0] - 1.2, hd[1] - 1.2, hd[0] + 1.2, hd[1] + 1.2], fill=skin if front else skin_s)
        return hd, a[0] + a[1]
    leg(P['bl'], False); bh = arm(P['ba'], False)

    # Rumpf
    bw = 5 if not dwarf else 6
    perp = (math.cos(math.radians(lean)), math.sin(math.radians(lean)))
    def off(p, k): return (p[0] + perp[0] * k, p[1] - perp[1] * k * 0 + 0)
    poly = [off(sho, -bw + 1), off(sho, bw - 1), off(hip, bw - 1), off(hip, -bw + 1)]
    lo = pt(hip, -lean * 0 + 0, 3)  # Saum
    d.polygon(poly + [off(lo, -bw + 1)][:0], fill=body_c)
    d.polygon([off(hip, -bw), off(hip, bw), (off(hip, bw)[0] + 1, hip[1] + 3), (off(hip, -bw)[0] - 1, hip[1] + 3)], fill=body_d)
    d.line([off(pt(hip, 180 - lean, 2), -bw + 1), off(pt(hip, 180 - lean, 2), bw - 1)], fill=belt if not armor else C('#6a4a3a'))
    d.line([off(sho, bw - 2), off(hip, bw - 2)], fill=body_d)
    if armor:
        d.ellipse([sho[0] - 3, sho[1] - 2, sho[0] + 3, sho[1] + 3], fill=STEEL_L)
        d.line([off(pt(hip, 180 - lean, 6), -bw + 2), off(pt(hip, 180 - lean, 6), bw - 2)], fill=STEEL_D)
    else:
        d.line([(sho[0] - 1, sho[1]), (sho[0] + 2, sho[1] + 3)], fill=shade(body_c, .65))  # Kragen

    # Kopf
    hx, hy = head; R = 5.5 if not dwarf else 5.5
    ears = race.get('ears'); muz = race.get('muzzle')
    def ear_back():
        if ears == 'lang': cap(d, (hx - 2, hy - 4), (hx - 6, hy - 13), 1.6, skin); cap(d, (hx - 2, hy - 5), (hx - 5, hy - 11), .6, fp.get('y', skin))
        elif ears in ('spitz', 'katze', 'fuchs'):
            h_ = {'spitz': 7, 'katze': 6, 'fuchs': 8}[ears]
            d.polygon([(hx - 4, hy - 3), (hx - 3, hy - 3 - h_), (hx + 1, hy - 5)], fill=skin); d.polygon([(hx - 3, hy - 4), (hx - 3, hy - 1 - h_), (hx - 1, hy - 5)], fill=fp.get('y', skin))
        elif ears == 'rund': d.ellipse([hx - 5, hy - 8, hx - 1, hy - 4], fill=skin)
        elif ears == 'buschel': d.polygon([(hx - 3, hy - 4), (hx - 5, hy - 10), (hx, hy - 5)], fill=fp.get('X', skin))
        elif ears == 'hoerner': cap(d, (hx - 1, hy - 4), (hx - 5, hy - 8), 1.2, race['h']); cap(d, (hx - 5, hy - 8), (hx - 8, hy - 7), .8, race['h'])
        elif ears == 'kamm':
            for i in range(3): d.polygon([(hx - 4 + i * 2, hy - 4 + i), (hx - 6 + i * 2, hy - 8 + i * .5), (hx - 2 + i * 2, hy - 5 + i)], fill=fp.get('X', skin))
    ear_back()
    hair = race.get('hair')
    if hair and hair[0] == 'lang': cap(d, (hx - 3, hy - 2), (hx - 4, hy + 7), 2.6, shade(hair[1], .85))
    if muz == 'frosch': d.ellipse([hx - 6, hy - 4, hx + 7, hy + 5], fill=INK); d.ellipse([hx - 5, hy - 3, hx + 6, hy + 4], fill=skin)
    else: d.ellipse([hx - R - 1, hy - R - 1, hx + R + 1, hy + R + 1], fill=INK); d.ellipse([hx - R, hy - R, hx + R, hy + R], fill=skin)
    d.chord([hx - R, hy - R, hx + R, hy + R], 100, 200, fill=skin_s)
    if muz == 'lang':
        m = fp.get('m', skin); d.rounded_rectangle([hx + 2, hy, hx + 9, hy + 4], 2, fill=INK); d.rounded_rectangle([hx + 2, hy + .5, hx + 8.5, hy + 3.5], 1.5, fill=m)
        d.rectangle([hx + 8, hy, hx + 9, hy + 1], fill=fp.get('n', INK)); d.line([(hx + 5, hy + 3), (hx + 8, hy + 3)], fill=shade(m, .7))
    elif muz == 'kurz':
        m = fp.get('m', skin); d.ellipse([hx + 2, hy, hx + 7, hy + 4], fill=m); d.point((hx + 6.5, hy + 1), fill=fp.get('n', INK))
    elif muz == 'eule':
        d.ellipse([hx - 1, hy - 4, hx + 6, hy + 4], fill=fp.get('w', WHITE)); d.polygon([(hx + 5, hy), (hx + 8, hy + 1), (hx + 5, hy + 3)], fill=race.get('b', C('#e0a040')))
    elif muz == 'frosch':
        d.ellipse([hx, hy - 7, hx + 6, hy - 1], fill=INK); d.ellipse([hx + 1, hy - 6, hx + 5, hy - 2], fill=fp.get('w', WHITE))
        d.line([(hx + 1, hy + 2), (hx + 6, hy + 2)], fill=fp.get('n', INK))
    else:
        d.point((hx + R, hy + 1), fill=skin_s)  # Nase
    if ears == 'haengend': d.ellipse([hx - 5, hy - 4, hx - 1, hy + 5], fill=fp.get('X', skin))
    if ears == 'elf': d.polygon([(hx - 2, hy - 1), (hx - 9, hy - 5), (hx - 2, hy + 2)], fill=skin); d.line([(hx - 3, hy), (hx - 7, hy - 4)], fill=skin_s)
    if race.get('spots'):
        for p in ((hx - 2, hy - 3), (hx - 4, hy + 1), (hx + 1, hy - 4)): d.point(p, fill=race.get('z', skin_s))
    if hair:
        hc = hair[1]; d.chord([hx - R - 1, hy - R - 1, hx + R + 1, hy + R + 1], 150, 360, fill=hc)
        d.polygon([(hx - R, hy - 1), (hx - R - 1, hy + 3), (hx - 2, hy + 1)], fill=hc)
        d.line([(hx - 2, hy - R + 1), (hx + 2, hy - R)], fill=mix(hc, WHITE, .3))
    if dwarf:
        bc = hair[1]; d.polygon([(hx, hy + 1), (hx + 6, hy + 1), (hx + 5, hy + 7), (hx + 1, hy + 10), (hx - 1, hy + 5)], fill=bc)
        d.line([(hx + 2, hy + 4), (hx + 3, hy + 7)], fill=shade(bc, .8))
    # Auge
    ex, ey = (hx + 2, hy - 1) if muz != 'frosch' else (hx + 2, hy - 5)
    ec = race.get('E', race.get('e', g.EYE)) if muz != 'eule' else INK
    if muz == 'eule': ex, ey = hx + 2, hy - 1
    if P['eye'] == 'zu': d.line([(ex - 1, ey + 1), (ex + 1, ey + 1)], fill=INK)
    elif P['eye'] == 'au': d.line([(ex - 1, ey - 1), (ex + 1, ey + 1)], fill=INK); d.line([(ex - 1, ey + 1), (ex + 1, ey - 1)], fill=INK)
    else: d.rectangle([ex, ey - 1, ex + 1, ey + 1], fill=ec); d.point((ex + 1, ey - 1), fill=WHITE)

    # Vorderes Bein & Arm + Schwert
    leg(P['fl'], True)
    hd, ang = arm(P['fa'], True)
    P['_hand'], P['_hand_ang'] = hd, ang
    if P.get('item'): P['item'](im, d, hd, ang, P)  # Gegenstand in der vorderen Hand (siehe hero_items.py)
    if P['sword'] is not None:
        sa = P['sword']; tip = pt(hd, sa, 13); gd = pt(hd, sa, 2)
        cap(d, hd, pt(hd, sa + 180, 2), .7, C('#6a4a3a'))
        q = (math.cos(math.radians(sa)) * 2, -math.sin(math.radians(sa)) * 2)
        d.line([(gd[0] - q[0], gd[1] - q[1]), (gd[0] + q[0], gd[1] + q[1])], fill=C('#e0b048'), width=1)
        d.line([gd, tip], fill=STEEL_L, width=2); d.line([pt(hd, sa, 3), tip], fill=STEEL, width=1)
    im = g.outline(im)
    if P['flash']:
        px = im.load()
        for y in range(CS):
            for x in range(CS):
                c = px[x, y]
                if c[3]: px[x, y] = mix(c, WHITE, P['flash'])[:3] + (c[3],)
    return im

# ---------------------------------------------------------------- Effekte
def fx_slash(im, cx, cy, a0, a1, r, k):
    d = ImageDraw.Draw(im)
    for w_, col in ((3, SLASH[:3] + (140,)), (1, SLASH)):
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=col, width=w_)
    return im
def fx_lines(im, y0, y1, n=4, seed=0):
    d = ImageDraw.Draw(im)
    for i in range(n):
        y = y0 + (y1 - y0) * i / max(1, n - 1); x = 4 + (i * 7 + seed * 3) % 9
        d.line([(x, y), (x + 6 + i % 2 * 3, y)], fill=(240, 240, 255, 200))
    return im
def fx_dust(im, x, y, t):
    d = ImageDraw.Draw(im)
    for s in (-1, 1):
        cx = x + s * (3 + t * 3); r = max(0, 2 - t * .6)
        if r > 0: d.ellipse([cx - r, y - r - t, cx + r, y + r - t], fill=(220, 210, 200, 200 - t * 50))
    return im
def fx_focus(im, t):
    d = ImageDraw.Draw(im)
    for i in range(7):
        a = i / 7 * 2 * math.pi + t * .4; r = 15 - t * 2 + (i % 2)
        x, y = MIDX + math.cos(a) * r, 30 + math.sin(a) * r * .9
        d.point((x, y), fill=C('#8ad8ff') if i % 2 else WHITE)
    if t >= 4:
        d.ellipse([MIDX - 6, 22, MIDX + 6, 38], outline=(200, 240, 255, 160))
    return im
def fx_dissolve(im, k):
    px = im.load()
    for y in range(CS):
        for x in range(CS):
            if px[x, y][3] and ((x * 7 + y * 13) % 10) / 10 < k: px[x, y] = (0, 0, 0, 0)
    return im
def fx_hit(im):
    d = ImageDraw.Draw(im)
    for a in range(0, 360, 45):
        r = math.radians(a); d.line([(30 + math.cos(r) * 4, 24 + math.sin(r) * 4), (30 + math.cos(r) * 8, 24 + math.sin(r) * 8)], fill=WHITE)
    return im

# ---------------------------------------------------------------- Animationen
def anims(race, outfit):
    D = lambda **k: draw(race, outfit, pose(**k))
    A = {}
    A['stehen'] = [D(dy=[0, 0, 1, 1, 1, 0][i], fl=(4, -4), bl=(-4, -2), fa=(4, 14), ba=(-6, 16), eye='zu' if i == 4 else 'auf', wave=[0, 1, 1, 0, -1, -1][i]) for i in range(6)]
    run = []
    for i in range(8):
        p = i / 8 * 2 * math.pi
        f = (40 * math.sin(p), -10 - 70 * max(0, math.cos(p))); b = (40 * math.sin(p + math.pi), -10 - 70 * max(0, math.cos(p + math.pi)))
        im = D(lean=14, fl=f, bl=b, fa=(-45 * math.sin(p), 70), ba=(45 * math.sin(p), 70), dy=-1 if abs(math.cos(p)) > .8 else 0, cape=.2, wave=[0, 1, 2, 1, 0, 1, 2, 1][i])
        run.append(im)
    A['rennen'] = run
    A['sprung_start'] = [D(dy=2, fl=(40, -80), bl=(20, -70), fa=(-20, 40), ba=(-30, 40)), D(lean=6, fl=(-5, 0), bl=(-25, -10), fa=(150, 20), ba=(120, 20), cape=-.3)]
    A['sprung_auf'] = [D(hip=(0, 26), fl=(55, -70), bl=(-15, -50), fa=(160, 10), ba=(130, 30), cape=-.6, wave=i) for i in range(2)]
    A['scheitel'] = [D(hip=(0, 27), fl=(40, -60), bl=(10, -70), fa=(100, 30), ba=(80, 30), cape=.2 + i * .2, wave=i) for i in range(2)]
    A['fallen'] = [D(hip=(0, 27), fl=(15, -20), bl=(-15, -30), fa=(140, 0), ba=(-140, 0), cape=.9, wave=i * 2) for i in range(2)]
    land = []
    for i, (dy, k) in enumerate(((4, 90), (2, 60), (0, 10))):
        im = D(dy=0, fl=(k * .8, -k * 1.5), bl=(k * .4, -k * 1.3), fa=(30, 30), ba=(-20, 30), lean=k * .15)
        if i < 2: fx_dust(im, MIDX, GROUND - 1, i)
        land.append(im)
    A['landen'] = land
    dash = []
    for i in range(4):
        im = D(lean=40, fl=(30, -40), bl=(-60, -10), fa=(-80, 20), ba=(-100, 20), cape=.6, wave=i, hip=(0, 30))
        fx_lines(im, 18, 36, 4, i); dash.append(im)
    A['dash'] = dash
    A['wand_rutschen'] = [D(hip=(-2, 28 + i), lean=-8, fl=(50, -90), bl=(10, -60), fa=(150, -30), ba=(120, -40), cape=.3, wave=i) for i in range(2)]
    for im in A['wand_rutschen']: fx_dust(im, 34, 20 + 6 * A['wand_rutschen'].index(im), 1)
    A['wandsprung'] = [D(hip=(0, 28), lean=-10, fl=(-20, -30), bl=(-50, -30), fa=(-120, 20), ba=(-150, 20), cape=.4),
                       D(hip=(0, 26), lean=10, fl=(50, -70), bl=(-10, -50), fa=(160, 10), ba=(120, 20), cape=-.4),
                       D(hip=(0, 26), lean=5, fl=(40, -60), bl=(0, -60), fa=(120, 20), ba=(100, 20), cape=-.2)]
    # Angriffe
    vo = []
    for i, (fa, sw, ln) in enumerate((((-150, 20), -160, -6), ((170, 10), 170, 0), ((100, 0), 95, 10), ((70, 0), 60, 14), ((40, 20), 40, 6))):
        im = D(lean=ln, fl=(25, -30), bl=(-25, -15), fa=fa, ba=(-40, 40), sword=sw, cape=.2)
        if i in (2, 3): fx_slash(im, 26, 22, -70 if i == 2 else -60, 50 if i == 2 else 70, 16, i)
        vo.append(im)
    A['angriff_vorne'] = vo
    ob = []
    for i, (fa, sw) in enumerate((((60, 20), 60), ((120, 10), 120), ((170, 0), 175), ((-160, 0), -150), ((140, 20), 150))):
        im = D(fl=(15, -20), bl=(-15, -15), fa=fa, ba=(-30, 30), sword=sw, cape=0, lean=-4)
        if i in (2, 3): fx_slash(im, 24, 18, 200 if i == 2 else 210, 340 if i == 2 else 330, 15, i)
        ob.append(im)
    A['angriff_oben'] = ob
    un = []
    for i, (fa, sw) in enumerate((((140, 10), 160), ((60, 10), 40), ((20, 0), 10), ((-20, 0), -15), ((40, 20), 20))):
        im = D(hip=(0, 24), fl=(50, -90), bl=(20, -80), fa=fa, ba=(-60, 40), sword=sw, cape=.5)
        if i in (2, 3): fx_slash(im, 24, 34, 20 if i == 2 else 30, 160 if i == 2 else 150, 13, i)
        un.append(im)
    A['angriff_unten'] = un
    A['treffer'] = [D(lean=-20, fl=(-10, -20), bl=(-35, -10), fa=(-60, 40), ba=(-80, 40), eye='au', flash=.8, cape=.4),
                    D(lean=-15, fl=(-10, -20), bl=(-30, -10), fa=(-50, 40), ba=(-70, 40), eye='au', cape=.3),
                    D(lean=-6, fl=(0, -10), bl=(-15, -10), fa=(-10, 30), ba=(-30, 30), cape=.1)]
    fx_hit(A['treffer'][0])
    tod = [D(lean=-20, fl=(-10, -20), bl=(-35, -10), fa=(-60, 40), ba=(-80, 40), eye='au', flash=.8),
           D(lean=10, fl=(25, -105), bl=(15, -100), fa=(20, 10), ba=(10, 10), eye='au'),
           D(lean=30, fl=(25, -105), bl=(15, -100), fa=(5, 0), ba=(0, 0), eye='zu')]
    lie = D(fl=(5, -5), bl=(-5, 0), fa=(10, 10), ba=(-5, 5), eye='zu').rotate(-85, resample=Image.NEAREST, center=(MIDX, GROUND - 4)); b = lie.getbbox()
    lying = Image.new('RGBA', (CS, CS)); lying.alpha_composite(lie.crop(b), (max(0, (CS - (b[2] - b[0])) // 2), GROUND - (b[3] - b[1])))
    tod += [lying, fx_dissolve(lying.copy(), .45), fx_dissolve(lying.copy(), .8)]
    A['tod'] = tod
    heal = []
    for i in range(6):
        im = D(dy=1 if i else 0, fl=(30, -60), bl=(10, -50), fa=(80, 120), ba=(70, 120), eye='zu' if 1 <= i <= 4 else 'auf', cape=-.2)
        fx_focus(im, i); heal.append(im)
    A['heilen'] = heal
    A['ducken'] = [D(fl=(70, -130), bl=(50, -120), fa=(40, 40), ba=(20, 40), lean=15, cape=-.4)]
    return A

ORDER = ['stehen', 'rennen', 'sprung_start', 'sprung_auf', 'scheitel', 'fallen', 'landen', 'dash', 'wand_rutschen', 'wandsprung',
         'angriff_vorne', 'angriff_oben', 'angriff_unten', 'treffer', 'tod', 'heilen', 'ducken']
FPS = {'stehen': 6, 'rennen': 12, 'dash': 16, 'angriff_vorne': 16, 'angriff_oben': 16, 'angriff_unten': 16, 'tod': 8, 'heilen': 8}

def job(args):
    ri, outfit = args; race = rc.RACES[ri]; A = anims(race, outfit)
    cols = max(len(v) for v in A.values()); s = Image.new('RGBA', (CS * cols, CS * len(ORDER)))
    for r, n in enumerate(ORDER):
        for c, f in enumerate(A[n]): s.alpha_composite(f, (c * CS, r * CS))
    s.save(os.path.join(OUT, f'{race["name"]}_{outfit}.png'))
    return race['name'], outfit, {n: len(A[n]) for n in ORDER}

def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [(i, o) for i in range(len(rc.RACES)) for o in rc.OUTFITS]
    with Pool(4) as p: res = p.map(job, jobs)
    meta = {'zelle': CS, 'boden_y': GROUND, 'mitte_x': MIDX, 'zeilen': ORDER, 'frames': res[0][2], 'fps': {n: FPS.get(n, 10) for n in ORDER},
            'dateien': [f'{a}_{b}.png' for a, b, _ in res], 'hinweis': 'Blick nach rechts. Schleifen: stehen, rennen, fallen, dash, wand_rutschen, heilen.'}
    json.dump(meta, open(os.path.join(OUT, 'held.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview()

def cut(name, outfit, anim, i):
    s = Image.open(os.path.join(OUT, f'{name}_{outfit}.png')); r = ORDER.index(anim)
    return s.crop((i * CS, r * CS, (i + 1) * CS, (r + 1) * CS))

def preview():
    meta = json.load(open(os.path.join(OUT, 'held.json'), encoding='utf-8')); nf = meta['frames']
    # 1: alle Animationen eines Helden (Mensch, Tunika + Zwerg in Rüstung)
    Z = 3; who = [('mensch', 'tunika'), ('fuchs', 'ruestung')]; cols = 6
    cw, chh = CS * Z, CS * Z + 16; rows = math.ceil(len(ORDER) / cols) * len(who)
    frames = []
    for t in range(16):
        im = Image.new('RGB', (cols * cw + 8, rows * chh + 8), (42, 36, 69)); d = ImageDraw.Draw(im)
        for wi, (n, o) in enumerate(who):
            for i, a in enumerate(ORDER):
                r = wi * math.ceil(len(ORDER) / cols) + i // cols; x, y = 4 + (i % cols) * cw, 4 + r * chh
                d.rectangle([x, y, x + cw - 3, y + CS * Z - 1], fill=(74, 62, 88)); d.line([(x, y + GROUND * Z), (x + cw - 3, y + GROUND * Z)], fill=(110, 96, 120), width=2)
                c = cut(n, o, a, t % nf[a]).resize((CS * Z, CS * Z), Image.NEAREST); im.paste(c, (x, y), c)
                d.text((x + 3, y + CS * Z + 1), a, fill=(230, 220, 200), font=g.font(11))
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_held.gif'), save_all=True, append_images=frames[1:], duration=110, loop=0)
    # 2: alle Völker rennen + greifen an
    Z = 2; names = [r['name'] for r in rc.RACES]; frames = []
    for t in range(16):
        im = Image.new('RGB', (7 * CS * Z + 8, 4 * CS * Z + 8), (42, 36, 69))
        for i, n in enumerate(names):
            for k, (o, a) in enumerate((('tunika', 'rennen'), ('ruestung', 'angriff_vorne'))):
                x = 4 + (i % 7) * CS * Z; y = 4 + ((i // 7) * 2 + k) * CS * Z
                c = cut(n, o, a, t % nf[a]).resize((CS * Z, CS * Z), Image.NEAREST); im.paste(c, (x, y), c)
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_held_voelker.gif'), save_all=True, append_images=frames[1:], duration=90, loop=0)

if __name__ == '__main__':
    main()
