import type { PlanDefinition, SimulationParameters } from "../types";

const CURRENT_YEAR = new Date().getFullYear();

export type PredefinedPlanChoice = "plan-g" | "plan-hdg" | "plan-n";
export type PlanChoice = PredefinedPlanChoice | "custom";

export interface PlanCostSettings {
  monthlyPremium: number;
  planDeductible: number;
  officeVisitCopay: number;
}

export type PlanCostSettingsById = Record<PlanChoice, PlanCostSettings>;

export const DEFAULT_SIMULATION_PARAMETERS: SimulationParameters = {
  medigapPremium2026: 157,
  medigapPremiumGrowthRate: 0.07,
  planDeductible2026: 0,
  planDeductibleGrowthRate: 0.06,
  partDPremium2026: 49,
  partDPremiumGrowthRate: 0.06,
  partADeductible2026: 1736,
  partADeductibleGrowthRate: 0.06,
  partBDeductible2026: 283,
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
    partADeductible2026: parameters.partADeductible2026,
    partADeductibleGrowthRate: parameters.partADeductibleGrowthRate,
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
    premium2026: 157,
    premiumGrowthRate: 0.07,
    planDeductible2026: 0,
    planDeductibleGrowthRate: 0.06,
    partDPremium2026: 49,
    partDPremiumGrowthRate: 0.06,
    partBDeductible2026: 283,
    partBDeductibleGrowthRate: 0.06,
    percentSick: 0.2,
    simulationYears: 25,
    startYear: CURRENT_YEAR,
    specialistVisitsPerYear: 12,
    specialistCopay2026: 0,
    specialistCopayGrowthRate: 0.07,
    ...overrides,
  };
}

export function createPlanHDG(overrides: Partial<PlanDefinition> = {}): PlanDefinition {
  return {
    ...createPlanG(),
    id: "plan-hdg",
    name: "High Deductible Plan G",
    premium2026: 70,
    planDeductible2026: 2875,
    specialistCopay2026: 20,
    ...overrides,
  };
}

export function createPlanN(overrides: Partial<PlanDefinition> = {}): PlanDefinition {
  return {
    ...createPlanG(),
    id: "plan-n",
    name: "Plan N",
    premium2026: 122,
    planDeductible2026: 0,
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

function costSettings(plan: PlanDefinition): PlanCostSettings {
  return {
    monthlyPremium: plan.premium2026,
    planDeductible: plan.planDeductible2026,
    officeVisitCopay: plan.specialistCopay2026 ?? 20,
  };
}

export const DEFAULT_PLAN_COST_SETTINGS: PlanCostSettingsById = {
  "plan-g": costSettings(createPlanG()),
  "plan-hdg": costSettings(createPlanHDG()),
  "plan-n": costSettings(createPlanN()),
  custom: costSettings(createCustomPlan()),
};

export const PLAN_COST_SETTINGS_STORAGE_KEY = "medicare-simulator.plan-costs.v3";

export function withPlanCostSettings(plan: PlanDefinition, settings: PlanCostSettings): PlanDefinition {
  return {
    ...plan,
    premium2026: settings.monthlyPremium,
    planDeductible2026: settings.planDeductible,
    specialistVisitsPerYear: plan.specialistVisitsPerYear ?? 12,
    specialistCopay2026: settings.officeVisitCopay,
    specialistCopayGrowthRate: plan.specialistCopayGrowthRate ?? plan.premiumGrowthRate,
  };
}

/** Single-plan and comparison scenarios intentionally exclude Part D coverage. */
export function withoutPartD(plan: PlanDefinition): PlanDefinition {
  return {
    ...plan,
    partDPremium2026: 0,
    partDPremiumGrowthRate: 0,
  };
}

export const PREDEFINED_PLANS = {
  "plan-g": createPlanG,
  "plan-hdg": createPlanHDG,
  "plan-n": createPlanN,
} as const;
