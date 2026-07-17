// Zapis večeri u dnevnik + oznaka "probao" na obje stavke.
import { addJournalEntry, getItemState, updateItem } from "../store/collection";

export interface EveningSessionInput {
  cigarId: string;
  drinkId: string;
  rating: number | null;
  note: string;
  markTried?: boolean;
}

/** Spremi pairing u dnevnik; po defaultu označi cigaru i piće kao probane. */
export function logEveningSession(input: EveningSessionInput): void {
  const note = input.note.trim();
  addJournalEntry({
    cigarId: input.cigarId,
    drinkId: input.drinkId,
    rating: input.rating,
    note,
  });

  if (input.markTried === false) return;

  for (const id of [input.cigarId, input.drinkId]) {
    const cur = getItemState(id);
    if (!cur.tried) updateItem(id, { tried: true });
  }
}
