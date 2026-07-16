// Brend stranica: opis + povijest marke i sve njene cigare, sort po ocjeni/cijeni.
import { useMemo, useState } from "react";
import type { Cigar } from "../types";
import { brandInfo, cigarsByBrand, cigarPriceForMarket } from "../data";
import { useI18n } from "../i18n";
import { Meter } from "./ui";
import { BackButton } from "./BackButton";
import { useMarket } from "../store/market";

type Sort = "strength" | "price";

export function BrandSheet({
  brand,
  onClose,
  onOpenCigar,
}: {
  brand: string;
  onClose: () => void;
  onOpenCigar: (c: Cigar) => void;
}) {
  const { t, lx, cn } = useI18n();
  const market = useMarket();
  const [sort, setSort] = useState<Sort>("strength");
  const info = brandInfo(brand);
  const cigars = useMemo(() => cigarsByBrand(brand), [brand]);

  const sorted = useMemo(() => {
    const list = [...cigars];
    if (sort === "price") {
      const p = (c: Cigar) => cigarPriceForMarket(c, market).price ?? 9e9;
      list.sort((a, b) => p(a) - p(b));
    } else {
      list.sort((a, b) => b.strength - a.strength || b.body - a.body);
    }
    return list;
  }, [cigars, sort, market]);

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

        <div className="font-display text-2xl tracking-wide text-zlato-2">{brand}</div>
        {info && (
          <div className="mt-0.5 text-xs uppercase tracking-widest text-dim">
            {cn(info.country)} · {info.founded}
          </div>
        )}
        {info && (
          <p className="mt-3 text-sm leading-relaxed text-papir/85">{lx(info.blurb)}</p>
        )}

        <div className="band-rule my-4" />

        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs text-dim">
            {cigars.length} · {t("cat.cigars")}
          </span>
          <div className="flex gap-1.5">
            <SortChip active={sort === "strength"} onClick={() => setSort("strength")}>
              {t("brand.byStrength")}
            </SortChip>
            <SortChip active={sort === "price"} onClick={() => setSort("price")}>
              {t("brand.byPrice")}
            </SortChip>
          </div>
        </div>

        <div className="space-y-1.5">
          {sorted.map((c) => {
            const mp = cigarPriceForMarket(c, market);
            return (
              <button
                key={c.id}
                onClick={() => onOpenCigar(c)}
                className="flex w-full items-center justify-between gap-3 rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
              >
                <div className="min-w-0">
                  <div className="truncate font-display text-sm text-papir">{c.line}</div>
                  <div className="truncate text-xs text-dim">
                    {c.wrapper} · {c.vitolas.length > 1 ? `${c.vitolas.length} ${t("common.vitolaCountSuffix")}` : c.vitola}
                  </div>
                  <div className="mt-1 flex gap-3">
                    <Meter value={c.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
                    <Meter value={c.body} label={t("common.body")} />
                  </div>
                </div>
                <span className="shrink-0 text-xs text-zlato-2">
                  {mp.price != null
                    ? `${mp.fromMany ? t("price.from") + " " : ""}${mp.price.toFixed(mp.price % 1 ? 2 : 0)} €`
                    : t("price.check")}
                </span>
              </button>
            );
          })}
        </div>

        <button
          onClick={onClose}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("common.close")}
        </button>
      </div>
    </div>
  );
}

function SortChip({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-2.5 py-1 text-[11px] ${
        active ? "border-zlato bg-zlato/15 text-zlato-2" : "border-dim/30 text-dim"
      }`}
    >
      {children}
    </button>
  );
}
