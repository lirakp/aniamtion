"""Innenräume der Läden und Gebäude (Seitenansicht, 320x180 = ein Bildschirm).
Aufruf: python3 interiors.py
Ausgabe je Raum in level/innenraeume/<raum>/:
  hintergrund.png  – Wand, Fenster, Möbel (hinter dem Spieler)
  anim.png         – 6 Frames untereinander, transparent: Feuer, Kerzen, Blasen, Leuchten (über den Hintergrund legen)
  vordergrund.png  – Balken/Hängendes vor dem Spieler (optional, transparent)
  vorschau.gif
level/innenraeume/innenraeume.json – Boden-y, Tür (Ausgang), Platz des Ladenbesitzers, Thekenbereich
preview_innenraeume.gif
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
import icons as IC

OUT = os.path.join(g.BASE, 'level', 'innenraeume')
W, H, N = 320, 180, 6
FLOOR = 150
INK, WHITE = C('#2b1e33'), C('#ffffff')
WOOD, WOOD_D, WOOD_L = g.WOOD, g.WOOD_D, g.WOOD_L
BEAM = C('#3e2a22')
ICON = {n: im for grp in IC.GROUPS.values() for n, im in grp}

def h(i, s):
    x = (i * 374761393 + s * 668265263) & 0xffffffff
    x = ((x ^ (x >> 13)) * 1274126177) & 0xffffffff
    return ((x ^ (x >> 16)) & 0xffffff) / 0x1000000

class Room:
    def __init__(self, wall='holz', floor='holz', wall_col=None, floor_col=None):
        self.bg = Image.new('RGBA', (W, H)); self.fg = Image.new('RGBA', (W, H)); self.anims = []
        self.d = ImageDraw.Draw(self.bg); self.fd = ImageDraw.Draw(self.fg)
        self.meta = {'boden_y': FLOOR}
        self.walls(wall, wall_col); self.floor(floor, floor_col)
    # ---------------- Grundgerüst
    def walls(self, kind, col):
        d = self.d
        if kind == 'holz':
            c = col or C('#8a6040')
            d.rectangle([0, 0, W, FLOOR], fill=c)
            for x in range(0, W, 12):
                d.line([(x, 0), (x, FLOOR)], fill=shade(c, .78))
                for y in range(int(h(x, 1) * 40) + 10, FLOOR, 45): d.point((x + 5, y), fill=shade(c, .7)); d.point((x + 6, y), fill=shade(c, .82))
            d.rectangle([0, FLOOR - 26, W, FLOOR], fill=shade(c, .82)); d.line([(0, FLOOR - 26), (W, FLOOR - 26)], fill=shade(c, 1.15))  # Täfelung
        elif kind == 'stein':
            c = col or C('#6e687a')
            d.rectangle([0, 0, W, FLOOR], fill=c)
            for r, y in enumerate(range(0, FLOOR, 10)):
                d.line([(0, y), (W, y)], fill=shade(c, .72))
                for x in range((r % 2) * 10, W, 20): d.line([(x, y), (x, y + 10)], fill=shade(c, .72))
                for x in range((r % 2) * 10 + 2, W, 20):
                    if h(x, y) < .3: d.rectangle([x, y + 2, x + 6, y + 7], fill=shade(c, .9 + h(y, x) * .2))
        elif kind == 'putz':
            c = col or C('#e0d2b8')
            d.rectangle([0, 0, W, FLOOR], fill=c)
            for i in range(160): d.point((h(i, 3) * W, h(i, 4) * FLOOR), fill=shade(c, .93))
            for x in range(0, W, 64): d.rectangle([x, 0, x + 5, FLOOR], fill=BEAM)
            d.rectangle([0, 60, W, 64], fill=BEAM)
            for x in range(0, W, 64): d.line([(x + 5, 64), (x + 34, 100)], fill=BEAM, width=4)
            d.rectangle([0, FLOOR - 22, W, FLOOR], fill=C('#8a6040')); d.line([(0, FLOOR - 22), (W, FLOOR - 22)], fill=WOOD_L)
        # Deckenbalken
        d.rectangle([0, 0, W, 9], fill=BEAM); d.line([(0, 9), (W, 9)], fill=shade(BEAM, 1.3))
        for x in range(30, W, 70):
            d.rectangle([x, 0, x + 8, 14], fill=shade(BEAM, .85)); d.line([(x, 14), (x + 8, 14)], fill=INK)
        d.rectangle([0, 0, 6, FLOOR], fill=BEAM); d.rectangle([W - 7, 0, W, FLOOR], fill=BEAM)
    def floor(self, kind, col):
        d = self.d
        if kind == 'holz':
            c = col or C('#6a4a32'); d.rectangle([0, FLOOR, W, H], fill=c)
            for y in range(FLOOR + 6, H, 7): d.line([(0, y), (W, y)], fill=shade(c, .75))
            for i, y in enumerate(range(FLOOR, H, 7)):
                for x in range((i * 23) % 40, W, 40): d.line([(x, y), (x, y + 6)], fill=shade(c, .72))
        else:
            c = col or C('#5a5468'); d.rectangle([0, FLOOR, W, H], fill=c)
            for y in range(FLOOR, H, 8):
                d.line([(0, y), (W, y)], fill=shade(c, .7))
                for x in range((y // 8 % 2) * 12, W, 24): d.line([(x, y), (x, y + 8)], fill=shade(c, .7))
        d.line([(0, FLOOR), (W, FLOOR)], fill=INK); d.line([(0, FLOOR + 1), (W, FLOOR + 1)], fill=shade(c, 1.2))
    # ---------------- Bauteile
    def tuer(self, x=14):
        d = self.d; d.rectangle([x - 3, FLOOR - 58, x + 29, FLOOR], fill=BEAM)
        d.rectangle([x, FLOOR - 55, x + 26, FLOOR], fill=g.DOORWOOD)
        for k in range(x + 6, x + 26, 7): d.line([(k, FLOOR - 55), (k, FLOOR)], fill=shade(g.DOORWOOD, .75))
        d.ellipse([x + 20, FLOOR - 29, x + 23, FLOOR - 26], fill=g.GOLD)
        d.rectangle([x - 6, FLOOR - 1, x + 32, FLOOR + 2], fill=shade(WOOD_D, .9))  # Fußmatte
        self.meta['tuer'] = [x, FLOOR - 55, 26, 55]
    def fenster(self, x, y=36, w=34, hh=42, nacht=True, arch=True):
        d = self.d; sky = C('#2a2a5a') if nacht else C('#8ac0e8')
        d.rectangle([x - 3, y - 3, x + w + 3, y + hh + 5], fill=BEAM)
        if arch: d.chord([x - 3, y - 3 - w // 2, x + w + 3, y + w // 2 + 3], 180, 360, fill=BEAM)
        d.rectangle([x, y, x + w, y + hh], fill=sky)
        if arch: d.chord([x, y - w // 2, x + w, y + w // 2], 180, 360, fill=sky)
        if nacht:
            d.ellipse([x + w - 12, y - 6, x + w - 4, y + 2], fill=C('#f0e8c0'))
            for i in range(6): d.point((x + 3 + h(i, x) * (w - 6), y - 4 + h(x, i) * (hh - 4)), fill=WHITE)
        else:
            d.ellipse([x + 4, y + 8, x + 18, y + 13], fill=WHITE)
        d.line([(x + w // 2, y - (w // 2 if arch else 0)), (x + w // 2, y + hh)], fill=BEAM, width=2); d.line([(x, y + hh // 2), (x + w, y + hh // 2)], fill=BEAM, width=2)
        d.rectangle([x - 5, y + hh + 3, x + w + 5, y + hh + 6], fill=WOOD_L)
        # Lichtstrahl auf den Boden (tagsüber hell, nachts Mondlicht)
        ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
        col = (220, 230, 255, 22) if nacht else (255, 240, 190, 34)
        od.polygon([(x, y + hh), (x + w, y + hh), (x + w + 40, FLOOR + 14), (x + 30, FLOOR + 14)], fill=col)
        self.bg.alpha_composite(ov)
    def regal(self, x, y, w, boards, items, back=None):
        """items: Liste von Icon-Namen, werden auf die Bretter verteilt."""
        d = self.d; bh = 22
        hh = boards * bh
        d.rectangle([x, y, x + w, y + hh], fill=back or shade(WOOD, .6))
        d.rectangle([x - 2, y - 3, x + w + 2, y], fill=WOOD); d.rectangle([x - 2, y, x, y + hh], fill=WOOD); d.rectangle([x + w, y, x + w + 2, y + hh], fill=WOOD)
        k = 0
        for b in range(boards):
            by = y + (b + 1) * bh
            d.rectangle([x, by - 2, x + w, by], fill=WOOD_L); d.line([(x, by + 1), (x + w, by + 1)], fill=WOOD_D)
            n = max(1, (w - 4) // 17)
            for i in range(n):
                if k < len(items) and items[k]:
                    ic = ICON.get(items[k])
                    if ic: self.bg.alpha_composite(ic, (x + 3 + i * 17, by - 18))
                k += 1
    def theke(self, x0, x1, top=118, items=(), col=None):
        d = self.d; c = col or WOOD
        d.rectangle([x0, top, x1, FLOOR], fill=c); d.rectangle([x0 - 3, top - 4, x1 + 3, top], fill=WOOD_L); d.line([(x0 - 3, top), (x1 + 3, top)], fill=WOOD_D)
        for x in range(x0 + 4, x1 - 4, 22): d.rectangle([x, top + 5, x + 16, FLOOR - 5], outline=shade(c, .72))
        for i, n in enumerate(items):
            ic = ICON.get(n)
            if ic: self.bg.alpha_composite(ic, (x0 + 6 + i * 19, top - 20))
        self.meta['theke'] = [x0, top, x1 - x0, FLOOR - top]
        self.meta['ladenbesitzer'] = [(x0 + x1) // 2, FLOOR]  # Figur steht hinter der Theke (Füße auf Boden)
    def kiste(self, x, w=20, hh=16, y=None):
        d = self.d; y = FLOOR if y is None else y
        d.rectangle([x, y - hh, x + w, y], fill=WOOD); d.rectangle([x, y - hh, x + w, y - hh + 2], fill=WOOD_L)
        d.line([(x, y - hh), (x + w, y)], fill=WOOD_D); d.rectangle([x, y - hh, x + w, y], outline=WOOD_D)
    def fass(self, x, y=None, w=18, hh=24):
        d = self.d; y = FLOOR if y is None else y
        d.ellipse([x, y - hh, x + w, y], fill=C('#8a5a3a')); d.rectangle([x + 1, y - hh + 3, x + w - 1, y - 3], fill=C('#8a5a3a'))
        for yy in (y - hh + 5, y - 6): d.line([(x + 1, yy), (x + w - 1, yy)], fill=C('#5a5468'), width=2)
        d.line([(x + 4, y - hh + 3), (x + 4, y - 3)], fill=C('#a8784a'))
    def tisch(self, x, w=36, top=128):
        d = self.d; d.rectangle([x, top, x + w, top + 3], fill=WOOD_L); d.rectangle([x + 3, top + 3, x + 6, FLOOR], fill=WOOD_D); d.rectangle([x + w - 6, top + 3, x + w - 3, FLOOR], fill=WOOD_D)
    def stuhl(self, x, face=1):
        d = self.d; d.rectangle([x, 136, x + 10, 138], fill=WOOD); d.rectangle([x + 1, 138, x + 2, FLOOR], fill=WOOD_D); d.rectangle([x + 8, 138, x + 9, FLOOR], fill=WOOD_D)
        bx = x if face > 0 else x + 9; d.rectangle([bx, 120, bx + 1, 136], fill=WOOD)
    def teppich(self, x0, x1, col):
        d = self.d; d.rectangle([x0, FLOOR + 2, x1, FLOOR + 7], fill=col); d.line([(x0, FLOOR + 4), (x1, FLOOR + 4)], fill=mix(col, (255, 230, 160, 255), .4))
        for x in range(x0, x1, 3): d.point((x, FLOOR + 8), fill=mix(col, WHITE, .3))
    def banner(self, x, col, emblem=None):
        d = self.d; d.line([(x - 2, 22), (x + 18, 22)], fill=WOOD_D, width=2)
        d.polygon([(x, 23), (x + 16, 23), (x + 16, 60), (x + 8, 54), (x, 60)], fill=col); d.line([(x + 2, 25), (x + 2, 56)], fill=mix(col, WHITE, .2))
        if emblem: self.bg.alpha_composite(ICON[emblem], (x, 30))
    def lampe(self, x, y=30, kette=True):
        d = self.d
        if kette: d.line([(x, 10), (x, y - 6)], fill=C('#3a3446'))
        d.rectangle([x - 4, y - 6, x + 4, y + 4], fill=C('#3a3446')); d.rectangle([x - 3, y - 4, x + 3, y + 2], fill=C('#ffd27a'))
        d.polygon([(x - 6, y - 6), (x + 6, y - 6), (x, y - 10)], fill=C('#3a3446'))
        self.anims.append(lambda od, t, x=x, y=y: glow(od, x, y, 26 + (t % 3), (255, 200, 120)))
    def kerzen(self, x, y, n=3):
        d = self.d
        for i in range(n):
            cx = x + i * 5; hh = 6 + (i * 3) % 5
            d.rectangle([cx - 1, y - hh, cx + 1, y], fill=C('#f0e8d8')); d.point((cx, y - hh - 1), fill=INK)
        def a(od, t, x=x, y=y, n=n):
            for i in range(n):
                cx = x + i * 5; hh = 6 + (i * 3) % 5; f = (t + i) % 3
                od.polygon([(cx - 1, y - hh - 1), (cx + 1, y - hh - 1), (cx + (f - 1) * .5, y - hh - 5 - (f == 1))], fill=(255, 190, 90, 255)); od.point((cx, y - hh - 2), fill=(255, 240, 180, 255))
            glow(od, x + n * 2, y - 10, 14 + t % 2, (255, 200, 120), .7)
        self.anims.append(a)
    def kamin(self, x, w=50):
        d = self.d
        d.rectangle([x - 6, FLOOR - 66, x + w + 6, FLOOR], fill=C('#6e687a'))
        for r, y in enumerate(range(FLOOR - 66, FLOOR, 8)):
            d.line([(x - 6, y), (x + w + 6, y)], fill=C('#4e485a'))
            for xx in range(x - 6 + (r % 2) * 7, x + w + 6, 14): d.line([(xx, y), (xx, y + 8)], fill=C('#4e485a'))
        d.rectangle([x - 9, FLOOR - 70, x + w + 9, FLOOR - 64], fill=WOOD); d.rectangle([x + 6, FLOOR - 40, x + w - 6, FLOOR], fill=C('#1e1a28'))
        d.chord([x + 6, FLOOR - 52, x + w - 6, FLOOR - 28], 180, 360, fill=C('#1e1a28'))
        for i in range(3): d.line([(x + 12 + i * 8, FLOOR - 3), (x + 20 + i * 8, FLOOR - 7)], fill=WOOD_D, width=3)
        self.anims.append(lambda od, t, x=x, w=w: feuer(od, x + w // 2, FLOOR - 6, w - 18, 22, t))
    def esse(self, x, w=60):
        d = self.d
        d.rectangle([x, FLOOR - 40, x + w, FLOOR], fill=C('#5a5468')); d.rectangle([x - 3, FLOOR - 44, x + w + 3, FLOOR - 38], fill=C('#3e3a4a'))
        d.polygon([(x + 6, FLOOR - 44), (x + w - 6, FLOOR - 44), (x + w // 2 + 10, 14), (x + w // 2 - 10, 14)], fill=C('#4e485a'))
        d.rectangle([x + 8, FLOOR - 40, x + w - 8, FLOOR - 26], fill=C('#2a1e1e'))
        self.anims.append(lambda od, t, x=x, w=w: (feuer(od, x + w // 2, FLOOR - 27, w - 20, 12, t, hot=True), glow(od, x + w // 2, FLOOR - 32, 40, (255, 120, 60), .9)))
    def amboss(self, x):
        d = self.d; ir = C('#5a5e70')
        d.polygon([(x, FLOOR - 22), (x + 26, FLOOR - 22), (x + 22, FLOOR - 17), (x + 6, FLOOR - 17)], fill=ir); d.polygon([(x - 6, FLOOR - 22), (x, FLOOR - 22), (x, FLOOR - 19)], fill=ir)
        d.line([(x - 4, FLOOR - 22), (x + 26, FLOOR - 22)], fill=C('#a8acbc')); d.rectangle([x + 8, FLOOR - 17, x + 18, FLOOR - 8], fill=shade(ir, .7)); d.rectangle([x + 3, FLOOR - 8, x + 23, FLOOR], fill=WOOD_D)
    def kessel(self, x, col):
        d = self.d
        for i in range(3): d.line([(x + 4 + i * 10, FLOOR), (x + 12 + i * 2, FLOOR - 10)], fill=WOOD_D, width=2)
        d.ellipse([x, FLOOR - 32, x + 32, FLOOR - 6], fill=C('#2e2a36')); d.ellipse([x + 2, FLOOR - 32, x + 30, FLOOR - 24], fill=col)
        d.arc([x + 4, FLOOR - 26, x + 12, FLOOR - 12], 120, 240, fill=C('#4e485a'))
        def a(od, t, x=x, col=col):
            for i in range(4):
                ph = (t + i * 2) % N; bx = x + 7 + i * 6; by = FLOOR - 29 - ph * 3
                r = 2 if ph < 3 else 1
                od.ellipse([bx - r, by - r, bx + r, by + r], outline=mix(col, WHITE, .5)[:3] + (230 - ph * 30,))
            glow(od, x + 16, FLOOR - 30, 22, col[:3], .7)
        self.anims.append(a)
    def puppe(self, x, ruestung='brustplatte_B', helm='helm_B'):
        d = self.d; d.rectangle([x + 7, FLOOR - 10, x + 9, FLOOR], fill=WOOD_D); d.rectangle([x + 2, FLOOR - 2, x + 14, FLOOR], fill=WOOD_D)
        big = ICON[ruestung].resize((24, 24), Image.NEAREST); self.bg.alpha_composite(big, (x - 4, FLOOR - 36))
        hb = ICON[helm].resize((20, 20), Image.NEAREST); self.bg.alpha_composite(hb, (x - 2, FLOOR - 54))
    def waffenwand(self, x, y, names):
        d = self.d; d.rectangle([x - 3, y - 3, x + len(names) * 18 + 1, y + 21], fill=shade(WOOD, .7), outline=WOOD_D)
        for i, n in enumerate(names):
            ic = ICON[n].rotate(45, resample=Image.NEAREST, expand=True); self.bg.alpha_composite(ic, (x + i * 18 - 3, y - 3))
            d.point((x + i * 18 + 8, y + 1), fill=C('#a8acbc'))
    def brett(self, x, y, w=70, hh=46):
        d = self.d; d.rectangle([x, y, x + w, y + hh], fill=C('#a8784a'), outline=WOOD_D)
        for i in range(7):
            px_, py = x + 4 + (i * 19) % (w - 16), y + 4 + (i * 13) % (hh - 18)
            d.rectangle([px_, py, px_ + 12, py + 14], fill=C('#f0e4cc') if i % 3 else C('#e8d0a0')); d.point((px_ + 6, py + 1), fill=C('#c83a3a'))
            for k in range(3): d.line([(px_ + 2, py + 5 + k * 3), (px_ + 10 - (k == 2) * 3, py + 5 + k * 3)], fill=C('#8a7a6a'))
        self.bg.alpha_composite(ICON['monsterkern_S'], (x + w - 18, y + hh - 18))
    def kugel(self, x, y):
        d = self.d; d.rectangle([x - 6, y + 8, x + 6, y + 11], fill=C('#e0b048')); d.polygon([(x - 4, y + 8), (x + 4, y + 8), (x + 2, y + 5), (x - 2, y + 5)], fill=C('#c89838'))
        def a(od, t, x=x, y=y):
            od.ellipse([x - 7, y - 8, x + 7, y + 6], fill=(150, 120, 240, 200))
            for i in range(5):
                ang = t / N * 2 * math.pi + i * 1.3; od.point((x + math.cos(ang) * 4, y - 1 + math.sin(ang) * 4), fill=(240, 230, 255, 255))
            od.point((x - 3, y - 5), fill=(255, 255, 255, 255)); glow(od, x, y - 1, 20, (180, 150, 255), .8)
        self.anims.append(a)
    def schwebe(self, x, y, name):
        ic = ICON[name]
        def a(od, t, x=x, y=y, ic=ic):
            dy = round(math.sin(t / N * 2 * math.pi) * 2); od._image.alpha_composite(ic, (x, y + dy))
            od.point((x + 3 + t % 3 * 4, y + 18 + dy), fill=(216, 200, 255, 200))
        self.anims.append(a)
    def ofen(self, x):
        d = self.d
        d.chord([x, FLOOR - 60, x + 60, FLOOR + 30], 180, 360, fill=C('#a8584a')); d.rectangle([x, FLOOR - 15, x + 60, FLOOR], fill=C('#a8584a'))
        for i in range(0, 60, 8): d.line([(x + i, FLOOR - 30), (x + i, FLOOR)], fill=C('#8a443a'))
        d.chord([x + 16, FLOOR - 32, x + 44, FLOOR - 4], 180, 360, fill=C('#2a1a1a')); d.rectangle([x + 16, FLOOR - 18, x + 44, FLOOR - 4], fill=C('#2a1a1a'))
        self.anims.append(lambda od, t, x=x: (feuer(od, x + 30, FLOOR - 6, 22, 12, t), glow(od, x + 30, FLOOR - 14, 30, (255, 150, 80), .8)))
    def staub(self):
        def a(od, t):
            for i in range(20):
                x = h(i, 50) * W; y = 20 + (h(i, 51) * 120 + t * 2) % 125
                od.point((x, y), fill=(255, 240, 200, 120 + int(80 * math.sin(t + i))))
        self.anims.append(a)
    def render(self):
        frames = []
        for t in range(N):
            ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov, 'RGBA')
            for a in self.anims: a(od, t)
            frames.append(ov)
        return frames

def glow(od, x, y, r, col, k=1.0):
    base = od._image; lay = Image.new('RGBA', base.size); ld = ImageDraw.Draw(lay)
    for rr, a in ((r, 18), (r * .65, 26), (r * .35, 36)):
        l2 = Image.new('RGBA', base.size); ImageDraw.Draw(l2).ellipse([x - rr, y - rr, x + rr, y + rr], fill=col[:3] + (int(a * k),)); lay.alpha_composite(l2)
    lay.alpha_composite(base.copy()); base.paste(lay)  # Glühen unter die schon gezeichneten Flammen legen
def feuer(od, cx, base, w, hh, t, hot=False):
    for i in range(int(w // 4)):
        x = cx - w / 2 + i * 4 + 2; fh = hh * (.5 + .5 * h(i, t + 7))
        c1 = (255, 230, 140, 255) if hot else (255, 210, 110, 255)
        od.polygon([(x - 3, base), (x + 3, base), (x + (t + i) % 3 - 1, base - fh)], fill=(232, 96, 58, 255))
        od.polygon([(x - 1.5, base), (x + 1.5, base), (x, base - fh * .55)], fill=c1)

# ---------------------------------------------------------------- Räume
def alchemie():
    r = Room('stein', 'stein', C('#5e6a6a')); r.tuer(); r.fenster(70, nacht=True)
    pots = [n for n, _ in IC.GROUPS['traenke']] + ['heilkraut', 'pilz', 'leuchtpilz', 'blume']
    r.regal(126, 26, 92, 3, pots + pots); r.kessel(236, C('#6ac84a')); r.theke(118, 222, items=['heil_gross', 'mana_klein', 'gegengift_klein', 'leuchtpilz'])
    r.lampe(100); r.kerzen(282, 74); r.d.rectangle([268, 74, 300, 77], fill=WOOD_L); r.staub()
    for x, n in ((272, 'heil_klein'), (288, 'mana_klein')): r.bg.alpha_composite(ICON[n], (x - 4, 56))
    return r
def ausruestung():  # Dungeon-Ausrüstung
    r = Room('holz'); r.tuer(); r.fenster(66, nacht=False, arch=False)
    r.regal(116, 28, 70, 3, ['seil', 'fackel', 'laterne', 'karte', 'schluessel_eisen', 'seil', 'fackel', 'laterne', 'mana_batterie', 'brief', 'karte', 'fackel'])
    r.kiste(260, 26, 20); r.kiste(266, 20, 14, FLOOR - 20); r.fass(232); r.theke(124, 220, items=['laterne', 'seil', 'karte', 'fackel'])
    r.waffenwand(200, 34, ['speer_C', 'axt_C', 'bogen_C']); r.lampe(160); r.teppich(40, 110, C('#7a4a3a'))
    return r
def magie():
    r = Room('stein', 'stein', C('#3e3a5a'), C('#3a3446')); r.tuer(); r.fenster(64, nacht=True)
    r.regal(120, 24, 76, 3, ['grimoire_' + e for e in ('feuer', 'eis', 'wasser', 'erde', 'dendro', 'wind', 'elektro', 'schatten', 'licht')] + ['mana_kristall', 'siegelring', 'seelenvase'])
    r.theke(124, 218, items=['amulett_A', 'ring_S', 'mana_kristall', 'stab_A'], col=C('#4a3a6a')); r.kugel(250, 104); r.d.rectangle([240, 116, 260, FLOOR], fill=C('#4a3a6a'))
    r.schwebe(212, 36, 'grimoire_elektro'); r.schwebe(274, 50, 'mana_kristall'); r.kerzen(276, 112); r.d.rectangle([268, 112, 296, 115], fill=WOOD_L)
    r.teppich(36, 116, C('#5a3a8a')); r.banner(284, C('#5a3a8a'), 'grimoire_schatten')
    return r
def ruestung_waffen():
    r = Room('holz', wall_col=C('#7a5a42')); r.tuer(); r.fenster(64, nacht=False)
    r.waffenwand(112, 30, ['schwert_C', 'schwert_B', 'axt_B', 'speer_B', 'hammer_C', 'dolch_B']); r.waffenwand(112, 62, ['schild_C', 'schild_B', 'bogen_B', 'stab_C'])
    r.puppe(236, 'brustplatte_B', 'helm_B'); r.puppe(270, 'brustplatte_A', 'helm_A'); r.theke(124, 214, items=['schwert_A', 'schild_A', 'handschuhe_B', 'stiefel_B'])
    r.lampe(176); r.teppich(40, 110, C('#8a3a3a')); r.banner(216, C('#8a3a3a'), 'schild_S')
    return r
def schmiede(waffen=True):
    r = Room('stein', 'stein', C('#5e5462')); r.tuer(); r.esse(64)
    r.amboss(148); r.fass(176, hh=20)
    if waffen: r.waffenwand(206, 34, ['schwert_S', 'axt_A', 'hammer_A', 'speer_A']); r.waffenwand(206, 66, ['dolch_S', 'schwert_SS', 'schwert_A'])
    else: r.puppe(214, 'brustplatte_S', 'helm_S'); r.puppe(250, 'brustplatte_SS', 'helm_SS'); r.waffenwand(204, 30, ['schild_S', 'schild_A', 'handschuhe_S'])
    r.theke(232 if waffen else 268, 306, items=['rohling_S', 'erz_gold'] if waffen else ['stiefel_S'])
    r.kiste(130, 14, 10); r.bg.alpha_composite(ICON['erz_eisen'], (128, FLOOR - 26)); r.bg.alpha_composite(ICON['rohling_A'], (150, FLOOR - 38))
    return r
def baeckerei():
    r = Room('putz'); r.tuer(); r.fenster(66, nacht=False, arch=False); r.ofen(236)
    r.regal(120, 30, 90, 3, ['brot'] * 6 + ['kaese', 'apfel', 'brot', 'brot', 'kaese', 'apfel', 'brot', 'brot', 'brot'], back=C('#c8a878'))
    r.theke(120, 214, items=['brot', 'brot', 'apfel', 'kaese']); r.fass(298, hh=20); r.lampe(186); r.staub()
    return r
def taverne():
    r = Room('holz', wall_col=C('#6e4a34')); r.tuer(); r.kamin(250)
    r.theke(60, 150, top=116, items=['fleisch', 'brot']); r.regal(64, 34, 82, 2, ['heil_klein', 'ausdauer_klein', 'mana_klein', 'heil_klein'] * 2)
    for x in (68, 88, 108): r.fass(x, y=FLOOR - 36, w=14, hh=0) if False else None
    r.tisch(176); r.stuhl(166, 1); r.stuhl(214, -1); r.kerzen(190, 128, 2); r.fass(300 - 12, hh=22)
    r.bg.alpha_composite(ICON['fisch'], (196, 112)); r.lampe(110); r.lampe(214); r.teppich(170, 236, C('#8a3a3a'))
    for x in range(30, W, 70): r.fd.rectangle([x, 0, x + 8, 14], fill=shade(BEAM, .7))
    return r
def gilde_abenteuer():
    r = Room('holz', wall_col=C('#7a5a42')); r.tuer(); r.fenster(64, nacht=True)
    r.brett(116, 40); r.theke(200, 300, items=['brief', 'karte', 'monsterkern_C', 'muenzen_gold']); r.banner(186, C('#a83a3a'), 'schwert_S')
    r.waffenwand(220, 30, ['schwert_C', 'schild_B', 'bogen_B']); r.tisch(118, 40); r.stuhl(106, 1); r.stuhl(160, -1); r.lampe(160); r.lampe(260)
    r.teppich(110, 180, C('#a83a3a'))
    return r
def gilde_handel():
    r = Room('putz', wall_col=C('#e8dcc4')); r.tuer(); r.fenster(64, nacht=False)
    r.regal(116, 28, 70, 3, ['muenzen_gold', 'muenzen_silber', 'erz_gold', 'mana_kristall', 'brief', 'karte', 'siegelring', 'amulett_B', 'ring_C', 'muenzen_kupfer', 'erz_silber', 'brief'])
    r.theke(196, 300, items=['muenzen_gold', 'brief', 'siegelring', 'muenzen_silber']); r.kiste(150, 24, 16); r.kiste(154, 16, 12, FLOOR - 16)
    d = r.d; d.line([(250, 70), (250, 94)], fill=C('#e0b048')); d.line([(236, 74), (264, 74)], fill=C('#e0b048'))
    for x in (236, 264): d.line([(x, 74), (x, 82)], fill=C('#e0b048')); d.chord([x - 6, 78, x + 6, 88], 0, 180, fill=C('#e0b048'))  # Waage-Schild
    r.banner(280, C('#3a6a4a'), 'muenzen_gold'); r.lampe(150); r.teppich(36, 110, C('#3a6a4a'))
    return r
def kirche():
    r = Room('stein', 'stein', C('#8a8296'), C('#6e687a')); r.tuer()
    d = r.d
    for x in (80, 210):  # Buntglasfenster
        d.rectangle([x - 3, 28, x + 33, 104], fill=BEAM); d.chord([x - 3, 10, x + 33, 46], 180, 360, fill=BEAM)
        for i in range(12):
            c = g.STAINED[i % 4]; cx, cy = x + (i % 3) * 11, 28 + (i // 3) * 19
            d.rectangle([cx, cy, cx + 9, cy + 17], fill=c)
        d.chord([x, 13, x + 30, 43], 180, 360, fill=g.STAINED[2])
        ov = Image.new('RGBA', (W, H)); od = ImageDraw.Draw(ov)
        for i, c in enumerate(g.STAINED): od.polygon([(x + i * 8, 104), (x + i * 8 + 8, 104), (x + i * 8 + 30, FLOOR + 10), (x + i * 8 + 18, FLOOR + 10)], fill=c[:3] + (26,))
        r.bg.alpha_composite(ov)
    d.rectangle([140, FLOOR - 26, 190, FLOOR], fill=C('#e8dcc0')); d.rectangle([136, FLOOR - 30, 194, FLOOR - 26], fill=C('#f4ecd8'))  # Altar
    d.rectangle([164, FLOOR - 64, 166, FLOOR - 30], fill=g.GOLD); d.rectangle([158, FLOOR - 56, 172, FLOOR - 54], fill=g.GOLD)
    r.kerzen(142, FLOOR - 30, 2); r.kerzen(182, FLOOR - 30, 2)
    for x in (60, 250):  # Bänke
        d.rectangle([x, 132, x + 40, 135], fill=WOOD); d.rectangle([x, 116, x + 3, 135], fill=WOOD); d.rectangle([x + 4, 135, x + 6, FLOOR], fill=WOOD_D); d.rectangle([x + 34, 135, x + 36, FLOOR], fill=WOOD_D)
    r.teppich(120, 210, C('#a83a3a')); r.staub()
    r.meta['ladenbesitzer'] = [165, FLOOR]
    return r
def wohnhaus():
    r = Room('putz'); r.tuer(); r.fenster(70, nacht=True, arch=False); r.kamin(240)
    d = r.d
    d.rectangle([120, 120, 190, 136], fill=C('#c8d8e8')); d.rectangle([120, 114, 136, 122], fill=WHITE); d.rectangle([118, 118, 121, FLOOR], fill=WOOD); d.rectangle([188, 126, 191, FLOOR], fill=WOOD)
    d.rectangle([120, 126, 190, 136], fill=C('#a83a3a')); d.rectangle([122, 136, 188, 139], fill=WOOD)  # Bett
    r.tisch(200, 30); r.kerzen(210, 128, 1); r.regal(124, 40, 54, 1, ['apfel', 'brot', 'laterne']); r.teppich(110, 200, C('#4a6aa0'))
    return r

ROOMS = {'alchemie': alchemie, 'ausruestung': ausruestung, 'magie': magie, 'ruestung_waffen': ruestung_waffen,
         'schmiede_waffen': lambda: schmiede(True), 'schmiede_ruestung': lambda: schmiede(False), 'baeckerei': baeckerei,
         'taverne': taverne, 'gilde_abenteuer': gilde_abenteuer, 'gilde_handel': gilde_handel, 'kirche': kirche, 'wohnhaus': wohnhaus}

def main():
    os.makedirs(OUT, exist_ok=True); meta = {}; prev = {}
    for name, fn in ROOMS.items():
        r = fn(); frames = r.render(); d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
        r.bg.save(os.path.join(d, 'hintergrund.png')); r.fg.save(os.path.join(d, 'vordergrund.png'))
        s = Image.new('RGBA', (W, H * N))
        for t, f in enumerate(frames): s.alpha_composite(f, (0, t * H))
        s.save(os.path.join(d, 'anim.png'))
        full = []
        for f in frames:
            im = r.bg.copy(); im.alpha_composite(f); im.alpha_composite(r.fg); full.append(im)
        big = [f.resize((640, 360), Image.NEAREST).convert('RGB') for f in full]
        big[0].save(os.path.join(d, 'vorschau.gif'), save_all=True, append_images=big[1:], duration=140, loop=0)
        prev[name] = full; meta[name] = r.meta
    json.dump({'groesse': [W, H], 'anim_frames': N, 'fps': 7, 'boden_y': FLOOR,
               'hinweis': 'Ebenen: hintergrund → anim (Frame nach Zeit) → Spieler/NPCs → vordergrund. tuer = [x, y, b, h] des Ausgangs; ladenbesitzer = Fußpunkt hinter der Theke.',
               'raeume': meta}, open(os.path.join(OUT, 'innenraeume.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cols = 3; names = list(ROOMS); rows = math.ceil(len(names) / cols); out = []
    import ui
    for t in range(N):
        im = Image.new('RGB', (cols * (W + 4), rows * (H + 4)), (20, 16, 26))
        for i, n in enumerate(names):
            c = prev[n][t].copy(); ui.text(c, 10, 14, n.upper().replace('_', ' '), C('#f0e4cc'), shadow=INK)
            im.paste(c.convert('RGB'), ((i % cols) * (W + 4), (i // cols) * (H + 4)))
        out.append(im)
    out[0].save(os.path.join(g.BASE, 'preview_innenraeume.gif'), save_all=True, append_images=out[1:], duration=140, loop=0)

if __name__ == '__main__':
    main()
