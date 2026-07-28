# Studio Wotto: de website

Platte HTML, CSS en een beetje JavaScript. **Geen Node, geen framework.** Je
opent een bestand, past het aan, en dat is wat er online staat.

Wel één commando: `python tools/build.py`. Dat zet de header, de footer en de
kaartjes in de pagina's, verkleint nieuwe foto's en werkt de sitemap bij. Draai
het na elke aanpassing, dan zie je met Live Server meteen het echte resultaat.
Waarom dat nodig werd: zie [Snelheid](#snelheid-wat-er-in-de-paginas-gebakken-wordt).

Waar mikken we op en wat doe je bij nieuwe content: [seo-route.md](seo-route.md).
Hoe het eruitziet en waarom: [stijl.md](stijl.md).
**Waar je op moet letten als je iets toevoegt: [snelheid.md](snelheid.md).**

---

## Waar staat wat

```
index.html                  homepage
contact/  over-ons/         losse pagina's
projecten/  blog/           overzichten (tonen items uit werk/)

interactieve-installaties/  de vier verkooppagina's
muzikale-webapps/
podium/
installatie-huren/
workshops/

werk/<slug>/                ALLE content: 24 items, elk een map met index.html
onderwerp/<slug>/           13 onderwerp-pagina's, gemaakt door een tool

partials/                   header.html en footer.html
css/styles.css              de hele stylesheet
js/site.js                  de hele JavaScript
tools/                      python-scripts, zie onderaan

.htaccess                   redirects + 404. Werkt ALLEEN op Vimexx.
robots.txt  sitemap.xml     zoekmachines
content.json                lijst met welke items bestaan (gemaakt door een tool)
```

---

## Vijf dingen die je moet snappen

### 1. Alle content staat in `werk/`, ook de blogs

Niet in `projecten/` of `blog/`. Dat lijkt slordig maar is met opzet: of iets
een project of een blog is, staat in een metatag **in** het bestand:

```html
<meta name="wotto:type" content="project">
```

Verander je dat in `blog`, dan verhuist het item van `/projecten/` naar
`/blog/` zonder dat de URL verandert. Zat het in een map `projecten/`, dan zou
je de map moeten verplaatsen, de URL breken en een redirect moeten maken. Nu is
het één woord.

De overzichten halen items op met `data-list`:

```html
<div class="grid" data-list="project" data-pilaar="installaties"></div>
```

Filters die je kunt combineren: `data-list` (project, blog, workshop, all, of
meerdere gescheiden door komma's), `data-pilaar`, `data-subject`, `data-huur`,
`data-featured`, `data-limit`, `data-empty`.

### 2. Een item is een map met metatags

```html
<meta name="wotto:type"     content="project">     <!-- project | blog | workshop -->
<meta name="wotto:pilaar"   content="installaties"><!-- installaties | webapps | podium, mag leeg -->
<meta name="wotto:subjects" content="Festival, Phygital">
<meta name="wotto:titel"    content="The Side Quest Rave">
<meta name="wotto:excerpt"  content="Een interactieve muziekinstallatie...">
<meta name="wotto:cover"    content="side-quest-rave.jpg">
<meta name="wotto:datum"    content="2025-08-14">  <!-- bepaalt de volgorde -->
<meta name="wotto:featured" content="ja">          <!-- selectie op de homepage -->
<meta name="wotto:huur"     content="ja">          <!-- te huur op locatie -->
<meta name="wotto:auteur"   content="Jan-Willem Otto">  <!-- alleen bij een ik-verhaal -->
<meta name="wotto:videocover" content="loop.mp4">  <!-- bewegende kaart, optioneel -->
```

Dit zijn ze alle elf. Leest `site.js` iets wat hier niet staat, dan is deze
lijst verouderd.

**`cover` is verplicht.** Zonder cover slaat `build-manifest.py` het item over
en verschijnt het nergens. Dat is met opzet: zo kun je aan iets werken zonder
dat het half zichtbaar wordt.

**`pilaar` mag leeg.** Een blog over jureren op een festival gaat nergens over
installaties, webapps of podium. Zo'n item verschijnt gewoon in `/blog/` en op
zijn onderwerp-pagina's, alleen niet op een pijlerpagina.

**`huur` staat los van de onderwerpen**, want te huur is geen thema maar een
verdienmodel. Een item met `huur` krijgt automatisch een chip naar de
verhuurpagina.

**`auteur`** zet onderaan de tekst "Geschreven door ..." met de datum erbij, en
maakt die persoon ook de `author` in de structured data in plaats van Studio
Wotto. Volg de tekst: staat er "ik", dan zet je een naam. Staat er "wij", dan
laat je dit leeg, want dan is het van de studio. Juist doordat het meestal
leeg is, betekent het iets als er wel een naam staat. De naam moet voorkomen in
`AUTEURS` bovenin `tools/build-seo.py`.

**`videocover`** vervangt de foto op het kaartje door een kort filmpje dat
vanzelf loopt. Alleen voor loops zonder geluid. `cover` blijft nodig: als
poster, als deel-thumbnail, en voor wie in zijn systeem minder beweging heeft
aangezet (dat controleert `site.js`).

Dit is een **apart, kort lusje** naast de video in het artikel, niet dezelfde
mp4. Een kaartje is klein en staat er vaak met meerdere naast elkaar, dus je
wilt geen filmpje van 11 seconden van een megabyte. Maak er een korte, stille,
lichte versie van: ongeveer 5 seconden, rond de 500x500, zonder audio. Noem 'm
`<slug>-kaart.mp4`. Ter vergelijking: de volle zapper-video is 11 sec en 1,1 MB,
het kaartje 5 sec en 76 kB. Er is geen tool voor, je maakt 'm met de ffmpeg die
al meekomt met de build (`imageio-ffmpeg`):

```
python -c "import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())"   # pad naar ffmpeg
ffmpeg -ss 3 -t 5 -i werk/<slug>/<video>.mp4 -an -vf scale=500:500 \
       -c:v libx264 -crf 30 -preset slow -pix_fmt yuv420p -movflags +faststart \
       werk/<slug>/<slug>-kaart.mp4
```

Kies met `-ss` het startmoment waar de meeste beweging in zit. De video mét
geluid blijft gewoon in de tekst staan, met een play-knop.

De chips onderin een item hoef je niet te typen, die komen uit `subjects`.

### 3. Foto's: slepen en bouwen

Zet foto's en filmpjes in `werk/<slug>/` en draai `python tools/build.py`. Dan:

- **Alles boven 1600px wordt verkleind.** Ook je cover, en juist die staat op
  elke lijstpagina. Een cameraorigineel van 7 MB werd zo 180 kB.
- **Foto's als PNG** (die eigenlijk gewoon foto's zijn) horen JPG te worden, dat
  scheelt tot 90%. PNG blijft alleen voor logo's en schermafdrukken, want JPG
  maakt tekst wazig.
- **Twee of meer ongebruikte bestanden** worden een galerij onderaan het item.
  Ongebruikt betekent: staat nog nergens in je tekst. Je zwevende foto, de
  poster van een filmpje en je `videocover` blijven er dus buiten, die zie je al.
- **Eén los bestand** krijgt geen galerij. Het script zegt het alleen, want een
  galerij van één foto is onzin: die hoort zwevend in je tekst.
- **Een eigen galerij blijft van jou.** Het script beheert alleen wat het zelf
  tussen zijn markers heeft neergezet.

**Elke foto heeft twee teksten**, twee losse dingen:

- `alt="..."` — beschrijving voor Google en schermlezers. Altijd. Dit maakt je
  vindbaar in Google Afbeeldingen. Lang en beschrijvend, zoekwoorden waar ze
  natuurlijk passen.
- `data-cap="..."` — kort, zichtbaar bijschrift dat je ziet als je een foto
  aanklikt. Optioneel: leeg = valt terug op de alt.

Elke foto in de tekst is aanklikbaar en gaat schermvullend open, met pijltjes,
toetsenbord en vegen. Het bijschrift dat je daar ziet: eerst de `data-cap`,
anders de figcaption van een video, anders de alt. Zonder JavaScript zie je
gewoon je foto's, er gaat niets stuk.

Wil je de bijschriften nakijken? Draai `python tools/bijschriften.py`, dat
maakt `bijschriften.txt` met per foto de alt en de cap op een rij. Pas aan,
laat Claude het terugzetten, en gooi het bestand daarna weer weg. Het is geen
vaste bron (dat is de HTML), alleen een werkblad dat je op elk moment opnieuw
maakt. Zo kan het niet verouderen.

### Werkwijze bij nieuwe foto's (voor Claude)

Zet Jan-Willem foto's of video's in een map, dan doet Claude dit, en **checkt
altijd eerst bij Jan-Willem voordat het definitief is**:

1. **Elke foto echt bekijken** met de Read-tool. Niet gokken wat erop staat.
2. Verkleinen, hernoemen naar zoekwoorden, video's comprimeren + poster eruit.
3. Een `alt` (voor Google) en een `cap` (zichtbaar) schrijven op basis van wat
   er echt op de foto staat.
4. `width`/`height` uit het bestand halen, niet verzinnen.
5. **Terugkoppelen aan Jan-Willem en laten checken.** Claude kan geen namen,
   plekken of merken verifiëren. In deze sessie ging dat een paar keer mis:
   een verzonnen afmeting, een naam op het verkeerde gezicht, "videosynthesizer"
   waar het een mengtafel was. Dus: Claude vult in, Jan-Willem controleert.
   De correcties gaan via `bijschriften.txt`.

### 4. Header en footer staan op één plek

`partials/header.html` en `partials/footer.html`. Op een pagina zet je:

```html
<div data-include="header"></div>
```

`tools/build-inbakken.py` pakt daaruit alleen het element met `data-partial` en
zet dat in de pagina, tussen markeringen:

```html
<!--ingebakken:header--> ...de header... <!--/ingebakken:header-->
```

De rest van de partial (de `<head>`, het voorbeeldkader) wordt genegeerd. Dat is
met opzet: **je kunt een partial los openen met Live Server en dan ziet hij er
gewoon uit**, inclusief vormgeving. Relatieve paden worden omgerekend naar de
maplaag van de pagina, dus `../projecten/` klopt overal.

**Je past de footer dus nog steeds op één plek aan.** Alleen: draai daarna
`python tools/build.py`, anders staat de oude versie nog in de pagina's. Niet
stuk, wel oud. Dezelfde afspraak als bij de onderwerp-pagina's.

Vergeet je te bouwen op een nieuwe pagina? Dan valt `site.js` terug op de oude
werkwijze en haalt de partial alsnog op bij de bezoeker. Je site is dus nooit
kapot, alleen langzamer.

### 5. Waarom de site op elke plek werkt

De site draait live op `https://studiowotto.com/` (Vimexx), en jij bekijkt 'm
lokaal met Live Server op `http://127.0.0.1:5500/`. Twee plekken, ander niveau.

`site.js` leidt zijn eigen locatie af uit het script-adres:

```js
const base = document.currentScript.src.replace(/js\/site\.js(?:\?.*)?$/, '');
```

Daarom werken de partials, `content.json` en de covers op allebei zonder
aanpassing. **Gebruik dus geen absolute paden** die met `/` beginnen: die zouden
op Live Server (waar de site in een submap kan staan) breken.

De enige uitzondering is `404.html`. Apache serveert die op elke kapotte URL
terwijl het adres in de balk blijft staan, dus relatieve paden zouden daar naar
het verkeerde niveau wijzen. Die pagina gebruikt als enige `/css/` en `/js/`.

---

## Valkuilen waar we al ingetrapt zijn

**`height:auto` in de basisregel voor `img` niet weghalen.** Elke foto heeft
`width` en `height` als attribuut, zodat de pagina niet springt tijdens het
laden. Die attributen werken als CSS. Zonder die regel legt `height="1500"` een
hoogte van 1500px op en rekt je foto uit.

**Foto's verkleinen hoeft niet meer met de hand.** `tools/build-galerij.py` doet
alles boven 1600px. Een cameraorigineel is zo 7 MB.

**JPEG voor foto's, PNG alleen voor logo's en schermafdrukken.** PNG slaat een
foto bijna pixel voor pixel op. Zeven foto's van Crafted stonden als PNG samen
op 12 MB, als JPEG op 1 MB. Bij vlakke kleuren en tekst is PNG juist beter.

**`clear:both` op zwevende beelden niet weghalen.** Zonder die regel kruipen
twee zwevende blokken naast elkaar en houdt je tekst 280px over van de 1200:
twee woorden per regel.

**`1fr` in een raster wordt nooit kleiner dan zijn inhoud.** Dat lijkt "de rest
van de ruimte" te betekenen, maar een grote foto duwt de rij gewoon buiten het
scherm. Wil je dat een rij mag krimpen, schrijf dan `minmax(0, 1fr)`.

**Een foto kan zijn eigen maximum niet bepalen.** Zet je `max-height:100%` op
een foto die zelf de hoogte van zijn vak bepaalt, dan is die 100% een cirkel en
negeert de browser hem zonder te klagen. Dat is waarom de foto in de
schermvullende weergave los van de indeling staat (`position:absolute` +
`margin:auto`). Ziet er ingewikkeld uit, is de enige manier waarop het werkt.

**Bestandsnamen met zoekwoorden.** Geen `cover.jpg`, geen `IMG_4021.jpg`.

**Geen GIF, en geen embed van YouTube of Vimeo voor een kort fragment.** Zet de
mp4 gewoon in de map met `poster` en `preload="none"`, dan kost hij nul bytes
tot iemand op play drukt. Gemeten op een loop van 8 seconden: GIF 1954 kB,
mp4 170 kB, en de GIF had dan nog de halve framerate en 256 kleuren. Wat mensen
"een GIF" noemen op Twitter of Slack is al jaren stiekem een mp4. Een embed
laadt een hele iframe, player-JavaScript en tracking van een ander domein, ook
als niemand kijkt. Loopt hij vanzelf en is hij stil? `autoplay loop muted
playsinline`. Zit er geluid op? `controls`. Filmpje dat op zichzelf iets
betekent en gevonden moet worden? Dán YouTube.

**`&amp;` telt in HTML als 5 tekens**, maar Google toont er 1. Let daarop bij
de 60-tekengrens van een titel.

**`.htaccess` doet niets op Live Server.** Alleen Apache leest het, dus alleen
Vimexx. Er staan 23 redirects in van de oude WordPress-URL's, de www- en
https-afdwinging, plus de 404. Lokaal zie je dus nooit wat het doet; dat merk je
pas live.

**`robots.txt` telt alleen vanaf een domeinroot.** Op `studiowotto.com` staat
hij op de root en wordt hij gelezen. Er staat geen `noindex` meer in de pagina's
(die zat er alleen in tijdens de GitHub-preview, om die uit Google te houden).

---

## De tools

Python, geen dependencies behalve Pillow. Draaien vanuit de projectmap.

```
python tools/build.py
```

Dat is het enige commando dat je nodig hebt. Het draait de zes stappen in de
juiste volgorde:

| Stap | Wat het doet |
|---|---|
| `build-manifest.py` | schrijft `content.json`: welke items bestaan er **en hun kenmerken**. Slaat items zonder cover over. |
| `build-galerij.py` | verkleint te grote foto's en bouwt de galerij onder een item |
| `build-onderwerpen.py` | onderwerp-pagina's, alle chip-wolken, en de chips op elk item |
| `build-seo.py` | structured data op elke pagina + `sitemap.xml` |
| `build-kaartbeeld.py` | maakt van elke cover een lichte `-kaart.webp` voor de kaartjes |
| `build-kaartfilm.py` | maakt van elk kaartfilmpje een lichte `-web.mp4`. Het filmpje in het artikel zelf blijft ongemoeid |
| `build-inbakken.py` | zet header, footer, kaartjes, iconen en `<main>` in de HTML |

Daarna draait `check-snelheid.py` nog als controle. Die bouwt niets, maar kijkt
het resultaat na op de regels uit [snelheid.md](snelheid.md): beeld zonder
`width`/`height`, uitschieters in bestandsgrootte, kapotte verwijzingen, gaten in
de kopvolgorde, titels die te lang of te kort zijn. **Hij blokkeert nooit iets.**
Of een zware foto de moeite waard is, bepaal jij.

**Draai ze niet los, of hou dan deze volgorde aan.** `build-onderwerpen.py`
schrijft de onderwerp-pagina's helemaal opnieuw uit zijn sjabloon, en dat
sjabloon bevat geen structured data. Draai je hem ná `build-seo.py`, dan staan
die 13 pagina's er zonder. En `build-inbakken.py` moet als laatste, want anders
gooit stap 3 het inbakwerk weer weg. Daarom bestaat `build.py`.

### Klusjes op aanvraag

Deze horen niet in `build.py`, want ze hoeven bijna nooit:

| Script | Wanneer |
|---|---|
| `haal-lettertypen.py` | een ander lettertype, of een nieuwe versie van Google overnemen |
| `haal-iconen.py` | je gebruikt een nieuw Phosphor-icoon. `build-inbakken.py` waarschuwt als er één mist |
| `verklein-logos.py` | een klantlogo toegevoegd of vervangen |
| `bijschriften.py` | overzicht van alle bijschriften nalopen |
| `check-snelheid.py` | los nakijken zonder te bouwen |

### Snelheid: wat er in de pagina's gebakken wordt

Hier zat een probleem dat je op je eigen snelle verbinding niet ziet. De pagina
had vier gaten die JavaScript pas na het laden vulde: de header, de footer en de
twee kaartenstroken. Voor die kaartjes werden ook nog **alle 29 projectpagina's
apart opgehaald**, puur om er de metatags uit te lezen.

Op een trage telefoonverbinding leverde dat drie problemen op:

1. De pagina versprong zichtbaar, vier keer. Google meet dat als CLS en gaf er
   0,467 voor, waar 0,1 de grens is. Dat kost een kwart van je snelheidsscore.
2. Het duurde lang. 82 verzoeken en bijna 5 MB voordat de pagina stond.
3. Wie geen JavaScript uitvoert zag een pagina zonder menu en zonder projecten.
   Google draait je JavaScript wel, maar de AI-assistenten die tegenwoordig
   websites lezen doen dat vaak niet.

Wat er nu anders is:

- **De kenmerken staan in `content.json`.** Eén klein bestand in plaats van 29
  grote. De metatags in de pagina's blijven de bron; `build-manifest.py` leest ze.
- **Header, footer, kaartjes en `<main>` staan in de HTML.** Geen gat, geen
  versprong, en iedereen ziet dezelfde pagina.
- **Lettertypen en iconen komen van je eigen server.** De `<link>`-regels naar
  `fonts.googleapis.com` en `unpkg.com` blokkeerden het tekenen van de pagina tot
  een vreemd domein antwoordde. In de bron schrijf je iconen nog gewoon als
  `<i class="ph-bold ph-naam"></i>`; het bouwen maakt er een SVG van en zet
  alleen de tekeningen die die pagina nodig heeft bovenaan.
- **Covers en logo's hebben een lichte WebP** naast het origineel. Het
  Summa-logo ging van 149 KB naar 8 KB: het stond op 3815 pixels breed en wordt
  op vijftig getoond.

Resultaat, gemeten met Lighthouse op mobiel: van 82 naar 37 verzoeken, van 4990
naar 2215 KB, CLS van 0,083 naar 0, en geen enkel verzoek meer naar een ander
domein. (Die 0,083 is de meting op localhost, waar geen netwerkvertraging is; op
de echte server stond hij op 0,467.)

Daarna waren de filmpjes op de kaarten het zwaarst. Die zijn met
`build-kaartfilm.py` teruggebracht van 1646 naar 913 KB, waarbij alleen de twee
uitschieters echt zijn aangepakt en de rest zijn kwaliteit hield. **De filmpjes
in de artikelen zelf zijn niet aangeraakt**: die staan op `preload="none"` met
een afspeelknop, dus ze kosten pas iets als iemand erop drukt, en dan wil je
juist het volledige bestand. De uitleg staat in [snelheid.md](snelheid.md).

Twee keer draaien geeft exact hetzelfde resultaat, dus je kunt het altijd doen.

**Pas de tools aan, niet de HTML die ze schrijven.** Alles tussen de
`structured data`-markers wordt overschreven.

- Je bedrijfsgegevens (adres, KVK, BTW, `knowsAbout`, `sameAs`): bovenin
  `tools/build-seo.py`
- De lijst met onderwerpen: bovenin `tools/build-onderwerpen.py`

---

## Online zetten

De site is live op **https://studiowotto.com** (Vimexx). Publiceren is niets
meer dan pushen:

```
git push
```

Elke push naar `main` start `.github/workflows/deploy.yml`. Die kopieert de site
via FTP naar Vimexx (`public_html/`). Binnen een minuut staat je wijziging
online. Je hoeft dus nooit met de hand te FTP-en. Wil je zien of het lukte, of
'm met de hand starten: de **Actions**-tab op GitHub.

Wat NIET mee naar de live site gaat, staat in de `exclude`-lijst onderin
`deploy.yml`: de dev-bestanden (dit README, `stijl.md`, `seo-route.md`,
`content-structuur.md`, `bijschriften.txt`, `_config.yml`) en de bronmappen
(`tools/`, `moodboard/`, `oude blogs en pagina's/`).

**Eenmalig ingesteld, hoef je niet meer aan te komen:**

- De FTP-inloggegevens staan als *secrets* in GitHub (Settings → Secrets and
  variables → Actions): `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`. Als
  *secret*, niet als *variable*, anders vindt de deploy ze niet.
- `.htaccess` regelt op Vimexx de redirects van de oude WordPress-URL's, dwingt
  `www` weg en `https` af, en wijst 404's naar `404.html`.
- De sitemap staat aangemeld in Google Search Console als
  `https://studiowotto.com/sitemap.xml`.

Nieuw item toevoegen dat vroeger op de oude WordPress-site stond? Zet er een
redirect-regel bij in `.htaccess` (zie de uitleg daar), anders krijgt iemand die
de oude link volgt een 404.
