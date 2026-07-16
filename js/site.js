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

  /* ---------- Klik een foto, blader er schermvullend doorheen ----------
     Pakt elke <img> in de tekst, in de volgorde waarin ze staan. De opmaak
     verandert dus niet: alles blijft staan waar het staat. Werkt JavaScript
     niet, dan zie je gewoon de foto's zoals altijd.
     Het bijschrift is de figcaption als die er is, anders de alt-tekst. */
  function galerij() {
    const thumbs = [...document.querySelectorAll('.article-body img')];
    if (thumbs.length < 1) return;
    thumbs.forEach(i => i.classList.add('kanGroot'));

    // Het bijschrift in de grote weergave: eerst een eigen data-cap (jouw
    // zichtbare bijschrift), anders de figcaption van een video, anders de alt.
    const bijschrift = img => {
      if (img.dataset.cap) return img.dataset.cap.trim();
      const fig = img.closest('figure');
      const cap = fig && fig.querySelector('figcaption');
      return (cap ? cap.textContent : img.alt || '').trim();
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
      const img = thumbs[nu];
      const t = bijschrift(img);
      figuur.innerHTML = '<img src="' + img.getAttribute('src') + '" alt="' + esc(img.alt || '') + '">';
      tekst.textContent = t;
      teller.textContent = (nu + 1) + ' / ' + thumbs.length;
      vorige.disabled = volgende.disabled = thumbs.length < 2;
    }

    function open(i, trigger) {
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

    thumbs.forEach((img, i) => {
      img.addEventListener('click', () => open(i, img));
      // ook bereikbaar zonder muis
      img.tabIndex = 0;
      img.setAttribute('role', 'button');
      img.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i, img); }
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

  function initSite() {
    huurChip();
    byline();
    galerij();
    const header = document.getElementById('header');
    const toggle = document.getElementById('navToggle');
    const logo   = document.getElementById('brandLogo');

    // Op content-pagina's (waar de homepage-secties ontbreken) wijzen de
    // hash-links in header en footer terug naar de homepage.
    document.querySelectorAll('.header a[href^="#"], .footer a[href^="#"]').forEach(a => {
      const id = a.getAttribute('href').slice(1);
      if (id && !document.getElementById(id)) a.setAttribute('href', base + 'index.html#' + id);
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
        d.style.transition = 'none';
        d.style.transform = 'rotate(' + rot.toFixed(1) + 'deg)';
      });
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        decos.forEach(d => { d.style.transition = 'transform .7s var(--ease-bounce)'; d.style.transform = 'rotate(0deg)'; });
      }, 130);
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
    addEventListener('resize', () => { syncHeader(); updateHeaderVisibility(); });
    syncHeader();

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
      function update(){
        if (prev) prev.disabled = track.scrollLeft <= 2;
        if (next) next.disabled = track.scrollLeft >= track.scrollWidth - track.clientWidth - 2;
      }
      prev && prev.addEventListener('click', () => track.scrollBy({left:-step(), behavior:'smooth'}));
      next && next.addEventListener('click', () => track.scrollBy({left: step(), behavior:'smooth'}));
      track.addEventListener('scroll', () => { update(); tintBtns(); }, {passive:true});
      addEventListener('resize', () => { update(); placeBtns(); tintBtns(); });
      track.querySelectorAll('img').forEach(im => { if (!im.complete) im.addEventListener('load', () => { measureItems(); placeBtns(); tintBtns(); }, {once:true}); });
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
