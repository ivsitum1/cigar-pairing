/** Hybrid OCR: tesseract for labels, paddleocr-js for receipts, optional API. */
import { preprocessImage } from "./ocrPreprocess";
import {
  apiAuthHeaders,
  apiBaseUrl,
  isOnlinePreferred,
  type OcrEngineResult,
  type OcrLine,
  type ScanMode,
} from "./ocrTypes";

type PaddleInstance = {
  predict: (input: File | Blob | ImageBitmap | HTMLCanvasElement) => Promise<unknown[]>;
};

let paddleSingleton: Promise<PaddleInstance | null> | null = null;

export type OcrWarmPhase = "paddle" | "tesseract";

/**
 * Resetira runtime cache-a za offline OCR modele.
 * Koristi se kada korisnik ukloni OCR pack.
 */
export function resetOcrEngines(): void {
  paddleSingleton = null;
}

function parsePaddleResult(result: unknown): { text: string; lines: OcrLine[] } {
  const lines: OcrLine[] = [];
  if (!result || typeof result !== "object") {
    return { text: "", lines };
  }
  const rec = result as {
    items?: { text?: string; score?: number; confidence?: number }[];
    texts?: string[];
    scores?: number[];
    rec_texts?: string[];
    rec_scores?: number[];
  };

  if (Array.isArray(rec.items)) {
    for (const item of rec.items) {
      const t = (item.text ?? "").trim();
      if (!t) continue;
      lines.push({
        text: t,
        confidence: item.score ?? item.confidence ?? 0,
      });
    }
  } else {
    const texts = rec.texts ?? rec.rec_texts ?? [];
    const scores = rec.scores ?? rec.rec_scores ?? [];
    texts.forEach((t, i) => {
      const text = String(t).trim();
      if (!text) return;
      lines.push({ text, confidence: scores[i] ?? 0 });
    });
  }
  return { text: lines.map((l) => l.text).join("\n"), lines };
}

/** Reject empty / low-confidence paddle output so we can fall through to tesseract. */
export function isUsableOcr(result: OcrEngineResult | null | undefined): boolean {
  if (!result) return false;
  const text = result.text.replace(/\s+/g, " ").trim();
  if (text.length < 4) return false;
  const confs = result.lines.map((l) => l.confidence).filter((c) => c > 0);
  if (confs.length >= 2) {
    const avg = confs.reduce((a, b) => a + b, 0) / confs.length;
    // paddleocr-js scores are typically 0–1
    if (avg < 0.35) return false;
  }
  // mostly digits / symbols → useless for brand matching
  const letters = (text.match(/[a-zA-ZÀ-ž]/g) ?? []).length;
  if (letters < 3) return false;
  return true;
}

async function getPaddleJs(): Promise<PaddleInstance | null> {
  if (!paddleSingleton) {
    paddleSingleton = (async () => {
      try {
        const mod = await import("@paddleocr/paddleocr-js");
        if (!mod?.PaddleOCR?.create) return null;
        const ocr = await mod.PaddleOCR.create({
          lang: "en",
          ocrVersion: "PP-OCRv5",
          worker: true,
          ortOptions: {
            backend: "auto",
            wasmPaths: "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/",
          },
        });
        return ocr as PaddleInstance;
      } catch (e) {
        console.warn("[ocr] paddleocr-js init failed", e);
        return null;
      }
    })();
  }
  return paddleSingleton;
}

/**
 * Preload / warmup offline OCR engine-a tako da first scan ne “puca” u hladnom startu.
 * Vraća false ako se Paddle ne može inicijalizirati (tesseract se ionako učitava po scan-u).
 */
export async function warmOcrEngines(
  onPhase?: (phase: OcrWarmPhase) => void,
): Promise<boolean> {
  onPhase?.("paddle");
  const paddle = await getPaddleJs();
  if (!paddle) return false;

  onPhase?.("tesseract");
  await import("tesseract.js");
  return true;
}

/** Downscale huge phone photos — browser OCR chokes on 12MP+ shots. */
async function downscaleForOcr(file: File, maxSide = 1600): Promise<Blob> {
  try {
    const bmp = await createImageBitmap(file);
    const side = Math.max(bmp.width, bmp.height);
    if (side <= maxSide) {
      bmp.close();
      return file;
    }
    const scale = maxSide / side;
    const w = Math.max(1, Math.round(bmp.width * scale));
    const h = Math.max(1, Math.round(bmp.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      bmp.close();
      return file;
    }
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(bmp, 0, 0, w, h);
    bmp.close();
    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob(resolve, "image/jpeg", 0.92),
    );
    return blob ?? file;
  } catch {
    return file;
  }
}

async function ocrOnline(file: File): Promise<OcrEngineResult | null> {
  const base = apiBaseUrl();
  if (!base || !isOnlinePreferred()) return null;
  try {
    const body = new FormData();
    body.append("file", file, file.name || "scan.jpg");
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 45_000);
    const res = await fetch(`${base}/ocr`, {
      method: "POST",
      headers: apiAuthHeaders(),
      body,
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (!res.ok) return null;
    const data = (await res.json()) as {
      text?: string;
      lines?: { text: string; confidence?: number; box?: number[][] | null }[];
    };
    const lines: OcrLine[] = (data.lines ?? []).map((l) => ({
      text: l.text ?? "",
      confidence: l.confidence ?? 0,
      box: l.box ?? null,
    }));
    return {
      text: data.text ?? lines.map((l) => l.text).join("\n"),
      lines,
      engine: "api",
      source: "online",
    };
  } catch {
    return null;
  }
}

async function ocrPaddleJs(file: File): Promise<OcrEngineResult | null> {
  try {
    const ocr = await getPaddleJs();
    if (!ocr) return null;
    const input = await downscaleForOcr(file);
    const raw = await ocr.predict(input);
    const first = Array.isArray(raw) ? raw[0] : raw;
    const parsed = parsePaddleResult(first);
    if (!parsed.text.trim() && parsed.lines.length === 0) return null;
    return {
      text: parsed.text,
      lines: parsed.lines,
      engine: "paddleocr-js",
      source: "offline",
    };
  } catch (e) {
    console.warn("[ocr] paddleocr-js predict failed", e);
    return null;
  }
}

async function ocrTesseract(
  file: File,
  mode: ScanMode = "cigar",
): Promise<OcrEngineResult> {
  const [{ createWorker, PSM }, variants] = await Promise.all([
    import("tesseract.js"),
    preprocessImage(file),
  ]);
  const worker = await createWorker(["eng", "spa"]);
  let text = "";
  try {
    // labels/bands: sparse; receipts: column/auto (SPARSE shreds thermal tables)
    const modes =
      mode === "receipt" ? [PSM.SINGLE_COLUMN, PSM.AUTO] : [PSM.SPARSE_TEXT, PSM.AUTO];
    for (const psm of modes) {
      await worker.setParameters({ tessedit_pageseg_mode: psm });
      for (const v of variants) {
        const r = await worker.recognize(v);
        text += (r.data.text ?? "") + "\n";
      }
    }
  } finally {
    await worker.terminate();
  }
  const lines: OcrLine[] = text
    .split(/\n+/)
    .map((t) => t.trim())
    .filter(Boolean)
    .map((t) => ({ text: t, confidence: 0 }));
  return { text, lines, engine: "tesseract", source: "offline" };
}

/**
 * Labels (cigar / bottle): tesseract first — previous PWA path that worked for bands.
 * Receipts: paddleocr-js first (better on thermal tables), then tesseract.
 * Optional local API when VITE_OCR_API_URL is set.
 */
export async function recognizeImage(
  file: File,
  onStatus?: (msg: string) => void,
  mode: ScanMode = "cigar",
): Promise<OcrEngineResult> {
  if (apiBaseUrl() && isOnlinePreferred()) {
    onStatus?.("online");
    const online = await ocrOnline(file);
    if (isUsableOcr(online)) return online!;
  }

  if (mode === "receipt") {
    onStatus?.("paddle");
    const paddle = await ocrPaddleJs(file);
    if (isUsableOcr(paddle)) return paddle!;
    onStatus?.("tesseract");
    return ocrTesseract(file, mode);
  }

  onStatus?.("tesseract");
  const tess = await ocrTesseract(file, mode);
  if (isUsableOcr(tess)) return tess;

  onStatus?.("paddle");
  const paddle = await ocrPaddleJs(file);
  if (isUsableOcr(paddle)) return paddle!;
  return tess;
}
