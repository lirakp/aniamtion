"""Tür-Animationen (Öffnen / Schließen) für alle Gebäude mit Türen.
Aufruf: python3 doors.py
Ausgabe in buildings/doors/:
  <name>_<tag>_tuer_auf.png   5 Bilder: zu -> offen   (ganzes Gebäude)
  <name>_<tag>_tuer_zu.png    5 Bilder: offen -> zu
  <name>_<tag>_tuer_overlay.png  nur der Türbereich (5 Bilder, zu -> offen) zum Drüberlegen,
                                 z.B. auf die animierten Gebäude (Rauch etc.)
  tueren.json                 Position des Overlays je Gebäude
Empfohlen: 70-90 ms pro Bild.
"""
import os, json
from PIL import Image
import generate as g, shops as sh

OUT = os.path.join(g.BASE, 'buildings', 'doors')
STEPS = 5

def render(fn, night, k):
    g.DOOR_OPEN, g.CUR_NIGHT = k, night
    try: return fn(night)
    finally: g.DOOR_OPEN, g.CUR_NIGHT = 0, False

def main():
    os.makedirs(OUT, exist_ok=True)
    meta, prev = {}, {False: [[] for _ in range(STEPS)], True: [[] for _ in range(STEPS)]}
    for name, title, fn in g.BUILDINGS + sh.SHOPS:
        g.DOOR_LOG = []; fn(False); doors = g.DOOR_LOG; g.DOOR_LOG = None
        if not doors: continue
        x0 = min(d[0] for d in doors) - 1; y0 = min(d[1] for d in doors) - 2
        x1 = max(d[0]+d[2] for d in doors) + 1; y1 = max(d[1]+d[3] for d in doors) + 1
        meta[name] = {'x': x0, 'y': y0, 'w': x1-x0, 'h': y1-y0, 'bilder': STEPS,
                      'hinweis': 'Overlay-Position im statischen Gebäude; im animierten Gebäude y + 16'}
        for night, tag in ((False, 'tag'), (True, 'nacht')):
            fr = [render(fn, night, k) for k in range(STEPS)]
            w, h = fr[0].size
            for order, suffix in ((fr, 'auf'), (fr[::-1], 'zu')):
                s = Image.new('RGBA', (w*STEPS, h), (0, 0, 0, 0))
                for i, f in enumerate(order): s.alpha_composite(f, (i*w, 0))
                s.save(os.path.join(OUT, f'{name}_{tag}_tuer_{suffix}.png'))
            ow, oh = x1-x0, y1-y0
            ov = Image.new('RGBA', (ow*STEPS, oh), (0, 0, 0, 0))
            for i, f in enumerate(fr): ov.alpha_composite(f.crop((x0, y0, x1, y1)), (i*ow, 0))
            ov.save(os.path.join(OUT, f'{name}_{tag}_tuer_overlay.png'))
            for k in range(STEPS): prev[night][k].append((title, fr[k]))
    with open(os.path.join(OUT, 'tueren.json'), 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    seq = [0, 0, 0, 1, 2, 3, 4, 4, 4, 4, 3, 2, 1]
    dur = [500, 300, 300, 90, 90, 90, 500, 300, 300, 90, 90, 90, 90]
    for night, tag in ((False, 'tag'), (True, 'nacht')):
        imgs = [g.sheet(prev[night][k], 3, night, f"Cosy - Türen auf/zu ({'Nacht' if night else 'Tag'})", 5).convert('RGB') for k in range(STEPS)]
        frames = [imgs[k] for k in seq]
        frames[0].save(os.path.join(g.BASE, f'preview_tueren_{tag}.gif'), save_all=True, append_images=frames[1:], duration=dur, loop=0)
    print(len(meta), 'Gebäude mit Türen:', ', '.join(meta))

if __name__ == '__main__':
    main()
