// Humidor: više kutija, stvarno stanje (broj cigara) i kalendar dnevnika.
//
// Kolekcija odgovara na "poznajem li ovu liniju", humidor na "koliko ih imam
// večeras". Zato zaliha živi u zasebnoj pohrani i troši se kad zabilježiš večer.
import { useMemo, useState } from "react";
import type { Cigar, Drink } from "../types";
import { brandDisplayName, cigarForItemId, drinkById } from "../data";
import { useI18n, type StringKey } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { drinkNameLoc } from "../lib/drinkName";
import { removeJournalEntry, useCollection, type JournalEntry } from "../store/collection";
import {
  addHumidor,
  adjustStock,
  removeHumidor,
  renameHumidor,
  setActiveHumidor,
  setStock,
  useHumidors,
} from "../store/humidor";
import { useMarket } from "../store/market";
import {
  MONTH_NAMES_EN,
  MONTH_NAMES_HR,
  WEEKDAY_SHORT_EN,
  WEEKDAY_SHORT_HR,
  groupByDay,
  localDayKey,
  monthGrid,
  shiftMonth,
} from "../lib/calendar";

export function HumidorPage({
  onOpenCigar,
}: {
  onOpenCigar?: (cigar: Cigar) => void;
}) {
  const { t } = useI18n();
  const data = useHumidors();
  const [newName, setNewName] = useState("");
  const [renaming, setRenaming] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const active =
    data.humidors.find((h) => h.id === data.activeId) ?? data.humidors[0] ?? null;

  const rows = useMemo(() => {
    if (!active) return [];
    return data.stock
      .filter((s) => s.humidorId === active.id)
      .map((s) => ({ ...s, cigar: cigarForItemId(s.itemId) }))
      .sort((a, b) => {
        const an = a.cigar ? `${a.cigar.brand} ${a.cigar.line}` : a.itemId;
        const bn = b.cigar ? `${b.cigar.brand} ${b.cigar.line}` : b.itemId;
        return an.localeCompare(bn);
      });
  }, [data.stock, active]);

  const totalPieces = rows.reduce((sum, r) => sum + r.count, 0);

  const create = () => {
    addHumidor(newName || t("hum.defaultName"));
    setNewName("");
  };

  return (
    <div className="pb-4">
      {/* odabir humidora */}
      <div className="mt-4 flex flex-wrap items-center gap-2">
        {data.humidors.map((h) => (
          <Chip
            key={h.id}
            active={active?.id === h.id}
            onClick={() => setActiveHumidor(h.id)}
          >
            {h.name}
          </Chip>
        ))}
      </div>

      <div className="mt-3 flex gap-2">
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && create()}
          placeholder={t("hum.addHint")}
          className="min-w-0 flex-1 rounded-lg border border-dim/25 bg-cedar px-3 py-2 text-sm text-papir placeholder:text-dim/60 focus:border-zlato/60 focus:outline-none"
        />
        <button
          type="button"
          onClick={create}
          className="shrink-0 rounded-lg border border-zlato/40 px-3 py-2 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          + {t("hum.add")}
        </button>
      </div>

      {data.humidors.length === 0 && (
        <p className="mt-6 rounded-xl border border-dim/20 bg-cedar p-4 text-sm leading-relaxed text-dim">
          {t("hum.empty")}
        </p>
      )}

      {active && (
        <>
          <div className="mt-5 flex items-baseline justify-between gap-2">
            {renaming === active.id ? (
              <div className="flex flex-1 gap-2">
                <input
                  autoFocus
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      renameHumidor(active.id, renameValue);
                      setRenaming(null);
                    }
                    if (e.key === "Escape") setRenaming(null);
                  }}
                  className="min-w-0 flex-1 rounded-lg border border-zlato/40 bg-cedar px-3 py-1.5 text-sm text-papir focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => {
                    renameHumidor(active.id, renameValue);
                    setRenaming(null);
                  }}
                  className="shrink-0 rounded-lg border border-zlato/40 px-2.5 py-1.5 text-xs text-zlato"
                >
                  {t("coll.save")}
                </button>
              </div>
            ) : (
              <span className="font-display text-lg text-papir">
                {active.name}
                <span className="ml-2 text-sm text-zlato-2">
                  {totalPieces} {t("hum.cigarsCount")}
                </span>
              </span>
            )}
          </div>

          {renaming !== active.id && (
            <div className="mt-2 flex flex-wrap gap-2">
              <Chip
                onClick={() => {
                  setRenaming(active.id);
                  setRenameValue(active.name);
                }}
              >
                {t("hum.rename")}
              </Chip>
              <Chip
                onClick={() => {
                  if (window.confirm(t("hum.removeConfirm"))) removeHumidor(active.id);
                }}
              >
                {t("hum.remove")}
              </Chip>
            </div>
          )}

          <SectionTitle>{t("hum.stock")}</SectionTitle>
          {rows.length === 0 ? (
            <p className="text-sm leading-relaxed text-dim">{t("hum.stockEmpty")}</p>
          ) : (
            <div className="space-y-2">
              {rows.map((row) => (
                <StockRow
                  key={row.itemId}
                  cigar={row.cigar}
                  fallbackId={row.itemId}
                  count={row.count}
                  onAdjust={(d) => adjustStock(active.id, row.itemId, d)}
                  onClear={() => setStock(active.id, row.itemId, 0)}
                  onOpen={row.cigar && onOpenCigar ? () => onOpenCigar(row.cigar!) : undefined}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function StockRow({
  cigar,
  fallbackId,
  count,
  onAdjust,
  onClear,
  onOpen,
}: {
  cigar: Cigar | undefined;
  fallbackId: string;
  count: number;
  onAdjust: (delta: number) => void;
  onClear: () => void;
  onOpen?: () => void;
}) {
  const { t, cn } = useI18n();
  const market = useMarket();
  const title = cigar
    ? `${brandDisplayName(cigar.brand, market)} ${cigar.line}`
    : fallbackId;

  return (
    <div className="rounded-xl border border-dim/15 bg-cedar p-3">
      <div className="flex items-start justify-between gap-3">
        <button
          type="button"
          onClick={onOpen}
          disabled={!onOpen}
          className="min-w-0 flex-1 text-left disabled:cursor-default"
        >
          <div className="truncate font-display text-base text-papir">{title}</div>
          {cigar && (
            <div className="mt-0.5 truncate text-xs text-dim">
              {cigar.selectedVitola ?? cigar.vitola} · {cigar.wrapper} · {cn(cigar.country)}
            </div>
          )}
        </button>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            aria-label="−1"
            onClick={() => onAdjust(-1)}
            className="h-8 w-8 rounded-lg border border-dim/30 font-display text-base text-dim hover:border-zlato/50 hover:text-papir"
          >
            −
          </button>
          <span className="min-w-[2ch] text-center font-display text-lg text-zlato-2">
            {count}
          </span>
          <button
            type="button"
            aria-label="+1"
            onClick={() => onAdjust(1)}
            className="h-8 w-8 rounded-lg border border-dim/30 font-display text-base text-dim hover:border-zlato/50 hover:text-papir"
          >
            +
          </button>
        </div>
      </div>
      <button
        type="button"
        onClick={onClear}
        className="mt-2 text-xs text-oxblood/80 hover:text-oxblood"
      >
        {t("coll.delete")}
      </button>
    </div>
  );
}

/** Kalendar dnevnika: mjesec, dani sa zapisima, detalji odabranog dana. */
export function JournalCalendar() {
  const { t, lx, lang } = useI18n();
  const market = useMarket();
  const { journal } = useCollection();
  const today = new Date();
  const [cursor, setCursor] = useState({
    year: today.getFullYear(),
    month: today.getMonth(),
  });
  const [selected, setSelected] = useState<string | null>(localDayKey(today));

  const byDay = useMemo(() => groupByDay(journal), [journal]);
  const days = useMemo(
    () => monthGrid(cursor.year, cursor.month, today),
    // today se mijenja svakim renderom, ali samo kao "je li ovo današnji dan"
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [cursor.year, cursor.month],
  );

  const monthNames = lang === "hr" ? MONTH_NAMES_HR : MONTH_NAMES_EN;
  const weekdays = lang === "hr" ? WEEKDAY_SHORT_HR : WEEKDAY_SHORT_EN;

  const inMonthCount = days
    .filter((d) => d.inMonth)
    .reduce((sum, d) => sum + (byDay.get(d.key)?.length ?? 0), 0);

  const selectedEntries = selected ? (byDay.get(selected) ?? []) : [];

  return (
    <div className="pb-4">
      <div className="mt-4 flex items-center justify-between gap-2">
        <button
          type="button"
          aria-label={t("hum.prevMonth")}
          onClick={() => setCursor((c) => shiftMonth(c.year, c.month, -1))}
          className="rounded-lg border border-dim/30 px-3 py-1.5 text-sm text-dim hover:border-zlato/50 hover:text-papir"
        >
          ‹
        </button>
        <div className="text-center">
          <div className="font-display text-base capitalize text-papir">
            {monthNames[cursor.month]} {cursor.year}
          </div>
          <div className="text-micro text-dim">
            {inMonthCount} {t("hum.entriesThisMonth")}
          </div>
        </div>
        <button
          type="button"
          aria-label={t("hum.nextMonth")}
          onClick={() => setCursor((c) => shiftMonth(c.year, c.month, 1))}
          className="rounded-lg border border-dim/30 px-3 py-1.5 text-sm text-dim hover:border-zlato/50 hover:text-papir"
        >
          ›
        </button>
      </div>

      <div className="mt-3 grid grid-cols-7 gap-1">
        {weekdays.map((w) => (
          <div key={w} className="pb-1 text-center text-micro uppercase tracking-wider text-dim">
            {w}
          </div>
        ))}
        {days.map((day) => {
          const count = byDay.get(day.key)?.length ?? 0;
          const isSelected = selected === day.key;
          return (
            <button
              key={day.key}
              type="button"
              onClick={() => setSelected(day.key)}
              className={`relative aspect-square rounded-lg border text-sm transition-colors ${
                isSelected
                  ? "border-zlato bg-zlato/15 text-zlato-2"
                  : count > 0
                    ? "border-zlato/30 bg-cedar text-papir"
                    : "border-dim/15 bg-cedar/40 text-dim"
              } ${day.inMonth ? "" : "opacity-40"} ${
                day.isToday && !isSelected ? "ring-1 ring-inset ring-dim/50" : ""
              }`}
            >
              {day.dayOfMonth}
              {count > 0 && (
                <span
                  className="absolute inset-x-0 bottom-1 text-micro text-zlato"
                  aria-hidden
                >
                  {"•".repeat(Math.min(count, 3))}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <SectionTitle>{t("coll.journal")}</SectionTitle>
      {selectedEntries.length === 0 ? (
        <p className="text-sm leading-relaxed text-dim">
          {selected ? t("hum.calendarDayEmpty") : t("hum.calendarPickDay")}
        </p>
      ) : (
        <div className="space-y-2">
          {selectedEntries.map((entry) => (
            <JournalCard
              key={entry.id}
              entry={entry}
              market={market}
              lang={lang}
              lx={lx}
              t={t}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function JournalCard({
  entry,
  market,
  lang,
  lx,
  t,
}: {
  entry: JournalEntry;
  market: ReturnType<typeof useMarket>;
  lang: "hr" | "en";
  lx: (text: { hr: string; en: string }) => string;
  t: (key: StringKey) => string;
}) {
  const cigar = cigarForItemId(entry.cigarId);
  const drink: Drink | undefined = drinkById(entry.drinkId);
  // 24-satni zapis na hrvatskom; engleski ostaje na 12-satnom
  const time = new Date(entry.date).toLocaleTimeString(
    lang === "hr" ? "hr-HR" : "en-GB",
    { hour: "2-digit", minute: "2-digit" },
  );

  return (
    <div className="rounded-xl border border-dim/15 bg-cedar p-3">
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-display text-sm text-papir">
          {cigar
            ? `${brandDisplayName(cigar.brand, market)} ${cigar.line}${
                cigar.selectedVitola ? ` ${cigar.selectedVitola}` : ""
              }`
            : entry.cigarId}
          <span className="text-zlato"> × </span>
          {drink ? lx(drinkNameLoc(drink)) : entry.drinkId}
        </span>
        {entry.rating != null && (
          <span className="shrink-0 text-sm text-zlato-2">{entry.rating}/10</span>
        )}
      </div>
      <div className="mt-1 text-xs text-dim">
        {time}
        {entry.note && ` — ${entry.note}`}
      </div>
      <button
        type="button"
        onClick={() => removeJournalEntry(entry.id)}
        className="mt-2 text-xs text-oxblood/80 hover:text-oxblood"
      >
        {t("coll.delete")}
      </button>
    </div>
  );
}
