/** Hybrid OCR: optional online API → embedded PaddleOCR.js → tesseract. */
import { preprocessImage } from "./ocrPreprocess";
import {
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

async function getPaddleJs(): Promise<PaddleInstance | null> {
  if (!paddleSingleton) {
    paddleSingleton = (async () => {
      try {
        const mod = await import("@paddleocr/paddleocr-js");
        if (!mod?.PaddleOCR?.create) return null;
        // latin/en brand names on cigars & HR receipts
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

async function ocrOnline(file: File): Promise<OcrEngineResult | null> {
  const base = apiBaseUrl();
  if (!base || !isOnlinePreferred()) return null;
  try {
    const body = new FormData();
    body.append("file", file, file.name || "scan.jpg");
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 45_000);
    const res = await fetch(`${base}/ocr`, { method: "POST", body, signal: ctrl.signal });
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
    const raw = await ocr.predict(file);
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
    const modes =
      mode === "receipt" ? [PSM.SINGLE_COLUMN, PSM.AUTO] : [PSM.SPARSE_TEXT];
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
 * PWA path: paddleocr-js (embedded) → tesseract.
 * Optional local/dev API when VITE_OCR_API_URL is set.
 */
export async function recognizeImage(
  file: File,
  onStatus?: (msg: string) => void,
  mode: ScanMode = "cigar",
): Promise<OcrEngineResult> {
  // Prefer embedded browser Paddle for GitHub Pages PWA; API only if configured.
  if (apiBaseUrl() && isOnlinePreferred()) {
    onStatus?.("online");
    const online = await ocrOnline(file);
    if (online && (online.text.trim() || online.lines.length > 0)) return online;
  }

  onStatus?.("paddle");
  const paddle = await ocrPaddleJs(file);
  if (paddle && (paddle.text.trim() || paddle.lines.length > 0)) return paddle;

  onStatus?.("tesseract");
  return ocrTesseract(file, mode);
}
