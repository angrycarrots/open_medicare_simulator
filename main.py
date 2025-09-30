"""Main application for Medicare/Medigap Monte Carlo simulation."""

import sys
import os
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from medigap.models.simulation_parameters import SimulationParameters
from medigap.simulation.monte_carlo import MonteCarloSimulation
from medigap.visualization.charts import Visualization


def main() -> None:
    """Main application entry point."""
    print("Medicare/Medigap Monte Carlo Simulation")
    print("=" * 50)
    
    # Create simulation parameters with default values
    params = SimulationParameters()
    print(f"Simulation Parameters:")
    print(f"  Medigap Premium (2026): ${params.medigap_premium_2026:,.2f}/month")
    print(f"  Medigap Premium Growth Rate: {params.medigap_premium_growth_rate:.1%}")
    print(f"  Plan Deductible (2026): ${params.plan_deductible_2026:,.2f}/year")
    print(f"  Plan Deductible Growth Rate: {params.plan_deductible_growth_rate:.1%}")
    print(f"  Part D Premium (2026): ${params.part_d_premium_2026:,.2f}/month")
    print(f"  Part D Premium Growth Rate: {params.part_d_premium_growth_rate:.1%}")
    print(f"  Part B Deductible (2026): ${params.part_b_deductible_2026:,.2f}/year")
    print(f"  Part B Deductible Growth Rate: {params.part_b_deductible_growth_rate:.1%}")
    print(f"  Percent Sick: {params.percent_sick:.1%}")
    print(f"  Simulation Years: {params.simulation_years}")
    print(f"  Start Year: {params.start_year}")
    print()
    
    # Create simulation engine
    simulation = MonteCarloSimulation(params)
    
    # Run comprehensive simulation
    print("Running Monte Carlo simulation...")
    num_simulations = 1000
    results = simulation.run_comprehensive_simulation(num_simulations)
    
    # Display summary statistics
    print(f"Simulation completed with {num_simulations:,} runs")
    print()
    
    # Calculate and display lifetime cost statistics
    lifetime_costs = results['lifetime_costs']
    mean_lifetime = sum(lifetime_costs) / len(lifetime_costs)
    min_lifetime = min(lifetime_costs)
    max_lifetime = max(lifetime_costs)
    median_lifetime = sorted(lifetime_costs)[len(lifetime_costs) // 2]
    
    # Calculate first 3 years cost statistics
    first_3_years_costs = []
    for result in results['simulation_results']:
        first_3_years_total = sum(result['costs'][:3])  # Sum of years 0, 1, 2 (2026, 2027, 2028)
        first_3_years_costs.append(first_3_years_total)
    
    mean_first_3 = sum(first_3_years_costs) / len(first_3_years_costs)
    min_first_3 = min(first_3_years_costs)
    max_first_3 = max(first_3_years_costs)
    median_first_3 = sorted(first_3_years_costs)[len(first_3_years_costs) // 2]
    
    print("Cost Statistics Summary:")
    print("=" * 60)
    print(f"{'Metric':<35} {'Minimum':<12} {'Maximum':<12} {'Median':<12}")
    print("-" * 60)
    print(f"{'Total Lifetime Costs (25 years)':<35} ${min_lifetime:>10,.0f} ${max_lifetime:>10,.0f} ${median_lifetime:>10,.0f}")
    print(f"{'First 3 Years Average (2026-2028)':<35} ${min_first_3:>10,.0f} ${max_first_3:>10,.0f} ${median_first_3:>10,.0f}")
    print("=" * 60)
    print()
    
    # Create detailed year-by-year breakdown table
    print("Year-by-Year Cost Breakdown:")
    print("=" * 140)
    print(f"{'Year':<6} {'Medigap':<12} {'Medigap':<12} {'Plan':<10} {'Part D':<10} {'Part D':<12} {'Part B':<10} {'Part B':<12} {'Total':<12}")
    print(f"{'#':<6} {'Monthly':<12} {'Annual':<12} {'Deductible':<10} {'Monthly':<10} {'Annual':<12} {'Monthly':<10} {'Annual':<12} {'Annual':<12}")
    print(f"{'':<6} {'Premium':<12} {'Premium':<12} {'':<10} {'Premium':<10} {'Premium':<12} {'Premium':<10} {'Premium':<12} {'Cost':<12}")
    print("-" * 140)
    
    # Calculate costs for each year
    for year_num in range(params.simulation_years):
        year = params.start_year + year_num
        
        # Calculate individual components
        medigap_monthly = params.medigap_premium_2026 * (1 + params.medigap_premium_growth_rate) ** year_num
        medigap_annual = medigap_monthly * 12
        
        plan_deductible = params.plan_deductible_2026 * (1 + params.plan_deductible_growth_rate) ** year_num
        
        part_d_monthly = params.part_d_premium_2026 * (1 + params.part_d_premium_growth_rate) ** year_num
        part_d_annual = part_d_monthly * 12
        
        part_b_deductible = params.part_b_deductible_2026 * (1 + params.part_b_deductible_growth_rate) ** year_num
        
        # Total annual cost (premiums + deductibles)
        total_annual = medigap_annual + part_d_annual + plan_deductible + part_b_deductible
        
        print(f"{year:<6} ${medigap_monthly:>10,.2f} ${medigap_annual:>10,.2f} ${plan_deductible:>8,.2f} ${part_d_monthly:>8,.2f} ${part_d_annual:>10,.2f} ${part_b_deductible:>8,.2f} ${part_b_deductible:>10,.2f} ${total_annual:>10,.2f}")
    
    print("=" * 140)
    print()
    
    # Display year-by-year statistics
    stats = results['statistics']
    years = list(range(params.start_year, params.start_year + params.simulation_years))
    
    print("Year-by-Year Cost Projections (Mean ± Std Dev):")
    for i, year in enumerate(years):
        mean_cost = stats['mean_costs'][i]
        std_cost = stats['std_costs'][i]
        print(f"  {year}: ${mean_cost:,.2f} ± ${std_cost:,.2f}")
    print()
    
    # Create visualizations
    print("Creating visualizations...")
    visualization = Visualization()
    
    # Create expenditure chart
    visualization.create_expenditure_chart(
        years, 
        stats['mean_costs'], 
        stats['std_costs'],
        save_path="medicare_cost_projection.png"
    )
    print("  - Expenditure chart saved as 'medicare_cost_projection.png'")
    
    # Create lifetime cost histogram
    visualization.create_lifetime_cost_histogram(
        lifetime_costs,
        save_path="lifetime_cost_distribution.png"
    )
    print("  - Lifetime cost histogram saved as 'lifetime_cost_distribution.png'")
    
    # Create comprehensive dashboard
    # Calculate utilization rates from simulation results
    utilization_rates = []
    for i in range(params.simulation_years):
        year_utilizations = [result['utilization'][i] for result in results['simulation_results']]
        utilization_rate = sum(year_utilizations) / len(year_utilizations)
        utilization_rates.append(utilization_rate)
    
    visualization.create_comprehensive_dashboard(
        years,
        stats['mean_costs'],
        stats['std_costs'],
        lifetime_costs,
        utilization_rates,
        save_path="medicare_analysis_dashboard.png"
    )
    print("  - Comprehensive dashboard saved as 'medicare_analysis_dashboard.png'")
    
    print()
    print("Simulation completed successfully!")
    print("Check the generated PNG files for detailed visualizations.")


if __name__ == "__main__":
    main()
