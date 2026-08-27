import { useEffect, useMemo, useRef, useState } from "react";
import type {
  Cigar,
  CoffeeRoastLevel,
  CoffeeSpecies,
  Drink,
  DrinkCategory,
  Vitola,
} from "../types";
import {
  CIGARS,
  DRINKS,
  ALL_BRANDS,
  BRAND_CATALOG,
  DRINK_BRAND_CATALOG,
  brandDisplayName,
  brandFromSlug,
  brandSearchHaystack,
  brandSlug,
  cigarsByBrand,
  cigarInRegion,
  cigarCountByRegion,
  drinkBrand,
  drinkBrandFromSlug,
  drinkBrandSlug,
  resolveCigarId,
  vitolaSlug,
} from "../data";
import { SHOPS, REGIONS } from "../data/shops";
import { useI18n, STYLE_LABELS, type StringKey } from "../i18n";
import { Chip, SearchInput } from "../components/ui";
import { LessonBody } from "../components/LessonBody";
import { CigarRow, DrinkRow } from "../components/cards";
import { DetailSheet } from "../components/DetailSheet";
import { EveningSessionSheet } from "../components/EveningSessionSheet";
import { BrandSheet } from "../components/BrandSheet";
import { DrinkBrandSheet } from "../components/DrinkBrandSheet";
import { FavoriteStar } from "../components/FavoriteStar";
import { LineSheet } from "../components/LineSheet";
import { MarketFilter } from "../components/MarketFilter";
import { VitolaPicker } from "../components/VitolaPicker";
import { applyVitola, uniqueVitolas } from "../lib/cigarVitola";
import { cigarLinePrice } from "../lib/cigarPrice";
import { cigarItemId } from "../lib/cigarItemId";
import {
  cycleSort,
  directedComparator,
  sortArrow,
  type SortDir,
  type SortState,
} from "../lib/sortToggle";
import {
  SHAPE_FAMILIES,
  firstVitolaOfShapeInRegion,
  type ShapeFamily,
} from "../lib/vitolaShape";
import {
  SCOTCH_REGIONS,
  SCOTLAND,
  scotchRegionCard,
  scotchRegionOf,
  whiskyStyleNote,
  type ScotchRegion,
} from "../lib/scotchRegion";
import {
  matchesAnySearch,
  matchesAnyToken,
  matchesSearch,
  searchTokens,
} from "../lib/searchMatch";
import { useMarket, setMarket } from "../store/market";
import { navigate, useRoute } from "../store/route";
import { favoriteKey, useFavoriteBrands } from "../store/favorites";

const norm = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();

// Prvi znak imena kao slovo indeksa (A–Z); sve ostalo (brojevi, simboli) → "#".
const letterFor = (s: string) => {
  const c = norm(s).charAt(0);
  return c >= "a" && c <= "z" ? c.toUpperCase() : "#";
};

const RAIL = ["#", ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")];

type SortKey = "quality" | "price" | "body" | "sweetness" | "strength" | "name";

// Smjer prvog klika: cijena i naziv rastu (jeftinije/A prvo), ocjene padaju
// (najbolje/najjače prvo). Drugi klik okreće, treći gasi — vidi lib/sortToggle.
const SORT_DEFAULT_DIR: Record<SortKey, SortDir> = {
  quality: "desc",
  price: "asc",
  body: "desc",
  sweetness: "desc",
  strength: "desc",
  name: "asc",
};

const CIGAR_SORTS: SortKey[] = ["name", "price", "body", "strength"];
const DRINK_SORTS: SortKey[] = ["quality", "price", "body", "sweetness"];

type CatalogSearchHit =
  | { kind: "brand"; brand: string }
  | { kind: "line"; cigar: Cigar }
  | { kind: "vitola"; cigar: Cigar; vitola: Vitola };

// Bočna A–Z traka za brzo skakanje po brendovima (tipa iOS kontakti):
// klik na slovo skoči na prvi brend s tim početnim slovom.
function AlphabetRail({
  letters,
  onJump,
}: {
  letters: Set<string>;
  onJump: (l: string) => void;
}) {
  return (
    <div className="fixed right-0 top-1/2 z-30 -translate-y-1/2 select-none">
      <div className="flex flex-col items-center rounded-l-lg border-y border-l border-zlato/20 bg-humidor/85 px-1 py-1.5 backdrop-blur">
        {RAIL.map((l) => {
          const has = letters.has(l);
          return (
            <button
              key={l}
              disabled={!has}
              onClick={() => onJump(l)}
              aria-label={`Skoči na ${l}`}
              className={`flex h-[15px] w-4 items-center justify-center font-display text-[9px] leading-none ${
                has ? "text-zlato active:text-zlato-2" : "text-dim/25"
              }`}
            >
              {l}
            </button>
          );
        })}
      </div>
    </div>
  );
}

type Tab = "cigars" | DrinkCategory;
const TABS: Tab[] = [
  "cigars",
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
  "digestif",
];
export function CatalogPage({
  onPair,
}: {
  onPair?: (target: { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink }) => void;
}) {
  const { t, lx, cn } = useI18n();
  const route = useRoute();
  const [tab, setTab] = useState<Tab>("cigars");
  const [query, setQuery] = useState("");
  const [styleFilter, setStyleFilter] = useState<string | null>(null);
  const [strengthFilter, setStrengthFilter] = useState<number | null>(null);
  const [shapeFilter, setShapeFilter] = useState<ShapeFamily | null>(null);
  // kava: tri okomite osi — priprema (styleFilter), prženje, zrno + zemlja
  const [roastFilter, setRoastFilter] = useState<CoffeeRoastLevel | null>(null);
  const [beanFilter, setBeanFilter] = useState<CoffeeSpecies | null>(null);
  const [originFilter, setOriginFilter] = useState<string | null>(null);
  // whisky: škotska regija je podfilter zemlje — ima smisla tek kad je izabrana Škotska
  const [scotchFilter, setScotchFilter] = useState<ScotchRegion | null>(null);
  const [wrapperOriginFilter, setWrapperOriginFilter] = useState<string | null>(null);
  const [binderOriginFilter, setBinderOriginFilter] = useState<string | null>(null);
  const [fillerOriginFilter, setFillerOriginFilter] = useState<string | null>(null);
  const [puroOnly, setPuroOnly] = useState(false);
  const [cleanOnly, setCleanOnly] = useState(false);
  // cigare se otvaraju na indeksu brendova; puni popis linija je iza "Brendovi" gumba
  const [browseBrands, setBrowseBrands] = useState(true);
  // „samo omiljene marke" — vrijedi i za indeks marki i za ravan popis
  const [favOnly, setFavOnly] = useState(false);
  const [limit, setLimit] = useState(120);
  const [showShops, setShowShops] = useState(false);
  // null = bez ručnog sortiranja (zadani poredak kartice: cigare po nazivu,
  // pića po kvaliteti). Chip ciklira zadani smjer → obrnuti → isključeno.
  const [sort, setSort] = useState<SortState<SortKey> | null>(null);
  const market = useMarket();
  const [detail, setDetail] = useState<
    { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink } | null
  >(null);
  const [logCigar, setLogCigar] = useState<Cigar | null>(null);
  const [pendingCigar, setPendingCigar] = useState<Cigar | null>(null);
  const [brand, setBrand] = useState<string | null>(null);
  const [line, setLine] = useState<Cigar | null>(null);
  const [dBrand, setDBrand] = useState<string | null>(null);
  const [drinkBrandBack, setDrinkBrandBack] = useState<string | null>(null);
  const favorites = useFavoriteBrands();
  const prevCatalogFocus = useRef(route.catalog);

  const openBrand = (b: string) => {
    setDetail(null);
    setLine(null);
    setPendingCigar(null);
    setDBrand(null);
    setBrand(b);
    navigate({ page: "catalog", catalog: { level: "brand", brandSlug: brandSlug(b) } });
  };

  const openDrinkBrand = (b: string) => {
    setDetail(null);
    setLine(null);
    setPendingCigar(null);
    setBrand(null);
    setDBrand(b);
    navigate({
      page: "catalog",
      catalog: { level: "drinkBrand", brandSlug: drinkBrandSlug(b) },
    });
  };

  // Boca otvorena iz marke: zatvaranje detalja vraća u usporedbu marke, a ne
  // na popis kategorije — inače se korisnik nakon svake boce mora vraćati ručno.
  const openDrinkFromBrand = (d: Drink) => {
    setDrinkBrandBack(dBrand);
    setDBrand(null);
    setDetail({ kind: "drink", item: d });
  };

  const openDrinkFromList = (d: Drink) => {
    setDrinkBrandBack(null);
    setDetail({ kind: "drink", item: d });
  };

  const openLine = (c: Cigar) => {
    const full = resolveCigarId(c.id) ?? c;
    setDetail(null);
    setPendingCigar(null);
    setBrand(null);
    setLine(full);
    navigate({ page: "catalog", catalog: { level: "line", cigarId: full.id } });
  };

  const openVitola = (c: Cigar, v: Vitola) => {
    const full = resolveCigarId(c.id) ?? c;
    setBrand(null);
    setLine(null);
    setPendingCigar(null);
    setDetail({ kind: "cigar", item: applyVitola(full, v) });
    navigate({
      page: "catalog",
      catalog: { level: "vitola", cigarId: full.id, vitolaSlug: vitolaSlug(v) },
    });
  };

  const clearCatalogFocus = () => {
    setBrand(null);
    setLine(null);
    setDetail(null);
    setPendingCigar(null);
    setDBrand(null);
    setDrinkBrandBack(null);
    navigate({ page: "catalog" });
  };

  const closeDetail = () => {
    if (drinkBrandBack) {
      const back = drinkBrandBack;
      setDrinkBrandBack(null);
      openDrinkBrand(back);
      return;
    }
    clearCatalogFocus();
  };

  // Sync sheets from deep-link hash
  useEffect(() => {
    if (route.page !== "catalog") {
      prevCatalogFocus.current = undefined;
      return;
    }
    const focus = route.catalog;
    if (!focus) {
      if (prevCatalogFocus.current) {
        setBrand(null);
        setLine(null);
        setDetail(null);
        setPendingCigar(null);
        setDBrand(null);
        setDrinkBrandBack(null);
      }
      prevCatalogFocus.current = focus;
      return;
    }
    prevCatalogFocus.current = focus;
    if (focus.level === "brand") {
      const b = brandFromSlug(focus.brandSlug);
      if (b) {
        setLine(null);
        setDetail(null);
        setPendingCigar(null);
        setDBrand(null);
        setBrand(b);
      }
      return;
    }
    if (focus.level === "drinkBrand") {
      const b = drinkBrandFromSlug(focus.brandSlug);
      if (b) {
        setLine(null);
        setDetail(null);
        setPendingCigar(null);
        setBrand(null);
        setDBrand(b);
      }
      return;
    }
    const cigar = resolveCigarId(focus.cigarId);
    if (!cigar) return;
    if (focus.level === "line") {
      setBrand(null);
      setDetail(null);
      setPendingCigar(null);
      setLine(cigar);
      return;
    }
    const v = uniqueVitolas(cigar).find((x) => vitolaSlug(x) === focus.vitolaSlug);
    if (!v) return;
    setBrand(null);
    setLine(null);
    setPendingCigar(null);
    setDetail({ kind: "cigar", item: applyVitola(cigar, v) });
  }, [route.page, route.catalog]);

  // Trostruki search hitovi (brand / line / vitola) kad je upit ≥ 2 znaka
  const searchHits = useMemo((): CatalogSearchHit[] => {
    const nq = query.trim();
    const tokens = searchTokens(nq);
    if (tab !== "cigars" || tokens.join("").length < 2) return [];
    const hits: CatalogSearchHit[] = [];
    const seenBrand = new Set<string>();
    const seenLine = new Set<string>();
    const seenVitola = new Set<string>();

    for (const b of ALL_BRANDS) {
      if (!matchesSearch(brandSearchHaystack(b), nq) || seenBrand.has(b)) continue;
      seenBrand.add(b);
      hits.push({ kind: "brand", brand: b });
      if (hits.length >= 8) break;
    }

    for (const c of CIGARS) {
      if (!cigarInRegion(c, market)) continue;
      const display = brandDisplayName(c.brand, market);
      const lineHit = matchesAnySearch(
        [
          c.line,
          `${c.brand} ${c.line}`,
          `${display} ${c.line}`,
          brandSearchHaystack(c.brand),
        ],
        nq,
      );
      if (lineHit && !seenLine.has(c.id)) {
        seenLine.add(c.id);
        hits.push({ kind: "line", cigar: c });
      }
      for (const v of c.vitolas ?? []) {
        // vitola se traži zajedno s linijom: „classic tempo" pogađa Tempo
        // unutar linije Classic, a ne traži obje riječi u imenu vitole
        if (!matchesAnySearch([v.name, `${c.brand} ${c.line} ${v.name}`], nq)) continue;
        const key = `${c.id}::${v.name}`;
        if (seenVitola.has(key)) continue;
        seenVitola.add(key);
        hits.push({ kind: "vitola", cigar: c, vitola: v });
        // vitola pogodak → ponudi i liniju i brand kao zasebne rezultate
        if (!seenLine.has(c.id)) {
          seenLine.add(c.id);
          hits.push({ kind: "line", cigar: c });
        }
        if (!seenBrand.has(c.brand)) {
          seenBrand.add(c.brand);
          hits.push({ kind: "brand", brand: c.brand });
        }
      }
      if (hits.length >= 24) break;
    }
    return hits.slice(0, 18);
  }, [tab, query, market]);

  const matchedBrands = useMemo(() => {
    const nq = query.trim();
    if (tab !== "cigars" || searchTokens(nq).join("").length < 2 || browseBrands) return [];
    return ALL_BRANDS.filter((b) => matchesAnyToken(brandSearchHaystack(b), nq)).slice(0, 4);
  }, [tab, query, browseBrands]);

  const brandRows = useMemo(() => {
    if (tab !== "cigars" || !browseBrands) return [];
    const nq = norm(query.trim());
    const rows = BRAND_CATALOG.filter((b) => {
      // kazalo marki traži marku, a ne cijeli naziv s kutije — dovoljna je
      // jedna riječ upita, inače „Oliva Serie O Toro" daje prazno kazalo
      if (
        nq &&
        !matchesAnyToken(brandSearchHaystack(b.brand), nq) &&
        !matchesAnyToken(b.info?.country ?? "", nq)
      ) {
        return false;
      }
      if (market !== "ALL" && !cigarsByBrand(b.brand).some((c) => cigarInRegion(c, market))) {
        return false;
      }
      if (favOnly && !favorites.has(favoriteKey("cigar", b.brand))) return false;
      return true;
    });
    return [...rows].sort((a, b) =>
      brandDisplayName(a.brand, market).localeCompare(brandDisplayName(b.brand, market)),
    );
  }, [tab, browseBrands, query, market, favOnly, favorites]);

  // Marke pića postoje samo unutar kategorije koja je otvorena — kuće s više
  // kategorija (Nikka: whisky + gin) tako se pojave u obje kartice, a u pogledu
  // marke se i dalje vide sve njihove boce.
  const drinkBrandRows = useMemo(() => {
    if (tab === "cigars" || !browseBrands) return [];
    const nq = norm(query.trim());
    return DRINK_BRAND_CATALOG.filter(
      (b) =>
        b.categories.includes(tab) &&
        (!nq || matchesAnyToken(b.brand, nq)) &&
        (!favOnly || favorites.has(favoriteKey("drink", b.brand))),
    );
  }, [tab, browseBrands, query, favOnly, favorites]);

  const drinkBrandAnchors = useMemo(() => {
    const at = new Map<number, string>();
    const letters = new Set<string>();
    let prev = "";
    drinkBrandRows.forEach((b, i) => {
      const L = letterFor(b.brand);
      letters.add(L);
      if (L !== prev) {
        at.set(i, L);
        prev = L;
      }
    });
    return { at, letters };
  }, [drinkBrandRows]);

  const brandAnchors = useMemo(() => {
    const at = new Map<number, string>();
    const letters = new Set<string>();
    let prev = "";
    brandRows.forEach((b, i) => {
      const L = letterFor(brandDisplayName(b.brand, market));
      letters.add(L);
      if (L !== prev) {
        at.set(i, L);
        prev = L;
      }
    });
    return { at, letters };
  }, [brandRows, market]);

  const jumpToLetter = (l: string) => {
    document
      .getElementById(`ci-alpha-${l}`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  /** Flat-list open: shape filter → that vitola in market; else LineSheet. */
  const openFromFlatList = (raw: Cigar) => {
    const cigar = resolveCigarId(raw.id) ?? raw;
    if (shapeFilter) {
      const match = firstVitolaOfShapeInRegion(cigar, shapeFilter, market);
      if (match) {
        openVitola(cigar, match);
        return;
      }
    }
    openLine(cigar);
  };

  const switchTab = (next: Tab) => {
    setTab(next);
    setStyleFilter(null);
    setStrengthFilter(null);
    setShapeFilter(null);
    setWrapperOriginFilter(null);
    setBinderOriginFilter(null);
    setFillerOriginFilter(null);
    setPuroOnly(false);
    setCleanOnly(false);
    setBrowseBrands(next === "cigars");
    // omiljene su po vrsti; nošenje filtra u karticu bez ijedne omiljene marke
    // izgleda kao prazan katalog
    setFavOnly(false);
    setShowShops(false);
    setRoastFilter(null);
    setBeanFilter(null);
    setOriginFilter(null);
    setScotchFilter(null);
    // promjena kartice gasi ručno sortiranje — svaka kartica ima svoj zadani
    // poredak (cigare po nazivu, pića po kvaliteti)
    setSort(null);
  };

  const styles = useMemo(() => {
    if (tab === "cigars") return [];
    const seen = new Set<string>();
    return DRINKS[tab]
      .filter((d) => {
        if (seen.has(d.style)) return false;
        seen.add(d.style);
        return true;
      })
      .map((d) => d.style);
  }, [tab]);

  /** Prženja i zrna kojih na kartici kave stvarno ima. */
  const coffeeFacets = useMemo(() => {
    if (tab !== "coffee") return { roasts: [], beans: [] };
    const roasts = new Set<CoffeeRoastLevel>();
    const beans = new Set<CoffeeSpecies>();
    for (const d of DRINKS.coffee) {
      if (d.roast) roasts.add(d.roast);
      if (d.species) beans.add(d.species);
    }
    return {
      roasts: (["light", "medium", "dark"] as CoffeeRoastLevel[]).filter((r) => roasts.has(r)),
      beans: (["arabica", "robusta", "blend"] as CoffeeSpecies[]).filter((b) => beans.has(b)),
    };
  }, [tab]);

  /**
   * Zemlje podrijetla na kartici, s brojem boca — najbrojnija prva. Kava ih
   * ima od početka; whisky ih dobiva jer je zemlja prva grana njegove karte
   * (Škotska → regija). Ostale kartice zemlju ne prikazuju: rum i brandy je
   * već nose u stilu, pa bi red chipova bio duplikat.
   */
  const originFacets = useMemo(() => {
    if (tab !== "coffee" && tab !== "whisky") return [];
    const counts = new Map<string, number>();
    for (const d of DRINKS[tab]) {
      // "—" = priprema bez jednog podrijetla (ristretto, cappuccino…)
      if (!d.country || d.country === "—") continue;
      counts.set(d.country, (counts.get(d.country) ?? 0) + 1);
    }
    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "hr"))
      .map(([country, count]) => ({ country, count }));
  }, [tab]);

  /** Škotske regije koje u katalogu stvarno imaju boce, s brojem. */
  const scotchFacets = useMemo(() => {
    if (tab !== "whisky") return [];
    const counts = new Map<ScotchRegion, number>();
    for (const d of DRINKS.whisky) {
      const r = scotchRegionOf(d);
      if (r) counts.set(r, (counts.get(r) ?? 0) + 1);
    }
    return SCOTCH_REGIONS.filter((r) => counts.has(r)).map((r) => ({
      region: r,
      count: counts.get(r)!,
    }));
  }, [tab]);

  const leafOriginOptions = useMemo(() => {
    const wrappers = new Set<string>();
    const binders = new Set<string>();
    const fillers = new Set<string>();
    for (const c of CIGARS) {
      if (c.wrapperOrigin) wrappers.add(c.wrapperOrigin);
      if (c.binderOrigin) binders.add(c.binderOrigin);
      if (c.fillerOrigin) fillers.add(c.fillerOrigin);
    }
    const sort = (a: string, b: string) => a.localeCompare(b, "hr");
    return {
      wrappers: [...wrappers].sort(sort),
      binders: [...binders].sort(sort),
      fillers: [...fillers].sort(sort),
    };
  }, []);

  const q = query.toLowerCase();

  // sortiranje po cijeni prati isti razrješivač kao prikazana cijena — inače
  // se "najjeftinije prvo" ne poklapa s brojevima u popisu
  const cigarPrice = (c: Cigar): number =>
    cigarLinePrice(c, market).price ?? Number.MAX_SAFE_INTEGER;

  const cigars = useMemo(() => {
    if (tab !== "cigars" || browseBrands) return [];
    const list = CIGARS.filter((c) => {
      if (!cigarInRegion(c, market)) return false;
      if (
        !matchesSearch(
          `${brandSearchHaystack(c.brand)} ${brandDisplayName(c.brand, market)} ${c.line} ${c.vitola} ${c.wrapper} ${c.country} ${(c.vitolas ?? [])
            .map((v) => [v.name, v.shape, v.format].filter(Boolean).join(" "))
            .join(" ")}`,
          q,
        )
      ) {
        return false;
      }
      if (strengthFilter != null && c.strength !== strengthFilter) return false;
      // oblik ∩ tržište: samo linije čiji matching oblik stvarno postoji u regiji
      if (shapeFilter != null && !firstVitolaOfShapeInRegion(c, shapeFilter, market)) {
        return false;
      }
      if (wrapperOriginFilter != null && c.wrapperOrigin !== wrapperOriginFilter) return false;
      if (binderOriginFilter != null && c.binderOrigin !== binderOriginFilter) return false;
      if (fillerOriginFilter != null && c.fillerOrigin !== fillerOriginFilter) return false;
      if (puroOnly && c.isPuro !== true) return false;
      if (favOnly && !favorites.has(favoriteKey("cigar", c.brand))) return false;
      return true;
    });
    // Uz aktivni shape filter: na listi prikaži tu vitolu (cijena/ime), ne „od“ linije
    const rows =
      shapeFilter == null
        ? list
        : list.map((c) => {
            const v = firstVitolaOfShapeInRegion(c, shapeFilter, market);
            return v ? applyVitola(c, v) : c;
          });
    // svaki komparator je pisan u SVOM zadanom smjeru (SORT_DEFAULT_DIR);
    // suprotan smjer nastaje obrtanjem u directedComparator
    const by: Partial<Record<SortKey, (a: Cigar, b: Cigar) => number>> = {
      name: (a, b) =>
        brandDisplayName(a.brand, market).localeCompare(brandDisplayName(b.brand, market)) ||
        a.line.localeCompare(b.line),
      price: (a, b) => cigarPrice(a) - cigarPrice(b),
      body: (a, b) => b.body - a.body,
      strength: (a, b) => b.strength - a.strength,
    };
    const cmp = sort ? by[sort.key] : undefined;
    if (!cmp || !sort) return [...rows].sort(by.name!);
    return [...rows].sort(directedComparator(cmp, SORT_DEFAULT_DIR[sort.key], sort.dir));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    tab,
    q,
    strengthFilter,
    shapeFilter,
    wrapperOriginFilter,
    binderOriginFilter,
    fillerOriginFilter,
    puroOnly,
    market,
    sort,
    browseBrands,
    favOnly,
    favorites,
  ]);

  const drinks = useMemo(() => {
    if (tab === "cigars") return [];
    const list = DRINKS[tab].filter((d) => {
      if (!matchesSearch(`${d.name} ${d.region} ${d.style}`, q)) return false;
      if (styleFilter != null && d.style !== styleFilter) return false;
      if (roastFilter != null && d.roast !== roastFilter) return false;
      if (beanFilter != null && d.species !== beanFilter) return false;
      if (originFilter != null && d.country !== originFilter) return false;
      if (scotchFilter != null && scotchRegionOf(d) !== scotchFilter) return false;
      if (cleanOnly && d.additiveStatus !== "clean" && d.additiveStatus !== "low") {
        return false;
      }
      if (favOnly) {
        const b = drinkBrand(d.id);
        if (!b || !favorites.has(favoriteKey("drink", b))) return false;
      }
      return true;
    });
    const mid = (d: Drink) =>
      d.priceEUR ? (d.priceEUR.min + d.priceEUR.max) / 2 : Number.MAX_SAFE_INTEGER;
    const by: Partial<Record<SortKey, (a: Drink, b: Drink) => number>> = {
      quality: (a, b) => (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
      price: (a, b) => mid(a) - mid(b),
      body: (a, b) => b.body - a.body || (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
      sweetness: (a, b) => b.sweetness - a.sweetness || (b.qualityScore ?? 0) - (a.qualityScore ?? 0),
    };
    const cmp = sort ? by[sort.key] : undefined;
    if (!cmp || !sort) return [...list].sort(by.quality!);
    return [...list].sort(directedComparator(cmp, SORT_DEFAULT_DIR[sort.key], sort.dir));
  }, [
    tab,
    q,
    styleFilter,
    roastFilter,
    beanFilter,
    originFilter,
    scotchFilter,
    cleanOnly,
    sort,
    favOnly,
    favorites,
  ]);

  useEffect(() => {
    setLimit(120);
  }, [
    tab,
    q,
    strengthFilter,
    shapeFilter,
    wrapperOriginFilter,
    binderOriginFilter,
    fillerOriginFilter,
    puroOnly,
    market,
    sort,
    browseBrands,
    favOnly,
    favorites,
  ]);

  const favKind = tab === "cigars" ? "cigar" : "drink";
  // Prazan popis pod „★ Omiljene" znači ili da marka nije označena, ili da ih
  // uopće nema — druga poruka bez ove je zagonetka.
  const emptyFavorites = ![...favorites].some((k) => k.startsWith(`${favKind}:`));

  const brandModeCount = tab === "cigars" ? brandRows.length : drinkBrandRows.length;
  const railLetters =
    tab === "cigars" ? brandAnchors.letters : drinkBrandAnchors.letters;
  const showRail =
    browseBrands &&
    brandModeCount > 12 &&
    !brand &&
    !line &&
    !detail &&
    !dBrand &&
    !pendingCigar;

  return (
    <div className="pb-4">
      <div className="no-scrollbar mt-4 flex gap-2 overflow-x-auto">
        {TABS.map((tb) => (
          <Chip key={tb} active={tab === tb} onClick={() => switchTab(tb)}>
            {tb === "cigars" ? t("cat.cigars") : t(`cat.${tb}` as const)}
          </Chip>
        ))}
      </div>

      <div className="mt-3">
        <SearchInput value={query} onChange={setQuery} placeholder={t("pair.search")} />
      </div>

      {searchHits.length > 0 && (
        <div className="mt-2 space-y-1.5 rounded-xl border border-zlato/25 bg-cedar/50 p-2">
          <div className="px-1 text-micro uppercase tracking-widest text-dim">
            {t("search.hits")}
          </div>
          {searchHits.map((h) => {
            if (h.kind === "brand") {
              return (
                <button
                  key={`b-${h.brand}`}
                  type="button"
                  onClick={() => openBrand(h.brand)}
                  className="flex w-full items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-zlato/10"
                >
                  <span className="text-sm text-papir">{brandDisplayName(h.brand, market)}</span>
                  <span className="shrink-0 text-micro text-zlato-2">{t("search.kindBrand")}</span>
                </button>
              );
            }
            if (h.kind === "line") {
              return (
                <button
                  key={`l-${h.cigar.id}`}
                  type="button"
                  onClick={() => openLine(h.cigar)}
                  className="flex w-full items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-zlato/10"
                >
                  <span className="truncate text-sm text-papir">
                    {brandDisplayName(h.cigar.brand, market)}{" "}
                    <span className="text-zlato-2">{h.cigar.line}</span>
                  </span>
                  <span className="shrink-0 text-micro text-zlato-2">{t("search.kindLine")}</span>
                </button>
              );
            }
            return (
              <button
                key={`v-${h.cigar.id}-${h.vitola.name}`}
                type="button"
                onClick={() => openVitola(h.cigar, h.vitola)}
                className="flex w-full items-baseline justify-between gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-zlato/10"
              >
                <span className="truncate text-sm text-papir">
                  {brandDisplayName(h.cigar.brand, market)} {h.cigar.line} · {h.vitola.name}
                </span>
                <span className="shrink-0 text-micro text-zlato-2">{t("search.kindVitola")}</span>
              </button>
            );
          })}
        </div>
      )}

      {matchedBrands.length > 0 && (
        <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
          {matchedBrands.map((b) => (
            <button
              key={b}
              type="button"
              onClick={() => openBrand(b)}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-zlato/50 bg-zlato/10 px-3 py-1.5 text-xs text-zlato-2 hover:bg-zlato/20"
            >
              {t("brand.open")}: {brandDisplayName(b, market)} →
            </button>
          ))}
        </div>
      )}

      <div className="no-scrollbar mt-2 flex gap-2 overflow-x-auto">
        {/* Kava nema proizvođača ("Ristretto" je priprema), pa ni marke ni omiljene. */}
        {tab !== "coffee" && (
          <Chip active={browseBrands} onClick={() => setBrowseBrands(!browseBrands)}>
            {t("brand.index")}
          </Chip>
        )}
        {tab !== "coffee" && (
          <Chip active={favOnly} onClick={() => setFavOnly(!favOnly)}>
            {t("fav.only")}
          </Chip>
        )}
        {tab === "cigars" && (
          <Chip active={showShops} onClick={() => setShowShops(!showShops)}>
            {t("shops.title")}
          </Chip>
        )}
        {tab === "cigars" &&
          !browseBrands &&
          [1, 2, 3, 4, 5].map((s) => (
            <Chip
              key={s}
              active={strengthFilter === s}
              onClick={() => setStrengthFilter(strengthFilter === s ? null : s)}
            >
              {t("filter.strength")} {s}
            </Chip>
          ))}
        {tab === "cigars" && !browseBrands && (
          <Chip active={puroOnly} onClick={() => setPuroOnly(!puroOnly)}>
            {t("filter.puro")}
          </Chip>
        )}
        {/* stil i „bez aditiva" filtriraju boce, a u pregledu marki boca nema */}
        {tab !== "cigars" && tab !== "coffee" && tab !== "tequila" && !browseBrands && (
          <Chip active={cleanOnly} onClick={() => setCleanOnly(!cleanOnly)}>
            {t("filter.clean")}
          </Chip>
        )}
        {!browseBrands &&
          styles.map((s) => (
            <Chip
              key={s}
              active={styleFilter === s}
              onClick={() => setStyleFilter(styleFilter === s ? null : s)}
            >
              {lx(STYLE_LABELS[s]) || s}
            </Chip>
          ))}
      </div>

      {/* kava: prženje / zrno / zemlja — priprema je gore, među stilovima */}
      {tab === "coffee" && !browseBrands && coffeeFacets.roasts.length > 1 && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.roast")}
          </span>
          {coffeeFacets.roasts.map((r) => (
            <Chip
              key={r}
              active={roastFilter === r}
              onClick={() => setRoastFilter(roastFilter === r ? null : r)}
            >
              {t(`roast.${r}` as StringKey)}
            </Chip>
          ))}
        </div>
      )}
      {tab === "coffee" && !browseBrands && coffeeFacets.beans.length > 1 && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.bean")}
          </span>
          {coffeeFacets.beans.map((b) => (
            <Chip
              key={b}
              active={beanFilter === b}
              onClick={() => setBeanFilter(beanFilter === b ? null : b)}
            >
              {t(`bean.${b}` as StringKey)}
            </Chip>
          ))}
        </div>
      )}
      {!browseBrands && originFacets.length > 1 && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.country")}
          </span>
          {originFacets.map(({ country, count }) => (
            <Chip
              key={country}
              active={originFilter === country}
              onClick={() => {
                const next = originFilter === country ? null : country;
                setOriginFilter(next);
                // regija je grana Škotske — čim se zemlja promijeni, otpada
                if (next !== SCOTLAND) setScotchFilter(null);
              }}
            >
              {cn(country)}
              <span className="ml-1.5 tabular-nums text-dim/70">{count}</span>
            </Chip>
          ))}
        </div>
      )}

      {/* škotske regije — druga grana karte, vidljiva kad je Škotska izabrana */}
      {tab === "whisky" && !browseBrands && originFilter === SCOTLAND && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.scotchRegion")}
          </span>
          {scotchFacets.map(({ region, count }) => (
            <Chip
              key={region}
              active={scotchFilter === region}
              onClick={() => setScotchFilter(scotchFilter === region ? null : region)}
            >
              {lx(scotchRegionCard(region).label)}
              <span className="ml-1.5 tabular-nums text-dim/70">{count}</span>
            </Chip>
          ))}
        </div>
      )}

      {/* pouka uz izbor: regija ima cijelu karticu, vrsta jedan redak */}
      {tab === "whisky" && !browseBrands && scotchFilter != null && (
        <article className="mt-3 rounded-xl border border-zlato/25 bg-cedar/60 px-3.5 py-3">
          <h3 className="font-display text-micro uppercase tracking-[0.18em] text-zlato">
            {lx(scotchRegionCard(scotchFilter).label)}
          </h3>
          <p className="mt-1 text-xs leading-relaxed text-papir/80">
            {lx(scotchRegionCard(scotchFilter).summary)}
          </p>
          <details className="group mt-2">
            <summary className="cursor-pointer list-none text-micro uppercase tracking-widest text-dim hover:text-zlato">
              {t("whisky.regionMore")}
            </summary>
            <div className="mt-1.5 border-t border-dim/15 pt-2">
              <LessonBody text={lx(scotchRegionCard(scotchFilter).body)} />
            </div>
          </details>
        </article>
      )}
      {tab === "whisky" && !browseBrands && styleFilter != null && whiskyStyleNote(styleFilter) && (
        <p className="mt-2.5 border-l-2 border-zlato/40 pl-3 text-xs leading-relaxed text-papir/75">
          <span className="font-medium text-papir">{lx(STYLE_LABELS[styleFilter]) || styleFilter}</span>
          <span className="text-dim"> — </span>
          {lx(whiskyStyleNote(styleFilter))}
        </p>
      )}

      {/* filter oblika (vitole) — samo u ravnom popisu cigara */}
      {tab === "cigars" && !browseBrands && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.shape")}
          </span>
          {SHAPE_FAMILIES.map((s) => (
            <Chip
              key={s}
              active={shapeFilter === s}
              onClick={() => setShapeFilter(shapeFilter === s ? null : s)}
            >
              {t(`shape.${s}` as StringKey)}
            </Chip>
          ))}
        </div>
      )}

      {tab === "cigars" && !browseBrands && leafOriginOptions.wrappers.length > 0 && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.wrapper")}
          </span>
          {leafOriginOptions.wrappers.map((o) => (
            <Chip
              key={`w-${o}`}
              active={wrapperOriginFilter === o}
              onClick={() => setWrapperOriginFilter(wrapperOriginFilter === o ? null : o)}
            >
              {cn(o)}
            </Chip>
          ))}
        </div>
      )}
      {tab === "cigars" && !browseBrands && leafOriginOptions.binders.length > 0 && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.binder")}
          </span>
          {leafOriginOptions.binders.map((o) => (
            <Chip
              key={`b-${o}`}
              active={binderOriginFilter === o}
              onClick={() => setBinderOriginFilter(binderOriginFilter === o ? null : o)}
            >
              {cn(o)}
            </Chip>
          ))}
        </div>
      )}
      {tab === "cigars" && !browseBrands && leafOriginOptions.fillers.length > 0 && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("filter.filler")}
          </span>
          {leafOriginOptions.fillers.map((o) => (
            <Chip
              key={`f-${o}`}
              active={fillerOriginFilter === o}
              onClick={() => setFillerOriginFilter(fillerOriginFilter === o ? null : o)}
            >
              {cn(o)}
            </Chip>
          ))}
        </div>
      )}

      {/* tržište uvijek vidljivo za cigare (indeks brendova + popis) */}
      {tab === "cigars" && <MarketFilter className="mt-2" />}

      {!browseBrands && (
        <div className="no-scrollbar mt-2 flex items-center gap-2 overflow-x-auto">
          <span className="shrink-0 text-micro uppercase tracking-widest text-dim">
            {t("sort.label")}
          </span>
          {(tab === "cigars" ? CIGAR_SORTS : DRINK_SORTS).map((s) => (
            <Chip
              key={s}
              active={sort?.key === s}
              onClick={() => setSort((cur) => cycleSort(cur, s, SORT_DEFAULT_DIR[s]))}
            >
              {t(`sort.${s}` as StringKey)}
              {sortArrow(sort, s)}
            </Chip>
          ))}
        </div>
      )}

      {tab === "cigars" && showShops && (
        <div className="mt-3 space-y-3 rounded-xl border border-zlato/25 bg-cedar/60 p-3">
          <p className="text-xs leading-relaxed text-dim">{t("shops.intro")}</p>
          {REGIONS.map((r) => (
            <div key={r}>
              <button
                type="button"
                onClick={() => {
                  setMarket(r);
                  setBrowseBrands(false);
                }}
                className="flex w-full items-baseline justify-between gap-2 text-left"
              >
                <span className="font-display text-sm uppercase tracking-widest text-zlato-2">
                  {t(`market.${r}` as StringKey)}
                </span>
                <span className="shrink-0 text-micro text-dim">
                  {cigarCountByRegion[r]} {t("shops.availableHere")} →
                </span>
              </button>
              <div className="mt-1.5 space-y-1.5">
                {SHOPS.filter((s) => s.region === r).map((s) => (
                  <a
                    key={s.id}
                    href={s.home}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-lg border border-dim/15 bg-humidor/40 px-2.5 py-1.5 hover:border-zlato/40"
                  >
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="text-sm text-papir/90">{s.name} ↗</span>
                      <span className="shrink-0 text-micro text-dim">
                        {s.walkIn
                          ? t("shops.walkIn")
                          : s.productHost
                            ? t("shops.direct")
                            : t("shops.search")}
                      </span>
                    </div>
                    <div className="text-micro text-dim/85">{lx(s.note)}</div>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-3 text-xs text-dim">
        {browseBrands
          ? `${tab === "cigars" ? brandRows.length : drinkBrandRows.length} · ${t("brand.index")}`
          : `${tab === "cigars" ? cigars.length : drinks.length} · ${
              tab === "cigars" ? t("cat.cigars") : t(`cat.${tab}` as const)
            }`}
      </div>

      {favOnly && emptyFavorites && (
        <p className="mt-2 rounded-xl border border-dim/20 bg-cedar/50 px-3 py-2.5 text-xs leading-relaxed text-dim">
          {t("fav.none")}
        </p>
      )}

      <div className="mt-2 space-y-2">
        {browseBrands &&
          tab === "cigars" &&
          brandRows.map((b, i) => {
            const anchor = brandAnchors.at.get(i);
            const linesInMarket = cigarsByBrand(b.brand).filter(
              (c) => c.line !== "Additional Vitolas" && cigarInRegion(c, market),
            );
            const lineCount = market === "ALL" ? b.lineCount : linesInMarket.length;
            return (
              <div
                key={b.brand}
                id={anchor ? `ci-alpha-${anchor}` : undefined}
                className="flex scroll-mt-4 items-start gap-2 rounded-xl border border-dim/15 bg-cedar p-3 transition-colors focus-within:border-zlato/40 hover:border-zlato/40"
              >
                <button
                  type="button"
                  onClick={() => openBrand(b.brand)}
                  className="min-w-0 flex-1 text-left"
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="font-display text-base text-papir">
                      {brandDisplayName(b.brand, market)}
                    </span>
                    {b.minPriceEUR != null && (
                      <span className="shrink-0 text-xs text-dim">
                        {t("brand.from")} {b.minPriceEUR.toFixed(b.minPriceEUR % 1 ? 2 : 0)} €
                      </span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-dim">
                    {b.info ? cn(b.info.country) : ""}
                    {b.info?.founded ? ` · ${b.info.founded}` : ""}
                    {" · "}
                    {lineCount} {t("brand.lines")}
                    {b.hasAdditionalVitolas && market === "ALL" ? " · +" : ""}
                  </div>
                  {b.info && (
                    <div className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-dim/90">
                      {lx(b.info.blurb)}
                    </div>
                  )}
                </button>
                <FavoriteStar kind="cigar" brand={b.brand} />
              </div>
            );
          })}
        {browseBrands &&
          tab !== "cigars" &&
          drinkBrandRows.map((b, i) => {
            const anchor = drinkBrandAnchors.at.get(i);
            return (
              <div
                key={b.brand}
                id={anchor ? `ci-alpha-${anchor}` : undefined}
                className="flex scroll-mt-4 items-start gap-2 rounded-xl border border-dim/15 bg-cedar p-3 transition-colors focus-within:border-zlato/40 hover:border-zlato/40"
              >
                <button
                  type="button"
                  onClick={() => openDrinkBrand(b.brand)}
                  className="min-w-0 flex-1 text-left"
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <span className="font-display text-base text-papir">{b.brand}</span>
                    {b.minPriceEUR != null && (
                      <span className="shrink-0 text-xs text-dim">
                        {t("brand.from")} {b.minPriceEUR.toFixed(0)} €
                      </span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-dim">
                    {b.countries.length > 0 && `${b.countries.map(cn).join(", ")} · `}
                    {b.count} {t("dbrand.bottles")}
                    {b.bestQuality != null && (
                      <span className="text-zlato-2"> · {b.bestQuality}/10</span>
                    )}
                  </div>
                  {b.categories.length > 1 && (
                    <div className="mt-1 text-micro uppercase tracking-widest text-dim/80">
                      {b.categories.map((c) => t(`cat.${c}` as StringKey)).join(" · ")}
                    </div>
                  )}
                </button>
                <FavoriteStar kind="drink" brand={b.brand} />
              </div>
            );
          })}
        {!browseBrands &&
          cigars.slice(0, limit).map((c) => (
            <CigarRow
              key={`${c.id}::${c.line}`}
              cigar={c}
              onClick={() => openFromFlatList(c)}
            />
          ))}
        {!browseBrands && tab === "cigars" && cigars.length > limit && (
          <button
            type="button"
            onClick={() => setLimit((n) => n + 200)}
            className="w-full rounded-xl border border-zlato/30 bg-cedar/60 py-2.5 text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
          >
            {t("catalog.showMore")} ({cigars.length - limit})
          </button>
        )}
        {!browseBrands &&
          drinks.map((d, i) => (
            <DrinkRow
              key={d.id}
              drink={d}
              rank={i + 1}
              onClick={() => openDrinkFromList(d)}
            />
          ))}
      </div>

      {showRail && <AlphabetRail letters={railLetters} onJump={jumpToLetter} />}

      {pendingCigar && (
        <VitolaPicker
          cigar={pendingCigar}
          onPick={(v) => openVitola(pendingCigar, v)}
          onBack={() => setPendingCigar(null)}
        />
      )}

      {brand && (
        <BrandSheet brand={brand} onClose={clearCatalogFocus} onOpenLine={openLine} />
      )}

      {dBrand && (
        <DrinkBrandSheet
          brand={dBrand}
          onClose={clearCatalogFocus}
          onOpenDrink={openDrinkFromBrand}
        />
      )}

      {line && (
        <LineSheet
          cigar={line}
          onClose={() => openBrand(line.brand)}
          onOpenBrand={openBrand}
          onOpenVitola={openVitola}
        />
      )}

      <DetailSheet
        target={detail}
        onClose={closeDetail}
        onOpenBrand={openBrand}
        onOpenDrinkBrand={openDrinkBrand}
        onOpenLine={openLine}
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
