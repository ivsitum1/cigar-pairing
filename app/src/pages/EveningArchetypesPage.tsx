import { useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
import { LessonBody } from "../components/LessonBody";
import eveningArchetypes from "../data/eveningArchetypes.json";

interface EveningArchetype {
  id: string;
  title: LocalizedText;
  body: LocalizedText;
  styleTags?: string[];
}

const ENTRIES = eveningArchetypes.entries as EveningArchetype[];

function preview(body: LocalizedText, lang: "hr" | "en"): string {
  const text = body[lang];
  const first = text.split("\n")[0] ?? text;
  return first.length > 112 ? first.slice(0, 109) + "…" : first;
}

export function EveningArchetypesPage({ onBack }: { onBack: () => void }) {
  const { t, lx, lang } = useI18n();
  const [entryId, setEntryId] = useState<string | null>(null);
  const entry = entryId ? ENTRIES.find((item) => item.id === entryId) ?? null : null;

  if (entry) {
    return (
      <div className="pb-4">
        <div className="mb-3">
          <BackButton onClick={() => setEntryId(null)}>{t("club.archetypesBackList")}</BackButton>
        </div>
        <SectionTitle>{lx(entry.title)}</SectionTitle>
        {entry.styleTags?.length ? (
          <div className="mb-3 flex flex-wrap gap-1.5">
            {entry.styleTags.map((tag) => (
              <span
                key={tag}
                className="rounded-full border border-zlato/25 px-2 py-1 text-[10px] uppercase tracking-widest text-zlato/75"
              >
                {tag}
              </span>
            ))}
          </div>
        ) : null}
        <article className="rounded-xl border border-zlato/20 bg-cedar px-4 py-5 sm:px-5">
          <LessonBody text={lx(entry.body)} />
        </article>
      </div>
    );
  }

  return (
    <div className="pb-4">
      <div className="mb-3">
        <BackButton onClick={onBack}>{t("club.archetypesBackClub")}</BackButton>
      </div>
      <SectionTitle>{lx(eveningArchetypes.title as LocalizedText)}</SectionTitle>
      <p className="mb-1 font-display text-[11px] uppercase tracking-[0.18em] text-zlato/70">
        {t("club.archetypesSubtitle")}
      </p>
      <p className="mb-4 text-sm leading-relaxed text-papir/80">
        {lx(eveningArchetypes.intro as LocalizedText)}
      </p>
      <p className="mb-2 text-[10px] uppercase tracking-widest text-dim">
        {ENTRIES.length} {t("club.archetypesEntries")}
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
              <span className="font-display text-[10px] tabular-nums text-zlato/60">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-display text-sm tracking-wide text-zlato-2">{lx(item.title)}</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-papir/65">{preview(item.body, lang)}</p>
            {item.styleTags?.length ? (
              <p className="mt-2 text-[10px] uppercase tracking-widest text-dim">
                {item.styleTags.join(" · ")}
              </p>
            ) : null}
            <span className="mt-3 inline-block font-display text-[10px] uppercase tracking-widest text-zlato">
              {t("club.archetypesOpenEntry")} →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
