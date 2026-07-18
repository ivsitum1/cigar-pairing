# Data code-split + večernji session/dnevnik — design

## Goals

1. **B — lakši PWA payload:** umjesto jednog `data-*.js` chunka (~1.15 MB),
   podijeliti indekse po kategoriji radi paralelnog downloada i boljeg cache
   invalidiranja; odgoditi shopping/brands do trenutka kad trebaju.
2. **C — večernji tok:** s pairing rezultata jednim korakom zabilježiti večer
   (cigara × piće, ocjena, bilješka) u postojeći dnevnik, bez novog backend-a.

## Non-goals

- Cloud sync (faza 2 u README-u)
- Rewrite bonton rukopisa / grill notebook
- Promjena pairing engine pravila

## B — Architecture

- `vite.config.ts` `manualChunks`: `data-cigars`, `data-whiskies`, `data-rums`,
  `data-brandies`, `data-drinks-small` (gin/wine/coffee), umjesto jednog `data`.
- `shopping.json` i `brands.json` izvan eager `data/index.ts` — lazy moduli
  koje učitaju ShoppingPage / BrandSheet.
- Sync API za `CIGARS` / `DRINKS` / `ALL_DRINKS` ostaje (pairing treba cijeli
  indeks); dobitak je paralelni fetch + granularni cache.

## C — Architecture

- Na PairingPage, kad postoji odabrana cigara i barem jedan prijedlog pića
  (ili obrnuto), CTA **„Zabilježi večer”** otvara sheet: prefill cigara/piće,
  ocjena 1–10, bilješka → `addJournalEntry` (+ opcionalno `tried` na obje stavke).
- Occasion chip `evening` ostaje postojeći filter; session ne mijenja routing.
- i18n hr+en; localStorage format journal zapisa ne mijenja shemu.

## Testing

- Postojeći vitest suite mora proći.
- Novi unit test za session helper (prefill + tried patch) ako logika nije trivijalna UI.
- `npm run build` — potvrditi više `data-*` chunkova umjesto jednog velikog.
