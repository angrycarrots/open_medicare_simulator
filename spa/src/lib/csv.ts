import type { SimulationResult } from "../types";

export function simulationCsv(result: SimulationResult): string {
  const header = "Year,Mean Cost,Standard Deviation,Minimum Cost,Maximum Cost";
  const rows = result.statistics.meanCosts.map((meanCost, index) =>
    [
      result.plan.startYear + index,
      meanCost,
      result.statistics.stdCosts[index],
      result.statistics.minCosts[index],
      result.statistics.maxCosts[index],
    ].join(","),
  );
  return [header, ...rows].join("\n");
}

export function downloadCsv(filename: string, contents: string): void {
  const blob = new Blob([contents], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
