# Logo — brainstorm (sidequest)

Šest smjerova za znak Cigar & Drink Pairinga. **Izabrano: 01 Banderola + 05 Pečat**, i
provedeno kroz app — specifikacija konačnog znaka je u [`LOGO.md`](LOGO.md). Ovaj dokument
ostaje zapis odluke: što je razmatrano i zašto ostalo nije prošlo.

Skice: `docs/brand/concepts/*.svg` (+ PNG preview na tamnoj i svijetloj podlozi).
Regeneracija: `python docs/brand/concepts/generate_concepts.py` — svi radijusi, nepravilnost
ruba i razina pića su parametri u toj jednoj datoteci.

## Brief

- Minimalistički znak, malo elemenata; ovalna ili nepravilna forma.
- Zemljana, smeđa, kožna paleta.
- Mora izdržati 16 px favicon i 192 px PWA ikonu na početnom zaslonu.
- Bez lifestyle klišeja i bez elementa koji ne nosi značenje.

## Paleta

Izvedena iz postojeće *Humidor* palete u `app/src/index.css`, pomaknuta prema koži.

| Ime | Hex | Uloga |
| --- | --- | --- |
| Duhan | `#241A12` | najdublja smeđa, tamna podloga |
| Koža | `#6B4A31` | masa, tijelo znaka, linija na papiru |
| Konjak | `#A9662F` | tekućina — jedini topli akcent |
| Zlato | `#C9A35C` | band zlato, keyline |
| Papir | `#E8DBC0` | stari label papir, svijetla podloga |
| Žar | `#8A3A2A` | oxblood; najviše jednom po znaku |

## Koncepti

### 01 Banderola — `01-banderola.svg`

Prsten cigar-banda je već ovalni kartuš — jedini oblik iz svijeta cigara koji je istovremeno
tipografski okvir. Ista elipsa gledana odozgo je obod čaše, pa ispunjena donja trećina čita
kao razina pića. Dvostruka zlatna linija je stvarni keyline s banda i već postoji u appu kao
`.band-rule`.

- **Za:** ovalno po briefu, drži se na 16 px, nasljeđuje postojeći vizualni sustav.
- **Protiv:** tanka unutarnja linija nestaje ispod 20 px.
- **Napomena:** zlato na papiru pada ispod čitljivog kontrasta → svijetla varijanta
  `01-banderola-papir.svg` vodi liniju u koži, ista geometrija.

### 02 Meniskus — `02-meniskus.svg`

Čaša odozgo, natočena do pola, a u praznini iznad razine lebdi kolut dima.

- **Za:** najizravnije čitanje, najmirnija forma.
- **Protiv:** bez cigare čita i kao šalica kave; kolut dima se prvi gubi. App pokriva sedam
  kategorija pića — znak koji je doslovno čaša sužava temu na jednu.

### 03 Presjek — `03-presjek.svg`

Cigara s glave: nepravilan obod ručno motanog omota, unutra jedan potez smotanog uloška, u
sredini žar. Nepravilnost je sadržaj, ne stil.

- **Za:** nepravilna forma po briefu, nitko u kategoriji to ne koristi.
- **Protiv:** spirala na 16 px postane mrlja; blizu je klišeju puža.

### 04 Spoj — `04-spoj.svg`

Dvije elipse, jedna cigara i jedno piće; ispunjeni presjek je točno ono što engine radi —
boduje preklapanje tijela, slatkoće i okusa.

- **Za:** najjasnija ideja, skalira bez gubitka.
- **Protiv:** Venn dijagram je generička forma; čita i kao atom ili oko.

### 05 Pečat — `05-pecat.svg`

Ista banderola, utisnuta u nepravilnu masu kože — pečat na kutiji, ne naljepnica. Jedini
znak iz serije koji je puna forma, pa sam nosi ikonu bez zaobljenog kvadrata ispod sebe.

- **Za:** najbolja masa na 16 px, nepravilan oval po briefu, radi na obje podloge.
- **Protiv:** nepravilan rub traži disciplinu — svaki naknadni retuš mora ići kroz generator.

### 06 Luk — `06-luk.svg`

Jedan oval razlomljen na dva luka: tanki gornji je dim, teški donji je piće. Debljina poteza
nosi cijelo značenje, praznina sa strane je mjesto spoja.

- **Za:** najmanje elemenata, odličan kao razdjelnik u UI-u.
- **Protiv:** otvorena forma slabo drži ikonu; čita kao osmijeh.

## Preporuka: 01 Banderola kao znak + 05 Pečat kao ikona

Nisu dva logotipa nego jedan sustav — isti unutarnji oval, ista razina pića. Linijska verzija
ide u zaglavlje i na papir, puna verzija na početni zaslon, gdje masa pobjeđuje liniju. Time
je riješen jedini stvarni problem: ikona koja mora preživjeti 16 px pored znaka koji mora
podnijeti veliki format.

## Provedeno

1. **Optički ispravak elipse** — potez prstena na vrhu i dnu je 7,9 naprama 7,0 sa strane.
2. **Kožna varijanta za papir** — zlato tamo ne drži kontrast.
3. **Maskable ikona** s 16 % zraka i punom podlogom, odvojena od `purpose: any`.
4. `app/public/icon.svg`, PNG-ovi, `apple-touch-icon`, manifest i `theme-color` (`#201812`).
5. Znak u UI-u (`<BrandMark />`, `<BrandSeal />`) i na hero dijelu flyera.

Detalji i pravila korištenja: [`LOGO.md`](LOGO.md).
