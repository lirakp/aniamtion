"""Animierte, freistehende Spielobjekte: Wasserfall + Dungeon-Tür (schwarzer Stein).
Aufruf: python3 objects.py
Ausgabe in objects/ (+ preview_objekte.gif), Kollisionsdaten in objects/objekte.json
"""
import os, math, json, random
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'objects')
WHITE = (255, 255, 255, 255)

# ================================================================ WASSERFALL
ROCK, ROCK_L, ROCK_D = C('#5a5670'), C('#7a7690'), C('#3e3a52')
MOSS, MOSS_L = C('#4f7a45'), C('#6e9e58')
WAT, WAT_L, WAT_D, FOAM = C('#4a8ac8'), C('#8ac4ee'), C('#3a6aa8'), C('#e8f6ff')
WF_W, WF_H, X0 = 70, 88, 3
BOULDERS = [(14, 14, 10), (30, 8, 9), (48, 13, 10), (8, 30, 8), (56, 30, 8), (12, 46, 10), (52, 46, 10),
            (20, 28, 9), (44, 28, 9), (10, 58, 7), (54, 58, 7),
            (22, 44, 9), (42, 44, 9), (4, 44, 6), (60, 44, 6), (32, 20, 8), (18, 56, 7), (46, 56, 7)]
POOL_CX, POOL_CY, POOL_RX, POOL_RY = 32 + X0, 73, 28, 9

def _wob(y, a):  # unregelmäßige Wasserkante (statisch)
    return round(math.sin(y*0.7 + a) * .8 + math.sin(y*0.23 + a*2) * .6)

def water_x(y):
    l, r = 22 + X0 + _wob(y, 1), 41 + X0 + _wob(y, 4)
    if y > 54: l -= (y-54)//3; r += (y-54)//3
    return l, r

def waterfall(t):
    img, px = g.new(WF_W, WF_H)
    rng = random.Random(7)
    def S(x, y, c):
        if 0 <= x < WF_W and 0 <= y < WF_H: px[x, y] = c
    # Felsen
    for (bx, by, r) in BOULDERS:
        bx += X0
        for y in range(by-r, by+r+1):
            for x in range(bx-r, bx+r+1):
                d = math.hypot(x-bx, y-by)
                if d > r: continue
                lv = math.hypot(x-(bx-r*.4), y-(by-r*.4)) / r
                c = ROCK_L if lv < .55 else ROCK if lv < 1.05 else ROCK_D
                if d > r-1.2 and (x-bx) + (y-by) > 0: c = ROCK_D
                S(x, y, c)
    src = img.copy().load()
    for y in range(1, 52):
        for x in range(WF_W):
            if src[x, y][3] and not src[x, y-1][3]:
                S(x, y, MOSS_L); S(x, y+1, MOSS if rng.random() < .7 else src[x, y+1])
    # Becken mit Steinrand
    for y in range(POOL_CY-POOL_RY-3, POOL_CY+POOL_RY+4):
        for x in range(POOL_CX-POOL_RX-4, POOL_CX+POOL_RX+5):
            e = math.hypot((x-POOL_CX)/POOL_RX, (y-POOL_CY)/POOL_RY)
            if e <= 1:
                c = WAT if e < .8 else WAT_D
                if .25 < e < .92 and ((e*12 - t*.75) % 3) < .45: c = WAT_L
                S(x, y, c)
            elif e <= 1.22:
                a = math.atan2(y-POOL_CY, x-POOL_CX)
                seg = int((a + math.pi) / (2*math.pi) * 22)
                c = ROCK_L if seg % 2 else ROCK
                if y > POOL_CY + 3 and e > 1.12: c = ROCK_D
                if e < 1.06: c = shade(c, .8)
                S(x, y, c)
    # fallendes Wasser
    for y in range(6, 68):
        l, r = water_x(y)
        for x in range(l, r+1):
            off = (x*37) % 11
            v = (y - t*4 + off*3) % 16
            if x in (l, r): c = WAT_D
            elif v < 2: c = FOAM
            elif v < 6 or (x*7) % 5 == 0: c = WAT_L
            else: c = WAT
            S(x, y, c)
    l, r = water_x(6)
    for x in range(l+1, r): S(x, 5, FOAM); S(x, 6, WAT_L)
    for x in range(l+2, r-1, 3): S(x, 4, FOAM)
    # Gischt + Tropfen
    l, r = water_x(66)
    for i in range(7):
        cx = l - 3 + i * (r-l+6) / 6
        cy = 67 + math.sin(t*math.pi/4 + i) * 1.0
        rad = 2.0 + ((i + t) % 3) * .6
        for y in range(int(cy-rad)-1, int(cy+rad)+2):
            for x in range(int(cx-rad)-1, int(cx+rad)+2):
                if (x-cx)**2 + (y-cy)**2 <= rad*rad: S(x, y, FOAM if y < cy+.5 else WAT_L)
    w = r - l + 10
    for i in range(6):
        S(l-5 + (i*13 + t*5) % w, 63 - ((t + i*3) % 5), FOAM)
    return g.outline(img, g.B_OUTLINE)

# ================================================================ DUNGEON-TÜR
OB, OB_L, OB_D, OB_HL = C('#26222e'), C('#38323f'), C('#121018'), C('#5a5268')
IRON, IRON_L = C('#4a4a58'), C('#7a7a8a')
LEAF_WOOD = C('#3a2a26')
RUNE_DIM, RUNE_HI = C('#4a3a8a'), C('#b8a0ff')
FIRE, FIRE_L, FIRE_D = C('#ff9a3c'), C('#ffd27a'), C('#e8603a')
D_W, D_H = 64, 80
CX, CY, RI, RO = 31.5, 38, 14, 22
BOTTOM = 73
TORCHES = [(13, 44), (50, 44)]

def inside_opening(x, y):
    return 18 <= x <= 45 and y <= BOTTOM and (y >= CY or (x-CX)**2 + (y-CY)**2 <= RI*RI)

def inside_outer(x, y):
    return 10 <= x <= 53 and y <= BOTTOM and (y >= CY or (x-CX)**2 + (y-CY)**2 <= RO*RO)

RUNE = [(31, 17), (31, 18), (31, 19), (31, 20), (31, 21), (29, 18), (33, 18), (30, 20), (32, 20)]
SIDE_RUNES = [(13, 58), (13, 59), (12, 60), (14, 60), (50, 58), (50, 59), (49, 60), (51, 60)]

def dungeon_door(k, t, rune_level):
    """k: 0 = zu ... 5 = offen; t: Bild für Fackeln; rune_level 0..1"""
    cv = g.Canvas(D_W, D_H, 77); rng = random.Random(3)
    tone = {}
    # Steinrahmen
    for y in range(0, BOTTOM+1):
        for x in range(D_W):
            if not inside_outer(x, y) or inside_opening(x, y): continue
            if y < CY:
                a = math.atan2(CY - y, x - CX); seg = a / (math.pi/9)
                bid = ('a', int(seg)); mortar = (seg % 1) < .12 and math.hypot(x-CX, y-CY) > RI + .5
            else:
                row = int((y - CY) // 7); side = 0 if x < CX else 1
                split = (13 if side == 0 else 49) + (row % 2) * 2
                bid = ('j', row, side, x >= split); mortar = (y - CY) % 7 == 6 or x == split
            if bid not in tone: tone[bid] = rng.uniform(.85, 1.15)
            c = OB_D if mortar else shade(OB, tone[bid])
            if bid == ('a', 4) and not mortar: c = OB_L
            cv.set(x, y, c)
    src = cv.img.copy().load()
    for y in range(1, BOTTOM+1):
        for x in range(1, D_W):
            if src[x, y][3] and src[x, y] != OB_D and (src[x, y-1] == OB_D or not src[x, y-1][3] or src[x-1, y] == OB_D):
                cv.set(x, y, OB_HL if not src[x, y-1][3] else shade(src[x, y], 1.35))
    # Stufen
    for i, (y0, x0, x1) in enumerate(((74, 6, 57), (77, 3, 60))):
        cv.rect(x0, y0, x1, y0+2, shade(OB, 1.1 - i*.15)); cv.rect(x0, y0, x1, y0, OB_HL)
        for x in range(x0+5, x1, 9): cv.rect(x, y0+1, x, y0+2, OB_D)
    # Ranken
    for (vx, vy, ln) in ((14, 24, 9), (20, 19, 5), (44, 20, 6), (51, 27, 7)):
        for j in range(ln):
            cv.set(vx + (1 if j % 4 == 2 else 0), vy + j, g.LEAF_D if j % 2 else g.LEAF)
            if j % 3 == 1: cv.set(vx - 1, vy + j, g.LEAF_L)
    # Innenraum
    f = k / 5
    if k:
        for y in range(0, BOTTOM+1):
            for x in range(18, 46):
                if not inside_opening(x, y): continue
                c = mix(C('#07060a'), C('#14101c'), max(0, (y - 40) / 33))
                for sy in (63, 67, 71):
                    if y == sy and abs(x - CX) < 6 + (sy - 60): c = C('#221c2c')
                if y >= 70 and (x + y + t) % 3 == 0: c = C('#3a2a5a')
                cv.set(x, y, c)
    # Türflügel
    for (x0, hinge) in ((18, 'left'), (32, 'right')):
        dw = 14 if k == 0 else max(1, round(14 * (1 - f)))
        lx = x0 if hinge == 'left' else x0 + 14 - dw
        pc = shade(LEAF_WOOD, 1 - .35*f)
        for y in range(0, BOTTOM+1):
            for i in range(dw):
                x = lx + i
                if not inside_opening(x, y): continue
                oi = int((i if hinge == 'left' else dw-1-i) * 14 / dw)
                c = shade(pc, .72) if oi % 3 == 2 or k == 5 else pc
                if k == 0 and ((hinge == 'left' and x == 31) or (hinge == 'right' and x == 32)): c = OB_D
                if y in (32, 48, 64): c = IRON_L if (x % 3 == 0 and dw > 3) else IRON
                cv.set(x, y, c)
        if dw >= 6:
            kx = lx + dw - 4 if hinge == 'left' else lx + 3
            for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1), (-1, 1), (1, 1), (0, 2)):
                cv.set(kx + dx, 54 + dy, IRON_L if dy < 1 else IRON)
            cv.set(kx, 54, C('#1a1620'))
    # Runen
    rc = mix(RUNE_DIM, RUNE_HI, rune_level)
    for (x, y) in RUNE + SIDE_RUNES: cv.set(x, y, rc)
    # Fackeln
    shapes = [[(0, 0, FIRE_L), (0, -1, FIRE), (0, -2, FIRE_D)],
              [(0, 0, FIRE_L), (0, -1, FIRE_L), (0, -2, FIRE), (1, -3, FIRE_D)],
              [(0, 0, FIRE), (0, -1, FIRE_L), (-1, -1, FIRE), (0, -2, FIRE_D)],
              [(0, 0, FIRE_L), (0, -1, FIRE), (0, -2, FIRE), (-1, -3, FIRE_D)]]
    for i, (tx, ty) in enumerate(TORCHES):
        cv.rect(tx-1, ty+1, tx+1, ty+1, IRON); cv.rect(tx, ty+2, tx, ty+5, IRON); cv.set(tx, ty+6, IRON_L)
        cv.rect(tx-1, ty, tx+1, ty, C('#5a3a2a'))
        for dx, dy, c in shapes[(t + i*2) % 4]: cv.set(tx+dx, ty-1+dy, c)
    cv.glow([(tx-1, ty-4, 3, 4) for tx, ty in TORCHES], FIRE)
    if rune_level > .5:
        for (x, y) in ((30, 16), (32, 16), (28, 19), (34, 19), (30, 22), (32, 22)):
            cv.set(x, y, mix(OB_L, RUNE_HI, (rune_level-.5)))
    return cv.done()

# ================================================================ EXPORT
def strip(frames):
    w, h = frames[0].size
    s = Image.new('RGBA', (w*len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(f, (i*w, 0))
    return s

def gif(frames, path, dur, scale=5, bg=g.SKY_NIGHT):
    w, h = frames[0].size
    out = []
    for f in frames:
        b = Image.new('RGBA', (w*scale, h*scale), bg); b.alpha_composite(f.resize((w*scale, h*scale), Image.NEAREST)); out.append(b.convert('RGB'))
    out[0].save(path, save_all=True, append_images=out[1:], duration=dur, loop=0)

def main():
    os.makedirs(OUT, exist_ok=True)
    wf = [waterfall(t) for t in range(8)]
    strip(wf).save(os.path.join(OUT, 'wasserfall_anim.png'))
    gif(wf, os.path.join(OUT, 'wasserfall.gif'), 110)

    pulse = [(1 + math.sin(2*math.pi*t/8)) / 2 * .6 for t in range(8)]
    idle_zu = [dungeon_door(0, t, pulse[t]) for t in range(8)]
    auf = [dungeon_door(k, k, .6 + .4*k/5) for k in range(6)]
    idle_offen = [dungeon_door(5, t, .75 + pulse[t]*.4) for t in range(8)]
    zu = [dungeon_door(5-k, 5-k, 1 - .4*k/5) for k in range(6)]
    for name, fr in (('idle_zu', idle_zu), ('auf', auf), ('idle_offen', idle_offen), ('zu', zu)):
        strip(fr).save(os.path.join(OUT, f'dungeon_tuer_{name}.png'))
    seq = idle_zu*2 + auf + idle_offen*2 + zu
    gif(seq, os.path.join(OUT, 'dungeon_tuer.gif'), 120)

    meta = {
        'wasserfall': {'bild': [WF_W, WF_H], 'bilder': 8, 'ms_pro_bild': 110,
                       'kollision': {'x': 2, 'y': 52, 'w': WF_W-4, 'h': 34},
                       'sortier_y': 84, 'hinweis': 'Felsen + Becken sind fest; Figuren laufen davor (y-Sortierung).'},
        'dungeon_tuer': {'bild': [D_W, D_H], 'animationen': {'idle_zu': 8, 'auf': 6, 'idle_offen': 8, 'zu': 6},
                         'ms_pro_bild': 120,
                         'kollision_rahmen': [{'x': 10, 'y': 60, 'w': 8, 'h': 14}, {'x': 46, 'y': 60, 'w': 8, 'h': 14}],
                         'kollision_tuer_zu': {'x': 18, 'y': 60, 'w': 28, 'h': 14},
                         'eingang_trigger': {'x': 20, 'y': 66, 'w': 24, 'h': 8}, 'sortier_y': 74},
    }
    with open(os.path.join(OUT, 'objekte.json'), 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)

    # gemeinsame Vorschau
    S = 5; Wp = (WF_W + D_W) * S + 60; Hp = max(WF_H, D_H) * S + 70
    door_seq = idle_zu + auf + idle_offen + idle_offen + zu + idle_zu
    frames = []
    for i, df in enumerate(door_seq):
        im = Image.new('RGBA', (Wp, Hp), g.SKY_NIGHT); d = ImageDraw.Draw(im)
        d.rectangle([0, Hp-40, Wp, Hp], fill=g.GROUND_NIGHT)
        w = wf[i % 8]; im.alpha_composite(w.resize((WF_W*S, WF_H*S), Image.NEAREST), (20, Hp-40-WF_H*S+S*2))
        im.alpha_composite(df.resize((D_W*S, D_H*S), Image.NEAREST), (40 + WF_W*S, Hp-40-D_H*S+S*2))
        d.text((20, 10), 'Wasserfall  +  Dungeon-Tür', fill=(255, 240, 200), font=g.font(20))
        frames.append(im.convert('RGB'))
    frames[0].save(os.path.join(g.BASE, 'preview_objekte.gif'), save_all=True, append_images=frames[1:], duration=120, loop=0)

if __name__ == '__main__':
    main()
