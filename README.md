# Medicare/Medigap Monte Carlo Simulation

A Python application that executes a Monte Carlo simulation of medical costs incurred over a 25-year period (2026-2050) for Medicare Parts A, B, D, and Medigap Plan N.

## Features

- **Monte Carlo Simulation**: Probabilistic modeling of medical cost projections
- **Comprehensive Cost Analysis**: Includes premiums, deductibles, and utilization patterns
- **Visualization**: Multiple chart types including expenditure projections and cost distributions
- **Configurable Parameters**: Easy customization of cost bases and growth rates
- **Graphical User Interface**: User-friendly tkinter GUI with interactive controls
- **Test-Driven Development**: Comprehensive test suite with 90%+ coverage
- **Object-Oriented Design**: Clean, maintainable code architecture

## Installation

### Prerequisites

- Python 3.13 or higher
- uv package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd medigap
```

2. Create and activate virtual environment:
```bash
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

## Usage

### Basic Usage

#### Command Line Interface

Run the simulation with default parameters:

```bash
python main.py
```

#### Graphical User Interface

For a more user-friendly experience, use the GUI application:

```bash
python gui.py
```

The GUI provides:
- Interactive parameter input with validation
- Real-time simulation progress
- Multiple chart types (expenditure, lifetime distribution, dashboard)
- Export functionality for results and charts
- Tabbed interface for easy navigation

This will:
- Run 1,000 Monte Carlo simulations
- Display comprehensive cost statistics table with minimum, maximum, and median values
- Show detailed year-by-year cost breakdown with all premium and deductible components
- Display year-by-year cost projections with confidence intervals
- Generate three visualization files:
  - `medicare_cost_projection.png` - Expenditure chart with confidence intervals
  - `lifetime_cost_distribution.png` - Histogram of lifetime costs
  - `medicare_analysis_dashboard.png` - Comprehensive dashboard

### Custom Parameters

You can customize simulation parameters by modifying the `SimulationParameters` class:

```python
from src.medigap.models.simulation_parameters import SimulationParameters
from src.medigap.simulation.monte_carlo import MonteCarloSimulation

# Create custom parameters
params = SimulationParameters(
    medigap_premium_2026=200.0,  # Higher base premium
    medigap_premium_growth_rate=0.05,  # Lower growth rate
    percent_sick=0.15  # Lower utilization rate
)

# Run simulation
simulation = MonteCarloSimulation(params)
results = simulation.run_comprehensive_simulation(1000)
```

### Programmatic Usage

```python
from src.medigap.models.simulation_parameters import SimulationParameters
from src.medigap.simulation.monte_carlo import MonteCarloSimulation
from src.medigap.visualization.charts import Visualization

# Initialize components
params = SimulationParameters()
simulation = MonteCarloSimulation(params)
visualization = Visualization()

# Run simulation
results = simulation.run_comprehensive_simulation(1000)

# Create custom visualizations
years = list(range(2026, 2051))
stats = results['statistics']

visualization.create_expenditure_chart(
    years, 
    stats['mean_costs'], 
    stats['std_costs'],
    title="Custom Medicare Cost Projection"
)
```

## Default Parameters

The simulation uses the following default parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Medigap Premium (2026) | $155.00/month | Base Medigap Plan N premium |
| Medigap Premium Growth Rate | 7.0% | Annual premium growth |
| Plan Deductible (2026) | $257.00/year | Base plan deductible |
| Plan Deductible Growth Rate | 6.0% | Annual deductible growth |
| Part D Premium (2026) | $49.00/month | Base Part D premium |
| Part D Premium Growth Rate | 6.0% | Annual Part D premium growth |
| Part B Deductible (2026) | $210.00/year | Base Part B deductible |
| Part B Deductible Growth Rate | 6.0% | Annual Part B deductible growth |
| Percent Sick | 20.0% | Probability of full utilization |
| Simulation Years | 25 | Years to simulate (2026-2050) |

## Simulation Logic

For each year in the simulation:

1. **Calculate Current Costs**: Apply growth rates to base costs
2. **Generate Random Number**: Random value between 0 and 1
3. **Determine Utilization**: If random number < Percent Sick, incur full deductibles
4. **Calculate Total Cost**: Premiums + deductibles (if sick)
5. **Record Results**: Store costs and utilization for analysis

## Project Structure

```
medigap/
├── src/
│   └── medigap/
│       ├── models/
│       │   └── simulation_parameters.py    # Configuration class
│       ├── simulation/
│       │   ├── monte_carlo.py             # Main simulation engine
│       │   └── cost_calculator.py         # Cost calculation utilities
│       └── visualization/
│           └── charts.py                  # Chart generation
├── tests/
│   ├── test_simulation_parameters.py      # Parameter validation tests
│   ├── test_cost_calculator.py           # Cost calculation tests
│   ├── test_monte_carlo.py               # Simulation engine tests
│   ├── test_visualization.py             # Visualization tests
│   └── test_integration.py               # End-to-end tests
├── main.py                               # Command-line application entry point
├── gui.py                                # Graphical user interface
├── pyproject.toml                        # Project configuration
├── PLAN.md                               # Development plan
└── README.md                             # This file
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/medigap --cov-report=html

# Run specific test file
pytest tests/test_monte_carlo.py

# Run with verbose output
pytest -v
```

## Development

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing framework

Run code quality checks:

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/
```

### Adding New Features

1. Write tests first (Test-Driven Development)
2. Implement the feature
3. Ensure all tests pass
4. Update documentation
5. Run code quality checks

## Output Files

The application generates several output files:

- **medicare_cost_projection.png**: Line chart showing mean costs with confidence intervals
- **lifetime_cost_distribution.png**: Histogram of total lifetime costs across simulations
- **medicare_analysis_dashboard.png**: Comprehensive dashboard with multiple charts

## Example Output

```
Medicare/Medigap Monte Carlo Simulation
==================================================
Simulation Parameters:
  Medigap Premium (2026): $155.00/month
  Medigap Premium Growth Rate: 7.0%
  Plan Deductible (2026): $257.00/year
  Plan Deductible Growth Rate: 6.0%
  Part D Premium (2026): $49.00/month
  Part D Premium Growth Rate: 6.0%
  Part B Deductible (2026): $210.00/year
  Part B Deductible Growth Rate: 6.0%
  Percent Sick: 20.0%
  Simulation Years: 25
  Start Year: 2026

Running Monte Carlo simulation...
Simulation completed with 1,000 runs

Cost Statistics Summary:
============================================================
Metric                              Minimum      Maximum      Median      
------------------------------------------------------------
Total Lifetime Costs (25 years)     $   149,904 $   163,641 $   154,770
First 3 Years Average (2026-2028)   $     7,852 $     9,338 $     7,852
============================================================

Year-by-Year Cost Breakdown:
============================================================================================================================================
Year   Medigap      Medigap      Plan       Part D     Part D       Part B     Part B       Total       
#      Monthly      Annual       Deductible Monthly    Annual       Monthly    Annual       Annual      
       Premium      Premium                 Premium    Premium      Premium    Premium      Cost        
--------------------------------------------------------------------------------------------------------------------------------------------
2026   $    155.00 $  1,860.00 $  257.00 $   49.00 $    588.00 $  210.00 $    210.00 $  2,915.00
2027   $    165.85 $  1,990.20 $  272.42 $   51.94 $    623.28 $  222.60 $    222.60 $  3,108.50
2028   $    177.46 $  2,129.51 $  288.77 $   55.06 $    660.68 $  235.96 $    235.96 $  3,314.91
...
2050   $    786.22 $  9,434.60 $1,040.58 $  198.40 $  2,380.77 $  850.28 $    850.28 $ 13,706.23
============================================================================================================================================

Year-by-Year Cost Projections (Mean ± Std Dev):
  2026: $2,541.40 ± $186.80
  2027: $2,709.51 ± $195.75
  2028: $2,895.66 ± $210.28
  ...

Creating visualizations...
  - Expenditure chart saved as 'medicare_cost_projection.png'
  - Lifetime cost histogram saved as 'lifetime_cost_distribution.png'
  - Comprehensive dashboard saved as 'medicare_analysis_dashboard.png'

Simulation completed successfully!
Check the generated PNG files for detailed visualizations.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Implement the feature
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This simulation is for educational and planning purposes only. Actual Medicare costs may vary significantly from projections. Consult with qualified professionals for financial planning decisions.
