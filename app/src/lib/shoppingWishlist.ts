import type { ItemState } from "../store/collection";

/** Stavka ide na Kupovinu: lista želja, ili restock kad je owned a zaliha 0. */
export function isShoppingWishlistItem(state: ItemState, stock: number): boolean {
  return state.wishlist && (!state.owned || stock === 0);
}
