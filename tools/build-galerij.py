#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bouwt de galerij onder een werk-item uit de bestanden in de map.

Draaien:  python tools/build-galerij.py   (of gewoon: python tools/build.py)

JIJ SLEEPT FOTO'S EN FILMPJES IN werk/<slug>/, DIT DOET DE REST:

  1. Elke foto breder dan 1600px wordt verkleind. Een cameraorigineel is zo
     7 MB, en dat wil je niet op een kaartje van 340px. Dit gebeurt altijd,
     ook bij je cover.
  2. Staan er twee of meer bestanden die nergens in je tekst gebruikt worden,
     dan komt er onderaan een galerij. Wat er niet in komt: de foto die al
     zwevend in je tekst staat, de poster van een filmpje, en de video van je
     kaartje (wotto:videocover). Die zie je immers al.
  3. Is er maar EEN ongebruikt bestand, dan doet dit script niets en zegt het
     dat alleen. Een galerij van een foto is onzin: die hoort zwevend in je
     tekst, en waar precies kan een script niet bedenken.
  4. Heb je zelf een galerij gemaakt? Die blijft van jou, daar blijft dit
     script van af.
  5. Een filmpje zonder poster krijgt er een, uit het filmpje zelf.
  6. De alt-tekst komt uit de bestandsnaam. Schrijf je zelf een betere, dan
     blijft die staan: dit script overschrijft je eigen alt-teksten nooit.
     Noem je bestanden dus fatsoenlijk, dat scheelt je werk.

Volgorde in de galerij = alfabetisch op bestandsnaam. Wil je een andere
volgorde, hernoem dan.
"""
import json, pathlib, re, sys

SITE_DIR = pathlib.Path(__file__).resolve().parent.parent
BEELD = (".jpg", ".jpeg", ".png")
FILM = (".mp4",)
MAX_BREED = 1600

START = '<!-- galerij: gemaakt door tools/build-galerij.py uit de bestanden in deze map -->'
EIND = "<!-- /galerij -->"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def alt_uit_naam(naam):
    """museum-speelklok-hall-of-fame.jpg -> 'Museum speelklok hall of fame'"""
    kaal = re.sub(r"\.[a-z0-9]+$", "", naam, flags=re.I)
    kaal = re.sub(r"[-_]+", " ", kaal).strip()
    return kaal[:1].upper() + kaal[1:] if kaal else naam


def bestaande_alts(html):
    """Alt-teksten die er al staan onthouden, zodat handwerk niet verdwijnt."""
    blok = re.search(re.escape(START) + r"(.*?)" + re.escape(EIND), html, re.S)
    if not blok:
        blok = re.search(r'<div class="gallery[^"]*">(.*?)</div>\s*(?=<|$)', html, re.S)
    if not blok:
        return {}
    uit = {}
    for m in re.finditer(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', blok.group(1)):
        uit[m.group(1)] = m.group(2)
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*data-tekst="([^"]*)"', blok.group(1)):
        uit[m.group(1)] = m.group(2)
    return uit


def main():
    try:
        from PIL import Image
    except ImportError:
        print("!! Pillow ontbreekt: pip install pillow")
        return 1

    slugs = json.load(open(SITE_DIR / "content.json", encoding="utf-8"))
    totaal_gal = totaal_klein = totaal_kb = 0

    # ---- 1. Alles web-klaar maken. Dit staat los van de galerij: ook je cover
    #         wordt verkleind, en juist die staat op elke lijstpagina.
    for slug in slugs:
        for p in sorted((SITE_DIR / "werk" / slug).iterdir()):
            if p.suffix.lower() not in BEELD:
                continue
            im = Image.open(p)
            if im.width <= MAX_BREED and im.height <= MAX_BREED:
                continue
            kb0 = p.stat().st_size / 1024
            if p.suffix.lower() in (".jpg", ".jpeg"):
                im = im.convert("RGB")
            im.thumbnail((MAX_BREED, MAX_BREED), Image.LANCZOS)
            im.save(p, quality=82, optimize=True)
            kb1 = p.stat().st_size / 1024
            print("  verkleind: %-46s %5.0f -> %4.0f kB" % (p.name, kb0, kb1))
            totaal_klein += 1
            totaal_kb += kb0 - kb1
    if totaal_klein:
        print("  %d foto's verkleind, samen %.1f MB minder\n" % (totaal_klein, totaal_kb / 1024))

    # ---- 2. De galerijen
    for slug in slugs:
        d = SITE_DIR / "werk" / slug
        f = d / "index.html"
        h = f.read_text(encoding="utf-8")

        # het blok zelf even wegdenken, anders zie je je eigen galerij aan voor tekst
        zonder = re.sub(re.escape(START) + r".*?" + re.escape(EIND), "", h, flags=re.S)

        # Heb je zelf een galerij gemaakt? Dan blijft die van jou. Dit script
        # beheert alleen wat het zelf heeft neergezet (tussen de markers), en
        # vult verder alleen aan waar nog niks staat. Anders was je die
        # kolommen-opmaak van Ramses bij de eerste build kwijt geweest.
        if START not in h and re.search(r'<div class="gallery', zonder):
            print("  %-30s eigen galerij, niet aangeraakt" % slug)
            continue
        gebruikt = set(re.findall(r'(?:src|href|poster)="([^"/]+)"', zonder))
        videocover = (re.search(r'wotto:videocover"\s+content="([^"]*)"', h) or [None, ""])[1]
        if videocover:
            gebruikt.add(videocover)

        media = sorted(p for p in d.iterdir()
                       if p.suffix.lower() in BEELD + FILM and p.name not in gebruikt)
        if not media:
            continue
        if len(media) < 2 and START not in h:
            print("  %-30s 1 los bestand (%s). Zet 'm zelf zwevend in de tekst,"
                  " een galerij van een foto is onzin." % (slug, media[0].name))
            continue

        oude = bestaande_alts(h)
        regels = []
        for p in media:
            if p.suffix.lower() in BEELD:
                w, hgt = Image.open(p).size
                alt = oude.get(p.name) or alt_uit_naam(p.name)
                regels.append(
                    '        <img src="%s" width="%d" height="%d" loading="lazy" decoding="async"\n'
                    '             alt="%s">' % (p.name, w, hgt, esc(alt)))
            else:
                poster = poster_voor(p)
                if not poster:
                    print("   !! %s/%s: geen poster te maken, filmpje overgeslagen" % (slug, p.name))
                    continue
                pw, ph = Image.open(d / poster).size
                alt = oude.get(p.name) or alt_uit_naam(p.name)
                regels.append(
                    '        <figure>\n'
                    '          <video src="%s" poster="%s" width="%d" height="%d"\n'
                    '                 controls preload="none" playsinline></video>\n'
                    '          <figcaption>%s</figcaption>\n'
                    '        </figure>' % (p.name, poster, pw, ph, esc(alt)))

        if not regels:
            continue
        blok = '%s\n      <div class="gallery">\n%s\n      </div>\n      %s' % (
            START, "\n".join(regels), EIND)

        if START in h:
            h = re.sub(re.escape(START) + r".*?" + re.escape(EIND), blok, h, flags=re.S)
        else:
            # een bestaande handgemaakte galerij vervangen, anders onderaan erbij
            oud = re.search(r'\n *<!--[^>]*?-->\n *<div class="gallery[^"]*">.*?\n      </div>|'
                            r'\n *<div class="gallery[^"]*">.*?\n      </div>', h, re.S)
            if oud:
                h = h.replace(oud.group(0), "\n      " + blok, 1)
            else:
                h = h.replace("    </div>\n  </div>\n</article>",
                              "\n      " + blok + "\n    </div>\n  </div>\n</article>", 1)
        f.write_text(h, encoding="utf-8")
        totaal_gal += 1
        print("  %-30s %d in de galerij" % (slug, len(regels)))

    print("\n%d galerijen, %d foto's verkleind" % (totaal_gal, totaal_klein))


def poster_voor(video):
    """Poster bij een filmpje: bestaande gebruiken, anders er een uit halen."""
    kaal = video.with_suffix("")
    for kand in (kaal.parent / (kaal.name + "-poster.jpg"), kaal.with_suffix(".jpg")):
        if kand.exists():
            return kand.name
    try:
        import subprocess, imageio_ffmpeg
        doel = kaal.parent / (kaal.name + "-poster.jpg")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                        "-ss", "1", "-i", str(video), "-frames:v", "1",
                        "-vf", "scale=%d:-2" % MAX_BREED, "-q:v", "3", str(doel)], check=True)
        print("   poster gemaakt: %s" % doel.name)
        return doel.name
    except Exception as e:
        print("   (geen ffmpeg: pip install imageio-ffmpeg)  %s" % str(e)[:40])
        return None


if __name__ == "__main__":
    sys.exit(main())
