# SEO-route

Dit bestand bestaat zodat je niet elke keer opnieuw hoeft te bedenken waar je
op mikt. Loop het langs als je iets nieuws toevoegt. Klopt er iets niet meer?
Pas het aan, dit is een werkdocument en geen wet.

Hij staat in de `exclude` van `_config.yml`, dus hij gaat niet mee online.

---

## 1. De kaart: waar mikt welke pagina op?

De regel eronder: **splits op publiek, niet op product.** Zelfde publiek? Eén
pagina met kopjes. Ander publiek? Eigen pagina. Daarom staan "laten maken" en
"huren" apart: dat is een museum met een bouwtraject tegenover een festival dat
iets voor één weekend inhuurt. Andere klant, ander budget, andere zoekopdracht.

| Pagina | Voor wie | Waar die op zoekt |
|---|---|---|
| `/` | iedereen | Studio Wotto (je merk) |
| `/interactieve-installaties/` | musea, scholen | interactieve installatie **laten maken** |
| `/installatie-huren/` | festivals, merken, bureaus | interactieve installatie **huren**, merkactivering |
| `/podium/` | artiesten, podia | muziekinstrument op maat · live visuals · stage props |
| `/muzikale-webapps/` | educatie | muzikale webapp laten maken |
| `/workshops/` | scholen | workshop muziek en techniek |

Het woord dat het meeste oplevert is **"huren"** en **"laten maken"**. Dat typt
iemand met een budget. "Interactieve installatie" alleen trekt studenten die een
werkstuk schrijven.

### Wat we niet weten

Er is **geen zoekvolumedata** gebruikt. Dit is beredeneerd vanuit koopintentie.
De echte cijfers komen pas uit Search Console als je een paar maanden live
staat. Kijk daar over een half jaar en pas deze tabel aan naar wat er echt
gezocht blijkt te worden.

---

## 2. De drie regels

**Eén zoekwoord per pagina.** Twee pagina's op hetzelfde woord vechten met
elkaar, en dan verlies je van jezelf. Daarom heet `/podium/` niet
"interactieve installaties": dat woord is al bezet.

**Titel maximaal 60 tekens, description maximaal 160.** Google kapt daarna af.
Let op: `&amp;` telt in je HTML als 5 tekens maar Google toont er 1.

**Een genre werkt op 3 tot 7 van je items.** Meer betekent dat het niets
filtert (klik je erop, dan krijg je alles). Minder betekent dat het geen
categorie is maar een etiket.

---

## 3. Nieuw item toevoegen

Een item is een map onder `werk/`. De map is de URL, en die is voorgoed.

### Voor je begint
- [ ] Op welk zoekwoord mik je? Eén per item. Kijk in tabel 5 of hij vrij is.
- [ ] Mapnaam = zoekwoord, kleine letters, streepjes, kort. `joost-klein`,
      niet `terugblik-op-de-show-van-joost-klein-2026`. Wijzigen kost je later
      een redirect in `.htaccess`.

### De kop van het bestand
Kopieer een bestaand item en pas aan. Kijk vooral naar:
- [ ] `<title>` max 60, zoekwoord vooraan, `| Studio Wotto` achteraan
- [ ] `description` max 160, één zin die iemand doet klikken (geen samenvatting)
- [ ] `canonical` en alle `og:` naar de nieuwe map
- [ ] `wotto:type` project, blog of workshop
- [ ] `wotto:pilaar` installaties, webapps of podium
- [ ] `wotto:subjects` alleen namen uit tabel 4
- [ ] `wotto:datum` (bepaalt de volgorde, nieuwste eerst)
- [ ] `wotto:huur` op `ja` als het te huur is. Dat is geen genre maar een
      verdienmodel, en het item krijgt er automatisch een chip van.
- [ ] `wotto:auteur` alleen bij een ik-verhaal. Dan komt er onderaan
      "Geschreven door ..." te staan en wordt die persoon ook de auteur in de
      structured data. Bij een wij-verhaal leeg laten: dan is het van de studio.
      Google kijkt naar wie iets schrijft (E-E-A-T), en een echt persoon met een
      profiel weegt zwaarder dan een merknaam.

### De foto's
- [ ] Bestandsnaam = zoekwoorden. **Geen `cover.jpg` of `IMG_4021.jpg`**,
      Google leest bestandsnamen mee.
- [ ] Grootte: **max 1600px breed**. Een cameraorigineel is zo 7 MB, dat is
      voor het web onbruikbaar. Op 1600px is dat ~200 kB en nog steeds scherp.
- [ ] `alt` = wat je ziet, in een zin. Niet "screenshot 1".
- [ ] `width` en `height` erop, dan springt de pagina niet tijdens het laden.
      **Let op:** die attributen werken als CSS. Zonder `height:auto` in de
      stylesheet rekt je foto uit. Die regel staat er, niet weghalen.
- [ ] `loading="lazy"` op alles behalve de eerste foto van de pagina.
- [ ] **JPEG voor foto's, PNG alleen voor logo's en schermafdrukken.** PNG slaat
      een foto bijna pixel voor pixel op. Zeven foto's van Crafted stonden als
      PNG samen op 12 MB, als JPEG op 1 MB. Bij vlakke kleuren en tekst is PNG
      juist wel beter, dus dit is geen algemene regel.
- [ ] Meerdere foto's? Eén zwevend in de tekst, de rest onderaan in een
      `<div class="gallery">` naast elkaar.

### Film
- [ ] **Geen GIF.** Nooit. Gemeten op een loop van 8 seconden: GIF 1954 kB
      tegenover mp4 170 kB, en de GIF had dan nog de halve framerate en 256
      kleuren. Wat mensen "een GIF" noemen op Twitter of Slack is al jaren
      stiekem een mp4.
- [ ] **Geen embed van YouTube of Vimeo** voor een kort fragment. Die laadt een
      hele iframe, player-JavaScript en tracking van een ander domein, ook als
      niemand kijkt. Een fragment van 8 seconden is 170 kB.
- [ ] Zet de mp4 gewoon in de map, met `poster` en `preload="none"`. Dan kost
      hij nul bytes tot iemand op play drukt.
- [ ] Loopt hij vanzelf en heeft hij geen geluid? `autoplay loop muted
      playsinline`. Zit er geluid op? `controls`, want ongevraagd geluid is
      onbeleefd.
- [ ] Een bewegende cover op de kaartjes kan met `wotto:videocover`. Alleen voor
      korte loops zonder geluid. Wie in zijn systeem minder beweging heeft
      aangezet, krijgt automatisch de foto.
- [ ] **Wel op YouTube** als het filmpje op zichzelf iets betekent. Dat is van
      Google, dus het kan zelf gevonden worden. Vimeo levert je niets op.

### Chips hoef je niet te typen
Die worden gegenereerd uit `wotto:subjects`. Vroeger stonden ze met de hand in
elk bestand en toen liepen ze uit de pas.

### Afronden
```
python tools/build.py
```
- [ ] Bekijken met Live Server, ook je venster smal slepen
- [ ] Zoekwoord toevoegen aan tabel 5 hieronder

---

## 4. De onderwerpen (genres)

Een genre zegt waar iets **over gaat**. Niet wat je ermee kunt (dat is
`wotto:huur`), en niet voor wie het is (dat is de pijler).

Toevoegen of schrappen doe je op één plek: de lijst bovenin
`tools/build-onderwerpen.py`. Dat script schrijft daarna de pagina's, alle
chip-wolken en de chips op elk item.

| Onderwerp | Items |
|---|---|
| Educatie | 12 |
| Festival | 8 |
| Phygital | 6 |
| Muziektechnologie | 6 |
| Gamification | 6 |
| Creatieve technologie | 5 |
| Muziekinstrumenten | 4 |
| Interactieve kunst | 4 |
| Games | 3 |
| Geluidsontwerp | 2 |
| Museum | 1 |
| Merkactivering | 1 |
| Interactieve reclame | 0 |

**Educatie zit op 12 van de 24.** Klik je erop, dan krijg je meer dan de helft
van je werk, dus het filtert weinig. Bewuste keuze, maar hou het in de gaten.

**Museum en Interactieve reclame staan er leeg in**, omdat er werk aan komt.
Zolang ze leeg zijn tonen ze de boodschap uit `data-empty`.

**Merkactivering en Interactieve reclame lijken op elkaar maar zijn het niet.**
Het verschil zit in de tekst en moet daar blijven: merkactivering is tijdelijk
en te huur (festival, beurs, event), interactieve reclame blijft staan en is op
maat (winkel, horeca, etalage). Vervaagt dat verschil, dan vechten die twee
pagina's om hetzelfde zoekwoord.

---

## 5. Zoekwoorden die bezet zijn

Vul dit aan bij elk nieuw item. Dít is waar dit bestand over een jaar voor
dient, en precies wat niemand ooit bijhoudt.

| Zoekwoord | Pagina |
|---|---|
| Studio Wotto | `/` |
| interactieve installatie laten maken | `/interactieve-installaties/` |
| interactieve installatie huren | `/installatie-huren/` |
| merkactivering | `/installatie-huren/` (kopje) |
| muziekinstrument op maat | `/podium/` (kopje) |
| live visuals, VJ | `/podium/` (kopje) |
| stage props | `/podium/` (kopje) |
| muzikale webapp laten maken | `/muzikale-webapps/` |
| workshop muziek en techniek | `/workshops/` |
| muzieknoten leren lezen | `/werk/crackthenotes/` |
| videosynthesizer | `/werk/snes-videosynthesizer/` |

---

## 6. Gevonden worden via ChatGPT en Claude

Werkt anders dan Google: een AI **rankt** niet, hij **citeert**. Vier dingen
sturen dat.

> **Let op: dit werkt nu niet, en het ligt niet aan de site.** Vimexx blokkeert
> AI-crawlers op de server, nog voordat je robots.txt aan de beurt komt. Alles
> hieronder klopt en is goed ingesteld, maar er komt geen AI-bot binnen zolang
> de site daar staat. Zie 7d.

**Je robots.txt laat AI-bots bewust binnen.** Er staat geen `Disallow`. Dat is
geen slordigheid: `GPTBot`, `OAI-SearchBot`, `ClaudeBot` en `PerplexityBot`
vallen onder de `*` en mogen er dus in. In het bestand staat hoe je ze
blokkeert als je ooit van gedachten verandert.

Er staat ook bewust geen `Disallow` naast de `noindex`. Wat Google niet mag
ophalen, kan hij ook niet lezen, dus dan ziet hij die noindex nooit en kan de
URL alsnog kaal in de resultaten belanden.

**Je bent een entiteit, geen pagina.** In je structured data staat wie je bent
(`LocalBusiness`), waar je zit (`PostalAddress`), waar je verstand van hebt
(`knowsAbout`) en waar je nog meer te vinden bent (`sameAs`). Die `sameAs`
moet exact overeenkomen met de links in je footer: Google vergelijkt die twee
en gelooft je pas als ze hetzelfde zeggen.

**Antwoord letterlijk op vragen.** Een AI pakt de alinea die de vraag
beantwoordt. Eén zin als "een installatie huren kost vanaf X" wordt geciteerd,
drie alinea's sfeer niet. *Op dit moment staan er bewust geen prijzen op de
site. Dat kost je zichtbaarheid bij "wat kost een interactieve installatie
huren", want daar heeft een AI dan geen antwoord op. Bewuste afweging.*

**Wat anderen over je schrijven telt zwaarder dan je eigen site.** Joost Klein,
Pukkelpop, de Effenaar, Museum Speelklok. Daar valt meer te halen dan uit welk
woord dan ook op je eigen pagina. Reddit weegt zwaar bij AI-assistenten, maar
dan gaat het om posts die jou noemen, niet om een link naar je profiel. En
zelfpromotie op Reddit is de snelste route naar een ban.

---

## 7. Openstaand: de onderwerp-pagina's zijn te dun

**Jan-Willem schrijft deze teksten zelf.** Niet inplannen als klus voor een
tool of voor Claude; wel klaarzetten zodat het zo ingevuld kan worden.

Dertien pagina's van 48 tot 127 woorden. Ze zijn nu een kop met een lijst
kaartjes eronder, en dat is precies te weinig om iets te betekenen voor
"interactieve installatie museum" of "muziektechnologie workshop". Juist die
pagina's zouden dat moeten opvangen.

Wat er per pagina bij hoort, ongeveer 300 woorden:

- wat je voor dat soort opdrachtgever maakt
- waarom het daar anders werkt dan elders (een festival is niet een museum)
- pas daarna de voorbeelden, die er via `data-subject` al automatisch onder staan

De sjabloontekst staat in `tools/build-onderwerpen.py`, dus een handgeschreven
stuk moet daar landen of als apart blok in het sjabloon meegenomen worden,
anders overschrijft de bouwstap het bij de eerstvolgende ronde.

**Begin niet alle dertien tegelijk.** De Prestaties-export uit Search Console
vertelt op welke onderwerpen je al vertoningen krijgt maar nog niet klikt. Dat
zijn de pagina's waar 300 woorden meteen iets doen. De rest kan wachten.

Bijkomend: de titels zijn 19 tot 29 tekens ("Museum | Studio Wotto") terwijl
Google er 60 toont. Die schrijf je in dezelfde ronde mee.

---

## 7b. Besloten: geen prijzen of richtprijzen op de site

Opgekomen als SEO-advies (het vangt zoekopdrachten met koopintentie af en
scheelt gesprekken zonder budget), en **bewust niet gedaan**. Dit is een
ondernemersbeslissing, geen technische. Niet opnieuw voorstellen.

---

## 7c. Openstaand: vier covers zijn foto's die als PNG zijn opgeslagen

Samen ruim 6 MB, en het zijn **covers**, dus ze staan op elke lijstpagina.

| Bestand | Nu | Zou moeten |
|---|---|---|
| `bouw-je-eigen-elektrische-gitaar.png` | 2192 kB | ~200 kB |
| `maak-muziek-met-techniek.png` | 1806 kB | ~200 kB |
| `tantu-beats.png` | 1235 kB | ~150 kB |
| `mkrdays-2024.png` | 1011 kB | ~120 kB |

`build-galerij.py` laat ze met rust, want ze zijn kleiner dan 1600px. Het
probleem is niet hun afmeting maar hun formaat: PNG slaat een foto bijna pixel
voor pixel op.

Waarom het niet automatisch gaat: omzetten naar JPEG verandert de
bestandsnaam, en die staat in `wotto:cover`, in `og:image` en in de HTML. Dat
moet dus in één ronde, met alle verwijzingen mee. Ook moet je eerst kijken of
het echt een foto is: bij een schermafdruk of een logo is PNG juist beter.
Dat is precies waarom `crackthenotes` PNG's mag houden.

---

## 7d. Openstaand: Vimexx blokkeert AI-crawlers, de site moet verhuizen

**Wat ik wil:** dat ChatGPT, Claude en Perplexity de site gewoon kunnen lezen.
Dat wordt een steeds belangrijker kanaal om gevonden te worden, en het is
precies waar sectie 6 op gebouwd is.

**Wat er gebeurt:** Vimexx weigert AI-crawlers met een 403. Vastgesteld op
4 augustus 2026, en bevestigd door hun support: *"We blokkeren zo goed als alle
AI agents. Dit komt omdat ze voor veel overlast zorgen op ons platform. Helaas
is er ook geen uitzondering op een gedeelde omgeving mogelijk. Je kunt wel een
VPS kiezen want daar worden ze niet geblokkeerd."*

Zelf testen:

```
curl -I -A "Mozilla/5.0"   https://studiowotto.com/    ->  200
curl -I -A "ClaudeBot/1.0" https://studiowotto.com/    ->  403
```

Het is een filter op user-agent-naam, afgegeven **vóór** Apache. Aan `.htaccess`
sleutelen heeft dus geen enkel effect: het verzoek bereikt de site niet eens.
Geblokkeerd zijn onder meer ClaudeBot, GPTBot, OAI-SearchBot, PerplexityBot,
AhrefsBot en SemrushBot. Googlebot en bingbot komen er gewoon in, dus je
gewone Google-vindbaarheid is niet geraakt. Ook `/robots.txt` zelf geeft 403,
wat het extra schadelijk maakt: een crawler die de robots.txt niet mag ophalen
gaat er standaard van uit dat de hele site verboden is.

Het raakt alle drie de domeinen (studiowotto.com, technomaker.org,
crackthenotes.com) en elke andere Vimexx-server die getest is.

**De oplossing: de website naar Cloudflare Pages, de mail bij Vimexx laten.**

De site is puur HTML, CSS en JavaScript, dus statische hosting is er letterlijk
voor gemaakt. Gratis, sneller (wereldwijd CDN in plaats van één server in Ede),
geen bot-blokkade, en pushen blijft publiceren via GitHub. Een VPS is voor een
site zonder PHP of database weggegooid geld en beheerwerk.

Alleen twee DNS-records wijzigen. De rest blijft staan:

| Record | Nu | Wat ermee gebeurt |
|---|---|---|
| `studiowotto.com` | 185.104.29.144 | naar Cloudflare Pages |
| `www.studiowotto.com` | 185.104.29.144 | naar Cloudflare Pages |
| MX (prio 10) | mail.studiowotto.com | blijft |
| `mail` / `smtp` / `pop` | 185.104.29.144 | blijft |

De stappen, in deze volgorde. Tot de laatste stap draait de site gewoon door
op Vimexx en merkt niemand iets.

- [ ] `.htaccess` omzetten naar `_redirects` en `_headers`. Dat bestand werkt
      niet op Cloudflare Pages, en het bevat de 43 WordPress-redirects en de
      cacheregels. GitHub Pages valt daarom af: dat kan helemaal geen redirects,
      en dan verlies je de opgebouwde posities van de oude URL's.
- [ ] Cloudflare Pages koppelen aan de GitHub-repo, testen op de tijdelijke
      `pages.dev`-URL. Redirects, video's, de 404 en de galerijen nalopen.
- [ ] **Cloudflare's eigen AI-blokkade uitzetten.** Die staat standaard aan op
      nieuwe projecten. Sla je dit over, dan ruil je Vimexx' filter in voor dat
      van Cloudflare.
- [ ] Nameservers naar Cloudflare, en controleren of de import van de
      mailrecords compleet is. Zo'n scan mist er soms één.
- [ ] `mail.studiowotto.com` op **grijs** zetten in Cloudflare (proxy uit).
      Staat dat op oranje, dan loopt mailverkeer door de webproxy en werkt je
      mailprogramma niet meer. Alleen `studiowotto.com` en `www` gaan door de
      proxy.
- [ ] Controleren: `curl -I -A "ClaudeBot/1.0" https://studiowotto.com/` moet
      200 geven in plaats van 403.
- [ ] Vimexx vragen of er een goedkoper e-mail-only pakket is. De webruimte
      gebruik je daarna niet meer, maar de mail zit in het hostingpakket. Opzeggen
      betekent dus ook je mail kwijt. Dit levert geen besparing op zonder zo'n
      pakket.

Meegenomen bij het DNS-werk: er staat nu **geen SPF- en geen DMARC-record**.
Daardoor belandt uitgaande mail eerder in spamfilters en kan iemand relatief
makkelijk uit jouw naam mailen. Twee DNS-regels, los van dit verhaal maar
handig om in dezelfde ronde te doen.

---

## 8. Bij het live gaan

In deze volgorde.

- [ ] **`noindex` van alle pagina's halen.** Dit is het vinkje waar alles op
      wacht. Doe je dit niet, dan doet de rest er niet toe.
      ```
      grep -rl 'name="robots" content="noindex' --include=*.html .
      ```
- [ ] Naar Vimexx. `.htaccess` werkt alleen daar, en die bevat je 301-redirects
      en de 404-pagina.
- [ ] Controleren of de oude URL's doorsturen naar de nieuwe.
- [ ] `sitemap.xml` indienen bij Google Search Console.
- [ ] Google Bedrijfsprofiel aanmaken. Zonder dat kom je niet op Maps, ook niet
      met `LocalBusiness` in je code.
- [ ] KVK-inschrijving: die staat op het huisadres, je site zegt Hurksestraat.
      Overweeg het bezoekadres bij de KVK in te schrijven, dan komen ze overeen
      en blijft je huis privé. Even met je boekhouder.

---

## 9. De gereedschapskist

| Commando | Wat het doet |
|---|---|
| `python tools/build.py` | draait alles hieronder, in de juiste volgorde. Dit is het enige dat je hoeft te onthouden. |
| `tools/build-manifest.py` | schrijft `content.json`: welke items bestaan er. Slaat items zonder cover over. |
| `tools/build-onderwerpen.py` | onderwerp-pagina's, chip-wolken en de chips op elk item |
| `tools/build-seo.py` | structured data op elke pagina + `sitemap.xml` |

De volgorde is niet vrij: `build-onderwerpen.py` schrijft de onderwerp-pagina's
opnieuw uit een sjabloon zonder structured data, dus `build-seo.py` moet erna.
Daarom is er `build.py`.

Je bedrijfsgegevens (adres, KVK, BTW, `knowsAbout`, `sameAs`) staan bovenin
`tools/build-seo.py`. De lijst met onderwerpen staat bovenin
`tools/build-onderwerpen.py`. Pas die bestanden aan, niet de HTML: alles tussen
de `structured data`-markers wordt overschreven.
