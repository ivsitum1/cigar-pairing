import type { ItemState } from "../store/collection";
import { parseCigarItemId } from "./cigarItemId";

/** Stavka ide na Kupovinu: lista želja, ili restock kad je owned a zaliha 0. */
export function isShoppingWishlistItem(state: ItemState, stock: number): boolean {
  return state.wishlist && (!state.owned || stock === 0);
}

/**
 * Linije cigara koje idu na Kupovinu — Kupovina ih prikazuje po liniji, a
 * stanje se čuva po vitoli.
 *
 * Zaliha se gleda na ključu na kojem je i želja zapisana: ključ vitole samo
 * svoju (potrošen Figurado traži nabavu i kad Robusto iste linije još stoji u
 * humidoru), goli ključ linije cijelu liniju. „Imam” se, obrnuto, čita s cijele
 * linije — posjedovanje formata vrijedi za liniju bez obzira na kojem je ključu
 * označeno.
 */
export function shoppingWishlistLineIds(
  items: Record<string, ItemState>,
  stock: { item: (itemId: string) => number; line: (cigarId: string) => number },
): Set<string> {
  const ownedLines = new Set<string>();
  for (const [id, s] of Object.entries(items)) {
    if (s.owned) ownedLines.add(parseCigarItemId(id).cigarId);
  }

  const out = new Set<string>();
  for (const [id, s] of Object.entries(items)) {
    if (!s.wishlist) continue;
    const { cigarId, vitolaSlug } = parseCigarItemId(id);
    const left = vitolaSlug ? stock.item(id) : stock.line(cigarId);
    const owned = s.owned || ownedLines.has(cigarId);
    if (isShoppingWishlistItem({ ...s, owned }, left)) out.add(cigarId);
  }
  return out;
}
