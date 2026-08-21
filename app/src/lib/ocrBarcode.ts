/** Barkod s fotke → katalog itemId (BarcodeDetector + digit fallback iz OCR teksta). */
import catalog from "../data/barcodeCatalog.json";

export type BarcodeHit = {
  code: string;
  itemId: string;
  source: "detector" | "ocr-digits";
};

const MAP = catalog as Record<string, string>;

/** Normaliziraj EAN/UPC: samo znamenke, trim leading zeros za UPC-A u EAN-13. */
export function normalizeBarcodeDigits(raw: string): string[] {
  const digits = raw.replace(/\D/g, "");
  if (digits.length < 8) return [];
  const out = new Set<string>([digits]);
  // UPC-A (12) ↔ EAN-13 s leading 0
  if (digits.length === 12) out.add(`0${digits}`);
  if (digits.length === 13 && digits.startsWith("0")) out.add(digits.slice(1));
  // drop leading zeros variants for 11–12 digit shop codes
  if (digits.length >= 11 && digits.startsWith("0")) out.add(digits.replace(/^0+/, ""));
  return [...out];
}

export function lookupBarcode(code: string): string | null {
  for (const n of normalizeBarcodeDigits(code)) {
    if (MAP[n]) return MAP[n];
  }
  return null;
}

/** Iz OCR teksta izvuci duge brojčane nizove i pokušaj lookup. */
export function lookupBarcodeInText(text: string): BarcodeHit | null {
  const matches = text.match(/\b\d{8,14}\b/g) ?? [];
  for (const m of matches) {
    const id = lookupBarcode(m);
    if (id) return { code: m, itemId: id, source: "ocr-digits" };
  }
  // razmaknuti EAN: "8 14539 01162 4"
  const spaced = text.match(/\b(?:\d[\d\s]{6,18}\d)\b/g) ?? [];
  for (const m of spaced) {
    const id = lookupBarcode(m);
    if (id) return { code: m.replace(/\s+/g, ""), itemId: id, source: "ocr-digits" };
  }
  return null;
}

type DetectorBarcode = { rawValue: string };

type BarcodeDetectorLike = {
  detect: (source: ImageBitmapSource) => Promise<DetectorBarcode[]>;
};

function getDetector(): BarcodeDetectorLike | null {
  const BD = (globalThis as { BarcodeDetector?: new (opts?: { formats?: string[] }) => BarcodeDetectorLike })
    .BarcodeDetector;
  if (!BD) return null;
  try {
    return new BD({
      formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128", "qr_code"],
    });
  } catch {
    try {
      return new BD();
    } catch {
      return null;
    }
  }
}

/** Pokušaj native BarcodeDetector na slici. */
export async function detectBarcodeFromImage(file: Blob): Promise<BarcodeHit | null> {
  const detector = getDetector();
  if (!detector) return null;
  try {
    const bmp = await createImageBitmap(file);
    try {
      const codes = await detector.detect(bmp);
      for (const c of codes) {
        const id = lookupBarcode(c.rawValue);
        if (id) return { code: c.rawValue, itemId: id, source: "detector" };
      }
    } finally {
      bmp.close();
    }
  } catch {
    return null;
  }
  return null;
}
