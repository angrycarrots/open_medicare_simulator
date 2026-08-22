import { Plot } from "./Plot";
import type { ComparisonResult, SimulationResult } from "../types";
import { currency, percent } from "../lib/format";
import { mean, percentile, populationStandardDeviation } from "../lib/simulation";

const chartConfig = { displaylogo: false, responsive: true };

function yearsFor(result: SimulationResult): number[] {
  return Array.from({ length: result.plan.simulationYears }, (_, index) => result.plan.startYear + index);
}

export function SimulationSummary({ result, includeDownload, onDownload }: {
  result: SimulationResult;
  includeDownload?: boolean;
  onDownload?: () => void;
}) {
  const values = result.lifetimeCosts;
  const lifetimeMean = mean(values);
  const lifetimeStandardDeviation = populationStandardDeviation(values);
  const years = yearsFor(result);
  const upper = result.statistics.meanCosts.map((value, index) => value + result.statistics.stdCosts[index]);
  const lower = result.statistics.meanCosts.map((value, index) => value - result.statistics.stdCosts[index]);
  const percentiles = [5, 10, 25, 50, 75, 90, 95];

  return (
    <section className="results" aria-label={`${result.plan.name} results`}>
      <div className="results-heading">
        <div>
          <p className="eyebrow">Completed scenario</p>
          <h2>{result.plan.name}</h2>
          <p>{result.numSimulations.toLocaleString()} simulations · {result.plan.simulationYears} years beginning {result.plan.startYear}</p>
        </div>
        {includeDownload && <button className="secondary-button" onClick={onDownload}>Download cost projections CSV</button>}
      </div>
      <div className="metric-grid">
        <Metric label="Mean lifetime cost" value={currency(lifetimeMean)} detail={`± ${currency(lifetimeStandardDeviation)}`} />
        <Metric label="Median lifetime cost" value={currency(percentile(values, 50))} />
        <Metric label="Minimum lifetime cost" value={currency(Math.min(...values))} />
        <Metric label="Maximum lifetime cost" value={currency(Math.max(...values))} />
      </div>
      <div className="chart-grid">
        <ChartCard title="Annual cost projection">
          <Plot
            data={[
              { x: years, y: result.statistics.meanCosts, type: "scatter", mode: "lines+markers", name: "Mean cost", line: { color: "#156b75", width: 3 } },
              { x: [...years, ...years.slice().reverse()], y: [...upper, ...lower.slice().reverse()], type: "scatter", mode: "lines", fill: "toself", fillcolor: "rgba(21, 107, 117, 0.16)", line: { color: "rgba(0,0,0,0)" }, name: "±1 standard deviation", hoverinfo: "skip" },
            ]}
            layout={{ autosize: true, margin: { l: 62, r: 20, t: 14, b: 50 }, xaxis: { title: "Year" }, yaxis: { title: "Annual cost", tickprefix: "$", tickformat: ",.0f" }, hovermode: "x unified", paper_bgcolor: "transparent", plot_bgcolor: "transparent", legend: { orientation: "h", y: -0.25 } }}
            config={chartConfig}
            style={{ width: "100%", height: "330px" }}
          />
        </ChartCard>
        <ChartCard title="Lifetime cost distribution">
          <Plot
            data={[{ x: values, type: "histogram", nbinsx: 50, marker: { color: "#6096b4" }, opacity: 0.8, name: "Lifetime cost" }] as any}
            layout={{ autosize: true, margin: { l: 62, r: 20, t: 14, b: 50 }, xaxis: { title: "Lifetime cost", tickprefix: "$", tickformat: ",.0f" }, yaxis: { title: "Frequency" }, paper_bgcolor: "transparent", plot_bgcolor: "transparent", shapes: [{ type: "line", x0: lifetimeMean, x1: lifetimeMean, y0: 0, y1: 1, yref: "paper", line: { color: "#c3423f", dash: "dash", width: 2 } }], annotations: [{ x: lifetimeMean, y: 1, yref: "paper", text: `Mean ${currency(lifetimeMean)}`, showarrow: false, yanchor: "bottom", font: { color: "#a13331" } }] }}
            config={chartConfig}
            style={{ width: "100%", height: "330px" }}
          />
        </ChartCard>
      </div>
      <div className="table-card">
        <h3>Lifetime cost percentiles</h3>
        <table>
          <thead><tr><th>Percentile</th><th>Lifetime cost</th></tr></thead>
          <tbody>{percentiles.map((value) => <tr key={value}><td>{value}%</td><td>{currency(percentile(values, value))}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}

export function ComparisonSummary({ result }: { result: ComparisonResult }) {
  const firstMean = mean(result.plan1.lifetimeCosts);
  const secondMean = mean(result.plan2.lifetimeCosts);
  return (
    <section className="results" aria-label="Plan comparison results">
      <div className="results-heading"><div><p className="eyebrow">Completed comparison</p><h2>Lifetime cost comparison</h2></div></div>
      <div className="metric-grid">
        <Metric label={`${result.plan1.plan.name} mean`} value={currency(firstMean)} detail={`± ${currency(populationStandardDeviation(result.plan1.lifetimeCosts))}`} />
        <Metric label={`${result.plan2.plan.name} mean`} value={currency(secondMean)} detail={`± ${currency(populationStandardDeviation(result.plan2.lifetimeCosts))}`} />
        <Metric label="Mean difference" value={currency(result.meanDifference)} detail={`${result.plan2.plan.name} minus ${result.plan1.plan.name}`} />
        <Metric label="Difference variability" value={currency(result.standardDeviationDifference)} />
      </div>
      <div className="chart-grid">
        <ChartCard title="Lifetime cost distributions">
          <Plot
            data={[
              { x: result.plan1.lifetimeCosts, type: "histogram", nbinsx: 50, name: result.plan1.plan.name, marker: { color: "#156b75" }, opacity: 0.65 },
              { x: result.plan2.lifetimeCosts, type: "histogram", nbinsx: 50, name: result.plan2.plan.name, marker: { color: "#c3423f" }, opacity: 0.6 },
            ] as any}
            layout={{ autosize: true, barmode: "overlay", margin: { l: 62, r: 20, t: 14, b: 50 }, xaxis: { title: "Lifetime cost", tickprefix: "$", tickformat: ",.0f" }, yaxis: { title: "Frequency" }, paper_bgcolor: "transparent", plot_bgcolor: "transparent", legend: { orientation: "h", y: -0.25 } }}
            config={chartConfig}
            style={{ width: "100%", height: "330px" }}
          />
        </ChartCard>
        <div className="table-card comparison-percentiles">
          <h3>Percentile comparison</h3>
          <table>
            <thead><tr><th>Percentile</th><th>{result.plan1.plan.name}</th><th>{result.plan2.plan.name}</th><th>Difference</th></tr></thead>
            <tbody>{[5, 10, 25, 50, 75, 90, 95].map((value) => {
              const first = percentile(result.plan1.lifetimeCosts, value);
              const second = percentile(result.plan2.lifetimeCosts, value);
              return <tr key={value}><td>{value}%</td><td>{currency(first)}</td><td>{currency(second)}</td><td className={second - first <= 0 ? "saving" : "cost"}>{currency(second - first)}</td></tr>;
            })}</tbody>
          </table>
        </div>
      </div>
      <p className="comparison-note">A negative difference means {result.plan2.plan.name} has the lower simulated cost. Both plans use independent random draws, matching the original web application.</p>
    </section>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="chart-card"><h3>{title}</h3>{children}</div>;
}

function Metric({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong>{detail && <small>{detail}</small>}</div>;
}

export function UtilizationLabel({ plan }: { plan: SimulationResult["plan"] }) {
  return <span>{percent(plan.percentSick)} probability of full utilization</span>;
}
