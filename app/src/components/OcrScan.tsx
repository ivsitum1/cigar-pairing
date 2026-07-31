// OCR: fotografija → tesseract (etikete) / paddleocr-js (računi) / optional API
// Jedna cigara: potvrda → Sparivanje (ne auto-Imam). Boce: direktan match.
// Račun: lista → batch Imam.
import { useRef, useState } from "react";
import { useI18n } from "../i18n";
import { matchOcrText, tokenize, STOP, type OcrCandidate } from "../lib/ocrMatch";
import { recognizeImage } from "../lib/ocrEngine";
import { fuseOcrAndBand, matchBandImage } from "../lib/bandMatch";
import { parseReceiptText, type ReceiptLineMatch } from "../lib/receiptParse";
import { markOwnedBatch } from "../store/collection";
import type { ScanMode } from "../lib/ocrTypes";

export type { OcrCandidate };

export type CigarConfirmAction = "pair" | "owned" | "detail" | "dismiss";

function previewText(text: string, max = 72): string {
  const compact = text.replace(/\s+/g, " ").trim();
  if (!compact) return "";
  return compact.length <= max ? compact : `${compact.slice(0, max)}…`;
}

export function OcrScan({
  candidates,
  onMatch,
  onText,
  onConfirmCigar,
  enableReceipt = true,
  enableBand = true,
}: {
  candidates: OcrCandidate[];
  onMatch?: (id: string) => void;
  onText: (recognized: string) => void;
  /** When set, cigar hits open confirm sheet. Drinks should omit this and use onMatch. */
  onConfirmCigar?: (id: string, action: CigarConfirmAction) => void;
  enableReceipt?: boolean;
  enableBand?: boolean;
}) {
  const { t } = useI18n();
  const fileRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [mode, setMode] = useState<ScanMode>("cigar");
  const [cigarHit, setCigarHit] = useState<{
    id: string;
    label: string;
    score: number;
    source: string;
  } | null>(null);
  const [receiptRows, setReceiptRows] = useState<ReceiptLineMatch[] | null>(null);

  const applyHit = (id: string, label: string, score: number, source: string) => {
    if (onConfirmCigar) {
      setCigarHit({ id, label, score, source });
      setStatus(null);
      return;
    }
    onMatch?.(id);
    setStatus(null);
  };

  const handleFile = async (file: File) => {
    setBusy(true);
    setStatus(t("ocr.working"));
    setCigarHit(null);
    setReceiptRows(null);
    try {
      const result = await recognizeImage(
        file,
        (phase) => {
          if (phase === "paddle") setStatus(t("ocr.workingPaddle"));
          else if (phase === "tesseract") setStatus(t("ocr.workingTess"));
          else setStatus(t("ocr.working"));
        },
        mode,
      );
      const text = result.text;
      const preview = previewText(text);

      if (mode === "receipt") {
        const rows = parseReceiptText(text, candidates);
        if (rows.length === 0) {
          const words = tokenize(text).filter((w) => !STOP.has(w));
          if (words.length > 0) {
            onText(words.sort((a, b) => b.length - a.length)[0]);
            setStatus(
              preview
                ? `${t("ocr.partial")}: ${preview}`
                : t("ocr.partial"),
            );
          } else {
            setStatus(
              preview ? `${t("ocr.noMatch")}: ${preview}` : t("ocr.noMatch"),
            );
          }
          return;
        }
        setReceiptRows(rows);
        setStatus(null);
        return;
      }

      let bandHits: Awaited<ReturnType<typeof matchBandImage>> = [];
      if (enableBand && onConfirmCigar) {
        bandHits = await matchBandImage(file);
      }
      const fused = fuseOcrAndBand(text, candidates, bandHits);
      if (fused) {
        applyHit(
          fused.candidate.id,
          fused.candidate.label,
          fused.score,
          fused.source,
        );
        return;
      }

      const match = matchOcrText(text, candidates);
      if (match) {
        applyHit(
          match.candidate.id,
          match.candidate.label,
          match.score,
          "text",
        );
        return;
      }

      const words = tokenize(text).filter((w) => !STOP.has(w));
      if (words.length > 0) {
        onText(words.sort((a, b) => b.length - a.length)[0]);
        setStatus(
          preview ? `${t("ocr.partial")}: ${preview}` : t("ocr.partial"),
        );
      } else {
        setStatus(
          preview ? `${t("ocr.noMatch")}: ${preview}` : t("ocr.noMatch"),
        );
      }
    } catch {
      setStatus(t("ocr.error"));
    } finally {
      setBusy(false);
      setTimeout(() => setStatus(null), 5000);
    }
  };

  const confirmCigar = (action: CigarConfirmAction) => {
    if (!cigarHit) return;
    const id = cigarHit.id;
    setCigarHit(null);
    if (action === "owned") markOwnedBatch([id]);
    if (onConfirmCigar) {
      onConfirmCigar(id, action);
      return;
    }
    if (action === "pair" || action === "detail" || action === "owned") {
      onMatch?.(id);
    }
  };

  const toggleReceipt = (idx: number) => {
    setReceiptRows((rows) =>
      rows
        ? rows.map((r, i) => (i === idx ? { ...r, selected: !r.selected } : r))
        : rows,
    );
  };

  const commitReceipt = () => {
    if (!receiptRows) return;
    const ids = receiptRows
      .filter((r) => r.selected && r.candidate)
      .map((r) => r.candidate!.id);
    markOwnedBatch(ids);
    setReceiptRows(null);
    setStatus(t("ocr.receiptDone").replace("{n}", String(ids.length)));
    setTimeout(() => setStatus(null), 3500);
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
          if (f) void handleFile(f);
          e.target.value = "";
        }}
      />
      <div className="flex items-stretch gap-1">
        {enableReceipt && (
          <div className="flex overflow-hidden rounded-lg border border-zlato/30 text-[10px]">
            <button
              type="button"
              disabled={busy}
              onClick={() => setMode("cigar")}
              className={`px-1.5 py-1 ${mode === "cigar" ? "bg-zlato/25 text-zlato-2" : "text-dim"}`}
              title={t("ocr.modeCigar")}
            >
              {t("ocr.modeCigarShort")}
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => setMode("receipt")}
              className={`px-1.5 py-1 ${mode === "receipt" ? "bg-zlato/25 text-zlato-2" : "text-dim"}`}
              title={t("ocr.modeReceipt")}
            >
              {t("ocr.modeReceiptShort")}
            </button>
          </div>
        )}
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={busy}
          title={mode === "receipt" ? t("ocr.scanReceipt") : t("ocr.scan")}
          className="flex h-full items-center gap-1.5 rounded-lg border border-zlato/40 bg-zlato/10 px-3 py-2.5 text-sm text-zlato-2 hover:bg-zlato/20 disabled:opacity-50"
        >
          📷
        </button>
      </div>

      {status && !cigarHit && !receiptRows && (
        <div className="fixed inset-x-4 bottom-20 z-50 mx-auto max-w-md rounded-lg border border-zlato/40 bg-humidor px-3 py-2 text-center text-sm text-papir shadow-lg">
          {status}
        </div>
      )}

      {cigarHit && (
        <div
          className="fixed inset-0 z-[60] flex items-end justify-center bg-black/60 sm:items-center"
          onClick={() => setCigarHit(null)}
        >
          <div
            className="w-full max-w-md rounded-t-2xl border border-zlato/30 bg-humidor p-4 pb-6 sm:rounded-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-xs uppercase tracking-wide text-dim">{t("ocr.confirmTitle")}</p>
            <p className="mt-1 font-display text-lg text-papir">{cigarHit.label}</p>
            <p className="mt-1 text-xs text-dim">{t("ocr.confirmHint")}</p>
            <div className="mt-4 flex flex-col gap-2">
              <button
                type="button"
                className="rounded-lg bg-zlato/90 px-3 py-2.5 text-sm font-medium text-humidor"
                onClick={() => confirmCigar("pair")}
              >
                {t("ocr.actionPair")}
              </button>
              <button
                type="button"
                className="rounded-lg border border-zlato/40 px-3 py-2 text-sm text-zlato-2"
                onClick={() => confirmCigar("owned")}
              >
                {t("ocr.actionOwned")}
              </button>
              <button
                type="button"
                className="rounded-lg border border-dim/40 px-3 py-2 text-sm text-papir"
                onClick={() => confirmCigar("detail")}
              >
                {t("ocr.actionDetail")}
              </button>
              <button
                type="button"
                className="text-sm text-dim underline"
                onClick={() => confirmCigar("dismiss")}
              >
                {t("ocr.actionWrong")}
              </button>
            </div>
          </div>
        </div>
      )}

      {receiptRows && (
        <div
          className="fixed inset-0 z-[60] flex items-end justify-center bg-black/60 sm:items-center"
          onClick={() => setReceiptRows(null)}
        >
          <div
            className="max-h-[80vh] w-full max-w-md overflow-y-auto rounded-t-2xl border border-zlato/30 bg-humidor p-4 pb-6 sm:rounded-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-xs uppercase tracking-wide text-dim">{t("ocr.receiptTitle")}</p>
            <p className="mt-1 text-sm text-papir/80">{t("ocr.receiptHint")}</p>
            <ul className="mt-3 space-y-2">
              {receiptRows.map((row, idx) => (
                <li
                  key={`${row.candidate?.id ?? "x"}-${idx}`}
                  className="flex items-start gap-2 rounded-lg border border-zlato/20 px-2 py-2"
                >
                  <input
                    type="checkbox"
                    checked={row.selected}
                    onChange={() => toggleReceipt(idx)}
                    className="mt-1"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-papir">
                      {row.candidate?.label ?? row.raw}
                    </p>
                    <p className="text-xs text-dim">
                      ×{row.qty} · {row.raw}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
            <button
              type="button"
              className="mt-4 w-full rounded-lg bg-zlato/90 px-3 py-2.5 text-sm font-medium text-humidor disabled:opacity-40"
              disabled={!receiptRows.some((r) => r.selected)}
              onClick={commitReceipt}
            >
              {t("ocr.receiptCommit")}
            </button>
            <button
              type="button"
              className="mt-2 w-full text-sm text-dim underline"
              onClick={() => setReceiptRows(null)}
            >
              {t("common.back")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
