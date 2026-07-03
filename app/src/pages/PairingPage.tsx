import { useMemo, useState } from "react";
import type { Cigar, Drink, DrinkCategory, PairingResult } from "../types";
import { ALL_DRINKS, CIGARS, formatPrice } from "../data";
import { pairCigarsForDrink, pairDrinksForCigar } from "../engine/pairing";
import { useI18n, STYLE_LABELS } from "../i18n";
import { Chip, Meter, ScoreBand, SearchInput, SectionTitle } from "../components/ui";
import { getItemState, useCollection } from "../store/collection";
import { DetailSheet } from "../components/DetailSheet";

type Mode = "cigarToDrink" | "drinkToCigar";
const CATEGORIES: (DrinkCategory | "all")[] = ["all", "rum", "whisky", "brandy", "coffee"];

export function PairingPage() {
  const { t, lx } = useI18n();
  useCollection();
  const [mode, setMode] = useState<Mode>("cigarToDrink");
  const [query, setQuery] = useState("");
  const [selectedCigar, setSelectedCigar] = useState<Cigar | null>(null);
  const [selectedDrink, setSelectedDrink] = useState<Drink | null>(null);
  const [category, setCategory] = useState<DrinkCategory | "all">("all");
  const [onlyMine, setOnlyMine] = useState(false);
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);

  const selected = mode === "cigarToDrink" ? selectedCigar : selectedDrink;

  const pickList = useMemo(() => {
    const q = query.toLowerCase();
    if (mode === "cigarToDrink") {
      return CIGARS.filter(
        (c) =>
          !q ||
          `${c.brand} ${c.line} ${c.vitola}`.toLowerCase().includes(q),
      ).slice(0, 30);
    }
    return ALL_DRINKS.filter(
      (d) => d.pairable && (!q || d.name.toLowerCase().includes(q)),
    ).slice(0, 30);
  }, [mode, query]);

  const results = useMemo(() => {
    if (mode === "cigarToDrink" && selectedCigar) {
      let drinks = ALL_DRINKS;
      if (category !== "all") drinks = drinks.filter((d) => d.category === category);
      if (onlyMine) drinks = drinks.filter((d) => getItemState(d.id).owned);
      return pairDrinksForCigar(selectedCigar, drinks).slice(0, 12);
    }
    if (mode === "drinkToCigar" && selectedDrink) {
      let cigars = CIGARS;
      if (onlyMine) cigars = cigars.filter((c) => getItemState(c.id).owned);
      return pairCigarsForDrink(selectedDrink, cigars).slice(0, 12);
    }
    return null;
  }, [mode, selectedCigar, selectedDrink, category, onlyMine]);

  const reset = () => {
    setSelectedCigar(null);
    setSelectedDrink(null);
    setQuery("");
  };

  return (
    <div className="pb-4">
      {/* mode toggle */}
      <div className="mt-4 grid grid-cols-2 gap-2">
        {(["cigarToDrink", "drinkToCigar"] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              reset();
            }}
            className={`rounded-lg border py-2.5 font-display text-xs uppercase tracking-[0.15em] transition-colors ${
              mode === m
                ? "border-zlato bg-zlato/15 text-zlato-2"
                : "border-dim/25 text-dim hover:border-zlato/40"
            }`}
          >
            {t(m === "cigarToDrink" ? "pair.cigarToDrink" : "pair.drinkToCigar")}
          </button>
        ))}
      </div>

      {/* picker */}
      {!selected && (
        <>
          <div className="mt-4">
            <SearchInput
              value={query}
              onChange={setQuery}
              placeholder={`${t(mode === "cigarToDrink" ? "pair.pickCigar" : "pair.pickDrink")} — ${t("pair.search")}`}
            />
          </div>
          <div className="mt-3 space-y-1.5">
            {pickList.map((item) =>
              mode === "cigarToDrink" ? (
                <PickRow
                  key={item.id}
                  title={`${(item as Cigar).brand} ${(item as Cigar).vitola}`}
                  sub={`${(item as Cigar).wrapper} · ${(item as Cigar).country}`}
                  onPick={() => setSelectedCigar(item as Cigar)}
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

      {/* selected + results */}
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

          {/* filteri rezultata */}
          <div className="no-scrollbar mt-3 flex gap-2 overflow-x-auto">
            {mode === "cigarToDrink" &&
              CATEGORIES.map((c) => (
                <Chip key={c} active={category === c} onClick={() => setCategory(c)}>
                  {c === "all" ? t("common.all") : t(`cat.${c}` as const)}
                </Chip>
              ))}
            <Chip active={onlyMine} onClick={() => setOnlyMine(!onlyMine)}>
              {t("pair.onlyMine")}
            </Chip>
          </div>

          <SectionTitle>{t("pair.why")}</SectionTitle>
          {results && results.length === 0 && (
            <p className="text-sm text-dim">{t("pair.noResults")}</p>
          )}
          <div className="space-y-2">
            {results?.map((r) =>
              mode === "cigarToDrink" ? (
                <ResultCard
                  key={r.item.id}
                  result={r as PairingResult<Drink>}
                  title={(r.item as Drink).name}
                  sub={lx(STYLE_LABELS[(r.item as Drink).style]) || ""}
                  price={formatPrice((r.item as Drink).priceEUR)}
                  excelHint={(r.item as Drink).cigarHint}
                  onOpen={() => setDetail({ kind: "drink", item: r.item as Drink })}
                />
              ) : (
                <ResultCard
                  key={r.item.id}
                  result={r as PairingResult<Cigar>}
                  title={`${(r.item as Cigar).brand} ${(r.item as Cigar).line}`}
                  sub={`${(r.item as Cigar).wrapper} · ${(r.item as Cigar).vitola}`}
                  price={formatPrice((r.item as Cigar).priceEUR)}
                  excelHint={null}
                  onOpen={() => setDetail({ kind: "cigar", item: r.item as Cigar })}
                />
              ),
            )}
          </div>
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
  excelHint,
  onOpen,
}: {
  result: PairingResult<T>;
  title: string;
  sub: string;
  price: string;
  excelHint: string | null | undefined;
  onOpen: () => void;
}) {
  const { t } = useI18n();
  const { lx } = useI18n();
  const [open, setOpen] = useState(false);
  const positive = result.reasons.filter((r) => r.score > 0);
  const negative = result.reasons.filter((r) => r.score < 0);
  return (
    <div className="rounded-xl border border-dim/15 bg-cedar p-3">
      <div className="flex items-center gap-3">
        <ScoreBand score={result.score} />
        <button onClick={onOpen} className="min-w-0 flex-1 text-left">
          <div className="truncate font-display text-[15px] text-papir">{title}</div>
          <div className="truncate text-xs text-dim">
            {sub} · {price}
          </div>
        </button>
        <button
          onClick={() => setOpen(!open)}
          className="shrink-0 rounded-md border border-dim/25 px-2 py-1 text-xs text-dim hover:border-zlato/50"
          aria-expanded={open}
        >
          {open ? "▴" : "▾"}
        </button>
      </div>
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
