import { useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
import { LessonBody } from "../components/LessonBody";
import lexicon from "../data/lexicon.json";

interface LexiconEntry {
  id: string;
  title: LocalizedText;
  body: string;
}

const ENTRIES = lexicon.entries as LexiconEntry[];

function preview(body: string): string {
  const first = body.split("\n")[0] ?? body;
  return first.length > 115 ? first.slice(0, 112) + "…" : first;
}

export function LexiconPage({ onBack }: { onBack: () => void }) {
  const { t, lx } = useI18n();
  const [entryId, setEntryId] = useState<string | null>(null);
  const entry = entryId ? ENTRIES.find((item) => item.id === entryId) ?? null : null;

  if (entry) {
    return (
      <div className="pb-4">
        <div className="mb-3">
          <BackButton onClick={() => setEntryId(null)}>{t("club.lexiconBackList")}</BackButton>
        </div>
        <SectionTitle>{lx(entry.title)}</SectionTitle>
        <article className="rounded-xl border border-zlato/20 bg-cedar px-4 py-5 sm:px-5">
          <LessonBody text={entry.body} />
        </article>
      </div>
    );
  }

  return (
    <div className="pb-4">
      <div className="mb-3">
        <BackButton onClick={onBack}>{t("club.lexiconBackClub")}</BackButton>
      </div>
      <SectionTitle>{lx(lexicon.title as LocalizedText)}</SectionTitle>
      <p className="mb-1 font-display text-micro uppercase tracking-[0.18em] text-zlato/70">
        {t("club.lexiconSubtitle")}
      </p>
      <p className="mb-4 text-sm leading-relaxed text-papir/80">{lx(lexicon.intro as LocalizedText)}</p>
      <p className="mb-2 text-micro uppercase tracking-widest text-dim">
        {ENTRIES.length} {t("club.lexiconEntries")}
      </p>
      <div className="space-y-2">
        {ENTRIES.map((item, index) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setEntryId(item.id)}
            className="block w-full rounded-xl border border-dim/15 bg-cedar p-4 text-left transition-colors hover:border-zlato/40"
          >
            <div className="flex items-baseline gap-2.5">
              <span className="font-display text-micro tabular-nums text-zlato/60">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-display text-sm tracking-wide text-zlato-2">{lx(item.title)}</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-papir/65">{preview(item.body)}</p>
            <span className="mt-3 inline-block font-display text-micro uppercase tracking-widest text-zlato">
              {t("club.lexiconOpenEntry")} →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
