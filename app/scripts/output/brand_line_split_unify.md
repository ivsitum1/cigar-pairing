# Brand-line split audit & unify (2026-08-01)

## Merged (high confidence) — wave 1

| From | Into | Line(s) |
|------|------|---------|
| Argyle Fumas | Argyle | Fumas, Fumas Connecticut |
| Bahia Blu | Bahia | Blu |
| Cain Black / Ct / Daytona / F. 1 | Cain | Black, Connecticut CT, Daytona, F (+ Habano/Maduro/Serie F cleanup) |
| Don Lino Fumas | Don Lino | Fumas, Fumas Connecticut |
| Nat Sherman Host / Metropolitan / Timeless + orphan Timeless | Nat Sherman | Host, Metropolitan *, Timeless * |
| Lunatic | JFR | Lunatic Classic / El Loquito / Maduro |

Also: La Aroma EE `edicion especial no 5` → `Edición Especial #5`.

## House lines under parent — wave 2 (marked for the reader)

Child marques folded into the house brand; **line name keeps the marque** so the card reads `Kuća › Imenovana linija`. House blurbs in `brands.json` say explicitly that named lines live under the house, not as separate brands.

| From | Into | How marked |
|------|------|------------|
| Four Kicks, La Imperiosa, Juarez, Mil Dias, Luminosa | **Crowned Heads** | e.g. Four Kicks, Juarez Limited Edition… |
| Charter Oak, The Tabernacle, Olmec, Menelik, El Gueguense, Wise Man | **Foundation** | Tabernacle / Charter Oak / Olmec as lines (+ vitolas) |
| Sobremesa, Mi Querida, Querida | **Dunbarton T&T** | Sobremesa Fino, Mi Querida Ancho Corto, … |

Script: `app/scripts/unify_house_lines.py`. Catalog 3738 → 3711.

## Still open (not house-line in the same sense)

~~Don Pepin ↔ Don Pépin García~~ → merged 2026-08-01  
~~Aliados ↔ Cuba Aliados~~ → merged 2026-08-01  
~~The Oscar → Oscar Valladares~~ → merged 2026-08-01  

Script: `app/scripts/unify_orthography_brands.py`. Catalog 3711 → 3701.

Leaf by Oscar remains a separate brand key (portfolio sibling; OV already has Leaf * lines).

## Fix during wave 1

`apply-taxonomy.py`: renameBrand **source** non-identity line remaps now win over destination identity maps (prevents Argyle Fumas Connecticut → Argyle Connecticut). Restored lost `cig-argyle-fumas-connecticut` from baseline.
