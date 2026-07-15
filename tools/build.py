#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Draait alle bouwstappen, in de juiste volgorde.

    python tools/build.py

Gebruik dit in plaats van de losse scripts. De volgorde is namelijk niet vrij:

  1. build-manifest.py     bepaalt welke items bestaan (content.json)
  2. build-onderwerpen.py  leest content.json en SCHRIJFT de onderwerp-pagina's
                           helemaal opnieuw uit zijn sjabloon
  3. build-seo.py          zet de structured data in ELKE pagina, dus ook in
                           de pagina's die stap 2 net heeft gemaakt

Draai je 2 na 3, dan overschrijft stap 2 de structured data van stap 3 en staan
je onderwerp-pagina's er zonder. Dat is precies één keer gebeurd, en daarom
bestaat dit bestand.
"""
import pathlib, subprocess, sys

TOOLS = pathlib.Path(__file__).resolve().parent
STAPPEN = ["build-manifest.py", "build-onderwerpen.py", "build-seo.py"]

for i, stap in enumerate(STAPPEN, 1):
    print("\n=== %d/%d  %s" % (i, len(STAPPEN), stap))
    r = subprocess.run([sys.executable, str(TOOLS / stap)], cwd=str(TOOLS.parent))
    if r.returncode != 0:
        print("\n!! %s ging mis, gestopt." % stap)
        sys.exit(r.returncode)

print("\nKlaar. Bekijken met Live Server.")
