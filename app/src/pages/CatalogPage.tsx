import { useEffect, useMemo, useState } from "react";
import type { Cigar, Drink, DrinkCategory, Vitola } from "../types";
import {
  CIGARS,
  DRINKS,
  ALL_BRANDS,
  BRAND_CATALOG,
  brandFromSlug,
  brandSlug,
  cigarsByBrand,
  cigarInRegion,
  cigarCountByRegion,
  resolveCigarId,
  vitolaSlug,
} from "../data";
import { SHOPS, REGIONS } from "../data/shops";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, SearchInput } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { DetailSheet } from "../components/DetailSheet";
import { BrandSheet } from "../components/BrandSheet";
import { LineSheet } from "../components/LineSheet";
import { MarketFilter } from "../components/MarketFilter";
import { VitolaPicker } from "../components/VitolaPicker";
import { applyVitola, uniqueVitolas } from "../lib/cigarVitola";
import {
  SHAPE_FAMILIES,
  cigarShapes,
  firstVitolaOfShape,
  type ShapeFamily,
} from "../lib/vitolaShape";
import { useMarket, setMarket } from "../store/market";
import { navigate, useRoute } from "../store/route";

const norm = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

// Prvi znak imena kao slovo indeksa (A–Z); sve ostalo (brojevi, simboli) → "#".
const letterFor = (s: string) => {
  const c = norm(s).charAt(0);
  return c >= "a" && c <= "z" ? c.toUpperCase() : "#";
};

const RAIL = ["#", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")];

type CatalogSearchHit =
  | { kind: "brand"; brand: string }
  | { kind: "line"; cigar: Cigar }
  | { kind: "vitola"; cigar: Cigar; vitola: Vitola };

// Bočna A–Z traka za brzo skakanje po brendovima (tipa iOS kontakti):
// klik na slovo skoči na prvi brend s tim početnim slovom.
function AlphabetRail({
  letters,
  onJump,
}: {
  letters: Set<string>;
  onJump: (l: string) => void;
}) {
  return (
    <div className="fixed right-0 top-1/2 z-30 -translate-y-1/2 select-none">
      <div className="flex flex-col items-center rounded-l-lg border-y border-l border-zlato/20 bg-humidor/85 px-1 py-1.5 backdrop-blur">
        {RAIL.map((l) => {
          const has = letters.has(l);
          return (
            <button
              key={l}
              disabled={!has}
              onClick={() => onJump(l)}
              aria-label={`Skoči na ${l}`}
              className={`flex h-[15px] w-4 items-center justify-center font-display text-[9px] leading-none ${
                has ? "text-zlato active:text-zlato-2" : "text-dim/25"
              }`}
            >
              {l}
            </button>
          );
        })}
      </div>
    </div>
  );
}

type Tab = "cigars" | DrinkCategory;
const TABS: Tab[] = [
  "cigars",
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
];
export function CatalogPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx, cn } = useI18n();
  const route = useRoute();
  const [tab, setTab] = useState<Tab>("cigars");
  const [query, setQuery] = useState("");
  const [styleFilter, setStyleFilter] = useState<string | null>(null);
  const [strengthFilter, setStrengthFilter] = useState<number | null>(null);
  const [shapeFilter, setShapeFilter] = useState<ShapeFamily | null>(null);
  const [cleanOnly, setCleanOnly] = useState(false);
  // cigare se otvaraju na indeksu brendova; puni popis linija je iza "Brendovi" gumba
  const [browseBrands, setBrowseBrands] = useState(true);
  const [limit, setLimit] = useState(120);
  const [showShops, setShowShops] = useState(false);
  const [sortBy, setSortBy] = useState<"quality" | "price" | "body" | "sweetness" | "strength" | "name">("quality");
  const market = useMarket();
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const [pendingCigar, setPendingCigar] = useState<Cigar | null>(null);
  const [brand, setBrand] = useState<string | null>(null);
  const [line, setLine] = useState<Cigar | null>(null);

  const openBrand = (b: string) => {
    setDetail(null);
    setLine(null);
    setPendingCigar(null);
    setBrand(b);
    navigate({ page: "catalog", catalog: { level: "brand", brandSlug: brandSlug(b) } });
  };

  const openLine = (c: Cigar) => {
    const full = resolveCigarId(c.id) ?? c;
    setDetail(null);
    setPendingCigar(null);
    setBrand(null);
    setLine(full);
    navigate({ page: "catalog", catalog: { level: "line", cigarId: full.id } });
  };

  const openVitola = (c: Cigar, v: Vitola) => {
    const full = resolveCigarId(c.id) ?? c;
    setBrand(null);
    setLine(null);
    setPendingCigar(null);
    setDetail({ kind: "cigar", item: applyVitola(full, v) });
    navigate({
      page: "catalog",
      catalog: { level: "vitola", cigarId: full.id, vitolaSlug: vitolaSlug(v) },
    });
  };

  const clearCatalogFocus = () => {
    setBrand(null);
    setLine(null);
    setDetail(null);
    setPendingCigar(null);
    navigate({ page: "catalog" });
  };

  // Sync sheets from deep-link hash
  useEffect(() => {
    if (route.page !== "catalog") return;
    const focus = route.catalog;
    if (!focus) return;
    if (focus.level === "brand") {
      const b = brandFromSlug(focus.brandSlug);
      if (b) {
        setLine(null);
        setDetail(null);
        setPendingCigar(null);
        setBrand(b);
      }
      return;
    }
    const cigar = resolveCigarId(focus.cigarId);
    if (!cigar) return;
    if (focus.level === "line") {
      setBrand(null);
      setDetail(null);
      setPendingCigar(null);
      setLine(cigar);
      return;
    }
    const v = uniqueVitolas(cigar).find((x) => vitolaSlug(x) === focus.vitolaSlug);
    if (!v) return;
    setBrand(null);
    setLine(null);
    setPendingCigar(null);
    setDetail({ kind: "cigar", item: applyVitola(cigar, v) });
  }, [route.page, route.catalog]);

  // Trostruki search hitovi (brand / line / vitola) kad je upit ≥ 2 znaka
  const searchHits = useMemo((): CatalogSearchHit[] => {
    const nq = norm(query.trim());
    if (tab !== "cigars" || nq.length < 2) return [];
    const hits: CatalogSearchHit[] = [];
    const seenBrand = new Set<string>();
    const seenLine = new Set<string>();
    const seenVitola = new Set<string>();

    for (const b of ALL_BRANDS) {
      if (!norm(b).includes(nq) || seenBrand.has(b)) continue;
      seenBrand.add(b);
      hits.push({ kind: "brand", brand: b });
      if (hits.length >= 8) break;
    }

    for (const c of CIGARS) {
      if (!cigarInRegion(c, market)) continue;
      const lineHit =
        norm(c.line).includes(nq) || norm(`${c.brand} ${c.line}`).includes(nq);
      if (lineHit && !seenLine.has(c.id)) {
        seenLine.add(c.id);
        hits.push({ kind: "line", cigar: c });
      }
      for (const v of c.vitolas ?? []) {
        if (!norm(v.name).includes(nq)) continue;
        const key = `${c.id}::${v.name}`;
        if (seenVitola.has(key)) continue;
        seenVitola.add(key);
        hits.push({ kind: "vitola", cigar: c, vitola: v });
        // vitola pogodak → ponudi i liniju i brand kao zasebne rezultate
        if (!seenLine.has(c.id)) {
          seenLine.add(c.id);
          hits.push({ kind: "line", cigar: c });
        }
        if (!seenBrand.has(c.brand)) {
          seenBrand.add(c.brand);
          hits.push({ kind: "brand", brand: c.brand });
        }
      }
      if (hits.length >= 24) break;
    }
    return hits.slice(0, 18);
  }, [tab, query, market]);

  const matchedBrands = useMemo(() => {
    const nq = norm(query.trim());
    if (tab !== "cigars" || nq.length < 2 || browseBrands) return [];
    return ALL_BRANDS.filter((b) => norm(b).includes(nq)).slice(0, 4);
  }, [tab, query, browseBrands]);

  const brandRows = useMemo(() => {
    if (tab !== "cigars" || !browseBrands) return [];
    const nq = norm(query.trim());
    return BRAND_CATALOG.filter((b) => {
      if (nq && !norm(b.brand).includes(nq) && !norm(b.info?.country ?? "").includes(nq)) {
        return false;
      }
      if (market !== "ALL" && !cigarsByBrand(b.brand).some((c) => cigarInRegion(c, market))) {
        return false;
      }
      return true;
    });
  }, [tab, browseBrands, query, market]);

  const brandAnchors = useMemo(() => {
    const at = new Map<number, string>();
    const letters = new Set<string>();
    let prev = "";
    brandRows.forEach((b, i) => {
      const L = letterFor(b.brand);
      letters.add(L);
      if (L !== prev) {
        at.set(i, L);
        prev = L;
      }
    });
    return { at, letters };
  }, [brandRows]);

  const jumpToLetter = (l: string) => {
    document
      .getElementById(`ci-alpha-${l}`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  /** Flat-list open: shape filter → that vitola; else LineSheet. */
  const openFromFlatList = (raw: Cigar) => {
    const cigar = resolveCigarId(raw.id) ?? raw;
    if (shapeFilter) {
      const match = firstVitolaOfShape(cigar, shapeFilter);
      if (match) {
        openVitola(cigar, match);
        return;
      }
    }
    openLine(cigar);
  };

  const switchTab = (next: Tab) => {
    setTab(next);
    setStyleFilter(null);
    setStrengthFilter(null);
    setShapeFilter(null);
    setCleanOnly(false);
    setBrowseBrands(next === "cigars");
    setShowShops(false);
    setSortBy(next === "cigars" ? "name" : "quality");
  };

  const styles = useMemo(() => {
    if (tab === "cigars") return [];
    const seen = new Set<string>();
    return DRINKS[tab]
      .filter((d) => {
        if (seen.has(d.style)) return false;
        seen.add(d.style);
        return true;
      })
      .map((d) => d.style);
  }, [tab]);

  const q = query.toLowerCase();

  const cigarPrice = (c: Cigar): number => {
    const priced = (c.vitolas ?? []).map((v) => v.priceEUR).filter((p): p is number => p != null);
    if (priced.length) return Math.min(...priced);
    return c.priceEUR ?? Number.MAX_SAFE_INTEGER;
  };

  const cigars = useMemo(() => {
    if (tab !== "cigars" || browseBrands) return [];
    const list = CIGARS.filter(
      (c) =>
        cigarInRegion(c, market) &&
        (!q ||
          norm(
            `${c.brand} ${c.line} ${c.vitola} ${c.wrapper} ${c.country} ${(c.vitolas ?? [])
              .map((v) => v.name)
              .join(" ")}`,
          ).includes(norm(q))) &&
        (strengthFilter == null || c.strength === strengthFilter) &&
        (shapeFilter == null || cigarShapes(c).has(shapeFilter)),
    );
    const by: Record<string, (a: Cigar, b: Cigar) => number> = {
      name: (a, b) => a.brand.localeCompare(b.brand) || a.line.localeCompare(b.line),
      price: (a, b) => cigarPrice(a) - cigarPrice(b),
      body: (a, b) => b.body - a.body,
      strength: (a, b) => b.strength - a.strength,
    };
    return [...list].sort(by[sortBy] ?? by.name);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tab, q, strengthFilter, shapeFilter, market, sortBy, browseBrands]);

  const drinks = useMemo(() => {
    if (tab === "cigars") return [];
    const list = DRINKS[tab].filter(
      (d) =>
        (!q || `${d.name} ${d.region}`.toLowerCase().includes(q)) &&
        (styleFilter == null || d.style === styleFilter) &&
        (!cleanOnly || d.additiveStatus === "clean" || d.additiveStatus === "low"),
    );
    const mid = (d: Drink) =>
      d.priceEUR ? (d.priceEUR.min + d.priceEUR.max) / 2 : Number.MAX_SAFE_INTEGER;
    const by: Record<string, (a: Drink, b: Drink) => number> = {
      quality: (a, b) => (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
      price: (a, b) => mid(a) - mid(b),
      body: (a, b) => b.body - a.body || (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
      sweetness: (a, b) => b.sweetness - a.sweetness || (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
    };
    return [...list].sort(by[sortBy] ?? by.quality);
  }, [tab, q, styleFilter, cleanOnly, sortBy]);

  useEffect(() => {
    setLimit(120);
  }, [tab, q, strengthFilter, shapeFilter, market, sortBy, browseBrands]);

  const showRail =
    tab === "cigars" &&
    browseBrands &&
    brandRows.length > 12 &&
    !brand &&
    !line &&
    !detail &&
    !pendingCigar;

  return (
    <div className="pb-4">
      <div className="no-scrollbar mt-4 flex gap-2 overflow-x-auto">
        {TABS.map((tb) => (
          <Chip key={tb} active={tab === tb} onClick={() => switchTab(tb)}>
            {tb === "cigars" ? t("cat.cigars") : t(`cat.${tb}` as const)}
          </Chip>
        ))}
      </div>

      <div className="mt-3">
        <SearchInput value={query} onChange={setQuery} placeholder={t("pair.search")} />
      </div>

      {searchHits.length > 0 && (
        <div className="mt-2 space-y-1.5 rounded-xl border border-zlato/25 bg-cedar/50 p-2">
          <div className="px-1 text-micro uppercase tracking-widest text-dim">
            {t("search.hits")}
          </div>
          {searchHits.map((h) => {
            if (h.kind === "brand") {
              return (
                <button
                  key={`b-${h.brand}`}
                  type="button"
                  onClick={() => openBrand(h.brand)}
                  className="flex w-full items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-zlato/10"
                >
                  <span className="text-sm text-papir">{h.brand}</span>
                  <span className="shrink-0 text-micro text-zlato-2">{t("search.kindBrand")}</span>
                </button>
              );
            }
            if (h.kind === "line") {
              return (
                <button
                  key={`l-${h.cigar.id}`}
                  type="button"
                  onClick={() => openLine(h.cigar)}
                  className="flex w-full items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-zlato/10"
                >
                  <span className="truncate text-sm text-papir">
                    {h.cigar.brand} <span className="text-zlato-2">{h.cigar.line}</span>
                  </span>
                  <span className="shrink-0 text-micro text-zlato-2">{t("search.kindLine")}</span>
                </button>
              );
            }
            return (
              <button
                key={`v-${h.cigar.id}-${h.vitola.name}`}
                type="button"
                onClick={() => openVitola(h.cigar, h.vitola)}
                className="flex w-full items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-zlato/10"
              >
                <span className="truncate text-sm text-papir">
                  {h.cigar.brand} {h.cigar.line} · {h.vitola.name}
                </span>
                <span className="shrink-0 text-micro text-zlato-2">{t("search.kindVitola")}</span>
              </button>
            );
          })}
        </div>
      )}

      {matchedBrands.length > 0 && (
        <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
          {matchedBrands.map((b) => (
            <button
              key={b}
              type="button"
              onClick={() => openBrand(b)}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-zlato/50 bg-zlato/10 px-3 py-1.5 text-xs text-zlato-2 hover:bg-zlato/20"
            >
              {t("brand.open")}: {b} →
            </button>
          ))}
        </div>
      )}

      <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
        {tab === "cigars" && (
          <Chip active={browseBrands} onClick={() => setBrowseBrands(!browseBrands)}>
            {t("brand.index")}
          </Chip>
        )}
        {tab === "cigars" && (
          <Chip active={showShops} onClick={() => setShowShops(!showShops)}>
            {t("shops.title")}
          </Chip>
        )}
        {tab === "cigars" &&
          !browseBrands &&
          [1, 2, 3, 4, 5].map((s) => (
            <Chip
              key={s}
              active={strengthFilter === s}
              onClick={() => setStrengthFilter(strengthFilter === s ? null : s)}
            >
              {t("filter.strength")} {s}
            </Chip>
          ))}
        {tab !== "cigars" && tab !== "coffee" && tab !== "tequila" && (
          <Chip active={cleanOnly} onClick={() => setCleanOnly(!cleanOnly)}>
            {t("filter.clean")}
          </Chip>
        )}
        {styles.map((s) => (
          <Chip
            key={s}
            active={styleFilter === s}
            onClick={() => setStyleFilter(styleFilter === s ? null : s)}
          >
            {lx(STYLE_LABELS[s]) || s}
          </Chip>
        ))}
      </div>

      {/* filter oblika (vitole) — samo u ravnom popisu cigara */}
      {tab === "cigars" && !browseBrands && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.shape")}
          </span>
          {SHAPE_FAMILIES.map((s) => (
            <Chip
              key={s}
              active={shapeFilter === s}
              onClick={() => setShapeFilter(shapeFilter === s ? null : s)}
            >
              {t(`shape.${s}` as StringKey)}
            </Chip>
          ))}
        </div>
      )}

      {/* tržište uvijek vidljivo za cigare (indeks brendova + popis) */}
      {tab === "cigars" && <MarketFilter className="mt-2" />}

      {!browseBrands && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("sort.label")}
          </span>
          {(tab === "cigars"
            ? (["name", "price", "body", "strength"] as const)
            : (["quality", "price", "body", "sweetness"] as const)
          ).map((s) => (
            <Chip key={s} active={sortBy === s} onClick={() => setSortBy(s)}>
              {t(`sort.${s}` as StringKey)}
              {sortBy === s ? (s === "price" || s === "name" ? " ↑" : " ↓") : ""}
            </Chip>
          ))}
        </div>
      )}

      {tab === "cigars" && showShops && (
        <div className="mt-3 space-y-3 rounded-xl border border-zlato/25 bg-cedar/60 p-3">
          <p className="text-xs leading-relaxed text-dim">{t("shops.intro")}</p>
          {REGIONS.map((r) => (
            <div key={r}>
              <button
                type="button"
                onClick={() => {
                  setMarket(r);
                  setBrowseBrands(false);
                }}
                className="flex w-full items-baseline justify-between gap-2 text-left"
              >
                <span className="font-display text-sm uppercase tracking-widest text-zlato-2">
                  {t(`market.${r}` as StringKey)}
                </span>
                <span className="shrink-0 text-micro text-dim">
                  {cigarCountByRegion[r]} {t("shops.availableHere")} →
                </span>
              </button>
              <div className="mt-1.5 space-y-1.5">
                {SHOPS.filter((s) => s.region === r).map((s) => (
                  <a
                    key={s.id}
                    href={s.home}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-lg border border-dim/15 bg-humidor/40 px-2.5 py-1.5 hover:border-zlato/40"
                  >
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="text-sm text-papir/90">{s.name} ↗</span>
                      <span className="shrink-0 text-micro text-dim">
                        {s.productHost ? t("shops.direct") : t("shops.search")}
                      </span>
                    </div>
                    <div className="text-micro text-dim/85">{lx(s.note)}</div>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-3 text-xs text-dim">
        {browseBrands
          ? `${brandRows.length} · ${t("brand.index")}`
          : `${tab === "cigars" ? cigars.length : drinks.length} · ${
              tab === "cigars" ? t("cat.cigars") : t(`cat.${tab}` as const)
            }`}
      </div>

      <div className="mt-2 space-y-2">
        {browseBrands &&
          brandRows.map((b, i) => {
            const anchor = brandAnchors.at.get(i);
            const linesInMarket = cigarsByBrand(b.brand).filter(
              (c) => c.line !== "Additional Vitolas" && cigarInRegion(c, market),
            );
            const lineCount = market === "ALL" ? b.lineCount : linesInMarket.length;
            return (
              <button
                key={b.brand}
                type="button"
                id={anchor ? `ci-alpha-${anchor}` : undefined}
                onClick={() => openBrand(b.brand)}
                className="w-full scroll-mt-4 rounded-xl border border-dim/15 bg-cedar p-3 text-left transition-colors hover:border-zlato/40"
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-display text-base text-papir">{b.brand}</span>
                  {b.minPriceEUR != null && (
                    <span className="shrink-0 text-xs text-dim">
                      {t("brand.from")} {b.minPriceEUR.toFixed(b.minPriceEUR % 1 ? 2 : 0)} €
                    </span>
                  )}
                </div>
                <div className="mt-1 text-xs text-dim">
                  {b.info ? cn(b.info.country) : ""}
                  {b.info?.founded ? ` · ${b.info.founded}` : ""}
                  {" · "}
                  {lineCount} {t("brand.lines")}
                  {b.hasAdditionalVitolas && market === "ALL" ? " · +" : ""}
                </div>
                {b.info && (
                  <div className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-dim/90">
                    {lx(b.info.blurb)}
                  </div>
                )}
              </button>
            );
          })}
        {!browseBrands &&
          cigars.slice(0, limit).map((c) => (
            <CigarRow
              key={`${c.id}::${c.line}`}
              cigar={c}
              onClick={() => openFromFlatList(c)}
            />
          ))}
        {!browseBrands && tab === "cigars" && cigars.length > limit && (
          <button
            type="button"
            onClick={() => setLimit((n) => n + 200)}
            className="w-full rounded-xl border border-zlato/30 bg-cedar/60 py-2.5 text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
          >
            {t("catalog.showMore")} ({cigars.length - limit})
          </button>
        )}
        {drinks.map((d, i) => (
          <DrinkRow
            key={d.id}
            drink={d}
            rank={i + 1}
            onClick={() => setDetail({ kind: "drink", item: d })}
          />
        ))}
      </div>

      {showRail && (
        <AlphabetRail letters={brandAnchors.letters} onJump={jumpToLetter} />
      )}

      {pendingCigar && (
        <VitolaPicker
          cigar={pendingCigar}
          onPick={(v) => openVitola(pendingCigar, v)}
          onBack={() => setPendingCigar(null)}
        />
      )}

      {brand && (
        <BrandSheet brand={brand} onClose={clearCatalogFocus} onOpenLine={openLine} />
      )}

      {line && (
        <LineSheet
          cigar={line}
          onClose={() => openBrand(line.brand)}
          onOpenBrand={openBrand}
          onOpenVitola={openVitola}
        />
      )}

      <DetailSheet
        target={detail}
        onClose={clearCatalogFocus}
        onOpenBrand={openBrand}
        onOpenLine={openLine}
        onPair={
          onPair
            ? (target) => {
                setDetail(null);
                onPair(target);
              }
            : undefined
        }
      />
    </div>
  );
}
