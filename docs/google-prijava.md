# Prijava Google računom (neobavezna)

Stanje: **pripremljeno, ugašeno**. Kod je u repou, ali dok `VITE_GOOGLE_CLIENT_ID`
nije postavljen app izgleda i radi točno kao prije — Googleova skripta se ni ne
učitava.

## Čemu služi

Dojmovi se u repou spajaju po ključu (osoba, cigara). "Osoba" je dosad bio
slobodan nadimak, pa je isti čovjek s dva uređaja i dva različito upisana
nadimka brojao kao dvoje ljudi: njegov glas ulazio je u prosjek dvaput, a
`strengthFromTasting` je pretjerivao o tome koliko je ljudi cigaru pušilo.
Prijava daje jedan stabilan potpis po čovjeku i tu rupu zatvara.

Ne služi ničemu drugome: nema privatnog sadržaja, nema sinkronizacije, nema
profila na serveru. Dnevnik, humidor i bilješke i dalje ne napuštaju uređaj.

## Što ide u javni repo

| Podatak | Gdje živi |
| --- | --- |
| Ime za prikaz | u prijavi na GitHubu, kao i dosad |
| `g_` + 12 znakova SHA-256 haša Googleovog `sub` | u prijavi i u `tasteReports.json` |
| E-mail | **nigdje** — ne sprema se, ne šalje se, ne izlazi iz `lib/googleIdentity.ts` |
| Googleov `sub` u čitljivom obliku | **nigdje izvan preglednika** — u repo ide samo haš |

## Uključivanje

1. [Google Cloud Console](https://console.cloud.google.com/) → projekt →
   **APIs & Services → Credentials → Create credentials → OAuth client ID**.
2. Tip: **Web application**.
3. **Authorized JavaScript origins** — domena s koje se app poslužuje, npr.
   `https://ivsitum1.github.io` (i `http://localhost:5173` za razvoj).
   Redirect URI nije potreban: koristi se Google Identity Services, token stiže
   u callback, ne preusmjeravanjem.
4. Dobiveni client ID u `app/.env.local`:
   `VITE_GOOGLE_CLIENT_ID=…apps.googleusercontent.com`
5. Za GitHub Pages build isto ime varijable treba postojati u okolini deploya
   (`.github/workflows/deploy.yml`). Client ID **nije tajna** — vidi ga svatko
   tko otvori app — ali origins iz koraka 3 su ono što ga veže uz tvoju domenu.

Ugasiti se vraća uklanjanjem varijable. Zapisi koji su već ušli u
`tasteReports.json` ostaju važeći i dalje se spajaju po potpisu.

## Granica: ovo NIJE provjeren identitet

App je statična stranica na GitHub Pagesu i nema server koji bi Googleov token
provjerio, pa je potpis **pogodnost, ne dokaz**. Tko hoće lagati o tome tko je,
može ručno urediti tijelo GitHub prijave — mogao je i prije ovoga. Prosjeku se
vjeruje točno koliko i dosad; jedino se prestaje dvaput brojati isti čovjek koji
ne pokušava ništa lažirati.

Da potpis postane dokaz, netko mora provjeriti token na serveru: proširiti
`backend/` (postoji, ali se vrti lokalno za OCR) endpointom koji provjerava
Googleov ID token i tek onda potpisuje izvještaj, te ga negdje hostati. To je
zaseban zahvat i nije napravljen.

## Gdje je što u kodu

| Datoteka | Uloga |
| --- | --- |
| `app/src/lib/googleIdentity.ts` | client ID iz okoline, učitavanje GIS skripte, čitanje tokena, haš potpisa |
| `app/src/store/account.ts` | prijavljeni račun u `localStorage` (ime + potpis) |
| `app/src/components/TasteReportSheet.tsx` | gumb za prijavu i potpis u izvještaju |
| `app/src/lib/tasteReport.ts` | `byId` u JSON bloku prijave |
| `app/scripts/import-taste-report.py` | spajanje po potpisu kad ga ima, inače po imenu |
| `app/scripts/apply-taste-reports.py` | broj kušača se broji po potpisu |
