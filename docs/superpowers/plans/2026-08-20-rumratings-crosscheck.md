# RumRatings × naš indeks — provjera ocjena i lov na materijal

**Status:** alat prilagođen živom siteu (2026-08-21); lokalni prolaz nad katalogom.
**Skripte:** `app/scripts/scrape-rumratings.py`, `app/scripts/compare-rumratings.py`,
`app/scripts/rumratings_shared.py`, test `app/scripts/test_rumratings.py` (CI gate).

Živi site (provjereno 2026-08-21): detalj je `/rum/<id>-<slug>` (ne `/brands/`);
ocjena je `<big>7.8</big>/10` u turbo-frameu, bez JSON-LD. Listing `/?sort=rating`
je JS ljuska (~5 boca). Otkriće ide sitemapom iz `robots.txt` (S3).
`crawl-delay: 30`. `RobotFileParser.read()` s Python UA dobiva 403 i lažno
zabranjuje sve — fetcher zato čita robots.txt našim User-Agentom.

## Zašto

Četiri pitanja, jedan prolaz kroz zajednicu:

1. Koliko se naš `qualityScore` poklapa s ocjenom zajednice?
2. Gdje se razilazimo i je li razilaženje sustavno?
3. Ima li po bocama priča i zanimljivosti za **Club**?
4. Ima li zapažanja o serviranju i stolu za **knjigu o bontonu**?

## Ograničenje okoline (važno)

Agentska sesija na webu nema izlaz prema `rumratings.com` — egress proxy vraća
403 na CONNECT za sve javne hostove osim registryja i GitHuba. Scrape se zato
**pokreće lokalno** (Cursor), kao i ostali scrapeovi u ovoj mapi. Parser je
pokriven testovima s fixture HTML-om, pa pad na živim podacima znači promjenu
na njihovoj stranici, ne neprovjeren kod.

## Pokretanje (iz `app/`)

```bash
python scripts/scrape-rumratings.py --targets rums --limit 8   # kratka proba
python scripts/scrape-rumratings.py --targets rums             # naš katalog (~320 boca)
python scripts/compare-rumratings.py --min-votes 25 --gap 1.2
```

- HTML se sprema u `scripts/output/rumratings_cache/` (git-ignorirano). Nakon
  ispravka selektora ide `--parse-only` — bez ijednog novog zahtjeva.
- Stranice koje parser nije pročitao završe u `rumratings_misses.json` zajedno s
  putanjom u cacheu. **Miss se prijavljuje, ne izmišlja se nula** — nula bi ušla
  u prosjek i pokvarila usporedbu.
- `robots.txt` se poštuje; razmak je `max(--delay, crawl-delay)` — na siteu je
  **30 s**. Puni sitemap (~13k) bez `--limit`/`--targets rums` skripta odbija.

## Što izlazi

| Datoteka | Sadržaj |
| --- | --- |
| `output/rumratings_raw.json` | boca, ocjena (1–10), broj glasova, tekst recenzija, `parseStrategy` |
| `output/rumratings_compare.json` | spoj s `rums.json` + sažetak (Spearman, MAE, pomak) |
| `output/rumratings_report.md` | HR izvještaj u šest dijelova |

Dijelovi izvještaja: (1) koliko se poklapamo, (2) gdje se ne slažemo — po bodu i
po **rangu**, (3) boce koje nemamo a zajednica ih drži visoko, (4) priče za Club,
(5) zapažanja za bonton, (6) slabi spojevi imena za ručnu provjeru.

## Kako čitati brojke

- **Dvije skale, dvije usporedbe.** Sirova razlika (`delta`) i razlika percentila
  (`rankDelta`). Naš `qualityScore` je ocjena *unutar stila* i ne kažnjava
  aditive; zajednica sustavno nagrađuje slatko. Zato je zanimljiv slučaj onaj
  gdje se razilazi **i rang** — tamo je stvarno drugačiji redoslijed police, a ne
  drugačija navika bodovanja.
- **Prag glasova.** `--min-votes 25` izbacuje boce s pet ocjena; ispod toga
  „ocjena zajednice" je nečije raspoloženje.
- **Dob se mora poklopiti.** Matcher tvrdo odbija spoj kad se brojevi u imenu
  razilaze (12 YO ≠ 15 YO) — inače bi popularna 15-ica tiho posudila ocjenu
  dvanaestici. Spojevi ispod 0,70 idu u dio 6 na provjeru prije nego se ijedan
  broj uzme zdravo za gotovo.
- **Razlika nije nalog za promjenu ocjene.** Uređivačka politika iz READMEa
  ostaje: ocjena unutar stila, aditivi deklarirani a ne kažnjeni. Rekalibrira se
  kad se razilaženje ponavlja kroz cijeli stil (npr. sve solere), ne po boci.

## Club i bonton — pravilo prerade

Dijelovi 4 i 5 izvještaja su **izvorni citati korisnika**, prikupljeni kao
polazište. U `club.json` i `bonton.json` ne ulazi ništa doslovno: činjenica se
provjeri u drugom izvoru i napiše našim glasom, dvojezično (`hr`/`en`), u
postojećem formatu. Tuđi tekst je tuđi tekst.

Sito je namjerno usko:
- **Club** — godine, destilerija, pot still / kolona, dunder i muck, esteri i
  marque, solera, obitelj i naraštaji, terroir.
- **Bonton** — čisto ili s ledom, čaša (copita, Glencairn), tempo, prvi gutljaj,
  nuđenje i dijeljenje za stolom, spoj s cigarom.

## Nakon prolaza

1. Pročitaj dio 6 i izbaci krive spojeve (`--floor` gore ako ih je puno).
2. Dio 3 → kandidati za `rums.json`; prije unosa provjeri HR dostupnost.
3. Dijelovi 4–5 → prerada u `club.json` / `bonton.json` u zasebnom commitu.
4. `rumratings_raw.json` i `rumratings_compare.json` se smiju commitati kao
   snimka; cache ne.
