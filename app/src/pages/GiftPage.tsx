import { useMemo, useState } from "react";
import type { Cigar, Drink } from "../types";
import { ALL_DRINKS, CIGARS } from "../data";
import giftQuestions from "../data/giftQuestions.json";
import { useI18n, type StringKey } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { MarketFilter } from "../components/MarketFilter";
import { CigarRow, DrinkRow } from "../components/cards";
import {
  CigarBrowseSheets,
  useCigarBrowseSheets,
} from "../components/useCigarBrowseSheets";
import { useMarket } from "../store/market";
import { navigate } from "../store/route";
import { drinkPrimaryLink } from "../lib/drinkShopLinks";
import { formatEur } from "../lib/cigarPrice";
import { BUCKETS } from "../lib/shoppingPicks";
import {
  findGifts,
  OWNED_STYLES_NONE,
  visibleGiftSteps,
  type GiftAnswers,
  type GiftDrinkPick,
  type GiftPick,
  type GiftWizardStep,
} from "../lib/giftFinder";

type CoreQuestionId = "recipient" | "budget" | "intensity" | "drink" | "shape";

const EMPTY_ANSWERS: GiftAnswers = {
  recipient: "unknown",
  budget: "unknown",
  drink: "unknown",
  intensity: "unknown",
  shape: "unknown",
  ownedStyles: [],
  drinkPick: "unknown",
};

const DRINK_PICK_OPTIONS: GiftDrinkPick[] = ["gap", "top", "value", "unknown"];

export function GiftPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx } = useI18n();
  const market = useMarket();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<GiftAnswers>(EMPTY_ANSWERS);
  const [seed, setSeed] = useState(0);
  const [exclude, setExclude] = useState<string[]>([]);
  const [done, setDone] = useState(false);
  const sheets = useCigarBrowseSheets();

  const catalog = useMemo(() => ({ cigars: CIGARS, drinks: ALL_DRINKS }), []);
  const steps = visibleGiftSteps(answers);
  const safeStep = Math.min(step, steps.length - 1);
  const stepId: GiftWizardStep = steps[safeStep] ?? "recipient";

  const results = useMemo(() => {
    if (!done) return [];
    return findGifts(answers, catalog, market, { seed, excludeIds: exclude });
  }, [answers, catalog, market, seed, exclude, done]);

  const q = giftQuestions.find((item) => item.id === stepId);
  const currentVal = q ? answers[q.id as CoreQuestionId] : undefined;

  const setCoreAnswer = (id: CoreQuestionId, value: string) => {
    setAnswers((a) => {
      const next = { ...a, [id]: value } as GiftAnswers;
      if (id === "drink") next.ownedStyles = [];
      if (id === "shape" && value === "cigar") {
        next.ownedStyles = [];
        next.drinkPick = "unknown";
      }
      return next;
    });
  };

  const toggleOwnedStyle = (id: string) => {
    setAnswers((a) => {
      const cur = a.ownedStyles ?? [];
      if (id === "unknown") return { ...a, ownedStyles: [] };
      if (id === OWNED_STYLES_NONE) {
        return {
          ...a,
          ownedStyles: cur.length === 1 && cur[0] === OWNED_STYLES_NONE ? [] : [OWNED_STYLES_NONE],
        };
      }
      const withoutNone = cur.filter((x) => x !== OWNED_STYLES_NONE);
      const next = withoutNone.includes(id)
        ? withoutNone.filter((x) => x !== id)
        : [...withoutNone, id];
      return { ...a, ownedStyles: next };
    });
  };

  const next = () => {
    if (safeStep < steps.length - 1) setStep(safeStep + 1);
    else {
      setDone(true);
      setSeed(0);
      setExclude([]);
    }
  };

  const back = () => {
    if (done) {
      setDone(false);
      setStep(visibleGiftSteps(answers).length - 1);
      return;
    }
    if (safeStep > 0) setStep(safeStep - 1);
  };

  const restart = () => {
    setAnswers(EMPTY_ANSWERS);
    setStep(0);
    setDone(false);
    setSeed(0);
    setExclude([]);
  };

  const reroll = (pick: GiftPick) => {
    setExclude((e) => [...e, pick.id]);
    setSeed((s) => s + 1);
  };

  return (
    <div className="pb-4">
      <div className="mb-3 flex items-center gap-2">
        <button
          type="button"
          onClick={() => navigate({ page: "shopping" })}
          className="font-display text-xs uppercase tracking-widest text-dim hover:text-zlato"
        >
          ← {t("nav.shopping")}
        </button>
      </div>

      <SectionTitle>{t("gift.title")}</SectionTitle>
      <p className="mb-3 text-sm leading-relaxed text-dim">{t("gift.intro")}</p>

      <MarketFilter label={t("gift.nearby")} className="mb-4" />

      {!done ? (
        <>
          <div className="mb-4 flex justify-center gap-2">
            {steps.map((id, i) => (
              <span
                key={id}
                className={`h-2 w-2 rounded-full ${i === safeStep ? "bg-zlato" : i < safeStep ? "bg-zlato/40" : "bg-dim/30"}`}
              />
            ))}
          </div>

          {stepId === "ownedStyles" ? (
            <OwnedStylesStep answers={answers} onToggle={toggleOwnedStyle} />
          ) : stepId === "drinkPick" ? (
            <DrinkPickStep
              value={answers.drinkPick ?? "unknown"}
              onChange={(value) => setAnswers((a) => ({ ...a, drinkPick: value }))}
            />
          ) : q ? (
            <>
              <h2 className="font-display text-lg text-papir">{lx(q.prompt)}</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {q.options.map((opt) => (
                  <Chip
                    key={opt.id}
                    active={currentVal === opt.id}
                    onClick={() => setCoreAnswer(q.id as CoreQuestionId, opt.id)}
                  >
                    {lx(opt.label)}
                  </Chip>
                ))}
              </div>
            </>
          ) : null}

          <div className="mt-6 flex gap-2">
            {safeStep > 0 && (
              <button
                type="button"
                onClick={back}
                className="flex-1 rounded-lg border border-dim/30 py-2.5 font-display text-xs uppercase tracking-widest text-dim"
              >
                {t("gift.back")}
              </button>
            )}
            <button
              type="button"
              onClick={next}
              className="flex-1 rounded-lg border border-zlato/50 bg-zlato/10 py-2.5 font-display text-xs uppercase tracking-widest text-zlato-2"
            >
              {safeStep < steps.length - 1 ? t("gift.next") : t("gift.show")}
            </button>
          </div>
        </>
      ) : (
        <>
          <p className="mb-2 text-xs text-dim">{t("gift.pricedNote")}</p>
          {results.some((p) => p.safeDefault) && (
            <p className="mb-3 rounded-xl border border-zlato/25 bg-zlato/5 p-3 text-xs leading-relaxed text-papir/85">
              {t("gift.safeDefault")}
            </p>
          )}
          {results.some((p) => p.kind === "pairing") && (
            <p className="mb-2 text-xs leading-relaxed text-dim">{t("gift.minMatchNote")}</p>
          )}
          {results.some((p) => p.droppedPairing) && (
            <p className="mb-2 text-xs leading-relaxed text-dim">{t("gift.noPairing")}</p>
          )}
          {results.some((p) => p.noGapLeft) && (
            <p className="mb-2 text-xs leading-relaxed text-dim">{t("gift.noGapLeft")}</p>
          )}
          {results.length === 0 ? (
            <p className="rounded-xl border border-dim/20 bg-cedar p-4 text-sm text-dim">
              {t("gift.empty")}
            </p>
          ) : (
            <div className="space-y-4">
              {results.map((pick) => (
                <GiftResultCard
                  key={`${pick.id}-${seed}`}
                  pick={pick}
                  onReroll={() => reroll(pick)}
                  onOpenCigar={sheets.openCigar}
                  onOpenDrink={sheets.openDrink}
                  onPair={onPair}
                />
              ))}
            </div>
          )}
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={restart}
              className="rounded-lg border border-dim/30 px-4 py-2 font-display text-xs uppercase tracking-widest text-dim"
            >
              {t("gift.restart")}
            </button>
            <button
              type="button"
              onClick={back}
              className="rounded-lg border border-dim/30 px-4 py-2 font-display text-xs uppercase tracking-widest text-dim"
            >
              {t("gift.editAnswers")}
            </button>
          </div>
          <p className="mt-4 text-xs leading-relaxed text-dim/80">⚖ {t("shop.legalNote")}</p>
        </>
      )}

      <CigarBrowseSheets
        line={sheets.line}
        detail={sheets.detail}
        onCloseLine={sheets.closeLine}
        onOpenVitola={sheets.openVitola}
        onCloseDetail={sheets.closeDetail}
        onOpenLine={sheets.openLine}
        onPair={
          onPair
            ? (target) => {
                sheets.closeSheets();
                onPair(target);
              }
            : undefined
        }
      />
    </div>
  );
}

function GiftResultCard({
  pick,
  onReroll,
  onOpenCigar,
  onOpenDrink,
  onPair,
}: {
  pick: GiftPick;
  onReroll: () => void;
  onOpenCigar: (c: Cigar) => void;
  onOpenDrink: (d: Drink) => void;
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx } = useI18n();

  const title = (() => {
    switch (pick.kind) {
      case "pairing":
        return t("gift.kind.pairing");
      case "cigar":
        return t("gift.kind.cigar");
      case "drink":
        return t("gift.kind.bottle");
      default: {
        const _exhaustive: never = pick.kind;
        return _exhaustive;
      }
    }
  })();

  const drinkHref = pick.drink ? drinkPrimaryLink(pick.drink).href : null;

  return (
    <article className="rounded-xl border border-zlato/25 bg-cedar/80 p-3.5">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-display text-sm uppercase tracking-[0.15em] text-zlato">{title}</h3>
        {pick.price != null && (
          <span className="shrink-0 font-display text-sm text-papir">{formatEur(pick.price)}</span>
        )}
      </div>
      {pick.matchScore != null && (
        <p className="mt-1 font-display text-xs uppercase tracking-widest text-zlato-2">
          {t("gift.match")} {pick.matchScore} %
        </p>
      )}
      {pick.swappedFromCategory && (
        <p className="mt-1 text-xs text-dim">
          {t("gift.swappedNote")}{" "}
          <span className="text-papir/90">{t(`cat.${pick.swappedFromCategory}`)}</span>
        </p>
      )}
      {pick.fellBackBudget && (
        <p className="mt-1 text-xs text-dim">{t("gift.fellBackBudget")}</p>
      )}
      {pick.noGapLeft && (
        <p className="mt-1 text-xs text-dim">{t("gift.noGapLeft")}</p>
      )}
      {pick.styleBucket && pick.kind === "pairing" && (
        <p className="mt-1 text-xs text-dim">{lx(pick.styleBucket.label)}</p>
      )}
      {pick.shop && (
        <p className="mt-1 text-xs text-dim">
          {t("gift.shop")}: <span className="text-papir/90">{pick.shop}</span>
        </p>
      )}

      <div className="mt-2 space-y-1">
        {pick.cigars?.map((c) => (
          <CigarRow key={c.id} cigar={c} onClick={() => onOpenCigar(c)} />
        ))}
        {pick.cigar && !pick.cigars && (
          <CigarRow cigar={pick.cigar} onClick={() => onOpenCigar(pick.cigar!)} />
        )}
        {pick.drink && <DrinkRow drink={pick.drink} onClick={() => onOpenDrink(pick.drink!)} />}
      </div>

      {pick.accessories && pick.accessories.length > 0 && (
        <ul className="mt-2 space-y-1 text-xs">
          {pick.accessories.map((a) => (
            <li key={a.url}>
              <a
                href={a.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-zlato underline-offset-2 hover:underline"
              >
                {lx(a.label)}
              </a>
            </li>
          ))}
        </ul>
      )}

      <p className="mt-2 border-l-2 border-zlato/30 pl-2.5 text-xs leading-relaxed text-papir/80">
        {lx(pick.why)}
      </p>

      <div className="mt-3 flex flex-wrap gap-2">
        {pick.drink && drinkHref && pick.region !== "HR" && (
          <a
            href={drinkHref}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-zlato/40 px-3 py-1.5 text-xs uppercase tracking-wider text-zlato"
          >
            {t("gift.buyDrink")}
          </a>
        )}
        {pick.drink && pick.region === "HR" && pick.drink.priceUrl && (
          <a
            href={pick.drink.priceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-zlato/40 px-3 py-1.5 text-xs uppercase tracking-wider text-zlato"
          >
            {t("gift.checkShop")}
          </a>
        )}
        {pick.kind === "pairing" && pick.cigar && pick.drink && onPair && (
          <button
            type="button"
            onClick={() => onPair({ kind: "cigar", item: pick.cigar! })}
            className="rounded-lg border border-dim/30 px-3 py-1.5 text-xs uppercase tracking-wider text-dim"
          >
            {t("gift.openPairing")}
          </button>
        )}
        <button
          type="button"
          onClick={onReroll}
          className="rounded-lg border border-dim/30 px-3 py-1.5 text-xs uppercase tracking-wider text-dim"
        >
          {t("gift.reroll")}
        </button>
      </div>
    </article>
  );
}

function OwnedStylesStep({
  answers,
  onToggle,
}: {
  answers: GiftAnswers;
  onToggle: (id: string) => void;
}) {
  const { t, lx } = useI18n();
  const owned = answers.ownedStyles ?? [];
  const buckets = answers.drink !== "unknown" ? (BUCKETS[answers.drink] ?? []) : [];
  const unknownActive = owned.length === 0;
  const noneActive = owned.length === 1 && owned[0] === OWNED_STYLES_NONE;

  return (
    <>
      <h2 className="font-display text-lg text-papir">{t("gift.ownedStyles")}</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {buckets.map((bucket) => (
          <Chip
            key={bucket.id}
            active={!unknownActive && !noneActive && owned.includes(bucket.id)}
            onClick={() => onToggle(bucket.id)}
          >
            {lx(bucket.label)}
          </Chip>
        ))}
        <Chip active={noneActive} onClick={() => onToggle(OWNED_STYLES_NONE)}>
          {t("gift.ownedStylesNone")}
        </Chip>
        <Chip active={unknownActive} onClick={() => onToggle("unknown")}>
          {t("gift.ownedStylesUnknown")}
        </Chip>
      </div>
    </>
  );
}

const DRINK_PICK_LABEL: Record<GiftDrinkPick, StringKey> = {
  gap: "gift.drinkPick.gap",
  top: "gift.drinkPick.top",
  value: "gift.drinkPick.value",
  unknown: "gift.drinkPick.unknown",
};

function DrinkPickStep({
  value,
  onChange,
}: {
  value: GiftDrinkPick;
  onChange: (value: GiftDrinkPick) => void;
}) {
  const { t } = useI18n();
  return (
    <>
      <h2 className="font-display text-lg text-papir">{t("gift.drinkPick")}</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {DRINK_PICK_OPTIONS.map((opt) => (
          <Chip key={opt} active={value === opt} onClick={() => onChange(opt)}>
            {t(DRINK_PICK_LABEL[opt])}
          </Chip>
        ))}
      </div>
    </>
  );
}
