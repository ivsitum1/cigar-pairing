// Hash-based routing: #/<stranica>[/…] — deep-linkovi + back tipka; radi na GH Pages.
import { useSyncExternalStore } from "react";

export type Page = "pairing" | "catalog" | "collection" | "shopping" | "club";
export type ClubView = "101" | "bonton" | "lexicon" | "hr-guide" | "archetypes";

/** Catalog deep links: brand → line → vitola (Phase 4). */
export type CatalogFocus =
  | { level: "brand"; brandSlug: string }
  | { level: "line"; cigarId: string }
  | { level: "vitola"; cigarId: string; vitolaSlug: string };

export interface Route {
  page: Page;
  pair?: { kind: "cigar" | "drink"; id: string };
  club?: ClubView;
  catalog?: CatalogFocus;
}

const PAGES: readonly string[] = ["pairing", "catalog", "collection", "shopping", "club"];
const CLUB_VIEWS: readonly string[] = ["101", "bonton", "lexicon", "hr-guide", "archetypes"];

export function parseHash(hash: string): Route {
  const parts = hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  const page: Page = PAGES.includes(parts[0]) ? (parts[0] as Page) : "pairing";
  if (page === "pairing" && (parts[1] === "cigar" || parts[1] === "drink") && parts[2]) {
    return { page, pair: { kind: parts[1], id: decodeURIComponent(parts[2]) } };
  }
  if (page === "club" && CLUB_VIEWS.includes(parts[1])) {
    return { page, club: parts[1] as ClubView };
  }
  if (page === "catalog" && parts[1] === "brand" && parts[2]) {
    return {
      page,
      catalog: { level: "brand", brandSlug: decodeURIComponent(parts[2]) },
    };
  }
  if (page === "catalog" && parts[1] === "line" && parts[2]) {
    return {
      page,
      catalog: { level: "line", cigarId: decodeURIComponent(parts[2]) },
    };
  }
  if (page === "catalog" && parts[1] === "vitola" && parts[2] && parts[3]) {
    return {
      page,
      catalog: {
        level: "vitola",
        cigarId: decodeURIComponent(parts[2]),
        vitolaSlug: decodeURIComponent(parts[3]),
      },
    };
  }
  return { page };
}

export function routeToHash(r: Route): string {
  if (r.page === "club" && r.club) {
    return `#/${r.page}/${r.club}`;
  }
  if (r.page === "catalog" && r.catalog) {
    const c = r.catalog;
    switch (c.level) {
      case "brand":
        return `#/catalog/brand/${encodeURIComponent(c.brandSlug)}`;
      case "line":
        return `#/catalog/line/${encodeURIComponent(c.cigarId)}`;
      case "vitola":
        return `#/catalog/vitola/${encodeURIComponent(c.cigarId)}/${encodeURIComponent(c.vitolaSlug)}`;
      default: {
        const _exhaustive: never = c;
        return _exhaustive;
      }
    }
  }
  return r.pair
    ? `#/${r.page}/${r.pair.kind}/${encodeURIComponent(r.pair.id)}`
    : `#/${r.page}`;
}

const hasWindow = typeof window !== "undefined";

let current: Route = hasWindow ? parseHash(window.location.hash) : { page: "pairing" };
const listeners = new Set<() => void>();

if (hasWindow) {
  window.addEventListener("hashchange", () => {
    current = parseHash(window.location.hash);
    listeners.forEach((l) => l());
  });
}

export function navigate(route: Route, opts?: { replace?: boolean }) {
  if (!hasWindow) return;
  const hash = routeToHash(route);
  if (hash === window.location.hash) return;
  if (opts?.replace) {
    // bez novog history zapisa (npr. promjena moda) — rucno obavijesti
    window.history.replaceState(null, "", hash);
    current = parseHash(hash);
    listeners.forEach((l) => l());
  } else {
    window.location.hash = hash; // okida hashchange
  }
}

export function useRoute(): Route {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => current,
  );
}
