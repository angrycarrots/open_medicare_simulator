#!/usr/bin/env python3
"""Demonstration script for the new Plan structure."""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from medigap.models.plans import PlanG, PlanHDG, PlanN
from medigap.simulation.plan_cost_calculator import PlanCostCalculator
from medigap.simulation.plan_monte_carlo import PlanMonteCarloSimulation


def demonstrate_plan_comparison():
    """Demonstrate the differences between Plan G and Plan HDG."""
    print("=" * 60)
    print("MEDICARE PLAN COMPARISON DEMONSTRATION")
    print("=" * 60)
    
    # Create all plans
    plan_g = PlanG()
    plan_hdg = PlanHDG()
    plan_n = PlanN()
    
    print(f"\nPlan G (Original Medigap Plan N):")
    print(f"  Premium (2026): ${plan_g.premium_2026:.2f}/month")
    print(f"  Premium Growth Rate: {plan_g.premium_growth_rate:.1%}")
    print(f"  Plan Deductible (2026): ${plan_g.plan_deductible_2026:.2f}/year")
    print(f"  Deductible Growth Rate: {plan_g.plan_deductible_growth_rate:.1%}")
    
    print(f"\nPlan HDG (High Deductible Plan G):")
    print(f"  Premium (2026): ${plan_hdg.premium_2026:.2f}/month")
    print(f"  Premium Growth Rate: {plan_hdg.premium_growth_rate:.1%}")
    print(f"  Plan Deductible (2026): ${plan_hdg.plan_deductible_2026:.2f}/year")
    print(f"  Deductible Growth Rate: {plan_hdg.plan_deductible_growth_rate:.1%}")
    
    print(f"\nPlan N (New Plan with Specialist Visits):")
    print(f"  Premium (2026): ${plan_n.premium_2026:.2f}/month")
    print(f"  Premium Growth Rate: {plan_n.premium_growth_rate:.1%}")
    print(f"  Plan Deductible (2026): ${plan_n.plan_deductible_2026:.2f}/year")
    print(f"  Deductible Growth Rate: {plan_n.plan_deductible_growth_rate:.1%}")
    print(f"  Specialist Visits per Year: {plan_n.specialist_visits_per_year}")
    print(f"  Specialist Copay (2026): ${plan_n.specialist_copay_2026:.2f}/visit")
    print(f"  Specialist Copay Growth Rate: {plan_n.specialist_copay_growth_rate:.1%}")
    
    print(f"\nPart D and Part B parameters (same for both plans):")
    print(f"  Part D Premium (2026): ${plan_g.part_d_premium_2026:.2f}/month")
    print(f"  Part D Growth Rate: {plan_g.part_d_premium_growth_rate:.1%}")
    print(f"  Part B Deductible (2026): ${plan_g.part_b_deductible_2026:.2f}/year")
    print(f"  Part B Growth Rate: {plan_g.part_b_deductible_growth_rate:.1%}")


def demonstrate_cost_calculations():
    """Demonstrate cost calculations for both plans."""
    print("\n" + "=" * 60)
    print("COST CALCULATIONS DEMONSTRATION")
    print("=" * 60)
    
    plan_g = PlanG()
    plan_hdg = PlanHDG()
    plan_n = PlanN()
    
    print(f"\nYear 0 (2026) Cost Comparison:")
    print(f"{'Scenario':<15} {'Plan G':<15} {'Plan HDG':<15} {'Plan N':<15}")
    print("-" * 75)
    
    # Healthy scenario (premiums + specialist visits for Plan N)
    g_healthy = plan_g.calculate_annual_costs(0, False)
    hdg_healthy = plan_hdg.calculate_annual_costs(0, False)
    n_healthy = plan_n.calculate_annual_costs(0, False)
    
    print(f"{'Healthy':<15} ${g_healthy:<14.2f} ${hdg_healthy:<14.2f} ${n_healthy:<14.2f}")
    
    # Sick scenario (premiums + deductibles + specialist visits for Plan N)
    g_sick = plan_g.calculate_annual_costs(0, True)
    hdg_sick = plan_hdg.calculate_annual_costs(0, True)
    n_sick = plan_n.calculate_annual_costs(0, True)
    
    print(f"{'Sick':<15} ${g_sick:<14.2f} ${hdg_sick:<14.2f} ${n_sick:<14.2f}")
    
    print(f"\nYear 5 (2031) Cost Comparison:")
    print(f"{'Scenario':<15} {'Plan G':<15} {'Plan HDG':<15} {'Plan N':<15}")
    print("-" * 75)
    
    # Healthy scenario year 5
    g_healthy_5 = plan_g.calculate_annual_costs(5, False)
    hdg_healthy_5 = plan_hdg.calculate_annual_costs(5, False)
    n_healthy_5 = plan_n.calculate_annual_costs(5, False)
    
    print(f"{'Healthy':<15} ${g_healthy_5:<14.2f} ${hdg_healthy_5:<14.2f} ${n_healthy_5:<14.2f}")
    
    # Sick scenario year 5
    g_sick_5 = plan_g.calculate_annual_costs(5, True)
    hdg_sick_5 = plan_hdg.calculate_annual_costs(5, True)
    n_sick_5 = plan_n.calculate_annual_costs(5, True)
    
    print(f"{'Sick':<15} ${g_sick_5:<14.2f} ${hdg_sick_5:<14.2f} ${n_sick_5:<14.2f}")


def demonstrate_monte_carlo_simulation():
    """Demonstrate Monte Carlo simulation comparison."""
    print("\n" + "=" * 60)
    print("MONTE CARLO SIMULATION DEMONSTRATION")
    print("=" * 60)
    
    plan_g = PlanG()
    plan_hdg = PlanHDG()
    plan_n = PlanN()
    
    # Run a small simulation for demonstration
    print(f"\nRunning Monte Carlo simulation (100 iterations)...")
    
    sim_g = PlanMonteCarloSimulation(plan_g)
    sim_hdg = PlanMonteCarloSimulation(plan_hdg)
    sim_n = PlanMonteCarloSimulation(plan_n)
    
    # Run comprehensive simulations
    results_g = sim_g.run_comprehensive_simulation(100)
    results_hdg = sim_hdg.run_comprehensive_simulation(100)
    results_n = sim_n.run_comprehensive_simulation(100)
    
    # Calculate lifetime cost statistics
    lifetime_g = results_g['lifetime_costs']
    lifetime_hdg = results_hdg['lifetime_costs']
    lifetime_n = results_n['lifetime_costs']
    
    print(f"\nLifetime Cost Statistics (25 years, 2026-2050):")
    print(f"{'Plan':<10} {'Mean':<12} {'Std Dev':<12} {'Min':<12} {'Max':<12}")
    print("-" * 60)
    
    import numpy as np
    
    print(f"{'Plan G':<10} ${np.mean(lifetime_g):<11.2f} ${np.std(lifetime_g):<11.2f} ${np.min(lifetime_g):<11.2f} ${np.max(lifetime_g):<11.2f}")
    print(f"{'Plan HDG':<10} ${np.mean(lifetime_hdg):<11.2f} ${np.std(lifetime_hdg):<11.2f} ${np.min(lifetime_hdg):<11.2f} ${np.max(lifetime_hdg):<11.2f}")
    print(f"{'Plan N':<10} ${np.mean(lifetime_n):<11.2f} ${np.std(lifetime_n):<11.2f} ${np.min(lifetime_n):<11.2f} ${np.max(lifetime_n):<11.2f}")
    
    # Calculate differences
    mean_diff_hdg_g = np.mean(lifetime_hdg) - np.mean(lifetime_g)
    mean_diff_n_g = np.mean(lifetime_n) - np.mean(lifetime_g)
    mean_diff_n_hdg = np.mean(lifetime_n) - np.mean(lifetime_hdg)
    
    print(f"\nMean differences:")
    print(f"Plan HDG vs Plan G: ${mean_diff_hdg_g:.2f}")
    print(f"Plan N vs Plan G: ${mean_diff_n_g:.2f}")
    print(f"Plan N vs Plan HDG: ${mean_diff_n_hdg:.2f}")


def main():
    """Main demonstration function."""
    print("Open Medicare Simulator - Plan Structure Demonstration")
    
    try:
        demonstrate_plan_comparison()
        demonstrate_cost_calculations()
        demonstrate_monte_carlo_simulation()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nThe new Plan structure allows for:")
        print("• Easy creation of different Medicare plans with custom parameters")
        print("• Consistent cost calculations across all plan types")
        print("• Monte Carlo simulations for any plan")
        print("• Plan comparison capabilities")
        print("• Specialist visit cost calculations for plans that support them")
        print("\nPlan-G, Plan-HDG, and Plan-N are now available for use!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


