import { useRef, useState } from "react";
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
  vitolaKeySlug,
} from "../lib/cigarItemId";
import { uniqueVitolas } from "../lib/cigarVitola";
import {
  ownedWithoutStockIds,
  shortlistItemIds,
} from "../lib/collectionPanels";
import {
  exportData,
  importData,
  removeJournalEntry,
  useCollection,
} from "../store/collection";
import { navigate, useRoute, type CollectionView } from "../store/route";
import { HumidorPage, JournalCalendar } from "./HumidorPage";
import { exportHumidors, importHumidors, totalStock } from "../store/humidor";
import { OcrScan } from "../components/OcrScan";
import { useMarket } from "../store/market";

export function CollectionPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx, lang } = useI18n();
  const market = useMarket();
  const route = useRoute();
  const data = useCollection();
  const {
    line,
    detail,
    openCigar,
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
  const [ocrQuery, setOcrQuery] = useState("");

  // Tab Kolekcija: Imam bez stocka + shortlist (tried); wishlist živi u Kupovini
  const ownedNoStockIds = dedupeCollectionCigarIds(
    ownedWithoutStockIds(data.items, totalStock).filter(
      (id) => cigarForItemId(id) != null,
    ),
  );
  const historyIds = dedupeCollectionCigarIds(
    shortlistItemIds(data.items).filter((id) => cigarForItemId(id) != null),
  );
  const historyDrinkIds = shortlistItemIds(data.items).filter(
    (id) => cigarForItemId(id) == null && drinkById(id) != null,
  );

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

  const panelCount =
    ownedNoStockCigars.length + historyCigars.length + historyDrinks.length;

  const doExport = () => {
    const payload = JSON.stringify(
      { ...JSON.parse(exportData()), humidors: exportHumidors() },
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
        const parsed = JSON.parse(text) as { humidors?: unknown };
        if (parsed.humidors !== undefined) importHumidors(parsed.humidors);
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

  const ocrCandidates = CIGARS.flatMap((c) => {
    const brand = brandDisplayName(c.brand, market);
    const base = {
      id: c.id,
      label: `${brand} ${c.line}`,
      brand: c.brand,
    };
    const vitolas = uniqueVitolas(c);
    if (vitolas.length <= 1) return [base];
    return [
      base,
      ...vitolas.map((v) => ({
        id: `${c.id}@${vitolaKeySlug(v.name)}`,
        label: `${brand} ${c.line} ${v.name}`,
        brand: c.brand,
      })),
    ];
  });

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
          <span className="font-display text-lg text-zlato-2">{panelCount}</span>{" "}
          {t("coll.stats")}
        </span>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <OcrScan
            candidates={ocrCandidates}
            onMatch={(id) => {
              const cigar = cigarForItemId(id) ?? CIGARS.find((c) => c.id === id);
              if (cigar) openCigar(cigar);
            }}
            onText={setOcrQuery}
          />
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
      {ocrQuery ? (
        <div className="mt-2">
          <SearchInput value={ocrQuery} onChange={setOcrQuery} placeholder={t("pair.search")} />
        </div>
      ) : null}
      {importMsg && <p className="mt-2 text-xs text-zlato-2">{importMsg}</p>}

      {panelCount === 0 && (
        <p className="mt-6 rounded-xl border border-dim/20 bg-cedar p-4 text-sm leading-relaxed text-dim">
          {t("coll.empty")}
        </p>
      )}

      {ownedNoStockCigars.length > 0 && (
        <>
          <SectionTitle>{t("coll.ownedNoStock")}</SectionTitle>
          <div className="space-y-2">
            {ownedNoStockCigars.map(({ id, cigar }) => (
              <CigarRow
                key={id}
                cigar={cigar}
                onClick={() => openCigar(cigar)}
              />
            ))}
          </div>
        </>
      )}

      {(historyCigars.length > 0 || historyDrinks.length > 0) && (
        <>
          <SectionTitle>{t("coll.historySection")}</SectionTitle>
          <div className="space-y-2 opacity-80">
            {historyCigars.map(({ id, cigar }) => (
              <CigarRow
                key={id}
                cigar={cigar}
                onClick={() => openCigar(cigar)}
              />
            ))}
            {historyDrinks.map((d) => (
              <DrinkRow key={d.id} drink={d} onClick={() => openDrink(d)} />
            ))}
          </div>
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
                {j.rating != null && (
                  <span className="shrink-0 text-sm text-zlato-2">{j.rating}/10</span>
                )}
              </div>
              <div className="mt-1 text-xs text-dim">
                {new Date(j.date).toLocaleDateString(lang === "hr" ? "hr-HR" : "en-GB")}
                {j.note && ` — ${j.note}`}
              </div>
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
