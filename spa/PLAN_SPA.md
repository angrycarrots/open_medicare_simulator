# TypeScript SPA Implementation Plan

## Objective

Port the recommended three-page Streamlit application into an isolated browser-only React, Vite, and TypeScript SPA. Keep the Python implementation unchanged and contain all SPA source, dependencies, tests, and build output under `spa/`.

## Architecture

- Use hash routes for Full Simulator, Single Plan Simulator, and Plan Comparison, allowing deployment to any static host without server-side route rewrites.
- Keep cost formulas and validation in framework-independent TypeScript modules. Port compound growth, predefined plans, custom plans, specialist copays, simulation statistics, population standard deviation, and linear percentiles.
- Execute simulations in a Web Worker. Aggregate annual results during execution and retain only lifetime-cost samples needed for histograms and percentiles.
- Use Plotly charts and client-side CSV downloads. Do not persist parameters or results outside the current browser session.

## Interfaces

- `SimulationParameters` represents the Full Simulator form.
- `PlanDefinition` represents Plan G, High Deductible Plan G, Plan N, or a custom plan.
- `SimulationRequest`, `ComparisonRequest`, `SimulationResult`, `ComparisonResult`, and `YearStatistics` define computation inputs and outputs.
- Worker requests and responses include a request ID, progress events, successful result events, and error events so stale results cannot overwrite the active view.
- Production uses browser randomness; tests can inject a seeded random source.

## Implementation and Verification

1. Scaffold the self-contained Vite project and static-relative build configuration.
2. Port and test models, validation, annual-cost formulas, aggregation, and percentile behavior.
3. Add the Web Worker and the three Streamlit-equivalent workflows.
4. Add responsive controls, result snapshots, tables, Plotly visualizations, and CSV export.
5. Verify TypeScript tests and a production build; confirm no Python file, dependency, entry point, or behavior changes.

## Scope Decisions

- “Full functionality” means the three-page Streamlit web app, not Tkinter or CLI-only workflows.
- The app is browser-only: no database, authentication, analytics, API, or provider-specific deployment configuration.
- Plan N healthy and full-utilization projections both include specialist copays, correcting the prior display inconsistency.
- Unseeded browser results need mathematical parity with Python distributions, not exact sequence-by-sequence random parity.
