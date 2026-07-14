# Content-architectuur (Studio Wotto)

> Blueprint voor de content en navigatie. Bepaalt de taxonomie, de URL's, de
> frontmatter-velden en hoe alles onderling linkt. Wordt de basis voor de Astro-bouw.
> (Uiterlijk staat in `stijl.md`.)

---

## 1. Taxonomie

### Thema's (pillars, primair) — 1 per item

De drie kern-diensten. Elk krijgt een eigen pillar page.

| Sleutel | Titel | URL | Omvat |
|---|---|---|---|
| `installaties` | Interactieve installaties | `/interactieve-installaties` | museuminstallaties, interactieve tentoonstellingen |
| `webapps` | Muzikale webapps & games | `/muzikale-webapps` | webapps, games, gamification, educatieve apps |
| `podium` | Podium & instrumenten | `/podium` | muziekinstrumenten, reactieve lasers, custom controllers, props |

### Sub-subjects / kernwoorden (secundair, meerdere per item)

Snijden dwars door de pillars heen. Voor filtering, gerelateerde content en extra
zoektermen (waar mensen echt op zoeken). Krijgen niet automatisch een zware eigen pagina.

De 10 vastgestelde sub-subjects:

`gamification` · `educatie` · `muziektechnologie` · `interactieve kunst` · `museum` ·
`geluidsontwerp` · `creatieve technologie` · `games` · `phygital` · `interactieve reclame`

**Nieuwe richting:** phygital marketing in de ruimte (interactieve merkbeleving op
locatie: winkel, horeca, etalage, out of home). Gevangen onder `interactieve reclame`
(+ `phygital`). Voorbeeldconcepten in Notion, o.a. "barkeet" (scherm bij de bar, scan
QR, bestuur de game op het grote scherm met je telefoon), "Interactieve Poster (Ridder
Klimb)", en de etalage-QR-game met kortingscode.

**Speciaal:** `workshop` blijft als markering voor blogs/verhalen over gegeven workshops.

---

## 2. Sitemap (URL-structuur)

```
/                            Homepage
/interactieve-installaties   Pillar: uitleg + projecten + blogs van dit thema
/muzikale-webapps            Pillar
/muziekinstrumenten          Pillar (podium)
/projecten                   Overzicht alle projecten (evt. filter op thema)
/projecten/[slug]            Projectdetail
/blog                        Overzicht alle blogs
/blog/[slug]                 Blogdetail
/workshops                   Workshops & talks (satelliet, onderwijs-funnel)
/over-ons                    Over de studio (+ kleine workshop-vermelding)
/contact                     Contact (of op de homepage)
```

Tag-pagina's (`/tag/onderwijs` etc.): pas genereren als er genoeg content is,
anders alleen als filter. Voorkomt dunne pagina's.

---

## 3. Content collections + frontmatter (Astro)

### `projecten` (portfolio, het maakwerk)

```yaml
title: "Draw & Play"
slug: "draw-and-play"
thema: "installaties"          # 1 van de 3 pillars (verplicht)
tags: ["museum", "gamification"]
cover: "./draw-and-play.jpg"
alt: "Draw & Play arcade-kast"
client: "Museum X"             # optioneel
date: 2025-06-01
featured: true                 # toont op de homepage-carousel
excerpt: "Bezoekers tekenen hun eigen speelfiguur en spelen er meteen mee."
# body: MDX
```

### `blog`

```yaml
title: "Samenwerking met Ramses3000"
slug: "ramses3000"
thema: "podium"                # optioneel: koppelt de blog aan een pillar
tags: ["artiest", "geluidsontwerp"]
cover: "./ramses3000.jpeg"
alt: "Ramses3000 in de Effenaar"
date: 2025-05-12
featured: true                 # toont op de homepage-carousel
excerpt: "Hoe vertaal je kunstenaarstaal naar iets technisch?"
# body: MDX
```

### `workshops` (satelliet)

Voor nu één handgebouwde pagina `/workshops` (het aanbod verandert weinig). De
**voorbeelden/bewijs** komen uit blogs met de `workshop`-tag.

```yaml
# /workshops pagina
title: "Workshops & talks"
description: "Workshops en gastcolleges over creatieve technologie, o.a. op hogescholen."
```

---

## 4. Interne links (de lijm)

Dit is waar de SEO-winst en de funnel zitten. Alles kruislings verbonden:

- **Homepage "Wat we doen"-kaarten** linken naar de 3 **pillar pages**.
- **Pillar page** toont: eigen introtekst (keywords) + gerelateerde **projecten**
  (zelfde thema) + gerelateerde **blogs** (zelfde thema) + CTA naar contact.
- **Project/blog-detail** toont een **thema-chip** die teruglinkt naar de pillar,
  plus gerelateerde items (zelfde thema/tags).
- **Workshops-pagina** linkt naar de pillars én naar **`onderwijs`-getagde projecten**
  ("ook voor het onderwijs gemaakt"), plus CTA. Blogs met `workshop`-tag verschijnen
  hier als bewijs.
- **Homepage** krijgt een klein secundair **"Workshops & talks"-blok** met link naar
  `/workshops`.

### De onderwijs-funnel

```
onderwijs zoekt/vindt  ->  /workshops  ->  ziet ook maakwerk (pillars + onderwijs-projecten)  ->  contact/opdracht
```

Daarom: geef relevante projecten de tag `onderwijs`, zodat `/workshops` automatisch
"ook voor het onderwijs gemaakt" kan tonen.

---

## 5. Positionering (samengevat)

- **3 pillars = het hart** (maakwerk, in "Wat we doen").
- **Workshops & talks = vindbare satelliet**, geen pillar. Eigen pagina, secundair
  blok op de homepage, `workshop`-tag op blogs. Versterkt de professionaliteit
  (autoriteit + R&D-verhaal) en werkt als etalage richting onderwijs.
- **Tags** verbinden alles zonder de structuur te vervuilen.

---

## 6. Openstaand / later beslissen

- URL pillar 3: besloten op `/podium`.
- Krijgt `/contact` een eigen pagina of blijft het de sectie op de homepage?
  (voorlopig: homepage-sectie + gedeelde CTA-partial)
- Wanneer tag-pagina's aanzetten (afhankelijk van hoeveelheid content).
- Workshops: alle workshop-pagina's van studiowotto.com (nog live) overnemen op `/workshops`.
