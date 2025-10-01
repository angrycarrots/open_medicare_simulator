# Medicare Plan Simulator - Applications

This directory contains multiple Streamlit applications for the Medicare Plan Simulator, each designed for different use cases.

## Available Applications

### 1. Plan Selection & Simulation (`app_updated.py`)
**Best for: Individual plan analysis and custom plan creation**

Features:
- Select from predefined plans (Plan-G, Plan-HDG)
- Create custom plans with your own parameters
- Run Monte Carlo simulations for any plan
- View detailed cost projections and statistics
- Interactive parameter adjustment

**To run:**
```bash
uv run streamlit run app_updated.py
```

### 2. Plan Comparison Tool (`app_comparison.py`)
**Best for: Comparing two plans side by side**

Features:
- Compare any two plans (Plan-G vs Plan-HDG)
- Side-by-side parameter comparison
- Visual cost comparison charts
- Statistical comparison with Monte Carlo simulation
- Percentile analysis comparison

**To run:**
```bash
uv run streamlit run app_comparison.py
```

### 3. Original App (`app.py`)
**Legacy version with manual parameter input**

Features:
- Manual parameter input for all values
- Original simulation structure
- Good for understanding the underlying parameters

**To run:**
```bash
uv run streamlit run app.py
```

### 4. Launcher Script (`launch_app.py`)
**Easy way to choose which app to run**

Features:
- Interactive menu to select which app to launch
- Descriptions of each app's purpose

**To run:**
```bash
uv run python launch_app.py
```

## Plan Types Available

### Plan-G (Original Medigap Plan N)
- **Premium**: $155/month (2026)
- **Premium Growth**: 7% annually
- **Deductible**: $257/year (2026)
- **Deductible Growth**: 6% annually
- **Part D**: $49/month (2026), 6% growth
- **Part B**: $210/year (2026), 6% growth

### Plan-HDG (High Deductible Plan G)
- **Premium**: $40/month (2026)
- **Premium Growth**: 7% annually
- **Deductible**: $2800/year (2026)
- **Deductible Growth**: 6% annually
- **Part D**: $49/month (2026), 6% growth (same as Plan-G)
- **Part B**: $210/year (2026), 6% growth (same as Plan-G)

## Key Features

### Monte Carlo Simulation
- Runs thousands of simulations to project costs
- Accounts for probabilistic health events
- Provides statistical confidence intervals
- Shows cost distributions and percentiles

### Interactive Interface
- Real-time parameter adjustment
- Visual charts and graphs
- Downloadable results
- Responsive design

### Plan Comparison
- Side-by-side parameter comparison
- Cost difference analysis
- Statistical significance testing
- Visual comparison charts

## Usage Tips

1. **Start with Plan Selection** (`app_updated.py`) to understand individual plans
2. **Use Plan Comparison** (`app_comparison.py`) to decide between options
3. **Adjust simulation parameters** based on your risk tolerance
4. **Consider your health status** when setting the "Percent Sick" parameter
5. **Review percentiles** to understand worst-case scenarios

## Technical Notes

- All apps use the new Plan structure for consistency
- Monte Carlo simulations use numpy for statistical calculations
- Charts are created with Plotly for interactivity
- Data is displayed using Pandas DataFrames
- All apps are responsive and work on mobile devices

## Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- NumPy
- The medigap package (included in src/)

## Getting Started

1. Install dependencies: `uv sync`
2. Run the launcher: `uv run python launch_app.py`
3. Choose your preferred app
4. Start exploring different Medicare plans!

