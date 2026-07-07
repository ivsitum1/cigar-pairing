# Poboljšano OCR prepoznavanje cigara i ruma — dizajn (v2, bez backenda)

Datum: 2026-07-07
Status: prijedlog (čeka odobrenje)

> v1 ovog dokumenta predlagala je Cloudflare Worker + Claude vision API.
> Odbačeno na zahtjev korisnika — bez vanjskih servisa. Ova verzija je u
> potpunosti klijentska: nema računa, nema troška, nema backenda.

## Kontekst i problem

Aplikacija (React PWA, statički hostana na GitHub Pages) ima OCR skeniranje preko
tesseract.js (`app/src/components/OcrScan.tsx`): fotografija → tekst → token-matching
na katalog. U praksi Tesseract s prstenova cigara često ne izvuče upotrebljiv tekst
(ukrasni fontovi, zakrivljen tekst, zlatotisak, španjolski nazivi), pa matching nema
s čime raditi.

## Cilj

Znatno podići postotak uspješnih prepoznavanja **bez ikakvog backenda ili vanjskog
API-ja**, kombinacijom tri zahvata: predobrada slike, OCR podešen za prstenove, i
matching tolerantan na OCR greške. Realno očekivanje: osjetno bolje nego sad, ali
neće biti savršeno na najtežim prstenovima — to je svjesni kompromis ove verzije.

## Arhitektura

Sve ostaje u browseru; mijenja se samo unutrašnjost postojeće OCR komponente:

```
fotka ──► predobrada (canvas) ──► tesseract.js (eng+spa) ──► fuzzy matching ──► artikl / tražilica
```

## Zahvat 1: predobrada slike (canvas)

Prije slanja Tesseractu, slika se u canvasu obradi:

- **skaliranje**: duža stranica na ~1600 px (premale slike su glavni uzrok praznog
  OCR-a; prevelike su spore),
- **grayscale + rastezanje kontrasta**: zlatotisak na tamnoj podlozi postaje
  čitljiviji; jednostavna linearna normalizacija histograma (bez teških algoritama),
- **druga prolaz s invertiranim tonovima**: prstenovi su često svijetli tekst na
  tamnoj podlozi — OCR se pokrene na normalnoj i invertiranoj verziji, tokeni se
  spoje (unija).

## Zahvat 2: OCR podešavanje

- **Jezici: `eng+spa`** — kubanski i nikaragvanski nazivi (Partagás, Hoyo de
  Monterrey, Flor de Cañas…) sadrže španjolske riječi i dijakritike koje engleski
  model krivo čita. Jezični podaci se i dalje lijeno učitavaju na prvu upotrebu.
- **PSM mod za raspršeni tekst** (`sparse text`): tekst na prstenu nije uredan
  odlomak nego razbacane riječi — default mod ga često odbaci.
- **Whitelist znakova nije opcija** (nazivi sadrže brojeve, točke, crtice), ali se
  odbacuju tokeni kraći od 3 znaka i tokeni s manje od 50 % slova.

## Zahvat 3: matching tolerantan na OCR greške

Postojeći `matchOcrText` traži **egzaktno** poklapanje tokena — jedna kriva OCR
zamjena (npr. „Partaqas") znači promašaj. Novi matching:

1. **Fuzzy usporedba tokena**: Levenshteinova udaljenost ≤ 1 za tokene do 6 znakova,
   ≤ 2 za dulje (vlastita ~20-redna implementacija, bez novih ovisnosti).
2. **Dvofazni matching: prvo brend, pa linija.** Katalog ima ~69 brendova cigara i
   manji broj rum brendova — prepozna li se brend, kandidati se sužavaju na njegove
   linije, pa i slabiji ostatak teksta često dovoljan za pogodak.
3. **Bodovanje**: egzaktan token 2 boda (5+ znakova) / 1 bod, fuzzy pogodak pola
   boda; prag pogotka se kalibrira testovima.
4. **Fallback nepromijenjen**: bez pouzdanog pogotka, najdulja prepoznata riječ ide
   u tražilicu.

## Klijentske izmjene (`app/`)

- `OcrScan.tsx`: dodaje se korak predobrade (nova pomoćna funkcija, npr.
  `preprocessImage` u istoj datoteci ili `lib/ocrPreprocess.ts`), Tesseract poziv
  prelazi na `eng+spa` + PSM opciju, dva prolaza (normalno + invertirano).
- `matchOcrText` se proširuje fuzzy logikom i dvofaznim brend→linija matchingom;
  potpis ostaje kompatibilan s pozivateljima (CatalogPage/CollectionPage).
- Nema novih npm ovisnosti; tesseract.js ostaje.

## Testiranje

- Vitest unit testovi za fuzzy matching: OCR-tipične greške („Partaqas",
  „C0hiba", „MONTECRIST0"), dvofazni brend→linija, prag odbijanja smeća,
  rum vs. cigara.
- Testovi za predobradu se ne pišu (canvas u jsdom-u nije reprezentativan);
  predobrada se provjerava ručno na stvarnim fotkama.
- Postojeći CI (test + build na push) pokriva sve.

## Izvan opsega

- Bilo kakav backend, vanjski API ili korisnički API ključevi.
- Offline ML modeli (TF.js klasifikacija prstenova — nema dataseta).
- Prepoznavanje vitole/formata sa slike.
- Savršena točnost na najtežim prstenovima (ukrasna kaligrafija na zlatu) —
  granica onoga što OCR u browseru može.
