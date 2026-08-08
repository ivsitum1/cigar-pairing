import { useMemo, useState } from "react";
import { SheetShell } from "./SheetShell";
import type { Cigar, Drink } from "../types";
import { ALL_DRINKS, cigarById } from "../data";
import { useI18n } from "../i18n";
import { BackButton } from "./BackButton";
import { logEveningSession } from "../lib/eveningSession";
import { drinkNameLoc, drinkNameHaystack } from "../lib/drinkName";
import { cigarItemId } from "../lib/cigarItemId";
import { applyVitola, uniqueVitolas } from "../lib/cigarVitola";
import { shouldOfferWishlist } from "../lib/lastCigar";
import { isoFromLocalParts, localDayKey, localTimeValue } from "../lib/calendar";
import { LastCigarPrompt } from "./LastCigarPrompt";

const SOLO = "__solo__";
const CUSTOM = "__custom__";

const norm = (s: string) =>
  s.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

export function EveningSessionSheet({
  cigars,
  drinks,
  initialCigarId,
  initialDrinkId,
  allowSolo = true,
  onClose,
  onSaved,
}: {
  cigars: Cigar[];
  /** Preporučena pića (prvi red); katalog se uvijek može pretražiti. */
  drinks: Drink[];
  initialCigarId?: string;
  initialDrinkId?: string | null;
  allowSolo?: boolean;
  onClose: () => void;
  onSaved?: () => void;
}) {
  const { t, lx } = useI18n();

  // kljuc nosi odabranu vitolu — Churchill i Corona iste linije su dva zapisa
  const cigarOptions = useMemo(() => {
    const seen = new Set<string>();
    const out: { key: string; label: string; lineId: string }[] = [];
    for (const c of cigars) {
      const key = cigarItemId(c);
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({
        key,
        lineId: c.id,
        label: c.selectedVitola
          ? `${c.brand} ${c.line} — ${c.selectedVitola}`
          : `${c.brand} ${c.line}`,
      });
    }
    return out;
  }, [cigars]);

  const drinkOptions = useMemo(() => {
    const seen = new Set<string>();
    return drinks.filter((d) => {
      if (seen.has(d.id)) return false;
      seen.add(d.id);
      return true;
    });
  }, [drinks]);

  const pairableDrinks = useMemo(
    () => ALL_DRINKS.filter((d) => d.pairable),
    [],
  );

  const [cigarId, setCigarId] = useState(
    () =>
      (initialCigarId && cigarOptions.some((c) => c.key === initialCigarId)
        ? initialCigarId
        : cigarOptions[0]?.key) ?? "",
  );
  const [vitolaName, setVitolaName] = useState("");

  const initialInRecs =
    initialDrinkId != null && drinkOptions.some((d) => d.id === initialDrinkId);
  const [drinkMode, setDrinkMode] = useState<"rec" | "custom" | "solo">(() => {
    if (initialDrinkId === null) return allowSolo ? "solo" : "custom";
    if (initialDrinkId && !initialInRecs) return "custom";
    if (drinkOptions.length === 0 && !initialDrinkId) {
      return allowSolo ? "solo" : "custom";
    }
    return "rec";
  });
  const [drinkId, setDrinkId] = useState<string | null>(() => {
    if (initialDrinkId === null) return null;
    if (initialDrinkId) return initialDrinkId;
    return drinkOptions[0]?.id ?? null;
  });
  const [drinkQuery, setDrinkQuery] = useState("");
  // večer se često bilježi dan poslije — datum je polje, a ne trenutak spremanja
  const [day, setDay] = useState(() => localDayKey(new Date()));
  const [time, setTime] = useState(() => localTimeValue(new Date()));
  const todayKey = useMemo(() => localDayKey(new Date()), []);
  const [rating, setRating] = useState<string>("");
  const [note, setNote] = useState("");
  const [markTried, setMarkTried] = useState(true);
  // zadnja iz humidora: sheet ostaje montiran dok se ne odgovori na ponudu
  const [lastCigarId, setLastCigarId] = useState<string | null>(null);

  const selectedOpt = cigarOptions.find((c) => c.key === cigarId);
  const lineForVitola = selectedOpt ? cigarById(selectedOpt.lineId) : undefined;
  const lineVitolas = useMemo(
    () => (lineForVitola && !cigarId.includes("@") ? uniqueVitolas(lineForVitola) : []),
    [lineForVitola, cigarId],
  );

  const drinkHits = useMemo(() => {
    const q = norm(drinkQuery.trim());
    if (!q) return [];
    return pairableDrinks
      .filter((d) => norm(drinkNameHaystack(d)).includes(q))
      .slice(0, 12);
  }, [drinkQuery, pairableDrinks]);

  const selectCls =
    "w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2.5 text-sm text-papir focus:border-zlato/60 focus:outline-none";

  const recSelectValue =
    drinkMode === "solo"
      ? SOLO
      : drinkMode === "custom"
        ? CUSTOM
        : (drinkId ?? "");

  const resolvedDrinkId = drinkMode === "solo" ? null : drinkId;

  const loggedAt = isoFromLocalParts(day, time);

  const save = () => {
    if (!cigarId) return;
    if (drinkMode !== "solo" && !drinkId) return;
    if (!loggedAt) return;

    let finalCigarId = cigarId;
    if (lineForVitola && lineVitolas.length > 1 && vitolaName) {
      const vitola = lineVitolas.find((v) => v.name === vitolaName);
      if (vitola) finalCigarId = cigarItemId(applyVitola(lineForVitola, vitola));
    }

    const result = logEveningSession({
      cigarId: finalCigarId,
      drinkId: resolvedDrinkId,
      rating: rating ? Number(rating) : null,
      note,
      markTried,
      date: loggedAt,
    });

    onSaved?.();

    // popušena zadnja iz humidora → ponuda za listu želja umjesto zatvaranja
    if (shouldOfferWishlist(result.consumedItemId)) {
      setLastCigarId(finalCigarId);
      return;
    }

    onClose();
  };

  const canSave =
    !!cigarId &&
    !!loggedAt &&
    (drinkMode === "solo" || !!drinkId) &&
    (lineVitolas.length <= 1 || !!vitolaName || cigarId.includes("@"));

  if (lastCigarId) {
    return <LastCigarPrompt itemId={lastCigarId} onDone={onClose} />;
  }

  return (
    <SheetShell
      onClose={onClose}
      label={t("session.title")}
      panelClassName="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
    >
        <div className="mb-3">
          <BackButton onClick={onClose}>{t("common.back")}</BackButton>
        </div>
        <h3 className="font-display text-lg text-papir">{t("session.title")}</h3>
        <p className="mt-1 text-sm leading-relaxed text-dim">{t("session.hint")}</p>

        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <label className="block text-xs uppercase tracking-widest text-dim">
              {t("session.date")}
              <input
                type="date"
                value={day}
                max={todayKey}
                onChange={(e) => setDay(e.target.value)}
                className={`mt-1 ${selectCls}`}
              />
            </label>
            <label className="block text-xs uppercase tracking-widest text-dim">
              {t("session.time")}
              <input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className={`mt-1 ${selectCls}`}
              />
            </label>
          </div>
          {day !== todayKey && (
            <p className="text-xs text-zlato-2">{t("session.datePast")}</p>
          )}

          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("common.cigar")}
            <select
              value={cigarId}
              onChange={(e) => {
                setCigarId(e.target.value);
                setVitolaName("");
              }}
              className={`mt-1 ${selectCls}`}
              disabled={cigarOptions.length <= 1}
            >
              {cigarOptions.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>

          {lineVitolas.length > 1 && (
            <label className="block text-xs uppercase tracking-widest text-dim">
              {t("common.vitola")}
              <select
                value={vitolaName}
                onChange={(e) => setVitolaName(e.target.value)}
                className={`mt-1 ${selectCls}`}
              >
                <option value="">—</option>
                {lineVitolas.map((v) => (
                  <option key={v.name} value={v.name}>
                    {v.name}
                    {v.format && v.format !== "—" ? ` · ${v.format}` : ""}
                  </option>
                ))}
              </select>
            </label>
          )}

          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("session.recommendations")}
            <select
              value={recSelectValue}
              onChange={(e) => {
                const v = e.target.value;
                if (v === SOLO) {
                  setDrinkMode("solo");
                  setDrinkId(null);
                  return;
                }
                if (v === CUSTOM) {
                  setDrinkMode("custom");
                  return;
                }
                setDrinkMode("rec");
                setDrinkId(v);
              }}
              className={`mt-1 ${selectCls}`}
            >
              {drinkOptions.length === 0 && (
                <option value="" disabled>
                  {t("session.noRecommendations")}
                </option>
              )}
              {drinkOptions.map((d) => (
                <option key={d.id} value={d.id}>
                  {lx(drinkNameLoc(d))}
                </option>
              ))}
              <option value={CUSTOM}>{t("session.customDrink")}</option>
              {allowSolo && <option value={SOLO}>{t("session.solo")}</option>}
            </select>
          </label>

          {drinkMode === "custom" && (
            <div>
              <label className="block text-xs uppercase tracking-widest text-dim">
                {t("session.customDrink")}
                <input
                  type="search"
                  value={drinkQuery}
                  onChange={(e) => setDrinkQuery(e.target.value)}
                  placeholder={t("session.searchDrink")}
                  className={`mt-1 ${selectCls}`}
                />
              </label>
              {drinkId && (
                <p className="mt-1.5 text-sm text-zlato-2">
                  {(() => {
                    const d = pairableDrinks.find((x) => x.id === drinkId);
                    return d ? lx(drinkNameLoc(d)) : drinkId;
                  })()}
                </p>
              )}
              {drinkHits.length > 0 && (
                <ul className="mt-2 max-h-40 overflow-y-auto rounded-lg border border-dim/20 bg-cedar">
                  {drinkHits.map((d) => (
                    <li key={d.id}>
                      <button
                        type="button"
                        className="w-full px-3 py-2 text-left text-sm text-papir hover:bg-zlato/10"
                        onClick={() => {
                          setDrinkId(d.id);
                          setDrinkQuery("");
                        }}
                      >
                        {lx(drinkNameLoc(d))}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {drinkMode === "solo" && (
            <p className="text-sm text-dim">{t("session.solo")}</p>
          )}

          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("coll.myRating")}
            <select
              value={rating}
              onChange={(e) => setRating(e.target.value)}
              className={`mt-1 ${selectCls}`}
            >
              <option value="">—</option>
              {Array.from({ length: 10 }, (_, i) => 10 - i).map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </label>

          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={t("coll.notePlaceholder")}
            rows={2}
            className={selectCls}
          />

          <label className="flex items-center gap-2 text-sm text-papir/90">
            <input
              type="checkbox"
              checked={markTried}
              onChange={(e) => setMarkTried(e.target.checked)}
              className="accent-[var(--color-zlato)]"
            />
            {t("session.markTried")}
          </label>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2">
          <button
            onClick={onClose}
            className="rounded-lg border border-dim/30 py-2.5 font-display text-xs uppercase tracking-widest text-dim"
          >
            {t("common.close")}
          </button>
          <button
            onClick={save}
            disabled={!canSave}
            className="rounded-lg border border-zlato bg-zlato/15 py-2.5 font-display text-xs uppercase tracking-widest text-zlato-2 disabled:opacity-40"
          >
            {t("session.save")}
          </button>
        </div>    </SheetShell>
  );
}
