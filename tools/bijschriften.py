#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maakt bijschriften.txt: een werkblad met per foto de alt en de cap.

    python tools/bijschriften.py

De HTML is de bron, niet dit bestand. Draai dit als je de bijschriften wilt
nakijken of aanpassen: het leest de actuele teksten uit de site. Pas daarna
bijschriften.txt aan en laat Claude het terugzetten in de foto's. Daarna mag
het bestand weer weg, het is altijd opnieuw te maken.

  alt = beschrijving voor Google en schermlezers. Altijd, dit maakt vindbaar.
  cap = kort zichtbaar bijschrift bij het aanklikken. Optioneel.
"""
import json, pathlib, re, html, sys

SITE = pathlib.Path(__file__).resolve().parent.parent
slugs = json.load(open(SITE / "content.json", encoding="utf-8"))

L = [
    "BIJSCHRIFTEN PER AFBEELDING EN VIDEO",
    "=" * 70,
    "",
    "Werkblad, gemaakt door tools/bijschriften.py uit de site zelf. Pas de tekst",
    "na 'alt:' of 'cap:' aan, laat de labels en het [foto]/[video]-regeltje staan.",
    "Klaar? Laat Claude het terugzetten. Daarna mag dit bestand weg, het is altijd",
    "opnieuw te maken.",
    "",
    "  alt = beschrijving voor Google en schermlezers. ALTIJD invullen.",
    "  cap = kort zichtbaar bijschrift bij het aanklikken. Optioneel, leeg = alt.",
    "",
    "=" * 70,
]

for slug in slugs:
    h = (SITE / "werk" / slug / "index.html").read_text(encoding="utf-8")
    body = re.search(r'<div class="article-body">.*?</article>', h, re.S)
    if not body:
        continue
    b = body.group(0)

    regels = []
    for m in re.finditer(r"<img[^>]*>", b):
        tag = m.group(0)
        src = (re.search(r'src="([^"]*)"', tag) or [None, ""])[1]
        if not src or src.startswith("http"):
            continue
        alt = html.unescape((re.search(r'alt="([^"]*)"', tag) or [None, ""])[1])
        cap = html.unescape((re.search(r'data-cap="([^"]*)"', tag) or [None, ""])[1])
        regels.append(("  [foto ]  " + src, "    alt: " + alt, "    cap: " + cap))
    for m in re.finditer(r'<video[^>]*src="([^"]+)"[^>]*>\s*</video>\s*<figcaption>(.*?)</figcaption>', b, re.S):
        cap = html.unescape(re.sub(r"\s+", " ", m.group(2)).strip())
        regels.append(("  [video]  " + m.group(1), None, "    cap: " + cap))

    if not regels:
        continue
    L.append("")
    L.append("### %s   (/werk/%s/)" % (slug, slug))
    for r in regels:
        for onderdeel in r:
            if onderdeel is not None:
                L.append(onderdeel)
        L.append("")

(SITE / "bijschriften.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
print("bijschriften.txt gemaakt: %d afbeeldingen/video's" %
      len([x for x in L if x.startswith("  [")]))
