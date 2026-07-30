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
}

export interface EveningSessionResult {
  /** true ako je stvarno skinuta jedna iz humidora */
  consumed: boolean;
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
  });

  let consumed = false;
  // popušena cigara odlazi iz zalihe — humidor prati stvarno stanje
  if (input.consumeStock !== false) {
    consumed = consumeFromStock(input.cigarId) != null;
  }

  if (input.markTried !== false) {
    const ids = drinkId ? [input.cigarId, drinkId] : [input.cigarId];
    for (const id of ids) {
      const cur = getItemState(id);
      if (!cur.tried) updateItem(id, { tried: true });
    }
  }

  return { consumed, stockAfter: totalStock(input.cigarId) };
}
