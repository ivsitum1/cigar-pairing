import { useCallback, useState } from "react";
import type { Cigar, Drink, Vitola } from "../types";
import { resolveCigarId } from "../data";
import { resolveSheetFromItemId } from "../lib/cigarIdentity";
import { parseCigarItemId } from "../lib/cigarItemId";
import { applyVitola, resolveCigarSheetOpen } from "../lib/cigarVitola";
import { LineSheet } from "./LineSheet";
import { DetailSheet } from "./DetailSheet";

export type BrowseDetail =
  | { kind: "cigar"; item: Cigar }
  | { kind: "drink"; item: Drink };

/**
 * Shared line → vitola drill-down for Shopping / Club / Collection / Pairing.
 * Multi-vitola → LineSheet; single / already applied → DetailSheet.
 */
export function useCigarBrowseSheets() {
  const [line, setLine] = useState<Cigar | null>(null);
  const [detail, setDetail] = useState<BrowseDetail | null>(null);

  const openCigar = useCallback((c: Cigar) => {
    const decision = resolveCigarSheetOpen(c);
    if (decision.mode === "line") {
      setDetail(null);
      setLine(decision.cigar);
    } else {
      setLine(null);
      setDetail({ kind: "cigar", item: decision.cigar });
    }
  }, []);

  /**
   * Kartica baš te stavke, bez skretanja na izbor vitole. Popis Kolekcije
   * prikazuje spremljeni ključ (može biti i na razini linije), pa kvačice u
   * kartici moraju dirati taj isti ključ — inače se označeno ne može odznačiti.
   */
  const openCigarCard = useCallback((c: Cigar) => {
    setLine(null);
    setDetail({ kind: "cigar", item: c });
  }, []);

  /**
   * Humidor / spremljeni ključ: `cig-x@churchill` nije katalog-id, pa
   * `resolveCigarId(itemId)` padne — linija se traži preko `cigarId`.
   * Goli `cig-x` ostaje bazen bez vitole (LineSheet ako ih linija ima više).
   */
  const openItemId = useCallback((itemId: string) => {
    const { cigarId } = parseCigarItemId(itemId);
    const line = resolveCigarId(itemId) ?? resolveCigarId(cigarId);
    if (!line) return;
    const decision = resolveSheetFromItemId(itemId, line);
    if (decision.mode === "line") {
      setDetail(null);
      setLine(decision.cigar);
    } else {
      setLine(null);
      setDetail({ kind: "cigar", item: decision.cigar });
    }
  }, []);

  const openVitola = useCallback((c: Cigar, v: Vitola) => {
    const full = resolveCigarId(c.id) ?? c;
    setLine(null);
    setDetail({ kind: "cigar", item: applyVitola(full, v) });
  }, []);

  const openDrink = useCallback((d: Drink) => {
    setLine(null);
    setDetail({ kind: "drink", item: d });
  }, []);

  /** From vitola DetailSheet crumb → full line (all vitolas intact). */
  const openLine = useCallback((c: Cigar) => {
    const full = resolveCigarId(c.id) ?? c;
    setDetail(null);
    setLine(full);
  }, []);

  const closeLine = useCallback(() => setLine(null), []);
  const closeDetail = useCallback(() => setDetail(null), []);
  const closeSheets = useCallback(() => {
    setLine(null);
    setDetail(null);
  }, []);

  return {
    line,
    detail,
    setDetail,
    openCigar,
    openCigarCard,
    openItemId,
    openVitola,
    openDrink,
    openLine,
    closeLine,
    closeDetail,
    closeSheets,
  };
}

export function CigarBrowseSheets({
  line,
  detail,
  onCloseLine,
  onOpenVitola,
  onCloseDetail,
  onOpenLine,
  onPair,
  onLogEvening,
}: {
  line: Cigar | null;
  detail: BrowseDetail | null;
  onCloseLine: () => void;
  onOpenVitola: (cigar: Cigar, vitola: Vitola) => void;
  onCloseDetail: () => void;
  onOpenLine?: (cigar: Cigar) => void;
  onPair?: (target: BrowseDetail) => void;
  onLogEvening?: (cigar: Cigar) => void;
}) {
  return (
    <>
      {line ? (
        <LineSheet cigar={line} onClose={onCloseLine} onOpenVitola={onOpenVitola} />
      ) : null}
      <DetailSheet
        target={detail}
        onClose={onCloseDetail}
        onOpenLine={onOpenLine}
        onPair={onPair}
        onLogEvening={onLogEvening}
      />
    </>
  );
}
