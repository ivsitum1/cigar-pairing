// „Popušio si zadnju iz humidora — na listu želja?”
//
// Prije je to bio window.confirm iz zapisa večeri: sustavni dijalog koji dio
// preglednika (i instalirani PWA) zna prigušiti nakon prvog puta, pa se popup
// naprosto ne bi pojavio. Sada je običan sheet u aplikaciji, isti na oba
// mjesta gdje zaliha padne na nulu — zapis večeri i −1 u humidoru.
import { SheetShell } from "./SheetShell";
import { BackButton } from "./BackButton";
import { brandDisplayName, cigarForItemId } from "../data";
import { useI18n } from "../i18n";
import { updateItem } from "../store/collection";
import { useMarket } from "../store/market";

export function LastCigarPrompt({
  itemId,
  onDone,
}: {
  /** Ključ zalihe koja je upravo pala na nulu. */
  itemId: string;
  onDone: () => void;
}) {
  const { t } = useI18n();
  const market = useMarket();
  const cigar = cigarForItemId(itemId);
  const name = cigar
    ? `${brandDisplayName(cigar.brand, market)} ${cigar.line}${
        cigar.selectedVitola ? ` — ${cigar.selectedVitola}` : ""
      }`
    : itemId;

  const add = () => {
    updateItem(itemId, { wishlist: true });
    onDone();
  };

  return (
    <SheetShell
      onClose={onDone}
      label={t("wish.lastTitle")}
      panelClassName="w-full max-w-sm rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
    >
      <div className="mb-3">
        <BackButton onClick={onDone}>{t("common.back")}</BackButton>
      </div>
      <h3 className="font-display text-lg text-papir">{t("wish.lastTitle")}</h3>
      <p className="mt-1 font-display text-sm text-zlato-2">{name}</p>
      <p className="mt-2 text-sm leading-relaxed text-dim">{t("wish.lastBody")}</p>

      <div className="mt-4 grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={onDone}
          className="rounded-lg border border-dim/30 py-2.5 font-display text-xs uppercase tracking-widest text-dim"
        >
          {t("wish.lastSkip")}
        </button>
        <button
          type="button"
          onClick={add}
          className="rounded-lg border border-zlato bg-zlato/15 py-2.5 font-display text-xs uppercase tracking-widest text-zlato-2"
        >
          {t("wish.lastAdd")}
        </button>
      </div>
    </SheetShell>
  );
}
