import { useMemo, useState } from "react";
import { ComparisonSummary } from "../components/Charts";
import { FieldGroup, NumberField, RangeField, RunStatus } from "../components/Fields";
import { percent } from "../lib/format";
import {
  createPlanG,
  createPlanHDG,
  createPlanN,
  DEFAULT_PLAN_COST_SETTINGS,
  PLAN_COST_SETTINGS_STORAGE_KEY,
  withoutPartD,
  withPlanCostSettings,
  type PlanCostSettings,
  type PlanCostSettingsById,
  type PredefinedPlanChoice,
} from "../lib/plans";
import { annualCost } from "../lib/simulation";
import { useSimulationWorker } from "../hooks/useSimulationWorker";
import { usePersistentState } from "../hooks/usePersistentState";
import type { ComparisonResult, PlanDefinition } from "../types";
import { PageLayout } from "./FullSimulatorPage";

const currentYear = new Date().getFullYear();

export function ComparisonPage() {
  const [firstChoice, setFirstChoice] = usePersistentState<PredefinedPlanChoice>("medicare-simulator.comparison.first-plan.v1", "plan-g");
  const [secondChoice, setSecondChoice] = usePersistentState<PredefinedPlanChoice>("medicare-simulator.comparison.second-plan.v1", "plan-hdg");
  const [percentSick, setPercentSick] = usePersistentState("medicare-simulator.comparison.utilization.v1", 0.2);
  const [numSimulations, setNumSimulations] = usePersistentState("medicare-simulator.comparison.simulations.v1", 2500);
  const [simulationYears, setSimulationYears] = usePersistentState("medicare-simulator.comparison.years.v1", 25);
  const [startYear, setStartYear] = usePersistentState("medicare-simulator.comparison.start-year.v1", currentYear);
  const [planCostSettings] = usePersistentState<PlanCostSettingsById>(PLAN_COST_SETTINGS_STORAGE_KEY, DEFAULT_PLAN_COST_SETTINGS);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const worker = useSimulationWorker();
  const plans = useMemo(() => ({
    first: makePlan(firstChoice, planCostSettings[firstChoice], percentSick, simulationYears, startYear),
    second: makePlan(secondChoice, planCostSettings[secondChoice], percentSick, simulationYears, startYear),
  }), [firstChoice, secondChoice, planCostSettings, percentSick, simulationYears, startYear]);
  const run = async () => {
    try {
      setResult(await worker.runComparison({ plan1: plans.first, plan2: plans.second, numSimulations }));
    } catch {
      // The worker hook displays the user-facing error.
    }
  };
  const stale = result !== null && (JSON.stringify(plans.first) !== JSON.stringify(result.plan1.plan) || JSON.stringify(plans.second) !== JSON.stringify(result.plan2.plan));

  return <PageLayout title="Plan comparison" lead="Compare Medicare plan trade-offs side by side, from first-year costs to the full distribution of simulated lifetime expenses.">
    <section className="workspace">
      <aside className="control-panel" aria-label="Plan comparison controls">
        <h2>Compare plans</h2>
        <label className="field" htmlFor="first-plan"><span>Plan 1</span><PlanSelect id="first-plan" value={firstChoice} onChange={setFirstChoice} /></label>
        <label className="field" htmlFor="second-plan"><span>Plan 2</span><PlanSelect id="second-plan" value={secondChoice} onChange={setSecondChoice} /></label>
        <p className="settings-note">Plan costs use the values saved on the Single Plan page.</p>
        <FieldGroup title="Shared simulation settings">
          <RangeField id="comparison-utilization" label="Probability of full utilization" value={percentSick} onChange={setPercentSick} step={0.05} format={percent} tooltip="This is the estimated percentage that you use the plan. How you use the plan impacts copays and other costs." />
          <NumberField id="comparison-simulations" label="Number of simulations" value={numSimulations} onChange={setNumSimulations} min={100} max={10000} step={100} />
          <NumberField id="comparison-years" label="Simulation years" value={simulationYears} onChange={setSimulationYears} min={10} max={50} step={5} />
          <NumberField id="comparison-start" label="Start year" value={startYear} onChange={setStartYear} min={currentYear - 10} max={currentYear + 10} />
        </FieldGroup>
        <button className="primary-button" onClick={run} disabled={worker.isRunning}>{worker.isRunning ? "Running comparison…" : "Run comparison"}</button>
        <RunStatus {...worker} />
      </aside>
      <div className="analysis-panel">
        {stale && <p className="status warning">Inputs have changed. Results below remain labeled with the scenarios that generated them.</p>}
        <PlanComparisonTable first={result?.plan1.plan ?? plans.first} second={result?.plan2.plan ?? plans.second} />
        <AnnualComparison first={result?.plan1.plan ?? plans.first} second={result?.plan2.plan ?? plans.second} />
        {result && <ComparisonSummary result={result} />}
      </div>
    </section>
  </PageLayout>;
}

function makePlan(choice: PredefinedPlanChoice, costs: PlanCostSettings, percentSick: number, simulationYears: number, startYear: number): PlanDefinition {
  const overrides = { percentSick, simulationYears, startYear };
  let plan: PlanDefinition;
  if (choice === "plan-hdg") plan = createPlanHDG(overrides);
  else if (choice === "plan-n") plan = createPlanN(overrides);
  else plan = createPlanG(overrides);
  return withoutPartD(withPlanCostSettings(plan, costs));
}

function PlanSelect({ id, value, onChange }: { id: string; value: PredefinedPlanChoice; onChange: (value: PredefinedPlanChoice) => void }) {
  return <select id={id} value={value} onChange={(event) => onChange(event.currentTarget.value as PredefinedPlanChoice)}><option value="plan-g">Plan G</option><option value="plan-hdg">High Deductible Plan G</option><option value="plan-n">Plan N</option></select>;
}

function PlanComparisonTable({ first, second }: { first: PlanDefinition; second: PlanDefinition }) {
  const fields: Array<[string, string, string]> = [
    ["Monthly premium", `$${first.premium2026.toFixed(2)}`, `$${second.premium2026.toFixed(2)}`],
    ["Annual plan deductible", `$${first.planDeductible2026.toFixed(2)}`, `$${second.planDeductible2026.toFixed(2)}`],
    ["Office visit copay", `$${first.specialistCopay2026?.toFixed(2)}`, `$${second.specialistCopay2026?.toFixed(2)}`],
    ["Part B annual deductible", `$${first.partBDeductible2026.toFixed(2)}`, `$${second.partBDeductible2026.toFixed(2)}`],
    ["Assumed office visits", `${first.specialistVisitsPerYear}/year`, `${second.specialistVisitsPerYear}/year`],
  ];
  return <section className="table-card"><h2>Plan details</h2><table><thead><tr><th>Cost component</th><th>{first.name}</th><th>{second.name}</th></tr></thead><tbody>{fields.map(([label, firstValue, secondValue]) => <tr key={label}><td>{label}</td><td>{firstValue}</td><td>{secondValue}</td></tr>)}</tbody></table></section>;
}

function AnnualComparison({ first, second }: { first: PlanDefinition; second: PlanDefinition }) {
  const rows = Array.from({ length: Math.min(10, first.simulationYears) }, (_, offset) => ({ year: first.startYear + offset, firstHealthy: annualCost(first, offset, false), firstSick: annualCost(first, offset, true), secondHealthy: annualCost(second, offset, false), secondSick: annualCost(second, offset, true) }));
  const money = (value: number) => value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  return <section className="table-card"><h2>Annual cost comparison</h2><div className="table-scroll"><table><thead><tr><th>Year</th><th>{first.name} healthy</th><th>{first.name} full utilization</th><th>{second.name} healthy</th><th>{second.name} full utilization</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><td>{row.year}</td><td>{money(row.firstHealthy)}</td><td>{money(row.firstSick)}</td><td>{money(row.secondHealthy)}</td><td>{money(row.secondSick)}</td></tr>)}</tbody></table></div></section>;
}
