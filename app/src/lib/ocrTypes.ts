/** Shared OCR result shapes (online API + on-device). */

export interface OcrLine {
  text: string;
  confidence: number;
  box?: number[][] | null;
}

export interface OcrEngineResult {
  text: string;
  lines: OcrLine[];
  engine: "api" | "paddleocr-js" | "tesseract" | "stub";
  source: "online" | "offline";
}

export type ScanMode = "cigar" | "receipt";

export function apiBaseUrl(): string {
  const raw = (import.meta.env.VITE_OCR_API_URL as string | undefined)?.trim();
  return raw?.replace(/\/$/, "") ?? "";
}

export function isOnlinePreferred(): boolean {
  return typeof navigator !== "undefined" ? navigator.onLine : true;
}

/**
 * Zaglavlja za lokalni OCR servis.
 * `VITE_OCR_API_TOKEN` mora odgovarati `OCR_API_TOKEN` na servisu; kad nije
 * postavljen, servis radi bez provjere (lokalni razvoj na 127.0.0.1).
 */
export function apiAuthHeaders(): Record<string, string> {
  const token = (import.meta.env.VITE_OCR_API_TOKEN as string | undefined)?.trim();
  return token ? { Authorization: `Bearer ${token}` } : {};
}
