# Bonton / Club — most knjiga ↔ app

**Repo:** [ivsitum1/cigar-pairing](https://github.com/ivsitum1/cigar-pairing)

| Što | Gdje u GitHubu | Grana |
|-----|----------------|-------|
| App (PWA, Club, pairing engine, `bonton.json`) | `app/`, `docs/bonton/APP-FROM-NOTEBOOKLM.md` | **`master`** |
| Knjižni rukopis (kratki kanon u appu) | `docs/bonton/mala-knjiga-pusackog-bontona.md` | **`master`** (+ sync na book) |
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

## Mapiranje sadržaja

| Tema iz NotebookLM | Knjiga (book branch) | App (`master`) |
|--------------------|----------------------|----------------|
| Lounge precepts | rukopis + `BOOK-FROM-NOTEBOOKLM.md` | `bonton.json` chapter *Lounge*; Club quiz |
| Higijena rezača / pepeo / telefon | vignette u knjizi | Club 101 lekcija; bonton V–VII |
| Čaša, voda, led, tempo gutljaja | stol / piće poglavlja | Club 101; pairing UI hints |
| Body / ABV / Maduro–slatkoća | bilješke, ne engine | `app/src/engine/rules.ts` |
| Obiteljske priče / arhetipovi | eseji / ton | `eveningArchetypes.json` |
| Holt's / Oliva povijest | selektivno | Club 101 / facts — ne bonton |

## NotebookLM bilježnice (share URL)

| Naziv | UUID |
|-------|------|
| Cigar 101 | `2707d3fe-73d1-4879-8e8d-b7538d1cb3f2` |
| Drink 101 | `e4921359-908c-40ee-b9f0-f68fd842a2cf` |
| The cigar family Story | `7d62a4d2-8cfa-46f0-a41e-89604cc1a547` |
| Rum 101 | `18ea7df7-bdc3-426c-b113-9083f48a936c` |
| Black Gold / rum tasting | `30d6a797-93bc-49f1-88e7-471c607b027c` |
| Holt's | `5b8ae55e-d6bf-4cde-afb2-33492c1b241b` |
| Cigar value & old school | `c4044fbd-39dd-47aa-b48a-24a9c2e41c23` |
| Oliva / heritage | `5d9870a0-c12c-4ecf-98b4-f1c9243bcca4` |

Puni grill dumpovi (2026-07-18 + refresh):  
`cursor/bonton-book-research-9b19` → `docs/bonton/research/notebooklm-grill/`

## Pravilo mergea

- Teški extracti / NotebookLM odgovori s fusnotama → **samo** book-research grana (`DO-NOT-MERGE.md`).
- Kad je poglavlje spremno za app: prenesi **originalan** HR/EN tekst u `app/src/data/bonton.json` (i po potrebi Club JSON) PR-om na `master` — ne cijeli research folder.
