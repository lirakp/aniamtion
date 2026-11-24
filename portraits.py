"""Dialog-Porträts (40x40) für alle Völker: 6 Gesichtsausdrücke × 3 Frames (Mund zu, Mund offen, Blinzeln),
je in Tunika und Rüstung.
Aufruf: python3 portraits.py
Ausgabe: portraits/<volk>_<kleidung>.png (Zeilen = Ausdrücke, Spalten = Frames), portraits/portraits.json,
         preview_portraits.gif, preview_portraits_dialog.gif
"""
import os, json
from PIL import Image, ImageDraw
import generate as g
from generate import C, shade, mix
import races as rc, ui

OUT = os.path.join(g.BASE, 'portraits')
SZ = 40
INK, WHITE = C('#2b1e33'), C('#ffffff')
MOUTH, MOUTH_IN, TEAR = C('#6a2a3a'), C('#a83a4a'), C('#8ad0ff')
EXPR = ['neutral', 'freude', 'wut', 'traurig', 'ueberrascht', 'verlegen']
FRAMES = ['zu', 'spricht', 'blinzeln']
def m(x): return 40 - x  # spiegeln an der Gesichtsmitte

def ears(d, race, skin, inner, dark, back):
    t = race.get('ears')
    if back:
        if t == 'elf':
            for s in (1, -1):
                xs = (lambda x: x) if s == 1 else m
                d.polygon([(xs(12), 15), (xs(3), 9), (xs(5), 12), (xs(12), 21)], fill=skin); d.line([(xs(11), 16), (xs(6), 12)], fill=shade(skin, .8))
        elif t in ('spitz', 'katze', 'fuchs'):
            top, base = {'spitz': (3, 10), 'katze': (4, 11), 'fuchs': (1, 9)}[t]
            for xs in ((lambda x: x), m):
                d.polygon([(xs(11), 16), (xs(12), top), (xs(base + 9), 9)], fill=skin); d.polygon([(xs(13), 13), (xs(13), top + 4), (xs(base + 6), 10)], fill=inner)
                if t == 'fuchs': d.line([(xs(12), top), (xs(13), top + 2)], fill=dark)
        elif t == 'lang':
            for x0 in (12, 23):
                d.ellipse([x0, -2, x0 + 5, 14], fill=skin); d.ellipse([x0 + 1, 1, x0 + 4, 12], fill=inner)
        elif t == 'rund':
            for xs in ((lambda x: x), m):
                x0, x1 = sorted((xs(10), xs(17))); d.ellipse([x0, 4, x1, 11], fill=skin); d.ellipse([x0 + 2, 6, x1 - 2, 10], fill=inner)
        elif t == 'buschel':
            for xs in ((lambda x: x), m): d.polygon([(xs(12), 12), (xs(10), 2), (xs(17), 9)], fill=dark)
        elif t == 'hoerner':
            for xs in ((lambda x: x), m): d.polygon([(xs(14), 10), (xs(9), 1), (xs(11), 1), (xs(17), 8)], fill=race['h']); d.line([(xs(10), 2), (xs(13), 6)], fill=shade(race['h'], .8))
        elif t == 'kamm':
            for x in (16, 20, 24): d.polygon([(x - 2, 9), (x, 3 + (x == 20) * -1), (x + 2, 9)], fill=dark)
    else:
        if t == 'haengend':
            d.ellipse([6, 9, 14, 27], fill=dark); d.ellipse([26, 9, 34, 27], fill=dark)

def eyes(d, px, ex, ey, ecol, expr, blink, brow, big=False):
    for i, x in enumerate(ex):
        side = -1 if i == 0 else 1  # -1 links, +1 rechts; "innen" = zur Mitte
        inner_x, outer_x = (x + 2, x - 1) if side == -1 else (x - 1, x + 2)
        if blink:
            d.line([(x - 1, ey + 2), (x + 2, ey + 2)], fill=INK)
        elif expr == 'freude':
            for p in ((x - 1, ey + 2), (x, ey + 1), (x + 1, ey + 1), (x + 2, ey + 2)): px[p] = INK
        elif expr == 'ueberrascht':
            d.rectangle([x - 1, ey - 1, x + 2, ey + 2], fill=WHITE); d.rectangle([x, ey, x + 1, ey + 1], fill=ecol)
        else:
            d.rectangle([x, ey, x + 1, ey + 2], fill=ecol)
            if big: d.rectangle([x - 1, ey, x + 2, ey + 2], fill=ecol)
            hx = x - 1 if (big and side == -1) else x
            px[hx if expr != 'verlegen' else x + 1, ey] = WHITE
            if expr == 'traurig': d.line([(x, ey), (x + 1, ey)], fill=shade(ecol, 1.0) if False else ecol)
        # Brauen
        if expr == 'wut': d.line([(outer_x, ey - 3), (inner_x, ey - 1)], fill=brow)
        elif expr == 'traurig': d.line([(outer_x, ey - 1), (inner_x, ey - 3)], fill=brow)
        elif expr == 'ueberrascht': d.line([(x - 1, ey - 3), (x + 2, ey - 3)], fill=brow)
        elif expr == 'verlegen': d.line([(outer_x, ey - 2), (inner_x, ey - 3)], fill=brow)
        else: d.line([(x - 1, ey - 2), (x + 2, ey - 2)], fill=brow)
    if expr == 'traurig' and not blink: px[ex[0], ey + 3] = TEAR; px[ex[0], ey + 4] = TEAR

def mouth(d, px, cx, cy, expr, talk, w=2, teeth=False):
    if expr == 'freude':
        if talk: d.polygon([(cx - w, cy - 1), (cx + w, cy - 1), (cx + w - 1, cy + 1), (cx - w + 1, cy + 1)], fill=MOUTH); d.line([(cx - 1, cy + 1), (cx + 1, cy + 1)], fill=MOUTH_IN)
        else: d.line([(cx - w, cy - 1), (cx - w + 1, cy), (cx + w - 1, cy), (cx + w, cy - 1)], fill=MOUTH)
    elif expr == 'wut':
        if talk: d.rectangle([cx - w + 1, cy - 1, cx + w - 1, cy + 1], fill=MOUTH); d.line([(cx - w + 1, cy - 1), (cx + w - 1, cy - 1)], fill=WHITE)
        else: d.line([(cx - w, cy + 1), (cx - w + 1, cy), (cx + w - 1, cy), (cx + w, cy + 1)], fill=MOUTH)
        if teeth: px[cx - w + 1, cy + 1 + talk] = WHITE; px[cx + w - 1, cy + 1 + talk] = WHITE
    elif expr == 'traurig':
        if talk: d.rectangle([cx - 1, cy, cx + 1, cy + 1], fill=MOUTH)
        else: d.line([(cx - w + 1, cy + 1), (cx - 1, cy), (cx + 1, cy), (cx + w - 1, cy + 1)], fill=MOUTH)
    elif expr == 'ueberrascht':
        if talk: d.ellipse([cx - 2, cy - 1, cx + 2, cy + 3], fill=MOUTH)
        else: d.rectangle([cx - 1, cy, cx + 1, cy + 2], fill=MOUTH)
    elif expr == 'verlegen':
        if talk: d.rectangle([cx - 1, cy, cx + 1, cy + 1], fill=MOUTH)
        else: d.line([(cx - w, cy), (cx - 1, cy - 1), (cx, cy), (cx + 1, cy - 1), (cx + w, cy)], fill=MOUTH)
    else:
        if talk: d.rectangle([cx - 1, cy, cx + 1, cy + 1], fill=MOUTH); px[cx, cy + 1] = MOUTH_IN
        else: d.line([(cx - w + 1, cy), (cx + w - 1, cy)], fill=MOUTH)

def body(d, outfit, race):
    pal = rc.pal_for(race, outfit); o = rc.OUTFITS[outfit]
    c = pal['c']; cd = shade(c, .78)
    d.polygon([(3, 40), (6, 33), (13, 30), (27, 30), (34, 33), (37, 40)], fill=c)
    d.polygon([(28, 30), (34, 33), (37, 40), (30, 40)], fill=cd)
    if outfit == 'ruestung':
        mail = o['C']; d.polygon([(14, 30), (26, 30), (23, 36), (17, 36)], fill=mail)
        for x in range(15, 26, 2): d.point((x, 32), fill=shade(mail, .8)); d.point((x + 1, 34), fill=shade(mail, .8))
        for x0 in (3, 27):
            d.ellipse([x0, 30, x0 + 10, 39], fill=o['pauldron'], outline=shade(o['pauldron'], .62)); d.arc([x0, 30, x0 + 10, 39], 180, 300, fill=WHITE); d.line([(x0 + 2, 36), (x0 + 8, 36)], fill=shade(o['pauldron'], .75))
    else:
        d.polygon([(15, 30), (25, 30), (20, 35)], fill=shade(c, .65))
        d.line([(20, 35), (20, 39)], fill=shade(c, .65)); d.point((20, 37), fill=C('#e0b048'))
        d.line([(6, 36), (11, 33)], fill=mix(c, WHITE, .25))

def portrait(race, outfit, expr, frame):
    im = Image.new('RGBA', (SZ, SZ)); d = ImageDraw.Draw(im); px = im.load()
    animal = race.get('animal'); dwarf = race.get('dwarf')
    fp = rc.feature_pal(race); pal = rc.pal_for(race, outfit)
    skin, skin_s = (race['s'], race.get('S', shade(race['s'], .82))) if 's' in race else (g.SKIN, g.SKIN_S)
    inner = fp.get('y', shade(skin, .7)); dark = fp.get('X', shade(skin, .62))
    ecol = race.get('e', g.EYE)
    hair_t, hair_c = race.get('hair', (None, None))
    talk, blink = frame == 'spricht', frame == 'blinzeln'
    muz = race.get('muzzle')

    # Hinterer Teil: lange Haare, Ohren
    if hair_t == 'lang':
        d.rounded_rectangle([9, 9, 31, 34], 6, fill=shade(hair_c, .85))
    ears(d, race, skin, inner, dark, back=True)
    body(d, outfit, race)
    d.rectangle([17, 26, 23, 31], fill=skin_s)

    # Kopf
    if muz == 'frosch': head = [7, 10, 33, 30]
    elif dwarf: head = [10, 9, 30, 30]
    elif muz == 'eule': head = [9, 7, 31, 30]
    else: head = [11, 7, 29, 29]
    d.ellipse(head, fill=skin_s); d.ellipse([head[0], head[1], head[2] - 2, head[3] - 1], fill=skin)
    ex, ey, mcx, mcy, mw = (15, 23), 16, 20, 24, 2

    if muz == 'frosch':
        for x0 in (9, 23):
            d.ellipse([x0, 5, x0 + 8, 14], fill=skin); d.ellipse([x0 + 1, 6, x0 + 7, 13], fill=fp.get('w', WHITE))
        ex, ey, mcy, mw = (12, 26), 8, 23, 6
        d.point((16, 17), fill=fp['n']); d.point((23, 17), fill=fp['n'])
    elif muz == 'eule':
        d.ellipse([11, 10, 19, 21], fill=fp['w']); d.ellipse([21, 10, 29, 21], fill=fp['w'])
        d.ellipse([11, 19, 29, 28], fill=mix(skin, fp['w'], .4))
        ex, ey = (14, 24), 14
    elif muz in ('lang', 'kurz'):
        mz = fp.get('m', mix(skin, WHITE, .4))
        if muz == 'lang': d.ellipse([14, 18, 26, 28], fill=mz); d.rectangle([18, 19, 22, 20], fill=fp.get('n', INK)); d.point((19, 19), fill=mix(fp.get('n', INK), WHITE, .4))
        else: d.ellipse([15, 19, 25, 27], fill=mz); d.rectangle([19, 20, 21, 21], fill=fp.get('n', INK))
        mcy = 24 if muz == 'kurz' else 25
        if race.get('spots'):
            for p in ((13, 11), (16, 9), (26, 12), (12, 15), (27, 16)): d.point(p, fill=race.get('z', dark))
        if race['name'] == 'drache':
            for y in (10, 12): d.line([(19, y), (21, y)], fill=shade(skin, .75))
        if race['name'] in ('katze', 'hase'):
            for s in (-1, 1):
                d.line([(20 + s * 6, 22), (20 + s * 10, 21)], fill=mix(mz, WHITE, .5)); d.line([(20 + s * 6, 23), (20 + s * 10, 24)], fill=mix(mz, WHITE, .5))
    ears(d, race, skin, inner, dark, back=False)

    # Haare vorne
    if hair_t:
        d.chord([head[0] - 1, head[1] - 2, head[2] + 1, head[1] + 14], 180, 360, fill=hair_c)
        for x in range(head[0] + 1, head[2] - 1, 3): d.polygon([(x, head[1] + 6), (x + 3, head[1] + 6), (x + 1, head[1] + 9 + (x % 2))], fill=hair_c)
        d.line([(head[0] + 3, head[1] + 1), (head[0] + 7, head[1] - 1)], fill=mix(hair_c, WHITE, .3))
        if hair_t == 'lang':
            d.rectangle([head[0] - 1, head[1] + 6, head[0] + 1, head[3] + 3], fill=hair_c); d.rectangle([head[2] - 1, head[1] + 6, head[2] + 1, head[3] + 3], fill=hair_c)
    if race.get('ears') == 'elf' and race['name'] == 'dunkelelf':
        d.point((14, 21), fill=C('#e8e4f0')); d.point((26, 21), fill=C('#e8e4f0'))  # Gesichtszeichnung

    brow = shade(hair_c, .8) if hair_c else (fp.get('n', dark) if muz == 'frosch' else dark)
    eyes(d, px, ex, ey, fp.get('E', ecol) if muz == 'frosch' else (INK if muz == 'eule' else ecol), expr, blink, brow, big=muz in ('eule', 'frosch'))
    if muz == 'eule':
        for x in ex:
            if not blink and expr not in ('freude', 'ueberrascht'): d.rectangle([x - 1, ey - 1, x + 2, ey - 1], fill=C('#e0a040')) if False else None
        beak = fp.get('b', C('#e0a040'))
        d.polygon([(18, 20), (22, 20), (20, 25 if not talk else 23)], fill=beak)
        if talk: d.polygon([(19, 24), (21, 24), (20, 26)], fill=shade(beak, .8)); d.line([(19, 23), (21, 23)], fill=MOUTH)
    elif dwarf:
        d.polygon([(10, 20), (30, 20), (28, 32), (20, 37), (12, 32)], fill=hair_c)
        for y in (24, 28, 32): d.line([(16, y), (17, y + 2)], fill=shade(hair_c, .8)); d.line([(24, y), (23, y + 2)], fill=shade(hair_c, .8))
        d.rectangle([16, 23, 24, 26], fill=skin) if talk or expr in ('ueberrascht',) else None
        mouth(d, px, 20, 24, expr, talk, 2)
        d.line([(14, 22), (19, 21)], fill=shade(hair_c, .75)); d.line([(21, 21), (26, 22)], fill=shade(hair_c, .75))
        d.point((20, 20), fill=shade(skin, .85)); d.point((21, 21), fill=shade(skin, .85))  # Nase
    else:
        if not muz: d.point((20, 21), fill=skin_s); d.point((21, 21), fill=skin_s)
        if race['name'] == 'hyaene': globals()['MOUTH'] = C('#2b1e33')
        mouth(d, px, mcx, mcy, expr, talk, mw, teeth=race['name'] in ('wolf', 'hyaene', 'drache', 'echse'))
    globals()['MOUTH'] = C('#6a2a3a')
    # Wangen / Schweiß
    if expr in ('freude', 'verlegen') and muz not in ('eule',):
        bl = race.get('k', g.BLUSH) if not animal else C('#e8a0b0')
        by = 20 if muz != 'frosch' else 19
        for x in (ex[0] - 2, ex[0] - 1, ex[1] + 2, ex[1] + 3): px[x, by] = bl
    if expr == 'verlegen':
        d.line([(31, 9), (31, 12)], fill=TEAR); d.point((30, 11), fill=TEAR); d.point((32, 11), fill=TEAR)
    if expr == 'wut':
        for p in ((30, 6), (32, 6), (31, 5), (31, 7)): px[p] = C('#e0443a')
    return g.outline(im)

def sheet(race, outfit):
    s = Image.new('RGBA', (SZ * len(FRAMES), SZ * len(EXPR)))
    for r, e in enumerate(EXPR):
        for c, f in enumerate(FRAMES): s.alpha_composite(portrait(race, outfit, e, f), (c * SZ, r * SZ))
    return s

def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {'groesse': SZ, 'zeilen_ausdruecke': EXPR, 'spalten_frames': FRAMES,
            'hinweis': 'Beim Sprechen zwischen "zu" und "spricht" wechseln (ca. 8 fps); alle 2–4 s kurz "blinzeln".', 'dateien': []}
    sheets = {}
    for race in rc.RACES:
        for outfit in rc.OUTFITS:
            s = sheet(race, outfit); sheets[(race['name'], outfit)] = s
            fn = f'{race["name"]}_{outfit}.png'; s.save(os.path.join(OUT, fn)); meta['dateien'].append(fn)
    json.dump(meta, open(os.path.join(OUT, 'portraits.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def cut(race, outfit, e, f):
        return sheets[(race, outfit)].crop((FRAMES.index(f) * SZ, EXPR.index(e) * SZ, (FRAMES.index(f) + 1) * SZ, (EXPR.index(e) + 1) * SZ))
    # Vorschau 1: alle Völker × Ausdrücke (Tunika links, Rüstung rechts als zweite Hälfte)
    Z = 2; cw = SZ * Z + 4; names = [r['name'] for r in rc.RACES]
    W = 110 + cw * len(EXPR) * 2 + 20; H = 30 + len(names) * cw
    frames = []
    for t in range(8):
        im = Image.new('RGB', (W, H), (42, 36, 69)); d = ImageDraw.Draw(im)
        d.text((110, 8), 'Tunika: ' + ' · '.join(EXPR), fill=(255, 240, 200), font=g.font(12))
        d.text((110 + cw * len(EXPR) + 20, 8), 'Rüstung', fill=(255, 240, 200), font=g.font(12))
        f = 'blinzeln' if t == 6 else ('spricht' if t % 2 else 'zu')
        for r, n in enumerate(names):
            y = 30 + r * cw; d.text((8, y + cw // 2 - 7), rc.RACES[r]['title'], fill=(230, 220, 200), font=g.font(12))
            for half, outfit in enumerate(rc.OUTFITS):
                for c, e in enumerate(EXPR):
                    x = 110 + half * (cw * len(EXPR) + 20) + c * cw
                    d.rectangle([x, y, x + SZ * Z - 1, y + SZ * Z - 1], fill=(74, 62, 88))
                    p = cut(n, outfit, e, f).resize((SZ * Z, SZ * Z), Image.NEAREST); im.paste(p, (x, y), p)
        frames.append(im)
    frames[0].save(os.path.join(g.BASE, 'preview_portraits.gif'), save_all=True, append_images=frames[1:], duration=180, loop=0)

    # Vorschau 2: Dialogfenster im Spiel (320x180, 3-fach)
    bg = Image.new('RGBA', (320, 180), (42, 36, 69, 255))
    for k in range(4):
        p = os.path.join(g.BASE, 'level', 'parallax', f'dorf_nacht_{k}_' + ['himmel', 'berge', 'huegel', 'wald'][k] + '.png')
        if os.path.exists(p): bg.alpha_composite(Image.open(p).convert('RGBA').crop((0, 0, 320, 180)))
    lines = [('fuchs', 'tunika', 'freude', 'NA, AUCH AUF DEM WEG ZUR GILDE?'), ('zwerg', 'ruestung', 'wut', 'DER DUNGEON HAT MEINE AXT GEFRESSEN!'),
             ('elf', 'tunika', 'verlegen', 'ICH ... HABE DEN WEG VERGESSEN.'), ('frosch', 'tunika', 'ueberrascht', 'QUAK?! EIN MONSTERKERN, RANG S?!')]
    frame9 = ui.frame9('holz'); out = []
    for name, outfit, e, txt in lines:
        for t in range(len(txt) // 2 + 6):
            im = bg.copy(); box = ui.nine(frame9, 300, 52); im.alpha_composite(box, (10, 122))
            pf = 'blinzeln' if t == len(txt) // 2 + 4 else ('spricht' if t % 2 and t * 2 < len(txt) else 'zu')
            im.alpha_composite(cut(name, outfit, e, pf), (16, 128))
            title = next(r['title'] for r in rc.RACES if r['name'] == name).upper()
            ui.text(im, 62, 131, title, C('#e0b048'), shadow=INK)
            ui.text(im, 62, 143, txt[:t * 2], C('#f0e4cc'), shadow=INK)
            if t * 2 >= len(txt) and t % 2: im.alpha_composite(ui.weiter_pfeil(0), (296, 160)) if hasattr(ui, 'weiter_pfeil') else None
            out.append(im.resize((960, 540), Image.NEAREST).convert('RGB'))
    out[0].save(os.path.join(g.BASE, 'preview_portraits_dialog.gif'), save_all=True, append_images=out[1:], duration=90, loop=0)

if __name__ == '__main__':
    main()
