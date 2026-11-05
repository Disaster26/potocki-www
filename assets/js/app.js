/* Potocki Dwór - skrypty wspólne dla wszystkich podstron. Bez bibliotek (poza Leaflet na stronie Kontakt). */
(function () {
  'use strict';
  var CFG = window.POTOCKI_CONFIG || {};
  var ROOT = document.body.getAttribute('data-root') || '';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var pamiec = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- pomiar: zdarzenia konwersji (GA4 + Meta Pixel), zgody Consent Mode v2 ---------- */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  var PIXEL_EV = { generate_lead: 'Lead', click_tel: 'Contact', begin_reservation: 'InitiateCheckout' };
  window.potockiTrack = function (nazwa, param) {
    param = param || {};
    window.dataLayer.push(Object.assign({ event: nazwa }, param));
    if (CFG.ga4 && window.gtag) window.gtag('event', nazwa, param);
    if (CFG.metaPixel && window.fbq && PIXEL_EV[nazwa]) window.fbq('track', PIXEL_EV[nazwa], param);
  };
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-ev]');
    if (a) window.potockiTrack(a.getAttribute('data-ev'), { miejsce: document.body.getAttribute('data-strona') });
  });

  (function zgody() {
    if (!CFG.ga4 && !CFG.metaPixel) return; /* brak kont = brak plikow cookies = brak banera */
    window.gtag = gtag;
    gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied', wait_for_update: 500 });
    if (CFG.ga4) {
      var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(CFG.ga4);
      document.head.appendChild(s); gtag('js', new Date()); gtag('config', CFG.ga4);
    }
    function pixel() {
      if (!CFG.metaPixel || window.fbq) return;
      /* oficjalny kod Meta Pixel (skrocony loader) */
      var n = window.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
      var t = document.createElement('script'); t.async = true; t.src = 'https://connect.facebook.net/en_US/fbevents.js'; document.head.appendChild(t);
      window.fbq('init', CFG.metaPixel); window.fbq('track', 'PageView');
    }
    function zastosuj(zgoda) {
      var v = zgoda ? 'granted' : 'denied';
      gtag('consent', 'update', { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v });
      if (zgoda) pixel();
    }
    function baner() {
      var b = document.createElement('div'); b.className = 'zgody'; b.setAttribute('role', 'dialog'); b.setAttribute('aria-label', 'Zgody na pliki cookies');
      b.innerHTML = '<p>Używamy plików cookies do statystyk odwiedzin (Google Analytics) i mierzenia skuteczności reklam (Meta). Możesz się zgodzić albo zostawić tylko niezbędne.</p>' +
        '<div class="akcje"><button type="button" class="btn btn-glowny" data-z="1">Zgadzam się</button><button type="button" class="btn btn-obrys" data-z="0">Tylko niezbędne</button></div>';
      b.addEventListener('click', function (e) { var x = e.target.closest('[data-z]'); if (!x) return; var z = x.getAttribute('data-z') === '1'; pamiec.set('potocki_zgoda', z ? '1' : '0'); zastosuj(z); b.remove(); });
      document.body.appendChild(b);
    }
    var zap = pamiec.get('potocki_zgoda');
    if (zap === null) baner(); else zastosuj(zap === '1');
    $$('[data-cookies-ustawienia]').forEach(function (x) { x.hidden = false; x.addEventListener('click', function () { if (!$('.zgody')) baner(); }); });
  })();

  /* ---------- naglowek: cienka linia po przewinieciu ---------- */
  (function () {
    var g = $('.gora'); if (!g) return;
    var u = function () { g.classList.toggle('przewiniete', scrollY > 8); };
    u(); window.addEventListener('scroll', u, { passive: true });
  })();

  /* ---------- pokaz zdjec w hero glownej (co ok. 6 s; stop: reduced motion, ukryta karta, wybor reczny) ---------- */
  (function () {
    var f = $('[data-pokaz]'); if (!f) return;
    var zdj = $$('img', f), wsk = $$('.pokaz-wsk button', f), i = 0, t = null, reczny = false;
    var spokoj = matchMedia('(prefers-reduced-motion: reduce)');
    var pokaz = function (n) {
      i = (n + zdj.length) % zdj.length;
      var im = zdj[i]; if (im.loading === 'lazy') im.loading = 'eager';
      zdj.forEach(function (x, k) { x.classList.toggle('aktywne', k === i); });
      wsk.forEach(function (b, k) { b.setAttribute('aria-current', k === i); });
    };
    var stop = function () { clearInterval(t); t = null; };
    var start = function () { stop(); if (reczny || spokoj.matches || document.hidden) return; t = setInterval(function () { pokaz(i + 1); }, 6000); };
    wsk.forEach(function (b, k) { b.addEventListener('click', function () { reczny = true; stop(); pokaz(k); }); });
    document.addEventListener('visibilitychange', start);
    if (spokoj.addEventListener) spokoj.addEventListener('change', start);
    /* kolejne zdjecia dociagamy po zaladowaniu strony (pierwsze ma preload) */
    window.addEventListener('load', function () { zdj.slice(1).forEach(function (x) { x.loading = 'eager'; }); });
    start();
  })();

  /* ---------- menu mobilne ---------- */
  (function () {
    var h = $('.ham'), p = $('#panel'); if (!h || !p) return;
    var ustaw = function (o) { h.setAttribute('aria-expanded', o); p.classList.toggle('otwarte', o); document.body.style.overflow = o ? 'hidden' : ''; };
    h.addEventListener('click', function () { ustaw(h.getAttribute('aria-expanded') !== 'true'); });
    $$('a', p).forEach(function (a) { a.addEventListener('click', function () { ustaw(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') ustaw(false); });
    matchMedia('(min-width:1001px)').addEventListener('change', function (e) { if (e.matches) ustaw(false); });
  })();

  /* ---------- dolny pasek na telefonie - dopiero po przewinieciu za przyciski z pierwszego ekranu ---------- */
  (function () {
    var m = $('.mob'); if (!m) return;
    var t = $('.hero-cta') || $('[data-mob-trigger]');
    var pokaz = function (v) { m.classList.toggle('widac', v); m.setAttribute('aria-hidden', !v); $$('a', m).forEach(function (a) { a.tabIndex = v ? 0 : -1; }); };
    if (!t || !('IntersectionObserver' in window)) { pokaz(true); return; }
    new IntersectionObserver(function (w) { w.forEach(function (x) { pokaz(!x.isIntersecting && x.boundingClientRect.top < 0); }); }, { threshold: 0 }).observe(t);
  })();

  /* ---------- powiekszanie zdjec ---------- */
  var LB = (function () {
    var d = $('#lightbox'); if (!d || !d.showModal) return null;
    var img = $('img', d), op = $('.lb-opis', d), lista = [], i = 0;
    function pokaz() { var x = lista[i]; img.src = x.getAttribute('data-src'); img.alt = x.getAttribute('data-opis') || ''; op.textContent = x.getAttribute('data-opis') || ''; $$('.lb-nav', d).forEach(function (b) { b.hidden = lista.length < 2; }); }
    function otworz(btn) {
      var gr = btn.closest('[data-lb-grupa]');
      lista = gr ? $$('[data-lb]', gr) : [btn]; i = Math.max(0, lista.indexOf(btn)); pokaz(); d.showModal();
    }
    document.addEventListener('click', function (e) { var b = e.target.closest('[data-lb]'); if (b) { e.preventDefault(); otworz(b); } });
    $('.lb-zamknij', d).addEventListener('click', function () { d.close(); });
    $('.lb-pop', d).addEventListener('click', function () { i = (i - 1 + lista.length) % lista.length; pokaz(); });
    $('.lb-nast', d).addEventListener('click', function () { i = (i + 1) % lista.length; pokaz(); });
    d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
    d.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') $('.lb-pop', d).click(); if (e.key === 'ArrowRight') $('.lb-nast', d).click(); });
    d.addEventListener('close', function () { img.removeAttribute('src'); });
    return { otworz: otworz };
  })();

  /* ---------- karta menu (dane z assets/js/menu-data.js) ---------- */
  (function () {
    var box = $('#menu-lista'), kat = $('#menu-kat'), M = window.POTOCKI_MENU;
    if (!box || !M) return;
    var IMG = ROOT + 'assets/img/';
    var html = '', chipy = '';
    M.forEach(function (k) {
      chipy += '<a href="#kat-' + k.id + '">' + esc(k.nazwa) + '</a>';
      html += '<section class="kat" id="kat-' + k.id + '" aria-labelledby="h-' + k.id + '"><h3 id="h-' + k.id + '"><button type="button" class="kat-przel" aria-expanded="true" aria-controls="kt-' + k.id + '">' + esc(k.nazwa) + '<span class="kat-ile">' + k.pozycje.filter(function (p) { return !p.grupa; }).length + '</span></button></h3><div class="kat-tresc" id="kt-' + k.id + '">';
      if (k.zdjecia) html += '<div class="drinki-foto" data-lb-grupa>' + k.zdjecia.map(function (z) { return '<button type="button" data-lb data-src="' + IMG + z + '-1200.webp" data-opis="Drinki z baru Potockiego Dworu"><img src="' + IMG + z + '-400.webp" alt="Drink z baru Potockiego Dworu" loading="lazy" width="300" height="400"></button>'; }).join('') + '</div>';
      html += '<div class="dania" data-lb-grupa>';
      k.pozycje.forEach(function (p) {
        if (p.grupa) { html += '<h4 class="kat-grupa">' + esc(p.grupa) + (p.uwaga ? ' <span class="kat-uwaga">(' + esc(p.uwaga) + ')</span>' : '') + '</h4>'; return; }
        var f = p.img ? '<button type="button" class="danie-foto" data-lb data-src="' + IMG + p.img + '-1200.webp" data-opis="' + esc(p.n) + (p.c ? ' - ' + esc(p.c) : '') + '" aria-label="Zdjęcie: ' + esc(p.n) + '"><img src="' + IMG + p.img + '-400.webp" alt="' + esc(p.n) + '" loading="lazy" width="92" height="92"></button>' : '';
        html += '<article class="danie' + (p.img ? ' z-foto' : '') + '">' + f + '<h4>' + esc(p.n) + '</h4><span class="cena">' + esc(p.c) + '</span>' + (p.s ? '<p class="sklad">' + esc(p.s) + '</p>' : '') + '</article>';
      });
      html += '</div></div></section>';
    });
    box.innerHTML = html;
    /* telefon: akordeon (pierwsza kategoria otwarta), komputer: wszystkie kategorie rozwiniete + zakladki */
    var tel = matchMedia('(max-width:760px)');
    var katy = $$('.kat', box);
    var rozwin = function (s, o) { s.classList.toggle('zwin', !o); $('.kat-przel', s).setAttribute('aria-expanded', o); };
    var trybTel = function () { katy.forEach(function (s, i) { rozwin(s, tel.matches ? i === 0 : true); }); };
    trybTel(); tel.addEventListener('change', trybTel);
    box.addEventListener('click', function (e) {
      var b = e.target.closest('.kat-przel'); if (!b || !tel.matches) return;
      var s = b.closest('.kat'), o = s.classList.contains('zwin'); rozwin(s, o);
      if (o) { var r = s.getBoundingClientRect(); if (r.top < 60) s.scrollIntoView({ block: 'start' }); }
    });
    if (location.hash && /^#kat-/.test(location.hash)) { var h = $(location.hash); if (h) rozwin(h, true); }
    if (kat) {
      kat.innerHTML = chipy;
      var linki = $$('a', kat), sekcje = $$('.kat', box);
      var ustaw = function (id) {
        linki.forEach(function (a) {
          var t = a.getAttribute('href') === '#' + id; a.setAttribute('aria-current', t);
          if (t) { var kr = kat.getBoundingClientRect(), ar = a.getBoundingClientRect(); if (ar.left < kr.left + 8 || ar.right > kr.right - 8) kat.scrollTo({ left: kat.scrollLeft + ar.left - kr.left - 16, behavior: 'smooth' }); }
        });
      };
      /* aktywna = ostatnia kategoria, ktorej poczatek minal pasek kategorii */
      var pasek = kat.closest('.menu-kat'), czeka = false, ostatnia = null;
      var sprawdz = function () {
        czeka = false;
        var granica = pasek.getBoundingClientRect().bottom + 24, akt = sekcje[0];
        sekcje.forEach(function (s) { if (s.getBoundingClientRect().top <= granica) akt = s; });
        if (akt.id !== ostatnia) { ostatnia = akt.id; ustaw(akt.id); }
      };
      window.addEventListener('scroll', function () { if (!czeka) { czeka = true; requestAnimationFrame(sprawdz); } }, { passive: true });
      sprawdz();
    }
  })();

  /* ---------- formularze: walidacja + podsumowanie zapytania (docelowo wysylka przez WordPress) ---------- */
  function adresDla(rodzaj) { var e = CFG.emaileFormularzy || {}; return e[rodzaj] || CFG.email || 'recepcja@potockidwor.pl'; }
  window.potockiDodatki = {}; /* rodzaj formularza -> funkcja zwracajaca dodatkowe linie (np. dane z planera) */
  /* wysylka przez serwer strony (wyslij.php): znacznik jednorazowy + pulapka na boty; bez adresu = tryb podgladu (program pocztowy) */
  var URL_F = (CFG.formularz && CFG.formularz.url) ? (/^(https?:)?\//.test(CFG.formularz.url) ? CFG.formularz.url : ROOT + CFG.formularz.url) : '';
  var znacznik = null, znKiedy = 0, znLaduje = null;
  function pobierzZnacznik(swiezy) {
    if (!swiezy && znacznik && Date.now() - znKiedy < 3 * 3600e3) return Promise.resolve(znacznik);
    if (znLaduje) return znLaduje;
    znLaduje = fetch(URL_F + '?znacznik=1', { cache: 'no-store', credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (j) { znacznik = j.z; znKiedy = Date.now(); return znacznik; })
      .then(function (z) { znLaduje = null; return z; }, function (e) { znLaduje = null; throw e; });
    return znLaduje;
  }
  var czekaj = function (ms) { return new Promise(function (ok) { setTimeout(ok, ms); }); };
  /* proba 0: znacznik z pamieci; 'szybko' (< 3 s od pobrania znacznika) = ten sam znacznik po chwili;
     'znacznik' (wygasl / zuzyty) = nowy znacznik i odczekanie 3 s; najwyzej jedna ponowna proba */
  function wyslijSerwer(dane, proba, zTen) {
    var zp = zTen ? Promise.resolve(zTen) : (proba ? pobierzZnacznik(true).then(function (z) { return czekaj(3200).then(function () { return z; }); }) : pobierzZnacznik());
    return zp.then(function (z) {
      /* serwer przyjmuje znacznik najwczesniej 3 s po wydaniu: przy bardzo szybkim wypelnieniu czekamy reszte */
      var wiek = Date.now() - znKiedy;
      return (z === znacznik && wiek < 3300 ? czekaj(3300 - wiek) : Promise.resolve()).then(function () { return z; });
    }).then(function (z) {
      dane.set('_z', z);
      return fetch(URL_F, { method: 'POST', body: dane, credentials: 'same-origin' }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (r.ok && j.success) { znacznik = null; return true; } /* znacznik jest jednorazowy */
          if (r.status === 403 && j.blad === 'szybko' && !proba) return czekaj(3200).then(function () { return wyslijSerwer(dane, 1, z); });
          if (r.status === 403 && j.blad === 'znacznik' && !proba) { znacznik = null; return wyslijSerwer(dane, 1); }
          throw new Error(j.blad || r.status);
        });
      });
    });
  }
  $$('form[data-form]').forEach(function (f) {
    var rodzaj = f.getAttribute('data-form'), temat = f.getAttribute('data-temat') || 'Zapytanie ze strony';
    var wynik = document.createElement('div'); wynik.className = 'form-wynik'; wynik.hidden = true; wynik.setAttribute('aria-live', 'polite'); f.appendChild(wynik);
    /* pulapka na boty: pole niewidoczne dla ludzi i czytnikow ekranu, wypelniaja je tylko automaty */
    var hp = document.createElement('div'); hp.className = 'hp'; hp.setAttribute('aria-hidden', 'true');
    hp.innerHTML = '<label for="hp-' + rodzaj + '">Strona firmy</label><input id="hp-' + rodzaj + '" name="_honey" type="text" tabindex="-1" autocomplete="off">';
    f.insertBefore(hp, f.firstChild);
    f.setAttribute('novalidate', '');
    f.addEventListener('input', function (e) { var p = e.target.closest('.pole'); if (p) p.classList.remove('zle'); });
    if (URL_F) f.addEventListener('focusin', function () { pobierzZnacznik().catch(function () {}); }, { once: true });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true, pierwszy = null;
      $$('input,select,textarea', f).forEach(function (el) {
        if (!el.name || el.name.charAt(0) === '_') return;
        var p = el.closest('.pole'); var v = el.value.trim(); var zle = false;
        if (el.required && !v) zle = true;
        if (v && el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) zle = true;
        if (v && el.type === 'tel' && v.replace(/\D/g, '').length < 9) zle = true;
        if (p) p.classList.toggle('zle', zle);
        if (zle) { ok = false; pierwszy = pierwszy || el; }
      });
      var dod = window.potockiDodatki[rodzaj] ? window.potockiDodatki[rodzaj]() : null;
      if (dod && dod.blad) { ok = false; dod.blad(); }
      if (!ok) { if (pierwszy) pierwszy.focus(); return; }
      var linie = dod && dod.linie ? dod.linie.slice() : [], pary = [], email = '';
      linie.forEach(function (l) { var i = l.indexOf(': '); if (i > 0) pary.push([l.slice(0, i), l.slice(i + 2)]); });
      $$('input,select,textarea', f).forEach(function (el) {
        if (!el.name || el.name.charAt(0) === '_' || !el.value.trim()) return;
        if ((el.type === 'checkbox' || el.type === 'radio') && !el.checked) return;
        var lab = f.querySelector('label[for="' + el.id + '"]'); var nazwa = lab ? lab.textContent.replace(/\s*\(.*\)\s*$/, '').replace(/\*$/, '').trim() : el.name;
        linie.push(nazwa + ': ' + el.value.trim()); pary.push([nazwa, el.value.trim()]);
        if (el.type === 'email') email = el.value.trim();
      });
      var tresc = linie.join('\n');
      var adres = adresDla(rodzaj);
      if (URL_F) {
        var przycisk = $('button[type=submit]', f), napis = przycisk ? przycisk.textContent : '';
        if (f.getAttribute('aria-busy') === 'true') return;
        f.setAttribute('aria-busy', 'true'); if (przycisk) { przycisk.disabled = true; przycisk.textContent = 'Wysyłanie...'; }
        var dane = new FormData();
        dane.append('_honey', ($('[name=_honey]', f) || {}).value || '');
        dane.append('_rodzaj', rodzaj); dane.append('_subject', temat); dane.append('_pola', JSON.stringify(pary)); dane.append('email', email);
        wyslijSerwer(dane, 0).then(function () {
          wynik.innerHTML = '<h4>Dziękujemy, zapytanie zostało wysłane</h4><p>Odpowiemy najszybciej, jak to możliwe. W pilnej sprawie prosimy o telefon: <a href="tel:' + esc(CFG.telefon || '') + '">' + esc(CFG.telefonTekst || '') + '</a>.</p>';
          wynik.hidden = false; f.classList.add('wyslany');
          $$('input,textarea', f).forEach(function (el) { if (el.name && el.name.charAt(0) !== '_' && el.type !== 'number' && el.type !== 'date') el.value = ''; });
          window.potockiTrack('generate_lead', { formularz: rodzaj });
        }).catch(function (err) {
          var mailto2 = 'mailto:' + adres + '?subject=' + encodeURIComponent(temat) + '&body=' + encodeURIComponent(tresc);
          var limit = /limit|globalny|429/.test(String(err && err.message));
          wynik.innerHTML = '<h4>Nie udało się wysłać zapytania</h4><p>' + (limit ? 'Z tej sieci wysłano już dużo zapytań. ' : 'Wystąpił chwilowy problem z połączeniem. ') +
            'Prosimy wysłać je e-mailem albo zadzwonić: <a href="tel:' + esc(CFG.telefon || '') + '">' + esc(CFG.telefonTekst || '') + '</a>.</p><pre>' + esc(tresc) + '</pre>' +
            '<div class="akcje"><a class="btn btn-glowny" href="' + esc(mailto2) + '">Wyślij e-mailem</a></div>';
          wynik.hidden = false;
        }).then(function () {
          f.removeAttribute('aria-busy'); if (przycisk) { przycisk.disabled = false; przycisk.textContent = napis; }
          wynik.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
        return;
      }
      var mailto = 'mailto:' + adres + '?subject=' + encodeURIComponent(temat) + '&body=' + encodeURIComponent(tresc + '\n\n(wysłano ze strony potockidwor.pl)');
      wynik.innerHTML = '<h4>Zapytanie gotowe</h4><p>Wersja robocza strony: po uruchomieniu formularz wyśle je automatycznie na ' + esc(adres) + '. Teraz można je wysłać z programu pocztowego.</p><pre>' + esc(tresc) + '</pre>' +
        '<div class="akcje"><a class="btn btn-glowny" href="' + esc(mailto) + '">Wyślij e-mailem</a><button type="button" class="btn btn-obrys" data-kopiuj>Skopiuj treść</button></div>';
      wynik.hidden = false;
      var kop = $('[data-kopiuj]', wynik);
      kop.addEventListener('click', function () { if (navigator.clipboard) navigator.clipboard.writeText(tresc).then(function () { kop.textContent = 'Skopiowano'; }).catch(function () {}); });
      window.potockiTrack('generate_lead', { formularz: rodzaj });
      wynik.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  });

  /* ---------- planer przyjecia ---------- */
  (function () {
    var root = $('#planer'); if (!root) return;
    var wyn = $('#planer-wynik'), kal = $('#kal'), rg = $('#goscie'), num = $('#goscie-n');
    var SALE = {
      bankietowa: { nazwa: 'Sala Bankietowa', ile: 'do 30 osób', foto: 'bankietowa-1' },
      balowa: { nazwa: 'Sala Balowa', ile: 'do 200 osób', foto: 'balowa-1' }
    };
    /* sale udostepniane po indywidualnych ustaleniach (klient 22.10) */
    var INNE = [{ id: 'patio', nazwa: 'Patio', max: 35 }, { id: 'restauracyjna', nazwa: 'Sala Restauracyjna', max: 50 }];
    var st = { okazja: 'Wesele', goscie: 80, data: null };
    var zajete = null; /* null = kalendarz niepodpiety */
    var dzis = new Date(); dzis.setHours(0, 0, 0, 0);
    var mies = new Date(dzis.getFullYear(), dzis.getMonth(), 1);
    var MN = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień'];
    var MD = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia'];
    var DT = ['niedziela', 'poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota'];
    var fmt = function (d) { return DT[d.getDay()] + ', ' + d.getDate() + ' ' + MD[d.getMonth()] + ' ' + d.getFullYear(); };
    var klucz = function (d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
    var sala = function () { return st.goscie <= 30 ? 'bankietowa' : 'balowa'; };
    var czyZajety = function (d) { if (!zajete || !d) return false; var z = zajete[klucz(d)]; return !!z && (z.indexOf('*') > -1 || z.indexOf(sala()) > -1); };

    function rysujKal() {
      var r = mies.getFullYear(), m = mies.getMonth(), dni = new Date(r, m + 1, 0).getDate(), start = (new Date(r, m, 1).getDay() + 6) % 7;
      var pierwszy = mies.getFullYear() === dzis.getFullYear() && mies.getMonth() === dzis.getMonth();
      var h = '<div class="kal-g"><button type="button" data-k="-1" aria-label="Poprzedni miesiąc"' + (pierwszy ? ' disabled' : '') + '>‹</button><b>' + MN[m] + ' ' + r + '</b><button type="button" data-k="1" aria-label="Następny miesiąc">›</button></div><div class="kal-s">' +
        ['pn', 'wt', 'śr', 'cz', 'pt', 'sb', 'nd'].map(function (x) { return '<span class="dn">' + x + '</span>'; }).join('');
      for (var i = 0; i < start; i++) h += '<span></span>';
      for (var n = 1; n <= dni; n++) {
        var d = new Date(r, m, n), prze = d < dzis, z = !prze && czyZajety(d), w = st.data && +st.data === +d;
        h += '<button type="button" data-d="' + n + '" class="' + (z ? 'zaj ' : '') + (d.getDay() === 6 ? 'sob ' : '') + (w ? 'wyb' : '') + '"' + (prze ? ' disabled' : '') + (z ? ' aria-disabled="true" title="termin zajęty"' : '') + ' aria-label="' + fmt(d) + (z ? ', termin zajęty' : '') + '">' + n + '</button>';
      }
      h += '</div><div class="kal-leg"><span><i class="l-wyb"></i>wybrany dzień</span>' + (zajete ? '<span><i class="l-zaj"></i>zajęty (przekreślony)</span>' : '') + '</div>';
      kal.innerHTML = h;
    }
    kal.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || b.disabled) return;
      if (b.dataset.k) { mies = new Date(mies.getFullYear(), mies.getMonth() + +b.dataset.k, 1); rysujKal(); return; }
      var d = new Date(mies.getFullYear(), mies.getMonth(), +b.dataset.d); if (czyZajety(d)) return;
      st.data = d; root.querySelector('.pole-data').classList.remove('zle'); rysujKal(); rysuj();
    });
    function rysuj() {
      var s = SALE[sala()], stan;
      if (!st.data) stan = '<p class="stan">Wybierz datę w kalendarzu.</p>';
      else if (zajete) stan = czyZajety(st.data) ? '<p class="stan zaj">' + fmt(st.data) + ': termin zajęty, wybierz inny dzień.</p>' : '<p class="stan wolny">' + fmt(st.data) + ': termin wolny, potwierdzimy go w odpowiedzi na zapytanie.</p>';
      else stan = '<p class="stan">' + fmt(st.data) + ': dostępność sali potwierdzimy w odpowiedzi na zapytanie.</p>';
      var foto = '<img class="sala-mini" src="' + ROOT + 'assets/img/' + s.foto + '-800.webp" alt="' + s.nazwa + '" width="800" height="450">';
      var inne = INNE.filter(function (x) { return st.goscie <= x.max; }).map(function (x) { return x.nazwa + ' (do ' + x.max + ' osób)'; });
      var inneH = inne.length ? '<p class="inne-sale">Do indywidualnego ustalenia: ' + inne.join(', ') + '.</p>' : '';
      wyn.innerHTML = '<h3>' + s.nazwa + '</h3><p class="sala-ile">' + s.ile + '</p>' + stan + foto +
        inneH + '<ul class="podsum"><li><span>Okazja</span>' + esc(st.okazja) + '</li><li><span>Liczba gości</span>' + st.goscie + '</li><li><span>Noclegi</span>23 pokoje na miejscu</li></ul>' +
        '<a class="btn btn-bialy" href="#planer-form" data-do-formularza>Przejdź do zapytania</a>';
    }
    wyn.addEventListener('click', function (e) { if (e.target.closest('[data-do-formularza]')) { e.preventDefault(); var f = $('#planer-form'); f.scrollIntoView({ behavior: 'smooth', block: 'start' }); setTimeout(function () { var i = $('input', f); if (i) i.focus({ preventScroll: true }); }, 450); } });
    $$('.chipy', root).forEach(function (g) {
      g.addEventListener('click', function (e) { var b = e.target.closest('button'); if (!b) return; $$('button', g).forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); st.okazja = b.dataset.v; rysuj(); });
    });
    var ustawGosci = function (v) { v = Math.max(10, Math.min(200, Math.round(+v || 10))); st.goscie = v; rg.value = v; num.value = v; rysujKal(); rysuj(); };
    rg.addEventListener('input', function () { ustawGosci(rg.value); });
    num.addEventListener('change', function () { ustawGosci(num.value); });
    window.potockiDodatki.przyjecia = function () {
      if (!st.data) return { blad: function () { root.querySelector('.pole-data').classList.add('zle'); } };
      if (czyZajety(st.data)) return { blad: function () { root.querySelector('.pole-data').classList.add('zle'); } };
      return { linie: ['Okazja: ' + st.okazja, 'Liczba gości: ' + st.goscie, 'Data: ' + fmt(st.data), 'Proponowana sala: ' + SALE[sala()].nazwa, ''] };
    };
    /* zajetosc z Kalendarza Google (przez serwer) - wlaczane w config.js */
    /* Ochrona endpointu (Apps Script ma dzienne limity): jedno zapytanie na wizyte (cala zajetosc na 12 miesiecy naraz),
       wynik w sessionStorage na 10 min (przejscia miedzy podstronami bez zapytan), pobranie dopiero gdy planer jest blisko ekranu,
       nigdy dwa zapytania naraz, limit czasu 10 s. Po bledzie: ponowienie tylko przy zmianie daty, z opoznieniem 600 ms, max 2 razy. */
    var KAL_PAMIEC = 'potocki_zajetosc_v1', kalStan = 'brak', kalProby = 0, kalTimer = null;
    function wczytajZajetosc() {
      var k = CFG.kalendarz || {}; if (!k.url || kalStan === 'laduje' || kalStan === 'ok') return;
      try {
        var c = JSON.parse(sessionStorage.getItem(KAL_PAMIEC) || 'null');
        if (c && c.u === k.url && Date.now() - c.t < 6e5 && c.z) { zajete = c.z; kalStan = 'ok'; rysujKal(); rysuj(); return; }
      } catch (e) {}
      kalStan = 'laduje'; kalProby++;
      var ac = window.AbortController ? new AbortController() : null, tm = setTimeout(function () { if (ac) ac.abort(); }, 10000);
      var kk = ''; try { kk = sessionStorage.getItem('potocki_k') || Math.random().toString(36).slice(2, 12); sessionStorage.setItem('potocki_k', kk); } catch (e) {}
      var adres = k.url + (kk ? (k.url.indexOf('?') > -1 ? '&' : '?') + 'k=' + kk : '');   /* klucz do limitu w Apps Script (_src/APPS_SCRIPT_LIMIT.md) */
      fetch(adres, ac ? { signal: ac.signal, credentials: 'omit' } : { credentials: 'omit' }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }).then(function (t) {
        zajete = k.format === 'ical' ? zIcal(t) : (JSON.parse(t).zajete || {});
        kalStan = 'ok';
        try { sessionStorage.setItem(KAL_PAMIEC, JSON.stringify({ u: k.url, t: Date.now(), z: zajete })); } catch (e) {}
        rysujKal(); rysuj();
      }).catch(function () { zajete = null; kalStan = 'blad'; }).then(function () { clearTimeout(tm); });
    }
    function ponowZajetosc() { /* wolane przy zmianie daty; debounce = jedno zapytanie na serie klikniec */
      if (kalStan !== 'blad' || kalProby > 2) return;
      clearTimeout(kalTimer); kalTimer = setTimeout(wczytajZajetosc, 600);
    }
    kal.addEventListener('click', function (e) { if (e.target.closest('button[data-d]')) ponowZajetosc(); });
    function startZajetosc() {
      if (!('IntersectionObserver' in window)) { wczytajZajetosc(); return; }
      var io = new IntersectionObserver(function (w) { if (w.some(function (x) { return x.isIntersecting; })) { io.disconnect(); wczytajZajetosc(); } }, { rootMargin: '600px 0px' });
      io.observe(root);
    }
    function zIcal(t) {
      /* DTSTART/DTEND z VEVENT; nazwa sali tylko jesli SUMMARY ja zawiera, inaczej caly dzien zajety */
      var wyn = {}, ev = t.replace(/\r?\n[ \t]/g, '').split('BEGIN:VEVENT').slice(1);
      ev.forEach(function (e) {
        var ds = (e.match(/DTSTART[^:]*:(\d{8})/) || [])[1], de = (e.match(/DTEND[^:]*:(\d{8})/) || [])[1], sum = ((e.match(/SUMMARY[^:]*:(.*)/) || [])[1] || '').toLowerCase();
        if (!ds) return;
        var salaE = /balow/.test(sum) ? 'balowa' : /bankiet/.test(sum) ? 'bankietowa' : /patio/.test(sum) ? 'patio' : /restaur/.test(sum) ? 'restauracyjna' : '*';
        var d = new Date(+ds.slice(0, 4), +ds.slice(4, 6) - 1, +ds.slice(6, 8)), koniec = de ? new Date(+de.slice(0, 4), +de.slice(4, 6) - 1, +de.slice(6, 8)) : new Date(d.getTime() + 864e5);
        if (/VALUE=DATE/.test(e) === false && de === ds) koniec = new Date(d.getTime() + 864e5);
        for (; d < koniec; d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1)) { var kk = klucz(d); (wyn[kk] = wyn[kk] || []).push(salaE); }
      });
      return wyn;
    }
    rysujKal(); rysuj(); startZajetosc();
  })();

  /* ---------- mapa dojazdu (OpenStreetMap) ---------- */
  (function () {
    var box = $('#mapa'); if (!box || !window.L) return;
    var ll = [50.6085, 20.2364];
    var mapa = L.map(box, { scrollWheelZoom: false }).setView(ll, 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(mapa);
    L.marker(ll, { icon: L.divIcon({ className: '', html: '<div class="pin"></div>', iconSize: [22, 22], iconAnchor: [11, 22] }), alt: 'Potocki Dwór', title: 'Potocki Dwór, Potok Wielki 83A' }).addTo(mapa)
      .bindTooltip('Potocki Dwór', { direction: 'top', offset: [0, -20], permanent: true });
  })();

  /* ---------- hotel: pasek przyjazd / wyjazd / osoby -> formularz zapytania (docelowo widget KW Hotel) ---------- */
  (function () {
    var f = $('#szybka-rez'); if (!f) return;
    var od = $('#sr-od'), dd = $('#sr-do');
    var iso = function (d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
    var dzis = new Date(); od.min = iso(dzis); dd.min = iso(new Date(dzis.getTime() + 864e5));
    od.addEventListener('change', function () { if (od.value) { var n = new Date(od.value); n.setDate(n.getDate() + 1); dd.min = iso(n); if (!dd.value || dd.value <= od.value) dd.value = iso(n); } });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (od.value) $('#h-od').value = od.value;
      if (dd.value) $('#h-do').value = dd.value;
      if ($('#sr-osoby').value) $('#h-osoby').value = $('#sr-osoby').value;
      var r = $('#rezerwacja'); r.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(function () { var i = $('#h-imie'); if (i) i.focus({ preventScroll: true }); }, 500);
    });
  })();

  /* ---------- modul rezerwacji KW Hotel PRO ---------- */
  (function () {
    var box = $('#kw-modul'); if (!box) return;
    var kw = CFG.kwHotel || {};
    if (kw.kod) {
      box.innerHTML = kw.kod;
      $$('script', box).forEach(function (s) { var n = document.createElement('script'); Array.prototype.forEach.call(s.attributes, function (a) { n.setAttribute(a.name, a.value); }); n.text = s.text; s.replaceWith(n); });
    } else if (kw.link) {
      box.innerHTML = '<a class="btn btn-glowny" href="' + esc(kw.link) + '" target="_blank" rel="noopener" data-ev="begin_reservation">Rezerwacja online</a>';
    }
  })();

})();
