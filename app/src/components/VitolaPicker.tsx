import type { Cigar, Vitola } from "../types";
import { useI18n } from "../i18n";
import { uniqueVitolas } from "../lib/cigarVitola";

export function VitolaPicker({
  cigar,
  onPick,
  onBack,
}: {
  cigar: Cigar;
  onPick: (vitola: Vitola) => void;
  onBack: () => void;
}) {
  const { t } = useI18n();
  const vitolas = uniqueVitolas(cigar);

  return (
    <div className="mt-3 rounded-xl border border-zlato/35 bg-cedar p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="font-display text-sm text-papir">
            {cigar.brand} <span className="text-zlato-2">{cigar.line}</span>
          </div>
          <p className="mt-1 text-xs text-dim">{t("pair.pickVitolaHint")}</p>
        </div>
        <button
          type="button"
          onClick={onBack}
          className="shrink-0 rounded-md border border-dim/30 px-2 py-1 text-xs text-dim hover:border-zlato/50"
        >
          ←
        </button>
      </div>
      <div className="mt-3 space-y-1.5">
        {vitolas.map((v) => (
          <button
            key={v.name}
            type="button"
            onClick={() => onPick(v)}
            className="flex w-full items-baseline justify-between gap-2 rounded-lg border border-dim/15 bg-humidor px-3 py-2.5 text-left hover:border-zlato/40"
          >
            <span className="text-sm text-papir">{v.name}</span>
            <span className="shrink-0 text-xs text-dim">
              {v.format && v.format !== "—" ? `${v.format} · ` : ""}
              {v.smokeTimeMin != null ? `⏱ ${v.smokeTimeMin}′` : ""}
              {v.priceEUR != null ? ` · ${v.priceEUR.toFixed(2)} €` : ""}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
