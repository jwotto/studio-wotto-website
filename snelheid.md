# Snelheid en toegankelijkheid

Wat je moet weten als je iets nieuws aan de site toevoegt.

De regels hieronder komen niet uit een boekje. Ze komen uit een echte meting van
deze site met Lighthouse (mobiel, nagebootst traag 4G, juli 2026). Elke regel
hoort bij iets dat we toen tegenkwamen. De homepage stond op **61 punten voor
snelheid** en op **1 van de 2 voor agentisch browsen**, en na het opruimen op
**37 verzoeken in plaats van 82** en **2215 KB in plaats van 4990 KB**.

Het venijnige eraan: op je eigen glasvezel met een MacBook zie je van dit alles
niets. Je moet het meten.

---

## Hoe je meet

**Lighthouse** is een laboratoriumtest die je zelf draait. Hij laadt je pagina
één keer op een nagebootste trage telefoon en zegt wat er beter kan.

- In Chrome: F12 → tabblad **Lighthouse** → Mobiel → Analyseren.
- Of online, zonder installeren: [pagespeed.web.dev](https://pagespeed.web.dev).

**Dat is iets anders dan Search Console.** Lighthouse is de meetlat waarmee je
verbouwt: meteen antwoord, werkt ook op een pagina die nog niet online staat.
Search Console is de thermometer achteraf: echte gegevens van Google over wat je
bezoekers meemaakten, met dagen vertraging. Voor optimaliseren gebruik je
Lighthouse.

**Meet op een echt adres, niet op localhost.** Lokaal is er geen
netwerkvertraging, en juist dat maakt het verschil. Dezelfde pagina die live 61
punten kreeg, haalde op localhost 94.

---

## De vier statistieken die tellen

| | wat het meet | grens |
|---|---|---|
| **CLS** | hoeveel de pagina verspringt tijdens het laden | onder 0,1 |
| **LCP** | wanneer het grootste ding in beeld staat | onder 2,5 s |
| **FCP** | wanneer je het eerste hebt gezien | onder 1,8 s |
| **TBT** | hoe lang de pagina niet reageert op een tik | onder 200 ms |

CLS is een kwart van je score en was hier de boosdoener: **0,467**. Dat is ook
de check waar "agentisch browsen" op zakte. Eén oorzaak, twee lage cijfers.

---

## De regels

### 1. Vul een pagina niet met JavaScript nadat hij geladen is

Dit was hier het hele probleem. De pagina had vier gaten die JavaScript pas
achteraf vulde: de header, de footer en de twee kaartenstroken. De browser
tekende eerst de pagina zonder, en propte ze er daarna in. Alles eronder schoof
mee naar beneden. Vier keer.

Zet het in de HTML. Dat doet `tools/build-inbakken.py` nu automatisch, dus in de
praktijk betekent deze regel: **draai `python tools/build.py` en zet niet zelf
iets nieuws op de pagina met JavaScript.**

Moet het toch, houd dan de ruimte vrij met `aspect-ratio` of `min-height`, zodat
er niets kan verschuiven.

### 2. Elke `<img>` krijgt `width` en `height`

Zonder die twee weet de browser pas hoe groot een foto wordt als hij binnen is,
en schuift alles eronder alsnog omlaag. Ze hoeven niet de weergavegrootte te
zijn, als de verhouding maar klopt: daaruit rekent de browser de ruimte uit. De
regel `img{ height:auto }` in de stylesheet zorgt dat de foto er niet door
uitgerekt wordt.

*Wordt automatisch gecontroleerd.*

### 3. Niets in de `<head>` mag van een ander domein komen

Een `<link rel="stylesheet">` naar een vreemd domein blokkeert het tekenen van
je pagina. De browser moet eerst dat domein opzoeken (DNS), een beveiligde
verbinding opzetten (TLS) en dan pas het bestand vragen. Hier stonden er twee:
Google Fonts en een iconenpakket van unpkg. Samen goed voor **2.510 ms** waarin
er niets te zien was.

Lettertypen staan nu in [fonts/](fonts/), iconen als SVG in de pagina zelf. Wil
je een nieuw lettertype: `python tools/haal-lettertypen.py`. Een nieuw icoon:
`python tools/haal-iconen.py`.

Een `<link rel="canonical">` mag wel: dat wijst ergens heen, het haalt niets op.

*Wordt automatisch gecontroleerd.*

### 4. Foto's op de maat die de pagina echt nodig heeft

Het logo van Summa stond op 3815 pixels breed en werd op vijftig getoond: 149 KB
voor een duimnagel. Na verkleinen 8 KB.

- **Coverfoto's** krijgen automatisch een `-kaart.webp` op 800 pixels
  (`build-kaartbeeld.py`). Je hoeft niets te doen.
- **Foto's in een artikel** worden op 1600 pixels gezet door `build-galerij.py`.
- **Logo's** doe je met `python tools/verklein-logos.py` als je er een toevoegt.
- **Artikelfoto's** krijgen automatisch een `.webp` ernaast met exact dezelfde
  afmetingen (`build-artikelbeeld.py`). Dat verkleint niets, het comprimeert
  alleen beter: 9,5 MB in plaats van 15,1 MB over 94 foto's. Op een project- of
  blogpagina zie je dus gewoon het grote beeld. De JPEG blijft staan als
  origineel en als deel-thumbnail.

Vuistregel voor de maat: **het dubbele van hoe groot het in beeld staat.** Dat
dekt een telefoon met dubbele pixeldichtheid, en meer zie je niet.

**Snijden doen we nooit, alleen verkleinen.** Een foto houdt zijn eigen
verhouding. Valt hij op een kaart in een vierkant vakje, dan doet de CSS dat met
`object-fit`, en dat kun je altijd terugdraaien.

*Uitschieters worden automatisch gemeld: beeld boven 400 KB, film boven 500 KB.*

### 5. Filmpjes zijn zwaar, gebruik ze met mate

Een filmpje in een artikel met een afspeelknop staat op `preload="none"`. Dat
kost pas iets als iemand erop drukt, dus dat mag gerust groot zijn.

Een filmpje dat **vanzelf speelt** als bewegende illustratie is iets anders: dat
haalde de browser altijd binnen, ook onderaan een pagina waar je nooit komt. Over
de hele site ging dat om 24 MB, waarvan 4,7 MB op één projectpagina. Die staan nu
op `data-src` en laden pas als ze in beeld komen. Je schrijft ze gewoon als
altijd; `build-inbakken.py` zet het adres om.

Een filmpje op een **kaart** is een ander verhaal: dat speelt vanzelf af, dus de
browser haalt hem altijd helemaal op, ook als de kaart onderaan de pagina staat
en niemand ernaar kijkt. Ze zijn nu samen **1258 KB**, meer dan de helft van de
homepage, waarvan 635 KB voor één bestand.

`tools/build-kaartfilm.py` maakt daarom naast elk kaartfilmpje een
`<naam>-web.mp4`. Het origineel blijft staan, en het filmpje in het artikel
blijft ook gewoon het volledige bestand.

**Wat we onderweg leerden.** De gebruikelijke adviezen bleken hier al opgevolgd:
de filmpjes stonden al op 500 of 600 pixels en hadden al geen geluidsspoor. Wat
overbleef was de bitrate van één uitschieter. Gemeten op
`aura-bouw-lasers-kaart.mp4` (634 KB, 5 seconden, 600x600):

| instelling | resultaat |
|---|---|
| crf 32 op 600 px | 84% van origineel |
| crf 34 op 600 px | 68% |
| crf 32 op 480 px met 20 fps | 47% |
| crf 34 op 480 px met 20 fps | 38% |

De winst zit dus in **resolutie en beeldjes per seconde**, niet in de
kwaliteitsknop. Ook helpt een ruisfilter: korrel is voor een codec zowat het
duurste dat er is, want het verandert elk beeldje overal een beetje.

Daarom werkt het script met een **trapje**. Het probeert eerst volle kwaliteit,
en zakt alleen een trede als het bestand boven de 250 KB blijft. Zo houden zes
goede filmpjes hun kwaliteit en wordt alleen de uitschieter echt aangepakt. Eén
instelling voor alles zou zes filmpjes verslechteren om er één te repareren.
Komt het resultaat groter uit dan het origineel, dan wint het origineel.

**Minder beeldjes per seconde: niet doen.** Dat zat er eerst in, en op 20 fps
schokten de twee zwaarste filmpjes zichtbaar. Vloeiend beeld is belangrijker dan
de laatste vijftig kilobyte. 25 is de ondergrens, en in de praktijk laten we de
beeldsnelheid nu helemaal met rust.

### En hoe ze geladen worden

Minstens zo belangrijk als de bestandsgrootte. Twee dingen gingen hier mis:

**`preload="none"` samen met `autoplay` is een tegenstrijdige opdracht.** De
browser mag niet vooruit laden, maar moet wel meteen spelen. Dus speelde hij
terwijl het bestand binnenkwam, en dat hapert. Met vijf filmpjes tegelijk vochten
ze ook nog om dezelfde bandbreedte. Nu blijft de foto staan tot de browser zegt
dat hij het in één keer kan uitspelen (`canplaythrough`), en pas dan wisselen we.
Er zit een vangnet van vier seconden op, want die belofte doet hij op een krappe
verbinding soms nooit, en eeuwig stilstaan is erger dan een klein hikje.

**Een IntersectionObserver kijkt niet door een scrollend vak heen.** Kaarten in
een carousel zitten in een vak met `overflow-x`, en een browser rekent
zichtbaarheid ook af tegen zo'n vak. De `rootMargin` die je meegeeft rekt alleen
het venster op, niet dat vak. Kijken-per-kaart werkt daar dus niet: het filmpje
begon pas te laden op het moment dat de kaart al voor je neus stond. De oplossing
is bij een carousel naar de carousel zelf kijken, en alles erin klaarzetten zodra
die in de buurt komt. Op een gewone rasterpagina kijk je wel gewoon per kaart.

Resultaat: op `/blog/` starten de drie zichtbare kaarten meteen en de rest bij
doorscrollen. Op de homepage gaat er **1020 KB** over de lijn voor zes filmpjes,
en dat is precies één keer elk bestand: de kopieën die de carousel maakt voor het
eindeloos doorscrollen komen uit het cachegeheugen.

*Wordt automatisch gecontroleerd, maar alleen voor filmpjes die vanzelf laden.*

Wat we bewust niet doen: **WebM of AV1 ernaast** zetten. Dat scheelt nog eens
30%, maar verdubbelt je bestandenbeheer voor de laatste paar procent.

### 6. Sluit geen Vimeo of YouTube rechtstreeks in

Een ingesloten speler haalt ruim 300 KB aan JavaScript op van een vreemd domein
en zet cookies van derden, en dat gebeurt al bij het laden van de pagina. Ook
voor de meeste bezoekers die nooit op play drukken. Op `side-quest-rave` kostte
dat 393 KB, een FCP van 5,3 seconden en een LCP van 10,2 seconden. De pagina
scoorde 60 op snelheid en 77 op praktische tips.

Je schrijft nog steeds gewoon een `<iframe>` in je artikel. `build-inbakken.py`
maakt daar een namaakspeler van: het posterbeeld met een afspeelknop, en pas op
klik de echte speler. Het posterbeeld haal je één keer op met
`python tools/haal-embedposters.py`, zodat ook dat van je eigen server komt.

Na die ingreep: FCP 1,8 s, LCP 4,5 s, 0 KB naar vreemde domeinen, en 100 op
praktische tips.

### 7. Het bovenste beeld krijgt voorrang, de rest laadt lui

Alles op `loading="lazy"` zetten voelt zuinig, maar voor het bovenste beeld is
het verkeerd. Dat is meestal het grootste ding in beeld, en daar meet Google je
LCP aan af. Een luie afbeelding wordt pas opgehaald als de browser klaar is met
de rest, dus je straft precies het beeld waar de bezoeker op wacht. Op
`museum-speelklok` stond zelfs de eerste galerijfoto op lazy.

`build-inbakken.py` regelt dit: het bovenste beeld in `<main>` krijgt
`fetchpriority="high"`, verliest zijn `loading="lazy"`, en komt als
`<link rel="preload">` in de head te staan zodat de browser er meteen aan begint.
Dat bovenste beeld hoeft trouwens geen foto te zijn: op `museum-speelklok` is het
het posterbeeld van een zwevend filmpje.

### 8. Eén `<h1>`, en geen gat in de kopvolgorde

Je mag afdalen met één niveau tegelijk: h1, dan h2, dan h3. Van h1 meteen naar
h3 mag niet. Wie met een schermlezer door de koppen springt om de pagina te
overzien, verdwaalt in zo'n gat.

Teruggaan mag wel: na een h3 weer een h2 is prima.

De kaartjes regelen dit zelf. `build-inbakken.py` kijkt welke kop erboven staat
en kiest het niveau eronder. Op de homepage staan de kaarten onder
"Recente blogs" (h2), dus worden het h3's. Op `/blog/` staan ze direct onder de
h1, en dan worden het h2's.

*Wordt automatisch gecontroleerd.*

### 7. Elke pagina heeft een `<main>`

Zonder dat weet hulpsoftware niet waar het menu ophoudt en de inhoud begint. Een
schermlezer kan dan niet naar de inhoud springen, en dezelfde vraag hebben de
AI-assistenten die een pagina willen samenvatten. `build-inbakken.py` zet hem er
zelf in, tussen de header en de footer.

*Wordt automatisch gecontroleerd.*

### 9. Titel tussen de 30 en 60 tekens, description maximaal 160

Boven de 60 kapt Google je titel af. Ver eronder laat je ruimte liggen:
"Museum | Studio Wotto" is 21 tekens waar je er 60 mag gebruiken.

*Wordt automatisch gecontroleerd.*

---

## Wat de controle voor je nakijkt

```
python tools/check-snelheid.py
```

Draait automatisch mee als laatste stap van `python tools/build.py`. Het
**blokkeert nooit** de bouw: een melding is een uitnodiging om te kijken, geen
fout. Soms is een grote foto gewoon de moeite waard, en dat mag jij bepalen.

Wat het niet kan zien, en jij dus zelf moet bewaken:

- Of een nieuwe pagina echt snel laadt. Meet met Lighthouse.
- Of je alt-teksten ergens over gaan.
- Of het kleurcontrast klopt.

---

## Wat er nu nog open staat

**Kleurcontrast.** Crèmekleurige tekst op het koraal haalt 3,08 waar 4,5 de norm
is. Repareren betekent aan de merkkleur of de tekstkleur draaien, en dat is een
ontwerpkeuze, geen technische. Zolang dat niet gebeurt blijft de
toegankelijkheidsscore op 95 steken in plaats van 100.

**De filmpjes.** 1258 KB, de grootste post die nog over is. Opnieuw comprimeren
is een kwaliteitsafweging.

**Verkleinen van CSS en JavaScript: niet doen.** Lighthouse rekent voor dat het
57 KB scheelt, maar dat cijfer gaat over de bestanden op schijf. Vimexx
comprimeert ze al met gzip voordat ze de deur uitgaan: `styles.css` is 48,5 KB
op schijf en 14,8 KB over de lijn, `site.js` 20,9 KB. Verkleinen levert daar
bovenop nog een paar kilobyte op, en dat weegt niet op tegen onleesbare
bestanden.

Dit is meteen een waarschuwing bij het meten: **een testserver op je eigen
machine comprimeert meestal niet**. Meet je lokaal, dan lijken je CSS en
JavaScript ruim drie keer zo zwaar als ze in het echt zijn.
