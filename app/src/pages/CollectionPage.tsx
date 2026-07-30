import { useRef, useState } from "react";
import type { Cigar, Drink } from "../types";
import {
  ALL_DRINKS,
  CIGARS,
  cigarForItemId,
  drinkById,
} from "../data";
import { useI18n, type StringKey } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { drinkNameLoc } from "../lib/drinkName";
import { DetailSheet } from "../components/DetailSheet";
import { EveningSessionSheet } from "../components/EveningSessionSheet";
import { cigarItemId } from "../lib/cigarItemId";
import {
  exportData,
  importData,
  removeJournalEntry,
  useCollection,
} from "../store/collection";
import { navigate, useRoute, type CollectionView } from "../store/route";
import { HumidorPage, JournalCalendar } from "./HumidorPage";
import { exportHumidors, importHumidors } from "../store/humidor";

export function CollectionPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx, lang } = useI18n();
  const route = useRoute();
  const data = useCollection();
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const [showAddPairing, setShowAddPairing] = useState(false);
  const [logCigar, setLogCigar] = useState<Cigar | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [importMsg, setImportMsg] = useState<string | null>(null);

  // "Imam" = stvarna kolekcija; ostalo (probano/ocjena/biljeska bez posjedovanja)
  // ide u zasebnu povijest i nestaje iz kolekcije kad se makne "Imam"
  const ownedIds = Object.entries(data.items)
    .filter(([, s]) => s.owned)
    .map(([id]) => id);
  // stavke s liste želja žive u Kupovina — ne dupliciraj ih u povijesti Kolekcije
  const historyIds = Object.entries(data.items)
    .filter(([, s]) => !s.owned && !s.wishlist && (s.tried || s.rating != null || s.note))
    .map(([id]) => id);

  // kljuc cigare moze nositi vitolu (`cig-x@churchill`) — razrijesi ga u liniju
  // s primijenjenom vitolom da red pokaze bas taj format
  const cigarsFor = (ids: string[]) =>
    ids
      .map((id) => ({ id, cigar: cigarForItemId(id) }))
      .filter((x): x is { id: string; cigar: Cigar } => x.cigar != null);

  const myCigars = cigarsFor(ownedIds);
  const myDrinks = ALL_DRINKS.filter((d) => ownedIds.includes(d.id));
  const historyCigars = cigarsFor(historyIds);
  const historyDrinks = ALL_DRINKS.filter((d) => historyIds.includes(d.id));

  // backup nosi i humidore — inače bi se zaliha izgubila pri prijenosu uređaja
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

  // Kolekcija / Humidor / Kalendar — sve što je "moje" na jednom mjestu
  const view = route.collection ?? "collection";
  const tabs: { id: CollectionView; key: StringKey }[] = [
    { id: "collection", key: "hum.tabCollection" },
    { id: "humidor", key: "hum.tabHumidor" },
    { id: "calendar", key: "hum.tabCalendar" },
  ];

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

  if (view === "humidor") {
    return (
      <div className="pb-4">
        {tabBar}
        <HumidorPage
          onOpenCigar={(cigar) => setDetail({ kind: "cigar", item: cigar })}
        />
        <DetailSheet
          target={detail}
          onClose={() => setDetail(null)}
          onPair={
            onPair
              ? (target) => {
                  setDetail(null);
                  onPair(target);
                }
              : undefined
          }
          onLogEvening={(cigar) => {
            setDetail(null);
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
      <div className="mt-4 flex items-center justify-between">
        <span className="text-sm text-dim">
          <span className="font-display text-lg text-zlato-2">{ownedIds.length}</span>{" "}
          {t("coll.stats")}
        </span>
        <div className="flex gap-2">
          <Chip onClick={doExport}>⭳ {t("coll.export")}</Chip>
          <Chip onClick={() => fileRef.current?.click()}>⭱ {t("coll.import")}</Chip>
          <input
            ref={fileRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && doImport(e.target.files[0])}
          />
        </div>
      </div>
      {importMsg && <p className="mt-2 text-xs text-zlato-2">{importMsg}</p>}

      {ownedIds.length === 0 && historyIds.length === 0 && (
        <p className="mt-6 rounded-xl border border-dim/20 bg-cedar p-4 text-sm leading-relaxed text-dim">
          {t("coll.empty")}
        </p>
      )}

      {myCigars.length > 0 && (
        <>
          <SectionTitle>{t("cat.cigars")}</SectionTitle>
          <div className="space-y-2">
            {myCigars.map(({ id, cigar }) => (
              <CigarRow
                key={id}
                cigar={cigar}
                onClick={() => setDetail({ kind: "cigar", item: cigar })}
              />
            ))}
          </div>
        </>
      )}

      {myDrinks.length > 0 && (
        <>
          <SectionTitle>{t("coll.drinks")}</SectionTitle>
          <div className="space-y-2">
            {myDrinks.map((d) => (
              <DrinkRow key={d.id} drink={d} onClick={() => setDetail({ kind: "drink", item: d })} />
            ))}
          </div>
        </>
      )}

      {/* probano/biljeske bez posjedovanja — ne racuna se u kolekciju */}
      {(historyCigars.length > 0 || historyDrinks.length > 0) && (
        <>
          <SectionTitle>{t("coll.historySection")}</SectionTitle>
          <div className="space-y-2 opacity-80">
            {historyCigars.map(({ id, cigar }) => (
              <CigarRow
                key={id}
                cigar={cigar}
                onClick={() => setDetail({ kind: "cigar", item: cigar })}
              />
            ))}
            {historyDrinks.map((d) => (
              <DrinkRow key={d.id} drink={d} onClick={() => setDetail({ kind: "drink", item: d })} />
            ))}
          </div>
        </>
      )}

      {/* dnevnik */}
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
            myCigars.length > 0 ? myCigars.map(({ cigar }) => cigar) : CIGARS
          }
          drinks={[]}
          initialCigarId={
            myCigars[0] ? cigarItemId(myCigars[0].cigar) : CIGARS[0]?.id
          }
          onClose={() => setShowAddPairing(false)}
        />
      )}
      <DetailSheet
        target={detail}
        onClose={() => setDetail(null)}
        onPair={
          onPair
            ? (target) => {
                setDetail(null);
                onPair(target);
              }
            : undefined
        }
        onLogEvening={(cigar) => {
          setDetail(null);
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
    </div>
  );
}
