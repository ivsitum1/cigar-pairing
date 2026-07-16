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

## YouTube → NotebookLM

- Lista kandidata: `notes/youtube-bonton-notebooklm.md`
- Raw search JSON: `notes/youtube-bonton-candidates.json`, `notes/youtube-bonton-candidates-hist.json`
- Agent **ne** ekstrahira pouzdane YouTube transcripte; korisnik uvozi Priority linkove u NotebookLM, pa exporta bilješke u `extracts/youtube-*.md`

## NotebookLM notebookovi (korisnik share)

1. https://notebooklm.google.com/notebook/5b8ae55e-d6bf-4cde-afb2-33492c1b241b
2. https://notebooklm.google.com/notebook/2707d3fe-73d1-4879-8e8d-b7538d1cb3f2
- Grill prompti: `notes/notebooklm-grill-pack.md`
- Status: agent ne može čitati bez Google login-a; čeka export odgovora

## Što napraviti odmah (sljedeći agent)

1. Kad stignu NotebookLM exporti, katalogizirati ih u `extracts/` + `CATALOG.md`.
2. Ugraditi citate iz round2 (Post, Morton, LOC, Davidoff paraphrase) u rukopis.
3. Po želji: Europeana/Wellcome item-level dig — round2 je dao search hubove; treba item permalinke.

## Ne raditi

- Ne mergati u `master`
- Ne printati / commitati `PARALLEL_API_KEY`
- Ne wholesale-kopirati Bridges *How to Be a Gentleman* (copyright) — samo forma kratkih precepta
- Ne redistribuirati Vukčević *Bonton* PDF — samo kratki fair-use citati / parafraza
