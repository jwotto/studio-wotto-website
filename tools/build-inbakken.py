#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bakt de header, de footer en de kaartenlijsten echt in de HTML.

    python tools/build-inbakken.py

WAAROM DIT BESTAAT
Tot nu toe stonden er gaten in de pagina's die JavaScript pas na het laden
vulde: een leeg <div data-include="header">, een leeg <div data-include="footer">
en lege kaartenstroken. Dat had drie nadelen.

  1. De pagina versprong. De browser tekende eerst de pagina zonder header en
     zonder kaarten, en propte ze er daarna in. Alles eronder schoof dan naar
     beneden. Google meet dat als CLS en gaf er 0,467 voor, waar 0,1 de grens is.
  2. Het was traag. Voor de kaarten werden alle projectpagina's apart opgehaald,
     puur om de meta-tags te lezen. Dat is nu opgelost in build-manifest.py.
  3. Wie geen JavaScript uitvoert zag een pagina zonder menu en zonder
     projecten. Google zelf draait je JavaScript wel, maar de AI-assistenten
     die tegenwoordig websites lezen doen dat vaak niet.

Na deze stap staat alles gewoon in het bestand. Geen gat, geen versprong, en
iedereen ziet dezelfde pagina.

BLIJFT HET AANPASBAAR?
Ja, en dat is het hele punt van de markeringen die je in de HTML terugziet:

    <!--ingebakken:header--> ... <!--/ingebakken:header-->

Dit script zoekt die markeringen en vervangt wat ertussen staat. Je kunt het dus
zo vaak draaien als je wilt zonder dat het zich opstapelt. Staat de oude
plekhouder <div data-include="header"></div> er nog, dan wordt die de eerste keer
vervangen door zo'n blok.

LET OP BIJ HET WERKEN AAN DE SITE
Pas je partials/header.html of partials/footer.html aan, of voeg je een blog toe,
dan zie je dat niet meteen in de pagina's. Draai daarna:

    python tools/build.py

Dat is dezelfde gewoonte als bij de onderwerp-pagina's, die ook uit een sjabloon
worden geschreven. De plekhouder blijft trouwens werken: zet je op een nieuwe
pagina een leeg <div data-include="header"></div> en vergeet je te bouwen, dan
vult JavaScript hem alsnog. Je site is dus nooit stuk, alleen langzamer.
"""
import html as htmlmod
import json
import pathlib
import posixpath
import re
import sys
import urllib.parse

# Alleen nodig om de maat van een posterbeeld te lezen, zodat er width en height
# op kunnen en de pagina niet verspringt. Ontbreekt Pillow, dan gaat de rest
# gewoon door.
try:
    from PIL import Image
except ImportError:
    Image = None

BASE = pathlib.Path(__file__).resolve().parent.parent

# Mappen die geen echte site-pagina's bevatten.
NEGEER = {"partials", "tools", "afbeeldingen", "moodboard", "logo's",
          "logo's klanten", "favicons", "css", "js", ".git", ".astro",
          ".github", "node_modules", "oude blogs en pagina's"}

PILAAR_LABEL = {
    "installaties": "Interactieve installaties",
    "webapps": "Muzikale webapps & games",
    "podium": "Podium & instrumenten",
}


def esc(s: str) -> str:
    """Zelfde ontsnapping als esc() in js/site.js, zodat de HTML identiek is."""
    return (s or "").replace("&", "&amp;").replace("<", "&lt;") \
                    .replace(">", "&gt;").replace('"', "&quot;")


def rel(van_map: str, naar: str) -> str:
    """Pad van 'naar' (gezien vanaf de site-root) gezien vanaf map 'van_map'.

    Voor een pagina in werk/ramses3000/ wordt werk/side-quest-rave/ dus
    ../side-quest-rave/. Root-absolute paden (/werk/...) zouden korter zijn,
    maar dan breekt de GitHub-preview, want die staat in een submap.

    De afsluitende schuine streep blijft staan: /werk/x/ en /werk/x zijn voor
    een webserver twee adressen, en die eerste is de onze.
    """
    slash = naar.endswith("/")
    p = posixpath.relpath(posixpath.normpath(naar), van_map or ".")
    return p + "/" if slash and not p.endswith("/") else p


# ---------------------------------------------------------------- partials


def element(txt: str, start: int, tag: str) -> str:
    """Het hele element vanaf 'start', inclusief geneste tags.

    Telt <tag ... en </tag mee tot de teller weer op nul staat. Dat kan omdat we
    op één specifieke tagnaam letten: een <img> binnen een <header> stoort niet,
    en een header in een header bestaat niet.
    """
    diepte, i = 0, start
    op = re.compile(r"<%s\b" % re.escape(tag), re.I)
    dicht = re.compile(r"</%s\s*>" % re.escape(tag), re.I)
    while i < len(txt):
        m_op, m_dicht = op.search(txt, i), dicht.search(txt, i)
        if not m_dicht:
            raise SystemExit("partial %s: sluit-tag </%s> niet gevonden" % (tag, tag))
        if m_op and m_op.start() < m_dicht.start():
            diepte += 1
            i = m_op.end()
        else:
            diepte -= 1
            i = m_dicht.end()
            if diepte == 0:
                return txt[start:i]
    raise SystemExit("partial %s: onbalans in de tags" % tag)


def lees_partial(naam: str) -> str:
    """De HTML van het element met data-partial uit partials/<naam>.html."""
    pad = BASE / "partials" / (naam + ".html")
    txt = pad.read_text(encoding="utf-8")
    m = re.search(r"<(\w+)([^>]*\bdata-partial\b[^>]*)>", txt)
    if not m:
        raise SystemExit("geen element met data-partial in %s" % pad.name)
    return element(txt, m.start(), m.group(1))


def verplaats_paden(part: str, van_map: str) -> str:
    """Rekent de ../-paden uit de partial om naar de map van de pagina.

    In de partial wijzen de paden met ../ terug naar de root, zodat het bestand
    ook los te bekijken is met Live Server. Op een echte pagina moet dat een
    ander aantal stappen worden. Dit is precies wat remap() in js/site.js deed,
    alleen nu één keer bij het bouwen in plaats van bij elke bezoeker.
    """
    def fix(m):
        attr, q, v = m.group(1), m.group(2), m.group(3)
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#|\?)", v, re.I) or not v:
            return m.group(0)                       # http:, mailto:, #anker: laten staan
        van_root = posixpath.normpath(posixpath.join("partials", v))
        return '%s=%s%s%s' % (attr, q, rel(van_map, van_root + ("/" if v.endswith("/") else "")), q)

    return re.sub(r'\b(src|href)=(")([^"]*)"', fix, part)


# ---------------------------------------------------------------- kaarten


def kaartfoto(item: dict) -> str:
    """De lichte WebP van tools/build-kaartbeeld.py, of anders het origineel.

    Zo werkt de site ook als die stap nog niet gedraaid heeft, en kun je een
    WebP weggooien zonder dat er een kapot plaatje achterblijft.
    """
    cover = pathlib.PurePosixPath(item["cover"])
    licht = cover.stem + "-kaart.webp"
    return licht if (BASE / "werk" / item["slug"] / licht).exists() else item["cover"]


def kopniveau(txt: str, tot: int) -> int:
    """Welk kopniveau hoort een kaartje hier te krijgen?

    Eén stapje onder de laatste kop die boven de lijst staat. Op de homepage
    staan de kaarten onder <h2>Recente blogs</h2>, dus worden het h3's. Op
    /blog/ komen ze direct onder de <h1>, en dan hoort er h2 te staan. Sla je
    een niveau over, dan keurt een toegankelijkheidstest dat af: wie met een
    schermlezer door de koppen springt, verdwaalt in zo'n gat.

    De koppen van kaartjes die er bij een vorige ronde al in gezet zijn tellen
    niet mee. Anders zou een tweede lijst zich richten naar de kaartkoppen van
    de eerste, en zakte het niveau bij elke bouwronde een stapje verder weg.
    """
    ervoor = re.sub(r"%s.*?%s" % (re.escape(MARK), re.escape(MARK_EIND)), "",
                    txt[:tot], flags=re.S)
    koppen = re.findall(r"<h([1-6])[\s>]", ervoor)
    return min(int(koppen[-1]) + 1, 6) if koppen else 3


def kaart(item: dict, van_map: str, in_carousel: bool, niveau: int = 3) -> str:
    """Eén kaartje, letterlijk dezelfde HTML als renderCard() in js/site.js.

    Het filmpje op de kaart bakken we NIET in. Of dat mag hangt af van de
    bezoeker: wie in zijn systeem heeft staan dat hij minder beweging wil
    (een echte instelling, onder andere tegen misselijkheid) hoort de stille
    foto te krijgen. Dat weet je hier niet. We zetten dus de foto in de HTML en
    laten data-video achter als briefje voor site.js, die het filmpje er daarna
    inzet als het mag. Verspringen kan daarbij niet, want .project__img heeft
    een vaste verhouding van 1/1.
    """
    if item["type"] == "project":
        onder = '<div class="project__theme">%s</div>' % esc(PILAAR_LABEL.get(item["pilaar"], ""))
    else:
        onder = '<p class="project__excerpt">%s</p>' % esc(item["excerpt"])

    url = rel(van_map, "werk/" + item["slug"] + "/")
    cover = rel(van_map, "werk/" + item["slug"] + "/" + kaartfoto(item))
    # De lichte versie van tools/build-kaartfilm.py als die er is. Staat er geen,
    # dan gewoon het origineel, zodat het ook werkt als die stap nog niet liep.
    film = item.get("videocover_licht") or item.get("videocover")
    video = (' data-video="%s"' % esc(rel(van_map, "werk/" + item["slug"] + "/" + film))
             ) if film else ""

    # width en height komen uit build-kaartbeeld.py. Ze zijn geen opsmuk: zonder
    # die twee weet de browser pas hoe hoog de foto wordt als hij binnen is, en
    # schuift alles eronder alsnog omlaag. De CSS zet er height:auto overheen,
    # dus de foto wordt er niet door uitgerekt.
    maat = item.get("kaartmaat")
    afmeting = ' width="%d" height="%d"' % tuple(maat) if maat else ""

    return ('<article class="project%s">'
            '<a href="%s">'
            '<div class="project__img"%s><img src="%s" alt="%s"%s loading="lazy"></div>'
            '<h%d class="project__titel">%s</h%d>%s'
            '</a></article>') % (
        " carousel__item" if in_carousel else "", url, video, cover,
        esc(item["titel"]), afmeting, niveau, esc(item["titel"]), niveau, onder)


def kies(items: list, attrs: dict) -> list:
    """Dezelfde selectie als renderCollections() in js/site.js."""
    types = [t.strip() for t in attrs.get("data-list", "").split(",") if t.strip()]
    lijst = [i for i in items if "all" in types or i["type"] in types]
    if attrs.get("data-featured") == "true":
        lijst = [i for i in lijst if i["featured"]]
    if attrs.get("data-huur") == "true":
        lijst = [i for i in lijst if i["huur"]]
    if attrs.get("data-pilaar"):
        lijst = [i for i in lijst if i["pilaar"] == attrs["data-pilaar"]]
    if attrs.get("data-subject"):
        lijst = [i for i in lijst if attrs["data-subject"] in i["subjects"]]
    # Nieuwste eerst. Python sorteert stabiel, net als JavaScript, dus items met
    # dezelfde datum houden de volgorde uit content.json.
    lijst = sorted(lijst, key=lambda i: i["datum"] or "", reverse=True)
    if attrs.get("data-limit", "").isdigit():
        lijst = lijst[:int(attrs["data-limit"])]
    return lijst


# ---------------------------------------------------------------- inbakken


MARK = "<!--ingebakken-->"
MARK_EIND = "<!--/ingebakken-->"


def bak_partials(txt: str, van_map: str, parts: dict) -> tuple:
    """Vervangt de plekhouders (of een eerder ingebakken blok) door de partial."""
    aantal = 0
    for naam, part in parts.items():
        blok = "<!--ingebakken:%s-->%s<!--/ingebakken:%s-->" % (
            naam, verplaats_paden(part, van_map), naam)
        patroon = re.compile(
            r'<div\s+data-include="%s"\s*>\s*</div>'                  # de oude plekhouder
            r'|<!--ingebakken:%s-->.*?<!--/ingebakken:%s-->' % (naam, naam, naam),
            re.S)
        txt, n = patroon.subn(lambda m: blok, txt)
        aantal += n
    return txt, aantal


# De regels die naar een vreemd domein wezen en het tekenen blokkeerden.
WEG_UIT_HEAD = [
    r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">',
    r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>',
    r'\s*<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">',
    r'\s*<link rel="stylesheet" href="https://unpkg\.com/@phosphor-icons[^"]*">',
]

# Alleen de latin-bestanden vooraf ophalen. Die heeft elke pagina nodig; latin-ext
# komt er alleen aan te pas bij een enkele letter in een naam en mag wachten.
VOORAF = ("fredoka-latin.woff2", "nunito-latin.woff2")


def bak_head(txt: str, van_map: str) -> tuple:
    """Haalt de blokkerende regels uit de <head> en zet de lettertypen vooraf klaar.

    De lettertypen en de iconen komen nu van onze eigen server. De <link>-regels
    naar fonts.googleapis.com en unpkg.com kunnen dus weg, en dat is precies de
    2.510 ms die Lighthouse als "verzoeken voor renderblokkering" aanwees.

    In plaats daarvan komt er een preload voor de twee woff2-bestanden. Zonder
    die regel ontdekt de browser het lettertype pas als hij de CSS gelezen heeft,
    en gaat hij dus twee keer op en neer. Met de preload begint hij er meteen aan
    en staat de juiste letter er vaak al bij de eerste tekening. Dat scheelt ook
    het zichtbare omklappen van vervangende letter naar merkletter.
    """
    n = 0
    for patroon in WEG_UIT_HEAD:
        txt, k = re.subn(patroon, "", txt)
        n += k

    if "rel=\"preload\"" not in txt:
        regels = "".join(
            '\n<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>'
            % rel(van_map, "fonts/" + f) for f in VOORAF)
        # Vlak voor de stylesheet, zodat de browser de lettertypen al ophaalt
        # terwijl hij de CSS nog aan het lezen is.
        m = re.search(r'\n?<link rel="stylesheet" href="[^"]*css/styles\.css">', txt)
        if m:
            txt = txt[:m.start()] + regels + txt[m.start():]
            n += 1
    return txt, n


def bak_iconen(txt: str, iconen: dict, ontbreekt: set) -> tuple:
    """Maakt van <i class="ph-bold ph-naam"> een <svg class="ph"> plus tekening.

    In de bronbestanden blijven de iconen staan als <i class="ph-bold ph-naam">,
    want dat is korter en beter te lezen dan een lap SVG. Deze stap zet ze om en
    plakt alleen de tekeningen die deze pagina nodig heeft bovenaan in een
    verborgen sprite. Een pagina met vier iconen sleept dus geen eenendertig
    tekeningen mee.

    Dezelfde vorm als de golf-sprite die er al stond: een <svg> van nul bij nul
    met de vormen in <defs>. Niet display:none, want dan weigeren sommige
    browsers de verwijzing te volgen.
    """
    def om(m):
        attrs = attrs_van(m.group(1))
        klassen = attrs.get("class", "").split()
        naam = next((k[3:] for k in klassen if k.startswith("ph-") and k != "ph-bold"), None)
        if not naam:
            return m.group(0)                       # geen icoon, met rust laten
        if naam not in iconen:
            ontbreekt.add(naam)
            return m.group(0)                       # laat staan; melding volgt onderaan
        rest = [k for k in klassen if not k.startswith("ph-")]
        stijl = ' style="%s"' % attrs["style"] if attrs.get("style") else ""
        return '<svg class="%s"%s aria-hidden="true"><use href="#ph-%s"/></svg>' % (
            " ".join(["ph"] + rest), stijl, naam)

    txt, n = re.subn(r"<i\s+([^>]*?)>\s*</i>", om, txt)

    # Welke tekeningen heeft deze pagina nodig? Uit de verwijzingen zelf, dus ook
    # de iconen die er bij een eerdere ronde al in gezet zijn.
    verwijzingen = set(re.findall(r'<use href="#ph-([a-z0-9-]+)"', txt))
    # Staat dit stuk te huur, dan hangt site.js er zelf een "Te huur"-chip aan met
    # een vrachtwagentje. Dat icoon staat nergens in de HTML, dus zou de sprite
    # het missen en bleef de chip leeg.
    if re.search(r'wotto:huur"\s+content="(?:ja|true|1)"', txt, re.I):
        verwijzingen.add("truck")
    nodig = sorted(verwijzingen & set(iconen))
    sprite = ""
    if nodig:
        vormen = "".join(
            '<symbol id="ph-%s" viewBox="%s">%s</symbol>' % (
                n_, iconen[n_]["viewBox"], iconen[n_]["body"]) for n_ in nodig)
        sprite = ('<!--ingebakken:iconen--><svg width="0" height="0" style="position:absolute"'
                  ' aria-hidden="true"><defs>%s</defs></svg><!--/ingebakken:iconen-->' % vormen)

    # Oude sprite eruit, nieuwe er direct na <body> in. De \s* ervoor is geen
    # netheid maar noodzaak: zonder dat blijft de regelovergang staan die we er
    # zelf voor zetten, en groeit het bestand bij elke bouwronde een regel.
    txt = re.sub(r"\s*<!--ingebakken:iconen-->.*?<!--/ingebakken:iconen-->", "", txt, flags=re.S)
    if sprite:
        m_body = re.search(r"<body[^>]*>", txt, re.I)
        if m_body:
            txt = txt[:m_body.end()] + "\n" + sprite + txt[m_body.end():]
    return txt, n


def bak_insluitingen(txt: str, van_map: str, ontbreekt: list) -> tuple:
    """Vervangt een Vimeo- of YouTube-iframe door een poster met afspeelknop.

    Zo'n ingesloten speler is duur. Op de pagina van side-quest-rave haalde hij
    312 KB aan JavaScript op van een vreemd domein, plús cookies van derden, en
    dat gebeurde al bij het laden. Die pagina scoorde 60 op snelheid met een LCP
    van 10,2 seconden, terwijl een blog zonder insluiting op 91 stond.

    Nu staat er een stilstaand beeld met een afspeelknop, en js/site.js zet de
    echte speler er pas in als iemand klikt. Dat is wat een bezoeker toch al
    verwacht, en wie niet klikt betaalt niets.

    De poster staat op onze eigen server (tools/haal-embedposters.py). Hem
    rechtstreeks van vimeocdn of ytimg laden zou het vreemde domein weer
    terugbrengen. Ontbreekt de poster, dan laten we het iframe met rust: liever
    een trage video dan geen video.

    YouTube wordt onderweg omgezet naar youtube-nocookie.com. Dat is dezelfde
    speler, maar hij zet pas een cookie als er echt gekeken wordt.
    """
    n = [0]

    def om(m):
        heel, attrs, klassen, src = m.group(0), m.group(1), m.group(2), m.group(4)
        titel = (re.search(r'\btitle="([^"]*)"', heel) or [None, "Video"])[1]

        vm = re.search(r"player\.vimeo\.com/video/(\d+)", src)
        yt = re.search(r"youtube(?:-nocookie)?\.com/embed/([\w-]+)", src)
        if vm:
            dienst, nummer = "vimeo", vm.group(1)
            speler = "https://player.vimeo.com/video/%s?autoplay=1" % nummer
        elif yt:
            dienst, nummer = "youtube", yt.group(1)
            speler = "https://www.youtube-nocookie.com/embed/%s?autoplay=1" % nummer
        else:
            return heel

        poster = "embed-%s-%s.webp" % (dienst, nummer)
        if not (BASE / van_map / poster).exists():
            ontbreekt.append("%s/%s" % (van_map, poster))
            return heel

        if Image is None:
            return heel                             # zonder maat geen fatsoenlijke poster
        with Image.open(BASE / van_map / poster) as im:
            breed, hoog = im.size

        n[0] += 1
        # De overige attributen blijven staan. Sommige insluitingen hebben
        # float-right en een eigen aspect-ratio in een style, en zonder die twee
        # springt de opmaak van het artikel om.
        nieuw_attrs = attrs.replace('class="%s"' % klassen,
                                    'class="%s video-embed--wacht"' % klassen, 1)
        return ('<div %s data-speler="%s">'
                '<img src="%s" alt="" width="%d" height="%d" loading="lazy" decoding="async">'
                '<button type="button" class="video-embed__knop" aria-label="Video afspelen: %s">'
                '<svg class="ph" aria-hidden="true"><use href="#ph-play"/></svg>'
                '</button></div>') % (nieuw_attrs, speler, poster, breed, hoog, esc(titel))

    # Het iframe zit in een div met de klasse video-embed, soms met extra
    # klassen erbij. Die hele div vervangen we, want de namaakspeler heeft zijn
    # eigen inhoud. Zonder iframe erin matcht dit niet meer, dus opnieuw draaien
    # is veilig.
    patroon = re.compile(
        r'<div\s+([^>]*\bclass="([^"]*\bvideo-embed\b[^"]*)"[^>]*)>'
        r'\s*(<iframe[^>]*\bsrc="([^"]+)"[^>]*>\s*</iframe>)\s*</div>', re.S)
    return patroon.sub(om, txt), n[0]


def bak_webp(txt: str, van_map: str) -> tuple:
    """Laat elke <img> naar de lichtere WebP wijzen als die er ligt.

    tools/build-artikelbeeld.py zet naast elke artikelfoto een .webp met exact
    dezelfde afmetingen, alleen beter gecomprimeerd: samen 15,1 MB in plaats van
    9,5 MB. Hier verhuist de verwijzing.

    Alleen de <img> in de pagina. De og:image en de structured data blijven naar
    de JPEG wijzen: sociale netwerken gaan wisselend om met WebP, en dat is nu
    net het plaatje dat je in een berichtje wilt zien verschijnen.
    """
    n = [0]

    def om(m):
        heel, src = m.group(0), m.group(1)
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|data:)", src, re.I):
            return heel
        if not re.search(r"\.(jpe?g|png)$", src, re.I):
            return heel
        webp = re.sub(r"\.(jpe?g|png)$", ".webp", src, flags=re.I)
        if not (BASE / van_map / urllib.parse.unquote(webp)).exists():
            return heel
        n[0] += 1
        return heel.replace('src="%s"' % src, 'src="%s"' % webp, 1)

    return re.sub(r'<img\s[^>]*\bsrc="([^"]+)"[^>]*>', om, txt, flags=re.S), n[0]


def bak_eerste_beeld(txt: str) -> tuple:
    """Het eerste beeld in <main> krijgt voorrang in plaats van luiheid.

    Alles op loading="lazy" zetten voelt zuinig, maar voor het beeld bovenaan is
    het juist verkeerd. Dat is meestal het grootste ding in beeld, en daar meet
    Google je LCP aan af. Een luie afbeelding wordt pas opgehaald als de browser
    klaar is met de rest van de pagina, dus je straft precies het beeld waar de
    bezoeker op wacht.

    Op museum-speelklok stond zelfs de eerste galerijfoto op lazy.

    Eén beeld per pagina, dus het risico is klein: staat het toch onder de vouw,
    dan heb je één afbeelding te vroeg opgehaald. fetchpriority="high" zegt er
    bovendien bij dat dit vóór de rest mag.
    """
    m_main = re.search(r"<main[^>]*>", txt)
    if not m_main:
        return txt, 0, None
    rest = txt[m_main.end():]

    # Het bovenste beeld hoeft geen <img> te zijn. Op museum-speelklok is het
    # grootste ding in beeld een zwevend filmpje, en dan is het posterbeeld
    # daarvan waar de bezoeker op wacht. Dus pakken we wat als eerste komt.
    m_img = re.search(r"<img\s[^>]*>", rest, re.S)
    m_vid = re.search(r'<video\s[^>]*\bposter="([^"]+)"[^>]*>', rest, re.S)

    if m_vid and (not m_img or m_vid.start() < m_img.start()):
        return txt, 0, m_vid.group(1)                # alleen vooraf klaarzetten

    if not m_img:
        return txt, 0, None

    tag = m_img.group(0)
    vooraf = (re.search(r'\bsrc="([^"]+)"', tag) or [None, None])[1]
    if 'fetchpriority="high"' in tag:
        return txt, 0, vooraf                        # al gedaan

    nieuw = re.sub(r'\s*loading="lazy"', "", tag)
    # decoding="async" zegt "je mag hiermee wachten", en dat is voor precies dit
    # beeld het verkeerde signaal.
    nieuw = re.sub(r'\s*decoding="async"', "", nieuw)
    nieuw = nieuw[:-1].rstrip() + ' fetchpriority="high">'

    start = m_main.end() + m_img.start()
    return txt[:start] + nieuw + txt[start + len(tag):], 1, vooraf


def bak_voorlader(txt: str, bron: str) -> str:
    """Zet het bovenste beeld al in de <head> klaar.

    fetchpriority alleen is niet genoeg. De browser ontdekt een beeld pas als
    hij bij die regel in de HTML aankomt, en dat is ná de stylesheet. Met een
    preload in de head begint hij er meteen aan. Op een trage verbinding scheelt
    dat een halve seconde op je LCP, en dat is precies het cijfer waar Google op
    let.

    Eén regel per pagina, tussen markeringen zodat opnieuw bouwen hem vervangt
    in plaats van er nog een bij te zetten.
    """
    blok = ('<!--ingebakken:voorlader--><link rel="preload" as="image" href="%s" '
            'fetchpriority="high"><!--/ingebakken:voorlader-->' % esc(bron)) if bron else ""
    txt = re.sub(r"\s*<!--ingebakken:voorlader-->.*?<!--/ingebakken:voorlader-->", "", txt, flags=re.S)
    if not blok:
        return txt
    m = re.search(r'\n?<link rel="stylesheet" href="[^"]*css/styles\.css">', txt)
    return txt[:m.start()] + "\n" + blok + txt[m.start():] if m else txt


def bak_luie_films(txt: str) -> tuple:
    """Zet automatisch spelende filmpjes op data-src, zodat ze pas laden in beeld.

    In de artikelen staan twee soorten filmpje. Eén met een afspeelknop
    (controls preload="none"): die kost pas iets als iemand erop drukt, en daar
    hoeven we niets aan te doen. En één die vanzelf speelt, als bewegende
    illustratie in de tekst. Die haalt de browser altijd binnen, ook als hij
    onderaan de pagina staat en je nooit zover scrolt.

    Over de hele site ging dat om 24 MB die ongevraagd binnenkwam, waarvan 4,7 MB
    op de pagina van aura-bouw-lasers alleen. Op traag 4G is dat het verschil
    tussen een pagina die staat en een pagina die blijft laden.

    De truc is klein: het adres verhuist van src naar data-src. Een <video>
    zonder src laat gewoon zijn poster zien, dus je ziet nog steeds een beeld.
    js/site.js zet het adres terug zodra het filmpje in de buurt van het scherm
    komt. Verspringen kan niet, want width en height staan er al op.
    """
    n = [0]

    def om(m):
        tag = m.group(0)
        # Geen autoplay? Dan staat er een afspeelknop op en laadt hij toch al
        # niets. Al omgezet? Dan niets te doen: dit script moet zo vaak te
        # draaien zijn als je wilt.
        if "autoplay" not in tag or "data-src=" in tag:
            return tag
        n[0] += 1
        return re.sub(r'\bsrc="', 'data-src="', tag, count=1)

    return re.sub(r"<video\s[^>]*>", om, txt, flags=re.S), n[0]


def bak_main(txt: str) -> tuple:
    """Zet alles tussen de header en de footer in een <main>.

    Zonder <main> weet hulpsoftware niet waar het menu ophoudt en de inhoud
    begint. Een schermlezer kan dan niet naar de inhoud springen, en dezelfde
    vraag hebben de AI-assistenten die een pagina willen samenvatten.
    Lighthouse noemt dat "het document heeft geen hoofdoriëntatiepunt".

    De header en de footer blijven er bewust buiten: dat zijn eigen landmarks,
    en de header moet buiten main blijven om sticky te kunnen zijn.
    """
    na_header = txt.find("<!--/ingebakken:header-->")
    voor_footer = txt.find("<!--ingebakken:footer-->")
    if na_header < 0 or voor_footer < 0 or voor_footer < na_header:
        return txt, 0
    na_header += len("<!--/ingebakken:header-->")
    binnen = txt[na_header:voor_footer]
    if "<main" in binnen:
        return txt, 0                               # al gedaan, of met de hand gezet
    return txt[:na_header] + '\n<main id="inhoud">' + binnen + '</main>\n' + txt[voor_footer:], 1


def attrs_van(s: str) -> dict:
    return {k.lower(): v for k, v in re.findall(r'([\w-]+)="([^"]*)"', s)}


def bak_lijsten(txt: str, van_map: str, items: list) -> tuple:
    """Vult elk element met data-list met de kaartjes die erin horen."""
    uit, cursor, aantal = [], 0, 0
    zoek = re.compile(r'<(\w+)([^>]*\bdata-list="[^"]*"[^>]*)>')
    while True:
        m = zoek.search(txt, cursor)
        if not m:
            uit.append(txt[cursor:])
            break
        tag, attrs = m.group(1), attrs_van(m.group(2))
        uit.append(txt[cursor:m.end()])

        # Waar eindigt de huidige inhoud? Of net na een eerder ingebakken blok,
        # of direct bij de sluit-tag als het element nog leeg is.
        na = m.end()
        if txt.startswith(MARK, na):
            eind = txt.find(MARK_EIND, na)
            if eind < 0:
                raise SystemExit("%s: %s zonder %s" % (van_map or "root", MARK, MARK_EIND))
            na = eind + len(MARK_EIND)
        sluit = txt.find("</%s>" % tag, na)
        if sluit < 0:
            raise SystemExit("%s: sluit-tag </%s> niet gevonden bij data-list" % (van_map or "root", tag))

        lijst = kies(items, attrs)
        in_car = "carousel__track" in attrs.get("class", "")
        niveau = kopniveau(txt, m.start())
        binnen = "".join(kaart(i, van_map, in_car, niveau) for i in lijst)
        if not binnen and attrs.get("data-empty"):
            binnen = '<p class="list-empty">%s</p>' % esc(attrs["data-empty"])
        uit.append(MARK + binnen + MARK_EIND)
        cursor = sluit
        aantal += len(lijst)
    return "".join(uit), aantal


def paginas():
    for p in sorted(BASE.rglob("*.html")):
        d = p.relative_to(BASE).parts
        if any(x in NEGEER for x in d):
            continue
        yield p


def main():
    items = json.loads((BASE / "content.json").read_text(encoding="utf-8"))
    if items and isinstance(items[0], str):
        raise SystemExit("content.json bevat nog alleen mapnamen.\n"
                         "Draai eerst: python tools/build-manifest.py")

    parts = {naam: lees_partial(naam) for naam in ("header", "footer")}

    iconen_pad = BASE / "tools" / "iconen.json"
    if not iconen_pad.exists():
        raise SystemExit("tools/iconen.json ontbreekt.\n"
                         "Draai eerst: python tools/haal-iconen.py")
    iconen = json.loads(iconen_pad.read_text(encoding="utf-8"))

    ontbreekt, geen_poster = set(), []
    tot_p = tot_k = tot_m = tot_i = tot_h = tot_f = tot_e = tot_b = tot_w = tot_bestanden = 0
    for pad in paginas():
        txt = oud = pad.read_text(encoding="utf-8")
        van_map = posixpath.dirname(pad.relative_to(BASE).as_posix())
        txt, n_h = bak_head(txt, van_map)
        txt, n_p = bak_partials(txt, van_map, parts)
        txt, n_e = bak_insluitingen(txt, van_map, geen_poster)
        txt, n_f = bak_luie_films(txt)
        txt, n_m = bak_main(txt)
        txt, n_w = bak_webp(txt, van_map)
        txt, n_k = bak_lijsten(txt, van_map, items)
        # Ná de lijsten: anders hangt het ervan af of de kaarten al in het
        # bestand stonden welk beeld hier het eerste is.
        txt, n_b, bovenste = bak_eerste_beeld(txt)
        txt = bak_voorlader(txt, bovenste)
        # De iconen als laatste: dan pakt hij ook de iconen mee die net uit de
        # header, de footer en de kaartjes in de pagina zijn gekomen.
        txt, n_i = bak_iconen(txt, iconen, ontbreekt)
        if txt != oud:
            pad.write_text(txt, encoding="utf-8")
            tot_bestanden += 1
        if n_p or n_k or n_m or n_i or n_f:
            print("  %-52s %d partial(s), %d kaart(en), %d icoon/iconen%s%s" % (
                pad.relative_to(BASE).as_posix(), n_p, n_k, n_i,
                ", %d luie film(s)" % n_f if n_f else "", ", main" if n_m else ""))
        tot_p += n_p
        tot_k += n_k
        tot_m += n_m
        tot_i += n_i
        tot_h += n_h
        tot_f += n_f
        tot_e += n_e
        tot_b += n_b
        tot_w += n_w

    print("\ningebakken: %d partial(s), %d kaart(en), %d icoon/iconen en %d nieuwe "
          "<main> in %d gewijzigd(e) bestand(en)"
          % (tot_p, tot_k, tot_i, tot_m, tot_bestanden))
    if tot_w:
        print("%d beeldverwijzing(en) staan op de lichtere WebP naast het origineel."
              % tot_w)
    if tot_b:
        # Let op: dit telt hoe vaak het attribuut gezet is, niet hoeveel er
        # veranderde. Op een lijstpagina worden de kaarten elke ronde opnieuw
        # opgebouwd, dus wordt het daar elke keer opnieuw gezet terwijl het
        # bestand identiek blijft.
        print("op %d pagina('s) staat het bovenste beeld op voorrang in plaats "
              "van lui laden." % tot_b)
    if tot_e:
        print("%d ingesloten video('s) wachten nu op een klik in plaats van dat ze "
              "meteen een speler van een vreemd domein ophalen." % tot_e)
    if geen_poster:
        print("\n!! posterbeeld ontbreekt, iframe blijft zoals het was:")
        for x in geen_poster:
            print("   %s" % x)
        print("   Draai: python tools/haal-embedposters.py")
    if tot_f:
        print("%d automatisch spelend(e) filmpje(s) wachten nu tot ze in beeld komen."
              % tot_f)
    if tot_h:
        print("head opgeruimd in %d geval(len): blokkerende <link>-regels weg, "
              "lettertypen vooraf klaargezet." % tot_h)
    if ontbreekt:
        print("\n!! deze iconen staan niet in tools/iconen.json en zijn dus blijven "
              "staan als <i>:\n   %s\n   Draai: python tools/haal-iconen.py"
              % ", ".join(sorted(ontbreekt)))
    if not tot_p:
        print("Let op: geen enkele header of footer gevonden. Staan de "
              "plekhouders er nog wel?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
