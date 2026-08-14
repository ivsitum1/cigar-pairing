// Humidor: više kutija, stvarno stanje (broj cigara) i kalendar dnevnika.
//
// Kolekcija odgovara na "poznajem li ovu liniju", humidor na "koliko ih imam
// večeras". Zato zaliha živi u zasebnoj pohrani i troši se kad zabilježiš večer.
import { useMemo, useState } from "react";
import type { Cigar, Drink, Vitola } from "../types";
import { ALL_DRINKS, brandDisplayName, cigarForItemId, drinkById } from "../data";
import { useI18n, type StringKey } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { DrinkRow } from "../components/cards";
import { LastCigarPrompt } from "../components/LastCigarPrompt";
import { VitolaPicker } from "../components/VitolaPicker";
import { shouldOfferWishlist } from "../lib/lastCigar";
import { drinkNameLoc } from "../lib/drinkName";
import { removeJournalEntry, updateJournalEntry, useCollection, type JournalEntry } from "../store/collection";
import {
  addHumidor,
  adjustStock,
  moveStock,
  removeHumidor,
  renameHumidor,
  setActiveHumidor,
  setStock,
  useHumidors,
} from "../store/humidor";
import { useMarket } from "../store/market";
import { dedupeCollectionCigarIds, parseCigarItemId } from "../lib/cigarItemId";
import {
  groupStockByLine,
  stockNeedsVitola,
  stockVitolaName,
  vitolaStockId,
  vitolasNotInStock,
} from "../lib/humidorVitola";
import { uniqueVitolas } from "../lib/cigarVitola";
import {
  claimOwnedForStock,
  releaseOwnedIfEmpty,
  transferOwnedToVitola,
} from "../lib/stockOwnership";
import {
  MONTH_NAMES_EN,
  MONTH_NAMES_HR,
  WEEKDAY_SHORT_EN,
  WEEKDAY_SHORT_HR,
  applyLocalDayToIso,
  groupByDay,
  localDayKey,
  monthGrid,
  shiftMonth,
} from "../lib/calendar";

export function HumidorPage({
  onOpenCigar,
  onOpenDrink,
}: {
  onOpenCigar?: (cigar: Cigar) => void;
  onOpenDrink?: (drink: Drink) => void;
}) {
  const { t } = useI18n();
  const market = useMarket();
  const data = useHumidors();
  const collection = useCollection();
  const [newName, setNewName] = useState("");
  const [renaming, setRenaming] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  // zadnja skinuta cigara — ponuda za listu želja
  const [lastCigarId, setLastCigarId] = useState<string | null>(null);
  // izbor vitole: dodavanje nove veličine ili određivanje stare zalihe po liniji
  const [pick, setPick] = useState<{ line: Cigar; fromItemId?: string } | null>(null);

  const ownedBottles = useMemo(() => {
    return ALL_DRINKS.filter((d) => collection.items[d.id]?.owned);
  }, [collection.items]);

  const active =
    data.humidors.find((h) => h.id === data.activeId) ?? data.humidors[0] ?? null;

  /**
   * Zaliha ide po vitoli: jedna kartica po liniji, unutar nje red za svaku
   * veličinu (3 Robusta, 2 Figurada, 1 Toro). Stara zaliha vođena po liniji
   * ostaje vidljiva kao red bez određene vitole, s gumbom koji je razrješava.
   */
  const groups = useMemo(() => {
    if (!active) return [];
    const mine = data.stock.filter((s) => s.humidorId === active.id);
    return groupStockByLine(mine)
      .map((group) => {
        const line = cigarForItemId(group.cigarId);
        const title = line
          ? `${brandDisplayName(line.brand, market)} ${line.line}`
          : group.cigarId;
        const rows = group.entries
          .map((s) => ({
            itemId: s.itemId,
            count: s.count,
            cigar: cigarForItemId(s.itemId),
            vitola: stockVitolaName(line, s.itemId),
            needsVitola: stockNeedsVitola(line, s.itemId),
          }))
          .sort((a, b) => (a.vitola ?? "").localeCompare(b.vitola ?? ""));
        const addable = line ? vitolasNotInStock(line, group.entries.map((s) => s.itemId)) : [];
        return {
          ...group,
          line,
          title,
          rows,
          // linija s jednim formatom nema što birati
          addableVitolas: line && uniqueVitolas(line).length > 1 ? addable : [],
        };
      })
      .sort((a, b) => a.title.localeCompare(b.title));
  }, [data.stock, active, market]);

  const totalPieces = groups.reduce((sum, g) => sum + g.total, 0);

  const applyPick = (vitola: Vitola) => {
    if (!pick || !active) return;
    const target = vitolaStockId(pick.line, vitola);
    if (pick.fromItemId) {
      // premještanje nije trošenje — zaliha samo dobiva ime
      moveStock(active.id, pick.fromItemId, target);
    } else {
      adjustStock(active.id, target, 1);
    }
    claimOwnedForStock(target);
    setPick(null);
  };

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
          {groups.length === 0 ? (
            <p className="text-sm leading-relaxed text-dim">{t("hum.stockEmpty")}</p>
          ) : (
            <div className="space-y-2">
              {groups.map((group) => (
                <LineStockCard
                  key={group.cigarId}
                  title={group.title}
                  total={group.total}
                  rows={group.rows}
                  canAddVitola={group.addableVitolas.length > 0}
                  onAddVitola={() => group.line && setPick({ line: group.line })}
                  onSetVitola={(itemId) =>
                    group.line && setPick({ line: group.line, fromItemId: itemId })
                  }
                  onAdjust={(itemId, d) => {
                    adjustStock(active.id, itemId, d);
                    if (d > 0) claimOwnedForStock(itemId);
                    // ručno skidanje je isto trošenje: „Imam” prati zalihu,
                    // a zadnja cigara nudi listu želja
                    if (d < 0) {
                      releaseOwnedIfEmpty(itemId);
                      if (shouldOfferWishlist(itemId)) setLastCigarId(itemId);
                    }
                  }}
                  onClear={(itemId) => {
                    setStock(active.id, itemId, 0);
                    releaseOwnedIfEmpty(itemId);
                  }}
                  onOpen={onOpenCigar}
                />
              ))}
            </div>
          )}

          <QuickAdd humidorId={active.id} />
        </>
      )}

      {ownedBottles.length > 0 && (
        <>
          <SectionTitle>{t("coll.drinks")}</SectionTitle>
          <div className="space-y-2">
            {ownedBottles.map((d) => (
              <DrinkRow
                key={d.id}
                drink={d}
                onClick={onOpenDrink ? () => onOpenDrink(d) : undefined}
              />
            ))}
          </div>
        </>
      )}

      {lastCigarId && (
        <LastCigarPrompt itemId={lastCigarId} onDone={() => setLastCigarId(null)} />
      )}

      {pick && (
        <VitolaPicker
          cigar={pick.line}
          onPick={applyPick}
          onBack={() => setPick(null)}
        />
      )}
    </div>
  );
}

/**
 * Brzi unos: sve što je u kolekciji označeno s „Imam”, a još nije u ovom
 * humidoru. Dodir dodaje jedan komad i stavka nestaje s popisa — punjenje
 * humidora tako ide bez otvaranja kataloga za svaku cigaru.
 *
 * Linija s više formata nema jedan „komad”: dodir otvara izbor vitole i u
 * humidor ide ključ te vitole. Bez toga bi zaliha opet sjela na goli ključ
 * linije, a svaka bi vitola pokazivala stanje 0.
 */
function QuickAdd({ humidorId }: { humidorId: string }) {
  const { t, cn } = useI18n();
  const market = useMarket();
  const collection = useCollection();
  const { stock } = useHumidors();
  const [open, setOpen] = useState(true);
  // {cigar, sourceId}: sourceId je ključ iz kolekcije (najčešće goli id linije
  // s računa), pa oznaka „Imam” može preseliti na vitolu koja ide u kutiju
  const [pick, setPick] = useState<{ cigar: Cigar; sourceId: string } | null>(null);

  const owned = useMemo(() => {
    const mine = stock.filter((s) => s.humidorId === humidorId);
    const inHumidor = new Set(mine.map((s) => s.itemId));
    const linesInHumidor = new Set(
      mine.map((s) => parseCigarItemId(s.itemId).cigarId),
    );
    const ids = Object.entries(collection.items)
      .filter(([id, state]) => state.owned && !inHumidor.has(id))
      .map(([id]) => id);
    return dedupeCollectionCigarIds(ids)
      .map((id) => ({ id, cigar: cigarForItemId(id) }))
      // pića su isto u `items` — u humidor idu samo cigare
      .filter((row): row is { id: string; cigar: Cigar } => row.cigar != null)
      .map((row) => ({ ...row, needsVitola: stockNeedsVitola(row.cigar, row.id) }))
      // liniju koja je već u humidoru ne nudimo dvaput: nove veličine se
      // dodaju gumbom „Dodaj vitolu” na njezinoj kartici
      .filter(
        (row) =>
          !row.needsVitola || !linesInHumidor.has(parseCigarItemId(row.id).cigarId),
      )
      .sort((a, b) =>
        `${a.cigar.brand} ${a.cigar.line}`.localeCompare(
          `${b.cigar.brand} ${b.cigar.line}`,
        ),
      );
  }, [collection.items, stock, humidorId]);

  const ownedCigarsTotal = Object.entries(collection.items).filter(
    ([id, state]) => state.owned && cigarForItemId(id) != null,
  ).length;

  return (
    <>
      <SectionTitle>{t("hum.quickAdd")}</SectionTitle>

      {ownedCigarsTotal === 0 ? (
        <p className="text-sm leading-relaxed text-dim">{t("hum.quickAddNone")}</p>
      ) : owned.length === 0 ? (
        <p className="text-sm leading-relaxed text-dim">{t("hum.quickAddEmpty")}</p>
      ) : (
        <>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="min-w-0 flex-1 text-xs leading-relaxed text-dim">
              {t("hum.quickAddHint")}
            </p>
            <div className="flex shrink-0 gap-2">
              <Chip onClick={() => setOpen((v) => !v)}>
                {open ? t("hum.quickAddHide") : `${t("hum.quickAddShow")} (${owned.length})`}
              </Chip>
              {open && owned.some((row) => !row.needsVitola) && (
                <Chip
                  onClick={() => {
                    // vitolu ne pogađamo — linije s više formata ostaju na popisu
                    for (const row of owned) {
                      if (!row.needsVitola) adjustStock(humidorId, row.id, 1);
                    }
                  }}
                >
                  + {t("hum.quickAddAll")}
                </Chip>
              )}
            </div>
          </div>

          {open && (
            <div className="mt-2 space-y-1.5">
              {owned.map(({ id, cigar, needsVitola }) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => {
                    if (needsVitola) {
                      setPick({ cigar, sourceId: id });
                      return;
                    }
                    adjustStock(humidorId, id, 1);
                    claimOwnedForStock(id);
                  }}
                  className="flex w-full items-center justify-between gap-3 rounded-lg border border-dim/15 bg-cedar px-3 py-2 text-left hover:border-zlato/40"
                >
                  <span className="min-w-0">
                    <span className="block truncate text-sm text-papir">
                      {brandDisplayName(cigar.brand, market)} {cigar.line}
                    </span>
                    <span className="block truncate text-micro text-dim">
                      {needsVitola
                        ? t("hum.pickVitolaToAdd")
                        : `${cigar.selectedVitola ?? cigar.vitola} · ${cn(cigar.country)}`}
                    </span>
                  </span>
                  <span
                    aria-hidden
                    className="shrink-0 font-display text-lg leading-none text-zlato"
                  >
                    +
                  </span>
                </button>
              ))}
            </div>
          )}
        </>
      )}

      {pick && (
        <VitolaPicker
          cigar={pick.cigar}
          onPick={(vitola) => {
            const target = vitolaStockId(pick.cigar, vitola);
            adjustStock(humidorId, target, 1);
            // stavka s računa („imam liniju”) sada je konkretna vitola u kutiji
            transferOwnedToVitola(pick.sourceId, target);
            setPick(null);
          }}
          onBack={() => setPick(null)}
        />
      )}
    </>
  );
}

interface VitolaStockRow {
  itemId: string;
  count: number;
  cigar: Cigar | undefined;
  /** null = zaliha još nema određenu vitolu (stari zapis po liniji). */
  vitola: string | null;
  needsVitola: boolean;
}

/**
 * Jedna linija u humidoru: naslov s ukupnim brojem, pa red po vitoli. Brojevi
 * se vode po vitoli jer po vitoli idu i kolekcija, dnevnik i kartica cigare —
 * inače „u humidoru 6” i „stanje 0” na Robustu govore o dva različita ključa.
 */
function LineStockCard({
  title,
  total,
  rows,
  canAddVitola,
  onAddVitola,
  onSetVitola,
  onAdjust,
  onClear,
  onOpen,
}: {
  title: string;
  total: number;
  rows: VitolaStockRow[];
  canAddVitola: boolean;
  onAddVitola: () => void;
  onSetVitola: (itemId: string) => void;
  onAdjust: (itemId: string, delta: number) => void;
  onClear: (itemId: string) => void;
  onOpen?: (cigar: Cigar) => void;
}) {
  const { t, cn } = useI18n();
  const first = rows.find((r) => r.cigar)?.cigar;

  return (
    <div className="rounded-xl border border-dim/15 bg-cedar p-3">
      <div className="flex items-baseline justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate font-display text-base text-papir">{title}</div>
          {first && (
            <div className="mt-0.5 truncate text-xs text-dim">
              {first.wrapper} · {cn(first.country)}
            </div>
          )}
        </div>
        <span className="shrink-0 text-xs text-dim">
          {total} {t("hum.cigarsCount")}
        </span>
      </div>

      <div className="mt-2 space-y-1.5">
        {rows.map((row) => (
          <div
            key={row.itemId}
            className="rounded-lg border border-dim/15 bg-humidor/40 px-2.5 py-2"
          >
            <div className="flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={row.cigar && onOpen ? () => onOpen(row.cigar!) : undefined}
                disabled={!row.cigar || !onOpen}
                className="min-w-0 flex-1 text-left disabled:cursor-default"
              >
                <span className="block truncate text-sm text-papir">
                  {row.vitola ?? t("hum.vitolaMissing")}
                </span>
                {/* dimenzije samo uz određenu vitolu — inače su to mjere
                    zadanog formata linije, a ovdje se ne zna koji je */}
                {row.vitola && row.cigar?.format && row.cigar.format !== "—" && (
                  <span className="block truncate text-micro text-dim">
                    {row.cigar.format}
                  </span>
                )}
              </button>
              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  aria-label="−1"
                  onClick={() => onAdjust(row.itemId, -1)}
                  className="h-8 w-8 rounded-lg border border-dim/30 font-display text-base text-dim hover:border-zlato/50 hover:text-papir"
                >
                  −
                </button>
                <span className="min-w-[2ch] text-center font-display text-lg text-zlato-2">
                  {row.count}
                </span>
                <button
                  type="button"
                  aria-label="+1"
                  onClick={() => onAdjust(row.itemId, 1)}
                  className="h-8 w-8 rounded-lg border border-dim/30 font-display text-base text-dim hover:border-zlato/50 hover:text-papir"
                >
                  +
                </button>
              </div>
            </div>

            {row.needsVitola && (
              <div className="mt-1.5 flex flex-wrap items-center gap-2">
                <span className="min-w-0 flex-1 text-micro leading-snug text-dim">
                  {t("hum.vitolaMissingHint")}
                </span>
                <button
                  type="button"
                  onClick={() => onSetVitola(row.itemId)}
                  className="shrink-0 rounded-md border border-zlato/40 px-2 py-1 text-micro uppercase tracking-widest text-zlato hover:bg-zlato/10"
                >
                  {t("hum.setVitola")}
                </button>
              </div>
            )}

            <button
              type="button"
              onClick={() => onClear(row.itemId)}
              className="mt-1.5 text-micro text-oxblood/80 hover:text-oxblood"
            >
              {t("coll.delete")}
            </button>
          </div>
        ))}
      </div>

      {canAddVitola && (
        <button
          type="button"
          onClick={onAddVitola}
          className="mt-2 rounded-md border border-zlato/40 px-2.5 py-1.5 text-micro uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          + {t("hum.addVitola")}
        </button>
      )}
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
              onDateMoved={(dayKey) => {
                setSelected(dayKey);
                const [y, m] = dayKey.split("-").map(Number);
                if (Number.isFinite(y) && Number.isFinite(m)) {
                  setCursor({ year: y, month: m - 1 });
                }
              }}
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
  onDateMoved,
}: {
  entry: JournalEntry;
  market: ReturnType<typeof useMarket>;
  lang: "hr" | "en";
  lx: (text: { hr: string; en: string }) => string;
  t: (key: StringKey) => string;
  onDateMoved?: (dayKey: string) => void;
}) {
  const cigar = cigarForItemId(entry.cigarId);
  const drink: Drink | undefined = drinkById(entry.drinkId);
  // 24-satni zapis na hrvatskom; engleski ostaje na 12-satnom
  const time = new Date(entry.date).toLocaleTimeString(
    lang === "hr" ? "hr-HR" : "en-GB",
    { hour: "2-digit", minute: "2-digit" },
  );
  const dayValue = localDayKey(new Date(entry.date));

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
          {drink
            ? lx(drinkNameLoc(drink))
            : entry.drinkId == null
              ? t("session.soloLabel")
              : entry.drinkId}
        </span>
        {entry.rating != null && (
          <span className="shrink-0 text-sm text-zlato-2">{entry.rating}/10</span>
        )}
      </div>
      <div className="mt-1 text-xs text-dim">
        {time}
        {entry.note && ` — ${entry.note}`}
      </div>
      <label className="mt-2 flex items-center gap-2 text-xs text-dim">
        <span className="shrink-0">{t("hum.editDate")}</span>
        <input
          type="date"
          value={dayValue}
          aria-label={t("hum.editDate")}
          onChange={(e) => {
            const nextKey = e.target.value;
            if (!nextKey || nextKey === dayValue) return;
            const nextIso = applyLocalDayToIso(entry.date, nextKey);
            if (!nextIso) return;
            updateJournalEntry(entry.id, { date: nextIso });
            onDateMoved?.(nextKey);
          }}
          className="min-w-0 flex-1 rounded-md border border-dim/30 bg-ink/40 px-2 py-1 text-papir [color-scheme:dark]"
        />
      </label>
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
