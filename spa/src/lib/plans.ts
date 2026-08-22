import type { PlanDefinition, SimulationParameters } from "../types";

const CURRENT_YEAR = new Date().getFullYear();

export const DEFAULT_SIMULATION_PARAMETERS: SimulationParameters = {
  medigapPremium2026: 155,
  medigapPremiumGrowthRate: 0.07,
  planDeductible2026: 257,
  planDeductibleGrowthRate: 0.06,
  partDPremium2026: 49,
  partDPremiumGrowthRate: 0.06,
  partBDeductible2026: 210,
  partBDeductibleGrowthRate: 0.06,
  percentSick: 0.2,
  simulationYears: 25,
  startYear: CURRENT_YEAR,
};

export function fullSimulatorPlan(parameters: SimulationParameters): PlanDefinition {
  return {
    id: "full-simulator",
    name: "Medicare/Medigap scenario",
    premium2026: parameters.medigapPremium2026,
    premiumGrowthRate: parameters.medigapPremiumGrowthRate,
    planDeductible2026: parameters.planDeductible2026,
    planDeductibleGrowthRate: parameters.planDeductibleGrowthRate,
    partDPremium2026: parameters.partDPremium2026,
    partDPremiumGrowthRate: parameters.partDPremiumGrowthRate,
    partBDeductible2026: parameters.partBDeductible2026,
    partBDeductibleGrowthRate: parameters.partBDeductibleGrowthRate,
    percentSick: parameters.percentSick,
    simulationYears: parameters.simulationYears,
    startYear: parameters.startYear,
  };
}

export function createPlanG(overrides: Partial<PlanDefinition> = {}): PlanDefinition {
  return {
    id: "plan-g",
    name: "Plan G",
    premium2026: 155,
    premiumGrowthRate: 0.07,
    planDeductible2026: 257,
    planDeductibleGrowthRate: 0.06,
    partDPremium2026: 49,
    partDPremiumGrowthRate: 0.06,
    partBDeductible2026: 210,
    partBDeductibleGrowthRate: 0.06,
    percentSick: 0.2,
    simulationYears: 25,
    startYear: CURRENT_YEAR,
    ...overrides,
  };
}

export function createPlanHDG(overrides: Partial<PlanDefinition> = {}): PlanDefinition {
  return {
    ...createPlanG(),
    id: "plan-hdg",
    name: "High Deductible Plan G",
    premium2026: 40,
    planDeductible2026: 2800,
    ...overrides,
  };
}

export function createPlanN(overrides: Partial<PlanDefinition> = {}): PlanDefinition {
  return {
    ...createPlanG(),
    id: "plan-n",
    name: "Plan N",
    premium2026: 118,
    specialistVisitsPerYear: 12,
    specialistCopay2026: 20,
    specialistCopayGrowthRate: 0.07,
    ...overrides,
  };
}

export function createCustomPlan(overrides: Partial<PlanDefinition> = {}): PlanDefinition {
  return {
    ...createPlanG(),
    id: "custom",
    name: "Custom plan",
    premium2026: 100,
    planDeductible2026: 1000,
    ...overrides,
  };
}

export const PREDEFINED_PLANS = {
  "plan-g": createPlanG,
  "plan-hdg": createPlanHDG,
  "plan-n": createPlanN,
} as const;
