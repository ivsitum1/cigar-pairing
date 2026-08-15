// Snaga i tijelo — s tvojom ocjenom kad postoji, i s gumbom da je daš.
//
// Isti blok stoji na kartici linije i na kartici vitole, pa živi na jednom
// mjestu: dvije kartice koje se razilaze u tome čiju vrijednost pokazuju bile
// bi gora greška od duplog koda.
import { useState } from "react";
import type { Cigar } from "../types";
import { Meter } from "./ui";
import { useI18n } from "../i18n";
import { useTasteProfiles } from "../store/tasteProfile";
import { withTaste } from "../lib/tasteProfile";
import { TastePrompt } from "./TastePrompt";

export function TasteMeters({ cigar }: { cigar: Cigar }) {
  const { t } = useI18n();
  const taste = useTasteProfiles();
  const [rating, setRating] = useState(false);
  const shown = withTaste(cigar, taste);
  const mine = shown.profileFromUser === true;

  return (
    <>
      <div className="mt-3 flex flex-wrap items-end gap-x-5 gap-y-2">
        <Meter value={shown.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
        <Meter value={shown.body} label={t("common.body")} />
        <button
          type="button"
          onClick={() => setRating(true)}
          className={
            mine
              ? "rounded-full border border-zlato bg-zlato/15 px-2.5 py-1 text-micro uppercase tracking-widest text-zlato-2"
              : "rounded-full border border-zlato/35 px-2.5 py-1 text-micro uppercase tracking-widest text-zlato-2/80"
          }
        >
          {mine ? `★ ${t("taste.mine")}` : t("taste.edit")}
        </button>
      </div>
      {rating && <TastePrompt itemId={cigar.id} onDone={() => setRating(false)} />}
    </>
  );
}

/** Nosi li ova cigara tvoju ocjenu? Za oznake izvora ispod opisa. */
export function useHasTaste(cigar: Cigar): boolean {
  const taste = useTasteProfiles();
  return withTaste(cigar, taste).profileFromUser === true;
}
