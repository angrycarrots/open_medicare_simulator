/// <reference types="vite/client" />

declare module "plotly.js-cartesian-dist-min" {
  import type { PlotlyHTMLElement } from "plotly.js";

  const Plotly: {
    react: (element: PlotlyHTMLElement, data: unknown[], layout?: unknown, config?: unknown) => Promise<PlotlyHTMLElement>;
    purge: (element: PlotlyHTMLElement) => void;
  };
  export default Plotly;
}
