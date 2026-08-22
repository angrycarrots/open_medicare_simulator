import { runComparison, runSimulation } from "../lib/simulation";
import type { WorkerRequest, WorkerResponse } from "../types";

const workerScope = self as unknown as {
  onmessage: ((event: MessageEvent<WorkerRequest>) => void) | null;
  postMessage: (message: WorkerResponse) => void;
};

workerScope.onmessage = (event: MessageEvent<WorkerRequest>) => {
  const message = event.data;
  try {
    if (message.type === "run-simulation") {
      const result = runSimulation(message.request, undefined, (completed, total) => {
        workerScope.postMessage({
          type: "progress",
          requestId: message.requestId,
          completed,
          total,
          label: message.request.plan.name,
        } satisfies WorkerResponse);
      });
      workerScope.postMessage({
        type: "simulation-result",
        requestId: message.requestId,
        result,
      } satisfies WorkerResponse);
      return;
    }

    const result = runComparison(
      message.request.plan1,
      message.request.plan2,
      message.request.numSimulations,
      message.request.randomSeed,
      (completed, total, label) => {
        workerScope.postMessage({
          type: "progress",
          requestId: message.requestId,
          completed,
          total,
          label,
        } satisfies WorkerResponse);
      },
    );
    workerScope.postMessage({
      type: "comparison-result",
      requestId: message.requestId,
      result,
    } satisfies WorkerResponse);
  } catch (error) {
    workerScope.postMessage({
      type: "error",
      requestId: message.requestId,
      message: error instanceof Error ? error.message : "The simulation could not be completed.",
    } satisfies WorkerResponse);
  }
};
