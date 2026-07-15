import { useState } from "react";
import { useI18n } from "./i18n";
import { PairingPage } from "./pages/PairingPage";
import { CatalogPage } from "./pages/CatalogPage";
import { CollectionPage } from "./pages/CollectionPage";
import { ShoppingPage } from "./pages/ShoppingPage";
import { ClubPage } from "./pages/ClubPage";
import { requestPairing } from "./store/pairingNav";
import type { Cigar, Drink } from "./types";

type Page = "pairing" | "catalog" | "collection" | "shopping" | "club";

const NAV: { id: Page; icon: string; key: "nav.pairing" | "nav.catalog" | "nav.collection" | "nav.shopping" | "nav.club" }[] = [
  { id: "pairing", icon: "◈", key: "nav.pairing" },
  { id: "catalog", icon: "☰", key: "nav.catalog" },
  { id: "collection", icon: "✓", key: "nav.collection" },
  { id: "shopping", icon: "€", key: "nav.shopping" },
  { id: "club", icon: "✦", key: "nav.club" },
];

export default function App() {
  const { t, lang, setLang } = useI18n();
  const [page, setPage] = useState<Page>("pairing");

  const goToPairing = (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => {
    requestPairing(
      target.kind === "cigar"
        ? { mode: "cigarToDrink", cigar: target.item }
        : { mode: "drinkToCigar", drink: target.item },
    );
    setPage("pairing");
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col px-4">
      {/* header — cigar band stil */}
      <header className="flex items-center justify-between pb-2 pt-5">
        <div>
          <div className="font-display text-lg uppercase tracking-[0.25em] text-zlato-2">
            Cigar <span className="text-oxblood">&</span> Pairing
          </div>
          <div className="band-rule mt-1.5" />
        </div>
        <button
          onClick={() => setLang(lang === "hr" ? "en" : "hr")}
          className="rounded-full border border-zlato/40 px-3 py-1.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
          aria-label="Language"
        >
          {lang === "hr" ? "EN" : "HR"}
        </button>
      </header>

      <main className="flex-1 pb-24">
        {page === "pairing" && <PairingPage />}
        {page === "catalog" && <CatalogPage onPair={goToPairing} />}
        {page === "collection" && <CollectionPage />}
        {page === "shopping" && <ShoppingPage />}
        {page === "club" && <ClubPage />}
      </main>

      {/* donja navigacija */}
      <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-zlato/20 bg-humidor/95 backdrop-blur">
        <div className="mx-auto grid max-w-2xl grid-cols-5">
          {NAV.map((n) => (
            <button
              key={n.id}
              onClick={() => setPage(n.id)}
              className={`flex flex-col items-center gap-0.5 py-2.5 pb-[max(0.625rem,env(safe-area-inset-bottom))] text-[11px] transition-colors ${
                page === n.id ? "text-zlato-2" : "text-dim hover:text-papir"
              }`}
              aria-current={page === n.id ? "page" : undefined}
            >
              <span className="text-base leading-none">{n.icon}</span>
              <span className="font-display uppercase tracking-wider">{t(n.key)}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}
