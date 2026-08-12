// Overlay za potvrdu punoljetnosti. Blokira aplikaciju dok se ne potvrdi.
//
// Namjerno NIJE modal preko sadržaja nego zamjena za njega: sadržaj se ne
// smije nazrijeti ispod, a ni pročitati iz DOM-a čitačem ekrana.
import { useState } from "react";
import { useI18n } from "../i18n";
import { rememberAgeConfirmed } from "../lib/ageGate";
import { BrandSeal, BrandWordmark } from "./BrandMark";

export function AgeGate({ onConfirm }: { onConfirm: () => void }) {
  const { t, lang, setLang } = useI18n();
  const [denied, setDenied] = useState(false);

  const confirm = () => {
    rememberAgeConfirmed();
    onConfirm();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={t("age.title")}
      className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-5 px-6 text-center"
    >
      {/* Prvi ekran koji korisnik vidi — ovdje znak stoji sam, u punoj formi. */}
      <BrandSeal className="h-20 w-20" title="Cigar & Drink Pairing" />
      <BrandWordmark className="-mt-2" />

      {denied ? (
        <>
          <h1 className="font-display text-base uppercase tracking-widest text-papir">
            {t("age.deniedTitle")}
          </h1>
          <p className="text-sm leading-relaxed text-dim">{t("age.deniedBody")}</p>
          <button
            type="button"
            onClick={() => setDenied(false)}
            className="mt-1 text-xs text-dim underline decoration-dim/40 underline-offset-4 hover:text-papir"
          >
            {t("age.deniedBack")}
          </button>
        </>
      ) : (
        <>
          <h1 className="font-display text-base uppercase tracking-widest text-papir">
            {t("age.title")}
          </h1>
          <p className="text-sm leading-relaxed text-papir">{t("age.body")}</p>
          <p className="-mt-2 text-xs leading-relaxed text-dim">
            {t("age.thresholds")}
          </p>
          <div className="mt-1 flex w-full flex-col gap-2">
            <button
              type="button"
              autoFocus
              onClick={confirm}
              className="w-full rounded-lg border border-zlato/50 bg-zlato/15 py-3 font-display text-sm uppercase tracking-widest text-zlato-2 hover:bg-zlato/25"
            >
              {t("age.confirm")}
            </button>
            <button
              type="button"
              onClick={() => setDenied(true)}
              className="w-full rounded-lg border border-dim/30 py-3 font-display text-sm uppercase tracking-widest text-dim hover:text-papir"
            >
              {t("age.deny")}
            </button>
          </div>
          <p className="text-xs leading-relaxed text-dim">{t("age.disclaimer")}</p>
        </>
      )}

      <button
        onClick={() => setLang(lang === "hr" ? "en" : "hr")}
        className="mt-2 rounded-full border border-zlato/40 px-3 py-1.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
        aria-label="Language"
      >
        {lang === "hr" ? "EN" : "HR"}
      </button>
    </div>
  );
}
