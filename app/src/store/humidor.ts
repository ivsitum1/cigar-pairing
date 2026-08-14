// Humidori — više kutija, svaka sa svojim stanjem (broj cigara po vitoli).
//
// Odvojeno od `collection`: "Imam" je oznaka da poznaješ i posjeduješ liniju,
// humidor je stvarna zaliha koja se troši. Ključ stavke je isti kao u kolekciji
// (`lib/cigarItemId`), pa Churchill i Corona iste linije stoje kao dvije zalihe.
//
// Sve živi u localStorageu, po uređaju, kao i ostatak podataka aplikacije.
import { useSyncExternalStore } from "react";
import { canonicalCigarStateKey } from "../data";
import { VITOLA_ID_SEP, parseCigarItemId } from "../lib/cigarItemId";

export interface Humidor {
  id: string;
  name: string;
  /** ISO datum stvaranja — određuje redoslijed prikaza. */
  createdAt: string;
}

export interface HumidorStock {
  humidorId: string;
  /** Ključ iz `lib/cigarItemId` — linija ili linija@vitola. */
  itemId: string;
  count: number;
  /** ISO datum zadnje promjene — koristi ga kalendar. */
  updatedAt: string;
}

export interface HumidorData {
  humidors: Humidor[];
  stock: HumidorStock[];
  /** Humidor koji je odabran u sučelju. */
  activeId: string | null;
}

const KEY = "cigar-pairing-humidors-v1";

const EMPTY: HumidorData = { humidors: [], stock: [], activeId: null };

/**
 * Alias itemId -> kanonski; spoji brojeve ako se sudare. Isti ključ kao
 * kolekcija (`canonicalCigarStateKey`) — inače zaliha ostane na mrtvoj vitoli
 * dok kartica broji na drugom ključu.
 */
export function remapHumidorAliases(data: HumidorData): HumidorData {
  const merged = new Map<string, HumidorStock>();
  for (const s of data.stock) {
    const itemId = canonicalCigarStateKey(s.itemId);
    const key = `${s.humidorId}\0${itemId}`;
    const prev = merged.get(key);
    if (prev) {
      const newer = s.updatedAt > prev.updatedAt ? s.updatedAt : prev.updatedAt;
      merged.set(key, {
        humidorId: s.humidorId,
        itemId,
        count: prev.count + s.count,
        updatedAt: newer,
      });
    } else {
      merged.set(key, { ...s, itemId });
    }
  }
  return {
    ...data,
    stock: [...merged.values()].filter((s) => s.count > 0),
  };
}



const nowIso = () => new Date().toISOString();

const newId = (prefix: string) =>
  `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;

function normalizeHumidor(value: unknown): Humidor | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const v = value as Record<string, unknown>;
  if (typeof v.id !== "string" || !v.id) return null;
  const name = typeof v.name === "string" ? v.name.trim() : "";
  return {
    id: v.id,
    name: name || "Humidor",
    createdAt: typeof v.createdAt === "string" ? v.createdAt : nowIso(),
  };
}

function normalizeStock(value: unknown): HumidorStock | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const v = value as Record<string, unknown>;
  if (typeof v.humidorId !== "string" || typeof v.itemId !== "string") return null;
  if (!v.humidorId || !v.itemId) return null;
  const count =
    typeof v.count === "number" && Number.isFinite(v.count)
      ? Math.max(0, Math.floor(v.count))
      : 0;
  return {
    humidorId: v.humidorId,
    itemId: v.itemId,
    count,
    updatedAt: typeof v.updatedAt === "string" ? v.updatedAt : nowIso(),
  };
}

/** Validira spremljeni/uvezeni oblik; vraća null kad je neupotrebljiv. */
export function normalizeHumidorPayload(parsed: unknown): HumidorData | null {
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) return null;
  const root = parsed as Record<string, unknown>;

  const rawHumidors = root.humidors === undefined ? [] : root.humidors;
  if (!Array.isArray(rawHumidors)) return null;
  const rawStock = root.stock === undefined ? [] : root.stock;
  if (!Array.isArray(rawStock)) return null;

  const humidors: Humidor[] = [];
  const seen = new Set<string>();
  for (const raw of rawHumidors) {
    const h = normalizeHumidor(raw);
    if (h && !seen.has(h.id)) {
      seen.add(h.id);
      humidors.push(h);
    }
  }

  // zalihe bez svog humidora su smeće — ne vraćaj ih
  const stock: HumidorStock[] = [];
  const pairs = new Set<string>();
  for (const raw of rawStock) {
    const s = normalizeStock(raw);
    if (!s || !seen.has(s.humidorId)) continue;
    const key = `${s.humidorId}\0${s.itemId}`;
    if (pairs.has(key)) continue;
    pairs.add(key);
    if (s.count > 0) stock.push(s);
  }

  const activeRaw = root.activeId;
  const activeId =
    typeof activeRaw === "string" && seen.has(activeRaw)
      ? activeRaw
      : (humidors[0]?.id ?? null);

  return { humidors, stock, activeId };
}

let cache: HumidorData = load();
const listeners = new Set<() => void>();

function load(): HumidorData {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const normalized = normalizeHumidorPayload(JSON.parse(raw));
      if (normalized) return remapHumidorAliases(normalized);
    }
  } catch {
    // pokvaren zapis — kreni ispočetka
  }
  return EMPTY;
}

let storageFailed = false;

function persist(next: HumidorData) {
  cache = next;
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
    storageFailed = false;
  } catch {
    storageFailed = true;
  }
  listeners.forEach((l) => l());
}

export function useHumidorStorageHealth(): boolean {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => storageFailed,
  );
}

export function useHumidors(): HumidorData {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => cache,
  );
}

export const humidorData = (): HumidorData => cache;

/** Novi humidor postaje aktivan — upravo si ga i otvorio. */
export function addHumidor(name: string): Humidor {
  const humidor: Humidor = {
    id: newId("hum"),
    name: name.trim() || "Humidor",
    createdAt: nowIso(),
  };
  persist({
    ...cache,
    humidors: [...cache.humidors, humidor],
    activeId: humidor.id,
  });
  return humidor;
}

export function renameHumidor(id: string, name: string) {
  const trimmed = name.trim();
  if (!trimmed) return;
  persist({
    ...cache,
    humidors: cache.humidors.map((h) => (h.id === id ? { ...h, name: trimmed } : h)),
  });
}

/** Brisanje humidora briše i njegovu zalihu — inače bi ostala visjeti. */
export function removeHumidor(id: string) {
  const humidors = cache.humidors.filter((h) => h.id !== id);
  persist({
    humidors,
    stock: cache.stock.filter((s) => s.humidorId !== id),
    activeId: cache.activeId === id ? (humidors[0]?.id ?? null) : cache.activeId,
  });
}

export function setActiveHumidor(id: string | null) {
  if (id !== null && !cache.humidors.some((h) => h.id === id)) return;
  persist({ ...cache, activeId: id });
}

export function stockCount(humidorId: string, itemId: string): number {
  return (
    cache.stock.find((s) => s.humidorId === humidorId && s.itemId === itemId)?.count ?? 0
  );
}

/** Zaliha stavke u SVIM humidorima — za oznaku na kartici. */
export function totalStock(itemId: string): number {
  return cache.stock
    .filter((s) => s.itemId === itemId)
    .reduce((sum, s) => sum + s.count, 0);
}

/** Zaliha cijele linije (id + sve vitole id@…). */
export function lineTotalStock(cigarId: string): number {
  const prefix = cigarId + "@";
  return cache.stock
    .filter((s) => s.itemId === cigarId || s.itemId.startsWith(prefix))
    .reduce((sum, s) => sum + s.count, 0);
}

/**
 * Zaliha koju taj ključ pokriva: ključ s vitolom broji samo svoju veličinu,
 * goli ključ linije cijelu liniju (takva stavka ne zna za formate, pa je
 * „imam je” istinito dok god ijedna vitola stoji u kutiji).
 */
export function stockForItemKey(itemId: string): number {
  const { cigarId, vitolaSlug } = parseCigarItemId(itemId);
  return vitolaSlug ? totalStock(itemId) : lineTotalStock(cigarId);
}

/** Postavi točan broj; 0 miče zapis (praznu zalihu ne čuvamo). */
export function setStock(humidorId: string, itemId: string, count: number) {
  if (!cache.humidors.some((h) => h.id === humidorId)) return;
  const next = Math.max(0, Math.floor(count));
  const rest = cache.stock.filter(
    (s) => !(s.humidorId === humidorId && s.itemId === itemId),
  );
  persist({
    ...cache,
    stock:
      next > 0
        ? [...rest, { humidorId, itemId, count: next, updatedAt: nowIso() }]
        : rest,
  });
}

export function adjustStock(humidorId: string, itemId: string, delta: number) {
  setStock(humidorId, itemId, stockCount(humidorId, itemId) + delta);
}

/**
 * Prebaci zalihu s jednog ključa na drugi unutar istog humidora — tako stara
 * zaliha vođena po liniji („3 komada te linije”) dobiva vitolu, bez ponovnog
 * unosa. Odredište koje već postoji se zbraja.
 */
export function moveStock(
  humidorId: string,
  fromItemId: string,
  toItemId: string,
  count?: number,
) {
  if (fromItemId === toItemId) return;
  const available = stockCount(humidorId, fromItemId);
  if (available <= 0) return;
  const moved = Math.min(available, Math.max(1, Math.floor(count ?? available)));
  setStock(humidorId, fromItemId, available - moved);
  setStock(humidorId, toItemId, stockCount(humidorId, toItemId) + moved);
}

/** Zaliha cijele linije u jednom humidoru — ključ linije + sve njezine vitole. */
export function lineStock(humidorId: string, cigarId: string): HumidorStock[] {
  const prefix = cigarId + VITOLA_ID_SEP;
  return cache.stock.filter(
    (s) =>
      s.humidorId === humidorId &&
      (s.itemId === cigarId || s.itemId.startsWith(prefix)),
  );
}

export interface StockHit {
  humidorId: string;
  /** Ključ zalihe koji je stvarno pogođen — ne mora biti traženi ključ. */
  itemId: string;
}

/** Prvo aktivni humidor, pa bilo koji drugi — zaliha je zaliha. */
function pickStock(match: (s: HumidorStock) => boolean): HumidorStock | undefined {
  return (
    cache.stock.find((s) => s.count > 0 && s.humidorId === cache.activeId && match(s)) ??
    cache.stock.find((s) => s.count > 0 && match(s))
  );
}

/**
 * Zaliha za traženi ključ, uz toleranciju na vitolu.
 *
 * Humidor se puni po vitoli (`cig-x@churchill`), ali stare kutije znaju imati
 * zalihu na golom ključu linije (`cig-x`). Zato:
 *  1. točan ključ,
 *  2. goli ključ linije — zaliha bez formata pokriva svaku vitolu,
 *  3. zapis BEZ vitole skida jedini format te linije koji je na stanju.
 * Vitola se nikad ne mijenja drugom vitolom: popušeni Robusto ne smije skinuti
 * Toro s police, pa makar Toro bio jedino što je ostalo od te linije.
 */
function findStockHit(itemId: string): StockHit | null {
  const exact = pickStock((s) => s.itemId === itemId);
  if (exact) return { humidorId: exact.humidorId, itemId: exact.itemId };

  const { cigarId, vitolaSlug } = parseCigarItemId(itemId);
  if (vitolaSlug) {
    const line = pickStock((s) => s.itemId === cigarId);
    return line ? { humidorId: line.humidorId, itemId: line.itemId } : null;
  }

  const prefix = cigarId + VITOLA_ID_SEP;
  const sameLine = cache.stock.filter(
    (s) => s.count > 0 && (s.itemId === cigarId || s.itemId.startsWith(prefix)),
  );
  const keys = new Set(sameLine.map((s) => s.itemId));
  if (keys.size !== 1) return null;
  const only = pickStock((s) => s.itemId === sameLine[0].itemId)!;
  return { humidorId: only.humidorId, itemId: only.itemId };
}

/**
 * Skini jednu cigaru iz zalihe pri zapisu večeri. Traži humidor koji je stvarno
 * ima; bez pogotka ne mijenja ništa (cigara nije bila iz humidora).
 */
export function consumeFromStock(itemId: string): StockHit | null {
  const hit = findStockHit(itemId);
  if (!hit) return null;
  adjustStock(hit.humidorId, hit.itemId, -1);
  return hit;
}

export function exportHumidors(): HumidorData {
  // Kopija, ne ziva referenca: pozivatelj (backup u CollectionPage) inace drzi
  // interni state i moze ga slucajno mutirati mimo persist()a.
  return {
    humidors: cache.humidors.map((h) => ({ ...h })),
    stock: cache.stock.map((s) => ({ ...s })),
    activeId: cache.activeId,
  };
}

export function importHumidors(data: unknown): boolean {
  const normalized = normalizeHumidorPayload(data);
  if (!normalized) return false;
  persist(remapHumidorAliases(normalized));
  return true;
}
