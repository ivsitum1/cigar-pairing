# CONTINUATION OF Claude Code

> **Cursor agent nastavlja** prekinute Claude Code sesije (usage limit).
> Ne počinji ispočetka — pročitaj status ispod, pa uzmi prvi neoznačeni checkbox.

## Claude sessions

| Tema | URL |
|------|-----|
| Data-quality plan (4 workstreama) | https://claude.ai/code/session_015pwQUH3RuLAoWuS66Ek9RW |
| Nomenklatura + pairing info | https://claude.ai/code/session_01KgdmTUcoUbMQDoEHHWgisB |

## Što je gotovo (pushano)

- [x] Plan + mjerilo: u PR #122 (`fix/drink-display-names-w4`) iz `613a0cb`
- [x] Nomenklatura P0–P2 + pairing klik: PR za `fix/cigar-nomenclature-curate` (rebase od `claude/cigar-nomenclature-pairing-info-klrken`)
- [x] W4: `derive-drink-display-names.py` + `drinkNameLoc` + `drinkDisplayNames.json` — **PR #122**
- [x] Vitola kuriranje + possessive (`Serie S`) — **isti nomenclature PR**

## Cursor dovršio (ovaj prolaz)

- [x] Handoff marker (ova datoteka) + `hot.md` red
- [x] PR A: W4 — https://github.com/ivsitum1/cigar-pairing/pull/122
- [x] PR B: nomenklatura + curate — `fix/cigar-nomenclature-curate`

## Backlog za Claude Code (namjerno van ovog prolaza)

- [ ] Rebase + PR cijele `claude/prices-brands-mismatch-6q2q35` (jedinstvena cijena, packaging rank, soft-band) — plan/report već u #122
- [ ] W3 shema/UI `fetchedAt` (offline)
- [ ] W1 `fold-market-vitolas.py` pa Neptune scrape (Cursor lokalno ima mrežu)
- [ ] W2 drink profile worklist pa note scrape
- [ ] Preostali line-tail mismatchi bez Neptune URL / scrape fail (vidi `scripts/output/line_tail_vitola_worklist.json`)

## Pravila sudara (W4) — ne izgubi

1. Sudar koji već postoji u sirovim `name` → propušti + evidentiraj (katalog duplikati).
2. Stvarne varijante (0,5 l vs 0,7 l, poklon-kutija) → disambiguate dodatkom.
3. Sudar koji bi čišćenje *stvorilo* → override, ne spoji slijepo.
4. Nikad ne mijenjaj sirovi `name` (buy-link / haystack).

## Lokalni checkout

Raditi u **worktreeima** od `origin/master`. Grana `design/glagolitic-ashtrays` se ne dira.
