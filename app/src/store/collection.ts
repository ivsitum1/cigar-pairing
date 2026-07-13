// Kolekcija i dnevnik — localStorage, s export/import backupom.
import { useSyncExternalStore } from "react";

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
      const parsed = JSON.parse(raw);
      return { items: parsed.items ?? {}, journal: parsed.journal ?? [] };
    }
  } catch {
    // pokvaren zapis — kreni ispocetka
  }
  return { items: {}, journal: [] };
}

function persist(next: CollectionData) {
  cache = next;
  localStorage.setItem(KEY, JSON.stringify(next));
  listeners.forEach((l) => l());
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
    const parsed = JSON.parse(json);
    if (typeof parsed !== "object" || parsed === null) return false;
    persist({ items: parsed.items ?? {}, journal: parsed.journal ?? [] });
    return true;
  } catch {
    return false;
  }
}
