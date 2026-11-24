"""Ordnet jedem Monster aus dem Bestiarium Körpertyp, Farben, Größe und Details zu.
Reihenfolge: Sonderfälle (OVERRIDES) -> Schlüsselwort-Regeln -> Element/Farbe aus Name, Merkmal, Lebensraum."""
import re, json, random, os
from engine import C, shade, mix, light

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- Elemente
ELEM_RULES = [
    ('feuer', r'glut|feuer|flamm|lava|asche|brenn|vulkan|höllen|funkenkäfer|ruß|glimm|phönix|kerze|brand|speit funken'),
    ('eis', r'frost|eis|schnee|gletscher|reif|lawine|winter|kalt|weißer bär|weißer wolf|yeti|nachtfrost'),
    ('blitz', r'blitz|donner|gewitter|sturm(?!ziege)|funken|strom|elektro|leuchtaal'),
    ('gift', r'gift|säure|fieber|seuche|sporen|pilz|stink|faul|schimmel|mücke|ätzend'),
    ('schatten', r'schatten|nacht|dämmer|zwielicht|albtraum|seelen|dunkel|tiefen|schwarzes moor|rote nacht'),
    ('blut', r'blut'),
    ('wasser', r'wasser|see(?!le)|meer|fjord|riff|tang|welle|ozean|flut|fluss|pfütz|tiefsee|ertrunk'),
    ('arkan', r'erinnerung|spiegel|zeit|mana|phasen|grimoire|bruchklang|echo|stau|trugbild|fata|schriftrolle|zauber'),
    ('nebel', r'nebel|geist(?!er)|gespenst|klage|weiße nichts|irr'),
    ('kristall', r'kristall'),
    ('natur', r'wald|wurzel|moos|ranke|dorn|blüte|keim|baum|eichen|weide|kriech|würge|lianen|dschungel'),
    ('wind', r'wind|böe|wirbel|flaute|heul|luft'),
    ('erde', r'erd|fels|stein|berg|lehm|kiesel|krümel|sand|staub|grube|salz'),
]
def element_of(text):
    t = text.lower()
    for el, pat in ELEM_RULES:
        if re.search(pat, t): return el
    return None

ELEM_TINT = {
    'feuer': C('#c84a3a'), 'eis': C('#a8d0ee'), 'blitz': C('#7a8ac8'), 'gift': C('#7aa84a'), 'schatten': C('#4a3a6a'),
    'blut': C('#a83a3a'), 'wasser': C('#4a7ab8'), 'arkan': C('#8a6ac8'), 'nebel': C('#c8c8dc'), 'kristall': C('#8ad0e8'),
    'natur': C('#5a8a4a'), 'wind': C('#c8d8e8'), 'erde': C('#8a7058'),
}

# ---------------------------------------------------------------- Grundfarben nach Wesen
BASE_COL = [
    (r'ratte|maus|wühlmaus', C('#7a6a6a')), (r'wolf|leittier', C('#8a8a9a')), (r'fuchs', C('#e07a34')),
    (r'bär', C('#6a4a34')), (r'eber|keiler', C('#6a4a3a')), (r'hund|köter', C('#8a6a4a')), (r'luchs', C('#b08a5a')),
    (r'panther|katze', C('#3a3446')), (r'tiger', C('#e08a3a')), (r'hyäne|schakal|gnoll', C('#c8a870')),
    (r'ziege|bock|schaf|widder', C('#e0d8c8')), (r'stier|bulle', C('#6a3a2a')), (r'hirsch', C('#a87a4a')),
    (r'wiesel', C('#b08050')), (r'hase', C('#e6ded2')), (r'maulwurf', C('#4a3e44')), (r'affe|gorilla|koloss(?=.*dschungel)', C('#6a5040')),
    (r'krokodil|echse|salamander|molch|basilisk', C('#5a7a4a')), (r'kröte|frosch', C('#7a8a4a')), (r'schnecke', C('#c8b898')),
    (r'krähe|rabe|elster', C('#3a3446')), (r'adler|geier|milan|falke|greif|roc', C('#8a6a4a')), (r'möwe|schwalbe', C('#d8d8e0')),
    (r'eule', C('#8a6a4a')), (r'hahn|henne', C('#c8603a')), (r'schwan', C('#f0ecf4')),
    (r'fledermaus|flatterer', C('#4a3a4a')), (r'spinne|witwe', C('#3a3446')), (r'skorpion', C('#c87a3a')),
    (r'krabbe|krebs', C('#c84a3a')), (r'käfer|skarabäus|kakerlake|assel', C('#5a4a3a')), (r'ameise', C('#7a3a2a')),
    (r'schlange|natter|otter|viper|python', C('#5a8a4a')), (r'wurm|made|egel', C('#c89a8a')), (r'aal', C('#4a6a7a')),
    (r'hai', C('#6a7a9a')), (r'hecht', C('#6a8a5a')), (r'wal', C('#5a6a8a')), (r'krake|oktopus', C('#a84a6a')), (r'qualle', C('#b8a0e8')),
    (r'skelett|knochen', C('#e8e0d0')), (r'leiche|ghul|wiedergänger|zombie', C('#8a9a7a')), (r'mumie', C('#d8ccae')),
    (r'goblin|kobold', C('#6a9a55')), (r'ork', C('#5a8a4a')), (r'troll', C('#7a8a6a')), (r'oger', C('#b0907a')),
    (r'dämon|imp|höllen', C('#a83a3a')), (r'golem|koloss', C('#8a8296')), (r'schleim', C('#6ac85a')),
]
def base_col(name):
    n = name.lower()
    for pat, c in BASE_COL:
        if re.search(pat, n): return c
    return None

RANK_PX = {'D': 22, 'C': 30, 'B': 40, 'A': 52, 'S': 68, 'SS': 86}

# ---------------------------------------------------------------- Bausteine
def Q(base=None, **k): d = dict(base or {}); d.update(k); d['typ'] = 'vierbeiner'; return d
def B(base=None, **k): d = dict(base or {}); d.update(k); d['typ'] = 'zweibeiner'; return d
def F(kind='vogel', **k): k['typ'] = 'flieger'; k['kind'] = kind; return k
def I(kind='kaefer', **k): k['typ'] = 'insekt'; k['kind'] = kind; return k
def SN(kind='schlange', **k): k['typ'] = 'schlange'; k['kind'] = kind; return k
def FI(kind='fisch', **k): k['typ'] = 'fisch'; k['kind'] = kind; return k
def SL(kind='schleim', **k): k['typ'] = 'schleim'; k['kind'] = kind; return k
def SP(kind='geist', **k): k['typ'] = 'geist'; k['kind'] = kind; return k
def CL(**k): k['typ'] = 'wolke'; return k
def PL(kind='bluete', **k): k['typ'] = 'pflanze'; k['kind'] = kind; return k
def SW(kind='insekt', **k): k['typ'] = 'schwarm'; k['kind'] = kind; return k
def O(kind='truhe', **k): k['typ'] = 'objekt'; k['kind'] = kind; return k
def D(kind='drache', **k): k['typ'] = 'drache'; k['kind'] = kind; return k
def KR(**k): k['typ'] = 'kroete'; return k
def SC(**k): k['typ'] = 'schnecke'; return k
def OC(**k): k['typ'] = 'krake'; return k
def MW(**k): k['typ'] = 'schlund'; return k

# Tier-Vorlagen
RAT = dict(L=.9, bh=.3, leg=.14, head=.14, snout=.12, ears='rund', tail='duenn')
WOLF = dict(L=1.05, bh=.34, leg=.32, head=.16, snout=.14, ears='spitz', tail='buschig')
DOG = dict(L=1.0, bh=.34, leg=.3, head=.16, snout=.12, ears='haengend', tail='duenn')
CAT = dict(L=1.05, bh=.3, leg=.3, head=.15, snout=.07, ears='spitz', tail='duenn')
BEAR = dict(L=1.1, bh=.44, leg=.3, head=.19, snout=.1, ears='rund', tail='kurz', bulk=1.4)
BOAR = dict(L=1.0, bh=.42, leg=.22, head=.17, snout=.12, ears='spitz', tail='duenn', tusks=True, bulk=1.2)
GOAT = dict(L=.95, bh=.34, leg=.34, head=.14, snout=.1, ears='spitz', tail='kurz', horns='gebogen')
BULL = dict(L=1.15, bh=.44, leg=.32, head=.18, snout=.1, ears='rund', tail='loewe', horns='bulle', bulk=1.4)
DEER = dict(L=1.0, bh=.32, leg=.42, head=.14, snout=.12, neck=.15, ears='spitz', tail='kurz', horns='geweih')
LIZ = dict(L=1.3, bh=.26, leg=.14, head=.14, snout=.18, ears=None, tail='echse', nobelly=False)
CROC = dict(L=1.5, bh=.26, leg=.12, head=.14, snout=.32, ears=None, tail='echse')
HORSE = dict(L=1.1, bh=.36, leg=.42, head=.14, snout=.16, neck=.2, ears='spitz', tail='buschig', mane=True)
LION = dict(L=1.1, bh=.38, leg=.34, head=.17, snout=.08, ears='rund', tail='loewe', mane=True)
WEASEL = dict(L=1.1, bh=.22, leg=.12, head=.12, snout=.1, ears='rund', tail='buschig')
HARE = dict(L=.85, bh=.32, leg=.2, head=.15, snout=.06, ears='lang', tail='kurz', puschel=True)
MOLE = dict(L=.9, bh=.36, leg=.1, head=.14, snout=.1, ears=None, tail='kurz', snout_col=C('#e8a0b0'))
APE = dict(headtype='affe', hunch=.4, claws=False, bare_arms=True, build='normal')

GOBLIN_SKIN, ORC_SKIN = C('#6a9a55'), C('#5a8a4a')
RAGS, LEATHER, STEEL = C('#6a5a4a'), C('#5a3a2a'), C('#a8acbc')

# ---------------------------------------------------------------- Sonderfälle (Name -> Spec)
OVR = {
    # --- D
    'Kanalratte': Q(RAT), 'Riesenkakerlake': I('kakerlake', shine=True), 'Grünschleim': SL(col=C('#6ac85a')),
    'Blauschleim': SL(col=C('#7ab8e8')), 'Goblin': B(headtype='goblin', skin=GOBLIN_SKIN, col=RAGS, build='schmal', weapon='messer', bare_arms=True),
    'Goblin-Späher': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#4a6a3a'), build='schmal', weapon='bogen'),
    'Kobold': B(headtype='goblin', skin=C('#b0603a'), col=C('#5a4a3a'), build='schmal', weapon='fackel', hunch=.2),
    'Höhlenflatterer': F('fledermaus'), 'Moorkröte': KR(warts=True, col=C('#6a7a3a')), 'Stachelratte': Q(RAT, spikes=True),
    'Hauereber': Q(BOAR), 'Graswolf': Q(WOLF, col=C('#8a9a7a'), element='natur'), 'Nebelfuchs': Q(WOLF, col=C('#d8d0e0'), ears='spitz', element='nebel'),
    'Sumpfegel': SN('egel', L=.8, th=.14, col=C('#4a3a3a')), 'Aaskrähe': F('vogel'), 'Knochenhund': Q(DOG, col=C('#e8e0d0'), eye=C('#ff5a3a'), nobelly=True),
    'Skelettkrieger': B(skeleton=True, headtype='schaedel', col=C('#e8e0d0'), skin=C('#e8e0d0'), weapon='schwert'),
    'Moderleiche': B(skin=C('#8a9a7a'), col=C('#4a4a3a'), hunch=.3, claws=True, eye=C('#c8d870')),
    'Irrlicht': SP('irrlicht', col=C('#a8f0e0')), 'Pilzling': PL('pilz', col=C('#c84a4a')), 'Netzspinne': I('spinne', col=C('#5a5048')),
    'Sandflohschwarm': SW('insekt', col=C('#a8805a')), 'Dünenechse': Q(LIZ, col=C('#c8a070')), 'Glutskorpion': I('skorpion', col=C('#c84a3a'), element='feuer'),
    'Klippenkrabbe': I('krabbe'), 'Raubmöwe': F('vogel', col=C('#e0e0e8'), col2=WHITE if False else C('#f4f4f8')),
    'Salzschnecke': SC(col=C('#e8e4d8'), col2=C('#c8c0b0')), 'Wurzelgnom': B(skin=C('#c8a070'), col=C('#5a7a3a'), build='schmal', beard=C('#e8e0d0'), hair=C('#4a7d4a'), weapon='messer'),
    'Moosling': O('stein', col=C('#7a7a8a')), 'Steinkäfer': I('kaefer', col=C('#7a7a8a')), 'Lehmling': B(skin=C('#a87a5a'), col=C('#a87a5a'), col2=C('#a87a5a'), material='schlamm', build='breit'),
    'Aschemotte': F('motte', col=C('#6a5a5a'), element='feuer'), 'Funkenkäfer': I('kaefer', col=C('#e0b048'), element='blitz', shine=True),
    'Frostmaus': Q(RAT, col=C('#c8d8e8'), element='eis'), 'Eishase': Q(HARE, col=C('#e8f0f8'), element='eis'),
    'Kriechdorn': PL('ranke', col=C('#5a7a3a')), 'Blutzecke': I('zecke', col=C('#8a2a3a')), 'Dämmermaus': Q(RAT, col=C('#4a3a5a')),
    'Grubenwurm': SN('wurm', L=1.0, th=.2), 'Wasserkobold': B(headtype='goblin', skin=C('#4a8ab8'), col=C('#3a5a7a'), build='schmal', claws=True),
    'Fiebermücke': SW('insekt', col=C('#5a6a3a')), 'Lianenaffe': B(APE, skin=C('#8a6a4a'), col=C('#8a6a4a'), col2=C('#8a6a4a'), tail='duenn', tail_col=C('#8a6a4a')),
    'Giftfrosch': KR(col=C('#3a8ad0'), spots=C('#2b1e33')), 'Riesenmaulwurf': Q(MOLE), 'Schädelkrabbe': I('krabbe', col=C('#e8e0d0'), col2=C('#e8e0d0')),
    'Klagegeist': SP('kapuze', col=C('#c8c4e0'), hood_col=C('#5a5478'), eye=C('#8ad0ff')),
    'Erinnerungsfalter': F('motte', col=C('#b8a0e8'), element='arkan'), 'Brunnenkröte': KR(warts=True, col=C('#5a6a5a'), element='gift'),
    'Panzerassel': I('assel', col=C('#6a6a7a')), 'Räudenhund': Q(DOG, col=C('#7a6a4a'), spots=True), 'Sumpfluchs': Q(CAT, col=C('#8a8a5a')),
    'Rammbock-Ziege': Q(GOAT), 'Kreischeule': F('vogel', col=C('#8a6a4a'), crest=C('#6a4e34')), 'Strandschnapper': O('muschel', col=C('#a8a0b8')),
    'Brennqualle': FI('qualle', col=C('#e888a8'), element='feuer'), 'Faulblase': SL('blase', col=C('#a8b85a'), element='gift'),
    'Sandmade': SN('made', L=.6, th=.16, col=C('#e8d8b8')), 'Stumpfbeißer': O('stumpf', col=C('#6a4a32')), 'Kistenmaul': O('truhe', col=C('#8a5a36')),
    'Kanalkrokodil': Q(CROC, col=C('#5a6a4a')), 'Kampfhahn': F('vogel', col=C('#c8603a'), crest=C('#c83a3a'), alt=.3),
    'Krümelgeist': SP('wicht', element='erde'), 'Böenkobold': SP('wicht', element='wind'), 'Funkengeist': SP('flamme', element='blitz'),
    'Pfützling': SP('wicht', element='wasser'), 'Glutling': SP('flamme', element='feuer'), 'Reifling': SP('wicht', element='eis'),
    'Keimling': SP('wicht', element='natur'), 'Diebselster': F('vogel', col=C('#2b2a3a'), col2=C('#f0f0f4')),
    'Grasotter': SN('schlange', col=C('#7aa84a')), 'Steinviper': SN('schlange', col=C('#8a8296'), stripes=C('#6a6276')),
    'Schnapphecht': FI('hecht'), 'Blutwiesel': Q(WEASEL, col=C('#a84a3a')), 'Schilfnatter': SN('schlange', col=C('#a8a85a'), stripes=C('#7a7a3a')),
    'Knochenratte': Q(RAT, col=C('#e8e0d0'), eye=C('#ff5a3a'), nobelly=True), 'Rostfresser': I('kaefer', col=C('#a85a3a'), shine=True),
    'Kerzenwicht': SP('flamme', element='feuer', candle=True), 'Grabschaufler': B(skin=C('#8a9a7a'), col=C('#4a4a3a'), hunch=.3, weapon='sense'),
    'Heuwurm': SN('made', L=.7, th=.16, col=C('#d8c878')), 'Torfmolch': Q(LIZ, col=C('#5a4a3a')), 'Distelbock': Q(GOAT, spikes=True, col=C('#a89a7a')),
    'Zornbienen': SW('insekt', col=C('#e0b048')), 'Glutwespen': SW('insekt', col=C('#e8603a')), 'Wanderameisen': SW('ameise', col=C('#7a3a2a'), n=30),
    'Riesenholzwurm': SN('made', L=.8, th=.18, col=C('#e8dcc0')), 'Tangkrabbe': I('krabbe', col=C('#4a7a5a'), col2=C('#6a9a6a')),
    'Sturmschwalbe': F('vogel', col=C('#3a4a6a'), element='blitz'), 'Wüstenhyäne': Q(WOLF, col=C('#c8a870'), spots=True, ears='rund', tail='kurz'),
    'Oasenkrokodil': Q(CROC, col=C('#6a7a4a')), 'Salzkrähe': F('vogel', col=C('#d8d4e0')), 'Felsenflitzer': Q(LIZ, col=C('#8a8296'), L=1.1),
    'Kalkspinne': I('spinne', col=C('#e8e4dc'), col2=C('#d0ccc4')), 'Glutkäfer': I('kaefer', col=C('#c84a3a'), element='feuer', shine=True),
    'Aschenratte': Q(RAT, col=C('#5a5258'), element='feuer'), 'Frostflatterer': F('fledermaus', col=C('#a8c8e8'), element='eis'),
    'Eismade': SN('made', L=.7, th=.16, col=C('#d8ecf8')), 'Schneegoblin': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#e8e4dc'), build='schmal', weapon='speer'),
    'Moorgoblin': B(headtype='goblin', skin=C('#5a7a4a'), col=C('#5a5a3a'), build='schmal', weapon='speer'),
    'Sandgoblin': Q(LIZ, col=C('#c8a070'), rider=dict(skin=GOBLIN_SKIN, col=C('#c8a878'), ears=True)),
    'Dschungelgoblin': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#4a6a3a'), build='schmal', weapon='bogen'),
    'Goblin-Schamane': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#6a4a6a'), build='schmal', weapon='stab', element='nebel', robe=True),
    'Schlammling': SL('schleim', col=C('#7a5a3a'), drip=True), 'Moosbär-Junges': Q(BEAR, col=C('#5a7a4a')), 'Raubmilan': F('vogel', col=C('#a8603a')),
    'Weidenwicht': PL('baum', col=C('#8aa85a'), trunk=C('#8a7a5a')), 'Kürbisgeist': B(headtype='kuerbis', col=C('#3a2a3a'), float=True, ghost_col=C('#3a2a3a')),
    'Strohwächter': B(headtype='stroh', col=C('#8a6a4a'), col2=C('#5a4a3a'), skin=C('#e8d8a0'), weapon='sense'),
    'Lumpenpuppe': B(headtype='puppe', skin=C('#e8d8c0'), col=C('#a86a7a'), col2=C('#7a5a6a'), build='schmal'),
    'Spiegelwicht': O('spiegel', col=C('#c8d8f0'), col2=C('#a89060')), 'Tintenschnecke': SC(col=C('#3a3a5a'), col2=C('#2a2a4a')),
    'Schriftrollenmilbe': I('zecke', col=C('#e8dcc0')), 'Schimmelkriecher': SL('pfuetze', col=C('#8aa87a'), element='gift'),
    'Blutfliege': F('insekt', col=C('#7a2a3a'), alt=.4), 'Dornenmaus': Q(RAT, spikes=True, col=C('#6a7a4a')), 'Fallenkäfer': I('kaefer', col=C('#5a5a3a')),
    'Steinfresser': SN('wurm', col=C('#8a8296'), th=.2), 'Lockleuchten': SW('licht', col=C('#c8f07a')), 'Moorhenne': F('vogel', col=C('#6a6a3a'), alt=.25),
    'Nebelkrähe': F('vogel', col=C('#8a8a9a')), 'Riesenhirschkäfer': I('hirschkaefer', col=C('#5a3a2a'), shine=True),
    'Wühlmausschwarm': SW('ratte', col=C('#8a7060'), n=18), 'Bockschaf': Q(GOAT, col=C('#e8e0d0')), 'Riesenflusskrebs': I('krabbe', col=C('#8a4a3a')),
    'Giftmolch': Q(LIZ, col=C('#e07a34'), spots=True, pattern=C('#2b1e33')), 'Grottenolm': Q(LIZ, col=C('#e8c8c8'), eye=C('#e8c8c8')),
    'Tropfsteinwurm': SN('wurm', col=C('#a8a0b0'), th=.16), 'Zwielichtkatze': Q(CAT, col=C('#5a4a7a'), eye=C('#e8d040')),
    'Sackratte': Q(RAT, col=C('#8a7a6a')), 'Kletterechse': Q(LIZ, col=C('#6a9a5a')), 'Torfgeist': SP('geist', col=C('#8a7a6a'), element='feuer'),
    'Würgewinde': PL('ranke', col=C('#4a7d4a'), flower=C('#e8e0f0')), 'Schnappblüte': PL('bluete', col=C('#d85a8a')),
    'Stinkkäfer': I('kaefer', col=C('#6a7a3a'), element='gift'), 'Rußfledermaus': F('fledermaus', col=C('#3a3438')),
    'Lavaschnecke': SC(col=C('#5a4040'), col2=C('#c84a2a'), element='feuer'), 'Eiskrabbe': I('krabbe', col=C('#a8d0ee'), col2=C('#e8f6ff')),
    'Schneewiesel': Q(WEASEL, col=C('#f0f0f4')), 'Heulböe': CL(col=C('#d8e4f0'), element='wind', puffs=6),
    'Kiesel': B(skin=C('#8a8296'), col=C('#8a8296'), col2=C('#8a8296'), material='stein', build='breit', headtype='normal'),
    'Salzgeist': SP('geist', col=C('#f0ece4')), 'Staubwirbel': CL(col=C('#c8a878'), element='erde', swirl=True, puffs=7),
    'Dattelaffe': B(APE, skin=C('#a8805a'), col=C('#a8805a'), col2=C('#a8805a'), tail='duenn', tail_col=C('#a8805a')),
    'Wanderdistel': O('kugel', col=C('#8a9a5a'), col2=C('#b8a0d0')), 'Klammkröte': KR(col=C('#7a7a6a'), warts=True),
    'Brückentroll-Junges': B(headtype='troll', skin=C('#7a7a5a'), col=C('#5a4a3a'), build='breit', weapon='keule', hunch=.3),
    'Galgenrabe': F('vogel', col=C('#2b2a3a')), 'Leuchtaal': SN('aal', col=C('#4a6a8a'), element='blitz', th=.12, fin=C('#8ad0ff')),
    'Rotkappe': B(headtype='goblin', skin=C('#c8a080'), col=C('#5a4a3a'), hair=C('#c83a3a'), build='schmal', weapon='messer'),
    'Leerer Helm': O('helm', col=C('#8a8e9e'), eye=C('#8ad0ff')), 'Pfützenschleim': SL('pfuetze', col=C('#7ab0d8')),
    # --- C
    'Goblin-Hauptmann': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#6a5a4a'), armor=True, acc=C('#8a8e9e'), weapon='schwert'),
    'Hobgoblin': B(headtype='goblin', skin=C('#c8803a'), col=C('#5a3a2a'), armor=True, weapon='speer'),
    'Ork-Plünderer': B(headtype='ork', skin=ORC_SKIN, col=RAGS, build='breit', weapon='keule', bare_arms=True),
    'Ork-Wolfsreiter': Q(WOLF, col=C('#7a7a8a'), rider=dict(skin=ORC_SKIN, col=LEATHER)),
    'Graues Leittier': Q(WOLF, col=C('#8a8a9a'), element='arkan'), 'Schwarzbär': Q(BEAR, col=C('#3a3438')), 'Höhlenbär': Q(BEAR, col=C('#7a5a42')),
    'Riesenspinne': I('spinne', col=C('#3a3446'), pattern=C('#e0b048')), 'Riesenskorpion': I('skorpion', col=C('#3a3438')),
    'Waldtroll': B(headtype='troll', skin=C('#6a8a5a'), col=C('#5a4a3a'), build='breit', weapon='keule', hunch=.3, bare_arms=True),
    'Sumpftroll': B(headtype='troll', skin=C('#5a7a6a'), col=C('#4a4a3a'), build='breit', claws=True, hunch=.3, bare_arms=True),
    'Ghul': B(skin=C('#8a9a8a'), col=C('#3a3a3a'), hunch=.5, claws=True, eye=C('#e8d040'), bare_arms=True),
    'Wiedergänger': B(skin=C('#a8b0a0'), col=C('#4a4a5a'), hunch=.2, claws=True, eye=C('#8ad0ff')),
    'Skelett-Bogenschütze': B(skeleton=True, headtype='schaedel', col=C('#e8e0d0'), skin=C('#e8e0d0'), weapon='bogen'),
    'Skelettritter': B(skeleton=True, headtype='helm', col=C('#e8e0d0'), skin=C('#e8e0d0'), armor=True, acc=C('#7a7e8e'), weapon='schwert'),
    'Harpyie': B(skin=C('#e8c8a8'), col=C('#8a6a4a'), hair=C('#5a3a2a'), wings='vogel', wingcol=C('#8a6a4a'), claws=True, float=False),
    'Gnoll': B(headtype='hyaene', skin=C('#c8a870'), col=LEATHER, weapon='speer', hunch=.2),
    'Echsenkrieger': B(headtype='echse', skin=C('#5a8a4a'), col=C('#7a5a3a'), tail='echse', weapon='dreizack', tail_col=C('#5a8a4a')),
    'Kobold-Fallensteller': B(headtype='goblin', skin=C('#b0603a'), col=C('#4a3a2a'), build='schmal', weapon='hammer'),
    'Hornbulle': Q(BULL), 'Riesenkröte': KR(warts=True, col=C('#7a6a4a')), 'Zweikopfnatter': SN('schlange', col=C('#6a8a3a'), stripes=C('#4a6a2a')),
    'Lianenpython': SN('schlange', col=C('#6a7a3a'), stripes=C('#a89a4a'), th=.18, L=1.5), 'Flussechse': Q(CROC, col=C('#4a6a4a')),
    'Junger Sandwurm': SN('sandwurm', col=C('#c8a070')), 'Glutechse': Q(LIZ, col=C('#c84a3a'), element='feuer'),
    'Frostwolf': Q(WOLF, col=C('#d8e8f4'), element='eis', breath='eis', breath_len=.4),
    'Schneeschrat': B(headtype='affe', skin=C('#e8ecf0'), col=C('#e8ecf0'), col2=C('#e8ecf0'), build='riesig', bare_arms=True, hunch=.3),
    'Kleiner Steingolem': B(skin=C('#8a8296'), col=C('#8a8296'), col2=C('#8a8296'), material='stein', build='riesig', eye=C('#7ae0ff')),
    'Junger Eichenwächter': PL('baum', col=C('#4a7d4a')), 'Sumpfvettel': B(headtype='normal', skin=C('#8aa07a'), col=C('#4a5a3a'), col2=C('#3a4a2a'), robe=True, hair=C('#d0d0c0'), hunch=.4, weapon='stab', element='gift'),
    'Irrwicht-Schwarm': SW('licht', col=C('#a8f0e0')), 'Klageweib': SP('kapuze', col=C('#e0dcf0'), hood_col=C('#7a74a0'), eye=C('#ffffff')),
    'Poltergeist': SP('geist', col=C('#d8d4e8')), 'Mimik': O('truhe', col=C('#7a4a2e')), 'Wasserspeier': B(headtype='echse', skin=C('#7a7a8a'), col=C('#7a7a8a'), col2=C('#7a7a8a'), wings='fledermaus', material='stein', claws=True, hunch=.4),
    'Riesenfledermaus': F('fledermaus', col=C('#4a3a4a'), span=.7), 'Keilerbulle': Q(BOAR, col=C('#5a3a2a'), bulk=1.4),
    'Felsluchs': Q(CAT, col=C('#a89a8a')), 'Klippenadler': F('vogel', col=C('#6a4a34'), head_col=C('#f0ece4')),
    'Junge Seeschlange': SN('schlange', col=C('#3a7a8a'), fin=C('#7ac8d8'), L=1.5), 'Fjordrobbe': Q(L=1.1, bh=.32, leg=.05, head=.14, snout=.08, ears=None, tail='kurz', col=C('#7a8a9a')),
    'Nixe': SN('schlange', naga=True, col=C('#4a8ab8'), skin=C('#e8d8c8'), hair=C('#7ac8a8'), L=1.0, th=.12),
    'Flussgeist': SP('wicht', element='wasser', sz=1.2), 'Gewitterwicht': SP('wicht', element='blitz'), 'Flammenwicht': SP('flamme', element='feuer', sz=1.2),
    'Frostwicht': SP('wicht', element='eis'), 'Steinwicht': SP('wicht', element='erde'), 'Wirbelwicht': SP('wicht', element='wind'),
    'Rankenwicht': SP('wicht', element='natur'), 'Wellenwicht': SP('wicht', element='wasser'), 'Blutfledermaus-Schwarm': SW('fledermaus', col=C('#7a2a3a')),
    'Dornenhund': Q(DOG, col=C('#5a6a3a'), spikes=True, spike_col=C('#c8b898')), 'Erinnerungsdieb': SP('kapuze', col=C('#a8a0c8'), hood_col=C('#4a4268'), eye=C('#b8a0ff'), element='arkan'),
    'Echo-Wanderer': B(skin=C('#b8b8d0'), col=C('#8a8aa8'), float=True, ghost_col=C('#9a9ab8'), element='arkan'),
    'Leere Rüstung': B(headtype='leer', col=STEEL, col2=C('#7a7e8e'), skin=C('#1a1420'), armor=True, acc=STEEL, weapon='schwert', eye=C('#8ad0ff')),
    'Schwebende Klinge': O('klinge', col=C('#c8ccd8')), 'Grabwächter': B(skeleton=True, headtype='helm', skin=C('#c8c0b0'), col=C('#c8c0b0'), armor=True, acc=C('#8a8a7a'), weapon='speer'),
    'Seuchenratte': Q(RAT, col=C('#6a7a5a'), element='gift'), 'Rattenkönig': SW('ratte', col=C('#6a5a5a'), n=12, core=C('#6a5a5a')),
    'Schlammgolem': B(skin=C('#6a5038'), col=C('#6a5038'), col2=C('#6a5038'), material='schlamm', build='riesig'),
    'Moosbär': Q(BEAR, col=C('#4a6a3a'), bulk=1.6), 'Speerigel': Q(L=.8, bh=.4, leg=.1, head=.13, snout=.1, ears='rund', tail=None, spikes=True, spike_h=1.8, col=C('#6a5a4a')),
    'Riesengrabkäfer': I('kaefer', col=C('#3a3438'), shine=True), 'Höhlenwurm': SN('wurm', col=C('#c8a8b0'), th=.24, element='gift'),
    'Hornviper': SN('schlange', col=C('#c8a070'), stripes=C('#8a6a4a')), 'Oasenschlange': SN('schlange', col=C('#5a8a7a'), element='gift'),
    'Salzgolem': B(skin=C('#e8e4dc'), col=C('#e8e4dc'), col2=C('#e8e4dc'), material='salz', build='riesig'),
    'Schluchtenläufer': F('vogel', col=C('#a87a4a'), alt=.3, beak=C('#5a4a3a')), 'Klammspinne': I('spinne', col=C('#7a6a5a')),
    'Fieberaffe': B(APE, skin=C('#7a8a4a'), col=C('#7a8a4a'), col2=C('#7a8a4a'), tail='duenn', tail_col=C('#7a8a4a')),
    'Lauerechse': Q(LIZ, col=C('#6a5a3a')), 'Dschungelwitwe': I('spinne', col=C('#2b2a30'), pattern=C('#c83a3a')),
    'Mückenkönigin': F('insekt', col=C('#5a6a3a'), stripes=C('#3a4a2a'), stinger=True, span=.5),
    'Glutwolf': Q(WOLF, col=C('#5a4a4a'), flames=True, element='feuer'), 'Aschenschleim': SL(col=C('#6a5a5a'), element='feuer'),
    'Lavakrabbe': I('krabbe', col=C('#4a3a3a'), col2=C('#c84a2a'), element='feuer'), 'Rauchschlange': SN('schlange', col=C('#6a6a7a'), element='nebel'),
    'Weißer Bär': Q(BEAR, col=C('#f0f0f4')), 'Frostspinne': I('spinne', col=C('#a8d0ee'), col2=C('#e8f6ff')), 'Eisschleim': SL(col=C('#b8e4ff'), element='eis'),
    'Lawinenbock': Q(GOAT, col=C('#f0f0f4'), bulk=1.3), 'Sturmziege': Q(GOAT, col=C('#8a8ab0'), horns='gerade', element='blitz'),
    'Donnerfalke': F('vogel', col=C('#4a5a8a'), element='blitz'), 'Blitzaal': SN('aal', col=C('#3a4a6a'), element='blitz', fin=C('#fff07a')),
    'Fjordkrake': OC(col=C('#7a4a6a')), 'Riffwächter': B(skin=C('#c87a6a'), col=C('#c87a6a'), col2=C('#c87a6a'), material='koralle', build='riesig'),
    'Tangweib': B(skin=C('#a8c8b8'), col=C('#3a6a4a'), col2=C('#2a5a3a'), robe=True, hair=C('#4a7a4a')),
    'Nebelwolf': Q(WOLF, col=C('#c8c8dc'), element='nebel'), 'Wanderbaum': PL('baum', col=C('#4a7d4a')),
    'Nebelhirsch': Q(DEER, col=C('#d0d0e0'), element='nebel', horn_col=C('#e8e4f0')), 'Moorhund': Q(DOG, col=C('#4a4a3a')),
    'Torfgolem': B(skin=C('#4a3a2a'), col=C('#4a3a2a'), col2=C('#4a3a2a'), material='schlamm', build='riesig', element='gift'),
    'Sumpfspinne': I('spinne', col=C('#4a5a3a')), 'Schilfmann': B(headtype='stroh', skin=C('#a8a85a'), col=C('#8a8a4a'), col2=C('#7a7a3a'), build='schmal'),
    'Goblin-Reiter': Q(BOAR, rider=dict(skin=GOBLIN_SKIN, col=RAGS, ears=True)), 'Werratte': B(headtype='ratte', skin=C('#7a6a6a'), col=C('#5a4a3a'), claws=True, hunch=.3, tail='duenn', tail_col=C('#c89a8a')),
    'Ork-Brecher': B(headtype='ork', skin=ORC_SKIN, col=LEATHER, build='breit', weapon='axt', armor=True, acc=C('#7a7e8e')),
    'Junger Oger': B(headtype='oger', skin=C('#b0907a'), col=RAGS, build='riesig', belly=C('#c8a890'), weapon='keule'),
    'Felsenwerfer': B(headtype='riese', skin=C('#a89080'), col=C('#6a5a4a'), build='riesig', bare_arms=True),
    'Junger Basilisk': Q(LIZ, col=C('#6a7a3a'), spikes=True, eye=C('#e8d040')), 'Kokatrize': Q(LIZ, col=C('#c8a050'), beak=C('#e0a040'), wings=True, wingspan=.4),
    'Hippogreif': Q(HORSE, col=C('#a87a4a'), beak=C('#e0a040'), wings=True, wingspan=.7, mane=False),
    'Junger Nachtmahr': Q(HORSE, col=C('#2b2a3a'), mane_col=C('#6a4aa8'), element='schatten'), 'Dämmerpanther': Q(CAT, col=C('#4a3a5a'), eye=C('#e8d040')),
    'Klingenkäfer': I('kaefer', col=C('#8a8e9e'), shine=True), 'Säurekäfer': I('kaefer', col=C('#8ab83a'), element='gift'),
    'Säureschleim': SL(col=C('#c8e05a'), element='gift'), 'Blutschleim': SL(col=C('#a83a3a'), element='blut'),
    'Dornranken-Wächter': PL('ranke', col=C('#3a5a2a')), 'Dornenkäfer': I('kaefer', col=C('#4a5a3a'), shine=True),
    'Blutpilz': PL('pilz', col=C('#8a2a3a')), 'Glockenwicht': O('glocke', col=C('#c8a040')), 'Wiegengeist': SP('geist', col=C('#e8e0f8'), element='arkan'),
    'Grabschwan': F('vogel', col=C('#f0ecf4'), eye=C('#c83a3a'), alt=.3), 'Kanalschlange': SN('schlange', col=C('#e8e0d8'), L=1.6, th=.18),
    'Sumpfleiche': B(skin=C('#6a7a5a'), col=C('#4a4a3a'), hunch=.3, claws=True), 'Sandmumie': B(headtype='mumie', skin=C('#d8ccae'), col=C('#d8ccae'), col2=C('#c8bc9e'), wrap=True),
    'Skarabäusschwarm': SW('kaefer', col=C('#3a5a6a'), n=26), 'Schakalrudel': SW('ratte', col=C('#c8a070'), n=8),
    'Dünenreiter': Q(LIZ, col=C('#c8a070'), rider=dict(skin=C('#5a8a4a'), col=C('#c8a878'))), 'Fata': CL(col=C('#e8d8b0'), element='arkan', puffs=6),
    'Felsgeier': F('vogel', col=C('#5a4a4a'), head_col=C('#e8a0a0')), 'Kristallkäfer': I('kaefer', col=C('#8ad0e8'), element='kristall', shine=True),
    'Stollenmaul': MW(col=C('#6a5a4a'), alt=.4), 'Kleiner Erzgolem': B(skin=C('#7a6a5a'), col=C('#7a6a5a'), col2=C('#7a6a5a'), material='erz', build='riesig'),
    'Grubengasgeist': SP('wicht', element='gift'), 'Bergtroll': B(headtype='troll', skin=C('#8a8a9a'), col=C('#5a4a3a'), build='riesig', weapon='keule', hunch=.3, bare_arms=True),
    'Felsenechse': Q(LIZ, col=C('#8a8296'), spikes=True), 'Riesensteinadler': F('vogel', col=C('#6a6a7a'), span=.7),
    'Pilzriese': B(headtype='pilz', skin=C('#e8dcc0'), col=C('#e8dcc0'), col2=C('#c8bca0'), cap=C('#8a5aa8'), build='riesig', element='gift'),
    'Sporenträger': B(headtype='pilz', skin=C('#a8b090'), col=C('#5a5a4a'), cap=C('#a8705a'), hunch=.3, element='gift'),
    'Blattmantis': I('mantis', col=C('#6aa84a'), col2=C('#8ac86a')), 'Riesenhornisse': F('insekt', col=C('#e0b048'), stripes=C('#2b1e33'), stinger=True),
    'Feuerameisen-Kolonie': SW('ameise', col=C('#c84a2a'), n=30), 'Staubmotte': F('motte', col=C('#b8a888')),
    'Schreckenskrähe': F('vogel', col=C('#2b2a3a'), span=.65), 'Verwilderter Kettenhund': Q(DOG, col=C('#6a5a4a'), ears='spitz'),
    'Brückentroll': B(headtype='troll', skin=C('#7a7a5a'), col=C('#5a4a3a'), build='riesig', weapon='keule', hunch=.3, bare_arms=True),
    'Höhlenoktopus': OC(col=C('#8a6a7a')), 'Knochenhecht': FI('hecht', col=C('#e8e0d0')), 'Eisenwolf': Q(WOLF, col=C('#6a6e7e'), ore=C('#a8acbc')),
    'Gewitterschaf': Q(GOAT, col=C('#e8e8f4'), horns=None, element='blitz', bulk=1.3), 'Ruinenwächter': B(skin=C('#9a9488'), col=C('#9a9488'), col2=C('#9a9488'), material='runen', build='riesig'),
    'Graue Gestalt': B(skin=C('#a8a8b0'), col=C('#8a8a92'), col2=C('#7a7a82'), element='arkan'), 'Ascheläufer': B(skin=C('#5a4a4a'), col=C('#3a3030'), material='asche', element='feuer'),
    'Höllenwelpe': Q(DOG, col=C('#8a2a2a'), ears='spitz', flames=True), 'Imp': B(skin=C('#c84a3a'), col=C('#c84a3a'), col2=C('#a83a2a'), build='schmal', horns=True, wings='fledermaus', tail='duenn', tail_col=C('#c84a3a'), wingspan=.35),
    'Werkstattwicht': B(headtype='goblin', skin=C('#8a7a6a'), col=C('#5a4a3a'), build='schmal', weapon='hammer'),
    'Riesenbücherwurm': SN('made', col=C('#e8dcc0'), th=.22, L=1.0),
    # --- B
    'Oger': B(headtype='oger', skin=C('#b0907a'), col=RAGS, build='riesig', belly=C('#c8a890'), weapon='keule'),
    'Troll': B(headtype='troll', skin=C('#7a8a6a'), col=C('#5a4a3a'), build='riesig', weapon='keule', hunch=.3, bare_arms=True),
    'Minotaurus': B(headtype='bulle', skin=C('#6a3a2a'), col=LEATHER, build='breit', weapon='axt', bare_arms=True),
    'Wyvern': D('wyvern', col=C('#5a7a4a')), 'Greif': Q(LION, col=C('#c8a060'), beak=C('#e0a040'), wings=True, wingspan=.85, mane=False),
    'Mantikor': Q(LION, col=C('#c87a4a'), tail='stachel', wings=True, wingkind='fledermaus', wingcol=C('#8a4a3a')),
    'Basilisk': Q(LIZ, col=C('#5a6a3a'), spikes=True, eye=C('#e8d040'), L=1.5), 'Chimäre': Q(LION, col=C('#c8903a'), horns='gebogen', tail='duenn', wings=True, wingkind='fledermaus', breath='feuer', breath_len=.5),
    'Sumpfhydra': D('hydra', col=C('#4a6a4a'), heads=5, nowings=True), 'Ausgewachsene Fjordkrake': OC(col=C('#6a3a5a')),
    'Seeschlange': SN('wyrm', col=C('#3a6a8a'), fin=C('#7ac8d8'), L=1.8, th=.22, rear=.4), 'Sandwurm': SN('sandwurm', col=C('#c8a070'), th=.36),
    'Erzbär': Q(BEAR, col=C('#6a6a6a'), ore=C('#d8a848')), 'Junger Frostriese': B(headtype='riese', skin=C('#b8d8f0'), col=C('#e8f0f8'), build='riesig', weapon='keule', beard=C('#ffffff'), element='eis'),
    'Hügelriese': B(headtype='riese', skin=C('#c8a080'), col=RAGS, build='riesig', weapon='baum'),
    'Steingolem': B(skin=C('#8a8296'), col=C('#8a8296'), col2=C('#8a8296'), material='stein', build='riesig', eye=C('#7ae0ff')),
    'Eisengolem': B(skin=C('#6a6e7e'), col=C('#6a6e7e'), col2=C('#6a6e7e'), material='eisen', build='riesig', eye=C('#ff9a3c')),
    'Eichenwächter': PL('baum', col=C('#3e6a3a')), 'Werwolf': B(headtype='wolf', skin=C('#6a6a7a'), col=C('#4a3a3a'), claws=True, hunch=.4, bare_arms=True, tail='buschig', tail_col=C('#6a6a7a'), build='breit'),
    'Blutsauger': B(headtype='vampir', skin=C('#e0d8e0'), col=C('#2b2a3a'), col2=C('#2b2a3a'), cape=C('#7a1e2a'), claws=True, eye=C('#c83a3a')),
    'Knochenmagier': B(skeleton=True, headtype='schaedel', skin=C('#e8e0d0'), col=C('#4a3a5a'), col2=C('#3a2a4a'), robe=True, weapon='stab', element='schatten'),
    'Gespensterritter': B(headtype='helm', col=C('#a8c0d8'), col2=C('#8aa0b8'), skin=C('#a8c0d8'), armor=True, acc=C('#c8d8e8'), float=True, ghost_col=C('#a8c0d8'), weapon='schwert', eye=C('#8ad0ff')),
    'Mumienpriester': B(headtype='mumie', skin=C('#d8ccae'), col=C('#d8ccae'), col2=C('#c8bc9e'), wrap=True, weapon='stab', element='erde', crown=True, crown_col=C('#3a7ab8')),
    'Gnollhäuptling': B(headtype='hyaene', skin=C('#c8a870'), col=LEATHER, weapon='axt', armor=True, acc=C('#8a8e9e'), build='breit'),
    'Ork-Kriegsherr': B(headtype='ork', skin=ORC_SKIN, col=LEATHER, build='riesig', weapon='axt', armor=True, acc=C('#6a6e7e'), horns=True),
    'Echsenschamane': B(headtype='echse', skin=C('#5a8a4a'), col=C('#6a4a6a'), robe=True, tail='echse', tail_col=C('#5a8a4a'), weapon='stab', element='gift'),
    'Harpyienkönigin': B(skin=C('#e8c8a8'), col=C('#6a4a8a'), hair=C('#3a2a3a'), wings='vogel', wingcol=C('#6a4a8a'), claws=True, crown=True, wingspan=.75),
    'Nachtmahr': Q(HORSE, col=C('#1e1a28'), mane_col=C('#8a5ad8'), element='schatten', flames=False),
    'Phasenspinne': I('spinne', col=C('#6a5ab8'), element='arkan'), 'Spinnenmutter': I('spinne', col=C('#3a3446'), pattern=C('#e0b048')),
    'Panzerskorpion': I('skorpion', col=C('#5a5a6a')), 'Säbelzahntiger': Q(CAT, col=C('#e08a3a'), stripes=True, tusks=True, bulk=1.3, ears='rund'),
    'Flussdrache': Q(CROC, col=C('#3a5a3a'), L=1.6, bulk=1.3), 'Dschungelwyrm': SN('wyrm', col=C('#4a7a3a'), stripes=C('#3a5a2a'), L=1.8, th=.22),
    'Krötenkönig': KR(warts=True, col=C('#6a7a3a'), element='gift'), 'Glutsalamander': Q(LIZ, col=C('#c84a2a'), element='feuer', flames=True),
    'Feuerelementar': SP('elementar', element='feuer', sz=1.4), 'Eiselementar': SP('elementar', element='eis', sz=1.4, chunks=True),
    'Erdelementar': SP('elementar', element='erde', sz=1.4, chunks=True), 'Windelementar': SP('elementar', element='wind', sz=1.4),
    'Wasserelementar': SP('elementar', element='wasser', sz=1.4), 'Blitzelementar': SP('elementar', element='blitz', sz=1.4),
    'Wurzelriese': PL('baum', col=C('#3a5a2a'), trunk=C('#5a3a2a')), 'Steinflügler': SW('fledermaus', col=C('#7a7a8a'), n=12),
    'Hausmimik': O('haus', col=C('#ded2be')), 'Grabgolem': B(skin=C('#8a8a7a'), col=C('#8a8a7a'), col2=C('#8a8a7a'), material='runen', build='riesig'),
    'Großer Höhlenoktopus': OC(col=C('#7a5a7a')), 'Dornenbestie': Q(BEAR, col=C('#3a5a2a'), spikes=True, spike_col=C('#c8b898')),
    'Blutwolf': Q(WOLF, col=C('#8a2a2a'), element='blut'), 'Erinnerungsfresser': MW(col=C('#6a5a9a'), element='arkan'),
    'Echo-Ritter': B(headtype='helm', col=C('#9a9ab8'), skin=C('#9a9ab8'), armor=True, acc=C('#b8b8d0'), weapon='schwert', element='arkan'),
    'Nebelbestie': Q(WOLF, col=C('#c8c8dc'), element='nebel', bulk=1.4, bh=.42), 'Irrwurzel': PL('ranke', col=C('#6a4a32')),
    'Moorwächter': B(skin=C('#5a6a4a'), col=C('#3a3a2a'), crown=True, hunch=.2, claws=True), 'Sumpfriese': B(headtype='riese', skin=C('#6a7a5a'), col=C('#4a4a3a'), build='riesig', robe=True, col2=C('#4a5a3a')),
    'Salzwurm': SN('wurm', col=C('#e8e4dc'), th=.3, L=1.6), 'Schluchtenroc': F('vogel', col=C('#8a5a3a'), span=.8),
    'Kristallgolem': B(skin=C('#8ad0e8'), col=C('#8ad0e8'), col2=C('#8ad0e8'), material='kristall', build='riesig'),
    'Stollenwyrm': SN('wurm', col=C('#6a6a6a'), th=.3, L=1.7), 'Gewittergreif': Q(LION, col=C('#6a7aa8'), beak=C('#e0a040'), wings=True, wingspan=.85, mane=False, element='blitz'),
    'Junger Donnervogel': F('vogel', col=C('#3a4a8a'), element='blitz', span=.7, crest=C('#fff07a')),
    'Seehexe': B(skin=C('#a8c8c8'), col=C('#2a5a6a'), col2=C('#1e4a5a'), robe=True, hair=C('#4a8a7a'), weapon='stab', element='wasser'),
    'Zahnhai': FI('hai', col=C('#6a7a9a')), 'Eiswurm': SN('wurm', col=C('#c8e4f4'), th=.3, L=1.6, element='eis'),
    'Yeti': B(headtype='affe', skin=C('#f0f0f4'), col=C('#f0f0f4'), col2=C('#f0f0f4'), build='riesig', bare_arms=True, hunch=.3, element='eis'),
    'Schneegreif': Q(LION, col=C('#f0f0f4'), beak=C('#e0a040'), wings=True, wingspan=.85, mane=False),
    'Lavagolem': B(skin=C('#4a3a3a'), col=C('#4a3a3a'), col2=C('#4a3a3a'), material='lava', build='riesig', eye=C('#ffd27a'), element='feuer'),
    'Aschenwyvern': D('wyvern', col=C('#5a5258'), breath='feuer'), 'Glutpanther': Q(CAT, col=C('#2b2a30'), flames=True, eye=C('#ffd27a')),
    'Aschegeist': SP('geist', col=C('#8a8088'), element='feuer'), 'Grauer Ritter': B(headtype='helm', col=C('#9a9aa0'), skin=C('#9a9aa0'), armor=True, acc=C('#b0b0b8'), weapon='schwert'),
    'Dämonensoldat': B(skin=C('#a83a3a'), col=C('#3a3446'), armor=True, acc=C('#4a4458'), horns=True, weapon='speer', tail='duenn', tail_col=C('#a83a3a')),
    'Höllenhund': Q(WOLF, col=C('#5a1e1e'), flames=True, breath='feuer', breath_len=.5, eye=C('#ffd27a')),
    'Dämonenreiter': Q(WOLF, col=C('#5a1e1e'), flames=True, rider=dict(skin=C('#a83a3a'), col=C('#3a3446'), horns=True)),
    'Wüstengolem': B(skin=C('#c8a070'), col=C('#c8a070'), col2=C('#c8a070'), material='sand', build='riesig'),
    'Junge Sphinx': Q(LION, col=C('#d8b870'), mane_col=C('#3a5a9a')), 'Oasenhydra': D('hydra', col=C('#4a8a7a'), heads=3, nowings=True),
    'Trugbildbestie': Q(LION, col=C('#e8d8b0'), element='arkan', mane=False), 'Riesenpython': SN('schlange', col=C('#6a6a3a'), stripes=C('#a89a5a'), L=2.0, th=.25),
    'Brüllaffen-König': B(dict(APE, build='breit'), skin=C('#7a5040'), col=C('#7a5040'), col2=C('#7a5040'), crown=True),
    'Fleischblüte': PL('bluete', col=C('#a83a5a')), 'Sporenmutter': PL('pilz', col=C('#8a5aa8'), element='gift'),
    'Hornissenkönigin': F('insekt', col=C('#e0b048'), stripes=C('#2b1e33'), stinger=True, span=.6, crest=C('#e0b048')),
    'Seeleiche': B(skin=C('#7a9a9a'), col=C('#2a3a5a'), col2=C('#1e2a3a'), weapon='schwert', hair=C('#2a2a3a'), claws=True),
    'Knochenkoloss': B(skeleton=True, headtype='schaedel', skin=C('#e8e0d0'), col=C('#e8e0d0'), build='riesig', weapon='keule'),
    'Glockengeist': O('glocke', col=C('#8a8aa8')), 'Grimoire-Biest': O('buch', col=C('#6a3a5a')),
    'Bruchklang-Wesen': SP('elementar', element='arkan', body_col=C('#8a6ac8'), sz=1.3, chunks=True), 'Staubestie': Q(BEAR, col=C('#8a6ac8'), element='arkan'),
    'Berserker-Keiler': Q(BOAR, col=C('#7a2a2a'), bulk=1.4, eye=C('#ff3a3a')), 'Weißer Wolf': Q(WOLF, col=C('#f0f0f4'), element='eis'),
    'Goblinkönig': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#6a3a6a'), crown=True, weapon='schwert', cape=C('#a83a3a')),
    'Trollmutter': B(headtype='troll', skin=C('#7a8a6a'), col=C('#6a4a3a'), build='riesig', hunch=.3, hair=C('#5a5a4a'), bare_arms=True),
    'Zweiköpfiger Oger': B(headtype='oger', skin=C('#a8887a'), col=RAGS, build='riesig', belly=C('#c8a890'), weapon='keule'),
    'Inselkröte': KR(col=C('#6a7a4a'), warts=True), 'Klippenwyrm': D('wyvern', col=C('#8a7a6a')), 'Flautegeist': SP('geist', col=C('#e8ecf4')),
    'Dürregeist': SP('geist', col=C('#d8b880'), element='erde'), 'Schwarzwasser-Nix': SN('schlange', naga=True, col=C('#2a3a3a'), skin=C('#8aa8a0'), hair=C('#2a3a3a')),
    'Krähenmutter': SW('vogel', col=C('#2b2a3a'), n=16, core=C('#2b2a3a')),
    # --- A
    'Roc': F('vogel', col=C('#8a6a4a'), span=.9), 'Junger Behemoth': Q(BULL, col=C('#6a5a4a'), horns='gebogen', bulk=1.6),
    'Krake': OC(col=C('#8a3a5a')), 'Tiefseeschlange': SN('wyrm', col=C('#2a4a6a'), fin=C('#5aa8c8'), L=2.0, th=.24, element='wasser'),
    'Frostriese': B(headtype='riese', skin=C('#b8d8f0'), col=C('#e8f0f8'), build='riesig', weapon='axt', beard=C('#ffffff'), element='eis'),
    'Feuerriese': B(headtype='riese', skin=C('#c8603a'), col=C('#3a3030'), build='riesig', weapon='hammer', beard=C('#ff9a3c'), element='feuer'),
    'Sturmriese': B(headtype='riese', skin=C('#8a9ac8'), col=C('#4a5a8a'), build='riesig', weapon='speer', beard=C('#e8ecf4'), element='blitz'),
    'Felsriese': B(skin=C('#8a8296'), col=C('#8a8296'), col2=C('#8a8296'), material='stein', build='riesig', headtype='riese'),
    'Große Hydra': D('hydra', col=C('#3a6a4a'), heads=9, nowings=True), 'Lich': B(skeleton=True, headtype='schaedel', skin=C('#e8e0d0'), col=C('#3a2a5a'), col2=C('#4a3a6a'), robe=True, weapon='stab', element='schatten', crown=True),
    'Todesritter': B(headtype='helm', col=C('#3a3446'), skin=C('#3a3446'), armor=True, acc=C('#4a4458'), weapon='schwert', weapon_col=C('#8a5ad8'), cape=C('#5a1e2a'), eye=C('#ff3a3a'), element='schatten'),
    'Vampirfürst': B(headtype='vampir', skin=C('#e8e0e8'), col=C('#2b2a3a'), col2=C('#2b2a3a'), cape=C('#a83a3a'), claws=True, crown=True, eye=C('#c83a3a'), element='blut'),
    'Großes Klageweib': SP('kapuze', col=C('#e0dcf0'), hood_col=C('#5a5478'), eye=C('#ffffff'), sz=1.4),
    'Knochendrache': D('drache', col=C('#5a5058'), bone=C('#e8e0d0'), eye=C('#8ad0ff'), wingcol=C('#4a4048'), breath='schatten'),
    'Wurzelkönig': PL('baum', col=C('#2e5a2e'), trunk=C('#4a3222'), flower=C('#e0b048')), 'Sphinx': Q(LION, col=C('#d8b870'), mane_col=C('#3a5a9a'), wings=True, wingcol=C('#d8b870')),
    'Lamia': SN('schlange', naga=True, col=C('#6a8a3a'), skin=C('#e8d0b0'), hair=C('#2b2a3a'), stripes=C('#a8a84a'), L=1.4, th=.18),
    'Steinblick-Gorgone': SN('schlange', naga=True, col=C('#5a7a5a'), skin=C('#a8c8a0'), hair=C('#4a8a3a'), eye=C('#e8d040'), L=1.3, th=.16),
    'Zyklop': B(headtype='zyklop', skin=C('#c8a080'), col=RAGS, build='riesig', weapon='keule', bare_arms=True),
    'Minotaurenfürst': B(headtype='bulle', skin=C('#4a2a2a'), col=C('#3a3446'), build='riesig', weapon='axt', armor=True, acc=C('#8a8e9e'), crown=True),
    'Ork-Großkhan': B(headtype='ork', skin=ORC_SKIN, col=C('#3a2a2a'), build='riesig', weapon='axt', armor=True, acc=C('#6a6e7e'), crown=True, cape=C('#7a1e2a')),
    'Goblin-Unsterblicher': B(headtype='goblin', skin=GOBLIN_SKIN, col=C('#4a3a6a'), robe=True, col2=C('#3a2a5a'), weapon='stab', element='arkan', crown=True),
    'Trollkönig': B(headtype='troll', skin=C('#6a7a5a'), col=C('#4a3a2a'), build='riesig', weapon='keule', crown=True, hunch=.3, bare_arms=True),
    'Werwolf-Alpha': B(headtype='wolf', skin=C('#4a4a5a'), col=C('#3a2a2a'), claws=True, hunch=.4, bare_arms=True, tail='buschig', tail_col=C('#4a4a5a'), build='riesig', eye=C('#ffd27a')),
    'Junger Phönix': F('vogel', col=C('#e8603a'), col2=C('#ffd27a'), element='feuer', crest=C('#ffd27a'), span=.7),
    'Donnervogel': F('vogel', col=C('#2a3a7a'), element='blitz', span=.85, crest=C('#fff07a')),
    'Frostschwinge': F('vogel', col=C('#b8e4ff'), col2=C('#ffffff'), element='eis', span=.9),
    'Mantikorfürst': Q(LION, col=C('#a85a3a'), tail='stachel', wings=True, wingkind='fledermaus', wingcol=C('#6a2a2a'), bulk=1.3),
    'Chimärenkönig': Q(LION, col=C('#a87a2a'), horns='gebogen', wings=True, wingkind='fledermaus', breath='feuer', breath_len=.6, bulk=1.3),
    'Greifenkönig': Q(LION, col=C('#e0b048'), beak=C('#e0a040'), wings=True, wingspan=1.0, mane=False, bulk=1.3),
    'Ur-Basilisk': Q(LIZ, col=C('#3a5a2a'), spikes=True, eye=C('#ff3a3a'), L=1.6, bulk=1.4), 'Sandwurm-Mutter': SN('sandwurm', col=C('#b8905a'), th=.42),
    'Salztitan': B(skin=C('#e8e4dc'), col=C('#e8e4dc'), col2=C('#e8e4dc'), material='salz', build='riesig', headtype='riese'),
    'Moorkönig': B(skin=C('#5a6a4a'), col=C('#3a3a2a'), crown=True, hunch=.2, claws=True, build='breit', robe=True, col2=C('#2e3a2a')),
    'Nebelfürst': CL(col=C('#d8d8e8'), element='nebel', eyes=C('#8ad0ff')), 'Irrlichtkönigin': SW('licht', col=C('#a8f0e0'), n=30, core=C('#e8fff8')),
    'Eisenkoloss': B(skin=C('#5a5e6e'), col=C('#5a5e6e'), col2=C('#5a5e6e'), material='eisen', build='riesig', eye=C('#ff9a3c')),
    'Kristallwyrm': D('drache', col=C('#7ab8d8'), nowings=True, breath='kristall', element='kristall'),
    'Lavawurm': SN('wurm', col=C('#4a3030'), th=.32, L=1.8, element='feuer'), 'Aschenkoloss': B(skin=C('#5a5258'), col=C('#5a5258'), col2=C('#5a5258'), material='asche', build='riesig'),
    'Dämonengeneral': B(skin=C('#a83a3a'), col=C('#2b2a30'), armor=True, acc=C('#4a4458'), horns=True, wings='fledermaus', wingspan=.7, weapon='schwert', weapon_col=C('#ff9a3c'), crown=True, build='breit', tail='duenn', tail_col=C('#a83a3a')),
    'Höllenbestie': Q(BULL, col=C('#6a1e1e'), horns='gebogen', flames=True, spikes=True, breath='feuer'),
    'Blutfürst': B(headtype='vampir', skin=C('#e0c8c8'), col=C('#5a1e2a'), col2=C('#3a1420'), cape=C('#a83a3a'), crown=True, element='blut', weapon='schwert', weapon_col=C('#c83a3a')),
    'Dornentitan': B(skin=C('#3a5a2a'), col=C('#3a5a2a'), col2=C('#3a5a2a'), material='dornen', build='riesig', headtype='riese', eye=C('#e8d040')),
    'Erinnerungsweber': I('spinne', col=C('#8a6ac8'), pattern=C('#e0d0ff'), element='arkan'),
    'Stillstandswächter': B(skin=C('#a8a090'), col=C('#a8a090'), col2=C('#a8a090'), material='runen', build='riesig', element='arkan'),
    'Wächter von Valmor': B(skin=C('#c8b070'), col=C('#c8b070'), col2=C('#c8b070'), material='runen', build='riesig', crown=True, weapon='speer'),
    'Bruchklang-Koloss': SP('elementar', element='arkan', body_col=C('#c84a8a'), sz=1.6, chunks=True),
    'Geisterschiff': O('schiff', col=C('#5a5a6a'), sail=C('#a8b8c8')), 'Seeschlangenkönigin': SN('wyrm', col=C('#2a5a7a'), fin=C('#7ac8d8'), L=2.1, th=.26, rear=.45),
    'Korallenkoloss': B(skin=C('#d87a6a'), col=C('#d87a6a'), col2=C('#d87a6a'), material='koralle', build='riesig'),
    'Sturmhai': FI('hai', col=C('#4a5a8a'), element='blitz'), 'Wolkenwal': FI('wal', col=C('#c8d4e8'), col2=C('#f0f4fa'), sky=True, L=1.2, h=.42),
    'Gletscherwurm': SN('wurm', col=C('#c8e4f4'), th=.34, L=1.9, element='eis'), 'Lawinenriese': B(headtype='riese', skin=C('#e8ecf4'), col=C('#c8d4e0'), build='riesig', bare_arms=True, element='eis'),
    'Frostwolf-Mutter': Q(WOLF, col=C('#e8f0f8'), element='eis', bulk=1.4, breath='eis'),
    'Fieberfürst': B(headtype='kapuze', col=C('#5a6a3a'), col2=C('#4a5a2a'), robe=True, hood_col=C('#4a5a2a'), eye=C('#c8f07a'), weapon='stab', element='gift'),
    'Dschungelkoloss': B(dict(APE, build='riesig'), skin=C('#3a3438'), col=C('#3a3438'), col2=C('#3a3438')),
    'Sporenkönigin': PL('pilz', col=C('#6a3a8a'), element='gift'), 'Würgebaum': PL('baum', col=C('#2e4a2e'), trunk=C('#3a2a1e')),
    'Sandsturmgeist': CL(col=C('#c8a070'), element='erde', swirl=True, eyes=C('#ffd27a')), 'Oasenwächter': SP('elementar', element='wasser', sz=1.5),
    'Grabkönig': B(skeleton=True, headtype='schaedel', skin=C('#e8e0d0'), col=C('#e8e0d0'), armor=True, acc=C('#8a7a5a'), crown=True, weapon='schwert', cape=C('#3a2a4a')),
    'Mumienkönig': B(headtype='mumie', skin=C('#d8ccae'), col=C('#d8ccae'), col2=C('#c8bc9e'), wrap=True, crown=True, crown_col=C('#3a7ab8'), weapon='stab', element='erde'),
    'Riesenskarabäus': I('kaefer', col=C('#2a5a6a'), shine=True), 'Junger Sumpfdrache': D('drache', col=C('#4a6a3a'), breath='gift'),
    'Schwarzwasserhydra': D('hydra', col=C('#2a3a3a'), heads=5, nowings=True), 'Krähenkönig': F('vogel', col=C('#2b2a3a'), crest=C('#e0b048'), span=.75),
    'Moorwolf-Alpha': Q(WOLF, col=C('#4a4a3a'), bulk=1.5), 'Bergwyrm': D('drache', col=C('#7a6a5a'), nowings=True),
    'Runengolem': B(skin=C('#7a7a8a'), col=C('#7a7a8a'), col2=C('#7a7a8a'), material='runen', build='riesig', eye=C('#7ae0ff')),
    'Geweihter Hirsch': Q(DEER, col=C('#e8e0d0'), horn_col=C('#6a4a32'), leaves=True, element='natur'),
    'Klingenwolf': Q(WOLF, col=C('#8a8e9e'), spikes=True, spike_col=C('#e8ecf4')), 'Phasenbestie': Q(CAT, col=C('#6a5ab8'), element='arkan', bulk=1.3),
    'Spiegelbestie': Q(CAT, col=C('#c8d8f0'), element='arkan'), 'Mimikkönig': O('truhe', col=C('#c8a040'), col2=C('#8a5a36')),
    'Flammenschädel': SP('flamme', element='feuer', sz=1.3), 'Gewitterkoloss': CL(col=C('#5a6080'), element='blitz', eyes=C('#fff07a'), rain=C('#8ac4ee')),
    'Seehexenkönigin': B(skin=C('#a8c8c8'), col=C('#1e4a5a'), col2=C('#123a4a'), robe=True, hair=C('#4a8a7a'), weapon='dreizack', crown=True, element='wasser'),
    'Treibgutriese': B(skin=C('#7a6a5a'), col=C('#7a6a5a'), col2=C('#7a6a5a'), material='wrack', build='riesig', headtype='riese'),
    'Windwyrm': SN('wyrm', col=C('#c8d8e8'), L=2.0, th=.2, element='wind'), 'Graswurm': SN('sandwurm', col=C('#7a8a4a'), dirt=C('#6a8a4a'), th=.4),
    'Erntefresser': I('kakerlake', col=C('#8a7a3a'), shine=True), 'Hügelkönig': B(headtype='riese', skin=C('#c8a080'), col=RAGS, build='riesig', weapon='baum', crown=True),
    'Arenabestie': Q(BULL, col=C('#8a4a3a'), spikes=True, horns='gebogen'), 'Verwilderter Inquisitionsgolem': B(skin=C('#d8d0c0'), col=C('#d8d0c0'), col2=C('#d8d0c0'), material='eisen', build='riesig', crown=True, eye=C('#ffd27a'), weapon='hammer'),
    'Seelenfresser': SP('kapuze', col=C('#2a2438'), hood_col=C('#1e1a28'), eye=C('#8ad0ff'), item='sense', sz=1.3, element='schatten'),
    'Albtraumkönig': SP('kapuze', col=C('#3a2a5a'), hood_col=C('#2a1e40'), eye=C('#ff3a3a'), sz=1.4, element='schatten'),
    'Riesenspinnenkönigin': I('spinne', col=C('#2b2a30'), pattern=C('#c83a3a')), 'Schwarmkönigin': F('insekt', col=C('#5a4a2a'), stripes=C('#2b1e33'), span=.7, stinger=True),
    'Schildkrötenkoloss': Q(L=1.3, bh=.38, leg=.2, head=.14, snout=.08, ears=None, tail='kurz', shell=True, island=True, col=C('#6a7a5a'), shell_col=C('#6a6a4a'), bulk=1.5),
    'Gletscherelementar': SP('elementar', element='eis', sz=1.6, chunks=True), 'Vulkanelementar': SP('elementar', element='feuer', body_col=C('#4a3a3a'), sz=1.6, chunks=True),
}

# Rang S / SS: Sonderfälle
OVR.update({
    'Behemoth': Q(BULL, col=C('#6a5a4a'), horns='gebogen', bulk=1.8, L=1.3),
    'Leviathan': SN('wyrm', col=C('#2a4a6a'), fin=C('#5aa8c8'), L=2.4, th=.32, rear=.5, element='wasser'),
    'Uralter Krake': OC(col=C('#6a2a4a')), 'Lindwurm': D('drache', col=C('#5a6a3a'), nowings=True, breath='feuer'),
    'Schattenschleim': SL(col=C('#3a2a5a'), element='schatten', eye=C('#ff3a3a')), 'Phönix': F('vogel', col=C('#e8603a'), col2=C('#ffd27a'), element='feuer', crest=C('#ffd27a'), span=.9),
    'Bergtitan': B(skin=C('#8a8296'), col=C('#8a8296'), col2=C('#8a8296'), material='stein', build='riesig', headtype='riese'),
    'Frosttitan': B(headtype='riese', skin=C('#a8d0ee'), col=C('#e8f0f8'), build='riesig', weapon='keule', beard=C('#ffffff'), element='eis', material='eis'),
    'Feuertitan': B(headtype='riese', skin=C('#4a3a3a'), col=C('#4a3a3a'), col2=C('#4a3a3a'), build='riesig', material='lava', element='feuer', weapon='hammer'),
    'Sturmtitan': B(headtype='riese', skin=C('#7a8ac8'), col=C('#3a4a7a'), build='riesig', weapon='speer', beard=C('#e8ecf4'), element='blitz'),
    'Lichkönig': B(skeleton=True, headtype='schaedel', skin=C('#e8e0d0'), col=C('#2a1e40'), col2=C('#3a2a5a'), robe=True, weapon='stab', element='schatten', crown=True, cape=C('#5a1e2a')),
    'Vampirkönig': B(headtype='vampir', skin=C('#f0e8f0'), col=C('#1e1a28'), col2=C('#1e1a28'), cape=C('#a83a3a'), crown=True, eye=C('#ff3a3a'), element='blut', wings='fledermaus', wingspan=.6),
    'Todesdrache': D('drache', col=C('#3a3438'), bone=C('#e8e0d0'), eye=C('#8ad0ff'), wingcol=C('#2a2430'), breath='schatten', element='schatten'),
    'Hydrenmutter': D('hydra', col=C('#3a6a4a'), heads=12, nowings=True), 'Ur-Greif': Q(LION, col=C('#c8a060'), beak=C('#e0a040'), wings=True, wingspan=1.1, mane=False, bulk=1.4),
    'Roc-König': F('vogel', col=C('#6a4a34'), span=1.0, crest=C('#e0b048')), 'Sandwurm-Ahne': SN('sandwurm', col=C('#a8805a'), th=.46),
    'Salzfürst': B(skin=C('#e8e4dc'), col=C('#c8c0b0'), col2=C('#e8e4dc'), material='salz', crown=True, robe=True, weapon='stab', element='erde'),
    'Der Weiße Nebel': CL(col=C('#f0f0f8'), element='nebel', puffs=12), 'Das Schwarze Moor': SL('schleim', col=C('#2e2a22'), drip=True, element='gift', w=1.2),
    'Fiebermutter': B(headtype='kapuze', col=C('#6a7a3a'), col2=C('#4a5a2a'), robe=True, hood_col=C('#3a4a2a'), eye=C('#c8f07a'), element='gift', build='breit'),
    'Wurzelfürst': PL('baum', col=C('#2e5a2e'), trunk=C('#4a3222')), 'Feldherr der Verlorenen Königin': B(headtype='helm', col=C('#3a3446'), skin=C('#3a3446'), armor=True, acc=C('#5a5468'), cape=C('#7a1e2a'), weapon='schwert', plume=C('#c83a3a'), eye=C('#ff3a3a'), build='breit'),
    'Dornenkoloss': B(skin=C('#3a5a2a'), col=C('#3a5a2a'), col2=C('#3a5a2a'), material='dornen', build='riesig', eye=C('#e8d040')),
    'Blutkönig': B(headtype='vampir', skin=C('#e0c8c8'), col=C('#5a1e2a'), col2=C('#3a1420'), cape=C('#c83a3a'), crown=True, element='blut', build='breit'),
    'Erinnerungsfürst': SP('kapuze', col=C('#6a5a9a'), hood_col=C('#4a3a7a'), eye=C('#e0d0ff'), element='arkan', sz=1.4),
    'Zeitwächter von Valmor': B(skin=C('#c8b070'), col=C('#c8b070'), col2=C('#c8b070'), material='runen', build='riesig', crown=True, element='arkan'),
    'Bruchklang-Titan': SP('elementar', element='arkan', body_col=C('#a84aa8'), sz=1.7, chunks=True),
    'Kristallkoloss': B(skin=C('#8ad0e8'), col=C('#8ad0e8'), col2=C('#8ad0e8'), material='kristall', build='riesig', element='kristall'),
    'Gletscherwyrm': SN('wyrm', col=C('#c8e4f4'), L=2.2, th=.3, element='eis'), 'Lavakoloss': B(skin=C('#4a3a3a'), col=C('#4a3a3a'), col2=C('#4a3a3a'), material='lava', build='riesig', element='feuer'),
    'Himmelswal': FI('wal', col=C('#8aa0c8'), col2=C('#e8eef8'), sky=True, L=1.4, h=.45),
    'Donnerkönig': F('vogel', col=C('#1e2a6a'), element='blitz', span=1.0, crest=C('#fff07a')),
    'Spiegelfürst': B(skin=C('#d8e4f4'), col=C('#a8b8d8'), col2=C('#8a9ab8'), crown=True, element='arkan', weapon='schwert'),
    'Seelenernter': SP('kapuze', col=C('#2a2438'), hood_col=C('#1e1a28'), eye=C('#8ad0ff'), item='sense', sz=1.5, element='schatten'),
    'Albtraumfürst': SP('kapuze', col=C('#3a2a5a'), hood_col=C('#2a1e40'), eye=C('#ff3a3a'), sz=1.5, element='schatten'),
    'Geisterflotte': O('schiff', col=C('#3a3a4a'), sail=C('#8a98a8')), 'Riffkönig': B(skin=C('#d87a6a'), col=C('#d87a6a'), col2=C('#d87a6a'), material='koralle', build='riesig', crown=True, weapon='dreizack'),
    'Uralte Sphinx': Q(LION, col=C('#e0c070'), mane_col=C('#2a4a8a'), wings=True, wingcol=C('#e0c070'), bulk=1.4),
    'Klingensturm': O('klinge', col=C('#c8ccd8'), n=12, core=C('#8ad0ff')), 'Mimikfestung': O('burg', col=C('#9a9488')),
    'Stau-Koloss': SP('elementar', element='arkan', body_col=C('#e07ae0'), sz=1.7, chunks=True),
    'Der Drachenrest': D('drache', col=C('#2a2a3a'), bone=C('#c8d0e0'), eye=C('#8ad0ff'), wingcol=C('#1e1e2a'), breath='eis', element='schatten'),
    # SS
    'Glutvater': D('drache', col=C('#a83a2a'), breath='feuer', element='feuer', span=1.1), 'Frostmutter': D('drache', col=C('#a8d0ee'), col2=C('#f0f8ff'), breath='eis', element='eis', span=1.1),
    'Urdrache des Sturms': D('drache', col=C('#4a5a9a'), breath='blitz', element='blitz', span=1.1), 'Urdrache der Erde': D('drache', col=C('#7a6a4a'), nowings=True, breath='erde', bulk=1.5),
    'Urdrache des Wassers': D('drache', col=C('#2a6a9a'), breath='wasser', element='wasser', span=1.0), 'Urdrache des Windes': D('drache', col=C('#c8d8e8'), breath='wind', element='wind', span=1.2),
    'Urdrache der Wälder': D('drache', col=C('#3a6a3a'), breath='natur', element='natur', span=1.0, acc=C('#6a4a32')),
    'Nachtfrostdrache': D('drache', col=C('#2a2a4a'), col2=C('#8ab8e8'), breath='eis', element='schatten', eye=C('#8ad0ff'), span=1.1),
    'Weltenschlange': SN('wyrm', col=C('#2a5a5a'), fin=C('#5ac8a8'), L=2.6, th=.34, rear=.55), 'Uralter Leviathan': SN('wyrm', col=C('#1e3a5a'), fin=C('#5aa8c8'), L=2.6, th=.36, rear=.55, element='wasser'),
    'Ur-Behemoth': Q(BULL, col=C('#4a3e34'), horns='gebogen', bulk=2.0, L=1.35, spikes=True),
    'Der Erste Tote': B(skeleton=True, headtype='schaedel', skin=C('#d8d0c0'), col=C('#1e1a28'), col2=C('#2a2438'), robe=True, crown=True, crown_col=C('#8a8e9e'), weapon='sense', element='schatten', eye=C('#8ad0ff')),
    'Die Rote Nacht': B(headtype='vampir', skin=C('#f0e0e8'), col=C('#7a1e2a'), col2=C('#5a1420'), robe=True, hair=C('#2b1e33'), crown=True, cape=C('#c83a3a'), element='blut', wings='fledermaus', wingspan=.7),
    'Ur-Phönix': F('vogel', col=C('#ff7a3a'), col2=C('#fff07a'), element='feuer', crest=C('#fff4c8'), span=1.1),
    'Schattenschleim-Mutter': SL(col=C('#2a1e40'), element='schatten', eye=C('#ff3a3a'), w=1.2, h=.8),
    'Dornenwyrm': SN('wyrm', col=C('#2e4a2a'), spikes=True, acc=C('#c8b898'), L=2.3, th=.3), 'Blutflut': SL(col=C('#8a1e2a'), element='blut', drip=True, w=1.3, h=.7),
    'Erinnerungsschlund': MW(col=C('#6a5a9a'), element='arkan', core=C('#b8a0ff')), 'Zeitlose Bestie': Q(LION, col=C('#a8a090'), element='arkan', mane_col=C('#e0d0ff'), bulk=1.5),
    'Bruchklang-Ur': SP('elementar', element='arkan', body_col=C('#4a4aa8'), sz=1.9, chunks=True),
    'Himmelsfresser': MW(col=C('#3a3a5a'), element='schatten', alt=.6, eyes=C('#ffd27a')),
    'Der Gefallene': B(skin=C('#e8e0d0'), col=C('#e8e8f0'), col2=C('#c8c8d8'), wings='vogel', wingcol=C('#f0f0f8'), wingspan=.8, hair=C('#e0b048'), weapon='schwert', weapon_col=C('#ffd27a'), element='licht', build='breit'),
    'Tiefenkönig': B(skin=C('#3a3446'), col=C('#2a2438'), col2=C('#1e1a28'), crown=True, eye=C('#8ad0ff'), build='riesig', claws=True, element='schatten'),
    'Nachtklüfte-Wyrm': SN('wyrm', col=C('#2a2438'), L=2.3, th=.3, eye=C('#c83a3a'), element='schatten'),
    'Höllentitan': B(skin=C('#8a2a2a'), col=C('#2b2a30'), build='riesig', horns=True, wings='fledermaus', wingspan=.8, weapon='axt', element='feuer', tail='duenn', tail_col=C('#8a2a2a')),
    'Dämonenkoloss': B(skin=C('#4a3a3a'), col=C('#4a3a3a'), col2=C('#4a3a3a'), material='eisen', build='riesig', horns=True, eye=C('#ff9a3c'), element='feuer'),
    'Hydrenkönig': D('hydra', col=C('#2a4a3a'), heads=15, nowings=True, crown=True), 'Seelenschlund': MW(col=C('#2a2438'), element='schatten', core=C('#8ad0ff')),
    'Die Fäule': CL(col=C('#6a6a3a'), element='gift', puffs=11, eyes=C('#e8d040')), 'Ewiger Sandsturm': CL(col=C('#c8a070'), element='erde', swirl=True, puffs=12, eyes=C('#ffd27a')),
    'Salzmeer-Titan': B(skin=C('#f0ece4'), col=C('#f0ece4'), col2=C('#f0ece4'), material='salz', build='riesig', headtype='riese', crown=True),
    'Gletschertitan': B(skin=C('#a8d0ee'), col=C('#a8d0ee'), col2=C('#a8d0ee'), material='eis', build='riesig', headtype='riese', element='eis'),
    'Der Erwachende': B(skin=C('#3a3030'), col=C('#3a3030'), col2=C('#3a3030'), material='lava', build='riesig', headtype='riese', horns=True, element='feuer'),
    'Der Ewige Blitz': SP('elementar', element='blitz', sz=1.9), 'Das Weiße Nichts': CL(col=C('#ffffff'), element='nebel', puffs=12),
    'Fieberkönigin': B(headtype='kapuze', col=C('#6a7a3a'), col2=C('#4a5a2a'), robe=True, hood_col=C('#3a4a2a'), eye=C('#c8f07a'), crown=True, element='gift', wings='insekt', wingspan=.6),
    'Schwarmgott': SW('insekt', col=C('#3a3438'), n=60, core=C('#5a4a2a')), 'Krakenkönig': OC(col=C('#5a1e3a'), element='wasser'),
    'Geisterkaiser': SP('kapuze', col=C('#a8c8d8'), hood_col=C('#4a6a7a'), eye=C('#8ad0ff'), sz=1.6, element='wasser'),
    'Wandernder Schlund': O('burg', col=C('#6a5a5a')), 'Spiegelgott': B(skin=C('#e8f0ff'), col=C('#c8d8f0'), col2=C('#a8b8d8'), crown=True, wings='vogel', wingcol=C('#e8f0ff'), element='arkan', build='breit', weapon='schwert'),
    'Der Tausendklingen': O('klinge', col=C('#b8bcc8'), n=20, core=C('#c83a3a')), 'Der Große Goblin': SW('goblin', col=GOBLIN_SKIN, n=40),
    'Die Mana-Flut': CL(col=C('#b8a0ff'), element='arkan', swirl=True, puffs=12, eyes=C('#ffffff')),
    'Himmelswal-Mutter': FI('wal', col=C('#7a90c0'), col2=C('#e8eef8'), sky=True, L=1.5, h=.5),
    'Erdenfresser': SN('sandwurm', col=C('#6a5a4a'), dirt=C('#6a5040'), th=.5), 'Der Rostlose': SN('wurm', col=C('#a85a3a'), th=.4, L=2.2),
    'Glutwurm-Ahne': SN('wurm', col=C('#3a2a2a'), th=.42, L=2.3, element='feuer'), 'Urschleim': SL(col=C('#5ab85a'), w=1.4, h=.9, inside=C('#e8e0d0')),
    'Weltenbaum-Wächter': PL('baum', col=C('#4a8a5a'), trunk=C('#6a4a32'), flower=C('#f0d0f0')),
})

# ---------------------------------------------------------------- Allgemeine Regeln (falls kein Sonderfall)
RULES = [
    (r'erddrache', lambda e: D('drache', nowings=True, bulk=1.3)), (r'drache', lambda e: D('drache')), (r'schleim', lambda e: SL()),
]

SIZE_MUL = [(r'riesen|groß|koloss|titan|mutter|könig|fürst|ahne|ur-|uralt', 1.2), (r'junge|klein|welpe|ling$', .85),
            (r'maus|floh|zecke|milbe|made|egel', .8)]
TYP_MUL = {'schwarm': 1.1, 'schleim': .9, 'insekt': 1.0, 'objekt': 1.0, 'schnecke': .9, 'kroete': .9}

def build_spec(entry):
    name = entry['name']
    text = f"{name} {entry['merkmal']} {entry['lebensraum']}"
    sp = dict(OVR.get(name) or {})
    if not sp:
        for pat, fn in RULES:
            if re.search(pat, name.lower()): sp = fn(entry); break
    if not sp:
        raise KeyError(name)
    sp['name'] = name; sp['rang'] = entry['rang']
    if 'col' not in sp:
        el = sp.get('element') or element_of(text)
        sp['col'] = base_col(name) or (ELEM_TINT.get(el) if el else C('#8a8296'))
    if sp['typ'] == 'drache' and not sp.get('breath') and sp.get('kind') != 'hydra':
        el = element_of(text)
        if el in ('feuer', 'eis', 'blitz', 'gift', 'schatten', 'wasser', 'natur', 'wind', 'erde', 'kristall'): sp['breath'] = el
    if 'element' not in sp and sp['typ'] in ('wolke', 'geist', 'schleim', 'schlund'):
        el = element_of(text)
        if el: sp['element'] = el
    px = RANK_PX[entry['rang']] * TYP_MUL.get(sp['typ'], 1.0)
    for pat, m in SIZE_MUL:
        if re.search(pat, name.lower()): px *= m; break
    if sp['typ'] == 'zweibeiner': px *= 1.3 if sp.get('build') == 'riesig' else 1.1
    if sp['typ'] == 'pflanze' and sp.get('kind') == 'baum': px *= 1.25
    if sp['typ'] == 'wolke': px *= 1.2
    sp['px'] = int(round(px))
    death = {'schatten': C('#8a6ab8'), 'feuer': C('#ff9a3c'), 'eis': C('#e8f6ff'), 'gift': C('#c8f07a'), 'blut': C('#ff6a6a'),
             'arkan': C('#e0d0ff'), 'blitz': C('#fff07a')}
    sp['death_col'] = death.get(sp.get('element') or element_of(text), C('#d8d0e8'))
    return sp

def all_specs():
    data = json.load(open(os.path.join(HERE, 'bestiarium.json'), encoding='utf-8'))
    out, missing = [], []
    for e in data:
        try: out.append((e, build_spec(e)))
        except KeyError: missing.append(e['name'])
    return out, missing

if __name__ == '__main__':
    specs, missing = all_specs()
    import collections
    print(len(specs), 'zugeordnet;', len(missing), 'fehlen')
    print(collections.Counter(s['typ'] for _, s in specs))
    print('FEHLEN:', missing)
