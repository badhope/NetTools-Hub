import { describe, it, expect } from "vitest";
import { formatNumber } from "@/lib/utils";

describe("formatNumber", () => {
  it("formats small numbers without abbreviation", () => {
    expect(formatNumber(0)).toBe("0");
    expect(formatNumber(1)).toBe("1");
    expect(formatNumber(999)).toBe("999");
  });

  it("formats thousands with K suffix", () => {
    expect(formatNumber(1000)).toBe("1K");
    expect(formatNumber(1500)).toBe("1.5K");
    expect(formatNumber(9999)).toBe("10K");
    expect(formatNumber(10000)).toBe("10K");
  });

  it("formats millions with M suffix", () => {
    expect(formatNumber(1000000)).toBe("1M");
    expect(formatNumber(1500000)).toBe("1.5M");
    expect(formatNumber(9999999)).toBe("10M");
  });

  it("handles undefined and null", () => {
    expect(formatNumber(undefined as any)).toBe("NaN");
    expect(formatNumber(null as any)).toBe("0");
  });

  it("handles negative numbers", () => {
    expect(formatNumber(-1000)).toBe("-1K");
  });

  it("handles decimal numbers", () => {
    expect(formatNumber(1234.56)).toBe("1.2K");
  });
});
