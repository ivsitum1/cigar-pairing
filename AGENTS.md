# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single frontend-only product: a **Vite + React + TypeScript + Tailwind PWA** for cigar/drink pairing, living entirely in `app/`. The same bundle is also packaged as an Android app via **Capacitor** (`app/android/`, see `docs/android-apk.md`) — there is still no backend. There is no backend — all user data (collection, ratings, pairing diary) is stored in the browser's `localStorage`, per device. The Python scripts under `app/scripts/` are an **optional local data-regeneration pipeline** (scrape → Excel → JSON); they are not needed to lint, test, build, or run the app, and require local Excel files that are git-ignored.

### Commands (run inside `app/`)
Standard commands are defined in `app/package.json` and mirrored by `.github/workflows/ci.yml`:
- Typecheck (lint gate in CI): `npx tsc -b --noEmit`
- Test: `npm test` (Vitest, `vitest run`)
- Build: `npm run build` (`tsc -b && vite build`)
- Dev server: `npm run dev` (Vite, defaults to port 5173)
- Android: `npm run android:sync` (`build:native` + `cap sync android`), then `npm run android:open`/`android:apk`

### Non-obvious notes
- The dev server serves the app under the base path **`/cigar-pairing/`**, not `/`. Open `http://localhost:5173/cigar-pairing/` — the bare root path will not render the app. This base is set in `app/vite.config.ts` to match the GitHub Pages repo name. The Android target (`--mode native`) instead builds to `app/dist-native` with a relative base and no service worker, because the WebView serves the app from `capacitor://localhost/`.
- Building the APK needs JDK 21 + the Android SDK, neither of which is available in Cursor Cloud / Claude web sandboxes (`dl.google.com` is blocked). Verify Android changes by building the native web bundle and serving `app/dist-native` from the **root** path; the APK itself comes from the `Android APK` workflow artifact.
- Node 22 is expected (see CI). The package manager is **npm** (`app/package-lock.json`).
- Deploy is automatic: push to `master` → GitHub Actions (`deploy.yml`) → GitHub Pages. Do not deploy manually.
- Since state is `localStorage`-only, a "hello world" smoke test is fully client-side: open the app → Pairing → pick a cigar → view scored drink pairings → "Zabilježi večer" to log an evening → confirm it appears under Kolekcija (Collection) diary.
