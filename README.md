# Studio Wotto: de website

Platte HTML, CSS en een beetje JavaScript. **Geen build-stap, geen Node, geen
framework.** Je opent een bestand, past het aan, en dat is wat er online staat.
Openen met Live Server en je ziet het meteen.

Waar mikken we op en wat doe je bij nieuwe content: `seo-route.md`.
Hoe het eruitziet en waarom: `stijl.md`.

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

`site.js` haalt het bestand op en pakt daaruit alleen het element met
`data-partial`. De rest van de partial (de `<head>`, het voorbeeldkader) wordt
genegeerd. Dat is met opzet: **je kunt een partial los openen met Live Server
en dan ziet hij er gewoon uit**, inclusief vormgeving.

Relatieve paden in een partial worden bij het inladen omgerekend tegen de
partial zelf, dus `../projecten/` klopt vanaf elke maplaag.

### 5. Waarom de site overal werkt

Op drie plekken staat hij op een ander niveau:

```
Live Server        http://127.0.0.1:5500/
GitHub Pages       https://jwotto.github.io/studio-wotto-website/
Vimexx (straks)    https://www.studiowotto.com/
```

`site.js` leidt zijn eigen locatie af uit het script-adres:

```js
const base = document.currentScript.src.replace(/js\/site\.js(?:\?.*)?$/, '');
```

Daarom werken de partials, `content.json` en de covers overal. **Gebruik dus
geen absolute paden** die met `/` beginnen: die breken op GitHub Pages.

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

**`.htaccess` doet niets op Live Server en niets op GitHub Pages.** Alleen
Apache leest het, dus alleen Vimexx. Er staan 23 redirects in van de oude
WordPress-URL's, plus de 404.

**`robots.txt` telt alleen vanaf een domeinroot.** Op GitHub Pages staat hij in
een submap en wordt hij dus nooit gelezen. Wat de preview nu uit Google houdt,
is de `noindex` in elke pagina.

---

## De tools

Python, geen dependencies behalve Pillow. Draaien vanuit de projectmap.

```
python tools/build.py
```

Dat is het enige commando dat je nodig hebt. Het draait de drie stappen in de
juiste volgorde:

| Stap | Wat het doet |
|---|---|
| `build-manifest.py` | schrijft `content.json`: welke items bestaan er. Slaat items zonder cover over. |
| `build-galerij.py` | verkleint te grote foto's en bouwt de galerij onder een item |
| `build-onderwerpen.py` | onderwerp-pagina's, alle chip-wolken, en de chips op elk item |
| `build-seo.py` | structured data op elke pagina + `sitemap.xml` |

**Draai ze niet los, of hou dan deze volgorde aan.** `build-onderwerpen.py`
schrijft de onderwerp-pagina's helemaal opnieuw uit zijn sjabloon, en dat
sjabloon bevat geen structured data. Draai je hem ná `build-seo.py`, dan staan
die 13 pagina's er zonder. Daarom bestaat `build.py`.

Twee keer draaien geeft exact hetzelfde resultaat, dus je kunt het altijd doen.

**Pas de tools aan, niet de HTML die ze schrijven.** Alles tussen de
`structured data`-markers wordt overschreven.

- Je bedrijfsgegevens (adres, KVK, BTW, `knowsAbout`, `sameAs`): bovenin
  `tools/build-seo.py`
- De lijst met onderwerpen: bovenin `tools/build-onderwerpen.py`

---

## Online zetten

Nu: elke push naar `main` gaat automatisch naar
`jwotto.github.io/studio-wotto-website/`. Dat is een preview, en hij staat op
`noindex`.

Straks: de map naar Vimexx. Zie de lanceerlijst in `seo-route.md`. Het eerste
punt daar is de `noindex` weghalen, en zonder dat doet de rest er niet toe.
