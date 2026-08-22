# Bonton / Club — most knjiga ↔ app

**Repo:** [ivsitum1/cigar-pairing](https://github.com/ivsitum1/cigar-pairing)

| Što | Gdje u GitHubu | Grana |
|-----|----------------|-------|
| App (PWA, Club, pairing engine, `bonton.json`) | `app/`, `docs/bonton/README.md` | **`master`** |
| EN rukopis (source of truth) | `docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md` | **`master`** |
| HR književni prijevod (downstream) | `docs/bonton/KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md` | **`master`** |
| Kratki kanon u appu | `app/src/data/bonton.json` + `mala-knjiga` sync | **`master`** |
| Istraživački korpus + NotebookLM dumpovi | `docs/bonton/research/` | **`cursor/bonton-book-research-9b19`** (ne merge u master) |
| Grill inbox (kratki bullets) | `docs/bonton/grill-inbox.md` | **`master`** |

## Kako imati sve lokalno

```bash
# App + actionable backlog
git checkout master
git pull

# Istraživanje za knjigu (paralelni worktree — ne miješa working tree)
git fetch origin
git worktree add ../cigar-pairing-book cursor/bonton-book-research-9b19
```

Zatim:
- App rad: folder `cigar_and_rum` na `master`
- Knjiga / NotebookLM dumpovi: `../cigar-pairing-book/docs/bonton/research/`

## Mapiranje sadržaja (2026-08-22 enrichment)

| Tema | EN rukopis | HR rukopis | App |
|------|------------|------------|-----|
| Riječi za stol / „ne paše mi” | Ch 5 + Interlude | Ch 5 | `lexicon.json` → `rijeci-za-stol` |
| Kušanje: red, voda, nos izdaleka | Ch 13 | Ch 13 | `bonton.json` → `b-table` |
| Rum etiketa (E150a, 5+3, distillery-first) | Ch 14 | Ch 14 | `dictionary.json` + Club `d-rum-reading-label` + `lexicon` `distillery-first` |
| Nikotin bez srama; snaga vs tijelo | Ch 15 | Ch 15 | `bonton.json` → `b-host`; `lexicon` → `snaga-vs-tijelo` |
| Tuđi stol; vjetar; strani običaji | Ch 20 | Ch 20 | `bonton.json` → `b-outdoors`; Club `t-foreign-table` |
| Unutarnja ljestvica / LE | Expansion I | (po potrebi) | `lexicon` → `unutarnja-ljestvica`, `limited-edition` |
| Lounge precepts | Ch 16 | Ch 16 | `bonton.json` → `b-lounge` |
| Body / ABV / Maduro–slatkoća | bilješke | — | `app/src/engine/` (ne bonton eseji) |
| **EN freeze** | `HOW-TO-BE-…-DRAFT.md` = source of truth | sync nakon EN pass | app sync iz kanona |
| **HR freeze** | — | `KAKO-BITI-…-DRAFT.md` | kratki isječci → `bonton.json` |

## NotebookLM bilježnice (share URL)

| Naziv | UUID |
|-------|------|
| Cigar 101 | `2707d3fe-73d1-4879-8e8d-b7538d1cb3f2` |
| Drink 101 | `e4921359-908c-40ee-b9f0-f68fd842a2cf` |
| The cigar family Story | `7d62a4d2-8cfa-46f0-a41e-89604cc1a547` |
| Rum 101 | `18ea7df7-bdc3-426c-b113-9083f48a936c` |
| Black Gold / rum tasting | `30d6a797-93bc-49f1-88e7-471c607b027c` |
| **Cigars daily** (grill 2026-07-30 → LE / pepeo / Club) | `7b267552-b11c-4f3a-9861-fdfc6e7e640a` |
| **Omaha whiskey value ethics** (grill 2026-07-30 → anti-snob stol) | `6ccc327c-bf66-426b-b201-d39f12498750` |
| Holt's | `5b8ae55e-d6bf-4cde-afb2-33492c1b241b` |
| Cigar value & old school | `c4044fbd-39dd-47aa-b48a-24a9c2e41c23` |
| Oliva / heritage | `5d9870a0-c12c-4ecf-98b4-f1c9243bcca4` |
| **Bonton / etiquette** (grill 2026-07-19) | `adfe8fc8-de29-4919-a308-8284de395a3e` |
| **Writing craft / publishing** (grill 2026-07-30 → handbook form) | `5017a44b-e896-4c56-aa47-8857912e67de` |

Puni grill dumpovi:  
`cursor/bonton-book-research-9b19` → `docs/bonton/research/notebooklm-grill/`

## Pravilo mergea

- Teški extracti / NotebookLM odgovori s fusnotama → **samo** book-research grana (`DO-NOT-MERGE.md`).
- Kad je poglavlje spremno za app: prenesi **sažet** HR/EN tekst u `app/src/data/bonton.json` (i po potrebi Club / lexicon) PR-om na `master` — ne cijeli research folder.
- `bonton.test.ts` drži **11** poglavlja; novo znanje ide u postojeće `id`-ove, ne kao 12. poglavlje.
