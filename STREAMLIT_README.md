# Medicare/Medigap Cost Simulator - Streamlit App

This Streamlit application provides an interactive web interface for the Medicare/Medigap Monte Carlo simulation.

## Features

- **Interactive Parameter Controls**: Adjust all simulation parameters through an intuitive sidebar interface
- **Real-time Cost Projections**: View year-by-year cost breakdowns and projections
- **Monte Carlo Simulation**: Run thousands of simulations to account for uncertainty
- **Interactive Visualizations**: 
  - Cost projection charts with confidence intervals
  - Lifetime cost distribution histograms
  - Statistical summaries and percentiles
- **Data Export**: Download simulation results as CSV files

## Installation

1. Install dependencies using uv:
```bash
uv sync
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

## Running the Application

To start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`.

## Usage

1. **Adjust Parameters**: Use the sidebar to modify:
   - Base costs for 2026 (premiums, deductibles)
   - Growth rates for each cost component
   - Simulation settings (years, probability of utilization)
   - Number of Monte Carlo simulations

2. **Run Simulation**: Click the "🚀 Run Simulation" button to execute the Monte Carlo simulation

3. **View Results**: The application will display:
   - Year-by-year cost breakdown table
   - Key statistics (mean, median, min, max lifetime costs)
   - Interactive cost projection charts
   - Lifetime cost distribution histogram
   - Cost percentiles analysis

4. **Export Data**: Download the cost projections as a CSV file for further analysis

## Parameters Explained

- **Medigap Premium**: Monthly premium for Medigap Plan N
- **Plan Deductible**: Annual deductible for the Medigap plan
- **Part D Premium**: Monthly premium for Medicare Part D prescription drug coverage
- **Part B Deductible**: Annual deductible for Medicare Part B
- **Growth Rates**: Annual percentage increase for each cost component
- **Probability of Full Utilization**: Chance of being "sick" (using full benefits) in any given year
- **Simulation Years**: Number of years to project costs forward
- **Number of Simulations**: How many Monte Carlo runs to perform (more = more accurate but slower)

## Technical Details

- Built with Streamlit for the web interface
- Uses Plotly for interactive visualizations
- Integrates with the existing Monte Carlo simulation engine
- Supports real-time parameter adjustment and immediate re-simulation
- Responsive design that works on desktop and mobile devices

## Troubleshooting

If you encounter issues:

1. **Port already in use**: Streamlit will automatically find an available port
2. **Browser doesn't open**: Navigate manually to the URL shown in the terminal
3. **Slow performance**: Reduce the number of simulations for faster results
4. **Memory issues**: Close other applications or reduce simulation parameters

## Dependencies

- streamlit>=1.28.0
- plotly>=5.15.0
- numpy>=1.24.0
- matplotlib>=3.7.0
- pandas (included with streamlit)
