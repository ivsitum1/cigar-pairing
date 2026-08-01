import { useI18n } from "../i18n";
import { legalAgeForMarket } from "../lib/ageGate";
import { useMarket } from "../store/market";

// Podnožje: autorska prava, licenca glazbe (CC BY 3.0 — obavezna atribucija) i
// pravni disclaimeri (duhan, cijene, procjene podataka, zdravlje).
export function Footer() {
  const { t } = useI18n();
  // Dobna granica nije ista svugdje: SAD 21 (Tobacco 21 + alkohol), EU/HR 18.
  // Podnožje zna odabrano tržište, pa broj prati njega umjesto da tvrdi 18.
  const market = useMarket();
  const age = String(legalAgeForMarket(market));
  const withAge = (key: "footer.tobacco" | "footer.alcohol") =>
    t(key).replace(/\{age\}/g, age);
  return (
    <footer className="mt-10 border-t border-zlato/20 pt-4 text-micro leading-relaxed text-dim/80">
      <div className="band-rule mb-3" />
      <p className="text-dim">{t("footer.copyright")}</p>
      <p className="mt-1.5">
        {t("footer.music")}{" "}
        <a
          href="https://creativecommons.org/licenses/by/4.0/"
          target="_blank"
          rel="noreferrer"
          className="text-zlato/80 underline decoration-zlato/30 underline-offset-2 hover:text-zlato-2"
        >
          CC BY 4.0
        </a>
      </p>
      <p className="mt-1.5">{withAge("footer.tobacco")}</p>
      <p className="mt-1.5">{withAge("footer.alcohol")}</p>
      <p className="mt-1.5">{t("footer.prices")}</p>
      <p className="mt-1.5">{t("footer.data")}</p>
      <p className="mt-2 font-display uppercase tracking-widest text-dim">
        {t("footer.health")}
      </p>
    </footer>
  );
}
