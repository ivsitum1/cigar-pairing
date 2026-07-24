// Chipovi za odabir tržišta (Sve / HR / EU / USA). Dijeljeno stanje u store/market.
import type { RegionFilter } from "../types";
import { useI18n, type StringKey } from "../i18n";
import { useMarket, setMarket } from "../store/market";
import { Chip } from "./ui";

export const REGION_FILTERS: RegionFilter[] = ["ALL", "HR", "EU", "USA"];

export function MarketFilter({
  label,
  className = "",
}: {
  /** Ako je zadano, prikaži labelu ispred chipova (npr. pairing). */
  label?: string;
  className?: string;
}) {
  const { t } = useI18n();
  const market = useMarket();
  return (
    <div className={`no-scrollbar flex items-center gap-2 overflow-x-auto ${className}`}>
      {label != null && (
        <span className="shrink-0 text-micro uppercase tracking-widest text-dim">{label}</span>
      )}
      {REGION_FILTERS.map((m) => (
        <Chip key={m} active={market === m} onClick={() => setMarket(m)}>
          {t(`market.${m}` as StringKey)}
        </Chip>
      ))}
    </div>
  );
}
