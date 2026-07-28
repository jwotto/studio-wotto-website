#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Werkt content.json bij: alle content-items (projecten en blogs) MET hun kenmerken.

Gebruik:
  - Dubbelklik op tools/update-manifest.bat (Windows), of
  - Draai in een terminal:  python tools/build-manifest.py

Elke map in werk/ met een index.html die <meta name="wotto:type"> bevat,
telt als content-item. Mappen zonder die tag worden overgeslagen.

Een item met een ontbrekende coverfoto is nog niet af en wordt ook
overgeslagen, zodat er nooit een kapot kaartje op de site komt.

WAAROM STAAN DE KENMERKEN HIER IN, EN NIET ALLEEN DE MAPNAMEN?
Eerst stond in dit bestand alleen een lijstje mapnamen. De browser haalde
daarna alle 29 projectpagina's apart op om er de meta-tags uit te lezen, puur
om een kaartje te kunnen tekenen. Dat waren dus 29 verzoeken en ruim een
megabyte aan HTML voordat er één kaart in beeld kwam, en op een trage
telefoonverbinding zag je de pagina daardoor zichtbaar verspringen.

Nu leest dit script die meta-tags één keer, hier, en zet het resultaat in
content.json. De browser heeft dan één klein bestand nodig in plaats van
dertig grote. De meta-tags in de pagina's blijven de bron: je verandert nog
altijd de pagina zelf en draait daarna de bouwstap. Dit bestand is dus nooit
iets om met de hand te wijzigen.
"""
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent.parent
WERK = BASE / "werk"

# De kenmerken die een kaartje nodig heeft. Alles wat hier niet in staat
# (zoals wotto:auteur) hoort bij de pagina zelf en niet bij het overzicht.
JA = re.compile(r"^(ja|true|1)$", re.I)


def meta(txt: str, naam: str) -> str:
    """Haalt <meta name="wotto:naam" content="..."> uit de HTML.

    De tags in de pagina's staan netjes uitgelijnd met meerdere spaties,
    vandaar de \\s+ in plaats van één spatie.
    """
    m = re.search(r'<meta\s+name="wotto:%s"\s+content="([^"]*)"' % re.escape(naam), txt)
    return m.group(1).strip() if m else ""


def slugify(s: str) -> str:
    return re.sub(r"\s+", "-", s.strip().lower())


def lees(folder: pathlib.Path):
    """Geeft (item_of_None, reden_om_over_te_slaan) terug."""
    index = folder / "index.html"
    if not index.exists():
        return None, None                       # geen pagina: stilletjes overslaan
    try:
        txt = index.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None, None
    if "wotto:type" not in txt:
        return None, None                       # gewone pagina, geen content-item

    cover = meta(txt, "cover") or "cover.jpg"
    if not (folder / cover).exists():
        return None, "coverfoto %s ontbreekt nog" % cover

    videocover = meta(txt, "videocover")
    if videocover and not (folder / videocover).exists():
        videocover = ""                         # filmpje weg? dan gewoon de foto

    return {
        "slug": folder.name,
        "type": (meta(txt, "type") or "project").lower(),
        "pilaar": meta(txt, "pilaar").lower(),
        "subjects": [slugify(s) for s in meta(txt, "subjects").split(",") if s.strip()],
        "titel": meta(txt, "titel") or folder.name,
        "excerpt": meta(txt, "excerpt"),
        "datum": meta(txt, "datum"),
        "featured": bool(JA.match(meta(txt, "featured"))),
        "huur": bool(JA.match(meta(txt, "huur"))),
        "cover": cover,
        "videocover": videocover,
    }, None


def main():
    if not WERK.is_dir():
        raise SystemExit("map werk/ niet gevonden naast tools/")

    items, skipped = [], []
    for p in sorted(WERK.iterdir()):
        if not p.is_dir() or p.name.startswith((".", "_")):
            continue
        item, reden = lees(p)
        if item:
            items.append(item)
        elif reden:
            skipped.append((p.name, reden))

    # Nieuwste eerst, net zoals de kaartenlijsten het tonen. Dan is de volgorde
    # in dit bestand meteen de volgorde op de site en hoef je nergens te zoeken.
    items.sort(key=lambda i: (i["datum"] or "", i["slug"]), reverse=True)

    (BASE / "content.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("content.json bijgewerkt: %d item(s)" % len(items))
    for i in items:
        vlag = " (uitgelicht)" if i["featured"] else ""
        film = " (filmpje op de kaart)" if i["videocover"] else ""
        print("  - %-38s %-8s %s%s%s" % (i["slug"], i["type"], i["datum"], vlag, film))
    if skipped:
        print("\nNog niet klaar, dus niet op de site gezet:")
        for name, reden in skipped:
            print("  - %s: %s" % (name, reden))


if __name__ == "__main__":
    main()
