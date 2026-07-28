#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maakt van de logo's een lichte WebP en wijst de pagina's daarnaar.

    python tools/verklein-logos.py

DIT IS EEN KLUSJE OP AANVRAAG, geen onderdeel van build.py. Logo's veranderen
bijna nooit, dus dit hoeft niet bij elke bouwronde. Draai het als je een
klantlogo toevoegt of vervangt.

WAAROM
De klantlogo's stonden als PNG van duizenden pixels breed op de pagina, terwijl
ze in de balk 50 pixels hoog worden getoond. Het logo van Summa was 3815 pixels
breed en 150 KB, voor een plaatje ter grootte van een duimnagel. Samen was dat
het grootste beeld dat nog overbleef nadat de coverfoto's al waren aangepakt.

WAT HET DOET
Naast elk logo komt een <naam>-web.webp op de maat die de pagina echt nodig
heeft (het dubbele van de weergavegrootte, zodat het scherp blijft op een
telefoon met dubbele pixeldichtheid). Daarna worden de verwijzingen in de HTML
en de partials omgezet, inclusief de width en height, want die twee bepalen de
verhouding waarmee de browser ruimte vrijhoudt.

De originele PNG's blijven staan. Wil je terug, dan zet je de verwijzing terug
en gooi je de webp weg.

DE VERHOUDING BLIJFT ONGEMOEID: er wordt alleen verkleind, nooit gesneden.
"""
import pathlib
import re
import sys
import urllib.parse

BASE = pathlib.Path(__file__).resolve().parent.parent

# Per logo: hoe groot heeft de pagina het nodig? De maten komen uit css/styles.css
# en zijn hier verdubbeld voor schermen met dubbele pixeldichtheid.
#   .clients__track img -> height:clamp(32px,5vw,50px)   =>  100 hoog
#   .hero__logo         -> width:min(680px,86%)          => 1360 breed
#   .brand-logo         -> height:40px                   =>   80 hoog
#   .footer__logo       -> height:38px                   =>  (zelfde bestand als hero)
KADERS = [
    ("logo's klanten", (4000, 100)),          # breedte vrij, hoogte bepaalt
    ("logo's/logo studio wotto white.png", (1360, 4000)),
    ("logo's/cropped-avatar-logo-2-e1721815131329-300x202.png", (4000, 80)),
]

# Waar staan de verwijzingen? Alleen deze bestanden gebruiken logo's.
PAGINAS = ["index.html", "partials/header.html", "partials/footer.html"]


def kader_voor(pad: pathlib.Path):
    rel = pad.relative_to(BASE).as_posix()
    for prefix, kader in KADERS:
        if rel == prefix or rel.startswith(prefix.rstrip("/") + "/"):
            return kader
    return None


def main():
    try:
        from PIL import Image
    except ImportError:
        print("!! Pillow ontbreekt: pip install pillow")
        return 1

    # ---- 1. De lichte versies maken -------------------------------------
    nieuw = {}                                  # png-pad (posix) -> (webp-naam, breed, hoog)
    for prefix, _ in KADERS:
        p = BASE / prefix
        bronnen = sorted(p.glob("*.png")) if p.is_dir() else ([p] if p.exists() else [])
        for bron in bronnen:
            kader = kader_voor(bron)
            if not kader:
                continue
            doel = bron.with_name(bron.stem + "-web.webp")
            with Image.open(bron) as im:
                if im.mode not in ("RGB", "RGBA"):
                    im = im.convert("RGBA")
                im.thumbnail(kader, Image.LANCZOS)   # houdt de verhouding intact
                # method=6 is de traagste en beste compressie; bij een handvol
                # logo's merk je daar niets van.
                im.save(doel, "WEBP", quality=88, method=6)
                breed, hoog = im.size
            # Twee sleutels naar dezelfde uitkomst: het pad van de PNG (de eerste
            # keer) en dat van de WebP zelf. Dat tweede maakt opnieuw draaien
            # veilig en herstelt onderweg een verkeerd gecodeerde verwijzing.
            for sleutel in (bron, doel):
                nieuw[sleutel.relative_to(BASE).as_posix()] = (doel.name, breed, hoog)
            print("  %-52s %5.0f KB -> %4.0f KB  (%dx%d)" % (
                doel.relative_to(BASE).as_posix(),
                bron.stat().st_size / 1024, doel.stat().st_size / 1024, breed, hoog))

    if not nieuw:
        print("geen logo's gevonden")
        return 1

    # ---- 2. De verwijzingen omzetten ------------------------------------
    # De src in de HTML is url-gecodeerd ("logo's%20klanten/..."), dus we
    # decoderen hem eerst om te kunnen vergelijken met wat er op schijf staat.
    def zet_om(m, van_map: str):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src:
            return tag
        pad = urllib.parse.unquote(src.group(1))
        heel = pathlib.PurePosixPath(van_map + "/" + pad) if van_map else pathlib.PurePosixPath(pad)
        # ../ oplossen
        delen = []
        for d in heel.parts:
            if d == "..":
                if delen:
                    delen.pop()
            elif d != ".":
                delen.append(d)
        sleutel = "/".join(delen)
        if sleutel not in nieuw:
            return tag
        naam, breed, hoog = nieuw[sleutel]
        # Het pad ervoor blijft precies zoals het was, inclusief de ../ en de
        # %20's. Alleen de bestandsnaam wordt vervangen, en die coderen we: een
        # letterlijke spatie in een src is geen geldige URL en kan op een andere
        # server stukgaan, ook al slikt de browser hem hier.
        oude = src.group(1)
        prefix = oude.rsplit("/", 1)[0] + "/" if "/" in oude else ""
        nieuwe_src = prefix + urllib.parse.quote(naam)
        tag = tag.replace('src="%s"' % oude, 'src="%s"' % nieuwe_src)
        tag = re.sub(r'\bwidth="\d+"', 'width="%d"' % breed, tag)
        tag = re.sub(r'\bheight="\d+"', 'height="%d"' % hoog, tag)
        return tag

    for rel in PAGINAS:
        pad = BASE / rel
        if not pad.exists():
            continue
        txt = oud = pad.read_text(encoding="utf-8")
        van_map = str(pathlib.PurePosixPath(rel).parent) if "/" in rel else ""
        van_map = "" if van_map == "." else van_map
        txt = re.sub(r"<img\s[^>]*>", lambda m: zet_om(m, van_map), txt)
        if txt != oud:
            pad.write_text(txt, encoding="utf-8")
            print("  verwijzingen bijgewerkt in %s" % rel)

    print("\nKlaar. Draai nu 'python tools/build.py' zodat de partials opnieuw "
          "in de pagina's komen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
