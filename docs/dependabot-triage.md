# Dependabot triage (do not merge from this PR)

**Date:** 2026-10-24  
**Source:** open Dependabot PRs on `ivsitum1/cigar-pairing` (CI status as of triage).  
**Rule:** document only — **no merges** here. Each bump needs its own GO after CI is green.

| PR | Title | Area | CI (app `test` / `backend`) | Breaking? | Proposed order | Notes |
|----|-------|------|-----------------------------|-----------|----------------|-------|
| [#223](https://github.com/ivsitum1/cigar-pairing/pull/223) | uvicorn ≥0.52.4 | backend pip | SUCCESS / SUCCESS | Low (min-version bump) | 1 | Safe alone; merge first among backend minors |
| [#221](https://github.com/ivsitum1/cigar-pairing/pull/221) | python-multipart ≥0.0.32 | backend pip | SUCCESS / SUCCESS | Low | 2 | After or with #223 |
| [#220](https://github.com/ivsitum1/cigar-pairing/pull/220) | pillow ≥12.3.0 | backend pip | SUCCESS / SUCCESS | Medium (10→12) | 3 | Test OCR image paths in `backend/` |
| [#219](https://github.com/ivsitum1/cigar-pairing/pull/219) | paddleocr 2.7.3→3.7.0 | backend pip | SUCCESS / SUCCESS | **Major** | 4 (solo) | PaddleOCR 3.x API; do **not** batch with numpy |
| [#222](https://github.com/ivsitum1/cigar-pairing/pull/222) | numpy ≥2.5.2,<3 | backend pip | SUCCESS / SUCCESS | **Major** (1.x→2.x) | 5 (solo, after #219) | Pin/test with paddleocr 3; separate GO |
| [#248](https://github.com/ivsitum1/cigar-pairing/pull/248) | vite 6.4.3→8.3.4 | app major | **FAILURE** / SUCCESS | **Major** | 6 (solo branch) | Fix Vite 8 / plugin peer deps before merge |
| [#249](https://github.com/ivsitum1/cigar-pairing/pull/249) | @vitejs/plugin-react 4.7→6.1.2 | app major | **FAILURE** / SUCCESS | **Major** | 7 (with or after #248) | Likely needs Vite 8; same fix train |
| [#254](https://github.com/ivsitum1/cigar-pairing/pull/254) | vitest 3.2.6→5.0.5 | app major | **FAILURE** / SUCCESS | **Major** | 8 (solo) | Vitest 5 config/API; fix CI then GO |
| [#207](https://github.com/ivsitum1/cigar-pairing/pull/207) | typescript 5.9.3→7.0.2 | app major | SUCCESS / SUCCESS | **Major** | 9 (solo, last) | TS 7; re-run `tsc -b` carefully; GO after app majors above |

## Proposed sequence (summary)

1. Backend non-majors: #223 → #221 → #220  
2. Backend majors (separate): #219 (paddleocr 3) then #222 (numpy 2)  
3. App majors (fix CI first): #248 + #249 (Vite/plugin) → #254 (Vitest 5) → #207 (TypeScript 7)

## Out of scope here

Merging, rebasing onto current `master`, or editing Dependabot PRs — wait for Ivan GO per item.
