# Shop scrape (raw catalog) design

**Datum:** 2026-07-21  
**Status:** predloženo → čeka approval za implementaciju  
**Cilj:** napraviti reproducibilan “raw” izvoz kataloga cigara iz odabranih web shopova, bez izravnog upisa u `app/src/data/cigars.json`.

## Kontekst (što već postoji)

- Repo već ima HR sink skriptu `app/scripts/sync-hr-shops.py` koja:
  - `havana-cigar-shop.com` čita preko WooCommerce Store API-ja (`/wp-json/wc/store/...` i WC Store “products” endpoint),
  - `humidor.hr` je ranije čitao preko HTML-a (kategorije), ali u ovom okruženju je dokazivo dostupna i WooCommerce Store API varijanta.
- Postoji policy/iskustvo da masovni HEAD/GET sweep Humidor URL-ova može vratiti **429** (rate-limit), pa se to ne smije interpretirati kao “dead link”.

## Scope

### U scopeu

- Raw katalozi za sljedeće domene:
  - **HR**: `humidor.hr`, `havana-cigar-shop.com`
  - **EU**: `cigarworld.de`
  - **USA**: `holts.com`, `cigarsdaily.com`
- Standardizirani format izlaznog JSON-a po shopu.
- Deterministična obrada: caching + rate-limit + retry/backoff.
- Minimalno parsiranje koje je stabilno na promjene UI-a (prefer API/sitemap/JSON-LD nad “scrape HTML layouta”).

### Izvan scopea (non-goals)

- Ne radimo “live scraping” u runtimeu aplikacije.
- Ne radimo automatski merge u `cigars.json` u ovoj fazi.
- Ne pokušavamo “probiti” anti-bot izazove (npr. Cloudflare JS challenge) putem browser automatizacije.

## Ključna zapažanja (evidencija iz ovog okruženja)

- `cigarsdaily.com/` vraća 403 i Cloudflare “Just a moment…” HTML challenge, ali:
  - `https://cigarsdaily.com/wp-json/wc/store/products?per_page=...` vraća 200 i JSON proizvode (cijene, stock, permalink).
- `humidor.hr` i `havana-cigar-shop.com` imaju dostupne WP/WooCommerce JSON endpointove:
  - `https://humidor.hr/wp-json/wc/store/products?...` → 200
  - `https://havana-cigar-shop.com/wp-json/wc/store/products?...` → 200
- `holts.com` i `cigarworld.de` imaju javno dostupne sitemapove:
  - `https://www.holts.com/sitemap.xml` → 200
  - `https://www.cigarworld.de/sitemap.xml` → index (DE/EN), te `https://www.cigarworld.de/sitemap_en.xml` s URL-ovima sadržaja/proizvoda.

## Dizajn: data model (standardizirani raw format)

Za svaki shop generira se jedan JSON:

- Lokacija: `app/scripts/output/cigar_shop_<shop_id>_raw.json`
- `shop_id`:
  - `humidor_hr`
  - `havana_hr`
  - `cigarworld_eu`
  - `holts_us`
  - `cigarsdaily_us`

### JSON schema (konceptualno)

```json
{
  "shop": {
    "id": "humidor_hr",
    "name": "The Humidor",
    "region": "HR",
    "baseUrl": "https://humidor.hr"
  },
  "scrapedAt": "2026-07-21T15:00:00Z",
  "currency": "EUR",
  "source": {
    "kind": "woocommerce-store-api | sitemap+jsonld | sitemap+html",
    "entrypoints": ["..."]
  },
  "items": [
    {
      "id": "shop-local-id-or-slug",
      "name": "Product title as displayed",
      "url": "https://...",
      "price": {
        "amount": 12.0,
        "currency": "EUR"
      },
      "availability": {
        "inStock": true,
        "onSale": false
      },
      "packaging": {
        "type": "single | 5-pack | box | sampler | unknown",
        "count": 1
      },
      "attributes": {
        "brand": "best-effort",
        "vitola": "best-effort",
        "dimensions": {
          "lengthIn": 6.0,
          "ringGauge": 54
        }
      },
      "categories": [
        { "name": "Cigars", "slug": "cigars", "url": "https://..." }
      ],
      "images": [
        { "src": "https://...", "alt": "" }
      ],
      "raw": {
        "sourcePayload": "optional: subset of vendor json"
      }
    }
  ]
}
```

**Napomena:** `attributes.brand/vitola/dimensions` su *best-effort* i služe kasnijem mapiranju; nije cilj savršeno parsirati sve varijante pakiranja u ovoj fazi.

## Dizajn: strategija po shopu

### 1) `humidor.hr` (HR) — WooCommerce Store API (preferirano)

- **Primarni izvor:** `GET /wp-json/wc/store/products` (paginacija) + opcionalno kategorije iz `/wp-json/wc/store/products/categories`.
- Prednosti:
  - stabilno (ne ovisi o HTML layoutu),
  - uključuje cijene i `is_in_stock`,
  - lakše rate-limitati.
- Filtriranje:
  - zadržati samo artikle koji su cigare (po kategoriji slug-u ili path-u).

### 2) `havana-cigar-shop.com` (HR) — WooCommerce Store API

- **Primarni izvor:** `GET /wp-json/wc/store/products` (paginacija).
- Dodatno:
  - fallback na postojeći WC store endpoint koji repo već koristi, ali standardizirati izlaz u gore opisani raw format.

### 3) `cigarsdaily.com` (USA) — WooCommerce Store API (izbjegava Cloudflare HTML challenge)

- **Izbjegavati** scraping homepage-a i HTML rute zbog 403/Cloudflare challenge.
- **Primarni izvor:** `GET /wp-json/wc/store/products` + `/categories`.
- Očekivanja:
  - USD cijene, varijabilni proizvodi (varijacije “Single / 5 Pack / Pack of 20”) dostupni kroz Store API.

### 4) `holts.com` (USA) — sitemap → product pages → JSON-LD extraction (preferirano)

- **Primarni izvor URL-ova:** `https://www.holts.com/sitemap.xml`.
- Zatim:
  - iz sitemap-a filtrirati URL-ove za cigare/brandove i, gdje je moguće, product-detail rute.
  - za product-detail stranice preferirati ekstrakciju iz `<script type="application/ld+json">` (Product schema), jer je stabilnija od CSS selektora.
- Ako JSON-LD nije dovoljan:
  - minimalni HTML fallback (npr. title + price), uz jasne “unknown” vrijednosti gdje podatak nije pouzdan.

### 5) `cigarworld.de` (EU) — sitemap_en → product pages → JSON-LD extraction

- **Primarni izvor URL-ova:** `https://www.cigarworld.de/sitemap.xml` → `sitemap_en.xml`.
- Filtrirati EN rute relevantne za proizvode (tipično `/en/zigarren/...`).
- Za product-detail stranice:
  - preferirati JSON-LD extraction (Product schema) za naziv/cijenu/stock/link.
  - HTML fallback samo ako JSON-LD nedostaje ili je nepotpun.

## Operativni zahtjevi (da bude “agent-friendly” i ponovljivo)

- **Rate limiting**
  - globalno po domeni (npr. 1–2 req/s) + jitter.
  - 429/503: exponential backoff (npr. 2s, 4s, 8s…) s capom.
- **Caching**
  - local disk cache (`.cache/` pod `app/scripts/`) keyed po URL-u i queryju,
  - TTL (npr. 24h) uz opciju `--no-cache`.
- **Idempotentnost**
  - izlazni JSON se regenerira deterministički za isti input (cache on),
  - stabilan sorting `items` (npr. po URL-u ili id-u).
- **Bez inline importa**: Python/TS importi na vrhu modula (workspace rule).

## CLI / UX dizajn (skripte)

Dodati novu skriptu koja može:

- `python app/scripts/scrape-cigar-shops.py --shop humidor_hr --out app/scripts/output/...`
- `--shop all` za sve
- `--limit N` za probe
- `--since-cache` / `--no-cache`
- `--verbose`

## Testiranje / verifikacija

- Minimalna provjera u skripti:
  - output JSON validan i sadrži `shop`, `scrapedAt`, `items[]`.
  - za WooCommerce izvore: `items` nije prazan (osim ako `--limit 0`).
- (Opcionalno kasnije) vitest/jest nije nužan za raw export; dovoljno je da skripta radi i da output ima očekivani shape.

## Rizici i mitigacije

- **Anti-bot / Cloudflare**: ne koristiti Playwright za zaobilaženje challenge-a; koristiti dostupne API-je (cigarsdaily) ili sitemap+JSON-LD (holts/cigarworld).
- **Rate limit (429)**: obavezno ugraditi backoff i ne raditi masovni sweep bez throttle-a.
- **Strukturne promjene HTML-a**: osloniti se na JSON-LD gdje god je moguće.

## “Definition of done” (za ovu fazu)

1. Nova skripta (`scrape-cigar-shops.py`) koja generira raw JSON za svaki shop iz scopea.
2. Output datoteke u `app/scripts/output/` (git-ignorirane, ako repo već tako tretira `output/`).
3. Dokumentirano kako pokrenuti scrape i što output sadrži.

