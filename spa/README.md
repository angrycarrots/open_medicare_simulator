# Medicare Cost Simulator SPA

This directory is an isolated React and TypeScript single-page application that ports the recommended Streamlit web experience. It runs all calculations in the browser and needs no Python process, server, database, or user account.

## Features

- Full Medicare/Medigap scenario simulator with CSV export.
- Single-plan simulator for Plan G, High Deductible Plan G, Plan N, and custom plans.
- Side-by-side plan comparison using independent Monte Carlo samples.
- Web Worker execution, so the UI remains interactive through the maximum 10,000-simulation workload.
- Static, relative-path build suitable for root or subpath hosting.

## Development

Run the commands inside this directory:

```sh
# Node 20 or later
npm install
npm run dev
```

Use `npm test` for the TypeScript domain tests and `npm run build` to produce static files in `dist/`. Deploy the contents of `dist/` to any static web host.

## Calculation notes

Each simulated year always includes annualized Medigap and Part D premiums. A full-utilization year adds the plan and Part B deductibles. Plan N also includes the configured annual specialist copays in both healthy and full-utilization outcomes. Growth compounds annually. Statistics use a population standard deviation and percentile interpolation compatible with NumPy's default linear method.

Results are educational estimates only and are not financial, insurance, or medical advice.
