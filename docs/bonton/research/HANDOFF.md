# HANDOFF — nastavak Parallel deep research

**Za novi Cloud Agent / razgovor.** Čitaj ovo prvo.

## Stanje (2026-07-16)

- Branch: `cursor/bonton-book-research-9b19` (**NE mergati u `master`**)
- Korpus: `docs/bonton/research/` (~2.6 MB) — vidi `CATALOG.md`
- Rukopis: `docs/bonton/mala-knjiga-pusackog-bontona.md`
- App bonton: `app/src/data/bonton.json` (na masteru, već deployano)
- Korisnik je dodao Cursor Secret: `PARALLEL_API_KEY` (Runtime Secret)
- Deep research (ultra) je završen; vidi `notes/parallel-ultra-bonton.md`

## Update (2026-07-16)

- Run ID: `trun_ba7dd13b06a5491d9a482024cf4b2c32`
- Rezultat: `notes/parallel-ultra-bonton.md` + `notes/parallel-ultra-bonton.json`
- URL-ovi: `notes/parallel-ultra-bonton-urls.txt` (40)
- Extract metadata: `sources/parallel-ultra-bonton-extracts.json`
- Extracti: `extracts/parallel-ultra-bonton-*.md` (31)

## Što napraviti odmah

1. Pregledaj `notes/parallel-ultra-bonton.md` i odaberi relevantne izvore za rukopis.
2. Po potrebi očisti duplicirane izvore i ažuriraj `CATALOG.md`.
3. Ako treba novi krug deep researcha, koristi `parallel-cli research run` uz precizniji upit i `--processor ultra`.

## Dodatni research krugovi (ako ultra uspije)

- Europeana / Library of Congress tobacco etiquette prints
- HR / regional hospitality norms (ako postoje kvalitetni izvori)
- Emily Post smoking sections (full)
- Davidoff essay text if licence-clean

## Ne raditi

- Ne mergati u `master`
- Ne printati / commitati `PARALLEL_API_KEY`
- Ne wholesale-kopirati Bridges *How to Be a Gentleman* (copyright) — samo forma kratkih precepta
