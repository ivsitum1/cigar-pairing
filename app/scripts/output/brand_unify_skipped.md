# Brand unify — skipped candidates

Source: `brand_dupe_candidates.json` (28) + `la-aroma-unify-review.md`.
Decision gate: merge only when the same physical product is sold under two market names.
Ambiguous / namesake / orthography → skip (do not guess).

## Merged (this branch)

| From | To | Reason |
|------|-----|--------|
| La Aroma del Caribe | La Aroma de Cuba | Confirmed EU/HR market name for Ashton La Aroma de Cuba (Option A). EE No. 5 → EE #5 merge; No. 1/2/4/60 kept as distinct lines under de Cuba. |

## Skipped

| Candidate | Type | Reason |
|-----------|------|--------|
| Aliados, Bauza, Bella Cuba, Bock y Ca., Cain Black, El Rey del Mundo, Excalibur, Gispert, Henry Clay, Illusione, La Antiguedad, La Capitana, La Gloria Cubana, La Ley, Montecristo (NW), Perla del Mar, Romeo y Julieta (NW), Saint Luis Rey, Santa Damiana, Tabacos Baez, Tatuaje, Toraño, Warped | non-cuban-habanos-hint | Non-Cuban namesake or Cuban-style marketing — **different physical product** from any Habanos namesake; not a market-name alias. |
| Silencio | non-cuban-habanos-hint | EU trademark for General Cigar / STG non-Cuban Cohiba Red Dot. Catalog has no separate US “Cohiba Red Dot” brand to merge into; Cuban Cohiba must not absorb Silencio. Leave as own brand. |
| Don Pepin ↔ Don Pépin García | orthography / parallel catalog | Same house, overlapping line names, but line spellings and SKU sets differ (`Original` vs `Pepin Garcia Original`, etc.). Not a clean market-name pair; needs a dedicated spelling/line remap review before renameBrand. |
| Exact-norm / shared-root pairs (if any beyond La Aroma) | — | None present as confirmed market-name duplicates in this sweep beyond La Aroma. |

## Notes

- Idempotent path: `taxonomy/la-aroma-del-caribe.json` + `apply-taxonomy.py` (renameBrand + EE #5 line merge + id rederive on brand rename → `cigarIdAliases.json`).
- Re-run: `cd app && python scripts/apply-taxonomy.py --check` should report `changed: false` after first apply.
