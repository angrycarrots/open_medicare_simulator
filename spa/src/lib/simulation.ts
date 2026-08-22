import type {
  ComparisonResult,
  PlanDefinition,
  SimulationRequest,
  SimulationResult,
  YearStatistics,
} from "../types";

export interface RandomSource {
  next(): number;
}

export class MathRandomSource implements RandomSource {
  next(): number {
    return Math.random();
  }
}

export class SeededRandomSource implements RandomSource {
  private state: number;

  constructor(seed: number) {
    this.state = seed >>> 0;
  }

  next(): number {
    let value = (this.state += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4_294_967_296;
  }
}

export function validatePlan(plan: PlanDefinition): void {
  if (!plan.name.trim()) throw new Error("Plan name is required.");
  const positiveFields: Array<[number, string]> = [
    [plan.premium2026, "Plan premium"],
    [plan.planDeductible2026, "Plan deductible"],
    [plan.partDPremium2026, "Part D premium"],
    [plan.partBDeductible2026, "Part B deductible"],
  ];
  for (const [value, label] of positiveFields) {
    if (!Number.isFinite(value) || value <= 0) throw new Error(`${label} must be positive.`);
  }
  const growthFields: Array<[number, string]> = [
    [plan.premiumGrowthRate, "Plan premium growth rate"],
    [plan.planDeductibleGrowthRate, "Plan deductible growth rate"],
    [plan.partDPremiumGrowthRate, "Part D premium growth rate"],
    [plan.partBDeductibleGrowthRate, "Part B deductible growth rate"],
  ];
  for (const [value, label] of growthFields) {
    if (!Number.isFinite(value) || value < 0) throw new Error(`${label} must be non-negative.`);
  }
  if (!Number.isFinite(plan.percentSick) || plan.percentSick < 0 || plan.percentSick > 1) {
    throw new Error("Probability of full utilization must be between 0 and 1.");
  }
  if (!Number.isInteger(plan.simulationYears) || plan.simulationYears <= 0) {
    throw new Error("Simulation years must be a positive whole number.");
  }
  if (!Number.isInteger(plan.startYear) || plan.startYear <= 0) {
    throw new Error("Start year must be a positive whole number.");
  }

  const specialistFields = [
    plan.specialistVisitsPerYear,
    plan.specialistCopay2026,
    plan.specialistCopayGrowthRate,
  ];
  const suppliedSpecialistFields = specialistFields.filter((value) => value !== undefined).length;
  if (suppliedSpecialistFields > 0 && suppliedSpecialistFields !== specialistFields.length) {
    throw new Error("Specialist visits, copay, and copay growth rate must be supplied together.");
  }
  if (suppliedSpecialistFields === specialistFields.length) {
    if (plan.specialistVisitsPerYear === undefined || !Number.isInteger(plan.specialistVisitsPerYear) || plan.specialistVisitsPerYear < 0) {
      throw new Error("Specialist visits per year must be a non-negative whole number.");
    }
    if (plan.specialistCopay2026 === undefined || plan.specialistCopay2026 < 0) {
      throw new Error("Specialist copay must be non-negative.");
    }
    if (plan.specialistCopayGrowthRate === undefined || plan.specialistCopayGrowthRate < 0) {
      throw new Error("Specialist copay growth rate must be non-negative.");
    }
  }
}

export function compound(base: number, growthRate: number, yearOffset: number): number {
  if (!Number.isInteger(yearOffset) || yearOffset < 0) throw new Error("Year offset must be non-negative.");
  return base * (1 + growthRate) ** yearOffset;
}

export function annualCost(plan: PlanDefinition, yearOffset: number, isSick: boolean): number {
  const premiums =
    (compound(plan.premium2026, plan.premiumGrowthRate, yearOffset) +
      compound(plan.partDPremium2026, plan.partDPremiumGrowthRate, yearOffset)) *
    12;
  const specialistCost =
    plan.specialistVisitsPerYear === undefined ||
    plan.specialistCopay2026 === undefined ||
    plan.specialistCopayGrowthRate === undefined
      ? 0
      : plan.specialistVisitsPerYear! *
        compound(plan.specialistCopay2026!, plan.specialistCopayGrowthRate!, yearOffset);
  if (!isSick) return premiums + specialistCost;
  return (
    premiums +
    specialistCost +
    compound(plan.planDeductible2026, plan.planDeductibleGrowthRate, yearOffset) +
    compound(plan.partBDeductible2026, plan.partBDeductibleGrowthRate, yearOffset)
  );
}

export function percentile(values: readonly number[], percentileValue: number): number {
  if (!values.length) throw new Error("Cannot calculate a percentile for an empty array.");
  if (percentileValue < 0 || percentileValue > 100) throw new Error("Percentile must be between 0 and 100.");
  const sorted = [...values].sort((left, right) => left - right);
  const position = (percentileValue / 100) * (sorted.length - 1);
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return sorted[lower];
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

export function mean(values: readonly number[]): number {
  return values.reduce((total, value) => total + value, 0) / values.length;
}

export function populationStandardDeviation(values: readonly number[]): number {
  const average = mean(values);
  return Math.sqrt(values.reduce((total, value) => total + (value - average) ** 2, 0) / values.length);
}

function createStatistics(years: number): YearStatistics {
  return {
    meanCosts: Array.from({ length: years }, () => 0),
    stdCosts: Array.from({ length: years }, () => 0),
    minCosts: Array.from({ length: years }, () => Number.POSITIVE_INFINITY),
    maxCosts: Array.from({ length: years }, () => Number.NEGATIVE_INFINITY),
    totalCosts: Array.from({ length: years }, () => 0),
  };
}

export function runSimulation(
  request: SimulationRequest,
  randomSource: RandomSource = request.randomSeed === undefined
    ? new MathRandomSource()
    : new SeededRandomSource(request.randomSeed),
  onProgress?: (completed: number, total: number) => void,
): SimulationResult {
  const { plan, numSimulations } = request;
  validatePlan(plan);
  if (!Number.isInteger(numSimulations) || numSimulations <= 0) {
    throw new Error("Number of simulations must be a positive whole number.");
  }

  const statistics = createStatistics(plan.simulationYears);
  const sumOfSquares = Array.from({ length: plan.simulationYears }, () => 0);
  const healthyCosts = Array.from({ length: plan.simulationYears }, (_, year) => annualCost(plan, year, false));
  const sickCostIncrements = Array.from(
    { length: plan.simulationYears },
    (_, year) => annualCost(plan, year, true) - healthyCosts[year],
  );
  const lifetimeCosts = new Float64Array(numSimulations);
  const progressInterval = Math.max(1, Math.floor(numSimulations / 20));

  for (let simulationIndex = 0; simulationIndex < numSimulations; simulationIndex += 1) {
    let lifetimeCost = 0;
    for (let year = 0; year < plan.simulationYears; year += 1) {
      const isSick = randomSource.next() < plan.percentSick;
      const cost = healthyCosts[year] + (isSick ? sickCostIncrements[year] : 0);
      lifetimeCost += cost;
      statistics.totalCosts[year] += cost;
      sumOfSquares[year] += cost * cost;
      statistics.minCosts[year] = Math.min(statistics.minCosts[year], cost);
      statistics.maxCosts[year] = Math.max(statistics.maxCosts[year], cost);
    }
    lifetimeCosts[simulationIndex] = lifetimeCost;
    if (onProgress && ((simulationIndex + 1) % progressInterval === 0 || simulationIndex + 1 === numSimulations)) {
      onProgress(simulationIndex + 1, numSimulations);
    }
  }

  for (let year = 0; year < plan.simulationYears; year += 1) {
    const average = statistics.totalCosts[year] / numSimulations;
    statistics.meanCosts[year] = average;
    statistics.stdCosts[year] = Math.sqrt(
      Math.max(0, sumOfSquares[year] / numSimulations - average * average),
    );
  }

  return {
    plan: { ...plan },
    numSimulations,
    statistics,
    lifetimeCosts: Array.from(lifetimeCosts),
  };
}

export function runComparison(
  plan1: PlanDefinition,
  plan2: PlanDefinition,
  numSimulations: number,
  randomSeed?: number,
  onProgress?: (completed: number, total: number, label: string) => void,
): ComparisonResult {
  const first = runSimulation(
    { plan: plan1, numSimulations, randomSeed },
    undefined,
    (completed, total) => onProgress?.(completed, total * 2, plan1.name),
  );
  const secondSeed = randomSeed === undefined ? undefined : randomSeed + 1;
  const second = runSimulation(
    { plan: plan2, numSimulations, randomSeed: secondSeed },
    undefined,
    (completed, total) => onProgress?.(completed + total, total * 2, plan2.name),
  );
  const pairedDifferences = second.lifetimeCosts.map((value, index) => value - first.lifetimeCosts[index]);
  return {
    plan1: first,
    plan2: second,
    meanDifference: mean(second.lifetimeCosts) - mean(first.lifetimeCosts),
    standardDeviationDifference: populationStandardDeviation(pairedDifferences),
  };
}
