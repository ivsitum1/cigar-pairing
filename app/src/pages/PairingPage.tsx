import { useEffect, useMemo, useState } from "react";
import type { Cigar, Drink, DrinkCategory, Market, PairingResult, Vitola } from "../types";
import { ALL_DRINKS, CIGARS, cigarById, cigarLinkForMarket, cigarPriceForMarket, formatPrice } from "../data";
import { pairCigarsForDrink, pairDrinksForCigar } from "../engine/pairing";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, Meter, ScoreBand, SearchInput, SectionTitle } from "../components/ui";
import { getItemState, useCollection } from "../store/collection";
import { DetailSheet } from "../components/DetailSheet";
import { OcrScan } from "../components/OcrScan";
import { VitolaPicker } from "../components/VitolaPicker";
import { applyVitola, needsVitolaPick, uniqueVitolas } from "../lib/cigarVitola";
import { useMarket, setMarket } from "../store/market";
import { consumePairingIntent, usePairingNavVersion } from "../store/pairingNav";
import { CustomPairing } from "./CustomPairing";

type Mode = "cigarToDrink" | "drinkToCigar" | "custom";
const MARKETS: Market[] = ["HR", "EU", "USA", "WW"];

// pretraga neosjetljiva na naglaske i velika/mala slova
const norm = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
// cigara -> tocno 3 kategorije pica (po jedan prijedlog iz svake)
const SUGGEST_CATEGORIES: DrinkCategory[] = ["rum", "whisky", "brandy", "gin", "wine"];

export function PairingPage() {
  const { t, lx, cn } = useI18n();
  useCollection();
  const [mode, setMode] = useState<Mode>("cigarToDrink");
  const [query, setQuery] = useState("");
  const [selectedCigar, setSelectedCigar] = useState<Cigar | null>(null);
  const [pendingCigar, setPendingCigar] = useState<Cigar | null>(null);
  const [selectedDrink, setSelectedDrink] = useState<Drink | null>(null);
  const [onlyMine, setOnlyMine] = useState(false);
  const market = useMarket();
  // indeks "sljedeceg prijedloga" po kategoriji (cigara->pice) ili offset (pice->cigare)
  const [cycle, setCycle] = useState<Record<string, number>>({});
  const [showPrefs, setShowPrefs] = useState(false);
  const [excludedCountries, setExcludedCountries] = useState<string[]>(
    () => JSON.parse(localStorage.getItem("prefs-excluded-countries") ?? "[]"),
  );
  const [excludedBrands, setExcludedBrands] = useState<string[]>(
    () => JSON.parse(localStorage.getItem("prefs-excluded-brands") ?? "[]"),
  );

  const toggleExcluded = (
    value: string,
    list: string[],
    set: (v: string[]) => void,
    key: string,
  ) => {
    const next = list.includes(value)
      ? list.filter((x) => x !== value)
      : [...list, value];
    localStorage.setItem(key, JSON.stringify(next));
    set(next);
  };
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const pairingNavVersion = usePairingNavVersion();

  const selected = mode === "cigarToDrink" ? selectedCigar : selectedDrink;

  const marketCigars = useMemo(
    () =>
      CIGARS.filter(
        (c) =>
          c.markets.includes(market) &&
          !excludedCountries.includes(c.country) &&
          !excludedBrands.includes(c.brand),
      ),
    [market, excludedCountries, excludedBrands],
  );

  const allCountries = useMemo(
    () => [...new Set(CIGARS.map((c) => c.country))].sort(),
    [],
  );
  const allBrands = useMemo(
    () => [...new Set(CIGARS.map((c) => c.brand))].sort(),
    [],
  );

  // PUNI popis — identican onome iz kojeg engine predlaze (bez skracivanja).
  // Pretraga ignorira naglaske ("Partagas" nalazi "Partagás").
  const pickList = useMemo(() => {
    const q = norm(query);
    if (mode === "cigarToDrink") {
      return marketCigars.filter(
        (c) =>
          !q ||
          norm(
            `${c.brand} ${c.line} ${c.country} ${c.wrapper} ${c.vitolas
              .map((v) => v.name)
              .join(" ")}`,
          ).includes(q),
      );
    }
    return ALL_DRINKS.filter(
      (d) => d.pairable && (!q || norm(`${d.name} ${d.style} ${d.region}`).includes(q)),
    );
  }, [mode, query, marketCigars]);

  // cigara -> po jedan najbolji prijedlog iz rum / whisky / brandy / gin / vino (+ kava bonus)
  const drinkSuggestions = useMemo(() => {
    if (mode !== "cigarToDrink" || !selectedCigar) return null;
    let drinks = ALL_DRINKS;
    if (onlyMine) drinks = drinks.filter((d) => getItemState(d.id).owned);
    const ranked = pairDrinksForCigar(selectedCigar, drinks);
    const perCategory = (cat: DrinkCategory) =>
      ranked.filter((r) => r.item.category === cat);
    return {
      cards: SUGGEST_CATEGORIES.map((cat) => {
        const list = perCategory(cat);
        const idx = list.length ? (cycle[cat] ?? 0) % list.length : 0;
        return { category: cat, result: list[idx], total: list.length };
      }),
      coffee: perCategory("coffee")[0] ?? null,
    };
  }, [mode, selectedCigar, onlyMine, cycle]);

  // pice -> tocno 3 cigare RAZLICITIH brendova (cycle pomice prozor za 3)
  const cigarSuggestions = useMemo(() => {
    if (mode !== "drinkToCigar" || !selectedDrink) return null;
    let cigars = marketCigars;
    if (onlyMine) cigars = cigars.filter((c) => getItemState(c.id).owned);
    const ranked = pairCigarsForDrink(selectedDrink, cigars);
    if (ranked.length === 0) return { window: [], total: 0 };
    // diversity: po jedna najbolja cigara svakog brenda
    const seen = new Set<string>();
    const diverse = ranked.filter((r) => {
      if (seen.has(r.item.brand)) return false;
      seen.add(r.item.brand);
      return true;
    });
    const pool = diverse.length >= 3 ? diverse : ranked;
    const offset = ((cycle["cigars"] ?? 0) * 3) % Math.max(pool.length, 1);
    return { window: pool.slice(offset, offset + 3), total: pool.length };
  }, [mode, selectedDrink, onlyMine, cycle, marketCigars]);

  const reset = () => {
    setSelectedCigar(null);
    setPendingCigar(null);
    setSelectedDrink(null);
    setQuery("");
    setCycle({});
  };

  const pickCigar = (raw: Cigar) => {
    const cigar = cigarById(raw.id) ?? raw;
    if (needsVitolaPick(cigar)) {
      setPendingCigar(cigar);
      return;
    }
    const vitolas = uniqueVitolas(cigar);
    setSelectedCigar(vitolas.length === 1 ? applyVitola(cigar, vitolas[0]) : cigar);
  };

  const confirmVitola = (vitola: Vitola) => {
    if (!pendingCigar) return;
    setSelectedCigar(applyVitola(pendingCigar, vitola));
    setPendingCigar(null);
  };

  useEffect(() => {
    const intent = consumePairingIntent();
    if (!intent) return;
    setCycle({});
    setDetail(null);
    if (intent.mode === "cigarToDrink") {
      setMode("cigarToDrink");
      setSelectedDrink(null);
      setQuery(`${intent.cigar.brand} ${intent.cigar.line}`);
      const cigar = cigarById(intent.cigar.id) ?? intent.cigar;
      if (needsVitolaPick(cigar)) {
        setPendingCigar(cigar);
        setSelectedCigar(null);
      } else {
        const vitolas = uniqueVitolas(cigar);
        setSelectedCigar(vitolas.length === 1 ? applyVitola(cigar, vitolas[0]) : cigar);
        setPendingCigar(null);
      }
    } else {
      setMode("drinkToCigar");
      setSelectedCigar(null);
      setPendingCigar(null);
      setSelectedDrink(intent.drink);
      setQuery(intent.drink.name);
    }
  }, [pairingNavVersion]);

  return (
    <div className="pb-4">
      {/* mode toggle */}
      <div className="mt-4 grid grid-cols-3 gap-2">
        {(["cigarToDrink", "drinkToCigar", "custom"] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              reset();
            }}
            className={`rounded-lg border py-2.5 font-display text-[11px] uppercase tracking-[0.12em] transition-colors ${
              mode === m
                ? "border-zlato bg-zlato/15 text-zlato-2"
                : "border-dim/25 text-dim hover:border-zlato/40"
            }`}
          >
            {t(
              m === "cigarToDrink"
                ? "pair.cigarToDrink"
                : m === "drinkToCigar"
                  ? "pair.drinkToCigar"
                  : "pair.custom",
            )}
          </button>
        ))}
      </div>

      {mode === "custom" && <CustomPairing onOpenDetail={setDetail} />}

      {/* market birac — bitan kad biras cigare */}
      {mode !== "custom" && (
      <div className="no-scrollbar mt-3 flex items-center gap-2 overflow-x-auto">
        <span className="shrink-0 text-[10px] uppercase tracking-widest text-dim">
          {t("pair.market")}
        </span>
        {MARKETS.map((m) => (
          <Chip key={m} active={market === m} onClick={() => setMarket(m)}>
            {t(`market.${m}` as StringKey)}
          </Chip>
        ))}
        <Chip
          active={showPrefs || excludedCountries.length > 0 || excludedBrands.length > 0}
          onClick={() => setShowPrefs(!showPrefs)}
        >
          ⚙ {excludedCountries.length + excludedBrands.length || ""}
        </Chip>
      </div>
      )}

      {/* preferencije: zemlje/brendovi koje NE zelis u prijedlozima */}
      {mode !== "custom" && showPrefs && (
        <div className="mt-2 rounded-xl border border-dim/20 bg-cedar p-3">
          <div className="mb-1 font-display text-[11px] uppercase tracking-[0.2em] text-zlato">
            {t("pair.prefs")}
          </div>
          <div className="mb-2 text-[11px] text-dim">{t("pair.prefsHint")}</div>
          <div className="flex flex-wrap gap-1.5">
            {allCountries.map((cty) => (
              <Chip
                key={cty}
                active={!excludedCountries.includes(cty)}
                onClick={() =>
                  toggleExcluded(cty, excludedCountries, setExcludedCountries, "prefs-excluded-countries")
                }
              >
                {excludedCountries.includes(cty) ? "✕ " : ""}{cty}
              </Chip>
            ))}
          </div>
          <div className="band-rule my-2" />
          <div className="flex max-h-32 flex-wrap gap-1.5 overflow-y-auto">
            {allBrands.map((b) => (
              <Chip
                key={b}
                active={!excludedBrands.includes(b)}
                onClick={() =>
                  toggleExcluded(b, excludedBrands, setExcludedBrands, "prefs-excluded-brands")
                }
              >
                {excludedBrands.includes(b) ? "✕ " : ""}{b}
              </Chip>
            ))}
          </div>
        </div>
      )}

      {/* picker + OCR (fotografiraj bocu/cigaru) */}
      {mode !== "custom" && !selected && !pendingCigar && (
        <>
          <div className="mt-3 flex items-stretch gap-2">
            <div className="flex-1">
              <SearchInput
                value={query}
                onChange={setQuery}
                placeholder={`${t(mode === "cigarToDrink" ? "pair.pickCigar" : "pair.pickDrink")} — ${t("pair.search")}`}
              />
            </div>
            <OcrScan
              candidates={
                mode === "cigarToDrink"
                  ? marketCigars.map((c) => ({
                      id: c.id,
                      label: `${c.brand} ${c.line}`,
                      brand: c.brand,
                    }))
                  : ALL_DRINKS.filter((d) => d.pairable).map((d) => ({
                      id: d.id,
                      label: d.name,
                    }))
              }
              onMatch={(id) => {
                // OCR prepoznato -> otvori karticu (može se odmah označiti u kolekciju)
                if (mode === "cigarToDrink") {
                  const c = cigarById(id) ?? marketCigars.find((x) => x.id === id);
                  if (c) setDetail({ kind: "cigar", item: c });
                } else {
                  const d = ALL_DRINKS.find((x) => x.id === id);
                  if (d) setDetail({ kind: "drink", item: d });
                }
              }}
              onText={setQuery}
            />
          </div>
          <div className="mt-3 space-y-1.5">
            {pickList.map((item) =>
              mode === "cigarToDrink" ? (
                <PickRow
                  key={`${item.id}::${(item as Cigar).line}`}
                  title={`${(item as Cigar).brand} ${(item as Cigar).line}`}
                  sub={`${(item as Cigar).vitolas.length > 1 ? `${(item as Cigar).vitolas.length} ${t("common.vitolaCountSuffix")} · ` : `${(item as Cigar).vitola} · `}${(item as Cigar).wrapper} · ${cn((item as Cigar).country)}`}
                  onPick={() => pickCigar((item as Cigar))}
                />
              ) : (
                <PickRow
                  key={item.id}
                  title={(item as Drink).name}
                  sub={lx(STYLE_LABELS[(item as Drink).style]) || (item as Drink).style}
                  onPick={() => setSelectedDrink(item as Drink)}
                />
              ),
            )}
          </div>
        </>
      )}

      {pendingCigar && !selected && (
        <VitolaPicker
          cigar={pendingCigar}
          onPick={confirmVitola}
          onBack={() => setPendingCigar(null)}
        />
      )}

      {/* odabrano + 3 prijedloga */}
      {selected && (
        <>
          <div className="mt-4 rounded-xl border border-zlato/40 bg-cedar p-3">
            <div className="flex items-center justify-between gap-2">
              <div>
                <div className="font-display text-base text-papir">
                  {mode === "cigarToDrink"
                    ? `${(selected as Cigar).brand} ${(selected as Cigar).line}`
                    : (selected as Drink).name}
                </div>
                {mode === "cigarToDrink" && (
                  <div className="mt-0.5 text-xs text-dim">
                    {(selected as Cigar).vitola} · {(selected as Cigar).wrapper} · {cn((selected as Cigar).country)}
                  </div>
                )}
                <div className="mt-1.5 flex gap-4">
                  {mode === "cigarToDrink" ? (
                    <>
                      <Meter value={(selected as Cigar).strength} label={t("common.strength")} accent="var(--color-oxblood)" />
                      <Meter value={(selected as Cigar).body} label={t("common.body")} />
                    </>
                  ) : (
                    <>
                      <Meter value={(selected as Drink).body} label={t("common.body")} />
                      <Meter value={(selected as Drink).sweetness} label={t("common.sweetness")} accent="var(--color-lista)" />
                    </>
                  )}
                </div>
              </div>
              <button
                onClick={reset}
                className="shrink-0 rounded-md border border-dim/30 px-3 py-1.5 text-xs text-dim hover:border-zlato/50"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="no-scrollbar mt-3 flex gap-2 overflow-x-auto">
            <Chip active={onlyMine} onClick={() => setOnlyMine(!onlyMine)}>
              {t("pair.onlyMine")}
            </Chip>
          </div>

          <SectionTitle>{t("pair.suggestions")}</SectionTitle>

          {/* CIGARA -> 5 pica (rum / whisky / konjak / gin / vino) */}
          {drinkSuggestions && (
            <div className="space-y-3">
              {drinkSuggestions.cards.map(({ category, result, total }) => (
                <div key={category}>
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-display text-[11px] uppercase tracking-[0.2em] text-oxblood">
                      {t(`cat.${category}` as StringKey)}
                    </span>
                    {total > 1 && (
                      <button
                        onClick={() =>
                          setCycle((c) => ({ ...c, [category]: (c[category] ?? 0) + 1 }))
                        }
                        className="text-[11px] text-dim hover:text-zlato-2"
                      >
                        ↻ {t("pair.next")}
                      </button>
                    )}
                  </div>
                  {result ? (
                    <ResultCard
                      result={result}
                      title={result.item.name}
                      sub={lx(STYLE_LABELS[result.item.style]) || result.item.style}
                      price={formatPrice(result.item.priceEUR)}
                      priceUrl={result.item.priceUrl}
                      excelHint={result.item.cigarHint}
                      onOpen={() => setDetail({ kind: "drink", item: result.item })}
                    />
                  ) : (
                    <p className="rounded-xl border border-dim/15 bg-cedar p-3 text-xs text-dim">
                      {t("pair.noResults")}
                    </p>
                  )}
                </div>
              ))}
              {drinkSuggestions.coffee && (
                <button
                  onClick={() =>
                    setDetail({ kind: "drink", item: drinkSuggestions.coffee!.item })
                  }
                  className="flex w-full items-center gap-2 rounded-lg border border-dim/20 bg-cedar/60 px-3 py-2 text-left text-xs text-dim hover:border-zlato/40"
                >
                  <span className="text-zlato">☕</span>
                  <span>
                    {t("pair.coffeeAlt")}:{" "}
                    <span className="text-papir/90">{drinkSuggestions.coffee.item.name}</span>
                  </span>
                  <span className="ml-auto shrink-0 font-display text-zlato-2">
                    {drinkSuggestions.coffee.score}
                  </span>
                </button>
              )}
            </div>
          )}

          {/* PICE -> 3 cigare */}
          {cigarSuggestions && (
            <div className="space-y-3">
              {cigarSuggestions.total > 3 && (
                <div className="flex justify-end">
                  <button
                    onClick={() => setCycle((c) => ({ ...c, cigars: (c["cigars"] ?? 0) + 1 }))}
                    className="text-[11px] text-dim hover:text-zlato-2"
                  >
                    ↻ {t("pair.next")}
                  </button>
                </div>
              )}
              {cigarSuggestions.window.length === 0 && (
                <p className="text-sm text-dim">{t("pair.noResults")}</p>
              )}
              {cigarSuggestions.window.map((r) => {
                const mp = cigarPriceForMarket(r.item, market);
                const priceStr =
                  mp.price != null
                    ? `${mp.fromMany ? t("price.from") + " " : ""}${mp.price.toFixed(mp.price % 1 ? 2 : 0)} €`
                    : t("price.check");
                return (
                  <ResultCard
                    key={r.item.id}
                    result={r}
                    title={`${r.item.brand} ${r.item.line}`}
                    sub={r.item.wrapper}
                    price={priceStr}
                    priceUrl={cigarLinkForMarket(r.item, market)}
                    vitolas={r.item.vitolas}
                    excelHint={null}
                    onOpen={() => setDetail({ kind: "cigar", item: r.item })}
                  />
                );
              })}
            </div>
          )}
        </>
      )}

      <DetailSheet target={detail} onClose={() => setDetail(null)} />
    </div>
  );
}

function PickRow({
  title,
  sub,
  onPick,
}: {
  title: string;
  sub: string;
  onPick: () => void;
}) {
  return (
    <button
      onClick={onPick}
      className="flex w-full items-baseline justify-between gap-2 rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
    >
      <span className="text-sm text-papir">{title}</span>
      <span className="shrink-0 text-xs text-dim">{sub}</span>
    </button>
  );
}

function ResultCard<T>({
  result,
  title,
  sub,
  price,
  priceUrl,
  vitolas,
  excelHint,
  onOpen,
}: {
  result: PairingResult<T>;
  title: string;
  sub: string;
  price: string;
  priceUrl?: string | null;
  vitolas?: import("../types").Vitola[];
  excelHint: string | null | undefined;
  onOpen: () => void;
}) {
  const { t, lx } = useI18n();
  const [open, setOpen] = useState(false);
  const positive = result.reasons.filter((r) => r.score > 0);
  const negative = result.reasons.filter((r) => r.score < 0);
  return (
    <div className="rounded-xl border border-dim/15 bg-cedar p-3">
      <div className="flex items-center gap-3">
        <ScoreBand score={result.score} title={t("rate.matchWhat")} />
        <div
          onClick={onOpen}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && onOpen()}
          className="min-w-0 flex-1 cursor-pointer text-left"
        >
          <div className="truncate font-display text-[15px] text-papir">{title}</div>
          <div className="truncate text-xs text-dim">
            {sub} ·{" "}
            {priceUrl ? (
              <a
                href={priceUrl}
                target="_blank"
                rel="noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-zlato-2 underline decoration-zlato/40 underline-offset-2"
              >
                {price} ↗
              </a>
            ) : (
              price
            )}
          </div>
        </div>
        <button
          onClick={() => setOpen(!open)}
          className="shrink-0 rounded-md border border-dim/25 px-2 py-1 text-xs text-dim hover:border-zlato/50"
          aria-expanded={open}
          aria-label={t("pair.why")}
        >
          {open ? "▴" : "▾"}
        </button>
      </div>
      {vitolas && vitolas.length > 0 && (
        <div className="no-scrollbar mt-2 flex gap-1.5 overflow-x-auto">
          {vitolas.map((v) => (
            <span
              key={v.name}
              className="inline-flex shrink-0 items-center gap-1 rounded-md border border-dim/25 px-2 py-1 text-[11px] text-papir/85"
            >
              {v.name}
              {v.smokeTimeMin != null && (
                <span className="text-dim">⏱{v.smokeTimeMin}′</span>
              )}
              {v.priceEUR != null && (
                <span className="text-zlato-2">{v.priceEUR.toFixed(1)}€</span>
              )}
            </span>
          ))}
        </div>
      )}
      {excelHint && (
        <div className="mt-2 rounded-md border border-zlato/25 bg-zlato/10 px-2.5 py-1.5 text-xs text-zlato-2">
          ★ {t("pair.excelHint")}: {excelHint}
        </div>
      )}
      {open && (
        <ul className="mt-2 space-y-1 border-t border-dim/15 pt-2">
          {positive.map((r, i) => (
            <li key={i} className="flex gap-2 text-xs leading-relaxed text-papir/85">
              <span className="text-lista">＋</span> {lx(r.text)}
            </li>
          ))}
          {negative.map((r, i) => (
            <li key={i} className="flex gap-2 text-xs leading-relaxed text-dim">
              <span className="text-oxblood">−</span> {lx(r.text)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
