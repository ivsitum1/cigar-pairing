import { useMemo, useState } from "react";
import type { Cigar, Drink, DrinkCategory, Market } from "../types";
import { CIGARS, DRINKS, cigarById, ALL_BRANDS } from "../data";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, SearchInput } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { DetailSheet } from "../components/DetailSheet";
import { BrandSheet } from "../components/BrandSheet";
import { VitolaPicker } from "../components/VitolaPicker";
import { applyVitola, needsVitolaPick, uniqueVitolas } from "../lib/cigarVitola";
import { useMarket, setMarket } from "../store/market";

const norm = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

type Tab = "cigars" | DrinkCategory;
const TABS: Tab[] = ["cigars", "rum", "whisky", "brandy", "gin", "coffee"];
const MARKETS: Market[] = ["HR", "EU", "USA", "WW"];

export function CatalogPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx } = useI18n();
  const [tab, setTab] = useState<Tab>("cigars");
  const [query, setQuery] = useState("");
  const [styleFilter, setStyleFilter] = useState<string | null>(null);
  const [strengthFilter, setStrengthFilter] = useState<number | null>(null);
  const [cleanOnly, setCleanOnly] = useState(false);
  const market = useMarket();
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const [pendingCigar, setPendingCigar] = useState<Cigar | null>(null);
  const [brand, setBrand] = useState<string | null>(null);

  // marke koje odgovaraju pretrazi (za "Otvori brend")
  const matchedBrands = useMemo(() => {
    const nq = norm(query.trim());
    if (tab !== "cigars" || nq.length < 2) return [];
    return ALL_BRANDS.filter((b) => norm(b).includes(nq)).slice(0, 4);
  }, [tab, query]);

  const openCigar = (raw: Cigar) => {
    const cigar = cigarById(raw.id) ?? raw;
    if (needsVitolaPick(cigar)) {
      setPendingCigar(cigar);
      return;
    }
    const vitolas = uniqueVitolas(cigar);
    setDetail({
      kind: "cigar",
      item: vitolas.length === 1 ? applyVitola(cigar, vitolas[0]) : cigar,
    });
  };

  const switchTab = (next: Tab) => {
    setTab(next);
    setStyleFilter(null);
    setStrengthFilter(null);
    setCleanOnly(false);
  };

  const styles = useMemo(() => {
    if (tab === "cigars") return [];
    const seen = new Set<string>();
    return DRINKS[tab].filter((d) => {
      if (seen.has(d.style)) return false;
      seen.add(d.style);
      return true;
    }).map((d) => d.style);
  }, [tab]);

  const q = query.toLowerCase();

  const cigars = useMemo(
    () =>
      tab !== "cigars"
        ? []
        : CIGARS.filter(
            (c) =>
              c.markets.includes(market) &&
              (!q || `${c.brand} ${c.line} ${c.vitola} ${c.wrapper}`.toLowerCase().includes(q)) &&
              (strengthFilter == null || c.strength === strengthFilter),
          ),
    [tab, q, strengthFilter, market],
  );

  // rangirano po kvaliteti, kao MASTER sheet u Excelu
  const drinks = useMemo(
    () =>
      tab === "cigars"
        ? []
        : DRINKS[tab]
            .filter(
              (d) =>
                (!q || `${d.name} ${d.region}`.toLowerCase().includes(q)) &&
                (styleFilter == null || d.style === styleFilter) &&
                (!cleanOnly || d.additiveStatus === "clean" || d.additiveStatus === "low"),
            )
            .sort((a, b) => (b.qualityScore ?? 0) - (a.qualityScore ?? 0)),
    [tab, q, styleFilter, cleanOnly],
  );

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

      {/* pretraga pogodila marku -> otvori brend stranicu */}
      {matchedBrands.length > 0 && (
        <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
          {matchedBrands.map((b) => (
            <button
              key={b}
              onClick={() => setBrand(b)}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-zlato/50 bg-zlato/10 px-3 py-1.5 text-xs text-zlato-2 hover:bg-zlato/20"
            >
              {t("brand.open")}: {b} →
            </button>
          ))}
        </div>
      )}

      {/* filteri */}
      <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
        {tab === "cigars" &&
          MARKETS.map((m) => (
            <Chip
              key={m}
              active={market === m}
              onClick={() => setMarket(m)}
            >
              {t(`market.${m}` as StringKey)}
            </Chip>
          ))}
        {tab === "cigars" &&
          [1, 2, 3, 4, 5].map((s) => (
            <Chip
              key={s}
              active={strengthFilter === s}
              onClick={() => setStrengthFilter(strengthFilter === s ? null : s)}
            >
              {t("filter.strength")} {s}
            </Chip>
          ))}
        {tab === "rum" && (
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

      <div className="mt-3 text-xs text-dim">
        {tab === "cigars" ? cigars.length : drinks.length} ·{" "}
        {tab === "cigars" ? t("cat.cigars") : t(`cat.${tab}` as const)}
      </div>

      <div className="mt-2 space-y-2">
        {cigars.map((c) => (
          <CigarRow
            key={`${c.id}::${c.line}`}
            cigar={c}
            onClick={() => openCigar(c)}
          />
        ))}
        {drinks.map((d, i) => (
          <DrinkRow
            key={d.id}
            drink={d}
            rank={i + 1}
            onClick={() => setDetail({ kind: "drink", item: d })}
          />
        ))}
      </div>

      {pendingCigar && (
        <VitolaPicker
          cigar={pendingCigar}
          onPick={(v) => {
            setDetail({ kind: "cigar", item: applyVitola(pendingCigar, v) });
            setPendingCigar(null);
          }}
          onBack={() => setPendingCigar(null)}
        />
      )}

      {brand && (
        <BrandSheet
          brand={brand}
          onClose={() => setBrand(null)}
          onOpenCigar={(c) => {
            setBrand(null);
            openCigar(c);
          }}
        />
      )}

      <DetailSheet
        target={detail}
        onClose={() => setDetail(null)}
        onOpenBrand={(b) => {
          setDetail(null);
          setBrand(b);
        }}
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
