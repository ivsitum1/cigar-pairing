import { useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
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
        <article className="rounded-xl border border-dim/15 bg-cedar p-4">
          {lx(lesson.body)
            .split("\n\n")
            .map((para, i) => (
              <p key={i} className={`text-sm leading-relaxed text-papir/90 ${i > 0 ? "mt-3" : ""}`}>
                {para}
              </p>
            ))}
          {lesson.shopLinks && lesson.shopLinks.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {lesson.shopLinks.map((link) => (
                <a
                  key={link.url + link.label.hr}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-full border border-zlato/40 px-3 py-1.5 font-display text-[10px] uppercase tracking-widest text-zlato hover:bg-zlato/10"
                >
                  {t("club.shopLink")}: {lx(link.label)} ↗
                </a>
              ))}
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
      <p className="mb-2 text-[10px] uppercase tracking-widest text-dim">
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
            <div className="flex items-baseline gap-2">
              <span className="font-display text-[10px] text-zlato/70">{String(index + 1).padStart(2, "0")}</span>
              <h3 className="font-display text-sm text-zlato-2">{lx(card.title)}</h3>
            </div>
            <p className="mt-1.5 text-xs leading-relaxed text-papir/70">{preview(card.body, lang)}</p>
            <span className="mt-2 inline-block font-display text-[10px] uppercase tracking-widest text-zlato">
              {t("club.101OpenLesson")} →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
