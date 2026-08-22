import { useState } from "react";
import { FieldGroup, NumberField, RangeField, RunStatus } from "../components/Fields";
import { SimulationSummary } from "../components/Charts";
import { downloadCsv, simulationCsv } from "../lib/csv";
import { percent } from "../lib/format";
import {
  DEFAULT_PLAN_COST_SETTINGS,
  DEFAULT_SIMULATION_PARAMETERS,
  fullSimulatorPlan,
  PLAN_COST_SETTINGS_STORAGE_KEY,
  PREDEFINED_PLANS,
  type PlanCostSettingsById,
  type PredefinedPlanChoice,
} from "../lib/plans";
import { annualCost } from "../lib/simulation";
import { useSimulationSettings } from "../hooks/useSimulationSettings";
import { useSimulationWorker } from "../hooks/useSimulationWorker";
import { usePersistentState } from "../hooks/usePersistentState";
import type { SimulationParameters, SimulationResult } from "../types";

const currentYear = new Date().getFullYear();

export function FullSimulatorPage() {
  const [parameters, setParameters] = usePersistentState<SimulationParameters>("medicare-simulator.full.parameters.v2", DEFAULT_SIMULATION_PARAMETERS);
  const [selectedPlan, setSelectedPlan] = usePersistentState<PredefinedPlanChoice>("medicare-simulator.full.selected-plan.v1", "plan-g");
  const [planCostSettings] = usePersistentState<PlanCostSettingsById>(PLAN_COST_SETTINGS_STORAGE_KEY, DEFAULT_PLAN_COST_SETTINGS);
  const { settings: simulationSettings, updateSetting } = useSimulationSettings();
  const [result, setResult] = useState<SimulationResult | null>(null);
  const worker = useSimulationWorker();
  const selectedPlanCosts = planCostSettings[selectedPlan];
  const resolvedParameters = { ...DEFAULT_SIMULATION_PARAMETERS, ...parameters };
  const effectiveParameters = {
    ...resolvedParameters,
    medigapPremium2026: selectedPlanCosts.monthlyPremium,
    planDeductible2026: selectedPlanCosts.planDeductible,
    percentSick: simulationSettings.percentSick,
    simulationYears: simulationSettings.simulationYears,
    startYear: simulationSettings.startYear,
  };
  const scenarioPlan = makeFullSimulatorPlan(effectiveParameters, selectedPlan);

  const update = <Key extends keyof SimulationParameters>(key: Key, value: SimulationParameters[Key]) => {
    setParameters((current) => ({ ...current, [key]: value }));
  };
  const run = async () => {
    try {
      const nextResult = await worker.runSimulation({ plan: scenarioPlan, numSimulations: simulationSettings.numSimulations });
      setResult(nextResult);
    } catch {
      // The hook exposes a user-facing error state.
    }
  };
  const snapshotIsStale = result !== null && (
    JSON.stringify(scenarioPlan) !== JSON.stringify(result.plan)
    || simulationSettings.numSimulations !== result.numSimulations
  );

  return (
    <PageLayout title="Medicare and Medigap cost simulator" lead="Model a range of Medicare and Medigap costs over time, then use Monte Carlo sampling to understand likely lifetime expenses.">
      <section className="workspace">
        <aside className="control-panel" aria-label="Simulation controls">
          <h2>Scenario inputs</h2>
          <FieldGroup title="Base costs">
            <label className="field" htmlFor="full-plan"><span>Select plan</span><select id="full-plan" value={selectedPlan} onChange={(event) => setSelectedPlan(event.currentTarget.value as PredefinedPlanChoice)}><option value="plan-g">Plan G</option><option value="plan-hdg">Plan G HD</option><option value="plan-n">Plan N</option></select></label>
            <p className="settings-note">Uses the selected plan page's saved premium (${selectedPlanCosts.monthlyPremium.toFixed(2)}/month) and deductible (${selectedPlanCosts.planDeductible.toFixed(2)}/year).</p>
            <NumberField id="full-part-d" label="Part D premium (monthly)" value={resolvedParameters.partDPremium2026} onChange={(value) => update("partDPremium2026", value)} min={10} max={200} step={5} />
            <NumberField id="full-part-a" label="Plan A deductible (annual)" value={resolvedParameters.partADeductible2026} onChange={(value) => update("partADeductible2026", value)} min={100} max={5000} step={1} />
            <NumberField id="full-part-b" label="Plan B deductible (annual)" value={resolvedParameters.partBDeductible2026} onChange={(value) => update("partBDeductible2026", value)} min={100} max={500} step={10} />
          </FieldGroup>
          <FieldGroup title="Annual growth rates">
            <RangeField id="full-medigap-growth" label="Medigap premium" value={resolvedParameters.medigapPremiumGrowthRate} onChange={(value) => update("medigapPremiumGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-deductible-growth" label="Plan deductible" value={resolvedParameters.planDeductibleGrowthRate} onChange={(value) => update("planDeductibleGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-part-d-growth" label="Part D premium" value={resolvedParameters.partDPremiumGrowthRate} onChange={(value) => update("partDPremiumGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-part-a-growth" label="Plan A deductible" value={resolvedParameters.partADeductibleGrowthRate} onChange={(value) => update("partADeductibleGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-part-b-growth" label="Plan B deductible" value={resolvedParameters.partBDeductibleGrowthRate} onChange={(value) => update("partBDeductibleGrowthRate", value)} max={0.15} format={percent} />
          </FieldGroup>
          <FieldGroup title="Simulation settings">
            <RangeField id="full-utilization" label="Probability of full utilization" value={simulationSettings.percentSick} onChange={(value) => updateSetting("percentSick", value)} step={0.05} format={percent} tooltip="This is the estimated percentage that you use the plan. How you use the plan impacts copays and other costs." />
            <NumberField id="full-simulations" label="Number of simulations" value={simulationSettings.numSimulations} onChange={(value) => updateSetting("numSimulations", value)} min={100} max={10000} step={100} />
            <NumberField id="full-years" label="Simulation years" value={simulationSettings.simulationYears} onChange={(value) => updateSetting("simulationYears", value)} min={10} max={50} step={5} />
            <NumberField id="full-start" label="Start year" value={simulationSettings.startYear} onChange={(value) => updateSetting("startYear", value)} min={currentYear - 10} max={currentYear + 10} />
          </FieldGroup>
          <button className="primary-button" onClick={run} disabled={worker.isRunning}>{worker.isRunning ? "Running simulation…" : "Run full simulation"}</button>
          <RunStatus {...worker} />
        </aside>
        <div className="analysis-panel">
          {result === null ? <EmptyState /> : <>
            {snapshotIsStale && <p className="status warning">Inputs have changed. Results below remain labeled with the scenario that generated them.</p>}
            <CostBreakdown plan={result.plan} />
            <SimulationSummary result={result} includeDownload onDownload={() => downloadCsv(`medicare_cost_projections_${result.plan.startYear}_${result.plan.startYear + result.plan.simulationYears - 1}.csv`, simulationCsv(result))} />
          </>}
        </div>
      </section>
    </PageLayout>
  );
}

function makeFullSimulatorPlan(parameters: SimulationParameters, selectedPlan: PredefinedPlanChoice) {
  const plan = fullSimulatorPlan(parameters);
  const selectedPlanName = PREDEFINED_PLANS[selectedPlan]().name;
  return {
    ...plan,
    id: `full-${selectedPlan}`,
    name: `${selectedPlanName} scenario`,
  };
}

function CostBreakdown({ plan }: { plan: ReturnType<typeof fullSimulatorPlan> }) {
  const rows = Array.from({ length: plan.simulationYears }, (_, offset) => ({
    year: plan.startYear + offset,
    medigapMonthly: plan.premium2026 * (1 + plan.premiumGrowthRate) ** offset,
    planDeductible: plan.planDeductible2026 * (1 + plan.planDeductibleGrowthRate) ** offset,
    partDMonthly: plan.partDPremium2026 * (1 + plan.partDPremiumGrowthRate) ** offset,
    partADeductible: (plan.partADeductible2026 ?? 0) * (1 + (plan.partADeductibleGrowthRate ?? 0)) ** offset,
    partBDeductible: plan.partBDeductible2026 * (1 + plan.partBDeductibleGrowthRate) ** offset,
    total: annualCost(plan, offset, true),
  }));
  const value = (amount: number) => `$${amount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  return <section className="table-card"><h2>Year-by-year cost breakdown</h2><div className="table-scroll"><table><thead><tr><th>Year</th><th>Medigap monthly</th><th>Plan deductible</th><th>Part D monthly</th><th>Plan A deductible</th><th>Plan B deductible</th><th>Full-utilization annual cost</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><td>{row.year}</td><td>{value(row.medigapMonthly)}</td><td>{value(row.planDeductible)}</td><td>{value(row.partDMonthly)}</td><td>{value(row.partADeductible)}</td><td>{value(row.partBDeductible)}</td><td>{value(row.total)}</td></tr>)}</tbody></table></div></section>;
}

export function PageLayout({ title, lead, children }: { title: string; lead: string; children: React.ReactNode }) {
  return <main className="page"><header className="page-header"><p className="eyebrow">Financial planning explorer</p><h1>{title}</h1><p>{lead}</p></header>{children}</main>;
}

function EmptyState() {
  return <section className="empty-state"><p className="eyebrow">Ready when you are</p><h2>Explore a cost scenario</h2><p>Adjust the assumptions, then run the simulation to see annual projections, lifetime-cost distribution, and percentiles.</p></section>;
}
