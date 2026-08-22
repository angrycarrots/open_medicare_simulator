import { describe, expect, it } from "vitest";
import { createPlanG, createPlanN } from "./plans";
import { annualCost, percentile, runSimulation, SeededRandomSource, validatePlan } from "./simulation";

describe("Medicare plan cost engine", () => {
  it("matches the base Plan G healthy and full-utilization costs", () => {
    const plan = createPlanG({ startYear: 2026 });
    expect(annualCost(plan, 0, false)).toBe(2448);
    expect(annualCost(plan, 0, true)).toBe(2915);
  });

  it("includes Plan N specialist copays in healthy and full-utilization costs", () => {
    const plan = createPlanN({ startYear: 2026 });
    expect(annualCost(plan, 0, false)).toBe(2244);
    expect(annualCost(plan, 0, true)).toBe(2711);
  });

  it("requires a complete specialist-cost configuration", () => {
    const plan = createPlanG({ specialistVisitsPerYear: 4 });
    expect(() => validatePlan(plan)).toThrow("must be supplied together");
  });

  it("uses NumPy-compatible linear percentile interpolation", () => {
    expect(percentile([0, 10, 20, 30], 25)).toBe(7.5);
    expect(percentile([0, 10, 20, 30], 50)).toBe(15);
  });

  it("is reproducible when a seeded random source is used", () => {
    const request = { plan: createPlanG({ simulationYears: 4, percentSick: 0.25 }), numSimulations: 12 };
    const first = runSimulation(request, new SeededRandomSource(42));
    const second = runSimulation(request, new SeededRandomSource(42));
    expect(first.lifetimeCosts).toEqual(second.lifetimeCosts);
    expect(first.statistics.meanCosts).toEqual(second.statistics.meanCosts);
  });

  it("rejects out-of-range utilization probabilities", () => {
    expect(() => validatePlan(createPlanG({ percentSick: 1.1 }))).toThrow("between 0 and 1");
  });
});
