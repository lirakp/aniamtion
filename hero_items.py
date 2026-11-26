"""Benutz-Animationen für den großen Helden: Tränke trinken, essen, werfen, Schriftrolle lesen, Item aufheben,
pflücken und Werkzeuge (Spitzhacke, Axt, Schaufel, Sichel, Gießkanne, Angel).
Aufruf: python3 hero_items.py
Ausgabe: characters/held/items/<volk>_<kleidung>.png (Zeile = Animation, Zelle 48x48 wie held/),
         characters/held/items/held_items.json, preview_held_items.gif
Blick nach rechts. Gleiche Zelle, Bodenlinie (y=46) und Mitte (x=24) wie characters/held/.
"""
import os, json, math
from PIL import Image, ImageDraw
from multiprocessing import Pool
import generate as g
from generate import C, shade, mix
import races as rc
import hero as hr

OUT = os.path.join(g.BASE, 'characters', 'held', 'items')
CS = hr.CS
WOOD, WOOD_D = g.WOOD, g.WOOD_D
STEEL, STEEL_L = C('#a8acbc'), C('#e0e4ee')
GLASS = C('#c8e0ee'); WHITE = C('#ffffff')
HEIL, MANA = C('#e0443a'), C('#4a8ae0')

# ---------------------------------------------------------------- Gegenstände (Griff in der Bildmitte, zeigt nach OBEN)
def canvas(s): im = Image.new('RGBA', (s, s)); return im, ImageDraw.Draw(im), s // 2
def spr_flasche(col):
    im, d, c = canvas(14)
    d.ellipse([c - 3, c - 2, c + 3, c + 4], fill=GLASS); d.ellipse([c - 2, c, c + 2, c + 3], fill=col)
    d.rectangle([c - 1, c - 5, c, c - 2], fill=GLASS); d.rectangle([c - 1, c - 6, c, c - 6], fill=WOOD); d.point((c - 2, c), fill=WHITE)
    return im
def spr_apfel(biss):
    im, d, c = canvas(12)
    d.ellipse([c - 3, c - 3, c + 3, c + 3], fill=C('#d8403a')); d.point((c - 1, c - 1), fill=C('#ff9a8a')); d.line([(c, c - 3), (c, c - 5)], fill=WOOD_D); d.point((c + 1, c - 5), fill=g.LEAF)
    for k in range(biss): d.ellipse([c + 1 - k * 2, c - 2 + k, c + 5 - k * 2, c + 2 + k], fill=(0, 0, 0, 0))
    if biss: d.point((c + 1 - (biss - 1) * 2, c), fill=C('#f8f0d0'))
    return im
def spr_rolle(offen):
    im, d, c = canvas(18)
    if offen:
        d.rectangle([c - 6, c - 4, c + 6, c + 3], fill=C('#f0e4cc')); d.rectangle([c - 7, c - 5, c - 6, c + 4], fill=C('#d8c8a8')); d.rectangle([c + 6, c - 5, c + 7, c + 4], fill=C('#d8c8a8'))
        for y in (c - 2, c, c + 2): d.line([(c - 4, y), (c + 4, y)], fill=C('#a89878'))
    else:
        d.rectangle([c - 1, c - 5, c + 1, c + 5], fill=C('#f0e4cc')); d.rectangle([c - 1, c - 1, c + 1, c], fill=C('#c83a3a'))
    return im
def spr_juwel():
    im, d, c = canvas(12)
    d.polygon([(c - 3, c - 2), (c + 3, c - 2), (c + 4, c), (c, c + 5), (c - 4, c)], fill=C('#b880ff')); d.polygon([(c - 3, c - 2), (c + 3, c - 2), (c + 3, c), (c - 3, c)], fill=C('#e0d0ff'))
    d.point((c - 2, c - 1), fill=WHITE)
    return im
def spr_beere():
    im, d, c = canvas(8); d.rectangle([c - 1, c - 1, c, c], fill=C('#d8403a')); d.point((c - 1, c - 1), fill=C('#ff9a8a')); return im
def spr_spitzhacke():
    im, d, c = canvas(30)
    d.line([(c, c + 3), (c, c - 10)], fill=WOOD, width=2); d.arc([c - 8, c - 13, c + 8, c - 5], 190, 350, fill=STEEL, width=2); d.point((c + 7, c - 9), fill=STEEL_L)
    return im
def spr_axt():
    im, d, c = canvas(30)
    d.line([(c, c + 3), (c, c - 10)], fill=WOOD, width=2); d.polygon([(c + 1, c - 11), (c + 6, c - 12), (c + 7, c - 6), (c + 1, c - 7)], fill=STEEL); d.line([(c + 6, c - 12), (c + 7, c - 6)], fill=STEEL_L)
    return im
def spr_schaufel(erde=False):
    im, d, c = canvas(30)
    d.line([(c, c + 4), (c, c - 9)], fill=WOOD, width=2); d.line([(c - 2, c + 4), (c + 2, c + 4)], fill=WOOD)
    d.polygon([(c - 3, c - 9), (c + 3, c - 9), (c + 2, c - 14), (c, c - 15), (c - 2, c - 14)], fill=STEEL); d.line([(c + 2, c - 9), (c + 2, c - 13)], fill=STEEL_L)
    if erde: d.ellipse([c - 3, c - 15, c + 3, c - 11], fill=C('#7a5a3e'))
    return im
def spr_sichel():
    im, d, c = canvas(24)
    d.line([(c, c + 3), (c, c - 3)], fill=WOOD, width=2); d.arc([c - 1, c - 11, c + 9, c - 1], 150, 330, fill=STEEL_L, width=2)
    return im
def spr_kanne():
    im, d, c = canvas(22)
    d.rectangle([c - 3, c - 2, c + 3, c + 4], fill=C('#7a9ab0')); d.line([(c + 3, c), (c + 8, c - 4)], fill=C('#7a9ab0'), width=2); d.arc([c - 5, c - 4, c + 1, c + 3], 90, 270, fill=C('#5a7a90'))
    d.line([(c - 3, c - 2), (c + 3, c - 2)], fill=C('#a8c8e0'))
    return im
def spr_angel():
    im, d, c = canvas(46)
    d.line([(c, c + 3), (c, c - 20)], fill=WOOD); d.line([(c + 1, c + 3), (c + 1, c - 6)], fill=WOOD_D); d.ellipse([c - 2, c, c + 1, c + 3], fill=C('#8a8296'))
    return im

def place(im, spr, at, a):
    """spr mit Griff (Mitte) an Punkt at, gedreht in Richtung a (0 = unten, 90 = vorne, 180 = oben)."""
    s = spr.width; r = spr.rotate(a - 180, resample=Image.NEAREST, center=(s / 2, s / 2))
    lay = Image.new('RGBA', im.size); lay.paste(r, (int(round(at[0] - s / 2)), int(round(at[1] - s / 2))), r); im.alpha_composite(lay)
def tip(at, a, L): return hr.pt(at, a, L)

def holding(spr, a=None, off=(0, 0)):
    def f(im, d, hd, ang, P):
        place(im, spr, (hd[0] + off[0], hd[1] + off[1]), ang if a is None else a)
    return f

# ---------------------------------------------------------------- Effekte
def funkeln(im, pts, col):
    d = ImageDraw.Draw(im)
    for x, y in pts:
        d.point((x, y), fill=WHITE); d.point((x - 1, y), fill=col); d.point((x + 1, y), fill=col); d.point((x, y - 1), fill=col); d.point((x, y + 1), fill=col)
def aufsteigen(im, col, t, n=6, sym='plus'):
    d = ImageDraw.Draw(im)
    for i in range(n):
        x = 14 + (i * 7) % 22; y = 40 - ((t * 5 + i * 9) % 30)
        if sym == 'plus': d.line([(x - 1, y), (x + 1, y)], fill=col); d.line([(x, y - 1), (x, y + 1)], fill=col)
        else: d.point((x, y), fill=col)
def krumen(im, at, t, col):
    d = ImageDraw.Draw(im)
    for i in range(3): d.point((at[0] + i - 1 + t, at[1] + 2 + t * 2 + i), fill=col)
def spritzer(im, at, t, col, n=4):
    d = ImageDraw.Draw(im)
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) * .7; r = 2 + t * 2
        d.point((at[0] + math.cos(a) * r, at[1] + math.sin(a) * r), fill=col)
def strahlen(im, c, t):
    d = ImageDraw.Draw(im)
    for k in range(8):
        a = k / 8 * 2 * math.pi + t * .2; r0, r1 = 7, 10 + (t % 2)
        d.line([(c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0), (c[0] + math.cos(a) * r1, c[1] + math.sin(a) * r1)], fill=C('#fff0a0'))

# ---------------------------------------------------------------- Animationen
STAND = dict(fl=(4, -4), bl=(-4, -2), ba=(-6, 16))
def anims(race, outfit):
    def D(**k):
        P = hr.pose(**{**STAND, **k}); im = hr.draw(race, outfit, P); return im, P
    A = {}
    # --- Trinken (Heiltrank / Manatrank)
    for name, col in (('trinken_heil', HEIL), ('trinken_mana', MANA)):
        fl = spr_flasche(col); seq = [((30, 60), 180, 0), ((70, 60), 190, 0), ((100, 80), 215, -3), ((100, 80), 250, -6), ((100, 80), 265, -7),
                                      ((100, 80), 250, -5), ((40, 60), 180, 0), ((4, 14), None, 0)]
        fr = []
        for i, (fa, ia, ln) in enumerate(seq):
            im, P = D(fa=fa, lean=ln, eye='zu' if 3 <= i <= 4 else 'auf', item=holding(fl, ia) if ia is not None else None)
            if i >= 5: aufsteigen(im, col, i, 6)
            if i == 7: funkeln(im, [(16, 18), (32, 24)], mix(col, WHITE, .4))
            fr.append(im)
        A[name] = fr
    # --- Essen
    fr = []
    for i, (fa, b) in enumerate((((30, 60), 0), ((80, 70), 0), ((100, 80), 1), ((100, 80), 1), ((100, 80), 2), ((100, 80), 3), ((60, 60), 3), ((4, 14), None))):
        im, P = D(fa=fa, eye='zu' if i in (3, 5) else 'auf', dy=1 if i in (3, 5) else 0, item=holding(spr_apfel(b), 180) if b is not None else None)
        if i in (3, 5): krumen(im, (P['_hand'][0], P['_hand'][1]), 0, C('#f8f0d0'))
        if i == 7: aufsteigen(im, C('#8ae06a'), i, 4)
        fr.append(im)
    A['essen'] = fr
    # --- Werfen (Wurftrank)
    fl = spr_flasche(C('#ff8a3a')); fr = []
    for i, fa in enumerate(((30, 60), (-150, 20), (170, 0), (100, 0), (60, 20), (20, 30))):
        im, P = D(fa=fa, fl=(25, -30), bl=(-25, -15), lean=[0, -8, -4, 10, 12, 4][i], item=holding(fl, None) if i <= 2 else None, cape=.2)
        if i >= 3:
            x, y = 32 + (i - 3) * 6, 18 + (i - 3) ** 2; place(im, fl, (x, y), 90 + i * 90)
            hr.fx_lines(im, y - 2, y + 2, 2, i) if i == 3 else None
        fr.append(im)
    A['werfen'] = fr
    # --- Schriftrolle lesen
    fr = []
    for i in range(8):
        offen = 1 <= i <= 5
        def rolle_item(im_, d_, hd, ang, P, offen=offen, i=i):
            if i == 6:
                return
            place(im_, spr_rolle(offen), (hd[0] + (3 if offen else 0), hd[1] - (2 if offen else 0)), 180)
        im, P = D(fa=(40, 60) if not offen else (60, 70), ba=(60, 70) if offen else STAND['ba'], item=rolle_item if i <= 5 else None)
        if 3 <= i <= 5:
            d = ImageDraw.Draw(im); hx, hy = P['_hand']
            for k in range(3): d.point((hx + 1 + k * 2, hy - 3 + (k + i) % 3), fill=C('#b880ff'))
            aufsteigen(im, C('#d8c8ff'), i, 5, 'punkt')
        if i >= 6: funkeln(im, [(28 + (i - 6) * 3, 22 - (i - 6) * 4), (22, 18 - (i - 6) * 3)], C('#b880ff'))
        fr.append(im)
    A['schriftrolle'] = fr
    # --- Aufheben + hochhalten
    fr = []; ju = spr_juwel()
    seq = [dict(fa=(20, 30)), dict(fl=(70, -130), bl=(50, -120), lean=25, fa=(50, 10)), dict(fl=(70, -130), bl=(50, -120), lean=25, fa=(45, 5)),
           dict(fl=(30, -50), bl=(20, -40), lean=10, fa=(80, 60)), dict(fa=(170, 10), ba=(-170, -10)), dict(fa=(170, 10), ba=(-170, -10), dy=-1),
           dict(fa=(170, 10), ba=(-170, -10)), dict(fa=(170, 10), ba=(-170, -10), dy=-1)]
    for i, k in enumerate(seq):
        it = None if i < 2 else holding(ju, 180, (0, -4) if i >= 4 else (0, 0))
        im, P = D(**k, item=it)
        if i < 2: place(im, ju, (36, 43), 180)
        if i >= 4: strahlen(im, (P['_hand'][0], P['_hand'][1] - 4), i)
        fr.append(im)
    A['aufheben'] = fr
    # --- Pflücken
    fr = []
    for i, (fa, has) in enumerate((((60, 40), False), ((85, 5), False), ((90, 0), True), ((60, 60), True), ((-10, 40), True), ((4, 14), False))):
        im, P = D(fa=fa, lean=8 if i in (1, 2) else 0, item=holding(spr_beere(), 180) if has else None)
        if i == 2: d = ImageDraw.Draw(im); d.point((40, 26), fill=g.LEAF_L); d.point((42, 30), fill=g.LEAF)
        if i == 5: funkeln(im, [(18, 30)], C('#ffd27a'))
        fr.append(im)
    A['pfluecken'] = fr
    # --- Werkzeuge: schlagende Bewegung
    def schlag(spr, col, L):
        fr = []
        for i, (fa, ln) in enumerate((((-150, 20), -6), ((-160, 10), -8), ((170, 0), -2), ((120, 0), 6), ((70, 0), 14), ((60, 10), 14), ((60, 20), 8), ((20, 40), 0))):
            im, P = D(fa=fa, lean=ln, fl=(25, -30), bl=(-25, -15), dy=1 if i in (4, 5) else 0, item=holding(spr), cape=.2)
            if i in (4, 5):
                t_ = tip(P['_hand'], P['_hand_ang'], L); spritzer(im, (min(46, t_[0]), min(45, t_[1])), i - 4, col, 5)
            fr.append(im)
        return fr
    A['spitzhacke'] = schlag(spr_spitzhacke(), C('#ffd27a'), 11)
    A['holz_hacken'] = schlag(spr_axt(), C('#e0c090'), 10)
    # --- Graben
    fr = []
    for i, (fa, ia, erde, ln) in enumerate((((60, 40), 30, False, 6), ((50, 30), 20, False, 10), ((40, 20), 15, False, 12), ((50, 40), 25, True, 10),
                                           ((80, 60), 120, True, 0), ((120, 40), 170, False, -6), ((60, 40), 60, False, 4), ((40, 50), 40, False, 4))):
        im, P = D(fa=fa, lean=ln, fl=(25, -30), bl=(-25, -15), item=holding(spr_schaufel(erde), ia))
        if i == 2: spritzer(im, (38, 44), 1, C('#7a5a3e'), 5)
        if i in (5, 6): d = ImageDraw.Draw(im); [d.point((20 - k * 3 - (i - 5) * 4, 14 + k * 2 + (i - 5) * 5), fill=C('#7a5a3e')) for k in range(4)]
        fr.append(im)
    A['graben'] = fr
    # --- Sichel
    fr = []
    for i, (fa, ln) in enumerate((((-40, 40), 4), ((20, 40), 14), ((70, 20), 18), ((110, 10), 12), ((120, 20), 4), ((20, 40), 0))):
        im, P = D(fa=fa, lean=ln, fl=(45, -80), bl=(10, -60), item=holding(spr_sichel()), cape=-.2)
        if i in (2, 3): d = ImageDraw.Draw(im); [d.line([(32 + k * 4, 40 - k), (33 + k * 4, 37 - k - (i - 2) * 2)], fill=g.LEAF_L) for k in range(3)]
        fr.append(im)
    A['sicheln'] = fr
    # --- Gießen
    fr = []
    for i, ia in enumerate((180, 170, 140, 120, 120, 170)):
        im, P = D(fa=(70, 40), item=holding(spr_kanne(), ia))
        if ia <= 140:
            t_ = tip(P['_hand'], ia - 52, 9); d = ImageDraw.Draw(im)
            for k in range(4): d.point((t_[0] + 2 + k % 2, t_[1] + 3 + k * 3 + (i % 2)), fill=C('#8ad0ff'))
        fr.append(im)
    A['giessen'] = fr
    # --- Angeln (auswerfen, warten, Biss)
    fr = []; rod = spr_angel()
    for i, (fa, ia) in enumerate((((-150, 20), 200), ((170, 0), 175), ((110, 0), 120), ((80, 40), 140), ((80, 40), 140), ((80, 40), 140), ((70, 40), 125), ((150, 0), 165))):
        im, P = D(fa=fa, lean=[-6, -2, 8, 0, 0, 0, 6, -4][i], item=holding(rod, ia))
        t_ = tip(P['_hand'], ia, 20)
        if i >= 3:
            d = ImageDraw.Draw(im); by = 44 + (i % 2) * (i < 6) + (2 if i == 6 else 0)
            d.line([t_, (46, by)], fill=C('#e8e0d0')); d.point((46, by - 1), fill=C('#e84a3a'))
            if i == 6: spritzer(im, (46, 45), 1, C('#8ac0f0'), 4)
        if i == 7: funkeln(im, [(t_[0] + 2, t_[1] + 4)], C('#8ac0f0')); place(im, spr_beere().resize((8, 8)), (t_[0] + 1, t_[1] + 6), 0)
        fr.append(im)
    A['angeln'] = fr
    return A

ORDER = ['trinken_heil', 'trinken_mana', 'essen', 'werfen', 'schriftrolle', 'aufheben', 'pfluecken', 'spitzhacke', 'holz_hacken', 'graben', 'sicheln', 'giessen', 'angeln']
FPS = {'trinken_heil': 10, 'trinken_mana': 10, 'essen': 9, 'werfen': 14, 'schriftrolle': 9, 'aufheben': 10, 'pfluecken': 12,
       'spitzhacke': 14, 'holz_hacken': 14, 'graben': 12, 'sicheln': 14, 'giessen': 8, 'angeln': 8}

def job(args):
    ri, outfit = args; race = rc.RACES[ri]; A = anims(race, outfit)
    cols = max(len(v) for v in A.values()); s = Image.new('RGBA', (CS * cols, CS * len(ORDER)))
    for r, n in enumerate(ORDER):
        for c, f in enumerate(A[n]): s.alpha_composite(f, (c * CS, r * CS))
    s.save(os.path.join(OUT, f'{race["name"]}_{outfit}.png'))
    return {n: len(A[n]) for n in ORDER}

def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [(i, o) for i in range(len(rc.RACES)) for o in rc.OUTFITS]
    with Pool(4) as p: res = p.map(job, jobs)
    json.dump({'zelle': CS, 'boden_y': hr.GROUND, 'mitte_x': hr.MIDX, 'zeilen': ORDER, 'frames': res[0], 'fps': FPS,
               'hinweis': 'Ergänzt characters/held/ (gleiches Raster). Einmal abspielen, danach zurück zu "stehen". Bei "aufheben" können Frames 4–7 als Schleife "Item hochhalten" genutzt werden. Angeln: Frames 3–5 loopen beim Warten, 6 = Biss, 7 = Fang.',
               'dateien': [f'{rc.RACES[i]["name"]}_{o}.png' for i, o in jobs]},
              open(os.path.join(OUT, 'held_items.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    preview(res[0])

def preview(nf):
    Z = 3; cols = 5; who = [('mensch', 'tunika'), ('katze', 'ruestung')]
    rows_per = math.ceil(len(ORDER) / cols); cw, chh = CS * Z, CS * Z + 16; frames = []
    sheets = {w: Image.open(os.path.join(OUT, f'{w[0]}_{w[1]}.png')) for w in who}
    for t in range(16):
        im = Image.new('RGB', (cols * cw + 8, rows_per * len(who) * chh + 8), (42, 36, 69)); d = ImageDraw.Draw(im)
        for wi, w in enumerate(who):
            for i, a in enumerate(ORDER):
                r = wi * rows_per + i // cols; x, y = 4 + (i % cols) * cw, 4 + r * chh
                d.rectangle([x, y, x + cw - 3, y + CS * Z - 1], fill=(74, 62, 88)); d.line([(x, y + hr.GROUND * Z), (x + cw - 3, y + hr.GROUND * Z)], fill=(110, 96, 120), width=2)
                k = t % nf[a]; c = sheets[w].crop((k * CS, ORDER.index(a) * CS, (k + 1) * CS, (ORDER.index(a) + 1) * CS)).resize((CS * Z, CS * Z), Image.NEAREST)
                im.paste(c, (x, y), c); d.text((x + 3, y + CS * Z + 1), a, fill=(230, 220, 200), font=g.font(11))
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_held_items.gif'), save_all=True, append_images=frames[1:], duration=130, loop=0)

if __name__ == '__main__':
    main()
