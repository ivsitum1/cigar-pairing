import type { Cigar, Vitola } from "../types";
import { useI18n } from "../i18n";
import { uniqueVitolas } from "../lib/cigarVitola";
import { vitolaBlurb } from "../lib/vitolaInfo";

// Modal: linija ima više formata -> odaberi vitolu.
// Overlay (ne inline) da se uvijek otvori odmah, i kod dugih popisa.
export function VitolaPicker({
  cigar,
  onPick,
  onBack,
}: {
  cigar: Cigar;
  onPick: (vitola: Vitola) => void;
  onBack: () => void;
}) {
  const { t, lang } = useI18n();
  const vitolas = uniqueVitolas(cigar);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onBack}
    >
      <div
        className="max-h-[80vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-dim/40 sm:hidden" />
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="font-display text-lg text-papir">
              {cigar.brand} <span className="text-zlato-2">{cigar.line}</span>
            </div>
            <p className="mt-1 text-xs text-dim">{t("pair.pickVitolaHint")}</p>
          </div>
          <button
            type="button"
            onClick={onBack}
            className="shrink-0 rounded-md border border-dim/30 px-2.5 py-1.5 text-xs text-dim hover:border-zlato/50"
          >
            ✕
          </button>
        </div>
        <div className="mt-3 space-y-1.5">
          {vitolas.map((v) => {
            const blurb = vitolaBlurb(v.name, lang);
            return (
              <button
                key={v.name}
                type="button"
                onClick={() => onPick(v)}
                className="w-full rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-sm text-papir">{v.name}</span>
                  <span className="shrink-0 text-xs text-dim">
                    {v.format && v.format !== "—" ? `${v.format} · ` : ""}
                    {v.smokeTimeMin != null ? `⏱ ${v.smokeTimeMin}′` : ""}
                    {v.priceEUR != null ? ` · ${v.priceEUR.toFixed(2)} €` : ""}
                  </span>
                </div>
                {blurb && (
                  <div className="mt-1 text-[11px] leading-snug text-dim/85">{blurb}</div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
