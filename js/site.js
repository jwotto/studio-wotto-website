/* ============================================================
   Studio Wotto - site.js
   ------------------------------------------------------------
   1. Laadt de gedeelde header en footer in (partials/).
   2. Start alle gedeelde interactie: meekleurende header,
      hamburger-menu, hide-on-scroll, zwevende iconen, carousels.

   Sluit dit op elke pagina in, als laatste in de body:
     <script src="js/site.js"></script>
   Op een pagina in een submap wijst het pad iets terug, bijv.
     <script src="../js/site.js"></script>
   Het script berekent zelf de site-root uit zijn eigen locatie,
   zodat de partials en assets kloppen op Live Server, GitHub
   Pages (submap) en Vimexx (domeinroot).
   ============================================================ */
(function () {
  'use strict';

  // Site-root afleiden uit de src van dit script.
  const self = document.currentScript;
  const base = self ? self.src.replace(/js\/site\.js(?:\?.*)?$/, '') : '';

  /* ---------- 1. Partials inladen ----------
     Elke partial is een compleet, los te bekijken HTML-bestand.
     We nemen er alleen het element met data-partial uit en zetten
     dat op de plek van de plekhouder. Relatieve paden in de partial
     (bijv. de logo's, met ../) rekenen we om naar de juiste locatie,
     zodat ze op elke pagina en op elke server kloppen. */
  function remap(node, attr, partialUrl){
    const v = node.getAttribute(attr);
    if (v && !/^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(v)) node.setAttribute(attr, new URL(v, partialUrl).href);
  }
  function includePartials() {
    const nodes = [...document.querySelectorAll('[data-include]')];
    return Promise.all(nodes.map(el => {
      const name = el.getAttribute('data-include');
      const url = new URL(base + 'partials/' + name + '.html', document.baseURI).href;
      return fetch(url)
        .then(r => r.text())
        .then(html => {
          const doc = new DOMParser().parseFromString(html, 'text/html');
          const part = doc.querySelector('[data-partial]');
          if (!part){ console.error('Geen element met data-partial in', name); return; }
          part.querySelectorAll('[src]').forEach(n => remap(n, 'src', url));
          part.querySelectorAll('[href]').forEach(n => remap(n, 'href', url));
          el.replaceWith(part);
        })
        .catch(err => console.error('Partial laden mislukt:', name, err));
    }));
  }

  /* ---------- 2. Gedeelde interactie ---------- */
  // Staat dit item te huur (meta wotto:huur)? Dan krijgt het automatisch een
  // chip naar de verhuurpagina. Zo hoef je die nooit met de hand toe te voegen
  // en kan hij ook niet vergeten worden als je later iets te huur zet.
  function huurChip() {
    const m = document.querySelector('meta[name="wotto:huur"]');
    if (!m || !/^(ja|true|1)$/i.test((m.getAttribute('content') || '').trim())) return;
    const chips = document.querySelector('.detail-chips');
    if (!chips || chips.querySelector('.chip--huur')) return;
    const a = document.createElement('a');
    a.className = 'chip chip--huur';
    a.href = base + 'installatie-huren/';
    a.innerHTML = '<i class="ph-bold ph-truck"></i> Te huur';
    chips.appendChild(a);
  }

  const MAANDEN = ['januari','februari','maart','april','mei','juni','juli',
                   'augustus','september','oktober','november','december'];

  // Wie schreef dit, en wanneer? Onderaan de tekst, uit de metatags, dus je
  // hoeft die regel nooit te typen en hij kan niet uit de pas lopen met de datum.
  //
  // Geen wotto:auteur = geen regel. Dat is met opzet: staat een stuk in de
  // wij-vorm, dan is het van de studio en hoeft er niemand onder. Juist daardoor
  // betekent het iets als er wel een naam staat.
  function byline() {
    const body = document.querySelector('.article-body');
    if (!body || body.querySelector('.byline')) return;
    const m = n => {
      const el = document.querySelector('meta[name="wotto:' + n + '"]');
      return el ? (el.getAttribute('content') || '').trim() : '';
    };
    const auteur = m('auteur');
    if (!auteur) return;

    let tekst = 'Geschreven door <a href="' + base + 'contact/">' + esc(auteur) + '</a>';
    const datum = m('datum');
    if (datum) {
      const d = datum.split('-');
      const mooi = d.length === 3 ? (+d[2]) + ' ' + MAANDEN[+d[1] - 1] + ' ' + d[0] : datum;
      tekst += ' · <time datetime="' + esc(datum) + '">' + mooi + '</time>';
    }
    const p = document.createElement('p');
    p.className = 'byline';
    p.innerHTML = tekst;
    body.appendChild(p);
  }

  /* ---------- Bijschrift onder een tegel ----------
     In het raster staat geen tekst onder de tegels, maar op een smal scherm
     staat elk beeld over de volle breedte en hoort het bijschrift er gewoon
     onder. Die tekst staat al in data-cap (die de schermvullende weergave ook
     gebruikt), dus die hoef je niet een tweede keer in de HTML te zetten: hier
     komt er een figure met figcaption omheen. De CSS bepaalt wanneer je hem
     ziet, dus in het raster blijft hij verborgen. Filmpjes hebben hun figcaption
     al in de HTML staan en worden overgeslagen. */
  function tegelBijschriften() {
    document.querySelectorAll('.article-body .gallery img[data-cap]').forEach(img => {
      if (img.closest('figure')) return;            // heeft er al een
      const tekst = img.dataset.cap.trim();
      if (!tekst) return;
      const fig = document.createElement('figure');
      const cap = document.createElement('figcaption');
      cap.textContent = tekst;
      img.parentNode.insertBefore(fig, img);
      fig.appendChild(img);
      fig.appendChild(cap);
    });
  }

  /* ---------- Klik een foto, blader er schermvullend doorheen ----------
     Pakt elke <img> in de tekst plus de filmpjes die in een galerij staan, in de
     volgorde waarin ze staan. Foto's en filmpjes zitten dus in dezelfde reeks:
     je bladert er in één keer doorheen. De opmaak verandert niet, alles blijft
     staan waar het staat. Werkt JavaScript niet, dan zie je gewoon de beelden.
     Hier hoort ook het bijschrift thuis: in het raster staat er geen tekst onder
     de tegels, die lees je pas als je een beeld openklikt.
     Zwevende filmpjes in de lopende tekst blijven erbuiten, die houden hun eigen
     "tik voor geluid". */
  function galerij() {
    const thumbs = [...document.querySelectorAll('.article-body img, .article-body .gallery video')];
    if (thumbs.length < 1) return;

    // Op een telefoon staat elk beeld al over de volle breedte, met het
    // bijschrift er gewoon onder. Schermvullend bladeren voegt daar niets toe,
    // dus daar zetten we deze weergave uit. Let op: niet één keer bij het laden
    // kijken, maar meeluisteren. Draai je je telefoon of sleep je je venster
    // smaller, dan gaat hij alsnog uit (en andersom weer aan).
    const smal = window.matchMedia('(max-width:720px)');

    // Het bijschrift in de grote weergave: eerst een eigen data-cap, anders de
    // figcaption uit de figure eromheen, anders de alt-tekst.
    const bijschrift = el => {
      if (el.dataset.cap) return el.dataset.cap.trim();
      const fig = el.closest('figure');
      const cap = fig && fig.querySelector('figcaption');
      return (cap ? cap.textContent : el.alt || '').trim();
    };

    const box = document.createElement('div');
    box.className = 'lightbox';
    box.hidden = true;
    box.innerHTML =
      '<div class="lightbox__bar"><span class="lightbox__teller"></span>'
      + '<button class="lightbox__sluit" type="button" aria-label="Sluiten">✕</button></div>'
      + '<div class="lightbox__figuur"></div>'
      + '<p class="lightbox__tekst"></p>'
      + '<button class="lightbox__knop lightbox__knop--vorige" type="button" aria-label="Vorige">←</button>'
      + '<button class="lightbox__knop lightbox__knop--volgende" type="button" aria-label="Volgende">→</button>';
    document.body.appendChild(box);

    const figuur = box.querySelector('.lightbox__figuur');
    const tekst  = box.querySelector('.lightbox__tekst');
    const teller = box.querySelector('.lightbox__teller');
    const vorige = box.querySelector('.lightbox__knop--vorige');
    const volgende = box.querySelector('.lightbox__knop--volgende');
    const sluitKnop = box.querySelector('.lightbox__sluit');
    let nu = 0, vanwaar = null;

    function toon(i) {
      nu = (i + thumbs.length) % thumbs.length;
      const el = thumbs[nu];
      const t = bijschrift(el);
      if (el.tagName === 'VIDEO') {
        // Schermvullend wil je het filmpje echt kunnen horen en terugspoelen,
        // dus hier mét bediening en geluid. In het raster speelt hij gedempt.
        const poster = el.getAttribute('poster');
        figuur.innerHTML = '<video src="' + esc(el.getAttribute('src')) + '"'
          + (poster ? ' poster="' + esc(poster) + '"' : '')
          + ' controls autoplay playsinline></video>';
      } else {
        figuur.innerHTML = '<img src="' + el.getAttribute('src') + '" alt="' + esc(el.alt || '') + '">';
      }
      tekst.textContent = t;
      teller.textContent = (nu + 1) + ' / ' + thumbs.length;
      vorige.disabled = volgende.disabled = thumbs.length < 2;
    }

    function open(i, trigger) {
      if (smal.matches) return;      // smal scherm: alles staat al vullend
      vanwaar = trigger;
      box.hidden = false;
      document.body.style.overflow = 'hidden';
      toon(i);
      sluitKnop.focus();
    }

    function sluit() {
      box.hidden = true;
      figuur.innerHTML = '';
      document.body.style.overflow = '';
      if (vanwaar) vanwaar.focus();          // terug naar de foto waar je vandaan kwam
    }

    // Aan of uit, afhankelijk van de schermbreedte. Is er niets te openen, dan
    // ook geen klikbare cursor, geen tabstop en geen knop-rol voor een
    // schermlezer: anders beloof je iets wat niet gebeurt.
    function stemAf() {
      const uit = smal.matches;
      thumbs.forEach(el => {
        el.classList.toggle('kanGroot', !uit);
        if (uit) { el.removeAttribute('role'); el.removeAttribute('tabindex'); }
        else { el.setAttribute('role', 'button'); el.tabIndex = 0; }
      });
      if (uit && !box.hidden) sluit();   // stond hij open, dan gaat hij dicht
    }
    stemAf();
    smal.addEventListener('change', stemAf);

    thumbs.forEach((el, i) => {
      el.addEventListener('click', () => open(i, el));
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i, el); }
      });
    });
    vorige.addEventListener('click', () => toon(nu - 1));
    volgende.addEventListener('click', () => toon(nu + 1));
    sluitKnop.addEventListener('click', sluit);
    // Klik je naast de foto, dan ga je eruit. Let op: alles behalve de foto zelf
    // en de knoppen telt als "naast", dus ook het bijschrift en de balk bovenin.
    // Een simpele check op e.target === box zou alleen werken op de smalle rand
    // eromheen, want de vakken erbinnen vangen de klik af.
    box.addEventListener('click', e => {
      if (e.target.closest('button')) return;
      if (e.target.tagName === 'IMG' || e.target.tagName === 'VIDEO') return;
      sluit();
    });
    document.addEventListener('keydown', e => {
      if (box.hidden) return;
      if (e.key === 'Escape') sluit();
      if (e.key === 'ArrowLeft') toon(nu - 1);
      if (e.key === 'ArrowRight') toon(nu + 1);
    });

    // vegen op een telefoon
    let x0 = null;
    box.addEventListener('touchstart', e => { x0 = e.changedTouches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', e => {
      if (x0 === null) return;
      const d = e.changedTouches[0].clientX - x0;
      if (Math.abs(d) > 50) toon(nu + (d < 0 ? 1 : -1));
      x0 = null;
    }, { passive: true });
  }

  /* ---------- Filmpjes: autoplay zonder geluid, tik voor geluid ----------
     De projectvideo's (class="film") spelen vanzelf af, gedempt en in een lus,
     net als de bewegende covers op de kaarten. Eén tik zet het geluid aan en
     brengt de bediening in beeld, zodat je kunt pauzeren of terugspoelen. Wie
     in zijn systeem minder beweging wil, krijgt geen autoplay maar de poster
     met bediening. Zonder JavaScript speelt de video gewoon gedempt door: dat
     is een nette terugval, geen kapotte pagina. */
  const SPEAKER_SVG =
    '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" aria-hidden="true">'
    + '<path d="M4 9v6h4l5 4V5L8 9H4z" fill="currentColor"/>'
    + '<path d="M16 9l5 5m0-5l-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

  function filmpjes() {
    const stil = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const smal = window.matchMedia('(max-width:720px)');
    document.querySelectorAll('.article-body video.film').forEach(v => {
      const fig = v.closest('figure') || v.parentElement;
      if (fig) fig.classList.add('heeft-film');

      // Minder beweging gewenst: niet automatisch spelen, wel bediening tonen.
      if (stil) {
        v.removeAttribute('autoplay');
        v.controls = true;
        v.pause();
        return;
      }

      v.muted = true;   // borgen dat de autoplay ook op mobiel mag starten

      // Staat het filmpje in een galerij, dan opent een tik op een breed scherm
      // de schermvullende weergave en zit daar de bediening én het geluid al.
      // Deze knop is daar dus overbodig; de CSS verbergt hem boven 720px. Op een
      // smal scherm is er geen schermvullende weergave, dus daar blijft hij
      // staan en is dit de enige manier om het filmpje te horen.
      const inGalerij = !!v.closest('.gallery');

      const badge = document.createElement('button');
      badge.type = 'button';
      badge.className = 'film-badge';
      badge.setAttribute('aria-label', 'Geluid aanzetten');
      badge.innerHTML = SPEAKER_SVG + '<span>Tik voor geluid</span>';
      if (fig) fig.appendChild(badge);

      // Geluid aan + bediening erbij. Vanaf nu handelt de speler zelf klikken
      // af (play/pauze), dus onze eigen klik-om-te-ontdempen trekt zich terug.
      function aan() {
        v.muted = false;
        v.volume = 1;
        v.controls = true;
        v.play().catch(() => {});
      }
      // In een galerij op een breed scherm is de klik van de schermvullende
      // weergave, niet van ons: dan hier niets doen.
      v.addEventListener('click', () => {
        if (inGalerij && !smal.matches) return;
        if (!v.controls) aan();
      });
      badge.addEventListener('click', e => { e.stopPropagation(); aan(); });
      // Dempt iemand later weer via de eigen knop van de speler, dan komt het
      // badge terug als hint.
      v.addEventListener('volumechange', () => { badge.hidden = !v.muted; });

      v.tabIndex = 0;
      v.addEventListener('keydown', e => {
        if ((e.key === 'Enter' || e.key === ' ') && !v.controls) { e.preventDefault(); aan(); }
      });
    });
  }

  /* ---------- Externe links in een nieuw tabblad ----------
     Alles wat naar een andere site wijst (social media, verwijzingen, enz.)
     opent in een nieuw tabblad, zodat de bezoeker studiowotto niet verlaat.
     Interne links en links naar je eigen (toekomstige) studiowotto-domein
     blijven gewoon in hetzelfde tabblad. Draait op elke <a>, ook op de links
     uit de partials en de kaarten, dus nieuwe externe links krijgen dit
     vanzelf: je hoeft nooit met de hand target="_blank" te typen.
     rel="noopener noreferrer" hoort erbij: zonder dat kan de nieuwe pagina via
     window.opener aan jouw tab zitten, en het houdt de verwijzer privé. */
  function externeLinks() {
    const hier = location.host;
    document.querySelectorAll('a[href]').forEach(a => {
      if (a.protocol !== 'http:' && a.protocol !== 'https:') return;  // mailto:, tel:, #: met rust laten
      if (!a.host || a.host === hier) return;                         // interne link
      if (/studiowotto/i.test(a.host)) return;                        // eigen domein telt als intern
      if (a.target) return;                                           // al bewust ingesteld? niet overschrijven
      a.target = '_blank';
      const rels = new Set((a.rel || '').split(/\s+/).filter(Boolean));
      rels.add('noopener'); rels.add('noreferrer');
      a.rel = [...rels].join(' ');
    });
  }

  function initSite() {
    huurChip();
    byline();
    tegelBijschriften();   // vóór galerij(): die pakt de tegels zoals ze dan staan
    galerij();
    filmpjes();
    externeLinks();
    const header = document.getElementById('header');
    const toggle = document.getElementById('navToggle');
    const logo   = document.getElementById('brandLogo');

    // Op content-pagina's (waar de homepage-secties ontbreken) wijzen de
    // hash-links in header en footer terug naar de homepage.
    document.querySelectorAll('.header a[href^="#"], .footer a[href^="#"]').forEach(a => {
      const id = a.getAttribute('href').slice(1);
      if (id && !document.getElementById(id)) a.setAttribute('href', base + '#' + id);
    });

    function closeMenu(){
      if (header) header.classList.remove('nav-open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }

    // Hamburger openen/sluiten + sluiten bij klik buiten header of Escape
    if (header && toggle){
      toggle.addEventListener('click', () => {
        const open = header.classList.toggle('nav-open');
        toggle.setAttribute('aria-expanded', open);
      });
      header.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', closeMenu));
      document.addEventListener('click', e => { if (header.classList.contains('nav-open') && !header.contains(e.target)) closeMenu(); });
      document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
    }

    /* De adresbalk van een mobiele browser kleurt mee met de sectie waar je bent.
       Dat is dezelfde kleur die de header krijgt, dus die zetten we hier gelijk
       mee. In de <head> van elke pagina staat theme-color op koraal; die stand
       geldt tot dit script draait en blijft gelden als er geen JavaScript is.
       Staat de meta er niet (een pagina die door een tool is gemaakt), dan maken
       we hem alsnog aan. Alleen bij een echte verandering, want dit loopt mee met
       elke scrollbeweging. */
    let themaMeta = document.querySelector('meta[name="theme-color"]');
    let themaKleur = '';
    function zetThemaKleur(kleur){
      if (!kleur || kleur === themaKleur) return;
      themaKleur = kleur;
      if (!themaMeta){
        themaMeta = document.createElement('meta');
        themaMeta.setAttribute('name', 'theme-color');
        document.head.appendChild(themaMeta);
      }
      themaMeta.setAttribute('content', kleur);
    }

    // Header kleurt mee met de sectie eronder; wit logo wordt zwart op lichte secties
    const blocks = [...document.querySelectorAll('[data-nav]')].filter(b => b !== header);
    function syncHeader(){
      if (!header || !blocks.length) return;
      const y = header.offsetHeight + 2;
      let active = blocks[0];
      for (const b of blocks){ const r = b.getBoundingClientRect(); if (r.top <= y && r.bottom > y){ active = b; break; } }
      const cs = getComputedStyle(active);
      header.style.setProperty('--hdr-bg', cs.backgroundColor);
      header.style.color = cs.color;
      zetThemaKleur(cs.backgroundColor);
      if (logo) logo.style.filter = active.dataset.nav === 'light' ? 'none' : 'brightness(0)';
    }

    // Zwevende figuurtjes draaien mee met scrollen, gaan recht staan bij stilstand
    const decos = [...document.querySelectorAll('.deco')];
    let idleTimer;
    function spinDecos(){
      const y = window.scrollY;
      decos.forEach((d, i) => {
        const dir = (i % 2) ? 1 : -1;
        const rot = y * (0.22 + (i % 4) * 0.05) * dir;
        d.style.transition = 'opacity .25s linear';   // draaien volgt de scroll direct, faden mag wel zacht
        d.style.transform = 'rotate(' + rot.toFixed(1) + 'deg)';
      });
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        decos.forEach(d => { d.style.transition = 'transform .7s var(--ease-bounce), opacity .25s linear'; d.style.transform = 'rotate(0deg)'; });
      }, 130);
    }

    /* Zwevende figuurtjes gaan nooit achter de inhoud staan
       -----------------------------------------------------
       Een icoon staat absoluut geplaatst in procenten van zijn sectie, maar de
       tekst zit in een container van maximaal 1200px. Op een breed scherm valt
       left:6% dus in de lege marge ernaast. Maak je het venster smaller, dan is
       die marge op en schuift de tekst onder het icoon. Een vaste breakpoint
       zou een gok zijn: de ene sectie is breder dan de andere, en de logoband
       bij de klanten loopt op elk formaat van rand tot rand. Dus meten we het
       na. Overlapt een icoon een inhoudsblok, dan faden we hem weg; is er weer
       ruimte, dan komt hij terug.
       Draait bij het laden, na het inladen van de kaarten en bij resize. Niet
       bij scrollen: dan verschuift het beeld, niet de indeling. */
    const DECO_LUCHT = 10;   // pixels ademruimte die een icoon om zich heen wil
    const DECO_BOTST = 'h1,h2,h3,h4,p,li,dl,figure,img,video,.btn,.chip,.card,.project,.carousel__viewport,.clients';
    const DECO_TEKST = /^(H1|H2|H3|H4|P|LI|DL)$/;
    // Een kop of alinea is een blok zo breed als de container, ook als er maar
    // twee woorden in staan of als de tekst gecentreerd is. Zouden we dat blok
    // meten, dan zou een icoon naast "Onze projecten" al botsen met de lege
    // helft ernaast. Daarom meten we bij tekst de regels zelf (getClientRects
    // geeft de regelvakken) en alleen bij beeld en kaarten het hele element.
    function vakken(el){
      if (DECO_TEKST.test(el.tagName)){
        const r = document.createRange();
        r.selectNodeContents(el);
        return [...r.getClientRects()];
      }
      return [el.getBoundingClientRect()];
    }
    function checkDecos(){
      if (!decos.length) return;
      // De golfranden hangen met translateY boven hun eigen sectie uit en liggen
      // dus in de sectie erbóven; de header ligt over de hero heen. Allebei niet
      // te vinden binnen de sectie van het icoon, dus die meten we apart.
      const vast = [...document.querySelectorAll('.wave-top'), header]
        .filter(Boolean).map(el => el.getBoundingClientRect());
      const perSectie = new Map();
      decos.forEach(d => {
        if (d.classList.contains('deco--kop')) return;   // hangt aan de kop, botst nooit
        const sec = d.closest('.section');
        if (!sec) return;
        if (!perSectie.has(sec)){
          perSectie.set(sec, [...sec.querySelectorAll(DECO_BOTST)]
            .flatMap(vakken)
            .filter(r => r.width > 0 && r.height > 0)
            .concat(vast));
        }
        // Het icoon draait mee met de scroll, en een gedraaid vierkant heeft een
        // grotere omhullende rechthoek. We rekenen daarom terug naar het
        // ongedraaide vak rond het middelpunt: anders zou hetzelfde icoon bij de
        // ene scrollstand wel botsen en bij de andere niet.
        const b = d.getBoundingClientRect();
        const mx = (b.left + b.right) / 2, my = (b.top + b.bottom) / 2;
        const hw = d.offsetWidth / 2 + DECO_LUCHT, hh = d.offsetHeight / 2 + DECO_LUCHT;
        const botst = perSectie.get(sec).some(o =>
          mx - hw < o.right && mx + hw > o.left && my - hh < o.bottom && my + hh > o.top);
        d.classList.toggle('deco--weg', botst);
      });
    }

    // Mobiel: header verbergt bij scrollen omlaag, verschijnt bij omhoog
    let lastScrollY = window.scrollY;
    function updateHeaderVisibility(){
      if (!header) return;
      const y = window.scrollY;
      if (window.innerWidth < 768 && !header.classList.contains('nav-open')){
        if (y > lastScrollY && y > header.offsetHeight + 8) header.classList.add('header--hidden');
        else if (y < lastScrollY) header.classList.remove('header--hidden');
      } else {
        header.classList.remove('header--hidden');
      }
      lastScrollY = y;
    }

    let ticking = false;
    addEventListener('scroll', () => {
      if (!ticking){ ticking = true; requestAnimationFrame(() => { if (header && header.classList.contains('nav-open')) closeMenu(); syncHeader(); updateHeaderVisibility(); spinDecos(); ticking = false; }); }
    }, {passive:true});
    // Resize meet de iconen opnieuw na: precies bij het slepen van je venster
    // schuift de tekst onder ze door. Via requestAnimationFrame, zodat we bij
    // het slepen één keer per beeld meten in plaats van per resize-event.
    let decoTicking = false;
    addEventListener('resize', () => {
      syncHeader();
      updateHeaderVisibility();
      if (!decoTicking){ decoTicking = true; requestAnimationFrame(() => { checkDecos(); decoTicking = false; }); }
    });
    syncHeader();
    checkDecos();
    // Nog een keer als alle foto's binnen zijn: die kunnen de indeling nog
    // verschuiven nadat het script al gedraaid heeft.
    addEventListener('load', checkDecos);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(checkDecos);

    // Carousels - pijltjes scrollen per kaart; verbergen als alles al past
    document.querySelectorAll('.carousel').forEach(car => {
      const viewport = car.querySelector('.carousel__viewport');
      const track = car.querySelector('.carousel__track');
      const prev  = car.querySelector('[data-dir="-1"]');
      const next  = car.querySelector('[data-dir="1"]');
      const btns  = car.querySelectorAll('.carousel__btn');
      function step(){
        const it = track.querySelector('.carousel__item');
        const g = parseFloat(getComputedStyle(track).columnGap) || 24;
        return it ? it.getBoundingClientRect().width + g : track.clientWidth;
      }
      function placeBtns(){
        const img = track.querySelector('.project__img') || track.querySelector('img');
        if (!img || !viewport) return;
        const vp = viewport.getBoundingClientRect(), ir = img.getBoundingClientRect();
        const top = (ir.top - vp.top) + ir.height * 0.85;   // echt onderin de foto
        btns.forEach(b => b.style.top = top + 'px');
      }
      // Meet de helderheid (0-255) van de onderste hoeken van een foto. Dit gebeurt
      // in de browser, dus het klopt vanzelf voor elke nieuwe foto die je toevoegt.
      function measureLum(img){
        const W = 32, H = 32;
        const c = document.createElement('canvas');
        c.width = W; c.height = H;
        const ctx = c.getContext('2d', { willReadFrequently: true });
        ctx.drawImage(img, 0, 0, W, H);
        function avg(x0, x1, y0, y1){
          const d = ctx.getImageData(x0, y0, x1 - x0, y1 - y0).data;
          let sum = 0, n = 0;
          for (let i = 0; i < d.length; i += 4){
            sum += 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];   // waargenomen helderheid
            n++;
          }
          return n ? sum / n : 255;
        }
        const yTop = Math.round(H * 0.68);   // de pijlen staan laag in de foto
        return { left: avg(0, Math.round(W * 0.3), yTop, H), right: avg(Math.round(W * 0.7), W, yTop, H) };
      }
      function measureItems(){
        track.querySelectorAll('.carousel__item').forEach(item => {
          if (item.dataset.lumLeft) return;                        // al gemeten
          const img = item.querySelector('.project__img img');
          if (!img || !img.complete || !img.naturalWidth) return;  // nog niet geladen
          try {
            const l = measureLum(img);
            item.dataset.lumLeft  = Math.round(l.left);
            item.dataset.lumRight = Math.round(l.right);
          } catch (e) { /* canvas afgeschermd: pijl blijft gewoon ink */ }
        });
      }
      function tintBtns(){
        // pijl + ring worden cream op een donkere onder-hoek van de foto, anders ink
        const THRESHOLD = 140;
        function darkFor(btn, side){
          const b = btn.getBoundingClientRect();
          const pad = b.width * 0.5;
          const zL = b.left - pad, zR = b.right + pad;
          let min = null;
          track.querySelectorAll('.carousel__item').forEach(item => {
            const r = item.getBoundingClientRect();
            if (r.right > zL && r.left < zR){
              const v = side === 'left' ? item.dataset.lumLeft : item.dataset.lumRight;
              if (v != null && v !== ''){ const n = +v; if (min === null || n < min) min = n; }
            }
          });
          return min !== null && min < THRESHOLD;
        }
        if (prev) prev.classList.toggle('on-dark', darkFor(prev, 'left'));
        if (next) next.classList.toggle('on-dark', darkFor(next, 'right'));
      }
      /* ---- Oneindig doorscrollen ----
         De reeks kaarten staat er drie keer: een kopie ervoor, de echte, en een
         kopie erna. Je begint in de middelste. Scrol je voorbij een grens, dan
         verspringt de scrollpositie met precies één reeksbreedte. Omdat de
         kopieën identiek zijn zie je van die sprong niets, maar je kunt eindeloos
         door in allebei de richtingen.
         Alleen als er meer kaarten zijn dan er passen. Hoeveel er passen hangt
         van de schermbreedte af, dus dit wordt bij resize opnieuw bekeken. */
      const echte = [...track.children];
      let reeksBreedte = 0;                 // 0 = geen lus actief
      let thuis = 0;                        // stand waarbij de echte reeks vooraan staat

      // Eén kopie aan elke kant is genoeg. Dat is te danken aan
      // scroll-snap-stop:always in de stylesheet: je legt nooit meer dan één
      // kaart per veeg af, dus na elke kaart staat de strook even stil en kan de
      // sprong daar ongemerkt gebeuren. Zonder die regel kwam je in één worp
      // twintig kaarten ver en had je hier veel meer aanloop voor nodig.
      // Zet je hem hoger, dan houden alleen de binnenste kopieën hun bewegende
      // cover; zie kopie() hieronder.
      const KOPIEEN_PER_KANT = 1;

      function sloopLus(){
        track.querySelectorAll('[data-kloon]').forEach(k => k.remove());
        reeksBreedte = 0;
        thuis = 0;
      }
      function bouwLus(){
        if (echte.length < 2) return;
        const kopie = binnenste => echte.map(el => {
          const k = el.cloneNode(true);
          k.dataset.kloon = '1';
          // Uit de tab-volgorde en weg voor een schermlezer: anders loop je
          // meerdere keren langs dezelfde projecten.
          k.setAttribute('aria-hidden', 'true');
          k.querySelectorAll('a').forEach(a => a.tabIndex = -1);
          // Een bewegende cover is een <video>, en die kosten een telefoon
          // geheugen. Alleen de kopieën naast de echte reeks houden hem: verder
          // dan die kom je nooit als de strook stilstaat. De buitenste kopieën
          // zie je alleen tijdens een snelle veeg, en dan is de posterfoto
          // ruimschoots genoeg.
          if (!binnenste) k.querySelectorAll('video').forEach(v => {
            const foto = document.createElement('img');
            foto.src = v.getAttribute('poster') || '';
            foto.alt = '';
            foto.loading = 'lazy';
            foto.decoding = 'async';
            v.replaceWith(foto);
          });
          return k;
        });
        // prepend en append met alle knopen van een reeks tegelijk, niet één voor
        // één met insertBefore: dan zou elke volgende kloon vóór de vorige
        // belanden en stond de reeks achterstevoren. Tussen de reeksen onderling
        // maakt de volgorde niet uit, die zijn identiek.
        // De eerste ronde komt tegen de echte reeks aan te liggen, de volgende
        // ronde daarbuiten. Vandaar dat alleen ronde 0 de binnenste is.
        for (let i = 0; i < KOPIEEN_PER_KANT; i++){
          track.prepend(...kopie(i === 0));
          track.append(...kopie(i === 0));
        }
        // Waar de echte reeks begint is precies het aantal kopieën maal één reeks.
        thuis = echte[0].offsetLeft;
        reeksBreedte = thuis / KOPIEEN_PER_KANT;
        zetDirect(thuis);
      }
      // Zonder animatie verspringen: scroll-behavior staat in de CSS op smooth,
      // en een sprong die je ziet aankomen is geen sprong meer.
      function zetDirect(x){
        const oud = track.style.scrollBehavior;
        track.style.scrollBehavior = 'auto';
        track.scrollLeft = x;
        track.style.scrollBehavior = oud;
      }
      function houdInHetMidden(){
        if (!reeksBreedte) return;
        let sprong = 0;
        if (track.scrollLeft < thuis - reeksBreedte * 0.5) sprong = reeksBreedte;
        else if (track.scrollLeft > thuis + reeksBreedte * 0.5) sprong = -reeksBreedte;
        if (!sprong) return;
        zetDirect(track.scrollLeft + sprong);
        // Sleep je op dit moment met de muis, dan moet je vertrekpunt mee
        // verspringen. Anders rekent de volgende muisbeweging nog vanaf de oude
        // positie en klapt de strook terug.
        if (sleep) sleep.links += sprong;
      }
      /* Wannéér we verspringen luistert nauw. Doe je het op het moment dat je de
         grens passeert, dan zit je midden in een veegbeweging: op een telefoon
         scrolt die daarna nog na, en zet je de scrollpositie hard om, dan hakt de
         browser die naloop af of tekent hij nog één beeldje vanaf de oude plek.
         Dat is de hapering. Daarom wachten we tot de beweging klaar is. Dat kan
         rustig, want na elke sprong heb je een volledige reeks speling, en dat
         zijn elf kaarten: verder komt geen enkele veeg.
         Twee uitzonderingen waarbij het wél meteen moet:
         - je sleept met de muis. Dan is er geen naloop om af te hakken, en de
           sprong moet bij zijn voordat je verder trekt.
         - je bent echt vlak bij het einde van de gekloonde reeks. Dan is
           verspringen minder erg dan tegen een muur aan lopen. Dat haal je alleen
           met een uitzonderlijk harde veeg. */
      /* ---- Onze eigen vloeiende beweging ----
         De pijltjes, het invliegen en het vastklikken na het slepen sturen we
         zelf, beeldje voor beeldje, in plaats van met behavior:'smooth'. Twee
         redenen. Ten eerste de duur: die van de browser is een stuk trager en
         valt niet in te stellen. Ten tweede, en dat is de belangrijkste: nu
         weten we precies wanneer hij bezig is. Tijdens zo'n beweging mag je hem
         niet opnieuw vastpakken, want dan volgt er nooit een rustig moment en
         moet de lus alsnog midden in je beweging verspringen. Aan het eind staat
         de strook gegarandeerd één beeldje stil, en juist daar doen we de sprong.
         Scroll-snap moet er tijdens onze eigen beweging even uit, anders vecht
         het vastklikken van de browser tegen wat wij aan het doen zijn. */
      const SNAPDUUR = 220;                 // milliseconden, korter dan de browser doet
      let animatie = 0;                     // 0 = wij bewegen niet
      function zachtNaar(x){
        if (animatie) cancelAnimationFrame(animatie);
        const start = track.scrollLeft, afstand = x - start, t0 = performance.now();
        track.style.scrollSnapType = 'none';
        track.style.scrollBehavior = 'auto';
        let klaar = false;
        function afronden(){
          if (klaar) return;
          klaar = true;
          if (animatie) cancelAnimationFrame(animatie);
          animatie = 0;
          track.scrollLeft = x;             // exact op de kaartgrens, nooit ertussenin
          track.style.scrollSnapType = '';
          track.style.scrollBehavior = '';
          houdInHetMidden();                // het stille moment: nu mag de sprong
          // Stond je al te wachten met je vinger op de strook? Dan pakken we hem
          // nu alsnog op, vanaf waar je vinger op dit moment is. Anders zou je
          // opnieuw moeten beginnen omdat je net iets te vroeg was.
          if (wilSlepen && vinger){
            wilSlepen = false;
            startSlepen(vinger.x, vinger.y);
          }
        }
        animatie = requestAnimationFrame(function stap(nu){
          if (klaar) return;
          const p = Math.min((nu - t0) / SNAPDUUR, 1);
          track.scrollLeft = start + afstand * (1 - Math.pow(1 - p, 3));   // vlot weg, netjes afremmen
          if (p < 1) animatie = requestAnimationFrame(stap); else afronden();
        });
        // Vangnet: in een tabblad op de achtergrond staat requestAnimationFrame
        // stil, en dan zou de strook halverwege blijven hangen met snap uit.
        setTimeout(afronden, SNAPDUUR + 400);
      }
      function zachtMet(d){ zachtNaar(track.scrollLeft + d); }

      let stilTimer, vorigeStand = 0, vingerOpScherm = false;
      track.addEventListener('touchstart', () => { vingerOpScherm = true; }, { passive: true });
      addEventListener('touchend', () => { vingerOpScherm = false; }, { passive: true });
      addEventListener('touchcancel', () => { vingerOpScherm = false; }, { passive: true });

      function bijnaOp(){
        const max = track.scrollWidth - track.clientWidth;
        const rand = reeksBreedte * 0.15;
        return track.scrollLeft < rand || track.scrollLeft > max - rand;
      }
      function naDeBeweging(){
        if (!reeksBreedte) return;
        if (sleep || bijnaOp()){ houdInHetMidden(); return; }
        const snelheid = Math.abs(track.scrollLeft - vorigeStand);
        vorigeStand = track.scrollLeft;
        // De staart van een veeg: je vinger is los en het rolt nog maar een paar
        // pixels per beeldje na. Dan hoeven we niet te wachten tot het écht
        // stilstaat, want zo'n sprong valt daar niet meer op. Zo pakken we het
        // gaatje tussen twee vegen, in plaats van het te missen omdat je alweer
        // aan het volgende bezig bent.
        // Ligt je vinger nog op het scherm, dan nooit: dan volgt de strook je
        // vinger en zou je hem onder je duim zien wegspringen.
        if (!vingerOpScherm && !animatie && snelheid < 3){ houdInHetMidden(); return; }
        clearTimeout(stilTimer);
        stilTimer = setTimeout(houdInHetMidden, 80);
      }
      function herbouwLus(){
        sloopLus();
        if (track.scrollWidth > track.clientWidth + 4) bouwLus();
        // Heeft het opschuiven nog niet plaatsgevonden (de carousel staat nog
        // onder de vouw), dan zet de strook zich opnieuw een kaart vooruit.
        zetKlaarVoorIntro();
      }

      function update(){
        // In een lus is er geen begin en geen eind, dus de pijlen blijven aan.
        if (reeksBreedte){
          if (prev) prev.disabled = false;
          if (next) next.disabled = false;
          return;
        }
        if (prev) prev.disabled = track.scrollLeft <= 2;
        if (next) next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 2;
      }

      /* ---- Slepen met de muis ----
         Vegen werkt op een telefoon vanzelf, maar met een muis is een
         scroll-strook niet uitnodigend. Tijdens het slepen gaat scroll-snap uit,
         want anders vecht het snappen tegen je hand; bij loslaten klikt hij op de
         dichtstbijzijnde kaart vast. Je mag zo ver trekken als je wilt: dat het
         vegen op een telefoon bij één kaart stopt komt uit scroll-snap-stop, en
         dat geldt hier niet omdat we de scrollpositie zelf sturen. Dat hoeft ook
         niet, want na het loslaten staat de strook stil en dáár kan de lus
         ongemerkt verspringen. Heb je echt gesleept, dan slikken we de klik erna
         in: anders open je een project terwijl je alleen wilde scrollen. */
      // vinger = waar de muis of vinger nu is, zolang hij neer is. Ook als we
      // (nog) niet slepen, want tijdens onze eigen animatie wachten we even.
      // wilSlepen = je hebt vastgepakt terwijl die animatie liep.
      let sleep = null, netGesleept = false, zelfGedaan = false, vinger = null, wilSlepen = false;
      // Raakt de bezoeker de strook zelf aan, dan laat het invliegen hem verder
      // met rust: dan weet hij het al.
      ['pointerdown', 'wheel', 'touchstart', 'keydown'].forEach(soort =>
        track.addEventListener(soort, () => { zelfGedaan = true; }, { passive: true }));
      // De dichtstbijzijnde kaartgrens bij een willekeurige scrollstand.
      function opKaart(x){
        const s = step(), basis = track.firstElementChild ? track.firstElementChild.offsetLeft : 0;
        return Math.round((x - basis) / s) * s + basis;
      }
      // Een kaart is een link met een foto erin, en daar heeft de browser zijn
      // eigen sleepgedrag voor: "sleep deze afbeelding of link ergens heen". Dat
      // kapen we hier, want anders neemt hij de muis over zodra je een foto
      // vastpakt, krijgen wij geen bewegingen meer door en kun je alleen tussen
      // de foto's slepen. Wat je ervoor inlevert: een projectfoto naar je
      // bureaublad slepen kan niet meer. Rechtermuisknop opslaan werkt gewoon.
      track.addEventListener('dragstart', e => e.preventDefault());
      function startSlepen(x, y){
        sleep = { x: x, y: y, links: track.scrollLeft, ver: 0, richting: 0, punten: [] };
        track.classList.add('sleept');
        track.style.scrollSnapType = 'none';
        track.style.scrollBehavior = 'auto';
      }
      track.addEventListener('pointerdown', e => {
        if (e.pointerType === 'mouse' && e.button !== 0) return;
        if (e.target.closest('.carousel__btn')) return;
        vinger = { x: e.clientX, y: e.clientY };
        // Loopt onze eigen beweging nog? Dan niet meteen vastpakken, anders grijp
        // je erin voordat hij op een kaartgrens staat en is er geen rustig moment
        // voor de lus. Maar we onthouden wél dat je wilt slepen: zodra de
        // animatie klaar is (hooguit 220 milliseconden) pakt hij alsnog op, en
        // dan vanaf de plek waar je vinger op dat moment is. Zo hoef je niet
        // opnieuw te beginnen als je te vroeg was.
        if (animatie){ wilSlepen = true; return; }
        startSlepen(e.clientX, e.clientY);
      });
      addEventListener('pointermove', e => {
        if (vinger){ vinger.x = e.clientX; vinger.y = e.clientY; }
        if (!sleep) return;
        const dx = e.clientX - sleep.x, dy = e.clientY - sleep.y;
        // Eerst uitzoeken wat je van plan bent. Een verticale veeg op een
        // telefoon is de pagina scrollen, niet de strook: daar blijven we vanaf.
        // Zolang het te klein is om dat te zien doen we nog niets.
        if (!sleep.richting){
          if (Math.abs(dx) < 6 && Math.abs(dy) < 6) return;
          sleep.richting = Math.abs(dx) > Math.abs(dy) ? 1 : 2;
          if (sleep.richting === 2){ stopSlepen(true); return; }
        }
        sleep.ver = Math.max(sleep.ver, Math.abs(dx));
        track.scrollLeft = sleep.links - dx;
        // De laatste tiende seconde onthouden, zodat we bij loslaten weten hoe
        // hard je aan het bewegen was. Een kort tikje is net zo goed een
        // bedoeling als een lange haal.
        const nu = performance.now();
        sleep.punten.push({ x: e.clientX, t: nu });
        while (sleep.punten.length > 2 && nu - sleep.punten[0].t > 100) sleep.punten.shift();
        if (e.cancelable) e.preventDefault();     // geen tekstselectie tijdens het slepen
      });
      // Acht pixels, niet vier: op een trackpad beweeg je tijdens een gewone klik
      // bijna altijd een paar pixels, en dan zou een bedoelde klik als sleep
      // gelden en het project niet opengaan.
      const SLEEPGRENS = 8;
      function stopSlepen(afbreken){
        if (!sleep) return;
        const gesleept = !afbreken && sleep.richting === 1;
        netGesleept = gesleept && sleep.ver > SLEEPGRENS;
        const sleepStand = sleep.links, sleepPunten = sleep.punten;
        sleep = null;
        track.classList.remove('sleept');
        if (gesleept){
          // Waar komt hij uit? Sleep je ver, dan gewoon naar de dichtstbijzijnde
          // kaart: twee of drie kaarten in één haal mag. Maar een klein veegje
          // moet ook tellen, anders veert hij terug en lijkt hij vastgeplakt.
          // Daarom twee manieren om "ik wil verder" te zeggen: een klein stukje
          // slepen (een twaalfde kaart, dus zo'n veertig pixels), of gewoon even
          // vegen. Dat laatste meten we over de laatste tiende seconde van je
          // beweging, zodat een tikje aan het eind ook telt.
          // De twee getallen onderin bepalen hoe gretig hij is: hoger betekent
          // dat je meer moeite moet doen voordat hij doorschuift. Ze staan
          // bewust laag: een veegje moet gewoon meegaan.
          const s = step();
          const vanaf = opKaart(sleepStand);
          const kaarten = (track.scrollLeft - vanaf) / s;
          let vaart = 0;                       // pixels per milliseconde, in scrollrichting
          if (sleepPunten.length > 1){
            const eerste = sleepPunten[0], laatste = sleepPunten[sleepPunten.length - 1];
            const dt = laatste.t - eerste.t;
            if (dt > 0) vaart = -(laatste.x - eerste.x) / dt;
          }
          const kant = Math.abs(kaarten) > 0.001 ? Math.sign(kaarten) : Math.sign(vaart);
          const stappen = Math.abs(kaarten) >= 0.5 ? Math.round(kaarten)
                        : (Math.abs(vaart) > 0.15 || Math.abs(kaarten) > 0.08) ? kant
                        : 0;
          // Let op: scroll-snap hier NIET eerst terugzetten. Doe je dat wel, dan
          // begint de browser meteen zijn eigen trage vastklik-animatie en loopt
          // die over de onze heen. Je ziet dan de traagste van de twee, en dat is
          // precies waarom slepen zwaarder aanvoelde dan de pijltjesknoppen.
          // zachtNaar regelt snap zelf: uit tijdens de beweging, aan als hij
          // exact op de kaartgrens staat.
          zachtNaar(vanaf + stappen * s);
        } else {
          // Niets zijwaarts gedaan (een klik, of je scrolde de pagina verticaal):
          // gewoon alles terugzetten zoals het was, zonder animatie.
          track.style.scrollSnapType = '';
          track.style.scrollBehavior = '';
        }
        setTimeout(() => { netGesleept = false; }, 0);
      }
      // Let op de pijltjesfuncties: geef je stopSlepen rechtstreeks mee, dan komt
      // het event als eerste argument binnen en is 'afbreken' altijd waar.
      addEventListener('pointerup', () => { vinger = null; wilSlepen = false; stopSlepen(false); });
      // pointercancel betekent dat de browser het gebaar heeft overgenomen,
      // bijvoorbeeld omdat je toch verticaal ging scrollen. Dan niets doen.
      addEventListener('pointercancel', () => { vinger = null; wilSlepen = false; stopSlepen(true); });
      // In de capture-fase, dus vóór de link zelf erop reageert.
      track.addEventListener('click', e => {
        if (netGesleept){ e.preventDefault(); e.stopPropagation(); }
      }, true);

      /* ---- Eén kaart opschuiven zodra je de carousel voor het eerst ziet ----
         De strook begint één kaart verder dan waar hij hoort te staan en schuift
         bij het eerste zicht die ene kaart terug. Je ziet dus een kaart naar
         rechts wegschuiven terwijl er van links een binnenkomt, en je eindigt
         precies goed: de eerste kaart op zijn plek. Zo weet je meteen dat er meer
         naast staat, en dat het allebei de kanten op kan.
         Eén keer per paginabezoek, en niet bij prefers-reduced-motion of als
         IntersectionObserver ontbreekt: dan staat de strook meteen goed. */
      const stil = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      // viewport moet erbij: zonder dat element kijken we nergens naar, en dan
      // zou de strook wél een kaart opgeschoven worden maar nooit terugschuiven.
      const magSchuiven = !stil && 'IntersectionObserver' in window && !!viewport;
      let introKlaar = false;
      function zetKlaarVoorIntro(){
        if (introKlaar || !magSchuiven) return;
        if (!reeksBreedte && track.scrollWidth <= track.clientWidth + 4) return;
        zetDirect(track.scrollLeft + step());
      }
      if (magSchuiven){
        // Het klaarzetten zelf gebeurt in herbouwLus, want daar staat de lus pas.
        // Pas schuiven als de kaarten hélemaal in beeld staan, niet als er een
        // rand van te zien is: anders beweegt de strook terwijl je er nog naartoe
        // scrollt en mis je het. Vandaar drempel 1 op de kaartenstrook zelf.
        // Past die niet in je scherm (een liggende telefoon), dan zou drempel 1
        // nooit gehaald worden en zou de strook een kaart verschoven blijven
        // staan. Daarom telt vanaf 0,6 ook, maar alléén in dat geval.
        const kijker = new IntersectionObserver((entries, obs) => {
          entries.forEach(en => {
            const past = en.boundingClientRect.height <= window.innerHeight;
            if (!en.isIntersecting) return;
            if (past ? en.intersectionRatio < 0.99 : en.intersectionRatio < 0.6) return;
            obs.disconnect();
            introKlaar = true;
            // Zelf al aan het scrollen of slepen? Dan laat de strook je met rust,
            // want dan weet je het al.
            if (sleep || zelfGedaan) return;
            zachtMet(-step());
          });
        }, { threshold: [0.6, 0.99, 1] });
        kijker.observe(viewport);
      }

      prev && prev.addEventListener('click', () => zachtMet(-step()));
      next && next.addEventListener('click', () => zachtMet(step()));
      track.addEventListener('scroll', () => { naDeBeweging(); update(); tintBtns(); }, {passive:true});
      // Kent de browser scrollend, dan weet hij zelf precies wanneer de beweging
      // klaar is, inclusief de naloop. Dat is nauwkeuriger dan onze eigen timer,
      // die blijft ernaast staan voor browsers die het nog niet kennen.
      if ('onscrollend' in window) track.addEventListener('scrollend', houdInHetMidden);
      // De lus opnieuw bouwen kost 22 kaarten slopen en terugzetten, dus dat doen
      // we niet bij elke pixel die je sleept aan je venster: pas als je stilstaat.
      let resizeTimer;
      addEventListener('resize', () => {
        update(); placeBtns(); tintBtns();
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(herbouwLus, 200);
      });
      track.querySelectorAll('img').forEach(im => { if (!im.complete) im.addEventListener('load', () => { measureItems(); placeBtns(); tintBtns(); }, {once:true}); });
      herbouwLus();
      measureItems();
      placeBtns();
      update();
      tintBtns();
    });
  }

  /* ---------- 3. Content laden en tonen ----------
     Elk content-item is een eigen map in werk/ (bijv. /werk/ramses3000/).
     De map is neutraal: de <meta name="wotto:type"> in de HTML bepaalt of
     het een project of een blog is, zodat de URL nooit hoeft te wijzigen
     als je dat omzet. We lezen content.json (de lijst mappen), halen per
     item de kenmerken uit de meta-tags, en vullen de lijsten/carousels. */
  function slugify(s){ return (s || '').trim().toLowerCase().replace(/\s+/g, '-'); }
  function esc(s){ return (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
  const PILAAR_LABEL = { installaties:'Interactieve installaties', webapps:'Muzikale webapps & games', podium:'Podium & instrumenten' };

  function parseItem(slug, html){
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const m = n => { const el = doc.querySelector('meta[name="wotto:' + n + '"]'); return el ? (el.getAttribute('content') || '').trim() : ''; };
    const cover = m('cover') || 'cover.jpg';
    return {
      slug,
      type: (m('type') || 'project').toLowerCase(),
      pilaar: m('pilaar').toLowerCase(),
      subjects: m('subjects').split(',').map(slugify).filter(Boolean),
      titel: m('titel') || slug,
      excerpt: m('excerpt'),
      datum: m('datum'),
      featured: /^(ja|true|1)$/i.test(m('featured')),
      huur: /^(ja|true|1)$/i.test(m('huur')),          // staat dit stuk te huur op locatie?
      url: base + 'werk/' + slug + '/',
      coverUrl: base + 'werk/' + slug + '/' + cover,
      // Optioneel: een kort, geluidloos filmpje dat op de kaart afspeelt in
      // plaats van de foto. Alleen voor loops. Goed gecomprimeerd is zo'n
      // filmpje lichter dan de foto zelf. De cover blijft nodig: als poster,
      // als deel-thumbnail, en voor wie geen beweging wil zien.
      videoUrl: m('videocover') ? base + 'werk/' + slug + '/' + m('videocover') : ''
    };
  }

  function loadItems(){
    return fetch(base + 'content.json')
      .then(r => r.ok ? r.json() : [])
      .then(slugs => Promise.all((slugs || []).map(slug =>
        fetch(base + 'werk/' + slug + '/index.html')
          .then(r => r.text())
          .then(html => parseItem(slug, html))
          .catch(err => { console.error('Content laden mislukt:', slug, err); return null; })
      )))
      .then(items => items.filter(Boolean))
      .catch(err => { console.error('Manifest laden mislukt:', err); return []; });
  }

  function renderCard(item, inCarousel){
    // Projecten tonen hun pijler, blogs en workshops hun korte intro.
    const onder = item.type === 'project'
      ? '<div class="project__theme">' + esc(PILAAR_LABEL[item.pilaar] || '') + '</div>'
      : '<p class="project__excerpt">' + esc(item.excerpt) + '</p>';
    // Bewegende cover, maar alleen als iemand daar geen last van heeft. Wie in
    // zijn systeem heeft staan dat hij minder beweging wil (dat is een echte
    // instelling, o.a. tegen misselijkheid), krijgt gewoon de foto.
    const stil = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const beeld = (item.videoUrl && !stil)
      ? '<video src="' + item.videoUrl + '" poster="' + item.coverUrl + '" preload="none"'
        + ' autoplay loop muted playsinline aria-label="' + esc(item.titel) + '"></video>'
      : '<img src="' + item.coverUrl + '" alt="' + esc(item.titel) + '" loading="lazy">';
    return '<article class="project' + (inCarousel ? ' carousel__item' : '') + '">'
      + '<a href="' + item.url + '">'
      + '<div class="project__img">' + beeld + '</div>'
      + '<h3>' + esc(item.titel) + '</h3>' + onder
      + '</a></article>';
  }

  function renderCollections(items){
    document.querySelectorAll('[data-list]').forEach(el => {
      // 'project' | 'blog' | 'workshop' | 'all', of meerdere: 'project,blog'
      const types = el.dataset.list.split(',').map(s => s.trim()).filter(Boolean);
      let list = items.filter(i => types.includes('all') || types.includes(i.type));
      if (el.dataset.featured === 'true') list = list.filter(i => i.featured);
      if (el.dataset.huur === 'true') list = list.filter(i => i.huur);
      if (el.dataset.pilaar)  list = list.filter(i => i.pilaar === el.dataset.pilaar);
      if (el.dataset.subject) list = list.filter(i => i.subjects.includes(el.dataset.subject));
      list.sort((a, b) => (b.datum || '').localeCompare(a.datum || ''));
      if (el.dataset.limit) list = list.slice(0, +el.dataset.limit);
      const inCarousel = el.classList.contains('carousel__track');
      // Niets gevonden? Toon de boodschap uit data-empty in plaats van een gat.
      el.innerHTML = list.map(i => renderCard(i, inCarousel)).join('')
        || (el.dataset.empty ? '<p class="list-empty">' + esc(el.dataset.empty) + '</p>' : '');
    });
  }

  /* ---------- Start ---------- */
  includePartials()
    .then(() => document.querySelector('[data-list]') ? loadItems() : [])
    .then(items => renderCollections(items))
    .then(initSite);
})();
