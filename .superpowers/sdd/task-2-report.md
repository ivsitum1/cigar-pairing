# Task 2 report: Inicijativa A — Leksikon pairing jezika

## Summary

- Added `app/src/data/lexicon.json` with the required shape: `{ title, intro, entries }`.
- Added the canonical 8 entries in the brief order: `most`, `tijelo-tijelo`, `snaga-vs-tijelo`, `trecine`, `obitelji-nota`, `ritam`, `rijeci-za-stol`, `mini-vjezbe`.
- Added `app/src/data/lexicon.test.ts` before production data and verified the red failure while `lexicon.json` was missing.
- Added `LexiconPage` using the same `LessonBody` + `BackButton` list/detail pattern as `BontonPage`.
- Added the Club teaser card, `club.lexicon*` i18n keys, and nested hash routing for `#/club/101`, `#/club/bonton`, and `#/club/lexicon`.

## Verification

- RED: `npm test -- src/data/lexicon.test.ts` failed because `./lexicon.json` did not exist.
- GREEN targeted: `npm test -- src/data/lexicon.test.ts` passed 2 tests.
- Final full suite: `npm test` passed 16 files / 101 tests.
- Type/build check: `npm run build` exited 0.

## Self-review

- Confirmed lexicon data keeps the brief's exact entry IDs and minimum count.
- Confirmed each body uses paragraph breaks plus `•` catalogue sections parsed by `parseLessonBody`.
- Confirmed `LexiconPage` mirrors `BontonPage` structure without introducing a new rendering pattern.
- Confirmed navigation back to Club resets the nested club hash and bottom nav remains on Club.
- Confirmed no generated `dist` artifacts are staged.

## Concerns

- `npm run build` still reports Vite's existing large chunk warning for app chunks; build exits 0 and this task did not address chunk splitting.
