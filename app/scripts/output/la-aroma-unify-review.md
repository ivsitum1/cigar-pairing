# P1 Review: La Aroma de Cuba ↔ La Aroma del Caribe

**Branch:** `fix/la-aroma-brand-unify`  
**Status:** REVIEW ONLY — no merge without choosing A/B/C  
**Recommendation:** Option A

## Facts (from catalog + brands.json)

- Same physical product family (Ashton / Pepín García, Nicaragua, 2002 relaunch).
- US name: **La Aroma de Cuba**; EU/HR name: **La Aroma del Caribe**.
- `brands.json` already states del Caribe is the EU name for de Cuba.
- Catalog counts: **8** de Cuba lines, **5** del Caribe lines (all Edición Especial No. 1/2/4/5/60).

## Line mapping table

| del Caribe (EU) | de Cuba (US) | Match confidence | Notes |
|---|---|---|---|
| Edición Especial No. 1 | — | none | No de Cuba EE #1 in catalog |
| Edición Especial No. 2 | — | none | No de Cuba EE #2 in catalog |
| Edición Especial No. 4 | — | none | No de Cuba EE #4 in catalog |
| Edición Especial No. 5 | Edición Especial #5 | **high** | Same ring×length 52×140mm; wrappers differ in data (H-2000 vs Ecuador Habano) — verify before hard merge |
| Edición Especial No. 60 | — | none | No de Cuba EE #60 in catalog |
| — | Base Line | n/a | de Cuba only |
| — | Connecticut | n/a | de Cuba only |
| — | La Aroma de Cuba (eponymous) | n/a | de Cuba only |
| — | Mi Amor | n/a | de Cuba only |
| — | Noblesse | n/a | de Cuba only |
| — | Pasión | n/a | de Cuba only |
| — | Reserva | n/a | de Cuba only |

### ID inventory

**de Cuba**
- `cig-la-aroma-de-cuba-base-line`
- `cig-la-aroma-de-cuba-connecticut`
- `cig-la-aroma-de-cuba-edicion-especial-5`
- `cig-la-aroma-de-cuba-la-aroma-de-cuba`
- `cig-la-aroma-de-cuba-mi-amor`
- `cig-la-aroma-de-cuba-noblesse`
- `cig-la-aroma-de-cuba-pasion`
- `cig-la-aroma-de-cuba-reserva`

**del Caribe**
- `cig-la-aroma-del-caribe-edicion-especial-no-1`
- `cig-la-aroma-del-caribe-edicion-especial-no-2`
- `cig-la-aroma-del-caribe-edicion-especial-no-4`
- `cig-la-aroma-del-caribe-edicion-especial-no-5` → candidate merge into `…-edicion-especial-5`
- `cig-la-aroma-del-caribe-edicion-especial-no-60`

## Options (choose one)

### Option A — one brand + market alias (recommended)

1. Canonical brand: **La Aroma de Cuba**.
2. Add market alias field or `renameBrand`-style mapping: `La Aroma del Caribe` → `La Aroma de Cuba` (EU/HR display name).
3. Move del Caribe Edición Especial lines under de Cuba (keep EU `regionLinks`).
4. Merge only EE No. 5 ↔ EE #5 after wrapper verification; keep No. 1/2/4/60 as distinct lines under de Cuba.
5. `cigarIdAliases.json`: map all `cig-la-aroma-del-caribe-*` → new de Cuba IDs so deep-links / localStorage survive.
6. Remove or redirect `La Aroma del Caribe` from `brands.json`.

### Option B — keep two brands, cross-note

1. Keep both brand entries.
2. Strengthen both blurbs + DetailSheet callout: “sold as *La Aroma de Cuba* in the US / *del Caribe* in EU”.
3. No ID changes; lowest risk, duplicate brand list remains.

### Option C — del Caribe as line family under de Cuba

1. Collapse del Caribe brand into a line prefix under de Cuba (e.g. line `Edición Especial No. N`).
2. Heaviest markets/link rewiring; probably overkill given Option A.

## Proposed alias stubs (Option A only — NOT applied)

```json
{
  "cig-la-aroma-del-caribe-edicion-especial-no-5": "cig-la-aroma-de-cuba-edicion-especial-5",
  "cig-la-aroma-del-caribe-edicion-especial-no-1": "cig-la-aroma-de-cuba-edicion-especial-no-1",
  "cig-la-aroma-del-caribe-edicion-especial-no-2": "cig-la-aroma-de-cuba-edicion-especial-no-2",
  "cig-la-aroma-del-caribe-edicion-especial-no-4": "cig-la-aroma-de-cuba-edicion-especial-no-4",
  "cig-la-aroma-del-caribe-edicion-especial-no-60": "cig-la-aroma-de-cuba-edicion-especial-no-60"
}
```

Implementation path when approved: extend existing taxonomy/`cigarIdAliases.json` mechanism (see commit `fafca5c` renameBrand pattern) — do not hand-edit `cigars.json` alone.

## Decision needed from owner

- [ ] Confirm option **A / B / C**
- [ ] Confirm EE No. 5 ↔ EE #5 merge (wrapper discrepancy H-2000 vs Ecuador Habano)
- [ ] Confirm EU `regionLinks` must be preserved on merged/moved rows
