// Zapis večeri u dnevnik + oznaka "probao" na obje stavke + skidanje iz humidora.
import { addJournalEntry, getItemState, updateItem } from "../store/collection";
import { consumeFromStock } from "../store/humidor";

export interface EveningSessionInput {
  cigarId: string;
  drinkId: string;
  rating: number | null;
  note: string;
  markTried?: boolean;
  /** false = ne diraj zalihu (npr. cigara nije bila iz humidora). */
  consumeStock?: boolean;
}

/** Spremi spoj u dnevnik; po zadanome označi cigaru i piće kao probane. */
export function logEveningSession(input: EveningSessionInput): void {
  const note = input.note.trim();
  addJournalEntry({
    cigarId: input.cigarId,
    drinkId: input.drinkId,
    rating: input.rating,
    note,
  });

  // popušena cigara odlazi iz zalihe — humidor prati stvarno stanje
  if (input.consumeStock !== false) consumeFromStock(input.cigarId);

  if (input.markTried === false) return;

  for (const id of [input.cigarId, input.drinkId]) {
    const cur = getItemState(id);
    if (!cur.tried) updateItem(id, { tried: true });
  }
}
