#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Draait alle bouwstappen, in de juiste volgorde.

    python tools/build.py

Gebruik dit in plaats van de losse scripts. De volgorde is namelijk niet vrij:

  1. build-manifest.py     bepaalt welke items bestaan (content.json)
  2. build-galerij.py      verkleint te grote foto's en zet de galerij onder een
                           item, dus dit moet voor stap 4 (die de foto's in de
                           structured data zet)
  3. build-onderwerpen.py  leest content.json en SCHRIJFT de onderwerp-pagina's
                           helemaal opnieuw uit zijn sjabloon
  4. build-seo.py          zet de structured data in ELKE pagina, dus ook in
                           de pagina's die stap 3 net heeft gemaakt

Draai je 3 na 4, dan overschrijft stap 3 de structured data van stap 4 en staan
je onderwerp-pagina's er zonder. Dat is precies één keer gebeurd, en daarom
bestaat dit bestand.
"""
import pathlib, subprocess, sys

TOOLS = pathlib.Path(__file__).resolve().parent
STAPPEN = ["build-manifest.py", "build-galerij.py", "build-onderwerpen.py", "build-seo.py"]

for i, stap in enumerate(STAPPEN, 1):
    print("\n=== %d/%d  %s" % (i, len(STAPPEN), stap))
    r = subprocess.run([sys.executable, str(TOOLS / stap)], cwd=str(TOOLS.parent))
    if r.returncode != 0:
        print("\n!! %s ging mis, gestopt." % stap)
        sys.exit(r.returncode)

print("\nKlaar. Bekijken met Live Server.")
