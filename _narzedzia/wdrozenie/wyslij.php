<?php
/* Formularze strony Potocki Dwór (przyjęcia, hotel, biznes, kontakt) - wysyłka e-mailem z serwera strony.
   Wzór: formularz SMARTPARKIET / Wylinka (mail() bez -f, From = skrzynka w domenie, znacznik HMAC, pułapka na boty,
   limity zapytań w plikach JSON z blokadą flock, odpowiedź JSON).

   Zabezpieczenia:
   - odbiorcy są STALI (tablica PF_ODBIORCY), z przeglądarki przychodzi tylko rodzaj formularza i Reply-To klienta,
     więc skryptu nie da się użyć do wysyłania poczty na dowolne adresy;
   - POST tylko z własnej domeny (nagłówek Origin), znacznik jednorazowy podpisany HMAC (ważny 3 s - 4 h, związany z siecią klienta),
     ukryte pole _honey (boty dostają "sukces", nic nie jest wysyłane);
   - limit z jednej sieci (IP / prefiks /64 dla IPv6): PF_LIMIT na godzinę, limit łączny na godzinę i dobę;
   - SEKRET i liczniki NIE leżą w repozytorium ani w katalogu strony: skrypt sam tworzy losowy sekret przy pierwszym użyciu
     w katalogu _potocki_formularz POZA katalogiem domeny (poziom wyżej niż public_html), a gdy to niemożliwe -
     w katalogu z blokadą .htaccess. W WordPressie (wtyczka "Potocki static") sekret jest opcją w bazie.

   Wejście (multipart/form-data, fetch z assets/js/app.js):
     GET  ?znacznik=1            -> {"z": "<czas>.<podpis>"}
     POST _z, _honey, _rodzaj (przyjecia|catering|hotel|biznes|kontakt), _subject, _pola = JSON [[etykieta, wartość], ...], email
   Wyjście: JSON {"success": true|false, "blad": ...}; kody 200, 204, 400, 403, 405, 413, 422, 429, 500.

   Tryb testowy (lokalnie): zmienna środowiskowa PF_MAIL_DO_PLIKU=<katalog> - zamiast mail() zapis .eml, dopuszczony Origin localhost;
   PF_KATALOG_DANYCH=<katalog> - sekret i liczniki. Na serwerze tych zmiennych nie ma. */

if (!defined('PF_WCZYTANY')) define('PF_WCZYTANY', 1); else return;

const PF_ODBIORCY = [
    'przyjecia' => 'k.wieczorek@potockidwor.pl',   // przyjęcia, wesela (klient 22.10.2026)
    'catering'  => 'k.wieczorek@potockidwor.pl',   // catering (klient 05.11.2026)
    'hotel'     => 'recepcja@potockidwor.pl',      // rezerwacje pokoi (klient 29.10.2026)
    'biznes'    => 'm.pronobis@potockidwor.pl',    // oferta dla firm (klient 22.10.2026)
    'kontakt'   => 'recepcja@potockidwor.pl',
];
const PF_NADAWCA_DOMYSLNY = 'recepcja@potockidwor.pl';   // istniejąca skrzynka w domenie (SPF/DKIM serwera); zmiana: plik konfiguracyjny niżej
const PF_NADAWCA_NAZWA = 'Formularz potockidwor.pl';
const PF_LIMIT = 6;                  // zgłoszeń z jednej sieci na godzinę
const PF_LIMIT_GLOBALNY_H = 30;      // łącznie na godzinę
const PF_LIMIT_GLOBALNY_D = 150;     // łącznie na dobę
const PF_MAX_ZADANIA = 64 * 1024;    // bajtów
const PF_ZNACZNIK_MIN = 3;
const PF_ZNACZNIK_MAX = 4 * 3600;
const PF_DOMENY = '#^https://(www\.)?potockidwor\.pl$#';
const PF_TELEFON = '798 033 101';
const PF_NL = "\r\n";

function pf_dev() { return (string) getenv('PF_MAIL_DO_PLIKU'); }
function pf_h($s) { return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8'); }
function pf_dziennik($s) { error_log('potocki formularz: ' . $s); }   // bez danych osobowych

/* opcjonalny plik konfiguracyjny POZA katalogiem domeny: <katalog nad public_html>/_potocki_formularz/konfiguracja.php
   z np. <?php define('PF_NADAWCA', 'formularz@potockidwor.pl'); */
function pf_konfiguracja() {
    static $wczytana = false;
    if ($wczytana) return;
    $wczytana = true;
    $dr = rtrim((string) ($_SERVER['DOCUMENT_ROOT'] ?? ''), '/\\');
    if ($dr !== '') {
        $p = dirname($dr) . '/_potocki_formularz/konfiguracja.php';
        if (is_file($p) && is_readable($p)) include $p;
    }
}
function pf_nadawca() { pf_konfiguracja(); return defined('PF_NADAWCA') ? (string) PF_NADAWCA : PF_NADAWCA_DOMYSLNY; }

function pf_naglowki() {
    header('X-Robots-Tag: noindex');
    header('X-Content-Type-Options: nosniff');
    header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
    header('X-LiteSpeed-Cache-Control: no-cache');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header_remove('X-Powered-By');
}
function pf_origin_ok($o) {
    return (bool) (preg_match(PF_DOMENY, $o) || (pf_dev() !== '' && preg_match('#^http://(localhost|127\.0\.0\.1)(:\d+)?$#', $o)));
}
function pf_odpowiedz($ok, $kod = 200, $extra = []) {
    http_response_code($kod);
    if ($kod === 405) header('Allow: GET, POST');
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['success' => $ok] + $extra, JSON_UNESCAPED_UNICODE);
    exit;
}
function pf_wlasny($p) {
    if (!function_exists('fileowner') || !function_exists('getmyuid') || PHP_OS_FAMILY === 'Windows') return true;
    $o = @fileowner($p);
    if ($o === false) return false;
    if ($o === getmyuid()) return true;
    return function_exists('posix_geteuid') && $o === posix_geteuid();
}
// katalog na sekret i liczniki: tryb testowy, POZA katalogiem domeny, wp-content/uploads, katalog strony z blokadą, katalog tymczasowy
function pf_katalog() {
    static $k = false;
    if ($k !== false) return $k;
    $kand = [];
    $t = (string) getenv('PF_KATALOG_DANYCH');
    if (pf_dev() !== '' && $t !== '') $kand[] = rtrim($t, '/\\');
    $dr = rtrim((string) ($_SERVER['DOCUMENT_ROOT'] ?? ''), '/\\');
    if ($dr !== '') $kand[] = dirname($dr) . '/_potocki_formularz';
    if (defined('ABSPATH')) {
        $kand[] = dirname(rtrim(ABSPATH, '/\\')) . '/_potocki_formularz';
        if (defined('WP_CONTENT_DIR')) $kand[] = WP_CONTENT_DIR . '/uploads/potocki-formularz';
    }
    $kand[] = __DIR__ . '/_formularz_dane';
    $kand[] = rtrim(sys_get_temp_dir(), '/\\') . '/potocki_formularz';
    foreach ($kand as $d) {
        if (!is_dir($d) && !@mkdir($d, 0700, true)) continue;
        if (!is_writable($d) || is_link($d) || !pf_wlasny($d)) continue;
        $wStronie = $dr !== '' && strpos(str_replace('\\', '/', realpath($d) ?: $d), str_replace('\\', '/', realpath($dr) ?: $dr) . '/') === 0;
        if ($wStronie || strpos(str_replace('\\', '/', $d), '/uploads/') !== false) {
            if (!is_file($d . '/.htaccess')) @file_put_contents($d . '/.htaccess', "Require all denied\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n");
            if (!is_file($d . '/index.php')) @file_put_contents($d . '/index.php', "<?php\n// Silence is golden.\n");
        }
        return $k = $d;
    }
    pf_dziennik('brak zapisywalnego katalogu na sekret i liczniki');
    return $k = null;
}
// sekret HMAC: w WordPressie opcja w bazie, poza nim plik w katalogu danych (tworzony losowo przy pierwszym użyciu)
function pf_sekret() {
    static $s = null;
    if ($s !== null) return $s;
    if (function_exists('get_option') && pf_dev() === '') {
        $v = get_option('potocki_formularz_sekret');
        if (is_string($v) && preg_match('/^[0-9a-f]{64}$/', $v)) return $s = $v;
        $v = bin2hex(random_bytes(32));
        add_option('potocki_formularz_sekret', $v, '', 'no');
        $v2 = get_option('potocki_formularz_sekret');
        return $s = (is_string($v2) && $v2 !== '' ? $v2 : $v);
    }
    $kat = pf_katalog();
    if ($kat === null) pf_odpowiedz(false, 500);
    $p = $kat . '/sekret.txt';
    $v = is_file($p) ? trim((string) @file_get_contents($p)) : '';
    if (!preg_match('/^[0-9a-f]{64}$/', $v)) { $v = bin2hex(random_bytes(32)); @file_put_contents($p, $v, LOCK_EX); @chmod($p, 0600); }
    return $s = $v;
}
function pf_siec() {
    $ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
    $bin = @inet_pton($ip);
    if ($bin !== false && strlen($bin) === 16) return bin2hex(substr($bin, 0, 8)) . '/64';
    return $ip;
}
function pf_podpis($t) { return hash_hmac('sha256', 'potocki-formularz|' . $t . '|' . pf_siec(), pf_sekret()); }
function pf_wiek($z) {
    if (!is_string($z) || !preg_match('/^(\d{10})\.([0-9a-f]{64})$/', $z, $m)) return null;
    if (!hash_equals(pf_podpis($m[1]), $m[2])) return null;
    $w = time() - (int) $m[1];
    return $w < -5 ? null : max(0, $w);
}
function pf_skrot($s) { return hash_hmac('sha256', 'potocki-limit|' . $s, pf_sekret()); }   // w plikach tylko skróty, bez adresów IP
function pf_z_limitem($plik, callable $fn) {
    $kat = pf_katalog();
    if ($kat === null) return null;
    $sc = $kat . '/' . $plik;
    if (file_exists($sc) && (is_link($sc) || !pf_wlasny($sc))) return null;
    $u = @fopen($sc, 'c+');
    if ($u === false) return null;
    if (!flock($u, LOCK_EX)) { fclose($u); return null; }
    $d = json_decode((string) stream_get_contents($u), true);
    if (!is_array($d)) $d = [];
    $w = $fn($d);
    $j = json_encode($d);
    $ok = ftruncate($u, 0) && rewind($u) && fwrite($u, $j) === strlen($j) && fflush($u);
    flock($u, LOCK_UN); fclose($u);
    return $ok ? $w : null;
}
function pf_zakoduj($s) {
    if (!preg_match('/[^\x20-\x7E]/', $s)) return $s;
    $out = []; $kaw = '';
    foreach (preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY) as $z) {
        if (strlen($kaw . $z) > 45) { $out[] = '=?UTF-8?B?' . base64_encode($kaw) . '?='; $kaw = ''; }
        $kaw .= $z;
    }
    if ($kaw !== '') $out[] = '=?UTF-8?B?' . base64_encode($kaw) . '?=';
    return implode(' ', $out);
}
function pf_b64($s) { return rtrim(chunk_split(base64_encode($s), 76, PF_NL)) . PF_NL; }
function pf_pole($v, $max) {
    $v = is_string($v) ? trim($v) : '';
    if ($v === '' || preg_match('//u', $v) !== 1) return '';
    $v = (string) preg_replace('/[\x00-\x09\x0B-\x1F\x7F]/u', '', $v);
    if (function_exists('mb_substr')) return mb_substr($v, 0, $max, 'UTF-8');
    return preg_match('/^.{0,' . (int) $max . '}/us', $v, $m) ? $m[0] : '';
}
function pf_linia($s) { return trim(preg_replace('/[\r\n\t]+/', ' ', $s)); }
function pf_wyslij($do, $temat, $naglowki, $typ, $tresc) {
    $nag = array_merge([
        'From: ' . pf_zakoduj(PF_NADAWCA_NAZWA) . ' <' . pf_nadawca() . '>',
        'Date: ' . date('r'),
        'Message-ID: <' . bin2hex(random_bytes(12)) . '@potockidwor.pl>',
        'MIME-Version: 1.0',
    ], $naglowki, [$typ]);
    $t = pf_zakoduj($temat);
    if (pf_dev() !== '') {
        $d = pf_dev();
        if (!is_dir($d)) @mkdir($d, 0777, true);
        $plik = rtrim($d, '/\\') . '/' . date('Ymd-His') . '-' . substr(md5($do . microtime()), 0, 6) . '.eml';
        return (bool) file_put_contents($plik, 'To: ' . $do . PF_NL . 'Subject: ' . $t . PF_NL . implode(PF_NL, $nag) . PF_NL . PF_NL . $tresc);
    }
    return mail($do, $t, $tresc, implode(PF_NL, $nag));
}

function pf_obsluz() {
    date_default_timezone_set('Europe/Warsaw');
    pf_naglowki();
    $metoda = $_SERVER['REQUEST_METHOD'] ?? '';
    if ($metoda === 'GET' && isset($_GET['znacznik'])) {
        $t = (string) time();
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['z' => $t . '.' . pf_podpis($t)]);
        exit;
    }
    if ($metoda !== 'POST') pf_odpowiedz(false, 405);

    $dl = (int) ($_SERVER['CONTENT_LENGTH'] ?? 0);
    if ($dl > PF_MAX_ZADANIA) pf_odpowiedz(false, 413, ['blad' => 'rozmiar']);

    // tylko z własnej strony (fetch zawsze wysyła Origin przy POST)
    $origin = (string) ($_SERVER['HTTP_ORIGIN'] ?? '');
    if ($origin === '' || !pf_origin_ok($origin)) pf_odpowiedz(false, 403, ['blad' => 'skad']);

    $wiek = pf_wiek($_POST['_z'] ?? null);
    if ($wiek !== null && $wiek < PF_ZNACZNIK_MIN) pf_odpowiedz(false, 403, ['blad' => 'szybko']);
    if ($wiek === null || $wiek > PF_ZNACZNIK_MAX) pf_odpowiedz(false, 403, ['blad' => 'znacznik']);

    if (!empty($_POST['_honey'])) pf_odpowiedz(true, 200);   // bot: udajemy sukces, nic nie wysyłamy

    $rodzaj = (string) ($_POST['_rodzaj'] ?? '');
    if (!isset(PF_ODBIORCY[$rodzaj])) pf_odpowiedz(false, 422, ['blad' => 'rodzaj']);
    $temat = pf_linia(pf_pole($_POST['_subject'] ?? '', 150));
    if ($temat === '') $temat = 'Zapytanie ze strony';
    $temat .= ' [potockidwor.pl]';
    $email = pf_linia(pf_pole($_POST['email'] ?? '', 120));
    $okMail = $email !== '' && filter_var($email, FILTER_VALIDATE_EMAIL) !== false && !preg_match('/[\r\n,;<>"]/', $email);
    $pola = json_decode((string) ($_POST['_pola'] ?? ''), true);
    if (!is_array($pola) || !$pola || count($pola) > 30) pf_odpowiedz(false, 422, ['blad' => 'pola']);
    $wiersze = [];
    foreach ($pola as $p) {
        if (!is_array($p) || count($p) !== 2) continue;
        $k = pf_linia(pf_pole((string) $p[0], 80));
        $v = str_replace("\r\n", "\n", pf_pole((string) $p[1], 3000));
        if ($k !== '' && $v !== '') $wiersze[] = [$k, $v];
    }
    if (count($wiersze) < 2) pf_odpowiedz(false, 422, ['blad' => 'pola']);

    // limity: z jednej sieci, znacznik jednorazowy, łączny
    $teraz = time();
    $sIp = pf_skrot('siec|' . pf_siec());
    $wolno = pf_z_limitem('ip.json', function (&$d) use ($teraz, $sIp) {
        foreach ($d as $k => $cz) { $d[$k] = array_values(array_filter((array) $cz, function ($t) use ($teraz) { return (int) $t > $teraz - 3600; })); if (!$d[$k]) unset($d[$k]); }
        if (count($d[$sIp] ?? []) >= PF_LIMIT) return false;
        $d[$sIp][] = $teraz; return true;
    });
    if ($wolno === false) pf_odpowiedz(false, 429, ['blad' => 'limit']);
    $sZ = pf_skrot('znacznik|' . $_POST['_z']);
    $wolnyZ = pf_z_limitem('zuzyte.json', function (&$d) use ($teraz, $sZ) {
        $d = array_filter($d, function ($t) use ($teraz) { return (int) $t > $teraz - PF_ZNACZNIK_MAX; });
        if (isset($d[$sZ])) return false;
        $d[$sZ] = $teraz; return true;
    });
    if ($wolnyZ === false) pf_odpowiedz(false, 403, ['blad' => 'znacznik']);
    $zwolnij = function () use ($sZ) { pf_z_limitem('zuzyte.json', function (&$d) use ($sZ) { unset($d[$sZ]); return true; }); };
    $glob = pf_z_limitem('globalny.json', function (&$d) use ($teraz) {
        $d = array_values(array_filter((array) $d, function ($t) use ($teraz) { return (int) $t > $teraz - 86400; }));
        $h = count(array_filter($d, function ($t) use ($teraz) { return (int) $t > $teraz - 3600; }));
        if ($h >= PF_LIMIT_GLOBALNY_H || count($d) >= PF_LIMIT_GLOBALNY_D) return false;
        $d[] = $teraz; return true;
    });
    if ($glob === false) { pf_dziennik('łączny limit przekroczony'); $zwolnij(); pf_odpowiedz(false, 429, ['blad' => 'globalny']); }

    // wiadomość do działu
    $kiedy = date('d.m.Y, H:i');
    $tab = '';
    foreach ($wiersze as $w) {
        $tab .= '<tr><td style="padding:10px 20px;border-bottom:1px solid #ECEAE4;font-family:Arial,Helvetica,sans-serif">'
              . '<div style="font-size:12px;color:#6B6F73;margin:0 0 3px">' . pf_h($w[0]) . '</div>'
              . '<div style="font-size:15px;line-height:1.5;color:#0F1D2B;word-break:break-word">' . nl2br(pf_h($w[1])) . '</div></td></tr>';
    }
    $html = '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' . pf_h($temat) . '</title></head>'
        . '<body style="margin:0;padding:0;background:#F3F3F0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="padding:14px 8px">'
        . '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#FFFFFF;border-radius:8px;overflow:hidden">'
        . '<tr><td style="padding:16px 20px;background:#0F1D2B;border-bottom:3px solid #8A6A2E;font:bold 17px/1.35 Arial,Helvetica,sans-serif;color:#FFFFFF">' . pf_h($temat) . '</td></tr>'
        . $tab
        . '<tr><td style="padding:12px 20px 16px;font:13px/1.5 Arial,Helvetica,sans-serif;color:#6B6F73">Wysłano ' . pf_h($kiedy) . ' z formularza na potockidwor.pl'
        . ($okMail ? '. Odpowiedz na tę wiadomość, żeby napisać do klienta (' . pf_h($email) . ').' : '. Klient nie podał e-maila - prosimy o kontakt telefoniczny.') . '</td></tr>'
        . '</table></td></tr></table></body></html>';
    $tekst = $temat . "\n\n";
    foreach ($wiersze as $w) $tekst .= $w[0] . ': ' . $w[1] . "\n";
    $tekst .= "\nWysłano: " . $kiedy . " (formularz potockidwor.pl)\n";
    $g = '=_pd_' . bin2hex(random_bytes(10));
    $tresc = '--' . $g . PF_NL . 'Content-Type: text/plain; charset=UTF-8' . PF_NL . 'Content-Transfer-Encoding: base64' . PF_NL . PF_NL . pf_b64($tekst)
           . '--' . $g . PF_NL . 'Content-Type: text/html; charset=UTF-8' . PF_NL . 'Content-Transfer-Encoding: base64' . PF_NL . PF_NL . pf_b64($html)
           . '--' . $g . '--' . PF_NL;
    $nag = [];
    if ($okMail) $nag[] = 'Reply-To: ' . $email;
    if (!pf_wyslij(PF_ODBIORCY[$rodzaj], $temat, $nag, 'Content-Type: multipart/alternative; boundary="' . $g . '"', $tresc)) {
        pf_dziennik('mail() zwrócił false'); $zwolnij(); pf_odpowiedz(false, 500, ['blad' => 'mail']);
    }
    pf_odpowiedz(true, 200);
}

pf_obsluz();
