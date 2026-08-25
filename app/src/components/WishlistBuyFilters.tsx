import { useState } from "react";
import type { StringKey } from "../i18n";
import { useI18n } from "../i18n";
import type {
  BuyFilters,
  BuySort,
  OptionCount,
} from "../lib/shoppingFilters";
import { EMPTY_BUY_FILTERS, hasActiveBuyFilters } from "../lib/shoppingFilters";
import type { ShapeFamily } from "../lib/vitolaShape";
import { Chip } from "./ui";

type ShopGroup = { shop: string; count: number };

function FilterScrollRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="min-w-0">
      <div className="mb-1 text-micro uppercase tracking-widest text-dim">{label}</div>
      <div className="no-scrollbar flex items-center gap-1.5 overflow-x-auto pb-0.5">
        {children}
      </div>
    </div>
  );
}

function CountChip({
  label,
  count,
  active,
  onClick,
}: {
  label: string;
  count?: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <Chip active={active} onClick={onClick}>
      {label}
      {count != null && (
        <span className="ml-1.5 tabular-nums text-dim/70">{count}</span>
      )}
    </Chip>
  );
}

export function WishlistBuyFilters({
  filters,
  sort,
  onFiltersChange,
  onSortChange,
  wishlistShops,
  shapes,
  strengths,
  countries,
  hasCigars,
  hasDrinks,
  visibleCount,
}: {
  filters: BuyFilters;
  sort: BuySort;
  onFiltersChange: (filters: BuyFilters) => void;
  onSortChange: (sort: BuySort) => void;
  wishlistShops: ShopGroup[];
  shapes: OptionCount<ShapeFamily>[];
  strengths: OptionCount<number>[];
  countries: OptionCount<string>[];
  hasCigars: boolean;
  hasDrinks: boolean;
  visibleCount: number;
}) {
  const { t, cn } = useI18n();
  const filtersActive = hasActiveBuyFilters(filters);
  const [expanded, setExpanded] = useState(filtersActive);

  const toggleShop = (shop: string) =>
    onFiltersChange({ ...filters, shop: filters.shop === shop ? null : shop });
  const toggleShape = (shape: ShapeFamily) =>
    onFiltersChange({
      ...filters,
      shape: filters.shape === shape ? null : shape,
    });
  const toggleStrength = (strength: number) =>
    onFiltersChange({
      ...filters,
      strength: filters.strength === strength ? null : strength,
    });
  const toggleCountry = (country: string) =>
    onFiltersChange({
      ...filters,
      country: filters.country === country ? null : country,
    });

  const showCigarFilters = filters.kind !== "drink";
  const hasDetailFilters =
    wishlistShops.length > 1 ||
    (showCigarFilters && shapes.length > 1) ||
    (showCigarFilters && strengths.length > 1) ||
    (showCigarFilters && countries.length > 1);

  const activeSummary: { key: string; label: string; clear: () => void }[] = [];
  if (filters.kind !== "all") {
    activeSummary.push({
      key: "kind",
      label:
        filters.kind === "cigar" ? t("cat.cigars") : t("shop.filterDrinks"),
      clear: () => onFiltersChange({ ...filters, kind: "all" }),
    });
  }
  if (filters.shop != null) {
    activeSummary.push({
      key: "shop",
      label: filters.shop,
      clear: () => onFiltersChange({ ...filters, shop: null }),
    });
  }
  if (filters.shape != null) {
    activeSummary.push({
      key: "shape",
      label: t(`shape.${filters.shape}` as StringKey),
      clear: () => onFiltersChange({ ...filters, shape: null }),
    });
  }
  if (filters.strength != null) {
    activeSummary.push({
      key: "strength",
      label: `${t("filter.strength")} ${filters.strength}`,
      clear: () => onFiltersChange({ ...filters, strength: null }),
    });
  }
  if (filters.country != null) {
    activeSummary.push({
      key: "country",
      label: cn(filters.country),
      clear: () => onFiltersChange({ ...filters, country: null }),
    });
  }

  return (
    <div className="rounded-xl border border-dim/15 bg-cedar/70">
      {/* primarni red: vrsta + poredak — uvijek vidljiv, jedan red */}
      <div className="flex items-center justify-between gap-2 px-3 py-2">
        <div className="no-scrollbar flex min-w-0 items-center gap-1.5 overflow-x-auto">
          {hasCigars && hasDrinks && (
            <>
              <CountChip
                label={t("shop.filterAll")}
                active={filters.kind === "all"}
                onClick={() => onFiltersChange({ ...filters, kind: "all" })}
              />
              <CountChip
                label={t("cat.cigars")}
                active={filters.kind === "cigar"}
                onClick={() =>
                  onFiltersChange({
                    ...filters,
                    kind: filters.kind === "cigar" ? "all" : "cigar",
                  })
                }
              />
              <CountChip
                label={t("shop.filterDrinks")}
                active={filters.kind === "drink"}
                onClick={() =>
                  onFiltersChange({
                    ...filters,
                    kind: filters.kind === "drink" ? "all" : "drink",
                    shape: filters.kind === "drink" ? filters.shape : null,
                    strength:
                      filters.kind === "drink" ? filters.strength : null,
                    country: filters.kind === "drink" ? filters.country : null,
                  })
                }
              />
            </>
          )}
        </div>
        <div className="no-scrollbar flex shrink-0 items-center gap-1 overflow-x-auto">
          {(
            [
              ["name", t("shop.sortName")],
              ["priceAsc", t("shop.sortPriceAsc")],
              ["priceDesc", t("shop.sortPriceDesc")],
            ] as [BuySort, string][]
          ).map(([key, label]) => (
            <Chip
              key={key}
              active={sort === key}
              onClick={() => onSortChange(key)}
            >
              {label}
            </Chip>
          ))}
        </div>
      </div>

      {/* red za sužavanje + broj stavke */}
      {hasDetailFilters && (
        <div className="flex items-center justify-between gap-2 border-t border-dim/10 px-3 py-1.5">
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="font-display text-micro uppercase tracking-widest text-zlato hover:text-zlato-2"
          >
            {expanded ? "▴ " : "▾ "}
            {expanded ? t("shop.filterHide") : t("shop.filterShow")}
            {filtersActive && !expanded && (
              <span className="ml-1.5 text-dim">
                ({activeSummary.length})
              </span>
            )}
          </button>
          <span className="shrink-0 text-xs tabular-nums text-dim">
            {visibleCount} {t("shop.filterItems")}
          </span>
        </div>
      )}

      {/* aktivni filteri kad je panel zatvoren */}
      {!expanded && activeSummary.length > 0 && (
        <div className="flex flex-wrap gap-1.5 border-t border-dim/10 px-3 py-2">
          {activeSummary.map((item) => (
            <Chip key={item.key} active onClick={item.clear}>
              {item.label} ✕
            </Chip>
          ))}
          <Chip onClick={() => onFiltersChange(EMPTY_BUY_FILTERS)}>
            ✕ {t("shop.filterReset")}
          </Chip>
        </div>
      )}

      {/* detaljni filteri — horizontalni redovi, ne hrpa chipova */}
      {expanded && hasDetailFilters && (
        <div className="space-y-2 border-t border-dim/10 px-3 py-2.5">
          {wishlistShops.length > 1 && (
            <FilterScrollRow label={t("shop.filterShop")}>
              {wishlistShops.map((g) => (
                <CountChip
                  key={g.shop}
                  label={g.shop}
                  count={g.count}
                  active={filters.shop === g.shop}
                  onClick={() => toggleShop(g.shop)}
                />
              ))}
            </FilterScrollRow>
          )}

          {showCigarFilters && shapes.length > 1 && (
            <FilterScrollRow label={t("filter.shape")}>
              {shapes.map((g) => (
                <CountChip
                  key={g.value}
                  label={t(`shape.${g.value}` as StringKey)}
                  count={g.count}
                  active={filters.shape === g.value}
                  onClick={() => toggleShape(g.value)}
                />
              ))}
            </FilterScrollRow>
          )}

          {showCigarFilters && strengths.length > 1 && (
            <FilterScrollRow label={t("filter.strength")}>
              {strengths.map((g) => (
                <CountChip
                  key={g.value}
                  label={String(g.value)}
                  count={g.count}
                  active={filters.strength === g.value}
                  onClick={() => toggleStrength(g.value)}
                />
              ))}
            </FilterScrollRow>
          )}

          {showCigarFilters && countries.length > 1 && (
            <FilterScrollRow label={t("filter.country")}>
              {countries.map((g) => (
                <CountChip
                  key={g.value}
                  label={cn(g.value)}
                  count={g.count}
                  active={filters.country === g.value}
                  onClick={() => toggleCountry(g.value)}
                />
              ))}
            </FilterScrollRow>
          )}

          {filtersActive && (
            <div className="pt-0.5">
              <Chip onClick={() => onFiltersChange(EMPTY_BUY_FILTERS)}>
                ✕ {t("shop.filterReset")}
              </Chip>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
