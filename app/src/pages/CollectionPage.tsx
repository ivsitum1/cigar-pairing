import { useRef, useState } from "react";
import type { Cigar, Drink } from "../types";
import { ALL_DRINKS, CIGARS, cigarById, drinkById } from "../data";
import { useI18n } from "../i18n";
import { Chip, SectionTitle } from "../components/ui";
import { CigarRow, DrinkRow } from "../components/cards";
import { DetailSheet } from "../components/DetailSheet";
import { BackButton } from "../components/BackButton";
import {
  addJournalEntry,
  exportData,
  importData,
  removeJournalEntry,
  useCollection,
} from "../store/collection";

export function CollectionPage() {
  const { t, lang } = useI18n();
  const data = useCollection();
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const [showAddPairing, setShowAddPairing] = useState(false);
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

  const myCigars = CIGARS.filter((c) => ownedIds.includes(c.id));
  const myDrinks = ALL_DRINKS.filter((d) => ownedIds.includes(d.id));
  const historyCigars = CIGARS.filter((c) => historyIds.includes(c.id));
  const historyDrinks = ALL_DRINKS.filter((d) => historyIds.includes(d.id));

  const doExport = () => {
    const blob = new Blob([exportData()], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cigar-pairing-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const doImport = async (file: File) => {
    const ok = importData(await file.text());
    setImportMsg(ok ? t("coll.importOk") : t("coll.importErr"));
    setTimeout(() => setImportMsg(null), 3000);
  };

  return (
    <div className="pb-4">
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
            {myCigars.map((c) => (
              <CigarRow key={c.id} cigar={c} onClick={() => setDetail({ kind: "cigar", item: c })} />
            ))}
          </div>
        </>
      )}

      {myDrinks.length > 0 && (
        <>
          <SectionTitle>
            {t("cat.rum")} / {t("cat.whisky")} / {t("cat.brandy")} / {t("cat.wine")} /{" "}
            {t("cat.coffee")} / {t("cat.tequila")} / {t("cat.gin")}
          </SectionTitle>
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
            {historyCigars.map((c) => (
              <CigarRow key={c.id} cigar={c} onClick={() => setDetail({ kind: "cigar", item: c })} />
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
          const cigar = cigarById(j.cigarId);
          const drink = drinkById(j.drinkId);
          return (
            <div key={j.id} className="rounded-xl border border-dim/15 bg-cedar p-3">
              <div className="flex items-baseline justify-between gap-2">
                <span className="font-display text-sm text-papir">
                  {cigar ? `${cigar.brand} ${cigar.line}` : j.cigarId}
                  <span className="text-zlato"> × </span>
                  {drink ? drink.name : j.drinkId}
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

      {showAddPairing && <AddPairingSheet onClose={() => setShowAddPairing(false)} />}
      <DetailSheet target={detail} onClose={() => setDetail(null)} />
    </div>
  );
}

function AddPairingSheet({ onClose }: { onClose: () => void }) {
  const { t } = useI18n();
  const [cigarId, setCigarId] = useState(CIGARS[0]?.id ?? "");
  const [drinkId, setDrinkId] = useState(ALL_DRINKS[0]?.id ?? "");
  const [rating, setRating] = useState<string>("");
  const [note, setNote] = useState("");

  const save = () => {
    addJournalEntry({
      cigarId,
      drinkId,
      rating: rating ? Number(rating) : null,
      note,
    });
    onClose();
  };

  const selectCls =
    "w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2.5 text-sm text-papir focus:border-zlato/60 focus:outline-none";

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center" onClick={onClose}>
      <div
        className="w-full max-w-lg rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3">
          <BackButton onClick={onClose}>{t("common.back")}</BackButton>
        </div>
        <h3 className="font-display text-lg text-papir">{t("coll.addPairing")}</h3>
        <div className="mt-4 space-y-3">
          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("common.cigar")}
            <select value={cigarId} onChange={(e) => setCigarId(e.target.value)} className={`mt-1 ${selectCls}`}>
              {CIGARS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.brand} {c.line}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("common.drink")}
            <select value={drinkId} onChange={(e) => setDrinkId(e.target.value)} className={`mt-1 ${selectCls}`}>
              {ALL_DRINKS.filter((d) => d.pairable).map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs uppercase tracking-widest text-dim">
            {t("coll.myRating")}
            <select value={rating} onChange={(e) => setRating(e.target.value)} className={`mt-1 ${selectCls}`}>
              <option value="">—</option>
              {Array.from({ length: 10 }, (_, i) => 10 - i).map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={t("coll.notePlaceholder")}
            rows={2}
            className={selectCls}
          />
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2">
          <button
            onClick={onClose}
            className="rounded-lg border border-dim/30 py-2.5 font-display text-xs uppercase tracking-widest text-dim"
          >
            {t("common.close")}
          </button>
          <button
            onClick={save}
            className="rounded-lg border border-zlato bg-zlato/15 py-2.5 font-display text-xs uppercase tracking-widest text-zlato-2"
          >
            {t("coll.save")}
          </button>
        </div>
      </div>
    </div>
  );
}
