import { useEffect, useRef } from "react";
import type { CSSProperties } from "react";
import type { PlotlyHTMLElement } from "plotly.js";
import Plotly from "plotly.js-cartesian-dist-min";

interface PlotProps {
  data: unknown[];
  layout?: unknown;
  config?: unknown;
  style?: CSSProperties;
}

/** A small React wrapper around Plotly's browser API without the full Plotly dependency. */
export function Plot({ data, layout, config, style }: PlotProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return undefined;
    const plotElement = element as unknown as PlotlyHTMLElement;
    void Plotly.react(plotElement, data, layout, config);
    return () => Plotly.purge(plotElement);
  }, [data, layout, config]);

  return <div ref={containerRef} style={style} />;
}
