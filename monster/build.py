"""Rendert alle 600 Monster aus dem Bestiarium.
Aufruf: python3 build.py [--nur RANG]
Ausgabe: monster/sprites/<rang>/<name>.png  (Spritesheet: Zeilen idle 4, move 6, attack 6, hurt 3, death 6; Blick nach rechts)
         monster/sprites/monster.json        (Bildgröße, Bodenpunkt, Bilder je Animation, Rang, Typ)
         monster/preview_rang_<rang>.png / .gif
"""
import os, sys, json, re, unicodedata
from multiprocessing import Pool
from PIL import Image, ImageDraw
from classify import all_specs
from render import render_all, sheet
from engine import ANIMS
FONT = None
def font():
    from PIL import ImageFont
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
    except Exception: return ImageFont.load_default()

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'sprites')

def slug(name):
    s = name.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')

def job(args):
    entry, spec = args
    fr, origin = render_all(spec)
    sh = sheet(fr)
    d = os.path.join(OUT, entry['rang']); os.makedirs(d, exist_ok=True)
    fn = slug(entry['name']) + '.png'
    sh.save(os.path.join(d, fn))
    w, h = fr['idle'][0].size
    return entry['name'], dict(datei=f"{entry['rang']}/{fn}", rang=entry['rang'], typ=spec['typ'], bild=[w, h],
                               bodenpunkt=list(origin), animationen={a: n for a, n in ANIMS},
                               lebensraum=entry['lebensraum'], merkmal=entry['merkmal'], schwaeche=entry['schwaeche'])

def previews(rank, items):
    """items: [(name, meta)] -> Kontaktbogen (Idle) + GIF (Laufen)"""
    cells = []
    for name, meta in items:
        sh = Image.open(os.path.join(OUT, meta['datei']))
        w, h = meta['bild']
        cells.append((name, [sh.crop((i*w, 0, (i+1)*w, h)) for i in range(4)], [sh.crop((i*w, h, (i+1)*w, 2*h)) for i in range(6)]))
    S = {'D': 3, 'C': 3, 'B': 2, 'A': 2, 'S': 2, 'SS': 1}[rank]
    cw = max(c[1][0].width for c in cells) * S + 12
    ch = max(c[1][0].height for c in cells) * S + 22
    cols = max(1, min(10, 1900 // cw))
    rows = (len(cells) + cols - 1) // cols
    def page(frame_of):
        im = Image.new('RGB', (cols * cw, rows * ch), (42, 36, 69)); d = ImageDraw.Draw(im)
        for i, (name, idle, move) in enumerate(cells):
            x, y = (i % cols) * cw, (i // cols) * ch
            f = frame_of(idle, move)
            im.paste(f.resize((f.width*S, f.height*S), Image.NEAREST), (x + 6, y + ch - 4 - f.height*S), f.resize((f.width*S, f.height*S), Image.NEAREST))
            d.text((x + 4, y + 2), name[:26], fill=(235, 225, 205), font=font())
        return im
    page(lambda i, m: i[0]).save(os.path.join(HERE, f'preview_rang_{rank}.png'))
    frames = [page(lambda i, m, k=k: m[k]) for k in range(6)]
    frames[0].save(os.path.join(HERE, f'preview_rang_{rank}.gif'), save_all=True, append_images=frames[1:], duration=140, loop=0)

def main():
    only = sys.argv[sys.argv.index('--nur') + 1] if '--nur' in sys.argv else None
    specs, missing = all_specs()
    assert not missing, missing
    todo = [(e, s) for e, s in specs if not only or e['rang'] == only]
    with Pool(4) as pool:
        res = pool.map(job, todo, chunksize=4)
    meta_path = os.path.join(OUT, 'monster.json')
    meta = json.load(open(meta_path, encoding='utf-8')) if os.path.exists(meta_path) else {}
    meta.update(dict(res))
    json.dump(meta, open(meta_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for rank in ('D', 'C', 'B', 'A', 'S', 'SS'):
        items = [(n, m) for n, m in res if m['rang'] == rank]
        if items: previews(rank, items)
    print(len(res), 'Monster gerendert')

if __name__ == '__main__':
    main()
