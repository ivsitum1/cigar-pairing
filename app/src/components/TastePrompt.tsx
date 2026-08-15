// „Kako ti je sjela?” — snaga i tijelo iz prve ruke.
//
// Katalog te dvije osi vecinom procjenjuje, a za oko 2200 linija nema izvor
// osim heuristike pokrova. Nijedan vanjski izvor to ne moze zatvoriti
// (provjereno: CigarWorldova ocjena zajednice predviđa gotovo uvijek „3”).
// Zato se pita onoga tko je cigaru upravo popusio — jednom po liniji, odmah
// nakon zapisa vecere, dok je dojam svjez.
import { useState } from "react";
import { SheetShell } from "./SheetShell";
import { BackButton } from "./BackButton";
import { brandDisplayName, cigarForItemId } from "../data";
import { useI18n } from "../i18n";
import { useMarket } from "../store/market";
import { getTasteProfile, setTasteProfile } from "../store/tasteProfile";

const STEPS = [1, 2, 3, 4, 5];

function AxisPicker({
  label,
  hint,
  value,
  onChange,
}: {
  label: string;
  hint: string;
  value: number | null;
  onChange: (n: number) => void;
}) {
  return (
    <div>
      <div className="text-xs uppercase tracking-widest text-dim">{label}</div>
      <div className="mt-1.5 grid grid-cols-5 gap-1.5">
        {STEPS.map((n) => (
          <button
            key={n}
            type="button"
            aria-pressed={value === n}
            onClick={() => onChange(n)}
            className={
              value === n
                ? "rounded-lg border border-zlato bg-zlato/20 py-2 font-display text-sm text-zlato-2"
                : "rounded-lg border border-dim/30 py-2 font-display text-sm text-dim"
            }
          >
            {"◆".repeat(n)}
          </button>
        ))}
      </div>
      <p className="mt-1 text-micro text-dim">{hint}</p>
    </div>
  );
}

export function TastePrompt({
  itemId,
  onDone,
}: {
  /** Ključ cigare koja je upravo zabilježena (smije nositi vitolu). */
  itemId: string;
  onDone: () => void;
}) {
  const { t } = useI18n();
  const market = useMarket();
  const cigar = cigarForItemId(itemId);
  const existing = getTasteProfile(itemId);
  const [strength, setStrength] = useState<number | null>(
    existing?.strength ?? cigar?.strength ?? null,
  );
  const [body, setBody] = useState<number | null>(existing?.body ?? cigar?.body ?? null);

  const name = cigar
    ? `${brandDisplayName(cigar.brand, market)} ${cigar.line}`
    : itemId;

  const save = () => {
    if (strength == null || body == null) return;
    setTasteProfile(itemId, strength, body);
    onDone();
  };

  return (
    <SheetShell
      onClose={onDone}
      label={t("taste.title")}
      panelClassName="w-full max-w-sm rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
    >
      <div className="mb-3">
        <BackButton onClick={onDone}>{t("common.back")}</BackButton>
      </div>
      <h3 className="font-display text-lg text-papir">{t("taste.title")}</h3>
      <p className="mt-1 font-display text-sm text-zlato-2">{name}</p>
      <p className="mt-2 text-sm leading-relaxed text-dim">{t("taste.body")}</p>

      <div className="mt-4 space-y-4">
        <AxisPicker
          label={t("common.strength")}
          hint={t("taste.strengthHint")}
          value={strength}
          onChange={setStrength}
        />
        <AxisPicker
          label={t("common.body")}
          hint={t("taste.bodyHint")}
          value={body}
          onChange={setBody}
        />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={onDone}
          className="rounded-lg border border-dim/30 py-2.5 font-display text-xs uppercase tracking-widest text-dim"
        >
          {t("taste.skip")}
        </button>
        <button
          type="button"
          onClick={save}
          disabled={strength == null || body == null}
          className="rounded-lg border border-zlato bg-zlato/15 py-2.5 font-display text-xs uppercase tracking-widest text-zlato-2 disabled:opacity-40"
        >
          {t("taste.save")}
        </button>
      </div>
    </SheetShell>
  );
}
