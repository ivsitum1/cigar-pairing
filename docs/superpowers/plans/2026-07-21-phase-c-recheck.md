# Faza C — recheck za Cursor (očisti brand_dictionary prije generiranja)

**Datum:** 2026-07-21
**Vlasnik:** Cursor (grana `cursor/phase-c-brand-data-d678`)
**Zašto:** engine Faze C je gotov i integriran u `build-market-cigars.py` (`--phase c/all`).
Probni run daje **773 novih linija (514→1287), +167 brendova, idempotentno, 1:1, embargo 0**.
ALI ~30 novih „brendova" su zapravo **brend+linija** stringovi → NE ispunjava „vrhunska
kvaliteta". Zato je generiranje Faze C **zadržano**; katalog ostaje na čistoj Fazi B (785).

## Problem

`brand_dictionary.json` ponekad mapira **sub-linijski slug** na brend koji uključuje
liniju, umjesto na baznu marku. Primjeri (slug → trenutačno → **treba**):

| slug | trenutačno (krivo) | treba (bazni brend) |
|------|--------------------|---------------------|
| `ortega-serie-d-exclusivo` | Ortega Serie D. Exclusivo | **Ortega** |
| `caldwell-blind-man-s-bluff` | Caldwell Blind Man S. Bluff | **Caldwell** |
| `caldwell-eastern-standard-dos-firmas` | Caldwell Eastern Standard Dos Firmas | **Caldwell** |
| `southern-draw-jacob-s-ladder` | Southern Draw Jacob S. Ladder | **Southern Draw** |
| `southern-draw-rose-of-sharon` | Southern Draw Rose of Sharon | **Southern Draw** |
| `don-pepin-garcia-serie-jj*` | Don Pepin Garcia Serie Jj | **Don Pépin García** |
| `jaime-garcia-reserva-especial*` | Jaime Garcia Reserva Especial | **Jaime García** (ili **My Father**) |
| `padilla-serie-1968*`, `padilla-reserva*`, `padilla-1932*` | … | **Padilla** |
| `the-griffin-s*` | The Griffin S. / Nicaragua | **Griffin's** |
| `torano-exodus-1959*` | Torano Exodus 1959 50 Years | **Toraño** |
| `room-101-master-collection*` | Room 101 Master Collection | **Room 101** |
| `gran-habano-vintage*`, `gran-habano-g-a-r*` | Gran Habano Vintage 2002 | **Gran Habano** |
| `la-aroma-de-cuba-mi-amor*` | La Aroma de Cuba Mi Amor | **La Aroma de Cuba** |
| `la-gloria-cubana-serie-r*` | La Gloria Cubana Serie R. Esteli | **La Gloria Cubana** |
| `kristoff-gc-signature-series` | Kristoff Gc Signature Series | **Kristoff** |
| `casa-fernandez-miami-reserva*` | Casa Fernandez Miami Reserva | **Casa Fernández** |
| `las-calaveras-edicion-limitada*` | Las Calaveras Edicion Limitada | **Crowned Heads** (Las Calaveras je linija) |
| `cromagnon-*-by-roma-craft`, `intemperance-*-by-roma-craft` | … By Roma Craft | **RoMa Craft** |

(Puna lista 99 sumnjivih: `python3 -c` heuristika u chatu; gornje su sigurni popravci.
Neki su OK kao brend i ne treba dirati: Patoro, The Tabernacle, El Rey del Mundo,
Flor de las Antillas, The Judge/Oscar/Traveler — koristi domensku prosudbu.)

## Zadatak (Cursor)

1. U `app/scripts/data/brand_dictionary.json` popravi sub-linijske slugove da mapiraju
   na **bazni brend** (gornja tablica + prosudba za ostatak 99). Cilj: vrijednosti su
   PRAVE marke, ne brend+linija.
2. Ako bazni brend nije u `new_brands_draft.json`, dodaj ga (country/founded/blurb).
   Ukloni draft unose koji su zapravo linije (npr. „Ortega Serie D. Exclusivo").
3. Ne diraj: `cigars.json`, `brands.json`, `build-market-cigars.py`, komponente.
4. Provjera bez pisanja u app: `cd app && python3 scripts/build-market-cigars.py --phase all`
   pa pogledaj `scripts/output/phase_hold.json` stats i novonastale brendove — ne smije
   biti brenda s vitolom/„Serie …"/„by …" u imenu. `npm test` mora ostati zelen (nakon
   što se generira, market-invariant + Habanos + embargo guard vrijede).
5. Kad je čisto, javi — Claude (ili ti) pokrene `--phase all`, commita generiranu Fazu C
   (deterministički, identično) i katalog naraste na ~1300.

## Napomena o OCR-u

Malformirani brendovi + inflacija „Serie" tokena obarali su `ocrMatch.test.ts`
(Partagás → kriva pogodba). Nakon čišćenja rječnika ponovno provjeri OCR test; ako
i čist Faza-C skup mijenja ranking, prijavi (možda treba blaga robusnost u matcheru).
