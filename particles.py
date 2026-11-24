"""Umgebungs-Partikel als nahtlos loopende Overlays (320x180, transparent) über der Szene.
Aufruf: python3 particles.py
Ausgabe: level/partikel/<effekt>.png (16 Frames untereinander), level/partikel/partikel.json, preview_partikel.gif
Jeder Effekt loopt nahtlos (Frame 15 → Frame 0). Für größere Szenen einfach kacheln.
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, mix
import ui

W, H, N = 320, 180, 16
OUT = os.path.join(g.BASE, 'level', 'partikel')
SCR = os.path.join(g.BASE, 'level', 'parallax')
def h(i, s):
    x = (i * 374761393 + s * 668265263) & 0xffffffff
    x = ((x ^ (x >> 13)) * 1274126177) & 0xffffffff
    return ((x ^ (x >> 16)) & 0xffffff) / 0x1000000
def wrap(v, m): return v % m

def gluehwuermchen(t, d):
    for i in range(26):
        ph = t / N * 2 * math.pi
        x = wrap(h(i, 1) * W + math.sin(ph + i) * 8 + math.cos(ph * 2 + i * 3) * 3, W); y = 60 + h(i, 2) * 110 + math.sin(ph + i * 1.7) * 5
        on = (math.sin(ph * 2 + i * 2.3) + 1) / 2
        if on > .25:
            core = C('#f8ffb0'); glow = (220, 255, 120, int(90 * on))
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=glow); d.point((x, y), fill=core)
def regen(t, d, heavy=False):
    n = 220 if heavy else 110; L = 9 if heavy else 6
    for i in range(n):
        x0 = h(i, 3) * W; y = wrap(h(i, 4) * H + t / N * H * (3 if heavy else 2), H + 20) - 10
        x = wrap(x0 - (y / 6 if heavy else y / 10), W)
        d.line([(x, y), (x - (1.5 if heavy else 1), y + L)], fill=(170, 200, 240, 170 if heavy else 130))
    for i in range(30 if heavy else 14):  # Spritzer am Boden
        ph = (t + int(h(i, 5) * N)) % N
        if ph < 3:
            x = h(i, 6) * W; y = H - 6 - h(i, 7) * 10
            d.point((x - ph, y - ph), fill=(200, 220, 250, 200)); d.point((x + ph, y - ph), fill=(200, 220, 250, 200))
    if heavy and t in (5, 6):
        d.rectangle([0, 0, W, H], fill=(230, 235, 255, 70 if t == 5 else 30))  # Blitz-Aufhellung
def regen_stark(t, d): regen(t, d, True)
def schnee(t, d):
    for i in range(140):
        sz = 1 + (i % 4 == 0)
        y = wrap(h(i, 8) * H + t / N * H * (1 if sz == 1 else 2), H + 4) - 2
        x = wrap(h(i, 9) * W + math.sin(t / N * 2 * math.pi + i) * 4, W)
        col = (255, 255, 255, 230 if sz == 2 else 170)
        d.rectangle([x, y, x + sz - 1, y + sz - 1], fill=col)
def blaetter(t, d):
    cols = [C('#d88a3a'), C('#c85a2a'), C('#e0b048'), C('#8a6a3a'), C('#6e9e58')]
    for i in range(28):
        y = wrap(h(i, 10) * H + t / N * H, H + 8) - 4
        x = wrap(h(i, 11) * W + math.sin(t / N * 4 * math.pi + i) * 10 - t / N * W, W)
        flip = (t + i) % 4
        c = cols[i % 5]
        if flip in (0, 2): d.ellipse([x, y, x + 4, y + 2], fill=c); d.point((x + 1, y + 1), fill=mix(c, (0, 0, 0, 255), .25))
        elif flip == 1: d.ellipse([x, y, x + 2, y + 4], fill=c)
        else: d.point((x, y), fill=c); d.point((x + 1, y + 1), fill=mix(c, (255,) * 4, .3))
def pollen(t, d):  # Staub im Sonnenlicht + Lichtstrahlen
    for k, x0 in enumerate((70, 150, 240)):
        a = 26 + int(6 * math.sin(t / N * 2 * math.pi + k))
        d.polygon([(x0, 0), (x0 + 22, 0), (x0 - 18, H), (x0 - 52, H)], fill=(255, 240, 190, a))
    for i in range(50):
        ph = t / N * 2 * math.pi
        x = wrap(h(i, 12) * W + t / N * 20 + math.sin(ph + i) * 3, W); y = h(i, 13) * H + math.cos(ph + i * 2) * 3
        d.point((x, y), fill=(255, 244, 200, 160 + int(80 * ((math.sin(ph * 2 + i) + 1) / 2))))
def nebel(t, d):
    for b in range(3):
        y = 110 + b * 22
        for i in range(8):
            x = wrap(i * 52 + t / N * W * (1 if b % 2 else -1) * (1 / (b + 1)) + b * 30, W + 80) - 40
            d.ellipse([x, y - 10 + (i % 2) * 4, x + 70, y + 14], fill=(220, 225, 240, 34 - b * 6))
def funken(t, d):
    for i in range(70):
        y = H - wrap(h(i, 14) * H + t / N * H * 2, H)
        x = wrap(h(i, 15) * W + math.sin(t / N * 4 * math.pi + i) * 5, W)
        life = y / H
        col = mix(C('#ffd27a'), C('#e8603a'), 1 - life)
        d.point((x, y), fill=col[:3] + (int(120 + 135 * life),))
        if i % 3 == 0: d.rectangle([x, y, x + 1, y + 1], fill=col[:3] + (int(120 + 135 * life),)); d.point((x, y + 2), fill=col[:3] + (90,))
def asche(t, d):
    for i in range(70):
        y = wrap(h(i, 16) * H + t / N * H, H)
        x = wrap(h(i, 17) * W + t / N * W * .5 * (1 if i % 2 else -1) + math.sin(i + t / 3) * 2, W)
        d.point((x, y), fill=(140, 130, 140, 170) if i % 3 else (255, 140, 80, 220))
def blasen(t, d):
    for i in range(30):
        y = H - wrap(h(i, 18) * H + t / N * H, H)
        x = h(i, 19) * W + math.sin(t / N * 4 * math.pi + i) * 2
        r = 1 + (i % 3 == 0)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(200, 235, 255, 200)); d.point((x - r + 1, y - r + 1), fill=(255, 255, 255, 230))
    for k in range(4):
        x0 = 30 + k * 80 + int(8 * math.sin(t / N * 2 * math.pi + k))
        d.polygon([(x0, 0), (x0 + 16, 0), (x0 + 4, H), (x0 - 12, H)], fill=(180, 230, 255, 18))
def magie(t, d):
    cols = [C('#d8c8ff'), C('#b880ff'), C('#8ad0ff')]
    for i in range(40):
        y = H - wrap(h(i, 20) * H + t / N * H, H)
        x = wrap(h(i, 21) * W + math.sin(t / N * 2 * math.pi + i) * 6, W)
        c = cols[i % 3]; tw = (t + i) % 4
        if tw == 0: d.point((x - 1, y), fill=c); d.point((x + 1, y), fill=c); d.point((x, y - 1), fill=c); d.point((x, y + 1), fill=c)
        d.point((x, y), fill=(255, 255, 255, 230) if tw == 0 else c)
def sternschnuppen(t, d):
    for i in range(60):
        x, y = h(i, 22) * W, h(i, 23) * 100
        if (i + t // 2) % 7: d.point((x, y), fill=(255, 255, 240, 200 if i % 3 else 120))
    k = t % 8
    if k < 4:
        sx = 240 - k * 22 + (t // 8) * -90; sy = 20 + k * 9 + (t // 8) * 20
        for j in range(8): d.point((sx + j * 2.4, sy - j), fill=(255, 255, 230, 255 - j * 30))
def hoehlentropfen(t, d):
    for i in range(10):
        x = 20 + i * 31 + int(h(i, 24) * 10); ph = (t + i * 5) % N
        if ph < 10: d.point((x, 4 + (ph > 6) * (ph - 6) * 0), fill=(150, 200, 240, 120 + ph * 12))
        elif ph < 14: y = 6 + (ph - 10) ** 2 * 10; d.line([(x, y), (x, y + 2)], fill=(170, 210, 250, 220))
        else: d.point((x - (ph - 13) * 2, H - 6 - (ph - 13)), fill=(170, 210, 250, 200)); d.point((x + (ph - 13) * 2, H - 6 - (ph - 13)), fill=(170, 210, 250, 200))

FX = {'gluehwuermchen': (gluehwuermchen, 'dorf_nacht', 'Nacht, Wiesen, Waldränder'),
      'regen': (regen, 'dorf_tag', 'leichter Regen mit Spritzern'), 'regen_stark': (regen_stark, 'dorf_nacht', 'Gewitter mit Blitz-Aufhellung'),
      'schnee': (schnee, 'dorf_nacht', 'Schneefall (Nah- und Fernflocken)'), 'blaetter': (blaetter, 'dorf_tag', 'Herbstlaub im Wind'),
      'pollen_licht': (pollen, 'dorf_tag', 'Sonnenstrahlen mit Staub (Wald, Kirche)'), 'nebel': (nebel, 'dorf_nacht', 'Bodennebel in drei Lagen'),
      'funken': (funken, 'hoehle', 'aufsteigende Funken (Schmiede, Lava)'), 'asche': (asche, 'dungeon_blut', 'fallende Asche mit Glut'),
      'blasen': (blasen, 'hoehle', 'Unterwasser: Blasen + Lichtstrahlen'), 'magie': (magie, 'dungeon_erinnerung', 'Mana-Funkeln (Magierorte, Portale)'),
      'sternschnuppen': (sternschnuppen, 'dorf_nacht', 'funkelnde Sterne + Sternschnuppe'), 'hoehlentropfen': (hoehlentropfen, 'hoehle', 'Tropfen von der Decke')}

def scene(kind):
    im = Image.new('RGBA', (W, H), (30, 24, 40, 255))
    for n in sorted(os.listdir(SCR)):
        if n.startswith(kind + '_'): im.alpha_composite(Image.open(os.path.join(SCR, n)).convert('RGBA'))
    return im

class _D(ImageDraw.ImageDraw):
    def rectangle(self, xy, *a, **k):
        x0, y0, x1, y1 = [int(round(v)) for v in xy]; super().rectangle([x0, y0, max(x0, x1), max(y0, y1)], *a, **k)

def frame(fn, t):
    im = Image.new('RGBA', (W, H)); d = _D(im, 'RGBA'); fn(t, d); return im

def main():
    os.makedirs(OUT, exist_ok=True); meta = {}
    frames_all = {}
    for n, (fn, bg, desc) in FX.items():
        fr = [frame(fn, t) for t in range(N)]; frames_all[n] = fr
        s = Image.new('RGBA', (W, H * N))
        for t, f in enumerate(fr): s.alpha_composite(f, (0, t * H))
        s.save(os.path.join(OUT, f'{n}.png')); meta[n] = desc
    json.dump({'groesse': [W, H], 'frames': N, 'fps': 10, 'hinweis': 'Overlay über der Spielebene; Frames liegen untereinander, Loop nahtlos.', 'effekte': meta},
              open(os.path.join(OUT, 'partikel.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    names = list(FX); cols = 4; Z = 1; rows = math.ceil(len(names) / cols)
    bgs = {n: scene(FX[n][1]) for n in names}
    out = []
    for t in range(N * 2):
        im = Image.new('RGB', (cols * (W + 4), rows * (H + 4)), (20, 16, 26))
        for i, n in enumerate(names):
            c = bgs[n].copy(); c.alpha_composite(frames_all[n][t % N]); ui.text(c, 4, 4, n.upper().replace('_', ' '), C('#f0e4cc'), shadow=C('#2b1e33'))
            im.paste(c.convert('RGB'), ((i % cols) * (W + 4), (i // cols) * (H + 4)))
        out.append(im)
    out[0].save(os.path.join(g.BASE, 'preview_partikel.gif'), save_all=True, append_images=out[1:], duration=100, loop=0)

if __name__ == '__main__':
    main()
