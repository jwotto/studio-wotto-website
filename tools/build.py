#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Draait alle bouwstappen, in de juiste volgorde.

    python tools/build.py

Gebruik dit in plaats van de losse scripts. De volgorde is namelijk niet vrij:

  1. build-manifest.py     bepaalt welke items bestaan EN wat hun kenmerken
                           zijn (content.json)
  2. build-galerij.py      verkleint te grote foto's en zet de galerij onder een
                           item, dus dit moet voor stap 4 (die de foto's in de
                           structured data zet)
  3. build-onderwerpen.py  leest content.json en SCHRIJFT de onderwerp-pagina's
                           helemaal opnieuw uit zijn sjabloon
  4. build-seo.py          zet de structured data in ELKE pagina, dus ook in
                           de pagina's die stap 3 net heeft gemaakt
  5. build-kaartbeeld.py   maakt van elke coverfoto een lichte WebP op
                           kaartformaat
  6. build-kaartfilm.py    maakt van elk kaartfilmpje een lichte mp4. Alleen de
                           uitschieters worden echt aangepakt
  7. build-artikelbeeld.py zet naast elke artikelfoto een lichtere WebP, in
                           dezelfde afmetingen
  8. build-llms.py         schrijft llms.txt: een wegwijzer door de site voor
                           AI-assistenten, uit content.json en build-seo.py
  9. build-inbakken.py     zet de header, de footer en de kaartjes in de HTML.
                           Moet als LAATSTE bouwstap, want stap 3 schrijft
                           pagina's helemaal opnieuw en zou het inbakwerk dus
                           weggooien.

Daarna volgt nog check-snelheid.py. Dat is geen bouwstap maar een controle: hij
kijkt het resultaat na op de regels uit snelheid.md en vertelt wat er opvalt.
Hij blokkeert nooit iets, want of een grote foto de moeite waard is bepaal jij.

Draai je 3 na 4, dan overschrijft stap 3 de structured data van stap 4 en staan
je onderwerp-pagina's er zonder. Dat is precies één keer gebeurd, en daarom
bestaat dit bestand.
"""
import pathlib, subprocess, sys

TOOLS = pathlib.Path(__file__).resolve().parent
STAPPEN = ["build-manifest.py", "build-galerij.py", "build-onderwerpen.py",
           "build-seo.py", "build-kaartbeeld.py", "build-kaartfilm.py",
           "build-artikelbeeld.py", "build-llms.py",
           "build-inbakken.py"]

# flush=True bij elke kop. Zonder dat houdt Python onze eigen regels vast in een
# buffer terwijl de deelscripts rechtstreeks naar het scherm schrijven, en komt
# de uitvoer door elkaar te staan: eerst het resultaat, dan pas de kop erboven.
for i, stap in enumerate(STAPPEN, 1):
    print("\n=== %d/%d  %s" % (i, len(STAPPEN), stap), flush=True)
    r = subprocess.run([sys.executable, str(TOOLS / stap)], cwd=str(TOOLS.parent))
    if r.returncode != 0:
        print("\n!! %s ging mis, gestopt." % stap)
        sys.exit(r.returncode)

# De controle staat bewust buiten de lus: hij hoort bij het resultaat, niet bij
# het bouwen, en zijn uitkomst mag de bouw nooit laten mislukken.
print("\n=== controle  check-snelheid.py", flush=True)
subprocess.run([sys.executable, str(TOOLS / "check-snelheid.py")], cwd=str(TOOLS.parent))

print("\nKlaar. Bekijken met Live Server.")
