/* Ustawienia strony Potocki Dwór. W WordPressie: strona opcji w panelu (ACF Options).
   Puste pola = funkcja wyłączona, strona działa w trybie zastępczym. */
window.POTOCKI_CONFIG = {
  /* Telefon i e-mail ogólny - z obecnej strony potockidwor.pl */
  telefon: '+48798033101',
  telefonTekst: '798 033 101',
  email: 'recepcja@potockidwor.pl',

  /* Adresy formularzy (klient 22.10): przyjęcia -> k.wieczorek@, biznes -> m.pronobis@.
     Puste = e-mail ogólny powyżej (hotel, kontakt - DO POTWIERDZENIA). */
  emaileFormularzy: { przyjecia: 'k.wieczorek@potockidwor.pl', hotel: '', biznes: 'm.pronobis@potockidwor.pl', kontakt: '' },

  /* DO UZUPEŁNIENIA (klient): Kalendarz Google "Rezerwacje sal" - zajętość dla planera przyjęć.
     url: publiczny adres iCal (.ics) albo JSON. Kalendarz Google nie pozwala czytać pliku .ics
     bezpośrednio z przeglądarki (CORS), dlatego w WordPressie adres będzie pobierany po stronie serwera
     (np. /wp-json/potocki/v1/zajetosc) i oddawany jako JSON:
       { "zajete": { "2026-11-14": ["*"], "2026-11-21": ["balowa"] } }
     "*" = zajęte wszystkie sale; inaczej identyfikatory sal: balowa, bankietowa, restauracyjna, patio.
     Z wydarzeń brana jest tylko data (i ewentualnie nazwa sali), bez treści. */
  kalendarz: { url: '', format: 'json' },

  /* Kod modułu rezerwacji KW Hotel PRO (HTML/skrypt od dostawcy) albo link - klient doda później, na razie formularz zapytania. */
  kwHotel: { kod: '', link: '' },

  /* Pomiar - konta należą do klienta. Po wpisaniu identyfikatorów pojawi się baner zgód (Consent Mode v2). */
  ga4: '',        /* np. G-XXXXXXXXXX */
  metaPixel: '',  /* np. 123456789012345 */

  social: { facebook: 'https://www.facebook.com/PotockiDwor', instagram: 'https://www.instagram.com/potocki_dwor/' },

  /* DO UZUPEŁNIENIA (klient): "Gościli u nas" na podstronie Dla biznesu.
     Pozycja: { firma: 'Nazwa', logo: 'assets/img/goscili/firma.png', opinia: 'Krótka opinia.' } */
  goscili: []
};
