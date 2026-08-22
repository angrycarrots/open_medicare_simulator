import { useState } from "react";
import { FieldGroup, NumberField, RangeField, RunStatus } from "../components/Fields";
import { SimulationSummary } from "../components/Charts";
import { downloadCsv, simulationCsv } from "../lib/csv";
import { percent } from "../lib/format";
import { fullSimulatorPlan, DEFAULT_SIMULATION_PARAMETERS } from "../lib/plans";
import { annualCost } from "../lib/simulation";
import { useSimulationWorker } from "../hooks/useSimulationWorker";
import type { SimulationParameters, SimulationResult } from "../types";

const simulationChoices = [100, 500, 1000, 2500, 5000];
const currentYear = new Date().getFullYear();

export function FullSimulatorPage() {
  const [parameters, setParameters] = useState<SimulationParameters>(DEFAULT_SIMULATION_PARAMETERS);
  const [numSimulations, setNumSimulations] = useState(2500);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const worker = useSimulationWorker();

  const update = <Key extends keyof SimulationParameters>(key: Key, value: SimulationParameters[Key]) => {
    setParameters((current) => ({ ...current, [key]: value }));
  };
  const run = async () => {
    try {
      const snapshot = { ...parameters };
      const nextResult = await worker.runSimulation({ plan: fullSimulatorPlan(snapshot), numSimulations });
      setResult(nextResult);
    } catch {
      // The hook exposes a user-facing error state.
    }
  };
  const snapshotIsStale = result !== null && JSON.stringify(fullSimulatorPlan(parameters)) !== JSON.stringify(result.plan);

  return (
    <PageLayout title="Medicare and Medigap cost simulator" lead="Model a range of Medicare and Medigap costs over time, then use Monte Carlo sampling to understand likely lifetime expenses.">
      <section className="workspace">
        <aside className="control-panel" aria-label="Simulation controls">
          <h2>Scenario inputs</h2>
          <FieldGroup title="Base costs">
            <NumberField id="full-medigap" label="Medigap premium (monthly)" value={parameters.medigapPremium2026} onChange={(value) => update("medigapPremium2026", value)} min={50} max={500} step={5} />
            <NumberField id="full-deductible" label="Plan deductible (annual)" value={parameters.planDeductible2026} onChange={(value) => update("planDeductible2026", value)} min={100} max={1000} step={10} />
            <NumberField id="full-part-d" label="Part D premium (monthly)" value={parameters.partDPremium2026} onChange={(value) => update("partDPremium2026", value)} min={10} max={200} step={5} />
            <NumberField id="full-part-b" label="Part B deductible (annual)" value={parameters.partBDeductible2026} onChange={(value) => update("partBDeductible2026", value)} min={100} max={500} step={10} />
          </FieldGroup>
          <FieldGroup title="Annual growth rates">
            <RangeField id="full-medigap-growth" label="Medigap premium" value={parameters.medigapPremiumGrowthRate} onChange={(value) => update("medigapPremiumGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-deductible-growth" label="Plan deductible" value={parameters.planDeductibleGrowthRate} onChange={(value) => update("planDeductibleGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-part-d-growth" label="Part D premium" value={parameters.partDPremiumGrowthRate} onChange={(value) => update("partDPremiumGrowthRate", value)} max={0.15} format={percent} />
            <RangeField id="full-part-b-growth" label="Part B deductible" value={parameters.partBDeductibleGrowthRate} onChange={(value) => update("partBDeductibleGrowthRate", value)} max={0.15} format={percent} />
          </FieldGroup>
          <FieldGroup title="Simulation settings">
            <RangeField id="full-utilization" label="Probability of full utilization" value={parameters.percentSick} onChange={(value) => update("percentSick", value)} step={0.05} format={percent} tooltip="This is the estimated percentage that you use the plan. How you use the plan impacts copays and other costs." />
            <NumberField id="full-years" label="Simulation years" value={parameters.simulationYears} onChange={(value) => update("simulationYears", value)} min={5} max={50} step={5} />
            <NumberField id="full-start" label="Start year" value={parameters.startYear} onChange={(value) => update("startYear", value)} min={currentYear - 10} max={currentYear + 10} />
            <label className="field" htmlFor="full-simulations"><span>Number of simulations</span><select id="full-simulations" value={numSimulations} onChange={(event) => setNumSimulations(Number(event.currentTarget.value))}>{simulationChoices.map((value) => <option key={value} value={value}>{value.toLocaleString()}</option>)}</select></label>
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

function CostBreakdown({ plan }: { plan: ReturnType<typeof fullSimulatorPlan> }) {
  const rows = Array.from({ length: plan.simulationYears }, (_, offset) => ({
    year: plan.startYear + offset,
    medigapMonthly: plan.premium2026 * (1 + plan.premiumGrowthRate) ** offset,
    planDeductible: plan.planDeductible2026 * (1 + plan.planDeductibleGrowthRate) ** offset,
    partDMonthly: plan.partDPremium2026 * (1 + plan.partDPremiumGrowthRate) ** offset,
    partBDeductible: plan.partBDeductible2026 * (1 + plan.partBDeductibleGrowthRate) ** offset,
    total: annualCost(plan, offset, true),
  }));
  const value = (amount: number) => `$${amount.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  return <section className="table-card"><h2>Year-by-year cost breakdown</h2><div className="table-scroll"><table><thead><tr><th>Year</th><th>Medigap monthly</th><th>Plan deductible</th><th>Part D monthly</th><th>Part B deductible</th><th>Full-utilization annual cost</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><td>{row.year}</td><td>{value(row.medigapMonthly)}</td><td>{value(row.planDeductible)}</td><td>{value(row.partDMonthly)}</td><td>{value(row.partBDeductible)}</td><td>{value(row.total)}</td></tr>)}</tbody></table></div></section>;
}

export function PageLayout({ title, lead, children }: { title: string; lead: string; children: React.ReactNode }) {
  return <main className="page"><header className="page-header"><p className="eyebrow">Financial planning explorer</p><h1>{title}</h1><p>{lead}</p></header>{children}</main>;
}

function EmptyState() {
  return <section className="empty-state"><p className="eyebrow">Ready when you are</p><h2>Explore a cost scenario</h2><p>Adjust the assumptions, then run the simulation to see annual projections, lifetime-cost distribution, and percentiles.</p></section>;
}
