import { useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
import { LessonBody } from "../components/LessonBody";
import hrGuide from "../data/hrGuide.json";

interface GuideSection {
  id: string;
  title: LocalizedText;
  body: LocalizedText;
}

const SECTIONS = hrGuide.sections as GuideSection[];

function preview(body: LocalizedText, lang: "hr" | "en"): string {
  const text = body[lang];
  const first = text.split("\n")[0] ?? text;
  return first.length > 112 ? first.slice(0, 109) + "…" : first;
}

export function HrGuidePage({ onBack }: { onBack: () => void }) {
  const { t, lx, lang } = useI18n();
  const [sectionId, setSectionId] = useState<string | null>(null);
  const section = sectionId ? SECTIONS.find((item) => item.id === sectionId) ?? null : null;

  if (section) {
    return (
      <div className="pb-4">
        <div className="mb-3">
          <BackButton onClick={() => setSectionId(null)}>{t("club.hrGuideBackList")}</BackButton>
        </div>
        <SectionTitle>{lx(section.title)}</SectionTitle>
        <article className="rounded-xl border border-zlato/20 bg-cedar px-4 py-5 sm:px-5">
          <LessonBody text={lx(section.body)} />
        </article>
      </div>
    );
  }

  return (
    <div className="pb-4">
      <div className="mb-3">
        <BackButton onClick={onBack}>{t("club.hrGuideBackClub")}</BackButton>
      </div>
      <SectionTitle>{lx(hrGuide.title as LocalizedText)}</SectionTitle>
      <p className="mb-1 font-display text-micro uppercase tracking-[0.18em] text-zlato/70">
        {t("club.hrGuideSubtitle")}
      </p>
      <p className="mb-4 text-sm leading-relaxed text-papir/80">{lx(hrGuide.intro as LocalizedText)}</p>
      <p className="mb-2 text-micro uppercase tracking-widest text-dim">
        {SECTIONS.length} {t("club.hrGuideSections")}
      </p>
      <div className="space-y-2">
        {SECTIONS.map((item, index) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setSectionId(item.id)}
            className="block w-full rounded-xl border border-dim/15 bg-cedar p-4 text-left transition-colors hover:border-zlato/40"
          >
            <div className="flex items-baseline gap-2.5">
              <span className="font-display text-micro tabular-nums text-zlato/60">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-display text-sm tracking-wide text-zlato-2">{lx(item.title)}</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-papir/65">{preview(item.body, lang)}</p>
            <span className="mt-3 inline-block font-display text-micro uppercase tracking-widest text-zlato">
              {t("club.hrGuideOpenSection")} →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
