# Android APK — prvi koraci

Status: **skela radi, debug APK se gradi u CI-u.** Potpisani release i Play
Store nisu napravljeni (vidi *Što još nije napravljeno*).

## Zašto Capacitor, a ne TWA

Razmatrane su dvije rute za pakiranje postojećeg PWA-a:

| | Capacitor (odabrano) | TWA / Bubblewrap |
|---|---|---|
| Sadržaj | bundlan u APK, radi bez mreže od prve sekunde | učitava se s `ivsitum1.github.io` |
| Verifikacija domene | ne treba | traži `assetlinks.json` u **korijenu** domene — na `github.io` poddomeni s projektnim putem `/cigar-pairing/` to nije naše mjesto za postavljanje |
| Offline | podaci su lokalni fileovi | ovisi o service workeru i prvom online startu |
| Nativni dodaci kasnije | plugin API (kamera, share, status bar) | nema |

Indeksi (2395 cigara, ~800 pića) su statični JSON i cijela poanta appa je da radi
offline uz cigaru — zato Capacitor.

## Kako je posloženo

Isti izvorni kod, **dva build targeta**:

| | web (default) | native (`--mode native`) |
|---|---|---|
| Naredba | `npm run build` | `npm run build:native` |
| Izlaz | `app/dist` | `app/dist-native` |
| `base` | `/cigar-pairing/` | `./` |
| Service worker | da (PWA, prompt update) | **ne** |
| Odredište | GitHub Pages | `android/app/src/main/assets/public` |

Zašto tako (`app/vite.config.ts`):

- U WebView-u app živi na `capacitor://localhost/`, dakle u korijenu — Pages base
  path bi razbio svaki asset. Relativni `./` radi neovisno o shemi i hostu.
- Service worker je u APK-u suvišan (sve je već lokalno) i uvodi drugi, nevidljivi
  cache sloj koji se ne osvježava kroz APK/Play update. `VitePWA({ disable: true })`
  ostavlja `virtual:pwa-register/react` uvozljiv kao no-op, pa `SystemBanners.tsx`
  ne mora granati po targetu.
- Odvojeni `dist-native` znači da se native bundle ne može slučajno deployati na Pages.

`app/index.html` više ne sadrži tvrdo kodiran `/cigar-pairing/` — Vite ubacuje
base po targetu.

## Lokalni build

Traži **JDK 21** (Capacitor 7 / AGP 8.7) i Android SDK — najlakše kroz Android
Studio, koji postavi `ANDROID_HOME`.

```powershell
cd app
npm run android:sync     # build:native + cap sync android
npm run android:open     # otvori u Android Studiju (Build > Build APK)
npm run android:run      # instaliraj na spojeni uređaj / emulator
```

Debug APK iz komandne linije:

```powershell
cd app
npm run android:sync
cd android
.\gradlew.bat assembleDebug     # Linux/macOS: ./gradlew assembleDebug
# app/build/outputs/apk/debug/app-debug.apk
```

`npm run android:apk` radi isto u jednom koraku (posix `./gradlew`).

## CI

`.github/workflows/android.yml` — na svaki push izvan `master` i na PR prema
`master`: `npm ci` → `build:native` → `cap sync android` → `assembleDebug` →
APK kao artefakt run-a (`cigar-pairing-debug-apk`). Ubuntu runner već ima Android
SDK, workflow samo dodaje JDK 21.

Pages deploy (`deploy.yml`) je nedirnut i dalje gradi web target.

## Što je u repou, a što se generira

Commitano je `app/android/` (Gradle projekt, manifest, resursi, ikone). Generira
se i gitignorirano:

- `app/android/app/src/main/assets/public` — kopija `dist-native` (`cap sync`)
- `app/android/app/src/main/assets/capacitor.config.json`, `capacitor.plugins.json`
- `app/android/capacitor-cordova-android-plugins/` — `cap sync` ga rekreira
- `app/android/app/build/`, `local.properties`

Zato CI **mora** pokrenuti `cap sync android` prije Gradlea.

## Ikona i launch screen

Capacitorov template dolazi s Android robotom i bijelim splashom — zamijenjeno
amblemom iz `app/public/icon.svg`:

- `python scripts/build-android-icons.py` generira launcher ikone (legacy 48dp,
  round, i adaptive foreground na 108dp canvasu, sve gustoće) iz iste geometrije
  kao `icon.svg`. PNG-ovi su commitani — `cap sync` ne dira `res/`.
- `res/values/ic_launcher_background.xml` → `#201812` (pločica iz `icon.svg`)
- `res/drawable/splash.xml` — layer-list (boja humidora `#1a1512` + amblem)
  umjesto 11 raster splash varijanti po gustoći/orijentaciji
- `capacitor.config.ts` → `android.backgroundColor: "#1a1512"`, da WebView ne
  bljesne bijelo prije prvog React paint-a

## Provjereno

Native bundle je posluživan iz korijena (kao u WebView-u) i prošao kroz Chromium
na 412×915:

- app se renderira, **nula** page errora i nula neuspjelih requestova
- service worker se ne registrira
- pairing radi: odabir cigare → bodovani prijedlozi s objašnjenjima i uredničkom preporukom
- hash deep link `#/pairing/cigar/<id>` renderira direktno
- svi lazy chunkovi se dohvaćaju s relativnim base-om: Sparivanje, Katalozi,
  Kolekcija, Kupnja, Klub (uklj. atlas)

APK se gradi: prvi run workflowa je prošao zeleno u **2m18s** (`assembleDebug`
91 s, bez Gradle cachea), artefakt `cigar-pairing-debug-apk` ~19 MB.

Nije provjereno na pravom uređaju — Android SDK se ne može instalirati u
sandboxu (`dl.google.com` blokiran), pa APK treba skinuti iz CI artefakta i
instalirati ručno (`adb install app-debug.apk` ili prijenos na mobitel uz
"instalacija iz nepoznatih izvora").

## Što još nije napravljeno

1. **Potpisani release build.** `assembleRelease` traži keystore; plan je
   keystore + lozinke u GitHub secrets i `signingConfigs` u `app/build.gradle`.
   Do tada je APK debug-signed (instalira se ručno, ne ide na Play).
2. **`versionCode` automatizacija.** Sada tvrdo 1 / `versionName "0.1.0"`
   (usklađeno s `package.json`). Play traži monotoni rast `versionCode`.
3. **Provjera na uređaju:**
   - hardverski Back — hash routing puni history pa bi Capacitorov `goBack`
     trebao raditi, treba potvrditi da izlaz iz appa nije preagresivan
   - OCR (`OcrScan.tsx`, `<input capture="environment">`) — Capacitorov
     `BridgeWebChromeClient` to hvata i ide kroz Android camera intent, pa
     `CAMERA` permission **nije** deklariran; ako se pokaže da uređaj traži
     dozvolu, dodati je u manifest
   - `viewport-fit=cover` i safe area (notch, gesture bar) — možda treba
     `@capacitor/status-bar`
   - glazba (`MusicToggle`) i tesseract.js worker u WebView-u
4. **Veličina.** APK je ~19 MB (asseti ~22 MB nekomprimirano: data-cigars 3.3 MB
   JS, fontovi, dva mp3-a). Radi, ali ako treba niže: mp3 na manji bitrate,
   `minifyEnabled` na releaseu, ili glazba na download po zahtjevu.
5. **Play Store listing** — ikona 512×512 (postoji), feature graphic, opis,
   privacy policy (app ne šalje podatke nikamo, sve je localStorage — to olakšava).
6. **Cloud sync** ostaje faza 2 iz README-a; APK ne mijenja tu priču jer je
   storage i dalje po uređaju.
