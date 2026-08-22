import type { ReactNode } from "react";

interface NumberFieldProps {
  id: string;
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  help?: string;
}

export function NumberField({ id, label, value, onChange, min, max, step = 1, help }: NumberFieldProps) {
  return (
    <label className="field" htmlFor={id}>
      <span>{label}</span>
      <input
        id={id}
        type="number"
        value={Number.isFinite(value) ? value : ""}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(event.currentTarget.valueAsNumber)}
      />
      {help && <small>{help}</small>}
    </label>
  );
}

interface RangeFieldProps extends NumberFieldProps {
  format?: (value: number) => string;
}

export function RangeField({ id, label, value, onChange, min = 0, max = 1, step = 0.01, help, format }: RangeFieldProps) {
  return (
    <div className="field range-field">
      <label htmlFor={id}>{label}</label>
      <div className="range-row">
        <input
          id={id}
          type="range"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(event) => onChange(event.currentTarget.valueAsNumber)}
        />
        <output htmlFor={id}>{format ? format(value) : value.toFixed(2)}</output>
      </div>
      {help && <small>{help}</small>}
    </div>
  );
}

export function FieldGroup({ title, children }: { title: string; children: ReactNode }) {
  return (
    <fieldset className="field-group">
      <legend>{title}</legend>
      <div className="field-grid">{children}</div>
    </fieldset>
  );
}

export function RunStatus({ isRunning, progress, label, error }: { isRunning: boolean; progress: number; label: string; error: string | null }) {
  if (error) return <p className="status error" role="alert">{error}</p>;
  if (!isRunning) return null;
  return (
    <div className="status" role="status" aria-live="polite">
      <div className="progress-label"><span>{label}</span><span>{Math.round(progress * 100)}%</span></div>
      <progress value={progress} max="1" />
    </div>
  );
}
