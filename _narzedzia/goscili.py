# Pasek "Gościli u nas" (Dla biznesu): przygotowuje logotypy i wstawia listę do _src/biznes.html.
# Oryginały (pobrane z oficjalnych stron firm) leżą w _src/goscili_oryg/ (poza repo).
# Uzycie: python -I _narzedzia/goscili.py, potem python -I _narzedzia/build.py
import os, re, math
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ORYG = os.path.join(ROOT, '_src', 'goscili_oryg')
OUT = os.path.join(ROOT, 'assets', 'img', 'goscili')
GRANAT = '#0e1c29'
H2X = 128  # wysokość pliku rastrowego (2x największej wysokości na stronie)

# kolejność = kolejność na pasku; (plik oryginału, nazwa pliku wyjściowego, alt, korekta wysokości optycznej)
LOGA = [
  ('universal.svg', 'universal', 'Universal', 0.92),
  ('bnp.png', 'bnp-paribas', 'BNP Paribas', 0.95),
  ('quickpack.svg', 'quickpack', 'Quickpack', 0.95),
  ('pge.png', 'pge', 'PGE', 0.9),
  ('sefako.png', 'sefako', 'Sefako', 1.05),
  ('deheus.svg', 'de-heus', 'De Heus', 1.0),
  ('famet.png', 'famet', 'Famet', 0.9),
  ('stefczyk.png', 'kasa-stefczyka', 'Kasa Stefczyka', 1.12),
  ('vanstar.svg', 'vanstar', 'Vanstar', 0.92),
  ('jedrzejow-baner.png', 'miasto-jedrzejow', 'Urząd Miasta Jędrzejów', 1.0),
  ('sano.svg', 'sano', 'Sano', 0.66),
  ('renmar.png', 'ren-mar', 'Ren-Mar', 1.0),
  ('iglomen.svg', 'iglomen', 'Iglomen', 1.0),
  ('bs.png', 'bs-jedrzejow', 'Świętokrzyski Bank Spółdzielczy w Jędrzejowie', 1.0),
  ('flora-biale.png', 'flora-praszka', 'Flora Praszka', 0.95),
]
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
pozycje = []
for plik, nazwa, alt, kor in LOGA:
    f, a = (svg if plik.endswith('.svg') else raster)(plik, nazwa)
    h = wysokosc(a, kor); w = round(h * a)
    pozycje.append(f'<li><img src="{{{{R}}}}assets/img/goscili/{f}" alt="{alt}" width="{w}" height="{h}" style="--h:{h}" decoding="async"></li>')
    print(f'{f:28} {a:5.2f}  {w}x{h}  {os.path.getsize(os.path.join(OUT, f)) // 1024} kB')

lista = ''.join(pozycje)
blok = ('<!--GOSCILI (generuje _narzedzia/goscili.py)-->\n'
        '    <div class="goscili-pas">\n'
        f'      <div class="goscili-tor"><ul class="goscili-lista" aria-label="Firmy i instytucje, które u nas gościły">{lista}</ul>'
        f'<ul class="goscili-lista goscili-kopia" aria-hidden="true">{re.sub(r'alt="[^"]*"', 'alt=""', lista)}</ul></div>\n'
        '    </div>\n'
        '    <!--/GOSCILI-->')
p = os.path.join(ROOT, '_src', 'biznes.html')
t = open(p, encoding='utf-8').read()
t, n = re.subn(r'<!--GOSCILI.*?<!--/GOSCILI-->', lambda m: blok, t, flags=re.S)
assert n == 1, 'brak znacznikow <!--GOSCILI--> w _src/biznes.html'
open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('OK:', len(LOGA), 'logotypów')
