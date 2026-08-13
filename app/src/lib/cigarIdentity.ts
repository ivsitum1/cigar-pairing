import type { Cigar } from "../types";
import { parseCigarItemId, vitolaFromItemId } from "./cigarItemId";
import { applyVitola, needsVitolaPick, type CigarSheetOpen } from "./cigarVitola";

export type StockRow = {
  itemId: string;
  count: number;
  humidorId?: string;
  updatedAt?: string;
};

export function resolveSheetFromItemId(
  itemId: string,
  line: Cigar,
): CigarSheetOpen {
  const { vitolaSlug } = parseCigarItemId(itemId);
  if (vitolaSlug) {
    const vitola = vitolaFromItemId(line, itemId);
    if (vitola) return { mode: "detail", cigar: applyVitola(line, vitola) };
    return { mode: "line", cigar: line };
  }
  if (needsVitolaPick(line)) return { mode: "line", cigar: line };
  return { mode: "detail", cigar: line };
}

export function explainStock(itemId: string, rows: StockRow[]) {
  const { cigarId, vitolaSlug } = parseCigarItemId(itemId);
  const prefix = cigarId + "@";
  const exact = rows.find((r) => r.itemId === itemId)?.count ?? 0;
  const unassignedLine = vitolaSlug
    ? (rows.find((r) => r.itemId === cigarId)?.count ?? 0)
    : 0;
  const siblings = rows.filter(
    (r) =>
      r.itemId.startsWith(prefix) &&
      r.itemId !== itemId &&
      r.count > 0,
  );
  return { exact, unassignedLine, siblings };
}

function sameHumidor(row: StockRow, humidorId: string): boolean {
  return row.humidorId === undefined || row.humidorId === humidorId;
}

/**
 * Premjesti 1 komad s golog id-a linije na konkretnu vitolu u istom humidoru.
 * Ne dira druge kutije. Bez sluga ili bez bazena vraća iste redove.
 */
export function bindStockToVitola(
  rows: StockRow[],
  humidorId: string,
  itemId: string,
): StockRow[] {
  const { cigarId, vitolaSlug } = parseCigarItemId(itemId);
  if (!vitolaSlug) return rows;

  const lineRow = rows.find((r) => r.itemId === cigarId && sameHumidor(r, humidorId));
  if (!lineRow || lineRow.count <= 0) return rows;

  let foundVitola = false;
  const next = rows.map((r) => {
    if (r.itemId === cigarId && sameHumidor(r, humidorId)) {
      return { ...r, count: r.count - 1 };
    }
    if (r.itemId === itemId && sameHumidor(r, humidorId)) {
      foundVitola = true;
      return { ...r, count: r.count + 1 };
    }
    return r;
  });

  if (!foundVitola) {
    next.push({
      itemId,
      count: 1,
      humidorId,
      updatedAt: lineRow.updatedAt,
    });
  }

  return next.filter((r) => r.count > 0);
}
