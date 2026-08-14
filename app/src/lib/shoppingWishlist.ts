import type { ItemState } from "../store/collection";

/** Stavka ide na Kupovinu: lista želja, ili restock kad je owned a zaliha 0. */
export function isShoppingWishlistItem(state: ItemState, stock: number): boolean {
  return state.wishlist && (!state.owned || stock === 0);
}

/**
 * Dopuna zalihe: imaš je i označena je, ali u humidorima je nema.
 *
 * Dvije su to liste, ne jedna. „Želim ovo kupiti” i „imam je, ali je nema u
 * humidoru” traže različitu odluku u trgovini, pa se na Kupovini prikazuju
 * odvojeno — zajedno su izgledale kao da je lista želja puna stvari koje već
 * imaš.
 */
export function isRestockItem(state: ItemState, stock: number): boolean {
  return state.wishlist && state.owned && stock === 0;
}
