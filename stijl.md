# Stijlgids — Studio Wotto website

> De single source of truth voor het uiterlijk van de site. Alle componenten
> toetsen we hieraan. De tokens onderaan vertalen deze keuzes direct naar CSS.

---

## Merkkarakter

Vrolijk, derpy maar toch serieus. De vibe leunt op Y2K Flash-nostalgie zonder
cheesy of kinderachtig te worden. Speels en uitnodigend aan de buitenkant, maar
strak en betrouwbaar in de basis. Kernwoorden om op terug te vallen bij twijfel:
**speels, energiek, eigenwijs, warm, en toch professioneel.**

De rode draad: het mag altijd een beetje overshooten in beweging en
persoonlijkheid, maar nooit in kleur of rommeligheid. De kleuren blijven vol en
helder, de layout blijft rustig, en de speelsheid zit in de details (beweging,
patronen, iconen). Voor een studioportfolio betekent dat: **het werk staat
centraal, de stijl is de lijst eromheen.**

---

## Kleuren

Het uitgangspunt is streng. Je gebruikt de volle merkkleuren zoals ze zijn, of
wit en ink. Geen verzachte of getinte varianten. Waar je normaal een "soft" tint
zou pakken, gebruik je in plaats daarvan een patroon (bijvoorbeeld een
stippellijn).

### Merkkleuren

| Kleur | Hex | Rol |
|---|---|---|
| **Koraal** | `#FF5757` | **Hoofd- / identiteitskleur** — hero, contact, de kleur die "Studio Wotto" is |
| **Blauw** | `#0061E0` | **Actie- / UI-kleur** — knoppen, actieve staten, links (draagt als enige witte tekst) |
| Mint | `#38C789` | Accent, vaak success |
| Zon | `#FFF069` | Accent, highlights |
| Bubblegum | `#F9B3D5` | Accent, zachte momenten |

> Koraal is de merkkleur en draagt **cream/witte tekst** als bewuste merkkeuze (hero
> + contact). Blauw blijft de werkkleur voor knoppen en acties. Zie de contrastnoot
> hieronder — wit-op-koraal gebruik je voor grote koppen/korte tekst, niet voor lange
> lopende tekst.

### Neutralen

| Kleur | Waarde | Rol |
|---|---|---|
| Ink | `#1A1A2E` | Tekst en donkere elementen |
| Cream | `#FFFEFB` | Warme off-white achtergrond |
| Cream warm | `#F7F5EE` | Subtiel warmer vlak (bijv. inputvelden) |
| Surface | `#FFFFFF` | Kaarten en panelen |
| Line | `#ECEAE2` | Zachte scheidingen |
| Border | `rgba(26,26,46,0.10)` | Definitie zonder zwart |
| Border sterk | `rgba(26,26,46,0.16)` | Waar iets meer nadruk nodig is |

### Contrast checks

- Ink op wit ≈ 17:1. Ruim AAA.
- Wit op blauw `#0061E0` ≈ 5,6:1. AA voor gewone tekst, AAA voor grote tekst.
- Ink op koraal, mint, zon en bubblegum: allemaal boven 5:1. Haalt AA.
- Wit op koraal of mint ≈ 2–3:1. Haalt géén AA → **niet gebruiken voor tekst.**

**De praktische regel:** cream/witte tekst op **blauw, ink én koraal**; op **mint, zon
en bubblegum** zet je **ink** tekst. Wit-op-koraal is een bewuste merkkeuze (contrast
~2,5:1, onder AA) — houd het daarom bij grote koppen en korte tekst, niet bij lange
lopende tekst.

---

## Achtergronden & sectiekleuren

De homepage is opgebouwd uit volle kleurvlakken: **elke sectie krijgt een eigen
merkkleur als achtergrond**, zodat je bij het scrollen door een reeks knallende
vlakken beweegt. De layout blíjft rustig — de energie zit in de kleurwissel, niet
in drukte.

### Regels

1. **Eén volle kleur per sectie.** Geen verlopen, geen getinte varianten.
2. **Tekstkleur volgt automatisch de contrastregel:** blauw/ink/koraal → cream tekst;
   mint/zon/bubblegum → ink tekst.
3. **De sectiekleur loopt overal door — géén witte vlakken.** Content staat op
   **transparante, omlijnde kaarten** (dikke ink- of cream-outline die de
   tekstkleur volgt), niet op witte surface-kaarten. Projectbeelden vullen straks
   het beeldvlak van de kaart; de sectiekleur blijft de achtergrond.
4. **Overgangen zijn golvend en bewegen continu.** Tussen twee secties een
   wave-divider die de kleur van de **volgende sectie** aanneemt en rustig, oneindig
   horizontaal meebeweegt. Pauzeert bij `prefers-reduced-motion`.
5. **Naastgelegen secties nooit dezelfde kleur.**

### Volgorde homepage

| # | Sectie | Achtergrond | Tekst |
|---|---|---|---|
| 1 | Header + Hero / landing | Koraal `#FF5757` | cream |
| 2 | Geselecteerde projecten | Zon `#FFF069` | ink |
| 3 | Wat we doen (3 kaarten) | Blauw `#0061E0` | cream |
| 4 | Klanten | Mint `#38C789` | ink |
| 5 | Recente blogs | Bubblegum `#F9B3D5` | ink |
| 6 | Get in touch (06 + e-mail) | Koraal `#FF5757` | cream |
| 7 | Footer | Ink `#1A1A2E` | cream |

Koraal (de hoofdkleur) omlijst de pagina: hero én contact. De **hero toont het logo
groot** (witte versie) + tagline. De **header kleurt mee met de sectie eronder** en
wisselt het logo tussen wit en zwart. De **header** gebruikt de **cropped
avatar-variant** (compact merk, wit → zwart op lichte secties); de **footer** de
volledige wordmark (wit). Volgorde: merk → warm-fel → koel → koel → warm-zacht →
merk → donker anker.

---

## Typografie

Fonts van Google Fonts.

- **Fredoka** — koppen én UI (hero-tagline, sectie-titels, knoppen, chips, labels,
  navigatie, kaart-titels). Rond en vriendelijk; **bold (700)** voor de grote koppen.
- **Nunito** — bodytekst en langere leesstukken. Zacht maar goed leesbaar.
- **Press Start 2P** — beschikbaar als spaarzaam pixel-/arcade-accent voor korte
  labels. Nooit voor lopende tekst. *(Momenteel niet actief in de mockup.)*

### Schaal (px)

`12, 14, 16, 18, 20, 24, 32, 40, 48` — **16** is de basis voor bodytekst. Voor de
hero mag een grotere display-maat (zie tokens: `--text-hero`).

### Gewichten

- **Nunito**: semibold voor UI-leesbaarheid, regular voor lange lopende tekst.
- **Fredoka**: medium of semibold voor koppen, bold voor de echte nadruk.
- Vermijd extra light — past niet bij het stevige karakter.

### Regelafstand & letterafstand

- Bodytekst ruim (~1,6), koppen compacter (~1,15–1,25).
- Letterafstand normaal; alleen op grote koppen een fractie strakker.

---

## Layout en ruimte

### Grid en breedte

Contentblokken in een rustig grid met een comfortabele maximale breedte
(`--content-max`), zodat regels niet te lang worden. Mobiel: één kolom. Desktop:
twee of drie kolommen voor kaartenoverzichten (projecten, blogs).

### Spacing schaal (4px-basis)

`4, 8, 12, 16, 24, 32, 48, 64` — marges en padding bouw je altíjd uit deze schaal
op (`--space-1` t/m `--space-8`), zodat alles op hetzelfde ritme zit.

### Afronding

Genereus. Kleine elementen zachte ronding, grotere vlakken meer, knoppen volledig
pill-vormig (`--radius-full`). Draagt de vriendelijke uitstraling.

---

## Responsiviteit & schaling

De site moet altijd mooi schalen tussen desktop en mobiel — nooit horizontaal
scrollen, nooit afgekapte koppen. **Mobiel-first**: we bouwen vanaf de smalste
breedte op en breiden uit.

### Breakpoints — Tailwind (min-width, mobiel-first)

| Naam | Vanaf | Gebruik |
|---|---|---|
| `sm` | 640px | grote telefoons |
| `md` | 768px | tablet — **nav wordt horizontaal** (eronder de hamburger) |
| `lg` | 1024px | kleine desktop |
| `xl` | 1280px | desktop — content capped op `--content-max` |
| `2xl` | 1536px | ruime schermen |

De kaarten-grids blijven bewust **vloeiend** (`auto-fit / minmax`) en klappen dus
op beschikbare breedte in, niet op een vaste breakpoint. De vaste breakpoints
hierboven gebruiken we voor de **nav** en eventuele latere media-queries.

### Fluïde typografie

Grote koppen schalen vloeiend mee met de viewport via `clamp()`, zodat ze op
mobiel nooit overlopen en op desktop groot blijven. De hero gebruikt `--text-hero`
(`clamp(48px, 9vw, 112px)`). Bodytekst blijft rond 16px.

### Fluïde ruimte

Sectie-padding schaalt mee met het scherm (`--section-y`, bijv.
`clamp(48px, 8vw, 96px)`), zodat de verhoudingen op elk formaat kloppen. Zijmarges
(gutters) via `--gutter` (`clamp(16px, 5vw, 64px)`).

### Grid & carousel

**Diensten** (Wat we doen) staan in een gewoon grid dat inklapt: 3 kolommen (desktop)
→ 2 (tablet) → 1 (mobiel), via `repeat(auto-fit, minmax(280px, 1fr))`.

**Projecten en blogs** staan in een **swipe-carousel** i.p.v. een grid (zie
UI-elementen → Carousel). Zo vermijden we de scheve "wees-kaart" (orphan) en blijven
de foto's groot.

### Beeld & touch

- Alle beelden `max-width: 100%` met vaste `aspect-ratio`, zodat niets rekt of overloopt.
- Touch-targets minimaal 44×44px (pill-knoppen voldoen ruim).
- Onder `md` (768px) wordt de navigatie een hamburger/uitklap (3 lijntjes → kruisje);
  vanaf `md` horizontaal.
- De **sectiekleuren blijven identiek** op elk formaat — alleen de layout herschikt.

---

## Beeld

De speelsheid komt niet uit gladde stockfotografie maar uit patronen en
iconografie.

- **Iconen:** Phosphor in **Bold**, in ink. Vaste maten: 16px inline in tekst,
  20px in knoppen/chips, 24px bij sectiekoppen, 28–32px voor hero/highlight-momenten.
- **Patronen i.p.v. tinten:** waar je een zachte variatie op een kleur wilt,
  gebruik je een behandeling zoals een stippellijn (`border-style: dotted`) in de
  volle kleur — niet de kleur lichter maken.
- **Illustratie mag**, mits het aansluit op de Y2K-speelsheid (starbursts,
  stempels, badges, mascottes met oogjes) en de vlakke, heldere kleurlogica volgt.
  Geen verlopen naar pastel.
- **Fotografie / projectbeeld** is voor een studioportfolio wél belangrijk, maar
  niet het hart van de *stijl*. Het staat **vierkant (1:1) en full-bleed** in de
  projectkaarten (geen witte omkadering), energiek en helder, en vertroebelt nooit
  de sectiekleur.
- **Zwarte outlines:** vlakke vormen en illustraties mogen een stevige zwarte
  contour krijgen (chunky stroke) — kernonderdeel van de moodboard-look (EMOTION
  SHAPES, de toetsen-illustratie). Fills blijven vlak; een speelse, verzadigde
  slagschaduw of gekleurde rand mag, maar géén pastel verloop.

### Patronen & texturen

- **Stippellijn (`dotted`)** in de volle kleur, als zachte variant i.p.v. een tint.
- **Raster / ruitjespapier** als subtiele achtergrondtextuur binnen een sectie of
  op een paneel (zoals de blauwe grid-panelen op de moodboard). Licht, laag
  contrast, nooit over lange tekst.
- **Pixel / halftone** mag als accent-textuur voor een Y2K-knipoog, spaarzaam.

### Decoratie: zwevende game- & muziek-iconen

Losse Phosphor-iconen (game én muziek: controller, ghost, dobbelsteen, vinyl,
music-notes, waveform, equalizer, sterren, hart) zweven rond de randen van elke
sectie. Regels:

- **Monochroom** — altijd `currentColor`, dus wit op koraal/blauw/ink en zwart op
  zon/mint/bubblegum. Nooit meerkleurig.
- **Spaarzaam en rond de randen** — achter de content, nooit over tekst.
- **Draaien mee met scrollen** en gaan **recht staan zodra je stilstaat** (bounce
  terug naar 0°). Pauzeert bij `prefers-reduced-motion`.

Andere Y2K-motieven mogen ook (starbursts, stickers/badges, squiggles,
speech-bubbles), mits monochroom en rustig.

### Sectie-overgangen (bewegende golf)

Tussen elke sectie zit een **golf-divider** die de kleur van de **volgende sectie**
aanneemt en **continu, langzaam horizontaal meebeweegt** (afwisselend van richting per
sectie). Pauzeert bij `prefers-reduced-motion`.

---

## Motion en interactie

Hier gaat het karakter echt leven. Alles voelt snappy en een beetje speelgoedachtig,
met net iets te veel enthousiasme in de beweging.

- **Knoppen** springen bij hover 3px omhoog en groeien 3%, met bounce-easing
  (`--ease-bounce`) die een tikje overshoot. Bij klik krimpen ze 3% en zakken 1px,
  sneller, zodat het als een echte klik voelt.
- **Schaduw beweegt mee:** groter bij hover, weg bij klik.
- **Focus** op een inputveld geeft een blauwe border plus een zachte glow-ring.
- **Modal-achtergrond** is een frosted witte blur, geen donkergrijs waas — houdt
  de sfeer licht.
- **Sectiekleuren** mogen bij binnenscrollen zacht infaden/omhoog schuiven (kort,
  subtiel) — de kleurwissel zelf is al het effect, dus overdrijf niet.
- **Zwevende iconen** draaien mee met de scroll en gaan recht staan bij stilstand;
  de **golf-overgangen** bewegen continu. Beide pauzeren bij reduced motion.
- **Algemeen principe:** korte, kwieke transities. Snel genoeg om responsief te
  voelen, met net genoeg overshoot om leuk te zijn. **Respecteer `prefers-reduced-motion`.**

---

## UI-elementen

### Header & navigatie

- **Sticky** bovenaan, compacte hoogte.
- **Kleurt mee met de sectie eronder** — achtergrond én tekstkleur nemen de kleur
  van de sectie over tijdens het scrollen (zachte transitie).
- **Logo = de cropped avatar** (compact merk): wit standaard, wordt **zwart** op
  lichte secties (zon/mint/bubblegum) via een filter, zodat het altijd leesbaar is.
- **Desktop:** horizontale links (Fredoka), meekleurend.
- **Onder `md` (< 768px):** een **hamburger** (3 lijntjes) die met een bounce naar een
  **kruisje** morpht; het menu klapt eronder uit met een **dekkende, meekleurende
  achtergrond** (nooit doorschijnend — de rest van de site blijft erachter verborgen).
- **Onder `md` — hide-on-scroll:** de header **verdwijnt bij omlaag scrollen** en
  **verschijnt weer bij omhoog scrollen** (slide met bounce). Vanaf `md` blijft de
  header altijd staan.
- **Uitklapmenu sluit vanzelf** bij scrollen, bij een klik buiten de header, bij
  Escape en na het kiezen van een link — zodat je nooit een open menu meesleept.

### Hero / landing

Koraal vlak met **het logo groot** (witte wordmark) als blikvanger, daaronder een
korte **tagline** (Fredoka bold), een lead-zin en twee knoppen (primary + ghost-light).
Zwevende game/muziek-iconen rond de randen.

### Knoppen

Pill-vormig, subtiele 1px border in ink op 10% (geen harde zwarte lijn), zachte
box-shadow. Bij interactie de bounce-animatie (hover: +3px & ×1,03; klik: krimpt).
Drie varianten:

- **Primary** — blauwe vulling, witte tekst (de actiekleur). Voor lichte/gekleurde secties.
- **Light** — cream vulling, ink tekst. Voor knoppen op koraal/blauw/ink (bijv. de
  mail- en telefoon-pills op contact).
- **Ghost (light)** — transparant met cream border + cream tekst. Secundaire actie op
  een gekleurde/donkere sectie (bijv. "Neem contact op" in de hero).

### Kaarten (algemeen)

**Transparante achtergrond** (de sectiekleur loopt door) met een **dikke omlijning
(±2,5px) in de tekstkleur** (`currentColor`: ink op lichte secties, cream op
blauw/ink). Genereuze afronding. Geen wit vlak, geen zware schaduw — de outline
geeft definitie. Bij hover een kwieke lift (bounce), evt. een klein tikje rotatie.

### Projectkaart

**Foto voorop** — de projectfoto vult de kaart **vierkant (1:1)**, afgerond, met
zachte schaduw en geen outline. Daaronder **alleen de titel** (Fredoka) en het
**thema** (discipline) als klein label. Geen omschrijving of datum. Hover: de foto
lift met bounce. De projectkaarten staan in een **carousel** (zie hieronder).

### Blogkaart

Zelfde opzet als de projectkaart: **vierkante (1:1) cover-foto** voorop, daaronder de
**titel** (Fredoka) en een korte **intro-zin** (excerpt). Ook in een **carousel**.
Hover: de foto lift met bounce.

### Carousel (projecten & blogs)

Projecten en blogs staan in een **horizontale swipe-carousel** met **scroll-snap**
(klikt netjes per kaart vast). Altijd **hele kaarten**, geen half-zichtbare "peek":
**1** op mobiel, **2** op tablet, **3** op desktop.

- **Pijlknoppen** links/rechts: een plain **Phosphor-pijl** (`arrow-right`, gespiegeld
  voor links) met een **dotted ink-ring** eromheen — geen dichte achtergrond. Ze staan
  laag in de foto (~85% hoogte), via JS gecentreerd op het beeld.
- **Adaptieve kleur:** pijl + ring zijn **ink**, maar worden **cream** boven een
  **donkere onder-hoek** van de foto. De helderheid van die hoek wordt vooraf gemeten
  (drempel ~140) en per kaart meegegeven; in productie doen we dit automatisch bij het
  bouwen. Met een beetje vooruitkijken zodat 'ie iets eerder omslaat.
- Knoppen **verbergen zich** aan begin/eind en als alles al past (desktop).

### Chips

Hier komt de stippelbehandeling het sterkst terug: in plaats van een lichte tint
de volle kleur met een `dotted` border als zachte variant. Icoon in Bold op 20px
waar nodig.

### Inputs

Warme cream-vulling, standaard zonder border. Bij focus een blauwe border plus
glow-ring. Bij validatie een dikkere border van 3px zodat fouten/successen
opvallen. *(Beperkt nodig op deze site — geen contactformulier.)*

### Tabs

Actieve tab krijgt een volle blauwe vulling (niet wit), zodat duidelijk is waar je
bent. Bijv. bruikbaar voor filters op het projectenoverzicht.

### Links & navigatie

In ink of blauw, met duidelijke maar niet schreeuwerige nadruk. Navigatie in de
UI-font (Fredoka). In het **mobiele uitklapmenu** zijn de links groter (~22px, bold)
en **volledige rijen** met genoeg padding (tikvlak ≥ 44px); op **desktop** compact
(16px, horizontaal).

### Klant-logo marquee

De klantsectie toont de logo's in een **langzame, oneindige band van links naar
rechts, over de volle breedte** (buiten de content-container, geen rand-fade).
Logo's op uniforme hoogte en **monochroom** (ink, via `brightness(0)`) zodat de set
cohesief oogt. **Pauzeert bij hover en bij `prefers-reduced-motion`.**

> Het HCM-logo heeft een eigen (bruine) achtergrond; daarvan is een omgekleurde versie
> gemaakt (`hcm_logo_bw.png`: bruin → **zwart**, tekst/balken → **wit**) die de
> zwart-filter overslaat (`.raw`) en zo naast de zwarte silhouetten past.

### Get in touch

Geen formulier. Eén grote, uitnodigende **koraal** sectie (cream tekst) met een
klikbaar **06-nummer** (`tel:`) en **e-mailadres** (`mailto:`) als **light-pills**
(cream vulling, ink tekst, met Phosphor-icoon), plus de locatie (Eindhoven).

---

## Tone of voice

Kort, direct en met een knipoog. Je spreekt de bezoeker aan alsof je naast ze
staat, niet vanaf een podium. Enthousiast zonder uitroeptekens te stapelen.
Nederlands, informeel en concreet. Waar het kan een grapje of speelse woordkeus,
maar nooit ten koste van duidelijkheid. In de kern serieus over wat de studio
doet, luchtig in hoe je het zegt. **De studio spreekt over zichzelf in de wij-vorm**
(we werken met meerdere mensen).

---

## CSS-tokens (implementatie)

Vertaling van bovenstaande keuzes naar CSS-variabelen. Deze zetten we straks in de
`:root` van de site.

```css
:root {
  /* — Kleuren — */
  --blue:        #0061E0;
  --coral:       #FF5757;
  --mint:        #38C789;
  --sun:         #FFF069;
  --bubblegum:   #F9B3D5;

  --ink:         #1A1A2E;
  --cream:       #FFFEFB;
  --cream-warm:  #F7F5EE;
  --surface:     #FFFFFF;
  --line:        #ECEAE2;
  --border:        rgba(26,26,46,0.10);
  --border-strong: rgba(26,26,46,0.16);

  /* — Sectie-tekstkleur volgt de contrastregel —
     op blauw/ink/koraal: var(--cream); op mint/zon/bubblegum: var(--ink) */
  --hdr-bg: var(--coral);  /* meekleurende header: JS zet dit per sectie */

  /* — Typografie — */
  --font-display: 'Fredoka', sans-serif;      /* grote koppen (bold) */
  --font-head:    'Fredoka', sans-serif;      /* UI, subkoppen, knoppen */
  --font-body:    'Nunito', sans-serif;       /* bodytekst */
  --font-pixel:   'Press Start 2P', monospace;/* arcade-accent */

  --text-xs:  12px;
  --text-sm:  14px;
  --text-base:16px;
  --text-md:  18px;
  --text-lg:  20px;
  --text-xl:  24px;
  --text-2xl: 32px;
  --text-3xl: 40px;
  --text-4xl: 48px;
  --text-hero: clamp(30px, 5vw, 54px); /* hero-tagline (het logo staat groot als beeld) */

  /* — Spacing (4px-basis) — */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;

  /* — Radius — */
  --radius-sm:   8px;
  --radius-md:   16px;
  --radius-lg:   24px;
  --radius-full: 999px;

  /* — Layout — */
  --content-max: 1200px;
  --gutter:    clamp(16px, 5vw, 64px);  /* zijmarge, schaalt mee */
  --section-y: clamp(48px, 8vw, 96px);  /* verticale sectie-padding */
  /* — Breakpoints (Tailwind) — @media gebruikt de vaste px; deze vars zijn ter referentie/JS — */
  --bp-sm:  640px;
  --bp-md:  768px;   /* nav wordt hier horizontaal; eronder de hamburger */
  --bp-lg:  1024px;
  --bp-xl:  1280px;
  --bp-2xl: 1536px;

  /* — Motion — */
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --dur-fast: 120ms;
  --dur:      200ms;

  /* — Schaduw (zacht, geen harde offset) — */
  --shadow-sm: 0 2px 8px  rgba(26,26,46,0.08);
  --shadow-md: 0 8px 24px rgba(26,26,46,0.12);
  --shadow-lg: 0 18px 44px rgba(26,26,46,0.18);
}
```

### Sectiekleuren als klassen (idee)

```css
.section--blue      { background: var(--blue);      color: var(--cream); }
.section--sun       { background: var(--sun);       color: var(--ink);   }
.section--coral     { background: var(--coral);     color: var(--cream); }
.section--mint      { background: var(--mint);      color: var(--ink);   }
.section--bubblegum { background: var(--bubblegum); color: var(--ink);   }
.section--ink       { background: var(--ink);       color: var(--cream); }
```
