"""Laufanimationen in 4 Richtungen für alle Cosy-Figuren.
Aufruf: python3 walk.py
Ausgabe: characters/walk/<name>_walk.png  (Spritesheet 5x4 Zellen à 18x26)
         Zeilen: 0=unten, 1=links, 2=rechts, 3=oben
         Spalten: 0=stehen, 1-4=laufen
         characters/walk/<name>.gif + preview_laufen.gif / preview_laufen.png
"""
from PIL import Image, ImageDraw
import os
import generate as g

OUT = os.path.join(g.BASE, 'characters', 'walk')
CW, CH = 18, 26

# ---------------------------------------------------------------- FRONT / BACK
FRONT_TOP = g.BODY_TOP + ['...s' + '.'*8 + 's...']          # Hände gehören zum Oberkörper
BACK_TOP = [r.replace('e', 's').replace('k', 's') for r in FRONT_TOP]
FB_LEGS = {
    'stand': ['....'+'p'*8+'....', '....'+'p'*8+'....', '....ppp..ppp....', '....ppp..ppp....', '....bbb..bbb....', '....bbb..bbb....'],
    'a':     ['....'+'p'*8+'....', '....'+'p'*8+'....', '....ppp..ppp....', '....bbb..ppp....', '....bbb..bbb....', '.........bbb....'],
    'b':     ['....'+'p'*8+'....', '....'+'p'*8+'....', '....ppp..ppp....', '....ppp..bbb....', '....bbb..bbb....', '....bbb.........'],
}
FB_DRESS = {
    'stand': ['....'+'d'*8+'....', '....'+'d'*8+'....', '...'+'d'*10+'...', '...'+'d'*10+'...', '...'+'D'*10+'...', '.....bb..bb.....'],
    'a':     ['....'+'d'*8+'....', '....'+'d'*8+'....', '...'+'d'*10+'...', '...'+'d'*10+'...', '...'+'D'*10+'...', '....bb.....bb...'],
    'b':     ['....'+'d'*8+'....', '....'+'d'*8+'....', '...'+'d'*10+'...', '...'+'d'*10+'...', '...'+'D'*10+'...', '.....bbb.bb.....'],
}
BACK_HAIR_FILL = {  # Hinterkopf
    'kurz': (5, ['....'+'h'*8+'....']*6),
    'zoepfe': (5, ['....'+'h'*8+'....']*6),
    'dutt': (5, ['....'+'h'*8+'....']*6),
    'lang': (5, ['....'+'h'*8+'....']*10),
}
BACK_EXTRAS = {
    'schuerze': (16, ['....'+'a'*8+'....']),
    'latz': (13, ['.....a....a.....']*4),
    'tuch': g.EXTRAS['tuch'],
    'schal': (12, ['....'+'a'*8+'....', '....'+'a'*8+'....']),
}

# ---------------------------------------------------------------- SIDE (Blick nach rechts)
SIDE_TOP = ['.'*16]*5 + [
    '......'+'s'*5+'.....',
    '.....'+'s'*7+'....',
    '.....'+'s'*7+'....',
    '.....sssssess....',
    '.....sssssess....',
    '.....sssskss....',
    '.....'+'s'*8+'...',
    '......'+'S'*4+'......',
    '.....'+'c'*6+'.....',
    '.....'+'c'*6+'.....',
    '.....'+'c'*6+'.....',
    '.....'+'l'*6+'.....',
]
SIDE_TOP = [r[:16] if len(r) > 16 else r for r in SIDE_TOP]
SIDE_TOP[8] = SIDE_TOP[9] = '.....' + 'sssss' + 'e' + 's' + '....'
SIDE_TOP[10] = '.....' + 'ssss' + 'k' + 'ss' + '....'
SIDE_ARM = {
    'mid':  (13, ['.......CC.......']*4 + ['.......ss.......']),
    'fwd':  (13, ['.......CC.......', '........CC......', '........CC......', '.........ss.....']),
    'back': (13, ['.......CC.......', '......CC........', '......CC........', '.....ss.........']),
}
SIDE_LEGS = {
    'stand': ['.....'+'p'*6+'.....', '......FFF.......', '......FFF.......', '......FFF.......', '......bbbb......', '.'*16],
    'pass':  ['.....'+'p'*6+'.....', '......FFF.......', '......FFF.......', '......FFF.......', '......bbbb......', '.'*16],
    'contact': ['.....'+'p'*6+'.....', '.....BB..FF.....', '....BB....FF....', '....BB....FF....', '....bbb...bbb...', '.'*16],
}
SIDE_DRESS = {
    'stand': ['.....'+'d'*6+'.....', '.....'+'d'*7+'....', '....'+'d'*8+'....', '....'+'D'*8+'....', '......bbb.......', '.'*16],
    'pass':  ['.....'+'d'*6+'.....', '.....'+'d'*7+'....', '....'+'d'*8+'....', '....'+'D'*8+'....', '......bbb.......', '.'*16],
    'contact': ['.....'+'d'*6+'.....', '.....'+'d'*7+'....', '....'+'d'*8+'....', '....'+'D'*8+'....', '....bb....bb....', '.'*16],
}
_side_short = ['......hhhh......', '.....'+'h'*6+'.....', '....'+'h'*8+'....', '....'+'h'*8+'....',
               '....hhhhh.......', '....hhhh........', '....hhh.........', '....hh..........']
SIDE_HAIR = {
    'kurz': (3, _side_short),
    'lang': (3, _side_short + ['....hh..........']*5 + ['....h...........']),
    'dutt': (3, ['......hhhh......', '..hh.'+'h'*6+'.....', '..hhhhhhhhhh....', '..hhhhhhhhhh....', '...hhhhh........', '....hhhh........', '....hhh.........']),
    'zoepfe': (3, _side_short + ['...hh...........']*4 + ['...h............']),
    'glatze': (5, []),
}
SIDE_BEARD = (10, ['........f.......', '.......'+'f'*5+'....', '.......'+'f'*4+'.....', '........fff.....'])
SIDE_HATS = {
    'hut': (1, ['......tttt......', '.....'+'t'*6+'.....', '.....'+'T'*6+'.....', '...'+'t'*10+'...']),
    'koch': g.HATS['koch'], 'muetze': g.HATS['muetze'], 'stroh': g.HATS['stroh'],
    'kapuze': (3, ['......tttt......', '.....'+'t'*6+'.....', '....'+'t'*8+'....', '....'+'t'*8+'....']
                  + ['....tttt........']*6 + ['....'+'t'*7+'.....']),
    'suedwester': (3, ['......tttt......', '.....'+'t'*6+'.....', '...'+'t'*10+'...', '...ttt..........', '...tt...........']),
}
SIDE_EXTRAS = {
    'schuerze': (14, ['.........aaa....']*6),
    'latz': (13, ['.........aa.....']*4),
    'tuch': (13, ['....'+'a'*7+'.....']*2 + ['.....aaaaa......']),
    'schal': (12, ['.....'+'a'*6+'.....', '...'+'a'*7+'......', '...a............']),
}

def _blink(top):
    t = list(top); t[8] = t[8].replace('e', 's'); return t

def paint(px, start, rows, pal, dy=0):
    for r, row in enumerate(rows):
        assert len(row) == 16, (row, len(row))
        for x, ch in enumerate(row):
            if ch in pal and pal[ch] is not None:
                px[x+1, start+r+dy+1] = pal[ch]

def palette(cfg):
    c = cfg['c']; p = cfg.get('p')
    return {'s': g.SKIN, 'S': g.SKIN_S, 'k': g.BLUSH, 'e': g.EYE, 'c': c, 'C': g.shade(c, .82),
            'l': cfg.get('l', c), 'p': p, 'b': cfg['b'],
            'd': cfg.get('d'), 'D': g.shade(cfg['d'], .8) if cfg.get('d') else None}

def finish(img):
    px = img.load(); src = img.copy().load()
    for y in range(CH):
        for x in range(CW):
            if src[x, y][3] and src[x, y] != g.EYE:
                if x+1 < CW and src[x+1, y][3] == 0: px[x, y] = g.shade(src[x, y], .85)
                elif x-1 >= 0 and src[x-1, y][3] == 0: px[x, y] = g.mix(src[x, y], (255, 255, 255, 255), .12)
    return g.outline(img)

def frame_fb(cfg, back, legs, dy, blink=False):
    img, px = g.new(CW, CH); pal = palette(cfg)
    paint(px, 17, (FB_DRESS if cfg.get('d') else FB_LEGS)[legs], pal)
    paint(px, 0, BACK_TOP if back else (_blink(FRONT_TOP) if blink else FRONT_TOP), pal, dy)
    if 'extra' in cfg:
        name, col = cfg['extra']
        s, rows = (BACK_EXTRAS if back else g.EXTRAS)[name]; paint(px, s, rows, {'a': col}, dy)
    hs, hc = cfg['hair']
    if hc is not None:
        s, rows = g.HAIR[hs]; paint(px, s, rows, {'h': hc}, dy)
        if back and hs in BACK_HAIR_FILL:
            s, rows = BACK_HAIR_FILL[hs]; paint(px, s, rows, {'h': hc}, dy)
    if 'beard' in cfg and not back:
        paint(px, g.BEARD[0], g.BEARD[1], {'f': cfg['beard']}, dy)
    if 'hat' in cfg:
        n, t, T = cfg['hat']; s, rows = g.HATS[n]; paint(px, s, rows, {'t': t, 'T': T}, dy)
        if back and n == 'kapuze': paint(px, 5, ['....'+'t'*8+'....']*7, {'t': t}, dy)
    return finish(img)

def frame_side(cfg, legs, arm, near_front, dy, blink=False):
    img, px = g.new(CW, CH); pal = palette(cfg)
    lp = cfg.get('p') or cfg.get('d')
    near, far = lp, g.shade(lp, .72)
    lpal = dict(pal, F=near if near_front else far, B=far if near_front else near)
    paint(px, 17, (SIDE_DRESS if cfg.get('d') else SIDE_LEGS)[legs], lpal)
    paint(px, 0, _blink(SIDE_TOP) if blink else SIDE_TOP, pal, dy)
    if 'extra' in cfg:
        name, col = cfg['extra']; s, rows = SIDE_EXTRAS[name]; paint(px, s, rows, {'a': col}, dy)
    s, rows = SIDE_ARM[arm]; paint(px, s, rows, pal, dy)
    hs, hc = cfg['hair']
    if hc is not None:
        s, rows = SIDE_HAIR[hs]; paint(px, s, rows, {'h': hc}, dy)
    if 'beard' in cfg:
        paint(px, SIDE_BEARD[0], SIDE_BEARD[1], {'f': cfg['beard']}, dy)
    if 'hat' in cfg:
        n, t, T = cfg['hat']; s, rows = SIDE_HATS[n]; paint(px, s, rows, {'t': t, 'T': T}, dy)
    return finish(img)

def directions(cfg):
    """liefert dict richtung -> [stand, w1, w2, w3, w4]"""
    down = [frame_fb(cfg, False, 'stand', 0), frame_fb(cfg, False, 'a', 1), frame_fb(cfg, False, 'stand', 0),
            frame_fb(cfg, False, 'b', 1), frame_fb(cfg, False, 'stand', 0)]
    up = [frame_fb(cfg, True, 'stand', 0), frame_fb(cfg, True, 'a', 1), frame_fb(cfg, True, 'stand', 0),
          frame_fb(cfg, True, 'b', 1), frame_fb(cfg, True, 'stand', 0)]
    right = [frame_side(cfg, 'stand', 'mid', True, 0),
             frame_side(cfg, 'contact', 'back', True, 1), frame_side(cfg, 'pass', 'mid', True, 0),
             frame_side(cfg, 'contact', 'fwd', False, 1), frame_side(cfg, 'pass', 'mid', True, 0)]
    left = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in right]
    return {'unten': down, 'links': left, 'rechts': right, 'oben': up}

ORDER = ['unten', 'links', 'rechts', 'oben']

def main():
    os.makedirs(OUT, exist_ok=True)
    S = 5
    gif_frames = [Image.new('RGBA', (len(g.CHARACTERS)*CW*S + 40, 4*CH*S + 50), g.SKY_NIGHT) for _ in range(4)]
    static = Image.new('RGBA', (len(g.CHARACTERS)*CW*S + 40, 4*CH*S + 50), g.SKY_NIGHT)
    for ci, cfg in enumerate(g.CHARACTERS):
        dirs = directions(cfg)
        sheet = Image.new('RGBA', (CW*5, CH*4), (0, 0, 0, 0))
        for r, d in enumerate(ORDER):
            for c, fr in enumerate(dirs[d]): sheet.alpha_composite(fr, (c*CW, r*CH))
        sheet.save(os.path.join(OUT, f"{cfg['name']}_walk.png"))
        # Einzel-GIF: 4 Richtungen nebeneinander, 6x
        frames = []
        for k in range(1, 5):
            im = Image.new('RGBA', (4*CW*6, CH*6), g.SKY_NIGHT)
            for r, d in enumerate(ORDER):
                im.alpha_composite(dirs[d][k].resize((CW*6, CH*6), Image.NEAREST), (r*CW*6, 0))
            frames.append(im.convert('RGB'))
        frames[0].save(os.path.join(OUT, f"{cfg['name']}.gif"), save_all=True, append_images=frames[1:], duration=150, loop=0)
        for k in range(4):
            for r, d in enumerate(ORDER):
                big = dirs[d][k+1].resize((CW*S, CH*S), Image.NEAREST)
                gif_frames[k].alpha_composite(big, (20 + ci*CW*S, 40 + r*CH*S))
        for r, d in enumerate(ORDER):
            static.alpha_composite(sheet.crop((0, r*CH, CW*5, (r+1)*CH)).resize((CW*5*2, CH*2), Image.NEAREST),
                                   (20 + ci*CW*S, 40 + r*CH*S + 20)) if False else None
    for f in gif_frames:
        ImageDraw.Draw(f).text((20, 10), 'Laufanimation: unten / links / rechts / oben', fill=(255, 240, 200), font=g.font(18))
    rgb = [f.convert('RGB') for f in gif_frames]
    rgb[0].save(os.path.join(g.BASE, 'preview_laufen.gif'), save_all=True, append_images=rgb[1:], duration=160, loop=0)
    # statische Übersicht aller Einzelbilder (Spritesheets 4x)
    sheets = [Image.open(os.path.join(OUT, f"{c['name']}_walk.png")) for c in g.CHARACTERS]
    S2 = 4; pad = 20
    ov = Image.new('RGBA', (4*(CW*5*S2 + pad) + pad, 2*(CH*4*S2 + 40) + 40), g.SKY_NIGHT)
    d = ImageDraw.Draw(ov)
    for i, (cfg, sh) in enumerate(zip(g.CHARACTERS, sheets)):
        x = pad + (i % 4)*(CW*5*S2 + pad); y = 40 + (i//4)*(CH*4*S2 + 40)
        d.text((x, y-4), cfg['title'], fill=(240, 230, 210), font=g.font(15))
        ov.alpha_composite(sh.resize((sh.width*S2, sh.height*S2), Image.NEAREST), (x, y+16))
    ov.save(os.path.join(g.BASE, 'preview_laufen_sheets.png'))

if __name__ == '__main__':
    main()
