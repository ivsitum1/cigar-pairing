// Prelazak iz Kataloga u Pairing s već odabranom cigaru ili pićem.
import { useSyncExternalStore } from "react";
import type { Cigar, Drink } from "../types";

export type PairingIntent =
  | { mode: "cigarToDrink"; cigar: Cigar }
  | { mode: "drinkToCigar"; drink: Drink };

const listeners = new Set<() => void>();
let pending: PairingIntent | null = null;
let version = 0;

export function requestPairing(intent: PairingIntent) {
  pending = intent;
  version += 1;
  listeners.forEach((l) => l());
}

export function consumePairingIntent(): PairingIntent | null {
  const intent = pending;
  pending = null;
  return intent;
}

export function usePairingNavVersion(): number {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => version,
  );
}
