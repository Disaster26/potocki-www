# Buduje strone ze wspolnego szablonu (naglowek, stopka) i tresci podstron z _src/.
# Uzycie:
#   python -I _narzedzia/build.py                 -> podglad w katalogu repo (GitHub Pages, noindex, formularze przez program pocztowy)
#   python -I _narzedzia/build.py --prod <katalog> -> wersja produkcyjna (canonical, bez noindex, sitemap, robots, llms.txt,
#                                                     404, manifest, formularze przez wyslij.php); paczki: _narzedzia/wdrozenie/paczka.py
import os, sys, json, re, shutil, subprocess, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, '_src')
V = '10'
FONTY = 'https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&family=Libre+Franklin:wght@400;500;600&display=swap'  # wersja plikow css/js (cache)

# DOCELOWA DOMENA - jedyne miejsce (canonical, og:url, JSON-LD, sitemap, robots, llms.txt). Bez www, z https i ukosnikiem.
DOMENA = 'https://potockidwor.pl/'
PODGLAD = 'https://disaster26.github.io/potocki-www/'
PROD = '--prod' in sys.argv
OUT = os.path.abspath(sys.argv[sys.argv.index('--prod') + 1]) if PROD else ROOT
BAZA = DOMENA if PROD else PODGLAD   # adresy bezwzgledne (og:image)

STRONY = [
  # plik zrodlowy, sciezka wyjsciowa, klucz menu
  ('start.html', 'index.html', 'start'),
  ('restauracja.html', 'restauracja/index.html', 'restauracja'),
  ('hotel.html', 'hotel/index.html', 'hotel'),
  ('przyjecia.html', 'przyjecia/index.html', 'przyjecia'),
  ('catering.html', 'catering/index.html', 'catering'),
  ('biznes.html', 'dla-biznesu/index.html', 'biznes'),
  ('kontakt.html', 'kontakt/index.html', 'kontakt'),
]
MENU = [('restauracja', 'restauracja/', 'Restauracja'), ('hotel', 'hotel/', 'Hotel'), ('przyjecia', 'przyjecia/', 'Przyjęcia'), ('catering', 'catering/', 'Catering'),
        ('biznes', 'dla-biznesu/', 'Dla biznesu'), ('kontakt', 'kontakt/', 'Kontakt')]
TEL, TEL_T, MAIL = '+48798033101', '798 033 101', 'recepcja@potockidwor.pl'  # z obecnej strony potockidwor.pl

IKONA_TEL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'

def wczytaj(plik):
    t = open(os.path.join(SRC, plik), encoding='utf-8').read()
    m = re.match(r'<!--META\s*(\{.*?\})\s*-->\s*', t, re.S)
    meta = json.loads(m.group(1)); return meta, t[m.end():]

def szablon(meta, tresc, klucz, R):
    menu = ''.join(f'<a href="{R}{h}"{" aria-current=\"page\"" if k == klucz else ""}>{n}</a>' for k, h, n in MENU)
    panel = ''.join(f'<a class="poz" href="{R}{h}"{" aria-current=\"page\"" if k == klucz else ""}>{n}</a>' for k, h, n in MENU)
    cta = meta.get('cta_naglowek')
    cta_h = f'<a class="btn btn-glowny btn-maly gora-cta" href="{R}{cta[1]}">{cta[0]}</a>' if cta else ''
    mob = meta.get('cta_mob')
    mob_h = f'<div class="mob" aria-hidden="true"><a class="btn btn-obrys" href="tel:{meta.get('tel_mob', TEL)}" data-ev="click_tel" tabindex="-1">Zadzwoń</a><a class="btn btn-glowny" href="{R}{mob[1]}" tabindex="-1">{mob[0]}</a></div>' if mob else ''
    preload = ''
    if meta.get('hero'):
        h = meta['hero']
        preload = f'<link rel="preload" as="image" href="{R}assets/img/{h}-1600.webp" imagesrcset="{R}assets/img/{h}-800.webp 800w, {R}assets/img/{h}-1600.webp 1600w" imagesizes="(max-width:760px) 100vw, 60vw">'
    elif meta.get('hero_c'):   # zdjecia cateringu: warianty 600/1400
        h = meta['hero_c']
        preload = f'<link rel="preload" as="image" href="{R}assets/img/{h}-1400.webp" imagesrcset="{R}assets/img/{h}-600.webp 600w, {R}assets/img/{h}-1400.webp 1400w" imagesizes="(max-width:760px) 100vw, 60vw">'
    ld_h = jsonld(meta, klucz)
    skrypty = ''.join(f'<script defer src="{R}{s}?v={V}"></script>' for s in meta.get('skrypty', []))
    leaflet_css = '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">' if meta.get('mapa') else ''
    leaflet_js = '<script defer src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>' if meta.get('mapa') else ''
    if PROD and not meta.get('noindex'):
        roboty = (f'<meta name="robots" content="index, follow, max-image-preview:large">\n<link rel="canonical" href="{DOMENA}{meta["sciezka"]}">\n'
                  '<meta name="generator" content="potocki-static">')
    elif PROD:
        roboty = '<meta name="robots" content="noindex, follow">\n<meta name="generator" content="potocki-static">'
    else:
        roboty = (f'<!-- PODGLĄD (GitHub Pages): noindex. Wersja produkcyjna: build.py --prod (canonical {DOMENA}{meta["sciezka"]}) -->\n'
                  '<meta name="robots" content="noindex, nofollow">')
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
{roboty}
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Potocki Dwór">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{BAZA}{meta["sciezka"]}">
<meta property="og:image" content="{BAZA}assets/img/og/og-{meta.get("og", "fasada")}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{meta.get("og_alt", "Potocki Dwór - hotel i restauracja w Potoku Wielkim pod Jędrzejowem")}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{R}favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" href="{R}assets/img/favicon.png">
<link rel="apple-touch-icon" href="{R}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{R}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{FONTY}" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="{FONTY}"></noscript>
{leaflet_css}
<link rel="stylesheet" href="{R}assets/css/style.css?v={V}">
{preload}
{ld_h}
<script defer src="{R}assets/js/config.js?v={V}"></script>
<!-- POMIAR: GA4 + Meta Pixel ładowane przez assets/js/app.js (zgody, Consent Mode v2) dopiero po wpisaniu identyfikatorów w config.js -->
</head>
<body data-strona="{klucz}" data-root="{R}">
<a class="pomin" href="#tresc">Przejdź do treści</a>
<header class="gora">
  <div class="wrap gora-in">
    <a class="logo" href="{R}" aria-label="Potocki Dwór - strona główna"><img src="{R}assets/img/logo-granat.png" width="720" height="237" alt="Potocki Hotel - Restauracja"></a>
    <nav class="menu" aria-label="Menu główne">{menu}</nav>
    <div class="gora-akcje">
      <a class="tel" href="tel:{TEL}" data-ev="click_tel" aria-label="Zadzwoń: {TEL_T}">{IKONA_TEL}<span>{TEL_T}</span></a>
      {cta_h}
      <button class="ham" type="button" aria-label="Menu" aria-expanded="false" aria-controls="panel"><span></span></button>
    </div>
  </div>
</header>
<div class="panel" id="panel">
  <a class="poz" href="{R}">Strona główna</a>{panel}
  <a class="panel-tel" href="tel:{TEL}" data-ev="click_tel">{IKONA_TEL}{TEL_T}</a>
</div>
<main id="tresc">
{tresc.replace("{{R}}", R).replace("{{TEL}}", TEL).replace("{{TEL_T}}", TEL_T).replace("{{MAIL}}", MAIL)}
</main>
<footer class="stopka">
  <div class="wrap stopka-in">
    <div class="stopka-marka">
      <img class="stopka-logo" src="{R}assets/img/logo-biale.png" width="720" height="238" alt="Potocki Hotel - Restauracja" loading="lazy">
      <p>Potok Wielki 83A<br>28-300 Jędrzejów</p>
      <p class="stopka-godz">Restauracja i hotel: codziennie <span class="nw">12:00-22:00</span>, w niedzielę <span class="nw">12:00-21:00</span></p>
    </div>
    <div class="stopka-kontakty">
      <div><h2>Recepcja</h2><p><a href="tel:{TEL}" data-ev="click_tel">{TEL_T}</a></p><p><a href="mailto:{MAIL}">{MAIL}</a></p></div>
      <div><h2>Przyjęcia i catering</h2><p>Manager</p><p><a href="tel:+48784043570" data-ev="click_tel">784 043 570</a></p><p><a href="mailto:k.wieczorek@potockidwor.pl">k.wieczorek@potockidwor.pl</a></p></div>
      <div><h2>Biznes</h2><p>M. Pronobis</p><p><a href="tel:+48532162301" data-ev="click_tel">532 162 301</a></p><p><a href="mailto:m.pronobis@potockidwor.pl">m.pronobis@potockidwor.pl</a></p></div>
    </div>
    <nav class="stopka-menu" aria-label="Menu w stopce"><a href="{R}">Strona główna</a>{"".join(f'<a href="{R}{h}">{n}</a>' for k, h, n in MENU)}</nav>
  </div>
  <div class="wrap stopka-dol">
    <p>© Potocki Dwór · ECOTUR Sp. z o.o.</p>
    {ZNAK}
    <p class="social"><a href="https://www.facebook.com/PotockiDwor" target="_blank" rel="noopener">Facebook</a><a href="https://www.instagram.com/potocki_dwor/" target="_blank" rel="noopener">Instagram</a><button type="button" class="link-cookies" data-cookies-ustawienia hidden>Ustawienia plików cookies</button></p>
  </div>
</footer>
{mob_h}
<dialog class="lightbox" id="lightbox" aria-label="Powiększone zdjęcie"><button type="button" class="lb-zamknij" aria-label="Zamknij">×</button><button type="button" class="lb-nav lb-pop" aria-label="Poprzednie zdjęcie">‹</button><img alt=""><button type="button" class="lb-nav lb-nast" aria-label="Następne zdjęcie">›</button><p class="lb-opis"></p></dialog>
{leaflet_js}
{skrypty}
<script defer src="{R}assets/js/app.js?v={V}"></script>
</body>
</html>
'''

# znak "wykonanie: Wylinka" (Downloads\Wylinka\strona\public\znak\badge.html, utm_source = domena klienta); style w style.css
ZNAK = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'znak-wylinka.html'), encoding='utf-8').read().strip()

SAME_AS = ["https://www.facebook.com/PotockiDwor", "https://www.instagram.com/potocki_dwor/"]
ADRES = {"@type": "PostalAddress", "streetAddress": "Potok Wielki 83A", "postalCode": "28-300", "addressLocality": "Jędrzejów", "addressRegion": "świętokrzyskie", "addressCountry": "PL"}
GEO = {"@type": "GeoCoordinates", "latitude": 50.6085192, "longitude": 20.2364365}   # OSM: budynek "Potocki Dwór", Potok Wielki 83a
WWW = DOMENA
GODZ = [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "12:00", "closes": "22:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "12:00", "closes": "21:00"}]
NAZWY = {'start': 'Strona główna', 'restauracja': 'Restauracja', 'hotel': 'Hotel', 'przyjecia': 'Przyjęcia', 'catering': 'Catering', 'biznes': 'Dla biznesu', 'kontakt': 'Kontakt'}


def menu_ld():
    """Karta menu (assets/js/menu-data.js) jako schema.org Menu - te same dane co na stronie."""
    js = ("global.window={};require(" + json.dumps(os.path.join(ROOT, 'assets', 'js', 'menu-data.js')) + ");"
          "process.stdout.write(JSON.stringify(window.POTOCKI_MENU))")
    dane = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, encoding='utf-8', check=True).stdout)
    sekcje = []
    for k in dane:
        poz = []
        for x in k['pozycje']:
            if x.get('grupa') or not x.get('n'):
                continue
            it = {"@type": "MenuItem", "name": x['n']}
            if x.get('s'):
                it['description'] = x['s']
            cena = re.match(r'^\s*(\d+(?:[.,]\d+)?)\s*zł\s*$', x.get('c', ''))
            if cena:
                it['offers'] = {"@type": "Offer", "price": cena.group(1).replace(',', '.'), "priceCurrency": "PLN"}
            if x.get('img'):
                it['image'] = WWW + 'assets/img/' + x['img'] + '-1200.webp'
            poz.append(it)
        if poz:
            sekcje.append({"@type": "MenuSection", "name": k['nazwa'], "hasMenuItem": poz})
    return {"@type": "Menu", "@id": WWW + "restauracja/#menu", "name": "Karta menu restauracji Potocki Dwór", "url": WWW + "restauracja/#menu",
            "inLanguage": "pl", "hasMenuSection": sekcje}


def wezly():
    firma = {"@type": "LocalBusiness", "@id": WWW + "#firma", "name": "Potocki Dwór", "alternateName": "Hotel i Restauracja Potocki Dwór",
             "legalName": "ECOTUR Sp. z o.o.", "url": WWW, "logo": WWW + "assets/img/logo-granat.png", "image": WWW + "assets/img/og/og-fasada.jpg",
             "description": "Hotel, restauracja i sale na przyjęcia oraz konferencje w Potoku Wielkim pod Jędrzejowem.",
             "telephone": TEL, "email": MAIL, "address": ADRES, "geo": GEO, "hasMap": "https://www.openstreetmap.org/way/522990394",
             "areaServed": ["Jędrzejów", "powiat jędrzejowski", "województwo świętokrzyskie"], "openingHoursSpecification": GODZ, "sameAs": SAME_AS,
             "vatID": "PL6562331030", "taxID": "6562331030",
             "contactPoint": [
                 {"@type": "ContactPoint", "contactType": "recepcja i rezerwacje", "telephone": TEL, "email": MAIL, "availableLanguage": "pl"},
                 {"@type": "ContactPoint", "contactType": "przyjęcia i wesela", "telephone": "+48784043570", "email": "k.wieczorek@potockidwor.pl", "availableLanguage": "pl"},
                 {"@type": "ContactPoint", "contactType": "oferta dla firm", "telephone": "+48532162301", "email": "m.pronobis@potockidwor.pl", "availableLanguage": "pl"}],
             "department": [{"@id": WWW + "#hotel"}, {"@id": WWW + "#restauracja"}, {"@id": WWW + "#sale"}]}
    hotel = {"@type": "Hotel", "@id": WWW + "#hotel", "name": "Hotel Potocki Dwór", "url": WWW + "hotel/", "telephone": TEL, "email": MAIL,
             "address": ADRES, "geo": GEO, "image": [WWW + "assets/img/og/og-pokoj-dbl.jpg", WWW + "assets/img/og/og-fasada.jpg"], "sameAs": SAME_AS,
             "description": "23 pokoje 1- i 2-osobowe z łazienką, biurkiem, Wi-Fi i TV, śniadanie w cenie noclegu.",
             "numberOfRooms": 23, "parentOrganization": {"@id": WWW + "#firma"},
             "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                                for n in ("Śniadanie w cenie noclegu", "Wi-Fi", "Telewizor", "Łazienka w pokoju", "Restauracja na miejscu", "Sale konferencyjne")]}
    resto = {"@type": "Restaurant", "@id": WWW + "#restauracja", "name": "Restauracja Potocki Dwór", "url": WWW + "restauracja/", "telephone": TEL, "email": MAIL,
             "address": ADRES, "geo": GEO, "image": WWW + "assets/img/og/og-resto-sala.jpg", "sameAs": SAME_AS, "servesCuisine": ["polska", "włoska"],
             "hasMenu": {"@id": WWW + "restauracja/#menu"}, "acceptsReservations": True, "openingHoursSpecification": GODZ, "parentOrganization": {"@id": WWW + "#firma"}}
    sale = {"@type": "EventVenue", "@id": WWW + "#sale", "name": "Sale Potocki Dwór: wesela, przyjęcia, konferencje", "url": WWW + "przyjecia/",
            "telephone": "+48784043570", "address": ADRES, "geo": GEO, "image": WWW + "assets/img/og/og-balowa-1.jpg", "maximumAttendeeCapacity": 200,
            "description": "Sala Balowa do 200 osób, Sala Bankietowa do 30 osób, Sala Restauracyjna do 50 i Patio do 35 osób po indywidualnych ustaleniach.",
            "containsPlace": [{"@type": "Place", "name": n, "maximumAttendeeCapacity": m}
                              for n, m in (("Sala Balowa", 200), ("Sala Bankietowa", 30), ("Sala Restauracyjna", 50), ("Patio", 35))],
            "parentOrganization": {"@id": WWW + "#firma"}}
    strona = {"@type": "WebSite", "@id": WWW + "#www", "url": WWW, "name": "Potocki Dwór", "inLanguage": "pl", "publisher": {"@id": WWW + "#firma"}}
    def oferta(n, cena, opis):
        return {"@type": "Offer", "price": cena, "priceCurrency": "PLN", "itemOffered": {"@type": "Product", "name": n, "description": opis}}
    catering = {"@type": "Service", "@id": WWW + "#catering", "name": "Catering Potocki Dwór", "serviceType": "Catering okolicznościowy",
                "url": WWW + "catering/", "image": WWW + "assets/img/og/og-catering.jpg", "provider": {"@id": WWW + "#firma"},
                "areaServed": ["Jędrzejów", "powiat jędrzejowski", "województwo świętokrzyskie"],
                "description": "Koryta mięsne, zestawy cateringowe i boxy okolicznościowe z transportem; na życzenie obsługa kelnerska, zastawa stołowa i szkło.",
                "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Standardowa oferta cateringu", "itemListElement": [
                    {"@type": "OfferCatalog", "name": "Koryta mięsne", "itemListElement": [
                        oferta("Koryto mięs I", "695", "ok. 10-12 osób, ok. 12 kg"), oferta("Koryto mięs II", "1150", "12-18 osób, ok. 19 kg"),
                        oferta("Koryto mięs III", "1995", "20-30 osób, ok. 33 kg")]},
                    {"@type": "OfferCatalog", "name": "Boxy okolicznościowe", "itemListElement": [
                        oferta("Box okolicznościowy na zimno", "260", "6-8 osób"), oferta("Box okolicznościowy na ciepło", "490", "6-8 osób"),
                        oferta("Box serów", "280", "6-8 osób"), oferta("Box wędlin dojrzewających", "280", "6-8 osób")]}]}}
    firma['department'].append({"@id": WWW + "#catering"})
    firma['makesOffer'] = {"@type": "Offer", "itemOffered": {"@id": WWW + "#catering"}}
    return {'firma': firma, 'hotel': hotel, 'restauracja': resto, 'sale': sale, 'www': strona, 'catering': catering}


# ktore wezly na ktorej stronie (pelne opisy tam, gdzie jest tresc)
LD_STRONY = {'start': ['www', 'firma', 'hotel', 'restauracja', 'sale'], 'restauracja': ['restauracja', 'menu'], 'hotel': ['hotel'],
             'przyjecia': ['sale'], 'catering': ['catering'], 'biznes': ['sale'], 'kontakt': ['firma']}
_MENU = []


def jsonld(meta, klucz):
    if klucz not in LD_STRONY:
        return ''
    W = wezly()
    graf = []
    for x in LD_STRONY[klucz]:
        if x == 'menu':
            if not _MENU:
                _MENU.append(menu_ld())
            graf.append(_MENU[0])
        else:
            graf.append(W[x])
    if klucz != 'start':
        graf.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Potocki Dwór", "item": WWW},
            {"@type": "ListItem", "position": 2, "name": NAZWY[klucz], "item": WWW + meta['sciezka']}]})
    graf.append({"@type": "WebPage", "@id": WWW + meta['sciezka'] + "#strona", "url": WWW + meta['sciezka'], "name": meta['title'],
                 "description": meta['description'], "inLanguage": "pl", "isPartOf": {"@id": WWW + "#www"},
                 "primaryImageOfPage": WWW + 'assets/img/og/og-' + meta.get('og', 'fasada') + '.jpg'})
    dane = {"@context": "https://schema.org", "@graph": graf}
    return '<script type="application/ld+json">' + json.dumps(dane, ensure_ascii=False, separators=(",", ":")).replace('</', '<\\/') + '</script>'


# ---------------------------------------------------------------- obrazy OG 1200x630, favicon.ico, ikony manifestu
def obrazy():
    from PIL import Image
    img = os.path.join(ROOT, 'assets', 'img')
    og = os.path.join(img, 'og')
    os.makedirs(og, exist_ok=True)
    kadry = {'fasada': .12, 'resto-sala': .5, 'pokoj-dbl': .55, 'balowa-1': .55, 'balowa-2': .55, 'catering': .5}
    for nazwa, pion in kadry.items():
        cel = os.path.join(og, f'og-{nazwa}.jpg')
        zr = os.path.join(img, f'{nazwa}-2000.webp')
        if nazwa == 'catering':
            zr = os.path.join(img, 'c-box-sery-1400.webp')
        elif not os.path.exists(zr):
            zr = os.path.join(img, f'{nazwa}-1600.webp')
        if os.path.exists(cel) and os.path.getmtime(cel) > os.path.getmtime(zr):
            continue
        im = Image.open(zr).convert('RGB')
        w, h = im.size
        nh = round(w * 630 / 1200)
        top = max(0, min(h - nh, round((h - nh) * pion)))
        im.crop((0, top, w, top + nh)).resize((1200, 630), Image.LANCZOS).save(cel, 'JPEG', quality=82, optimize=True, progressive=True)  # bez EXIF
    ikona = Image.open(os.path.join(img, 'favicon.png')).convert('RGBA')
    ico = os.path.join(ROOT, 'favicon.ico')
    if not os.path.exists(ico):
        ikona.save(ico, sizes=[(16, 16), (32, 32), (48, 48)])
    for n in (192, 512):
        c = os.path.join(img, f'ikona-{n}.png')
        if not os.path.exists(c):
            t = Image.new('RGBA', (n, n), (255, 255, 255, 255))
            m = ikona.resize((round(n * .8),) * 2, Image.LANCZOS)
            t.paste(m, ((n - m.width) // 2, (n - m.height) // 2), m)
            t.save(c, optimize=True)


def zapisz(rel, txt):
    sc = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(sc), exist_ok=True)
    open(sc, 'w', encoding='utf-8', newline='\n').write(txt)


obrazy()
if PROD:
    # czysta kopia: strony + assets + favicon (bez _src, _narzedzia, .git)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    shutil.copy2(os.path.join(ROOT, 'favicon.ico'), os.path.join(OUT, 'favicon.ico'))
    # formularze w produkcji wysylane przez wyslij.php na serwerze klienta
    cfg = os.path.join(OUT, 'assets', 'js', 'config.js')
    c = open(cfg, encoding='utf-8').read()
    c2 = c.replace("formularz: { url: '' }", "formularz: { url: 'wyslij.php' }")
    assert c2 != c, 'config.js: brak pola formularz'
    open(cfg, 'w', encoding='utf-8', newline='\n').write(c2)

zapisz('site.webmanifest', json.dumps({
    "name": "Potocki Dwór - hotel i restauracja", "short_name": "Potocki Dwór", "lang": "pl", "start_url": "./",
    "display": "browser", "background_color": "#ffffff", "theme_color": "#ffffff",
    "icons": [{"src": "assets/img/ikona-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "assets/img/ikona-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False, indent=1) + '\n')

lista = list(STRONY) + ([('404.html', '404.html', '404')] if PROD else [])
for src, out, klucz in lista:
    if klucz == '404':
        meta = {"title": "Nie ma takiej strony | Potocki Dwór", "description": "Strona nie istnieje. Przejdź do strony głównej Potockiego Dworu.",
                "noindex": True, "og": "fasada", "cta_naglowek": ["Zapytaj o termin", "przyjecia/#planer"]}
        tresc = ('<section class="sekcja"><div class="wrap"><h1>Nie ma takiej strony</h1><p class="lead-s">Adres mógł się zmienić po odświeżeniu strony. '
                 'Zapraszamy na stronę główną albo do działu, którego szukasz.</p><p class="hero-cta"><a class="btn btn-glowny" href="{{R}}">Strona główna</a>'
                 '<a class="btn btn-obrys" href="{{R}}restauracja/#menu">Karta menu</a><a class="btn btn-obrys" href="{{R}}kontakt/">Kontakt</a></p></div></section>')
        R = '/'   # 404 serwowana pod dowolnym adresem - sciezki od katalogu glownego domeny
    else:
        meta, tresc = wczytaj(src)
        R = '../' * out.count('/')
    meta['sciezka'] = out.replace('index.html', '') if klucz != '404' else ''
    html = szablon(meta, tresc, klucz, R)
    if PROD:
        html = re.sub(r'<!--(?!\[).*?-->\n?', '', html, flags=re.S)   # notatki robocze z _src nie trafiaja na serwer
    zapisz(out, html)
    dl = re.findall('[–—]', html)
    print(out, len(html), 'DLUGIE MYSLNIKI!' if dl else '')

if PROD:
    dzis = datetime.date.today().isoformat()
    zapisz('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /wyslij.php\n\nSitemap: {DOMENA}sitemap.xml\n')
    zapisz('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
           ''.join(f'  <url><loc>{DOMENA}{o.replace("index.html", "")}</loc><lastmod>{dzis}</lastmod></url>\n' for _s, o, _k in STRONY) + '</urlset>\n')
    zapisz('llms.txt', f"""# Potocki Dwór - hotel i restauracja (Potok Wielki, Jędrzejów)

> Hotel (23 pokoje ze śniadaniem), restauracja z kuchnią polsko-włoską oraz sale na wesela, przyjęcia okolicznościowe i konferencje w Potoku Wielkim 83A, 28-300 Jędrzejów (województwo świętokrzyskie). Operator: ECOTUR Sp. z o.o.

## Kontakt
- Recepcja i rezerwacje pokoi: {TEL_T}, {MAIL}
- Przyjęcia, wesela, imprezy okolicznościowe i catering: Manager przyjęć, 784 043 570, k.wieczorek@potockidwor.pl
- Oferta dla firm, konferencje, szkolenia: Michał Pronobis, 532 162 301, m.pronobis@potockidwor.pl
- Adres: Potok Wielki 83A, 28-300 Jędrzejów; GPS 50.60852, 20.23644
- Godziny restauracji i recepcji: codziennie 12:00-22:00, w niedzielę 12:00-21:00

## Strony
- [Strona główna]({DOMENA}): hotel, restauracja, sale i oferta w skrócie
- [Restauracja i karta menu]({DOMENA}restauracja/): pełna karta z cenami i gramaturami (przystawki, zupy, steki, makarony, pizza, pierogi, desery, piwa kraftowe, drinki)
- [Hotel]({DOMENA}hotel/): 23 pokoje 1- i 2-osobowe z łazienką, Wi-Fi i TV, śniadanie w cenie noclegu, zapytanie o pokój
- [Przyjęcia i wesela]({DOMENA}przyjecia/): Sala Balowa do 200 osób, Sala Bankietowa do 30, Sala Restauracyjna do 50 i Patio do 35 po indywidualnych ustaleniach; planer przyjęcia z kalendarzem wolnych terminów
- [Catering]({DOMENA}catering/): koryta mięsne (I: ok. 10-12 osób 695 zł, II: 12-18 osób 1150 zł, III: 20-30 osób 1995 zł) i boxy okolicznościowe dla 6-8 osób (na zimno 260 zł, na ciepło 490 zł, serów 280 zł, wędlin dojrzewających 280 zł); transport, na życzenie obsługa kelnerska, zastawa i szkło; zamówienia: 784 043 570, k.wieczorek@potockidwor.pl
- [Dla biznesu]({DOMENA}dla-biznesu/): konferencje i szkolenia do 200 osób, przerwy kawowe, noclegi, integracje, spływy kajakowe Nidą
- [Kontakt i dojazd]({DOMENA}kontakt/): telefony działów, mapa, formularz
""")
    # nieuzywane zdjecia nie trafiaja na serwer (lzejsza paczka): plik zostaje, gdy jego nazwa albo rdzen ('d-tatar') wystepuje w tekstach strony
    teksty = ''
    for r_, d_, f_ in os.walk(OUT):
        for n_ in f_:
            if n_.endswith(('.html', '.js', '.css', '.webmanifest', '.txt', '.xml')):
                teksty += open(os.path.join(r_, n_), encoding='utf-8').read()
    usuniete = 0
    for r_, d_, f_ in os.walk(os.path.join(OUT, 'assets', 'img')):
        for n_ in f_:
            rdzen = re.sub(r'-\d{3,4}$', '', os.path.splitext(n_)[0])
            if n_ not in teksty and ("'" + rdzen + "'") not in teksty and ('"' + rdzen + '"') not in teksty:
                os.remove(os.path.join(r_, n_)); usuniete += 1
    print('usuniete nieuzywane zdjecia:', usuniete)
    print('PROD:', OUT)
