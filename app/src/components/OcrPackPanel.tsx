/** Panel za preuzimanje / brisanje offline OCR packa. */
import { useI18n } from "../i18n";
import { useOcrPack } from "../lib/ocrPack";

export function OcrPackPanel() {
  const { t } = useI18n();
  const pack = useOcrPack();

  return (
    <div className="mt-3 rounded-xl border border-zlato/25 bg-cedar/40 px-3 py-3 text-sm">
      <p className="font-display text-xs uppercase tracking-wider text-zlato-2">
        {t("ocr.packTitle")}
      </p>
      <p className="mt-1 text-xs leading-relaxed text-dim">{t("ocr.packHint")}</p>
      <p className="mt-2 text-xs text-papir/80">
        {pack.status === "ready"
          ? t("ocr.packStatusReady")
          : pack.status === "downloading"
            ? t("ocr.packStatusDownloading")
            : pack.status === "failed"
              ? t("ocr.packStatusFailed")
              : t("ocr.packStatusOff")}
      </p>
      <div className="mt-2 flex flex-wrap gap-2">
        {pack.status !== "ready" ? (
          <button
            type="button"
            disabled={pack.status === "downloading"}
            onClick={() => void pack.install()}
            className="rounded-lg border border-zlato/40 bg-zlato/15 px-3 py-1.5 text-xs text-zlato-2 hover:bg-zlato/25 disabled:opacity-50"
          >
            {t("ocr.packInstall")}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => pack.uninstall()}
            className="rounded-lg border border-dim/40 px-3 py-1.5 text-xs text-dim hover:border-oxblood/50 hover:text-papir"
          >
            {t("ocr.packUninstall")}
          </button>
        )}
      </div>
    </div>
  );
}
