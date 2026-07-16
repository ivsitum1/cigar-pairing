import { useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
import { LessonBody } from "../components/LessonBody";
import bonton from "../data/bonton.json";

interface Chapter {
  id: string;
  title: LocalizedText;
  body: LocalizedText;
}

const CHAPTERS = bonton.chapters as Chapter[];

function preview(body: LocalizedText, lang: "hr" | "en"): string {
  const text = body[lang];
  const first = text.split("\n")[0] ?? text;
  return first.length > 110 ? first.slice(0, 107) + "…" : first;
}

export function BontonPage({ onBack }: { onBack: () => void }) {
  const { t, lx, lang } = useI18n();
  const [chapterId, setChapterId] = useState<string | null>(null);
  const chapter = chapterId ? CHAPTERS.find((c) => c.id === chapterId) ?? null : null;

  if (chapter) {
    return (
      <div className="pb-4">
        <div className="mb-3">
          <BackButton onClick={() => setChapterId(null)}>{t("club.bontonBackList")}</BackButton>
        </div>
        <SectionTitle>{lx(chapter.title)}</SectionTitle>
        <article className="rounded-xl border border-zlato/20 bg-cedar px-4 py-5 sm:px-5">
          <LessonBody text={lx(chapter.body)} />
        </article>
      </div>
    );
  }

  return (
    <div className="pb-4">
      <div className="mb-3">
        <BackButton onClick={onBack}>{t("club.101BackClub")}</BackButton>
      </div>
      <SectionTitle>{lx(bonton.title as LocalizedText)}</SectionTitle>
      <p className="mb-1 font-display text-[11px] uppercase tracking-[0.18em] text-zlato/70">
        {t("club.bontonSubtitle")}
      </p>
      <p className="mb-4 text-sm leading-relaxed text-papir/80">{lx(bonton.epigraph as LocalizedText)}</p>
      <p className="mb-2 text-[10px] uppercase tracking-widest text-dim">
        {CHAPTERS.length} {t("club.bontonChapters")}
      </p>
      <div className="space-y-2">
        {CHAPTERS.map((ch, index) => (
          <button
            key={ch.id}
            type="button"
            onClick={() => setChapterId(ch.id)}
            className="block w-full rounded-xl border border-dim/15 bg-cedar p-4 text-left transition-colors hover:border-zlato/40"
          >
            <div className="flex items-baseline gap-2.5">
              <span className="font-display text-[10px] tabular-nums text-zlato/60">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-display text-sm tracking-wide text-zlato-2">{lx(ch.title)}</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-papir/65">{preview(ch.body, lang)}</p>
            <span className="mt-3 inline-block font-display text-[10px] uppercase tracking-widest text-zlato">
              {t("club.bontonOpenChapter")} →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
