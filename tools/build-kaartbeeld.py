#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maakt van elke coverfoto een lichte versie op kaartformaat.

    python tools/build-kaartbeeld.py

WAAROM
Op de homepage en de overzichtspagina's staan de covers als kaartje van een paar
honderd pixels breed. Ze werden daar geladen als het volledige bestand van 1600
pixels, en dat kost 250 tot 500 KB per stuk. Bij elf kaarten op een pagina loopt
dat hard op: Lighthouse rekende voor dat er zo'n 2 MB te besparen was. Op een
trage telefoonverbinding is dat het verschil tussen wachten en niet wachten.

Naast elke cover komt daarom een tweede bestand:

    side-quest-rave.jpg        <- het origineel, voor de projectpagina zelf
    side-quest-rave-kaart.webp <- de lichte versie, alleen voor de kaartjes

tools/build-inbakken.py pakt automatisch die -kaart.webp als hij bestaat.

DE VERHOUDING BLIJFT ONGEMOEID
Er wordt alleen verkleind, nooit gesneden. Een foto houdt zijn eigen verhouding,
ook als hij op de kaart in een vierkant vakje valt: dat vierkant maakt de CSS
met object-fit, en dat kun je altijd terugdraaien. Zou dit script snijden, dan
was de weggegooide rand voorgoed weg.

Alleen nieuwe of gewijzigde foto's worden verwerkt, dus opnieuw draaien is snel.
"""
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent

# Kaarten zijn op een grote schermbreedte ongeveer 380 px breed. Het dubbele
# daarvan is genoeg voor een scherm met dubbele pixeldichtheid, en meer heeft
# geen zichtbaar effect.
MAX_BREED = 800
KWALITEIT = 78


def main():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("!! Pillow ontbreekt: pip install pillow")
        return 1

    items = json.loads((BASE / "content.json").read_text(encoding="utf-8"))
    if items and isinstance(items[0], str):
        print("!! content.json bevat nog alleen mapnamen; draai eerst build-manifest.py")
        return 1

    gemaakt = overgeslagen = 0
    bespaard = 0

    for item in items:
        bron = BASE / "werk" / item["slug"] / item["cover"]
        if not bron.exists():
            continue
        doel = bron.with_name(bron.stem + "-kaart.webp")

        # Al up-to-date? Dan alleen de maten noteren en door. Zo blijft opnieuw
        # bouwen snel, maar heeft build-inbakken.py ze toch altijd bij de hand.
        if doel.exists() and doel.stat().st_mtime >= bron.stat().st_mtime:
            with Image.open(doel) as im:
                item["kaartmaat"] = list(im.size)
            overgeslagen += 1
            continue

        try:
            with Image.open(bron) as im:
                # Draaiing uit de camera meteen goed zetten, anders staat de
                # kaart op zijn kant terwijl het origineel rechtop lijkt.
                im = ImageOps.exif_transpose(im)
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGB")
                # thumbnail() verkleint binnen een kader en houdt de verhouding
                # dus altijd intact. Kleiner dan het kader blijft ongemoeid.
                im.thumbnail((MAX_BREED, MAX_BREED), Image.LANCZOS)
                im.save(doel, "WEBP", quality=KWALITEIT, method=6)
                # De maat gaat mee naar content.json, zodat build-inbakken.py er
                # width en height op de kaart van kan zetten zonder zelf een
                # afbeelding te hoeven openen. Zonder die twee weet de browser
                # pas hoe hoog de kaart wordt als de foto binnen is.
                item["kaartmaat"] = list(im.size)
        except Exception as e:
            print("  !! %s: %s" % (bron.name, e))
            continue

        winst = (bron.stat().st_size - doel.stat().st_size) / 1024
        bespaard += winst
        gemaakt += 1
        print("  %-46s %5.0f KB -> %4.0f KB" % (
            item["slug"] + "/" + doel.name,
            bron.stat().st_size / 1024, doel.stat().st_size / 1024))

    # De maten terugschrijven naar content.json. build-manifest.py heeft dat
    # bestand net gemaakt; wij vullen er alleen een veld bij aan.
    (BASE / "content.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\nkaartbeeld: %d nieuw, %d al bij. Samen %.1f MB lichter op de kaartjes."
          % (gemaakt, overgeslagen, bespaard / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
