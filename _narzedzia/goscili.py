# "Gościli u nas": przygotowuje logotypy i wstawia je do stron:
#   _src/biznes.html - statyczna siatka wszystkich logotypów (znaczniki <!--GOSCILI-->),
#   _src/start.html  - pasek 8 najbardziej rozpoznawalnych pod hero (znaczniki <!--GOSCILI8-->).
# Logotypy pokazywane są jednobarwnie (CSS: grayscale + brightness(--b) + contrast), kolor po najechaniu.
# Oryginały (pobrane z oficjalnych stron firm) leżą w _src/goscili_oryg/ (poza repo).
# Uzycie: python -I _narzedzia/goscili.py, potem python -I _narzedzia/build.py
import os, re, math
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ORYG = os.path.join(ROOT, '_src', 'goscili_oryg')
OUT = os.path.join(ROOT, 'assets', 'img', 'goscili')
GRANAT = '#0e1c29'
H2X = 128  # wysokość pliku rastrowego (2x największej wysokości na stronie)

# kolejność = kolejność w siatce; (plik oryginału, nazwa pliku wyjściowego, alt, korekta wysokości optycznej,
#   jasność przed progowaniem do jednego koloru: niższa = jasne kolory logo ciemnieją, wyższa = jasne tło znika)
LOGA = [
  ('bnp.png', 'bnp-paribas', 'BNP Paribas', 0.95, .85),
  ('pge.png', 'pge', 'PGE', 0.9, .75),
  ('deheus.svg', 'de-heus', 'De Heus', 1.0, .6),
  ('stefczyk.png', 'kasa-stefczyka', 'Kasa Stefczyka', 1.12, .85),
  ('universal.svg', 'universal', 'Universal', 0.92, .85),
  ('quickpack.svg', 'quickpack', 'Quickpack', 0.95, .85),
  ('famet.png', 'famet', 'Famet', 0.9, .85),
  ('sefako.png', 'sefako', 'Sefako', 1.05, .55),
  ('vanstar.svg', 'vanstar', 'Vanstar', 0.92, .85),
  ('jedrzejow-baner.png', 'miasto-jedrzejow', 'Urząd Miasta Jędrzejów', 1.0, .85),
  ('sano.svg', 'sano', 'Sano', 0.95, 1.15),
  ('renmar.png', 'ren-mar', 'Ren-Mar', 1.0, .5),
  ('iglomen.svg', 'iglomen', 'Iglomen', 1.0, .85),
  ('bs.png', 'bs-jedrzejow', 'Świętokrzyski Bank Spółdzielczy w Jędrzejowie', 1.0, .7),
  ('flora-biale.png', 'flora-praszka', 'Flora Praszka', 0.95, .85),
]
# pasek na stronie głównej (brief 04.11): 8 najbardziej rozpoznawalnych
NA_GLOWNA = ['bnp-paribas', 'pge', 'de-heus', 'kasa-stefczyka', 'universal', 'quickpack', 'famet', 'sefako']
# logotypy jednobarwne białe (na stronie firmy na ciemnym tle) -> ten sam kształt w kolorze granatowym
NA_GRANAT = {'universal.svg', 'flora-biale.png'}


def wysokosc(aspekt, korekta):
    # jednolita wysokość optyczna: szerokie logotypy niższe, zwarte wyższe (podobna powierzchnia)
    h = 46 * math.sqrt(2.6 / aspekt) * korekta
    return round(min(max(h, 28), 58))


def svg(plik, nazwa):
    t = open(os.path.join(ORYG, plik), encoding='utf-8').read()
    t = re.sub(r'<\?xml.*?\?>|<!--.*?-->|<desc>.*?</desc>|<title>.*?</title>', '', t, flags=re.S)
    t = re.sub(r'\s(class="bu-header__logo__icon"|id="[^"]*"|data-name="[^"]*")', '', t, count=3)
    if plik in NA_GRANAT:
        t = re.sub(r'fill="(white|#fff|#ffffff)"', f'fill="{GRANAT}"', t, flags=re.I)
    t = re.sub(r'>\s+<', '><', t).strip()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', t).group(1).replace(',', ' ').split()]
    open(os.path.join(OUT, nazwa + '.svg'), 'w', encoding='utf-8', newline='\n').write(t)
    return nazwa + '.svg', vb[2] / vb[3]


def raster(plik, nazwa):
    im = Image.open(os.path.join(ORYG, plik)).convert('RGBA')
    im = im.crop(im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox())  # bez pustych marginesów
    if plik in NA_GRANAT:
        r, g, b = (int(GRANAT[i:i + 2], 16) for i in (1, 3, 5))
        kolor = Image.new('RGBA', im.size, (r, g, b, 255)); kolor.putalpha(im.getchannel('A')); im = kolor
    if im.height > H2X:
        im = im.resize((round(im.width * H2X / im.height), H2X), Image.LANCZOS)
    im.save(os.path.join(OUT, nazwa + '.webp'), 'WEBP', quality=90, method=6)
    return nazwa + '.webp', im.width / im.height


os.makedirs(OUT, exist_ok=True)
pozycje = {}
for plik, nazwa, alt, kor, jasn in LOGA:
    f, a = (svg if plik.endswith('.svg') else raster)(plik, nazwa)
    h = wysokosc(a, kor); w = round(h * a)
    pozycje[nazwa] = f'<li><img src="{{{{R}}}}assets/img/goscili/{f}" alt="{alt}" width="{w}" height="{h}" style="--h:{h};--b:{jasn}" loading="lazy" decoding="async"></li>'
    print(f'{f:28} {a:5.2f}  {w}x{h}  {os.path.getsize(os.path.join(OUT, f)) // 1024} kB')



def wstaw(plik, znacznik, blok):
    p = os.path.join(ROOT, '_src', plik)
    t = open(p, encoding='utf-8').read()
    t, n = re.subn(rf'<!--{znacznik} .*?<!--/{znacznik}-->', lambda m: blok, t, flags=re.S)
    assert n == 1, f'brak znacznikow <!--{znacznik} ...--> w _src/{plik}'
    open(p, 'w', encoding='utf-8', newline='\n').write(t)


wstaw('biznes.html', 'GOSCILI', '<!--GOSCILI (generuje _narzedzia/goscili.py)-->\n'
      f'    <ul class="goscili-siatka" aria-label="Firmy i instytucje, które u nas gościły">{"".join(pozycje.values())}</ul>\n'
      '    <!--/GOSCILI-->')
wstaw('start.html', 'GOSCILI8', '<!--GOSCILI8 (generuje _narzedzia/goscili.py)-->\n'
      f'      <ul class="goscili-rzad" aria-label="Wybrane firmy i instytucje, które u nas gościły">{"".join(pozycje[n] for n in NA_GLOWNA)}'
      '<li class="goscili-link"><a href="{{R}}dla-biznesu/#goscili">Oferta dla firm</a></li></ul>\n'
      '      <!--/GOSCILI8-->')
print('OK:', len(LOGA), 'logotypów')
