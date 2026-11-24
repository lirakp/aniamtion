"""Händler-Läden und Meisterschmieden im Cosy-Stil.
Aufruf: python3 shops.py  -> buildings/<name>_tag.png / _nacht.png + preview_laeden_*.png
"""
import os
from PIL import Image, ImageDraw
import generate as g
from generate import (C, shade, mix, Canvas, WOOD, WOOD_D, WOOD_L, DOORWOOD, STONE, GOLD, CREAM, RED,
                      GLOW, GLOW_L, GLASS, GLASS_L, BRICK, LEAF, LEAF_D)

g.ROOFS['lila'] = (C('#5e4a7a'), C('#443660'), C('#7a64a0'))
g.ROOFS['nacht'] = (C('#3a3e7a'), C('#2a2c5c'), C('#5a60a8'))

DARK = C('#3a3446')
STEEL, STEEL_L, STEEL_D = C('#b8bccc'), C('#e8ecf4'), C('#6a6e80')
FIRE, FIRE_L = C('#ff9a3c'), C('#ffd27a')

# ---------------------------------------------------------------- Symbole 9x9
ICONS = {
    'trank': (['...ccc...', '....g....', '....g....', '...gpg...', '..gpppg..', '.gpPpppg.', '.gPppppg.', '.gppppPg.', '..ggggg..'],
              {'c': WOOD, 'g': C('#cfe6f0'), 'p': C('#5ac85a'), 'P': C('#b8f0a8')}),
    'fackel': (['....f....', '...fff...', '..fFFFf..', '..fFyFf..', '...fff...', '...www...', '....w....', '....w....', '....w....'],
               {'f': C('#e8603a'), 'F': C('#ffb040'), 'y': C('#fff0b8'), 'w': WOOD_D}),
    'kugel': (['...ooo...', '..oLooo..', '.oLooSoo.', '.ooooooo.', '.oooooSo.', '..ooooo..', '...ooo...', '..GGGGG..', '.GGGGGGG.'],
              {'o': C('#7a5ad0'), 'L': C('#f0e8ff'), 'S': C('#c0a8ff'), 'G': GOLD}),
    'schild': (['.sssssss.', '.sbbbbbs.', '.sbbbbbs.', '.sbbGbbs.', '.sbGGGbs.', '.sbbGbbs.', '..sbbbs..', '...sbs...', '....s....'],
               {'s': STEEL, 'b': RED, 'G': GOLD}),
    'helm': (['...sss...', '..sSsss..', '.sSsssss.', '.sSsssss.', '.sSdddds.', '.sSsdsss.', '.sSsdsss.', '.ss...ss.', '.s.....s.'],
             {'s': STEEL, 'S': STEEL_L, 'd': DARK}),
    'schwert': (['........s', '.......Ls', '......Ls.', '.....Ls..', '..g.Ls...', '...gs....', '...wg....', '..w..g...', '.G.......'],
                {'s': STEEL, 'L': STEEL_L, 'g': GOLD, 'w': WOOD_D, 'G': GOLD}),
}

def icon(cv, x, y, name):
    rows, pal = ICONS[name]
    for dy, row in enumerate(rows):
        assert len(row) == 9, (name, row)
        for dx, ch in enumerate(row):
            if ch in pal: cv.set(x+dx, y+dy, pal[ch])

def board(cv, x0, y0, name, col=WOOD):
    cv.rect(x0, y0, x0+10, y0+10, col)
    cv.rect(x0, y0, x0+10, y0, mix(col, (255,)*4, .2))
    cv.rect(x0, y0+10, x0+10, y0+10, shade(col, .7)); cv.rect(x0+10, y0, x0+10, y0+10, shade(col, .7))
    icon(cv, x0+1, y0+1, name)

def hanging_sign(cv, x0, y, name, col=WOOD):
    cv.rect(x0-1, y, x0+11, y, WOOD_D)
    cv.set(x0+1, y+1, DARK); cv.set(x0+9, y+1, DARK)
    board(cv, x0, y+2, name, col)

# ---------------------------------------------------------------- Bauteile
def win(cv, x, y, w, h, night, lit=(GLOW, GLOW_L), box=False, mullion=True, content=None):
    cv.rect(x, y, x+w-1, y+h-1, WOOD_D)
    for yy in range(y+1, y+h-1):
        for xx in range(x+1, x+w-1):
            if night: c = lit[1] if (xx-x)+(yy-y) < (w+h)//3 else lit[0]
            else:
                c = mix(GLASS_L, GLASS, (yy-y)/h)
                if (xx-x)-(yy-y) in (1, 2) and yy < y+h//2: c = GLASS_L
            cv.set(xx, yy, c)
    if content: content()
    if mullion:
        cv.rect(x+w//2, y, x+w//2, y+h-1, WOOD_D); cv.rect(x, y+h//2, x+w-1, y+h//2, WOOD_D)
    cv.rect(x-1, y+h, x+w, y+h, WOOD_L)
    if box:
        cv.rect(x, y+h+1, x+w-1, y+h+3, WOOD)
        for xx in range(x, x+w):
            cv.set(xx, y+h, LEAF if xx % 2 else LEAF_D)
            if xx % 3 == 1: cv.set(xx, y+h-1, [RED, C('#e888a8'), GOLD][(xx//3) % 3])

def arch_win(cv, x0, y0, w, h, night, lit):
    for y in range(y0, y0+h):
        cut = 2 if y == y0 else 1 if y == y0+1 else 0
        for x in range(x0+cut, x0+w-cut):
            border = x in (x0+cut, x0+w-1-cut) or y in (y0, y0+h-1) or (y == y0+1 and cut)
            if border: c = WOOD_D
            elif x == x0+w//2 or y == y0+h//2: c = WOOD_D
            elif night: c = lit[1] if (x-x0)+(y-y0) < (w+h)//3 else lit[0]
            else: c = mix(GLASS_L, GLASS, (y-y0)/h)
            cv.set(x, y, c)
    cv.rect(x0-1, y0+h, x0+w, y0+h, WOOD_L)

def awning(cv, x0, x1, y0, c1, c2):
    for x in range(x0, x1+1):
        col = c1 if (x//3) % 2 else c2
        cv.rect(x, y0, x, y0+4, col)
        if x % 2: cv.set(x, y0+5, col)
    cv.rect(x0, y0, x1, y0, shade(c1, .75))

def wall_torch(cv, x, y):
    cv.rect(x, y+1, x, y+4, WOOD_D); cv.set(x-1, y+1, DARK); cv.set(x+1, y+1, DARK)
    cv.set(x, y, FIRE); cv.set(x, y-1, FIRE_L)

def barrel(cv, x, y):
    for yy in range(9):
        half = 3 if 2 <= yy <= 6 else 2
        for xx in range(3-half, 4+half):
            cv.set(x+xx, y+yy, WOOD_D if xx == 3+half or xx % 2 == 0 else WOOD)
    for yy in (1, 7): cv.rect(x, y+yy, x+6, y+yy, C('#5a5a6a'))
    cv.rect(x+1, y, x+5, y, WOOD_L)

def crate(cv, x, y, w=8, h=7):
    cv.rect(x, y, x+w-1, y+h-1, WOOD_L); cv.rect(x, y, x+w-1, y, WOOD)
    cv.rect(x, y+h-1, x+w-1, y+h-1, WOOD_D); cv.rect(x+w-1, y, x+w-1, y+h-1, WOOD_D)
    ImageDraw.Draw(cv.img).line([(x+1, y+h-2), (x+w-2, y+1)], fill=WOOD)

def rope(cv, x, y):
    rc, rd = C('#c8a870'), C('#8a6a40')
    for yy in range(5):
        for xx in range(9):
            if ((xx-4)/4.5)**2 + ((yy-2)/2.5)**2 <= 1:
                cv.set(x+xx, y+yy, rd if (xx + yy) % 3 == 0 else rc)
    cv.rect(x+3, y+2, x+5, y+2, rd)

def pickaxe(cv, x, y):
    ImageDraw.Draw(cv.img).line([(x, y+13), (x+5, y+1)], fill=WOOD)
    for (dx, dy) in ((1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 1), (8, 2), (0, 2)):
        cv.set(x+dx, y+dy, STEEL)
    cv.set(x+5, y+1, STEEL_D)

ARMOR = ['...sss...', '..sSssd..', '..sddds..', '...sss...', '....w....', 'sS.sss.ss', 'sSsssssds', '.sSssssd.',
         '.sSssssd.', '..sssss..', '..GGGGG..', '..sSssd..', '....w....', '....w....', '....w....', '....w....',
         '....w....', '....w....', '..wwwww..']
def armor_stand(cv, x, y, metal=STEEL, belt=WOOD):
    pal = {'s': metal, 'S': mix(metal, (255,)*4, .5), 'd': shade(metal, .6), 'w': WOOD_D, 'G': belt}
    for dy, row in enumerate(ARMOR):
        for dx, ch in enumerate(row):
            if ch in pal: cv.set(x+dx, y+dy, pal[ch])

def sword_up(cv, x, y, blade=11):
    cv.rect(x, y, x, y+blade-1, STEEL); cv.set(x, y, STEEL_L)
    cv.rect(x-1, y+blade, x+1, y+blade, GOLD)
    cv.rect(x, y+blade+1, x, y+blade+3, WOOD_D); cv.set(x, y+blade+4, GOLD)

def weapon_rack(cv, x, y, h=20):
    cv.rect(x, y+4, x, y+h-1, WOOD_D); cv.rect(x+9, y+4, x+9, y+h-1, WOOD_D)
    sword_up(cv, x+2, y+1); sword_up(cv, x+4, y+2, 10)
    cv.rect(x+7, y+1, x+7, y+h-3, WOOD)                         # Axt
    cv.rect(x+8, y+1, x+8, y+5, STEEL); cv.rect(x+6, y+2, x+6, y+4, STEEL_D)
    cv.rect(x, y+6, x+9, y+6, WOOD); cv.rect(x, y+h-3, x+9, y+h-3, WOOD)

ANVIL = ['LLLLLLLL.', '.dsssssd.', '...sss...', '...sss...', '..sssss..', '.ddddddd.']
def anvil(cv, x, y, hot=False):
    pal = {'L': C('#8a8ea0'), 's': C('#5a5e6e'), 'd': C('#3e4050')}
    for dy, row in enumerate(ANVIL):
        for dx, ch in enumerate(row):
            if ch in pal: cv.set(x+dx, y+dy, pal[ch])
    if hot: cv.rect(x+2, y-1, x+6, y-1, FIRE); cv.set(x+6, y-1, FIRE_L)

def forge_hearth(cv, x0, y0, x1, y1):
    cv.stones(x0, y0, x1, y1, C('#5a5464'), rh=2)
    for x in range(x0+1, x1):
        cv.set(x, y0-1, FIRE if x % 2 else FIRE_L)
        if x % 3: cv.set(x, y0-2, C('#e8603a'))

def grindstone(cv, x, y):
    d = ImageDraw.Draw(cv.img)
    d.line([(x+1, y+14), (x+6, y+5)], fill=WOOD_D); d.line([(x+11, y+14), (x+6, y+5)], fill=WOOD_D)
    cv.rect(x+1, y+10, x+11, y+13, WOOD); cv.rect(x+2, y+11, x+10, y+11, C('#5a7aa0'))
    for yy in range(11):
        for xx in range(13):
            r = ((xx-6)**2 + (yy-5)**2) ** .5
            if r <= 5.2: cv.set(x+xx, y+yy, shade(STONE, .75) if r > 4.2 else mix(STONE, (255,)*4, .15) if xx < 6 and yy < 5 else STONE)
    cv.set(x+6, y+5, WOOD_D); cv.rect(x+6, y+5, x+10, y+5, WOOD_D); cv.rect(x+10, y+5, x+10, y+8, WOOD_D)

def smoke(cv, puffs, col):
    if g.ANIMATING: return
    for (cx, cy, r) in puffs:
        for y in range(int(cy-r)-1, int(cy+r)+2):
            for x in range(int(cx-r)-1, int(cx+r)+2):
                if (x-cx)**2 + (y-cy)**2 <= r*r:
                    cv.set(x, y, mix(col, (255,)*4, .35) if x < cx and y < cy else col)

def open_workshop(cv, x0, y0, x1, y1):
    cv.rect(x0-1, y0-1, x1+1, y1, WOOD_D)
    cv.rect(x0, y0, x1, y1, C('#241a22'))
    cv.rect(x0, y0, x1, y0+1, C('#1a1218'))

# ================================================================ Gebäude
GREEN_LIT = (C('#8ee08a'), C('#d8f8c8'))
MAGIC_LIT = (C('#a88af0'), C('#e0d4ff'))

def alchemie(night):
    cv = Canvas(70, 96, 41)
    g.chimney(cv, 44, 12, 50, 34)
    smoke(cv, [(47, 8, 2.2), (51, 4.5, 2.6), (55, 1.8, 1.6)], C('#a8d8a0'))
    cv.planks(7, 38, 60, 59, C('#6a5a7a'), pw=3)
    cv.roof(3, 64, 14, 40, 20, 'lila')
    cv.rect(8, 41, 59, 42, shade(C('#6a5a7a'), .7))
    cv.rect(6, 59, 61, 60, WOOD_D)
    cv.plaster(10, 61, 57, 91, C('#cfd4c0'))
    cv.stones(9, 90, 58, 95)
    win(cv, 16, 45, 10, 9, night, GREEN_LIT, box=True); win(cv, 42, 45, 10, 9, night, GREEN_LIT, box=True)
    def potions():
        cols = [C('#5ac85a'), C('#9a6ad8'), C('#d85a5a'), C('#5a9ad8'), GOLD]
        for sy in (73, 81):
            cv.rect(15, sy, 34, sy, WOOD)
            for i, bx in enumerate(range(16, 33, 3)):
                c = cols[(i + sy) % 5]
                cv.set(bx, sy-3, C('#cfe6f0')); cv.rect(bx, sy-2, bx+1, sy-1, c); cv.set(bx, sy-2, mix(c, (255,)*4, .5))
    win(cv, 14, 66, 22, 18, night, GREEN_LIT, mullion=False, content=potions)
    cv.door(42, 69, 9, 21, col=C('#3e5a48'))
    hanging_sign(cv, 58, 63, 'trank', C('#4e3a5e'))
    if night: cv.glow([(16, 45, 10, 9), (42, 45, 10, 9), (14, 66, 22, 18)], GREEN_LIT[0])
    return cv.done()

def dungeon(night):
    cv = Canvas(92, 78, 43)
    cv.stones(10, 36, 81, 73, C('#7a7488'))
    cv.roof(4, 87, 14, 38, 10, 'braun')
    cv.rect(11, 39, 80, 40, shade(C('#7a7488'), .6))
    awning(cv, 13, 42, 44, C('#3e6a50'), CREAM)
    def gear():
        rope(cv, 17, 59)
        cv.rect(28, 53, 30, 53, DARK); cv.rect(27, 54, 31, 58, DARK); cv.rect(28, 55, 30, 57, GLOW_L if night else C('#c8c0a0'))
        pickaxe(cv, 32, 52)
    win(cv, 15, 51, 26, 16, night, mullion=False, content=gear)
    board(cv, 51, 41, 'fackel')
    cv.door(52, 54, 9, 20)
    wall_torch(cv, 47, 56); wall_torch(cv, 65, 56)
    cv.stones(9, 73, 82, 77)
    barrel(cv, 83, 66); barrel(cv, 83, 57)
    pickaxe(cv, 72, 60)
    crate(cv, 1, 68); rope(cv, 0, 63)
    if night: cv.glow([(47, 55, 1, 2), (65, 55, 1, 2), (15, 51, 26, 16)])
    return cv.done()

def magie(night):
    cv = Canvas(78, 106, 47)
    base = C('#cfc6e4')
    for x in range(18, 60):
        t = (x-18)/41
        c = mix(base, (255,)*4, .2) if t < .15 else base if t < .7 else shade(base, .88) if t < .88 else shade(base, .74)
        for y in range(40, 99):
            cv.set(x, y, shade(c, .94) if cv.rng.random() < .05 else c)
    cv.stones(16, 97, 61, 103, C('#8a86a8'))
    cv.roof(12, 65, 8, 44, 26, 'nacht')
    for (x, y) in ((32, 30), (44, 22), (25, 38), (50, 36), (38, 16), (40, 40)): cv.set(x, y, GOLD)
    cv.rect(38, 5, 38, 9, GOLD)                                # Mondsichel
    for (x, y) in ((37, 0), (38, 0), (36, 1), (37, 1), (36, 2), (37, 2), (36, 3), (37, 3), (37, 4), (38, 4)):
        cv.set(x, y, GOLD)
    cv.set(36, 2, C('#fff0b8'))
    arch_win(cv, 34, 50, 9, 13, night, MAGIC_LIT)
    def orb(): icon(cv, 24, 73, 'kugel')
    win(cv, 22, 71, 14, 13, night, MAGIC_LIT, mullion=False, content=orb)
    cv.door(45, 78, 10, 20, col=C('#5a3a7a'))
    cv.rect(44, 76, 55, 76, GOLD)
    hanging_sign(cv, 5, 54, 'kugel', C('#3a3e7a'))
    cv.rect(16, 54, 17, 54, WOOD_D)
    sp = C('#e0f0ff')
    for (x, y) in ((6, 22), (70, 30), (67, 14), (9, 42), (72, 52), (64, 66)):
        cv.set(x, y, sp)
        if (x + y) % 2: cv.set(x-1, y, MAGIC_LIT[0]); cv.set(x+1, y, MAGIC_LIT[0]); cv.set(x, y-1, MAGIC_LIT[0]); cv.set(x, y+1, MAGIC_LIT[0])
    if night: cv.glow([(34, 50, 9, 13), (22, 71, 14, 13)], MAGIC_LIT[0])
    return cv.done()

def ruestung_waffen(night):
    cv = Canvas(98, 78, 53)
    cv.plaster(14, 30, 75, 51, C('#ead9bc'))
    for y in (30, 31, 50, 51): cv.rect(14, y, 75, y, WOOD_D)
    for x in (14, 15, 44, 45, 74, 75): cv.rect(x, 30, x, 51, WOOD_D)
    cv.stones(14, 52, 75, 75)
    cv.roof(8, 81, 10, 32, 12, 'rot')
    cv.rect(16, 33, 73, 34, shade(C('#ead9bc'), .8))
    win(cv, 22, 37, 11, 9, night, box=True); win(cv, 56, 37, 11, 9, night, box=True)
    awning(cv, 17, 46, 54, RED, C('#8a8a9a'))
    def wares(): icon(cv, 21, 62, 'helm'); icon(cv, 33, 62, 'schild')
    win(cv, 19, 61, 26, 11, night, mullion=False, content=wares)
    cv.door(55, 56, 9, 20)
    hanging_sign(cv, 77, 34, 'schild')
    armor_stand(cv, 78, 57)
    weapon_rack(cv, 88, 56)
    barrel(cv, 3, 66)
    for sx in (4, 6, 8):
        cv.rect(sx, 53 + (sx % 4), sx, 65, WOOD); cv.set(sx, 52 + (sx % 4), STEEL); cv.set(sx, 51 + (sx % 4), STEEL_L)
    cv.stones(13, 75, 76, 77)
    if night: cv.glow([(22, 37, 11, 9), (56, 37, 11, 9), (19, 61, 26, 11)])
    return cv.done()

def ruestungsschmiede(night):
    cv = Canvas(106, 88, 59)
    g.chimney(cv, 62, 2, 73, 26, STONE)
    smoke(cv, [(66, 0, 1.5), (70, -1, 1.8)], C('#8a8296'))
    for x in range(63, 73):
        if x % 2: cv.set(x, 3, FIRE)
    cv.stones(8, 36, 83, 85)
    cv.roof(2, 89, 14, 38, 12, 'schiefer')
    cv.rect(9, 39, 82, 40, shade(STONE, .6))
    board(cv, 24, 41, 'helm', C('#4a5068'))
    open_workshop(cv, 13, 54, 45, 85)
    forge_hearth(cv, 15, 74, 24, 85)
    anvil(cv, 25, 80, hot=True)
    armor_stand(cv, 35, 63, C('#c8d0e0'), GOLD)
    win(cv, 52, 48, 12, 10, night)
    cv.door(68, 64, 9, 22)
    cv.rect(67, 62, 77, 62, C('#4a5068'))
    armor_stand(cv, 87, 67, C('#c8d0e0'), GOLD)
    for yy in range(76, 86):                                 # Löschfass
        cv.rect(97, yy, 104, yy, WOOD_D if yy in (78, 84) else WOOD)
    cv.rect(98, 76, 103, 76, C('#5a8ac0')); cv.set(99, 76, C('#a8d0f0'))
    cv.stones(7, 85, 84, 87)
    cv.glow([(15, 72, 10, 3), (27, 78, 5, 2)] + ([(52, 48, 12, 10)] if night else []), FIRE)
    return cv.done()

def waffenschmiede(night):
    cv = Canvas(106, 88, 61)
    g.chimney(cv, 22, 2, 31, 26)
    smoke(cv, [(25, 0, 1.6), (29, -1, 1.8)], C('#8a8296'))
    for x in range(23, 31):
        if x % 2: cv.set(x, 3, FIRE)
    cv.planks(8, 36, 83, 59, C('#6a4632'), pw=3, vertical=False)
    cv.stones(8, 60, 83, 85)
    cv.rect(8, 59, 83, 60, WOOD_D)
    cv.roof(2, 89, 14, 38, 12, 'dunkel')
    cv.rect(9, 39, 82, 40, shade(C('#6a4632'), .6))
    board(cv, 62, 42, 'schwert', C('#5a3a2a'))
    open_workshop(cv, 48, 63, 80, 85)
    weapon_rack(cv, 50, 64)
    forge_hearth(cv, 69, 76, 78, 85)
    anvil(cv, 59, 80, hot=True)
    win(cv, 16, 44, 12, 10, night); win(cv, 34, 44, 10, 10, night)
    win(cv, 14, 66, 12, 10, night)
    cv.door(32, 64, 9, 22)
    grindstone(cv, 0, 72)
    weapon_rack(cv, 88, 66)
    barrel(cv, 99, 77)
    for sx in (100, 102, 104):
        cv.rect(sx, 67 + sx % 3, sx, 76, STEEL); cv.set(sx, 66 + sx % 3, STEEL_L); cv.set(sx, 76, GOLD)
    cv.stones(7, 85, 84, 87)
    cv.glow([(69, 74, 10, 3), (61, 78, 5, 2)] + ([(16, 44, 12, 10), (34, 44, 10, 10), (14, 66, 12, 10)] if night else []), FIRE)
    return cv.done()

SHOPS = [('laden_alchemie', 'Alchemist', alchemie),
         ('laden_dungeon', 'Dungeon-Ausrüstung', dungeon),
         ('laden_magie', 'Magische Gegenstände', magie),
         ('laden_ruestung_waffen', 'Rüstung & Waffen', ruestung_waffen),
         ('schmiede_ruestung', 'Rüstungsschmiede', ruestungsschmiede),
         ('schmiede_waffen', 'Waffenschmiede', waffenschmiede)]

def main():
    os.makedirs(os.path.join(g.BASE, 'buildings'), exist_ok=True)
    for night, tag in ((False, 'tag'), (True, 'nacht')):
        items = []
        for name, title, fn in SHOPS:
            im = fn(night); im.save(os.path.join(g.BASE, 'buildings', f'{name}_{tag}.png')); items.append((title, im))
        g.sheet(items, 4, night, f"Cosy - Läden & Meisterschmieden ({'Nacht' if night else 'Tag'})", 3).save(
            os.path.join(g.BASE, f'preview_laeden_{tag}.png'))

if __name__ == '__main__':
    main()
