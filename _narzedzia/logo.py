# Logo z plikow klienta (1500x1500 JPG) -> przezroczyste PNG (granatowe i biale) + favicon.
import sys, os
from PIL import Image, ImageOps, ImageChops
SRC = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'img')
GRANAT = (14, 28, 41)
def alfa(path, ciemne_na_jasnym):
    g = ImageOps.grayscale(Image.open(path))
    a = ImageOps.invert(g) if ciemne_na_jasnym else g
    a = a.point(lambda v: 0 if v < 45 else min(255, int((v-45)*255/190)))
    return a
for nazwa, plik, ciemne, kolor in [('logo-granat', 'biale_logo.jpg', True, GRANAT), ('logo-biale', 'logo_ciemne.jpg', False, (255, 255, 255))]:
    a = alfa(os.path.join(SRC, plik), ciemne); bb = a.getbbox(); a = a.crop(bb)
    im = Image.new('RGBA', a.size, kolor + (0,)); im.putalpha(a)
    w = 720; im = im.resize((w, round(a.size[1]*w/a.size[0])), Image.LANCZOS)
    im.save(os.path.join(OUT, nazwa + '.png'), optimize=True); print(nazwa, im.size, bb)
    if nazwa == 'logo-biale':
        # litera P jako favicon
        t = im.crop((0, 0, round(im.size[0]*0.115), round(im.size[1]*0.68)))
        t = t.crop(t.getbbox())
        fav = Image.new('RGBA', (256, 256), GRANAT + (255,))
        s = 190 / t.size[1]; t = t.resize((round(t.size[0]*s), 190), Image.LANCZOS)
        fav.alpha_composite(t, ((256-t.size[0])//2, 33))
        fav.save(os.path.join(OUT, 'favicon.png')); fav.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, 'apple-touch-icon.png'))
