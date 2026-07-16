#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bouwt alles wat met onderwerpen (genres) te maken heeft.

Draaien:  python tools/build-onderwerpen.py

Dit bestand is de ENIGE plek waar je de lijst met onderwerpen aanpast. Een
onderwerp toevoegen, hernoemen of weghalen doe je hieronder in ONDERWERPEN,
daarna dit script draaien. Het regelt dan:

  1. /onderwerp/<slug>/     de pagina zelf, met de juiste tekst en SEO
  2. de chip-wolken         op de homepage, op /onderwerp/ en op elke
                            onderwerp-pagina (die van zichzelf is 'vol')
  3. de chips op elk item   gelezen uit wotto:subjects, dus die kunnen niet
                            meer uit de pas lopen met de metatags
  4. lege mappen            een onderwerp dat hier weg is, wordt opgeruimd

Welk item welk onderwerp krijgt, staat NIET hier maar in de
<meta name="wotto:subjects"> van het item zelf.
"""
import json, pathlib, re, shutil, sys

SITE = "https://studiowotto.com"
BASE = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- de lijst
# Volgorde bepaalt de volgorde van de chips. Naam is wat mensen zien,
# de map wordt daaruit afgeleid (kleine letters, streepjes).
ONDERWERPEN = [
    ("Gamification", "ph-trophy",
     "Werk waarin spelprincipes het leren of de beleving versterken. Punten als middel, "
     "niet als doel: is het spel zonder punten niet leuk, dan helpen punten niet."),
    ("Educatie", "ph-student",
     "Werk voor het onderwijs. Workshops en installaties waarmee leerlingen niet over "
     "techniek horen, maar er zelf iets mee maken."),
    ("Muziektechnologie", "ph-waveform",
     "Waar muziek en techniek elkaar raken. Instrumenten, machines en tools die geluid "
     "maken, vaak zelf gebouwd omdat ze nog niet bestonden."),
    ("Muziekinstrumenten", "ph-guitar",
     "Instrumenten die nog niet bestonden. Zelf gebouwd, met een eigen bediening en een "
     "eigen geluid, voor wie iets wil spelen dat niemand anders heeft."),
    ("Interactieve kunst", "ph-palette",
     "Kunst die reageert. Installaties waarin het publiek het werk afmaakt, en die pas "
     "tot leven komen als iemand anders eraan begint."),
    ("Geluidsontwerp", "ph-speaker-high",
     "Geluid als materiaal. Van ritmes programmeren met tikkende motoren tot een "
     "tekening die je kunt horen."),
    ("Creatieve technologie", "ph-wrench",
     "Techniek als creatief gereedschap. Van 3D-ontwerp en printen tot circuit bending: "
     "kijken wat er gebeurt als je verder gaat dan waar iets voor bedoeld was."),
    ("Games", "ph-game-controller",
     "Games en gametechniek. Van een arcadekast waarin jij de avatar bent tot een game "
     "die je in een middag zelf leert bouwen."),
    ("Phygital", "ph-cube",
     "Waar fysiek en digitaal in elkaar overlopen. Teken iets op papier en zie het "
     "bewegen op het scherm, of scan een code en je telefoon wordt de controller."),
    # Merkactivering en Interactieve reclame lijken op elkaar, maar zijn het niet:
    # het verschil is tijdelijk tegenover blijvend. Hou dat verschil in de tekst,
    # anders vechten deze twee pagina's om hetzelfde zoekwoord.
    ("Merkactivering", "ph-megaphone",
     "Een merk dat ergens even neerstrijkt. Een installatie op een festival, beurs of "
     "event, met jouw merk erop, die na afloop weer meegaat. Meestal te huur."),
    # Museum en Interactieve reclame hebben nu nog geen items. Ze staan er
    # bewust in omdat er werk aan komt. Zolang ze leeg zijn tonen ze de
    # boodschap uit data-empty in plaats van een gat.
    ("Museum", "ph-bank",
     "Interactieve installaties voor musea en tentoonstellingen, waarmee bezoekers zelf "
     "aan de slag gaan in plaats van alleen kijken."),
    ("Interactieve reclame", "ph-storefront",
     "Merkbeleving die blijft staan. In een winkel, horeca of etalage, waar "
     "voorbijgangers stoppen en meedoen in plaats van doorlopen. Op maat gebouwd."),
    ("Festival", "ph-confetti",
     "Installaties die het festivalterrein op gaan. Druk, kort, en zonder uitleg: het "
     "moet meteen duidelijk zijn hoe het werkt."),
]

PILAAR = {"installaties": ("Interactieve installaties", "interactieve-installaties"),
          "webapps": ("Muzikale webapps & games", "muzikale-webapps"),
          "podium": ("Podium & instrumenten", "podium")}


def slug(naam):
    return naam.strip().lower().replace(" ", "-")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def lees_items():
    """Alle items met hun pijler en onderwerpen, uit de metatags zelf."""
    slugs = json.load(open(BASE / "content.json", encoding="utf-8"))
    uit = []
    for s in slugs:
        h = (BASE / "werk" / s / "index.html").read_text(encoding="utf-8")
        g = lambda k: (re.search(r'wotto:%s"\s+content="([^"]*)"' % k, h) or [None, ""])[1]
        uit.append({"slug": s, "pilaar": g("pilaar"), "cover": g("cover"),
                    "subs": [x.strip() for x in g("subjects").split(",") if x.strip()]})
    return uit


def wolk(actief, prefix):
    """De rij chips. Het actieve onderwerp is een span, niet een link."""
    r = []
    for naam, _, _ in ONDERWERPEN:
        if naam == actief:
            r.append('        <span class="chip chip--on">%s</span>' % esc(naam))
        else:
            r.append('        <a class="chip" href="%s%s/">%s</a>' % (prefix, slug(naam), esc(naam)))
    return "\n".join(r)


SJABLOON = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel} | Studio Wotto</title>
<link rel="canonical" href="{url}">
<meta name="description" content="{desc}">

<!-- Deel-thumbnail (LinkedIn, WhatsApp, enz.) -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="Studio Wotto">
<meta property="og:locale" content="nl_NL">
<meta property="og:title" content="{titel}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{beeld}">
<meta name="twitter:card" content="summary_large_image">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/bold/style.css">
<link rel="stylesheet" href="../../css/styles.css">
<!-- Favicon -->
<link rel="icon" href="../../favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" href="../../favicons/favicon-96x96.png" sizes="96x96">
<link rel="apple-touch-icon" href="../../favicons/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<meta name="theme-color" content="#FF5757">
</head>
<body>

<!-- Golf-sprite -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <symbol id="wave" viewBox="0 0 2400 80" preserveAspectRatio="none">
    <path d="M0,40 C150,8 450,8 600,40 C750,72 1050,72 1200,40 C1350,8 1650,8 1800,40 C1950,72 2250,72 2400,40 L2400,80 L0,80 Z"/></symbol>
</defs></svg>

<div data-include="header"></div>

<!-- ============ ONDERWERP (blauw) ============ -->
<section class="section section--blue" data-nav="light">
  <i class="ph-bold {icon} deco" style="top:14%;right:7%;font-size:56px"></i>
  <div class="container">
    <div class="section-head">
      <p class="kicker">Onderwerp</p>
      <h1>{titel}</h1>
      <p class="lead">{desc}</p>
    </div>
    <div class="cloud">
{wolk}
    </div>
  </div>
</section>

<!-- ============ ALLES OVER DIT ONDERWERP (zon) ============ -->
<section class="section section--sun" data-nav="dark">
  <div class="wave-top" aria-hidden="true"><svg preserveAspectRatio="none"><use href="#wave"/></svg></div>
  <div class="container">
    <div class="section-head"><h2>Alles over {klein}</h2></div>
    <div class="grid" data-list="all" data-subject="{slug}"
         data-empty="Hier staat nog niets. Kijk eens bij een van de andere onderwerpen hierboven."></div>
  </div>
</section>

<!-- ============ GET IN TOUCH (koraal) ============ -->
<section class="section section--coral touch" data-nav="light">
  <div class="wave-top" aria-hidden="true"><svg preserveAspectRatio="none"><use href="#wave"/></svg></div>
  <div class="container">
    <p class="kicker">Get in touch</p>
    <h2>Iets moois maken samen?</h2>
    <p class="lead">Zoiets voor jouw plek? Bel of mail gerust, we denken graag mee.</p>
    <div class="touch__pills">
      <a class="btn btn--light" href="mailto:info@studiowotto.com"><i class="ph-bold ph-envelope-simple"></i> info@studiowotto.com</a>
      <a class="btn btn--light" href="tel:+31643474328"><i class="ph-bold ph-phone"></i> +31 6 43474328</a>
    </div>
  </div>
</section>

<div data-include="footer"></div>

<script src="../../js/site.js"></script>
</body>
</html>
"""


def main():
    items = lees_items()
    namen = [n for n, _, _ in ONDERWERPEN]

    # 1. de onderwerp-pagina's
    for naam, icon, desc in ONDERWERPEN:
        s = slug(naam)
        hoort_bij = [i for i in items if naam in i["subs"]]
        # deel-thumbnail: pak de cover van het eerste item dat dit onderwerp heeft
        beeld = ("%s/werk/%s/%s" % (SITE, hoort_bij[0]["slug"], hoort_bij[0]["cover"])
                 if hoort_bij and hoort_bij[0]["cover"]
                 else "%s/favicons/web-app-manifest-512x512.png" % SITE)
        d = BASE / "onderwerp" / s
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(SJABLOON.format(
            titel=esc(naam), desc=esc(desc), url="%s/onderwerp/%s/" % (SITE, s),
            beeld=beeld, icon=icon, wolk=wolk(naam, "../"), klein=naam.lower(), slug=s,
        ), encoding="utf-8")
        print("  %-24s %d item(s)" % (s, len(hoort_bij)))

    # 2. lege mappen opruimen
    for d in sorted((BASE / "onderwerp").iterdir()):
        if d.is_dir() and d.name not in [slug(n) for n in namen]:
            shutil.rmtree(d)
            print("  verwijderd: onderwerp/%s/ (staat niet meer in de lijst)" % d.name)

    # 3. de chip-wolken elders
    for pad, prefix in [("index.html", "onderwerp/"), ("onderwerp/index.html", "")]:
        f = BASE / pad
        h = f.read_text(encoding="utf-8")
        h2, n = re.subn(r'(<div class="cloud">\n).*?(\n    </div>)',
                        lambda m: m.group(1) + wolk(None, prefix) + m.group(2), h, count=1, flags=re.S)
        if n != 1:
            print("  !! chip-wolk niet gevonden in %s" % pad)
        else:
            f.write_text(h2, encoding="utf-8")
            print("  chip-wolk bijgewerkt: %s" % pad)

    # 4. de chips op elk item, uit wotto:subjects
    for i in items:
        f = BASE / "werk" / i["slug"] / "index.html"
        h = f.read_text(encoding="utf-8")
        # Een item hoeft geen pijler te hebben. Een blog over jureren op een
        # festival gaat nergens over installaties, webapps of podium. Zonder
        # deze controle kreeg zo'n item een lege chip naar "../..//".
        r = []
        if i["pilaar"] in PILAAR:
            label, plink = PILAAR[i["pilaar"]]
            r.append('        <a class="chip" href="../../%s/">%s</a>' % (plink, esc(label)))
        elif i["pilaar"]:
            print("  !! %s heeft onbekende pijler: %s" % (i["slug"], i["pilaar"]))
        for s in i["subs"]:
            if s not in namen:
                print("  !! %s heeft onbekend onderwerp: %s" % (i["slug"], s))
                continue
            r.append('        <a class="chip" href="../../onderwerp/%s/">%s</a>' % (slug(s), esc(s)))
        # Let op de vorm van deze regex: een item kan NUL chips hebben (geen
        # pijler en geen onderwerpen). Dan staat er <div ...></div> met alleen
        # witruimte ertussen, en een patroon dat een regeleinde verwacht mist 'm.
        binnenin = ("\n" + "\n".join(r) + "\n      ") if r else "\n      "
        h2, n = re.subn(r'(<div class="detail-chips">).*?(</div>)',
                        lambda m: m.group(1) + binnenin + m.group(2), h, count=1, flags=re.S)
        if n != 1:
            print("  !! detail-chips niet gevonden in %s" % i["slug"])
        else:
            f.write_text(h2, encoding="utf-8")

    print("\n%d onderwerpen, %d items van chips voorzien" % (len(ONDERWERPEN), len(items)))


if __name__ == "__main__":
    sys.exit(main())
