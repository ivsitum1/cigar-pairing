// Hash-based routing: #/<stranica>[/cigar|drink/<id>] or #/club/<view>.
// Daje deep-linkove (podijeli cigaru/pice) i ispravnu back tipku na mobitelu;
// hash radi i na GitHub Pages bez server-side ruta.
import { useSyncExternalStore } from "react";

export type Page = "pairing" | "catalog" | "collection" | "shopping" | "club";
export type ClubView = "101" | "bonton" | "lexicon" | "hr-guide" | "archetypes";

export interface Route {
  page: Page;
  pair?: { kind: "cigar" | "drink"; id: string };
  club?: ClubView;
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
  return { page };
}

export function routeToHash(r: Route): string {
  if (r.page === "club" && r.club) {
    return `#/${r.page}/${r.club}`;
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
