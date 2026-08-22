import { describe, expect, it } from "vitest";
import { simulationCsv } from "./csv";
import { createPlanG } from "./plans";

describe("simulation CSV export", () => {
  it("exports the annual projection columns and start-year offsets", () => {
    const csv = simulationCsv({
      plan: createPlanG({ startYear: 2026, simulationYears: 2 }),
      numSimulations: 100,
      lifetimeCosts: [1, 2],
      statistics: {
        meanCosts: [2448, 2600],
        stdCosts: [0, 100],
        minCosts: [2448, 2500],
        maxCosts: [2448, 2700],
        totalCosts: [244800, 260000],
      },
    });
    expect(csv).toBe([
      "Year,Mean Cost,Standard Deviation,Minimum Cost,Maximum Cost",
      "2026,2448,0,2448,2448",
      "2027,2600,100,2500,2700",
    ].join("\n"));
  });
});
