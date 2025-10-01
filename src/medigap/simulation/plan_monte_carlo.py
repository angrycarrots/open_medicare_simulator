"""Monte Carlo simulation engine for Medicare plans."""

import numpy as np
from typing import List, Dict, Any
from ..models.plan import Plan
from .plan_cost_calculator import PlanCostCalculator


class PlanMonteCarloSimulation:
    """Monte Carlo simulation engine for Medicare plan cost projections.
    
    This class runs Monte Carlo simulations to project medical costs over time
    based on probabilistic utilization patterns and cost growth rates for any Plan.
    """
    
    def __init__(self, plan: Plan) -> None:
        """Initialize the Monte Carlo simulation.
        
        Args:
            plan: Plan object containing cost bases and growth rates
        """
        self.plan = plan
        self.calculator = PlanCostCalculator(plan)

    def generate_utilization_pattern(self, num_years: int) -> List[bool]:
        """Generate a utilization pattern for the simulation period.
        
        Args:
            num_years: Number of years to generate pattern for
            
        Returns:
            List of boolean values indicating sick (True) or healthy (False) for each year
        """
        # Generate random numbers between 0 and 1
        random_values = np.random.random(num_years)
        
        # Convert to boolean: True if random value < percent_sick
        utilization_pattern = [value < self.plan.percent_sick for value in random_values]
        
        return utilization_pattern

    def run_single_simulation(self) -> Dict[str, Any]:
        """Run a single Monte Carlo simulation.
        
        Returns:
            Dictionary containing costs and utilization pattern for each year
        """
        # Generate utilization pattern for all simulation years
        utilization_pattern = self.generate_utilization_pattern(self.plan.simulation_years)
        
        # Calculate costs for each year based on utilization pattern
        costs = self.calculator.calculate_all_years_costs(utilization_pattern)
        
        return {
            'costs': costs,
            'utilization': utilization_pattern
        }

    def run_multiple_simulations(self, num_simulations: int) -> List[Dict[str, Any]]:
        """Run multiple Monte Carlo simulations.
        
        Args:
            num_simulations: Number of simulations to run
            
        Returns:
            List of simulation results, each containing costs and utilization pattern
            
        Raises:
            ValueError: If num_simulations is not positive
        """
        if num_simulations <= 0:
            raise ValueError("Number of simulations must be positive")
        
        results = []
        for _ in range(num_simulations):
            result = self.run_single_simulation()
            results.append(result)
        
        return results

    def calculate_statistics(self, simulation_results: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Calculate statistics across multiple simulation runs.
        
        Args:
            simulation_results: List of simulation results from run_multiple_simulations
            
        Returns:
            Dictionary containing mean, std, min, max, and total costs for each year
        """
        if not simulation_results:
            raise ValueError("No simulation results provided")
        
        # Extract costs for each year across all simulations
        num_years = len(simulation_results[0]['costs'])
        costs_by_year = [[] for _ in range(num_years)]
        
        for result in simulation_results:
            for year, cost in enumerate(result['costs']):
                costs_by_year[year].append(cost)
        
        # Calculate statistics for each year
        statistics = {
            'mean_costs': [],
            'std_costs': [],
            'min_costs': [],
            'max_costs': [],
            'total_costs': []
        }
        
        for year_costs in costs_by_year:
            statistics['mean_costs'].append(np.mean(year_costs))
            statistics['std_costs'].append(np.std(year_costs))
            statistics['min_costs'].append(np.min(year_costs))
            statistics['max_costs'].append(np.max(year_costs))
            statistics['total_costs'].append(np.sum(year_costs))
        
        return statistics

    def calculate_total_lifetime_costs(self, simulation_results: List[Dict[str, Any]]) -> List[float]:
        """Calculate total lifetime costs for each simulation.
        
        Args:
            simulation_results: List of simulation results from run_multiple_simulations
            
        Returns:
            List of total lifetime costs for each simulation
        """
        lifetime_costs = []
        for result in simulation_results:
            total_cost = sum(result['costs'])
            lifetime_costs.append(total_cost)
        
        return lifetime_costs

    def run_comprehensive_simulation(self, num_simulations: int = 1000) -> Dict[str, Any]:
        """Run a comprehensive simulation with statistics.
        
        Args:
            num_simulations: Number of simulations to run (default: 1000)
            
        Returns:
            Dictionary containing all simulation results and statistics
        """
        # Run multiple simulations
        simulation_results = self.run_multiple_simulations(num_simulations)
        
        # Calculate statistics
        statistics = self.calculate_statistics(simulation_results)
        
        # Calculate lifetime costs
        lifetime_costs = self.calculate_total_lifetime_costs(simulation_results)
        
        return {
            'simulation_results': simulation_results,
            'statistics': statistics,
            'lifetime_costs': lifetime_costs,
            'num_simulations': num_simulations,
            'plan_summary': self.calculator.get_plan_summary()
        }

    def compare_plans(self, other_plan: Plan, num_simulations: int = 1000) -> Dict[str, Any]:
        """Compare this plan with another plan.
        
        Args:
            other_plan: Another Plan to compare with
            num_simulations: Number of simulations to run for comparison
            
        Returns:
            Dictionary containing comparison results
        """
        # Run simulations for both plans
        this_results = self.run_comprehensive_simulation(num_simulations)
        
        other_simulation = PlanMonteCarloSimulation(other_plan)
        other_results = other_simulation.run_comprehensive_simulation(num_simulations)
        
        # Calculate comparison statistics
        this_lifetime_costs = this_results['lifetime_costs']
        other_lifetime_costs = other_results['lifetime_costs']
        
        comparison = {
            'plan_1': {
                'name': self.plan.name,
                'mean_lifetime_cost': np.mean(this_lifetime_costs),
                'std_lifetime_cost': np.std(this_lifetime_costs),
                'min_lifetime_cost': np.min(this_lifetime_costs),
                'max_lifetime_cost': np.max(this_lifetime_costs),
                'results': this_results
            },
            'plan_2': {
                'name': other_plan.name,
                'mean_lifetime_cost': np.mean(other_lifetime_costs),
                'std_lifetime_cost': np.std(other_lifetime_costs),
                'min_lifetime_cost': np.min(other_lifetime_costs),
                'max_lifetime_cost': np.max(other_lifetime_costs),
                'results': other_results
            },
            'difference': {
                'mean_difference': np.mean(this_lifetime_costs) - np.mean(other_lifetime_costs),
                'std_difference': np.std(np.array(this_lifetime_costs) - np.array(other_lifetime_costs))
            }
        }
        
        return comparison

