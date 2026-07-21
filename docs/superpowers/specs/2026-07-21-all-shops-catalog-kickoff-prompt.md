# Kickoff prompt — pravi katalog cigara (svih trgovina)

Zalijepiti na početku **Claude Code sesije na ovom repou** (gdje Claude može i
pisati skripte i voziti Chrome), u sesiji s uključenom mrežom za trgovine i
Chrome kontrolom. Prati spec: `2026-07-21-all-shops-catalog-scrape.md`.

## Prompt (copy-paste)

```
Repo: ivsitum1/cigar-pairing. Radi na NOVOJ grani claude/eu-usa-catalog-scrape
(odvojeno od PR-a s filterom). Cijeli plan je u:
docs/superpowers/specs/2026-07-21-all-shops-catalog-scrape.md — PROČITAJ GA PRVO
i drži ga se.

Cilj: zamijeniti heurističke EU/USA markets oznake STVARNOM dostupnošću i
stvarnim linkom po proizvodu, scrapajući sve trgovine kroz Chrome (Playwright).

Prije bilo kakvog scrapea:
1. Provjeri pristup: curl -sS "$HTTPS_PROXY/__agentproxy/status" — potvrdi da
   cigarworld.de, holts.com i cigarsdaily.com više NISU odbijeni (403). Ako jesu,
   stani i reci mi da mreža nije uključena.
2. Potvrdi da imaš Chrome kontrolu (Playwright launch uspije).

Onda kreni od FAZE 0 iz spec-a: scrape SAMO jedne kategorije po trgovini, pokaži
mi 5–10 primjera normaliziranih zapisa (brand, linija, vitola, format, cijena,
država, product URL) i ČEKAJ moje odobrenje prije punog scrapea.

Trgovine: humidor.hr, havana-cigar-shop.com (HR, već imamo), cigarworld.de (EU),
holts.com + cigarsdaily.com (USA).

Nepregovaralna pravila:
- Embargo: kubanke smiju EU, NIKAD USA.
- Jedan zapis po cigari (ključ brand+linija+ring×dužina), markets = unija regija;
  NE stvarati duplikate.
- HR podaci su izvor istine — EU/USA se DODAJU, ne prepisuju.
- Product URL > search URL; ne izmišljati cijene ni dostupnost.
- USD → EUR uz pinnani tečaj, označi priceApprox.
- Rate-limit 1–2 s, backoff na 429; rukuj cookie/consent i age-gate zidovima.

Kad je gotovo: dedupe, embargo/valuta testovi, npm test zelen, ažuriran panel
"Trgovine" sa stvarnim brojevima, pa otvori PR. Idi fazama iz spec-a, ne sve odjednom.
```

## Napomene

- Ako se nastavlja na istoj grani/PR-u umjesto nove, promijeni ime grane u 1. retku.
- Ključno je „čekaj odobrenje nakon Faze 0" — prvo vidiš uzorak podataka i potvrdiš
  selektore prije punog scrapea.
- Cilja se Claude Code sesija (uređivanje `cigars.json`/testova + Chrome), ne čista
  Claude-for-Chrome ekstenzija.
