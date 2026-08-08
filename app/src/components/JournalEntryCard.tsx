// Kartica zapisa iz dnevnika — ista u kalendaru i na popisu Kolekcije.
//
// Datum je uredljiv na licu mjesta: večer se često bilježi tek sutradan, a
// zapis onda visi na krivom danu u kalendaru. Mijenja se samo trenutak, sve
// ostalo (cigara, piće, ocjena) ostaje kakvo je spremljeno.
import { useState } from "react";
import { brandDisplayName, cigarForItemId, drinkById } from "../data";
import { useI18n } from "../i18n";
import { drinkNameLoc } from "../lib/drinkName";
import {
  isoFromLocalParts,
  localDayKey,
  localTimeValue,
} from "../lib/calendar";
import {
  removeJournalEntry,
  updateJournalEntry,
  type JournalEntry,
} from "../store/collection";
import { useMarket } from "../store/market";

export function JournalEntryCard({
  entry,
  onMoved,
}: {
  entry: JournalEntry;
  /** Zapis je premješten na `dayKey` — kalendar tada skoči na taj dan. */
  onMoved?: (dayKey: string) => void;
}) {
  const { t, lx, lang } = useI18n();
  const market = useMarket();
  const [editing, setEditing] = useState(false);

  const when = new Date(entry.date);
  const valid = !Number.isNaN(when.getTime());
  const [day, setDay] = useState(() =>
    localDayKey(valid ? when : new Date()),
  );
  const [time, setTime] = useState(() =>
    localTimeValue(valid ? when : new Date()),
  );

  const cigar = cigarForItemId(entry.cigarId);
  const drink = drinkById(entry.drinkId);
  const locale = lang === "hr" ? "hr-HR" : "en-GB";
  // 24-satni zapis na hrvatskom; engleski ostaje na 12-satnom
  const stamp = valid
    ? `${when.toLocaleDateString(locale)} · ${when.toLocaleTimeString(locale, {
        hour: "2-digit",
        minute: "2-digit",
      })}`
    : entry.date;

  const inputCls =
    "w-full rounded-lg border border-dim/25 bg-humidor px-2.5 py-2 text-sm text-papir focus:border-zlato/60 focus:outline-none";

  const openEdit = () => {
    const base = valid ? when : new Date();
    setDay(localDayKey(base));
    setTime(localTimeValue(base));
    setEditing(true);
  };

  const saveDate = () => {
    const iso = isoFromLocalParts(day, time);
    if (!iso) return;
    updateJournalEntry(entry.id, { date: iso });
    setEditing(false);
    onMoved?.(day);
  };

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
        {stamp}
        {entry.note && ` — ${entry.note}`}
      </div>

      {editing ? (
        <div className="mt-2">
          <div className="grid grid-cols-2 gap-2">
            <label className="block text-micro uppercase tracking-widest text-dim">
              {t("session.date")}
              <input
                type="date"
                value={day}
                onChange={(e) => setDay(e.target.value)}
                className={`mt-1 ${inputCls}`}
              />
            </label>
            <label className="block text-micro uppercase tracking-widest text-dim">
              {t("session.time")}
              <input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className={`mt-1 ${inputCls}`}
              />
            </label>
          </div>
          <div className="mt-2 grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setEditing(false)}
              className="rounded-lg border border-dim/30 py-2 font-display text-micro uppercase tracking-widest text-dim"
            >
              {t("common.cancel")}
            </button>
            <button
              type="button"
              onClick={saveDate}
              disabled={!isoFromLocalParts(day, time)}
              className="rounded-lg border border-zlato bg-zlato/15 py-2 font-display text-micro uppercase tracking-widest text-zlato-2 disabled:opacity-40"
            >
              {t("coll.save")}
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-2 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={openEdit}
            className="text-xs text-zlato/80 hover:text-zlato-2"
          >
            {t("coll.editDate")}
          </button>
          <button
            type="button"
            onClick={() => removeJournalEntry(entry.id)}
            className="text-xs text-oxblood/80 hover:text-oxblood"
          >
            {t("coll.delete")}
          </button>
        </div>
      )}
    </div>
  );
}
