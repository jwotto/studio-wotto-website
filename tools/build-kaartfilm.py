#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maakt van elk kaartfilmpje een lichte versie.

    python tools/build-kaartfilm.py

WAAROM
Een filmpje in een artikel staat op preload="none" met een afspeelknop: dat kost
pas iets als iemand erop drukt. Een filmpje op een KAART speelt vanzelf af, dus
de browser haalt hem altijd helemaal op, ook als de kaart onderaan de pagina
staat en niemand ernaar kijkt. Op de homepage waren ze samen 1258 KB, meer dan
de helft van het hele gewicht.

WAT ER TE HALEN VALT, EN WAT NIET
Bij het nameten bleek het meeste al goed: ze staan al op 500 of 600 pixels en
hebben al geen geluidsspoor. De gebruikelijke adviezen "verklein het" en "sloop
het geluid eruit" waren hier dus al opgevolgd.

Wat overbleef is de bitrate. aura-bouw-lasers-kaart.mp4 was 634 KB voor vijf
seconden: dat is bijna 1 Mbit/s voor een vierkantje van 600 pixels. Laserlicht
en korrelig beeld comprimeren nu eenmaal slecht, en de codering was er niet op
ingesteld. Dat is wat dit script rechtzet.

En één filmpje duurde 8 seconden waar de rest er 5 doet.

LET OP BIJ HET INKORTEN
Een loopje dat je afkapt kan gaan haperen op het punt waar hij terugspringt.
Wordt er iets ingekort, dan zegt dit script dat erbij. Kijk daar even naar op de
site. Vind je het lelijk, zet MAX_SEC dan hoger of maak het origineel korter met
een echt begin en eind.

De originelen blijven staan. Naast elke <naam>.mp4 komt een <naam>-web.mp4, en
tools/build-inbakken.py pakt die als hij bestaat.
"""
import json
import pathlib
import re
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent

MAX_SEC = 5           # langer dan dit wordt afgekapt
DOEL_KB = 250         # hier proberen we onder te blijven

# Een trapje van instellingen, van mooiste naar kleinste. We nemen de EERSTE die
# onder DOEL_KB uitkomt. Zo blijven filmpjes die al licht zijn op volle kwaliteit
# staan, en wordt alleen de uitschieter echt aangepakt. Eén instelling voor alles
# zou zes goede filmpjes verslechteren om er één te repareren.
#
# De grote winst zit in de resolutie en het aantal beeldjes, niet in de
# kwaliteitsknop (crf). Gemeten op aura-bouw-lasers, het zwaarste geval:
#   crf 32 op 600 px ............ 84% van origineel
#   crf 34 op 600 px ............ 68%
#   crf 32 op 480 px met 20 fps . 47%
#   crf 34 op 480 px met 20 fps . 38%
#
# hqdn3d is een ruisfilter. Korrel is voor een codec zowat het duurste dat er
# is, want het verandert elk beeldje overal een beetje. Bij laserlicht en
# schemerige opnames scheelt een beetje ruis wegpoetsen echt iets, en op een
# kaartje van 400 pixels zie je dat niet.
#
# MINDER BEELDJES PER SECONDE: NIET DOEN. Dat stond hier eerst wel, en op 20
# fps zag je de twee zwaarste filmpjes zichtbaar schokken. Vloeiend beeld is
# belangrijker dan de laatste vijftig kilobyte, dus we knijpen liever in de
# resolutie en de kwaliteit. 25 is de ondergrens.
TRAPPEN = [
    ("volle kwaliteit",   800, 30, 30, False),
    ("iets kleiner",      600, 32, 30, False),
    ("harder geknepen",   600, 34, 30, True),
    ("zuinigst",          480, 34, 30, True),
]


def duur_en_fps(ff: str, pad: pathlib.Path):
    """Leest de duur en het aantal beeldjes uit wat ffmpeg over het bestand zegt."""
    err = subprocess.run([ff, "-i", str(pad)], capture_output=True, text=True).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    sec = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0.0
    f = re.search(r"([\d.]+) fps", err)
    return sec, float(f.group(1)) if f else 0.0


def main():
    try:
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        print("!! geen ffmpeg: pip install imageio-ffmpeg  (%s)" % str(e)[:50])
        return 1

    items = json.loads((BASE / "content.json").read_text(encoding="utf-8"))
    if items and isinstance(items[0], str):
        print("!! content.json bevat nog alleen mapnamen; draai eerst build-manifest.py")
        return 1

    gemaakt = overgeslagen = 0
    voor = na = 0.0
    ingekort = []

    for item in items:
        naam = item.get("videocover")
        if not naam:
            continue
        bron = BASE / "werk" / item["slug"] / naam
        if not bron.exists():
            continue
        doel = bron.with_name(bron.stem + "-web.mp4")

        if doel.exists() and doel.stat().st_mtime >= bron.stat().st_mtime:
            item["videocover_licht"] = doel.name
            overgeslagen += 1
            continue

        sec, fps = duur_en_fps(FF, bron)
        bron_kb = bron.stat().st_size / 1024

        gelukt = None
        for label, breed, crf, max_fps, ruis in TRAPPEN:
            # scale='min(N,iw)':-2 verkleint alleen als het nodig is en nooit
            # omhoog. De -2 laat ffmpeg de hoogte uitrekenen op een even getal,
            # wat h264 vereist, en houdt zo de verhouding intact.
            filters = ("hqdn3d=3:2:4:4," if ruis else "") + "scale='min(%d,iw)':-2" % breed
            if fps and fps > max_fps:
                filters += ",fps=%d" % max_fps

            r = subprocess.run(
                [FF, "-y", "-loglevel", "error", "-i", str(bron),
                 "-t", str(MAX_SEC),
                 "-an",                                  # geluid eruit
                 "-vf", filters,
                 "-c:v", "libx264", "-crf", str(crf), "-preset", "slow",
                 "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart",              # begint met afspelen
                                                         # voordat alles binnen is
                 str(doel)], capture_output=True, text=True)
            if r.returncode != 0 or not doel.exists():
                print("  !! %s: %s" % (bron.name, (r.stderr or "").strip()[:70]))
                break
            gelukt = (label, doel.stat().st_size / 1024)
            if gelukt[1] <= DOEL_KB:
                break

        if not gelukt:
            continue

        label, doel_kb = gelukt

        # Groter dan het origineel? Dan was dat al beter gecodeerd dan wij het
        # kunnen. Weggooien en het origineel laten staan, anders maken we de
        # site zwaarder in plaats van lichter.
        if doel_kb >= bron_kb:
            doel.unlink()
            print("  %-44s %5.0f KB, origineel was al kleiner: gelaten"
                  % (bron.name, bron_kb))
            item.pop("videocover_licht", None)
            continue

        item["videocover_licht"] = doel.name
        voor += bron_kb
        na += doel_kb
        gemaakt += 1
        if sec > MAX_SEC + 0.1:
            ingekort.append((bron.name, sec))
        print("  %-44s %5.0f KB -> %4.0f KB   (%s)" % (
            doel.name, bron_kb, doel_kb, label))

    (BASE / "content.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\nkaartfilm: %d nieuw, %d al bij." % (gemaakt, overgeslagen))
    if gemaakt:
        print("Samen %.0f KB in plaats van %.0f KB (%.0f%% lichter)."
              % (na, voor, 100 - na / voor * 100 if voor else 0))
    if ingekort:
        print("\nAfgekapt op %d seconden, kijk of het loopje niet hapert:" % MAX_SEC)
        for naam, sec in ingekort:
            print("  - %s (was %.1fs)" % (naam, sec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
