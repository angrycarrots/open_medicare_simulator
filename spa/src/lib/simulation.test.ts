import { describe, expect, it } from "vitest";
import { createPlanG, createPlanHDG, createPlanN, DEFAULT_SIMULATION_PARAMETERS, fullSimulatorPlan, normalizePlanCostSettings, withoutPartD, withPlanCostSettings } from "./plans";
import { annualCost, percentile, runSimulation, SeededRandomSource, validatePlan } from "./simulation";

describe("Medicare plan cost engine", () => {
  it("uses the configured plan and Medicare deductible defaults", () => {
    const planG = createPlanG();
    const planHDG = createPlanHDG();
    const planN = createPlanN();

    expect(DEFAULT_SIMULATION_PARAMETERS.partADeductible2026).toBe(1736);
    expect(DEFAULT_SIMULATION_PARAMETERS.partBDeductible2026).toBe(283);
    expect([planG.premium2026, planG.planDeductible2026]).toEqual([157, 0]);
    expect([planHDG.premium2026, planHDG.planDeductible2026]).toEqual([70, 2875]);
    expect([planN.premium2026, planN.planDeductible2026]).toEqual([122, 0]);
    expect([planG.specialistCopay2026, planHDG.specialistCopay2026, planN.specialistCopay2026]).toEqual([0, 30, 20]);
    expect([planG.specialistVisitsPerYear, planHDG.specialistVisitsPerYear, planN.specialistVisitsPerYear]).toEqual([4, 4, 4]);
    expect([planG.specialistCopayGrowthRate, planHDG.specialistCopayGrowthRate, planN.specialistCopayGrowthRate]).toEqual([0.06, 0.06, 0.06]);
  });

  it("repairs missing growth rates in previously saved plan settings", () => {
    const settings = normalizePlanCostSettings({
      "plan-g": { monthlyPremium: 165, planDeductible: 0, officeVisitCopay: 0 },
    });

    expect(settings["plan-g"].monthlyPremium).toBe(165);
    expect(settings["plan-g"].planPremiumGrowthRate).toBe(0.07);
    expect(settings["plan-g"].planDeductibleGrowthRate).toBe(0.06);
    expect(settings["plan-g"].officeVisitsPerYear).toBe(4);
    expect(settings["plan-g"].officeVisitCopayGrowthRate).toBe(0.06);
    expect(settings["plan-hdg"].planPremiumGrowthRate).toBe(0.07);
    expect(settings["plan-n"].planDeductibleGrowthRate).toBe(0.06);
  });

  it("matches the base Plan G healthy and full-utilization costs", () => {
    const plan = createPlanG({ startYear: 2026 });
    expect(annualCost(plan, 0, false)).toBe(2472);
    expect(annualCost(plan, 0, true)).toBe(2755);
  });

  it("applies editable plan costs to the simulation", () => {
    const plan = withPlanCostSettings(createPlanG({ startYear: 2026 }), {
      monthlyPremium: 175,
      planDeductible: 300,
      officeVisitCopay: 25,
      officeVisitsPerYear: 4,
      officeVisitCopayGrowthRate: 0.06,
      planPremiumGrowthRate: 0.08,
      planDeductibleGrowthRate: 0.05,
    });
    expect(plan.premium2026).toBe(175);
    expect(plan.planDeductible2026).toBe(300);
    expect(plan.specialistCopay2026).toBe(25);
    expect(plan.premiumGrowthRate).toBe(0.08);
    expect(plan.planDeductibleGrowthRate).toBe(0.05);
    expect(annualCost(plan, 0, false)).toBe(2788);
    expect(annualCost(plan, 0, true)).toBe(3371);
    expect(annualCost(withoutPartD(plan), 1, false)).toBeCloseTo(2374);
    expect(annualCost(withoutPartD(plan), 1, true)).toBeCloseTo(2988.98);
  });

  it("includes Plan N specialist copays in healthy and full-utilization costs", () => {
    const plan = createPlanN({ startYear: 2026 });
    expect(annualCost(plan, 0, false)).toBe(2132);
    expect(annualCost(plan, 0, true)).toBe(2415);
  });

  it("can exclude Part D costs from single-plan and comparison scenarios", () => {
    const plan = withoutPartD(createPlanG({ startYear: 2026 }));
    expect(plan.partDPremium2026).toBe(0);
    expect(plan.partDPremiumGrowthRate).toBe(0);
    expect(annualCost(plan, 0, false)).toBe(1884);
    expect(annualCost(plan, 0, true)).toBe(2167);
    expect(() => validatePlan(plan)).not.toThrow();
  });

  it("includes the Plan A deductible in full-utilization Full Simulator costs", () => {
    const plan = fullSimulatorPlan({ ...DEFAULT_SIMULATION_PARAMETERS, startYear: 2026 });
    expect(plan.partADeductible2026).toBe(1736);
    expect(annualCost(plan, 0, false)).toBe(2472);
    expect(annualCost(plan, 0, true)).toBe(4491);
    expect(annualCost(plan, 1, true) - annualCost(plan, 1, false)).toBeCloseTo(2019 * 1.06);
  });

  it("requires a complete specialist-cost configuration", () => {
    const plan = createPlanG({ specialistVisitsPerYear: 4, specialistCopay2026: undefined });
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
