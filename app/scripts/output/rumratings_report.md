# RumRatings × naš indeks

Automatski izvještaj (`scripts/compare-rumratings.py`). Ocjene zajednice su
mišljenje druge publike na drugoj skali — zato se gleda i sirova razlika i
razlika u *rangu* unutar svake liste.


## 1. Koliko se poklapamo

- Boca u našem indeksu: **320**
- Boca s RumRatingsa (≥ 25 glasova): **103** od 160 skinutih
- Spojeno po imenu: **102**
- Spearman (poklapanje redoslijeda): **0.518**
- Prosječna apsolutna razlika: **0.93** boda; sustavni pomak (mi − oni): **-0.18**
- Unutar ±0,5 boda: **36** / 102
- Isti rang (±20 percentila): **52** / 102

## 2. Gdje se ne slažemo


### Mi hvalimo više nego zajednica (Δ ≥ 1.2)

| Boca | naša | zajednica | Δ | glasova |
| --- | ---: | ---: | ---: | ---: |
| Clément VSOP (agricole) | 8.5 | 6.6 | +1.90 | 229 |
| Saint James XO (agricole) | 8.4 | 6.5 | +1.90 | 26 |
| Havana Club 7 Anos | 8 | 6.5 | +1.50 | 1140 |
| Eminente Reserva 7 | 8.5 | 7.1 | +1.40 | 65 |
| Hampden Estate 8 YO | 9 | 7.7 | +1.30 | 177 |
| Worthy Park 109 | 7.8 | 6.6 | +1.20 | 79 |
| HSE Black Sheriff | 7.9 | 6.7 | +1.20 | 54 |

### Zajednica hvali više nego mi (Δ ≤ −1.2)

| Boca | naša | zajednica | Δ | glasova |
| --- | ---: | ---: | ---: | ---: |
| Ron Centenario 30 | 5.5 | 8.9 | -3.40 | 202 |
| Ron Centenario 1985 (20 YO) | 5 | 8.2 | -3.20 | 395 |
| Barcelo Gran Anejo | 4 | 6.1 | -2.10 | 261 |
| A.H. Riise Non Plus Ultra Black Edition | 6.2 | 8.3 | -2.10 | 114 |
| A.H. Riise XO Reserve 175 Years Anniversary | 5.5 | 7.6 | -2.10 | 79 |
| A.H. Riise Family Reserve Solera 1838 | 5.5 | 7.4 | -1.90 | 107 |
| A.H. Riise XO Royal Reserve Kong Haakon | 5.5 | 7.4 | -1.90 | 37 |
| A.H. Riise 1888 Copenhagen Gold Medal | 5.5 | 7.3 | -1.80 | 127 |
| A.H. Riise Black Barrel Navy Spiced | 5 | 6.7 | -1.70 | 64 |
| Chairman's Reserve Spiced Original | 5.5 | 7.2 | -1.70 | 220 |
| A.H. Riise Non Plus Ultra Very Rare | 6.2 | 7.8 | -1.60 | 210 |
| A.H. Riise Royal Danish Navy Naval Cadet | 5.5 | 7.1 | -1.60 | 29 |
| A.H. Riise XO Reserve Christmas Limited | 5.5 | 7.1 | -1.60 | 88 |
| Zacapa Centenario 23 | 7 | 8.5 | -1.50 | 77 |
| Remedy Spiced | 4.5 | 6.0 | -1.50 | 50 |
| A.H. Riise Non Plus Ultra Ambre d'Or | 6 | 7.5 | -1.50 | 42 |
| A.H. Riise Royal Danish Navy | 5.5 | 7.0 | -1.50 | 163 |
| A.H. Riise XO Reserve Superior Cask | 5.5 | 7.0 | -1.50 | 181 |
| Captain Morgan Spiced/White/Black | 4.5 | 5.9 | -1.40 | 359 |
| Ron Millonario 15 Reserva Especial | 6.5 | 7.8 | -1.30 | 461 |
| Barcelo Blanco | 4 | 5.3 | -1.30 | 26 |
| Foursquare Spiced Rum | 5.5 | 6.7 | -1.20 | 115 |
| Opthimus 25 Malt Whisky Finish | 7.8 | 9.0 | -1.20 | 69 |
| A.H. Riise Royal Danish Navy Frogman | 5.8 | 7.0 | -1.20 | 51 |
| A.H. Riise XO Reserve Port Cask | 5.5 | 6.7 | -1.20 | 51 |

> Razlika sama po sebi nije greška: naša ocjena je *unutar stila* i ne kažnjava
> aditive, a zajednica voli slađe profile. Provjeri redom one gdje se **i rang**
> razilazi — to su kandidati za rekalibraciju, ne pojedinačni bodovi.


### Razilaženje u rangu (|Δ percentila| ≥ 0.25)

| Boca | naš percentil | njihov | Δ |
| --- | ---: | ---: | ---: |
| Ron Centenario 30 | 0.17 | 0.99 | -0.82 |
| Ron Centenario 1985 (20 YO) | 0.10 | 0.87 | -0.77 |
| A.H. Riise Non Plus Ultra Black Edition | 0.28 | 0.90 | -0.62 |
| A.H. Riise XO Reserve 175 Years Anniversary | 0.17 | 0.73 | -0.56 |
| Saint James XO (agricole) | 0.79 | 0.25 | +0.54 |
| Clément VSOP (agricole) | 0.83 | 0.32 | +0.51 |
| Zacapa Centenario 23 | 0.42 | 0.93 | -0.51 |
| A.H. Riise Non Plus Ultra Very Rare | 0.28 | 0.77 | -0.49 |
| A.H. Riise Family Reserve Solera 1838 | 0.17 | 0.65 | -0.48 |
| A.H. Riise XO Royal Reserve Kong Haakon | 0.17 | 0.65 | -0.48 |
| A.H. Riise Non Plus Ultra Ambre d'Or | 0.25 | 0.70 | -0.45 |
| Ron Millonario 15 Reserva Especial | 0.33 | 0.77 | -0.45 |
| A.H. Riise 1888 Copenhagen Gold Medal | 0.17 | 0.60 | -0.44 |
| Havana Club 7 Anos | 0.68 | 0.25 | +0.43 |
| Chairman's Reserve Spiced Original | 0.17 | 0.57 | -0.40 |
| Opthimus 25 Malt Whisky Finish | 0.61 | 1.00 | -0.38 |
| Zafra Master Reserve 21 | 0.54 | 0.90 | -0.36 |
| A.H. Riise Royal Danish Navy Naval Cadet | 0.17 | 0.53 | -0.36 |
| A.H. Riise XO Reserve Christmas Limited | 0.17 | 0.53 | -0.36 |
| Kirk and Sweeney 18 Reserva | 0.42 | 0.08 | +0.33 |
| Clément Select Barrel | 0.54 | 0.21 | +0.33 |
| Barcelo Imperial Onyx | 0.33 | 0.65 | -0.32 |
| A.H. Riise Royal Danish Navy | 0.17 | 0.49 | -0.32 |
| A.H. Riise XO Reserve Superior Cask | 0.17 | 0.49 | -0.32 |
| Eminente Reserva 7 | 0.83 | 0.53 | +0.30 |

## 3. Boce koje nemamo, a zajednica ih drži visoko

| Boca | ocjena | glasova | link |
| --- | ---: | ---: | --- |

Kandidati za `rums.json` — provjeri dostupnost u HR prije unosa (`shopHR`).


## 4. Materijal za Club — priče i zanimljivosti (58 boca)

**Izvorni citati, za uredničku preradu — ne kopirati doslovno u `club.json`.**


### Foursquare Nobiliary (8.8 / 46 gl.) — https://rumratings.com/rum/11343-foursquare-2005-nobiliary-14-year
- I have been unimpressed by this distillery.
- A blend of pot and column still, I expect this one to be balanced.
- NR: Balanced Foursquare, good blend of pot and column still

### Foursquare Sagacity (8.7 / 90 gl.) — https://rumratings.com/rum/11549-foursquare-2007-sagacity-12-year
- Awfully good rum, totally recognizable with the Foursquare distillery.
- It consists of a blend from both Pot and Coffey stills distillate aged for twelve years in ex-Bourbon and ex-Madeira casks before blended at ABV 48%.
- We have a blend of pot and coffey still that has been matured in ex-bourbon barrels for 12 years.

### Hampden Estate 8 YO (7.7 / 177 gl.) — https://rumratings.com/rum/6622-hampden-estate-8-year
- JUNGLE BIRD (23% ABV before shaking) 2½ Hampden pot still (Jamaica 92 proof) ¾ Campari (Italy 48 proof) 1½ pineapple juice (Dole can NFC) ½ lime juice (fresh) ½ demerara syrup 1:1
- Tastes sort of like a blend between agricole (grassy tones) and whisky.
- This rum, together with its overproof brother, marking an historic moment for all rum enthusiasts loving the funky 100% pot still rum from Jamaica.
- However this rum is a piece of history and fully deserves respect.

### Appleton Estate 15 YO Black River Casks (7.8 / 62 gl.) — https://rumratings.com/rum/13170-appleton-estate-black-river-casks-15-year
- Nose: Ripe bananas, molasses, vanilla, and dried apricots Taste: really oaky ,more smooth and complex version of the Appleton 12 year(rare cask), definitely a good sipper but not balanced enough to be great.
- It is a 43% rum named after the Black River, which springs in the Appleton Estate in the Nassau Valley of Jamaica.
- It is on the southwest coast of Jamaica about 20 miles south of the Appleton Estate.
- Back when I visited Jamaica in 1988 and 1996, this part of Jamaica saw no tourism at all.

### Chairman's Reserve 1931 (8.2 / 53 gl.) — https://rumratings.com/rum/7161-chairman-s-reserve-1931-6-12-years
- It’s like some of the former editions a blend of distillates from different stills and some agricole as well.
- It says it’s blended from 14 different distillates, but the one that makes this stand out is the agricole blend.
- Nose: Mostly grassy agricole and brown sugar with a mild wood spice.
- Pot still, column still and some agricole blended into a very well balanced and complex rum that is easy to drink but has a punch.

### Clément VSOP (agricole) (6.6 / 229 gl.) — https://rumratings.com/rum/225-clement-vsop-4-year
- As a first foray into rhum agricole, this proved to be a pleasant surprise as I had read how different agricoles were to molasses-based rums and was expecting something radically different.
- Yes, it is drier than molasses-based rum, with a grassy note and a herbal undercurrent that I just can't place, but it has a pleasant sweetness and complexity.
- Strong, made from pressed sugar cane instead of molasses.
- Molasses nose, wooden barrel maturation apparent in the taste, agricole experience is provided as expected, I prefer a bit less kick in my rums.

### Mount Gay XO (7.8 / 768 gl.) — https://rumratings.com/rum/565-mount-gay-xo-extra-old
- It's impossibly smooth, naturally sweet, full of molasses and toffee, some oak, and a whole lot of perfection.
- Beautiful example of pot still Bajan rum
- Beautiful example of pot still Bajan rum A lesson to most in rum making

### Mount Gay 1703 (8.0 / 137 gl.) — https://rumratings.com/rum/561-mount-gay-1703-old-cask
- Chewy molasses, rich butterscotch, fragrant toffee, a light touch of vanilla and cocoa - this rum has it all.
- Has a slightly medical taste and not the smooth sweet molasses taste of a rum.
- Caramel, pear, molasses, excellence.

### Saint James XO (agricole) (6.5 / 26 gl.) — https://rumratings.com/rum/6182-saint-james-xo-6-year
- If you want to try an agricole rum for the first time, this is a god start.
- The cane juice is totally candied, but also studded with woody tannins, resin and red fruits.Aeration brings a breath of fresh air and the fruits of the orchard shine through, even floral notes with elderflower.
- 43% agricole rum from Martinique made from sugar cane juice.
- Summary: My first encounter with agricole rum.

### Worthy Park 109 (6.6 / 79 gl.) — https://rumratings.com/rum/13127-worthy-park-109
- Nose is reasonably light on the funk scale (but no doubt it is Jamaican), accompanied by a fruit sweetness, oak, alcohol, hints of molasses and maple.
- It's nice and spicy up front, peppery, lightly sweet evolving into a well-balanced woody presentation accented by mild earth, citrus, pineapple, with solid oak, molasses, and a bit of clove in the medium finish.

### Worthy Park Single Estate Reserve (7.6 / 107 gl.) — https://rumratings.com/rum/6464-worthy-park-single-estate-reserve-6-10-years
- The Worthy Park Single Estate Reserva is a molasses blend from Jamaica.
- Single estate means that everything around the 6-10 years old rum stored in bourbon oak barrels, is done in-house.
- The ester content is not specified.
- On the palate, the ester is rather mild.

### Appleton Estate 12 YO Rare Casks (7.8 / 214 gl.) — https://rumratings.com/rum/12087-appleton-estate-rare-casks-12-year
- Thought I would try the new Appleton Estate Reserve 8 Yr & Appleton Rare Casks 12 yr Rums recently released from Jamaica.

### Havana Club 7 Anos (6.5 / 1140 gl.) — https://rumratings.com/rum/436-havana-club-7-year
- It is not completely smooth, but leaves a lingering taste of oak and molasses that makes drinking it memorable.
- It's lovely on the nose giving lots of sweet molasses and noticeable vanilla.
- 15) Havana Club 7YO, Molasses on Copper Lined Column Still.

### Appleton Estate Reserve 8 (6.9 / 212 gl.) — https://rumratings.com/rum/40-appleton-estate-reserve-8-year
- Thought I would try the new Appleton Estate Reserve 8 Yr & Appleton Rare Casks 12 yr Rums recently released from Jamaica.
- Appleton Estate is my favourite rum distillery, their 21 years is absolute perfection for my taste.
- Both have that hint of molasses that I like, but this one is more spicy or peppery - it has some burn.
- Another great rum by this fantastic distillery

### Don Q Gran Anejo (7.4 / 179 gl.) — https://rumratings.com/rum/334-don-q-gran-anejo
- Why don't you guys buy some cheap 151, raw molasses, vermouth, spices and make your own pre-batched cocktail because that's what you're really drinking (and this includes Zacapa, Zaya and even Diplomatico).
- Molasses, oak, honey, vanilla, bourbon, leather, tobacco, and cinnamon.
- Hints of molasses, bourbon, and cinnamon heat make this a great rum to experience neat.

### Zafra Master Reserve 21 (8.3 / 376 gl.) — https://rumratings.com/rum/1029-zafra-master-reserve-21
- A lot of sweetness, smooth, almost no burn, and it taste like molasses with hint of orange peel.
- The rum is produced in Column Still gets bottled with just 40% alcohol.
- Der im Column Still Verfahren hergestellte Rum wird mit mageren 40% Alkohol abgefüllt.

### Angostura 1919 (6.8 / 519 gl.) — https://rumratings.com/rum/24-angostura-1919-8-year
- The Angostura 1919 is a nice blender that works very fine in different cocktail and drinks.
- "The history of Angostura lies with a German apothecary..." "Angostura 1919 rum review Matt Cottom via Rum & Reviews"

### Ron Abuelo Centuria (8.7 / 186 gl.) — https://rumratings.com/rum/738-abuelo-centuria
- However the ready availability of this rum makes me wonder if the bottle I have is a "second generation" Centuria.
- Almost a 7, but the burnt molasses - present but much better balanced in the Abeulo 12 - says "6".
- It’s produced from molasses in a multi column still whereafter it’s aged in Jack Daniel’s barrels using the Solera method.

### Ron Matusalem 15 Solera Gran Reserva (6.4 / 727 gl.) — https://rumratings.com/rum/532-matusalem-gran-reserva-15-year
- The first rum to use solera aging system, previously used only in sherry and spanish brandy making.
- One of my favorite things about Matusalem is how they enjoy reminding us of their great history, which begin in Cuba.

### Wray & Nephew Overproof (6.6 / 282 gl.) — https://rumratings.com/rum/1165-wray-nephew-white-overproof
- I believe it is a mix of pot and column still distillate (I'd love to see a pot still only expression, btw).
- The world's most famous drink mixer rum(?) is a blend of rum distilled in a column still and a pot still whereafter it’s stored in a steel tank for a year before being bottled.
- It was this rum that was used by Victor Bergeron when he created Mai Tai in 1944.
- Tastes just like how it smells at the Appleton Estate.

### Bacardi 8 (6.6 / 492 gl.) — https://rumratings.com/rum/74-bacardi-8
- Strong molasses flavor, has a auburn color, and a bit sharper than some others that are pricier.

### Barcelo Imperial Onyx (7.4 / 176 gl.) — https://rumratings.com/rum/4185-barcelo-imperial-onyx
- which is also made of cane juice and matured on Jack Daniels barrels.

### Botran Añejo 12 Solera (6.2 / 70 gl.) — https://rumratings.com/rum/754-botran-anejo-12-year
- Cardiff Rum Festival good 12 year solera well aged and a decent sipper
- Pourer said age statement is solera (sigh), so there's only trace amounts of 12 year-old juice in here.

### Diplomatico Reserva Exclusiva (7.9 / 3148 gl.) — https://rumratings.com/rum/316-diplomatico-reserva-exclusiva
- A sipper that also goes well as a blender.

### Ron Dos Maderas (5+3/5+5) (6.1 / 137 gl.) — https://rumratings.com/rum/340-dos-maderas-5-3
- Then time for the 5+3, there the 5 stands for the aging of the base in the Caribbean and the 3 for 3 years of Solera aging in used Dos Cortados barrels in Jerez.
- 5 years in oak casks + 3 years in spain in sherry Dos Cortados casks in solera system.
- Interesting method of aging already used by different company but the double or triple aging is the "marque de fabrique" of Dos Maderas.

### Zacapa Centenario 23 (8.5 / 77 gl.) — https://rumratings.com/rum/1283-ron-zacapa-centenario-23
- This is the original bottling of the 23 years old and isn't SOLERA method, but the old method, only 23 years oaks ( same method used for whisky) is out of production by many years......
- the new products are only solera method and the bottle has a straw stripe
- Ron Zacapa Centenario Sistem Solera 23.

### Zacapa Centenario Edición Negra (7.5 / 189 gl.) — https://rumratings.com/rum/3704-ron-zacapa-edicion-negra
- While the Zacapa solera 23 I find to be amazing, the negra is just too overpowered with smokey flavour and over priced.
- I'm going to be sticking to the solera 23.
- I prefer the regular 23 solera.
- In terms of flavour and rating the Edicion Negra his sits right between the Solera 23 and the Zacapa XO.

### Ron Centenario 30 (8.9 / 202 gl.) — https://rumratings.com/rum/783-centenario-30-year
- Smells of caramel, molasses, oak, and vanilla.
- My first taste of Oak, Molasses, and hints of vanilla hooked me all the way.

### Ron Centenario 1985 (20 YO) (8.2 / 395 gl.) — https://rumratings.com/rum/781-centenario-20-year
- I prefer sweet Rum , and this one is a good choice,less sweet as the A.H.Riise Family .
- Lots of added sugar and a Solera 20 are meant to convey premium character.
- The Centenario Solera 20 kommt aus Costa Rica und ist ein Solera Blend, was einfach ausgedrückt bedeutet, das der älteste verarbeitete Rum 20 Jahre lagern durfte.
- Mit der Zeit habe ich gelernt das der Centenario ein klassischer Blender ist.

### Barcelo Gran Anejo (6.1 / 261 gl.) — https://rumratings.com/rum/97-barcelo-gran-anejo
- Molasses, fruit, and sugar are not the centerpiece of this Anejo.

### The Kraken Black Spiced (6.0 / 1948 gl.) — https://rumratings.com/rum/482-kraken-black-spiced
- A caramel/treacley heavy molasses like smell.

### Foursquare Spiced Rum (6.7 / 115 gl.) — https://rumratings.com/rum/413-foursquare-spiced
- We visited the distillery in Barbados on our last trip there and could not get enough of this.

### Diplomatico Distillery Collection N°3 Pot Still (7.9 / 28 gl.) — https://rumratings.com/rum/8488-diplomatico-distillery-collection-no-3-pot-still
- My favourite rum from the distillery collection.
- The copper pot still and use of sugar cane “honey” probably have a big influence.
- Distillery Collection No 1 is still my favorite in that series, but this is a close 2nd.
- The best one from the distillery collection

### Flor de Caña 7 YO Gran Reserva (6.5 / 388 gl.) — https://rumratings.com/rum/409-flor-de-cana-gran-reserva-7-year
- Flor de Caña always keeps its distinct molasses-taste, also in this younger brother of the family.
- Think about trying the other fine rums in the Flor de Cana family as well!

### Zacapa Reserva Limitada 2015 (8.2 / 51 gl.) — https://rumratings.com/rum/2267-ron-zacapa-2015-reserva-limitada
- Sweet with smooth caramel sugar cane taste, and that familiar touch of smoke we know from the ordinary Zacapa 23 solera.

### Zacapa Reserva Limitada 2019 (8.0 / 33 gl.) — https://rumratings.com/rum/8931-ron-zacapa-reserva-limitada-2019
- But even ii it is flavorful the quality is about the same with solera 23 just they make richer and boost the flavours with spices & "magics" (so bit expensive for what you get at around 90 euro).
- Prefer both the XO and Solera 23, that is better rums in my opinion.

### Ron Matusalem Platino (6.0 / 49 gl.) — https://rumratings.com/rum/533-matusalem-platino
- Having had the older Matusalem 18 Solera Blender and it being an acceptable to actually pretty decent Cuban style rum, I picked up this bottle to use for Mojitos and perhaps an occasional Daiquiri.
- From what I can find this is a molasses based column distilled rum that has been “triple distilled” and then aged using the Solera process for an unknown period of time (some places say an average of 10 years but I find that very difficult to believe).
- It does resemble agricole rum slightly.
- Made in the Dominican Republic closely following an old Cuban recipe passed down through this family for generations.

### Ron Matusalem 10 Solera Clásico (5.9 / 99 gl.) — https://rumratings.com/rum/530-matusalem-clasico-10-year
- What a stunning brand history!
- They were born in Cuba, survived repression by the Cuban government (where they were considered the largest rum distillery in Cuba at the time), moved to the Dominican Republic, revived production using a recipe created 130 years ago, and yet their tenth release is simply frankly bad!

### Doorly's 5 YO (6.6 / 126 gl.) — https://rumratings.com/rum/338-doorly-s-5-year
- The brand Doorly’s was founded by Martin Doorly & Company, but is nowadays owned and produced by Foursquare and Mr.
- The 5yo is a single blended rum, a combination of column and pot still, aged in former bourbon casks whereafter it’s bottled without any dosage or additives at 40%.
- I love what Seales has done at the Four Square Distillery and can not recommend their products enough.
- Definitely bringing this to the family beach house this summer.

### Doorly's 8 YO (7.4 / 105 gl.) — https://rumratings.com/rum/3749-doorly-s-8-year
- The brand Doorly’s was founded in 1908 by Martin Doorly & Company, but is since 1992 owned and some years later produced by Foursquare and Mr.
- The 8yo is a rather new bottling in the Doorly’s line-up that saw the light of day in 2016, in the beginning mentioned for the Australian market.
- It’s a single blended rum, a combination of column and pot still, aged in former bourbon casks of American oak whereafter it’s bottled without any dosage or additives at 40%.

### Mount Gay Black Barrel (6.7 / 465 gl.) — https://rumratings.com/rum/1217-mount-gay-black-barrel
- Charred oak barrel notes open up to leave you with a classic pot still Bajan rum.

### Clément Blanc Canne Bleue (7.2 / 79 gl.) — https://rumratings.com/rum/2297-clement-canne-bleue
- Few producers does white agricole better than Clement from Maritinique.
- Nose: Green apples, sugar cane, pepper, red licorice and fresh cut grass Taste: Spicy peppers, plums, grass, citrus peel, licorice that comes together and punches you in the face until it slowly fades out over time Overall: This is without a doubt my favorite white agricole.
- Love to use it as a sipper, but it is also really effective to improve any cocktail that calls for agricole.
- Für Agricole Lover und Barkeeper.

### Clément Select Barrel (6.4 / 99 gl.) — https://rumratings.com/rum/1232-clement-select-barrel
- Overall, an excellent introduction to rhum agricole that won't leave you disappointed.
- Although the taste is a bit harsh but I love the fruity flavour of the agricole rum.
- I like this offering because the young age really lets the cane juice flavor come to the forefront.
- Good for an introduction to Agricole.

### Clément XO (8.1 / 63 gl.) — https://rumratings.com/rum/226-clement-xo-6-year
- It’s not what you expect when you taste an Agricole.
- This one has a nice nose which is not very common when it comes to Agricole.
- hasn't only a nice bottle and packaging, but it's certainly a premium french aged agricole rum!
- En dejlig Agricole rum med noter af eg - karamel og lakrids.

### Depaz VSOP (7.3 / 57 gl.) — https://rumratings.com/rum/1973-depaz-vsop-7-year
- This rum possess one of the most appealing aromas out there, no matter if wer' talking agricole or molasse based.
- Unbelivebly nice and the essense of how delicate agricole can be.
- Briliant balance if your into agricole.
- However, it is a wonderful, smooth and well oaked dry rhum agricole that plays well in a Ti Punch.

### HSE Black Sheriff (6.7 / 54 gl.) — https://rumratings.com/rum/1687-hse-black-sheriff-3-year
- Great and strong taste, smoky, grassy, a real agricole.

### Trois Rivières Cuvée de l'Océan (6.6 / 46 gl.) — https://rumratings.com/rum/2078-trois-rivieres-cuvee-de-l-ocean
- Very different especially for agricole.
- I think it’s an quite smooth Agricole Blanc with the saltiness, from the sea where the cane grows, very present.
- Sehr eigenständiger und spezieller Rhum der das Terroir zeigt und erleben lässt wie es nur wenige Rum vermögen.
- Für Entdecker, Agricole Liebhaber und Freunde des weissen R(h)ums.

### Trois Rivières Cuvée du Moulin (6.6 / 33 gl.) — https://rumratings.com/rum/6782-trois-rivieres-cuvee-du-moulin-3-year
- Good to discover agricole rum.
- I,ve tried a few agricole which tasted very grassy but not this one.
- Für diesen speziellen Rhum sollte man schon Agricole Fan sein In der Nase schön fruchtig.
- For this special Rhum you should already be Agricole fan Fruity nose.

### A.H. Riise Black Barrel Navy Spiced (6.7 / 64 gl.) — https://rumratings.com/rum/2294-a-h-riise-black-barrel-navy-spiced
- 7:The attack on the palate is very round, but quickly balanced by cocoa and molasses.

### A.H. Riise Non Plus Ultra Ambre d'Or (7.5 / 42 gl.) — https://rumratings.com/rum/12251-a-h-riise-non-plus-ultra-ambre-d-or-excellence
- Great addition to the non plus ultras family.

### A.H. Riise Non Plus Ultra Very Rare (7.8 / 210 gl.) — https://rumratings.com/rum/1313-a-h-riise-non-plus-ultra-very-rare
- Riise rums come from a distillery that produces a long list of flavored rums.

### Admiral Rodney HMS Formidable (7.5 / 45 gl.) — https://rumratings.com/rum/6468-admiral-rodney-hms-formidable
- This one is named after the Admiral’s flagship during the battle of the Saintes in 1782.
- The different destillates used is taken from the bottom of the Coffey column still, which should make it more complex and powerful despite the low ABV, and was aged between 9 and 12 years in American white oak ex-bourbon barrels.
- It is named after Admiral Rodney’s flagship in the Battle of the Saints – the crucial battle where he broke the French lines and secured Britain’s dominance over the Caribbean.
- Another great rum from a GREAT DISTILLERY.

### Banks 7 Golden Age (6.7 / 40 gl.) — https://rumratings.com/rum/89-banks-7-golden-age
- Smells and tastes of molasses, oak, spice (pepper), and walnuts.

### Chairman's Reserve Legacy Edition (7.2 / 75 gl.) — https://rumratings.com/rum/12489-chairman-s-reserve-legacy-5-8-years
- Just like the 1931 this has both pot and column still rums, both from molasses and sugarcane (agricole) and just like with the 1931 they made it work beautifully.
- Grassy notes from the agricole part are noticable as well.
- Most of rum is molasses based and comes from column stills, but there are also some pot still rum of which a little part is cane juice based.
- The hidden spank of the agricole is a real marvel to behold, to feel, to taste.

### Compagnie des Indes Caraïbes (6.5 / 30 gl.) — https://rumratings.com/rum/2093-compagnie-des-indes-caraibes
- The molasses takes off quickly rum is even a little smoky, with accents of metal or petroleum.
- Licorice molasses are accompanied by banana and salted butter caramel with some sweet spices of this simple, light palate.
- 5:The finish we notice molasses with its mild sweetness and a little smoke.

### Flor de Caña Extra Seco Reserva N°4 (6.3 / 56 gl.) — https://rumratings.com/rum/7236-flor-de-cana-extra-seco-4-year
- But like a real one, not a blender drink.

### Compagnie des Indes Jamaica Navy Strength 5 YO (7.0 / 52 gl.) — https://rumratings.com/rum/2102-compagnie-des-indes-jamaica-navy-strength-5-year
- The special thing about this rum is that it is a blend of pot and column still.
- Then wonderful ester notes with ripe fruit develop.
- The ester notes are intense but not too intense.
- The ester notes are not that dominant.

### Worthy Park Select (6.7 / 45 gl.) — https://rumratings.com/rum/13841-worthy-park-select-4-year
- This Jamaican rum is a blend of copper pot distilled molasses based rums that have been aged between 4 and 12 years in American white oak ex-bourbon barrels.
- Jämfört med t ex Appleton Estate rare blend så är det mycket smak i den här.

## 5. Materijal za knjigu o bontonu (90 boca)

Zapažanja o serviranju, čaši, ritmu i dijeljenju za stolom. Isto pravilo:
polazište za pisanje, ne citat.


### Foursquare Detente 10 YO — https://rumratings.com/rum/12149-foursquare-2010-detente-10-year
- Real dope toasted almond and apple skin like feel on the pallet.
- After breaking the seal on this bad boy and pouring myself a small glass of Detente I immediately notice a much lighter color from this particular offering.
- I like this rum, but it isn’t as memorable as some other offerings.

### Foursquare Nobiliary — https://rumratings.com/rum/11343-foursquare-2005-nobiliary-14-year
- First sip is also strong Bourbon taste.
- In the first sip you do get some of the wood overtones of the bourbon casks but it's not overpowering.
- Dark Waters United Kingdom 🇬🇧 | 7 ratings

### Foursquare Sagacity — https://rumratings.com/rum/11549-foursquare-2007-sagacity-12-year
- Careful with sipping neat an overproof rum.
- First sip and I understand why this rum gathered such good reviews.
- Picture: My emptied samples poured in a glass.

### Hampden Estate 8 YO — https://rumratings.com/rum/6622-hampden-estate-8-year
- Great chunky bottle, neat lable, but plastic stopper.
- 4/10 EDIT: So in recent months after tasting a lot of whiskies I came around to this style of rum, funky but interesting, just add tablespoon or two of water.
- Its almost like a marriage between Smith & Cross and Kentucky bourbon with some bitter herbs, cigar smoke, and pear brandy thrown in for good measure.

### Appleton Estate 15 YO Black River Casks — https://rumratings.com/rum/13170-appleton-estate-black-river-casks-15-year
- Nose: Ripe bananas, molasses, vanilla, and dried apricots Taste: really oaky ,more smooth and complex version of the Appleton 12 year(rare cask), definitely a good sipper but not balanced enough to be great.
- This rum is better suited as a mixer or bargain sipper.
- This place is also the source of water for Appleton rums.

### Chairman's Reserve 1931 — https://rumratings.com/rum/7161-chairman-s-reserve-1931-6-12-years
- I couldn't wait anymore, so i finally opened it and am sipping from my precious, right now!
- Nice alcohol bite, very smooth and crisp but immediately fades to velvet sipping pleasure on the pallet.
- WOW, what a pleasant Sipper this rum is.

### Clément VSOP (agricole) — https://rumratings.com/rum/225-clement-vsop-4-year
- With a splash of water it really opened up.
- Slightly harsh, better with a dab of water
- Long finish - taste really evolves/matures through the sipping process.

### Eminente Reserva 7 — https://rumratings.com/rum/12213-eminente-reserva-7-year
- Finale : long (pour du rhum de mélasse), notes de caramel.

### Havana Club Seleccion Maestros — https://rumratings.com/rum/442-havana-club-seleccion-de-maestros
- I love this rhum and when I had enjoyed a special dinner it's the right choice to finish the evening with a cigar!
- I have had my share of rums over the years and I found Selection de maestro to be very smooth.

### Havana Club Union — https://rumratings.com/rum/3679-havana-club-union
- This is a very good rum but believe I need a good Cohiba Cigar to pair with it.
- Package in a nice wooden box which still smell like Cigars factory we visit.

### Mount Gay XO — https://rumratings.com/rum/565-mount-gay-xo-extra-old
- I enjoyed this drink neat with some chocolates
- Almost perfect on most levels, great neat or with single ice cube
- Its smooth, intese, easy sipping, sweet, and affordable.

### Mount Gay 1703 — https://rumratings.com/rum/561-mount-gay-1703-old-cask
- No doubt he'd add that if drinkers gave a pure, un-sugared rum like this one (and his own superb Foursquare rums) a chance they'd appreciate the immense pleasure from all that they have to offer.
- I simply feel that skillfully aged and unsweetened rum like this, offer a delicate taste profile, that non of the additive rums can hope to achieve.
- Great offering but a wee bit pricey.

### Worthy Park 109 — https://rumratings.com/rum/13127-worthy-park-109
- Worthy of experimentation (no pun intended) in mixed cocktails, great in the Jet Pilot - but also serves nicely as a sipper.

### Worthy Park Single Estate Reserve — https://rumratings.com/rum/6464-worthy-park-single-estate-reserve-6-10-years
- The body could be a little more full-bodied and in between it sometimes appears minimally too watery.
- Super smooth and great for sipping.
- Not too sweet and good neat or on the rocks, would probably hold its own in a cocktail too!

### Appleton Estate 12 YO Rare Casks — https://rumratings.com/rum/12087-appleton-estate-rare-casks-12-year
- I was really surprised with the younger rum which I find even better than the Older version of the Appleton Rare Blend 12 yr version and Its quality is definitely worthy of being drank neat.
- Great for sipping, and the right amount of hogo to take a good cocktail over the top while not getting lost.

### Havana Club 7 Anos — https://rumratings.com/rum/436-havana-club-7-year
- I always drink it neat, and I love the linging taste it leaves behind, even after a few minutes.
- I personally don't like it, but if you sip your rum while smoking cigars, you'll love it.
- I have it with a little water, sometimes with ice.

### Appleton Estate Reserve 8 — https://rumratings.com/rum/40-appleton-estate-reserve-8-year
- such a great everyday sipping wine that transports me back to the Caribbean every time.
- Yeah, not top shelf but reliable, affordable, full flavour, a real cigar of a rum.
- I was really surprised with the younger rum which I find even better than the Older version of the Appleton Rare Blend 12 yr version and Its quality is definitely worthy of being drank neat.

### Brugal 1888 — https://rumratings.com/rum/143-brugal-1888
- It doesn't excel at any particular point, but for the money, it's just a great no nonsense sipper, perfectly enjoyed in the sun.

### Don Q Gran Anejo — https://rumratings.com/rum/334-don-q-gran-anejo
- when Fidel took power) can also be credited with pumping a whole lot of waste water into the Caribbean and confusing consumers about what really is Puerto Rican rum.
- I love sipping it on special ocassions.
- Very smooth, light with subtle vanilla, oak and caramel, I enjoy it on the rocks.

### Zafra Master Reserve 21 — https://rumratings.com/rum/1029-zafra-master-reserve-21
- Zafra 21 is a must have for any person who enjoys sipping rum.
- For me the rum was a little too thin and watery.
- For me, the rum is too diluted and 43% or 45% would make it so much better.

### Angostura 1919 — https://rumratings.com/rum/24-angostura-1919-8-year
- I tried to drink it neat but don´t think it´s good enough.
- This rum is a bit too harsh to drink neat, in my opinion.
- Great for sipping, great for mixing, and lovely on the tongue.

### Angostura 1787 — https://rumratings.com/rum/3958-angostura-1787-15-year
- The composition is very inviting and mouth watering.
- Especially since the fruit hit me very unexpected on the first sip.
- Nie som fajciar a cigaru si dám len ojedinele.

### Kirk and Sweeney Gran Reserva — https://rumratings.com/rum/13219-kirk-and-sweeney-gran-reserva
- I still gave it an 8 as it is still a good sipping rum.
- Note: this is not a rum you pour and drink.
- Kirk and Sweeney have some truly excellent sipping rums, but this one is a notch or two below those.

### Ron Abuelo Añejo — https://rumratings.com/rum/737-abuelo-anejo
- I prefer it on rocks, but could go neat, as well.
- The Abuelo costs around $2.5 more (it was an offer that came with two glasses) but the quality and the taste of this ron is so much better.
- I just had it pure or on the rocks.

### Ron Abuelo Centuria — https://rumratings.com/rum/738-abuelo-centuria
- This will make you buy a Panama hat and smoke cigars, if you don't already.
- This is an elegant, sumptuous sipper.
- Although it has a pleasant aroma and looks great in the snifter with a deep mahogany color, the flavor is...well...lacking.

### Ron Matusalem 15 Solera Gran Reserva — https://rumratings.com/rum/532-matusalem-gran-reserva-15-year
- It's important to know that this was the first rum produced to be a sipper.
- Matusalem is a stupendous, refined rum that is slightly above average sipper and mixer.
- I would recommend trying it as a digestif, instead of the typical port wine.

### Wray & Nephew Overproof — https://rumratings.com/rum/1165-wray-nephew-white-overproof
- Although it is intended as a mixer--it's pretty much an essential white OP for many cocktails--I actually quite enjoy this neat, albeit with a few drops of water to bring it down to a more manageable 45-50%.
- The more useful question is, how does this stuff taste on the rocks or even neat?
- Also, I had no luck drinking it on the rocks, even with lime and sugar.

### Angostura 5 YO — https://rumratings.com/rum/1510-angostura-5-year
- My opinion is based on sipping characteristics.
- Upon first sip, there were rums I could think of that resemble the taste.
- Finishes like sweet salt water taffy.

### Bacardi 8 — https://rumratings.com/rum/74-bacardi-8
- An excellent sipping rum with good (if not very strong) flavor, and lacking the heavy kick of many aged rums.
- I'd recommend this as a first step for anyone looking to explore sipping rums.
- Feel: A little light and watery but warms up increasing the flavours along the way.

### Barcelo Imperial Onyx — https://rumratings.com/rum/4185-barcelo-imperial-onyx
- another good sipper, not oversweet.
- On the palate very mild and soft, discreet caramel in chocolate coating, cream toffee vanilla cream, candied tropical fruits lie in a toasted wooden bowl.Could have a little more body, maybe it's the low vol.%?
- Otherwise, on the nose, we're on classic Barcelo, it's very pastry, caramel, coconut, almond, vanilla, toasted, cherry.

### Botran Añejo 12 Solera — https://rumratings.com/rum/754-botran-anejo-12-year
- rien de particulier ni au nez ni en bouche, correct avec glaçon et cigare^^
- Did taste it in Ciudad de Guatemala, rumhouse near the airport (zona 13) and then with ice in some bar in Antiqua, Guatemala which tasted even worse.
- The taste is watery, the dilution is bad.

### Diplomatico Reserva Exclusiva — https://rumratings.com/rum/316-diplomatico-reserva-exclusiva
- From the first sip, I was like.."huh?" My background is, I have dietary restrictions and don't drink soda or eat a lot of candy (sugar) or sugary drinks or food, even.
- Diplomatico RE was my first sipping rum.
- Drinking it neat is the way to go.

### Ron Dos Maderas (5+3/5+5) — https://rumratings.com/rum/340-dos-maderas-5-3
- Sweet notes of dried fruits (nuts) and toasted aroma in the mouth.
- Nice and light sipper for a change of flavours but at its pricepoint underperforming; I can buy a Mount Gay XO (with some change left) or a Doorly's 12yo and there is no way this comes even remotely close.
- It took me back to the 70's when we used to get used whiskey or rum barrels and put water in them to eventually create a wild beverage called "Barrel Wash".

### Ron Millonario 15 Reserva Especial — https://rumratings.com/rum/805-millonario-reserva-especial-15
- You can drink this rum neat as a sipper but also as a base in cocktails and drinks.
- It's certainly not my favorite for sipping, and haven't found an amazing cocktail for it yet.

### Zacapa Centenario 23 — https://rumratings.com/rum/1283-ron-zacapa-centenario-23
- This is a very good straight forward sipping rum, but a little to sweet for my taste.
- Very nice entry rum if you try to introduce someone to drink neat rum.
- Drinks very similar to a whiskey, and is best enjoyed on the rocks.

### Diplomatico Mantuano — https://rumratings.com/rum/4262-diplomatico-mantuano
- Beautifully smooth rum, perfect for sipping over ice.

### Zacapa Centenario Edición Negra — https://rumratings.com/rum/3704-ron-zacapa-edicion-negra
- A dark sipping rum with a taste profile contains the well known Caramel, oak, and vanilla flavours associated with the Zacapa line of rums.
- Lots going on here, great sipper.

### Ron Centenario 30 — https://rumratings.com/rum/783-centenario-30-year
- Another exceptional offering from Ron Centenario!
- Let them sit at least 10 min after pouring before reviewing/drinking.

### Havana Club Original 3 — https://rumratings.com/rum/435-havana-club-3-year
- and it is old enough to have it's own attitude to present, so drinking neat "young" rums is finally enjoyable (but mostly on the rocks).
- It is by no means a sipper, so don't drink it neat.
- Some say this HC 3yo can only be judged as a mixer but that is nonsense in my book; every rum out there is a sipper, or it is not.

### Ron Centenario 1985 (20 YO) — https://rumratings.com/rum/781-centenario-20-year
- I normally enjoy rum on the rocks but could easily see myself drinking this straight up.
- I usually enjoy my sipping rums neat, but this one is also great with a single ice cube.

## 6. Spojevi imena za provjeru (0)

Slabije poklapanje imena — potvrdi da je riječ o istoj boci prije nego što
ijedan broj iz gornjih tablica uzmeš zdravo za gotovo.

| Naše ime | Njihovo ime | poklapanje |
| --- | --- | ---: |

## Uredničke napomene (prolaz 2026-08-21)

- Skinuto **160** boca iz kataloga (162 URL-a; 2 stranice bez ocjene ostaju miss, ne nula: Mauritius Rom Club White, CDI 2022 14 YO).
- Sitemap ima ~13 165 boca; spoj s naših 320 iznad praga 0,70 dao je **162** URL-a. Dio 3 (boce koje nemamo) prazan je namjerno: nismo vukli cijeli sitemap (robots `crawl-delay: 30` → višednevni posao).
- Usporedba s `--floor 0.70` — pet slabih spojeva s praga 0,55 (Riise XO↔Christmas, Jylland↔Frogman, CDI Jamaica 5↔Navy Strength, Flor de Caña Blanco↔Gran Reserva, CDI Spiced↔Caraibes) **nisu** u tablicama.
- Sustavni obrazac u dijelu 2: solera/slatki profili (Centenario, Zacapa, Riise, Barceló) zajednica hvali više; agricole (Clément VSOP, Saint James XO) mi držimo više. To je razlika ljestvice, ne nalog za mijenjanje `qualityScore` po boci.
- Club: u `club.json` ušle tri provjerene zanimljivosti (Doorly's = Foursquare; Dos Maderas 5+3; Admiral Rodney HMS Formidable / Saintes 1782). Recenzijski mit da je Wray Overproof originalni Mai Tai iz 1944. **nije** unesen — original je koristio 17-godišnji Wray, ne bijeli overproof.
- Bonton: poglavlje VI već pokriva čašu, vodu uz high-proof i prvi gutljaj. Citati iz recenzija nisu lijepljeni. Ako se bude dograđivalo: overproof (Wray) je prvo mixer; agricole često otvara kap vode; ECS ne suditi na prvom dimu.
