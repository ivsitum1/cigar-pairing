import { useEffect, useMemo, useState } from "react";
import type { Cigar, Drink, DrinkCategory, PairingResult, ServeStyle, Vitola } from "../types";
import { ALL_DRINKS, CIGARS, cigarInRegion, cigarLinkForMarket, cigarPriceForMarket, drinkById, formatPrice, resolveCigarId } from "../data";
import { pairCigarsForDrink, pairDrinksForCigar } from "../engine/pairing";
import { buildPrefs } from "../engine/personal";
import { curatedPairingOpinion } from "../engine/curatedOpinion";
import { pairingBlurb } from "../engine/pairingExplain";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, Meter, ScoreBand, SearchInput, SectionTitle } from "../components/ui";
import { getItemState, useCollection } from "../store/collection";
import { DetailSheet } from "../components/DetailSheet";
import { EveningSessionSheet } from "../components/EveningSessionSheet";
import { MarketFilter } from "../components/MarketFilter";
import { ServeChips } from "../components/ServeChips";
import { buildShareCardModel, sharePairing } from "../lib/shareCard";
import { ritualHint } from "../lib/cigarRitual";
import { OcrScan } from "../components/OcrScan";
import { VitolaPicker } from "../components/VitolaPicker";
import { applyVitola, needsVitolaPick, uniqueVitolas } from "../lib/cigarVitola";
import { drinkBuyLink } from "../lib/drinkBuyLink";
import { drinkNameLoc, drinkNameHaystack } from "../lib/drinkName";
import { useMarket } from "../store/market";
import { consumePairingIntent, usePairingNavVersion } from "../store/pairingNav";
import { navigate, useRoute } from "../store/route";
import { CustomPairing } from "./CustomPairing";

type Mode = "cigarToDrink" | "drinkToCigar" | "custom";
type Occasion = "any" | "morning" | "afternoon" | "evening";

// prilika filtrira pica po punoci: jutro uz kavu/lagane sippere, vecer uz bogate
const OCCASION_KEEP: Record<Occasion, (d: Drink) => boolean> = {
  any: () => true,
  morning: (d) => d.category === "coffee" || d.body <= 2,
  afternoon: (d) => d.category === "coffee" || d.body <= 3,
  evening: (d) => d.category === "coffee" || d.body >= 3,
};

// pretraga neosjetljiva na naglaske i velika/mala slova
const norm = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
// cigara -> po jedan prijedlog; gin zadnji; kava i tequila pune kartice
const SUGGEST_CATEGORIES: DrinkCategory[] = [
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
];

export function PairingPage() {
  const { t, lx, cn, lang, sv } = useI18n();
  const collection = useCollection();
  const [mode, setMode] = useState<Mode>("cigarToDrink");
  const [occasion, setOccasion] = useState<Occasion>("any");

  // osobni afiniteti iz ocijenjenih zapisa dnevnika (sve lokalno)
  const prefs = useMemo(() => {
    const rated = collection.journal.map((j) => ({
      rating: j.rating,
      drinkStyle: drinkById(j.drinkId)?.style,
      cigarBrand: resolveCigarId(j.cigarId)?.brand,
    }));
    const built = buildPrefs(rated);
    return built.entries > 0 ? built : undefined;
  }, [collection.journal]);
  const [query, setQuery] = useState("");
  const [selectedCigar, setSelectedCigar] = useState<Cigar | null>(null);
  const [pendingCigar, setPendingCigar] = useState<Cigar | null>(null);
  const [selectedDrink, setSelectedDrink] = useState<Drink | null>(null);
  const [serve, setServe] = useState<ServeStyle | undefined>(undefined);
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
  const [sessionOpen, setSessionOpen] = useState(false);
  const [sessionFlash, setSessionFlash] = useState<string | null>(null);
  const pairingNavVersion = usePairingNavVersion();
  const route = useRoute();

  const selected = mode === "cigarToDrink" ? selectedCigar : selectedDrink;

  const marketCigars = useMemo(
    () =>
      CIGARS.filter(
        (c) =>
          cigarInRegion(c, market) &&
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
      (d) =>
        d.pairable &&
        (!q || norm(`${drinkNameHaystack(d)} ${d.style} ${d.region}`).includes(q)),
    );
  }, [mode, query, marketCigars]);

  // cigara -> po jedan najbolji prijedlog po kategoriji (gin zadnji)
  const drinkSuggestions = useMemo(() => {
    if (mode !== "cigarToDrink" || !selectedCigar) return null;
    let drinks = ALL_DRINKS;
    if (onlyMine) drinks = drinks.filter((d) => getItemState(d.id).owned);
    if (occasion !== "any") drinks = drinks.filter(OCCASION_KEEP[occasion]);
    const ranked = pairDrinksForCigar(selectedCigar, drinks, prefs);
    const perCategory = (cat: DrinkCategory) =>
      ranked.filter((r) => r.item.category === cat);
    return {
      cards: SUGGEST_CATEGORIES.map((cat) => {
        const list = perCategory(cat);
        const idx = list.length ? (cycle[cat] ?? 0) % list.length : 0;
        return { category: cat, result: list[idx], total: list.length };
      }),
    };
  }, [mode, selectedCigar, onlyMine, cycle, occasion, prefs]);

  // pice -> tocno 3 cigare RAZLICITIH brendova (cycle pomice prozor za 3)
  const cigarSuggestions = useMemo(() => {
    if (mode !== "drinkToCigar" || !selectedDrink) return null;
    let cigars = marketCigars;
    if (onlyMine) cigars = cigars.filter((c) => getItemState(c.id).owned);
    const ranked = pairCigarsForDrink(selectedDrink, cigars, prefs, serve);
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
  }, [mode, selectedDrink, onlyMine, cycle, marketCigars, prefs, serve]);

  // kandidati za večernji zapis: trenutno vidljivi prijedlozi
  const sessionDrinks: Drink[] = useMemo(() => {
    if (mode === "drinkToCigar" && selectedDrink) return [selectedDrink];
    return (
      drinkSuggestions?.cards
        .map((c) => c.result?.item)
        .filter((d): d is Drink => !!d) ?? []
    );
  }, [mode, selectedDrink, drinkSuggestions]);

  const sessionCigars: Cigar[] = useMemo(() => {
    if (mode === "cigarToDrink" && selectedCigar) return [selectedCigar];
    return cigarSuggestions?.window.map((r) => r.item) ?? [];
  }, [mode, selectedCigar, cigarSuggestions]);

  const canLogEvening =
    selected != null && sessionCigars.length > 0 && sessionDrinks.length > 0;

  const reset = () => {
    setSelectedCigar(null);
    setPendingCigar(null);
    setSelectedDrink(null);
    setServe(undefined);
    setQuery("");
    setCycle({});
    navigate({ page: "pairing" }, { replace: true });
  };

  const pickCigar = (raw: Cigar) => {
    const cigar = resolveCigarId(raw.id) ?? raw;
    if (needsVitolaPick(cigar)) {
      setPendingCigar(cigar);
      return;
    }
    const vitolas = uniqueVitolas(cigar);
    setSelectedCigar(vitolas.length === 1 ? applyVitola(cigar, vitolas[0]) : cigar);
    navigate({ page: "pairing", pair: { kind: "cigar", id: cigar.id } });
  };

  const confirmVitola = (vitola: Vitola) => {
    if (!pendingCigar) return;
    setSelectedCigar(applyVitola(pendingCigar, vitola));
    navigate({ page: "pairing", pair: { kind: "cigar", id: pendingCigar.id } });
    setPendingCigar(null);
  };

  const pickDrink = (drink: Drink) => {
    setSelectedDrink(drink);
    setServe(undefined);
    navigate({ page: "pairing", pair: { kind: "drink", id: drink.id } });
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
      const cigar = resolveCigarId(intent.cigar.id) ?? intent.cigar;
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
      setServe(undefined);
      setQuery(intent.drink.name);
    }
  }, [pairingNavVersion]);

  // deep-link i back tipka: hash je izvor istine za ODABRANU stavku.
  // Odabir kroz UI zove navigate(), pa se ovdje samo uskladjujemo kad se
  // hash promijeni izvana (podijeljeni link, back/forward).
  useEffect(() => {
    if (route.page !== "pairing") return;
    const pair = route.pair;
    if (!pair) {
      if (selectedCigar || selectedDrink || pendingCigar) {
        setSelectedCigar(null);
        setPendingCigar(null);
        setSelectedDrink(null);
        setQuery("");
        setCycle({});
      }
      return;
    }
    if (pair.kind === "cigar") {
      if (selectedCigar?.id === pair.id || pendingCigar?.id === pair.id) return;
      const cigar = resolveCigarId(pair.id);
      if (!cigar) return;
      setMode("cigarToDrink");
      setSelectedDrink(null);
      setCycle({});
      setQuery(`${cigar.brand} ${cigar.line}`);
      const vitolas = uniqueVitolas(cigar);
      setSelectedCigar(vitolas.length === 1 ? applyVitola(cigar, vitolas[0]) : cigar);
    } else {
      if (selectedDrink?.id === pair.id) return;
      const drink = drinkById(pair.id);
      if (!drink) return;
      setMode("drinkToCigar");
      setSelectedCigar(null);
      setPendingCigar(null);
      setCycle({});
      setQuery(drink.name);
      setSelectedDrink(drink);
      setServe(undefined);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [route]);

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
            className={`rounded-lg border py-2.5 font-display text-micro uppercase tracking-[0.12em] transition-colors ${
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

      {/* market birac — uvijek vidljiv (i u custom načinu) */}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <MarketFilter label={t("pair.market")} className="min-w-0 flex-1" />
        {mode !== "custom" && (
          <Chip
            active={showPrefs || excludedCountries.length > 0 || excludedBrands.length > 0}
            onClick={() => setShowPrefs(!showPrefs)}
          >
            ⚙ {excludedCountries.length + excludedBrands.length || ""}
          </Chip>
        )}
      </div>

      {/* preferencije: zemlje/brendovi koje NE zelis u prijedlozima */}
      {mode !== "custom" && showPrefs && (
        <div className="mt-2 rounded-xl border border-dim/20 bg-cedar p-3">
          <div className="mb-1 font-display text-micro uppercase tracking-[0.2em] text-zlato">
            {t("pair.prefs")}
          </div>
          <div className="mb-2 text-micro text-dim">{t("pair.prefsHint")}</div>
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
                  const c = resolveCigarId(id) ?? marketCigars.find((x) => x.id === id);
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
                  title={lx(drinkNameLoc(item as Drink))}
                  sub={lx(STYLE_LABELS[(item as Drink).style]) || (item as Drink).style}
                  onPick={() => pickDrink(item as Drink)}
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
                    : lx(drinkNameLoc(selected as Drink))}
                </div>
                {mode === "cigarToDrink" && (
                  <div className="mt-0.5 text-xs text-dim">
                    {(selected as Cigar).vitola} · {(selected as Cigar).wrapper} · {cn((selected as Cigar).country)}
                  </div>
                )}
                {mode === "cigarToDrink" &&
                  ((selected as Cigar).profileEstimated ||
                    (selected as Cigar).flavorTags.length === 0) && (
                    <div
                      className="mt-1 text-micro uppercase tracking-wider text-dim/80"
                      title={t("common.estimatedProfile")}
                    >
                      ≈ {t("common.estimatedProfile")}
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
                {mode === "cigarToDrink" &&
                  (() => {
                    const rh = ritualHint((selected as Cigar).smokeTimeMin, lang);
                    return rh ? (
                      <div className="mt-2 text-micro leading-snug text-dim/85">
                        {rh.icon} {rh.text}
                      </div>
                    ) : null;
                  })()}
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
            {mode === "cigarToDrink" &&
              (["morning", "afternoon", "evening"] as const).map((o) => (
                <Chip
                  key={o}
                  active={occasion === o}
                  onClick={() => setOccasion(occasion === o ? "any" : o)}
                >
                  {t(`occ.${o}` as StringKey)}
                </Chip>
              ))}
          </div>

          {mode === "drinkToCigar" && selectedDrink && (
            <ServeChips drink={selectedDrink} serve={serve} onChange={setServe} />
          )}

          <SectionTitle>{t("pair.suggestions")}</SectionTitle>

          {/* CIGARA -> kategorije (gin zadnji) */}
          {drinkSuggestions && (
            <div className="space-y-3">
              {drinkSuggestions.cards.map(({ category, result, total }) => (
                <div key={category}>
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-display text-micro uppercase tracking-[0.2em] text-oxblood">
                      {t(`cat.${category}` as StringKey)}
                    </span>
                    {total > 1 && (
                      <button
                        onClick={() =>
                          setCycle((c) => ({ ...c, [category]: (c[category] ?? 0) + 1 }))
                        }
                        className="text-micro text-dim hover:text-zlato-2"
                      >
                        ↻ {t("pair.next")}
                      </button>
                    )}
                  </div>
                  {result && selectedCigar ? (
                    <ResultCard
                      result={result}
                      cigar={selectedCigar as Cigar}
                      drink={result.item}
                      title={lx(drinkNameLoc(result.item))}
                      sub={`${t(`cat.${category}` as StringKey)} · ${lx(STYLE_LABELS[result.item.style]) || result.item.style}${
                        result.item.serving?.best
                          ? ` · ${t("serve.best")}: ${sv(result.item.serving.best)}`
                          : ""
                      }`}
                      price={formatPrice(result.item.priceEUR)}
                      priceUrl={drinkBuyLink(result.item).href}
                      onOpen={() => setDetail({ kind: "drink", item: result.item })}
                    />
                  ) : (
                    <p className="rounded-xl border border-dim/15 bg-cedar p-3 text-xs text-dim">
                      {t("pair.noResults")}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* PICE -> 3 cigare */}
          {cigarSuggestions && (
            <div className="space-y-3">
              {cigarSuggestions.total > 3 && (
                <div className="flex justify-end">
                  <button
                    onClick={() => setCycle((c) => ({ ...c, cigars: (c["cigars"] ?? 0) + 1 }))}
                    className="text-micro text-dim hover:text-zlato-2"
                  >
                    ↻ {t("pair.next")}
                  </button>
                </div>
              )}
              {cigarSuggestions.window.length === 0 && (
                <p className="text-sm text-dim">{t("pair.noResults")}</p>
              )}
              {cigarSuggestions.window.map((r) => {
                if (!selectedDrink) return null;
                const mp = cigarPriceForMarket(r.item, market);
                const priceStr =
                  mp.price != null
                    ? `${mp.fromMany ? t("price.from") + " " : ""}${mp.price.toFixed(mp.price % 1 ? 2 : 0)} €`
                    : t("price.check");
                return (
                  <ResultCard
                    key={r.item.id}
                    result={r}
                    cigar={r.item}
                    drink={selectedDrink}
                    title={`${r.item.brand} ${r.item.line}`}
                    sub={`${r.item.wrapper}${
                      r.item.profileEstimated || r.item.flavorTags.length === 0
                        ? ` · ≈ ${t("common.estimatedShort")}`
                        : ""
                    }`}
                    price={priceStr}
                    priceUrl={cigarLinkForMarket(r.item, market)}
                    vitolas={r.item.vitolas}
                    serve={serve}
                    onOpen={() => setDetail({ kind: "cigar", item: r.item })}
                  />
                );
              })}
            </div>
          )}

          {canLogEvening && (
            <button
              onClick={() => setSessionOpen(true)}
              className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
            >
              {t("session.log")}
            </button>
          )}
          {sessionFlash && (
            <p className="mt-2 text-center text-xs text-zlato-2">{sessionFlash}</p>
          )}
        </>
      )}

      {sessionOpen && (
        <EveningSessionSheet
          cigars={sessionCigars}
          drinks={sessionDrinks}
          initialCigarId={sessionCigars[0]?.id}
          initialDrinkId={sessionDrinks[0]?.id}
          onClose={() => setSessionOpen(false)}
          onSaved={() => {
            setSessionFlash(t("session.saved"));
            setTimeout(() => setSessionFlash(null), 2500);
          }}
        />
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
      <span className="min-w-0 truncate text-sm text-papir">{title}</span>
      <span className="min-w-0 shrink truncate text-right text-xs text-dim">{sub}</span>
    </button>
  );
}

function ResultCard({
  result,
  cigar,
  drink,
  title,
  sub,
  price,
  priceUrl,
  vitolas,
  serve,
  onOpen,
}: {
  result: PairingResult<Cigar> | PairingResult<Drink>;
  cigar: Cigar;
  drink: Drink;
  title: string;
  sub: string;
  price: string;
  priceUrl?: string | null;
  vitolas?: import("../types").Vitola[];
  serve?: ServeStyle;
  onOpen: () => void;
}) {
  const { t, lx, lang } = useI18n();
  const [open, setOpen] = useState(false);
  const [shareMsg, setShareMsg] = useState<string | null>(null);
  const positive = result.reasons.filter((r) => r.score > 0);
  const negative = result.reasons.filter((r) => r.score < 0);

  const onShare = async () => {
    const model = buildShareCardModel(cigar, drink, serve, result.score, result.reasons, lang);
    try {
      const how = await sharePairing(model);
      setShareMsg(t(how === "shared" ? "share.shared" : "share.downloaded"));
    } catch {
      setShareMsg(t("share.failed"));
    }
    setTimeout(() => setShareMsg(null), 2500);
  };
  const pairingOpinion = curatedPairingOpinion(
    cigar,
    drink,
    result.reasons,
    result.score,
  );
  const blurb = pairingBlurb(cigar, drink, result.reasons, result.score);
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
          <div className="truncate font-display text-base text-papir">{title}</div>
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
          onClick={onShare}
          className="shrink-0 rounded-md border border-dim/25 px-2 py-1 text-xs text-dim hover:border-zlato/50"
          aria-label={t("share.pairing")}
          title={t("share.pairing")}
        >
          ⤴
        </button>
        <button
          onClick={() => setOpen(!open)}
          className="shrink-0 rounded-md border border-dim/25 px-2 py-1 text-xs text-dim hover:border-zlato/50"
          aria-expanded={open}
          aria-label={t("pair.why")}
        >
          {open ? "▴" : "▾"}
        </button>
      </div>
      {shareMsg && (
        <p className="mt-2 text-center text-micro text-zlato-2">{shareMsg}</p>
      )}
      {vitolas && vitolas.length > 0 && (
        <div className="no-scrollbar mt-2 flex gap-1.5 overflow-x-auto">
          {vitolas.map((v) => (
            <span
              key={v.name}
              className="inline-flex shrink-0 items-center gap-1 rounded-md border border-dim/25 px-2 py-1 text-micro text-papir/85"
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
      <p className="mt-2 text-xs leading-relaxed text-papir/80">{lx(blurb)}</p>
      {pairingOpinion && (
        <div
          className={`mt-2 rounded-md border px-2.5 py-1.5 text-xs ${
            pairingOpinion.tone === "praise"
              ? "border-zlato/25 bg-zlato/10 text-zlato-2"
              : "border-oxblood/50 bg-oxblood/10 text-papir/90"
          }`}
        >
          {pairingOpinion.tone === "praise"
            ? `★ ${t("pair.excelHint")}`
            : `⚠ ${t("pair.curatedWarn")}`}
          : {lx(pairingOpinion.text)}
        </div>
      )}
      {open && (
        <div className="mt-2 space-y-2 border-t border-dim/15 pt-2">
          <ul className="space-y-1">
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
        </div>
      )}
    </div>
  );
}
