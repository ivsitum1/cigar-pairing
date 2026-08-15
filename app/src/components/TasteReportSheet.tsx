// „Pošalji dojmove” — sve ocjene iz ovog preglednika, spremne za repo.
import { useMemo, useState } from "react";
import { SheetShell } from "./SheetShell";
import { BackButton } from "./BackButton";
import { useI18n } from "../i18n";
import { cigarById } from "../data";
import { useTasteProfiles } from "../store/tasteProfile";
import { setTaster, useTaster } from "../store/taster";
import {
  buildTasteReport,
  githubIssueUrl,
  issueUrlTooLong,
  reportMarkdown,
} from "../lib/tasteReport";

export function TasteReportSheet({ onClose }: { onClose: () => void }) {
  const { t } = useI18n();
  const profiles = useTasteProfiles();
  const taster = useTaster();
  const [name, setName] = useState(taster);
  const [copied, setCopied] = useState(false);

  const report = useMemo(
    () => buildTasteReport(profiles, name, (id) => cigarById(id)),
    [profiles, name],
  );
  const url = useMemo(() => githubIssueUrl(report), [report]);
  const tooLong = issueUrlTooLong(url);
  const empty = report.reports.length === 0;

  const remember = () => {
    if (name.trim() !== taster) setTaster(name);
  };

  const copy = async () => {
    remember();
    const text = reportMarkdown(report);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // bez dopuštenja za međuspremnik ostaje dijeljenje
      await navigator.share?.({ text }).catch(() => {});
    }
  };

  return (
    <SheetShell
      onClose={onClose}
      label={t("report.title")}
      panelClassName="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl"
    >
      <div className="mb-3">
        <BackButton onClick={onClose}>{t("common.back")}</BackButton>
      </div>
      <h3 className="font-display text-lg text-papir">{t("report.title")}</h3>
      <p className="mt-1 text-sm leading-relaxed text-dim">{t("report.hint")}</p>

      <label className="mt-4 block text-xs uppercase tracking-widest text-dim">
        {t("report.who")}
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onBlur={remember}
          placeholder={t("report.whoPlaceholder")}
          className="mt-1 w-full rounded-lg border border-dim/30 bg-cedar px-3 py-2 text-sm text-papir placeholder:text-dim/60"
        />
      </label>

      <div className="mt-4 rounded-lg border border-dim/20 bg-cedar/60 p-3">
        <div className="text-micro uppercase tracking-widest text-dim">
          {t("report.count")}: {report.reports.length}
        </div>
        {empty ? (
          <p className="mt-2 text-sm leading-relaxed text-dim">{t("report.empty")}</p>
        ) : (
          <ul className="mt-2 space-y-1">
            {report.reports.slice(0, 12).map((r) => (
              <li key={r.cigarId} className="flex justify-between gap-3 text-xs text-papir/85">
                <span className="min-w-0 truncate">{r.label}</span>
                <span className="shrink-0 text-zlato-2">
                  {"◆".repeat(r.strength)} · {"◆".repeat(r.body)}
                </span>
              </li>
            ))}
            {report.reports.length > 12 && (
              <li className="text-micro text-dim">+{report.reports.length - 12}…</li>
            )}
          </ul>
        )}
      </div>

      <div className="mt-4 space-y-2">
        {!empty && !tooLong && (
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            onClick={remember}
            className="block rounded-lg border border-zlato bg-zlato/15 py-2.5 text-center font-display text-xs uppercase tracking-widest text-zlato-2"
          >
            {t("report.github")}
          </a>
        )}
        {!empty && tooLong && (
          <p className="text-micro leading-snug text-dim">{t("report.tooLong")}</p>
        )}
        <button
          type="button"
          onClick={copy}
          disabled={empty}
          className="w-full rounded-lg border border-dim/30 py-2.5 font-display text-xs uppercase tracking-widest text-dim disabled:opacity-40"
        >
          {copied ? t("report.copied") : t("report.copy")}
        </button>
      </div>

      <p className="mt-3 text-micro leading-snug text-dim/70">{t("report.privacy")}</p>
    </SheetShell>
  );
}
