import { beforeEach, describe, expect, it, vi } from "vitest";

function installMemoryStorage() {
  const store = new Map<string, string>();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => {
        store.set(k, String(v));
      },
      removeItem: (k: string) => {
        store.delete(k);
      },
      clear: () => store.clear(),
    },
  });
}

describe("ocrPack", () => {
  beforeEach(() => {
    installMemoryStorage();
    vi.resetModules();
  });

  it("pocinje kao not_installed", async () => {
    const { getOcrPackStatus, isOcrPackReady } = await import("./ocrPack");
    expect(getOcrPackStatus()).toBe("not_installed");
    expect(isOcrPackReady()).toBe(false);
  });

  it("uninstall vraca na not_installed", async () => {
    localStorage.setItem(
      "cigar-pairing-ocr-pack-v1",
      JSON.stringify({ status: "ready", readyAt: "2026-08-01T00:00:00.000Z" }),
    );
    const { uninstallOcrPack, getOcrPackStatus } = await import("./ocrPack");
    uninstallOcrPack();
    expect(getOcrPackStatus()).toBe("not_installed");
  });
});
