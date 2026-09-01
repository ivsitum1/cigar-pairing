# Širenje kataloga fotografija — runbook za lokalno pokretanje

Ovo je posao koji traži mrežu do dućana i Pillow, pa se **ne može pokrenuti iz
Claude Code sesije u oblaku** — proxy blokira cigarworld.de, humidor.hr i
allez.hr. Skripte su pripremljene i otestirane; ovdje je redoslijed.

Sve komande se pokreću **iz `app/`**.

## Preduvjeti

```bash
cd app
pip install Pillow beautifulsoup4      # Pillow za obradu, bs4 za scrape stranica
```

`scripts/output/` je git-ignoriran i **prazan na svježem klonu**. Tamo žive
originali slika i sirovi crawlovi; u repo ulazi samo gotov WebP i manifest.

## Gdje smo

```bash
python3 scripts/report-image-gaps.py
```

```
sloj                zapisa  obradjeno  ducansko  bez slike  pokriveno  obradjeno
cigare-linija         3293       3238        20         35        98%        98%
cigare-vitola         3547          0      3547          0       100%         0%
pica                  1113        347         8        758        31%        31%
```

---

## Zadatak A — sloj po vitoli (spreman, ~3540 slika, ~74 MB)

`productImages.json` nosi 3547 adresa oblika `cig-x@vitola` jer dućan ima
zaseban SKU po veličini. Obrađenih je **nula**, pa `productPhotoForCigar`
preferira scoped ključ i vrati **neobrađenu dućansku fotografiju** s tuđeg
poslužitelja — kartica tada dobije tamnu plohu iza slike umjesto izreza.

### 1. Probni prolaz

```bash
python3 scripts/fetch-product-images.py --kind cigars --scoped only --limit 20
ls scripts/output/product-images/raw/cigars/ | grep '@' | head
```

Ispis mora reći koliko je adresa po vitoli i koliko ih je za preuzeti. Ako je
`0 za preuzeti`, sve je već lokalno preuzeto (`--force` za ponovno).

### 2. Obrada i provjera na malom uzorku

```bash
python3 scripts/normalize-product-images.py --kind cigars
npx vitest run src/data/productImageFiles.test.ts src/lib/productImage.test.ts
python3 scripts/report-image-gaps.py     # cigare-vitola / obradjeno mora porasti
```

Pogledaj nekoliko slika u `public/img/products/cigars/*@*.webp` prije nego
pustiš puni prolaz — ako obrada nešto krivo izreže, bolje na 20 nego na 3540.

### 3. Puni prolaz, u serijama

```bash
python3 scripts/fetch-product-images.py --kind cigars --scoped only --limit 400
python3 scripts/normalize-product-images.py --kind cigars --jobs 4
```

Ponavljaj dok `--scoped only` ne kaže `0 za preuzeti`. Skripta je pristojna
prema dućanima (pauza između zahtjeva) i ima resume — već preuzeto se
preskače, pa prekid nije problem. `--jobs 4` ubrzava obradu; `--pause` diže
razmak ako dućan počne odbijati.

### 4. Zaključi

```bash
npm test && npm run build
python3 scripts/report-image-gaps.py --update-baseline
git add public/img/products src/data/productImagesLocal.json scripts/data/image_coverage_baseline.json
git commit -m "Obradi sloj fotografija po vitoli"
```

Baseline se diže **nakon** uspješnog širenja, da idući pad bude uhvaćen prema
novoj razini.

---

## Zadatak B — pića (758 bez slike)

Redoslijed je drukčiji nego kod cigara: **samo 12** od 758 ima `priceUrl` s
kojeg se slika skida. Ostalih **734** nose samo ime dućana (`shopHR`:
allez.hr 397, Vivat 61, ecuga.com 48), pa im prvo treba pronaći stranicu
proizvoda. Bez toga `fetch-product-images.py --kind drinks` nema što raditi.

### 1. Crawl dućanskih listinga (ako `scripts/output/drink_shop_listings_raw.json` ne postoji)

```bash
python3 scripts/scrape-drink-shop-listings.py --shops allez,tipsy,cugaklik,miva,roto,humidor
```

### 2. Spoji listinge na katalog — tako pića dobiju `priceUrl`

```bash
python3 scripts/scan-drink-shop-gaps.py
python3 scripts/merge-drink-shops-additive.py --dry-run --tiers a,b   # pregledaj plan
python3 scripts/merge-drink-shops-additive.py --apply --tiers a,b
```

Tier C (`catalog_ask_queue.json`) i D (`shop_ingest_staging.json`) su ručna
odluka — vidi odjeljak „Drink shop crawl → map" u `AGENTS.md`.

### 3. Tek sada slike

```bash
python3 scripts/attach-product-images.py            # adrese → productImages.json
python3 scripts/fetch-product-images.py --kind drinks
python3 scripts/normalize-product-images.py --kind drinks
```

### 4. Zaključi

```bash
npm test && npm run build
python3 scripts/report-image-gaps.py --update-baseline
```

---

## Što će te zaustaviti ako nešto preskočiš

| Gate | Pada kad |
|------|----------|
| `src/data/productImageFiles.test.ts` | zapis u manifestu nema datoteku, ili datoteka nema zapis — **commitaj slike i `productImagesLocal.json` zajedno** |
| `src/lib/productImage.test.ts` | manifest spominje id koji katalog ne zna |
| `python3 scripts/report-image-gaps.py --check` | broj slika je **pao** ispod baselinea; namjerno uklanjanje traži `--update-baseline` u istom commitu |
| `python3 scripts/test_scoped_product_images.py` | znak `@` je negdje izgubljen u lancu ime datoteke → `Path.stem` → ključ manifesta |

## Dvije stvari koje se ne diraju

- **`productImages.json` (dućanske adrese) i `productImagesLocal.json`
  (obrađene) su odvojena popisa.** `normalize-product-images.py` ne dira prvi —
  pregazio bi ono čime aplikacija radi danas. Zato obrada smije stati na pola.
- **`webp` ne ide u `globPatterns`.** Precache bi na instalaciji povukao cijeli
  katalog slika. Slike idu kroz `runtimeCaching` pravilo `product-images`.
