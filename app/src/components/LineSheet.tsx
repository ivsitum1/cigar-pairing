// Linija: priča + metrike + puna tablica vitola (Phase 4).
import { useMemo } from "react";
import { SheetShell } from "./SheetShell";
import type { Cigar, Vitola } from "../types";
import { brandInfo, brandDisplayName, resolveCigarId } from "../data";
import { useI18n } from "../i18n";
import { Meter } from "./ui";
import { BackButton } from "./BackButton";
import { applyVitola, needsVitolaPick, uniqueVitolas } from "../lib/cigarVitola";
import { formatEur, vitolaPriceForMarket } from "../lib/cigarPrice";
import { vitolaBlurb } from "../lib/vitolaInfo";
import { cigarDescription } from "../lib/cigarNote";
import { cigarItemId } from "../lib/cigarItemId";
import { useMarket } from "../store/market";
import { totalStock, useHumidors } from "../store/humidor";

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
  const { t, cn, lang } = useI18n();
  const market = useMarket();
  useHumidors();
  const description = cigarDescription(raw, lang);
  const cigar = resolveCigarId(raw.id) ?? raw;
  const info = brandInfo(cigar.brand);
  const displayBrand = brandDisplayName(cigar.brand, market);
  const vitolas = useMemo(() => uniqueVitolas(cigar), [cigar]);
  const unassignedPool = totalStock(cigar.id);
  const showUnassignedBanner = unassignedPool > 0 && needsVitolaPick(cigar);

  return (
    <SheetShell
      onClose={onClose}
      label={`${cigar.brand} ${cigar.line}`}
      panelClassName="max-h-[88vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
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
              {displayBrand}
            </button>
          ) : (
            displayBrand
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

        {description && (
          <p className="mt-3 text-sm leading-relaxed text-papir/85">{description}</p>
        )}

        <div className="band-rule my-4" />

        <div className="mb-2 flex items-baseline justify-between gap-2">
          <span className="text-micro uppercase tracking-widest text-dim">
            {t("common.vitolas")}
          </span>
          <span className="text-xs text-dim">
            {vitolas.length} {t("common.vitolaCountSuffix")}
          </span>
        </div>

        {showUnassignedBanner && (
          <p className="mb-2 text-xs text-dim">
            {t("hum.unassignedLine")}: {unassignedPool}
          </p>
        )}

        <div className="space-y-1.5">
          {vitolas.map((v) => {
            const blurb = vitolaBlurb(v.name, lang);
            const shape = v.shape && v.shape !== v.name ? v.shape : null;
            // isti razrješivač kao popis i kartica — ranije je ovdje stajalo
            // "provjeri cijenu" za vitolu čiju je cijenu kartica pokazivala
            const { price, url, approx, region } = vitolaPriceForMarket(v, market);
            const n = totalStock(cigarItemId(applyVitola(cigar, v)));
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
                  {price != null
                    ? `${approx ? "~" : ""}${formatEur(price)}${
                        market === "ALL" && region && region !== "HR" ? ` ${region}` : ""
                      }`
                    : t("price.check")}
                  {n > 0 && <div className="text-micro text-zlato-2">⌂ {n}</div>}
                  {url ? (
                    <a
                      href={url}
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
        </button>    </SheetShell>
  );
}
