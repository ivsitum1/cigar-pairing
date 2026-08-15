// Tvoja ocjena snage i tijela — jedini izvor koji je stvarno pušio cigaru.
//
// Katalog snagu i tijelo vecinom procjenjuje: iz opisa trgovine, iz karaktera
// pokrova, ili — za oko 2200 linija — ni iz cega osim heuristike. Provjereno je
// i moze li ih zamijeniti CigarWorldova ocjena zajednice; ne moze (vidi
// scripts/audit-cigarworld-axes.py: predvida gotovo uvijek "3"). Ostaje jedan
// izvor koji ne procjenjuje nego zna — onaj tko je cigaru popusio.
//
// Zapis je po LINIJI, ne po vitoli: katalog snagu i tijelo drzi na liniji, a
// razliku medu formatima pairing i dalje racuna sam (engine/vitolaGeometry).
import { useSyncExternalStore } from "react";
import { resolveCigarIdAlias } from "../data";

export interface TasteProfile {
  /** 1–5, kako ti je sjela */
  strength: number;
  /** 1–5, koliko je dim bio gust */
  body: number;
  /** ISO datum zadnje izmjene */
  at: string;
}

export type TasteProfiles = Record<string, TasteProfile>;

const KEY = "cigar-pairing-taste-v1";

const clamp = (n: number) => Math.max(1, Math.min(5, Math.round(n)));

/** Ne vjeruj localStorageu na rijec — tudi ili stari zapis ne smije srusiti app. */
export function normalizeTasteProfiles(raw: unknown): TasteProfiles {
  if (!raw || typeof raw !== "object") return {};
  const out: TasteProfiles = {};
  for (const [id, value] of Object.entries(raw as Record<string, unknown>)) {
    if (!value || typeof value !== "object") continue;
    const v = value as Partial<TasteProfile>;
    if (typeof v.strength !== "number" || typeof v.body !== "number") continue;
    if (!Number.isFinite(v.strength) || !Number.isFinite(v.body)) continue;
    out[resolveCigarIdAlias(id)] = {
      strength: clamp(v.strength),
      body: clamp(v.body),
      at: typeof v.at === "string" ? v.at : new Date().toISOString(),
    };
  }
  return out;
}

function read(): TasteProfiles {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? normalizeTasteProfiles(JSON.parse(raw)) : {};
  } catch {
    return {};
  }
}

let cache: TasteProfiles = read();
const listeners = new Set<() => void>();

function emit() {
  for (const fn of listeners) fn();
}

function write(next: TasteProfiles) {
  cache = next;
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    // pun spremnik ne smije pojesti ocjenu iz trenutne sesije
  }
  emit();
}

export function useTasteProfiles(): TasteProfiles {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    () => cache,
    () => cache,
  );
}

/** Ocjena za liniju te cigare, ili null. Prima i kljuc s vitolom. */
export function getTasteProfile(cigarId: string): TasteProfile | null {
  const lineId = resolveCigarIdAlias(cigarId.split("@")[0]);
  return cache[lineId] ?? null;
}

export function setTasteProfile(cigarId: string, strength: number, body: number) {
  const lineId = resolveCigarIdAlias(cigarId.split("@")[0]);
  write({
    ...cache,
    [lineId]: { strength: clamp(strength), body: clamp(body), at: new Date().toISOString() },
  });
}

export function clearTasteProfile(cigarId: string) {
  const lineId = resolveCigarIdAlias(cigarId.split("@")[0]);
  if (!(lineId in cache)) return;
  const next = { ...cache };
  delete next[lineId];
  write(next);
}

/** Za backup/restore uz ostatak kolekcije. */
export function exportTasteProfiles(): TasteProfiles {
  return { ...cache };
}

export function importTasteProfiles(raw: unknown) {
  write({ ...cache, ...normalizeTasteProfiles(raw) });
}
