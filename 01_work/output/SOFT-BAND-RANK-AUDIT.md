# Soft-band ranking audit

**Generirano:** 2026-07-26T14:42:56.018Z
**Margin:** max − 5
**Day keys:** 7; **cycles:** 0, 1, 2
**Trajanje:** 81226 ms

## Opseg

| | |
|--|--|
| Pairable pića | 779 |
| Cigare | 2394 |

## Usporedba smjerova

| Smjer | % anchora gdje soft #1 rotira | Mean bandSize | bandSize==1 % |
|-------|-------------------------------|---------------|---------------|
| drink → cigara (ship) | 100.0% | 35.64 | 1.9% |
| cigar → piće (samo usporedba) | 100.0% | 3.25 | 3.7% |

Soft-band u oba smjera rotira #1 na **100%** anchora (7 day keys × 3 cycle). Drink→cigara ima **širi** pojas (mean bandSize 35.64 vs 3.25) — zato je mehanizam primjereniji za shipani smjer; cigar→piće ostaje na starom UI mehanizmu.

**Score gate:** drink→cigara bandSize==1 ispod 40% — formula ostaje netaknuta.

Napomena: kad je `bandSize < 3`, UI pada na brand-diverse listu (kao prije); day seed i cycle tada rotiraju taj širi pool — zato „sticky soft” tablica može biti prazna iako baseline ima jake favorite.

## Drink → cigara (proizvod)

| Metrika | Vrijednost |
|---------|------------|
| Anchora | 779 |
| Mean bandSize | 35.64 |
| bandSize == 1 | 15 (1.9%) |
| bandSize 2–5 | 189 (24.3%) |
| bandSize ≥ 6 | 575 (73.8%) |
| Soft #1 mijenja se (≥1× u 7 dana × 3 cycle) | 779 (100.0%) |
| Mean score u soft prozoru | 87.86 |
| Score follow-up gate (bandSize==1 > 40%) | NE (1.9%) |

### Top-20 sticky baseline #1 (cigara)

| # | Id | Label | Anchora |
|---|----|-------|---------|
| 1 | `cig-black-works-studio-hyena` | Black Works Studio Studio Hyena | 83 (10.7%) |
| 2 | `cig-san-cristobal-de-la-habana-regular-production` | San Cristóbal de la Habana Regular Production | 80 (10.3%) |
| 3 | `cig-drew-estate-acid` | Drew Estate Acid | 72 (9.2%) |
| 4 | `cig-aj-fernandez-last-call` | AJ Fernandez Last Call | 45 (5.8%) |
| 5 | `cig-perdomo-10th-anniversary-champagne` | Perdomo 10th Anniversary Champagne | 39 (5.0%) |
| 6 | `cig-flor-de-selva-grand-presse-maduro` | Flor de Selva Grand Presse Maduro | 34 (4.4%) |
| 7 | `cig-quai-d-orsay-clasica` | Quai d'Orsay Clásica | 33 (4.2%) |
| 8 | `cig-partagas-clasica` | Partagás Clásica | 30 (3.9%) |
| 9 | `cig-balmoral-dominican-selection` | Balmoral Dominican Selection | 29 (3.7%) |
| 10 | `cig-e-p-carrillo-la-historia` | E.P. Carrillo La Historia | 23 (3.0%) |
| 11 | `cig-black-label-trading-company-morph-vintage-2020` | Black Label Trading Company Morph Vintage 2020 | 23 (3.0%) |
| 12 | `cig-7-20-4-hustler-five-amp-dime` | 7-20-4 Hustler Five & Dime | 21 (2.7%) |
| 13 | `cig-cohiba-linea-clasica` | Cohiba Línea Clásica | 20 (2.6%) |
| 14 | `cig-black-label-trading-company-royalty` | Black Label Trading Company Royalty | 17 (2.2%) |
| 15 | `cig-partagas-linea-maestra` | Partagás Línea Maestra | 16 (2.1%) |
| 16 | `cig-cohiba-siglo` | Cohiba Siglo | 14 (1.8%) |
| 17 | `cig-1502-emerald` | 1502 Emerald | 12 (1.5%) |
| 18 | `cig-ashton-heritage` | Ashton Heritage | 12 (1.5%) |
| 19 | `cig-drew-estate-undercrown-shade` | Drew Estate Undercrown Shade | 12 (1.5%) |
| 20 | `cig-aganorsa-leaf-la-validacion-maduro` | Aganorsa Leaf La Validación Maduro | 12 (1.5%) |

### Top-20 sticky soft-band #1 (nikad ne rotira)

*(prazno — soft #1 rotira na 100% anchora u ovom uzorku day/cycle)*

## Cigar → piće (usporedba; diversity key = category)

| Metrika | Vrijednost |
|---------|------------|
| Anchora | 2394 |
| Mean bandSize | 3.25 |
| bandSize == 1 | 89 (3.7%) |
| bandSize 2–5 | 2276 (95.1%) |
| bandSize ≥ 6 | 29 (1.2%) |
| Soft #1 mijenja se (≥1× u 7 dana × 3 cycle) | 2394 (100.0%) |
| Mean score u soft prozoru | 82.24 |
| Score follow-up gate (bandSize==1 > 40%) | NE (3.7%) |

### Top-20 sticky baseline #1 (piće)

| # | Id | Label | Anchora |
|---|----|-------|---------|
| 1 | `br-frapin-vsop` | Frapin VSOP | 824 (34.4%) |
| 2 | `wine-franciacorta-ca-del-bosco` | Franciacorta Ca' del Bosco Cuvée Prestige | 318 (13.3%) |
| 3 | `wine-rieussec-sauternes` | Chateau Rieussec Sauternes | 221 (9.2%) |
| 4 | `cf-guatemala-antigua` | Gvatemala Antigua (medium) | 101 (4.2%) |
| 5 | `wine-antinori-tignanello` | Antinori Tignanello | 96 (4.0%) |
| 6 | `cf-espresso-cognac` | Espresso + cognac (corretto) | 88 (3.7%) |
| 7 | `cf-yemen-mocha` | Yemen Mocha (natural) | 81 (3.4%) |
| 8 | `cf-cuba-serrano` | Cubita / Cuba Serrano (dark) | 81 (3.4%) |
| 9 | `wh-woodford-reserve` | Woodford Reserve | 61 (2.5%) |
| 10 | `rum-ableforth-s-rumbullion` | Ableforth's Rumbullion! | 52 (2.2%) |
| 11 | `cf-jamaica-blue-mountain` | Jamaica Blue Mountain (medium) | 35 (1.5%) |
| 12 | `wine-tokaji-essencia` | Royal Tokaji Essencia | 34 (1.4%) |
| 13 | `wh-redbreast-21-yo-single-pot-still-irish-whiskey-46-vol-0-7l-u-drvenoj-poklon-kutiji` | Redbreast 21 YO | 33 (1.4%) |
| 14 | `wh-ardbeg-uigeadail` | Ardbeg Uigeadail | 29 (1.2%) |
| 15 | `wh-kavalan-solist-fino-sherry-cask-single-malt-whisky-57-8-vol-0-7-l-u-drvenoj-poklon-kutiji` | Kavalan SOLIST FINO SHERRY CASK | 29 (1.2%) |
| 16 | `rum-foursquare-ecs-detente-2005` | Foursquare ECS (Exceptional Cask Selection) | 25 (1.0%) |
| 17 | `wh-auchentoshan-american-oak` | Auchentoshan American Oak | 24 (1.0%) |
| 18 | `wh-glendronach-15` | GlenDronach 15 Revival | 20 (0.8%) |
| 19 | `br-remy-martin-louis-xiii-cognac-fine-champagne-40-vol-0-7l-u-poklon-kutiji` | Rémy Martin LOUIS XIII Cognac Fine Champagne 40% Vol. 0,7l u poklon kutiji | 20 (0.8%) |
| 20 | `wh-benriach-27-yo-smoky-cask-edition-oloroso-sherry-vintage-1994-53-vol-0-7l-u-poklon-kutiji` | Benriach 27 YO Smoky CASK EDITION Oloroso Sherry Vintage 1994 | 17 (0.7%) |

### Top-20 sticky soft-band #1 (nikad ne rotira)

*(prazno — soft #1 rotira na 100% anchora u ovom uzorku day/cycle)*
