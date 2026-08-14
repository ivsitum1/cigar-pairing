import { useEffect, useMemo, useRef, useState } from "react";
import type { Cigar, Drink, DrinkCategory } from "../types";
import {
  ALL_DRINKS,
  DRINKS,
  SHOPPING,
  brandDisplayName,
  cigarForItemId,
  formatPrice,
} from "../data";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import {
  CigarBrowseSheets,
  useCigarBrowseSheets,
} from "../components/useCigarBrowseSheets";
import { EveningSessionSheet } from "../components/EveningSessionSheet";
import { getItemState, useCollection } from "../store/collection";
import { totalStock, lineTotalStock, useHumidors } from "../store/humidor";
import { useMarket } from "../store/market";
import { isRestockItem, isShoppingWishlistItem } from "../lib/shoppingWishlist";
import {
  cigarItemId,
  dedupeCollectionCigarIds,
  parseCigarItemId,
} from "../lib/cigarItemId";
import { drinkNameLoc } from "../lib/drinkName";
import { vitolaFamily, vitolaFamilyLabel, type VitolaFamily } from "../lib/vitolaFamily";
import {
  EMPTY_BUY_FILTERS,
  type BuyFilterable,
  buyTotal,
  familyCounts,
  filterBuyEntries,
  hasActiveBuyFilters,
  sortBuyEntries,
  type BuyFilters,
  type BuySort,
} from "../lib/shoppingFilters";
import {
  buffetFive,
  buffetTotal,
  collectionGaps,
  groupWishlistByShop,
  groupWishlistDrinksByCategory,
  segmentPicks,
  wishlistShopKey,
  wishlistTextSections,
} from "../lib/shoppingPicks";

const CATEGORIES: DrinkCategory[] = [
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
  "digestif",
];

/**
 * Redak Kupovine — cigara (ključ nosi vitolu) ili boca, u obliku koji filteri
 * i sortiranje razumiju bez granjanja po vrsti.
 */
type BuyEntry = BuyFilterable & {
  key: string;
  /** true = imaš je, ali je zaliha 0 → ide u „Dopuna zalihe”, ne u želje. */
  restock: boolean;
  /** Ime trgovine kako stoji u podacima (za dijeljenje popisa). */
  shopRaw?: string | null;
} & ({ kind: "cigar"; cigar: Cigar } | { kind: "drink"; drink: Drink });

export function ShoppingPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx, lang } = useI18n();
  const market = useMarket();
  const collection = useCollection(); // re-render na promjene kolekcije/liste zelja
  const { stock: humidors } = useHumidors(); // zaliha odlucuje sto je „dopuna"
  const {
    line,
    detail,
    openCigar,
    openVitola,
    openDrink,
    openLine,
    closeLine,
    closeDetail,
    closeSheets,
  } = useCigarBrowseSheets();
  const [logCigar, setLogCigar] = useState<Cigar | null>(null);
  const [buffetCat, setBuffetCat] = useState<DrinkCategory>("rum");
  const [showPlan, setShowPlan] = useState(false);
  const [copied, setCopied] = useState(false);
  const [filters, setFilters] = useState<BuyFilters>(EMPTY_BUY_FILTERS);
  const [sort, setSort] = useState<BuySort>("name");
  const shopFilterRef = useRef<HTMLDivElement>(null);
  const shopFilterScrollSkip = useRef(true);

  const isOwned = (id: string) => getItemState(id).owned;
  // ☆ uz preporuku = vec je na tvojoj listi zelja (liste su neovisne)
  const wishMark = (id: string) => (getItemState(id).wishlist ? "☆ " : "");
  const otherShopsLabel = t("shop.otherShops");

  /**
   * Sve što ide na Kupovinu, u jednom obliku — cigara po VITOLI (ključ nosi
   * odabranu veličinu, kao humidor i dnevnik) i boca po id-u. `restock` dijeli
   * popis na dvoje: „želim kupiti” i „imam je, ali je nema u humidoru”.
   */
  const buyEntries = useMemo<BuyEntry[]>(() => {
    const cigarKeys = Object.keys(collection.items).filter((id) => {
      if (cigarForItemId(id) == null) return false;
      const { cigarId, vitolaSlug } = parseCigarItemId(id);
      // goli ključ linije pokriva sve njezine vitole
      const stock = vitolaSlug ? totalStock(id) : lineTotalStock(cigarId);
      return isShoppingWishlistItem(getItemState(id), stock);
    });

    const cigars: BuyEntry[] = dedupeCollectionCigarIds(cigarKeys).flatMap((key) => {
      const cigar = cigarForItemId(key);
      if (!cigar) return [];
      const { cigarId, vitolaSlug } = parseCigarItemId(key);
      const stock = vitolaSlug ? totalStock(key) : lineTotalStock(cigarId);
      const vitola = cigar.selectedVitola ?? cigar.vitola;
      return [
        {
          kind: "cigar",
          key,
          cigar,
          name: `${brandDisplayName(cigar.brand, market)} ${cigar.line}`,
          price: cigar.priceEUR,
          shopKey: wishlistShopKey(cigar.availabilityHR?.[0], otherShopsLabel),
          shopRaw: cigar.availabilityHR?.[0],
          family: vitolaFamily(vitola),
          restock: isRestockItem(getItemState(key), stock),
        },
      ];
    });

    const drinks: BuyEntry[] = ALL_DRINKS.filter((d) =>
      isShoppingWishlistItem(getItemState(d.id), totalStock(d.id)),
    ).map((d) => ({
      kind: "drink",
      key: d.id,
      drink: d,
      name: lx(drinkNameLoc(d)),
      price: d.priceEUR?.min ?? null,
      shopKey: wishlistShopKey(d.shopHR, otherShopsLabel),
      shopRaw: d.shopHR,
      family: null,
      restock: isRestockItem(getItemState(d.id), totalStock(d.id)),
    }));

    return [...cigars, ...drinks];
    // getItemState/totalStock citaju modul-cache; ovisnosti su store snapshoti
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collection, humidors, market, otherShopsLabel, lx]);

  // pillovi uvijek iz pune liste (brojevi se ne mijenjaju dok filtriraš)
  const wishlistShops = groupWishlistByShop(
    buyEntries.map((e) => ({ shop: e.shopKey, price: e.price })),
    otherShopsLabel,
  );
  const vitolaFamilies = familyCounts(buyEntries);
  const hasCigars = buyEntries.some((e) => e.kind === "cigar");
  const hasDrinks = buyEntries.some((e) => e.kind === "drink");

  const visible = sortBuyEntries(filterBuyEntries(buyEntries, filters), sort);
  const wishVisible = visible.filter((e) => !e.restock);
  const restockVisible = visible.filter((e) => e.restock);

  const cigarsOf = (list: BuyEntry[]) =>
    list.filter((e): e is BuyEntry & { kind: "cigar"; cigar: Cigar } => e.kind === "cigar");
  const drinksOf = (list: BuyEntry[]) =>
    list
      .filter((e): e is BuyEntry & { kind: "drink"; drink: Drink } => e.kind === "drink")
      .map((e) => e.drink);

  const wishlistDrinkGroups = groupWishlistDrinksByCategory(
    drinksOf(wishVisible),
    CATEGORIES,
  );
  const wishlistTotal = buyTotal(wishVisible);
  const restockTotal = buyTotal(restockVisible);
  const filtersActive = hasActiveBuyFilters(filters);

  // nakon filtera lista ispod se skraćuje — chipovi ostanu u središtu viewporta
  useEffect(() => {
    if (shopFilterScrollSkip.current) {
      shopFilterScrollSkip.current = false;
      return;
    }
    const el = shopFilterRef.current;
    if (!el) return;
    const id = requestAnimationFrame(() => {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    return () => cancelAnimationFrame(id);
  }, [filters]);

  const toggleShop = (shop: string) =>
    setFilters((f) => ({ ...f, shop: f.shop === shop ? null : shop }));
  const toggleFamily = (family: VitolaFamily) =>
    setFilters((f) => ({ ...f, family: f.family === family ? null : family }));

  const shareWishlist = async () => {
    const shareItems = (list: BuyEntry[]) =>
      list.map((e) => ({
        name: e.kind === "cigar" && e.cigar.selectedVitola
          ? `${e.name} — ${e.cigar.selectedVitola}`
          : e.name,
        price: e.price,
        shop: e.shopRaw ?? undefined,
      }));
    const text = wishlistTextSections(
      [
        {
          title: t("cat.cigars"),
          items: shareItems(cigarsOf(wishVisible)),
        },
        ...wishlistDrinkGroups.map(({ category, drinks }) => ({
          title: t(`cat.${category}` as StringKey),
          items: drinks.map((d) => ({
            name: d.name,
            price: d.priceEUR?.min ?? null,
            shop: d.shopHR,
          })),
        })),
        // dopuna zalihe ide u isti popis, ali pod svojim naslovom
        { title: t("shop.restockTitle"), items: shareItems(restockVisible) },
      ],
      t("shop.total"),
    );
    try {
      if (navigator.share) {
        await navigator.share({ title: t("coll.wishlist"), text });
        return;
      }
    } catch {
      // korisnik odustao od share — probaj clipboard
    }
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // clipboard nedostupan (http) — nista
    }
  };

  // rupe u kolekciji — zivi plan: segmenti bez ijedne boce + preporuka
  const gaps = useMemo(
    () =>
      CATEGORIES.map((cat) => ({
        cat,
        missing: collectionGaps(cat, DRINKS[cat], isOwned),
      })).filter((g) => g.missing.length > 0),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [collection],
  );
  const totalBuckets = CATEGORIES.length * 5;
  const coveredBuckets = totalBuckets - gaps.reduce((s, g) => s + g.missing.length, 0);

  // preporuke po segmentu (vrh / omjer / pristupacno) po kategoriji
  const segments = useMemo(
    () =>
      CATEGORIES.map((cat) => ({
        cat,
        picks: segmentPicks(DRINKS[cat], isOwned),
      })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [collection],
  );

  // buffet petorka za odabranu kategoriju
  const buffet = useMemo(
    () => buffetFive(buffetCat, DRINKS[buffetCat], isOwned),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [buffetCat, collection],
  );

  const tierGroups = ["S", "A", "B", "C"].map((tier) => ({
    tier,
    rows: SHOPPING.tiers.filter((x) => x.tier === tier),
  }));

  return (
    <div className="pb-4">
      {/* ☆ 1) lista zelja + dopuna zalihe — dva popisa, ne jedan */}
      <SectionTitle>☆ {t("coll.wishlistTitle")}</SectionTitle>
      {buyEntries.length === 0 ? (
        <p className="rounded-xl border border-dim/20 bg-cedar p-4 text-sm leading-relaxed text-dim">
          {t("shop.wishlistEmpty")}
        </p>
      ) : (
        <>
          {/* filteri iznad popisa — u trgovini se prvo suzi, pa gleda */}
          <div ref={shopFilterRef} className="space-y-1.5">
            {hasCigars && hasDrinks && (
              <div className="flex flex-wrap gap-1.5">
                <Chip
                  active={filters.kind === "all"}
                  onClick={() => setFilters((f) => ({ ...f, kind: "all" }))}
                >
                  {t("shop.filterAll")}
                </Chip>
                <Chip
                  active={filters.kind === "cigar"}
                  onClick={() =>
                    setFilters((f) => ({
                      ...f,
                      kind: f.kind === "cigar" ? "all" : "cigar",
                    }))
                  }
                >
                  {t("cat.cigars")}
                </Chip>
                <Chip
                  active={filters.kind === "drink"}
                  onClick={() =>
                    setFilters((f) => ({
                      ...f,
                      kind: f.kind === "drink" ? "all" : "drink",
                      // vitola je pitanje o cigarama — uz pića nema smisla
                      family: f.kind === "drink" ? f.family : null,
                    }))
                  }
                >
                  {t("shop.filterDrinks")}
                </Chip>
              </div>
            )}

            {wishlistShops.length > 1 && (
              <div className="flex flex-wrap gap-1.5">
                <span className="self-center text-micro uppercase tracking-widest text-dim">
                  {t("shop.filterShop")}
                </span>
                {wishlistShops.map((g) => (
                  <Chip
                    key={g.shop}
                    active={filters.shop === g.shop}
                    onClick={() => toggleShop(g.shop)}
                  >
                    {g.shop}: {g.count}×{g.total > 0 ? ` · ~${g.total.toFixed(0)} €` : ""}
                  </Chip>
                ))}
              </div>
            )}

            {vitolaFamilies.length > 1 && filters.kind !== "drink" && (
              <div className="flex flex-wrap gap-1.5">
                <span className="self-center text-micro uppercase tracking-widest text-dim">
                  {t("shop.filterVitola")}
                </span>
                {vitolaFamilies.map((g) => (
                  <Chip
                    key={g.family}
                    active={filters.family === g.family}
                    onClick={() => toggleFamily(g.family)}
                  >
                    {vitolaFamilyLabel(g.family, lang)}: {g.count}×
                  </Chip>
                ))}
              </div>
            )}

            <div className="flex flex-wrap gap-1.5">
              <span className="self-center text-micro uppercase tracking-widest text-dim">
                {t("shop.sort")}
              </span>
              {(
                [
                  ["name", t("shop.sortName")],
                  ["priceAsc", t("shop.sortPriceAsc")],
                  ["priceDesc", t("shop.sortPriceDesc")],
                ] as [BuySort, string][]
              ).map(([key, label]) => (
                <Chip key={key} active={sort === key} onClick={() => setSort(key)}>
                  {label}
                </Chip>
              ))}
              {filtersActive && (
                <Chip onClick={() => setFilters(EMPTY_BUY_FILTERS)}>
                  ✕ {t("shop.filterReset")}
                </Chip>
              )}
            </div>
          </div>

          {visible.length === 0 && (
            <p className="mt-3 rounded-xl border border-dim/20 bg-cedar p-3 text-sm text-dim">
              {t("shop.filterNoHits")}
            </p>
          )}

          {wishVisible.length > 0 && (
            <div className="mt-3 space-y-4">
              {cigarsOf(wishVisible).length > 0 && (
                <div>
                  <div className="mb-1.5 font-display text-xs uppercase tracking-[0.2em] text-zlato">
                    {t("cat.cigars")}
                  </div>
                  <div className="space-y-2">
                    {cigarsOf(wishVisible).map((e) => (
                      <CigarRow
                        key={e.key}
                        cigar={e.cigar}
                        onClick={() => openCigar(e.cigar)}
                      />
                    ))}
                  </div>
                </div>
              )}
              {wishlistDrinkGroups.map(({ category, drinks }) => (
                <div key={category}>
                  <div className="mb-1.5 font-display text-xs uppercase tracking-[0.2em] text-zlato">
                    {t(`cat.${category}` as StringKey)}
                  </div>
                  <div className="space-y-2">
                    {drinks.map((d) => (
                      <DrinkRow key={d.id} drink={d} onClick={() => openDrink(d)} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-2 flex items-center justify-between gap-2">
            <Chip onClick={shareWishlist}>
              {copied ? `✓ ${t("shop.copied")}` : `⇪ ${t("shop.share")}`}
            </Chip>
            {wishlistTotal > 0 && (
              <span className="rounded-lg border border-zlato/25 bg-zlato/10 px-3 py-1.5 text-sm text-zlato-2">
                {t("shop.total")}: ~{wishlistTotal.toFixed(0)} €
              </span>
            )}
          </div>

          {/* drugi popis: imaš ih, ali ih nema u humidoru */}
          {restockVisible.length > 0 && (
            <div className="mt-4 rounded-xl border border-oxblood/30 bg-oxblood/5 p-3">
              <div className="font-display text-xs uppercase tracking-[0.2em] text-zlato">
                {t("shop.restockTitle")}
              </div>
              <p className="mt-1 text-xs leading-relaxed text-dim">
                {t("shop.restockHint")}
              </p>
              <div className="mt-2 space-y-2">
                {restockVisible.map((e) =>
                  e.kind === "cigar" ? (
                    <CigarRow
                      key={e.key}
                      cigar={e.cigar}
                      onClick={() => openCigar(e.cigar)}
                    />
                  ) : (
                    <DrinkRow key={e.key} drink={e.drink} onClick={() => openDrink(e.drink)} />
                  ),
                )}
              </div>
              {restockTotal > 0 && (
                <div className="mt-2 text-right text-sm text-zlato-2">
                  {t("shop.total")}: ~{restockTotal.toFixed(0)} €
                </div>
              )}
            </div>
          )}
        </>
      )}
      <p className="mt-2 text-xs leading-relaxed text-dim">{t("shop.wishlistNote")}</p>

      {/* 2) praznine u kolekciji — zivi plan */}
      <SectionTitle>{t("shop.gaps")}</SectionTitle>
      <p className="mb-2 text-xs leading-relaxed text-dim">
        {t("shop.gapsHint")} · {coveredBuckets}/{totalBuckets}
      </p>
      {gaps.length === 0 ? (
        <p className="rounded-xl border border-lista/40 bg-lista/10 p-3 text-sm text-papir/90">
          {t("shop.gapsDone")}
        </p>
      ) : (
        <div className="space-y-3">
          {gaps.map(({ cat, missing }) => (
            <div key={cat} className="rounded-xl border border-dim/15 bg-cedar p-3">
              <div className="mb-2 font-display text-xs uppercase tracking-[0.2em] text-zlato">
                {t(`cat.${cat}` as StringKey)}
              </div>
              <div className="space-y-1.5">
                {missing.map(({ bucket, suggestion }) => (
                  <button
                    key={bucket.id}
                    onClick={() => suggestion && openDrink(suggestion)}
                    className="flex w-full items-baseline justify-between gap-2 rounded-lg border border-dim/15 bg-humidor/60 px-2.5 py-2 text-left hover:border-zlato/40"
                  >
                    <span className="min-w-0">
                      <span className="text-micro uppercase tracking-widest text-oxblood">
                        {lx(bucket.label)}
                      </span>
                      <span className="block truncate text-sm text-papir">
                        {suggestion ? `${wishMark(suggestion.id)}${suggestion.name}` : "—"}
                      </span>
                    </span>
                    {suggestion && (
                      <span className="shrink-0 text-xs text-dim">
                        <span className="text-zlato-2">{suggestion.qualityScore}/10</span>
                        {" · "}
                        {formatPrice(suggestion.priceEUR)}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 3) preporuke po segmentu — vrh / omjer / pristupacno */}
      <SectionTitle>{t("shop.segments")}</SectionTitle>
      <div className="space-y-3">
        {segments.map(({ cat, picks }) => (
          <div key={cat} className="rounded-xl border border-dim/15 bg-cedar p-3">
            <div className="mb-2 font-display text-xs uppercase tracking-[0.2em] text-zlato">
              {t(`cat.${cat}` as StringKey)}
            </div>
            <div className="space-y-1.5">
              {(
                [
                  ["shop.pickTop", picks.top],
                  ["shop.pickValue", picks.value],
                  ["shop.pickBudget", picks.budget],
                ] as [StringKey, Drink | null][]
              ).map(
                ([key, d]) =>
                  d && (
                    <button
                      key={key}
                      onClick={() => openDrink(d)}
                      className="flex w-full items-baseline justify-between gap-2 rounded-lg border border-dim/15 bg-humidor/60 px-2.5 py-2 text-left hover:border-zlato/40"
                    >
                      <span className="min-w-0">
                        <span className="text-micro uppercase tracking-widest text-dim">
                          {t(key)}
                        </span>
                        <span className="block truncate text-sm text-papir">{wishMark(d.id)}{d.name}</span>
                      </span>
                      <span className="shrink-0 text-xs text-dim">
                        <span className="text-zlato-2">{d.qualityScore}/10</span>
                        {" · "}
                        {formatPrice(d.priceEUR)}
                      </span>
                    </button>
                  ),
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 4) buffet petorka — 5 boca za najbolji presjek kategorije */}
      <SectionTitle>{t("shop.buffet")}</SectionTitle>
      <p className="mb-2 text-xs leading-relaxed text-dim">{t("shop.buffetHint")}</p>
      <div className="no-scrollbar mb-2 flex gap-2 overflow-x-auto">
        {CATEGORIES.map((cat) => (
          <Chip key={cat} active={buffetCat === cat} onClick={() => setBuffetCat(cat)}>
            {t(`cat.${cat}` as StringKey)}
          </Chip>
        ))}
      </div>
      <div className="space-y-1.5">
        {buffet.map(({ bucket, drink }) => (
          <button
            key={bucket.id}
            onClick={() => openDrink(drink)}
            className="flex w-full items-baseline justify-between gap-2 rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
          >
            <span className="min-w-0">
              <span className="text-micro uppercase tracking-widest text-zlato">
                {lx(bucket.label)}
              </span>
              <span className="block truncate text-sm text-papir">{wishMark(drink.id)}{drink.name}</span>
              <span className="block truncate text-xs text-dim">
                {lx(STYLE_LABELS[drink.style]) || drink.style}
              </span>
            </span>
            <span className="shrink-0 text-xs text-dim">
              <span className="text-zlato-2">{drink.qualityScore}/10</span>
              {" · "}
              {formatPrice(drink.priceEUR)}
            </span>
          </button>
        ))}
      </div>
      {buffet.length > 0 && (
        <div className="mt-2 rounded-lg border border-zlato/25 bg-zlato/10 px-3 py-2 text-right text-sm text-zlato-2">
          {t("shop.total")}: ~{buffetTotal(buffet).toFixed(0)} €
        </div>
      )}

      {/* 5) moj plan (rum tierovi iz Excela) — sklopivo */}
      <SectionTitle>{t("shop.myPlan")}</SectionTitle>
      <button
        onClick={() => setShowPlan(!showPlan)}
        className="w-full rounded-lg border border-dim/25 py-2 font-display text-xs uppercase tracking-widest text-dim hover:border-zlato/40"
      >
        {showPlan ? "▴" : "▾"} {t("shop.tiers")}
      </button>
      {showPlan && (
        <div className="mt-2 space-y-4">
          {tierGroups.map(({ tier, rows }) => (
            <div key={tier}>
              <div className="mb-1.5 font-display text-sm tracking-widest text-zlato">
                {t("shop.tier")} {tier}
              </div>
              <div className="space-y-1.5">
                {rows.map((row, i) => (
                  <div
                    key={i}
                    className={`flex items-start gap-3 rounded-lg border p-2.5 ${
                      row.owned ? "border-lista/40 bg-lista/10" : "border-dim/15 bg-cedar"
                    }`}
                  >
                    <span
                      className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-xs ${
                        row.owned ? "border-lista text-lista" : "border-dim/40 text-transparent"
                      }`}
                    >
                      ✓
                    </span>
                    <div className="min-w-0">
                      <div className="text-sm text-papir">
                        <span className="text-dim">{lx(row.styleTarget)}:</span> {row.bottleTarget}
                      </div>
                      <div className="mt-0.5 text-xs text-dim">
                        {lx(row.profile)}
                        {row.priceSource && ` · ${row.priceSource}`}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* trgovine + pravna napomena */}
      <SectionTitle>{t("shop.shops")}</SectionTitle>
      <div className="grid gap-2 sm:grid-cols-2">
        {SHOPPING.shops.map((s) => (
          <div key={s.name} className="rounded-xl border border-dim/15 bg-cedar p-3">
            <div className="font-display text-base text-papir">{s.name}</div>
            <div className="text-xs text-dim">{s.location}</div>
            <div className="mt-1 text-xs leading-relaxed text-dim/90">{lx(s.note)}</div>
          </div>
        ))}
      </div>

      <p className="mt-4 text-xs leading-relaxed text-dim/80">⚖ {t("shop.legalNote")}</p>

      <CigarBrowseSheets
        line={line}
        detail={detail}
        onCloseLine={closeLine}
        onOpenVitola={openVitola}
        onCloseDetail={closeDetail}
        onOpenLine={openLine}
        onPair={
          onPair
            ? (target) => {
                closeSheets();
                onPair(target);
              }
            : undefined
        }
        onLogEvening={(cigar) => {
          closeSheets();
          setLogCigar(cigar);
        }}
      />
      {logCigar && (
        <EveningSessionSheet
          cigars={[logCigar]}
          drinks={[]}
          initialCigarId={cigarItemId(logCigar)}
          onClose={() => setLogCigar(null)}
        />
      )}
    </div>
  );
}
