# Pepeljare u obliku uglate glagoljice

**Samostalan side project** — nije dio aplikacije (`app/`) ni knjige / bontona (`docs/bonton/`).  
Grana: `design/glagolitic-ashtrays` · putanja: `sideprojects/pepeljare-glagoljica/` · 2026-08-02

## Namjera

Pepeljara **nije** okrugla zdjelica s ugraviranim slovom.  
Cijeli predmet **jest** tlocrt uglatog (hrvatskog) glagoljičkog slova: vanjski obris = zid, unutarnje grede = odlagališta za cigaru, polja = ležišta za pepeo.

## Pravila oblika

1. Čitljivost odozgo — za stolom mora ostati prepoznatljivo slovo.
2. Vanjski obris zatvoren (drži pepeo).
3. Unutarnje grede niže od ruba, s plitkim urezom (ø ≈ 18–22 mm za tipičnu cigaru).
4. Tip pisma: **uglata** glagoljica (ne obla).
5. Materijali u kasnijoj fazi: keramika, bronca, kamen; prvi krug = tlocrti + siluete.

## Sva slova u obziru

Pregledna galerija: **[GALERIJA-sva-slova.svg](./GALERIJA-sva-slova.svg)**  
Pojedinačni tlocrti: **[slova/](./slova/)** ([INDEX.md](./slova/INDEX.md))

Regeneracija: `python sideprojects/pepeljare-glagoljica/generate_letter_svgs.py`

| Razred | Slova |
|--------|--------|
| **A** (jaka) | Az, trokutasto az, Slovo, On, Ot, Frt |
| **B** (upotrebljiva) | Dobro, Pokoj, Ša, I, Tvrdo, Zemlja |
| **C** (rastezljiva) | Jest, Živjeti, Đerv, Kako |

Tlocrti su **dizajnerske siluete** za pepeljaru, ne paleografski faksimili.

## Raniji kratki prijedlozi (v0)

| ID | Slovo | Datoteka |
|----|--------|----------|
| **A** | Az | [prijedlog-A-az.svg](./prijedlog-A-az.svg) |
| **B** | Trokutasto az | [prijedlog-B-trokutasti-az.svg](./prijedlog-B-trokutasti-az.svg) |
| **C** | Slovo | [prijedlog-C-slovo.svg](./prijedlog-C-slovo.svg) |
| **D** | Serija | [prijedlog-D-serija.md](./prijedlog-D-serija.md) |

Detalji i mjere: [BRIEF.md](./BRIEF.md).

## Sljedeći koraci

- [ ] Odabrati A / B / C (ili kombinaciju za seriju)
- [ ] Profil (presjek): dubina zdjelice, visina grede, urez
- [ ] Prototip u glini ili 3D print (tlocrt 1:1)
- [ ] Odlučiti branding (samo oblik vs. sitni natpis na dnu)
