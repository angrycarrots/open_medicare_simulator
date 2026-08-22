export interface SimulationParameters {
  medigapPremium2026: number;
  medigapPremiumGrowthRate: number;
  planDeductible2026: number;
  planDeductibleGrowthRate: number;
  partDPremium2026: number;
  partDPremiumGrowthRate: number;
  partBDeductible2026: number;
  partBDeductibleGrowthRate: number;
  percentSick: number;
  simulationYears: number;
  startYear: number;
}

export interface PlanDefinition {
  id: string;
  name: string;
  premium2026: number;
  premiumGrowthRate: number;
  planDeductible2026: number;
  planDeductibleGrowthRate: number;
  partDPremium2026: number;
  partDPremiumGrowthRate: number;
  partBDeductible2026: number;
  partBDeductibleGrowthRate: number;
  percentSick: number;
  simulationYears: number;
  startYear: number;
  specialistVisitsPerYear?: number;
  specialistCopay2026?: number;
  specialistCopayGrowthRate?: number;
}

export interface YearStatistics {
  meanCosts: number[];
  stdCosts: number[];
  minCosts: number[];
  maxCosts: number[];
  totalCosts: number[];
}

export interface SimulationResult {
  plan: PlanDefinition;
  numSimulations: number;
  statistics: YearStatistics;
  lifetimeCosts: number[];
}

export interface ComparisonResult {
  plan1: SimulationResult;
  plan2: SimulationResult;
  meanDifference: number;
  standardDeviationDifference: number;
}

export interface SimulationRequest {
  plan: PlanDefinition;
  numSimulations: number;
  randomSeed?: number;
}

export interface ComparisonRequest {
  plan1: PlanDefinition;
  plan2: PlanDefinition;
  numSimulations: number;
  randomSeed?: number;
}

export type WorkerRequest =
  | { type: "run-simulation"; requestId: string; request: SimulationRequest }
  | { type: "run-comparison"; requestId: string; request: ComparisonRequest };

export type WorkerResponse =
  | { type: "progress"; requestId: string; completed: number; total: number; label: string }
  | { type: "simulation-result"; requestId: string; result: SimulationResult }
  | { type: "comparison-result"; requestId: string; result: ComparisonResult }
  | { type: "error"; requestId: string; message: string };
