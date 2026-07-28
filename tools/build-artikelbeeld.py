#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zet naast elke artikelfoto een lichtere WebP, in dezelfde afmetingen.

    python tools/build-artikelbeeld.py

WAT DIT WEL EN NIET DOET
Het verkleint niets. De foto houdt precies dezelfde afmetingen en dus dezelfde
verhouding; alleen de manier van comprimeren verandert. WebP haalt bij hetzelfde
beeld ongeveer een derde van de bestandsgrootte weg. Over de 86 artikelfoto's
gaat dat van 15,1 MB naar 9,5 MB.

Dat is precies de afspraak: op een project- of blogpagina wil je het grote beeld
zien, niet een uitgeklede versie. Dit maakt het beeld niet kleiner, alleen het
bestand.

WAAROM HET UITMAAKT
Op de projectpagina's is de bovenste foto meestal het grootste ding in beeld, en
daar meet Google je LCP aan af. Op side-quest-rave was dat een JPEG van 206 KB.
Hoe eerder die binnen is, hoe eerder de pagina "staat".

De JPEG's blijven gewoon staan. Ze zijn het origineel, ze worden nog gebruikt
als deel-thumbnail (og:image) en in de structured data, en je kunt altijd terug.
tools/build-inbakken.py laat de <img> in de pagina naar de WebP wijzen als die
bestaat.

Alleen nieuwe of gewijzigde foto's worden verwerkt, dus opnieuw draaien is snel.
"""
import json
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
BRON = (".jpg", ".jpeg", ".png")
KWALITEIT = 82


def main():
    try:
        from PIL import Image
    except ImportError:
        print("!! Pillow ontbreekt: pip install pillow")
        return 1

    items = json.loads((BASE / "content.json").read_text(encoding="utf-8"))
    if items and isinstance(items[0], str):
        print("!! content.json bevat nog alleen mapnamen; draai eerst build-manifest.py")
        return 1

    gemaakt = overgeslagen = 0
    voor = na = 0.0

    for item in items:
        for bron in sorted((BASE / "werk" / item["slug"]).iterdir()):
            if bron.suffix.lower() not in BRON:
                continue
            # De kaartversies zijn al WebP en hebben hier niets te zoeken.
            if bron.stem.endswith("-kaart"):
                continue
            doel = bron.with_suffix(".webp")
            if doel.exists() and doel.stat().st_mtime >= bron.stat().st_mtime:
                overgeslagen += 1
                continue
            try:
                with Image.open(bron) as im:
                    if im.mode not in ("RGB", "RGBA"):
                        im = im.convert("RGB")
                    # Geen resize: de afmetingen blijven exact gelijk.
                    im.save(doel, "WEBP", quality=KWALITEIT, method=6)
            except Exception as e:
                print("  !! %s: %s" % (bron.name, e))
                continue

            kb0 = bron.stat().st_size / 1024
            kb1 = doel.stat().st_size / 1024
            # Groter geworden? Dan was de JPEG al beter en gooien we de WebP weg,
            # anders maken we de pagina zwaarder in plaats van lichter.
            if kb1 >= kb0:
                doel.unlink()
                overgeslagen += 1
                continue
            voor += kb0
            na += kb1
            gemaakt += 1

    print("artikelbeeld: %d nieuw, %d al bij of niet de moeite." % (gemaakt, overgeslagen))
    if gemaakt:
        print("Samen %.1f MB in plaats van %.1f MB, bij dezelfde afmetingen."
              % (na / 1024, voor / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
