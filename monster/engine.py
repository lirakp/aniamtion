"""Zeichen-Engine für die Monster: Primitive in Welt-Einheiten (y nach oben, Boden = 0),
Posen für die Animationen und allgemeine Effekte (Treffer, Tod, Element-Partikel)."""
import math, random
from PIL import Image, ImageDraw

def C(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)
def shade(c, f): return tuple(max(0, min(255, int(v*f))) for v in c[:3]) + (c[3] if len(c) > 3 else 255,)
def mix(a, b, t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3)) + (255,)
WHITE, BLACK = (255, 255, 255, 255), (0, 0, 0, 255)
OUTLINE = C('#2b1e33')
TRANSP = (0, 0, 0, 0)

ANIMS = [('idle', 4), ('move', 6), ('attack', 6), ('hurt', 3), ('death', 6)]

def light(c, t=.22): return mix(c, WHITE, t)

class R:
    """Zeichenfläche. S = Pixel pro Welteinheit, (ox, oy) = Pixel des Ursprungs (Boden-Mitte)."""
    def __init__(self, W, H, S, ox, oy):
        self.img = Image.new('RGBA', (W, H), TRANSP); self.px = self.img.load()
        self.W, self.H, self.S, self.ox, self.oy = W, H, S, ox, oy
        self.dx = 0.0; self.dy = 0.0          # globaler Versatz (Pose)
    def P(self, x, y):
        return self.ox + (x + self.dx) * self.S, self.oy - (y + self.dy) * self.S
    def set(self, ix, iy, c):
        if 0 <= ix < self.W and 0 <= iy < self.H: self.px[ix, iy] = c
    def get(self, ix, iy):
        if 0 <= ix < self.W and 0 <= iy < self.H: return self.px[ix, iy]
        return TRANSP
    def dot(self, x, y, c, r=0):
        cx, cy = self.P(x, y); cx, cy = int(math.floor(cx)), int(math.floor(cy))
        for yy in range(cy-r, cy+r+1):
            for xx in range(cx-r, cx+r+1):
                if r == 0 or (xx-cx)**2 + (yy-cy)**2 <= r*r + r: self.set(xx, yy, c)
    def ell(self, x, y, rx, ry, col, shaded=True, rot=0.0, lo=None, hi=None):
        cx, cy = self.P(x, y)
        rxp, ryp = max(.5, rx*self.S), max(.5, ry*self.S)
        R_ = max(rxp, ryp) + 1
        ca, sa = math.cos(rot), math.sin(rot)
        L, D = (hi or light(col)), (lo or shade(col, .72))
        for iy in range(int(cy-R_), int(cy+R_)+2):
            for ix in range(int(cx-R_), int(cx+R_)+2):
                dx, dy = ix + .5 - cx, -(iy + .5 - cy)
                u = (dx*ca + dy*sa) / rxp; v = (-dx*sa + dy*ca) / ryp
                if u*u + v*v <= 1:
                    c = col
                    if shaded:
                        l = -u*.55 + v*.75
                        c = L if l > .5 else D if l < -.55 else col
                    self.set(ix, iy, c)
    def capsule(self, x0, y0, x1, y1, w0, col, w1=None, shaded=False):
        w1 = w0 if w1 is None else w1
        a, b = self.P(x0, y0), self.P(x1, y1)
        n = max(1, int(math.hypot(b[0]-a[0], b[1]-a[1]) * 2))
        for i in range(n+1):
            t = i / n
            self.ell(x0 + (x1-x0)*t, y0 + (y1-y0)*t, (w0 + (w1-w0)*t)/2, (w0 + (w1-w0)*t)/2, col, shaded)
    def poly(self, pts, col):
        ImageDraw.Draw(self.img).polygon([self.P(x, y) for x, y in pts], fill=col)
    def line(self, x0, y0, x1, y1, col):
        ImageDraw.Draw(self.img).line([self.P(x0, y0), self.P(x1, y1)], fill=col)
    def tri(self, x, y, w, h, col, lean=0.0):
        """Dreieck (Ohr, Horn, Stachel): Basis-Mitte x,y, Breite w, Höhe h."""
        self.poly([(x - w/2, y), (x + w/2, y), (x + lean, y + h)], col)
    def shadow(self, x, w, alpha=70):
        cx, cy = self.P(x, 0); rx = w * self.S / 2
        for iy in range(int(cy-2), int(cy+2)):
            for ix in range(int(cx-rx), int(cx+rx)+1):
                if ((ix+.5-cx)/rx)**2 + ((iy+.5-cy)/2.2)**2 <= 1 and self.get(ix, iy)[3] == 0:
                    self.set(ix, iy, (20, 14, 30, alpha))

# ---------------------------------------------------------------- Posen
def pose(anim, t):
    p = dict(anim=anim, t=t, bob=0.0, lunge=0.0, open=0.0, swing=0.0, flap=0.0, walk=0.0, moving=False,
             recoil=0.0, phase=0.0, cast=0.0)
    if anim == 'idle':
        ph = t / 4 * 2*math.pi
        p.update(bob=math.sin(ph) * .012, flap=math.sin(ph), phase=ph, open=0.0)
    elif anim == 'move':
        ph = t / 6 * 2*math.pi
        p.update(walk=ph, bob=abs(math.sin(ph)) * .03, flap=math.sin(ph*2), phase=ph, moving=True)
    elif anim == 'attack':
        p.update(lunge=[-.04, -.07, .10, .14, .06, 0][t], open=[0, .2, 1, 1, .4, 0][t],
                 swing=[0, -.7, -1, .9, 1, .3][t], cast=[0, .3, .8, 1, .5, 0][t],
                 flap=[0, .5, 1, -1, -.5, 0][t], phase=t / 6 * 2*math.pi)
    elif anim in ('hurt', 'death'):
        p.update(recoil=[-.08, -.06, -.02][min(t, 2)] if anim == 'hurt' else -.08, open=.6)
    return p

# ---------------------------------------------------------------- Effekte
ELEMENT_COLS = {
    'feuer': [C('#ffd27a'), C('#ff9a3c'), C('#e8603a')],
    'eis': [C('#ffffff'), C('#b8e4ff'), C('#7ab8e8')],
    'blitz': [C('#ffffff'), C('#fff07a'), C('#8ad0ff')],
    'gift': [C('#d8f07a'), C('#8ad04a'), C('#5a9a3a')],
    'schatten': [C('#8a6ab8'), C('#4a3a6a'), C('#2a2040')],
    'blut': [C('#ff6a6a'), C('#c83a3a'), C('#7a1e2a')],
    'wasser': [C('#e8f6ff'), C('#8ac4ee'), C('#4a8ac8')],
    'arkan': [C('#f0e4ff'), C('#b8a0ff'), C('#7a5ad0')],
    'erde': [C('#c8a878'), C('#8a6a4a'), C('#5a4430')],
    'wind': [C('#ffffff'), C('#d8e8f0'), C('#a8c0d0')],
    'licht': [C('#ffffff'), C('#fff4c8'), C('#ffd27a')],
    'natur': [C('#c8e88a'), C('#6e9e58'), C('#4a7d4a')],
    'nebel': [C('#f4f4fa'), C('#d0d0e0'), C('#a8a8c0')],
    'kristall': [C('#ffffff'), C('#c0f0ff'), C('#7ad0e8')],
}

def breath(r, x, y, k, element, length=.8, spread=.25, seed=0):
    """Atem-/Zauberstrahl nach rechts ab (x,y), Stärke k 0..1"""
    cols = ELEMENT_COLS.get(element, ELEMENT_COLS['feuer'])
    rng = random.Random(seed)
    n = int(60 * k * max(1, r.S / 40))
    for _ in range(n):
        d = rng.random() * length * k
        off = (rng.random() - .5) * 2 * spread * (d / length + .15)
        c = cols[0] if d < length * .3 else cols[1] if d < length * .7 else cols[2]
        r.dot(x + d, y + off, c, 1 if r.S > 50 else 0)

def particles(r, element, t, cx, cy, radius, n=6, seed=1, rise=True):
    cols = ELEMENT_COLS.get(element)
    if not cols: return
    rng = random.Random(seed)
    for i in range(n):
        a = rng.random() * 2*math.pi; rr = radius * (.5 + rng.random() * .6)
        p = ((t + i * 7) % 8) / 8
        x = cx + math.cos(a) * rr
        y = cy + math.sin(a) * rr * .6 + (p * radius * .8 if rise else 0)
        if p < .85: r.dot(x, y, cols[i % 3])

def finalize(img, outline=OUTLINE):
    w, h = img.size; src = img.load(); out = img.copy(); p = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] == 255:
                        p[x, y] = outline; break
    return out

def tint(img, col, k):
    out = img.copy(); p = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = p[x, y]
            if c[3] > 100: p[x, y] = mix(c, col, k)[:3] + (c[3],)
    return out

def death_frame(img, k, seed=3, col=None):
    """k: 0..1 Auflösung. Zusammensacken + Zerfallen in Pixel."""
    w, h = img.size
    sq = 1 - .35 * k
    nh = max(1, int(h * sq))
    body = img.resize((w, nh), Image.NEAREST)
    out = Image.new('RGBA', (w, h), TRANSP); out.alpha_composite(body, (0, h - nh))
    p = out.load(); rng = random.Random(seed)
    for y in range(h):
        for x in range(w):
            c = p[x, y]
            if c[3] == 0: continue
            if rng.random() < k * 1.05 - .05: p[x, y] = TRANSP
            else: p[x, y] = mix(c, (40, 30, 50, 255), k * .6)[:3] + (c[3],)
    if col:
        d = ImageDraw.Draw(out)
        for i in range(int(8 * k) + 2):
            x = rng.randint(w // 5, w * 4 // 5); y = int(h - rng.random() * h * (.3 + k * .6))
            d.point((x, y), fill=col)
    return out
