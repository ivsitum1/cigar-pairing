// Zapis večeri u dnevnik + oznaka "probao" na obje stavke + skidanje iz humidora.
import { addJournalEntry, getItemState, updateItem } from "../store/collection";
import { consumeFromStock, totalStock } from "../store/humidor";

export interface EveningSessionInput {
  cigarId: string;
  /** null / undefined = solo cigara */
  drinkId?: string | null;
  rating: number | null;
  note: string;
  markTried?: boolean;
  /** false = ne diraj zalihu (npr. cigara nije bila iz humidora). */
  consumeStock?: boolean;
  /** ISO trenutak večeri; bez njega je zapis „sada”. */
  date?: string;
}

export interface EveningSessionResult {
  /** true ako je stvarno skinuta jedna iz humidora */
  consumed: boolean;
  /** Ključ zalihe koji je skinut — zna se razlikovati od zapisa po vitoli. */
  consumedItemId: string | null;
  stockAfter: number;
}

/** Spremi spoj u dnevnik; po zadanome označi cigaru i piće kao probane. */
export function logEveningSession(input: EveningSessionInput): EveningSessionResult {
  const note = input.note.trim();
  const drinkId = input.drinkId ?? null;
  addJournalEntry({
    cigarId: input.cigarId,
    drinkId,
    rating: input.rating,
    note,
    date: input.date,
  });

  let consumedItemId: string | null = null;
  // popušena cigara odlazi iz zalihe — humidor prati stvarno stanje
  if (input.consumeStock !== false) {
    consumedItemId = consumeFromStock(input.cigarId)?.itemId ?? null;
  }

  if (input.markTried !== false) {
    const ids = drinkId ? [input.cigarId, drinkId] : [input.cigarId];
    for (const id of ids) {
      const cur = getItemState(id);
      if (!cur.tried) updateItem(id, { tried: true });
    }
  }

  return {
    consumed: consumedItemId != null,
    consumedItemId,
    // zaliha se broji na ključu koji je stvarno skinut, inače bi zapis po
    // vitoli gledao praznu policu dok linija u humidoru još stoji
    stockAfter: totalStock(consumedItemId ?? input.cigarId),
  };
}
