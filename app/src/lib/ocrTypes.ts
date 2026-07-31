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
