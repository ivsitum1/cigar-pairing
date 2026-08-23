# YouTube stub curation — autonomy run (2026-08-23)

## Goal

Proći **sve** stavke u `cigar_review_queue.json` (+ rum match proposals) **bez stajanja i pitanja**, zatim:

1. ono što je **točno i u skladu** s postojećim enrichments → apply + commit + push + merge (live)
2. ono što **odstupa / sumnjivo** → karantena (korisnik odlučuje kasnije)

## Rules (ne kršiti)

- Originalni HR/EN copy — **nikad** paste transkripta
- HR kanon: *cigara* (padeži), *dim*, *draw* (loan), *sparivanje*; bez eng. *cigar* / *wrapper* u HR
- Schema: `notes.hr` / `notes.en` ≥ 40 znakova; rum može + `cigarHint`
- Grounding: snaga / pokrov / origin / flavorTags iz kataloga — ne izmišljati rare tasting note iz titla

## Pipeline

```
queue → classify → draft (approve) | quarantine → schema+canon check → apply --check → ship
```

### Classify → APPROVE

| Gate | Uvjet |
|------|--------|
| Catalog | `cigarId` / `drinkId` postoji u `cigars.json` / `rums.json` |
| Title | brand + line (ili drink name) u naslovu videa |
| Specificity | linija je najduži match na tom `videoId` (ili ≤3 siblinga) |
| Confidence | ≥ 0.90 |
| Reject | sampler, bundle, gift pack, unboxing-only, listicle multi-brand |

### Classify → QUARANTINE

- Ambiguous sibling match (jedan video → više linija)
- Naslov ne sadrži liniju / brand
- Samo listicle / “Top 10” / “brands ranked”
- Sampler / LE godina koja ne odgovara katalogu
- Catalog notes već dugi (>140 en) — ne pregaziti
- Rum: match bez dediciranog review naslova

Karantena: `app/scripts/data/youtube/enrichment_quarantine.json`

### Draft

- Template po (strength band × wrapper family × origin)
- Tone kao postojeći Ashton/Punch/Davidoff unosi
- `sourceVideoIds` samo kad je video 1:1 s linijom

### Verify

```powershell
python -m unittest test_youtube_enrichment -v
python apply-youtube-cigar-enrichment.py --check
python apply-youtube-rum-enrichment.py --check
# + lokalni HR canon scan (cigar/wrapper u hr notes)
```

### Ship (samo curated + apply + docs/ops)

- **Ne** commitati cookies, `.worktrees`, agent-brain noise
- Branch `feat/youtube-corpus-complete` → push → PR → merge u `master` (Pages deploy)

## Acceptance

- Svi APPROVE prošli schema + HR canon
- Quarantine datoteka s razlozima i count
- Live: GitHub Pages nakon merge
