# Shop detail enrichment

**Datum:** 2026-07-21  
**Status:** done for Humidor, Cigarworld, Havana, Holts  
**Cilj:** raw shop scrape s wrapper/binder/filler (i srodnim specifikacijama) gdje shop to nudi.

## Shop strategije

| Shop | Listing | Details |
|------|---------|---------|
| **Humidor** | HTML kategorija `…/cigare/` | product-page `SPECIFIKACIJE` |
| **Cigarworld** | sitemap_en + JSON-LD | `VariantInfo` W/B/F |
| **Havana** | WooCommerce Store API | API `attributes` (Wrapper/Binder/Filler/Ring/Duljina/…) — bez ekstra HTTP |
| **Holts** | sitemap line pages (`/cigars/all-cigar-brands/*.html`) | PDP country/wrapper/strength + vitola tablica (single-stick cijena) |
| **CigarsDaily** | WooCommerce Store API | isti WC attribute parser (ako atributi postoje) |

## Polja

Zajednički `item.details`:

- wrapper, binder, filler, origin
- strength, burnTimeMin, size
- ringGauge, lengthIn, lengthCm, diameterCm
- boxPressed, flavoured, tabacalera, brandLabel

+ `detailsSource: { url, extractedFrom, extractedAt }`

## Napomene

- Holts rijetko ima binder/filler na line pageu (često samo wrapper + country).
- Holts item = jedna vitola na line pageu; URL ostaje line page, id je `url#vitola`.
- Havana W/B/F dolazi iz Store API list responsea — brzo i pouzdano.
