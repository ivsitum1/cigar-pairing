# Audit ocjena sparivanja (cigara × piće)

**Generirano:** 2026-07-22T21:10:54.618Z  
**Engine:** `scorePairing` bez osobnih preferencija (`prefs` isključeno)  
**Trajanje:** 43296 ms

## 1. Opseg

| Veličina | Vrijednost |
|----------|------------|
| Cigare (dedupe) | 3104 |
| Pairable pića | 633 |
| Parova (N) | **1964832** |

## 2. Deskriptivna statistika scorea (0–100)

| Stat | Vrijednost |
|------|------------|
| Mean (μ) | 48.8967 |
| Median | 48.00 |
| Mode | 68 (n=65095) |
| SD (σ) | 21.1766 |
| Variance | 448.4468 |
| Skewness | -0.1382 |
| Excess kurtosis | -0.5883 |
| Min | 0 |
| Max | 100 |
| P5 | 13.00 |
| P25 | 34.00 |
| P75 | 67.00 |
| P95 | 82.00 |
| IQR | 33.00 |

### Rubovi i pragovi kuriranih poruka

| Event | n | udio |
|-------|---|------|
| score = 0 | 29317 | 1.49% |
| score = 100 | 4006 | 0.20% |
| score ≥ 80 (pohvala) | 131343 | 6.68% |
| score ≤ 45 (upozorenje) | 911886 | 46.41% |

## 3. Gaussova pretpostavka

Fit: **N(μ=48.8967, σ²=448.4468)** s empirijskim momentima.

| Test | Rezultat |
|------|----------|
| Jarque–Bera | 34590.24 |
| JB reject α=0.05 (krit. 5.991) | DA |
| JB reject α=0.01 (krit. 9.210) | DA |
| χ² vs N(μ,σ) (binovi širine 5, spojeni E<5) | 243927.59 (df≈17) |
| Približni p (Wilson–Hilferty) | 0.0000 |

**Interpretacija:** Formalni Jarque–Bera **odbacuje** normalnost (α=0.05). To je očekivano pri n≈2.0×10⁶ zbog diskretnih scoreova, clampa, multimodalnosti (body-diff mješavina) i rule-mješavine.

Detektirano 13 lokalnih maksimuma (nakon glatke): 14, 20, 26, 31, 39, 46, 49, 56, 59, 65, 69, 77, 86 → distribucija nije strogo unimodalna.

Za rule-based aditivni score **nije** razumno očekivati strogi Gaus: baza 36, kazne u koracima od 12, capovi tagova i `clamp` stvaraju diskretnu mješavinu. „Bell-like“ oblik (unimodalnost, umjerena širina) može se pojaviti, ali formalni normalitet pri ovom N gotovo uvijek pada.

### χ² binovi (opaženo vs očekivano pod N)

| Raspon | Obs | Exp | Obs−Exp |
|--------|-----|-----|---------|
| 0–4 | 49521 | 16081.3 | 33439.7 |
| 5–9 | 36092 | 26321.4 | 9770.6 |
| 10–14 | 40190 | 40756.4 | -566.4 |
| 15–19 | 43375 | 59700.8 | -16325.8 |
| 20–24 | 60190 | 82730.4 | -22540.4 |
| 25–29 | 99130 | 108455.4 | -9325.4 |
| 30–34 | 166451 | 134505.2 | 31945.8 |
| 35–39 | 216387 | 157807.8 | 58579.2 |
| 40–44 | 170028 | 175153.0 | -5125.0 |
| 45–49 | 140897 | 183911.3 | -43014.3 |
| 50–54 | 113245 | 182683.7 | -69438.7 |
| 55–59 | 135599 | 171669.8 | -36070.8 |
| 60–64 | 119232 | 152611.9 | -33379.9 |
| 65–69 | 195897 | 128346.3 | 67550.7 |
| 70–74 | 159158 | 102112.7 | 57045.3 |
| 75–79 | 88097 | 76856.0 | 11241.0 |
| 80–84 | 63357 | 54723.9 | 8633.1 |
| 85–89 | 44323 | 36861.7 | 7461.3 |
| 90–94 | 12850 | 23489.4 | -10639.4 |
| 95–100 | 10813 | 16173.9 | -5360.9 |

### Histogram (grubo, korak 5)

| Raspon | n | udio |
|--------|---|------|
| 0–4 | 49521 | 2.52% |
| 5–9 | 36092 | 1.84% |
| 10–14 | 40190 | 2.05% |
| 15–19 | 43375 | 2.21% |
| 20–24 | 60190 | 3.06% |
| 25–29 | 99130 | 5.05% |
| 30–34 | 166451 | 8.47% |
| 35–39 | 216387 | 11.01% |
| 40–44 | 170028 | 8.65% |
| 45–49 | 140897 | 7.17% |
| 50–54 | 113245 | 5.76% |
| 55–59 | 135599 | 6.90% |
| 60–64 | 119232 | 6.07% |
| 65–69 | 195897 | 9.97% |
| 70–74 | 159158 | 8.10% |
| 75–79 | 88097 | 4.48% |
| 80–84 | 63357 | 3.22% |
| 85–89 | 44323 | 2.26% |
| 90–94 | 12850 | 0.65% |
| 95–99 | 6807 | 0.35% |
| 100–100 | 4006 | 0.20% |

<details><summary>Puni histogram po scoreu (0–100)</summary>

| Score | n | udio | bar |
|-------|---|------|-----|
| 0 | 29317 | 1.49% | ███ |
| 1 | 3424 | 0.17% |  |
| 2 | 3696 | 0.19% |  |
| 3 | 5302 | 0.27% | █ |
| 4 | 7782 | 0.40% | █ |
| 5 | 8321 | 0.42% | █ |
| 6 | 6108 | 0.31% | █ |
| 7 | 6435 | 0.33% | █ |
| 8 | 9215 | 0.47% | █ |
| 9 | 6013 | 0.31% | █ |
| 10 | 4122 | 0.21% |  |
| 11 | 2662 | 0.14% |  |
| 12 | 4892 | 0.25% |  |
| 13 | 12057 | 0.61% | █ |
| 14 | 16457 | 0.84% | ██ |
| 15 | 9492 | 0.48% | █ |
| 16 | 6508 | 0.33% | █ |
| 17 | 5822 | 0.30% | █ |
| 18 | 8812 | 0.45% | █ |
| 19 | 12741 | 0.65% | █ |
| 20 | 11242 | 0.57% | █ |
| 21 | 10718 | 0.55% | █ |
| 22 | 10635 | 0.54% | █ |
| 23 | 13063 | 0.66% | █ |
| 24 | 14532 | 0.74% | █ |
| 25 | 17416 | 0.89% | ██ |
| 26 | 21606 | 1.10% | ██ |
| 27 | 27414 | 1.40% | ███ |
| 28 | 15150 | 0.77% | ██ |
| 29 | 17544 | 0.89% | ██ |
| 30 | 36439 | 1.85% | ████ |
| 31 | 46195 | 2.35% | █████ |
| 32 | 38519 | 1.96% | ████ |
| 33 | 20844 | 1.06% | ██ |
| 34 | 24454 | 1.24% | ██ |
| 35 | 36549 | 1.86% | ████ |
| 36 | 36530 | 1.86% | ████ |
| 37 | 34132 | 1.74% | ███ |
| 38 | 45284 | 2.30% | █████ |
| 39 | 63892 | 3.25% | ███████ |
| 40 | 51709 | 2.63% | █████ |
| 41 | 44444 | 2.26% | █████ |
| 42 | 34200 | 1.74% | ███ |
| 43 | 22309 | 1.14% | ██ |
| 44 | 17366 | 0.88% | ██ |
| 45 | 30522 | 1.55% | ███ |
| 46 | 20998 | 1.07% | ██ |
| 47 | 28931 | 1.47% | ███ |
| 48 | 28964 | 1.47% | ███ |
| 49 | 31482 | 1.60% | ███ |
| 50 | 43585 | 2.22% | ████ |
| 51 | 24148 | 1.23% | ██ |
| 52 | 17920 | 0.91% | ██ |
| 53 | 13852 | 0.70% | █ |
| 54 | 13740 | 0.70% | █ |
| 55 | 37050 | 1.89% | ████ |
| 56 | 27267 | 1.39% | ███ |
| 57 | 31105 | 1.58% | ███ |
| 58 | 22265 | 1.13% | ██ |
| 59 | 17912 | 0.91% | ██ |
| 60 | 35722 | 1.82% | ████ |
| 61 | 16473 | 0.84% | ██ |
| 62 | 16578 | 0.84% | ██ |
| 63 | 17238 | 0.88% | ██ |
| 64 | 33221 | 1.69% | ███ |
| 65 | 23407 | 1.19% | ██ |
| 66 | 35538 | 1.81% | ████ |
| 67 | 31113 | 1.58% | ███ |
| 68 | 65095 | 3.31% | ███████ |
| 69 | 40744 | 2.07% | ████ |
| 70 | 54963 | 2.80% | ██████ |
| 71 | 44668 | 2.27% | █████ |
| 72 | 32389 | 1.65% | ███ |
| 73 | 15223 | 0.77% | ██ |
| 74 | 11915 | 0.61% | █ |
| 75 | 12862 | 0.65% | █ |
| 76 | 19283 | 0.98% | ██ |
| 77 | 21534 | 1.10% | ██ |
| 78 | 18524 | 0.94% | ██ |
| 79 | 15894 | 0.81% | ██ |
| 80 | 15919 | 0.81% | ██ |
| 81 | 13297 | 0.68% | █ |
| 82 | 14078 | 0.72% | █ |
| 83 | 11784 | 0.60% | █ |
| 84 | 8279 | 0.42% | █ |
| 85 | 8377 | 0.43% | █ |
| 86 | 11654 | 0.59% | █ |
| 87 | 10156 | 0.52% | █ |
| 88 | 7810 | 0.40% | █ |
| 89 | 6326 | 0.32% | █ |
| 90 | 5196 | 0.26% | █ |
| 91 | 2157 | 0.11% |  |
| 92 | 1955 | 0.10% |  |
| 93 | 1455 | 0.07% |  |
| 94 | 2087 | 0.11% |  |
| 95 | 2525 | 0.13% |  |
| 96 | 3182 | 0.16% |  |
| 97 | 872 | 0.04% |  |
| 98 | 195 | 0.01% |  |
| 99 | 33 | 0.00% |  |
| 100 | 4006 | 0.20% |  |

</details>

## 4. Matematika i logika mehanizma

### Teoretski vs empirijski raspon (raw prije clamp)

| | Vrijednost |
|--|------------|
| Teoretski min (neclamp, pretpostavke) | -46.0 |
| Teoretski max (neclamp, pretpostavke) | 128.0 |
| Empirijski raw min | -32.0 |
| Empirijski raw max | 122.0 |
| Parova s round(raw) < 0 (clamp dolje) | 27367 (1.39%) |
| Parova s round(raw) > 100 (clamp gore) | 3297 (0.17%) |

Težišta (`WEIGHTS`): base=36, bodyBonus=18, bodyPerStep=12, overwhelm=12, tagOverlap=7, tagComplement=5, contrastSweetMaduro=14, wrapperMatch=10, powerMatch=8, powerMismatch=10, qualityNudge=2.

### Invarijante (puna populacija)

| Provjera | Rezultat |
|----------|----------|
| Score izvan [0,100] | 0 |
| Ne-cjelobrojni score | 0 |
| Neslaganje reconstruktcije (base+reasons+quality−silentBodyDiff1 → clamp∘round) | 0 |
| Cap shared/complement > 3×težina | 0 |
| Body-monotonija (sintetički body 1–5, uzorak cigara) | 0 kršenja / 666 usporedbi |

### Dokumentirane asimetrije (nisu nužno bugovi)

1. **`qualityNudge`** ulazi u broj, ali **nema** `PairingReason` — UI zbroj razloga ≠ score.
2. **`bodyDiff === 1`**: kazna −12 bez reason; reason tek za `bodyDiff >= 2`.
3. **`clamp(round(raw), 0, 100)`**: saturacija na 0/100 skraćuje repove (anti-Gauss).
4. **Wrapper affinity**: samo prvi matching profil (`break`).
5. **Complement** zahtijeva `dt !== ct`, pa self-unosi u `COMPLEMENTS` ne double-countaju isti tag s `flavor-shared`.

## 5. Breakdown

### Mean score po kategoriji pića

| Kategorija | n parova | mean |
|------------|----------|------|
| brandy | 260736 | 54.85 |
| gin | 62080 | 53.73 |
| whisky | 862912 | 49.04 |
| tequila | 43456 | 48.92 |
| coffee | 102432 | 47.08 |
| rum | 456288 | 46.52 |
| wine | 176928 | 44.89 |

### Mean score po |Δbody|

| \|Δbody\| | n | mean |
|---------|---|------|
| 0 | 705599 | 71.22 |
| 1 | 917936 | 42.07 |
| 2 | 290092 | 23.69 |
| 3 | 47939 | 6.75 |
| 4 | 3266 | 1.24 |

### Frekvencija pravila (udio parova u kojima se rule pojavio)

| Rule | n | udio parova |
|------|---|-------------|
| flavor-complement | 1768469 | 90.01% |
| body-match | 705599 | 35.91% |
| flavor-shared | 600178 | 30.55% |
| wrapper-affinity | 538618 | 27.41% |
| body-mismatch | 341297 | 17.37% |
| strength-overwhelm | 62784 | 3.20% |
| power-match | 57552 | 2.93% |
| power-mismatch | 54208 | 2.76% |
| contrast-sweet-maduro | 29928 | 1.52% |

## 6. Ekstremi (top / bottom 20)

### Najbolji spojevi

| # | Score | Cigara | Piće | Rules |
|---|-------|--------|------|-------|
| 1 | 100 | 1502 Emerald (`cig-1502-emerald`) | Syrah / Shiraz (Rhone / Barossa) (`wine-syrah-shiraz`) | body-match, flavor-shared, flavor-complement, wrapper-affinity, power-match |
| 2 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Kavalan SOLIST FINO SHERRY CASK (`wh-kavalan-solist-fino-sherry-cask-single-malt-whisky-57-8-vol-0-7-l-u-drvenoj-poklon-kutiji`) | body-match, flavor-shared, flavor-complement, wrapper-affinity, power-match |
| 3 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Edradour 21 YO Oloroso Cask Finish 1995 (`wh-edradour-21-yo-oloroso-cask-finish-1995-56-2-vol-0-7l-u-poklon-kutiji`) | body-match, flavor-shared, flavor-complement, wrapper-affinity, power-match |
| 4 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Graham's Tawny Port 20 Y.O. (`wine-grahams-tawny-20`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 5 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Sandeman Tawny Port 20 Y.O. (`wine-sandeman-tawny-20`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 6 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Fonseca Bin No. 27 Reserve Ruby (`wine-fonseca-bin-27`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 7 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Blandy's Madeira 10 Y.O. (Bual/Malmsey) (`wine-blandys-madeira-10`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 8 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Prošek (Hvar/Dalmacija) (`wine-prosek-hvar`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 9 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Tokaji Aszú 5 Puttonyos (`wine-tokaji-aszu-5`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 10 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Sauternes (`wine-sauternes`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 11 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Moka pot (Bialetti) (`cf-moka-pot`) | body-match, flavor-shared, flavor-complement, wrapper-affinity |
| 12 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Cubita / Cuba Serrano (dark) (`cf-cuba-serrano`) | body-match, flavor-shared, flavor-complement, wrapper-affinity |
| 13 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | French press — tamna mješavina (`cf-french-press-dark`) | body-match, flavor-shared, flavor-complement, wrapper-affinity |
| 14 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Irish coffee (`cf-irish-coffee`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 15 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Carajillo / caffè corretto (s rumom ili brandyjem) (`cf-carajillo`) | body-match, flavor-shared, flavor-complement, wrapper-affinity |
| 16 | 100 | 7-20-4 Hustler Five &amp; Dime (`cig-7-20-4-hustler-five-amp-dime`) | Vijetnamska ledena kava (cà phê sữa đá) (`cf-vietnamese-iced`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 17 | 100 | 7-20-4 Robusto (`cig-7-20-4-robusto`) | Espresso — talijanska tamna mješavina (80/20) (`cf-espresso-italian-dark`) | body-match, flavor-shared, flavor-complement, wrapper-affinity |
| 18 | 100 | 7-20-4 Robusto (`cig-7-20-4-robusto`) | Café Cubano (zaslađeni espresso) (`cf-cubano-sweet`) | body-match, flavor-shared, flavor-complement, wrapper-affinity |
| 19 | 100 | A. Flores Gran Reserva Maduro (`cig-a-flores-gran-reserva-maduro`) | Graham's Tawny Port 20 Y.O. (`wine-grahams-tawny-20`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |
| 20 | 100 | A. Flores Gran Reserva Maduro (`cig-a-flores-gran-reserva-maduro`) | Sandeman Tawny Port 20 Y.O. (`wine-sandeman-tawny-20`) | body-match, flavor-shared, flavor-complement, contrast-sweet-maduro, wrapper-affinity |

### Najslabiji spojevi

| # | Score | Cigara | Piće | Rules |
|---|-------|--------|------|-------|
| 1 | 0 | 1502 Emerald (`cig-1502-emerald`) | Maraboo Brown (`rum-maraboo-brown`) | body-mismatch, strength-overwhelm |
| 2 | 0 | 1502 Emerald (`cig-1502-emerald`) | Professore Rum (Carib. Elixir) (`rum-professore-rum-carib-elixir`) | body-mismatch, strength-overwhelm |
| 3 | 0 | 1502 Emerald (`cig-1502-emerald`) | Bacardi Carta Blanca/Oro/Negra (`rum-bacardi-carta-blanca-oro-negra`) | body-mismatch, strength-overwhelm |
| 4 | 0 | 1502 Emerald (`cig-1502-emerald`) | Barcelo Blanco (`rum-barcelo-blanco`) | body-mismatch, strength-overwhelm |
| 5 | 0 | 1502 Emerald (`cig-1502-emerald`) | Pampero Blanco (`rum-pampero-blanco`) | body-mismatch, strength-overwhelm |
| 6 | 0 | 1502 Emerald (`cig-1502-emerald`) | Ron Cana del Caribe White (`rum-ron-cana-del-caribe-white`) | body-mismatch, strength-overwhelm |
| 7 | 0 | 1502 Emerald (`cig-1502-emerald`) | Stroh 80 (Austrija) (`rum-stroh-80-austrija`) | body-mismatch, strength-overwhelm |
| 8 | 0 | 1502 Emerald (`cig-1502-emerald`) | Bumbu Cream liker (`rum-bumbu-cream-liker`) | body-mismatch, strength-overwhelm |
| 9 | 0 | 1502 Emerald (`cig-1502-emerald`) | Malibu (`rum-malibu`) | body-mismatch, strength-overwhelm |
| 10 | 0 | 1502 Emerald (`cig-1502-emerald`) | Edradour Cream Liqueur (`wh-edradour-cream-liqueur`) | body-mismatch, strength-overwhelm |
| 11 | 0 | 1502 Emerald (`cig-1502-emerald`) | Chivas Regal XV (`wh-chivas-regal-xv`) | body-mismatch, strength-overwhelm |
| 12 | 0 | 1502 Emerald (`cig-1502-emerald`) | Ballantine's Finest (`wh-ballantine-s-finest`) | body-mismatch, strength-overwhelm |
| 13 | 0 | 1502 Emerald (`cig-1502-emerald`) | Dewar's White Label (`wh-dewar-s-white-label`) | body-mismatch, strength-overwhelm |
| 14 | 0 | 1502 Emerald (`cig-1502-emerald`) | Paddy (`wh-paddy`) | body-mismatch, strength-overwhelm |
| 15 | 0 | 1502 Emerald (`cig-1502-emerald`) | Jameson Caskmates Stout (`wh-jameson-caskmates-stout`) | body-mismatch, strength-overwhelm |
| 16 | 0 | 1502 Emerald (`cig-1502-emerald`) | Aberfeldy 12 (`wh-aberfeldy-12`) | body-mismatch, strength-overwhelm |
| 17 | 0 | 1502 Emerald (`cig-1502-emerald`) | Nikka Days (`wh-nikka-days`) | body-mismatch, strength-overwhelm |
| 18 | 0 | 1502 Emerald (`cig-1502-emerald`) | Togouchi Premium (`wh-togouchi-premium`) | body-mismatch, strength-overwhelm |
| 19 | 0 | 1502 Emerald (`cig-1502-emerald`) | Canadian Club 1858 (`wh-canadian-club-1858`) | body-mismatch, strength-overwhelm, flavor-complement |
| 20 | 0 | 1502 Emerald (`cig-1502-emerald`) | The Glenlivet 12 (`wh-the-glenlivet-12`) | body-mismatch, strength-overwhelm |

## 7. Zaključak

- Engine je **deterministički aditivni rule-sustav** s diskretnim koracima i clampom, ne probabilistički generator iz normale.
- Empirijska distribucija na punom katalogu: μ≈48.9, σ≈21.2, median≈48.
- Stroga Gaussova hipoteza: **odbijena** (JB); χ² p≈0.0000.
- Logičke invarijante ([0,100], integer, tag capovi) **prolaze** na punoj populaciji.

### Artefakti

- `app/scripts/output/pairing-audit/summary.json`
- `app/scripts/output/pairing-audit/histogram.csv`
- `app/scripts/output/pairing-audit/top50.json`
- `app/scripts/output/pairing-audit/bottom50.json`
- `app/scripts/output/pairing-audit/chi2-bins.json`
