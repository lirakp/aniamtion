# Cosy Pixel-Art Assets – Seitenansicht-Plattformer

Alle Grafiken und Animationen für das Spiel: prozedural mit Python (Pillow) erzeugt, im cosy Nacht-Dorf-Stil.
Blickrichtung in allen Seitenansichten ist **rechts** – für links horizontal spiegeln.
Kontur-Farbe überall `#2b1e33`. Alle Bilder sind PNG mit Transparenz; Sprite-Sheets sind Raster aus gleich großen Zellen.

**Wichtig für die Einbindung:** Zu (fast) jeder Gruppe gibt es eine JSON-Datei mit Zellgröße, Frame-Anzahl,
Reihenfolge der Animationen, FPS und Bodenpunkt. Immer zuerst die JSON lesen.

## Übersicht

| Bereich | Ordner | Beschreibung | Metadaten |
|---|---|---|---|
| **Spieler (groß)** | `characters/held/` | 48x48-Zellen, ~40 px, 14 Völker × Tunika/Rüstung, 17 Animationen (stehen, rennen, Sprung, fallen, landen, Dash, Wand, Angriffe vorne/oben/unten, Treffer, Tod, Heilen, ducken) | `characters/held/held.json` |
| Völker (klein) Plattformer | `characters/voelker/plattformer/` | 18x26-Figuren, Plattformer-Animationen | `plattformer.json` |
| Völker laufen/idle/Kampf/Magie | `characters/voelker/`, `characters/voelker/kampf/` | 4 Richtungen bzw. Seitenansicht | – |
| Dorfbewohner bei der Arbeit | `characters/arbeit/` | 10 Arbeitsschleifen, 8 Frames, 48x34 | `arbeit.json` |
| Dorf-Figuren (Vorlagen) | `characters/*.png`, `walk/`, `idle/` | Schmied, Bäckerin, Oma, Kind … | – |
| **Monster** | `monster/sprites/<Rang>/` | alle 600 Monster aus dem Bestiarium, Seitenansicht: idle, move, attack, hurt, death | `monster/sprites/monster.json` |
| **Bosse** | `monster/sprites/bosse/` | 12 SS-Bosse groß: idle, bewegen, angriff_nah, angriff_spezial, bruellen (Phasenwechsel), benommen, treffer, tod | `bosse.json` |
| Gebäude | `buildings/` | Tag/Nacht, animiert (`anim/`), Türen (`doors/`) | `doors/tueren.json` |
| Portal | `objects/portal/` | Stehendes Oval, halbtransparent, 4 Farben: öffnen, offen (Schleife), Durchgang, schließen | `portal.json` |
| Objekte & Licht | `objects/` | Wasserfall, Dungeon-Tür, Lagerfeuer, Laternen, Fackeln, Lichtkreise | `objekte.json`, `licht/licht.json` |
| Requisiten | `props/` | Dorf-Requisiten | – |
| Level / Tiles | `level/` | Terrain-Autotiles (Wang 4x4), Rückwände, Schrägen, Plattformen, Leiter, Stacheln, Parallax-Ebenen | `level.json` |
| Tag-Nacht | `level/tageszeit/` | 4 Himmel + Tönung je Stunde | `tageszeit.json` |
| Umgebungs-Partikel | `level/partikel/` | 13 loopende Overlays 320x180 (Regen, Schnee, Glühwürmchen, Nebel …) | `partikel.json` |
| Dungeon | `dungeon/` | Fallen, Truhen, Details, Geister; `fallen_seite/` = Fallen in Seitenansicht | `dungeon.json`, `fallen_seite.json` |
| Sammel-Items | `welt/sammeln/` | 22 Fundstücke (Beeren, Weizen, Pilze, Kräuter, Erze, Kristall, Eier, Honig …): idle, ernten, leer, nachwachsen + 16x16-Icons | `sammeln.json` |
| Welt-Details & Gags | `welt/` | Brunnen-Münze, Bäume, Blitz, wütender Baum, Gags … | `welt.json` |
| Magie | `effects/magie/`, `zauber/` | Element-Effekte, Bruchklang, Mehrklang; alle 270 Zauber | `effekte.json`, `zauber/sprites/zauber.json` |
| UI | `ui/` | Herzen, Mana, Rangabzeichen, Schadenszahlen, 9-Slice-Rahmen, Knöpfe, Banner | `ui.json` |
| Übergänge | `ui/uebergaenge/` | 6 Szenenübergänge, 12 Masken à 320x180 | `uebergaenge.json` |
| Kartensymbole | `ui/karte/` | 24 Symbole 12x12 | `karte.json` |
| Gegenstands-Icons | `icons/` | ~130 Icons 16x16 (Waffen/Rüstung je Rang D–SS, Tränke, Beute …) | `icons.json` |
| Statuseffekte | `status/` | 15 Effekte: 9x9-Icons + Overlays 32x32 + Tönung | `status.json` |
| Dialog-Porträts | `portraits/` | 40x40, 14 Völker × 2 Outfits, 6 Ausdrücke × (zu, spricht, blinzeln) | `portraits.json` |
| Vorschauen | `preview_*.gif/png` | Übersichtsbilder aller Gruppen (nicht fürs Spiel) | – |
| Alt (Draufsicht) | `_draufsicht/` | frühere Top-down-Tiles, nicht mehr verwendet | – |

## Rang-Farben
D grau `#9a94a8` · C grün `#6ab06a` · B blau `#5a9ad8` · A violett `#b880ff` · S gold `#e0b048` · SS rot `#e0443a`

## Neu erzeugen
Voraussetzung: Python 3 + Pillow (`pip install pillow`). Jedes Skript erzeugt seine Gruppe neu, z. B.:

```bash
python3 hero.py        # großer Spieler
python3 ui.py          # UI
cd monster && python3 build.py && python3 boss.py   # Monster + Bosse
```

Weitere Skripte: `generate.py` (Basis/Gebäude), `walk.py`, `idle.py`, `shops.py`, `animate.py`, `doors.py`, `objects.py`, `lights.py`,
`races.py`, `combat.py`, `platformer.py`, `magic.py`, `zauber/spells.py`, `dungeon.py`, `world.py`, `gags.py`, `sidetiles.py`,
`sidetraps.py`, `portal.py`, `sammeln.py`, `icons.py`, `status.py`, `portraits.py`, `work.py`, `extras.py`, `particles.py`.
