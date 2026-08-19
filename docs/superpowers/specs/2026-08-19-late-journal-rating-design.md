# Late Journal Rating Design

## Goal

Omogućiti naknadni unos ocjene za već zabilježenu večer u `collection` i `calendar` prikazima, bez diranja opće ocjene cigare u kolekciji.

## Confirmed Behavior

- Naknadno unesena ocjena mijenja samo `journal.rating` tog konkretnog zapisa večeri.
- Polje `collection.items[id].rating` ostaje zasebna, opća `Moja ocjena` za cigaru ili piće.
- UI mora jasnije razgraničiti ta dva zapisa ocjene.

## Recommended Approach

Preporučeni pristup je lokalni editor na samom journal zapisu:

- u `CollectionPage` journal listi
- u `JournalCalendar` / `JournalCard`

Kad zapis još nema `rating`, kartica prikazuje kontrolu `Ocjena večeri` s izborom `1–10`. Odabir odmah poziva `updateJournalEntry(entry.id, { rating })`.

Ovaj pristup je najmanje dvosmislen jer korisnik ocjenu upisuje upravo ondje gdje vidi konkretnu večer, datum i bilješku.

## UI Separation

Da bi se dvije ocjene prestale miješati:

- `Moja ocjena` ostaje naziv za opću ocjenu na kartici cigare / pića
- `Ocjena večeri` postaje naziv za ocjenu jednog journal zapisa
- uz journal editor treba dodati kratku pomoćnu rečenicu da ta ocjena vrijedi samo za tu večer

Predloženi smisao copyja:

- `Ocjena večeri`
- kratki hint: `Vrijedi samo za ovu zabilježenu večer. Ne mijenja Moju ocjenu cigare.`

## Data Flow

1. `EveningSessionSheet` i dalje može spremiti večer s ocjenom ili bez nje.
2. Ako je večer spremljena bez ocjene, `journal.rating` ostaje `null`.
3. `CollectionPage` i `JournalCalendar` prepoznaju `rating == null` i prikazuju editor.
4. Nakon odabira vrijednosti poziva se `updateJournalEntry`.
5. `useCollection()` ponovno re-renderira oba prikaza s novim stanjem.

## Files Likely To Change

- `app/src/pages/CollectionPage.tsx`
- `app/src/pages/HumidorPage.tsx`
- `app/src/i18n/index.tsx`
- po potrebi `app/src/store/collection.test.ts`

## Testing

Treba provjeriti:

- da se editor vidi samo kad `journal.rating` nedostaje
- da odabir sprema ocjenu samo u taj journal zapis
- da se `collection.items[id].rating` ne mijenja
- da se nakon spremanja u oba prikaza vidi broj umjesto editora

## Out of Scope

- sinkronizacija journal ocjene s općom ocjenom cigare
- retroaktivno otvaranje `TastePrompt` toka
- uređivanje već postojeće journal ocjene, osim ako se to naknadno posebno zatraži
