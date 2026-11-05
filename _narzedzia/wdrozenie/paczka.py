# Paczki wdrozeniowe Potocki Dwor -> C:\Users\Admin\Downloads\Potocki_wdrozenie\
#   site/                         wersja produkcyjna (build.py --prod)
#   potocki-www-ftp.zip           do wgrania przez FTP do katalogu domeny (strona + .htaccess + wyslij.php)
#   potocki-static-wordpress.zip  wtyczka WordPress (na wypadek WordPressa): kopiuje strone do katalogu glownego, blok .htaccess, formularze
#   htaccess-blok.txt             sam blok regul (przekierowania 301, https, bez www)
# Uzycie: python -I _narzedzia/wdrozenie/paczka.py
import os, sys, shutil, subprocess, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = r'C:\Users\Admin\Downloads\Potocki_wdrozenie'
SITE = os.path.join(OUT, 'site')
DOM = 'potockidwor.pl'

subprocess.run([sys.executable, '-I', os.path.join(REPO, '_narzedzia', 'build.py'), '--prod', SITE], check=True)

# stare adresy (obecna strona potockidwor.pl = jeden plik index.html + 5 zdjec, sprawdzone 05.11.2026)
# oraz typowe adresy, pod ktorymi ludzie i wyszukiwarki szukaja dzialow hotelu/restauracji
STARE = [
    (r'^(o-nas|onas|oferta|start|home|strona-glowna)/?$', '/'),
    (r'^(menu|karta|karta-menu|kuchnia)/?$', '/restauracja/'),
    (r'^(noclegi|pokoje|nocleg|rezerwacja|rezerwacje)/?$', '/hotel/'),
    (r'^(wesela|wesele|sale|sala|imprezy|przyjecie|przyjecia-okolicznosciowe|uroczystosci)/?$', '/przyjecia/'),
    (r'^(koryta|boxy|catering-jedrzejow)/?$', '/catering/'),
    (r'^(konferencje|konferencja|szkolenia|biznes|dla-firm|firmy)/?$', '/dla-biznesu/'),
    (r'^(dojazd|mapa|kontakty)/?$', '/kontakt/'),
    (r'^elewacja\.jpg$', '/'),
    (r'^restauracja\.jpg$', '/restauracja/'),
    (r'^jedzenie\.jpg$', '/restauracja/'),
    (r'^pokoj\.jpg$', '/hotel/'),
    (r'^wesele\.jpg$', '/przyjecia/'),
]
L = ['# Potocki Dwor - strona statyczna (Wylinka, 05.11.2026)',
     'DirectoryIndex index.html index.php',
     'Options -Indexes',
     'ErrorDocument 404 /404.html',
     '<IfModule mod_headers.c>',
     '  Header always set X-Content-Type-Options "nosniff"',
     '  Header always set Referrer-Policy "strict-origin-when-cross-origin"',
     '  <FilesMatch "\\.(html|webmanifest|xml|txt)$">',
     '    Header set Cache-Control "no-cache, must-revalidate"',
     '  </FilesMatch>',
     '  <FilesMatch "\\.(webp|png|jpg|ico|css|js)$">',
     '    Header set Cache-Control "public, max-age=2592000"',
     '  </FilesMatch>',
     '</IfModule>',
     '<IfModule mod_rewrite.c>',
     'RewriteEngine On',
     'RewriteBase /',
     '# dane formularza (sekret, liczniki) nigdy publicznie',
     'RewriteRule ^_formularz_dane(/|$) - [F,L]',
     '# www i http -> https://potockidwor.pl jednym skokiem',
     'RewriteCond %{HTTP_HOST} ^www\\. [NC]',
     'RewriteRule ^ https://%s%%{REQUEST_URI} [R=301,L]' % DOM,
     'RewriteCond %{HTTPS} !=on',
     'RewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]',
     'RewriteRule ^ https://%s%%{REQUEST_URI} [R=301,L]' % DOM,
     '# /index.html -> / (jeden adres strony glownej)',
     'RewriteCond %{THE_REQUEST} \\s/index\\.html[\\s?] [NC]',
     'RewriteRule ^index\\.html$ / [R=301,L]',
     '# dzialy bez ukosnika na koncu -> z ukosnikiem',
     'RewriteRule ^(restauracja|hotel|przyjecia|catering|dla-biznesu|kontakt)$ /$1/ [R=301,L]',
     '# stare i potoczne adresy -> nowe dzialy']
L += ['RewriteRule %s %s [R=301,L,NC]' % (a, b) for a, b in STARE]
L += ['# strona glowna = index.html (takze gdy w katalogu jest index.php WordPressa)',
      'RewriteCond %{QUERY_STRING} !(^|&)(rest_route|preview|p|page_id)= [NC]',
      'RewriteRule ^$ /index.html [L]',
      '</IfModule>']
BLOK = '\n'.join(L) + '\n'
open(os.path.join(OUT, 'htaccess-blok.txt'), 'w', encoding='utf-8', newline='\n').write('# BEGIN POTOCKI-STATIC\n' + BLOK + '# END POTOCKI-STATIC\n')

def zipuj(katalog, cel, prefiks=''):
    with zipfile.ZipFile(cel, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(katalog):
            for fn in files:
                full = os.path.join(root, fn)
                zf.write(full, prefiks + os.path.relpath(full, katalog).replace('\\', '/'))

# (a) FTP
FTP = os.path.join(OUT, '_ftp')
shutil.rmtree(FTP, ignore_errors=True)
shutil.copytree(SITE, FTP)
shutil.copy2(os.path.join(HERE, 'wyslij.php'), os.path.join(FTP, 'wyslij.php'))
open(os.path.join(FTP, '.htaccess'), 'w', encoding='utf-8', newline='\n').write('# BEGIN POTOCKI-STATIC\n' + BLOK + '# END POTOCKI-STATIC\n')
zipuj(FTP, os.path.join(OUT, 'potocki-www-ftp.zip'))
shutil.rmtree(FTP)

# (b) WordPress
PL = os.path.join(OUT, '_wp', 'potocki-static')
shutil.rmtree(os.path.join(OUT, '_wp'), ignore_errors=True)
shutil.copytree(SITE, os.path.join(PL, 'site'))
shutil.copy2(os.path.join(HERE, 'potocki-static.php'), os.path.join(PL, 'potocki-static.php'))
shutil.copy2(os.path.join(HERE, 'wyslij.php'), os.path.join(PL, 'wyslij.php'))
open(os.path.join(PL, 'htaccess-blok.txt'), 'w', encoding='utf-8', newline='\n').write(BLOK)
open(os.path.join(PL, 'index.php'), 'w', encoding='utf-8', newline='\n').write('<?php\n// Silence is golden.\n')
open(os.path.join(PL, '.htaccess'), 'w', encoding='utf-8', newline='\n').write(
    '# Pliki wtyczki nie sa publiczne (kopia strony jest w katalogu glownym).\n'
    '<IfModule mod_authz_core.c>\n  Require all denied\n</IfModule>\n'
    '<IfModule !mod_authz_core.c>\n  Order allow,deny\n  Deny from all\n</IfModule>\n')
zipuj(os.path.join(OUT, '_wp'), os.path.join(OUT, 'potocki-static-wordpress.zip'))
shutil.rmtree(os.path.join(OUT, '_wp'))
for z in ('potocki-www-ftp.zip', 'potocki-static-wordpress.zip'):
    print(z, os.path.getsize(os.path.join(OUT, z)) // 1024, 'KB')
