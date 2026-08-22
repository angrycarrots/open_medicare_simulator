import { useMemo, useState } from "react";
import { FieldGroup, NumberField, RangeField, RunStatus } from "../components/Fields";
import { SimulationSummary } from "../components/Charts";
import { percent } from "../lib/format";
import { annualCost } from "../lib/simulation";
import { createCustomPlan, createPlanG, createPlanHDG, createPlanN } from "../lib/plans";
import { useSimulationWorker } from "../hooks/useSimulationWorker";
import type { PlanDefinition, SimulationResult } from "../types";
import { PageLayout } from "./FullSimulatorPage";

type PlanChoice = "plan-g" | "plan-hdg" | "plan-n" | "custom";
const currentYear = new Date().getFullYear();

export function SinglePlanPage() {
  const [planChoice, setPlanChoice] = useState<PlanChoice>("plan-g");
  const [percentSick, setPercentSick] = useState(0.2);
  const [simulationYears, setSimulationYears] = useState(25);
  const [startYear, setStartYear] = useState(currentYear);
  const [numSimulations, setNumSimulations] = useState(2500);
  const [customPlan, setCustomPlan] = useState<PlanDefinition>(createCustomPlan());
  const [result, setResult] = useState<SimulationResult | null>(null);
  const worker = useSimulationWorker();

  const selectedPlan = useMemo(() => buildPlan(planChoice, customPlan, percentSick, simulationYears, startYear), [planChoice, customPlan, percentSick, simulationYears, startYear]);
  const updateCustom = <Key extends keyof PlanDefinition>(key: Key, value: PlanDefinition[Key]) => setCustomPlan((plan) => ({ ...plan, [key]: value }));
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
          <FieldGroup title="Simulation settings">
            <RangeField id="single-utilization" label="Probability of full utilization" value={percentSick} onChange={setPercentSick} step={0.05} format={percent} />
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

function buildPlan(choice: PlanChoice, custom: PlanDefinition, percentSick: number, simulationYears: number, startYear: number): PlanDefinition {
  const overrides = { percentSick, simulationYears, startYear };
  if (choice === "plan-hdg") return createPlanHDG(overrides);
  if (choice === "plan-n") return createPlanN(overrides);
  if (choice === "custom") return { ...custom, ...overrides };
  return createPlanG(overrides);
}

function CustomPlanFields({ plan, update }: { plan: PlanDefinition; update: <Key extends keyof PlanDefinition>(key: Key, value: PlanDefinition[Key]) => void }) {
  return <>
    <FieldGroup title="Custom plan costs">
      <NumberField id="custom-premium" label="Premium (monthly)" value={plan.premium2026} onChange={(value) => update("premium2026", value)} min={10} max={1000} step={10} />
      <RangeField id="custom-premium-growth" label="Premium growth rate" value={plan.premiumGrowthRate} onChange={(value) => update("premiumGrowthRate", value)} max={0.2} format={percent} />
      <NumberField id="custom-deductible" label="Plan deductible (annual)" value={plan.planDeductible2026} onChange={(value) => update("planDeductible2026", value)} min={100} max={10000} step={100} />
      <RangeField id="custom-deductible-growth" label="Deductible growth rate" value={plan.planDeductibleGrowthRate} onChange={(value) => update("planDeductibleGrowthRate", value)} max={0.2} format={percent} />
    </FieldGroup>
    <FieldGroup title="Part D and Part B">
      <NumberField id="custom-part-d" label="Part D premium (monthly)" value={plan.partDPremium2026} onChange={(value) => update("partDPremium2026", value)} min={10} max={200} step={5} />
      <RangeField id="custom-part-d-growth" label="Part D growth rate" value={plan.partDPremiumGrowthRate} onChange={(value) => update("partDPremiumGrowthRate", value)} max={0.2} format={percent} />
      <NumberField id="custom-part-b" label="Part B deductible (annual)" value={plan.partBDeductible2026} onChange={(value) => update("partBDeductible2026", value)} min={100} max={500} step={10} />
      <RangeField id="custom-part-b-growth" label="Part B growth rate" value={plan.partBDeductibleGrowthRate} onChange={(value) => update("partBDeductibleGrowthRate", value)} max={0.2} format={percent} />
    </FieldGroup>
  </>;
}

function PlanSummary({ plan }: { plan: PlanDefinition }) {
  return <section className="summary-card"><div><p className="eyebrow">Selected plan</p><h2>{plan.name}</h2><p>{percent(plan.percentSick)} probability of full utilization · {plan.simulationYears} years from {plan.startYear}</p></div><div className="plan-details"><div><span>Monthly premium</span><strong>${plan.premium2026.toFixed(2)}</strong><small>{percent(plan.premiumGrowthRate)} annual growth</small></div><div><span>Plan deductible</span><strong>${plan.planDeductible2026.toFixed(2)}</strong><small>{percent(plan.planDeductibleGrowthRate)} annual growth</small></div><div><span>Part D premium</span><strong>${plan.partDPremium2026.toFixed(2)}</strong><small>per month</small></div>{plan.specialistVisitsPerYear !== undefined && <div><span>Specialist copays</span><strong>{plan.specialistVisitsPerYear} visits</strong><small>${plan.specialistCopay2026?.toFixed(2)} each in year one</small></div>}</div></section>;
}

function HealthySickTable({ plan }: { plan: PlanDefinition }) {
  const rows = Array.from({ length: Math.min(5, plan.simulationYears) }, (_, offset) => ({ year: plan.startYear + offset, healthy: annualCost(plan, offset, false), sick: annualCost(plan, offset, true) }));
  const money = (value: number) => value.toLocaleString("en-US", { style: "currency", currency: "USD" });
  return <section className="table-card"><h2>Cost projections by year</h2><p className="table-description">Plan N specialist copays are included in both healthy and full-utilization projections.</p><table><thead><tr><th>Year</th><th>Healthy annual cost</th><th>Full-utilization annual cost</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><td>{row.year}</td><td>{money(row.healthy)}</td><td>{money(row.sick)}</td></tr>)}</tbody></table></section>;
}
