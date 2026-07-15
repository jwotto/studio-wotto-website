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
| Educatie | 10 |
| Festival | 7 |
| Muziektechnologie | 5 |
| Phygital | 5 |
| Gamification | 5 |
| Creatieve technologie | 5 |
| Muziekinstrumenten | 4 |
| Games | 3 |
| Interactieve kunst | 3 |
| Geluidsontwerp | 2 |
| Merkactivering | 1 |
| Museum | 0 |
| Interactieve reclame | 0 |

**Educatie zit op 10 van de 19.** Klik je erop, dan krijg je meer dan de helft
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

## 7. Bij het live gaan

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

## 8. De gereedschapskist

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
