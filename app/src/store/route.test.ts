import { describe, expect, it } from "vitest";
import { parseHash, routeToHash } from "./route";

describe("hash route helpers", () => {
  it("round-trips the HR guide club subroute", () => {
    expect(parseHash("#/club/hr-guide")).toEqual({ page: "club", club: "hr-guide" });
    expect(routeToHash({ page: "club", club: "hr-guide" })).toBe("#/club/hr-guide");
  });
});
