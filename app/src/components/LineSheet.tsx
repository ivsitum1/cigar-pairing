// Linija: priča + metrike + puna tablica vitola (Phase 4).
import { useMemo } from "react";
import type { Cigar, Vitola } from "../types";
import { brandInfo, resolveCigarId } from "../data";
import { useI18n } from "../i18n";
import { Meter } from "./ui";
import { BackButton } from "./BackButton";
import { uniqueVitolas } from "../lib/cigarVitola";
import { vitolaBlurb } from "../lib/vitolaInfo";

function dimLabel(v: Vitola): string {
  if (v.ring != null && v.lengthMM != null) return `${v.ring} × ${v.lengthMM} mm`;
  if (v.format && v.format !== "—") return v.format;
  return "—";
}

export function LineSheet({
  cigar: raw,
  onClose,
  onOpenBrand,
  onOpenVitola,
}: {
  cigar: Cigar;
  onClose: () => void;
  onOpenBrand?: (brand: string) => void;
  onOpenVitola: (cigar: Cigar, vitola: Vitola) => void;
}) {
  const { t, lx, cn, lang } = useI18n();
  const cigar = resolveCigarId(raw.id) ?? raw;
  const info = brandInfo(cigar.brand);
  const vitolas = useMemo(() => uniqueVitolas(cigar), [cigar]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onClose}
    >
      <div
        className="max-h-[88vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-dim/40 sm:hidden" />

        <div className="mb-3">
          <BackButton onClick={onClose}>{t("common.back")}</BackButton>
        </div>

        <div className="text-xs text-dim">
          {onOpenBrand ? (
            <button
              type="button"
              onClick={() => onOpenBrand(cigar.brand)}
              className="underline decoration-zlato/40 underline-offset-2 hover:text-zlato-2"
            >
              {cigar.brand}
            </button>
          ) : (
            cigar.brand
          )}
          {" › "}
          <span className="text-zlato-2">{cigar.line}</span>
        </div>

        <div className="mt-1 font-display text-2xl tracking-wide text-papir">
          {cigar.line}
        </div>
        <div className="mt-0.5 text-xs uppercase tracking-widest text-dim">
          {cn(cigar.country)} · {cigar.wrapper}
          {info?.founded ? ` · ${info.founded}` : ""}
        </div>

        <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
          <Meter value={cigar.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
          <Meter value={cigar.body} label={t("common.body")} />
        </div>

        <p className="mt-3 text-sm leading-relaxed text-papir/85">{lx(cigar.notes)}</p>

        <div className="band-rule my-4" />

        <div className="mb-2 flex items-baseline justify-between gap-2">
          <span className="text-micro uppercase tracking-widest text-dim">
            {t("common.vitolas")}
          </span>
          <span className="text-xs text-dim">
            {vitolas.length} {t("common.vitolaCountSuffix")}
          </span>
        </div>

        <div className="space-y-1.5">
          {vitolas.map((v) => {
            const blurb = vitolaBlurb(v.name, lang);
            const shape = v.shape && v.shape !== v.name ? v.shape : null;
            return (
              <button
                key={v.name}
                type="button"
                onClick={() => onOpenVitola(cigar, v)}
                className="flex w-full items-start justify-between gap-3 rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
              >
                <div className="min-w-0">
                  <div className="truncate font-display text-sm text-papir">{v.name}</div>
                  <div className="mt-0.5 truncate text-xs text-dim">
                    {[shape, dimLabel(v), v.smokeTimeMin != null ? `⏱ ${v.smokeTimeMin}′` : null]
                      .filter(Boolean)
                      .join(" · ")}
                  </div>
                  {blurb && (
                    <div className="mt-1 line-clamp-2 text-micro leading-snug text-dim/85">
                      {blurb}
                    </div>
                  )}
                </div>
                <div className="shrink-0 text-right text-xs text-zlato-2">
                  {v.priceEUR != null ? `${v.priceEUR.toFixed(v.priceEUR % 1 ? 2 : 0)} €` : t("price.check")}
                  {v.url ? (
                    <a
                      href={v.url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1 block underline decoration-zlato/40 underline-offset-2"
                    >
                      {t("common.buy")} ↗
                    </a>
                  ) : null}
                </div>
              </button>
            );
          })}
        </div>

        <button
          type="button"
          onClick={onClose}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("common.close")}
        </button>
      </div>
    </div>
  );
}
