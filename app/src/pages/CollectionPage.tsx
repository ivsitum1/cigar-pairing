import { useMemo, useRef, useState, type ReactNode } from "react";
import type { Cigar, Drink } from "../types";
import {
  ALL_DRINKS,
  CIGARS,
  brandDisplayName,
  cigarForItemId,
  drinkById,
} from "../data";
import { useI18n, type StringKey } from "../i18n";
import { Chip, SearchInput, SectionTitle } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { drinkNameLoc } from "../lib/drinkName";
import {
  CigarBrowseSheets,
  useCigarBrowseSheets,
} from "../components/useCigarBrowseSheets";
import { EveningSessionSheet } from "../components/EveningSessionSheet";
import {
  cigarItemId,
  dedupeCollectionCigarIds,
} from "../lib/cigarItemId";
import { buildCigarOcrCandidates } from "../lib/ocrCigarCandidates";
import {
  ownedWithoutStockIds,
  shortlistItemIds,
} from "../lib/collectionPanels";
import {
  smokerProfile,
  type SmokerProfile,
  type TriedCigar,
} from "../lib/smokerProfile";
import { cigarShapes } from "../lib/vitolaShape";
import { flavorLabel } from "../engine/rules";
import {
  clearItem,
  exportData,
  importData,
  removeJournalEntry,
  updateJournalEntry,
  useCollection,
} from "../store/collection";
import { navigate, useRoute, type CollectionView } from "../store/route";
import { HumidorPage, JournalCalendar } from "./HumidorPage";
import { exportHumidors, importHumidors, stockForItemKey } from "../store/humidor";
import { exportFavorites, importFavorites } from "../store/favorites";
import {
  exportTasteProfiles,
  importTasteProfiles,
  useTasteProfiles,
} from "../store/tasteProfile";
import { withTaste } from "../lib/tasteProfile";
import { TasteReportSheet } from "../components/TasteReportSheet";
import { OcrScan } from "../components/OcrScan";
import { OcrPackPanel } from "../components/OcrPackPanel";
import { useMarket } from "../store/market";
import { applyLocalDayToIso, localDayKey } from "../lib/calendar";

/**
 * Redak popisa Kolekcije + izlaz. Bez njega se stavka miče samo gašenjem svih
 * kvačica u kartici, a ako ključ ne odgovara onome što kartica piše (stara
 * vitola, oznaka na razini linije) ne miče se nikako.
 */
function CollectionEntry({
  itemId,
  children,
}: {
  itemId: string;
  children: ReactNode;
}) {
  const { t } = useI18n();
  return (
    <div className="flex items-start gap-2">
      <div className="min-w-0 flex-1">{children}</div>
      <button
        type="button"
        onClick={() => clearItem(itemId)}
        aria-label={t("coll.removeFromList")}
        title={t("coll.removeFromList")}
        className="mt-1 h-8 w-8 shrink-0 rounded-lg border border-dim/25 text-sm text-dim hover:border-oxblood/60 hover:text-oxblood"
      >
        ✕
      </button>
    </div>
  );
}

const STYLE_KEYS: Record<
  SmokerProfile["style"],
  { title: StringKey; body: StringKey }
> = {
  novice: { title: "score.styleNovice", body: "score.styleNoviceBody" },
  mild: { title: "score.styleMild", body: "score.styleMildBody" },
  balanced: { title: "score.styleBalanced", body: "score.styleBalancedBody" },
  full: { title: "score.styleFull", body: "score.styleFullBody" },
  strong: { title: "score.styleStrong", body: "score.styleStrongBody" },
};

/** Jedna brojka sa svojim natpisom. */
function ScoreStat({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-lg border border-dim/15 bg-humidor/50 px-2.5 py-2 text-center">
      <div className="font-display text-xl leading-none text-zlato-2">{value}</div>
      <div className="mt-1 text-micro leading-snug text-dim">{label}</div>
    </div>
  );
}

function ScoreFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-t border-dim/10 pt-1.5">
      <span className="shrink-0 text-micro uppercase tracking-widest text-dim">{label}</span>
      <span className="min-w-0 truncate text-sm text-papir/90">{value}</span>
    </div>
  );
}

/**
 * Zbroj probanog: koliko, kako ocijenjeno i kakav si pušač. Zamjenjuje popis
 * „Probano” — popis je rastao, a ništa nije govorio.
 */
function SmokerScoreboard({ profile }: { profile: SmokerProfile }) {
  const { t, lx, cn, lang } = useI18n();
  const market = useMarket();
  const style = STYLE_KEYS[profile.style];

  if (profile.tried === 0 && profile.evenings === 0) {
    return (
      <p className="rounded-xl border border-dim/20 bg-cedar p-4 text-sm leading-relaxed text-dim">
        {t("score.empty")}
      </p>
    );
  }

  const bestCigar = profile.best ? cigarForItemId(profile.best.itemId) : undefined;
  const bestDrink = profile.topDrink ? drinkById(profile.topDrink.value) : undefined;
  const oneDecimal = (v: number) => v.toFixed(1);

  return (
    <div className="rounded-xl border border-zlato/25 bg-cedar p-3">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <ScoreStat value={String(profile.tried)} label={t("score.tried")} />
        <ScoreStat value={String(profile.evenings)} label={t("score.evenings")} />
        <ScoreStat
          value={profile.avgRating != null ? oneDecimal(profile.avgRating) : "—"}
          label={`${t("score.avgRating")} (${profile.rated} ${t("score.rated")})`}
        />
        <ScoreStat value={String(profile.triedDrinks)} label={t("score.triedDrinks")} />
      </div>

      <div className="mt-3 rounded-lg border border-zlato/20 bg-zlato/5 px-3 py-2">
        <div className="text-micro uppercase tracking-widest text-dim">
          {t("score.style")}
        </div>
        <div className="font-display text-base text-zlato-2">{t(style.title)}</div>
        <p className="mt-0.5 text-xs leading-relaxed text-papir/85">{t(style.body)}</p>
      </div>

      <div className="mt-3 space-y-1.5">
        {profile.avgStrength != null && profile.avgBody != null && (
          <ScoreFact
            label={t("score.strengthBody")}
            value={`${oneDecimal(profile.avgStrength)} / ${oneDecimal(profile.avgBody)}`}
          />
        )}
        {profile.topShape && (
          <ScoreFact
            label={t("score.topShape")}
            value={`${t(`shape.${profile.topShape.value}` as StringKey)} · ${profile.topShape.count}×`}
          />
        )}
        {profile.topCountry && (
          <ScoreFact
            label={t("score.topCountry")}
            value={`${cn(profile.topCountry.value)} · ${profile.topCountry.count}×`}
          />
        )}
        {profile.topWrapper && (
          <ScoreFact
            label={t("score.topWrapper")}
            value={`${profile.topWrapper.value} · ${profile.topWrapper.count}×`}
          />
        )}
        {profile.topFlavors.length > 0 && (
          <ScoreFact
            label={t("score.topFlavors")}
            value={profile.topFlavors
              .map((f) => flavorLabel(f.value, lang))
              .join(" · ")}
          />
        )}
        {bestDrink && profile.topDrink && (
          <ScoreFact
            label={t("score.topDrink")}
            value={`${lx(drinkNameLoc(bestDrink))} · ${profile.topDrink.count}×`}
          />
        )}
        {profile.best && (
          <ScoreFact
            label={t("score.best")}
            value={`${
              bestCigar
                ? `${brandDisplayName(bestCigar.brand, market)} ${bestCigar.line}${
                    bestCigar.selectedVitola ? ` ${bestCigar.selectedVitola}` : ""
                  }`
                : profile.best.itemId
            } · ${profile.best.rating}/10`}
          />
        )}
      </div>
    </div>
  );
}

export function CollectionPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx, lang } = useI18n();
  const market = useMarket();
  const route = useRoute();
  const data = useCollection();
  const taste = useTasteProfiles();
  const {
    line,
    detail,
    openCigar,
    openCigarCard,
    openVitola,
    openDrink,
    openLine,
    closeLine,
    closeDetail,
    closeSheets,
  } = useCigarBrowseSheets();
  const [showAddPairing, setShowAddPairing] = useState(false);
  const [logCigar, setLogCigar] = useState<Cigar | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [importMsg, setImportMsg] = useState<string | null>(null);
  const [reportOpen, setReportOpen] = useState(false);
  // popis probanih postoji samo za ispravke — zbroj je ono što se gleda
  const [showHistory, setShowHistory] = useState(false);
  const [ocrQuery, setOcrQuery] = useState("");

  // Tab Kolekcija: Imam bez stocka + shortlist (tried); wishlist živi u Kupovini
  const ownedNoStockIds = dedupeCollectionCigarIds(
    ownedWithoutStockIds(data.items, stockForItemKey).filter(
      (id) => cigarForItemId(id) != null,
    ),
  );
  const historyIds = dedupeCollectionCigarIds(
    shortlistItemIds(data.items).filter((id) => cigarForItemId(id) != null),
  );
  const historyDrinkIds = shortlistItemIds(data.items).filter(
    (id) => cigarForItemId(id) == null && drinkById(id) != null,
  );

  /**
   * Profil pušača: zbroj svega probanog, a ne popis. Ulaze sve cigare koje su
   * označene s „Probano” ili nose ocjenu — bez obzira imaš li ih još.
   *
   * Snaga i tijelo idu kroz `withTaste`: profil se zove „moj”, pa se ne smije
   * računati iz katalogove procjene kad za tu liniju postoji tvoja ocjena.
   */
  const profile = useMemo(() => {
    const tried: TriedCigar[] = [];
    for (const [id, state] of Object.entries(data.items)) {
      if (!state.tried && state.rating == null) continue;
      const raw = cigarForItemId(id);
      if (!raw) continue;
      const cigar = withTaste(raw, taste);
      // linija s više formata ne zna koji je pušen — oblik tada ne ulazi u zbroj
      const shapes = cigarShapes(cigar);
      tried.push({
        itemId: id,
        strength: cigar.strength,
        body: cigar.body,
        country: cigar.country,
        wrapper: cigar.wrapper,
        flavorTags: cigar.flavorTags,
        shape: shapes.size === 1 ? [...shapes][0] : null,
        rating: state.rating,
      });
    }
    const triedDrinks = Object.entries(data.items).filter(
      ([id, s]) => (s.tried || s.rating != null) && drinkById(id) != null,
    ).length;
    return smokerProfile(tried, triedDrinks, data.journal);
  }, [data, taste]);

  const allOwnedCigarIds = Object.entries(data.items)
    .filter(([id, s]) => s.owned && cigarForItemId(id) != null)
    .map(([id]) => id);

  const cigarsFor = (ids: string[]) =>
    ids
      .map((id) => ({ id, cigar: cigarForItemId(id) }))
      .filter((x): x is { id: string; cigar: Cigar } => x.cigar != null);

  const ownedNoStockCigars = cigarsFor(ownedNoStockIds);
  const historyCigars = cigarsFor(historyIds);
  const historyDrinks = ALL_DRINKS.filter((d) => historyDrinkIds.includes(d.id));
  const ownedCigarsForLog = cigarsFor(
    dedupeCollectionCigarIds(allOwnedCigarIds),
  );

  const doExport = () => {
    const payload = JSON.stringify(
      {
        ...JSON.parse(exportData()),
        humidors: exportHumidors(),
        favoriteBrands: exportFavorites(),
        tasteProfiles: exportTasteProfiles(),
      },
      null,
      2,
    );
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cigar-pairing-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const doImport = async (file: File) => {
    const text = await file.text();
    const ok = importData(text);
    if (ok) {
      try {
        const parsed = JSON.parse(text) as {
          humidors?: unknown;
          favoriteBrands?: unknown;
          tasteProfiles?: unknown;
        };
        if (parsed.humidors !== undefined) importHumidors(parsed.humidors);
        // Stariji backup nema ključ — tada omiljene ostaju kakve jesu. Uvoz
        // praznog polja bi ih obrisao, a to nije ono što stara datoteka kaže.
        if (parsed.favoriteBrands !== undefined) importFavorites(parsed.favoriteBrands);
        if (parsed.tasteProfiles !== undefined) importTasteProfiles(parsed.tasteProfiles);
      } catch {
        // kolekcija je uvezena; humidori iz starijeg backupa jednostavno ne postoje
      }
    }
    setImportMsg(ok ? t("coll.importOk") : t("coll.importErr"));
    setTimeout(() => setImportMsg(null), 3000);
  };

  // Humidor | Kolekcija | Kalendar — zaliha prva, shortlist druga
  const view = route.collection ?? "humidor";
  const tabs: { id: CollectionView; key: StringKey }[] = [
    { id: "humidor", key: "hum.tabHumidor" },
    { id: "collection", key: "hum.tabCollection" },
    { id: "calendar", key: "hum.tabCalendar" },
  ];

  const ocrCandidates = buildCigarOcrCandidates(CIGARS, (b) =>
    brandDisplayName(b, market),
  );

  const tabBar = (
    <div className="mt-4 grid grid-cols-3 gap-1 rounded-xl border border-dim/20 bg-cedar/60 p-1">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => navigate({ page: "collection", collection: tab.id })}
          aria-current={view === tab.id ? "page" : undefined}
          className={`rounded-lg py-2 font-display text-xs uppercase tracking-widest transition-colors ${
            view === tab.id
              ? "bg-zlato/15 text-zlato-2"
              : "text-dim hover:text-papir"
          }`}
        >
          {t(tab.key)}
        </button>
      ))}
    </div>
  );

  const sheets = (
    <>
      {reportOpen && <TasteReportSheet onClose={() => setReportOpen(false)} />}
      <CigarBrowseSheets
        line={line}
        detail={detail}
        onCloseLine={closeLine}
        onOpenVitola={openVitola}
        onCloseDetail={closeDetail}
        onOpenLine={openLine}
        onPair={
          onPair
            ? (target) => {
                closeSheets();
                onPair(target);
              }
            : undefined
        }
        onLogEvening={(cigar) => {
          closeSheets();
          setLogCigar(cigar);
        }}
      />
      {logCigar && (
        <EveningSessionSheet
          cigars={[logCigar]}
          drinks={[]}
          initialCigarId={cigarItemId(logCigar)}
          onClose={() => setLogCigar(null)}
        />
      )}
    </>
  );

  if (view === "humidor") {
    return (
      <div className="pb-4">
        {tabBar}
        <HumidorPage
          onOpenCigar={(cigar) => openCigar(cigar)}
          onOpenDrink={(drink) => openDrink(drink)}
        />
        {sheets}
      </div>
    );
  }

  if (view === "calendar") {
    return (
      <div className="pb-4">
        {tabBar}
        <JournalCalendar />
      </div>
    );
  }

  return (
    <div className="pb-4">
      {tabBar}
      <div className="mt-4 flex items-center justify-between gap-2">
        <span className="text-sm text-dim">
          <span className="font-display text-lg text-zlato-2">
            {ownedNoStockCigars.length}
          </span>{" "}
          {t("coll.stats")}
        </span>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <OcrScan
            candidates={ocrCandidates}
            enableReceipt
            onConfirmCigar={(id, action) => {
              if (action === "dismiss") return;
              const cigar = cigarForItemId(id) ?? CIGARS.find((c) => c.id === id);
              if (!cigar) return;
              if (action === "pair" && onPair) {
                closeSheets();
                onPair({ kind: "cigar", item: cigar });
                return;
              }
              openCigar(cigar);
            }}
            onMatch={(id) => {
              const cigar = cigarForItemId(id) ?? CIGARS.find((c) => c.id === id);
              if (cigar) openCigar(cigar);
            }}
            onText={setOcrQuery}
          />
          <Chip onClick={() => setReportOpen(true)}>{t("report.open")}</Chip>
          <Chip onClick={doExport}>{t("coll.export")}</Chip>
          <Chip onClick={() => fileRef.current?.click()}>{t("coll.import")}</Chip>
          <input
            ref={fileRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && doImport(e.target.files[0])}
          />
        </div>
      </div>
      <OcrPackPanel />
      {ocrQuery ? (
        <div className="mt-2">
          <SearchInput value={ocrQuery} onChange={setOcrQuery} placeholder={t("pair.search")} />
        </div>
      ) : null}
      {importMsg && <p className="mt-2 text-xs text-zlato-2">{importMsg}</p>}

      {ownedNoStockCigars.length > 0 && (
        <>
          <SectionTitle>{t("coll.ownedNoStock")}</SectionTitle>
          <div className="space-y-2">
            {ownedNoStockCigars.map(({ id, cigar }) => (
              <CollectionEntry key={id} itemId={id}>
                {/* kartica baš tog ključa: što je ovdje označeno mora se i
                    odavde moći odznačiti */}
                <CigarRow cigar={cigar} onClick={() => openCigarCard(cigar)} />
              </CollectionEntry>
            ))}
          </div>
        </>
      )}

      <SectionTitle>{t("score.title")}</SectionTitle>
      <SmokerScoreboard profile={profile} />

      {(historyCigars.length > 0 || historyDrinks.length > 0) && (
        <>
          <div className="mt-2">
            <Chip onClick={() => setShowHistory((v) => !v)}>
              {showHistory ? t("score.hideList") : t("score.showList")} (
              {historyCigars.length + historyDrinks.length})
            </Chip>
          </div>
          {showHistory && (
            <>
              <p className="mt-2 text-xs leading-relaxed text-dim">{t("score.listHint")}</p>
              <div className="mt-2 space-y-2 opacity-80">
                {historyCigars.map(({ id, cigar }) => (
                  <CollectionEntry key={id} itemId={id}>
                    <CigarRow cigar={cigar} onClick={() => openCigarCard(cigar)} />
                  </CollectionEntry>
                ))}
                {historyDrinks.map((d) => (
                  <CollectionEntry key={d.id} itemId={d.id}>
                    <DrinkRow drink={d} onClick={() => openDrink(d)} />
                  </CollectionEntry>
                ))}
              </div>
            </>
          )}
        </>
      )}

      <SectionTitle>{t("coll.journal")}</SectionTitle>
      <button
        onClick={() => setShowAddPairing(true)}
        className="w-full rounded-lg border border-zlato/40 py-2.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
      >
        + {t("coll.addPairing")}
      </button>
      {data.journal.length === 0 && (
        <p className="mt-3 text-sm leading-relaxed text-dim">{t("coll.journalEmpty")}</p>
      )}
      <div className="mt-3 space-y-2">
        {data.journal.map((j) => {
          const cigar = cigarForItemId(j.cigarId);
          const drink = drinkById(j.drinkId);
          const dayValue = localDayKey(new Date(j.date));
          return (
            <div key={j.id} className="rounded-xl border border-dim/15 bg-cedar p-3">
              <div className="flex items-baseline justify-between gap-2">
                <span className="font-display text-sm text-papir">
                  {cigar
                    ? `${cigar.brand} ${cigar.line}${
                        cigar.selectedVitola ? ` ${cigar.selectedVitola}` : ""
                      }`
                    : j.cigarId}
                  <span className="text-zlato"> × </span>
                  {drink
                    ? lx(drinkNameLoc(drink))
                    : j.drinkId == null
                      ? t("session.soloLabel")
                      : j.drinkId}
                </span>
                {j.rating != null ? (
                  <span className="shrink-0 text-sm text-zlato-2">{j.rating}/10</span>
                ) : (
                  <label className="shrink-0 inline-flex items-center gap-2 text-xs text-dim">
                    <span>{t("coll.eveningRating")}</span>
                    <select
                      value=""
                      onChange={(e) =>
                        updateJournalEntry(j.id, {
                          rating: e.target.value ? Number(e.target.value) : null,
                        })
                      }
                      className="rounded-md border border-dim/30 bg-cedar px-2 py-1 text-sm text-papir focus:border-zlato/60 [color-scheme:dark]"
                      aria-label={t("coll.eveningRating")}
                    >
                      <option value="" disabled>
                        —
                      </option>
                      {Array.from({ length: 10 }, (_, i) => 10 - i).map((v) => (
                        <option key={v} value={v}>
                          {v}/10
                        </option>
                      ))}
                    </select>
                  </label>
                )}
              </div>
              <div className="mt-1 text-xs text-dim">
                {new Date(j.date).toLocaleDateString(lang === "hr" ? "hr-HR" : "en-GB")}
                {j.note && ` — ${j.note}`}
              </div>
              {j.rating == null && (
                <p className="mt-1 text-[11px] leading-relaxed text-dim/80">
                  {t("coll.eveningRatingHint")}
                </p>
              )}
              <label className="mt-2 flex items-center gap-2 text-xs text-dim">
                <span className="shrink-0">{t("hum.editDate")}</span>
                <input
                  type="date"
                  value={dayValue}
                  aria-label={t("hum.editDate")}
                  onChange={(e) => {
                    const nextKey = e.target.value;
                    if (!nextKey || nextKey === dayValue) return;
                    const nextIso = applyLocalDayToIso(j.date, nextKey);
                    if (!nextIso) return;
                    updateJournalEntry(j.id, { date: nextIso });
                  }}
                  className="min-w-0 flex-1 rounded-md border border-dim/30 bg-ink/40 px-2 py-1 text-papir [color-scheme:dark]"
                />
              </label>
              <button
                onClick={() => removeJournalEntry(j.id)}
                className="mt-2 text-xs text-oxblood/80 hover:text-oxblood"
              >
                {t("coll.delete")}
              </button>
            </div>
          );
        })}
      </div>

      {showAddPairing && (
        <EveningSessionSheet
          cigars={
            ownedCigarsForLog.length > 0
              ? ownedCigarsForLog.map(({ cigar }) => cigar)
              : CIGARS
          }
          drinks={[]}
          initialCigarId={
            ownedCigarsForLog[0]
              ? cigarItemId(ownedCigarsForLog[0].cigar)
              : CIGARS[0]?.id
          }
          onClose={() => setShowAddPairing(false)}
        />
      )}
      {sheets}
    </div>
  );
}
