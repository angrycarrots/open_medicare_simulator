import { useMemo, useState } from "react";
import { FieldGroup, NumberField, RangeField, RunStatus } from "../components/Fields";
import { SimulationSummary } from "../components/Charts";
import { percent } from "../lib/format";
import { annualCost } from "../lib/simulation";
import {
  DEFAULT_PLAN_COST_SETTINGS,
  normalizePlanCostSettings,
  PLAN_COST_SETTINGS_STORAGE_KEY,
  PREDEFINED_PLANS,
  withoutPartD,
  withPlanCostSettings,
  type PlanCostSettings,
  type PlanCostSettingsById,
  type PredefinedPlanChoice,
} from "../lib/plans";
import { useSimulationSettings } from "../hooks/useSimulationSettings";
import { useSimulationWorker } from "../hooks/useSimulationWorker";
import { usePersistentState } from "../hooks/usePersistentState";
import type { PlanDefinition, SimulationResult } from "../types";
import { PageLayout } from "./FullSimulatorPage";

const currentYear = new Date().getFullYear();

const PAGE_CONTENT: Record<PredefinedPlanChoice, { title: string; lead: string }> = {
  "plan-g": {
    title: "Plan G",
    lead: "Explore Plan G costs over time using your plan assumptions and the universal simulation settings.",
  },
  "plan-hdg": {
    title: "Plan G HD",
    lead: "Explore high-deductible Plan G costs over time using your plan assumptions and the universal simulation settings.",
  },
  "plan-n": {
    title: "Plan N",
    lead: "Explore Plan N costs over time using your plan assumptions and the universal simulation settings.",
  },
};

export function PlanPage({ planId }: { planId: PredefinedPlanChoice }) {
  const [storedPlanCostSettings, setStoredPlanCostSettings] = usePersistentState<PlanCostSettingsById>(
    PLAN_COST_SETTINGS_STORAGE_KEY,
    DEFAULT_PLAN_COST_SETTINGS,
  );
  const planCostSettings = useMemo(
    () => normalizePlanCostSettings(storedPlanCostSettings),
    [storedPlanCostSettings],
  );
  const { settings: simulationSettings, updateSetting } = useSimulationSettings();
  const [result, setResult] = useState<SimulationResult | null>(null);
  const worker = useSimulationWorker();
  const page = PAGE_CONTENT[planId];

  const selectedPlan = useMemo(() => {
    const plan = PREDEFINED_PLANS[planId]({
      percentSick: simulationSettings.percentSick,
      simulationYears: simulationSettings.simulationYears,
      startYear: simulationSettings.startYear,
    });
    return withoutPartD(withPlanCostSettings(plan, planCostSettings[planId]));
  }, [planId, planCostSettings, simulationSettings]);

  const updatePlanCost = <Key extends keyof PlanCostSettings>(
    key: Key,
    value: PlanCostSettings[Key],
  ) => {
    setStoredPlanCostSettings((storedSettings) => {
      const allSettings = normalizePlanCostSettings(storedSettings);
      return {
        ...allSettings,
        [planId]: { ...allSettings[planId], [key]: value },
      };
    });
  };

  const run = async () => {
    try {
      setResult(await worker.runSimulation({
        plan: selectedPlan,
        numSimulations: simulationSettings.numSimulations,
      }));
    } catch {
      // The worker hook displays the user-facing error.
    }
  };

  const stale = result !== null && (
    JSON.stringify(selectedPlan) !== JSON.stringify(result.plan)
    || simulationSettings.numSimulations !== result.numSimulations
  );
  const pageResult = result?.plan.id === planId ? result : null;

  return (
    <PageLayout title={page.title} lead={page.lead}>
      <section className="workspace">
        <aside className="control-panel" aria-label={`${page.title} simulation controls`}>
          <h2>{page.title} settings</h2>
          <PlanCostFields planId={planId} settings={planCostSettings[planId]} update={updatePlanCost} />
          <PlanGrowthFields planId={planId} settings={planCostSettings[planId]} update={updatePlanCost} />
          <FieldGroup title="Simulation settings">
            <RangeField id={`${planId}-utilization`} label="Probability of full utilization" value={simulationSettings.percentSick} onChange={(value) => updateSetting("percentSick", value)} step={0.05} format={percent} tooltip="This is the estimated percentage that you use the plan. How you use the plan impacts copays and other costs." />
            <NumberField id={`${planId}-simulations`} label="Number of simulations" value={simulationSettings.numSimulations} onChange={(value) => updateSetting("numSimulations", value)} min={100} max={10000} step={100} />
            <NumberField id={`${planId}-years`} label="Simulation years" value={simulationSettings.simulationYears} onChange={(value) => updateSetting("simulationYears", value)} min={10} max={50} step={5} />
            <NumberField id={`${planId}-start`} label="Start year" value={simulationSettings.startYear} onChange={(value) => updateSetting("startYear", value)} min={currentYear - 10} max={currentYear + 10} />
          </FieldGroup>
          <button className="primary-button" onClick={run} disabled={worker.isRunning}>{worker.isRunning ? "Running simulation…" : `Run ${page.title} simulation`}</button>
          <RunStatus {...worker} />
        </aside>
        <div className="analysis-panel">
          {pageResult && stale && <p className="status warning">Inputs have changed. Results below remain labeled with the plan that generated them.</p>}
          <PlanSummary plan={pageResult?.plan ?? selectedPlan} />
          <HealthySickTable plan={pageResult?.plan ?? selectedPlan} />
          {pageResult && <SimulationSummary result={pageResult} />}
        </div>
      </section>
    </PageLayout>
  );
}

function PlanCostFields({ planId, settings, update }: { planId: PredefinedPlanChoice; settings: PlanCostSettings; update: <Key extends keyof PlanCostSettings>(key: Key, value: PlanCostSettings[Key]) => void }) {
  return <FieldGroup title="Plan parameters">
    <NumberField id={`${planId}-premium`} label="Monthly premium" value={settings.monthlyPremium} onChange={(value) => update("monthlyPremium", value)} min={1} max={1000} step={1} />
    <NumberField id={`${planId}-deductible`} label="Plan deductible (annual)" value={settings.planDeductible} onChange={(value) => update("planDeductible", value)} min={0} max={10000} step={1} />
    <NumberField id={`${planId}-office-copay`} label="Office visit copay" value={settings.officeVisitCopay} onChange={(value) => update("officeVisitCopay", value)} min={0} max={500} step={1} help="Applied to the plan's assumed 12 office visits per year." />
  </FieldGroup>;
}

function PlanGrowthFields({ planId, settings, update }: { planId: PredefinedPlanChoice; settings: PlanCostSettings; update: <Key extends keyof PlanCostSettings>(key: Key, value: PlanCostSettings[Key]) => void }) {
  return <FieldGroup title="Annual growth rates">
    <RangeField id={`${planId}-premium-growth`} label="Plan premium" value={settings.planPremiumGrowthRate} onChange={(value) => update("planPremiumGrowthRate", value)} max={0.2} format={percent} />
    <RangeField id={`${planId}-deductible-growth`} label="Plan deductible" value={settings.planDeductibleGrowthRate} onChange={(value) => update("planDeductibleGrowthRate", value)} max={0.2} format={percent} />
  </FieldGroup>;
}

function PlanSummary({ plan }: { plan: PlanDefinition }) {
  return <section className="summary-card"><div><p className="eyebrow">Selected plan</p><h2>{plan.name}</h2><p>{percent(plan.percentSick)} probability of full utilization · {plan.simulationYears} years from {plan.startYear}</p></div><div className="plan-details"><div><span>Monthly premium</span><strong>${plan.premium2026.toFixed(2)}</strong><small>{percent(plan.premiumGrowthRate)} annual growth</small></div><div><span>Plan deductible</span><strong>${plan.planDeductible2026.toFixed(2)}</strong><small>{percent(plan.planDeductibleGrowthRate)} annual growth</small></div><div><span>Office visit copay</span><strong>${plan.specialistCopay2026?.toFixed(2)}</strong><small>{plan.specialistVisitsPerYear} assumed visits per year</small></div></div></section>;
}

function HealthySickTable({ plan }: { plan: PlanDefinition }) {
  const rows = Array.from({ length: Math.min(5, plan.simulationYears) }, (_, offset) => ({ year: plan.startYear + offset, healthy: annualCost(plan, offset, false), sick: annualCost(plan, offset, true) }));
  const money = (value: number) => value.toLocaleString("en-US", { style: "currency", currency: "USD" });
  return <section className="table-card"><h2>Cost projections by year</h2><p className="table-description">Office visit copays are included in both healthy and full-utilization projections.</p><table><thead><tr><th>Year</th><th>Healthy annual cost</th><th>Full-utilization annual cost</th></tr></thead><tbody>{rows.map((row) => <tr key={row.year}><td>{row.year}</td><td>{money(row.healthy)}</td><td>{money(row.sick)}</td></tr>)}</tbody></table></section>;
}
