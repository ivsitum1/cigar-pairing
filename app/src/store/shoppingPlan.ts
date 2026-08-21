// Ručni „Moj plan” na Kupovini — checklista razina S–C iz shopping.json.
//
// `owned` u JSON-u je samo početna sjeme: nakon prvog otvaranja kvačice žive
// u localStorageu i korisnik ih može stavljati i micati. Ne vežu se na
// oznaku „Imam” na boci (to rade praznine u kolekciji).

import { useSyncExternalStore } from "react";
import shoppingJson from "../data/shopping.json";

const KEY = "cigar-pairing-shopping-plan-v1";

type TierRow = {
  tier: string;
  owned: boolean;
  bottleTarget: string;
};

/** Stabilan ključ retka plana — tier + ciljna boca (jedinstveni u seedu). */
export const planRowKey = (tier: string, bottleTarget: string): string =>
  `${tier}::${bottleTarget}`;

function seedOwned(): Set<string> {
  const tiers = (shoppingJson as { tiers?: TierRow[] }).tiers ?? [];
  return new Set(
    tiers.filter((r) => r.owned).map((r) => planRowKey(r.tier, r.bottleTarget)),
  );
}

function load(): Set<string> {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw == null) return seedOwned();
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return seedOwned();
    return new Set(parsed.filter((x): x is string => typeof x === "string" && x.includes("::")));
  } catch {
    return seedOwned();
  }
}

let cache = load();
const listeners = new Set<() => void>();

function persist(next: Set<string>) {
  cache = next;
  try {
    localStorage.setItem(KEY, JSON.stringify([...next].sort()));
  } catch {
    // pun ili blokiran storage — oznaka vrijedi do zatvaranja
  }
  listeners.forEach((l) => l());
}

const subscribe = (cb: () => void) => {
  listeners.add(cb);
  return () => listeners.delete(cb);
};

/** Snapshot za re-render — referenca se mijenja samo na persist. */
export function useShoppingPlanOwned(): Set<string> {
  return useSyncExternalStore(subscribe, () => cache);
}

export const isPlanRowOwned = (tier: string, bottleTarget: string): boolean =>
  cache.has(planRowKey(tier, bottleTarget));

export function togglePlanRow(tier: string, bottleTarget: string): boolean {
  const key = planRowKey(tier, bottleTarget);
  const next = new Set(cache);
  const nowOwned = !next.has(key);
  if (nowOwned) next.add(key);
  else next.delete(key);
  persist(next);
  return nowOwned;
}

/** Backup: ide uz kolekciju u Export/Import. */
export function exportShoppingPlan(): string[] {
  return [...cache].sort();
}

export function importShoppingPlan(value: unknown): boolean {
  if (!Array.isArray(value)) return false;
  const valid = value.filter(
    (x): x is string => typeof x === "string" && /^[^:]+::.+/.test(x),
  );
  if (value.length > 0 && valid.length === 0) return false;
  persist(new Set(valid));
  return true;
}
