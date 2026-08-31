import { useEffect, useState } from "react";
import { useI18n } from "../i18n";
import {
  appendPromptStarter,
  appendSuggestion,
  applySkeleton,
  promptsFor,
  ratingScaleSummary,
  skeletonFor,
  type NotePromptContext,
} from "../lib/ratingPrompts";

/**
 * Šprance + banka prijedloga: pitanje otvara riječi koje početnik može
 * tipnuti umjesto praznog lista. Ocjenska ljestvica je opcionalna.
 */
export function NotePrompts({
  context,
  value,
  onChange,
  showRatingScale = false,
}: {
  context: NotePromptContext;
  value: string;
  onChange: (next: string) => void;
  showRatingScale?: boolean;
}) {
  const { t, lx, lang } = useI18n();
  const questions = promptsFor(context);
  const [activeId, setActiveId] = useState(questions[0]?.id ?? "");

  useEffect(() => {
    setActiveId(promptsFor(context)[0]?.id ?? "");
  }, [context]);

  const active = questions.find((q) => q.id === activeId) ?? questions[0];

  const pickQuestion = (id: string) => {
    const q = questions.find((x) => x.id === id);
    if (!q) return;
    setActiveId(id);
    onChange(appendPromptStarter(value, lx(q.starter)));
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs uppercase tracking-widest text-dim">
          {t("notePrompts.title")}
        </span>
        <button
          type="button"
          onClick={() => onChange(applySkeleton(value, skeletonFor(context, lang)))}
          disabled={value.trim().length > 0}
          className="rounded-md border border-dim/30 px-2 py-1 font-display text-micro uppercase tracking-wider text-dim disabled:opacity-40"
        >
          {t("notePrompts.insertSkeleton")}
        </button>
      </div>
      <p className="text-micro leading-relaxed text-dim/90">{t("notePrompts.hint")}</p>
      <div className="flex flex-wrap gap-1.5">
        {questions.map((q) => (
          <button
            key={q.id}
            type="button"
            title={lx(q.hint)}
            aria-pressed={q.id === active?.id}
            onClick={() => pickQuestion(q.id)}
            className={
              q.id === active?.id
                ? "rounded-md border border-zlato bg-zlato/20 px-2 py-1 text-xs text-zlato-2"
                : "rounded-md border border-zlato/30 bg-zlato/5 px-2 py-1 text-xs text-zlato-2 hover:bg-zlato/15"
            }
          >
            {lx(q.label)}
          </button>
        ))}
      </div>

      {active && active.suggestions.length > 0 && (
        <div className="rounded-lg border border-dim/20 bg-cedar/60 px-2.5 py-2">
          <div className="text-micro uppercase tracking-wider text-dim">
            {t("notePrompts.suggestions")} · {lx(active.label)}
          </div>
          <p className="mt-0.5 text-micro leading-relaxed text-dim/85">{lx(active.hint)}</p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {active.suggestions.map((s) => {
              const label = lx(s);
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() =>
                    onChange(appendSuggestion(value, lx(active.starter), label))
                  }
                  className="rounded-md border border-dim/25 bg-humidor px-2 py-1 text-xs text-papir/90 hover:border-zlato/40 hover:text-zlato-2"
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {showRatingScale && (
        <p className="text-micro leading-relaxed text-dim/80">
          {t("notePrompts.ratingScale")}: {ratingScaleSummary(lang)}
        </p>
      )}
    </div>
  );
}
