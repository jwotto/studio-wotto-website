#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Haalt van elke ingesloten video (Vimeo, YouTube) het posterbeeld op.

    python tools/haal-embedposters.py

DIT IS EEN KLUSJE OP AANVRAAG, geen onderdeel van build.py. Draai het als je
ergens een nieuwe video insluit. build-inbakken.py waarschuwt je als er een
poster mist, dus je kunt het niet vergeten.

WAAROM
Een ingesloten Vimeo- of YouTube-speler is duur. Op de pagina van side-quest-rave
haalde hij 312 KB aan JavaScript op van een vreemd domein, plus cookies van
derden, en dat gebeurde meteen bij het laden. De pagina scoorde daardoor 60 op
snelheid, met een LCP van 10,2 seconden, terwijl een blog zonder insluiting op
91 stond.

De oplossing is een namaakspeler: je ziet het posterbeeld met een afspeelknop,
en pas als iemand klikt wordt de echte speler geladen. Dat is precies wat de
bezoeker verwacht, en wie niet klikt betaalt niets.

Daarvoor is dat posterbeeld nodig, en dat halen we hier op. Eén keer, en dan
staat het op onze eigen server. Zouden we het rechtstreeks van vimeocdn of ytimg
laden, dan hadden we alsnog een vreemd domein aan de lijn.

De poster komt naast de pagina te staan als embed-<dienst>-<nummer>.jpg.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

from PIL import Image

BASE = pathlib.Path(__file__).resolve().parent.parent
NEGEER = {"tools", ".git", ".astro", "node_modules", "oude blogs en pagina's", "partials"}

# De insluiting is een 16:9-vlak van hoogstens de containerbreedte (1200 px).
# Het dubbele daarvan is ruim genoeg voor een scherm met dubbele pixeldichtheid.
MAX_BREED = 1280

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def haal(url: str) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()


def herken(src: str):
    """Geeft (dienst, nummer) terug, of None als we het niet kennen."""
    m = re.search(r"player\.vimeo\.com/video/(\d+)", src)
    if m:
        return "vimeo", m.group(1)
    m = re.search(r"youtube(?:-nocookie)?\.com/embed/([\w-]+)", src)
    if m:
        return "youtube", m.group(1)
    return None


def poster_url(dienst: str, nummer: str):
    """Het adres van het grootste posterbeeld dat de dienst heeft."""
    if dienst == "youtube":
        # maxresdefault bestaat niet altijd; hqdefault altijd wel.
        for naam in ("maxresdefault", "hqdefault"):
            u = "https://i.ytimg.com/vi/%s/%s.jpg" % (nummer, naam)
            try:
                if len(haal(u)) > 2000:      # een 404 van ytimg is een klein plaatje
                    return u
            except urllib.error.HTTPError:
                continue
        return None
    # Vimeo vertelt zelf waar de poster staat.
    try:
        d = json.loads(haal("https://vimeo.com/api/oembed.json"
                            "?url=https://vimeo.com/%s&width=1280" % nummer).decode("utf-8"))
    except Exception:
        return None
    u = d.get("thumbnail_url")
    if not u:
        return None
    # De standaardmaat is klein; vragen om een breedte geeft een scherper beeld.
    return re.sub(r"_\d+x\d+(\.\w+)$", r"_1280\1", u)


def paginas():
    for p in sorted(BASE.rglob("*.html")):
        if any(x in p.relative_to(BASE).parts for x in NEGEER):
            continue
        yield p


def main():
    gevonden = gemaakt = overgeslagen = 0
    mislukt = []

    for pad in paginas():
        txt = pad.read_text(encoding="utf-8", errors="ignore")
        for src in re.findall(r'<iframe[^>]+src="([^"]+)"', txt):
            kend = herken(src)
            if not kend:
                mislukt.append((pad.name, src[:60]))
                continue
            dienst, nummer = kend
            gevonden += 1
            doel = pad.parent / ("embed-%s-%s.webp" % (dienst, nummer))
            if doel.exists():
                overgeslagen += 1
                continue
            u = poster_url(dienst, nummer)
            if not u:
                mislukt.append((pad.parent.name, "%s %s: geen poster" % (dienst, nummer)))
                continue
            try:
                rauw = haal(u)
            except Exception as e:
                mislukt.append((pad.parent.name, str(e)[:50]))
                continue

            # Wat de diensten leveren is een JPEG van soms 200 KB, terwijl het
            # als stilstaand beeld achter een afspeelknop staat. Zelfde
            # behandeling als de rest van het beeld op de site: WebP, en niet
            # groter dan hij getoond wordt. Verhouding blijft ongemoeid.
            tijdelijk = doel.with_suffix(".tijdelijk")
            tijdelijk.write_bytes(rauw)
            try:
                with Image.open(tijdelijk) as im:
                    if im.mode not in ("RGB", "RGBA"):
                        im = im.convert("RGB")
                    im.thumbnail((MAX_BREED, MAX_BREED), Image.LANCZOS)
                    im.save(doel, "WEBP", quality=80, method=6)
            except Exception as e:
                mislukt.append((pad.parent.name, "omzetten mislukt: %s" % str(e)[:40]))
                tijdelijk.unlink(missing_ok=True)
                continue
            tijdelijk.unlink(missing_ok=True)

            gemaakt += 1
            print("  %-52s %5.0f KB -> %4.0f KB" % (
                doel.relative_to(BASE).as_posix(), len(rauw) / 1024,
                doel.stat().st_size / 1024))

    print("\n%d insluiting(en) gevonden: %d poster(s) opgehaald, %d stond(en) er al."
          % (gevonden, gemaakt, overgeslagen))
    if mislukt:
        print("\nNiet gelukt:")
        for waar, wat in mislukt:
            print("  - %s: %s" % (waar, wat))
    return 0


if __name__ == "__main__":
    sys.exit(main())
