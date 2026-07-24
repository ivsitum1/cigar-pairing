import { useMemo, useState } from "react";
import type { Cigar, Drink } from "../types";
import { useI18n } from "../i18n";
import { BackButton } from "./BackButton";
import { logEveningSession } from "../lib/eveningSession";
import { drinkNameLoc } from "../lib/drinkName";

export function EveningSessionSheet({
  cigars,
  drinks,
  initialCigarId,
  initialDrinkId,
  onClose,
  onSaved,
}: {
  cigars: Cigar[];
  drinks: Drink[];
  initialCigarId?: string;
  initialDrinkId?: string;
  onClose: () => void;
  onSaved?: () => void;
}) {
  const { t, lx } = useI18n();

  const cigarOptions = useMemo(() => {
    const seen = new Set<string>();
    return cigars.filter((c) => {
      if (seen.has(c.id)) return false;
      seen.add(c.id);
      return true;
    });
  }, [cigars]);

  const drinkOptions = useMemo(() => {
    const seen = new Set<string>();
    return drinks.filter((d) => {
      if (seen.has(d.id)) return false;
      seen.add(d.id);
      return true;
    });
  }, [drinks]);

  const [cigarId, setCigarId] = useState(
    () =>
      (initialCigarId && cigarOptions.some((c) => c.id === initialCigarId)
        ? initialCigarId
        : cigarOptions[0]?.id) ?? "",
  );
  const [drinkId, setDrinkId] = useState(
    () =>
      (initialDrinkId && drinkOptions.some((d) => d.id === initialDrinkId)
        ? initialDrinkId
        : drinkOptions[0]?.id) ?? "",
  );
  const [rating, setRating] = useState<string>("");
  const [note, setNote] = useState("");
  const [markTried, setMarkTried] = useState(true);

  const selectCls =
    "w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2.5 text-sm text-papir focus:border-zlato/60 focus:outline-none";

  const save = () => {
    if (!cigarId || !drinkId) return;
    logEveningSession({
      cigarId,
      drinkId,
      rating: rating ? Number(rating) : null,
      note,
      markTried,
    });
    onSaved?.();
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3">
          <BackButton onClick={onClose}>{t("common.back")}</BackButton>
        </div>
        <h3 className="font-display text-lg text-papir">{t("session.title")}</h3>
        <p className="mt-1 text-sm leading-relaxed text-dim">{t("session.hint")}</p>

        <div className="mt-4 space-y-3">
          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("common.cigar")}
            <select
              value={cigarId}
              onChange={(e) => setCigarId(e.target.value)}
              className={`mt-1 ${selectCls}`}
              disabled={cigarOptions.length <= 1}
            >
              {cigarOptions.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.brand} {c.line}
                </option>
              ))}
            </select>
          </label>

          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("common.drink")}
            <select
              value={drinkId}
              onChange={(e) => setDrinkId(e.target.value)}
              className={`mt-1 ${selectCls}`}
              disabled={drinkOptions.length <= 1}
            >
              {drinkOptions.map((d) => (
                <option key={d.id} value={d.id}>
                  {lx(drinkNameLoc(d))}
                </option>
              ))}
            </select>
          </label>

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
            disabled={!cigarId || !drinkId}
            className="rounded-lg border border-zlato bg-zlato/15 py-2.5 font-display text-xs uppercase tracking-widest text-zlato-2 disabled:opacity-40"
          >
            {t("session.save")}
          </button>
        </div>
      </div>
    </div>
  );
}
