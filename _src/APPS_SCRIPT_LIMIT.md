# Apps Script "Potocki - zajetosc sal": limit zapytan i pulapka na boty

Projekt: Apps Script na koncie odrobimy@gmail.com (u/2), web app "wykonaj jako ja, dostep: kazdy",
adres w `assets/js/config.js` -> `kalendarz.url`. Fragment do wklejenia przez nas w edytorze Apps Script
(nie jest edytowany automatycznie). Po wklejeniu: Wdrozenie -> Zarzadzaj wdrozeniami -> edytuj -> Nowa wersja
(adres /exec zostaje ten sam, nic nie trzeba zmieniac na stronie).

## Co juz chroni po stronie strony (assets/js/app.js, 05.11.2026)

- jedno zapytanie na wizyte: zajetosc na 12 miesiecy przychodzi naraz, zmiana miesiaca i daty nie wysyla zapytan,
- wynik w `sessionStorage` na 10 minut (przejscia miedzy podstronami bez zapytan),
- pobranie dopiero, gdy planer jest blisko ekranu (IntersectionObserver), nigdy dwa zapytania naraz, limit czasu 10 s,
- po bledzie ponowienie tylko przy zmianie daty (debounce 600 ms), najwyzej 2 razy na wizyte.

Strona nie chroni przed kims, kto wola adres /exec skryptem. Do tego sluzy limit ponizej.

## Ograniczenie Apps Script

Web app nie widzi adresu IP odwiedzajacego, wiec limit "na IP" nie jest mozliwy po stronie Google.
Stosujemy dwa poziomy:

1. limit globalny: maks. 30 obliczen na minute i 3000 na dobe (CacheService), powyzej - odpowiedz z pamieci podrecznej
   albo `{"zajete":{},"limit":true}` (planer dziala wtedy bez przekreslen, zapytanie i tak trafia do managera),
2. limit na klucz klienta: strona moze wysylac `?k=<losowy identyfikator z sessionStorage>`; 30 zapytan na minute
   na skrot tego klucza (klucz da sie podrobic, wiec to tylko dodatkowe zabezpieczenie; glowny jest limit globalny i cache).

Najwazniejsze: odpowiedz jest liczona z Kalendarza najwyzej raz na 10 minut (cache), wiec nawet zalew zapytan
nie wyczerpie limitow Calendar API - kosztuje tylko czas wykonania skryptu.

```javascript
/* ---------- limit zapytan (wkleic nad istniejaca funkcja doGet) ---------- */
var LIMIT_MIN = 30;        // obliczen na minute (globalnie)
var LIMIT_DOBA = 3000;     // obliczen na dobe (globalnie)
var LIMIT_KLUCZ_MIN = 30;  // zapytan na minute na klucz klienta

function przekroczony_(nazwa, limit, ttl) {
  var c = CacheService.getScriptCache();
  var lock = LockService.getScriptLock();
  try { lock.waitLock(2000); } catch (e) { return false; }  // brak blokady = nie blokujemy uzytkownika
  try {
    var n = Number(c.get(nazwa) || 0) + 1;
    c.put(nazwa, String(n), ttl);
    return n > limit;
  } finally { lock.releaseLock(); }
}

function skrot_(t) {
  var b = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, 'potocki|' + t);
  return b.slice(0, 8).map(function (x) { return ((x + 256) % 256).toString(16); }).join('');
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  var c = CacheService.getScriptCache();

  // pulapka: prawdziwa strona nigdy nie wysyla parametru "www"; boty wypelniajace wszystko - pusta odpowiedz
  if (p.www) return json_({ zajete: {} });

  // gotowy wynik z pamieci (10 min) - bez liczenia i bez limitu
  var gotowe = c.get('zajetosc_json');
  if (gotowe) return ContentService.createTextOutput(gotowe).setMimeType(ContentService.MimeType.JSON);

  var minuta = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyyMMddHHmm');
  var doba = minuta.slice(0, 8);
  var klucz = String(p.k || '').slice(0, 64);
  if (klucz && przekroczony_('k_' + skrot_(klucz) + '_' + minuta, LIMIT_KLUCZ_MIN, 120)) return json_({ zajete: {}, limit: true });
  if (przekroczony_('g_' + minuta, LIMIT_MIN, 120) || przekroczony_('d_' + doba, LIMIT_DOBA, 21600)) return json_({ zajete: {}, limit: true });

  var wynik = JSON.stringify({ zajete: policzZajetosc() });   // dotychczasowa funkcja (Calendar.Freebusy na 12 mies.)
  c.put('zajetosc_json', wynik, 600);                           // 10 min, jak dotad
  return ContentService.createTextOutput(wynik).setMimeType(ContentService.MimeType.JSON);
}
```

`policzZajetosc()` = obecna logika z dotychczasowego `doGet` (Freebusy dla "Sala Balowa" i "Sala Bankietowa",
zwraca `{ "2026-11-14": ["balowa"], ... }`). Jesli obecny `doGet` ma juz wlasny cache, nalezy zostawic jeden (ten powyzej).

## Gdyby skrypt kiedys przyjmowal zapytania z formularza (doPost)

Dzis formularze ida przez `wyslij.php` na serwerze strony, nie przez Apps Script. Gdyby to sie zmienilo:

```javascript
function doPost(e) {
  var p = (e && e.parameter) || {};
  if (p._honey) return json_({ success: true });                       // bot: udajemy sukces, nic nie wysylamy
  var t = Number(p._t || 0);                                           // czas wyswietlenia formularza (ms) z przegladarki
  if (!t || Date.now() - t < 3000) return json_({ success: false, blad: 'szybko' });
  var minuta = Utilities.formatDate(new Date(), 'Europe/Warsaw', 'yyyyMMddHHmm');
  if (przekroczony_('post_' + minuta, 10, 120) || przekroczony_('post_d_' + minuta.slice(0, 8), 100, 21600)) {
    return json_({ success: false, blad: 'limit' });
  }
  // odbiorca STALY w kodzie, z formularza tylko Reply-To - skryptu nie da sie uzyc do wysylki na dowolny adres
  // MailApp.sendEmail({ to: 'k.wieczorek@potockidwor.pl', subject: ..., body: ..., replyTo: p.email });
  return json_({ success: true });
}
```

Opcjonalnie po stronie strony: dopisac do `kalendarz.url` parametr `k` (losowy identyfikator zapisany w sessionStorage),
wtedy zadziala tez limit na klucz. Bez tego dziala limit globalny i cache 10 min.
