"""Idle-Animationen (Atmen + Blinzeln) für alle Figuren.
Aufruf: python3 idle.py
Ausgabe: characters/idle/<name>_idle.png  (6 Spalten x 4 Zeilen à 18x26; Zeilen: unten, links, rechts, oben)
         preview_idle.gif
Empfohlenes Timing: 200 ms pro Bild (Bild 6 = Blinzeln, gern nur 120 ms).
"""
from PIL import Image, ImageDraw
import os
import generate as g, walk as w

OUT = os.path.join(g.BASE, 'characters', 'idle')
DY    = [0, 0, 1, 1, 0, 0]          # Atmen: Oberkörper sinkt 1px
BLINK = [False]*5 + [True]          # letztes Bild: Augen zu

def char_idle(cfg):
    down  = [w.frame_fb(cfg, False, 'stand', d, b) for d, b in zip(DY, BLINK)]
    up    = [w.frame_fb(cfg, True,  'stand', d) for d in DY]
    right = [w.frame_side(cfg, 'stand', 'mid', True, d, b) for d, b in zip(DY, BLINK)]
    left  = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in right]
    return {'unten': down, 'links': left, 'rechts': right, 'oben': up}

def main():
    os.makedirs(OUT, exist_ok=True)
    CW, CH, S = w.CW, w.CH, 5
    allc = []
    for cfg in g.CHARACTERS:
        dirs = char_idle(cfg)
        sh = Image.new('RGBA', (CW*6, CH*4), (0, 0, 0, 0))
        for r, d in enumerate(w.ORDER):
            for c, f in enumerate(dirs[d]): sh.alpha_composite(f, (c*CW, r*CH))
        sh.save(os.path.join(OUT, f"{cfg['name']}_idle.png"))
        allc.append(dirs)
    # Vorschau-GIF: Zeile 1 = vorne, Zeile 2 = Seite
    n = len(g.CHARACTERS)
    Wd, Hd = 20 + n*CW*S, 50 + 2*CH*S
    frames = []
    for k in range(6):
        im = Image.new('RGBA', (Wd, Hd), g.SKY_NIGHT); d = ImageDraw.Draw(im)
        d.text((20, 12), 'Idle: Atmen + Blinzeln', fill=(255, 240, 200), font=g.font(18))
        for i, dirs in enumerate(allc):
            im.alpha_composite(dirs['unten'][k].resize((CW*S, CH*S), Image.NEAREST), (20 + i*CW*S, 40))
            im.alpha_composite(dirs['rechts'][k].resize((CW*S, CH*S), Image.NEAREST), (20 + i*CW*S, 40 + CH*S))
        frames.append(im.convert('RGB'))
    dur = [200, 200, 200, 200, 200, 130]
    frames[0].save(os.path.join(g.BASE, 'preview_idle.gif'), save_all=True, append_images=frames[1:], duration=dur, loop=0)

if __name__ == '__main__':
    main()
