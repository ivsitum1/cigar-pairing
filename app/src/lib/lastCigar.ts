// Zadnja cigara iz humidora → ponuda da ide na listu želja.
//
// Odluka stoji ovdje, a ne u komponenti, jer je isti trenutak dolazi s dva
// mjesta: zapis večeri (EveningSessionSheet) i ručno skidanje u humidoru
// (−1 na kartici zalihe).
import { getItemState } from "../store/collection";
import { lineTotalStock, totalStock } from "../store/humidor";
import { parseCigarItemId } from "./cigarItemId";

/**
 * Nakon što je zaliha već smanjena: treba li ponuditi listu želja?
 *
 * Da — kad je to bila zadnja tog ključa, a stavka nije već na listi.
 * `itemId` je ključ zalihe koji je stvarno skinut (`null` = ništa nije skinuto,
 * cigara nije bila iz humidora).
 *
 * Ključ nosi vitolu, pa se i zaliha broji na njoj: zadnji Figurado iz serije
 * prazno je mjesto i kad Robusto iste linije još stoji u humidoru — to su dva
 * različita formata, kupuju se odvojeno. Goli ključ linije (zaliha unesena bez
 * formata) i dalje gleda cijelu liniju, jer se na njemu ništa drugo ne broji.
 */
export function shouldOfferWishlist(itemId: string | null): boolean {
  if (!itemId) return false;
  const { cigarId, vitolaSlug } = parseCigarItemId(itemId);
  const left = vitolaSlug ? totalStock(itemId) : lineTotalStock(cigarId);
  if (left > 0) return false;
  // želja upisana na cijelu liniju pokriva i njezine vitole
  return !getItemState(itemId).wishlist && !getItemState(cigarId).wishlist;
}
