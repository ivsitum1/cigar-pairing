import { useEffect, useState } from "react";
import { SheetShell } from "./SheetShell";
import type { Cigar, Drink, Region } from "../types";
import { useI18n, STYLE_LABELS, ADDITIVE_LABELS, ADDITIVE_RULES, COFFEE_ROAST_LABELS, COFFEE_PROCESS_LABELS, COFFEE_SPECIES_LABELS, leafMetaParts, leafOriginDisplay } from "../i18n";
import { flavorLabel } from "../engine/rules";
import {
  brandInfo,
  brandDisplayName,
  cigarShopLinks,
  cigarShopLinkPrice,
  cigarLatestFetchedAt,
  drinkBrand,
  resolveCigarId,
  formatPrice,
} from "../data";
import { REGIONS } from "../data/shops";
import { drinkBuyLink } from "../lib/drinkBuyLink";
import {
  DRINK_REGIONS,
  drinkAvailabilityHR,
  drinkRegionAvailability,
  drinkShopLinks,
} from "../lib/drinkShopLinks";
import { formatEur, vitolaPriceForMarket } from "../lib/cigarPrice";
import { drinkNameLoc } from "../lib/drinkName";
import { vitolaBlurb } from "../lib/vitolaInfo";
import { cigarLinkStockView, drinkStockView, type StockView } from "../lib/shopStock";
import { resolveSamplerCigar } from "../lib/samplerLink";
import { cigarItemId, parseCigarItemId } from "../lib/cigarItemId";
import {
  stockNeedsVitola,
  stockVitolaName,
  vitolaStockId,
} from "../lib/humidorVitola";
import { cigarDescription } from "../lib/cigarNote";
import { needsVitolaPick } from "../lib/cigarVitola";
import { shouldOfferWishlist } from "../lib/lastCigar";
import {
  claimOwnedForStock,
  releaseOwnedIfEmpty,
  unpackSamplerIntoStock,
} from "../lib/stockOwnership";
import { isSampler, samplerPieceCount } from "../lib/samplerStock";
import { Chip, Meter } from "./ui";
import { BackButton } from "./BackButton";
import { ProductThumb } from "./ProductThumb";
import { productPhoto, productPhotoForCigar } from "../lib/productImage";
import { FavoriteStar } from "./FavoriteStar";
import { LastCigarPrompt } from "./LastCigarPrompt";
import { VitolaPicker } from "./VitolaPicker";
import {
  getItemState,
  updateItem,
  useCollection,
} from "../store/collection";
import { useMarket } from "../store/market";
import { useTasteProfiles } from "../store/tasteProfile";
import { withTaste } from "../lib/tasteProfile";
import { TasteMeters } from "./TasteMeters";
import { NotePrompts } from "./NotePrompts";
import {
  addHumidor,
  adjustStock,
  setActiveHumidor,
  useHumidors,
} from "../store/humidor";

type Item = { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink };

export function DetailSheet({
  target,
  onClose,
  onOpenBrand,
  onOpenDrinkBrand,
  onOpenLine,
  onPair,
  onLogEvening,
}: {
  target: Item | null;
  onClose: () => void;
  onOpenBrand?: (brand: string) => void;
  /** Marka pića (izvedena iz imena) — vodi u usporedbu ostalih boca iste kuće. */
  onOpenDrinkBrand?: (brand: string) => void;
  onOpenLine?: (cigar: Cigar) => void;
  onPair?: (target: Item) => void;
  /** Samo za cigare — otvara večernji zapis s ovom cigarom. */
  onLogEvening?: (cigar: Cigar) => void;
}) {
  const { t } = useI18n();
  useCollection();
  // interni stog: navigacija unutar kartice (npr. sampler → pojedina cigara)
  const [stack, setStack] = useState<Item[]>([]);
  useEffect(() => {
    setStack([]);
  }, [target?.item.id]);
  const active = stack.length ? stack[stack.length - 1] : target;
  // cigare: ključ nosi odabranu vitolu (Churchill ≠ Corona iste linije)
  const id =
    active?.kind === "cigar" ? cigarItemId(active.item) : active?.item.id;
  const state = id ? getItemState(id) : null;
  const [note, setNote] = useState("");

  useEffect(() => {
    if (id) setNote(getItemState(id).note);
  }, [id]);

  if (!target || !active || !id || !state) return null;

  const saveNote = () => updateItem(id, { note });
  const goBack = () =>
    stack.length ? setStack((s) => s.slice(0, -1)) : onClose();
  const pushCigar = (c: Cigar) =>
    setStack((s) => [...s, { kind: "cigar", item: c }]);

  const sheetLabel =
    active?.kind === "cigar"
      ? `${active.item.brand} ${active.item.line}`
      : (active?.item.name ?? "");

  return (
    <SheetShell
      onClose={onClose}
      label={sheetLabel}
      scrollKey={id}
      panelClassName="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
    >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-dim/40 sm:hidden" />

        <div className="mb-3">
          <BackButton onClick={goBack}>{t("common.back")}</BackButton>
        </div>

        {active.kind === "cigar" ? (
          <CigarDetails
            cigar={active.item}
            onOpenBrand={onOpenBrand}
            onOpenLine={onOpenLine}
            onOpenCigar={pushCigar}
          />
        ) : (
          <DrinkDetails drink={active.item} onOpenBrand={onOpenDrinkBrand} />
        )}

        <div className="band-rule my-4" />

        {/* kolekcija kontrole */}
        <div className="flex flex-wrap items-center gap-2">
          <Chip
            active={state.owned}
            onClick={() => {
              // multi-vitola linija bez odabrane veličine — Imam ide po vitoli
              if (
                active.kind === "cigar" &&
                !state.owned &&
                needsVitolaPick(active.item) &&
                !active.item.selectedVitola
              ) {
                onOpenLine?.(active.item);
                return;
              }
              // kupljeno -> makni s liste zelja; skidanje "Imam" ne dira listu
              updateItem(
                id,
                state.owned ? { owned: false } : { owned: true, wishlist: false },
              );
            }}
          >
            ✓ {t("coll.owned")}
          </Chip>
          <Chip
            active={state.tried}
            onClick={() => updateItem(id, { tried: !state.tried })}
          >
            {t("coll.tried")}
          </Chip>
          <Chip
            active={state.wishlist}
            onClick={() => updateItem(id, { wishlist: !state.wishlist })}
          >
            ☆ {t("coll.wishlist")}
          </Chip>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs text-dim">{t("coll.myRating")}</span>
            <select
              // opcije su "10.0","9.5"... — broj 10 mora postati "10.0" da se prikaže
              value={state.rating != null ? state.rating.toFixed(1) : ""}
              onChange={(e) =>
                updateItem(id, {
                  rating: e.target.value ? Number(e.target.value) : null,
                })
              }
              className="rounded-md border border-dim/30 bg-cedar px-2 py-1 text-sm text-papir"
            >
              <option value="">—</option>
              {Array.from({ length: 19 }, (_, i) => (10 - i * 0.5).toFixed(1)).map(
                (v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ),
              )}
            </select>
          </div>
        </div>
        <div className="mt-3">
          <NotePrompts
            context={active.kind}
            value={note}
            onChange={(next) => {
              setNote(next);
              updateItem(id, { note: next });
            }}
            showRatingScale
          />
        </div>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          onBlur={saveNote}
          placeholder={
            active.kind === "drink"
              ? t("coll.notePlaceholderDrink")
              : t("coll.notePlaceholderCigar")
          }
          rows={4}
          className="mt-2 w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2 text-sm text-papir placeholder:text-dim/60 focus:border-zlato/60 focus:outline-none"
        />

        {active.kind === "cigar" && (
          <HumidorControls cigar={active.item} itemId={id} />
        )}

        {onPair && (
          <button
            type="button"
            onClick={() => onPair(active)}
            className="mt-4 w-full rounded-lg border border-oxblood/50 bg-oxblood/15 py-2.5 font-display text-sm uppercase tracking-widest text-zlato-2 hover:bg-oxblood/25"
          >
            {active.kind === "cigar" ? t("cat.pairWithDrink") : t("cat.pairWithCigar")}
          </button>
        )}

        {active.kind === "cigar" && onLogEvening && (
          <button
            type="button"
            onClick={() => onLogEvening(active.item)}
            className="mt-2 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
          >
            {t("session.log")}
          </button>
        )}

        <button
          onClick={onClose}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("common.close")}
        </button>
    </SheetShell>
  );
}

function CigarDetails({
  cigar,
  onOpenBrand,
  onOpenLine,
  onOpenCigar,
}: {
  cigar: Cigar;
  onOpenBrand?: (brand: string) => void;
  onOpenLine?: (cigar: Cigar) => void;
  onOpenCigar?: (c: Cigar) => void;
}) {
  const { t, lxStrict, cn, lang } = useI18n();
  const market = useMarket();
  // tvoja ocjena, kad postoji, nadjačava katalogovu procjenu i ovdje i u pairingu
  const taste = useTasteProfiles();
  const shown = withTaste(cigar, taste);
  const mine = shown.profileFromUser === true;
  const description = cigarDescription(cigar, lang);
  const brand = brandInfo(cigar.brand);
  const displayBrand = brandDisplayName(cigar.brand, market);
  const photo = productPhotoForCigar(cigar);
  const vitolaCrumb =
    cigar.vitolas.length === 1 ? cigar.vitolas[0].name : cigar.vitola;
  // Bez odabranog tržišta ("Sve") cijena zna doći iz EU/USA kataloga — reci
  // odakle je, da se HR i EU broj ne miješaju bez oznake.
  const regionTag = (region: Region | null) =>
    market === "ALL" && region && region !== "HR" ? ` ${region}` : "";
  return (
    <>
      {/* Brand › Line › Vitola — svaki crumb navigira gore */}
      <div className="mb-2 flex flex-wrap items-center gap-x-1.5 text-xs text-dim">
        {onOpenBrand ? (
          <button
            type="button"
            onClick={() => onOpenBrand(cigar.brand)}
            className="underline decoration-zlato/40 underline-offset-2 hover:text-zlato-2"
          >
            {displayBrand}
          </button>
        ) : (
          <span>{displayBrand}</span>
        )}
        <span aria-hidden>›</span>
        {onOpenLine ? (
          <button
            type="button"
            onClick={() => onOpenLine(cigar)}
            className="underline decoration-zlato/40 underline-offset-2 hover:text-zlato-2"
          >
            {cigar.line}
          </button>
        ) : (
          <span className="text-zlato-2">{cigar.line}</span>
        )}
        {vitolaCrumb ? (
          <>
            <span aria-hidden>›</span>
            <span className="text-papir/90">{vitolaCrumb}</span>
          </>
        ) : null}
      </div>

      <div className="flex items-start gap-3">
        <div className="min-w-0 flex-1">
          <div className="font-display text-xl text-papir">
            {displayBrand}{" "}
            <span className="text-zlato-2">{cigar.line}</span>
            {vitolaCrumb && vitolaCrumb !== cigar.line ? (
              <span className="text-papir/80"> · {vitolaCrumb}</span>
            ) : null}
          </div>
          <div className="mt-1 text-sm text-dim">
            {leafMetaParts(cigar.wrapper, cigar.country, lang).join(" · ")}
            {cigar.isPuro === true ? ` · ${t("leaf.puro")}` : null}
            {onOpenBrand && (
              <>
                {" · "}
                <button
                  type="button"
                  onClick={() => onOpenBrand(cigar.brand)}
                  className="text-zlato hover:text-zlato-2"
                >
                  {t("brand.viewAll")} →
                </button>
              </>
            )}
          </div>
        </div>
        {photo && (
          <ProductThumb
            src={photo.src}
            treatment={photo.treatment}
            alt={`${displayBrand} ${cigar.line}`}
          />
        )}
      </div>
      {(cigar.wrapperOrigin || cigar.binderOrigin || cigar.fillerOrigin) && (
        <div className="mt-1.5 space-y-0.5 text-xs text-dim/90">
          {cigar.wrapperOrigin ? (
            <div>
              {t("leaf.wrapper")}:{" "}
              {leafOriginDisplay(cigar.wrapperOrigin, cigar.wrapper, lang)}
            </div>
          ) : null}
          {cigar.binderOrigin ? (
            <div>
              {t("leaf.binder")}:{" "}
              {leafOriginDisplay(cigar.binderOrigin, cigar.binder, lang)}
            </div>
          ) : null}
          {cigar.fillerOrigin ? (
            <div>
              {t("leaf.filler")}:{" "}
              {leafOriginDisplay(cigar.fillerOrigin, cigar.filler, lang)}
            </div>
          ) : null}
        </div>
      )}
      <TasteMeters cigar={cigar} />

      {/* vitole s vremenom pusenja i cijenom */}
      <div className="mt-3">
        <div className="mb-1 text-micro uppercase tracking-widest text-dim">
          {t("common.vitolas")}
        </div>
        <div className="space-y-1">
          {cigar.vitolas.map((v) => {
            const blurb = vitolaBlurb(v.name, lang);
            // cijena+link te vitole u ODABRANOM tržištu — isti razrješivač koji
            // koristi popis i linija, pa je broj svugdje isti
            const { price, url, approx, region } = vitolaPriceForMarket(v, market);
            return (
              <div
                key={v.name}
                className="rounded-md border border-dim/15 px-2.5 py-1.5 text-sm"
              >
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-papir/90">{v.name}</span>
                  <span className="shrink-0 text-xs text-dim">
                    {v.format && v.format !== "—" ? `${v.format} · ` : ""}
                    {v.smokeTimeMin != null ? `⏱ ~${v.smokeTimeMin} min` : ""}
                    {price != null &&
                      (url ? (
                        <a href={url} target="_blank" rel="noreferrer" className="ml-1.5 text-zlato-2 underline decoration-zlato/40 underline-offset-2">
                          {approx ? "~" : ""}{formatEur(price)}{regionTag(region)} ↗
                        </a>
                      ) : (
                        <span className="ml-1.5 text-zlato-2">
                          {approx ? "~" : ""}{formatEur(price)}{regionTag(region)}
                        </span>
                      ))}
                  </span>
                </div>
                {blurb && (
                  <div className="mt-0.5 text-micro leading-snug text-dim/85">{blurb}</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <dl className="mt-3 space-y-1 text-sm">
        {cigar.availabilityHR.length > 0 && (
          <Row k={t("common.shop")} v={cigar.availabilityHR.join(", ")} />
        )}
        <Row
          k={t("common.markets")}
          v={cigar.markets.map((m) => t(`market.${m}` as Parameters<typeof t>[0])).join(", ")}
        />
      </dl>

      {/* kupnja po regiji — kad je filter na regiji prikazi samo tu, inace sve */}
      <CigarBuyLinks cigar={cigar} />
      <CigarPriceNote cigar={cigar} />
      <div className="mt-2 flex flex-wrap items-center gap-1.5">
        {cigar.flavoured && (
          <span className="rounded-full border border-lista/50 bg-lista/15 px-2 py-0.5 text-micro uppercase tracking-wide text-lista">
            ✿ {t("common.flavoured")}
          </span>
        )}
        {cigar.flavorTags.map((tag) => (
          <Chip key={tag}>{flavorLabel(tag, lang)}</Chip>
        ))}
      </div>
      {/* opis samo kad postoji — generirano prepricavanje atributa nije opis */}
      {description && (
        <p className="mt-3 text-sm leading-relaxed text-papir/85">{description}</p>
      )}
      {/* poštene oznake izvora podataka */}
      {(shown.profileEstimated ||
        cigar.formatEstimated ||
        (cigar.strengthFromTasting && !mine) ||
        (cigar.strengthFromShop && !mine)) && (
        <div className="mt-1.5 space-y-0.5">
          {shown.profileEstimated && (
            <p className="text-micro leading-snug text-dim/70">≈ {t("common.estimatedProfile")}</p>
          )}
          {!!cigar.strengthFromTasting && !mine && (
            <p className="text-micro leading-snug text-dim/70">
              ★ {t("common.strengthTasted")} ({cigar.strengthFromTasting})
            </p>
          )}
          {cigar.strengthFromShop && !cigar.strengthFromTasting && !mine && (
            <p className="text-micro leading-snug text-dim/70">✓ {t("common.strengthReal")}</p>
          )}
          {cigar.formatEstimated && (
            <p className="text-micro leading-snug text-dim/70">± {t("common.formatEstimated")}</p>
          )}
        </div>
      )}
      {/* sadrzaj samplera / gift-packa */}
      {cigar.lineup && cigar.lineup.length > 0 && (
        <div className="mt-3 rounded-lg border border-dim/20 bg-cedar/60 p-3">
          <div className="text-[10px] uppercase tracking-widest text-dim">
            {t("common.samplerContents")}
          </div>
          <ul className="mt-1.5 flex flex-wrap gap-1.5">
            {cigar.lineup.map((b) => {
              const hit = onOpenCigar
                ? resolveSamplerCigar(cigar.brand, b, cigar.id)
                : null;
              return (
                <li key={b}>
                  {hit ? (
                    <Chip onClick={() => onOpenCigar!(hit)}>{b} →</Chip>
                  ) : (
                    <Chip>{b}</Chip>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
      {/* o brendu — kratka povijest odmah u kartici */}
      {brand && (
        <div className="mt-3 rounded-lg border border-dim/20 bg-cedar/60 p-3">
          <div className="text-micro uppercase tracking-widest text-dim">
            {displayBrand} · {cn(brand.country)} · {brand.founded}
          </div>
          <p className="mt-1 text-xs leading-relaxed text-papir/80">
            {lxStrict(brand.blurb)}
          </p>
          {brand.signature && (
            <p className="mt-1.5 text-xs leading-relaxed text-zlato-2">
              ◈ {lxStrict(brand.signature)}
            </p>
          )}
          {brand.story && (
            <p className="mt-1.5 text-xs leading-relaxed text-papir/70">
              {lxStrict(brand.story)}
            </p>
          )}
        </div>
      )}
    </>
  );
}

function DrinkDetails({
  drink,
  onOpenBrand,
}: {
  drink: Drink;
  onOpenBrand?: (brand: string) => void;
}) {
  const { t, lx, lxStrict, sv, rgn, lang } = useI18n();
  const style = STYLE_LABELS[drink.style];
  const availability = drinkAvailabilityHR(drink);
  const brand = drinkBrand(drink.id);
  const photo = productPhoto("drink", drink.id);
  return (
    <>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="font-display text-xl text-papir">{lx(drinkNameLoc(drink))}</div>
          {brand &&
            (onOpenBrand ? (
              <button
                type="button"
                onClick={() => onOpenBrand(brand)}
                className="mt-0.5 text-xs uppercase tracking-widest text-zlato-2 hover:underline"
              >
                {brand} →
              </button>
            ) : (
              <div className="mt-0.5 text-xs uppercase tracking-widest text-dim">{brand}</div>
            ))}
        </div>
        <div className="flex shrink-0 items-start gap-2">
          {photo && (
            <ProductThumb
              src={photo.src}
              treatment={photo.treatment}
              alt={lx(drinkNameLoc(drink))}
            />
          )}
          {brand && <FavoriteStar kind="drink" brand={brand} />}
        </div>
      </div>
      <div className="mt-1 text-sm text-dim">
        {style ? lx(style) : drink.style} · {rgn(drink.region)}
        {drink.abv ? ` · ${drink.abv}%` : ""}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
        <Meter value={drink.body} label={t("common.body")} />
        <Meter value={drink.sweetness} label={t("common.sweetness")} accent="var(--color-lista)" />
      </div>
      <dl className="mt-3 space-y-1 text-sm">
        {drink.qualityScore != null && (
          <Row
            k={t("common.quality")}
            v={`${drink.qualityScore}/10 · ${t("rate.editorial")}`}
          />
        )}
        {drink.additiveStatus && (
          <Row
            k={t("common.additives")}
            v={`${lx(ADDITIVE_LABELS[drink.additiveStatus])}${drink.additiveDetail ? ` (${lx(drink.additiveDetail)})` : ""}`}
          />
        )}
        {drink.coffeeDetail && (
          <>
            <Row k={t("common.roast")} v={lx(COFFEE_ROAST_LABELS[drink.coffeeDetail.roast])} />
            {drink.coffeeDetail.process && (
              <Row
                k={t("common.process")}
                v={lx(COFFEE_PROCESS_LABELS[drink.coffeeDetail.process])}
              />
            )}
            {drink.coffeeDetail.species && (
              <Row
                k={t("common.species")}
                v={lx(COFFEE_SPECIES_LABELS[drink.coffeeDetail.species])}
              />
            )}
          </>
        )}
        <Row
          k={t("common.price")}
          v={`${drink.priceApprox ? t("common.approx") + " " : ""}${formatPrice(drink.priceEUR)}`}
        />
        {/* `shopHR` je urednička napomena, ne provjerena zaliha — bez potvrđene
            stranice proizvoda prikazuje se kao orijentir, ne kao tvrdnja. */}
        {availability && (
          <Row
            k={t("common.shop")}
            v={
              availability.verified
                ? availability.text
                : `${availability.text} · ${t("shops.indicative")}`
            }
          />
        )}
        {drink.serving?.best && <Row k={t("common.serving")} v={sv(drink.serving.best)} />}
      </dl>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {drink.flavorTags.map((tag) => (
          <Chip key={tag}>{flavorLabel(tag, lang)}</Chip>
        ))}
      </div>
      {drink.qualityScore != null && (
        <p className="mt-1 text-micro leading-snug text-dim/70">
          {t("rate.qualityWhat")}
        </p>
      )}
      {/* neutralna pravila kategorije — što je zakonski dopušteno dodati */}
      {drink.additiveStatus && ADDITIVE_RULES[drink.category] && (
        <p className="mt-1 text-micro leading-snug text-dim/70">
          {lx(ADDITIVE_RULES[drink.category])}
        </p>
      )}
      {lxStrict(drink.notes) && (
        <p className="mt-3 text-sm leading-relaxed text-papir/85">
          {lxStrict(drink.notes)}
        </p>
      )}
      {drink.cigarHint && lxStrict(drink.cigarHint) && (
        <p className="mt-3 text-sm leading-relaxed text-papir/85">
          <span className="mb-1 block text-[10px] uppercase tracking-widest text-dim">
            {t("common.cigarHint")}
          </span>
          {lxStrict(drink.cigarHint)}
        </p>
      )}
      {drink.lineup && drink.lineup.length > 0 && (
        <div className="mt-3 rounded-lg border border-dim/20 bg-cedar/60 p-3">
          <div className="text-[10px] uppercase tracking-widest text-dim">
            {t("common.lineup")}
          </div>
          <ul className="mt-1.5 flex flex-wrap gap-1.5">
            {drink.lineup.map((b) => (
              <li key={b}>
                <Chip>{b}</Chip>
              </li>
            ))}
          </ul>
        </div>
      )}
      <DrinkBuyLinks drink={drink} />
    </>
  );
}

function StockBadge({ view }: { view: StockView | null }) {
  const { t } = useI18n();
  if (!view) return null;
  const label = view.inStock ? t("stock.in") : t("stock.out");
  const tone = view.inStock ? "text-emerald-400/90" : "text-orange-400/90";
  return (
    <span className={`block text-[10px] leading-tight ${tone}`}>
      {label}
      {view.stale && (
        <span className="text-dim/70"> · {t("stock.stale")}</span>
      )}
    </span>
  );
}

// Kupnja boce po regiji: HR → Europa → SAD → svjetski cjenik, a na kraju izlaz
// na web kad nijedna polica nije potvrđena. Uz svaku regiju piše KOLIKO app
// zna o dostupnosti — potvrđena stranica boce, urednički orijentir ili ništa.
function DrinkBuyLinks({ drink }: { drink: Drink }) {
  const { t } = useI18n();
  const links = drinkShopLinks(drink);
  const shelf = drinkStockView(drink);
  if (links.length === 0) {
    const buy = drinkBuyLink(drink);
    return (
      <>
        <BuyLink href={buy.href} label={buy.label} />
        {shelf && (
          <p className="mt-1 text-center">
            <StockBadge view={shelf} />
          </p>
        )}
      </>
    );
  }
  const availability = drinkRegionAvailability(drink);
  const ref = links.filter((l) => l.scope === "REF");
  const web = links.filter((l) => l.scope === "WEB");
  const KIND_LABEL = {
    product: t("shops.direct"),
    search: t("shops.search"),
    browse: t("shops.browse"),
    ref: t("price.check"),
    web: t("shops.webSearch"),
  } as const;
  const buttons = (items: typeof links) => (
    <div className="grid grid-cols-2 gap-2">
      {items.map((l) => {
        const linkShelf =
          l.kind === "product" ? drinkStockView(drink) : null;
        return (
          <a
            key={`${l.scope}-${l.shopId}`}
            href={l.url}
            target="_blank"
            rel="noreferrer"
            className="rounded-lg border border-zlato/40 bg-zlato/10 px-2 py-2 text-center text-xs text-zlato-2 hover:bg-zlato/20"
          >
            {l.shop} <span className="text-[10px] text-dim">· {KIND_LABEL[l.kind]}</span> ↗
            <StockBadge view={linkShelf} />
          </a>
        );
      })}
    </div>
  );
  const group = (title: string, items: typeof links, status?: string) =>
    items.length === 0 && !status ? null : (
      <div className="mt-2">
        <div className="mb-1 flex flex-wrap items-baseline gap-x-2">
          <span className="text-[10px] uppercase tracking-widest text-dim/80">{title}</span>
          {status && <span className="text-micro text-dim/70">{status}</span>}
        </div>
        {items.length > 0 && buttons(items)}
      </div>
    );
  const statusText = (r: (typeof DRINK_REGIONS)[number]) => {
    const s = availability[r];
    if (s === "confirmed") return t("avail.confirmed");
    if (s === "viaHR") return t("avail.euViaHr");
    if (s === "listed") return t("avail.listed");
    return t("avail.unknown");
  };
  return (
    <div className="mt-3">
      <div className="mb-1 text-micro uppercase tracking-widest text-dim">{t("common.buy")}</div>
      {DRINK_REGIONS.map((r) => (
        <div key={r}>
          {group(
            t(`market.${r}` as Parameters<typeof t>[0]),
            links.filter((l) => l.scope === r),
            statusText(r),
          )}
        </div>
      ))}
      {group(t("shops.priceRef"), ref)}
      {group(t("shops.notOnShelves"), web)}
      {!links.some((l) => l.kind === "product") && (
        <p className="mt-1.5 text-micro leading-snug text-dim/70">{t("shops.drinkNoDirect")}</p>
      )}
    </div>
  );
}

// "Gdje kupiti" — direktan link ili fallback na pretragu
function BuyLink({ href, label }: { href: string; label: "buy" | "search" }) {
  const { t } = useI18n();
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="mt-3 block w-full rounded-lg border border-zlato/40 bg-zlato/10 py-2.5 text-center font-display text-sm uppercase tracking-widest text-zlato-2 hover:bg-zlato/20"
    >
      {label === "buy" ? t("common.buy") : t("common.searchOnline")} ↗
    </a>
  );
}

const STALE_DAYS = 90;

/**
 * Mala bilješka ispod gumba za kupnju: kad je cijena preuzeta i je li stara.
 * Ne prikazuje se kad fetchedAt nedostaje — tada ostaje genericka napomena.
 */
function CigarPriceNote({ cigar }: { cigar: Cigar }) {
  const { t, lang } = useI18n();
  const fetchedAt = cigarLatestFetchedAt(cigar);
  if (!fetchedAt) {
    return (
      <p className="mt-1.5 text-micro leading-snug text-dim/60">{t("price.marketNote")}</p>
    );
  }
  const fetchedDate = new Date(fetchedAt);
  const ageMs = Date.now() - fetchedDate.getTime();
  const ageDays = ageMs / (1000 * 60 * 60 * 24);
  const isStale = ageDays > STALE_DAYS;
  const localDate = fetchedDate.toLocaleDateString(lang === "hr" ? "hr-HR" : "en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
  const snapshotText = t("price.snapshotNote").replace("{date}", localDate);
  return (
    <div className="mt-1.5 space-y-0.5">
      <p className="text-micro leading-snug text-dim/60">{snapshotText}</p>
      {isStale && (
        <p className="text-micro leading-snug text-orange-400/80">⚠ {t("price.staleNote")}</p>
      )}
    </div>
  );
}

// Kupnja po regiji — prikazuje SVE regije gdje je cigara dostupna (HR uz EU/USA,
// da HR link ne bude skriven), svaka trgovina kao ravnopravan gumb s cijenom.
function CigarBuyLinks({ cigar }: { cigar: Cigar }) {
  const { t } = useI18n();
  const links = cigarShopLinks(cigar);
  const regions = REGIONS.filter((r) => links.some((l) => l.region === r));
  if (regions.length === 0) return null;
  return (
    <div className="mt-3">
      <div className="mb-1 text-micro uppercase tracking-widest text-dim">
        {t("common.buyIn")}
      </div>
      <div className="space-y-2">
        {regions.map((r) => (
          <div key={r}>
            <div className="mb-1 text-[10px] uppercase tracking-widest text-dim/80">
              {t(`market.${r}` as Parameters<typeof t>[0])}
            </div>
            <div className="grid grid-cols-2 gap-2">
              {links
                .filter((l) => l.region === r)
                .map((l) => {
                  const { price: priceNum, approx } = cigarShopLinkPrice(cigar, l);
                  const price =
                    priceNum != null
                      ? `${approx ? "~" : ""}${formatEur(priceNum)}`
                      : null;
                  const linkShelf = cigarLinkStockView(cigar, l.url, l.kind);
                  return (
                    <a
                      key={l.shop}
                      href={l.url}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-lg border border-zlato/40 bg-zlato/10 px-2 py-2 text-center text-xs text-zlato-2 hover:bg-zlato/20"
                    >
                      {l.shop}{" "}
                      {price ? (
                        <span className="text-zlato-2">· {price}</span>
                      ) : (
                        <span className="text-[10px] text-dim">
                          ·{" "}
                          {l.kind === "product"
                            ? t("shops.direct")
                            : l.kind === "line"
                              ? t("shops.linePage")
                              : l.kind === "walkin"
                                ? t("shops.walkIn")
                                : t("shops.search")}
                        </span>
                      )}{" "}
                      ↗
                      <StockBadge view={linkShelf} />
                    </a>
                  );
                })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex gap-3">
      <dt className="w-24 shrink-0 text-dim">{k}</dt>
      <dd className="text-papir/90">{v}</dd>
    </div>
  );
}

/**
 * Zaliha te cigare po humidorima. Prikazuje se samo za cigare — pića nemaju
 * humidor. Bez ijednog humidora nudi da se prvi otvori odmah odavde.
 *
 * Brojka uz +/− je zaliha BAŠ ove vitole (ključ `cig-x@robusto`), jer se po
 * tom ključu troši i zapis večeri. Ispod stoji rastav cijele linije, pa se
 * vidi zašto Robusto stoji na 0 dok u kutiji ima Toro i Figurado — ranije je
 * tu bila samo nula bez objašnjenja.
 */
function HumidorControls({ cigar, itemId }: { cigar: Cigar; itemId: string }) {
  const { t } = useI18n();
  const { humidors, stock, activeId } = useHumidors();
  const active = humidors.find((h) => h.id === activeId) ?? humidors[0];
  // skidanje zadnje ovdje nudi listu želja, kao i u humidoru i u zapisu večeri
  const [lastCigar, setLastCigar] = useState(false);
  // multi-vitola linija otvorena bez odabrane veličine — pitaj koja ide u kutiju
  const [pick, setPick] = useState(false);

  // `cigar` je ovdje već sužen na odabranu vitolu (applyVitola briše ostale),
  // pa imena sestrinskih vitola i izbornik traže cijelu liniju iz kataloga.
  const { cigarId } = parseCigarItemId(itemId);
  const line = resolveCigarId(cigarId) ?? cigar;
  const needsVitola = stockNeedsVitola(line, itemId);
  // paket (sampler) nije komad zalihe nego pet cigara — vidi lib/samplerStock
  const samplerPieces = isSampler(cigar) ? samplerPieceCount(cigar) : 0;
  const total = stock
    .filter((s) => s.itemId === itemId)
    .reduce((sum, s) => sum + s.count, 0);

  if (humidors.length === 0) {
    return (
      <>
        <button
          type="button"
          onClick={() => {
            if (needsVitola) {
              setPick(true);
              return;
            }
            const created = addHumidor(t("hum.defaultName"));
            // paket ide razložen: na stanje idu njegove vitole, ne kutija
            if (samplerPieces > 0 && unpackSamplerIntoStock(created.id, cigar) > 0) {
              return;
            }
            adjustStock(created.id, itemId, 1);
            claimOwnedForStock(itemId);
          }}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          + {samplerPieces > 0 ? t("hum.samplerUnpack") : t("hum.addToHumidor")}
        </button>
        {pick && (
          <VitolaPicker
            cigar={line}
            onPick={(vitola) => {
              const created = addHumidor(t("hum.defaultName"));
              const target = vitolaStockId(line, vitola);
              adjustStock(created.id, target, 1);
              claimOwnedForStock(target);
              setPick(false);
            }}
            onBack={() => setPick(false)}
          />
        )}
      </>
    );
  }

  const inActive = active
    ? (stock.find((s) => s.humidorId === active.id && s.itemId === itemId)?.count ?? 0)
    : 0;

  // rastav linije u aktivnom humidoru: koja je vitola stvarno na stanju
  const lineRows = active
    ? stock
        .filter(
          (s) =>
            s.humidorId === active.id &&
            parseCigarItemId(s.itemId).cigarId === cigarId,
        )
        .map((s) => ({
          itemId: s.itemId,
          count: s.count,
          name: stockVitolaName(line, s.itemId) ?? t("hum.vitolaMissing"),
        }))
        .sort((a, b) => a.name.localeCompare(b.name))
    : [];
  const lineTotal = lineRows.reduce((sum, r) => sum + r.count, 0);

  return (
    <div className="mt-4 rounded-lg border border-dim/20 bg-cedar/60 p-3">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-micro uppercase tracking-widest text-dim">
          {t("hum.addToHumidor")}
        </span>
        {total > 0 && (
          <span className="text-micro text-dim">
            {t("hum.inHumidor")}: {total}
          </span>
        )}
      </div>

      {humidors.length > 1 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {humidors.map((h) => (
            <Chip
              key={h.id}
              active={active?.id === h.id}
              onClick={() => setActiveHumidor(h.id)}
            >
              {h.name}
            </Chip>
          ))}
        </div>
      )}

      {/* paket: jedan gumb koji ga razloži na police, bez brojača komada */}
      {active && samplerPieces > 0 && (
        <div className="mt-2">
          <p className="text-micro leading-snug text-dim">{t("hum.samplerHint")}</p>
          <button
            type="button"
            onClick={() => unpackSamplerIntoStock(active.id, cigar)}
            className="mt-1.5 w-full rounded-lg border border-zlato/40 py-2 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
          >
            {t("hum.samplerUnpack")} · {samplerPieces} {t("hum.cigarsCount")}
          </button>
        </div>
      )}

      {active && !needsVitola && samplerPieces === 0 && (
        <div className="mt-2 flex items-center justify-between gap-3">
          <span className="min-w-0 truncate text-sm text-papir/90">
            {active.name}
            <span className="ml-1.5 text-micro text-dim">
              {stockVitolaName(line, itemId) ?? ""}
            </span>
          </span>
          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              aria-label="−1"
              onClick={() => {
                if (inActive <= 0) return;
                adjustStock(active.id, itemId, -1);
                // zaliha na nuli gasi „Imam” — popis kolekcije prati stvarnost
                releaseOwnedIfEmpty(itemId);
                if (shouldOfferWishlist(itemId)) setLastCigar(true);
              }}
              className="h-8 w-8 rounded-lg border border-dim/30 font-display text-base text-dim hover:border-zlato/50 hover:text-papir"
            >
              −
            </button>
            <span className="min-w-[2ch] text-center font-display text-lg text-zlato-2">
              {inActive}
            </span>
            <button
              type="button"
              aria-label="+1"
              onClick={() => {
                adjustStock(active.id, itemId, 1);
                claimOwnedForStock(itemId);
              }}
              className="h-8 w-8 rounded-lg border border-dim/30 font-display text-base text-dim hover:border-zlato/50 hover:text-papir"
            >
              +
            </button>
          </div>
        </div>
      )}

      {/* linija bez odabrane veličine: humidor prima vitolu, ne liniju */}
      {active && needsVitola && samplerPieces === 0 && (
        <div className="mt-2">
          <p className="text-micro leading-snug text-dim">{t("hum.vitolaMissingHint")}</p>
          <button
            type="button"
            onClick={() => setPick(true)}
            className="mt-1.5 rounded-md border border-zlato/40 px-2.5 py-1.5 text-micro uppercase tracking-widest text-zlato hover:bg-zlato/10"
          >
            + {t("hum.addVitola")}
          </button>
        </div>
      )}

      {/* rastav linije: zašto ova vitola stoji na nuli, a kutija nije prazna */}
      {lineTotal > 0 && (
        <div className="mt-2 border-t border-dim/15 pt-2">
          <div className="text-micro uppercase tracking-widest text-dim">
            {t("hum.stockByVitola")}
          </div>
          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1">
            {lineRows.map((row) => (
              <span
                key={row.itemId}
                className={`text-xs ${
                  row.itemId === itemId ? "text-zlato-2" : "text-dim"
                }`}
              >
                {row.name} <span className="font-display">{row.count}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {pick && (
        <VitolaPicker
          cigar={line}
          onPick={(vitola) => {
            if (active) {
              const target = vitolaStockId(line, vitola);
              adjustStock(active.id, target, 1);
              claimOwnedForStock(target);
            }
            setPick(false);
          }}
          onBack={() => setPick(false)}
        />
      )}

      {lastCigar && (
        <LastCigarPrompt itemId={itemId} onDone={() => setLastCigar(false)} />
      )}
    </div>
  );
}
