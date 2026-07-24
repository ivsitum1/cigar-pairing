# Integracijski merge — evidencija (za povrat)

**Datum:** 2026-07-24
**Grana:** `claude/integration-overnight-merge`
**Baza (master prije):** `67424a3c48ebd394978b11ca865ad6e14e5a5486`
**Stanje:** 197/197 testova ✓ · `tsc -b` ✓ · `vite build` ✓ · nula konflikata

Konsolidacija noćnog rada. Spojena **4 ready PR-a** off aktualnog mastera, sigurnim redom, s testovima nakon svakog. Namjerno izostavljeno: `fix/last-call-regionlinks` (zaseban PR poslije), draftovi #38/#36 (samo data, kasnije), 22 stare grane + slice-2 kitchen-sink (ne spajati).

## Što je ušlo (redom)

| # | PR | Izvor (head SHA) | Merge commit | Sadržaj |
|---|----|------------------|--------------|---------|
| 1 | **#61** | `2ffb739` `claude/gin-cigarettes-cocktails-3i4fcd` | `c5ecbf3` | gin `cigarHint` ×20 + „gin-koktel most” u Leksikon |
| 2 | **#64** | `08fa423` `fix/localization-wishlist-abc` | `d4ee71e` | prijevod okusa (`TAG_LABELS`/`flavorLabel`) + `localizeServing` + wishlist dedup (maknut iz Kolekcije) |
| 3 | **#57** | `cce3105` `feat/pairing-explanations` | `9c86557` | uvijek-vidljiv blurb + narativ na expand (`pairingExplain.ts`) |
| 4 | **#17** | `e7510f3` `cursor/setup-dev-environment-f11c` | `7fe4070` | `AGENTS.md` |

Svi PR-ovi spojeni s `--no-ff` (svaki = jedan merge commit → čist povrat).

## Povrat (rollback)

Svaki merge se vraća neovisno, bez diranja ostalih (mainline = 1):

```bash
# vrati POJEDINI PR (primjer: samo #57 pairing-explanations)
git revert -m 1 9c86557        # #57
git revert -m 1 d4ee71e        # #64
git revert -m 1 c5ecbf3        # #61
git revert -m 1 7fe4070        # #17
```

Cijela integracija odjednom — vrati merge commit kojim je ova grana ušla u master
(vidljiv u `git log master` nakon spajanja PR-a; `git revert -m 1 <taj-sha>`),
ili tvrdi reset na bazu:

```bash
git checkout master
git reset --hard 67424a3c48ebd394978b11ca865ad6e14e5a5486   # master prije integracije
```

## Provjere prije spajanja
- `cd app && npx tsc -b` → 0
- `npx vitest run` → 27 datoteka, **197** testova prolazi
- `npm run build` → ok (PWA precache generiran)
- Vizualno (preview): serve selektor (#64), blurb na svakoj kartici (#57) i lokalizacija (#64) rade zajedno.

## Namjerno izostavljeno (i zašto)
- `fix/last-call-regionlinks` — vrijedan UI (market filter), ali nema PR i dira `PairingPage`; ide kao **zaseban PR** nakon ovoga.
- Draft #38 (`line-quality`), #36 (`brand-metadata`) — nose i zastarjeli `cigars.json`; spojiti **samo data datoteke** kad se žice u build.
- `feat/cigar-taxonomy-phase3-w1-slice2` — kitchen-sink (vraća revertirano vino + agent-brain dump). **Ne spajati.**
- 22 stare grane (`bonton-*`, `club-101-*`, `fix-*-fe85`, …) — već pokrivene kroz kasnije merge-ove; landmine zbog starog basea.
