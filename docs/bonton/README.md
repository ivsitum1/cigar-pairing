# Bonton — mapa kanona

Tri sloja: **rukopis knjige**, **app (PWA)** i **brain-lite wiki**. Ne miješaj ih u jedan izvor.

## Aktivni rukopis

| Datoteka | Uloga |
|----------|--------|
| `HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md` | Glavni EN manuskript (~2400 redaka). Part I proširen 2026-08-19. |
| `archived/` | HR draftovi, grill istraživanje, editor bilješke — **ne** app-kanon |
| `archived/EDITOR-NOTES.md` | Checkliste i proces izvan tijela knjige |

## App-kanon (što korisnik vidi u Klubu)

| Sadržaj | Put | Pravilo |
|---------|-----|---------|
| Bonton (11 poglavlja) | `app/src/data/bonton.json` | Etiketa, domaćin, salon… Test: točno 11 `id`-ova. |
| Leksikon sparivanja | `app/src/data/lexicon.json` | Govor o mostu, ritmu, riječima za stol |
| Rječnik | `app/src/data/dictionary.json` | Pojmovi (cigara, piće, sparivanje) — ne bonton eseji |
| Club 101 | `app/src/data/club101.json` | Praktični kutovi (pića, pribor, savjeti) |
| HR vodič kupnje | `app/src/data/hrGuide.json` | Trgovina, linkovi, Moj plan |

## Distilacija knjiga → app (2026-08-22)

| Poglavlje rukopisa | App dom |
|--------------------|---------|
| Ch 5 — words at the table | `lexicon.json` → `rijeci-za-stol` |
| Ch 13 — tasting host order | `bonton.json` → `b-table` |
| Ch 14 — rum label literacy | `dictionary.json` + Club 101 `d-rum-reading-label` + `lexicon` `distillery-first` |
| Ch 15 — nicotine / strength vs body | `bonton.json` → `b-host` (+ `lexicon` `snaga-vs-tijelo`) |
| Ch 20 — when the table is not yours | `bonton.json` → `b-outdoors` + Club 101 `t-foreign-table` |
| Expansion — inner scorecard / LE | `lexicon.json` → `unutarnja-ljestvica`, `limited-edition` |

Detaljna mapa: [`CROSSWALK.md`](./CROSSWALK.md).

## Sparivanje (mehanizam)

| Sloj | Put |
|------|-----|
| Motor | `app/src/engine/pairing.ts`, `coffeePairing.ts` |
| Objašnjenja | `app/src/engine/pairingExplain.ts` — `pairingBlurb` (kartica), `pairingNarrative` (proširenje) |
| Wiki | `agent-brain-lite/knowledge/concepts/pairing-mechanism.md` |

## Brain-lite

Operativno znanje: `agent-brain-lite/knowledge/concepts/` + `hot.md` / `log.md`.
