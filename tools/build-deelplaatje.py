#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maakt voor elke blog een deelplaatje voor Facebook, LinkedIn en WhatsApp.

    python tools/build-deelplaatje.py

WAAROM
Deel je een link, dan haalt Facebook of LinkedIn het plaatje uit og:image en
toont het liggend, ongeveer 1200 bij 630. Was dat plaatje gewoon de cover, dan
sneed het platform er zelf een strook uit. Bij een staande foto viel die strook
op schouderhoogte en waren de hoofden weg.

Daarom maakt dit script per blog een eigen plaatje van precies 1200x630:

    deense-makers-spelen-op-de-side-quest-rave.jpg        <- de cover
    deense-makers-spelen-op-de-side-quest-rave-deel.jpg   <- het deelplaatje

De cover staat er in zijn geheel op, met afgeronde hoeken, op een vlak in de
blogkleur (bubblegum) met het logo ernaast. Er wordt niets van de foto
afgesneden: staand of liggend, je ziet de hele foto. Het platform hoeft dan
niets meer te snijden, want het plaatje heeft al de goede vorm.

Daarna zet het script in de pagina:

    og:image          naar het deelplaatje
    og:image:type     image/jpeg
    og:image:width    1200
    og:image:height   630
    og:image:alt      de alt van de cover in de tekst, of anders de titel

Met breedte en hoogte erbij hoeft Facebook het plaatje niet eerst op te halen
om te weten hoe groot het is. Zonder die twee blijft de eerste keer dat iemand
de link deelt het plaatje soms leeg.

De structured data blijft naar de cover zelf wijzen, want daar hoort de echte
foto in en geen compositie.

Het deelplaatje staat nergens in de tekst en is geen artikelfoto, dus
build-galerij.py en build-artikelbeeld.py slaan alles over dat op -deel eindigt.

Alleen nieuwe of gewijzigde covers worden verwerkt, dus opnieuw draaien is snel.
Verander je de opmaak hieronder, gooi dan de -deel.jpg's weg of draai met
--opnieuw, dan worden ze allemaal opnieuw gemaakt.
"""
import html
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://studiowotto.com"

# Voor welke soorten items. Projecten en workshops kunnen er later bij.
SOORTEN = ("blog",)

BREED, HOOG = 1200, 630
ACHTERGROND = "#F9B3D5"       # --bubblegum, de kleur van de blogpagina's
MARGE = 40                     # ruimte rond de foto
RONDING = 24                   # afgeronde hoeken, zoals de kaartjes op de site
LOGO_VAK = 300                 # breedte van het vak rechts waar het logo staat
LOGO = BASE / "logo's" / "logo studio wotto black.png"
KWALITEIT = 85


def maak_plaatje(bron, doel, Image, ImageDraw, ImageOps):
    doek = Image.new("RGB", (BREED, HOOG), ACHTERGROND)

    # De foto past in het vak links, zonder te snijden.
    foto = ImageOps.exif_transpose(Image.open(bron)).convert("RGB")
    vak_b = BREED - LOGO_VAK - 2 * MARGE
    vak_h = HOOG - 2 * MARGE
    foto.thumbnail((vak_b, vak_h), Image.LANCZOS)
    masker = Image.new("L", foto.size, 0)
    ImageDraw.Draw(masker).rounded_rectangle(
        (0, 0, foto.width - 1, foto.height - 1), RONDING, fill=255)
    x = MARGE + (vak_b - foto.width) // 2
    y = (HOOG - foto.height) // 2
    doek.paste(foto, (x, y), masker)

    # Het logo in het midden van het vak rechts.
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((LOGO_VAK - MARGE, HOOG), Image.LANCZOS)
    lx = BREED - LOGO_VAK - MARGE // 2 + (LOGO_VAK - logo.width) // 2
    ly = (HOOG - logo.height) // 2
    doek.paste(logo, (lx, ly), logo)

    doek.save(doel, "JPEG", quality=KWALITEIT, optimize=True, progressive=True)


def zet_meta(h, slug, deelnaam, alt):
    """Vervangt og:image en alle og:image:* door een vast blok."""
    h = re.sub(r'[ \t]*<meta property="og:image:[a-z]+" content="[^"]*">\n', "", h)
    blok = ('<meta property="og:image" content="%s/werk/%s/%s">\n'
            '<meta property="og:image:type" content="image/jpeg">\n'
            '<meta property="og:image:width" content="%d">\n'
            '<meta property="og:image:height" content="%d">\n'
            '<meta property="og:image:alt" content="%s">'
            % (SITE, slug, deelnaam, BREED, HOOG, html.escape(alt, quote=True)))
    return re.sub(r'<meta property="og:image" content="[^"]*">', lambda m: blok, h, count=1)


def kies_alt(h, cover, titel):
    # Een met de hand geschreven og:image:alt blijft staan.
    m = re.search(r'<meta property="og:image:alt" content="([^"]*)">', h)
    if m and m.group(1):
        return html.unescape(m.group(1))
    # Anders de alt van de cover zoals die in de tekst staat (vaak als .webp).
    stam = re.escape(pathlib.PurePosixPath(cover).stem)
    for tag in re.findall(r"<img\b[^>]*>", h, re.S):
        if re.search(r'src="%s\.[a-z]+"' % stam, tag):
            a = re.search(r'alt="([^"]*)"', tag)
            if a and a.group(1):
                return html.unescape(a.group(1))
    return titel


def main():
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        print("!! Pillow ontbreekt: pip install pillow")
        return 1

    opnieuw = "--opnieuw" in sys.argv
    items = json.loads((BASE / "content.json").read_text(encoding="utf-8"))
    if items and isinstance(items[0], str):
        print("!! content.json bevat nog alleen mapnamen; draai eerst build-manifest.py")
        return 1

    script_tijd = pathlib.Path(__file__).stat().st_mtime
    gemaakt = bijgewerkt = 0

    for item in items:
        if item.get("type") not in SOORTEN:
            continue
        slug, cover = item["slug"], item["cover"]
        map_ = BASE / "werk" / slug
        bron = map_ / cover
        if not bron.exists():
            continue
        deelnaam = pathlib.PurePosixPath(cover).stem + "-deel.jpg"
        doel = map_ / deelnaam

        oud = (not doel.exists()
               or doel.stat().st_mtime < max(bron.stat().st_mtime, script_tijd))
        if opnieuw or oud:
            maak_plaatje(bron, doel, Image, ImageDraw, ImageOps)
            gemaakt += 1
            print("  %-40s %4d KB" % (slug + "/" + deelnaam, doel.stat().st_size // 1024))

        pagina = map_ / "index.html"
        h = pagina.read_text(encoding="utf-8")
        nieuw = zet_meta(h, slug, deelnaam, kies_alt(h, cover, item.get("titel", "")))
        if nieuw != h:
            pagina.write_text(nieuw, encoding="utf-8")
            bijgewerkt += 1

    print("deelplaatje: %d gemaakt, %d pagina('s) bijgewerkt." % (gemaakt, bijgewerkt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
