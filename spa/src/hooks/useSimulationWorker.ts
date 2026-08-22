import { useCallback, useEffect, useRef, useState } from "react";
import type { ComparisonRequest, ComparisonResult, SimulationRequest, SimulationResult, WorkerResponse } from "../types";

type JobKind = "simulation" | "comparison";

interface WorkerState {
  isRunning: boolean;
  progress: number;
  label: string;
  error: string | null;
}

export function useSimulationWorker() {
  const workerRef = useRef<Worker | null>(null);
  const activeRequestRef = useRef<string | null>(null);
  const [state, setState] = useState<WorkerState>({
    isRunning: false,
    progress: 0,
    label: "",
    error: null,
  });

  useEffect(() => {
    const worker = new Worker(new URL("../workers/simulation.worker.ts", import.meta.url), { type: "module" });
    workerRef.current = worker;
    return () => worker.terminate();
  }, []);

  const execute = useCallback(<TResult,>(
    kind: JobKind,
    request: SimulationRequest | ComparisonRequest,
  ): Promise<TResult> => new Promise((resolve, reject) => {
    const worker = workerRef.current;
    if (!worker) {
      reject(new Error("Simulation worker is unavailable."));
      return;
    }
    const requestId = crypto.randomUUID();
    activeRequestRef.current = requestId;
    setState({ isRunning: true, progress: 0, label: "Preparing simulation", error: null });

    worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
      const message = event.data;
      if (message.requestId !== activeRequestRef.current) return;
      if (message.type === "progress") {
        setState({
          isRunning: true,
          progress: message.total === 0 ? 0 : message.completed / message.total,
          label: `Simulating ${message.label}`,
          error: null,
        });
      } else if (message.type === "error") {
        activeRequestRef.current = null;
        setState({ isRunning: false, progress: 0, label: "", error: message.message });
        reject(new Error(message.message));
      } else if (message.type === "simulation-result" || message.type === "comparison-result") {
        activeRequestRef.current = null;
        setState({ isRunning: false, progress: 1, label: "Complete", error: null });
        resolve(message.result as TResult);
      }
    };

    if (kind === "simulation") {
      worker.postMessage({ type: "run-simulation", requestId, request: request as SimulationRequest });
    } else {
      worker.postMessage({ type: "run-comparison", requestId, request: request as ComparisonRequest });
    }
  }), []);

  return {
    ...state,
    runSimulation: (request: SimulationRequest) => execute<SimulationResult>("simulation", request),
    runComparison: (request: ComparisonRequest) => execute<ComparisonResult>("comparison", request),
  };
}
