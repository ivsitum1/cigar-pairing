// Odabrano tržište cigara (HR/EU/USA/WW) — dijeljeno reaktivno stanje.
// Svi prikazi cijena/linkova cigara prate ovo, da cijena i trgovina odgovaraju.
import { useSyncExternalStore } from "react";
import type { Market } from "../types";

const KEY = "market";
const listeners = new Set<() => void>();

let current: Market = ((): Market => {
  const v = localStorage.getItem(KEY);
  return v === "HR" || v === "EU" || v === "USA" || v === "WW" ? v : "HR";
})();

export function setMarket(m: Market) {
  current = m;
  localStorage.setItem(KEY, m);
  listeners.forEach((l) => l());
}

export function useMarket(): Market {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => current,
  );
}
