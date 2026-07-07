// OCR unos: fotografiraj bocu/cigaru -> prepoznaj tekst -> pronadji u indeksu.
// Koristi tesseract.js (radi u pregledniku; ucitava se tek na prvu upotrebu).
import { useRef, useState } from "react";
import { useI18n } from "../i18n";
import { matchOcrText, tokenize, STOP, type OcrCandidate } from "../lib/ocrMatch";

export type { OcrCandidate };

export function OcrScan({
  candidates,
  onMatch,
  onText,
}: {
  candidates: OcrCandidate[];
  onMatch: (id: string) => void;
  onText: (recognized: string) => void; // fallback: ubaci u pretragu
}) {
  const { t } = useI18n();
  const fileRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setBusy(true);
    setStatus(t("ocr.working"));
    try {
      const Tesseract = await import("tesseract.js");
      const result = await Tesseract.recognize(file, "eng", {
        logger: (m) => {
          if (m.status === "recognizing text") {
            setStatus(`${t("ocr.working")} ${Math.round(m.progress * 100)}%`);
          }
        },
      });
      const text = result.data.text ?? "";
      const match = matchOcrText(text, candidates);
      if (match) {
        setStatus(`✓ ${match.candidate.label}`);
        onMatch(match.candidate.id);
      } else {
        // nema pouzdanog pogotka — ponudi najdulju prepoznatu rijec u pretrazi
        const words = tokenize(text).filter((w) => !STOP.has(w));
        if (words.length > 0) {
          const longest = words.sort((a, b) => b.length - a.length)[0];
          onText(longest);
          setStatus(t("ocr.partial"));
        } else {
          setStatus(t("ocr.noMatch"));
        }
      }
    } catch {
      setStatus(t("ocr.error"));
    } finally {
      setBusy(false);
      setTimeout(() => setStatus(null), 4000);
    }
  };

  return (
    <div className="shrink-0">
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
          e.target.value = "";
        }}
      />
      <button
        onClick={() => fileRef.current?.click()}
        disabled={busy}
        title={t("ocr.scan")}
        className="flex h-full items-center gap-1.5 rounded-lg border border-zlato/40 bg-zlato/10 px-3 py-2.5 text-sm text-zlato-2 hover:bg-zlato/20 disabled:opacity-50"
      >
        📷
      </button>
      {status && (
        <div className="fixed inset-x-4 bottom-20 z-50 mx-auto max-w-md rounded-lg border border-zlato/40 bg-humidor px-3 py-2 text-center text-sm text-papir shadow-lg">
          {status}
        </div>
      )}
    </div>
  );
}
