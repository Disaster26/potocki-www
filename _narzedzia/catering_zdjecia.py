# Zdjecia cateringu (Dysk klienta, folder "Catering", 05.11.2026) -> assets/img/c-*.webp (600 i 1400 px, bez EXIF).
# Uzycie: python -I _narzedzia/catering_zdjecia.py "C:/Users/Admin/Downloads/PotockiDwor_dysk_2210/Catering_0511"
import sys, os
from PIL import Image, ImageOps
SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'img')
# nazwa: (plik, obciecie gory 0-1, obciecie dolu 0-1) - pudelka ze zdjec z osoba: bez koszuli u gory
M = {
    'koryto-1': ('koryto-1.jpg', 0, 0), 'koryto-2': ('koryto-2.jpg', 0, 0),
    'box-zimno': ('box-zimno.jpg', .2, 0), 'box-goraco': ('box-goraco.jpg', 0, 0),
    'box-sery': ('box-sery.jpg', .2, 0), 'box-wedliny': ('box-wedliny.jpg', .2, 0),
    'patery-1': ('f02.jpg', 0, 0), 'patery-2': ('f03.jpg', 0, 0), 'patery-3': ('f04.jpg', 0, 0), 'przekaski': ('f05.jpg', 0, 0),
    'koreczki': ('f06.jpg', 0, 0), 'przekaski-2': ('f08.jpg', 0, 0), 'patera-sery': ('f09.jpg', 0, 0), 'stripsy': ('f10.jpg', 0, 0),
    'kotleciki': ('f11.jpg', 0, 0), 'wedliny': ('wa-0923.jpg', 0, 0),
}
for nazwa, (plik, gora, dol) in M.items():
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, plik))).convert('RGB')
    w, h = im.size
    im = im.crop((0, round(h * gora), w, round(h * (1 - dol))))
    for d in (600, 1400):
        k = im.copy()
        k.thumbnail((d, d), Image.LANCZOS)
        k.save(os.path.join(OUT, f'c-{nazwa}-{d}.webp'), 'WEBP', quality=80, method=6)
    print(nazwa, im.size)
