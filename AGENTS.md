# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single frontend-only product: a **Vite + React + TypeScript + Tailwind PWA** for cigar/drink pairing, living entirely in `app/`. There is no backend — all user data (collection, ratings, pairing diary) is stored in the browser's `localStorage`, per device. The Python scripts under `app/scripts/` are an **optional local data-regeneration pipeline** (scrape → Excel → JSON); they are not needed to lint, test, build, or run the app, and require local Excel files that are git-ignored.

### Commands (run inside `app/`)
Standard commands are defined in `app/package.json` and mirrored by `.github/workflows/ci.yml`:
- Typecheck (lint gate in CI): `npx tsc -b --noEmit`
- Test: `npm test` (Vitest, `vitest run`)
- Build: `npm run build` (`tsc -b && vite build`)
- Dev server: `npm run dev` (Vite, defaults to port 5173)

### Non-obvious notes
- The dev server serves the app under the base path **`/cigar-pairing/`**, not `/`. Open `http://localhost:5173/cigar-pairing/` — the bare root path will not render the app. This base is set in `app/vite.config.ts` to match the GitHub Pages repo name.
- Node 22 is expected (see CI). The package manager is **npm** (`app/package-lock.json`).
- Deploy is automatic: push to `master` → GitHub Actions (`deploy.yml`) → GitHub Pages. Do not deploy manually.
- Since state is `localStorage`-only, a "hello world" smoke test is fully client-side: open the app → Pairing → pick a cigar → view scored drink pairings → "Zabilježi večer" to log an evening → confirm it appears under Kolekcija (Collection) diary.
