# YouTube sources (research corpus)

Local caption dumps for Club / rum research live under
`app/scripts/output/youtube/` (gitignored). They are **not** shipped in the PWA.

## Policy

- Use transcripts as research input only.
- Ship original HR/EN prose in Club / lexicon / drink notes.
- Cite channels or specific videos in `app/src/data/clubSources.json` (label + URL).
- Do not treat YouTube opinion as authority for `additiveStatus` / `additiveSource`.

## Pilot

- Channel: [Steve the Barman UK](https://www.youtube.com/@StevetheBarmanUK)
- Registry: `app/scripts/data/youtube/channels.json`
- Pipeline: `youtube-inventory.py` → `youtube-fetch-captions.py` → `youtube-classify.py` → `youtube-match-rums.py`

See `docs/superpowers/specs/2026-08-21-youtube-rum-corpus-design.md`.
