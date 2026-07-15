import { useMemo, useState } from "react";
import type { Cigar, Drink, LocalizedText } from "../types";
import { ALL_DRINKS, CIGARS } from "../data";
import { useI18n } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { DetailSheet } from "../components/DetailSheet";
import { COUNTRIES, cigarCountries, drinkCountries, type CountryInfo } from "../lib/geo";
import club from "../data/club.json";
import WORLD_OUTLINE from "../data/world_outline.json";

interface Quote { text: LocalizedText; author: string; note?: LocalizedText }
interface Fact { hr: string; en: string }
interface QuizQ { q: LocalizedText; a: LocalizedText[]; correct: number; why: LocalizedText }

const QUOTES = club.quotes as Quote[];
const FACTS = club.facts as Fact[];
const QUIZ = club.quiz as QuizQ[];

// dan u godini — deterministicki "dnevni" izbor
const dayOfYear = () => {
  const now = new Date();
  return Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 0).getTime()) / 86400000);
};

// deterministicko mijesanje pitanja (mulberry32 + Fisher-Yates), seed = datum
function shuffledOrder(n: number, seed: number): number[] {
  let s = seed >>> 0;
  const rnd = () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const idx = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [idx[i], idx[j]] = [idx[j], idx[i]];
  }
  return idx;
}

const BEST_KEY = "club-quiz-best-streak";

export function ClubPage() {
  const { t, lx } = useI18n();
  const day = dayOfYear();

  // citat i zanimljivost dana (+ rucno listanje zanimljivosti)
  const quote = QUOTES[day % QUOTES.length];
  const [factOffset, setFactOffset] = useState(0);
  const fact = FACTS[(day + factOffset) % FACTS.length];

  // kviz: dnevno promijesan redoslijed, sekvencijalno kroz pitanja
  const order = useMemo(() => shuffledOrder(QUIZ.length, day * 2654435761), [day]);
  const [qPos, setQPos] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [score, setScore] = useState({ ok: 0, total: 0 });
  const [streak, setStreak] = useState(0);
  const [best, setBest] = useState(() => Number(localStorage.getItem(BEST_KEY) ?? 0));
  const question = QUIZ[order[qPos % order.length]];

  const answer = (i: number) => {
    if (picked != null) return;
    setPicked(i);
    const ok = i === question.correct;
    setScore((s) => ({ ok: s.ok + (ok ? 1 : 0), total: s.total + 1 }));
    const ns = ok ? streak + 1 : 0;
    setStreak(ns);
    if (ns > best) {
      setBest(ns);
      localStorage.setItem(BEST_KEY, String(ns));
    }
  };
  const nextQ = () => {
    setPicked(null);
    setQPos((p) => p + 1);
  };

  // karta
  const [view, setView] = useState<"world" | "carib" | "europe">("world");
  const [country, setCountry] = useState<CountryInfo | null>(null);
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);

  // zemlje koje stvarno imaju proizvode + broj
  const countryCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const d of ALL_DRINKS) {
      for (const c of drinkCountries(d)) counts.set(c.hr, (counts.get(c.hr) ?? 0) + 1);
    }
    for (const c of CIGARS) {
      for (const ci of cigarCountries(c)) counts.set(ci.hr, (counts.get(ci.hr) ?? 0) + 1);
    }
    return counts;
  }, []);
  const active = COUNTRIES.filter((c) => (countryCounts.get(c.hr) ?? 0) > 0);

  const countryDrinks = useMemo(
    () => (country ? ALL_DRINKS.filter((d) => drinkCountries(d).includes(country)) : []),
    [country],
  );
  const countryCigars = useMemo(
    () => (country ? CIGARS.filter((c) => cigarCountries(c).includes(country)) : []),
    [country],
  );

  // projekcija: x = lon+180, y = 75-lat (viewBox pokriva lat -45..75)
  const X = (lon: number) => lon + 180;
  const Y = (lat: number) => 75 - lat;
  // zoom pogledi: Karibi lon -108..-50 / lat 1..37; Europa lon -12..48 / lat 34..62
  const VIEWBOXES: Record<typeof view, string> = {
    world: "0 0 360 120",
    carib: "72 38 58 36",
    europe: "168 13 60 28",
  };
  const viewBox = VIEWBOXES[view];
  const markerSize = view === "world" ? 7 : 3.2;

  // Atlas: Natural Earth obrisi kopna (world_outline.json generira
  // scripts/build-world-outline.mjs). Jedan <path> s evenodd popunom —
  // rupe (jezera/unutarnji prsteni) ostaju "ocean".
  const landPath = useMemo(() => {
    const polygons = WORLD_OUTLINE as Array<Array<Array<[number, number]>>>;
    const parts: string[] = [];
    for (const rings of polygons) {
      for (const ring of rings) {
        const [lon0, lat0] = ring[0];
        let d = `M${X(lon0)} ${Y(lat0)}`;
        for (let i = 1; i < ring.length; i++) {
          const [lon, lat] = ring[i];
          d += `L${X(lon)} ${Y(lat)}`;
        }
        parts.push(d + "Z");
      }
    }
    return parts.join("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="pb-4">
      {/* citat dana */}
      <SectionTitle>{t("club.quote")}</SectionTitle>
      <figure className="rounded-xl border border-zlato/25 bg-cedar p-4">
        <blockquote className="font-display text-[15px] leading-relaxed text-papir">
          „{lx(quote.text)}”
        </blockquote>
        <figcaption className="mt-2 text-xs text-zlato-2">
          — {quote.author}
          {quote.note && <span className="text-dim"> ({lx(quote.note)})</span>}
        </figcaption>
      </figure>

      {/* znas li? */}
      <SectionTitle>{t("club.fact")}</SectionTitle>
      <div className="rounded-xl border border-dim/15 bg-cedar p-4">
        <p className="text-sm leading-relaxed text-papir/90">💡 {lx(fact)}</p>
        <button
          onClick={() => setFactOffset((o) => o + 1)}
          className="mt-3 rounded-full border border-zlato/40 px-3 py-1.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("club.factNext")} →
        </button>
      </div>

      {/* kviz */}
      <SectionTitle>{t("club.quiz")}</SectionTitle>
      <div className="rounded-xl border border-dim/15 bg-cedar p-4">
        <div className="mb-2 flex items-baseline justify-between text-xs text-dim">
          <span>
            {t("club.quizScore")}: <span className="text-zlato-2">{score.ok}/{score.total}</span>
          </span>
          <span>
            {t("club.quizStreak")}: <span className="text-zlato-2">{streak}</span> · 🏆 {best}
          </span>
        </div>
        <p className="text-sm leading-relaxed text-papir">{lx(question.q)}</p>
        <div className="mt-3 space-y-1.5">
          {question.a.map((opt, i) => {
            const isCorrect = i === question.correct;
            const cls =
              picked == null
                ? "border-dim/25 hover:border-zlato/50"
                : isCorrect
                  ? "border-lista bg-lista/15"
                  : i === picked
                    ? "border-oxblood bg-oxblood/15"
                    : "border-dim/15 opacity-60";
            return (
              <button
                key={i}
                onClick={() => answer(i)}
                disabled={picked != null}
                className={`block w-full rounded-lg border px-3 py-2 text-left text-sm text-papir/90 transition-colors ${cls}`}
              >
                {String.fromCharCode(65 + i)}. {lx(opt)}
              </button>
            );
          })}
        </div>
        {picked != null && (
          <>
            <p className="mt-3 rounded-lg border border-zlato/25 bg-zlato/10 px-3 py-2 text-xs leading-relaxed text-papir/90">
              {picked === question.correct ? "✓ " + t("club.correct") : "✗ " + t("club.wrong")} — {lx(question.why)}
            </p>
            <button
              onClick={nextQ}
              className="mt-3 w-full rounded-lg border border-zlato/40 py-2 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
            >
              {t("club.quizNext")} →
            </button>
          </>
        )}
      </div>

      {/* karta */}
      <SectionTitle>{t("club.map")}</SectionTitle>
      <p className="mb-2 text-xs leading-relaxed text-dim">{t("club.mapHint")}</p>
      <div className="mb-2 flex gap-2">
        <Chip active={view === "world"} onClick={() => setView("world")}>
          🌍 {t("club.mapWorld")}
        </Chip>
        <Chip active={view === "carib"} onClick={() => setView("carib")}>
          🏝 {t("club.mapCarib")}
        </Chip>
        <Chip active={view === "europe"} onClick={() => setView("europe")}>
          🏛 {t("club.mapEurope")}
        </Chip>
      </div>
      <div className="overflow-hidden rounded-xl border border-dim/15 bg-humidor/80">
        <svg viewBox={viewBox} className="block w-full" role="img" aria-label={t("club.map")}>
          {/* ocean = tamna pozadina; kopno = monokromna ispuna + tanka obala.
              Eksplicitne opacity vrijednosti — currentColor s alpha klasom bi
              se množio sa strokeOpacity i obala bi postala nevidljiva. */}
          <path
            d={landPath}
            fillRule="evenodd"
            fill="var(--color-papir)"
            fillOpacity={0.1}
            stroke="var(--color-papir)"
            strokeOpacity={0.35}
            strokeWidth={0.5}
            vectorEffect="non-scaling-stroke"
            strokeLinejoin="round"
          />
          {/* graticule */}
          {Array.from({ length: 11 }, (_, i) => i * 36).map((x) => (
            <line key={`v${x}`} x1={x} y1={0} x2={x} y2={120} stroke="currentColor" strokeWidth={0.15} className="text-dim/30" />
          ))}
          {Array.from({ length: 5 }, (_, i) => i * 30).map((y) => (
            <line key={`h${y}`} x1={0} y1={y} x2={360} y2={y} stroke="currentColor" strokeWidth={0.15} className="text-dim/30" />
          ))}
          {/* ekvator */}
          <line x1={0} y1={Y(0)} x2={360} y2={Y(0)} stroke="currentColor" strokeWidth={0.3} className="text-zlato/30" />
          {active.map((c) => (
            <g
              key={c.hr}
              onClick={() => setCountry(country?.hr === c.hr ? null : c)}
              className="cursor-pointer"
            >
              <circle
                cx={X(c.lon)}
                cy={Y(c.lat)}
                r={markerSize * 0.62}
                fill={country?.hr === c.hr ? "rgba(200,160,60,0.45)" : "rgba(200,160,60,0.12)"}
                stroke={country?.hr === c.hr ? "#d4af37" : "rgba(200,160,60,0.5)"}
                strokeWidth={markerSize * 0.06}
              />
              <text
                x={X(c.lon)}
                y={Y(c.lat) + markerSize * 0.32}
                textAnchor="middle"
                fontSize={markerSize * 0.9}
                style={{ userSelect: "none" }}
              >
                {c.flag}
              </text>
            </g>
          ))}
        </svg>
      </div>

      {/* zemlje kao chipovi (i za one koji ne vole kartu) */}
      <div className="no-scrollbar mt-2 flex gap-1.5 overflow-x-auto">
        {active.map((c) => (
          <Chip key={c.hr} active={country?.hr === c.hr} onClick={() => setCountry(country?.hr === c.hr ? null : c)}>
            {c.flag} {lx({ hr: c.hr, en: c.en })} ({countryCounts.get(c.hr)})
          </Chip>
        ))}
      </div>

      {country && (
        <>
          <SectionTitle>
            {country.flag} {lx({ hr: country.hr, en: country.en })} · {countryCigars.length + countryDrinks.length}{" "}
            {t("club.products")}
          </SectionTitle>
          <div className="space-y-2">
            {countryCigars.map((c) => (
              <CigarRow key={c.id} cigar={c} onClick={() => setDetail({ kind: "cigar", item: c })} />
            ))}
            {countryDrinks.map((d) => (
              <DrinkRow key={d.id} drink={d} onClick={() => setDetail({ kind: "drink", item: d })} />
            ))}
          </div>
        </>
      )}

      <DetailSheet target={detail} onClose={() => setDetail(null)} />
    </div>
  );
}
