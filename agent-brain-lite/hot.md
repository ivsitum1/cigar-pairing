---
title: Session Hot Cache
category: meta
tags: [session, cache]
updated: 2026-07-30
---

# Session Hot Cache

~500 riječi snapshot nedavne aktivnosti. Agent ažurira nakon svake značajnije operacije pisanja u wiki.

> **2026-07-30:** Dnevnik večeri: ulaz C (DetailSheet + kartice sparivanja), pretraga kataloga pića + solo cigara, wishlist upit kad zaliha → 0, Kupovina restock. Don Tomas Clásico HR @ Tobacco Petica. Testovi 381/381.

> **2026-07-30:** Club facts/kviz: *vlak* → **draw** (loan; otpor/protok). Kanon: *dim* = brojivi gutljaj; *vlak* zabranjen kao calque. Rez: „tri **uobičajena**” + fact „Jeste li znali?” (škare, casino, Cuban cut, pinch).

> **2026-07-27:** Live: kategorija **digestif** (Biljni digestivi / Herbal digestifs) + Club101 `d-digestif` + 12 boca. PR #102 merged; Pages deploy OK. CI fix: taxonomy linije La Aroma (No. 3 / Habano Reserve / Small Batch) + re-apply.

> **2026-07-27:** HR kanon (projekt): `.cursor/rules/hr-copy-canon.mdc` — *cigara* (padeži), *pepeo*, *domaćin*≠kuća-agens, bez infinitivnih lanaca, Rječnik≠Leksikon≠Bonton. Rječnik očišćen (maknut table/bonton; Leksikon više nije „rječnik”).

> **2026-07-26:** Pairing/copy prolaz: agricole light-band + bidirekcionalni tag komplem.; 34 slash-boca razdvojene; Holts Clubhouse scrape (34 čl.) + gap map; Club facts (tanini, pepeo, Boveda RH, vino/žestice); 16 brand blurba; krivi URL-ovi (ADN, Perdomo, Camacho, Cohiba); filter tipa pića u Pairing. Testovi 279/279.

> **2026-07-26:** Soft-band drink→cigara: `softBandRank` (max−5 + day seed + cycle); UI samo taj smjer. Audit 779×2394: mean band 35.6, bandSize==1 1.9% (gate OK, formula netaknuta). Izvještaj `01_work/output/SOFT-BAND-RANK-AUDIT.md`.

> **2026-07-26:** Klub facts/kviz krugovi 6–8 (nastavak Claude sesije): 148→190 facts, 148→196 quiz u `club.json`; bez em dasha / dimka.

> **2026-07-26:** HR rječnik (puff): **dim** (brojivo: prvi dim, jedan dim). Ne: dimka, povlačenje, potez, usis. Tvar/atmosfera i dalje *dim*.

> **2026-07-26:** HR spirits: gin/tequila pipeline (scrape→Excel→calibrate-master→JSON); brandy refresh + orphan merge. Katalog: gin 70, tequila 26, brandy 98. Branch `catalog-hr-gin-tequila-cognac`.

> **2026-07-26:** Bonton salon: „kuća” (agens) → „domaćin”; „kućna pravila” / „kućni rezač” ostaju. Prije: „javna pušionica” → „cigar lounge”; XI 3. pravilo.

> **2026-07-25:** Flavor scrape: CW HTTP (VariantInfo + aroma canvas; 429→resume/backoff). Famous: urllib/CAPTCHA; Cursor browser `fetch` radi — 22 linije u korpusu. Learning: `knowledge/learnings/shop-flavor-scrape.md`.

> **2026-07-24:** Cigare na popisu: „od X €” samo kad je X stvarno najniža stick cijena; LE/krivi brend URL i sampler/pack isključeni iz zadane cijene. HR bilješke: pokrov→wrapper (runtime + generatori); filler/binder u brands.

> **2026-07-24:** Katalog: filter oblika (Robusto/Toro/…) opet vidljiv uz indeks brendova; odabir oblika prebacuje na filtrirani ravni popis (+ BrandSheet poštuje filter).

> **2026-07-23:** Round 3 C/D/J/B: katalog **2729 / 5528**; residual J 0; lexicon `slugs` 36; dims 239 + 28 dash leftover; H/I exact-URL fill out of scope (no invent).

> **2026-07-22:** App dijakritike: cijeli `hrGuide.json` + pića/notes (`doslađivanje`, `Čist`, `klasična`, `kuća`, `više regija`/`miješanje`); shops + regions.uskladjeno.

> **2026-07-22:** Prolaz dijakritika u draftu bontona (gl. pića/čaša i cijeli rukopis): skener visoke pouzdanosti; ispravak `nepceu` → `nepcu` u gl. 13; ostalo čisto (filename `pusackog` namjerno ASCII).

> **2026-07-22:** Exhaustivni audit pairing scorea: 3104 cigare × 633 pića = 1 964 832 parova; μ≈48.9, σ≈21.2; JB/χ² odbacuju Gaus; invarijante OK. Izvještaj `01_work/output/PAIRING-SCORE-AUDIT.md`, skripta `app/scripts/audit-pairing-distribution.mts`.

> **2026-07-20:** App: Brand Index (Catalog chip Brendovi + Excel sheet); Batch A remap Padrón + Drew Estate Additional Vitolas. Audit sad 26 brendova.

> **2026-07-20:** App katalog: AJ Fernandez usklađen s humidor.hr (Blend 15, Last Call, Enclave, New World, Bellas Artes…); Additional Vitolas audit → `docs/superpowers/specs/2026-07-20-cigar-additional-vitolas-audit.md`.

> **2026-07-20:** Jedini kanonski draft: `docs/bonton/KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md`. Backup + PDF → `docs/bonton/archive/`. README u bonton/.
