# YouTube rum corpus → Club / rums catalog

**Date:** 2026-08-21  
**Status:** implemented (pilot scripts on `feat/youtube-rum-corpus`)  
**Pilot channel:** https://www.youtube.com/@StevetheBarmanUK  
**Goals:** A (writing corpus for Club 101 / lexicon / NotebookLM) + B (enrichment proposals for `rums.json`)

## Problem

The app already ships original HR/EN Club and drink copy, with sources listed in `clubSources`. Rum education and tasting commentary exist in volume on YouTube (pilot: Steve the Barman UK, ~1400 videos across rum, cocktails, and other spirits). We need a repeatable, multi-channel pipeline that:

1. Inventories every video on a channel.
2. Fetches captions/transcripts where available.
3. Classifies content so rum-relevant material is easy to find.
4. Proposes catalog enrichments against `app/src/data/rums.json`.
5. Feeds a research corpus for human/Writer/NotebookLM rewriting — never republishing third-party speech in the PWA.

## Non-goals

- Downloading video/audio files.
- Auto-merging proposals into `rums.json` or any catalog JSON.
- Showing raw transcripts, captions, or third-party quotes as primary UI content.
- CI jobs that call YouTube (network, quota, ToS).
- Treating a YouTuber as an authority for additive declarations (keep distillery / lab-backed `additiveSource` rules).

## Constraints

- **Copyright / attribution:** Captions are research inputs only. Shipped text must be original HR/EN prose. Videos appear as links in `clubSources` (or equivalent citation list), not as pasted transcript.
- **YouTube ToS / ops:** Prefer `yt-dlp` for personal research inventory + subtitles; rate-limit; support resume/delta. Expect blocks; do not hammer.
- **Scale:** Pilot channel is large (~1.4k videos). First full pass may take hours. Subsequent runs only fetch new or previously missing captions.
- **Multi-channel:** Design around a channel registry; Steve is the first entry, not a one-off script.
- **App architecture:** Corpus and run artifacts live under `app/scripts/output/` (gitignored). Committed assets are scripts, registry, tests, and (later) reviewed catalog/Club copy only.
- **HR copy canon:** Any text that eventually lands in Club / dictionary / lexicon follows project HR rules (`cigara`, `dim`, `sparivanje`, finite verbs, etc.).

## Architecture

```
channels.json
     │
     ▼
youtube-inventory.py ──► inventory.json (all video ids + meta)
     │
     ▼
youtube-fetch-captions.py ──► videos/<videoId>.json (text + caption meta)
     │
     ▼
youtube-classify.py ──► tags on each video + classify.json summary
     │
     ├──────────────────────────────┐
     ▼                              ▼
A: corpus for Writer/NLM      B: youtube-match-rums.py
   (rum + relevant bar)            │
   → Club 101 / lexicon           ▼
   → clubSources link         rum_match_proposals.json
                                   │
                                   ▼
                              human review → optional rums.json edits
```

Tooling: Python scripts beside existing `app/scripts/scrape-*`, shared helpers in `youtube_common.py`, captions via `yt-dlp` (manual EN preferred, else auto `en`).

## File layout

```
app/scripts/
  data/youtube/
    channels.json                 # committed registry
  youtube_common.py
  youtube-inventory.py
  youtube-fetch-captions.py
  youtube-classify.py
  youtube-match-rums.py
  output/youtube/                 # gitignore this tree
    <channelSlug>/
      inventory.json
      videos/<videoId>.json
      classify.json
      rum_match_proposals.json
      run.log
docs/superpowers/specs/
  2026-08-21-youtube-rum-corpus-design.md
docs/sources/youtube/             # optional: README + citation checklist (no raw captions)
```

Add to `app/.gitignore`:

```
scripts/output/youtube/
```

## Channel registry

`app/scripts/data/youtube/channels.json`:

```json
{
  "channels": [
    {
      "id": "stevethebarmanuk",
      "handle": "@StevetheBarmanUK",
      "url": "https://www.youtube.com/@StevetheBarmanUK",
      "langs": ["en"],
      "priority": 1,
      "enabled": true
    }
  ]
}
```

Later channels are new objects; scripts take `--channel <id>` or `--all-enabled`.

## Video record schema

Each `videos/<videoId>.json`:

| Field | Type | Notes |
|-------|------|--------|
| `videoId` | string | YouTube id |
| `channelId` | string | Registry `id` |
| `title` | string | |
| `url` | string | `https://www.youtube.com/watch?v=…` |
| `uploadedAt` | string \| null | ISO date if known |
| `durationSec` | number \| null | |
| `captionStatus` | `"ok"` \| `"missing"` \| `"error"` \| `"unavailable"` | `unavailable` = members-only / private / removed |
| `captionSource` | `"manual"` \| `"auto"` \| `"none"` | |
| `captionLang` | string \| null | e.g. `en` |
| `text` | string | Plain caption text; empty if missing |
| `fetchedAt` | string \| null | ISO date of caption fetch |
| `tags` | string[] | Filled by classify step |
| `error` | string \| null | Last error message if `captionStatus=error` |

`inventory.json` is the authoritative list of ids + lightweight meta before/without full caption payload. Caption fetch updates both the per-video file and inventory status fields as needed.

## Script behaviours

### `youtube-inventory.py`

- Input: channel from registry.
- Action: flat playlist / channel dump via `yt-dlp` (metadata only).
- Output: `inventory.json` with all videos; idempotent merge (keep existing caption fields).
- Flags: `--channel`, `--limit N` (smoke).

### `youtube-fetch-captions.py`

- Input: inventory.
- Action: for each video missing `ok` captions, write/update `videos/<id>.json`.
- Prefer manual English subs; fallback auto `en`; else `missing`.
- Flags: `--channel`, `--limit N`, `--force` (re-fetch), sleep/backoff between requests.
- Do not download media.

### `youtube-classify.py`

- Input: video JSON (title + text prefix).
- Heuristic tags, at least: `rum`, `cocktail`, `whisky`, `other-spirit`, `bar-technique`, `skip`.
- A video may have multiple tags (e.g. `rum` + `cocktail`).
- Output: update `tags` on each file; write `classify.json` counts.

### `youtube-match-rums.py`

- Input: videos tagged `rum` (and optionally title hits) + `app/src/data/rums.json`.
- Action: extract brand/line-like tokens; fuzzy/substring match against rum `name` / slug tokens from `id`.
- Output: `rum_match_proposals.json` only — never writes `rums.json`.
- Each proposal: `drinkId`, `videoId`, `url`, `confidence`, `matchedName`, `snippet`, `suggestedFields` (e.g. notes hint — advisory).

## Path A (writing)

1. Filter corpus: `rum` primary; include `cocktail` / `bar-technique` when useful for Club etiquette or serving.
2. Ingest into NotebookLM or local Writer workflow (chunk by video; keep URL on every chunk).
3. Produce original Club 101 / lexicon / pairing blurbs in project voice.
4. Add channel or specific videos to `clubSources` as citations.
5. Do not commit caption dumps.

## Path B (catalog)

1. Review `rum_match_proposals.json` (high confidence first).
2. Optionally update `notes` / `cigarHint` with original copy informed by the video.
3. Do **not** change `additiveStatus` / `additiveSource` solely from YouTube opinion.
4. Optional later field (out of scope for v1): `researchRefs: [{ label, url }]` on drinks — only if product owners want it; v1 keeps citations in Club/sources, not necessarily on each drink.

## Error handling and ops

- Missing captions → continue; log count in `run.log`.
- HTTP 429 / timeout → exponential backoff; persist progress so resume works.
- Delta sync: skip videos already `captionStatus: ok` unless `--force`.
- Smoke path: `--limit 5` through inventory + captions + classify.
- No secrets required for public captions via `yt-dlp` (document if that changes).

## Testing

- Unit tests (no network): classifier fixtures (titles → tags); matcher fixtures (small fake rum list + fake video titles/snippets).
- Manual smoke: five videos from Steve channel.
- CI: run unit tests only if added under `app/scripts/test_youtube_*.py` (or equivalent); never hit YouTube in CI.

## Success criteria (pilot)

1. Inventory covers all public uploads for `@StevetheBarmanUK` (minus deletions / region blocks).
2. Captions stored for every video that exposes EN subs; clear `missing` otherwise.
3. Classify summary shows a usable rum-tagged subset.
4. At least a sample of high-confidence rum match proposals reviewable by a human.
5. Zero transcript text in `app/src/` or shipped build artifacts.
6. Adding a second channel requires only a registry entry + re-run, not a new pipeline.

## Open follow-ups (explicitly later)

- Steve’s dedicated rum-reviews channel (if separate) as second registry entry.
- Stronger NER / LLM-assisted classification (optional; heuristics first).
- Scheduled weekly delta inventory (Task Scheduler), same pattern as stock refresh — only after pilot proves stable.

## Approval

Design agreed in chat 2026-08-21: approach 1 (yt-dlp local pipeline), A+B goals, no auto-merge, no transcripts in UI, multi-channel registry, pilot `@StevetheBarmanUK`.
