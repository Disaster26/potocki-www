# Buduje statyczny podgląd ze wspólnego szablonu (nagłówek, stopka) i treści podstron z _src/.
# Uzycie: python -I _narzedzia/build.py
# W WordPressie: szablon() = header.php + footer.php, pliki _src/*.html = szablony stron / bloki.
import os, json, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, '_src')
V = '2'  # wersja plikow css/js (cache)

STRONY = [
  # plik zrodlowy, sciezka wyjsciowa, klucz menu
  ('start.html', 'index.html', 'start'),
  ('restauracja.html', 'restauracja/index.html', 'restauracja'),
  ('hotel.html', 'hotel/index.html', 'hotel'),
  ('przyjecia.html', 'przyjecia/index.html', 'przyjecia'),
  ('biznes.html', 'dla-biznesu/index.html', 'biznes'),
  ('kontakt.html', 'kontakt/index.html', 'kontakt'),
]
MENU = [('restauracja', 'restauracja/', 'Restauracja'), ('hotel', 'hotel/', 'Hotel'), ('przyjecia', 'przyjecia/', 'Przyjęcia'),
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
    cta_h = f'<a class="btn btn-zloty btn-maly gora-cta" href="{R}{cta[1]}">{cta[0]}</a>' if cta else ''
    mob = meta.get('cta_mob')
    mob_h = f'<div class="mob" aria-hidden="true"><a class="btn btn-linia-j" href="tel:{meta.get('tel_mob', TEL)}" data-ev="click_tel">Zadzwoń</a><a class="btn btn-zloty" href="{R}{mob[1]}" tabindex="-1">{mob[0]}</a></div>' if mob else ''
    preload = ''
    if meta.get('hero'):
        h = meta['hero']
        preload = f'<link rel="preload" as="image" href="{R}assets/img/{h}-1600.webp" imagesrcset="{R}assets/img/{h}-800.webp 800w, {R}assets/img/{h}-1600.webp 1600w" imagesizes="100vw">'
    ld = meta.get('jsonld', [])
    ld_h = ''.join(f'<script type="application/ld+json">{json.dumps(LD[x], ensure_ascii=False, separators=(",", ":"))}</script>' for x in ld)
    skrypty = ''.join(f'<script src="{R}{s}?v={V}"></script>' for s in meta.get('skrypty', []))
    leaflet_css = '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">' if meta.get('mapa') else ''
    leaflet_js = '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>' if meta.get('mapa') else ''
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<!-- PODGLĄD: noindex do czasu przełączenia na potockidwor.pl. Po przełączeniu: usunąć noindex, dodać canonical https://potockidwor.pl/{meta["sciezka"]} -->
<meta name="robots" content="noindex, nofollow">
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="Potocki Dwór">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["description"]}">
<meta property="og:image" content="{R}assets/img/{meta.get("og", "fasada")}-1600.webp">
<meta name="theme-color" content="#0e1c29">
<link rel="icon" type="image/png" href="{R}assets/img/favicon.png">
<link rel="apple-touch-icon" href="{R}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
{leaflet_css}
<link rel="stylesheet" href="{R}assets/css/style.css?v={V}">
{preload}
{ld_h}
<script src="{R}assets/js/config.js?v={V}"></script>
<!-- POMIAR: GA4 + Meta Pixel ładowane przez assets/js/app.js (zgody, Consent Mode v2) dopiero po wpisaniu identyfikatorów w config.js -->
</head>
<body data-strona="{klucz}" data-root="{R}">
<a class="pomin" href="#tresc">Przejdź do treści</a>
<header class="gora">
  <div class="wrap gora-in">
    <a class="logo" href="{R}" aria-label="Potocki Dwór - strona główna"><img src="{R}assets/img/logo-biale.png" width="720" height="238" alt="Potocki Hotel - Restauracja"></a>
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
    <div class="stopka-l">
      <img class="stopka-logo" src="{R}assets/img/logo-biale.png" width="720" height="238" alt="Potocki Hotel - Restauracja" loading="lazy">
      <p>Potok Wielki 83A, 28-300 Jędrzejów</p>
      <p><a href="tel:{TEL}" data-ev="click_tel">{TEL_T}</a> · <a href="mailto:{MAIL}">{MAIL}</a></p>
      <p class="social"><a href="https://www.facebook.com/PotockiDwor" target="_blank" rel="noopener">Facebook</a> · <a href="https://www.instagram.com/potocki_dwor/" target="_blank" rel="noopener">Instagram</a></p>
    </div>
    <nav class="stopka-menu" aria-label="Menu w stopce"><a href="{R}">Strona główna</a>{"".join(f'<a href="{R}{h}">{n}</a>' for k, h, n in MENU)}</nav>
  </div>
  <div class="wrap stopka-dol">
    <p>© Potocki Dwór · ECOTUR Sp. z o.o.</p>
    <p><button type="button" class="link-cookies" data-cookies-ustawienia hidden>Ustawienia plików cookies</button> <span class="robocza">Wersja robocza strony - podgląd dla Potockiego Dworu.</span></p>
  </div>
</footer>
{mob_h}
<dialog class="lightbox" id="lightbox" aria-label="Powiększone zdjęcie"><button type="button" class="lb-zamknij" aria-label="Zamknij">×</button><button type="button" class="lb-nav lb-pop" aria-label="Poprzednie zdjęcie">‹</button><img alt=""><button type="button" class="lb-nav lb-nast" aria-label="Następne zdjęcie">›</button><p class="lb-opis"></p></dialog>
{leaflet_js}
{skrypty}
<script src="{R}assets/js/app.js?v={V}"></script>
</body>
</html>
'''

SAME_AS = ["https://www.facebook.com/PotockiDwor", "https://www.instagram.com/potocki_dwor/"]
ADRES = {"@type": "PostalAddress", "streetAddress": "Potok Wielki 83A", "postalCode": "28-300", "addressLocality": "Jędrzejów", "addressRegion": "świętokrzyskie", "addressCountry": "PL"}
GEO = {"@type": "GeoCoordinates", "latitude": 50.6085, "longitude": 20.2364}
WWW = "https://potockidwor.pl/"
LD = {
  'hotel': {"@context": "https://schema.org", "@type": "Hotel", "@id": WWW + "#hotel", "name": "Potocki Dwór", "url": WWW + "hotel/",
            "telephone": TEL, "email": MAIL, "address": ADRES, "geo": GEO, "image": WWW + "assets/img/fasada-1600.webp", "sameAs": SAME_AS,
            "numberOfRooms": 23, "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": "Śniadanie w cenie noclegu", "value": True},
            {"@type": "LocationFeatureSpecification", "name": "Wi-Fi", "value": True}]},
  'restauracja': {"@context": "https://schema.org", "@type": "Restaurant", "@id": WWW + "#restauracja", "name": "Restauracja Potocki Dwór", "url": WWW + "restauracja/",
            "telephone": TEL, "email": MAIL, "address": ADRES, "geo": GEO, "image": WWW + "assets/img/resto-sala-1600.webp", "sameAs": SAME_AS,
            "servesCuisine": ["polska", "włoska"], "hasMenu": WWW + "restauracja/#menu",
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"], "opens": "12:00", "closes": "22:00"},
                                          {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "12:00", "closes": "21:00"}]},
}

for src, out, klucz in STRONY:
    meta, tresc = wczytaj(src)
    glebokosc = out.count('/')
    R = '../' * glebokosc
    meta['sciezka'] = out.replace('index.html', '')
    html = szablon(meta, tresc, klucz, R)
    sciezka = os.path.join(ROOT, out); os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    open(sciezka, 'w', encoding='utf-8', newline='\n').write(html)
    dl = re.findall('[–—]', html)
    print(out, len(html), 'DLUGIE MYSLNIKI!' if dl else '')
