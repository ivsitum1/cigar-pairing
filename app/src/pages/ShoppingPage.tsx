import { useMemo, useState } from "react";
import type { Cigar, Drink, DrinkCategory } from "../types";
import { ALL_DRINKS, CIGARS, DRINKS, SHOPPING, formatPrice } from "../data";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { DetailSheet } from "../components/DetailSheet";
import { getItemState, useCollection } from "../store/collection";
import {
  buffetFive,
  buffetTotal,
  collectionGaps,
  segmentPicks,
  wishlistText,
} from "../lib/shoppingPicks";

const CATEGORIES: DrinkCategory[] = ["rum", "whisky", "brandy", "gin", "wine"];

export function ShoppingPage() {
  const { t, lx } = useI18n();
  const collection = useCollection(); // re-render na promjene kolekcije/liste zelja
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const [buffetCat, setBuffetCat] = useState<DrinkCategory>("rum");
  const [showPlan, setShowPlan] = useState(false);
  const [copied, setCopied] = useState(false);

  const isOwned = (id: string) => getItemState(id).owned;

  // ☆ lista zelja — pice + cigare, s ukupnim troskom
  const wishlistDrinks = ALL_DRINKS.filter((d) => {
    const s = getItemState(d.id);
    return s.wishlist && !s.owned;
  });
  const wishlistCigars = CIGARS.filter((c) => {
    const s = getItemState(c.id);
    return s.wishlist && !s.owned;
  });
  const wishlistTotal =
    wishlistDrinks.reduce((s, d) => s + (d.priceEUR?.min ?? 0), 0) +
    wishlistCigars.reduce((s, c) => s + (c.priceEUR ?? 0), 0);

  const shareWishlist = async () => {
    const text = wishlistText([
      ...wishlistCigars.map((c) => ({
        name: `${c.brand} ${c.line}`,
        price: c.priceEUR,
        shop: c.availabilityHR?.[0],
      })),
      ...wishlistDrinks.map((d) => ({
        name: d.name,
        price: d.priceEUR?.min ?? null,
        shop: d.shopHR,
      })),
    ]);
    try {
      if (navigator.share) {
        await navigator.share({ title: "Lista želja", text });
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

  const openDrink = (d: Drink) => setDetail({ kind: "drink", item: d });

  return (
    <div className="pb-4">
      {/* ☆ 1) lista zelja */}
      <SectionTitle>☆ {t("coll.wishlistTitle")}</SectionTitle>
      {wishlistDrinks.length === 0 && wishlistCigars.length === 0 ? (
        <p className="rounded-xl border border-dim/20 bg-cedar p-4 text-sm leading-relaxed text-dim">
          {t("shop.wishlistEmpty")}
        </p>
      ) : (
        <>
          <div className="space-y-2">
            {wishlistCigars.map((c) => (
              <CigarRow key={c.id} cigar={c} onClick={() => setDetail({ kind: "cigar", item: c })} />
            ))}
            {wishlistDrinks.map((d) => (
              <DrinkRow key={d.id} drink={d} onClick={() => openDrink(d)} />
            ))}
          </div>
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
        </>
      )}

      {/* 2) rupe u kolekciji — zivi plan */}
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
                      <span className="text-[10px] uppercase tracking-widest text-oxblood">
                        {lx(bucket.label)}
                      </span>
                      <span className="block truncate text-sm text-papir">
                        {suggestion ? suggestion.name : "—"}
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
                        <span className="text-[10px] uppercase tracking-widest text-dim">
                          {t(key)}
                        </span>
                        <span className="block truncate text-sm text-papir">{d.name}</span>
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
              <span className="text-[10px] uppercase tracking-widest text-zlato">
                {lx(bucket.label)}
              </span>
              <span className="block truncate text-sm text-papir">{drink.name}</span>
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
                TIER {tier}
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
                        <span className="text-dim">{row.styleTarget}:</span> {row.bottleTarget}
                      </div>
                      <div className="mt-0.5 text-xs text-dim">
                        {row.profile}
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
            <div className="font-display text-[15px] text-papir">{s.name}</div>
            <div className="text-xs text-dim">{s.location}</div>
            <div className="mt-1 text-xs leading-relaxed text-dim/90">{lx(s.note)}</div>
          </div>
        ))}
      </div>

      <p className="mt-4 text-xs leading-relaxed text-dim/80">⚖ {t("shop.legalNote")}</p>

      <DetailSheet target={detail} onClose={() => setDetail(null)} />
    </div>
  );
}
