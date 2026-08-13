// Gumbi za odabir tržišta (HR / EU / USA / Sve). Dijeljeno stanje u store/market.
// Labela je IZNAD redova — inače dugački HR tekst ("Gdje kupuješ cigare?")
// potisne chipove u horizontalni scroll. App ima overflow-x-hidden pa se
// chipovi u jednom redu odrežu i nestanu s ekrana.
import type { RegionFilter } from "../types";
import { useI18n, type StringKey } from "../i18n";
import { useMarket, setMarket } from "../store/market";

export const REGION_FILTERS: RegionFilter[] = ["HR", "EU", "USA", "ALL"];

export function MarketFilter({
  label,
  className = "",
}: {
  /** Ako je zadano, prikaži labelu iznad gumbi (npr. pairing). */
  label?: string;
  className?: string;
}) {
  const { t } = useI18n();
  const market = useMarket();
  return (
    <div className={className}>
      {label != null && (
        <div className="mb-1.5 text-micro uppercase tracking-widest text-dim">
          {label}
        </div>
      )}
      <div
        role="radiogroup"
        aria-label={label ?? t("market.ALL")}
        className="grid grid-cols-2 gap-2 sm:grid-cols-4"
      >
        {REGION_FILTERS.map((m) => {
          const active = market === m;
          return (
            <button
              key={m}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => setMarket(m)}
              className={`rounded-lg border py-2.5 font-display text-micro uppercase tracking-[0.12em] transition-colors ${
                active
                  ? "border-zlato bg-zlato/15 text-zlato-2"
                  : "border-dim/25 text-dim hover:border-zlato/40"
              }`}
            >
              {t(`market.${m}` as StringKey)}
            </button>
          );
        })}
      </div>
    </div>
  );
}
