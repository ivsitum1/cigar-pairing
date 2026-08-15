// Sampler u humidor ulazi RAZLOŽEN.
//
// Paket od pet Toro cigara nije jedna cigara: kad ga staviš u humidor, na
// stanju moraju biti te vitole pojedinačno — inače ih ne možeš rasporediti,
// popušiti jednu po jednu ni zabilježiti večer s onom pravom.
//
// Sadržaj paketa je opisni tekst (`lineup`), pa se razrješava istim
// razrješivačem koji već otvara chipove na kartici (`lib/samplerLink`).
import type { Cigar } from "../types";
import { cigarItemId } from "./cigarItemId";
import { resolveSamplerCigar } from "./samplerLink";

export interface SamplerPart {
  /** Ključ zalihe/kolekcije te vitole. */
  itemId: string;
  cigar: Cigar;
  /** Koliko komada paket sadrži (oznaka „×2"). */
  count: number;
  /** Izvorna oznaka iz paketa. */
  label: string;
}

/** Paket je sve što ima popis sadržaja. */
export function isSampler(cigar: Cigar): boolean {
  return (cigar.lineup?.length ?? 0) > 0;
}

const QTY = /[×x]\s*(\d+)\b/;

/** „Serie V Robusto ×2" → 2; bez oznake → 1. */
export function samplerLabelCount(label: string): number {
  const m = QTY.exec(label);
  if (!m) return 1;
  const n = Number(m[1]);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 1;
}

/** Sadržaj paketa razriješen u stvarne ključeve; nerazriješeno se izostavlja. */
export function samplerParts(cigar: Cigar): SamplerPart[] {
  const parts = new Map<string, SamplerPart>();
  for (const label of cigar.lineup ?? []) {
    const hit = resolveSamplerCigar(cigar.brand, label, cigar.id);
    if (!hit) continue;
    const itemId = cigarItemId(hit);
    const count = samplerLabelCount(label);
    const prev = parts.get(itemId);
    // isti format dvaput u paketu → zbroji, ne prepiši
    if (prev) prev.count += count;
    else parts.set(itemId, { itemId, cigar: hit, count, label });
  }
  return [...parts.values()];
}

/** Oznake koje katalog ne zna razriješiti — korisniku se kaže što je ispalo. */
export function unresolvedSamplerLabels(cigar: Cigar): string[] {
  return (cigar.lineup ?? []).filter(
    (label) => resolveSamplerCigar(cigar.brand, label, cigar.id) == null,
  );
}

/** Ukupan broj cigara u paketu (samo razriješene). */
export function samplerPieceCount(cigar: Cigar): number {
  return samplerParts(cigar).reduce((sum, p) => sum + p.count, 0);
}
