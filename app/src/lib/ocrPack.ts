/**
 * Opcionalni offline OCR pack — korisnik mora eksplicitno preuzeti.
 * Modeli (Paddle ONNX / Tesseract) dolaze lazy pri warmupu; preference živi u localStorage.
 */
import { useSyncExternalStore } from "react";

export type OcrPackStatus = "not_installed" | "downloading" | "ready" | "failed";

const KEY = "cigar-pairing-ocr-pack-v1";

interface Stored {
  status: "ready" | "not_installed" | "failed";
  /** ISO — kad je pack uspješno zagrijan. */
  readyAt?: string;
  lastError?: string;
}

type Snapshot = {
  status: OcrPackStatus;
  lastError: string | null;
  progress: string | null;
};

const listeners = new Set<() => void>();
let ephemeral: { status: OcrPackStatus; progress: string | null; lastError: string | null } = {
  status: "not_installed",
  progress: null,
  lastError: null,
};
let warmed = false;

function readStored(): Stored {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { status: "not_installed" };
    const p = JSON.parse(raw) as Stored;
    if (p?.status === "ready" || p?.status === "failed" || p?.status === "not_installed") {
      return p;
    }
  } catch {
    /* ignore */
  }
  return { status: "not_installed" };
}

function writeStored(s: Stored) {
  // localStorage can throw in blocked/locked contexts (e.g. privacy modes).
  // UI should not crash the entire scan flow; we can treat pack state as "unknown".
  try {
    localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    /* ignore */
  }
}

function notify() {
  listeners.forEach((l) => l());
}

function snapshot(): Snapshot {
  if (ephemeral.status === "downloading") {
    return {
      status: "downloading",
      lastError: ephemeral.lastError,
      progress: ephemeral.progress,
    };
  }
  const s = readStored();
  return {
    status: s.status,
    lastError: s.lastError ?? null,
    progress: null,
  };
}

export function getOcrPackStatus(): OcrPackStatus {
  return snapshot().status;
}

export function isOcrPackReady(): boolean {
  return getOcrPackStatus() === "ready";
}

export function subscribeOcrPack(cb: () => void): () => void {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

export function useOcrPack(): Snapshot & {
  install: (onProgress?: (msg: string) => void) => Promise<boolean>;
  uninstall: () => void;
} {
  const snap = useSyncExternalStore(subscribeOcrPack, snapshot, snapshot);
  return {
    ...snap,
    install: installOcrPack,
    uninstall: uninstallOcrPack,
  };
}

/** Preuzmi/inizijaliziraj Paddle (+ lagani Tesseract warm). */
export async function installOcrPack(
  onProgress?: (msg: string) => void,
): Promise<boolean> {
  ephemeral = { status: "downloading", progress: "paddle", lastError: null };
  notify();
  onProgress?.("paddle");
  try {
    const { warmOcrEngines, resetOcrEngines } = await import("./ocrEngine");
    resetOcrEngines();
    const ok = await warmOcrEngines((phase: "paddle" | "tesseract") => {
      ephemeral = { ...ephemeral, progress: phase };
      notify();
      onProgress?.(phase);
    });
    if (!ok) {
      writeStored({ status: "failed", lastError: "warmup-failed" });
      ephemeral = { status: "failed", progress: null, lastError: "warmup-failed" };
      notify();
      return false;
    }
    warmed = true;
    writeStored({ status: "ready", readyAt: new Date().toISOString() });
    ephemeral = { status: "ready", progress: null, lastError: null };
    notify();
    return true;
  } catch (e) {
    const msg = e instanceof Error ? e.message : "error";
    writeStored({ status: "failed", lastError: msg });
    ephemeral = { status: "failed", progress: null, lastError: msg };
    notify();
    return false;
  }
}

/** Isključi pack (sljedeći scan traži ponovni download). */
export function uninstallOcrPack() {
  writeStored({ status: "not_installed" });
  ephemeral = { status: "not_installed", progress: null, lastError: null };
  warmed = false;
  void import("./ocrEngine").then((m) => m.resetOcrEngines());
  notify();
}

/** Ako je preference ready a engine još nije u memoriji — zagrij prije scana. */
export async function ensureOcrPackWarm(): Promise<boolean> {
  if (getOcrPackStatus() !== "ready") return false;
  if (warmed) return true;
  const { warmOcrEngines } = await import("./ocrEngine");
  const ok = await warmOcrEngines();
  warmed = ok;
  if (!ok) {
    writeStored({ status: "failed", lastError: "rewarm-failed" });
    notify();
  }
  return ok;
}
