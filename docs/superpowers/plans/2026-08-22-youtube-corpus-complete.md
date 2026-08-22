# YouTube corpus — complete scrape + knowledge integration

**Date:** 2026-08-22  
**Status:** in progress  
**Spec:** `docs/superpowers/specs/2026-08-21-youtube-rum-corpus-design.md`

## Goal

Finish caption harvest for all 13 registry channels, refresh classify/match queues, and land curated output in catalog JSON, Club sources, and (Path A) bonton/lexicon/dictionary via human/Writer review — never raw transcripts in the PWA.

## Phase 1 — Captions

### 1A — No cookies (public)

Channels: `therumrevival`, `williamhansonetiquette`, `rumverdict`, `liquidinfo`, `mayfaircigarledger`, `cigarrnation`, `cigaraficionado` (pending), `stevethebarmanuk` (stragglers).

```powershell
cd app\scripts
python youtube-batch.py captions --channel <id>
```

### 1B — Age-gate (fresh `data/youtube/cookies.txt` per channel)

Channels: `holtscigars`, `cigarsdaily`, `cigarsdotcom`, `cigaraficionado` (unavailable retries).

```powershell
cd app\scripts
python youtube-reset-age-gate.py --channel holtscigars
python youtube-batch.py captions --channel holtscigars --cookies data/youtube/cookies.txt
```

Ops: one channel per cookie export; use relative cookie path; members-only stays `unavailable`.

### 1C — Closed

Steve members-only (~155) and other permanent `unavailable` — no retry.

**Acceptance:** pending (`missing`+`error`) &lt; 50; rum/etiquette &gt; 90% `ok`; age-gate &gt; 80% `ok` or documented `unavailable`.

## Phase 2 — Classify + match

```powershell
cd app\scripts
python youtube-batch.py classify --all-enabled
python youtube-batch.py match-rums --all-enabled
python youtube-batch.py match-cigars --all-enabled
python youtube-batch.py summarize-cigars --prefer-stubs
python youtube-export-etiquette-index.py
```

## Phase 3 — Curation (human + Writer)

| Priority | Source | Target |
|----------|--------|--------|
| P0 | `cigar_review_queue.json` | `cigar_enrichments.json` |
| P0 | `rum_match_proposals.json` | `rum_enrichments.json` |
| P1 | Etiquette index | `docs/bonton/` → `bonton.json` |
| P2 | Lexicon themes | `lexicon.json` |
| P3 | Terms | `dictionary.json` |

HR canon: `cigara`, `dim`, `sparivanje`, original prose only.

## Phase 4 — Ship

```powershell
cd app
python scripts/apply-youtube-rum-enrichment.py
python scripts/apply-youtube-cigar-enrichment.py
```

- `clubSources.json` — YouTube channel citations
- CI: `apply-youtube-rum-enrichment.py --check`
- Pairing: optional `pairingBlurbs.json` (curated); engine does not read `cigarHint` today

## Phase 5 — Maintenance

Weekly `youtube-inventory.py --all-enabled`; caption delta for `missing`; quarterly re-match.

## Status snapshot (2026-08-22)

| Metric | Count |
|--------|-------|
| Inventory | 3764 |
| ok | 2177 |
| pending (missing+error) | 741 |
| unavailable | 846 |

Run `python scripts/youtube-caption-status.py` for live tally.
