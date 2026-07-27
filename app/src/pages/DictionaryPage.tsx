import { useMemo, useState } from "react";
import type { LocalizedText } from "../types";
import { useI18n } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { BackButton } from "../components/BackButton";
import dictionary from "../data/dictionary.json";

type DictionaryCategory = "cigar" | "drink" | "pairing" | "table";

interface DoNotConfuse {
  with: string;
  note: LocalizedText;
}

interface DictionaryEntry {
  id: string;
  term: LocalizedText;
  def: LocalizedText;
  body: LocalizedText;
  aliases: string[];
  seeAlso: string[];
  category: DictionaryCategory;
  doNotConfuse?: DoNotConfuse[];
}

const ENTRIES = dictionary.entries as DictionaryEntry[];
const BY_ID = new Map(ENTRIES.map((e) => [e.id, e]));

const CATEGORIES: Array<DictionaryCategory | "all"> = [
  "all",
  "cigar",
  "drink",
  "pairing",
  "table",
];

function letterKey(term: string): string {
  const ch = term.trim().charAt(0).toLocaleUpperCase("hr");
  if (/[A-ZÁČĆĐŠŽ]/i.test(ch) || /[A-Z]/.test(ch)) return ch.normalize("NFC");
  // Digits / symbols → #
  if (/[0-9]/.test(ch)) return "#";
  return ch || "#";
}

function BodyParagraphs({ text }: { text: string }) {
  const parts = text.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
  return (
    <div className="space-y-3">
      {parts.map((p, i) => (
        <p key={i} className="text-sm leading-relaxed text-papir/90 whitespace-pre-wrap">
          {p}
        </p>
      ))}
    </div>
  );
}

export function DictionaryPage({ onBack }: { onBack: () => void }) {
  const { t, lx, lang } = useI18n();
  const [entryId, setEntryId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<DictionaryCategory | "all">("all");

  const filtered = useMemo(() => {
    const q = query.trim().toLocaleLowerCase("hr");
    return ENTRIES.filter((e) => {
      if (category !== "all" && e.category !== category) return false;
      if (!q) return true;
      const hay = [
        e.term.hr,
        e.term.en,
        e.def.hr,
        e.def.en,
        ...e.aliases,
      ]
        .join("\n")
        .toLocaleLowerCase("hr");
      return hay.includes(q);
    });
  }, [query, category]);

  const letters = useMemo(() => {
    const set = new Set<string>();
    for (const e of filtered) set.add(letterKey(lx(e.term)));
    return Array.from(set).sort((a, b) => a.localeCompare(b, lang === "en" ? "en" : "hr"));
  }, [filtered, lx, lang]);

  const entry = entryId ? BY_ID.get(entryId) ?? null : null;

  const catLabel = (c: DictionaryCategory | "all") => {
    switch (c) {
      case "all":
        return t("club.dictionaryCatAll");
      case "cigar":
        return t("club.dictionaryCatCigar");
      case "drink":
        return t("club.dictionaryCatDrink");
      case "pairing":
        return t("club.dictionaryCatPairing");
      case "table":
        return t("club.dictionaryCatTable");
      default: {
        const _exhaustive: never = c;
        return _exhaustive;
      }
    }
  };

  if (entry) {
    return (
      <div className="pb-4">
        <div className="mb-3">
          <BackButton onClick={() => setEntryId(null)}>{t("club.dictionaryBackList")}</BackButton>
        </div>
        <SectionTitle>{lx(entry.term)}</SectionTitle>
        <p className="mb-1 font-display text-micro uppercase tracking-[0.18em] text-zlato/70">
          {catLabel(entry.category)}
        </p>
        <article className="rounded-xl border border-zlato/20 bg-cedar px-4 py-5 sm:px-5">
          <p className="mb-4 text-sm font-medium leading-relaxed text-papir">{lx(entry.def)}</p>
          <BodyParagraphs text={lx(entry.body)} />
          {(entry.doNotConfuse?.length ?? 0) > 0 && (
            <div className="mt-5 border-t border-dim/15 pt-4">
              <h3 className="mb-2 font-display text-micro uppercase tracking-[0.18em] text-zlato">
                {t("club.dictionaryDoNotConfuse")}
              </h3>
              <ul className="space-y-2">
                {entry.doNotConfuse!.map((d) => {
                  const other = BY_ID.get(d.with);
                  return (
                    <li key={d.with} className="text-sm leading-relaxed text-papir/85">
                      {other ? (
                        <button
                          type="button"
                          className="font-medium text-zlato-2 underline-offset-2 hover:underline"
                          onClick={() => setEntryId(d.with)}
                        >
                          {lx(other.term)}
                        </button>
                      ) : (
                        <span className="font-medium text-zlato-2">{d.with}</span>
                      )}
                      <span className="text-dim"> — </span>
                      {lx(d.note)}
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
          {entry.seeAlso.length > 0 && (
            <div className="mt-5 border-t border-dim/15 pt-4">
              <h3 className="mb-2 font-display text-micro uppercase tracking-[0.18em] text-zlato">
                {t("club.dictionarySeeAlso")}
              </h3>
              <div className="flex flex-wrap gap-2">
                {entry.seeAlso.map((id) => {
                  const other = BY_ID.get(id);
                  if (!other) return null;
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setEntryId(id)}
                      className="rounded-full border border-zlato/35 px-3 py-1 font-display text-micro uppercase tracking-widest text-zlato hover:bg-zlato/10"
                    >
                      {lx(other.term)}
                    </button>
                  );
                })}
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
        <BackButton onClick={onBack}>{t("club.dictionaryBackClub")}</BackButton>
      </div>
      <SectionTitle>{lx(dictionary.title as LocalizedText)}</SectionTitle>
      <p className="mb-1 font-display text-micro uppercase tracking-[0.18em] text-zlato/70">
        {t("club.dictionarySubtitle")}
      </p>
      <p className="mb-4 text-sm leading-relaxed text-papir/80">{lx(dictionary.intro as LocalizedText)}</p>

      <label className="mb-3 block">
        <span className="sr-only">{t("club.dictionarySearch")}</span>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t("club.dictionarySearch")}
          className="w-full rounded-xl border border-dim/20 bg-cedar px-3 py-2.5 text-sm text-papir placeholder:text-dim/60 focus:border-zlato/40 focus:outline-none"
        />
      </label>

      <div className="mb-3 flex flex-wrap gap-1.5">
        {CATEGORIES.map((c) => (
          <Chip key={c} active={category === c} onClick={() => setCategory(c)}>
            {catLabel(c)}
          </Chip>
        ))}
      </div>

      {letters.length > 1 && (
        <div className="mb-3 flex flex-wrap gap-1">
          {letters.map((L) => (
            <a
              key={L}
              href={`#letter-${encodeURIComponent(L)}`}
              className="rounded px-1.5 py-0.5 font-display text-micro text-zlato/80 hover:bg-zlato/10"
            >
              {L}
            </a>
          ))}
        </div>
      )}

      <p className="mb-2 text-micro uppercase tracking-widest text-dim">
        {filtered.length} {t("club.dictionaryEntries")}
      </p>

      {filtered.length === 0 ? (
        <p className="rounded-xl border border-dim/15 bg-cedar p-4 text-sm text-papir/70">
          {t("club.dictionaryEmpty")}
        </p>
      ) : (
        <div className="space-y-2">
          {filtered.map((item, index) => {
            const L = letterKey(lx(item.term));
            const prev = index > 0 ? letterKey(lx(filtered[index - 1].term)) : null;
            const showLetter = L !== prev;
            return (
              <div key={item.id}>
                {showLetter && (
                  <h3
                    id={`letter-${L}`}
                    className="mb-1.5 mt-3 scroll-mt-20 font-display text-micro uppercase tracking-[0.2em] text-zlato/60 first:mt-0"
                  >
                    {L}
                  </h3>
                )}
                <button
                  type="button"
                  onClick={() => setEntryId(item.id)}
                  className="block w-full rounded-xl border border-dim/15 bg-cedar p-4 text-left transition-colors hover:border-zlato/40"
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <h4 className="font-display text-sm tracking-wide text-zlato-2">{lx(item.term)}</h4>
                    <span className="shrink-0 font-display text-micro uppercase tracking-widest text-dim">
                      {catLabel(item.category)}
                    </span>
                  </div>
                  <p className="mt-2 text-xs leading-relaxed text-papir/65">{lx(item.def)}</p>
                  <span className="mt-3 inline-block font-display text-micro uppercase tracking-widest text-zlato">
                    {t("club.dictionaryOpenEntry")} →
                  </span>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
