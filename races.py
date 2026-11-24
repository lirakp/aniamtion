"""Zivilisierte Völker aus der „Bibel der Welt“ – Lauf- und Idle-Animationen.
Völker: Mensch, Zwerg, Elf, Dunkelelf + Tiermenschen (Wolf, Hund, Hase, Katze, Fuchs, Echse, Drache, Hyäne, Frosch, Eule).
Halbwesen sehen zu 90–95 % wie ihr nicht-menschliches Elternvolk aus -> sie nutzen dessen Sprites.
Kleidung: 'tunika' oder 'ruestung'.

Aufruf: python3 races.py
Ausgabe: characters/voelker/<volk>_<kleidung>_walk.png  (5 Spalten x 4 Zeilen à 18x26)
         characters/voelker/<volk>_<kleidung>_idle.png  (6 Spalten x 4 Zeilen à 18x26)
         Zeilen: unten, links, rechts, oben. Walk: Spalte 0 = stehen, 1-4 = laufen. Idle: Bild 6 = blinzeln.
         preview_voelker_laufen.gif, preview_voelker_idle.gif, preview_voelker.png
"""
import os
from PIL import Image, ImageDraw
import generate as g, walk as w
from generate import C, shade, mix

OUT = os.path.join(g.BASE, 'characters', 'voelker')
CW, CH = w.CW, w.CH
P16 = lambda *parts: ''.join(parts)

# ================================================================ Overlays (Start-Zeile, Zeilen)
# -- Ohren / Kopfschmuck: vorne/hinten (FB) und Seite (S)
EARS = {
    'spitz':  ((2, ['....x......x....', '....xx....xx....', '....xyx..xyx....']),
               (3, ['.......x........', '......xyx.......'])),
    'fuchs':  ((1, ['...X........X...', '...xx......xx...', '...xyx....xyx...', '....xyx..xyx....']),
               (2, ['.......X........', '......xx........', '......xyx.......'])),
    'katze':  ((3, ['....x......x....', '....xy....yx....']),
               (4, ['......xx........'])),
    'lang':   ((0, ['.....xx..xx.....', '.....xy..yx.....', '.....xy..yx.....', '.....xy..yx.....', '.....xx..xx.....']),
               (0, ['.....xx.........', '.....xy.........', '......xy........', '......xy........', '......xx........'])),
    'haengend': ((5, ['...X........X...'] + ['..XX........XX..']*5),
                 (6, ['.....XX.........']*5)),
    'rund':   ((3, ['...xx......xx...', '...xy......yx...']),
               (3, ['......xx........', '......xy........'])),
    'buschel': ((3, ['...x........x...', '...xx......xx...']),
                (3, ['......x.........', '......xx........'])),
    'hoerner': ((1, ['...h........h...', '....h......h....', '....hh....hh....', '.....h....h.....']),
                (2, ['.....h..........', '.....hh.........', '......hh........'])),
    'kamm':   ((3, ['.......XX.......', '......XXXX......']),
               (3, ['......XXX.......', '.....XXXX.......'])),
    'elf':    ((6, ['..s'+'.'*10+'s..', '...s'+'.'*8+'s...']),
               (6, ['.....s..........', '......s.........', '......ss........'])),
}
# -- Schnauze / Gesicht (nur vorne + Seite)
MUZZLE = {
    'lang':  ((10, ['......mnnm......', '.....mmmmmm.....']), (10, ['.........mmmn...', '.........mmm....'])),
    'kurz':  ((10, ['.......nn.......', '......mmmm......']), (10, ['..........mn....'])),
    'frosch': ((4, ['....gg....gg....', '...gwwg..gwwg...', '...gwEg..gEwg...', '................',
                    '................', '................', '....nnnnnnnn....']),
               (4, ['........gg......', '........gwg.....', '........gEg.....', '................',
                    '................', '................', '.........nnnn...'])),
    'eule':  ((7, ['....www..www....', '....wew..wew....', '....www..www....', '.......bb.......']),
              (7, ['........www.....', '........wew.....', '........www.....', '...........b....'])),
}
SPOTS = ((6, ['.....z....z.....', '........z.......', '................', '................', '......z.........']),
         (6, ['......z.........', '.....z..z.......']))
# -- Schwänze: vorne (hinter dem Körper), Seite (hinter dem Körper), hinten (über dem Körper)
TAILS = {
    'buschig': ((15, ['.'*13+'tt.', '.'*13+'tt.', '.'*13+'tT.']),
                (15, ['...ttt..........', '..tttt..........', '.ttt............', '.tT.............']),
                (16, ['.......tt.......', '......tttt......', '......tttt......', '.......tT.......'])),
    'duenn':   ((14, ['.'*14+'t.']*4),
                (12, ['..t.............', '..t.............', '...t............', '....t...........']),
                (16, ['........t.......', '........t.......', '.........t......', '.........t......'])),
    'puschel': ((16, ['.'*13+'t..']),
                (16, ['...tt...........']),
                (16, ['.......tt.......', '.......tt.......'])),
    'hund':    ((15, ['.'*13+'t..', '.'*13+'tt.']),
                (14, ['...t............', '...t............', '....tt..........']),
                (15, ['........t.......', '........t.......', '.......tt.......'])),
    'echse':   ((17, ['.'*13+'tt.']*3 + ['.'*14+'t.']),
                (16, ['....tt..........', '...tt...........', '..tt............', '.tt.............', 't'+'.'*15]),
                (16, ['......tttt......', '......tttt......', '.......tt.......', '.......tt.......', '........t.......', '........T.......'])),
    'quaste':  ((16, ['.'*13+'tt.', '.'*13+'TT.']),
                (16, ['...ttt..........', '..TT............']),
                (16, ['.......tt.......', '.......TT.......'])),
}
# -- Haare / Bärte für Humanoide (nutzt die bestehenden Vorlagen)
DWARF_BEARD = ((10, ['....f......f....', '....'+'f'*8+'....', '....'+'f'*8+'....', '....'+'f'*8+'....',
                     '.....'+'f'*6+'.....', '......ffff......', '.......ff.......']),
               (10, ['........f.......', '.......'+'f'*5+'....', '.......'+'f'*4+'.....', '.......'+'f'*4+'.....',
                     '........fff.....', '........ff......']))
# -- Kleidung
HEM = {'fb': (17, ['....'+'a'*8+'....', '...'+'a'*10+'...']), 'side': (17, ['.....'+'a'*6+'.....', '....'+'a'*7+'.....'])}
PAULDRON = {'fb': (13, ['..PP'+'.'*8+'PP..', '..P'+'.'*10+'P..']), 'side': (13, ['......PPP.......', '......PP........'])}

STEEL, STEEL_D, MAIL = C('#aeb2c2'), C('#868a9c'), C('#7a7e8e')
OUTFITS = {
    'tunika':   dict(l=C('#5a3a2a'), p=C('#5e4636'), b=C('#3b2a2a')),
    'ruestung': dict(c=STEEL, C=MAIL, l=C('#5a3a2a'), p=C('#3e3a4a'), b=C('#2a2228'), hem=MAIL, pauldron=C('#c8ccd8')),
}

# ================================================================ Völker
def fur(base, muzzle=None, inner=None, dark=None):
    return dict(s=base, S=shade(base, .82), k=base, m=muzzle or mix(base, (255,)*4, .45),
                y=inner or shade(base, .65), X=dark or shade(base, .62))

RACES = [
    dict(name='mensch', title='Mensch', tunic=C('#4a6aa0'), hair=('kurz', C('#6a4a30'))),
    dict(name='zwerg', title='Zwerg', tunic=C('#5a7a4a'), hair=('kurz', C('#a0522d')), dwarf=True,
         s=C('#e8b48a'), S=C('#c48a66')),
    dict(name='elf', title='Elf', tunic=C('#3e7a5a'), hair=('lang', C('#f0d890')), ears='elf',
         s=C('#f6dcc0'), S=C('#dcb498'), e=C('#2a5a3a')),
    dict(name='dunkelelf', title='Dunkelelf', tunic=C('#5a3a7a'), hair=('lang', C('#e8e4f0')), ears='elf',
         s=C('#7a6a90'), S=C('#5e4e74'), k=C('#8a6a9a'), e=C('#e05a6a')),
    dict(name='wolf', title='Wolf', tunic=C('#6a5a8a'), animal=True, ears='spitz', muzzle='lang', tail='buschig',
         **fur(C('#8a8a9a'), C('#d4d4dc'), C('#5a5a6a')), n=g.EYE),
    dict(name='hund', title='Hund', tunic=C('#a84a4a'), animal=True, ears='haengend', muzzle='lang', tail='hund',
         **fur(C('#b07a48'), C('#ecd2a8'), dark=C('#7a4e2e')), n=g.EYE),
    dict(name='hase', title='Hase', tunic=C('#7a9a5a'), animal=True, ears='lang', muzzle='kurz', tail='puschel',
         **fur(C('#e6ded2'), C('#f8f4ee'), C('#e8a0b0')), n=C('#e888a0'), t=C('#f8f4ee')),
    dict(name='katze', title='Katze', tunic=C('#c88a3a'), animal=True, ears='katze', muzzle='kurz', tail='duenn',
         **fur(C('#4a4458'), C('#6a6478'), C('#e8a0b0')), n=C('#e888a0'), e=C('#e8d040')),
    dict(name='fuchs', title='Fuchs', tunic=C('#3e6a7a'), animal=True, ears='fuchs', muzzle='lang', tail='buschig',
         **fur(C('#e07a34'), C('#f4ece0'), C('#3a2a2a'), C('#3a2a2a')), n=g.EYE, T=C('#f4ece0')),
    dict(name='echse', title='Echse', tunic=C('#8a6a3a'), animal=True, ears='kamm', muzzle='lang', tail='echse',
         **fur(C('#5a9a5a'), C('#c8d890'), dark=C('#3e7a44')), n=C('#2e4e34'), e=C('#e0c040')),
    dict(name='drache', title='Drache', tunic=C('#3a3a5a'), animal=True, ears='hoerner', muzzle='lang', tail='echse',
         **fur(C('#b84a4a'), C('#e8c070'), dark=C('#8a2e36')), n=C('#5a1e26'), e=C('#ffd040'),
         h=C('#e8dcc0'), T=C('#8a2e36')),
    dict(name='hyaene', title='Hyäne', tunic=C('#6a7a4a'), animal=True, ears='rund', muzzle='lang', tail='quaste', spots=True,
         **fur(C('#c8a870'), C('#5a4030'), C('#7a5a3a')), n=g.EYE, z=C('#7a5a3a'), T=C('#4a3428')),
    dict(name='frosch', title='Frosch', tunic=C('#a86a4a'), animal=True, muzzle='frosch',
         **fur(C('#6a9a55'), dark=C('#4a7a45')), g=C('#6a9a55'), w=C('#f4f0e0'), E=g.EYE, n=C('#3a5a34'), e=C('#6a9a55')),
    dict(name='eule', title='Eule', tunic=C('#4a5a8a'), animal=True, ears='buschel', muzzle='eule',
         **fur(C('#8a6a4a'), C('#d8c8a8'), C('#6a4e34')), w=C('#f0e4c8'), b=C('#e0a040')),
]

# ================================================================ Zeichnen
def pal_for(race, outfit):
    o = OUTFITS[outfit]
    c = o.get('c', race['tunic'])
    p = {'s': race.get('s', g.SKIN), 'S': race.get('S', g.SKIN_S), 'k': race.get('k', g.BLUSH),
         'e': race.get('e', g.EYE), 'c': c, 'C': o.get('C', shade(c, .82)), 'l': o['l'], 'p': o['p'], 'b': o['b']}
    return p

def feature_pal(race):
    keys = ('x', 'y', 'X', 'm', 'n', 'h', 'g', 'w', 'E', 'b', 'z')
    p = {k: race[k] for k in keys if k in race}
    p['x'] = race.get('s', g.SKIN); p.setdefault('y', shade(p['x'], .7)); p.setdefault('X', shade(p['x'], .65))
    p['s'] = race.get('s', g.SKIN)
    if 'e' in race: p['e'] = race['e']
    return p

def tail_pal(race):
    base = race.get('s')
    return {'t': base, 'T': race.get('T', shade(base, .7))}

def finish(img, dwarf):
    img = w.finish(img)
    if dwarf:   # 2 Zeilen kürzer: eine Rumpf- und eine Beinzeile entfernen
        src = img.copy(); img = Image.new('RGBA', src.size, (0, 0, 0, 0))
        keep = [y for y in range(CH) if y not in (16, 20)]
        for i, y in enumerate(keep):
            img.paste(src.crop((0, y, CW, y+1)), (0, i+2))
    return img

def blinkify(rows):
    return w._blink(rows)

def frame_fb(race, outfit, back, legs, dy, blink=False):
    img, px = g.new(CW, CH); pal = pal_for(race, outfit); o = OUTFITS[outfit]
    fp = feature_pal(race)
    if race.get('tail') and not back:
        s, rows = TAILS[race['tail']][0]; w.paint(px, s, rows, tail_pal(race), dy)
    w.paint(px, 17, w.FB_LEGS[legs], pal)
    top = w.BACK_TOP if back else (blinkify(w.FRONT_TOP) if blink else w.FRONT_TOP)
    w.paint(px, 0, top, pal, dy)
    s, rows = HEM['fb']; w.paint(px, s, rows, {'a': o.get('hem', pal['c'])}, dy)
    if 'pauldron' in o: s, rows = PAULDRON['fb']; w.paint(px, s, rows, {'P': o['pauldron']}, dy)
    if race.get('animal'):
        if race.get('spots'): s, rows = SPOTS[0]; w.paint(px, s, rows, fp, dy)
        if race.get('muzzle') and not back:
            s, rows = MUZZLE[race['muzzle']][0]
            if blink and race['muzzle'] in ('frosch', 'eule'):
                rows = [r.replace('E', 'g').replace('e', 'w') for r in rows]
            w.paint(px, s, rows, fp, dy)
    else:
        hs, hc = race['hair']
        s, rows = g.HAIR[hs]; w.paint(px, s, rows, {'h': hc}, dy)
        if back and hs in w.BACK_HAIR_FILL:
            s, rows = w.BACK_HAIR_FILL[hs]; w.paint(px, s, rows, {'h': hc}, dy)
        if race.get('dwarf') and not back:
            s, rows = DWARF_BEARD[0]; w.paint(px, s, rows, {'f': hc}, dy)
    if race.get('ears'):
        s, rows = EARS[race['ears']][0]; w.paint(px, s, rows, fp, dy)
    if race.get('tail') and back:
        s, rows = TAILS[race['tail']][2]; w.paint(px, s, rows, tail_pal(race), dy)
    return finish(img, race.get('dwarf'))

def frame_side(race, outfit, legs, arm, near_front, dy, blink=False):
    img, px = g.new(CW, CH); pal = pal_for(race, outfit); o = OUTFITS[outfit]
    fp = feature_pal(race)
    lp = pal['p']; lpal = dict(pal, F=lp if near_front else shade(lp, .72), B=shade(lp, .72) if near_front else lp)
    if race.get('tail'):
        s, rows = TAILS[race['tail']][1]; w.paint(px, s, rows, tail_pal(race), dy)
    w.paint(px, 17, w.SIDE_LEGS[legs], lpal)
    w.paint(px, 0, blinkify(w.SIDE_TOP) if blink else w.SIDE_TOP, pal, dy)
    s, rows = HEM['side']; w.paint(px, s, rows, {'a': o.get('hem', pal['c'])}, dy)
    s, rows = w.SIDE_ARM[arm]; w.paint(px, s, rows, pal, dy)
    if 'pauldron' in o: s, rows = PAULDRON['side']; w.paint(px, s, rows, {'P': o['pauldron']}, dy)
    if race.get('animal'):
        if race.get('spots'): s, rows = SPOTS[1]; w.paint(px, s, rows, fp, dy)
        if race.get('muzzle'):
            s, rows = MUZZLE[race['muzzle']][1]
            if blink and race['muzzle'] in ('frosch', 'eule'):
                rows = [r.replace('E', 'g').replace('e', 'w') for r in rows]
            w.paint(px, s, rows, fp, dy)
    else:
        hs, hc = race['hair']
        s, rows = w.SIDE_HAIR[hs]; w.paint(px, s, rows, {'h': hc}, dy)
        if race.get('dwarf'):
            s, rows = DWARF_BEARD[1]; w.paint(px, s, rows, {'f': hc}, dy)
    if race.get('ears'):
        s, rows = EARS[race['ears']][1]; w.paint(px, s, rows, fp, dy)
    return finish(img, race.get('dwarf'))

def walk_dirs(race, outfit):
    fb = lambda back: [frame_fb(race, outfit, back, 'stand', 0), frame_fb(race, outfit, back, 'a', 1),
                       frame_fb(race, outfit, back, 'stand', 0), frame_fb(race, outfit, back, 'b', 1),
                       frame_fb(race, outfit, back, 'stand', 0)]
    right = [frame_side(race, outfit, 'stand', 'mid', True, 0),
             frame_side(race, outfit, 'contact', 'back', True, 1), frame_side(race, outfit, 'pass', 'mid', True, 0),
             frame_side(race, outfit, 'contact', 'fwd', False, 1), frame_side(race, outfit, 'pass', 'mid', True, 0)]
    return {'unten': fb(False), 'links': [f.transpose(Image.FLIP_LEFT_RIGHT) for f in right], 'rechts': right, 'oben': fb(True)}

DY, BLINK = [0, 0, 1, 1, 0, 0], [False]*5 + [True]
def idle_dirs(race, outfit):
    down = [frame_fb(race, outfit, False, 'stand', d, b) for d, b in zip(DY, BLINK)]
    up = [frame_fb(race, outfit, True, 'stand', d) for d in DY]
    right = [frame_side(race, outfit, 'stand', 'mid', True, d, b) for d, b in zip(DY, BLINK)]
    return {'unten': down, 'links': [f.transpose(Image.FLIP_LEFT_RIGHT) for f in right], 'rechts': right, 'oben': up}

def sheet(dirs, cols):
    s = Image.new('RGBA', (CW*cols, CH*4), (0, 0, 0, 0))
    for r, d in enumerate(w.ORDER):
        for c, f in enumerate(dirs[d]): s.alpha_composite(f, (c*CW, r*CH))
    return s

def main():
    os.makedirs(OUT, exist_ok=True)
    data = []
    for race in RACES:
        for outfit in OUTFITS:
            wd, idd = walk_dirs(race, outfit), idle_dirs(race, outfit)
            sheet(wd, 5).save(os.path.join(OUT, f"{race['name']}_{outfit}_walk.png"))
            sheet(idd, 6).save(os.path.join(OUT, f"{race['name']}_{outfit}_idle.png"))
            data.append((race, outfit, wd, idd))
    # Vorschauen
    S, n = 4, len(RACES)
    Wd = 20 + n*(CW*S + 6); Hd = 60 + 4*CH*S + 30
    def make(frames_of, count, title, path, dur):
        out = []
        for k in range(count):
            im = Image.new('RGBA', (Wd, Hd), g.SKY_NIGHT); d = ImageDraw.Draw(im)
            d.text((20, 10), title, fill=(255, 240, 200), font=g.font(18))
            for i, race in enumerate(RACES):
                x = 20 + i*(CW*S + 6)
                d.text((x, 36), race['title'], fill=(230, 220, 200), font=g.font(11))
                for row, (outfit, view) in enumerate((('tunika', 'unten'), ('tunika', 'rechts'), ('ruestung', 'unten'), ('ruestung', 'oben'))):
                    dirs = next(dd for (r, o, *dd) in data if r is race and o == outfit)
                    f = frames_of(dirs)[view][k]
                    im.alpha_composite(f.resize((CW*S, CH*S), Image.NEAREST), (x, 54 + row*CH*S))
            out.append(im.convert('RGB'))
        out[0].save(path, save_all=True, append_images=out[1:], duration=dur, loop=0)
        return out[0]
    first = make(lambda dd: {k: v[1:] for k, v in dd[0].items()}, 4,
                 'Völker: Laufen  (Tunika vorne / Tunika Seite / Rüstung vorne / Rüstung hinten)',
                 os.path.join(g.BASE, 'preview_voelker_laufen.gif'), 150)
    make(lambda dd: dd[1], 6, 'Völker: Idle (Atmen + Blinzeln)',
         os.path.join(g.BASE, 'preview_voelker_idle.gif'), [200, 200, 200, 200, 200, 130])
    first.save(os.path.join(g.BASE, 'preview_voelker.png'))

if __name__ == '__main__':
    main()
