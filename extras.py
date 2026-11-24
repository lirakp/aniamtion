"""Übergänge, Tag-Nacht-Wechsel und Kartensymbole.
Aufruf: python3 extras.py
Ausgabe:
  ui/uebergaenge/<art>.png   – 12 Masken à 320x180 untereinander (schwarz = verdeckt), uebergaenge.json
  level/tageszeit/himmel_<phase>.png + tageszeit.json (Tönung je Stunde), preview_tageszeit.gif
  ui/karte/kartensymbole.png (12x12) + karte.json, preview_karte.png
"""
import os, json, math
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
import ui

W, H, N = 320, 180, 12
INK = C('#2b1e33'); BLACK = (20, 14, 26, 255)
SCR = os.path.join(g.BASE, 'level', 'parallax')

def h(x, y, s=0): return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) % 1000 / 1000

# ================================================================ Übergänge
def iris(k):  # Kreis schließt sich zur Bildmitte (Spielerposition frei wählbar im Spiel)
    im = Image.new('RGBA', (W, H), BLACK); d = ImageDraw.Draw(im)
    r = (1 - k) * 190
    if r > 0:
        # pixelige Kreiskante: in 4er-Blöcken
        for y in range(0, H, 4):
            for x in range(0, W, 4):
                if math.hypot(x + 2 - W / 2, y + 2 - H / 2) < r: d.rectangle([x, y, x + 3, y + 3], fill=(0, 0, 0, 0))
    return im
def blende(k):
    a = int(255 * k); im = Image.new('RGBA', (W, H), BLACK[:3] + (a,))
    return im
def pixel(k):  # Pixel-Auflösung (Blöcke erscheinen zufällig)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(0, H, 10):
        for x in range(0, W, 10):
            if h(x, y) < k: d.rectangle([x, y, x + 9, y + 9], fill=BLACK)
    return im
def vorhang(k):  # Bühnenvorhang von links und rechts mit Falten
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = int(k * (W / 2 + 12))
    red, dk = C('#7a2a3a'), C('#4a1a2a')
    for side in (0, 1):
        x0, x1 = (0, w) if side == 0 else (W - w, W)
        d.rectangle([x0, 0, x1, H], fill=red)
        for x in range(x0, x1, 8): d.line([(x, 0), (x, H)], fill=dk, width=2)
        edge = x1 if side == 0 else x0
        for y in range(0, H, 6): d.point((edge + (1 if side == 0 else -1) * (y // 6 % 2), y), fill=C('#e0b048'))
    d.rectangle([0, 0, W, 6], fill=C('#5a1a2a')) if k > 0 else None
    return im
def blaetter(k):  # Blätterwirbel weht von links herein und deckt ab
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    front = k * (W + 120) - 60
    for i in range(900):
        x0, y = h(i, 1) * (W + 80) - 40, h(i, 2) * H
        x = x0 + math.sin(y / 20 + i) * 10
        if x < front:
            s = 6 + int(h(i, 3) * 6); col = [C('#d88a3a'), C('#c85a2a'), C('#e0b048'), C('#8a6a3a')][i % 4]
            d.ellipse([x, y, x + s, y + s * .6], fill=col)
    if k > .55:
        d.rectangle([0, 0, max(0, front - 80), H], fill=C('#3a2a2a'))
    return im
def magie(k):  # Runen-Kreis + violetter Wirbel (Teleport / Portal)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx, cy = W / 2, H / 2
    for y in range(0, H, 3):
        for x in range(0, W, 3):
            a = math.atan2(y - cy, x - cx); r = math.hypot(x - cx, y - cy)
            v = (r / 200) + .15 * math.sin(a * 5 + r / 15)
            if v > 1.15 - k * 1.3: d.rectangle([x, y, x + 2, y + 2], fill=C('#3a2a5a') if (int(r / 6) + int(a * 4)) % 3 else C('#6a4aa8'))
    if 0 < k < 1:
        R = 30 + k * 60
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=C('#d8c8ff'))
        for i in range(8):
            a = i / 8 * 2 * math.pi + k * 3; x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
            d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=C('#f0e8ff'))
    return im

TRANS = {'iris': (iris, 'Kreis schließt sich (Tür/Szenenwechsel)'), 'blende': (blende, 'Schwarzblende'),
         'pixel': (pixel, 'Pixel-Auflösung (Kampf beginnt)'), 'vorhang': (vorhang, 'Bühnenvorhang (Kapitelwechsel)'),
         'blaetter': (blaetter, 'Blätterwirbel (Reise über die Karte)'), 'magie': (magie, 'Magiewirbel (Teleport/Portal)')}

def scene(kind):
    im = Image.new('RGBA', (W, H))
    for n in sorted(os.listdir(SCR)):
        if n.startswith(kind + '_'): im.alpha_composite(Image.open(os.path.join(SCR, n)).convert('RGBA'))
    return im

def transitions():
    out = os.path.join(g.BASE, 'ui', 'uebergaenge'); os.makedirs(out, exist_ok=True); meta = {}
    for n, (fn, desc) in TRANS.items():
        s = Image.new('RGBA', (W, H * N))
        for i in range(N): s.alpha_composite(fn(i / (N - 1)), (0, i * H))
        s.save(os.path.join(out, f'{n}.png')); meta[n] = desc
    json.dump({'groesse': [W, H], 'frames': N, 'hinweis': 'Frames 0→11 = Szene zudecken; rückwärts abspielen = aufdecken. Szene wechseln, wenn Frame 11 erreicht ist.',
               'arten': meta}, open(os.path.join(out, 'uebergaenge.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    a, b = scene('dorf_tag'), scene('hoehle'); frames = []
    for n, (fn, _) in TRANS.items():
        seq = [fn(i / (N - 1)) for i in range(N)]
        for bg, order in ((a, seq), (b, seq[::-1])):
            for m in order:
                im = bg.copy(); im.alpha_composite(m); ui.text(im, 6, 6, n.upper(), C('#f0e4cc'), shadow=INK)
                frames.append(im.convert('RGB'))
        for _ in range(3): frames.append(frames[-1])
    frames = [f.resize((640, 360), Image.NEAREST) for f in frames]
    frames[0].save(os.path.join(g.BASE, 'preview_uebergaenge.gif'), save_all=True, append_images=frames[1:], duration=70, loop=0)

# ================================================================ Tag-Nacht
# Tönung je Stunde: Farbe, Stärke (Multiplikation), Lichter an/aus
KEYS = [(0, '#2a2a5a', .68, 1), (4, '#2a2a5a', .62, 1), (6, '#e08a6a', .3, 1), (8, '#ffe8c8', .08, 0), (12, '#ffffff', 0, 0),
        (17, '#ffd8a0', .12, 0), (19, '#e0704a', .35, 1), (20.5, '#6a3a7a', .45, 1), (22, '#2a2a5a', .68, 1), (24, '#2a2a5a', .68, 1)]
def tint_at(hr):
    for (h0, c0, k0, l0), (h1, c1, k1, l1) in zip(KEYS, KEYS[1:]):
        if h0 <= hr <= h1:
            f = (hr - h0) / (h1 - h0) if h1 > h0 else 0
            return mix(C(c0), C(c1), f), k0 + (k1 - k0) * f, l0 if f < .5 else l1
def grade(im, col, k):
    if k <= 0: return im
    ov = Image.new('RGBA', im.size, col[:3] + (255,))
    from PIL import ImageChops
    mul = ImageChops.multiply(im.convert('RGB'), ov.convert('RGB')).convert('RGBA'); mul.putalpha(im.getchannel('A'))
    return Image.blend(im, mul, k)
SKY = {'morgen': ['#6a6aa8', '#e0a0a0', '#f8d8a8'], 'tag': ['#7ab0e0', '#a8d0f0', '#d8ecf8'],
       'abend': ['#4a3a7a', '#c86a6a', '#f0a860'], 'nacht': ['#14122a', '#2a2a5a', '#3e3a6a']}
def sky(phase):
    cols = [C(c) for c in SKY[phase]]; im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        f = y / (H - 1) * 2; i = min(1, int(f)); c = mix(cols[i], cols[i + 1], f - i)
        # Bänder statt glattem Verlauf (Pixel-Look)
        d.line([(0, y), (W, y)], fill=mix(cols[i], cols[i + 1], round((f - i) * 6) / 6))
    if phase in ('nacht', 'morgen'):
        for i in range(70 if phase == 'nacht' else 15):
            x, y = int(h(i, 7) * W), int(h(i, 8) * H * .6); d.point((x, y), fill=(255, 255, 240, 255 if i % 3 else 150))
    if phase == 'tag': d.ellipse([250, 22, 272, 44], fill=C('#fff4c0')); d.ellipse([253, 25, 269, 41], fill=C('#fffbe8'))
    if phase == 'abend': d.ellipse([140, 120, 180, 160], fill=C('#ffb060')); d.ellipse([145, 125, 175, 155], fill=C('#ffd890'))
    if phase == 'morgen': d.ellipse([40, 130, 64, 154], fill=C('#ffd8a0'))
    if phase == 'nacht': d.ellipse([60, 26, 78, 44], fill=C('#f0e8c0')); d.ellipse([66, 24, 82, 40], fill=C('#14122a'))
    for i in range(5 if phase != 'nacht' else 3):  # Wolkenbänder
        y = 30 + i * 17; x = int(h(i, 9) * W)
        cc = mix(cols[1], (255, 255, 255, 255), .45 if phase == 'tag' else .2)
        d.rounded_rectangle([x, y, x + 50 + i * 8, y + 5], 2, fill=cc); d.rounded_rectangle([x + 10, y - 4, x + 34, y + 1], 2, fill=cc)
    return im
def daynight():
    out = os.path.join(g.BASE, 'level', 'tageszeit'); os.makedirs(out, exist_ok=True)
    for p in SKY: sky(p).save(os.path.join(out, f'himmel_{p}.png'))
    hours = []
    for hr in range(24):
        col, k, lights = tint_at(hr); hours.append({'stunde': hr, 'toenung': '#%02x%02x%02x' % col[:3], 'staerke': round(k, 3), 'lichter_an': bool(lights)})
    json.dump({'hinweis': 'Ebenen (außer Himmel) mit der Tönung multiplizieren, Stärke = Mischanteil. Himmel zwischen den 4 Phasen überblenden: morgen 5–8, tag 8–17, abend 17–21, nacht 21–5. Bei lichter_an Fenster/Laternen einschalten.',
               'stunden': hours}, open(os.path.join(out, 'tageszeit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau: Dorf durch den Tag, mit Lichtkreisen ab Abend
    layers = [Image.open(os.path.join(SCR, f'dorf_tag_{i}_{n}.png')).convert('RGBA') for i, n in ((1, 'berge'), (2, 'huegel'), (3, 'wald'))]
    try:
        cot = Image.open(os.path.join(g.BASE, 'buildings', 'cottage_tag.png')).convert('RGBA')
        cot_n = Image.open(os.path.join(g.BASE, 'buildings', 'cottage_nacht.png')).convert('RGBA')
        px = cot_n.load(); pts = [(x, y) for y in range(cot_n.height) for x in range(cot_n.width) if px[x, y][3] and px[x, y][0] > 230 and px[x, y][1] > 180 and px[x, y][2] < 150]
        wins = []
        for p in pts:
            if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) > 8 for q in wins): wins.append(p)
    except Exception: cot = None
    def sky_at(hr):
        ph = [(5, 'nacht', 'morgen'), (7, 'morgen', 'tag'), (17.5, 'tag', 'abend'), (20.5, 'abend', 'nacht')]
        cur = 'nacht'
        for t0, a, b in ph:
            if hr >= t0: cur = (a, b, min(1, (hr - t0) / 1.5))
        if isinstance(cur, str): return sky('nacht')
        a, b, f = cur; return Image.blend(sky(a), sky(b), f)
    frames = []
    for step in range(48):
        hr = step / 2; col, k, lights = tint_at(hr)
        im = sky_at(hr)
        scene_ = Image.new('RGBA', (W, H))
        for L in layers: scene_.alpha_composite(L)
        im.alpha_composite(grade(scene_, col, k))
        if cot:
            c_ = cot_n if lights else cot
            im.alpha_composite(grade(c_, col, k * (.45 if lights else 1)), (150, H - cot.height - 6))
        if lights and cot:
            gl = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(gl)
            for wx, wy in wins:
                for r, a in ((9, 35), (5, 55)): gd.ellipse([150 + wx - r, H - cot.height - 6 + wy - r, 150 + wx + r, H - cot.height - 6 + wy + r], fill=(255, 200, 120, a))
            im.alpha_composite(gl)
        ui.text(im, 6, 6, f'{int(hr):02d}:{"30" if hr % 1 else "00"}', C('#f0e4cc'), scale=2, shadow=INK)
        frames.append(im.resize((640, 360), Image.NEAREST).convert('RGB'))
    frames[0].save(os.path.join(g.BASE, 'preview_tageszeit.gif'), save_all=True, append_images=frames[1:], duration=160, loop=0)

# ================================================================ Kartensymbole 12x12
RANK = ui.RANK_COL
def mi(): im = Image.new('RGBA', (12, 12)); return im, ImageDraw.Draw(im)
def fin(im): return g.outline(im)
def sym(kind, rank=None):
    im, d = mi()
    if kind == 'spieler': d.ellipse([0, 0, 11, 11], fill=C('#4a8ae0')); d.polygon([(5.5, 2), (9, 9), (5.5, 7), (2, 9)], fill=C('#ffffff'))
    elif kind == 'gilde': d.polygon([(1, 5), (6, 1), (11, 5)], fill=C('#a83a3a')); d.rectangle([2, 5, 9, 10], fill=C('#e8dcc0')); d.rectangle([5, 7, 6, 10], fill=g.WOOD); d.line([(9, 0), (9, 3)], fill=g.WOOD); d.rectangle([9, 0, 11, 1], fill=C('#e0b048'))
    elif kind == 'schmiede': d.polygon([(1, 6), (10, 6), (9, 8), (3, 8)], fill=C('#6a6e80')); d.rectangle([4, 8, 7, 10], fill=C('#3e4050')); d.line([(3, 1), (8, 5)], fill=g.WOOD); d.rectangle([7, 2, 10, 4], fill=C('#a8acbc'))
    elif kind == 'laden': d.ellipse([2, 3, 10, 11], fill=C('#c8a070')); d.rectangle([4, 1, 8, 3], fill=C('#a8804a')); d.text((4, 3), '', fill=INK); d.point((6, 7), fill=C('#e0b048')); d.point((5, 6), fill=C('#e0b048')); d.point((7, 8), fill=C('#e0b048'))
    elif kind == 'taverne': d.rectangle([2, 3, 8, 10], fill=C('#c8a060')); d.rectangle([2, 2, 8, 3], fill=C('#ffffff')); d.rectangle([9, 5, 10, 8], outline=C('#c8a060'))
    elif kind == 'kirche': d.polygon([(3, 5), (6, 2), (9, 5)], fill=C('#5a6a9a')); d.rectangle([3, 5, 8, 11], fill=C('#e8dcc0')); d.line([(6, 0), (6, 2)], fill=C('#e0b048')); d.line([(5, 1), (7, 1)], fill=C('#e0b048')); d.rectangle([5, 8, 6, 11], fill=g.WOOD)
    elif kind == 'brunnen': d.ellipse([1, 5, 10, 11], fill=C('#8a8296')); d.ellipse([3, 6, 8, 9], fill=C('#4a8ae0')); d.line([(2, 2), (2, 7)], fill=g.WOOD); d.line([(9, 2), (9, 7)], fill=g.WOOD); d.line([(1, 2), (10, 2)], fill=C('#a83a3a'))
    elif kind == 'rastplatz': d.line([(2, 10), (9, 8)], fill=g.WOOD, width=2); d.line([(2, 8), (9, 10)], fill=g.WOOD_D, width=2); d.polygon([(4, 8), (6, 2), (8, 8)], fill=C('#ff9a3c')); d.polygon([(5, 8), (6, 5), (7, 8)], fill=C('#ffe08a'))
    elif kind == 'dungeon':
        d.polygon([(1, 11), (1, 5), (6, 1), (11, 5), (11, 11)], fill=C('#3a3446')); d.chord([3, 4, 9, 12], 180, 360, fill=BLACK); d.rectangle([3, 8, 9, 11], fill=BLACK)
        d.rectangle([5, 0, 7, 2], fill=RANK[rank]) if rank else None
    elif kind == 'boss': d.ellipse([1, 1, 10, 9], fill=C('#e8e0d0')); d.rectangle([3, 8, 8, 11], fill=C('#e8e0d0')); d.rectangle([3, 4, 4, 6], fill=C('#a83a3a')); d.rectangle([7, 4, 8, 6], fill=C('#a83a3a')); d.line([(4, 10), (7, 10)], fill=INK)
    elif kind == 'schatz': d.rectangle([1, 4, 10, 10], fill=g.WOOD); d.rectangle([1, 3, 10, 5], fill=g.WOOD_L); d.line([(1, 6), (10, 6)], fill=C('#e0b048')); d.rectangle([5, 6, 6, 7], fill=C('#e0b048'))
    elif kind == 'auftrag': d.rectangle([5, 0, 6, 7], fill=C('#e0b048')); d.rectangle([5, 9, 6, 10], fill=C('#e0b048'))
    elif kind == 'auftrag_fertig': d.line([(4, 1), (8, 1), (8, 5), (6, 6), (6, 7)], fill=C('#e0b048'), width=2); d.rectangle([5, 9, 6, 10], fill=C('#e0b048'))
    elif kind == 'portal': d.ellipse([1, 0, 10, 11], fill=C('#6a4aa8')); d.ellipse([3, 2, 8, 9], fill=C('#b880ff')); d.ellipse([5, 4, 6, 7], fill=C('#f0e8ff'))
    elif kind == 'tor': d.rectangle([1, 2, 10, 11], fill=C('#6e687a')); d.chord([3, 3, 8, 10], 180, 360, fill=g.WOOD); d.rectangle([3, 6, 8, 11], fill=g.WOOD); d.line([(1, 2), (10, 2)], fill=C('#8a8296'))
    elif kind == 'haendler_reise': d.rectangle([1, 4, 8, 8], fill=C('#e8dcc0')); d.chord([1, 1, 8, 8], 180, 360, fill=C('#e8dcc0')); d.ellipse([1, 8, 4, 11], fill=g.WOOD_D); d.ellipse([6, 8, 9, 11], fill=g.WOOD_D); d.line([(8, 7), (11, 7)], fill=g.WOOD)
    elif kind == 'gefahr': d.polygon([(6, 0), (11, 10), (1, 10)], fill=C('#e0b048')); d.line([(6, 3), (6, 7)], fill=INK); d.point((6, 9), fill=INK)
    elif kind == 'markierung': d.ellipse([2, 0, 9, 7], fill=C('#e0443a')); d.polygon([(3, 5), (8, 5), (5.5, 11)], fill=C('#e0443a')); d.ellipse([4, 2, 7, 5], fill=C('#f0e4cc'))
    elif kind == 'nebel': d.rectangle([0, 0, 11, 11], fill=C('#4a4458'))
    for x, y in ((2, 3), (8, 7)) if kind == 'nebel' else ():
        d.line([(x, y), (x + 3, y)], fill=C('#6a6478'))
    return fin(im) if kind != 'nebel' else im

MAP = ['spieler', 'gilde', 'schmiede', 'laden', 'taverne', 'kirche', 'brunnen', 'rastplatz', 'boss', 'schatz', 'auftrag', 'auftrag_fertig',
       'portal', 'tor', 'haendler_reise', 'gefahr', 'markierung', 'nebel'] + [f'dungeon_{r}' for r in RANK]
def mapsyms():
    out = os.path.join(g.BASE, 'ui', 'karte'); os.makedirs(out, exist_ok=True)
    s = Image.new('RGBA', (12 * len(MAP), 12))
    icons = [sym('dungeon', n.split('_')[1]) if n.startswith('dungeon_') else sym(n) for n in MAP]
    for i, ic in enumerate(icons): s.alpha_composite(ic, (i * 12, 0))
    s.save(os.path.join(out, 'kartensymbole.png'))
    json.dump({'groesse': 12, 'reihenfolge': MAP, 'hinweis': '"nebel" ist eine Kachel für unerforschte Bereiche.'},
              open(os.path.join(out, 'karte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # Vorschau: kleine Weltkarte auf Pergament
    perg = ui.nine(ui.frame9('pergament'), 300, 170); m = Image.new('RGBA', (320, 180), (42, 36, 69, 255)); m.alpha_composite(perg, (10, 5)); d = ImageDraw.Draw(m)
    path = [(40, 140), (80, 120), (120, 125), (160, 100), (200, 90), (240, 60), (280, 50)]
    for a, b in zip(path, path[1:]):
        for k in range(0, 10, 2):
            f = k / 10; d.point((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), fill=C('#a8804a'))
    d.line([(20, 40), (70, 60), (60, 100)], fill=C('#7ab0e0'), width=3)
    for x, y in ((210, 130), (230, 145), (250, 125), (270, 140)): d.polygon([(x - 6, y + 4), (x, y - 6), (x + 6, y + 4)], fill=C('#8a7a9a'))
    for x, y in ((100, 40), (115, 50), (130, 38)): d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=C('#6e9e58'))
    place = {'gilde': (80, 112), 'schmiede': (92, 124), 'taverne': (70, 126), 'kirche': (104, 110), 'brunnen': (86, 136), 'laden': (60, 112),
             'rastplatz': (160, 92), 'dungeon_C': (130, 140), 'dungeon_A': (250, 110), 'dungeon_SS': (290, 30), 'boss': (290, 18),
             'auftrag': (200, 80), 'schatz': (40, 60), 'portal': (240, 48), 'gefahr': (180, 130), 'haendler_reise': (140, 112),
             'markierung': (225, 28), 'spieler': (120, 118)}
    for n, (x, y) in place.items(): m.alpha_composite(icons[MAP.index(n)], (x - 6, y - 6))
    for x in range(262, 298, 12):
        for y in range(140, 164, 12): m.alpha_composite(icons[MAP.index('nebel')], (x, y))
    big = Image.new('RGB', (W * 3 + 12 * 4 * len(MAP) // 2 * 0, 540 + 100), (42, 36, 69))
    big.paste(m.resize((960, 540), Image.NEAREST), (0, 0))
    bd = ImageDraw.Draw(big)
    for i, ic in enumerate(icons):
        x, y = 8 + (i % 12) * 78, 548 + (i // 12) * 46
        e = ic.resize((36, 36), Image.NEAREST); big.paste(e, (x, y), e); bd.text((x + 40, y + 12), MAP[i].replace('_', ' ')[:9], fill=(230, 220, 200), font=g.font(10))
    big.save(os.path.join(g.BASE, 'preview_karte.png'))

if __name__ == '__main__':
    transitions(); daynight(); mapsyms()
