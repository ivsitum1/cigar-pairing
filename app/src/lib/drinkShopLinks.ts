// "Gdje kupiti" za bocu: police po regiji (HR → EU → SAD → svjetski cjenik),
// a na kraju uvijek izlaz na web kad nijedna polica nije potvrđena.
//
// Pravilo je isto kao kod cigara — nikad ne tvrdi vise nego sto app zna:
//   product — `priceUrl` je potvrdena stranica bas te boce,
//   search  — trgovina ima pretragu po nazivu (link stvarno trazi tu bocu),
//   browse  — znamo trgovinu, ali ne i njen endpoint pretrage -> katalog,
//   ref     — svjetski cjenik (Wine-Searcher) kao orijentir za cijenu,
//   web     — Google pretraga: izlaz kad boce nema ni na jednoj poznatoj polici.
//
// Zasto je popis kratak: prije je kartica nudila do pet HR gumba, od cega je
// vecina bila katalog kategorije ("sva zestica") — klik bi otvorio policu na
// kojoj te boce nema. Sada po regiji ide potvrdena stranica, najvise dvije
// pretrage po nazivu i najvise jedan katalog.
import { DRINK_SHOPS, type DrinkShop, type DrinkShopScope } from "../data/drinkShops";
import type { Drink } from "../types";
import { drinkSearchHref, drinkSearchName, urlMatchesDrinkName } from "./drinkBuyLink";

export type DrinkShopLinkKind = "product" | "search" | "browse" | "ref" | "web";

export interface DrinkShopLink {
  shopId: string;
  shop: string;
  scope: DrinkShopScope | "WEB";
  url: string;
  kind: DrinkShopLinkKind;
}

/** Police po regiji, redom kako se prikazuju. */
export const DRINK_REGIONS = ["HR", "EU", "USA"] as const;
export type DrinkRegion = (typeof DRINK_REGIONS)[number];

/** Pretrage stvarno traze bocu; katalog je samo polica, pa ide jedan. */
const MAX_SEARCH_LINKS = 2;
const MAX_BROWSE_LINKS = 1;

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

/** Trgovine jedne regije za tu kategoriju pica. */
function shopsIn(scope: DrinkShopScope, drink: Drink): DrinkShop[] {
  return DRINK_SHOPS.filter(
    (s) => s.scope === scope && s.categories.includes(drink.category),
  );
}

function linksForRegion(
  region: DrinkRegion,
  drink: Drink,
  productShopId: string | undefined,
): DrinkShopLink[] {
  const name = drinkSearchName(drink);
  const shops = shopsIn(region, drink).filter((s) => s.id !== productShopId);
  const out: DrinkShopLink[] = [];

  for (const shop of shops.filter((s) => s.search)) {
    if (out.length >= MAX_SEARCH_LINKS) break;
    out.push({
      shopId: shop.id,
      shop: shop.name,
      scope: region,
      url: shop.search!(name),
      kind: "search",
    });
  }

  let browse = 0;
  for (const shop of shops.filter((s) => !s.search)) {
    if (browse >= MAX_BROWSE_LINKS) break;
    const url = shop.browse?.[drink.category];
    if (!url) continue;
    out.push({ shopId: shop.id, shop: shop.name, scope: region, url, kind: "browse" });
    browse += 1;
  }

  return out;
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
      // potvrdena stranica dolazi iz HR scrapea (allez/ecuga), osim ako host
      // kaze drugacije
      scope: productShop?.scope ?? "HR",
      url: product,
      kind: "product",
    });
  }

  for (const region of DRINK_REGIONS) {
    out.push(...linksForRegion(region, drink, productShop?.id));
  }

  // Svjetski cjenik pred kraj — koristan bas kad police nemaju bocu.
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

  // Bez potvrdene stranice boce nijedan gornji link nije jamstvo — zato izlaz
  // na web. S potvrdenom stranicom nema sto traziti.
  if (!product) {
    out.push({
      shopId: "web",
      shop: "Google",
      scope: "WEB",
      url: drinkSearchHref(drink),
      kind: "web",
    });
  }

  return out;
}

/**
 * Jedan link za skucene prikaze (kartica prijedloga): potvrdena boca, pa
 * prva trgovina, pa web pretraga.
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

/**
 * Koliko app zna o dostupnosti u toj regiji:
 *   confirmed — potvrdena stranica bas te boce u trgovini te regije,
 *   listed    — uredniska napomena o polici (`shopHR`), bez potvrde,
 *   unknown   — app nema podatak; ostaje pretraga u trgovinama i na webu.
 *
 * EU nasljeduje HR jer je Hrvatska u EU: sto stoji na hrvatskoj polici,
 * dostupno je i unutar EU. Za SAD podatka nema — nista se ne izmislja.
 */
export type DrinkAvailabilityStatus = "confirmed" | "viaHR" | "listed" | "unknown";

export function drinkRegionAvailability(
  drink: Drink,
): Record<DrinkRegion, DrinkAvailabilityStatus> {
  const product = verifiedProductUrl(drink);
  const productScope = product ? (shopForHost(hostOf(product))?.scope ?? "HR") : null;
  const listedHR = (drink.shopHR ?? "").trim().length > 0;

  const hr: DrinkAvailabilityStatus =
    productScope === "HR" ? "confirmed" : listedHR ? "listed" : "unknown";
  // potvrda na hrvatskoj polici je i EU polica, ali ne obrnuto — i to se kaže
  // baš tako ("potvrđeno u HR"), da EU pretraga ne izgleda kao potvrda
  const eu: DrinkAvailabilityStatus =
    productScope === "EU"
      ? "confirmed"
      : productScope === "HR"
        ? "viaHR"
        : hr === "listed"
          ? "listed"
          : "unknown";
  return {
    HR: hr,
    EU: eu,
    USA: productScope === "USA" ? "confirmed" : "unknown",
  };
}
