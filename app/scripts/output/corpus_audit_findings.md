# Corpus audit findings

## Line display cleanup (`fix/cigar-line-display-cleanup`)

### Auto-fixed

- Decoded HTML entities in `line` / `vitola` (`&amp;` to `&`, `&quot;` to `"`, `&#215;` to `x`).
- Stripped dangling `&` brand tails after incomplete brand strip (20 lines).
- Integrity follow-ups after decode: El Vinyet `5x52` to `Robusto` (dim-only line); Mexico `"01"` quotes removed (`Mexico 01 Small Batch Nat. Sumatra`) so digit-inch false positive does not fail integrity.
- Same-class: `Heaven& Hell` to `Heaven & Hell` (Oscar Valladares).
- Taxonomy baselines refreshed to decoded/cleaned line keys (fail-on-new stays green without re-encoding).
- Permanent cleaners: `build-market-cigars.canon_line` / `_clean` and `sync-hr-shops.line_name_from_product` unescape + strip leading `&` / brand-tail.
- Notes HR translated (market_note style): Bolivar Regional & Special, Padron 1964 Anniversary Series, Padron Damaso.

### Line before to after (30)

- `cig-7-20-4-hustler-five-amp-dime`: `Hustler Five &amp; Dime` to `Hustler Five & Dime`
- `cig-black-works-studio-s-amp-r`: `Studio S&amp;R` to `Studio S&R`
- `cig-carlos-amp-maria-amorio`: `&amp; Maria Amorio` to `Maria Amorio`
- `cig-cornelius-amp-anthony-daddy-mac`: `&amp; Anthony Daddy Mac` to `Daddy Mac`
- `cig-cornelius-amp-anthony-meridian`: `&amp; Anthony Meridian` to `Meridian`
- `cig-el-vinyet-5-215-52`: `5&#215;52` to `Robusto`
- `cig-factory-overrun-mexico-quot-01-quot-small-batch-nat-sumatra`: `Mexico &quot;01&quot; Small Batch Nat. Sumatra` to `Mexico 01 Small Batch Nat. Sumatra`
- `cig-hernandez-amp-ruiz`: `&amp; Ruiz` to `Ruiz`
- `cig-hiram-amp-solomon-entered-apprentice-connecticut`: `&amp; Solomon Entered Apprentice Connecticut` to `Entered Apprentice Connecticut`
- `cig-hiram-amp-solomon-entered-apprentice-limited-edition-heart-amp-soul`: `&amp; Solomon Entered Apprentice Limited Edition Heart &amp; Soul` to `Entered Apprentice Limited Edition Heart & Soul`
- `cig-hiram-amp-solomon-fellow-craft-oscuro`: `&amp; Solomon Fellow Craft Oscuro` to `Fellow Craft Oscuro`
- `cig-hiram-amp-solomon-master-mason`: `&amp; Solomon Master Mason` to `Master Mason`
- `cig-hiram-amp-solomon-traveling-man`: `&amp; Solomon Traveling Man` to `Traveling Man`
- `cig-leite-amp-alves-arapiraca`: `&amp; Alves Arapiraca` to `Arapiraca`
- `cig-leite-amp-alves-mata-sul`: `&amp; Alves Mata Sul` to `Mata Sul`
- `cig-leite-amp-alves-stalk-cut`: `&amp; Alves Stalk Cut` to `Stalk Cut`
- `cig-oscar-valladares-heaven-hell-claro`: `Heaven& Hell Claro` to `Heaven & Hell Claro`
- `cig-oscar-valladares-heaven-hell-oscuro`: `Heaven& Hell Oscuro` to `Heaven & Hell Oscuro`
- `cig-partageno-amp-corona-brasil`: `&amp; Corona Brasil` to `Corona Brasil`
- `cig-partageno-amp-corona-robust-corona-brasil`: `&amp; Corona Robust Corona Brasil` to `Corona Robust Corona Brasil`
- `cig-partageno-amp-corona-robust-corona-sumatra`: `&amp; Corona Robust Corona Sumatra` to `Corona Robust Corona Sumatra`
- `cig-partageno-amp-corona-slanke-brasil`: `&amp; Corona Slanke Brasil` to `Corona Slanke Brasil`
- `cig-partageno-amp-corona-slanke-sumatra`: `&amp; Corona Slanke Sumatra` to `Corona Slanke Sumatra`
- `cig-partageno-amp-corona-small-brasil`: `&amp; Corona Small Brasil` to `Corona Small Brasil`
- `cig-partageno-amp-corona-small-sumatra`: `&amp; Corona Small Sumatra` to `Corona Small Sumatra`
- `cig-partageno-amp-corona-sumatra`: `&amp; Corona Sumatra` to `Corona Sumatra`
- `cig-partageno-panatela-amp-corona-brasil`: `Panatela &amp; Corona Brasil` to `Panatela & Corona Brasil`
- `cig-partageno-panatela-amp-corona-fehlfarben-brasil`: `Panatela &amp; Corona Fehlfarben Brasil` to `Panatela & Corona Fehlfarben Brasil`
- `cig-partageno-panatela-amp-corona-fehlfarben-sumatra`: `Panatela &amp; Corona Fehlfarben Sumatra` to `Panatela & Corona Fehlfarben Sumatra`
- `cig-partageno-panatela-amp-corona-sumatra`: `Panatela &amp; Corona Sumatra` to `Panatela & Corona Sumatra`

### Review (not invented in this PR)

- Brand rename candidates (truncated brand left `& Surname` residue): `Carlos` + line `Maria Amorio` (likely Carlos & Maria); `Hernandez` + line `Ruiz` (likely Hernandez & Ruiz). Leading `&` removed; brand merge deferred.
- Partageno `& Corona ...` to `Corona ...` (product family; brand stays Partageno).
- Taxonomy `my-father.json`: only renamed dangling key `& Tatuaje 'La Union' Red Especial` to `La Union Red Especial` (nested line already correct). Did not rewrite intentional alias keys (`#2`, `Classic No. 1`, ...).
- Out of scope here: EU/USA markets cleanup, P1 La Aroma merge, blurb translations, outliers.
