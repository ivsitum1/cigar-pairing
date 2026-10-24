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
    favorite: typeof v.favorite === "boolean" ? v.favorite : false,
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
    typeof v.cigarId !== "string"
  ) {
    return null;
  }
  // solo: null / nedostaje / prazan string; krivi tip = odbaci cijeli zapis
  let drinkId: string | null;
  if (v.drinkId === null || v.drinkId === undefined || v.drinkId === "") {
    drinkId = null;
  } else if (typeof v.drinkId === "string") {
    drinkId = v.drinkId;
  } else {
    return null;
  }
  return {
    id: v.id,
    date: v.date,
    cigarId: v.cigarId,
    drinkId,
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

  // Politika A: ocjena 1–10 živi u dnevniku večeri, ne na stavci.
  // Stari items[].rating za cigare → solo journal zapis; pića ostaju na stavci
  // dok se ne zabilježi večer (journal zahtijeva cigarId).
  return migrateItemRatingsToJournal({ items, journal });
}

/**
 * Jednokratna migracija: cigara s items[].rating bez dnevničkog zapisa dobiva
 * solo večer (datum epoch da prava večer ostane „zadnja”).
 */
export function migrateItemRatingsToJournal(data: CollectionData): CollectionData {
  const journal = data.journal.slice();
  const items: Record<string, ItemState> = { ...data.items };
  let n = 0;
  for (const [id, state] of Object.entries(data.items)) {
    if (state.rating == null) continue;
    if (!id.startsWith("cig-")) continue;
    const hasJournal = journal.some((j) => j.cigarId === id && j.rating != null);
    if (!hasJournal) {
      journal.push({
        id: `j-migrated-${id}-${n++}`,
        date: "1970-01-01T00:00:00.000Z",
        cigarId: id,
        drinkId: null,
        rating: state.rating,
        note: "",
      });
    }
    const next = { ...state, rating: null };
    if (
      !next.owned &&
      !next.tried &&
      !next.wishlist &&
      !next.favorite &&
      !next.note
    ) {
      delete items[id];
    } else {
      items[id] = next;
    }
  }
  return { items, journal };
}
