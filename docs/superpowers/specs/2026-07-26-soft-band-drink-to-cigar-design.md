# Soft-band ranking (drink → cigara)

**Date:** 2026-07-26  
**Status:** approved  
**Scope:** ranking presentation for drink→cigar; corpus audit both directions; no `scorePairing` / `WEIGHTS` change unless audit gate fires

## Goal

When the user picks a drink, the first suggested cigar should not always be the same catalog winner. Keep quality (only near-top scores), add controlled diversity via a soft score band, day seed, and cycle.

## Non-goals

- No change to cigar→drink UI (existing per-category cycle stays)
- No rewrite of `scorePairing` in the first ship
- No softmax / random UI sampling

## Current state

- Shared scorer: `scorePairing` in `app/src/engine/pairing.ts`
- Drink→cigar: `pairCigarsForDrink` sorts score DESC, then alphabetical `brand + line`
- UI (`PairingPage`): brand-diverse filter, window of 3, offset `cycle * 3`
- Fully deterministic → same drink always yields the same #1; alphabetical ties favor early brands

## Approach

**Soft band + seed (product only on drink→cigar).** Corpus audit runs the same helper in reverse for comparison.

## Ranking helper

Module: `app/src/engine/softBandRank.ts`

Pipeline:

1. Input: already score-sorted `PairingResult[]`
2. `brandDiverse` — first occurrence per `item.brand`
3. Soft band: keep items with `score >= maxScore - 5`
4. If `band.length < 3`: fall back to diverse (or full ranked if diverse too short) — same idea as today
5. Rotate: `offset = (baseOffset + cycle * windowSize) % band.length`
6. `baseOffset = stableHash(anchorId + "|" + dayKey) % band.length`
7. `dayKey` = UTC `YYYY-MM-DD`
8. Window size default 3

Returns `{ window, band, total }` where `total` is the pool length used for cycling (band or fallback).

## UI

`PairingPage` `cigarSuggestions` calls `softBandWindow` after `pairCigarsForDrink`. Serve, market filter, excluded brands, and `onlyMine` remain unchanged inputs. Cigar→drink cards untouched.

## Corpus audit

Script: `app/scripts/audit-soft-band-rank.mts`  
Report: `01_work/output/SOFT-BAND-RANK-AUDIT.md`

For each pairable drink and each cigar (comparison only on cigar→drink):

- `bandSize` histogram (`1` / `2–5` / `≥6`)
- baseline #1 vs soft-band #1 across 7 day keys and cycles 0..2
- % anchors where #1 changes at least once under soft-band
- sticky #1 lists; side-by-side usefulness of the two directions

## Score follow-up gate

If drink→cigar has `bandSize == 1` on more than ~40% of pairable drinks, consider a separate light calibration (tie-break / dampening). Otherwise leave the formula alone.

## Tests

`app/src/engine/softBandRank.test.ts`: band cut, diversity, dayKey stability/rotation, cycle step, small-band fallback. Existing pairing tests must still pass.
