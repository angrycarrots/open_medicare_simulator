import { useMemo, useState } from "react";
import { FieldGroup, NumberField, RangeField, RunStatus } from "../components/Fields";
import { SimulationSummary } from "../components/Charts";
import { percent } from "../lib/format";
import { annualCost } from "../lib/simulation";
import {
  createCustomPlan,
  createPlanG,
  createPlanHDG,
  createPlanN,
  DEFAULT_PLAN_COST_SETTINGS,
  PLAN_COST_SETTINGS_STORAGE_KEY,
  withoutPartD,
  withPlanCostSettings,
  type PlanChoice,
  type PlanCostSettings,
  type PlanCostSettingsById,
} from "../lib/plans";
import { useSimulationWorker } from "../hooks/useSimulationWorker";
import { usePersistentState } from "../hooks/usePersistentState";
import type { PlanDefinition, SimulationResult } from "../types";
import { PageLayout } from "./FullSimulatorPage";

const currentYear = new Date().getFullYear();

export function SinglePlanPage() {
  const [planChoice, setPlanChoice] = usePersistentState<PlanChoice>("medicare-simulator.single.plan-choice.v1", "plan-g");
  const [percentSick, setPercentSick] = usePersistentState("medicare-simulator.single.utilization.v1", 0.2);
  const [simulationYears, setSimulationYears] = usePersistentState("medicare-simulator.single.years.v1", 25);
  const [startYear, setStartYear] = usePersistentState("medicare-simulator.single.start-year.v1", currentYear);
  const [numSimulations, setNumSimulations] = usePersistentState("medicare-simulator.single.simulations.v1", 2500);
  const [customPlan, setCustomPlan] = usePersistentState<PlanDefinition>("medicare-simulator.single.custom-plan.v1", createCustomPlan());
  const [planCostSettings, setPlanCostSettings] = usePersistentState<PlanCostSettingsById>(PLAN_COST_SETTINGS_STORAGE_KEY, DEFAULT_PLAN_COST_SETTINGS);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const worker = useSimulationWorker();

  const selectedPlan = useMemo(
    () => buildPlan(planChoice, customPlan, planCostSettings[planChoice], percentSick, simulationYears, startYear),
    [planChoice, customPlan, planCostSettings, percentSick, simulationYears, startYear],
  );
  const updateCustom = <Key extends keyof PlanDefinition>(key: Key, value: PlanDefinition[Key]) => setCustomPlan((plan) => ({ ...plan, [key]: value }));
  const updatePlanCost = <Key extends keyof PlanCostSettings>(key: Key, value: PlanCostSettings[Key]) => {
    setPlanCostSettings((settings) => ({
      ...settings,
      [planChoice]: { ...settings[planChoice], [key]: value },
    }));
  };
  const run = async () => {
    try {
      setResult(await worker.runSimulation({ plan: selectedPlan, numSimulations }));
    } catch {
      // The worker hook displays the user-facing error.
    }
  };
  const stale = result !== null && JSON.stringify(selectedPlan) !== JSON.stringify(result.plan);

  return (
    <PageLayout title="Single-plan simulator" lead="Explore the cost pattern of a predefined Medicare plan or a custom plan using the same assumptions as the original web simulator.">
      <section className="workspace">
        <aside className="control-panel" aria-label="Plan simulation controls">
          <h2>Plan and settings</h2>
          <label className="field" htmlFor="plan-choice"><span>Medicare plan</span><select id="plan-choice" value={planChoice} onChange={(event) => setPlanChoice(event.currentTarget.value as PlanChoice)}><option value="plan-g">Plan G</option><option value="plan-hdg">High Deductible Plan G</option><option value="plan-n">Plan N</option><option value="custom">Custom plan</option></select></label>
          <PlanCostFields choice={planChoice} settings={planCostSettings[planChoice]} update={updatePlanCost} />
          <FieldGroup title="Simulation settings">
            <RangeField id="single-utilization" label="Probability of full utilization" value={percentSick} onChange={setPercentSick} step={0.05} format={percent} tooltip="This is the estimated percentage that you use the plan. How you use the plan impacts copays and other costs." />
            <NumberField id="single-simulations" label="Number of simulations" value={numSimulations} onChange={setNumSimulations} min={100} max={10000} step={100} />
            <NumberField id="single-years" label="Simulation years" value={simulationYears} onChange={setSimulationYears} min={10} max={50} step={5} />
            <NumberField id="single-start" label="Start year" value={startYear} onChange={setStartYear} min={currentYear - 10} max={currentYear + 10} />
          </FieldGroup>
          {planChoice === "custom" && <CustomPlanFields plan={customPlan} update={updateCustom} />}
          <button className="primary-button" onClick={run} disabled={worker.isRunning}>{worker.isRunning ? "Running simulation…" : "Run plan simulation"}</button>
          <RunStatus {...worker} />
        </aside>
        <div className="analysis-panel">
          {stale && <p className="status warning">Inputs have changed. Results below remain labeled with the plan that generated them.</p>}
          <PlanSummary plan={result?.plan ?? selectedPlan} />
          <HealthySickTable plan={result?.plan ?? selectedPlan} />
          {result && <SimulationSummary result={result} />}
        </div>
      </section>
    </PageLayout>
  );
}

function buildPlan(choice: PlanChoice, custom: PlanDefinition, costs: PlanCostSettings, percentSick: number, simulationYears: number, startYear: number): PlanDefinition {
  const overrides = { percentSick, simulationYears, startYear };
  let plan: PlanDefinition;
  if (choice === "plan-hdg") plan = createPlanHDG(overrides);
  else if (choice === "plan-n") plan = createPlanN(overrides);
  else if (choice === "custom") plan = { ...custom, ...overrides };
  else plan = createPlanG(overrides);
  return withoutPartD(withPlanCostSettings(plan, costs));
}

function PlanCostFields({ choice, settings, update }: { choice: PlanChoice; settings: PlanCostSettings; update: <Key extends keyof PlanCostSettings>(key: Key, value: PlanCostSettings[Key]) => void }) {
  const title = choice === "custom" ? "Custom plan costs" : "Selected plan costs";
  return <FieldGroup title={title}>
    <NumberField id={`${choice}-premium`} label="Monthly premium" value={settings.monthlyPremium} onChange={(value) => update("monthlyPremium", value)} min={1} max={1000} step={1} />
    <NumberField id={`${choice}-deductible`} label="Plan deductible (annual)" value={settings.planDeductible} onChange={(value) => update("planDeductible", value)} min={1} max={10000} step={1} />
    <NumberField id={`${choice}-office-copay`} label="Office visit copay" value={settings.officeVisitCopay} onChange={(value) => update("officeVisitCopay", value)} min={0} max={500} step={1} help="Applied to the plan's assumed 12 office visits per year." />
  </FieldGroup>;
}

function CustomPlanFields({ plan, update }: { plan: PlanDefinition; update: <Key extends keyof PlanDefinition>(key: Key, value: PlanDefinition[Key]) => void }) {
  return <>
    <FieldGroup title="Custom plan growth rates">
      <RangeField id="custom-premium-growth" label="Premium growth rate" value={plan.premiumGrowthRate} onChange={(value) => update("premiumGrowthRate", value)} max={0.2} format={percent} />
      <RangeField id="custom-deductible-growth" label="Deductible growth rate" value={plan.planDeductibleGrowthRate} onChange={(value) => update("planDeductibleGrowthRate", value)} max={0.2} format={percent} />
    </FieldGroup>
    <FieldGroup title="Part B">
      <NumberField id="custom-part-b" label="Part B deductible (annual)" value={plan.partBDeductible2026} onChange={(value) => update("partBDeductible2026", value)} min={100} max={500} step={10} />
      <RangeField id="custom-part-b-growth" label="Part B growth rate" value={plan.partBDeductibleGrowthRate} onChange={(value) => update("partBDeductibleGrowthRate", value)} max={0.2} format={percent} />
    </FieldGroup>
  </>;
}

function PlanSummary({ plan }: { plan: PlanDefinition }) {
  return <section className="summary-card"><div><p className="eyebrow">Selected plan</p><h2>{plan.name}</h2><p>{percent(plan.percentSick)} probability of full utilization · {plan.simulationYears} years from {plan.startYear}</p></div><div className="plan-details"><div><span>Monthly premium</span><strong>${plan.premium2026.toFixed(2)}</strong><small>{percent(plan.premiumGrowthRate)} annual growth</small></div><div><span>Plan deductible</span><strong>${plan.planDeductible2026.toFixed(2)}</strong><small>{percent(plan.planDeductibleGrowthRate)} annual growth</small></div><div><span>Office visit copay</span><strong>${plan.specialistCopay2026?.toFixed(2)}</strong><small>{plan.specialistVisitsPerYear} assumed visits per year</small></div></div></section>;
}

function HealthySickTable({ plan }: { plan: PlanDefinition }) {
  const rows = Array.from({ length: Math.min(5, plan.simulationYears) }, (_, offset) => ({ year: plan.startYear + offset, healthy: annualCost(plan, offset, false), sick: annualCost(plan, offset, true) }));
  const money = (value: number) => value.toLocaleString("en-US", { style: "currency", currency: "USD" });
  return <section className="table-card"><h2>Cost projections by year</h2><p className="table-description">Office visit copays are included in both healthy and full-utilization projections.</p><table><thead><tr><th>Year</th><th>Healthy annual cost</th><th>Full-utilization annual cost</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><td>{row.year}</td><td>{money(row.healthy)}</td><td>{money(row.sick)}</td></tr>)}</tbody></table></section>;
}
