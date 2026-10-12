import { describe, it, expect } from "vitest";
import { localizeShopHR } from "./index";

describe("localizeShopHR", () => {
  it("HR ostaje kako jest", () => {
    expect(localizeShopHR("svugdje", "hr")).toBe("svugdje");
    expect(localizeShopHR("allez.hr", "hr")).toBe("allez.hr");
  });

  it("EN prevodi uredničke fraze, hostove ostavlja", () => {
    expect(localizeShopHR("svugdje", "en")).toBe("widely available");
    expect(localizeShopHR("allez.hr", "en")).toBe("allez.hr");
    expect(localizeShopHR("allez.hr (rijetko)", "en")).toBe("allez.hr (scarce)");
  });
});
