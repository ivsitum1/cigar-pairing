import type { Lang } from "../types";
import type { CollectionData, ItemState, JournalEntry } from "../store/collection";

/** Cita localStorage JSON niz; na gresku ili krivi oblik vraca []. */
export function readJsonStringArray(key: string): string[] {
  try {
    const raw = localStorage.getItem(key);
    if (raw == null) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((x): x is string => typeof x === "string");
  } catch {
    return [];
  }
}

/** Dozvoljava samo hr|en; sve ostalo pada na hr. */
export function resolveLang(raw: string | null): Lang {
  if (raw === "hr" || raw === "en") return raw;
  return "hr";
}

function normalizeRating(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  if (value < 1 || value > 10) return null;
  return value;
}

function normalizeItem(value: unknown): ItemState | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const v = value as Record<string, unknown>;
  return {
    owned: typeof v.owned === "boolean" ? v.owned : false,
    tried: typeof v.tried === "boolean" ? v.tried : false,
    wishlist: typeof v.wishlist === "boolean" ? v.wishlist : false,
    rating: normalizeRating(v.rating),
    note: typeof v.note === "string" ? v.note.trim() : "",
  };
}

function normalizeJournalEntry(value: unknown): JournalEntry | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const v = value as Record<string, unknown>;
  if (
    typeof v.id !== "string" ||
    typeof v.date !== "string" ||
    typeof v.cigarId !== "string" ||
    typeof v.drinkId !== "string"
  ) {
    return null;
  }
  return {
    id: v.id,
    date: v.date,
    cigarId: v.cigarId,
    drinkId: v.drinkId,
    rating: normalizeRating(v.rating),
    note: typeof v.note === "string" ? v.note : "",
  };
}

/**
 * Validira/normalizira payload kolekcije (load ili import).
 * Vraca null kad je oblik neupotrebljiv (npr. items nije zapis).
 */
export function normalizeCollectionPayload(parsed: unknown): CollectionData | null {
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) return null;
  const root = parsed as Record<string, unknown>;

  const rawItems = root.items === undefined ? {} : root.items;
  if (typeof rawItems !== "object" || rawItems === null || Array.isArray(rawItems)) {
    return null;
  }

  const rawJournal = root.journal === undefined ? [] : root.journal;
  if (!Array.isArray(rawJournal)) return null;

  const items: Record<string, ItemState> = {};
  for (const [id, value] of Object.entries(rawItems)) {
    const item = normalizeItem(value);
    if (item) items[id] = item;
  }

  const journal: JournalEntry[] = [];
  for (const entry of rawJournal) {
    const j = normalizeJournalEntry(entry);
    if (j) journal.push(j);
  }

  return { items, journal };
}
