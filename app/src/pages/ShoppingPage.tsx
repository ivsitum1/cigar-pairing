import { SHOPPING } from "../data";
import { useI18n } from "../i18n";
import { SectionTitle } from "../components/ui";

export function ShoppingPage() {
  const { t, lx } = useI18n();

  const tierGroups = ["S", "A", "B", "C"].map((tier) => ({
    tier,
    rows: SHOPPING.tiers.filter((x) => x.tier === tier),
  }));

  return (
    <div className="pb-4">
      <SectionTitle>{t("shop.recs")}</SectionTitle>
      <div className="grid gap-2 sm:grid-cols-2">
        {SHOPPING.recommendations.map((r, i) => (
          <div key={i} className="rounded-xl border border-zlato/25 bg-cedar p-3">
            <div className="text-[10px] uppercase tracking-widest text-dim">{lx(r.title)}</div>
            <div className="mt-1 font-display text-[15px] text-zlato-2">{r.pick}</div>
            <div className="mt-0.5 text-xs text-dim">{lx(r.detail)}</div>
          </div>
        ))}
      </div>

      <SectionTitle>{t("shop.tiers")}</SectionTitle>
      <div className="space-y-4">
        {tierGroups.map(({ tier, rows }) => (
          <div key={tier}>
            <div className="mb-1.5 font-display text-sm tracking-widest text-zlato">
              TIER {tier}
            </div>
            <div className="space-y-1.5">
              {rows.map((row, i) => (
                <div
                  key={i}
                  className={`flex items-start gap-3 rounded-lg border p-2.5 ${
                    row.owned ? "border-lista/40 bg-lista/10" : "border-dim/15 bg-cedar"
                  }`}
                >
                  <span
                    className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-xs ${
                      row.owned ? "border-lista text-lista" : "border-dim/40 text-transparent"
                    }`}
                  >
                    ✓
                  </span>
                  <div className="min-w-0">
                    <div className="text-sm text-papir">
                      <span className="text-dim">{row.styleTarget}:</span>{" "}
                      {row.bottleTarget}
                    </div>
                    <div className="mt-0.5 text-xs text-dim">
                      {row.profile}
                      {row.priceSource && ` · ${row.priceSource}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-xl border border-zlato/25 bg-zlato/10 p-3 text-sm text-zlato-2">
        <span className="font-display text-xs uppercase tracking-widest">
          {t("shop.miniPath")}
        </span>
        <div className="mt-1 text-papir/85">{SHOPPING.miniPath.join(" · ")}</div>
      </div>

      <SectionTitle>{t("shop.shops")}</SectionTitle>
      <div className="grid gap-2 sm:grid-cols-2">
        {SHOPPING.shops.map((s) => (
          <div key={s.name} className="rounded-xl border border-dim/15 bg-cedar p-3">
            <div className="font-display text-[15px] text-papir">{s.name}</div>
            <div className="text-xs text-dim">{s.location}</div>
            <div className="mt-1 text-xs leading-relaxed text-dim/90">{lx(s.note)}</div>
          </div>
        ))}
      </div>

      <p className="mt-4 text-xs leading-relaxed text-dim/80">⚖ {t("shop.legalNote")}</p>
    </div>
  );
}
