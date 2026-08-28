// Odabrani filter regije za cigare (ALL/HR/EU/USA) — dijeljeno reaktivno stanje.
// Svi prikazi cijena/linkova cigara prate ovo, da cijena i trgovina odgovaraju
// odabranoj regiji. Zadano "HR" — inače sparivanje piće→cigara nudi linije
// koje u Hrvatskoj nisu u prodaji. "ALL" ostaje izričit odabir (gumb Sve).
import { useSyncExternalStore } from "react";
import type { RegionFilter } from "../types";

const KEY = "market";
const listeners = new Set<() => void>();
let storageFailed = false;

export function parseMarket(v: string | null): RegionFilter {
  if (v === "HR" || v === "EU" || v === "USA" || v === "ALL") return v;
  // stara vrijednost "WW" (Svijet) i sve nepoznato → HR
  return "HR";
}

function readStored(): RegionFilter {
  try {
    return parseMarket(localStorage.getItem(KEY));
  } catch {
    // storage blokiran (Safari private, stroga pravila) — zadano HR
    return "HR";
  }
}

let current: RegionFilter = readStored();

export function setMarket(m: RegionFilter) {
  current = m;
  try {
    localStorage.setItem(KEY, m);
    storageFailed = false;
  } catch {
    // pun ili blokiran storage — in-memory odabir i dalje vrijedi
    storageFailed = true;
  }
  listeners.forEach((l) => l());
}

const subscribe = (cb: () => void) => {
  listeners.add(cb);
  return () => listeners.delete(cb);
};

export function getMarket(): RegionFilter {
  return current;
}

export function useMarket(): RegionFilter {
  return useSyncExternalStore(subscribe, () => current);
}

export function useMarketStorageHealth(): boolean {
  return useSyncExternalStore(subscribe, () => storageFailed);
}
