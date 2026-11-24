"""Cosy pixel-art asset generator.
Erzeugt Figuren, Gebäude und Props im Stil der Cosy-Szene.
Aufruf: python3 generate.py  -> PNGs in ./characters, ./buildings, ./props, ./preview_*.png
"""
from PIL import Image, ImageDraw, ImageFont
import random, math, os

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- Palette
def C(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
def shade(c, f): return tuple(max(0, min(255, int(v*f))) for v in c[:3]) + (255,)
def mix(a, b, t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3)) + (255,)

OUTLINE   = C('#2b1e33')
MILL_ANGLE = 0        # Drehung der Windmühlenflügel (für Animation)
DOOR_OPEN = 0         # Tür-Animation: 0 = zu ... 4 = ganz offen
DOOR_LOG = None       # Liste, in die Türpositionen geschrieben werden
CUR_NIGHT = False     # Innenraum-Farbe beim Öffnen
ANIMATING = False     # True: statischer Rauch wird weggelassen (animate.py zeichnet ihn)
B_OUTLINE = C('#3a2838')
SKIN, SKIN_S, BLUSH, EYE = C('#f2c69b'), C('#d4936e'), C('#e8897a'), C('#2b1e33')
WALL      = C('#ded2be')
WOOD, WOOD_D, WOOD_L = C('#7a5236'), C('#4d3324'), C('#9c6c46')
DOORWOOD  = C('#5c3f34')
STONE     = C('#8a8296')
BRICK     = C('#8a4a44')
GLOW, GLOW_L = C('#ffd27a'), C('#fff0b8')
GLASS, GLASS_L = C('#6f93b8'), C('#b4d2ea')
GOLD      = C('#e0b048')
GOLD_L    = C('#f4d88a')
RED, CREAM = C('#b84a4a'), C('#f0e4cc')
LEAF, LEAF_D, LEAF_L = C('#4a7d4a'), C('#2f5a3c'), C('#6e9e58')
ROOFS = {
    'rot':    (C('#953a40'), C('#6e2a3a'), C('#b2524c')),
    'braun':  (C('#7a5038'), C('#563828'), C('#9a6a48')),
    'schiefer': (C('#525a7a'), C('#3a3e5c'), C('#6c789a')),
    'dunkel': (C('#4e3646'), C('#382636'), C('#6a4a5a')),
}

def new(w, h):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return img, img.load()

def put(px, x, y, c, w, h):
    if 0 <= x < w and 0 <= y < h: px[x, y] = c

def fill(img, x0, y0, x1, y1, c):
    px = img.load(); w, h = img.size
    for y in range(y0, y1+1):
        for x in range(x0, x1+1): put(px, x, y, c, w, h)

def outline(img, col=OUTLINE):
    w, h = img.size; src = img.load(); out = img.copy(); p = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
                        p[x, y] = col; break
    return out

# ================================================================ FIGUREN
W16 = 16
BODY_TOP = ['.'*16]*5 + [
    '.....' + 's'*6 + '.....',
    '....' + 's'*8 + '....',
    '....' + 's'*8 + '....',
    '....ssessess....',
    '....ssessess....',
    '....skssssks....',
    '....' + 's'*8 + '....',
    '.....' + 'S'*6 + '.....',
    '....' + 'c'*8 + '....',
    '...C' + 'c'*8 + 'C...',
    '...C' + 'c'*8 + 'C...',
    '...C' + 'l'*8 + 'C...',
]  # rows 0..16
LEGS = {
    'idle':  ['...s'+'p'*8+'s...', '....'+'p'*8+'....', '....ppp..ppp....', '....ppp..ppp....', '....bbb..bbb....', '....bbb..bbb....'],
    'walk1': ['...s'+'p'*8+'s...', '....'+'p'*8+'....', '....ppp..ppp....', '....bbb..ppp....', '....bbb..bbb....', '.........bbb....'],
    'walk2': ['...s'+'p'*8+'s...', '....'+'p'*8+'....', '....ppp..ppp....', '....ppp..bbb....', '....bbb..bbb....', '....bbb.........'],
}
DRESS = {
    'idle':  ['...s'+'d'*8+'s...', '....'+'d'*8+'....', '...'+'d'*10+'...', '...'+'d'*10+'...', '...'+'D'*10+'...', '.....bb..bb.....'],
    'walk1': ['...s'+'d'*8+'s...', '....'+'d'*8+'....', '...'+'d'*10+'...', '...'+'d'*10+'...', '...'+'D'*10+'...', '....bb.....bb...'],
    'walk2': ['...s'+'d'*8+'s...', '....'+'d'*8+'....', '...'+'d'*10+'...', '...'+'d'*10+'...', '...'+'D'*10+'...', '.....bbb.bb.....'],
}
_short_top = ['.....'+'h'*6+'.....', '....'+'h'*8+'....', '...'+'h'*10+'...', '...'+'h'*10+'...']
HAIR = {
    'kurz':    (3, _short_top + ['...'+'h'*6+'..hh...', '...hh......hh...', '...h........h...']),
    'lang':    (3, _short_top + ['...hhhh..hhhh...'] + ['...hh......hh...']*8 + ['...h........h...']),
    'dutt':    (1, ['......hhhh......', '......hhhh......', '.....'+'h'*6+'.....', '....'+'h'*8+'....',
                    '...'+'h'*10+'...', '...hhh'+'.'*4+'hhh...', '...hh'+'.'*6+'hh...', '...h'+'.'*8+'h...']),
    'zoepfe':  (3, _short_top + ['...'+'h'*10+'...', '..hhh......hhh..', '.hh'+'.'*10+'hh.', '.hh'+'.'*10+'hh.',
                                  '.hh'+'.'*10+'hh.', '..h'+'.'*10+'h..']),
    'glatze':  (5, []),
}
BEARD = (10, ['....f......f....', '....'+'f'*8+'....', '....'+'f'*8+'....', '.....'+'f'*6+'.....', '......ffff......'])
HATS = {
    'hut':     (1, ['.....'+'t'*6+'.....', '....'+'t'*8+'....', '....'+'T'*8+'....', '..'+'t'*12+'..']),
    'koch':    (0, ['....'+'t'*8+'....', '...'+'t'*10+'...', '...'+'t'*10+'...', '....'+'t'*8+'....', '....'+'T'*8+'....']),
    'muetze':  (1, ['.......TT.......', '.....'+'t'*6+'.....', '....'+'t'*8+'....', '...'+'T'*10+'...']),
    'stroh':   (1, ['.....'+'t'*6+'.....', '....'+'t'*8+'....', '....'+'T'*8+'....', '.'+'t'*14+'.']),
    'kapuze':  (3, ['.....'+'t'*6+'.....', '....'+'t'*8+'....', '...'+'t'*10+'...', '...'+'t'*10+'...',
                    '...tt'+'.'*6+'tt...'] + ['...t'+'.'*8+'t...']*5 + ['...'+'t'*10+'...']),
    'suedwester': (3, ['.....'+'t'*6+'.....', '....'+'t'*8+'....', '..'+'t'*12+'..', '..tt'+'.'*8+'tt..', '..t'+'.'*10+'t..']),
}
EXTRAS = {
    'schuerze': (14, ['.....'+'a'*6+'.....']*2 + ['....'+'a'*8+'....']*5),
    'latz':     (13, ['.....a....a.....'] + ['.....'+'a'*6+'.....']*3),
    'tuch':     (13, ['...'+'a'*10+'...', '...'+'a'*10+'...', '.....'+'a'*6+'.....', '......aaaa......']),
    'schal':    (12, ['....'+'a'*8+'....', '....'+'a'*8+'....', '.........aa.....']),
}

CHARACTERS = [
    dict(name='abenteurer', title='Abenteurer', hair=('kurz', C('#c0603a')), hat=('hut', C('#7a5236'), C('#4d3324')),
         c=C('#4a6aa0'), l=C('#4d3324'), p=C('#6b4a34'), b=C('#3b2a2a'), extra=('schal', C('#b84a4a'))),
    dict(name='baeckerin', title='Bäckerin', hair=('lang', C('#e8c070')), hat=('koch', C('#f4ede0'), C('#d0c6b6')),
         c=C('#d88a9a'), d=C('#c9a27a'), b=C('#5a3a30'), extra=('schuerze', C('#f4ede0'))),
    dict(name='schmied', title='Schmied', hair=('glatze', None), beard=C('#5a3a2a'),
         c=C('#7a7a8a'), l=C('#4d3324'), p=C('#3e3a4a'), b=C('#2a2228'), extra=('schuerze', C('#7a4e30'))),
    dict(name='oma', title='Oma Ilse', hair=('dutt', C('#c8c4d0')),
         c=C('#9a86b8'), d=C('#6a4e8a'), b=C('#4a3040'), extra=('tuch', C('#b8667a'))),
    dict(name='gaertner', title='Gärtner', hair=('kurz', C('#6a4a30')), hat=('stroh', C('#e0c070'), C('#b84a4a')),
         c=C('#e8dcc0'), l=C('#4f7a45'), p=C('#4f7a45'), b=C('#5a3a30'), extra=('latz', C('#4f7a45'))),
    dict(name='kind', title='Kind', hair=('zoepfe', C('#4a3020')),
         c=C('#e8c050'), d=C('#3f8a8a'), b=C('#a84a4a')),
    dict(name='haendler', title='Händler', hair=('kurz', C('#3a2a3a')), hat=('kapuze', C('#5a3a7a'), C('#4a2a6a')),
         c=C('#5a3a7a'), l=GOLD, d=C('#5a3a7a'), b=C('#2a2228')),
    dict(name='fischer', title='Fischer', hair=('kurz', C('#b0aab8')), beard=C('#b0aab8'),
         hat=('suedwester', C('#e8b830'), C('#c09020')), c=C('#e8b830'), l=C('#c09020'), p=C('#2e3a5a'), b=C('#2a2228')),
]

def paint_rows(px, start, rows, pal):
    for dy, row in enumerate(rows):
        assert len(row) == 16, (row, len(row))
        for x, ch in enumerate(row):
            if ch in pal and pal[ch] is not None:
                px[x+1, start+dy+1] = pal[ch]

def make_character(cfg, frame):
    img, px = new(18, 26)
    c = cfg['c']
    pal = {'s': SKIN, 'S': SKIN_S, 'k': BLUSH, 'e': EYE, 'c': c, 'C': shade(c, .82),
           'l': cfg.get('l', c), 'p': cfg.get('p'), 'b': cfg['b'],
           'd': cfg.get('d'), 'D': shade(cfg['d'], .8) if cfg.get('d') else None}
    paint_rows(px, 0, BODY_TOP, pal)
    paint_rows(px, 17, (DRESS if cfg.get('d') else LEGS)[frame], pal)
    if 'extra' in cfg:
        s, rows = EXTRAS[cfg['extra'][0]]; paint_rows(px, s, rows, {'a': cfg['extra'][1]})
    hs, hc = cfg['hair']
    if hc is not None:
        s, rows = HAIR[hs]; paint_rows(px, s, rows, {'h': hc})
    if 'beard' in cfg:
        paint_rows(px, BEARD[0], BEARD[1], {'f': cfg['beard']})
    if 'hat' in cfg:
        n, t, T = cfg['hat']; s, rows = HATS[n]; paint_rows(px, s, rows, {'t': t, 'T': T})
    # Licht von links: rechte Kanten abdunkeln, linke leicht aufhellen
    src = img.copy().load()
    for y in range(26):
        for x in range(18):
            if src[x, y][3] and src[x, y] not in (EYE,):
                if x+1 < 18 and src[x+1, y][3] == 0: px[x, y] = shade(src[x, y], .85)
                elif x-1 >= 0 and src[x-1, y][3] == 0: px[x, y] = mix(src[x, y], (255, 255, 255, 255), .12)
    return outline(img)

# ================================================================ GEBÄUDE
def door_panel(cv, x, y, w, h, col=None, arch='both', hinge='left', bands=()):
    """Türblatt im Zustand DOOR_OPEN (0..4). Scharnier links oder rechts."""
    col = col or DOORWOOD
    if DOOR_LOG is not None: DOOR_LOG.append((x, y, w, h))
    k = DOOR_OPEN; f = k / 4
    def cut(xx, yy):
        if arch == 'both': return yy == y and xx in (x, x+w-1)
        if arch == 'l2': return (yy == y and xx <= x+1) or (yy == y+1 and xx == x)
        if arch == 'r2': return (yy == y and xx >= x+w-2) or (yy == y+1 and xx == x+w-1)
        return False
    if k:
        for yy in range(y, y+h):
            t = (yy-y) / max(1, h-1)
            if CUR_NIGHT: c = mix(C('#b8703a'), C('#ffd27a'), t)
            else: c = C('#3e2c30') if yy >= y+h-2 else mix(C('#1e1520'), C('#2e2028'), t)
            for xx in range(x, x+w):
                if not cut(xx, yy): cv.set(xx, yy, c)
    dw = w if k == 0 else max(1, round(w * (1 - f)))
    x0 = x if hinge == 'left' else x + w - dw
    pc = shade(col, 1 - .3*f)
    for yy in range(y, y+h):
        for i in range(dw):
            xx = x0 + i
            if cut(xx, yy): continue
            oi = int((i if hinge == 'left' else dw-1-i) * w / dw)
            cv.set(xx, yy, shade(pc, .75) if (oi % 3 == 2 or (k == 4)) else pc)
    for b in bands: cv.rect(x0, y+b, x0+dw-1, y+b, C('#3a3446'))
    if dw >= 4:
        kx = x0 + dw - 3 if hinge == 'left' else x0 + 2
        cv.set(kx, y+h//2, GOLD)

class Canvas:
    def __init__(self, w, h, seed=1):
        self.img, self.px = new(w, h); self.w, self.h = w, h; self.rng = random.Random(seed)
    def set(self, x, y, c): put(self.px, x, y, c, self.w, self.h)
    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1+1):
            for x in range(x0, x1+1): self.set(x, y, c)
    def plaster(self, x0, y0, x1, y1, base=WALL):
        self.rect(x0, y0, x1, y1, base)
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                if self.rng.random() < .06: self.set(x, y, shade(base, .93))
        self.rect(x1, y0, x1, y1, shade(base, .86)); self.rect(x0, y0, x0, y1, mix(base, (255,)*4, .15))
    def stones(self, x0, y0, x1, y1, base=STONE, rh=3):
        self.rect(x0, y0, x1, y1, shade(base, .68))
        for i, y in enumerate(range(y0, y1+1, rh)):
            x = x0 - (i % 2) * 3
            while x <= x1:
                bw = self.rng.randint(4, 7); col = shade(base, self.rng.uniform(.9, 1.1))
                for yy in range(y, min(y+rh-1, y1+1)):
                    for xx in range(max(x, x0), min(x+bw-1, x1+1)): self.set(xx, yy, col)
                if x >= x0: self.set(x, y, mix(col, (255,)*4, .2))
                x += bw
    def planks(self, x0, y0, x1, y1, base, pw=3, vertical=True):
        self.rect(x0, y0, x1, y1, base)
        rng = range(x0, x1+1) if vertical else range(y0, y1+1)
        for i in rng:
            if (i - (x0 if vertical else y0)) % pw == pw-1:
                if vertical: self.rect(i, y0, i, y1, shade(base, .7))
                else: self.rect(x0, i, x1, i, shade(base, .7))
        for _ in range((x1-x0)*(y1-y0)//25):
            self.set(self.rng.randint(x0, x1), self.rng.randint(y0, y1), mix(base, (255,)*4, .15))
    def roof(self, xl, xr, y0, y1, inset, style='rot', rows=3):
        col, dark, light = ROOFS[style]
        for y in range(y0, y1+1):
            t = (y-y0) / max(1, y1-y0)
            a, b = round(xl + inset*(1-t)), round(xr - inset*(1-t))
            for x in range(a, b+1):
                c = col
                if (y-y0) % rows == rows-1 and (x + (y//rows)*2) % 5: c = dark
                if x == a: c = light
                elif x == b: c = dark
                self.set(x, y, c)
            if y == y0: self.rect(a, y, b, y, light)
        a, b = xl, xr
        self.rect(a, y1, b, y1, shade(dark, .85))
    def window(self, x, y, w, h, night, box=False, frame=WOOD_D):
        self.rect(x, y, x+w-1, y+h-1, frame)
        for yy in range(y+1, y+h-1):
            for xx in range(x+1, x+w-1):
                if night: c = GLOW_L if (xx-x)+(yy-y) < (w+h)//3 else GLOW
                else:
                    c = mix(GLASS_L, GLASS, (yy-y)/h)
                    if (xx-x) - (yy-y) in (1, 2) and yy < y+h//2: c = GLASS_L
                self.set(xx, yy, c)
        self.rect(x+w//2, y, x+w//2, y+h-1, frame); self.rect(x, y+h//2, x+w-1, y+h//2, frame)
        self.rect(x-1, y+h, x+w, y+h, WOOD_L)
        if box:
            self.rect(x, y+h+1, x+w-1, y+h+3, WOOD)
            for xx in range(x, x+w):
                self.set(xx, y+h, LEAF if xx % 2 else LEAF_D)
                if xx % 3 == 1: self.set(xx, y+h-1, [RED, C('#e888a8'), GOLD][xx % 3 and (xx//3) % 3])
    def door(self, x, y, w, h, col=DOORWOOD, arch=True, hinge='left', bands=()):
        self.rect(x-1, y-1, x+w, y+h-1, WOOD_D)
        door_panel(self, x, y, w, h, col, 'both' if arch else None, hinge, bands)
    def glow(self, rects, col=GLOW):
        src = self.img.copy().load()
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3] == 0: continue
                d = 99
                for (rx, ry, rw, rh) in rects:
                    if rx <= x < rx+rw and ry <= y < ry+rh: d = -1; break
                    dx = max(rx-x, 0, x-(rx+rw-1)); dy = max(ry-y, 0, y-(ry+rh-1))
                    d = min(d, max(dx, dy) + min(dx, dy)//2)
                if d < 0: continue
                if d <= 3 and (x+y) % 2 == 0: self.px[x, y] = mix(src[x, y], col, .55)
                elif d <= 7 and x % 2 == 0 and y % 2 == 0: self.px[x, y] = mix(src[x, y], col, .45)
                elif d <= 11 and x % 4 == 0 and y % 4 == 0: self.px[x, y] = mix(src[x, y], col, .35)
    def done(self): return outline(self.img, B_OUTLINE)

def chimney(cv, x0, y0, x1, y1, base=BRICK):
    cv.stones(x0, y0+1, x1, y1, base, rh=2); cv.rect(x0-1, y0, x1+1, y0, shade(base, .6))

def cottage(night):
    cv = Canvas(76, 66, 3)
    chimney(cv, 50, 6, 56, 26)
    cv.plaster(12, 34, 63, 61)
    cv.roof(4, 71, 14, 36, 12, 'rot')
    cv.rect(13, 37, 62, 38, shade(WALL, .82))
    cv.stones(11, 60, 64, 64)
    cv.door(18, 44, 9, 16)
    cv.window(38, 42, 14, 12, night, box=True)
    if night: cv.glow([(38, 42, 14, 12)])
    return cv.done()

def baeckerei(night):
    cv = Canvas(86, 80, 5)
    chimney(cv, 58, 2, 63, 18)
    cv.plaster(12, 26, 71, 77, C('#ead9bc'))
    beam = WOOD_D
    for y in (26, 27, 50, 51): cv.rect(12, y, 71, y, beam)
    for x in (12, 13, 41, 42, 70, 71): cv.rect(x, 26, x, 77, beam)
    d = ImageDraw.Draw(cv.img)
    for a, b in (((14, 49), (24, 28)), ((39, 49), (29, 28)), ((44, 49), (54, 28)), ((69, 49), (59, 28))):
        d.line([a, b], fill=beam, width=1)
    cv.roof(5, 78, 2, 28, 30, 'braun')
    cv.window(38, 12, 8, 7, night)
    cv.rect(13, 28, 70, 29, shade(C('#ead9bc'), .8))
    cv.window(19, 34, 12, 11, night, box=True); cv.window(53, 34, 12, 11, night, box=True)
    cv.window(16, 60, 22, 13, night)
    cv.door(48, 58, 10, 18)
    # Markise
    for x in range(14, 40):
        for y in range(53, 58): cv.set(x, y, RED if (x//3) % 2 else CREAM)
        if x % 2: cv.set(x, 58, RED if (x//3) % 2 else CREAM)
    cv.rect(14, 53, 39, 53, shade(RED, .8))
    # Schild mit Brezel
    cv.rect(71, 54, 80, 54, WOOD_D); cv.set(73, 55, WOOD_D); cv.set(78, 55, WOOD_D)
    cv.rect(72, 56, 80, 64, WOOD); cv.rect(72, 64, 80, 64, WOOD_D)
    for (x, y) in ((74, 58), (75, 57), (77, 57), (78, 58), (78, 59), (77, 60), (76, 59), (75, 60), (74, 59), (76, 61), (76, 62)):
        cv.set(x, y, GOLD)
    cv.stones(11, 77, 72, 79)
    if night: cv.glow([(38, 12, 8, 7), (19, 34, 12, 11), (53, 34, 12, 11), (16, 60, 22, 13)])
    return cv.done()

def schmiede(night):
    cv = Canvas(88, 66, 7)
    chimney(cv, 62, 2, 71, 24, STONE)
    cv.stones(8, 30, 79, 63)
    cv.roof(2, 85, 10, 32, 10, 'schiefer')
    cv.rect(9, 33, 78, 34, shade(STONE, .6))
    # offene Esse
    cv.rect(13, 39, 38, 63, WOOD_D)
    cv.rect(14, 40, 37, 63, C('#241a22'))
    cv.stones(17, 52, 34, 63, C('#5a5464'))
    for x in range(19, 33):
        cv.set(x, 51, C('#ff9a3c') if x % 2 else C('#ffd27a'))
        if x % 3: cv.set(x, 50, C('#e8603a'))
    for (x, y) in ((22, 48), (26, 47), (29, 49), (24, 45)): cv.set(x, y, C('#ffb050'))
    cv.window(50, 41, 12, 10, night)
    # Schild mit Amboss
    cv.rect(19, 34, 32, 38, WOOD); cv.rect(19, 38, 32, 38, WOOD_D)
    cv.rect(22, 35, 29, 35, C('#cfd2dc')); cv.rect(24, 36, 27, 36, C('#cfd2dc')); cv.rect(23, 37, 28, 37, C('#cfd2dc'))
    rects = [(19, 47, 15, 6)] + ([(50, 41, 12, 10)] if night else [])
    cv.glow(rects, C('#ff9a4a'))
    return cv.done()

def scheune(night):
    cv = Canvas(84, 72, 9)
    red = C('#9a3e3a')
    for y in range(10, 70):
        t = min(1, (y-10)/22); half = round(4 + (34-4)*t)
        for x in range(42-half, 42+half):
            c = shade(red, .72) if (x % 4 == 3) else red
            if cv.rng.random() < .05: c = mix(red, (255,)*4, .15)
            cv.set(x, y, c)
    trim = C('#e8e0d0')
    d = ImageDraw.Draw(cv.img); dark, mid, lt = ROOFS['dunkel']
    for k in range(7):
        col = [lt, lt, mid, mid, dark, mid, dark][k]
        d.line([(40, 6+k), (2, 34+k)], fill=col); d.line([(43, 6+k), (81, 34+k)], fill=col)
    cv.rect(39, 5, 44, 9, lt)
    cv.rect(36, 16, 47, 27, trim); cv.rect(37, 17, 46, 26, C('#3a2630'))
    if night: cv.rect(38, 18, 45, 25, C('#5a4030'))
    cv.rect(24, 40, 59, 69, trim)
    for (x0, x1) in ((25, 41), (42, 58)):
        cv.rect(x0, 41, x1, 69, shade(red, .85))
        d.line([(x0, 41), (x1, 69)], fill=trim); d.line([(x1, 41), (x0, 69)], fill=trim)
    cv.rect(41, 41, 42, 69, trim)
    return cv.done()

def windmuehle(night):
    cv = Canvas(74, 102, 11)
    for y in range(40, 99):
        t = (y-40)/58; half = round(8 + 6*t)
        for x in range(37-half, 37+half):
            c = WALL
            if x == 37-half: c = mix(WALL, (255,)*4, .15)
            elif x >= 37+half-2: c = shade(WALL, .86)
            elif cv.rng.random() < .06: c = shade(WALL, .93)
            cv.set(x, y, c)
    cv.stones(21, 94, 52, 100)
    cv.door(33, 82, 8, 12)
    cv.window(33, 62, 7, 8, night)
    cv.roof(26, 47, 26, 42, 9, 'braun')
    cx, cy = 37, 36
    for ang in (45+MILL_ANGLE, 135+MILL_ANGLE, 225+MILL_ANGLE, 315+MILL_ANGLE):
        a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
        r = 5.0
        while r <= 33:
            o = 0.0
            while o <= 6.5:
                x = round(cx + r*ca - o*sa); y = round(cy + r*sa + o*ca)
                if o < 1: c = WOOD_D
                elif int(r) % 4 == 0 or int(o) % 3 == 0: c = WOOD
                else: c = CREAM
                if o >= 1 and r < 9: o += .5; continue
                cv.set(x, y, c); o += .5
            r += .5
    cv.rect(cx-2, cy-2, cx+2, cy+2, WOOD_D); cv.set(cx, cy, GOLD)
    if night: cv.glow([(33, 62, 7, 8)])
    return cv.done()

def marktstand(night):
    cv = Canvas(58, 50, 13)
    cv.rect(6, 10, 7, 47, WOOD); cv.rect(49, 10, 50, 47, WOOD)
    cv.rect(7, 10, 7, 47, WOOD_D); cv.rect(50, 10, 50, 47, WOOD_D)
    for x in range(2, 56):
        for y in range(5, 14): cv.set(x, y, RED if (x//4) % 2 else CREAM)
        if (x % 4) in (1, 2): cv.set(x, 14, RED if (x//4) % 2 else CREAM)
    cv.rect(2, 5, 55, 5, shade(RED, .8)); cv.rect(4, 3, 53, 4, shade(RED, .7))
    cv.planks(4, 31, 53, 47, WOOD, pw=3, vertical=False)
    cv.rect(3, 30, 54, 30, WOOD_L)
    for i, (fx, col) in enumerate(((8, RED), (22, C('#e88a3a')), (36, C('#6a9a55')))):
        cv.planks(fx, 25, fx+12, 29, WOOD_L, pw=4)
        for k in range(6):
            x = fx + 1 + k*2; cv.set(x, 24, col); cv.set(x+1, 24, shade(col, .8)); cv.set(x, 23, mix(col, (255,)*4, .3) if k % 2 else col)
    cv.rect(44, 18, 51, 22, CREAM); cv.rect(45, 20, 50, 20, WOOD_D)
    return cv.done()

def brunnen(night):
    cv = Canvas(36, 44, 15)
    cv.rect(7, 10, 8, 33, WOOD); cv.rect(27, 10, 28, 33, WOOD)
    cv.rect(7, 16, 28, 17, WOOD_D)
    cv.rect(17, 18, 17, 24, C('#c8b898'))
    cv.rect(15, 25, 19, 29, WOOD); cv.rect(15, 25, 19, 25, WOOD_D)
    cv.roof(2, 33, 3, 12, 13, 'rot', rows=2)
    cv.stones(4, 31, 31, 42)
    cv.rect(3, 30, 32, 31, shade(STONE, 1.15))
    return cv.done()

def taverne(night):
    cv = Canvas(98, 90, 17)
    chimney(cv, 16, 2, 22, 20); chimney(cv, 74, 0, 80, 18)
    cv.stones(10, 56, 85, 87)
    cv.planks(8, 30, 87, 55, C('#8a5e3e'), pw=3, vertical=False)
    cv.rect(8, 55, 87, 56, WOOD_D)
    cv.roof(2, 93, 8, 32, 14, 'rot')
    cv.rect(9, 33, 86, 34, shade(C('#8a5e3e'), .7))
    wins = []
    for x in (18, 42, 66):
        cv.window(x, 37, 12, 11, night, box=True); wins.append((x, 37, 12, 11))
    cv.window(18, 64, 14, 12, night); cv.window(64, 64, 14, 12, night)
    wins += [(18, 64, 14, 12), (64, 64, 14, 12)]
    cv.door(42, 66, 6, 20); cv.door(48, 66, 6, 20, hinge='right')
    cv.rect(41, 63, 55, 64, WOOD_D)
    # Laterne
    cv.rect(37, 66, 39, 70, WOOD_D); cv.rect(38, 67, 38, 69, GLOW_L if night else C('#e8d8a0'))
    # Schild mit Krug
    cv.rect(86, 47, 96, 47, WOOD_D); cv.set(88, 48, WOOD_D); cv.set(94, 48, WOOD_D)
    cv.rect(87, 49, 96, 58, WOOD); cv.rect(87, 58, 96, 58, WOOD_D)
    cv.rect(89, 51, 93, 56, GOLD); cv.rect(89, 51, 93, 51, CREAM); cv.set(94, 52, GOLD); cv.set(95, 53, GOLD); cv.set(94, 55, GOLD); cv.set(95, 54, GOLD)
    if night: cv.glow(wins + [(37, 66, 3, 5)])
    return cv.done()

def gilde(night, kind='abenteuer'):
    cv = Canvas(110, 114, 31)
    d = ImageDraw.Draw(cv.img)
    plaster, beam = C('#ead9bc'), WOOD_D
    BANNER, BANNER_D, CREST, ROOF = {
        'abenteuer': (C('#a8383e'), C('#7a2834'), C('#3a5a9a'), 'rot'),
        'handel':    (C('#3f7a52'), C('#2c5a3c'), C('#2f6a4a'), 'braun')}[kind]
    # Flügel links/rechts
    for (x0, x1) in ((6, 44), (65, 103)):
        cv.plaster(x0, 46, x1, 79, plaster)
        for y in (46, 47, 78, 79): cv.rect(x0, y, x1, y, beam)
        for x in (x0, x0+1, x1-1, x1, (x0+x1)//2): cv.rect(x, 46, x, 79, beam)
        cv.stones(x0, 80, x1, 110)
    for (xl, xr) in ((2, 48), (61, 107)):
        cv.roof(xl, xr, 30, 49, 9, ROOF)
    cv.rect(7, 50, 43, 51, shade(plaster, .8)); cv.rect(66, 50, 102, 51, shade(plaster, .8))
    wins = []
    for x in (11, 30, 70, 89):
        cv.window(x, 56, 10, 10, night, box=True); wins.append((x, 56, 10, 10))
    for x in (18, 80):
        cv.window(x, 86, 12, 12, night); wins.append((x, 86, 12, 12))
    # Turm
    cv.stones(42, 26, 67, 110, C('#948ca2'))
    cv.rect(41, 28, 68, 29, shade(STONE, .6))
    cv.roof(37, 72, 8, 29, 16, 'schiefer')
    cv.rect(54, 0, 54, 9, C('#3a3446'))
    for i, y in enumerate(range(1, 6)): cv.rect(55, y, 55 + 5 - abs(i-2)*2, y, BANNER)
    cv.set(54, 0, GOLD)
    cv.window(51, 34, 8, 10, night); wins.append((51, 34, 8, 10))
    cv.rect(50, 33, 59, 33, shade(STONE, .7))
    # Banner
    for bx in (44, 61):
        cv.rect(bx-1, 48, bx+5, 48, WOOD_D)
        for y in range(49, 67):
            for x in range(bx, bx+5):
                if y >= 64 and abs(x - (bx+2)) < (y-63): continue
                cv.set(x, y, BANNER_D if x == bx+4 else BANNER)
        cv.rect(bx+1, 54, bx+3, 56, GOLD); cv.set(bx+2, 55, BANNER)
    # Wappen
    for y in range(64, 80):
        cut = max(0, (y-74)*2)
        for x in range(50+cut//2, 60-cut//2):
            edge = (x in (50+cut//2, 59-cut//2)) or y in (64, 79) or (y >= 74 and (x == 50+cut//2 or x == 59-cut//2))
            cv.set(x, y, GOLD if edge else CREST)
    if kind == 'abenteuer':   # gekreuzte Schwerter
        silver = C('#d8dce6')
        d.line([(52, 66), (58, 74)], fill=silver); d.line([(57, 66), (51, 74)], fill=silver)
        cv.rect(51, 72, 53, 72, GOLD); cv.rect(56, 72, 58, 72, GOLD)
    else:                     # Goldmünze
        for y in range(65, 76):
            for x in range(50, 60):
                r = ((x-54.5)**2 + (y-70)**2) ** .5
                if r <= 4.3: cv.set(x, y, shade(GOLD, .7) if r > 3.4 else GOLD_L if (x < 54 and y < 70) else GOLD)
        cv.rect(54, 68, 55, 72, shade(GOLD, .7))
    # Tor
    cv.rect(46, 86, 63, 87, WOOD_D)
    cv.door(47, 89, 8, 21, arch=False, bands=(5, 15)); cv.door(55, 89, 8, 21, arch=False, hinge='right', bands=(5, 15))
    cv.rect(47, 88, 62, 88, WOOD_D); cv.rect(48, 87, 61, 87, WOOD_D)
    # Fackeln
    for tx in (44, 65):
        cv.rect(tx, 92, tx, 97, WOOD_D); cv.set(tx, 91, C('#ff9a3c')); cv.set(tx, 90, C('#ffd27a'))
    cv.stones(43, 110, 66, 113, C('#a29ab0'))
    if kind == 'handel':      # Waren vor dem Haus
        for (x0, y0) in ((31, 101), (34, 94), (70, 101)):
            cv.rect(x0, y0, x0+8, y0+7, WOOD_L); cv.rect(x0, y0, x0+8, y0, WOOD)
            cv.rect(x0, y0+7, x0+8, y0+7, WOOD_D); cv.rect(x0+8, y0, x0+8, y0+7, WOOD_D)
            d.line([(x0+1, y0+6), (x0+7, y0+1)], fill=WOOD)
        for (x0, col) in ((80, C('#d8c8a0')), (86, C('#c8b890'))):   # Säcke
            for y in range(102, 109):
                hw = 2 if y < 104 else 3
                cv.rect(x0+3-hw, y, x0+3+hw, y, col)
            cv.rect(x0+2, 101, x0+4, 101, shade(col, .7))
    if night: cv.glow(wins + [(44, 89, 1, 3), (65, 89, 1, 3)])
    return cv.done()

STAINED = [C('#4a6aa8'), C('#a8383e'), C('#e0b048'), C('#4f8a5a')]

def arch_window(cv, x0, y0, w, h, night, stained=True):
    for y in range(y0, y0+h):
        cut = 2 if y == y0 else 1 if y == y0+1 else 0
        for x in range(x0+cut, x0+w-cut):
            border = x in (x0+cut, x0+w-1-cut) or y in (y0, y0+h-1) or (y == y0+1 and cut)
            if border: c = WOOD_D if not stained else C('#3a3446')
            elif (y-y0) % 4 == 3 or x == x0 + w//2: c = C('#3a3446')
            else:
                c = STAINED[((x-x0)//2 + (y-y0)//4) % 4]
                if night: c = mix(c, GLOW_L, .45)
            cv.set(x, y, c)
    cv.rect(x0-1, y0+h, x0+w, y0+h, shade(STONE, 1.15))

def kirche(night):
    cv = Canvas(98, 132, 37)
    d = ImageDraw.Draw(cv.img)
    # Kirchenschiff
    cv.plaster(36, 68, 93, 125, C('#e6e0d4'))
    cv.stones(36, 119, 93, 126)
    cv.roof(32, 96, 48, 70, 8, 'rot')
    cv.rect(37, 71, 92, 72, shade(C('#e6e0d4'), .82))
    wins = []
    for x in (45, 61, 77):
        arch_window(cv, x, 80, 9, 26, night); wins.append((x, 80, 9, 26))
    # Turm
    cv.stones(12, 34, 35, 126, C('#948ca2'))
    cv.roof(9, 38, 10, 36, 14, 'schiefer')
    for y in (38, 39, 72, 73): cv.rect(11, y, 36, y, shade(STONE, .6))
    cv.rect(23, 1, 24, 10, GOLD); cv.rect(20, 4, 27, 5, GOLD)            # Kreuz
    # Glockenstube
    for y in range(43, 57):
        cut = 2 if y == 43 else 1 if y == 44 else 0
        cv.rect(17+cut, y, 30-cut, y, C('#241a22'))
    cv.rect(21, 47, 26, 47, GOLD); cv.rect(20, 48, 27, 52, GOLD); cv.rect(19, 53, 28, 53, GOLD)
    cv.rect(21, 48, 21, 51, GOLD_L); cv.rect(23, 54, 24, 54, C('#b08030'))
    cv.rect(23, 45, 24, 46, WOOD_D)
    cv.rect(16, 57, 31, 57, shade(STONE, 1.15))
    # Uhr
    for y in range(58, 70):
        for x in range(17, 31):
            r = ((x-23.5)**2 + (y-63.5)**2) ** .5
            if r <= 5.6: cv.set(x, y, C('#3a3446') if r > 4.6 else CREAM)
    cv.rect(23, 60, 23, 63, C('#3a3446')); cv.rect(24, 63, 26, 63, C('#3a3446'))
    for (x, y) in ((23, 59), (28, 63), (23, 68), (19, 63)): cv.set(x, y, GOLD)
    # Turmfenster + Tor
    arch_window(cv, 20, 78, 8, 14, night); wins.append((20, 78, 8, 14))
    for y in range(100, 126):
        cut = 3 if y == 100 else 2 if y == 101 else 1 if y == 102 else 0
        cv.rect(16+cut, y, 31-cut, y, WOOD_D)
    door_panel(cv, 17, 102, 7, 24, DOORWOOD, 'l2', 'left', bands=(6, 17))
    door_panel(cv, 24, 102, 7, 24, DOORWOOD, 'r2', 'right', bands=(6, 17))
    cv.stones(12, 126, 36, 131, C('#a29ab0'))
    if night: cv.glow(wins)
    return cv.done()

BUILDINGS = [('cottage', 'Cottage', cottage), ('baeckerei', 'Bäckerei', baeckerei), ('schmiede', 'Schmiede', schmiede),
             ('taverne', 'Taverne', taverne), ('scheune', 'Scheune', scheune), ('windmuehle', 'Windmühle', windmuehle),
             ('marktstand', 'Marktstand', marktstand), ('brunnen', 'Brunnen', brunnen), ('gilde_abenteuer', 'Abenteurergilde', lambda n: gilde(n, 'abenteuer')),
             ('gilde_handel', 'Handelsgilde', lambda n: gilde(n, 'handel')), ('kirche', 'Kirche', kirche)]

# ================================================================ PROPS
def baum(night):
    cv = Canvas(42, 50, 21)
    cv.rect(18, 28, 22, 49, WOOD); cv.rect(22, 28, 22, 49, WOOD_D); cv.rect(18, 28, 18, 49, WOOD_L)
    cv.rect(16, 48, 24, 49, WOOD)
    blobs = [(21, 16, 14), (10, 24, 9), (32, 24, 9), (21, 28, 9)]
    for y in range(50):
        for x in range(42):
            best = None
            for bx, by, r in blobs:
                if (x-bx)**2 + (y-by)**2 <= r*r:
                    lv = ((x-bx+r*.4)**2 + (y-by+r*.4)**2) ** .5 / r
                    best = lv if best is None else min(best, lv)
            if best is None: continue
            c = LEAF_L if best < .45 else LEAF if best < .9 else LEAF_D
            if .4 < best < .5 and (x+y) % 2: c = LEAF
            if .85 < best < .95 and (x+y) % 2: c = LEAF_D
            cv.set(x, y, c)
    for (x, y) in ((14, 12), (26, 9), (8, 22), (30, 20), (20, 22)):
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): cv.set(x+dx, y+dy, C('#8ab868'))
    return cv.done()

def tanne(night):
    cv = Canvas(26, 44, 22)
    cv.rect(12, 36, 14, 43, WOOD_D)
    for (top, bot, hw) in ((2, 16, 7), (9, 26, 10), (18, 37, 12)):
        for y in range(top, bot+1):
            half = round(hw * (y-top)/(bot-top))
            for x in range(13-half, 13+half+1):
                c = LEAF_D if x > 13 else C('#3c6a46')
                if y == bot: c = shade(LEAF_D, .8)
                cv.set(x, y, c)
    return cv.done()

def busch(night):
    cv = Canvas(24, 14, 23)
    for y in range(14):
        for x in range(24):
            for bx, by, r in ((7, 8, 6), (15, 7, 7), (20, 10, 4)):
                if (x-bx)**2 + (y-by)**2 <= r*r:
                    cv.set(x, y, LEAF_L if (y < by-2 and x < bx) else LEAF if y < by+3 else LEAF_D)
    for x in (6, 13, 17): cv.set(x, 5, C('#e888a8'))
    return cv.done()

def fass(night):
    cv = Canvas(14, 16, 24)
    for y in range(1, 15):
        half = 5 + (1 if 4 <= y <= 11 else 0)
        for x in range(7-half, 7+half):
            cv.set(x, y, WOOD_D if x == 7+half-1 or (x-1) % 3 == 0 else WOOD)
    for y in (3, 12): cv.rect(1, y, 12, y, C('#5a5a6a'))
    cv.rect(2, 1, 11, 1, WOOD_L)
    return cv.done()

def kiste(night):
    cv = Canvas(14, 14, 25)
    cv.planks(1, 1, 12, 12, WOOD_L, pw=4, vertical=False)
    cv.rect(1, 1, 12, 1, WOOD); cv.rect(1, 12, 12, 12, WOOD_D); cv.rect(1, 1, 1, 12, WOOD); cv.rect(12, 1, 12, 12, WOOD_D)
    ImageDraw.Draw(cv.img).line([(2, 11), (11, 2)], fill=WOOD)
    return cv.done()

def laterne(night):
    cv = Canvas(12, 30, 26)
    cv.rect(5, 8, 6, 29, C('#3a3446')); cv.rect(3, 28, 8, 29, C('#3a3446'))
    cv.rect(3, 1, 8, 1, C('#3a3446')); cv.rect(2, 2, 9, 2, C('#3a3446'))
    cv.rect(3, 3, 8, 7, C('#3a3446')); cv.rect(4, 3, 7, 6, GLOW_L if night else C('#c8c0a0'))
    if night: cv.glow([(4, 3, 4, 4)])
    return cv.done()

def schild(night):
    cv = Canvas(20, 22, 27)
    cv.rect(9, 8, 10, 21, WOOD_D)
    cv.rect(1, 1, 18, 10, WOOD); cv.rect(1, 10, 18, 10, WOOD_D); cv.rect(1, 1, 18, 1, WOOD_L)
    for y in (4, 7): cv.rect(4, y, 15, y, WOOD_D)
    return cv.done()

def zaun(night):
    cv = Canvas(26, 16, 28)
    for x in (1, 12, 23): cv.rect(x, 1, x+1, 15, WOOD); cv.set(x+1, 1, WOOD_D)
    for y in (4, 10): cv.rect(0, y, 25, y+1, WOOD_L); cv.rect(0, y+1, 25, y+1, WOOD)
    return cv.done()

def beet(night):
    cv = Canvas(26, 10, 29)
    cv.rect(0, 3, 25, 9, C('#4a2e2a'))
    for x in range(1, 25, 2):
        cv.set(x, 4 + (x % 4)//2, C('#5e3c34'))
    for x in (3, 9, 15, 21):
        cv.set(x, 2, LEAF); cv.set(x-1, 1, LEAF_L); cv.set(x+1, 1, LEAF); cv.set(x, 3, LEAF_D)
    return cv.done()

PROPS = [('baum', 'Baum', baum), ('tanne', 'Tanne', tanne), ('busch', 'Busch', busch), ('fass', 'Fass', fass),
         ('kiste', 'Kiste', kiste), ('laterne', 'Laterne', laterne), ('schild', 'Schild', schild),
         ('zaun', 'Zaun', zaun), ('beet', 'Beet', beet)]

# ================================================================ EXPORT + VORSCHAU
SKY_DAY, SKY_NIGHT = C('#8fb4d8'), C('#2a2445')
GROUND_DAY, GROUND_NIGHT = C('#5a8a4a'), C('#33503c')

def font(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sz)
    except Exception: return ImageFont.load_default(size=sz)

def sheet(items, scale, night, title, cols, cell_h=None):
    """items: list of (label, image)"""
    pad = 24
    cw = max(i.width for _, i in items)*scale + pad
    ch = (cell_h or max(i.height for _, i in items))*scale + 40
    rows = math.ceil(len(items)/cols)
    W, H = cols*cw + pad, rows*ch + 70
    sh = Image.new('RGBA', (W, H), SKY_NIGHT if night else SKY_DAY)
    d = ImageDraw.Draw(sh)
    d.text((pad, 18), title, fill=(255, 240, 200) if night else (40, 30, 50), font=font(22))
    for k, (label, im) in enumerate(items):
        cx, cy = pad + (k % cols)*cw, 60 + (k//cols)*ch
        base = cy + ch - 36
        d.rectangle([cx-6, base, cx+cw-pad+6, base+8], fill=GROUND_NIGHT if night else GROUND_DAY)
        big = im.resize((im.width*scale, im.height*scale), Image.NEAREST)
        x = cx + (cw-pad-big.width)//2
        sh.alpha_composite(big, (x, base-big.height+scale))
        d.text((cx, base+12), label, fill=(240, 230, 210) if night else (30, 30, 40), font=font(15))
    return sh

def main():
    for sub in ('characters', 'buildings', 'props'): os.makedirs(os.path.join(BASE, sub), exist_ok=True)
    # Figuren: Einzelbilder + Spritesheet (idle, walk1, walk2)
    char_items, anim_items = [], []
    for cfg in CHARACTERS:
        frames = [make_character(cfg, f) for f in ('idle', 'walk1', 'walk2')]
        ss = Image.new('RGBA', (18*3, 26), (0, 0, 0, 0))
        for i, fr in enumerate(frames): ss.alpha_composite(fr, (18*i, 0))
        ss.save(os.path.join(BASE, 'characters', f"{cfg['name']}_sheet.png"))
        frames[0].save(os.path.join(BASE, 'characters', f"{cfg['name']}.png"))
        char_items.append((cfg['title'], frames[0])); anim_items.append((cfg['title'], ss))
    sheet(char_items, 6, True, 'Cosy - Figuren', 4).save(os.path.join(BASE, 'preview_figuren.png'))
    sheet(anim_items, 5, True, 'Cosy - Spritesheets (idle / walk1 / walk2)', 4).save(os.path.join(BASE, 'preview_animation.png'))
    for night, tag in ((False, 'tag'), (True, 'nacht')):
        b_items = []
        for name, title, fn in BUILDINGS:
            im = fn(night); im.save(os.path.join(BASE, 'buildings', f'{name}_{tag}.png')); b_items.append((title, im))
        sheet(b_items, 4, night, f"Cosy - Gebäude ({'Nacht' if night else 'Tag'})", 4).save(os.path.join(BASE, f'preview_gebaeude_{tag}.png'))
        p_items = []
        for name, title, fn in PROPS:
            im = fn(night); im.save(os.path.join(BASE, 'props', f'{name}_{tag}.png')); p_items.append((title, im))
        sheet(p_items, 5, night, f"Cosy - Props ({'Nacht' if night else 'Tag'})", 5).save(os.path.join(BASE, f'preview_props_{tag}.png'))

if __name__ == '__main__':
    main()
