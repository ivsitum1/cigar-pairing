// Filteri članstva panela Kolekcija / Humidor — bez UI ovisnosti, lako testirati.
import type { ItemState } from "../store/collection";

/** Shortlist: probano / ocjena / bilješka, bez Imam i bez wishlista. */
export function shortlistItemIds(
  items: Record<string, ItemState>,
): string[] {
  return Object.entries(items)
    .filter(
      ([, s]) =>
        !s.owned && !s.wishlist && (s.tried || s.rating != null || !!s.note),
    )
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

