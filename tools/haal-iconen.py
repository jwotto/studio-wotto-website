#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Haalt de gebruikte Phosphor-iconen op en zet ze in tools/iconen.json.

    python tools/haal-iconen.py

DIT IS EEN KLUSJE OP AANVRAAG, geen onderdeel van build.py. Draai het als je
een nieuw icoon in een pagina zet. build-inbakken.py waarschuwt je trouwens als
hij een icoon tegenkomt dat hier nog niet in staat, dus je kunt het niet vergeten.

WAAROM
De iconen kwamen van een stylesheet op unpkg.com die een compleet
iconenlettertype meebracht: ruim vijftienhonderd iconen om er eenendertig te
kunnen tekenen. Die stylesheet stond in de <head> en blokkeerde dus het tekenen
van de pagina, net als de lettertypen.

Nu staan alleen de iconen die je echt gebruikt als SVG in de pagina zelf. Geen
vreemd domein, geen wachttijd, geen lettertype dat eerst binnen moet zijn
voordat je een icoontje ziet.

Phosphor is van Phosphor Icons en staat onder de MIT-licentie, dus meenemen mag.
De licentietekst komt naast de iconen te staan in fonts/PHOSPHOR-LICENSE.txt.

WELKE ICONEN?
Dit script zoekt ze zelf op in de HTML, de partials en js/site.js. Het zoekt
twee vormen: de bron-notatie class="ph-bold ph-naam" en de ingebakken vorm
<use href="#ph-naam">. Zo blijft de lijst automatisch kloppen.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent.parent
BRON = "https://unpkg.com/@phosphor-icons/core@2.1.1/assets/bold/%s-bold.svg"
LICENTIE = "https://unpkg.com/@phosphor-icons/core@2.1.1/LICENSE"

NEGEER_MAPPEN = {"tools", ".git", ".astro", "node_modules", "oude blogs en pagina's"}

# JavaScript zet de "Te huur"-chip zelf in elkaar, met een icoon dat dus nergens
# in de HTML staat. Die moet er altijd bij.
# play staat in de namaakspeler die build-inbakken.py maakt, dus ook niet in de
# bron te vinden.
ALTIJD = {"truck", "play"}


def gebruikte_iconen() -> set:
    namen = set(ALTIJD)
    patroon = re.compile(r"(?:ph-bold\s+ph-|#ph-)([a-z0-9][a-z0-9-]*)")
    for pad in list(BASE.rglob("*.html")) + list(BASE.rglob("*.js")):
        if any(x in pad.relative_to(BASE).parts for x in NEGEER_MAPPEN):
            continue
        namen |= set(patroon.findall(pad.read_text(encoding="utf-8", errors="ignore")))
    namen.discard("bold")
    return namen


def main():
    namen = sorted(gebruikte_iconen())
    print("%d icoon/iconen gevonden in de site." % len(namen))

    iconen, mislukt = {}, []
    for naam in namen:
        try:
            svg = urllib.request.urlopen(BRON % naam, timeout=25).read().decode("utf-8")
        except urllib.error.HTTPError:
            mislukt.append(naam)
            continue
        m = re.search(r"<svg[^>]*viewBox=\"([^\"]+)\"[^>]*>(.*)</svg>", svg, re.S)
        if not m:
            mislukt.append(naam)
            continue
        # fill="currentColor" staat op de buitenste <svg> en zetten we straks in
        # de CSS, dus die hoeft hier niet mee.
        iconen[naam] = {"viewBox": m.group(1), "body": m.group(2).strip()}
        print("  %-24s %4d bytes" % (naam, len(iconen[naam]["body"])))

    if mislukt:
        print("\n!! niet gevonden bij Phosphor: %s" % ", ".join(mislukt))
        print("   Tikfout in de naam? Kijk op https://phosphoricons.com")

    if not iconen:
        return 1

    (BASE / "tools" / "iconen.json").write_text(
        json.dumps(iconen, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    totaal = sum(len(v["body"]) for v in iconen.values())
    print("\ntools/iconen.json geschreven: %d iconen, %.1f KB aan padgegevens."
          % (len(iconen), totaal / 1024))

    try:
        tekst = urllib.request.urlopen(LICENTIE, timeout=25).read().decode("utf-8")
        (BASE / "fonts").mkdir(exist_ok=True)
        (BASE / "fonts" / "PHOSPHOR-LICENSE.txt").write_text(tekst, encoding="utf-8")
        print("fonts/PHOSPHOR-LICENSE.txt bijgewerkt.")
    except Exception as e:
        print("licentie ophalen mislukt (%s), doe dat met de hand." % e)

    return 1 if mislukt else 0


if __name__ == "__main__":
    sys.exit(main())
