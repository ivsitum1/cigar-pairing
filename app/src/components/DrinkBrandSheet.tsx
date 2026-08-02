// Marka pića: sve boce jedne kuće, jedna pored druge.
//
// Kod cigara marka → linija → vitola postoji odavno; pića su do sada bila samo
// ravan popis po kategoriji, pa se GlenDronach 12 i 18 nikad nisu vidjeli
// zajedno. Ovdje je težište na USPOREDBI: ista tablica za sve boce, s
// istaknutim krajnostima, a klik na redak vodi u postojeći detalj boce.
import { useMemo, useState } from "react";
import type { Drink } from "../types";
import { SheetShell } from "./SheetShell";
import { BackButton } from "./BackButton";
import { FavoriteStar } from "./FavoriteStar";
import { drinkBrandStats, drinksByBrand, formatPrice } from "../data";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { bottleLabel, drinkNameLoc } from "../lib/drinkName";
import { Meter } from "./ui";

type Sort = "quality" | "price" | "body" | "sweetness" | "name";

const SORTS: Sort[] = ["quality", "price", "body", "sweetness", "name"];

const midPrice = (d: Drink): number =>
  d.priceEUR ? (d.priceEUR.min + d.priceEUR.max) / 2 : Number.MAX_SAFE_INTEGER;

export function DrinkBrandSheet({
  brand,
  onClose,
  onOpenDrink,
}: {
  brand: string;
  onClose: () => void;
  onOpenDrink: (d: Drink) => void;
}) {
  const { t, lx, cn } = useI18n();
  const [sort, setSort] = useState<Sort>("quality");

  const bottles = useMemo(() => drinksByBrand(brand), [brand]);
  const stats = useMemo(() => drinkBrandStats(brand), [brand]);

  const sorted = useMemo(() => {
    const by: Record<Sort, (a: Drink, b: Drink) => number> = {
      quality: (a, b) => (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
      price: (a, b) => midPrice(a) - midPrice(b),
      body: (a, b) => b.body - a.body,
      sweetness: (a, b) => b.sweetness - a.sweetness,
      name: (a, b) => a.name.localeCompare(b.name),
    };
    return [...bottles].sort((a, b) => by[sort](a, b) || a.name.localeCompare(b.name));
  }, [bottles, sort]);

  // Krajnosti se boje u tablici — bez njih je usporedba samo popis brojeva.
  const extremes = useMemo(() => {
    const quality = bottles.map((d) => d.qualityScore).filter((q): q is number => q != null);
    const prices = bottles.map(midPrice).filter((p) => p !== Number.MAX_SAFE_INTEGER);
    return {
      bestQuality: quality.length ? Math.max(...quality) : null,
      cheapest: prices.length ? Math.min(...prices) : null,
      bodyMin: Math.min(...bottles.map((d) => d.body)),
      bodyMax: Math.max(...bottles.map((d) => d.body)),
      sweetMin: Math.min(...bottles.map((d) => d.sweetness)),
      sweetMax: Math.max(...bottles.map((d) => d.sweetness)),
    };
  }, [bottles]);

  // Rumovi i vina u katalogu uglavnom nemaju ABV — prazan stupac samo gura
  // ocjenu i cijenu izvan ekrana na telefonu.
  const showAbv = bottles.some((d) => d.abv != null);

  const range = (min: number, max: number) => (min === max ? `${min}` : `${min}–${max}`);

  return (
    <SheetShell
      onClose={onClose}
      label={brand}
      panelClassName="max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
    >
      <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-dim/40 sm:hidden" />

      <div className="mb-3">
        <BackButton onClick={onClose}>{t("common.back")}</BackButton>
      </div>

      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="font-display text-2xl tracking-wide text-zlato-2">{brand}</div>
          <div className="mt-0.5 text-xs uppercase tracking-widest text-dim">
            {stats.categories.map((c) => t(`cat.${c}` as StringKey)).join(" · ")}
            {stats.countries.length > 0 && ` · ${stats.countries.map(cn).join(", ")}`}
          </div>
        </div>
        <FavoriteStar kind="drink" brand={brand} size="lg" />
      </div>

      <div className="mt-2 text-xs text-dim">
        {stats.count} {t("dbrand.bottles")}
        {stats.minPriceEUR != null && ` · ${t("brand.from")} ${stats.minPriceEUR.toFixed(0)} €`}
        {stats.bestQuality != null && ` · ${stats.bestQuality}/10 ${t("dbrand.best")}`}
      </div>

      <div className="band-rule my-4" />

      {bottles.length < 2 ? (
        <p className="mb-3 rounded-lg border border-dim/20 bg-cedar/50 px-3 py-2 text-xs leading-relaxed text-dim">
          {t("dbrand.single")}
        </p>
      ) : (
        <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-micro uppercase tracking-widest text-dim">
          <span className="text-zlato/70">{t("dbrand.spread")}</span>
          <span>
            {t("common.body")} {range(extremes.bodyMin, extremes.bodyMax)}
          </span>
          <span>
            {t("common.sweetness")} {range(extremes.sweetMin, extremes.sweetMax)}
          </span>
        </div>
      )}

      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs text-dim">{t("dbrand.compare")}</span>
        <div className="flex flex-wrap gap-1.5">
          {SORTS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSort(s)}
              className={`rounded-full border px-2.5 py-1 text-micro ${
                sort === s ? "border-zlato bg-zlato/15 text-zlato-2" : "border-dim/30 text-dim"
              }`}
            >
              {t(`sort.${s}` as StringKey)}
            </button>
          ))}
        </div>
      </div>

      <div className="-mx-1 overflow-x-auto px-1">
        <table className="w-full min-w-[20rem] border-collapse text-left text-xs">
          <thead>
            <tr className="text-micro uppercase tracking-widest text-dim">
              <th scope="col" className="py-1.5 pr-2 font-normal">
                {t("dbrand.colName")}
              </th>
              {showAbv && (
                <th scope="col" className="py-1.5 pr-2 text-right font-normal">
                  {t("dbrand.colAbv")}
                </th>
              )}
              <th scope="col" className="py-1.5 pr-2 font-normal">
                {t("dbrand.colBody")}
              </th>
              <th scope="col" className="py-1.5 pr-2 font-normal">
                {t("dbrand.colSweet")}
              </th>
              <th scope="col" className="py-1.5 pr-2 text-right font-normal">
                {t("dbrand.colQuality")}
              </th>
              <th scope="col" className="py-1.5 text-right font-normal">
                {t("dbrand.colPrice")}
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((d) => {
              const style = STYLE_LABELS[d.style];
              const isBest =
                extremes.bestQuality != null && d.qualityScore === extremes.bestQuality;
              const isCheapest =
                extremes.cheapest != null && midPrice(d) === extremes.cheapest;
              return (
                <tr
                  key={d.id}
                  onClick={() => onOpenDrink(d)}
                  className="cursor-pointer border-t border-dim/15 align-middle hover:bg-zlato/10"
                >
                  <th scope="row" className="py-2 pr-2 font-normal">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenDrink(d);
                      }}
                      className="block w-full text-left font-display text-sm leading-tight text-papir hover:text-zlato-2"
                    >
                      {bottleLabel(lx(drinkNameLoc(d)), brand)}
                    </button>
                    <span className="block text-micro text-dim">
                      {style ? lx(style) : d.style}
                    </span>
                  </th>
                  {showAbv && (
                    <td className="py-2 pr-2 text-right tabular-nums text-dim">
                      {d.abv != null ? `${d.abv}%` : "—"}
                    </td>
                  )}
                  {/* Meter bez natpisa — stupac ga već imenuje, a natpis u
                      svakoj ćeliji izgura ocjenu i cijenu izvan ekrana. */}
                  <td className="py-2 pr-2">
                    <Meter value={d.body} />
                  </td>
                  <td className="py-2 pr-2">
                    <Meter value={d.sweetness} accent="var(--color-lista)" />
                  </td>
                  <td
                    className={`whitespace-nowrap py-2 pr-2 text-right tabular-nums ${
                      isBest ? "text-zlato-2" : "text-dim"
                    }`}
                  >
                    {d.qualityScore != null ? `${d.qualityScore}/10` : "—"}
                  </td>
                  <td
                    className={`whitespace-nowrap py-2 text-right tabular-nums ${
                      isCheapest ? "text-zlato-2" : "text-dim"
                    }`}
                  >
                    {formatPrice(d.priceEUR)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-2 text-micro text-dim/80">{t("dbrand.openBottle")}</p>

      <button
        type="button"
        onClick={onClose}
        className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
      >
        {t("common.close")}
      </button>
    </SheetShell>
  );
}
