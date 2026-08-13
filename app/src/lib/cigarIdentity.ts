import type { Cigar } from "../types";
import { parseCigarItemId, vitolaFromItemId } from "./cigarItemId";
import { applyVitola, needsVitolaPick, type CigarSheetOpen } from "./cigarVitola";

export type StockRow = { itemId: string; count: number };

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
