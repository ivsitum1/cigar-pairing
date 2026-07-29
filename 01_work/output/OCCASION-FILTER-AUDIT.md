# Audit filtera doba dana (hibrid)

**Generirano:** 2026-07-29T16:11:52.744Z  
**Trajanje:** 93060 ms  
**Engine:** soft occasion nudge u `pairDrinksForCigar` + `rankByOccasion` (izbor unutar pojasa izjednacenih po kategoriji)

## 1. Opseg

| Veličina | Vrijednost |
|----------|------------|
| Cigare (dedupe) | 2397 |
| Pairable pića | 821 |
| Pool any (ref. body 3) | 821 |
| Pool jutro (ref. body 3) | 821 |
| Pool poslijepodne (ref. body 3) | 821 |
| Pool večer (ref. body 3) | 821 |

## 2. Metrike razlike top-prijedloga

Udio cigara gdje se **barem jedna** kategorija (rum/whisky/brandy/wine/coffee/tequila/gin) razlikuje u top-1:

| Usporedba | n | udio | Prag | Status |
|-----------|---|------|------|--------|
| jutro vs večer | 2397 | 100.0% | ≥ 50% | PASS |
| jutro vs poslijepodne | 2383 | 99.4% | ≥ 25% | PASS |

### Occasion reasoni na top karticama

Broj top-1 slotova (kategorija × cigara × prilika) koji nose reason:

| Reason | pogodaka |
|--------|----------|
| occasion-fit | 36372 |
| occasion-clash | 5809 |

## 3. Uzorak — top rum po prilici

| Cigara | str/body | any | jutro | poslijepodne | večer |
|--------|----------|-----|-------|--------------|-------|
| Ashton Cabinet | 1/1 | Clément VSOP (agricole) (82) | Clément VSOP (agricole) (85) | Clément VSOP (agricole) (88) | Ableforth's Rumbullion! (86) |
| Luciano Maria Lucia | 2/2 | Clément VSOP (agricole) (82) | Clément VSOP (agricole) (87) | Clément VSOP (agricole) (90) | Ableforth's Rumbullion! (84) |
| Holt's House Selection Maduro | 2/4 | 23 (solera) (90) | 30 (87) | 23 (solera) (95) | 23 (solera) (97) |
| Casdagli D'Boiss | 3/3 | Eminente Gran Reserva 10 (80) | Saint James 12 (agricole) (77) | Eminente Gran Reserva 10 (88) | Zafra Master Series 30 (78) |
| Freud Limited Edition 2023 Sigmund Collaboration Disruptor | 3/3 | Eminente Gran Reserva 10 (80) | Saint James 12 (agricole) (77) | Eminente Gran Reserva 10 (88) | Zafra Master Series 30 (78) |
| My Father La Reloba | 3/3 | Avuá (cachaça) (89) | Saint James 12 (agricole) (87) | Avuá (cachaça) (97) | Zafra Master Series 30 (88) |
| West Tampa Tobacco Co. Tampa Black | 3/3 | Eminente Gran Reserva 10 (80) | Saint James 12 (agricole) (77) | Eminente Gran Reserva 10 (88) | Zafra Master Series 30 (78) |
| La Gloria Cubana Churchill | 3/4 | 23 (solera) (90) | 30 (87) | 23 (solera) (95) | 23 (solera) (97) |
| Alec Bradley Nica Puro Rosado | 4/3 | Eminente Gran Reserva 10 (80) | Saint James 12 (agricole) (77) | Eminente Gran Reserva 10 (88) | Eminente Gran Reserva 10 (86) |
| La Gloria Cubana Coleccion Reserva | 4/4 | 23 (solera) (86) | 10 Gran Reserva (78) | 10 Gran Reserva (86) | 23 (solera) (94) |

## 4. Kako prilika djeluje

Nista se ne rezi iz poola (`occasionKeep` je no-op). Dva sloja:

1. **Soft nudge** u scoreu — `|delta| ≤ occasionFit + occasionMild < bodyPerStep`,
   pa doba dana ne moze pretvoriti los par u dobar.
2. **Izbor unutar izjednacenih** — medju kandidatima iste kategorije koji su
   unutar `OCCASION_BAND_MARGIN` bodova od najboljeg presudjuje `occasionAffinity`
   (kategorija + stil + relativno tijelo + zestina).

JSON sažetak: `app/scripts/output/occasion-audit/summary.json`
