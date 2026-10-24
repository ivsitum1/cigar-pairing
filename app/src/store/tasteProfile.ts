// Tvoja ocjena snage, tijela i intenziteta note — jedini izvor koji je stvarno
// pušio cigaru.
//
// Katalog te tri osi većinom procjenjuje: iz opisa trgovine, iz karaktera
// pokrova, ili — za oko 2200 linija — ni iz čega osim heuristike. Provjereno je
// i može li ih zamijeniti CigarWorldova ocjena zajednice za snagu/tijelo; ne
// može (vidi scripts/audit-cigarworld-axes.py). Za intenzitet note CigarWorldov
// `aroma strength` jest mjerenje (~565 linija); ostatak je izvod po zapisu.
// Ostaje jedan izvor koji ne procjenjuje nego zna — onaj tko je cigaru popušio.
//
// Zapis je po LINIJI, ne po vitoli: katalog osi drži na liniji, a razliku među
// formatima pairing i dalje računa sam (engine/vitolaGeometry).
import { useSyncExternalStore } from "react";
import { resolveCigarIdAlias } from "../data";

export interface TasteProfile {
  /** 1–5, kako ti je sjela */
  strength: number;
  /** 1–5, koliko je dim bio gust */
  body: number;
  /**
   * 1–5, koliko je okus bio glasan. Stari localStorage (samo snaga+tijelo) nema
   * polje — tada se katalogov intenzitet ne dira.
   */
  flavorIntensity?: number;
  /** ISO datum zadnje izmjene */
  at: string;
}

export type TasteProfiles = Record<string, TasteProfile>;

const KEY = "cigar-pairing-taste-v1";

const clamp = (n: number) => Math.max(1, Math.min(5, Math.round(n)));

/** Ne vjeruj localStorageu na riječ — tuđi ili stari zapis ne smije srušiti app. */
export function normalizeTasteProfiles(raw: unknown): TasteProfiles {
  if (!raw || typeof raw !== "object") return {};
  const out: TasteProfiles = {};
  for (const [id, value] of Object.entries(raw as Record<string, unknown>)) {
    if (!value || typeof value !== "object") continue;
    const v = value as Partial<TasteProfile>;
    if (typeof v.strength !== "number" || typeof v.body !== "number") continue;
    if (!Number.isFinite(v.strength) || !Number.isFinite(v.body)) continue;
    const entry: TasteProfile = {
      strength: clamp(v.strength),
      body: clamp(v.body),
      at: typeof v.at === "string" ? v.at : new Date().toISOString(),
    };
    if (typeof v.flavorIntensity === "number" && Number.isFinite(v.flavorIntensity)) {
      entry.flavorIntensity = clamp(v.flavorIntensity);
    }
    out[resolveCigarIdAlias(id)] = entry;
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

/** Ocjena za liniju te cigare, ili null. Prima i ključ s vitolom. */
export function getTasteProfile(cigarId: string): TasteProfile | null {
  const lineId = resolveCigarIdAlias(cigarId.split("@")[0]);
  return cache[lineId] ?? null;
}

export function setTasteProfile(
  cigarId: string,
  strength: number,
  body: number,
  flavorIntensity?: number,
) {
  const lineId = resolveCigarIdAlias(cigarId.split("@")[0]);
  const entry: TasteProfile = {
    strength: clamp(strength),
    body: clamp(body),
    at: new Date().toISOString(),
  };
  if (flavorIntensity != null && Number.isFinite(flavorIntensity)) {
    entry.flavorIntensity = clamp(flavorIntensity);
  }
  write({
    ...cache,
    [lineId]: entry,
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
