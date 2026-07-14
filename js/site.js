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
  function initSite() {
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
      function tintBtns(){
        // pijl + ring worden cream op een donkere onder-hoek (vooraf gemeten helderheid), anders ink
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
      track.querySelectorAll('img').forEach(im => { if (!im.complete) im.addEventListener('load', () => { placeBtns(); tintBtns(); }, {once:true}); });
      placeBtns();
      update();
      tintBtns();
    });
  }

  /* ---------- 3. Content laden en tonen ----------
     Elke map in content/ is een project of blog. We lezen manifest.json
     (de lijst mappen), halen per item de kenmerken uit de <meta>-tags,
     en vullen de lijsten/carousels op de pagina. Zo verschijnt een nieuw
     item vanzelf op de goede plek zodra het in het manifest staat. */
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
      url: base + 'content/' + slug + '/',
      coverUrl: base + 'content/' + slug + '/' + cover
    };
  }

  function loadItems(){
    return fetch(base + 'content/manifest.json')
      .then(r => r.ok ? r.json() : [])
      .then(slugs => Promise.all((slugs || []).map(slug =>
        fetch(base + 'content/' + slug + '/index.html')
          .then(r => r.text())
          .then(html => parseItem(slug, html))
          .catch(err => { console.error('Content laden mislukt:', slug, err); return null; })
      )))
      .then(items => items.filter(Boolean))
      .catch(err => { console.error('Manifest laden mislukt:', err); return []; });
  }

  function renderCard(item){
    const onder = item.type === 'blog'
      ? '<p class="project__excerpt">' + esc(item.excerpt) + '</p>'
      : '<div class="project__theme">' + esc(PILAAR_LABEL[item.pilaar] || '') + '</div>';
    return '<article class="project carousel__item">'
      + '<a href="' + item.url + '">'
      + '<div class="project__img"><img src="' + item.coverUrl + '" alt="' + esc(item.titel) + '" loading="lazy"></div>'
      + '<h3>' + esc(item.titel) + '</h3>' + onder
      + '</a></article>';
  }

  function renderCollections(items){
    document.querySelectorAll('[data-list]').forEach(el => {
      const type = el.dataset.list;              // 'project' | 'blog' | 'all'
      let list = items.filter(i => type === 'all' || i.type === type);
      if (el.dataset.featured === 'true') list = list.filter(i => i.featured);
      if (el.dataset.pilaar)  list = list.filter(i => i.pilaar === el.dataset.pilaar);
      if (el.dataset.subject) list = list.filter(i => i.subjects.includes(el.dataset.subject));
      list.sort((a, b) => (b.datum || '').localeCompare(a.datum || ''));
      if (el.dataset.limit) list = list.slice(0, +el.dataset.limit);
      el.innerHTML = list.map(renderCard).join('');
    });
  }

  /* ---------- Start ---------- */
  includePartials()
    .then(() => document.querySelector('[data-list]') ? loadItems() : [])
    .then(items => renderCollections(items))
    .then(initSite);
})();
