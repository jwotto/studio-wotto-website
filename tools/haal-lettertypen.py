#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Haalt Fredoka en Nunito bij Google weg en zet ze in fonts/.

    python tools/haal-lettertypen.py

DIT IS EEN EENMALIG KLUSJE, geen onderdeel van build.py. Je draait het alleen
opnieuw als je een ander lettertype wilt, of als Google een nieuwe versie
uitbrengt en je die wilt overnemen.

WAAROM NIET MEER BIJ GOOGLE LATEN STAAN
De regel <link href="fonts.googleapis.com..."> in de <head> blokkeert het
tekenen van de pagina. De browser mag pas iets op het scherm zetten als hij die
stylesheet binnen heeft, en daarvoor moet hij eerst een vreemd domein opzoeken
(DNS), een beveiligde verbinding opzetten (TLS) en dan pas vragen om het
bestand. Op een trage 4G-verbinding kostte dat samen ruim twee seconden voordat
er ook maar iets in beeld kwam. Vanaf je eigen server is de verbinding er al.

Dat het scheelt voor je privacyverhaal is een prettige bijkomstigheid: er gaat
geen IP-adres van je bezoekers meer naar Google voordat ze iets gezien hebben.

WAT ER WORDT OPGEHAALD
Alleen de subsets latin en latin-ext. De rest die Google meestuurt (cyrillisch,
Hebreeuws, Vietnamees) heeft een Nederlandse site nooit nodig. latin-ext houden
we wel: daar zitten letters in als de ł en de ő, en die kunnen in namen staan.

Beide families zijn variabele lettertypen: één bestand dekt alle dikten. Daarom
staat er in de CSS een bereik (400 700) in plaats van een los gewicht.
"""
import pathlib
import re
import sys
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent.parent
FONTS = BASE / "fonts"

CSS_URL = ("https://fonts.googleapis.com/css2"
           "?family=Fredoka:wght@400;500;600;700"
           "&family=Nunito:wght@400;600;700;800&display=swap")

# Een moderne browser-UA, anders stuurt Google ouderwetse formaten in plaats
# van woff2 (dat is het kleinste en wordt overal ondersteund).
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

HOUDEN = ("latin", "latin-ext")
BEREIK = {"Fredoka": "400 700", "Nunito": "400 800"}


def haal(url: str) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def main():
    FONTS.mkdir(exist_ok=True)
    css = haal(CSS_URL).decode("utf-8")

    # Google zet boven elk blok een commentaar met de naam van de subset.
    blokken = re.findall(r"/\* ([a-z-]+) \*/\s*(@font-face \{.*?\})", css, re.S)

    gevonden, regels = {}, []
    for subset, blok in blokken:
        if subset not in HOUDEN:
            continue
        familie = re.search(r"font-family: '([^']+)'", blok).group(1)
        url = re.search(r"url\((https[^)]+)\)", blok).group(1)
        stretch = re.search(r"font-stretch: ([^;]+);", blok)
        bereik = re.search(r"unicode-range: ([^;]+);", blok).group(1)
        sleutel = (familie, subset)
        if sleutel in gevonden:
            continue                        # alle dikten wijzen naar hetzelfde bestand
        gevonden[sleutel] = True

        naam = "%s-%s.woff2" % (familie.lower(), subset)
        (FONTS / naam).write_bytes(haal(url))
        kb = (FONTS / naam).stat().st_size / 1024
        print("  %-24s %5.0f KB" % (naam, kb))

        regels.append("\n".join([
            "@font-face{",
            "  font-family:'%s';" % familie,
            "  font-style:normal;",
            "  font-weight:%s;" % BEREIK.get(familie, "400 700"),
            ("  font-stretch:%s;" % stretch.group(1)) if stretch else "",
            "  font-display:swap;",
            "  src:url('../fonts/%s') format('woff2');" % naam,
            "  unicode-range:%s;" % bereik,
            "}",
        ]).replace("\n\n", "\n"))

    if not regels:
        print("!! niets gevonden; is de opmaak van Google's CSS gewijzigd?")
        return 1

    # De blokken gaan RECHTSTREEKS in styles.css, niet in een eigen bestand met
    # een @import erheen. Een @import zou de browser dwingen eerst styles.css op
    # te halen, dat te lezen, en daarna nog een verzoek te doen. Precies het
    # soort wachtrij dat we hier juist aan het opruimen zijn.
    kop = ("/* ===== lettertypen: begin (gezet door tools/haal-lettertypen.py) =====\n"
           "   Niet met de hand wijzigen: dit blok wordt bij het ophalen overschreven.\n"
           "\n"
           "   Dit stond eerst als <link> naar fonts.googleapis.com in de <head> van\n"
           "   elke pagina. Die regel blokkeerde het tekenen van de pagina tot een\n"
           "   vreemd domein antwoordde, en dat kostte op traag 4G ruim twee seconden. */")
    voet = "/* ===== lettertypen: eind ===== */"

    styles = BASE / "css" / "styles.css"
    txt = styles.read_text(encoding="utf-8")
    blok = kop + "\n\n" + "\n\n".join(regels) + "\n\n" + voet
    patroon = re.compile(re.escape(kop.split("\n")[0]) + r".*?" + re.escape(voet), re.S)
    txt, n = patroon.subn(lambda m: blok, txt)
    if not n:
        txt = blok + "\n\n" + txt
    styles.write_text(txt, encoding="utf-8")

    print("\n%d @font-face-blok(ken) bovenaan css/styles.css gezet." % len(regels))
    print("Haal nu de <link> naar fonts.googleapis.com uit de pagina's.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
