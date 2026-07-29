// Kolekcija i dnevnik — localStorage, s export/import backupom.
import { useSyncExternalStore } from "react";
import { normalizeCollectionPayload } from "../lib/safeStorage";

export interface ItemState {
  owned: boolean;
  tried: boolean;
  wishlist: boolean; // lista zelja — zelim kupiti
  rating: number | null; // 1-10
  note: string;
}

export interface JournalEntry {
  id: string;
  date: string; // ISO
  cigarId: string;
  drinkId: string;
  rating: number | null;
  note: string;
}

export interface CollectionData {
  items: Record<string, ItemState>;
  journal: JournalEntry[];
}

const KEY = "cigar-pairing-collection-v1";

let cache: CollectionData = load();
const listeners = new Set<() => void>();

function load(): CollectionData {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const normalized = normalizeCollectionPayload(JSON.parse(raw));
      if (normalized) return normalized;
    }
  } catch {
    // pokvaren zapis — kreni ispocetka
  }
  return { items: {}, journal: [] };
}

// zapis moze puknuti (pun storage, Safari private mode) — promjene tada zive
// samo u memoriji, a UI preko useStorageHealth pokazuje upozorenje
let storageFailed = false;

function persist(next: CollectionData) {
  cache = next;
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
    storageFailed = false;
  } catch {
    storageFailed = true;
  }
  listeners.forEach((l) => l());
}

export function useStorageHealth(): boolean {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => storageFailed,
  );
}

export function useCollection(): CollectionData {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => cache,
  );
}

// stariji zapisi u localStorage nemaju wishlist polje — defaulti po polju
export const getItemState = (id: string): ItemState => {
  const s = cache.items[id] as Partial<ItemState> | undefined;
  return {
    owned: s?.owned ?? false,
    tried: s?.tried ?? false,
    wishlist: s?.wishlist ?? false,
    rating: s?.rating ?? null,
    note: s?.note ?? "",
  };
};

/**
 * Zbirno stanje cijele LINIJE cigare. Stanje se čuva po vitoli
 * (`cig-x@churchill`), pa filteri na razini linije ("samo moje", Kupovina)
 * moraju gledati sve njezine vitole: posjedujem liniju ako posjedujem bilo koji
 * njezin format. Ocjena je najviša zabilježena.
 */
export function lineState(cigarId: string): ItemState {
  const prefix = `${cigarId}@`;
  const out: ItemState = {
    owned: false,
    tried: false,
    wishlist: false,
    rating: null,
    note: "",
  };
  for (const [key, s] of Object.entries(cache.items)) {
    if (key !== cigarId && !key.startsWith(prefix)) continue;
    out.owned ||= s.owned ?? false;
    out.tried ||= s.tried ?? false;
    out.wishlist ||= s.wishlist ?? false;
    if (s.rating != null && (out.rating == null || s.rating > out.rating)) {
      out.rating = s.rating;
    }
    if (!out.note && s.note) out.note = s.note;
  }
  return out;
}

export function updateItem(id: string, patch: Partial<ItemState>) {
  const current = getItemState(id);
  const next = { ...current, ...patch, note: (patch.note ?? current.note).trim() };
  const items = { ...cache.items };
  if (!next.owned && !next.tried && !next.wishlist && next.rating == null && !next.note) {
    delete items[id]; // ne cuvamo prazna stanja
  } else {
    items[id] = next;
  }
  persist({ ...cache, items });
}

export function addJournalEntry(entry: Omit<JournalEntry, "id" | "date">) {
  const full: JournalEntry = {
    ...entry,
    id: `j-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    date: new Date().toISOString(),
  };
  persist({ ...cache, journal: [full, ...cache.journal] });
}

export function removeJournalEntry(id: string) {
  persist({ ...cache, journal: cache.journal.filter((j) => j.id !== id) });
}

export function exportData(): string {
  return JSON.stringify(cache, null, 2);
}

export function importData(json: string): boolean {
  try {
    const normalized = normalizeCollectionPayload(JSON.parse(json));
    if (!normalized) return false;
    persist(normalized);
    return true;
  } catch {
    return false;
  }
}
