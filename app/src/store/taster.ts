// Tko ocjenjuje. Jedno ime, lokalno, bez računa i bez prijave.
//
// Dojmove skuplja više ljudi (vlasnik i kolega), pa svaki izvještaj mora nositi
// potpis — inače se u repou ne zna čija je koja ocjena, a prosjek dvoje ljudi
// koji se ne razlikuju nije prosjek nego zbrka.
import { useSyncExternalStore } from "react";

const KEY = "cigar-pairing-taster-v1";

/** Ime bez razmaka na rubovima i bez pretjerivanja u duljini. */
export function normalizeTasterName(raw: unknown): string {
  if (typeof raw !== "string") return "";
  return raw.trim().replace(/\s+/g, " ").slice(0, 40);
}

function read(): string {
  try {
    return normalizeTasterName(localStorage.getItem(KEY));
  } catch {
    return "";
  }
}

let cache = read();
const listeners = new Set<() => void>();

export function useTaster(): string {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    () => cache,
    () => cache,
  );
}

export function setTaster(name: string) {
  cache = normalizeTasterName(name);
  try {
    localStorage.setItem(KEY, cache);
  } catch {
    // ime nije vrijedno rušenja spremanja
  }
  for (const fn of listeners) fn();
}
