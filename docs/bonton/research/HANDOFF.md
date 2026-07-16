# HANDOFF — nastavak Parallel deep research

**Za novi Cloud Agent / razgovor.** Čitaj ovo prvo.

## Stanje (2026-07-16)

- Branch: `cursor/bonton-book-research-9b19` (**NE mergati u `master`**)
- Korpus: `docs/bonton/research/` — vidi `CATALOG.md`
- Rukopis: `docs/bonton/mala-knjiga-pusackog-bontona.md`
- App bonton: `app/src/data/bonton.json` (na masteru, već deployano)
- Auth: `PARALLEL_API_KEY` (Runtime Secret) — radi
- Ultra deep research **round 1 + round 2** završeni; deduplikacija obavljena

## Round 1

- Run ID: `trun_ba7dd13b06a5491d9a482024cf4b2c32`
- Notes: `notes/parallel-ultra-bonton.md` + `.json`

## Round 2 (Europeana/LoC, HR/regional, Emily Post full, Davidoff)

- Run ID: `trun_ba7dd13b06a5491d81f840604a1de4d0`
- Notes: `notes/parallel-ultra-bonton-round2.md` + `.json`
- Ključni nalazi:
  - LOC item-level smoking-room planovi: `extracts/loc-*.md`
  - Emily Post full HTML: `extracts/gutenberg-14314-emily-post-etiquette-full.html.md`
  - Agnes Morton + Hand-book for Ladies full texts
  - Regionalni bonton (Vukčević PDF) — **©, samo parafraza**
  - Davidoff essay — **nema licence-clean full text**; citirati preko Wikipedia/paraphrase
  - Negativni nalaz: nema samostalne hrvatske knjige *pušački bonton*

## Deduplikacija

- Log: `notes/dedup-round2.md`
- Aktivni extracti: **51** (šum/duplikati u `extracts/_deduped/`)
- Politika: kurirana imena (`wikipedia-*`, `gutenberg-*`, `web-*`, `loc-*`); Parallel landing pageovi arhivirani

## Što napraviti odmah (sljedeći agent)

1. Ugraditi citate iz round2 (Post, Morton, LOC, Davidoff paraphrase) u rukopis.
2. Po želji: Europeana/Wellcome item-level dig — round2 je dao search hubove; treba item permalinke.
3. Ako treba treći research krug, fokusiraj se na item-level Europeana/Rijksmuseum/Gallica, ne na homepageove.

## Ne raditi

- Ne mergati u `master`
- Ne printati / commitati `PARALLEL_API_KEY`
- Ne wholesale-kopirati Bridges *How to Be a Gentleman* (copyright) — samo forma kratkih precepta
- Ne redistribuirati Vukčević *Bonton* PDF — samo kratki fair-use citati / parafraza
