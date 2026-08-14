// „Imam” prati stvarnu zalihu.
//
// Popis „Imam (još nije u humidoru)” bio je jednosmjeran: oznaka se palila pri
// kupnji, a nikad se nije gasila. Svaka popušena cigara ostajala je na njemu
// zauvijek, pa je popis rastao unedogled i prestao značiti išta.
//
// Pravilo je jednostavno: zaliha padne na nulu → „Imam” se gasi. Ono što si
// kupio a još nisi složio u humidor ostaje netaknuto (takva stavka nikad nije
// ni imala zalihu), pa popis i dalje radi svoj posao.
import { getItemState, updateItem } from "../store/collection";
import { stockForItemKey } from "../store/humidor";

/**
 * Pozvati NAKON što je zaliha smanjena. Vraća true kad je oznaka ugašena.
 *
 * Ne diraj kod premještanja zalihe s ključa na ključ („Odredi vitolu”) — ondje
 * cigara nije potrošena, samo je dobila ime.
 */
export function releaseOwnedIfEmpty(itemId: string): boolean {
  if (stockForItemKey(itemId) > 0) return false;
  if (!getItemState(itemId).owned) return false;
  updateItem(itemId, { owned: false });
  return true;
}

/**
 * Ono što je u humidoru — tvoje je. Pozvati nakon dodavanja u zalihu.
 *
 * Skida i zvjezdicu, isto kao kvačica „Imam” na kartici: stavka koja je stigla
 * u kutiju nije više popis za kupnju. Kad se popuši zadnja, ponuda „na listu
 * želja?” vraća je natrag ako je stvarno želiš opet.
 */
export function claimOwnedForStock(itemId: string): boolean {
  const state = getItemState(itemId);
  if (state.owned && !state.wishlist) return false;
  updateItem(itemId, { owned: true, wishlist: false });
  return true;
}

/**
 * Neraspoređena stavka („kupio sam, još nije u kutiji") složena je u humidor
 * pod konkretnom vitolom — oznaka seli s golog ključa linije na tu vitolu.
 *
 * Bez toga bi goli ključ zauvijek ostao na popisu „Imam (još nije u humidoru)":
 * zaliha te linije jest veća od nule, ali stoji na drugom ključu, pa ga ni
 * `releaseOwnedIfEmpty` ne bi ugasio. Ocjena i bilješka s linije ostaju.
 */
export function transferOwnedToVitola(fromItemId: string, toItemId: string) {
  claimOwnedForStock(toItemId);
  if (fromItemId === toItemId) return;
  if (!getItemState(fromItemId).owned) return;
  updateItem(fromItemId, { owned: false });
}
