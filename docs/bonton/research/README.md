# Bonton book research branch

**Branch:** `cursor/bonton-book-research-9b19`  
**Status:** research-only — **do not merge to `master`** until the manuscript is ready.

This branch collects source material for *Mala knjiga pušačkog bontona* / a longer etiquette book: scholarly metadata, cultural repositories, historical etiquette texts, and extracted excerpts with citations.

## Layout

```
docs/bonton/
  mala-knjiga-pusackog-bontona.md   # working manuscript (from app)
  research/
    README.md                       # this file
    CATALOG.md                      # master index of sources
    notes/                          # thematic synthesis notes
    sources/                        # bibliographic records (JSON/MD)
    extracts/                       # downloaded / extracted text
```

## Method

1. Open scholarly APIs (Crossref, OpenAlex where available)
2. Cultural repositories (Internet Archive, Wikipedia/Wikidata, library catalogs)
3. Web discovery of etiquette manuals, cigar lounge customs, hospitality norms
4. Every extract notes URL, title, access date, and licence/status when known

## Parallel deep research

Ultra deep research je završen (2026-07-16). Rezultat je u:

- `notes/parallel-ultra-bonton.md`
- `notes/parallel-ultra-bonton.json`
- `sources/parallel-ultra-bonton-extracts.json`

Ako treba novi krug, koristi:

```bash
export PATH="$HOME/.local/bin:$PATH"
parallel-cli research run "…" --processor ultra --no-wait --json
```

Zatim pokreni poll i ekstrakcije kao u `HANDOFF.md`.
