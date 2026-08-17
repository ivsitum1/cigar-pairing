import { useMemo, useState } from "react";
import type { Cigar, Drink } from "../types";
import { ALL_DRINKS, CIGARS } from "../data";
import giftQuestions from "../data/giftQuestions.json";
import { useI18n } from "../i18n";
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
import {
  findGifts,
  type GiftAnswers,
  type GiftPick,
} from "../lib/giftFinder";

type QuestionId = keyof GiftAnswers;

const EMPTY_ANSWERS: GiftAnswers = {
  recipient: "unknown",
  budget: "unknown",
  drink: "unknown",
  intensity: "unknown",
  shape: "unknown",
};

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

  const results = useMemo(() => {
    if (!done) return [];
    return findGifts(answers, catalog, market, { seed, excludeIds: exclude });
  }, [answers, catalog, market, seed, exclude, done]);

  const q = giftQuestions[step];
  const currentVal = q ? answers[q.id as QuestionId] : undefined;

  const setAnswer = (id: QuestionId, value: GiftAnswers[QuestionId]) => {
    setAnswers((a) => ({ ...a, [id]: value }));
  };

  const next = () => {
    if (step < giftQuestions.length - 1) setStep((s) => s + 1);
    else {
      setDone(true);
      setSeed(0);
      setExclude([]);
    }
  };

  const back = () => {
    if (done) {
      setDone(false);
      setStep(giftQuestions.length - 1);
      return;
    }
    if (step > 0) setStep((s) => s - 1);
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
            {giftQuestions.map((_, i) => (
              <span
                key={i}
                className={`h-2 w-2 rounded-full ${i === step ? "bg-zlato" : i < step ? "bg-zlato/40" : "bg-dim/30"}`}
              />
            ))}
          </div>

          <h2 className="font-display text-lg text-papir">{lx(q.prompt)}</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {q.options.map((opt) => (
              <Chip
                key={opt.id}
                active={currentVal === opt.id}
                onClick={() => setAnswer(q.id as QuestionId, opt.id as GiftAnswers[QuestionId])}
              >
                {lx(opt.label)}
              </Chip>
            ))}
          </div>

          <div className="mt-6 flex gap-2">
            {step > 0 && (
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
              {step < giftQuestions.length - 1 ? t("gift.next") : t("gift.show")}
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
