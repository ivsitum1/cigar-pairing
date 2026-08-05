# Što čeka novi scrape trgovina

Popravci kataloga iz kolovoza 2026. izvučeni su **iz samih imena zapisa** jer su
trgovine (humidor.hr, ecuga.com, neptunecigar.com) kroz agentski proxy vraćale
403. Sve niže je zato ostalo nedovršeno i traži podatak iz trgovine —
**cursor agent ponovno vrti scrape**, pa se ovo rješava tim podacima.

Skripte koje treba ponovno pokrenuti nakon scrapea (redoslijed iz README-a):
`enrich-cigars.py` → `profile-cigars.py` → `build-market-cigars.py` →
`scripts/repair-market-lines.py` → `scripts/repair-brand-line-split.py`.
Zadnje dvije su idempotentne i same se zaustave kad nema što popraviti.

## 1. Dimenzije vitola koje ne stoje nigdje u imenu

**806 vitola** još nosi izmišljenih `50 x 124mm` (i 180 komada `52 x 152mm`) —
to je default koji je `build-market-cigars.py` upisao kad shop nije dao mjeru.
`repair-market-lines.py` je izvukao mjeru svima kojima je stajala u imenu
(`do not disturb 6 52`, `Nub 460`, `xo salomon 7 58`); ostatak nema izvora.

Provjera stanja:

```
python3 - <<'EOF'
import json
c=json.load(open('app/src/data/cigars.json'))
print(sum(1 for x in c if x.get('catalogSource')=='market'
          for v in x['vitolas'] if v.get('format')=='50 x 124mm'))
EOF
```

## 2. Zapisi s nečitljivim numeričkim repom (17)

Rep nije čista mjera nego složena oznaka, pa ga skripta namjerno ne dira da ne
ostavi krnje ime. Trebaju prave dimenzije iz trgovine:

- `Tatuaje — Miami 8 9 8 63 4 44`
- `Quesada — Oktoberfest Salomon Press 6 3 4 50 33`
- `Asylum — Time Capsule Limited Edition 11 18 6 48 54 48`
- `Patoro — Cuvee Royale Xxv 63 10 53`, `Toscano — Terre 63 10 38`
- `Rough Rider — Senoritas 41 4 26`, `Eiroa — Dark 30th Anniversary 11 18 6 54`
- ostatak: `grep -nE '[0-9]+ [0-9]{2}"$' app/src/data/cigars.json`

## 3. 1502 XO — dvije mjere su procjena, jedna je sporna

- **Churchill** (`48 x 178mm`) i **Robusto Gordo** (`52 x 127mm`) uzeti su po
  istoimenoj vitoli istog proizvođača (1502 Nicaragua Churchill 7 x 48,
  1502 Blue Sapphire Robusto Gordo 5 x 52). Zapis nosi `formatEstimated`.
- **Conquistador**: humidor.hr ga drži kao 6 x 50, Neptune kao 6 x 56. Ostala je
  HR mjera (jedina s potvrđenom cijenom) i oba linka na istoj vitoli.

## 4. Cijene pića bez potvrđenog izvora

- **Camus VSOP Intensely Aromatic** — scrape mu je prepisao XO-ovu cijenu
  (110 €); stavljeno približno **40–50 €** po europskoj maloprodaji. HR cijena
  nije nađena (ecuga ga drži samo u 1 l).
- **Martell Cordon Bleu** — kurirani zapis kaže 195 € s potvrđenom stranicom,
  scrape blizanac je imao 50 € (razina VSOP-a). Zadržano 195 €, treba provjeriti.
- **Courvoisier VS** — dodan s približnih **36–39 €** (Stridon 35,99 €,
  Roto 38,99 €); ecuga link nije bilo moguće otvoriti kroz proxy.

## 5. Market stubovi koji dupliraju kuriranu liniju

Neptune stub čije je ime skraćeno ime kurirane linije iste marke opisuje isti
proizvod, ali s izmišljenim dimenzijama. Davidoff je riješen ručno (`Winston` i
`Winston LE 2025` su otišli u `Winston Churchill`), ali uzorak treba proći kroz
cijeli katalog kad dođu prave dimenzije — tada se vitole mogu spojiti po imenu
umjesto da se stub odbaci.

Kandidati: market zapis čija je linija token-prefiks linije drugog zapisa iste
marke.
