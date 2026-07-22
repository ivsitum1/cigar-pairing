import { useEffect, useState } from "react";
import type { Cigar, Drink } from "../types";
import { useI18n, STYLE_LABELS, ADDITIVE_LABELS, ADDITIVE_RULES } from "../i18n";
import { brandInfo, cigarShopLinks, cigarPriceForMarket, formatPrice } from "../data";
import { REGIONS } from "../data/shops";
import { drinkBuyLink } from "../lib/drinkBuyLink";
import { vitolaBlurb } from "../lib/vitolaInfo";
import { resolveSamplerCigar } from "../lib/samplerLink";
import { Chip, Meter } from "./ui";
import { BackButton } from "./BackButton";
import {
  getItemState,
  updateItem,
  useCollection,
} from "../store/collection";

type Item = { kind: "cigar"; item: Cigar } | { kind: "drink"; item: Drink };

export function DetailSheet({
  target,
  onClose,
  onOpenBrand,
  onPair,
}: {
  target: Item | null;
  onClose: () => void;
  onOpenBrand?: (brand: string) => void;
  onPair?: (target: Item) => void;
}) {
  const { t } = useI18n();
  useCollection();
  // interni stog: navigacija unutar kartice (npr. sampler → pojedina cigara)
  const [stack, setStack] = useState<Item[]>([]);
  useEffect(() => {
    setStack([]);
  }, [target?.item.id]);
  const active = stack.length ? stack[stack.length - 1] : target;
  const id = active?.item.id;
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

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onClose}
    >
      <div
        className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-dim/40 sm:hidden" />

        <div className="mb-3">
          <BackButton onClick={goBack}>{t("common.back")}</BackButton>
        </div>

        {active.kind === "cigar" ? (
          <CigarDetails
            cigar={active.item}
            onOpenBrand={onOpenBrand}
            onOpenCigar={pushCigar}
          />
        ) : (
          <DrinkDetails drink={active.item} />
        )}

        <div className="band-rule my-4" />

        {/* kolekcija kontrole */}
        <div className="flex flex-wrap items-center gap-2">
          <Chip
            active={state.owned}
            onClick={() =>
              // kupljeno -> makni s liste zelja; skidanje "Imam" ne dira listu
              updateItem(
                id,
                state.owned ? { owned: false } : { owned: true, wishlist: false },
              )
            }
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
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          onBlur={saveNote}
          placeholder={t("coll.notePlaceholder")}
          rows={2}
          className="mt-3 w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2 text-sm text-papir placeholder:text-dim/60 focus:border-zlato/60 focus:outline-none"
        />

        {onPair && (
          <button
            type="button"
            onClick={() => onPair(active)}
            className="mt-4 w-full rounded-lg border border-oxblood/50 bg-oxblood/15 py-2.5 font-display text-sm uppercase tracking-widest text-zlato-2 hover:bg-oxblood/25"
          >
            {active.kind === "cigar" ? t("cat.pairWithDrink") : t("cat.pairWithCigar")}
          </button>
        )}

        <button
          onClick={onClose}
          className="mt-4 w-full rounded-lg border border-zlato/40 py-2.5 font-display text-sm uppercase tracking-widest text-zlato hover:bg-zlato/10"
        >
          {t("common.close")}
        </button>
      </div>
    </div>
  );
}

function CigarDetails({
  cigar,
  onOpenBrand,
  onOpenCigar,
}: {
  cigar: Cigar;
  onOpenBrand?: (brand: string) => void;
  onOpenCigar?: (c: Cigar) => void;
}) {
  const { t, lx, cn, lang } = useI18n();
  const brand = brandInfo(cigar.brand);
  return (
    <>
      <div className="font-display text-xl text-papir">
        {onOpenBrand ? (
          <button
            onClick={() => onOpenBrand(cigar.brand)}
            className="underline decoration-zlato/40 underline-offset-2 hover:text-zlato-2"
          >
            {cigar.brand}
          </button>
        ) : (
          cigar.brand
        )}{" "}
        <span className="text-zlato-2">{cigar.line}</span>
      </div>
      <div className="mt-1 text-sm text-dim">
        {cn(cigar.country)} · {cigar.wrapper}
        {onOpenBrand && (
          <>
            {" · "}
            <button
              onClick={() => onOpenBrand(cigar.brand)}
              className="text-zlato hover:text-zlato-2"
            >
              {t("brand.viewAll")} →
            </button>
          </>
        )}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
        <Meter value={cigar.strength} label={t("common.strength")} accent="var(--color-oxblood)" />
        <Meter value={cigar.body} label={t("common.body")} />
      </div>

      {/* vitole s vremenom pusenja i cijenom */}
      <div className="mt-3">
        <div className="mb-1 text-micro uppercase tracking-widest text-dim">
          {t("common.vitolas")}
        </div>
        <div className="space-y-1">
          {cigar.vitolas.map((v) => {
            const blurb = vitolaBlurb(v.name, lang);
            // cijena+link te vitole: HR (humidor) ili prva regija iz njenih regionLinks
            const rl = v.regionLinks ?? {};
            const region = (["HR", "EU", "USA"] as const).find((r) => rl[r]?.priceEUR != null);
            const price = v.priceEUR ?? (region ? rl[region]!.priceEUR ?? null : null);
            const url = v.url ?? (region ? rl[region]!.url : null);
            const approx = v.priceEUR == null && region ? rl[region]!.priceApprox : false;
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
                          {approx ? "~" : ""}{price.toFixed(2)} € ↗
                        </a>
                      ) : (
                        <span className="ml-1.5 text-zlato-2">{approx ? "~" : ""}{price.toFixed(2)} €</span>
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
      <div className="mt-2 flex flex-wrap items-center gap-1.5">
        {cigar.flavoured && (
          <span className="rounded-full border border-lista/50 bg-lista/15 px-2 py-0.5 text-micro uppercase tracking-wide text-lista">
            ✿ {t("common.flavoured")}
          </span>
        )}
        {cigar.flavorTags.map((tag) => (
          <Chip key={tag}>{tag}</Chip>
        ))}
      </div>
      <p className="mt-3 text-sm leading-relaxed text-papir/85">
        {lx(cigar.notes)}
      </p>
      {/* poštene oznake izvora podataka */}
      {(cigar.profileEstimated || cigar.formatEstimated || cigar.strengthFromShop) && (
        <div className="mt-1.5 space-y-0.5">
          {cigar.profileEstimated && (
            <p className="text-micro leading-snug text-dim/70">≈ {t("common.estimatedProfile")}</p>
          )}
          {cigar.strengthFromShop && (
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
            {cigar.brand} · {cn(brand.country)} · {brand.founded}
          </div>
          <p className="mt-1 text-xs leading-relaxed text-papir/80">
            {lx(brand.blurb)}
          </p>
        </div>
      )}
    </>
  );
}

function DrinkDetails({ drink }: { drink: Drink }) {
  const { t, lx, sv, rgn } = useI18n();
  const style = STYLE_LABELS[drink.style];
  const buy = drinkBuyLink(drink);
  return (
    <>
      <div className="font-display text-xl text-papir">{drink.name}</div>
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
        <Row
          k={t("common.price")}
          v={`${drink.priceApprox ? t("common.approx") + " " : ""}${formatPrice(drink.priceEUR)}`}
        />
        {drink.shopHR && <Row k={t("common.shop")} v={drink.shopHR} />}
        {drink.serving?.best && <Row k={t("common.serving")} v={sv(drink.serving.best)} />}
      </dl>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {drink.flavorTags.map((tag) => (
          <Chip key={tag}>{tag}</Chip>
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
      {lx(drink.notes) && (
        <p className="mt-3 text-sm leading-relaxed text-papir/85">
          {lx(drink.notes)}
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
      <BuyLink href={buy.href} label={buy.label} />
    </>
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

// Kupnja po regiji — prikazuje SVE regije gdje je cigara dostupna (HR uz EU/USA,
// da HR link ne bude skriven), svaka trgovina kao ravnopravan gumb s cijenom.
function CigarBuyLinks({ cigar }: { cigar: Cigar }) {
  const { t } = useI18n();
  const links = cigarShopLinks(cigar);
  const hrPrice = cigarPriceForMarket(cigar, "HR").price;
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
                  const rl = cigar.regionLinks?.[r];
                  const priceNum =
                    rl && rl.shop === l.shop && rl.priceEUR != null
                      ? rl.priceEUR
                      : r === "HR" && l.exact
                        ? hrPrice
                        : null;
                  const approx = rl && rl.shop === l.shop ? rl.priceApprox : false;
                  const price =
                    priceNum != null
                      ? `${approx ? "~" : ""}${priceNum.toFixed(priceNum % 1 ? 2 : 0)} €`
                      : null;
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
                          · {l.exact ? t("shops.direct") : t("shops.search")}
                        </span>
                      )}{" "}
                      ↗
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
