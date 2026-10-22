# Przygotowanie zdjec: oryginaly (poza repo) -> assets/img/*.webp (1600/800 px, dania takze 1200/600).
# Uzycie: python -I _narzedzia/zdjecia.py "C:/Users/Admin/Downloads/PotockiDwor_dysk_2210"
import sys, os
from PIL import Image, ImageOps
SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'img')
M = {
 # obiekt i hotel
 'fasada': 'obiekt&hotel/R&B-9222.jpg', 'fasada2': 'obiekt&hotel/R&B-9214.jpg', 'fasada3': 'obiekt&hotel/R&B-9226.jpg',
 'pokoj-dbl': 'obiekt&hotel/R&B-8930.jpg', 'pokoj-dbl2': 'obiekt&hotel/R&B-8933.jpg', 'pokoj-twin': 'obiekt&hotel/R&B-8849.jpg',
 'pokoj-twin2': 'obiekt&hotel/R&B-8852.jpg', 'pokoj-twin3': 'obiekt&hotel/R&B-8903.jpg', 'pokoj-lozko': 'obiekt&hotel/R&B-8910.jpg',
 'pokoj-biurko': 'obiekt&hotel/R&B-8872.jpg', 'lazienka': 'obiekt&hotel/R&B-8886.jpg', 'recznik': 'obiekt&hotel/R&B-8891.jpg',
 'pokoj-wejscie': 'obiekt&hotel/R&B-8896.jpg', 'pokoj-detal': 'obiekt&hotel/R&B-8856.jpg',
 # restauracja
 'resto-sala': 'resto/R&B-9088.jpg', 'resto-sala2': 'resto/R&B-9093.jpg', 'resto-stol': 'resto/R&B-9079.jpg', 'resto-okno': 'resto/R&B-9084.jpg',
 'resto-detal': 'resto/R&B-9085.jpg', 'oliwy': 'resto/R&B-9096.jpg', 'resto-kwiat': 'resto/R&B-9073.jpg', 'resto-nakryta': 'resto/DSC06708.jpg',
 'resto-kolumny': 'resto/DSC06844.jpg', 'resto-pusta': 'resto/R&B-9098.jpg',
 # sala balowa
 'balowa-1': 'sala balowa/DSC06564.jpg', 'balowa-2': 'sala balowa/DSC06971.jpg', 'balowa-parkiet': 'sala balowa/DSC06984.jpg',
 'balowa-3': 'sala balowa/DSC07866.jpg', 'balowa-4': 'sala balowa/DSC07474.jpg', 'balowa-stol': 'sala balowa/DSC06536.jpg',
 'balowa-stol2': 'sala balowa/DSC07054.jpg', 'balowa-scianka': 'sala balowa/DSC06391.jpg', 'balowa-dj': 'sala balowa/DSC07845.jpg',
 'balowa-5': 'sala balowa/DSC06501.jpg', 'balowa-stol3': 'sala balowa/DSC07378.jpg',
 # sala bankietowa (zdjecia z telefonu, pionowe)
 'bankietowa-1': 'sala bankietowa/prev.Eidy7tXKPjDCtxnIZctif0UjBR7XsynpcSFQ0afPvdE.jpeg',
 'bankietowa-2': 'sala bankietowa/prev.SkDqoqcezSLkNPraQPPqyyk2thg_03_6tAczWpbyQs4.jpeg',
 'bankietowa-3': 'sala bankietowa/prev.8USrD-AWY_VzYre-5Zte1NyWRzF7r35K4v-ZiSDStNY.jpeg',
 'bankietowa-4': 'sala bankietowa/prev.ycyI6iTWFflOgXhyblILyz0CvOb57nzqzQGne33-znM.jpeg',
 'bankietowa-bar': 'sala bankietowa/prev.169EvwkmxGigKTUPVkTDc9PaFh84OYijcpFvVVkpc_c.jpeg',
 # patio, bufety, catering
 'patio': 'patio/DSC06265.jpg', 'patio-2': 'patio/DSC06272.jpg', 'patio-stol': 'patio/DSC06290.jpg', 'kawa': 'patio/DSC06328.jpg', 'desery': 'patio/DSC06343.jpg',
 'bufet-1': 'bufety/DSC07736.jpg', 'bufet-2': 'bufety/DSC07756.jpg', 'bufet-3': 'bufety/DSC06823.jpg', 'bufet-desery': 'bufety/DSC06833.jpg',
 'bufet-wina': 'bufety/DSC06638.jpg', 'bufet-4': 'bufety/DSC07781.jpg', 'bufet-5': 'bufety/DSC07105.jpg', 'bufet-6': 'bufety/DSC06944.jpg',
 'bufet-mule': 'bufety/DSC07648.jpg', 'bufet-piwo': 'bufety/DSC07353.jpg',
 'catering-1': 'Cateringi/IMG-20261022-WA0020.jpg', 'catering-2': 'Cateringi/IMG-20261022-WA0001.jpg', 'catering-3': 'Cateringi/IMG-20261022-WA0024.jpg',
 'catering-4': 'Cateringi/IMG-20261022-WA0021.jpg',
}
DANIA = {
 'd-gruszka': 'burak_koziser_gruszka.jpg', 'd-deska-sery': 'deska_serywloskie.jpg', 'd-deska-wedliny': 'deska_wedliny.jpg', 'd-dorada': 'dorada.jpg',
 'd-dynia': 'dyniaigorgonzola.jpg', 'd-flaki': 'flaczki_boczniak.jpg', 'd-gicz': 'gicz_jagnieca.jpg', 'd-kaczka': 'kaczka.jpg',
 'd-krem-pomidorowy': 'krem_pomidorowy.jpg', 'd-kurczak-verde': 'kurczak_verde.jpg', 'd-losos': 'losos_zaferano.jpg', 'd-losos2': 'losos_zaferrano.jpg',
 'd-menu-stol': 'menu_total.jpg', 'd-osmiornica': 'osmiornica_mediteranera.jpg', 'd-risotto': 'risotto_bosco.jpg', 'd-spaghetti-gamberi': 'spagetti_gamberi.jpg',
 'd-poledwica': 'stek_poledwica.jpg', 'd-stek-rostbef': 'stek_rosbef.jpg', 'd-stek-rostbef2': 'stek_rostbef.jpg', 'd-steki': 'steki.jpg',
 'd-tagliatelle-salmone': 'tagiatele_salmone.jpg', 'd-tagliatelle-tartufo': 'tagiatele_tartufo.jpg', 'd-owoce-morza': 'talerz_owocemorza (2).jpg',
 'd-owoce-morza2': 'talerz_owocemorza.jpg', 'd-tatar': 'tatar.jpg', 'd-tiramisu': 'tiramisu_tropicale.jpg',
}
DRINKI = sorted(os.listdir(os.path.join(SRC, 'Drinki')))
def zapisz(im, nazwa, dl, q=78):
    w, h = im.size; s = dl / max(w, h)
    if s < 1: im = im.resize((round(w*s), round(h*s)), Image.LANCZOS)
    im.save(os.path.join(OUT, f'{nazwa}-{dl}.webp'), 'WEBP', quality=q, method=6)
def otworz(p):
    im = Image.open(p); im = ImageOps.exif_transpose(im); return im.convert('RGB')
os.makedirs(OUT, exist_ok=True)
for n, p in M.items():
    im = otworz(os.path.join(SRC, p)); zapisz(im, n, 1600); zapisz(im, n, 800)
im = otworz(os.path.join(SRC, M['fasada'])); zapisz(im, 'fasada', 2000)
for n, p in DANIA.items():
    im = otworz(os.path.join(SRC, 'nowe dania', p)); zapisz(im, n, 1200); zapisz(im, n, 400, 74)
for i, f in enumerate([f for f in DRINKI if f.lower().endswith('.jpg')], 1):
    im = otworz(os.path.join(SRC, 'Drinki', f)); zapisz(im, f'drink-{i:02d}', 1200); zapisz(im, f'drink-{i:02d}', 400, 74)
print('ok', len(os.listdir(OUT)))
