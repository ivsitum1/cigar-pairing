// Traka iznad donje navigacije: upozorenje kad localStorage zapis ne uspije.
//
// Trake "nova verzija" više nema: service worker je u `autoUpdate` načinu, pa
// se objavljena promjena preuzme i primijeni sama. Ovdje uz to stoji i provjera
// koja to čini pouzdanim — sam SW provjerava novu verziju samo pri učitavanju
// stranice, a instalirani PWA se danima ne učitava iznova, pa bi novost čekala
// u redu neviđena.
import { useEffect } from "react";
import { useRegisterSW } from "virtual:pwa-register/react";
import { useI18n } from "../i18n";
import { useStorageHealth } from "../store/collection";
import { useFavoritesStorageHealth } from "../store/favorites";
import { useHumidorStorageHealth } from "../store/humidor";
import { useMarketStorageHealth } from "../store/market";

/** Redovita provjera nove verzije: pola sata, plus svaki povratak u aplikaciju. */
const CHECK_EVERY_MS = 30 * 60 * 1000;

export function SystemBanners() {
  const { t } = useI18n();
  // Svaki store pise u svoj kljuc i svaki moze pasti zasebno: kvota se puni
  // zajednicki, pa je humidor cesto prvi koji odbije zapis dok je kolekcija
  // jos prosla. Traka je pratila samo kolekciju, pa je upozorenje "izvezi
  // sigurnosnu kopiju" izostajalo bas kad su podaci o zalihama u opasnosti.
  //
  // Sve cetiri kuke se zovu bezuvjetno i tek se rezultati spajaju: `a() || b()`
  // preskace b() cim je a() istinit, a to je uvjetni poziv kuke.
  const collectionFailed = useStorageHealth();
  const humidorFailed = useHumidorStorageHealth();
  const favoritesFailed = useFavoritesStorageHealth();
  const marketFailed = useMarketStorageHealth();
  const storageFailed =
    collectionFailed || humidorFailed || favoritesFailed || marketFailed;
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisteredSW(_url, registration) {
      if (!registration) return;
      const check = () => {
        if (document.visibilityState !== "visible") return;
        // mreža zna pasti — neuspjela provjera nije razlog za rušenje ničega
        registration.update().catch(() => {});
      };
      document.addEventListener("visibilitychange", check);
      window.addEventListener("focus", check);
      window.setInterval(check, CHECK_EVERY_MS);
    },
  });

  // sigurnosna mreža: ako verzija ipak ostane čekati, primijeni je i osvježi
  useEffect(() => {
    if (needRefresh) updateServiceWorker(true);
  }, [needRefresh, updateServiceWorker]);

  if (!storageFailed) return null;

  return (
    <div className="fixed inset-x-0 bottom-16 z-50 mx-auto max-w-2xl space-y-2 px-4 pb-2">
      <div className="rounded-lg border border-oxblood/60 bg-humidor/95 p-3 text-xs text-papir shadow-lg backdrop-blur">
        {t("sys.storageFail")}
      </div>
    </div>
  );
}
