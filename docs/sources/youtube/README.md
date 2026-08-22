# YouTube sources (research corpus)

Local caption dumps for Club / rum research live under
`app/scripts/output/youtube/` (gitignored). They are **not** shipped in the PWA.

## Policy

- Use transcripts as research input only.
- Ship original HR/EN prose in Club / lexicon / drink notes.
- Cite channels or specific videos in `app/src/data/clubSources.json` (label + URL).
- Do not treat YouTube opinion as authority for `additiveStatus` / `additiveSource`.

## Pilot channels

- Rum/spirits: [Steve the Barman UK](https://www.youtube.com/@StevetheBarmanUK), @RumVerdict, @therumrevival, @BottledVerdict, @LiquidInfo1
- Cigar: @CigarsDaily, @holtscigars, @CigarrNation, @cigaraficionado, @MayfairCigarLedger, @GentlemensCollectiveOfficial, @Cigarsdotcom
- Etiquette: @WilliamHansonEtiquette
- Registry: `app/scripts/data/youtube/channels.json`
- Pipeline: `youtube-inventory.py` → `youtube-fetch-captions.py` → `youtube-classify.py` → `youtube-match-rums.py` / `youtube-match-cigars.py` → `summarize-youtube-cigar-proposals.py`
- Curated merges: `scripts/data/youtube/rum_enrichments.json` / `cigar_enrichments.json` via `apply-youtube-*-enrichment.py`
- Review queue (gitignored): `scripts/output/youtube/cigar_review_queue.json`

### Captions ops

```powershell
cd app
python scripts/youtube-batch.py captions --all-enabled
# Age-gated channels (e.g. Holt's): pass browser cookies once
python scripts/youtube-batch.py captions --channel holtscigars --cookies scripts/data/youtube/cookies.txt
# Or Netscape cookies.txt (preferred on Windows Chrome 127+)
python scripts/youtube-fetch-captions.py --channel holtscigars --cookies data/youtube/cookies.txt
# Ops helpers
python scripts/youtube-caption-status.py
python scripts/youtube-reset-age-gate.py --channel holtscigars
powershell -File scripts/youtube-run-corpus-phases.ps1 -Phase 1A
```

Age-gate / members-only videos are marked `captionStatus: unavailable` so resume does not hammer them.

See `docs/superpowers/specs/2026-08-21-youtube-rum-corpus-design.md`.
