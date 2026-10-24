# Cleanup proposal (data layer prep)

**Date:** 2026-10-24  
**Branch:** `chore/cleanup-proposal`  
**Rule:** proposal only — **no deletions in this PR**. Every row needs Ivan GO on its own follow-up branch.

Referenced? = hit in `app/src`, `app/scripts/pipeline.py`, or `.github/workflows` (excluding OneDrive `*-DESKTOP-*` workflow copies).

| Path | Size (approx) | Last commit | Referenced by build/tests? | Proposed action | Needs Ivan GO |
|------|---------------|-------------|----------------------------|-----------------|---------------|
| `01_work/` | 110 files, ~1.5 MB (under `output/`, mostly gitignored) | 2026-07-29 | No | archive / move to separate notes repo | yes |
| `agent-brain-lite/` | ~15 tracked local files; junctions into external brain | 2026-09-09 | No (product runtime) | move/archive; keep out of product tree | yes |
| `.agent/` | tracked MEMORY + task; runtime memory ~21 MB local (gitignored) | 2026-08-23 | Partial (harness markers after colonize) | keep tracked markers; runtime already ignored | yes (only if changing policy) |
| `.claude/` | ~1485 files, ~168 MB (`worktrees/` nested checkout) | 2026-07-06 | No | gitignore `worktrees/` + archive/delete worktree | yes |
| `sideprojects/` | ~51 files, ~0.5 MB | 2026-08-27 | No | move to separate repo or archive branch | yes |
| `marketing/` | 3 files, ~0.2 MB | 2026-08-12 | No | move/archive | yes |
| `docs/superpowers/` | 46 files, ~0.3 MB | 2026-08-23 | No | archive (historical SDD plans/specs) | yes |
| `app/scripts/output/` | ~23 269 files, ~526 MB (YouTube dominant) | 2026-10-20 | **Yes** — `drink-shop-scan.yml`, `hr-availability.yml` force-track / artifact some paths | keep CI-required artifacts; gitignore or CI-artifact the rest (esp. YouTube) | yes |
| `app/scripts/phase3*` | 11 scripts | see inventory | No (candidate in `docs/scripts-inventory.md`) | move to `app/scripts/legacy/` then later delete | yes |
| `app/scripts/fix*` | 7 scripts | see inventory | No (candidate) | move to `legacy/` then later delete | yes |
| `app/scripts/merge*` | 11 scripts | mix | **Partial** — live: `merge-cigarworld-aroma`, `merge-leaf-details` in CI; others candidate | keep live; legacy the rest | yes (per script) |
| `app/scripts/youtube*` | ~17 top-level | mix | **Partial** — CI runs `test_youtube*` + `apply-youtube-* --check` | keep live/check scripts; legacy one-off runners | yes (per script) |
| `app/scripts/apply*` | 9 scripts | mix | **Partial** — live: taxonomy, descriptions, taste-reports, stock-overlay, youtube apply | keep CI-live; review rest | yes (per script) |
| OCR deps in `app/package.json` (`tesseract.js` + `@paddleocr/paddleocr-js`) | n/a | n/a | **Yes** — `app/src/lib/ocrEngine.ts` hybrid | **keep both** (labels→tesseract; receipts→paddle then tesseract). Not a dead duplicate. | yes only if dropping one engine |

## Notes

- Live vs candidate script lists: [`docs/scripts-inventory.md`](scripts-inventory.md) (190 top-level · 63 live · 127 candidate).
- OneDrive conflict copies (`*-DESKTOP-*`) already covered by `.gitignore`; stray workflow copies under `.github/workflows/` should be removed on a dedicated GO branch if still tracked.
- Snapshot tag (local): `pre-data-layer-2026-10` on `master` (push tag only with Ivan GO).
