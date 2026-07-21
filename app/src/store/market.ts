// Odabrani filter regije za cigare (ALL/HR/EU/USA) — dijeljeno reaktivno stanje.
// Svi prikazi cijena/linkova cigara prate ovo, da cijena i trgovina odgovaraju
// odabranoj regiji. Zadano "ALL" = bez filtera (prikaži sve).
import { useSyncExternalStore } from "react";
import type { RegionFilter } from "../types";

const KEY = "market";
const listeners = new Set<() => void>();

let current: RegionFilter = ((): RegionFilter => {
  const v = localStorage.getItem(KEY);
  if (v === "HR" || v === "EU" || v === "USA" || v === "ALL") return v;
  // stara vrijednost "WW" (Svijet) = bez filtera
  return "ALL";
})();

export function setMarket(m: RegionFilter) {
  current = m;
  localStorage.setItem(KEY, m);
  listeners.forEach((l) => l());
}

export function useMarket(): RegionFilter {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => current,
  );
}
