# Android APK — faza 1 (sideload)

**Grana:** `release/android` (dugoročna; **ne merga se** u `master` dok eksplicitno ne odlučimo).  
**Status faze 1:** Capacitor skela + sync s `master` + debug APK iz CI-ja za ručnu instalaciju na telefon.  
**Faza 2 (kasnije):** potpisani release, Google Play Developer račun, listing, Play policy.

---

## Rječnik (kratko)

| Pojam | Značenje |
|-------|----------|
| **Capacitor** | Omotač: Android “kutija” (WebView) u kojoj radi ista web app. |
| **WebView** | Ugrađeni preglednik unutar APK-a; nije Chrome kao zasebna app. |
| **debug APK** | Testna verzija potpisana debug ključem — za telefon, **ne** za Play Store. |
| **release APK / AAB** | Potpisana produkcijska verzija (faza 2). |
| **artefakt** | Datoteka koju GitHub Actions spremi nakon uspješnog builda (ovdje: APK). |
| **sideload** | Instalacija APK-a izvan Play Storea (datoteka + “nepoznati izvori”). |
| **`build:native`** | Vite build za Android: relativni `base`, bez service workera, izlaz `dist-native`. |
| **`cap sync`** | Kopira `dist-native` u Android projekt i osvježi nativne plugine. |

---

## Zašto Capacitor, a ne TWA

| | Capacitor (odabrano) | TWA / Bubblewrap |
|---|---|---|
| Sadržaj | bundlan u APK, radi bez mreže od prve sekunde | učitava se s `ivsitum1.github.io` |
| Verifikacija domene | ne treba | traži `assetlinks.json` u **korijenu** domene — na Pages podputu `/cigar-pairing/` to nije naše |
| Offline | podaci su lokalni fileovi | ovisi o service workeru i prvom online startu |
| Nativni dodaci kasnije | plugin API (kamera, share, status bar) | nema |

Katalozi su statični JSON; bit je offline uz cigaru — zato Capacitor.

---

## Dva build targeta

| | web (default) | native (`--mode native`) |
|---|---|---|
| Naredba | `npm run build` | `npm run build:native` |
| Izlaz | `app/dist` | `app/dist-native` |
| `base` | `/cigar-pairing/` | `./` |
| Service worker | da (PWA) | **ne** |
| Odredište | GitHub Pages | Capacitor Android assets |

`master` i dalje deploya **samo** web. Android živi na `release/android`.

---

## Sinkronizacija s `master` (povremeno)

Kad na `masteru` popravite web app i želite iste popravke u APK-u:

```powershell
git fetch origin
git checkout release/android
git merge origin/master
# riješi konflikte: zadrži OBA targeta (web + native) u vite.config.ts / package.json
# tipični konflikti: app/vite.config.ts, app/package.json, AGENTS.md, README.md
npm ci   # u app/
npm test
npm run build
npm run build:native
git push origin release/android
```

Merge (ne squash) olakšava buduće syncove. Nakon pusha CI gradi novi debug APK.

**Ne** otvaraj PR `release/android` → `master` dok ne dogovorimo lansiranje / fazu 2.

---

## Kako skinuti debug APK (bez lokalnog Androida)

1. Otvori [Actions → Android APK](https://github.com/ivsitum1/cigar-pairing/actions/workflows/android.yml).
2. Odaberi zadnji uspješan run na grani **`release/android`** (zelena kvačica).
3. Na dnu stranice, **Artifacts** → `cigar-pairing-debug-apk` → Download (ZIP).
4. Raspakiraj ZIP — unutra je `app-debug.apk` (~19 MB).

Workflow se pali na svaki push izvan `master` i na `workflow_dispatch`.

---

## Sideload na Android telefon (korak po korak)

1. Prenesi `app-debug.apk` na telefon (USB, Google Drive, Telegram “Saved Messages”, e-mail…).
2. Na telefonu otvori datoteku (Files / Downloads).
3. Ako Android pita za **instalaciju iz nepoznatog izvora** — dopusti za taj File Manager / Chrome / Drive (samo taj izvor).
4. Potvrdi instalaciju. Upozorenje “Play Protect” / “nepoznata app” je **očekivano** za debug APK.
5. Otvori **Cigar Pairing**.

Ako imaš USB debugging i `adb`:

```text
adb install -r app-debug.apk
```

---

## Checklist na uređaju (faza 1)

Označi na telefonu nakon instalacije:

- [ ] App se otvara; splash nije dugi bijeli bljesak
- [ ] Age gate radi; nakon potvrde ostaje zapamćen (restart appa)
- [ ] Sparivanje: odabir cigare → bodovani prijedlozi
- [ ] Lazy stranice: Katalozi, Kolekcija, Kupnja, Klub
- [ ] Hardverski Back: vraća se unutar appa, ne izlazi odmah
- [ ] Offline: isključi Wi‑Fi/mobilne podatke → pairing i katalozi i dalje rade
- [ ] Kolekcija / “Zabilježi večer” preživi zatvaranje appa (localStorage)
- [ ] Glazba (`MusicToggle`) ako je uključena
- [ ] OCR / kamera: otvori sken — bilježi treba li `CAMERA` dozvolu (trenutačno nije u manifestu; Android camera intent često radi bez nje)

Poznate greške / napomene zapisati ovdje ili u Issueu na GitHubu.

### Što je već provjereno (2026-08-05, sync s master)

| Provjera | Rezultat |
|----------|----------|
| Merge `master` → `release/android` | OK (konflikti vite/AGENTS/README/lock riješeni) |
| `npx tsc -b --noEmit`, `npm test` (530) | OK |
| `npm run build` + `npm run build:native` | OK |
| Native `index.html` relativni `./assets/…` | OK (HTTP 200 iz korijena) |
| Service worker u `dist-native` | Nema (namjerno) |
| Lazy chunkovi Catalog / Collection / Shopping / Club / OCR | Prisutni u `dist-native/assets` |
| CI `android.yml` run 31021965372 | Zelen (~2m35s), artefakt APK |
| APK na disku | `Downloads\cigar-pairing-debug-apk\app-debug.apk` (~36 MB) |
| Hardverski Back / kamera / offline na fizičkom telefonu | **Vi** — checklist iznad |

---

## Lokalni build (opcionalno)

Traži **JDK 21** + Android SDK (Android Studio → `ANDROID_HOME`).

```powershell
cd app
npm run android:sync     # build:native + cap sync android
npm run android:open     # Android Studio
npm run android:run      # spojeni uređaj / emulator
```

Debug APK:

```powershell
cd app
npm run android:sync
cd android
.\gradlew.bat assembleDebug
# app/build/outputs/apk/debug/app-debug.apk
```

---

## CI

`.github/workflows/android.yml`: `npm ci` → `build:native` → `cap sync android` → `assembleDebug` → artefakt `cigar-pairing-debug-apk`.

Pages (`deploy.yml`) nedirnut — gradi web target s `mastera`.

---

## Što je u repou, a što se generira

Commitano: `app/android/` (Gradle, manifest, resursi, ikone), `capacitor.config.ts`.  
Gitignorirano (generira `cap sync` / Gradle):

- `app/android/app/src/main/assets/public`
- `capacitor.config.json` / `capacitor.plugins.json` u assets
- `capacitor-cordova-android-plugins/`
- `app/build/`, `local.properties`

---

## Faza 2 — još nije (namjerno)

1. Google Play Developer račun (~25 USD).
2. Keystore + potpisani `assembleRelease` + GitHub secrets.
3. Automatski rast `versionCode`.
4. Store listing (feature graphic, opis, privacy policy).
5. Play policy za duhan/alkohol (age rating) — **provjera prije submita**.
6. Optimizacija veličine APK-a ako treba.

Cloud sync korisničkih podataka ostaje odvojena priča; APK i dalje drži stanje u localStorageu po uređaju.
