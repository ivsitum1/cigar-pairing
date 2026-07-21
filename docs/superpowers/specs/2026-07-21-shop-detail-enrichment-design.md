# Shop detail enrichment (Humidor + Cigarworld)

**Datum:** 2026-07-21  
**Status:** approved (user: “kako ti kažeš”)  
**Cilj:** drugi krug scrape-a koji iz product pages izvlači wrapper/binder/filler (i srodne specifikacije) za Humidor i Cigarworld.

## Odlučeno

- **Humidor**: zamijeniti WooCommerce Store API listing s HTML kategorijom `…/kategorija-proizvoda/cigare/` + product-page `SPECIFIKACIJE` (jer WC categories API je nestabilan/Cloudflare, a WC listing je ranije vukao i pipe-ove).
- **Cigarworld**: zadržati sitemap + JSON-LD (cijene/stock), te iz istog product HTML-a parsirati `VariantInfo` (wrapper/binder/filler origin, ring, size…).

## Polja koja se skupljaju

### Humidor (`product-specs-grid`)

- Length (inch + cm)
- Diameter / Ring
- Wrapper Type
- Binder
- Filler
- Origin
- Strength (aria-label `N/5`)
- Burning Time (min)
- Brand label (iz listing/product pagea, ako postoji)

### Cigarworld (`VariantInfo-item`)

- Size
- Ring / Diameter
- Wrapper origin
- Binder origin
- Filler origin
- Boxpressed
- Flavoured
- Tabacalera

## Output shape

Svaki raw `item` dobiva:

```json
{
  "details": {
    "wrapper": "…",
    "binder": "…",
    "filler": "…",
    "origin": "…",
    "strength": 3,
    "burnTimeMin": 75,
    "size": "Robusto",
    "ringGauge": 50,
    "lengthIn": 6.0,
    "lengthCm": 15.2,
    "diameterCm": 1.91,
    "boxPressed": false,
    "flavoured": false,
    "tabacalera": "…",
    "brandLabel": "…"
  },
  "detailsSource": {
    "url": "https://…",
    "extractedFrom": "humidor-product-specs|cigarworld-variantinfo",
    "extractedAt": "2026-07-21T…"
  }
}
```

Polja koja shop ne daje ostaju `null` (ne izmišljamo).

## Non-goals

- Merge u `app/src/data/cigars.json` u ovom prolazu.
- Playwright / zaobilaženje Cloudflare challenge-a.
