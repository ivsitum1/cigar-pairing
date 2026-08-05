// Zadnja cigara iz humidora → ponuda da ide na listu želja.
//
// Odluka stoji ovdje, a ne u komponenti, jer je isti trenutak dolazi s dva
// mjesta: zapis večeri (EveningSessionSheet) i ručno skidanje u humidoru
// (−1 na kartici zalihe).
import { lineState } from "../store/collection";
import { lineTotalStock } from "../store/humidor";
import { parseCigarItemId } from "./cigarItemId";

/**
 * Nakon što je zaliha već smanjena: treba li ponuditi listu želja?
 *
 * Da — kad je to bila zadnja u SVIM humidorima, a stavka nije već na listi.
 * `itemId` je ključ zalihe koji je stvarno skinut (`null` = ništa nije skinuto,
 * cigara nije bila iz humidora).
 */
export function shouldOfferWishlist(itemId: string | null): boolean {
  if (!itemId) return false;
  const { cigarId } = parseCigarItemId(itemId);
  if (lineTotalStock(cigarId) > 0) return false;
  return !lineState(cigarId).wishlist;
}
