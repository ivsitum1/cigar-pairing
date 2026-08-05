// "Gdje kupiti" za bocu: lista trgovina umjesto jednog Google linka.
//
// Pravilo je isto kao kod cigara — nikad ne tvrdi vise nego sto app zna:
//   product — `priceUrl` je potvrdena stranica bas te boce,
//   search  — trgovina ima pretragu po nazivu (link stvarno trazi tu bocu),
//   browse  — znamo trgovinu, ali ne i njen endpoint pretrage -> katalog,
//   ref     — svjetski cjenik (Wine-Searcher) kao orijentir za cijenu.
import { DRINK_SHOPS, type DrinkShop, type DrinkShopScope } from "../data/drinkShops";
import type { Drink } from "../types";
import { drinkSearchHref, drinkSearchName, urlMatchesDrinkName } from "./drinkBuyLink";

export type DrinkShopLinkKind = "product" | "search" | "browse" | "ref";

export interface DrinkShopLink {
  shopId: string;
  shop: string;
  scope: DrinkShopScope;
  url: string;
  kind: DrinkShopLinkKind;
}

/** Vise od pet gumba je zid linkova — ostalo ionako vodi na iste kataloge. */
const MAX_HR_LINKS = 5;

function hostOf(url: string): string {
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return "";
  }
}

/** Trgovina kojoj pripada host product URL-a (www./webshop. prefiks se tolerira). */
function shopForHost(host: string): DrinkShop | undefined {
  if (!host) return undefined;
  return DRINK_SHOPS.find(
    (s) => s.productHost && (host === s.productHost || host.endsWith(`.${s.productHost}`)),
  );
}

/** `priceUrl` samo kad je stvarno stranica te boce, inace null. */
export function verifiedProductUrl(drink: Drink): string | null {
  const url = drink.priceUrl ?? null;
  if (!url) return null;
  return urlMatchesDrinkName(drink.name, url) ? url : null;
}

export function drinkShopLinks(drink: Drink): DrinkShopLink[] {
  const name = drinkSearchName(drink);
  const out: DrinkShopLink[] = [];

  const product = verifiedProductUrl(drink);
  const productShop = product ? shopForHost(hostOf(product)) : undefined;
  if (product) {
    out.push({
      shopId: productShop?.id ?? "shop",
      shop: productShop?.name ?? hostOf(product),
      scope: "HR",
      url: product,
      kind: "product",
    });
  }

  const hr = DRINK_SHOPS.filter(
    (s) =>
      s.scope === "HR" && s.categories.includes(drink.category) && s.id !== productShop?.id,
  );
  // Trgovine s pretragom prve: one traze bas tu bocu, katalog je samo polica.
  const ordered = [...hr.filter((s) => s.search), ...hr.filter((s) => !s.search)];
  for (const shop of ordered) {
    if (out.length >= MAX_HR_LINKS) break;
    const url = shop.search ? shop.search(name) : shop.browse?.[drink.category];
    if (!url) continue;
    out.push({
      shopId: shop.id,
      shop: shop.name,
      scope: "HR",
      url,
      kind: shop.search ? "search" : "browse",
    });
  }

  // Svjetski cjenik na kraju — koristan bas kad HR police nemaju bocu.
  for (const shop of DRINK_SHOPS) {
    if (shop.scope !== "REF" || !shop.categories.includes(drink.category)) continue;
    if (!shop.search) continue;
    out.push({
      shopId: shop.id,
      shop: shop.name,
      scope: "REF",
      url: shop.search(name),
      kind: "ref",
    });
  }

  return out;
}

/**
 * Jedan link za skucene prikaze (kartica prijedloga): potvrdena boca, pa
 * prva HR trgovina, pa Google (kategorije bez trgovina — npr. kava).
 */
export function drinkPrimaryLink(drink: Drink): { href: string; kind: DrinkShopLinkKind | "web" } {
  const links = drinkShopLinks(drink);
  const first = links[0];
  if (!first) return { href: drinkSearchHref(drink), kind: "web" };
  return { href: first.url, kind: first.kind };
}

/** "allez.hr (rijetko)" -> "allez.hr"; usporedba imena trgovina bez sitnica. */
const shopKey = (s: string) =>
  s
    .replace(/\s*\(.*\)$/, "")
    .trim()
    .toLowerCase();

/**
 * Dostupnost u HR iz `shopHR`. `verified` je true samo kad ta ista trgovina
 * ima potvrdenu stranicu boce — inace je tekst orijentir (police se mijenjaju,
 * a fuzzy match kataloga zna promasiti), pa ga UI tako i oznaci.
 */
export function drinkAvailabilityHR(
  drink: Drink,
): { text: string; verified: boolean } | null {
  const text = (drink.shopHR ?? "").trim();
  if (!text) return null;
  const product = drinkShopLinks(drink).find((l) => l.kind === "product");
  const verified = product != null && shopKey(text).includes(shopKey(product.shop));
  return { text, verified };
}
