// Odabrani filter regije za cigare (ALL/HR/EU/USA) — dijeljeno reaktivno stanje.
// Svi prikazi cijena/linkova cigara prate ovo, da cijena i trgovina odgovaraju
// odabranoj regiji. Zadano "HR" — inače sparivanje piće→cigara nudi linije
// koje u Hrvatskoj nisu u prodaji. "ALL" ostaje izričit odabir (gumb Sve).
import { useSyncExternalStore } from "react";
import type { RegionFilter } from "../types";

const KEY = "market";
const listeners = new Set<() => void>();

export function parseMarket(v: string | null): RegionFilter {
  if (v === "HR" || v === "EU" || v === "USA" || v === "ALL") return v;
  // stara vrijednost "WW" (Svijet) i sve nepoznato → HR
  return "HR";
}

let current: RegionFilter = parseMarket(localStorage.getItem(KEY));

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
