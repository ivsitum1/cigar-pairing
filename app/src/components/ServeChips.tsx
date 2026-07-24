import type { Drink, ServeStyle } from "../types";
import { useI18n, type StringKey } from "../i18n";
import { Chip } from "./ui";

const SERVE_ORDER: ServeStyle[] = ["neat", "water", "rocks", "highball", "cola"];

// Serve selektor: prikaži samo stilove koje piće podnosi (serving[style] > 0).
// Odabir mijenja rang/score (aroma/žestina); "neat" je baseline (serve = undefined).
export function ServeChips({
  drink,
  serve,
  onChange,
}: {
  drink: Drink;
  serve: ServeStyle | undefined;
  onChange: (s: ServeStyle | undefined) => void;
}) {
  const { t, sv } = useI18n();
  const available = SERVE_ORDER.filter((s) => (drink.serving[s] ?? 0) > 0);
  if (available.length < 2) return null; // nema smisla birati ako je samo jedan način

  return (
    <div className="mt-3">
      <div className="mb-1.5 flex items-center gap-2">
        <span className="text-micro uppercase tracking-widest text-dim">
          {t("serve.title")}
        </span>
        {drink.serving.best && (
          <span className="text-micro text-dim/70">
            · {t("serve.best")}: {sv(drink.serving.best)}
          </span>
        )}
      </div>
      <div className="no-scrollbar flex gap-2 overflow-x-auto">
        {available.map((s) => {
          const active = s === "neat" ? serve === undefined : serve === s;
          return (
            <Chip
              key={s}
              active={active}
              onClick={() => onChange(s === "neat" ? undefined : s)}
            >
              {t(`serve.${s}` as StringKey)}
            </Chip>
          );
        })}
      </div>
    </div>
  );
}
