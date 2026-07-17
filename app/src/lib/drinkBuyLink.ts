// Pouzdan "Gdje kupiti" link za pice: odbaci kategorije i ocito krive proizvode.
import type { Drink } from "../types";

const STOP = new Set([
  "vol",
  "years",
  "year",
  "old",
  "yo",
  "single",
  "malt",
  "scotch",
  "whisky",
  "whiskey",
  "rum",
  "rhum",
  "cognac",
  "armagnac",
  "calvados",
  "brandy",
  "gin",
  "port",
  "porto",
  "sherry",
  "wine",
  "the",
  "and",
  "gift",
  "box",
  "poklon",
  "kutiji",
  "kutija",
  "dry",
  "extra",
  "reserve",
  "grande",
  "champagne",
  "islay",
  "limited",
  "edition",
  "batch",
  "no",
  "in",
  "gb",
  "l",
  "cl",
]);

/** Tokeni imena / slug-a (uklj. brojeve godina). */
export function drinkLinkTokens(s: string): Set<string> {
  return new Set(
    s
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .split(/\s+/)
      .filter((t) => t.length > 0)
      .filter((t) => /^\d+$/.test(t) || t.length >= 2)
      .filter((t) => !STOP.has(t)),
  );
}

function slugFromUrl(url: string): string {
  try {
    const path = new URL(url).pathname;
    const parts = path.split("/").filter(Boolean);
    return parts[parts.length - 1] ?? "";
  } catch {
    return "";
  }
}

/** Je li URL stranica proizvoda, a ne katalog/kategorija/pretraga. */
export function isDrinkProductUrl(url: string): boolean {
  let u: URL;
  try {
    u = new URL(url);
  } catch {
    return false;
  }
  const path = u.pathname.toLowerCase();
  if (path.includes("/svi-proizvodi/") || path.includes("/proizvod/")) return true;
  // Vivat / Roto / Vrutak: proizvodni pathovi obicno imaju slug dulji od kategorije
  if (/\/vrsta\//.test(path) || /\/katalog\//.test(path)) return false;
  if (/\/search/.test(path) || /\/shop\/(?:rum|whiskey|whisky|gin|cognac)\/?$/.test(path)) {
    return false;
  }
  if (/\/webshop\/?$/.test(path)) return false;
  // genericki shop rootovi
  if ((path === "/" || path === "") && !u.search) return false;
  // ostali hostovi: zahtijevaj barem jedan path segment koji nije prazan
  const segs = path.split("/").filter(Boolean);
  return segs.length >= 1 && segs[segs.length - 1]!.length >= 4;
}

/**
 * Da li slug URL-a dovoljno odgovara imenu boce.
 * Namjerno konzervativno: bolje "Traži online" nego krivi proizvod.
 */
export function urlMatchesDrinkName(name: string, url: string): boolean {
  if (!isDrinkProductUrl(url)) return false;
  const nameToks = drinkLinkTokens(name);
  const urlToks = drinkLinkTokens(slugFromUrl(url));
  if (nameToks.size === 0 || urlToks.size === 0) return false;

  const shared = [...nameToks].filter((t) => urlToks.has(t));
  if (shared.length < 2) return false;

  // godine / batch brojevi iz imena moraju biti u URL-u
  const nameNums = [...nameToks].filter((t) => /^\d{1,4}$/.test(t));
  if (nameNums.length > 0 && !nameNums.every((n) => urlToks.has(n))) return false;

  // barem polovica "srednjih" tokena (>=4) mora biti u slug-u
  const mid = [...nameToks].filter((t) => t.length >= 4 && !/^\d+$/.test(t));
  if (mid.length >= 2) {
    const hit = mid.filter((t) => urlToks.has(t)).length;
    if (hit * 2 < mid.length) return false;
  }

  // dugi potpis (>=6): svi moraju biti u slug-u (inače ista marka, krivi SKU)
  const long = [...nameToks].filter((t) => t.length >= 6 && !/^\d+$/.test(t));
  if (long.length >= 1 && !long.every((t) => urlToks.has(t))) return false;

  return true;
}

export type DrinkBuyLink = { href: string; label: "buy" | "search" };

export function drinkSearchHref(drink: Drink): string {
  const shop = (drink.shopHR ?? "").trim();
  const hint = shop && shop.toLowerCase() !== "razno" ? ` ${shop}` : "";
  const q = `"${drink.name}" cijena kupnja${hint}`;
  return `https://www.google.com/search?q=${encodeURIComponent(q)}`;
}

export function drinkBuyLink(drink: Drink): DrinkBuyLink {
  const url = drink.priceUrl ?? null;
  if (!url) return { href: drinkSearchHref(drink), label: "search" };

  const shop = (drink.shopHR ?? "").toLowerCase();
  const isEcuga = url.includes("ecuga.com");
  const isAllez = url.includes("allez.hr");
  const shopMatchesDomain =
    (isEcuga && shop.includes("ecuga")) || (isAllez && shop.includes("allez"));

  // Ako link nije na isti izvor koji se navodi kao HR shop, to je praktično pretraga.
  if ((isEcuga || isAllez) && shop && !shopMatchesDomain) {
    return { href: drinkSearchHref(drink), label: "search" };
  }

  if (!urlMatchesDrinkName(drink.name, url)) {
    return { href: drinkSearchHref(drink), label: "search" };
  }

  return { href: url, label: "buy" };
}
