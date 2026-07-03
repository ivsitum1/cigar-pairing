import { useEffect, useState } from "react";
import type { Cigar, Drink } from "../types";
import { useI18n, STYLE_LABELS, ADDITIVE_LABELS } from "../i18n";
import { formatPrice } from "../data";
import { Chip, Meter } from "./ui";
import {
  getItemState,
  updateItem,
  useCollection,
} from "../store/collection";

type Item = { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink };

export function DetailSheet({
  target,
  onClose,
}: {
  target: Item | null;
  onClose: () => void;
}) {
  const { t } = useI18n();
  useCollection();
  const id = target?.item.id;
  const state = id ? getItemState(id) : null;
  const [note, setNote] = useState("");

  useEffect(() => {
    if (id) setNote(getItemState(id).note);
  }, [id]);

  if (!target || !id || !state) return null;

  const saveNote = () => updateItem(id, { note });

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onClose}
    >
      <div
        className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-dim/40 sm:hidden" />

        {target.kind === "cigar" ? (
          <CigarDetails cigar={target.item} />
        ) : (
          <DrinkDetails drink={target.item} />
        )}

        <div className="band-rule my-4" />

        {/* kolekcija kontrole */}
        <div className="flex flex-wrap items-center gap-2">
          <Chip
            active={state.owned}
            onClick={() => updateItem(id, { owned: !state.owned })}
          >
            ✓ {t("coll.owned")}
          </Chip>
          <Chip
            active={state.tried}
            onClick={() => updateItem(id, { tried: !state.tried })}
          >
            {t("coll.tried")}
          </Chip>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs text-dim">{t("coll.myRating")}</span>
            <select
              value={state.rating ?? ""}
              onChange={(e) =>
                updateItem(id, {
                  rating: e.target.value ? Number(e.target.value) : null,
                })
              }
              className="rounded-md border border-dim/30 bg-cedar px-2 py-1 text-sm text-papir"
            >
              <option value="">—</option>
              {Array.from({ length: 19 }, (_, i) => (10 - i * 0.5).toFixed(1)).map(
                (v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ),
              )}
            </select>
          </div>
        </div>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          onBlur={saveNote}
          placeholder={t("coll.notePlaceholder")}
          rows={2}
          className="mt-3 w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2 text-sm text-papir placeholder:text-dim/60 focus:border-zlato/60 focus:outline-none"
        />

        <button
          onClick={onClose}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("common.close")}
        </button>
      </div>
    </div>
  );
}

function CigarDetails({ cigar }: { cigar: Cigar }) {
  const { t, lx } = useI18n();
  return (
    <>
      <div className="font-display text-xl text-papir">
        {cigar.brand} <span className="text-zlato-2">{cigar.line}</span>
      </div>
      <div className="mt-1 text-sm text-dim">
        {cigar.vitola} · {cigar.format} · {cigar.country}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
        <Meter value={cigar.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
        <Meter value={cigar.body} label={t("common.body")} />
      </div>
      <dl className="mt-3 space-y-1 text-sm">
        <Row k={t("common.wrapper")} v={cigar.wrapper} />
        <Row
          k={t("common.price")}
          v={`${cigar.priceApprox ? t("common.approx") + " " : ""}${formatPrice(cigar.priceEUR)}`}
        />
        <Row k={t("common.time")} v={`~${cigar.smokeTimeMin} ${t("common.minutes")}`} />
        {cigar.availabilityHR.length > 0 && (
          <Row k={t("common.shop")} v={cigar.availabilityHR.join(", ")} />
        )}
        <Row
          k={t("common.markets")}
          v={cigar.markets.map((m) => t(`market.${m}` as Parameters<typeof t>[0])).join(", ")}
        />
      </dl>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {cigar.flavorTags.map((tag) => (
          <Chip key={tag}>{tag}</Chip>
        ))}
      </div>
      <p className="mt-3 text-sm leading-relaxed text-papir/85">
        {lx(cigar.notes)}
      </p>
    </>
  );
}

function DrinkDetails({ drink }: { drink: Drink }) {
  const { t, lx } = useI18n();
  const style = STYLE_LABELS[drink.style];
  return (
    <>
      <div className="font-display text-xl text-papir">{drink.name}</div>
      <div className="mt-1 text-sm text-dim">
        {style ? lx(style) : drink.style} · {drink.region}
        {drink.abv ? ` · ${drink.abv}%` : ""}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
        <Meter value={drink.body} label={t("common.body")} />
        <Meter value={drink.sweetness} label={t("common.sweetness")} accent="var(--color-lista)" />
      </div>
      <dl className="mt-3 space-y-1 text-sm">
        {drink.qualityScore != null && (
          <Row k={t("common.quality")} v={`${drink.qualityScore}/10`} />
        )}
        {drink.additiveStatus && (
          <Row
            k={t("common.additives")}
            v={`${lx(ADDITIVE_LABELS[drink.additiveStatus])}${drink.additiveDetail ? ` (${drink.additiveDetail})` : ""}`}
          />
        )}
        <Row
          k={t("common.price")}
          v={`${drink.priceApprox ? t("common.approx") + " " : ""}${formatPrice(drink.priceEUR)}`}
        />
        {drink.shopHR && <Row k={t("common.shop")} v={drink.shopHR} />}
        {drink.serving?.best && <Row k={t("common.serving")} v={drink.serving.best} />}
      </dl>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {drink.flavorTags.map((tag) => (
          <Chip key={tag}>{tag}</Chip>
        ))}
      </div>
      {lx(drink.notes) && (
        <p className="mt-3 text-sm leading-relaxed text-papir/85">
          {lx(drink.notes)}
        </p>
      )}
      {drink.cigarHint && (
        <p className="mt-2 rounded-lg border border-zlato/25 bg-zlato/10 px-3 py-2 text-sm text-zlato-2">
          🚬 {drink.cigarHint}
        </p>
      )}
    </>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex gap-3">
      <dt className="w-24 shrink-0 text-dim">{k}</dt>
      <dd className="text-papir/90">{v}</dd>
    </div>
  );
}
