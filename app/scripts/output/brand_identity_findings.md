# Brand identity findings — 2026-07-25

Scope: Don Pepin / Don Pépin García unify, Carlos split, Hernandez & Ruiz rename.
Method: taxonomy `renameBrand` + line remaps (+ per-line `brand` override in `apply-taxonomy.py`); no hand edits to `cigars.json`.

## Applied (sourced)

### Don Pépin García
- **Unify** catalogue key `Don Pepin` → brand `Don Pépin García`.
- **Dedup merges:** Original; E.R.H. / E.R.H; Series JJ Selectos + Series JJ Sublimes + Serie JJ → **Series JJ**.
- **Strip** redundant `Pepin Garcia ` / `Don Pepin Garcia ` line prefixes.
- **Keep distinct:** Clasicos 1950/1979, VC, Limited Edition Original 20th Anniversary 2023, 15th/20th/Clasico 20th Anniversary, Cuban Classic, Vegas Cubanas, Vintage, Series JJ Limited Edition 2025.
- Sources: [halfwheel E.R.H.](https://halfwheel.com/my-fathers-el-rey-de-los-habanos-returns/444463/), [halfwheel Series JJ](https://halfwheel.com/don-pepin-garcia-series-jj-20th-anniversary-ships/453053/), [My Father E.R.H.](https://myfathercigars.com/cigar/don-pepin-garcia-e-r-h/), [Holt’s Original](https://www.holts.com/cigars/all-cigar-brands/don-pepin-garcia-original.html), CigarWorld Don Pepin EU pages.

### Carlos André
- Lines `André Airborne` / `André Cast Off` / `André Pace` → brand **Carlos André**, lines **Airborne** / **Cast Off** / **Pace**.
- Sources: [carlos-andre.com brand](https://www.carlos-andre.com/en/brand/), [Airborne](https://www.carlos-andre.com/en/cigars/airborne/), [Cast Off](https://www.carlos-andre.com/en/cigars/cast-off/), [cigarworld.de/carlos-andre](https://www.cigarworld.de/en/carlos-andre).

### Carlos & Maria · Amorio
- Catalogue mash `Carlos` + `Maria Amorio` is **not** Arnold André.
- Brand **Carlos & Maria**, line **Amorio** (Freud Cigar Co.; El Maestro / Wiber Ventura).
- Sources: [halfwheel shipping](https://halfwheel.com/freuds-carlos-maria-amorio-begins-shipping/429872/), [halfwheel review](https://halfwheel.com/carlos-maria-amorio-corona-gorda/437615/), [cigarworld.de](https://www.cigarworld.de/en/zigarren/dominikanische-republik/carlos-amp-maria-amorio-90017277), [freudcigars.com](https://freudcigars.com/carlos-maria/amorio/).

### Hernandez & Ruiz
- Full brand name **Hernandez & Ruiz** (Panama; Tabacalera H & R; Paul Bugge DE from 13.09.2012).
- Single-series catalogue → line equals brand (class H).
- Sources: [cigarworld.de](https://www.cigarworld.de/en/zigarren/panama/hernandez-ruiz-90012340), [paul-bugge.com](https://www.paul-bugge.com/zigarren/panama/hernandez-y-ruiz/1700), [noblego.de](https://www.noblego.de/hernandez-und-ruiz-zigarren/).

## Notes / residual (not blocking)

| Item | Decision | Why |
| --- | --- | --- |
| Series JJ vs Serie JJ | Canonical **Series JJ** | My Father / halfwheel English usage; EU CigarWorld “Series JJ” |
| Amorío accent | Line stored as **Amorio** | Matches prior ASCII catalogue; brand materials use Amorío |
| Hernández / Ruíz accents | Brand **Hernandez & Ruiz** without accents | Matches CigarWorld EN + Paul Bugge shop titles |
| VC vs Vegas Cubanas | Kept **separate** | Explicit keep list; no sourced proof they are the same line |
| Clasicos / VC / LE 20th IDs | Kept stable `cig-don-pepin-*` where line unchanged | apply-taxonomy stable-id rule; still under brand Don Pépin García |

## Engine note
`apply-taxonomy.py` line specs may set `"brand"` for per-line brand splits (Carlos → Carlos André vs Carlos & Maria). Global `renameBrand` alone cannot split one truncated key into two makers.
