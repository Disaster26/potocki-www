/* Karta menu Potocki Dwór - przepisana z Menu_Potocki__final_dodruku.docx (źródło nadrzędne, 22.10.2026;
   zgodne 1:1 z Menu_Potocki_01..09.jpg) oraz Karta_drinkow_Potocki_A4.pdf (drinki). Kolejność jak w karcie. Jedyne źródło menu na stronie.
   W WordPressie: kategorie = taksonomia / grupa pól, pozycje = pola powtarzalne
   (nazwa, sklad, cena, zdjecie). Ceny w zł, tekst dokładnie jak w karcie.
   Pola: n - nazwa, s - skład / opis z gramaturą, c - cena, img - zdjęcie (assets/img/<img>-400.webp i -1200.webp) */
window.POTOCKI_MENU = [
  { id: 'przystawki', nazwa: 'Przystawki', pozycje: [
    { n: 'Tatar wołowy Potocki', s: 'polędwica 120 g | dodatki 163 g: majonez lubczykowy, musztarda francuska, żółtko, ogórek, czerwona cebula, chips, włoskie chlebki', c: '52 zł', img: 'd-tatar' },
    { n: 'Krewetki w sosie maślano-winnym', s: 'krewetki 120 g | dodatki 185 g: sos maślano-winny, pomidorki koktajlowe, włoskie chlebki', c: '48 zł' },
    { n: 'Gruszka, kozi ser i burak', s: 'marynowana gruszka, burak, kozi ser, granat, pistacje, dressing, 295 g', c: '42 zł', img: 'd-gruszka' }
  ]},
  { id: 'zupy', nazwa: 'Zupy', pozycje: [
    { n: 'Tradycyjny rosół Potocki', s: 'rosół 300 ml | dodatki 90 g: domowy makaron, warzywa i zioła', c: '20 zł' },
    { n: 'Krem pomidorowy po włosku', s: 'krem pomidorowy 300 ml | dodatki 65 g: kozi ser, grissini, oliwa bazyliowa', c: '27 zł', img: 'd-krem-pomidorowy' },
    { n: 'Żurek Potocki', s: 'żurek 280 ml | dodatki 263 g: purée ziemniaczane, jajko gotowane, pulpeciki z białej kiełbasy, boczek, puder grzybowy', c: '32 zł' },
    { n: 'Flaki z boczniaków', s: 'wywar warzywny 300 ml | dodatki 240 g: boczniaki, warzywa, domowy chleb', c: '29 zł', img: 'd-flaki' }
  ]},
  { id: 'salatki', nazwa: 'Sałatki', pozycje: [
    { n: 'Cezar Potocki', s: 'grillowany kurczak 150 g lub krewetki 120 g | dodatki 265 g: grillowana sałata rzymska, sos Cezar, włoskie chlebki, boczek, parmezan', c: '42 / 47 zł' },
    { n: 'Ośmiornica Mediterranea', s: 'marynowana ośmiornica 130 g, mieszanka sałat, warzywa, filety z pomarańczy, oliwki, orzechy, włoskie chlebki', c: '59 zł', img: 'd-osmiornica' },
    { n: 'Dynia & Gorgonzola', s: 'marynowana dynia 120 g, mieszanka sałat, pomidorki koktajlowe, gorgonzola, czerwona cebula, mieszanka ziaren, ogórek, figa, winegret, włoskie chlebki', c: '46 zł', img: 'd-dynia' }
  ]},
  { id: 'steki', nazwa: 'Steki', pozycje: [
    { n: 'Ribeye - antrykot wołowy', s: 'antrykot wołowy 200 g, dodatek do wyboru, sos do wyboru 50 g', c: '109 zł', img: 'd-stek-rostbef' },
    { n: 'Polędwica wołowa', s: 'polędwica wołowa 200 g, dodatek do wyboru, sos do wyboru 50 g', c: '115 zł', img: 'd-poledwica' },
    { n: 'Dodatki do wyboru', s: 'purée truflowe 150 g lub frytki stekowe 150 g lub warzywa grillowane 100 g + mieszanka sałat 100 g', c: '' },
    { n: 'Sosy do wyboru', s: 'gorgonzola 50 g, sos winny 50 g, chimichurri 50 g', c: '' }
  ]},
  { id: 'glowne', nazwa: 'Dania główne', pozycje: [
    { n: 'Kurczak Verde', s: 'kurczak supreme 180 g | dodatki 310 g: purée z groszku, dziki brokuł, groszek cukrowy, kukurydza', c: '62 zł', img: 'd-kurczak-verde' },
    { n: 'Pierś z kaczki Potocki', s: 'pierś z kaczki 180 g | dodatki 300 g: gnocchi z kozim serem, sos z czarnej porzeczki, dziki brokuł, karmelizowana marchew', c: '69 zł', img: 'd-kaczka' },
    { n: 'Schabowy Potocki z jajkiem', s: 'schab 180 g | dodatki 355 g: jajko sadzone, purée ziemniaczane, kapusta zasmażana', c: '48 zł' },
    { n: 'Gicz jagnięca', s: 'gicz jagnięca 300 g | dodatki 360 g: purée śmietanowe, sos własny, salsa ratatouille', c: '95 zł', img: 'd-gicz' }
  ]},
  { id: 'makarony', nazwa: 'Makarony i risotto', pozycje: [
    { n: 'Tagliatelle Tartufo', s: 'tagliatelle 200 g | kurczak 150 g | dodatki 115 g: sos śmietanowo-truflowy, Parmigiano Reggiano', c: '48 zł', img: 'd-tagliatelle-tartufo' },
    { n: 'Spaghetti Gamberi', s: 'spaghetti 200 g | krewetki 120 g | dodatki 180 g: sos maślano-winny, pomidorki koktajlowe', c: '56 zł', img: 'd-spaghetti-gamberi' },
    { n: 'Tagliatelle Salmone', s: 'tagliatelle 200 g | pieczony łosoś 120 g | dodatki 245 g: szpinak, pomidorki koktajlowe, kremowy sos, cytryna', c: '62 zł', img: 'd-tagliatelle-salmone' },
    { n: 'Risotto Bosco', s: 'ryż arborio, grzyby, Parmigiano Reggiano, prażone orzechy, oliwa truflowa, 413 g', c: '44 zł', img: 'd-risotto' }
  ]},
  { id: 'ryby', nazwa: 'Ryby i owoce morza', pozycje: [
    { n: 'Dorada Mediterranea', s: 'dorada 350-400 g | dodatki 280 g: ziemniaki opiekane, grillowana sałata rzymska', c: '68 zł', img: 'd-dorada' },
    { n: 'Łosoś Zafferano', s: 'łosoś 180 g | dodatki 240 g: risotto szafranowe, szpinak, sos imbirowy', c: '72 zł', img: 'd-losos' },
    { n: 'Talerz owoców morza', s: 'mule, ośmiornica, krewetki, kalmary, sos maślano-winny, cebulka, czosnek, pietruszka, limonka, pieczywo, 450 g', c: '85 zł', img: 'd-owoce-morza' }
  ]},
  { id: 'desery', nazwa: 'Desery', pozycje: [
    { n: 'Tiramisù Tropicale', s: 'krem mascarpone, mango, marakuja, biszkopt, biała czekolada, 230 g', c: '26 zł', img: 'd-tiramisu' },
    { n: 'Affogato Pistacchio', s: 'lody pistacjowe, espresso, pistacje, 110 g / 30 ml', c: '26 zł' },
    { n: 'Szarlotka Potocki', s: 'szarlotka, lody waniliowe, słony karmel, kruszonka, 260 g', c: '26 zł' }
  ]},
  { id: 'kanapki', nazwa: 'Włoskie kanapki', pozycje: [
    { n: 'Panuozzo Pollo Napoli', s: 'mozzarella, salami łagodne, kurczak grillowany w sosie mango, mieszanka sałat, pomidorki koktajlowe, sos czosnkowo-jogurtowy, 550-600 g', c: '45 zł' },
    { n: 'Panuozzo Pollo Piccante', s: 'mozzarella, salami pikantne, kurczak grillowany w sosie mango, mieszanka sałat, pomidorki koktajlowe, sos czosnkowo-jogurtowy, 550-600 g', c: '45 zł' },
    { n: 'Bruschetta Potocki', s: 'stracciatella, pomidorki koktajlowe, rukola, pesto bazyliowe, 360 g', c: '28 zł' }
  ]},
  { id: 'pizza', nazwa: 'Pizza', pozycje: [
    { n: 'Pizza Margherita', s: 'sos pomidorowy, ser mozzarella, bazylia, Grana Padano', c: '29 zł' },
    { n: 'Pizza Wegetariańska', s: 'sos pomidorowy, ser mozzarella, grillowana cukinia, grillowana papryka, suszone pomidory, oliwki czarne, Grana Padano', c: '38 zł' },
    { n: 'Pizza Cztery Sery', s: 'sos pomidorowy, ser mozzarella, ser gorgonzola, ser fontal, Grana Padano', c: '37 zł' },
    { n: 'Pizza Pollo', s: 'sos pomidorowy, ser mozzarella, grillowany kurczak, kukurydza, suszone pomidory, Grana Padano', c: '44 zł' },
    { n: 'Pizza Capricciosa', s: 'sos pomidorowy, ser mozzarella, gotowana szynka cotto, oregano, pieczarki, Grana Padano', c: '41 zł' },
    { n: 'Pizza Chorizo', s: 'sos pomidorowy, ser mozzarella, chorizo, ser gorgonzola, papryczka jalapeño, Grana Padano', c: '43 zł' },
    { n: 'Pizza Pepperoni', s: 'sos pomidorowy, ser mozzarella, salami pikantne, czerwona cebula, czosnek, Grana Padano', c: '44 zł' },
    { n: 'Pizza Salami Łagodne', s: 'sos pomidorowy, ser mozzarella, salami łagodne, ser gorgonzola, Grana Padano', c: '43 zł' },
    { n: 'Pizza Salami Ostre', s: 'sos pomidorowy, ser mozzarella, salami pikantne, ser gorgonzola, Grana Padano', c: '44 zł' },
    { n: 'Pizza Pancetta', s: 'sos pomidorowy, ser mozzarella, ser fontal, boczek pancetta, ser Grana Padano', c: '43 zł' },
    { n: 'Pizza Tre Gusti', s: 'sos pomidorowy, ser mozzarella, boczek pancetta, grillowany kurczak, salami łagodne, ser Grana Padano', c: '45 zł' },
    { n: 'Pizza Crudo', s: 'sos pomidorowy, ser mozzarella, szynka parmeńska, pomidorki koktajlowe, rukola, ser Grana Padano', c: '45 zł' }
  ]},
  { id: 'klasyka', nazwa: 'Klasyka Potockiego Dworu', pozycje: [
    { n: 'Policzek wołowy', s: 'policzek wołowy 200 g | dodatki 250 g: purée chrzanowe, czerwona kapusta', c: '69 zł' },
    { n: 'Marynowane żeberko', s: 'marynowane żeberko 390 g | dodatki 270 g: pieczone ziemniaki, mieszanka sałat', c: '62 zł' },
    { n: 'Golonka w ciemnym piwie', s: 'golonka 550 g, ziemniaki opiekane, kiszonki, chrzan, musztarda', c: '66 zł' }
  ]},
  { id: 'pierogi', nazwa: 'Pierogi', pozycje: [
    { grupa: 'Pierogi wytrawne', uwaga: 'Porcja: 8 sztuk, pielmieni: 16 sztuk' },
    { n: 'Pierogi ukraińskie', s: '', c: '24 zł' },
    { n: 'Pierogi ze szpinakiem i serem ricotta', s: '', c: '24 zł' },
    { n: 'Pierogi z cielęciną', s: '', c: '36 zł' },
    { n: 'Pielmieni (16 sztuk)', s: '', c: '28 zł' },
    { n: 'Pierogi z mięsem', s: '', c: '26 zł' },
    { grupa: 'Dodatki do pierogów wytrawnych' },
    { n: 'Kwaśna śmietana', s: '', c: '3 zł' },
    { n: 'Boczek smażony', s: '', c: '4 zł' },
    { n: 'Zasmażana cebulka', s: '', c: '3 zł' },
    { n: 'Sos grzybowy', s: '', c: '4 zł' },
    { grupa: 'Pierogi na słodko', uwaga: 'Porcja: 8 sztuk' },
    { n: 'Pierogi z twarogiem', s: '', c: '24 zł' },
    { n: 'Pierogi z wiśnią', s: '', c: '24 zł' },
    { n: 'Pierogi z truskawkami', s: '', c: '24 zł' },
    { grupa: 'Dodatki do pierogów na słodko' },
    { n: 'Śmietana na słodko', s: '', c: '4 zł' },
    { n: 'Sos z owoców leśnych', s: '', c: '3 zł' }
  ]},
  { id: 'dzieci', nazwa: 'Menu dla dzieci', pozycje: [
    { n: 'Zupa pomidorowa z makaronem', s: 'zupa pomidorowa z makaronem 250 ml', c: '18 zł' },
    { n: 'Nuggetsy z frytkami i marchewką', s: 'nuggetsy 150 g, frytki i marchewka 200 g', c: '28 zł' },
    { n: 'Spaghetti w sosie pomidorowym z parmezanem', s: 'spaghetti, sos pomidorowy, parmezan, 250 g', c: '24 zł' },
    { n: 'Pancakes z polewami', s: '3 pancakes, polewy', c: '20 zł' },
    { n: 'Lody', s: '2 gałki do wyboru - zapytaj obsługę o smaki', c: '16 zł' }
  ]},
  { id: 'napoje', nazwa: 'Napoje', pozycje: [
    { grupa: 'Napoje zimne' },
    { n: 'Coca-Cola, Coca-Cola Zero, Fanta, Sprite 0,25 l', s: '', c: '9 zł' },
    { n: 'Kropla Beskidu gazowana / niegazowana 0,25 l', s: '', c: '8 zł' },
    { n: 'Sok Cappy - jabłko/pomarańcza/multiwitamina 0,25 l', s: '', c: '9 zł' },
    { n: 'Domowa lemoniada cytrynowa 300 ml / 700 ml', s: '', c: '16 / 23 zł' },
    { n: 'Tonic Kinley 0,25 l', s: '', c: '9 zł' },
    { grupa: 'Napoje gorące' },
    { n: 'Espresso', s: '', c: '7 zł' },
    { n: 'Espresso Doppio', s: '', c: '9 zł' },
    { n: 'Kawa czarna', s: '', c: '9 zł' },
    { n: 'Kawa biała', s: '', c: '10 zł' },
    { n: 'Cappuccino', s: '', c: '12 zł' },
    { n: 'Kawa Latte', s: '', c: '14 zł' },
    { n: 'Herbata Richmont', s: '', c: '12 zł' }
  ]},
  { id: 'piwo', nazwa: 'Piwo', pozycje: [
    { n: 'Heineken 0,5 l', s: '', c: '13 zł' },
    { n: 'Heineken 0% 0,5 l', s: '', c: '14 zł' },
    { n: 'Żywiec Biały 0% 0,5 l', s: '', c: '14 zł' },
    { n: 'Złoto Kurozwęk 0,5 l', s: 'Kraftowe piwo typu jasny pils', c: '20 zł' },
    { n: 'Pan Paweł 0,5 l', s: 'Kraftowe piwo marcowe', c: '20 zł' },
    { n: 'Czas 0,5 l', s: 'Kraftowe piwo IPA', c: '20 zł' },
    { n: 'Sarmata 0,5 l', s: 'Kraftowe piwo typu czerwony dunkiel', c: '20 zł' },
    { n: 'Biały Bizon 0,5 l', s: 'Kraftowe piwo pszeniczne', c: '20 zł' },
    { n: 'Pani Karen 0,5 l', s: 'Kraftowe piwo typu witbier różane', c: '20 zł' },
    { n: 'Pan Staszek FREE 0% 0,5 l', s: 'Kraftowe piwo bezalkoholowe jasne mango i marakuja', c: '20 zł' }
  ]},
  { id: 'drinki', nazwa: 'Drinki', zdjecia: ['drink-01','drink-03','drink-04','drink-06','drink-08','drink-09'], pozycje: [
    { n: 'Aperol Spritz', s: 'Prosecco, aperol, woda gazowana, plaster pomarańczy, lód', c: '30 zł' },
    { n: 'Mojito', s: 'rum, limonka, mięta, cukier, woda gazowana, lód', c: '28 zł' },
    { n: 'Mojito Pear', s: 'rum, limonka, mięta, cukier, syrop z gruszki, lód', c: '28 zł' },
    { n: 'Moscow Mule', s: 'wódka, sok z cytryny, piwo imbirowe, lód', c: '32 zł' },
    { n: 'Whisky Sour', s: 'whisky, sok z cytryny, syrop cukrowy, białko jajka, angostura', c: '32 zł' },
    { n: 'Pornstar Martini', s: 'wódka infuzowana wanilią, puree z marakui, passoa, syrop waniliowy, sok z cytryny, prosecco', c: '35 zł' },
    { n: 'Baileys Coffee', s: 'baileys, rum, mleko, likier kokosowy, krem kokosowy', c: '31 zł' },
    { n: 'G&T', s: 'gin, tonic, ogórek, lód', c: '25 zł' },
    { n: 'Raspberry Daiquiri', s: 'rum, sok z cytryny, puree z malin, syrop malinowy', c: '26 zł' },
    { n: 'Lillet Rosé Tonic', s: 'Lillet Rosé, różowy tonic, syrop różany, lód', c: '38 zł' },
    { n: 'Negroni Sour', s: 'gin, campari, wermut, sok z cytryny, syrop cukrowy, białko jajka', c: '34 zł' },
    { n: 'A&G Sour', s: 'aperol, gin, sok z cytryny, syrop cukrowy, białko jajka', c: '32 zł' },
    { n: 'Hugo Spritz', s: 'prosecco, syrop z czarnego bzu, mięta, limonka, woda gazowana, lód', c: '28 zł' },
    { n: 'Passion Fruit Spritz', s: 'prosecco, passoa, syrop z marakui, mięta, lód', c: '28 zł' },
    { n: 'Blueberry Collins', s: 'gin, syrop jagodowy, sok z cytryny, lód', c: '34 zł' },
    { n: 'Flower’s Spritz', s: 'prosecco, Lillet Rosé, syrop lawendowy, sok z cytryny, lód', c: '35 zł' },
    { n: 'Jäger Ginger', s: 'likier Jägermeister, syrop z trawy cytrynowej, sok z cytryny, piwo imbirowe, lód', c: '36 zł' },
    { n: 'French 95', s: 'whisky, sok z cytryny, sok z pomarańczy, syrop cukrowy, prosecco, lód', c: '34 zł' },
    { n: 'Manhattan', s: 'Bourbon, wermut, angostura, lód', c: '26 zł' }
  ]}
];
