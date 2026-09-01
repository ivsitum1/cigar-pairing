/** Client helpers for band reference upload + visual match fusion. */
import { apiAuthHeaders, apiBaseUrl, isOnlinePreferred } from "./ocrTypes";
import type { OcrCandidate } from "./ocrMatch";
import { matchOcrText } from "./ocrMatch";

export interface BandMatch {
  cigarId: string;
  score: number;
  refId: string;
}

/**
 * Puni referentnu bazu prstena (`POST /band/reference`, vidi backend/README.md).
 * Aplikacija je namjerno ne zove: baza se puni izvan nje, a `matchBandImage`
 * je onda samo cita. Nije zaostatak — brisanje bi ostavilo dokumentirani
 * endpoint bez klijenta.
 */
export async function uploadBandReference(
  cigarId: string,
  file: File,
): Promise<{ ok: true; refId: string } | { ok: false; error: string }> {
  const base = apiBaseUrl();
  if (!base) return { ok: false, error: "no-api" };
  if (!isOnlinePreferred()) return { ok: false, error: "offline" };
  try {
    const body = new FormData();
    body.append("cigar_id", cigarId);
    body.append("file", file, file.name || "band.jpg");
    const res = await fetch(`${base}/band/reference`, {
      method: "POST",
      headers: apiAuthHeaders(),
      body,
    });
    if (!res.ok) return { ok: false, error: `http-${res.status}` };
    const data = (await res.json()) as { ref_id?: string };
    return { ok: true, refId: data.ref_id ?? "" };
  } catch {
    return { ok: false, error: "network" };
  }
}

export async function matchBandImage(file: File, topK = 5): Promise<BandMatch[]> {
  const base = apiBaseUrl();
  if (!base || !isOnlinePreferred()) return [];
  try {
    const body = new FormData();
    body.append("file", file, file.name || "scan.jpg");
    const res = await fetch(`${base}/band/match?top_k=${topK}`, {
      method: "POST",
      headers: apiAuthHeaders(),
      body,
    });
    if (!res.ok) return [];
    const data = (await res.json()) as { matches?: BandMatch[] };
    return data.matches ?? [];
  } catch {
    return [];
  }
}

/**
 * Fuse text OCR score with visual band scores.
 * Text match wins when strong; otherwise band can promote a candidate.
 */
export function fuseOcrAndBand(
  ocrText: string,
  candidates: OcrCandidate[],
  bandHits: BandMatch[],
): { candidate: OcrCandidate; score: number; source: "text" | "band" | "fusion" } | null {
  const textHit = matchOcrText(ocrText, candidates);
  const byId = new Map(candidates.map((c) => [c.id, c]));

  let bestBand: { candidate: OcrCandidate; score: number } | null = null;
  for (const h of bandHits) {
    const c = byId.get(h.cigarId);
    if (!c) continue;
    // phash/clip cosine typically 0–1; scale to OCR-ish points
    const scaled = h.score * 6;
    if (!bestBand || scaled > bestBand.score) bestBand = { candidate: c, score: scaled };
  }

  if (textHit && bestBand && textHit.candidate.id === bestBand.candidate.id) {
    return {
      candidate: textHit.candidate,
      score: textHit.score + bestBand.score * 0.5,
      source: "fusion",
    };
  }
  if (textHit && textHit.score >= 3) {
    return { candidate: textHit.candidate, score: textHit.score, source: "text" };
  }
  if (bestBand && bestBand.score >= 3.5) {
    return { candidate: bestBand.candidate, score: bestBand.score, source: "band" };
  }
  if (textHit) {
    return { candidate: textHit.candidate, score: textHit.score, source: "text" };
  }
  if (bestBand) {
    return { candidate: bestBand.candidate, score: bestBand.score, source: "band" };
  }
  return null;
}
