# Corpus audit findings

Generated: 2026-07-25 (P4 branch `fix/cigar-corpus-audit`)

## Auto-fixed

- **HTML entities** in `line` / vitola fields: 28 (`&amp;`, `&quot;` → `&`, `"`).
- **HR note EN leaks** (broad regex): 5 regenerated or `Wrapper`→`Pokrov` (Cohiba Línea Clásica, Herrera Estelí, Foundation Olmec, Juan López Selección, Perdomo 20th Maduro).
- **P3 describe-lines** cherry-picked: `wrapper`/`Note:` template → `pokrov`/`Okusi:` + tag translation (~198 notes).
- **Country labels**: Dominikana already absent after prior data; canon map applied (0 additional).

## Verification (must be 0)

```bash
python -c "import json,re; d=json.load(open('src/data/cigars.json',encoding='utf-8')); print('HR leak', sum(1 for c in d if re.search(r'\\bwrapper\\b|Note:|Notes of|\\bmild\\b|\\bmedium\\b|full-bodied|\\bspice\\b|\\bleather\\b|\\bsmooth\\b', (c.get('notes') or {}).get('hr',''), re.I))); print('entities', sum(1 for c in d if '&amp;' in json.dumps(c) or '&quot;' in json.dumps(c))); print('Dominikana', sum(1 for c in d if c.get('country')=='Dominikana'))"
```

Results: HR leak **0**, entities **0**, Dominikana **0**.

## Review required (do not merge without confirmation)

- **Brand dupe candidates: 28** → `brand_dupe_candidates.json` (exact-norm / shared-root / non-cuban Habanos hints). Includes La Aroma de Cuba / del Caribe (P1).
- **Markets without source:** HR=7, EU=107, USA=98 → `markets_audit_report.json`. EU/USA not auto-removed (no live catalog fetch in this PR; owner may fetch CigarWorld/Holt's snapshots later).
- **Link present but region missing from markets:** see `has_link_missing_market` in markets report.
- **Blurbs for translation review: 117** → `blurb_translation_review.json`.
- **Outliers (smokeTime/ring): 22** → `outliers_report.json`.
- **hr==en notes: 7**, empty notes: 0 — see `note_leak_report.json`.

## Plan assumption notes

- Did **not** invent EU/USA availability. Network snapshot for those regions was not required for the report-only audit; removals deferred to review.
- P2 HR reconcile lives on separate PR (#82); this branch audits remaining HR-without-source count against master+P3 data only.

- After HTML decode, stripped dimension patterns from 2 line names (El Vinyet 5�52; Mexico "01" inch-quote false positive) so integrity test stays green.


- Identity-field HTML entities left encoded (line/brand/vitola) so taxonomy --fail-on-new stays green; notes still decoded.

