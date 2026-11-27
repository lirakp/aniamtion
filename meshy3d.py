"""3D-Modelle über die Meshy-API (Text → 3D, Voxel-Stil) mit dem Pixel-Sprite als Textur-Vorlage.
Aufruf: python3 meshy3d.py [name ...]        (ohne Namen: alle in OBJEKTE)
Der API-Schlüssel wird vom Netzwerk-Proxy der Umgebung eingesetzt; lokal ggf. MESHY_API_KEY setzen.
Ausgabe: modelle_3d/<name>/<name>.glb (+ .fbx, .obj, .usdz wenn verfügbar), vorschau.png, info.json
Ablauf je Objekt: preview (Form) → refine (Textur) → Download. Jede Stufe kostet Meshy-Credits.
"""
import os, sys, json, time, base64, io, urllib.request, urllib.error
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'modelle_3d')
API = 'https://api.meshy.ai/openapi/v2/text-to-3d'
KEY = os.environ.get('MESHY_API_KEY', 'proxy-injected')
STIL = ('voxel art style, built from small cubes like 3D pixel art, cozy fantasy village, soft warm colors, '
        'chunky blocky shapes, single object, centered, no ground plane')

def sprite(path, box=None, scale=16):
    im = Image.open(os.path.join(BASE, path)).convert('RGBA')
    if box: im = im.crop(box)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    buf = io.BytesIO(); bg.convert('RGB').save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

OBJEKTE = {
    'brunnen': dict(prompt='a small round village stone well with a red wooden roof, a wooden crank and a bucket, grey stones',
                    sprite=('buildings/brunnen_tag.png', None)),
    'laterne': dict(prompt='a wooden street lantern post with a glowing warm yellow lantern on top, dark iron frame',
                    sprite=('props/laterne_tag.png', None)),
    'truhe': dict(prompt='a fantasy dungeon treasure chest, wooden with gold metal bands and a lock, closed lid',
                  sprite=('dungeon/truhen/gold_zu.png', None)),
    'portal': dict(prompt='a standing magic portal, tall vertical oval ring of glowing violet light with a swirling purple vortex inside, stone base',
                   sprite=('objects/portal/portal_violett.png', (0, 72, 56, 144))),
    'heiltrank': dict(prompt='a round glass potion bottle filled with glowing red healing liquid, cork stopper',
                      sprite=('icons/traenke.png', (16, 0, 32, 16))),
}

def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f'Meshy-Fehler {e.code}: {e.read().decode()[:400]}')

def warte(task_id, name, stufe):
    while True:
        t = call('GET', f'{API}/{task_id}'); st = t.get('status')
        print(f'  {name} {stufe}: {st} {t.get("progress", "")}%', flush=True)
        if st == 'SUCCEEDED': return t
        if st in ('FAILED', 'CANCELED', 'EXPIRED'): raise SystemExit(f'{name} {stufe} fehlgeschlagen: {t.get("task_error")}')
        time.sleep(10)

def lade(url, path):
    with urllib.request.urlopen(url, timeout=120) as r, open(path, 'wb') as f: f.write(r.read())

def erzeuge(name):
    o = OBJEKTE[name]; d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
    pid = call('POST', API, {'mode': 'preview', 'prompt': f"{o['prompt']}, {STIL}", 'art_style': 'realistic',
                             'should_remesh': True, 'topology': 'quad', 'target_polycount': 8000})['result']
    warte(pid, name, 'Form')
    path, box = o['sprite']
    body = {'mode': 'refine', 'preview_task_id': pid, 'enable_pbr': False,
            'texture_prompt': f"{o['prompt']}, voxel pixel art colors", 'texture_image_url': sprite(path, box)}
    rid = call('POST', API, body)['result']
    t = warte(rid, name, 'Textur')
    for fmt, url in (t.get('model_urls') or {}).items():
        if url: lade(url, os.path.join(d, f'{name}.{fmt}'))
    if t.get('thumbnail_url'): lade(t['thumbnail_url'], os.path.join(d, 'vorschau.png'))
    json.dump({'name': name, 'prompt': o['prompt'], 'stil': STIL, 'preview_task': pid, 'refine_task': rid,
               'formate': [k for k, v in (t.get('model_urls') or {}).items() if v]},
              open(os.path.join(d, 'info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{name}: fertig', flush=True)

if __name__ == '__main__':
    names = sys.argv[1:] or list(OBJEKTE)
    for n in names: erzeuge(n)
