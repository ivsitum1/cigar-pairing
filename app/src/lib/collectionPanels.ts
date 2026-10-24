// Filteri članstva panela Kolekcija / Humidor — bez UI ovisnosti, lako testirati.
import type { ItemState, JournalEntry } from "../store/collection";

/** Shortlist: probano / ocjena / bilješka, bez Imam i bez wishlista. */
export function shortlistItemIds(
  items: Record<string, ItemState>,
  journal: JournalEntry[] = [],
): string[] {
  const rated = new Set<string>();
  for (const j of journal) {
    if (j.rating == null) continue;
    rated.add(j.cigarId);
    if (j.drinkId) rated.add(j.drinkId);
  }
  const fromItems = Object.entries(items)
    .filter(
      ([id, s]) =>
        !s.owned &&
        !s.wishlist &&
        (s.tried || s.rating != null || !!s.note || rated.has(id)),
    )
    .map(([id]) => id);
  const out = new Set(fromItems);
  // ocjena u dnevniku nakon migracije rating-only stavke (item obrisan)
  for (const id of rated) {
    if (items[id]) continue;
    out.add(id);
  }
  return [...out];
}

/** Go-to omiljeno — Collection panel; neovisno o wishlist/Kupovini. */
export function favoriteItemIds(items: Record<string, ItemState>): string[] {
  return Object.entries(items)
    .filter(([, s]) => s.favorite)
    .map(([id]) => id);
}

/** Imam, ali još 0 komada u svim humidorima (kandidat za QuickAdd / tab Kolekcija). */
export function ownedWithoutStockIds(
  items: Record<string, ItemState>,
  totalStockOf: (itemId: string) => number,
): string[] {
  return Object.entries(items)
    .filter(([id, s]) => s.owned && totalStockOf(id) === 0)
    .map(([id]) => id);
}
