# CONTINUATION OF Claude Code

> **Cursor agent nastavlja** prekinute Claude Code sesije (usage limit).
> Ne počinji ispočetka — pročitaj status ispod, pa uzmi prvi neoznačeni checkbox.

## Claude sessions

| Tema | URL |
|------|-----|
| Data-quality plan (4 workstreama) | https://claude.ai/code/session_015pwQUH3RuLAoWuS66Ek9RW |
| Nomenklatura + pairing info | https://claude.ai/code/session_01KgdmTUcoUbMQDoEHHWgisB |

## Što je gotovo (pushano, ali nije na masteru)

- [x] Plan + mjerilo: `docs/superpowers/plans/2026-08-05-data-quality-four-workstreams.md` + `app/scripts/data-quality-report.py` (commit `613a0cb` na `claude/prices-brands-mismatch-6q2q35`)
- [x] Nomenklatura P0–P2 + pairing klik na odabranu stavku: `claude/cigar-nomenclature-pairing-info-klrken` @ `7586126`

## Što je izgubljeno (nikad commitano)

- [x] W4: `derive-drink-display-names.py` + `drinkNameLoc` wiring + `drinkDisplayNames.json` — **Cursor prepisuje**
- [ ] ~72 vitola kuriranje + possessive false-positive u `taxonomy_lib.py` — **Cursor rekonstruira**

## Cursor dovršava (ovaj prolaz)

- [x] Handoff marker (ova datoteka) + `hot.md` red
- [x] PR A: W4 prikazna imena pića (`fix/drink-display-names-w4`)
- [ ] PR B: nomenklatura rebase + ~72 vitola curate + otvoreni PR

## Backlog za Claude Code (namjerno van ovog prolaza)

- [ ] Rebase + PR cijele `claude/prices-brands-mismatch-6q2q35` (jedinstvena cijena, packaging rank, soft-band) — **osim** plana/reporta koji Cursor već izvlači u W4 PR
- [ ] W3 shema/UI `fetchedAt` (offline)
- [ ] W1 `fold-market-vitolas.py` pa 🌐 Neptune scrape (Cursor lokalno ima mrežu)
- [ ] W2 drink profile worklist pa 🌐 note scrape

## Pravila sudara (W4) — ne izgubi

1. Sudar koji već postoji u sirovim `name` → propušti + evidentiraj (katalog duplikati).
2. Stvarne varijante (0,5 l vs 0,7 l, poklon-kutija) → disambiguate dodatkom.
3. Sudar koji bi čišćenje *stvorilo* → override, ne spoji slijepo.
4. Nikad ne mijenjaj sirovi `name` (buy-link / haystack).

## Lokalni checkout

Raditi u **worktreeima** od `origin/master`. Grana `design/glagolitic-ashtrays` se ne dira.
