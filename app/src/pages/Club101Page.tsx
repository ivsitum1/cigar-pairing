import { useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
import { LessonBody } from "../components/LessonBody";
import club101 from "../data/club101.json";

interface ShopLink { label: LocalizedText; url: string }
interface GuideCard {
  id: string;
  title: LocalizedText;
  body: LocalizedText;
  shopLinks?: ShopLink[];
}
export type GuideTrack = "cigars" | "drinks" | "accessories" | "tips";

const GUIDE_TRACKS = club101.tracks as Record<GuideTrack, GuideCard[]>;

const TRACK_KEYS: Record<GuideTrack, "club.trackCigars" | "club.trackDrinks" | "club.trackAccessories" | "club.trackTips"> = {
  cigars: "club.trackCigars",
  drinks: "club.trackDrinks",
  accessories: "club.trackAccessories",
  tips: "club.trackTips",
};

function preview(body: LocalizedText, lang: "hr" | "en"): string {
  const text = body[lang];
  const first = text.split("\n")[0] ?? text;
  return first.length > 120 ? first.slice(0, 117) + "…" : first;
}

export function Club101Page({ onBack }: { onBack: () => void }) {
  const { t, lx, lang } = useI18n();
  const [track, setTrack] = useState<GuideTrack>("cigars");
  const [lessonId, setLessonId] = useState<string | null>(null);
  const cards = GUIDE_TRACKS[track];
  const lesson = lessonId ? cards.find((c) => c.id === lessonId) ?? null : null;

  if (lesson) {
    return (
      <div className="pb-4">
        <div className="mb-3">
          <BackButton onClick={() => setLessonId(null)}>{t("club.101BackTrack")}</BackButton>
        </div>
        <SectionTitle>{lx(lesson.title)}</SectionTitle>
        <article className="rounded-xl border border-dim/15 bg-cedar px-4 py-5 sm:px-5">
          <LessonBody text={lx(lesson.body)} />
          {lesson.shopLinks && lesson.shopLinks.length > 0 && (
            <div className="mt-6 border-t border-dim/15 pt-4">
              <p className="mb-2.5 font-display text-micro uppercase tracking-[0.18em] text-dim">
                {t("club.shopLink")}
              </p>
              <div className="flex flex-wrap gap-2">
                {lesson.shopLinks.map((link) => (
                  <a
                    key={link.url + link.label.hr}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-full border border-zlato/40 px-3 py-1.5 font-display text-micro uppercase tracking-widest text-zlato hover:bg-zlato/10"
                  >
                    {lx(link.label)} ↗
                  </a>
                ))}
              </div>
            </div>
          )}
        </article>
      </div>
    );
  }

  return (
    <div className="pb-4">
      <div className="mb-3">
        <BackButton onClick={onBack}>{t("club.101BackClub")}</BackButton>
      </div>
      <SectionTitle>{t("club.101")}</SectionTitle>
      <p className="mb-3 text-xs leading-relaxed text-dim">{t("club.101CourseHint")}</p>
      <div className="mb-3 flex flex-wrap gap-2">
        {(Object.keys(TRACK_KEYS) as GuideTrack[]).map((id) => (
          <Chip key={id} active={track === id} onClick={() => setTrack(id)}>
            {t(TRACK_KEYS[id])}
          </Chip>
        ))}
      </div>
      <p className="mb-2 text-micro uppercase tracking-widest text-dim">
        {cards.length} {t("club.101Lessons")}
      </p>
      <div className="space-y-2">
        {cards.map((card, index) => (
          <button
            key={card.id}
            type="button"
            onClick={() => setLessonId(card.id)}
            className="block w-full rounded-xl border border-dim/15 bg-cedar p-4 text-left transition-colors hover:border-zlato/40"
          >
            <div className="flex items-baseline gap-2.5">
              <span className="font-display text-micro tabular-nums text-zlato/60">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-display text-sm tracking-wide text-zlato-2">{lx(card.title)}</h3>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-papir/65">{preview(card.body, lang)}</p>
            <span className="mt-3 inline-block font-display text-micro uppercase tracking-widest text-zlato">
              {t("club.101OpenLesson")} →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
