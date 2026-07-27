# Drink reference pass — Wine-Searcher + Drinkology

**Date:** 2026-07-27  
**Branch:** `research/digestifs-regional-liqueurs` (also useful beyond digestifs)  
**Sources added to Club:** [`app/src/data/clubSources.json`](../../app/src/data/clubSources.json)

| Source | Role |
|--------|------|
| [Wine-Searcher — Spirits](https://www.wine-searcher.com/spirits) | Taxonomy, legal/style definitions, serve notes, critic/producer notes |
| [Drinkology](https://www.drinkology.de) | EU shop + blog lexicon (Weinbrand, whisky categories, fortified wines, tequila ages, genever, grappa, bitters) |

**Scope:** all app drink categories (rum, whisky, brandy, wine, coffee, tequila, gin) plus herbal/digestif adjacency.  
**Not used as:** price truth for HR shops (AlleZ / Ecuga remain buy-link sources) or invented tasting notes for catalog bottles.

---

## Method

1. Domain-restricted search across both sites for each `DrinkCategory` + fortified wine + herbal/liqueur/bitters.  
2. Fetch category / blog pages for definitions and production contrasts.  
3. Diff against `app/src/data/dictionary.json` (drink entries) and `club.json` facts.  
4. Fill glossary gaps where catalog already has SKUs but dictionary lacked a term; strengthen defs with source-backed production facts only.

---

## What the sources cover well (by app category)

### Rum
- [Wine-Searcher — Rhum Agricole](https://www.wine-searcher.com/spirit-2233-rhum-agricole): cane **juice** vs molasses; generally dry / little added sugar; Martinique AOP context.  
- [Wine-Searcher — Cachaça](https://www.wine-searcher.com/spirit-2022-cachaca): Brazilian cane-juice spirit; white vs aged (ouro); Brazil classifies as *aguardente de cana*.  
- Drinkology blog [Rum in aller Kürze](https://www.drinkology.de/blog/Rum-in-aller-Kuerze): short EU-facing rum overview (shop taxonomy).

**App gap closed:** dictionary `cachaca` (catalog has 10 cachaça SKUs). Club already taught cane-juice vs molasses.

### Whisky
- [Single malt](https://www.wine-searcher.com/spirit-2281-whisky-single-malt): one distillery, malted barley, Scotch regs (3yr oak, E150a allowed).  
- [Bourbon](https://www.wine-searcher.com/spirit-2029-whiskey-bourbon): ≥51% corn; charred **new** oak; vanilla/sweetness from cask; serve neat/rocks/cola/ginger.  
- [Blended whiskey](https://www.wine-searcher.com/spirit-1748-whiskey-blended): malleable house style; not automatically “inferior”; blended malt ≠ malt+grain.  
- [Drinkology whisky hub](https://www.drinkology.de/whisky): malt / blend / bourbon / Tennessee (charcoal) / rye (≥51%) / grain / pot still.

**App gap closed:** `blended-whisky`, `tennessee-whiskey`. Bourbon dictionary def aligned with 51% + new charred oak (already in Club facts).

### Brandy / eaux-de-vie
- [Wine-Searcher Cognac region](https://www.wine-searcher.com/regions-cognac): Charentais; Ugni Blanc dominance; pot still vs Armagnac continuous; drop of water opens fruit.  
- Drinkology [Weinbrand – International](https://www.drinkology.de/blog/Weinbrand-International): Cognac crus, Armagnac history/still, Spanish *holandas* + sherry butts, Italian min 38%, Metaxa ≠ brandy under EU framing, Deutscher Weinbrand naming.  
- [Drinkology Grappa](https://www.drinkology.de/en/Digestif/Grappa/): pomace; clear vs barrel-aged; monovitigno; Nonino quality arc.  
- [Wine-Searcher Pisco](https://www.wine-searcher.com/spirit-2025-pisco): grape brandy PE/CL — still outside pairing catalog (by design).

**App gap closed:** dictionary `grappa` (8 grappa brandies in catalog). Pisco remains deferred (digestif audit phase 2).

### Wine (fortified + table adjacency)
- [What are Fortified Wines?](https://www.wine-searcher.com/select/what-is-fortified-wine): spirit addition; timing → sweetness; Port/Sherry/Madeira/Marsala/Vermouth family.  
- Drinkology [Gespritete Weine: Port und Sherry](https://www.drinkology.de/blog/Gespritete-Weine-Port-und-Sherry): **Port fortified mid-ferment**; **Sherry fully fermented then fortified**; flor / solera; Fino, Manzanilla, Oloroso, Amontillado, Cream, PX.

**App gap closed:** dictionary `fortified-wine`; Club fact contrasting Sherry vs Port fortification timing; Port/Sherry dictionary bodies sharpened.

### Tequila / mezcal
- [Tequila](https://www.wine-searcher.com/spirit-2027-tequila) / [Mezcal](https://www.wine-searcher.com/spirit-2024-mezcal): DO zones; Weber blue vs many agaves; steam oven vs pit roast; mezcal traditionally **neat, sipped**, water on side.  
- Drinkology [Tequila; ganz ohne roten Hut](https://www.drinkology.de/en/blog/Tequila-ganz-ohne-roten-Hut): Blanco / Reposado (2–12 mo) / Añejo (≥1 yr) / Extra Añejo (≥3 yr); 100% agave vs mixto culture.

**App change:** mezcal dictionary body strengthened (family vs tequila + serve). Club already covered 51% / 100% agave.

### Gin
- [Wine-Searcher Gin](https://www.wine-searcher.com/spirit-2023-gin): juniper-defining; Plymouth PGI; G&T ratios; botanical → mixer logic.  
- Drinkology [Plymouth Gin](https://www.drinkology.de/plymouth-gin-1-0l-41-2-196) / [Navy Strength](https://www.drinkology.de/en/Plymouth-Gin-Navy-Strength-0-7-L-57/PD-02399): PGI Plymouth only; ~41.2% classic; 57% navy.  
- [Genever](https://www.drinkology.de/en/Genever/): ancestor of dry gin; oude / jonge / corenwijn; often neat, lightly chilled in NL.

**App gap closed:** `plymouth-gin`, `genever` (catalog has 4 Plymouth SKUs; Club already taught genever/Plymouth).

### Coffee
- Wine-Searcher lists [Liqueur – Coffee](https://www.wine-searcher.com/spirits) as coffee-flavoured liqueur — **not** brew coffee.  
- Drinkology has little on espresso/filter ritual relevant to our `coffees.json`.

**Verdict:** no coffee dictionary change from these two sites; keep Club101 / existing coffee entries as authority for brew styles.

### Herbal / bitters / digestif (feeds shortlist)
- [Wine-Searcher Bitters](https://www.wine-searcher.com/spirit-2201-bitters): aperitif bitters vs digestifs/amaro vs cocktail bitters; Averna vs Fernet intensity; Unicum / Jägermeister framing.  
- Style bucket **Liqueur – Herb – Spice** for Becherovka, Unicum, Strega, Benedictine, Chartreuse, Galliano, pelinkovac (Badel Antique on WS).  
- Drinkology [Bitter aisle](https://www.drinkology.de/en/Aperitif/Bitter/): national map (IT Averna/Fernet, FR Chartreuse, HU Unicum…); [Chartreuse Verte 55%](https://www.drinkology.de/chartreuse-verte-0-7-l-55-2258) (~130 herbs); [Averna 29%](https://www.drinkology.de/en/Averna-Amaro-Siciliano-Bitter-1-0L-29/PD-04995); [Benedictine 40%](https://www.drinkology.de/en/Benedictine-Dom-Liqueur-1-L-40/PD-01052).

**Note:** botanical **counts** differ by source (e.g. Benedictine 27 on Drinkology vs 56 on Wine-Searcher producer notes). Do **not** hard-code disputed counts into pairing JSON; prefer ABV + style family.

Cross-link: [`DIGESTIF-REGIONAL-AUDIT.md`](DIGESTIF-REGIONAL-AUDIT.md).

---

## App actions taken (this pass)

| Asset | Change |
|-------|--------|
| `clubSources.json` | + Wine-Searcher (spirits), + Drinkology |
| `dictionary.json` | **New:** `blended-whisky`, `cachaca`, `fortified-wine`, `genever`, `grappa`, `plymouth-gin`, `tennessee-whiskey`. **Strengthened:** `bourbon`, `mezcal`, `port`, `sherry`; seeAlso links from `gin-london-dry` |
| `club.json` | + fact: Sherry fermented fully then fortified (contrast with Port) |
| This audit | Evidence map for future catalog / Club101 work |

## Explicitly **not** done

- No new `DrinkCategory` / `digestifs.json` (still awaiting design approval).  
- No ABV/price rewrites on existing rum/whisky/… JSON from foreign list prices.  
- No Coffee brew rewrite from liqueur pages.  
- No Metaxa reclassification (Drinkology notes EU “not brandy” — Club/brandy catalog already use `brandy-greek`).

---

## Suggested next lookups (same sources)

1. Per shortlist bottle: WS find pages for ABV + Herb–Spice confirmation when seeding `digestifs.json`.  
2. Armagnac vs Cognac distillation contrast → optional Club101 brandy card.  
3. Drinkology Cognac aging labels — **re-check current BNIC XO age** before quoting years (older blogs may lag regulation).
