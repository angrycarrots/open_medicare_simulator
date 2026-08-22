import { useEffect, useState, type Dispatch, type SetStateAction } from "react";

function readValue<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;

  try {
    const stored = window.localStorage.getItem(key);
    return stored === null ? fallback : JSON.parse(stored) as T;
  } catch {
    return fallback;
  }
}

/** Keeps non-sensitive simulator preferences on this browser and device. */
export function usePersistentState<T>(key: string, fallback: T): [T, Dispatch<SetStateAction<T>>] {
  const [value, setValue] = useState<T>(() => readValue(key, fallback));

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Storage may be disabled or full. The simulator remains usable in memory.
    }
  }, [key, value]);

  useEffect(() => {
    const syncFromAnotherTab = (event: StorageEvent) => {
      if (event.key !== key || event.newValue === null) return;
      try {
        setValue(JSON.parse(event.newValue) as T);
      } catch {
        // Ignore malformed values and keep the current in-memory settings.
      }
    };
    window.addEventListener("storage", syncFromAnotherTab);
    return () => window.removeEventListener("storage", syncFromAnotherTab);
  }, [key]);

  return [value, setValue];
}
