#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schrijft llms.txt: een wegwijzer door de site voor AI-assistenten.

    python tools/build-llms.py   (of gewoon: python tools/build.py)

WAT IS DIT
llms.txt is een voorstel voor een bestand op https://studiowotto.com/llms.txt
waarin je in gewone taal uitlegt wat je site is en welke pagina's waarover gaan.
Het idee komt van llmstxt.org en is de tegenhanger van robots.txt: die zegt wat
een bot mag, dit zegt wat er te halen valt.

WEES EERLIJK OVER WAT HET OPLEVERT
Geen enkele grote aanbieder heeft toegezegd dit bestand te gebruiken. Het staat
er omdat het niets kost en omdat het klopt, niet omdat het gegarandeerd werkt.
Wat wél al werkt voor AI-assistenten is de rest: de pagina's staan compleet in
de HTML (die lezers draaien vaak geen JavaScript), er staat structured data in,
en robots.txt laat ze bewust binnen.

WAAROM EEN BOUWSTAP EN GEEN LOS BESTAND
Een met de hand geschreven llms.txt is na één nieuwe blog verouderd, en een
verouderde wegwijzer is erger dan geen. Dit script leest content.json en de
metatags, dus het klopt altijd. Je verandert er dan ook niets met de hand aan.

De bedrijfsgegevens komen uit build-seo.py, zodat de omschrijving die een
assistent hier leest exact dezelfde is als die in je structured data staat.
"""
import html as htmlmod
import importlib.util
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent


def laad_seo():
    """build-seo.py inlezen als module.

    Kan niet met een gewone import: een streepje mag niet in een modulenaam.
    Het alternatief was de bedrijfsgegevens hier overtypen, en dan lopen ze een
    keer uit de pas met de structured data. Dit is lelijker maar veiliger.
    """
    pad = BASE / "tools" / "build-seo.py"
    spec = importlib.util.spec_from_file_location("build_seo", pad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Alles wat uit de HTML komt moet door htmlmod.unescape. In een HTML-attribuut
# staat "&amp;", maar llms.txt is gewoon tekst en daar hoort een &.
def meta(txt: str, naam: str) -> str:
    m = re.search(r'<meta\s+name="%s"\s+content="([^"]*)"' % re.escape(naam), txt)
    return htmlmod.unescape(m.group(1).strip()) if m else ""


def titel(txt: str) -> str:
    m = re.search(r"<title>(.*?)</title>", txt, re.S)
    if not m:
        return ""
    kaal = htmlmod.unescape(" ".join(m.group(1).split()))
    return re.sub(r"\s*\|\s*Studio Wotto\s*$", "", kaal)


def paginainfo(rel: str):
    """(titel, omschrijving) van een pagina, uit de pagina zelf."""
    f = BASE / rel / "index.html"
    if not f.exists():
        return None
    h = f.read_text(encoding="utf-8", errors="ignore")
    return titel(h), meta(h, "description")


def regel(url: str, naam: str, uitleg: str) -> str:
    uitleg = " ".join((uitleg or "").split())
    return "- [%s](%s)%s" % (naam, url, ": " + uitleg if uitleg else "")


def main():
    seo = laad_seo()
    SITE = seo.SITE
    org = seo.ORGANISATIE

    items = json.loads((BASE / "content.json").read_text(encoding="utf-8"))
    if items and isinstance(items[0], str):
        print("!! content.json bevat nog alleen mapnamen; draai eerst build-manifest.py")
        return 1

    adres = org["address"]
    L = []
    L.append("# Studio Wotto")
    L.append("")
    # De blockquote is de zin die een assistent overneemt als iemand vraagt wie
    # je bent. Zelfde tekst als in de structured data, dus geen twee verhalen.
    L.append("> %s" % org["description"])
    L.append("")
    L.append("Studio Wotto zit in %s (%s, %s) en werkt in heel %s. "
             "Contact: %s, %s."
             % (adres["addressLocality"], adres["streetAddress"], adres["postalCode"],
                org["areaServed"]["name"], org["email"], org["telephone"]))
    L.append("")
    L.append("Waar de studio verstand van heeft: %s." % ", ".join(org["knowsAbout"]).lower())
    L.append("")
    L.append("Over de opbouw van deze site: alle content (projecten, blogs en "
             "workshops) staat in /werk/<naam>/. De overzichten /projecten/, "
             "/blog/ en /werk/ tonen dezelfde items, alleen anders gefilterd. "
             "Elke pagina staat volledig in de HTML, dus er is geen JavaScript "
             "nodig om hem te lezen.")
    L.append("")

    # --- Diensten -----------------------------------------------------------
    L.append("## Diensten")
    L.append("")
    for map_, wat in seo.DIENSTEN.items():
        info = paginainfo(map_)
        if info:
            L.append(regel("%s/%s/" % (SITE, map_), info[0] or wat, info[1]))
    L.append("")

    # --- Content ------------------------------------------------------------
    soorten = [("project", "Projecten", "Gemaakt werk, met per stuk het verhaal erachter."),
               ("blog", "Blogs", "Verslagen, achtergronden en aantekeningen."),
               ("workshop", "Workshops", "Wat er te boeken is voor scholen en groepen.")]
    for soort, kop, intro in soorten:
        lijst = [i for i in items if i["type"] == soort]
        if not lijst:
            continue
        L.append("## %s" % kop)
        L.append("")
        L.append(intro)
        L.append("")
        for i in lijst:                     # content.json staat al op datum, nieuwste eerst
            L.append(regel("%s/werk/%s/" % (SITE, i["slug"]), i["titel"], i["excerpt"]))
        L.append("")

    # --- Over ---------------------------------------------------------------
    L.append("## Over de studio")
    L.append("")
    for map_ in ("over-ons", "contact"):
        info = paginainfo(map_)
        if info:
            L.append(regel("%s/%s/" % (SITE, map_), info[0], info[1]))
    for p in org.get("founder", []):
        L.append("- %s, %s. Profielen: %s"
                 % (p["name"], p["jobTitle"].lower(), ", ".join(p.get("sameAs", []))))
    L.append("")

    # --- Optioneel ----------------------------------------------------------
    # In de llms.txt-opzet is "Optional" bedoeld voor wat je kunt overslaan als
    # je weinig ruimte hebt. De onderwerp-pagina's zijn ingangen naar werk dat
    # hierboven al staat, dus daar horen ze.
    onderwerpen = sorted((BASE / "onderwerp").glob("*/index.html"))
    if onderwerpen:
        L.append("## Optional")
        L.append("")
        L.append("Ingangen per onderwerp. Ze bevatten geen nieuw werk, alleen een "
                 "andere doorsnede van wat hierboven staat.")
        L.append("")
        for f in onderwerpen:
            h = f.read_text(encoding="utf-8", errors="ignore")
            L.append(regel("%s/onderwerp/%s/" % (SITE, f.parent.name), titel(h), meta(h, "description")))
        L.append("")

    tekst = "\n".join(L).rstrip() + "\n"
    (BASE / "llms.txt").write_text(tekst, encoding="utf-8")
    print("llms.txt geschreven: %d regels, %.1f KB" % (len(L), len(tekst.encode("utf-8")) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
