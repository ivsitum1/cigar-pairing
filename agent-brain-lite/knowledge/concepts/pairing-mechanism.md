---
title: Mehanizam sparivanja (app)
category: domain
tags: [pairing, engine, club]
updated: 2026-08-22
---

# Mehanizam sparivanja u aplikaciji

## Tok

1. **Profili** — `cigar.body`, `strength`, `flavorTags`; piće `category`, `style`, tagovi, ABV, slatkoća (rum).
2. **Motor** — `pairing.ts` (+ `coffeePairing.ts` za kavu) boduje parove; izlaz: `score`, `reasons[]` s lokaliziranim tekstom.
3. **UI** — `PairingPage` / `ResultCard`: traka postotka, `pairingBlurb` u sažetku, **`pairingNarrative` u proširenom panelu** (▾), zatim lista +/- razloga.
4. **Kurirano** — `curatedPairingOpinion` može prigušiti karticu upozorenjem; blurb i narrative i dalje objašnjavaju zašto.

## Objašnjenja (bez LLM)

`pairingExplain.ts` je deterministički: uzima sortirane pozitivne/negativne `reasons` i zajedničke `flavorTags`. Nije isto što Leksikon — leksikon uči govor; motor boduje pravila.

## Club poveznice

- **Leksikon** — most, tijelo, ritam, distillery-first, riječi za stol.
- **Rječnik** — pojmovi (E150, solera, vitola…).
- **101** — praksa degustacije i čitanja etikete.
- **Bonton** — kako se ponašati dok sparivaš, ne formula.

## Što još nije u UI

- `eveningArchetypes.json` — referenca za buduće filtre/tekst, nije vezana na karticu.
