"""Monte Carlo simulation engine for Medicare/Medigap costs."""

import numpy as np
from typing import List, Dict, Any
from ..models.simulation_parameters import SimulationParameters
from .cost_calculator import CostCalculator


class MonteCarloSimulation:
    """Monte Carlo simulation engine for Medicare/Medigap cost projections.
    
    This class runs Monte Carlo simulations to project medical costs over time
    based on probabilistic utilization patterns and cost growth rates.
    """
    
    def __init__(self, params: SimulationParameters) -> None:
        """Initialize the Monte Carlo simulation.
        
        Args:
            params: Simulation parameters containing cost bases and growth rates
        """
        self.params = params
        self.calculator = CostCalculator(params)

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
        utilization_pattern = [value < self.params.percent_sick for value in random_values]
        
        return utilization_pattern

    def run_single_simulation(self) -> Dict[str, Any]:
        """Run a single Monte Carlo simulation.
        
        Returns:
            Dictionary containing costs and utilization pattern for each year
        """
        # Generate utilization pattern for all simulation years
        utilization_pattern = self.generate_utilization_pattern(self.params.simulation_years)
        
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
            'parameters': {
                'medigap_premium_2026': self.params.medigap_premium_2026,
                'medigap_premium_growth_rate': self.params.medigap_premium_growth_rate,
                'plan_deductible_2026': self.params.plan_deductible_2026,
                'plan_deductible_growth_rate': self.params.plan_deductible_growth_rate,
                'part_d_premium_2026': self.params.part_d_premium_2026,
                'part_d_premium_growth_rate': self.params.part_d_premium_growth_rate,
                'part_b_deductible_2026': self.params.part_b_deductible_2026,
                'part_b_deductible_growth_rate': self.params.part_b_deductible_growth_rate,
                'percent_sick': self.params.percent_sick,
                'simulation_years': self.params.simulation_years,
                'start_year': self.params.start_year
            }
        }
