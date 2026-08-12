# Znak — specifikacija

Znak je **sustav od dvije težine iste geometrije**, ne dva logotipa.

| | **Banderola** | **Pečat** |
| --- | --- | --- |
| Forma | linija (prsten cigar-banda) | puna masa kože s utisnutom banderolom |
| Gdje | zaglavlje appa, dokumenti, papir | ikona, favicon, mjesta gdje znak stoji sam |
| Boja linije | nasljeđuje boju teksta (`currentColor`) | fiksno zlato na koži |

Isti unutarnji oval i ista razina pića vežu ih u jedno: prsten banda gledan odozgo je obod
čaše, a puna donja trećina je piće u njoj. To je cijeli sadržaj znaka — cigara i piće u
jednom obliku, bez ilustracije.

## Ime

**Cigar & Drink Pairing** — jedno ime, svugdje, bez iznimke: zaglavlje, dobna potvrda,
naslov stranice, manifest (`name` i `short_name`), share sheet, podnožje, flyer, README.

Zašto to ime, a ne kraće: par nose *Cigar & Drink* (`&` obećava dvije stvari, a pairing je
radnja, ne druga stvar), dok *Pairing* kaže što app s tim parom radi. Ime k tome **lijepo
podnosi rezanje** — launcher koji ga skrati na "Cigar & Drink" i dalje pokazuje ispravno
ime, a ne krnji fragment.

U znaku se ime postavlja u **dva reda** — `CIGAR & DRINK` iznad razmaknutog `PAIRING`. To
nije drugo ime nego tipografska hijerarhija istog imena; nikad ga ne skraćivati u tekstu.
`&` je u boji žara, jedino mjesto gdje ta boja dodiruje ime.

## Regeneracija

```bash
python docs/brand/generate_logo_assets.py     # traži cairosvg za PNG izlaz
```

Geometrija (radijusi, optički ispravak, nepravilnost ruba, razina pića) mijenja se **samo**
u toj skripti. Sve ostalo je njezin ispis i ne uređuje se ručno:

| Datoteka | Uloga |
| --- | --- |
| `docs/brand/logo-mark.svg` | banderola, zlato — tamna podloga |
| `docs/brand/logo-mark-papir.svg` | banderola, koža — svijetla podloga |
| `docs/brand/logo-seal.svg` | pečat |
| `docs/brand/logo-mark-mono.svg`, `logo-seal-mono.svg` | jedna boja (crna) — svijetla podloga |
| `docs/brand/logo-mark-mono-invert.svg`, `logo-seal-mono-invert.svg` | jedna boja (bijela) — tamna podloga |
| `docs/brand/*-512.png` | rasterski preview |
| `app/public/icon.svg` | favicon + PWA ikona (pečat, bez podloge) |
| `app/public/icon-192.png`, `icon-512.png` | PWA `purpose: any` |
| `app/public/icon-512-maskable.png` | PWA `purpose: maskable` — 16 % zraka + podloga |
| `app/public/apple-touch-icon.png` | iOS početni zaslon (iOS ignorira prozirnost) |
| `app/src/components/brandArt.ts` | putanje koje `<BrandMark />` crta inline |
| `marketing/flyer.html` | znak između `<!-- LOGO:pecat -->` markera |

## U aplikaciji

`app/src/components/BrandMark.tsx`:

- `<BrandMark />` — linijski znak; boja dolazi iz `text-*` klase roditelja
- `<BrandSeal />` — puna forma; koristi se kad znak stoji sam (dobna potvrda)
- `<BrandWordmark />` — ime + zlatna linija, bez znaka
- `<BrandLockup />` — znak uz ime (zaglavlje)

Znak je `aria-hidden` kad stoji uz ispisano ime; `title` prop postavlja `role="img"` i
naziv za čitač ekrana kad stoji sam.

## Pravila

1. **Ne mijenjati omjer.** Oval je 83 × 61; skalira se cijeli, nikad samo jedna os.
2. **Optički ispravak je namjeran.** Potez prstena na vrhu i dnu deblji je od bočnog
   (7,9 naprama 7,0), inače oval izgleda stisnuto. Zato su prstenovi ispune s
   `fill-rule="evenodd"`, a ne `stroke` — obični potez to ne može dati.
3. **Zlato ne ide na papir.** Ispod ~4,5:1 kontrasta zlato na svijetloj podlozi ne drži;
   tamo ide kožna varijanta.
4. **Razina pića je vodoravna i uvijek u donjoj trećini.** Nagnuta razina čita kao greška.
5. **Ikona bez podloge, osim gdje platforma traži drukčije** — maskable i iOS.
6. **Žar (oxblood) nije dio znaka.** Ostaje rezerviran za `&` u imenu i za upozorenja u UI-u.

## Jednobojna verzija

Za tisak u jednoj boji, graviranje, žig, vez i svaku podlogu na kojoj dvije nijanse ne prežive.
Cijeli znak je **jedna putanja s `fill-rule="evenodd"`** — bez maski, prozirnosti i preklopa,
onako kako to traži rezač i tiskar.

- **Banderola** ostaje pozitiv: prsten, keyline i puna razina pića u istoj boji.
- **Pečat se obrće**: masa je tinta, pa banderola u njoj postaje izrez. Parnost preklapanja
  radi posao — masa 1×, prsten 2× (izrez), unutrašnjost 3×, piće 4× (izrez).
- Ne rekonstruirati jednobojnu verziju uklanjanjem boja iz obojene — pečat bi nestao u masi.
- U aplikaciji: `<BrandMark mono />` i `<BrandSeal mono />`, boja iz `currentColor`.

## Paleta znaka

| Ime | Hex | Uloga |
| --- | --- | --- |
| Koža | `#6B4A31` | masa pečata, linija na papiru (`--color-koza`) |
| Konjak | `#A9662F` | razina pića u banderoli (`--color-konjak`) |
| Zlato | `#C9A35C` | linija znaka, razina pića u pečatu (`--color-zlato`) |
| Humidor | `#201812` | podloga ikone, `theme_color` i `background_color` |

Odabir znaka i odbačeni smjerovi: [`LOGO_BRAINSTORM.md`](LOGO_BRAINSTORM.md),
skice u [`concepts/`](concepts/).
