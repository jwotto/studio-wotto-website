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
| `installaties` | Interactieve installaties | `/interactieve-installaties` | museuminstallaties, interactieve tentoonstellingen, sensor-kunst |
| `webapps` | Muzikale webapps & games | `/muzikale-webapps` | webapps, games, gamification, educatieve apps, QR-spellen |
| `podium` | Podium & instrumenten | `/muziekinstrumenten` | muziekinstrumenten, reactieve lasers, custom controllers, props |

*Besloten: pillar 3 gebruikt URL `/muziekinstrumenten` (sterkere zoekterm).*

### Tags (secundair, meerdere per item)

Snijden dwars door de pillars heen. Voor filtering, gerelateerde content en extra
zoektermen. Krijgen niet automatisch een zware eigen pagina.

- **Publiek/sector:** `museum`, `festival`, `onderwijs`, `merk`
- **Discipline:** `gamification`, `geluidsontwerp`, `phygital`, `conceptontwikkeling`, `props`
- **Speciaal:** `workshop` (voor blogs/verhalen over gegeven workshops)

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
/contact                     Contactpagina met het team (Jan-Willem en Jaimy)
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

## 6. Besloten

- Pillar 3 URL: `/muziekinstrumenten`.
- Contact: **beide**. Een contactsectie onderaan de homepage én een aparte
  `/contact`-pagina met het team (Jan-Willem en Jaimy).
- Tantu Beats en Ramses3000 zijn **projecten** (geen blog).
- The SideQuest Rave: 1 projectpagina, plus de Nerdland- en Muzikale-Speelplaats-verhalen als blog.

### Nog open
- Wanneer we tag-pagina's aanzetten (afhankelijk van hoeveelheid content).
- Meer projecten en artikelen volgen binnenkort (o.a. vanaf LinkedIn); de structuur is erop gebouwd.
