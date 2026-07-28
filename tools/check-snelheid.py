#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Loopt de snelheids- en toegankelijkheidsregels na. Waarschuwt, blokkeert niet.

    python tools/check-snelheid.py

Draait automatisch mee als laatste stap van build.py, zodat je het niet kunt
vergeten. Hij stopt nooit de bouw: een waarschuwing is een uitnodiging om te
kijken, geen fout.

WAAROM DIT BESTAAT
De regels hieronder komen niet uit een boekje maar uit een echte meting van deze
site (Lighthouse, mobiel, juli 2026). Elke regel hoort bij iets dat we toen
tegenkwamen en hebben opgelost. Zonder deze controle sluipt het er bij de
volgende pagina zo weer in, want op je eigen snelle verbinding zie je er niets van.

De uitleg per regel staat in snelheid.md.
"""
import html as htmlmod
import pathlib
import re
import sys
import urllib.parse

BASE = pathlib.Path(__file__).resolve().parent.parent
NEGEER = {"partials", "tools", "moodboard", ".git", ".astro", ".github",
          "node_modules", "oude blogs en pagina's"}

# Grenzen. Ruim gekozen: dit moet je waarschuwen bij een uitschieter, niet
# zeuren over elke foto.
MAX_BEELD_KB = 400          # een foto op een detailpagina
MAX_FILM_KB = 500           # een filmpje op een kaart
MAX_TITEL = 60              # daarboven kapt Google de titel af
MIN_TITEL = 30              # daaronder laat je ruimte liggen
MAX_OMSCHRIJVING = 160


def paginas():
    for p in sorted(BASE.rglob("*.html")):
        if any(x in p.relative_to(BASE).parts for x in NEGEER):
            continue
        yield p


def bestand_van(src: str, van_map: pathlib.Path):
    """Het bestand op schijf waar deze src naar wijst, of None bij een externe."""
    if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#|data:)", src, re.I):
        return None
    pad = urllib.parse.unquote(src.split("?")[0].split("#")[0])
    if not pad:
        return None
    # Een pad dat met / begint hoort bij de site-root, niet bij de map van de
    # pagina. 404.html gebruikt dat bewust: die pagina kan op elk adres worden
    # getoond, dus een relatief pad zou daar juist misgaan.
    if pad.startswith("/"):
        return (BASE / pad.lstrip("/")).resolve()
    return (van_map / pad).resolve()


def kb(p: pathlib.Path) -> float:
    return p.stat().st_size / 1024


def controleer(pad: pathlib.Path) -> list:
    txt = pad.read_text(encoding="utf-8", errors="ignore")
    van_map = pad.parent
    op = []

    # --- 1. Elke afbeelding heeft width en height ---------------------------
    # Zonder die twee weet de browser pas hoe groot een foto wordt als hij
    # binnen is, en schuift alles eronder alsnog omlaag. Dat is de CLS waar
    # we 0,467 voor kregen.
    for tag in re.findall(r"<img\s[^>]*>", txt):
        if not (re.search(r'\bwidth="\d+"', tag) and re.search(r'\bheight="\d+"', tag)):
            src = (re.search(r'src="([^"]*)"', tag) or [None, "?"])[1]
            op.append(("beeld zonder width/height", src))

    # --- 2. Niets uit de <head> mag van een ander domein komen --------------
    # Een <link> naar een vreemd domein blokkeert het tekenen van de pagina:
    # eerst DNS, dan TLS, dan pas het bestand. Dat kostte hier 2.510 ms.
    # Let op: alleen dingen die de browser echt moet ophalen. Een
    # <link rel="canonical"> wijst naar je eigen adres en kost niets.
    head = txt.split("</head>")[0]
    for tag in re.findall(r"<link\s[^>]*>", head):
        soort = (re.search(r'\brel="([^"]*)"', tag) or [None, ""])[1].lower()
        href = (re.search(r'\bhref="([^"]*)"', tag) or [None, ""])[1]
        if soort in ("stylesheet", "preload", "modulepreload") and href.startswith(("http://", "https://")):
            op.append(("blokkerende <link rel=%s> naar een ander domein" % soort, href))
    for tag in re.findall(r"<script\s[^>]*>", head):
        src = (re.search(r'\bsrc="(https?://[^"]*)"', tag) or [None, ""])[1]
        if src and not re.search(r"\b(defer|async)\b", tag):
            op.append(("<script> uit de <head> van een ander domein", src))

    # --- 3. Geen uitschieters in bestandsgrootte ----------------------------
    # Alleen wat de bezoeker ongevraagd binnenkrijgt telt mee. Een artikelvideo
    # staat op preload="none" met een afspeelknop: die kost pas iets als iemand
    # erop drukt, en mag dus gerust groot zijn. Een filmpje op een kaart speelt
    # vanzelf af en wordt dus altijd opgehaald, ook als niemand kijkt.
    films = set(re.findall(r'data-video="([^"]+)"', txt))
    for tag in re.findall(r"<video\s[^>]*>", txt):
        src = (re.search(r'\bsrc="([^"]*)"', tag) or [None, ""])[1]
        vanzelf = "autoplay" in tag or 'preload="none"' not in tag
        if src and vanzelf:
            films.add(src)

    beelden = set(re.findall(r'<img\s[^>]*\bsrc="([^"]+)"', txt))

    for src, grens in [(s, MAX_BEELD_KB) for s in beelden] + [(s, MAX_FILM_KB) for s in films]:
        f = bestand_van(src, van_map)
        if f and f.exists() and kb(f) > grens:
            op.append(("%.0f KB, boven de grens van %d KB" % (kb(f), grens), f.name))

    # --- 4. Verwijzingen die nergens heen gaan ------------------------------
    for src in re.findall(r'(?:src|poster|data-video)="([^"]+)"', txt):
        f = bestand_van(src, van_map)
        if f and not f.exists():
            op.append(("verwijst naar een bestand dat niet bestaat", src))

    # --- 5. Eén <main>, precies één <h1>, en geen gat in de koppen ----------
    if "<main" not in txt:
        op.append(("geen <main>", "hulpsoftware weet niet waar de inhoud begint"))

    koppen = [int(h) for h in re.findall(r"<h([1-6])[\s>]", txt)]
    if koppen.count(1) != 1:
        op.append(("%d keer een <h1>" % koppen.count(1), "er hoort er precies één te zijn"))
    vorig = 0
    for h in koppen:
        if vorig and h > vorig + 1:
            op.append(("kopniveau springt van h%d naar h%d" % (vorig, h),
                       "afdalen mag maar één stap tegelijk"))
            break
        vorig = h

    # --- 6. Titel en omschrijving ------------------------------------------
    # Een pagina met noindex komt niet in Google, dus deze regels gelden daar
    # niet. Dat is precies het geval bij 404.html.
    noindex = bool(re.search(r'name="robots"[^>]*content="[^"]*noindex', txt, re.I))

    t = re.search(r"<title>(.*?)</title>", txt, re.S)
    if not t:
        op.append(("geen <title>", ""))
    elif not noindex:
        # html.unescape eerst: in de HTML staat &amp;, en dat is één teken in de
        # zoekresultaten, geen vijf. Zonder dit meldt hij titels te lang die het
        # helemaal niet zijn.
        n = len(htmlmod.unescape(re.sub(r"\s+", " ", t.group(1)).strip()))
        if n > MAX_TITEL:
            op.append(("titel is %d tekens" % n, "Google kapt af boven de %d" % MAX_TITEL))
        elif n < MIN_TITEL:
            op.append(("titel is maar %d tekens" % n, "je laat ruimte liggen tot %d" % MAX_TITEL))

    d = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', txt)
    if not d and not noindex:
        op.append(("geen meta description", ""))
    elif d and len(htmlmod.unescape(d.group(1))) > MAX_OMSCHRIJVING:
        op.append(("description is %d tekens" % len(htmlmod.unescape(d.group(1))),
                   "boven de %d wordt hij afgekapt" % MAX_OMSCHRIJVING))

    # --- 7. Iconen die niet zijn omgezet ------------------------------------
    if re.search(r'<i class="ph-', txt):
        op.append(("nog een <i class=\"ph-...\">", "draai python tools/build.py"))

    return op


def main():
    alles = {}
    for pad in paginas():
        op = controleer(pad)
        if op:
            alles[pad.relative_to(BASE).as_posix()] = op

    if not alles:
        print("snelheidscheck: alles in orde.")
        return 0

    n = sum(len(v) for v in alles.values())
    print("snelheidscheck: %d aandachtspunt(en) op %d pagina('s).\n"
          "Uitleg per regel staat in snelheid.md.\n" % (n, len(alles)))
    for pagina, op in alles.items():
        print("  %s" % pagina)
        for wat, waar in op:
            print("     - %-46s %s" % (wat, waar))
    print("\n(Dit blokkeert niets. Beoordeel zelf of het erg is.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
