#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bouwt de structured data en de sitemap.

Structured data is een blokje JSON in de <head> waarmee je aan Google en aan
AI-assistenten zoals ChatGPT en Claude vertelt WAT je bent, niet alleen wat er
op de pagina staat. Zonder dit moeten ze het uit je lopende tekst raden.

Draaien:  python tools/build-seo.py

Alles tussen de MARKER-regels wordt opnieuw gegenereerd. Pas dus dit bestand
aan, niet de HTML, anders ben je je wijziging de volgende keer kwijt.
"""
import json, pathlib, re, sys

SITE = "https://www.studiowotto.com"
BASE = pathlib.Path(__file__).resolve().parent.parent
ORG = SITE + "/#organization"
WEB = SITE + "/#website"

START = "<!-- structured data: gemaakt door tools/build-seo.py, niet met de hand aanpassen -->"
EIND = "<!-- /structured data -->"

# ---------------------------------------------------------------- je bedrijf
# Dit is de plek om je gegevens aan te passen.
ORGANISATIE = {
    "@type": "Organization",
    "@id": ORG,
    "name": "Studio Wotto",
    "url": SITE + "/",
    "email": "info@studiowotto.com",
    "logo": {"@type": "ImageObject", "url": SITE + "/favicons/web-app-manifest-512x512.png",
             "width": 512, "height": 512},
    "image": SITE + "/favicons/web-app-manifest-512x512.png",
    "description": "Studio Wotto maakt interactieve muziekinstallaties, muzikale webapps "
                   "en podiumtechniek. Van festivalinstallatie tot videosynthesizer.",
    "areaServed": {"@type": "Country", "name": "Nederland"},
    # sameAs: alle plekken waar Studio Wotto te vinden is. Hier bouwt Google
    # zijn beeld van "wie is Studio Wotto" mee op.
    #
    # Jan-Willem is het merk, dus zijn profielen staan hier bewust ook bij.
    # Ze staan daarnaast bij hem als persoon (zie founder), en die twee zijn
    # via founder/worksFor aan elkaar geknoopt. Jaimy's persoonlijke
    # profielen staan alleen bij haar, niet bij het bedrijf.
    "sameAs": [
        "https://www.linkedin.com/company/studio-wotto/",
        "https://www.instagram.com/studio.wotto/",
        "https://www.linkedin.com/in/jan-willem-otto/",
        "https://www.instagram.com/jw.otto/",
        "https://www.youtube.com/@jwotto",
        "https://x.com/otto_jw",
        "https://www.reddit.com/user/jw-otto/",
    ],
    # knowsAbout: hiermee vertel je waar je verstand van hebt. Juist AI-assistenten
    # gebruiken dit om te bepalen of jij het antwoord bent op een vraag.
    "knowsAbout": [
        "Interactieve installaties", "Interactieve muziekinstallaties",
        "Muzikale webapps", "Podiumtechniek", "Videosynthesizers",
        "Muziektechnologie", "Interactieve kunst", "Creatieve technologie",
        "Phygital marketing", "Workshops muziek en techniek",
    ],
    "founder": [
        {"@type": "Person", "@id": SITE + "/over-ons/#jan-willem", "name": "Jan-Willem Otto",
         "alternateName": "JWOTTO",          # de artiestennaam, zo knoop je die aan de persoon
         "jobTitle": "Creatief leider & innovatieve technoloog", "email": "jan@studiowotto.com",
         "telephone": "+31643474328", "worksFor": {"@id": ORG},
         "sameAs": ["https://www.linkedin.com/in/jan-willem-otto/",
                    "https://www.instagram.com/jw.otto/",
                    "https://www.youtube.com/@jwotto",
                    "https://x.com/otto_jw",
                    "https://www.reddit.com/user/jw-otto/"]},
        {"@type": "Person", "@id": SITE + "/over-ons/#jaimy", "name": "Jaimy Kortenhoff",
         "jobTitle": "Projectmanager & communicatie", "email": "jaimy@studiowotto.com",
         "telephone": "+31651598367", "worksFor": {"@id": ORG},
         "sameAs": ["https://www.linkedin.com/in/jaimy-kortenhoff-384105319/",
                    "https://www.instagram.com/jaimykortenhoff/",
                    "https://www.youtube.com/user/jaimykortenhoff"]},
    ],
}

WEBSITE = {"@type": "WebSite", "@id": WEB, "url": SITE + "/", "name": "Studio Wotto",
           "publisher": {"@id": ORG}, "inLanguage": "nl-NL"}

# ------------------------------------------------- wat is elke pagina er een
# Service = een dienst die je verkoopt. Dit zijn je verkooppagina's.
DIENSTEN = {
    "interactieve-installaties": "Interactieve installatie",
    "muzikale-webapps": "Muzikale webapp",
    "podium": "Podiumtechniek",
    "workshops": "Workshop muziek en techniek",
}
VERZAMELINGEN = ["blog", "projecten", "onderwerp"]     # en alles onder onderwerp/


def leesmeta(h, naam, attr="name"):
    m = re.search(r'%s="%s"\s+content="([^"]*)"' % (attr, re.escape(naam)), h)
    return m.group(1) if m else None


def paginadata(f):
    h = f.read_text(encoding="utf-8")
    rel = f.relative_to(BASE).as_posix().replace("index.html", "")
    return h, rel, {
        "titel": (re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1].strip(),
        "desc": leesmeta(h, "description") or "",
        "url": SITE + "/" + rel,
    }


def bouw(f):
    """Geeft het juiste schema terug voor deze pagina, of None."""
    h, rel, d = paginadata(f)
    map0 = rel.split("/")[0] if rel else ""

    if rel == "":                                        # homepage
        return {"@context": "https://schema.org", "@graph": [ORGANISATIE, WEBSITE]}

    if map0 == "contact":
        return {"@context": "https://schema.org", "@type": "ContactPage", "url": d["url"],
                "name": d["titel"], "description": d["desc"], "about": {"@id": ORG},
                "inLanguage": "nl-NL", "isPartOf": {"@id": WEB}}

    if map0 == "over-ons":
        return {"@context": "https://schema.org", "@type": "AboutPage", "url": d["url"],
                "name": d["titel"], "description": d["desc"], "about": {"@id": ORG},
                "inLanguage": "nl-NL", "isPartOf": {"@id": WEB},
                "mainEntity": {"@id": ORG}}

    if map0 in DIENSTEN:
        return {"@context": "https://schema.org", "@type": "Service", "@id": d["url"] + "#dienst",
                "name": d["titel"].split("|")[0].strip(), "serviceType": DIENSTEN[map0],
                "description": d["desc"], "url": d["url"], "provider": {"@id": ORG},
                "areaServed": {"@type": "Country", "name": "Nederland"},
                "inLanguage": "nl-NL"}

    if map0 in VERZAMELINGEN:
        return {"@context": "https://schema.org", "@type": "CollectionPage", "url": d["url"],
                "name": d["titel"].split("|")[0].strip(), "description": d["desc"],
                "isPartOf": {"@id": WEB}, "inLanguage": "nl-NL", "publisher": {"@id": ORG}}

    if map0 == "werk":
        soort = leesmeta(h, "wotto:type")
        titel = leesmeta(h, "wotto:titel") or d["titel"]
        cover = leesmeta(h, "wotto:cover")
        datum = leesmeta(h, "wotto:datum")
        excerpt = leesmeta(h, "wotto:excerpt") or d["desc"]
        onderwerpen = [s.strip() for s in (leesmeta(h, "wotto:subjects") or "").split(",") if s.strip()]
        beeld = d["url"] + cover if cover else None

        typ = {"blog": "Article", "workshop": "Course"}.get(soort, "CreativeWork")
        node = {"@context": "https://schema.org", "@type": typ, "@id": d["url"] + "#item",
                "name": titel, "description": excerpt, "url": d["url"], "inLanguage": "nl-NL"}
        if beeld:
            node["image"] = beeld
        if onderwerpen:
            node["keywords"] = ", ".join(onderwerpen)
        if typ == "Article":
            node["headline"] = titel
            node["author"] = {"@id": ORG}
            node["publisher"] = {"@id": ORG}
            if datum:
                node["datePublished"] = datum
        elif typ == "Course":
            node["provider"] = {"@id": ORG}
        else:
            node["creator"] = {"@id": ORG}
            if datum:
                node["dateCreated"] = datum

        kruimels = {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Werk", "item": SITE + "/projecten/"},
            {"@type": "ListItem", "position": 3, "name": titel, "item": d["url"]}]}
        return {"@context": "https://schema.org", "@graph": [node, kruimels]}

    return None


def schrijf(f, data):
    h = f.read_text(encoding="utf-8")
    tekst = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    blok = "%s\n<script type=\"application/ld+json\">\n%s\n</script>\n%s\n" % (START, tekst, EIND)

    if START in h:
        h = re.sub(re.escape(START) + r".*?" + re.escape(EIND) + r"\n?", blok, h, flags=re.S)
    else:
        h = h.replace("</head>", blok + "</head>", 1)
    f.write_text(h, encoding="utf-8")


def main():
    SKIP = (".git", "oude blogs", "moodboard", "node_modules", "_site", "partials")
    pages = [f for f in sorted(BASE.rglob("*.html")) if not any(s in str(f) for s in SKIP)]

    per_soort, urls = {}, []
    for f in pages:
        data = bouw(f)
        if not data:
            print("  ?  geen type bekend: %s" % f.relative_to(BASE))
            continue
        schrijf(f, data)
        node = data.get("@graph", [data])[0]
        soort = node.get("@type", "?")
        per_soort[soort] = per_soort.get(soort, 0) + 1
        urls.append(SITE + "/" + f.relative_to(BASE).as_posix().replace("index.html", ""))

    print("structured data toegevoegd aan %d pagina's:" % len(urls))
    for k, v in sorted(per_soort.items(), key=lambda x: -x[1]):
        print("   %-18s %d" % (k, v))

    # sitemap
    regels = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
              "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    for u in sorted(urls, key=lambda u: (u.count("/"), u)):
        prio = "1.0" if u.rstrip("/") == SITE else ("0.8" if u.count("/") == 4 else "0.6")
        regels.append("  <url><loc>%s</loc><priority>%s</priority></url>" % (u, prio))
    regels.append("</urlset>")
    (BASE / "sitemap.xml").write_text("\n".join(regels) + "\n", encoding="utf-8")
    print("\nsitemap.xml: %d URL's" % len(urls))


if __name__ == "__main__":
    sys.exit(main())
