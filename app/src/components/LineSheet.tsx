// Linija: priča + metrike + puna tablica vitola (Phase 4).
import { useMemo } from "react";
import { SheetShell } from "./SheetShell";
import type { Cigar, Vitola } from "../types";
import { brandInfo, brandDisplayName, resolveCigarId } from "../data";
import { useI18n, leafMetaParts } from "../i18n";
import { TasteMeters } from "./TasteMeters";
import { ProductThumb } from "./ProductThumb";
import { applyVitola, vitolasForMarket } from "../lib/cigarVitola";
import { productPhoto, productPhotoForCigar } from "../lib/productImage";
import { BackButton } from "./BackButton";
import { formatEur, vitolaPriceForMarket } from "../lib/cigarPrice";
import { vitolaBlurb } from "../lib/vitolaInfo";
import { cigarDescription } from "../lib/cigarNote";
import { vitolaStockId } from "../lib/humidorVitola";
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
  const { t, lang } = useI18n();
  const market = useMarket();
  useHumidors();
  const description = cigarDescription(raw, lang);
  const cigar = resolveCigarId(raw.id) ?? raw;
  const info = brandInfo(cigar.brand);
  const displayBrand = brandDisplayName(cigar.brand, market);
  const vitolas = useMemo(() => vitolasForMarket(cigar, market), [cigar, market]);
  const photo =
    vitolas.length === 1
      ? productPhotoForCigar(applyVitola(cigar, vitolas[0]!))
      : productPhoto("cigar", cigar.id);

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

        {/* Slika stoji uz naziv linije, jednako kao na kartici vitole — ista
            stavka ne smije se u dva sheeta prikazivati na dva nacina. */}
        <div className="flex items-start gap-3">
          <div className="min-w-0 flex-1">
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
              {leafMetaParts(cigar.wrapper, cigar.country, lang).join(" · ")}
              {info?.founded ? ` · ${info.founded}` : ""}
            </div>
          </div>
          {photo && (
            <ProductThumb
              src={photo.src}
              treatment={photo.treatment}
              alt={`${displayBrand} ${cigar.line}`}
            />
          )}
        </div>

        <TasteMeters cigar={cigar} />

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

        {vitolas.length === 0 ? (
          <p className="rounded-lg border border-dim/20 bg-cedar/50 px-3 py-3 text-sm leading-relaxed text-dim">
            {t("brand.noneInMarket")}
          </p>
        ) : (
        <div className="space-y-1.5">
          {vitolas.map((v) => {
            const blurb = vitolaBlurb(v.name, lang);
            const shape = v.shape && v.shape !== v.name ? v.shape : null;
            // isti razrješivač kao popis i kartica — ranije je ovdje stajalo
            // "provjeri cijenu" za vitolu čiju je cijenu kartica pokazivala
            const { price, url, approx, region } = vitolaPriceForMarket(v, market);
            // koliko ih te veličine stoji u humidorima — zaliha ide po vitoli
            const stock = totalStock(vitolaStockId(cigar, v));
            return (
              <button
                key={v.name}
                type="button"
                onClick={() => onOpenVitola(cigar, v)}
                className="flex w-full items-start justify-between gap-3 rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
              >
                <div className="min-w-0">
                  <div className="truncate font-display text-sm text-papir">
                    {v.name}
                    {stock > 0 && (
                      <span
                        className="ml-1.5 rounded-full border border-zlato/40 px-1.5 py-0.5 align-middle text-micro text-zlato-2"
                        title={t("hum.inHumidor")}
                      >
                        ⌂ {stock}
                      </span>
                    )}
                  </div>
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
        )}

        <button
          type="button"
          onClick={onClose}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("common.close")}
        </button>    </SheetShell>
  );
}
