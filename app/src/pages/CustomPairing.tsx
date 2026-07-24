// Custom pairing prostor: ručno izaberi JEDNU cigaru i JEDNO piće -> % slaganja.
import { useMemo, useState } from "react";
import type { Cigar, Drink, ServeStyle } from "../types";
import { ALL_DRINKS, CIGARS, cigarInRegion, formatPrice } from "../data";
import { scorePairing } from "../engine/pairing";
import { curatedPairingOpinion } from "../engine/curatedOpinion";
import { pairingBlurb, pairingNarrative } from "../engine/pairingExplain";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Meter, ScoreBand, SearchInput } from "../components/ui";
import { ServeChips } from "../components/ServeChips";
import { useMarket } from "../store/market";

const norm = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

type Detail =
  | { kind: "cigar"; item: Cigar }
  | { kind: "drink"; item: Drink };

export function CustomPairing({
  onOpenDetail,
}: {
  onOpenDetail: (d: Detail) => void;
}) {
  const { t, lx, cn } = useI18n();
  const market = useMarket();
  const [cigar, setCigar] = useState<Cigar | null>(null);
  const [drink, setDrink] = useState<Drink | null>(null);
  const [serve, setServe] = useState<ServeStyle | undefined>(undefined);
  const [picking, setPicking] = useState<"cigar" | "drink" | null>("cigar");

  const marketCigars = useMemo(
    () => CIGARS.filter((c) => cigarInRegion(c, market)),
    [market],
  );
  const drinks = useMemo(() => ALL_DRINKS.filter((d) => d.pairable), []);

  const result = cigar && drink ? scorePairing(cigar, drink, undefined, serve) : null;
  const pairingOpinion = result
    ? curatedPairingOpinion(cigar!, drink!, result.reasons, result.score)
    : null;
  const blurb =
    result && cigar && drink
      ? pairingBlurb(cigar, drink, result.reasons, result.score)
      : null;
  const narrative =
    result && cigar && drink
      ? pairingNarrative(cigar, drink, result.reasons, result.score)
      : null;

  const verdictKey = (score: number): StringKey =>
    score >= 82
      ? "pair.verdict5"
      : score >= 68
        ? "pair.verdict4"
        : score >= 52
          ? "pair.verdict3"
          : score >= 38
            ? "pair.verdict2"
            : "pair.verdict1";

  return (
    <div className="pb-4">
      <div className="mt-4 mb-1 font-display text-sm uppercase tracking-[0.15em] text-zlato">
        {t("pair.customTitle")}
      </div>
      <p className="mb-3 text-xs text-dim">{t("pair.customHint")}</p>

      {/* dva slota */}
      <div className="grid grid-cols-2 gap-2">
        <Slot
          label={t("common.cigar")}
          filled={cigar ? `${cigar.brand} ${cigar.line}` : null}
          onClick={() => setPicking(picking === "cigar" ? null : "cigar")}
          active={picking === "cigar"}
        />
        <Slot
          label={t("common.drink")}
          filled={drink ? drink.name : null}
          onClick={() => setPicking(picking === "drink" ? null : "drink")}
          active={picking === "drink"}
        />
      </div>

      {/* serve style — mijenja rezultat (aroma/žestina) */}
      {drink && <ServeChips drink={drink} serve={serve} onChange={setServe} />}

      {/* rezultat slaganja */}
      {result && (
        <div className="mt-4 rounded-xl border border-zlato/40 bg-cedar p-4">
          <div className="flex items-center gap-4">
            <ScoreBand score={result.score} title={t("rate.matchWhat")} />
            <div className="min-w-0">
              <div className="font-display text-lg text-zlato-2">
                {t(verdictKey(result.score))}
              </div>
              <div className="text-xs text-dim">{t("rate.match")}</div>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
            <button
              onClick={() => onOpenDetail({ kind: "cigar", item: cigar! })}
              className="rounded-lg border border-dim/20 bg-humidor/40 p-2 text-left"
            >
              <div className="font-display text-papir">{cigar!.brand} {cigar!.line}</div>
              <div className="mt-1 flex gap-3">
                <Meter value={cigar!.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
                <Meter value={cigar!.body} label={t("common.body")} />
              </div>
            </button>
            <button
              onClick={() => onOpenDetail({ kind: "drink", item: drink! })}
              className="rounded-lg border border-dim/20 bg-humidor/40 p-2 text-left"
            >
              <div className="font-display text-papir">{drink!.name}</div>
              <div className="mt-1 flex gap-3">
                <Meter value={drink!.body} label={t("common.body")} />
                <Meter value={drink!.sweetness} label={t("common.sweetness")} accent="var(--color-lista)" />
              </div>
            </button>
          </div>

          {blurb && (
            <p className="mt-3 text-xs leading-relaxed text-papir/80">{lx(blurb)}</p>
          )}
          {pairingOpinion && (
            <div
              className={`mt-3 rounded-md border px-2.5 py-1.5 text-xs ${
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
          {narrative && (
            <p className="mt-2 text-xs leading-relaxed text-papir/85">{lx(narrative)}</p>
          )}

          <ul className="mt-3 space-y-1 border-t border-dim/15 pt-3">
            {result.reasons
              .filter((r) => r.score > 0)
              .map((r, i) => (
                <li key={`p${i}`} className="flex gap-2 text-xs leading-relaxed text-papir/85">
                  <span className="text-lista">＋</span> {lx(r.text)}
                </li>
              ))}
            {result.reasons
              .filter((r) => r.score < 0)
              .map((r, i) => (
                <li key={`n${i}`} className="flex gap-2 text-xs leading-relaxed text-dim">
                  <span className="text-oxblood">−</span> {lx(r.text)}
                </li>
              ))}
          </ul>
        </div>
      )}

      {/* birač (ispod, kad je slot aktivan) */}
      {picking && (
        <MiniPicker
          key={picking}
          items={
            picking === "cigar"
              ? marketCigars.map((c) => ({
                  id: c.id,
                  title: `${c.brand} ${c.line}`,
                  sub: `${c.wrapper} · ${cn(c.country)}`,
                  hay: `${c.brand} ${c.line} ${c.wrapper} ${c.country}`,
                  raw: c as Cigar | Drink,
                }))
              : drinks.map((d) => ({
                  id: d.id,
                  title: d.name,
                  sub: `${lx(STYLE_LABELS[d.style]) || d.style} · ${formatPrice(d.priceEUR)}`,
                  hay: `${d.name} ${d.style} ${d.region}`,
                  raw: d as Cigar | Drink,
                }))
          }
          onPick={(raw) => {
            if (picking === "cigar") {
              setCigar(raw as Cigar);
              setPicking(drink ? null : "drink");
            } else {
              setDrink(raw as Drink);
              setServe(undefined);
              setPicking(cigar ? null : "cigar");
            }
          }}
        />
      )}
    </div>
  );
}

function Slot({
  label,
  filled,
  active,
  onClick,
}: {
  label: string;
  filled: string | null;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-xl border p-3 text-left transition-colors ${
        active ? "border-zlato bg-zlato/10" : "border-dim/25 bg-cedar hover:border-zlato/40"
      }`}
    >
      <div className="text-micro uppercase tracking-widest text-dim">{label}</div>
      <div className={`mt-1 font-display text-sm ${filled ? "text-papir" : "text-dim/60"}`}>
        {filled ?? "—"}
      </div>
    </button>
  );
}

function MiniPicker({
  items,
  onPick,
}: {
  items: { id: string; title: string; sub: string; hay: string; raw: Cigar | Drink }[];
  onPick: (raw: Cigar | Drink) => void;
}) {
  const { t } = useI18n();
  const [q, setQ] = useState("");
  const filtered = useMemo(() => {
    const nq = norm(q);
    return items.filter((it) => !nq || norm(it.hay).includes(nq)).slice(0, 60);
  }, [items, q]);
  return (
    <div className="mt-3">
      <SearchInput value={q} onChange={setQ} placeholder={t("pair.search")} />
      <div className="mt-2 max-h-72 space-y-1.5 overflow-y-auto">
        {filtered.map((it) => (
          <button
            key={it.id}
            onClick={() => onPick(it.raw)}
            className="flex w-full items-baseline justify-between gap-2 rounded-lg border border-dim/15 bg-cedar px-3 py-2.5 text-left hover:border-zlato/40"
          >
            <span className="min-w-0 truncate text-sm text-papir">{it.title}</span>
            <span className="min-w-0 shrink truncate text-right text-xs text-dim">{it.sub}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
