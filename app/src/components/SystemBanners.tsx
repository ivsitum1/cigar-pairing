// Trake iznad donje navigacije: "nova verzija spremna" (service worker u
// prompt modu) i upozorenje kad localStorage zapis ne uspije.
import { useRegisterSW } from "virtual:pwa-register/react";
import { useI18n } from "../i18n";
import { useStorageHealth } from "../store/collection";

export function SystemBanners() {
  const { t } = useI18n();
  const storageFailed = useStorageHealth();
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW();

  if (!needRefresh && !storageFailed) return null;

  return (
    <div className="fixed inset-x-0 bottom-16 z-50 mx-auto max-w-2xl space-y-2 px-4 pb-2">
      {storageFailed && (
        <div className="rounded-lg border border-oxblood/60 bg-humidor/95 p-3 text-xs text-papir shadow-lg backdrop-blur">
          {t("sys.storageFail")}
        </div>
      )}
      {needRefresh && (
        <div className="flex items-center justify-between gap-3 rounded-lg border border-zlato/40 bg-humidor/95 p-3 text-xs text-papir shadow-lg backdrop-blur">
          <span>{t("sys.updateReady")}</span>
          <button
            onClick={() => updateServiceWorker(true)}
            className="shrink-0 rounded-md border border-zlato/60 px-3 py-1.5 font-display text-micro uppercase tracking-widest text-zlato hover:bg-zlato/10"
          >
            {t("sys.reload")}
          </button>
        </div>
      )}
    </div>
  );
}
