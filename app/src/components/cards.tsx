import type { Cigar, Drink } from "../types";
import { useI18n, STYLE_LABELS, ADDITIVE_LABELS } from "../i18n";
import { cigarPriceForMarket, formatPrice } from "../data";
import { Meter } from "./ui";
import { getItemState, useCollection } from "../store/collection";
import { useMarket } from "../store/market";

// Cijena cigare koja odgovara odabranom tržištu (HR = konkretna, ostalo = "provjeri")
export function CigarPrice({ cigar }: { cigar: Cigar }) {
  const { t } = useI18n();
  const market = useMarket();
  const { price, fromMany } = cigarPriceForMarket(cigar, market);
  if (price == null) {
    return <span className="text-dim/70">{t("price.check")}</span>;
  }
  return (
    <span>
      {fromMany ? `${t("price.from")} ` : ""}
      {price.toFixed(price % 1 ? 2 : 0)} €
    </span>
  );
}

function OwnedDot({ id }: { id: string }) {
  const { t } = useI18n();
  useCollection();
  const s = getItemState(id);
  if (!s.owned && !s.tried) return null;
  return (
    <span
      className="ml-1 inline-block h-2 w-2 rounded-full"
      style={{ background: s.owned ? "var(--color-lista)" : "var(--color-dim)" }}
      title={s.owned ? t("coll.inCollection") : t("coll.triedTitle")}
    />
  );
}

export function CigarRow({
  cigar,
  onClick,
}: {
  cigar: Cigar;
  onClick?: () => void;
}) {
  const { t, lx, cn } = useI18n();
  return (
    <button
      onClick={onClick}
      className="w-full rounded-xl border border-dim/15 bg-cedar p-3 text-left transition-colors hover:border-zlato/40"
    >
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-display text-[15px] text-papir">
          {cigar.brand} <span className="text-zlato-2">{cigar.line}</span>
          <OwnedDot id={cigar.id} />
        </span>
        <span className="shrink-0 text-xs text-dim">
          <CigarPrice cigar={cigar} />
        </span>
      </div>
      <div className="mt-1 text-xs text-dim">
        {cigar.vitola} · {cigar.wrapper} · {cn(cigar.country)} ·{" "}
        {cigar.smokeTimeMin} {t("common.minutes")}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
        <Meter value={cigar.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
        <Meter value={cigar.body} label={t("common.body")} />
      </div>
      <div className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-dim/90">
        {lx(cigar.notes)}
      </div>
    </button>
  );
}

export function DrinkRow({
  drink,
  rank,
  onClick,
}: {
  drink: Drink;
  rank?: number;
  onClick?: () => void;
}) {
  const { t, lx } = useI18n();
  const style = STYLE_LABELS[drink.style];
  return (
    <button
      onClick={onClick}
      className="w-full rounded-xl border border-dim/15 bg-cedar p-3 text-left transition-colors hover:border-zlato/40"
    >
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-display text-[15px] text-papir">
          {rank != null && <span className="mr-1.5 text-xs text-dim">#{rank}</span>}
          {drink.name}
          <OwnedDot id={drink.id} />
        </span>
        <span className="shrink-0 text-xs text-dim">
          {formatPrice(drink.priceEUR)}
        </span>
      </div>
      <div className="mt-1 text-xs text-dim">
        {style ? lx(style) : drink.style}
        {drink.qualityScore != null && (
          <span className="text-zlato-2"> · {drink.qualityScore}/10</span>
        )}
        {drink.additiveStatus && drink.category === "rum" && (
          <span> · {lx(ADDITIVE_LABELS[drink.additiveStatus])}</span>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
        <Meter value={drink.body} label={t("common.body")} />
        <Meter
          value={drink.sweetness}
          label={t("common.sweetness")}
          accent="var(--color-lista)"
        />
      </div>
      {lx(drink.notes) && (
        <div className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-dim/90">
          {lx(drink.notes)}
        </div>
      )}
    </button>
  );
}
