import { usePersistentState } from "./usePersistentState";

export interface SimulationSettings {
  percentSick: number;
  numSimulations: number;
  simulationYears: number;
  startYear: number;
}

const currentYear = new Date().getFullYear();

export const DEFAULT_SIMULATION_SETTINGS: SimulationSettings = {
  percentSick: 0.2,
  numSimulations: 2500,
  simulationYears: 25,
  startYear: currentYear,
};

export const SIMULATION_SETTINGS_STORAGE_KEY = "medicare-simulator.settings.v1";

/** Simulation settings shared by every simulator and plan page. */
export function useSimulationSettings() {
  const [settings, setSettings] = usePersistentState<SimulationSettings>(
    SIMULATION_SETTINGS_STORAGE_KEY,
    DEFAULT_SIMULATION_SETTINGS,
  );

  const updateSetting = <Key extends keyof SimulationSettings>(
    key: Key,
    value: SimulationSettings[Key],
  ) => {
    setSettings((current) => ({ ...current, [key]: value }));
  };

  return { settings, updateSetting };
}
