"""Cost calculation utilities for Medicare/Medigap simulation."""

import numpy as np
from typing import List
from ..models.simulation_parameters import SimulationParameters


class CostCalculator:
    """Calculator for Medicare/Medigap costs with growth rates.
    
    This class handles all cost calculations including premiums, deductibles,
    and total annual costs based on the simulation parameters.
    """
    
    def __init__(self, params: SimulationParameters) -> None:
        """Initialize the cost calculator with simulation parameters.
        
        Args:
            params: Simulation parameters containing cost bases and growth rates
        """
        self.params = params

    def calculate_medigap_premium(self, year: int) -> float:
        """Calculate Medigap premium for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Monthly Medigap premium for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        if year < 0:
            raise ValueError("Year must be non-negative")
        
        return self.params.medigap_premium_2026 * (1 + self.params.medigap_premium_growth_rate) ** year

    def calculate_plan_deductible(self, year: int) -> float:
        """Calculate plan deductible for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Plan deductible for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        if year < 0:
            raise ValueError("Year must be non-negative")
        
        return self.params.plan_deductible_2026 * (1 + self.params.plan_deductible_growth_rate) ** year

    def calculate_part_d_premium(self, year: int) -> float:
        """Calculate Part D premium for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Monthly Part D premium for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        if year < 0:
            raise ValueError("Year must be non-negative")
        
        return self.params.part_d_premium_2026 * (1 + self.params.part_d_premium_growth_rate) ** year

    def calculate_part_b_deductible(self, year: int) -> float:
        """Calculate Part B deductible for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Part B deductible for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        if year < 0:
            raise ValueError("Year must be non-negative")
        
        return self.params.part_b_deductible_2026 * (1 + self.params.part_b_deductible_growth_rate) ** year

    def calculate_total_premiums(self, year: int) -> float:
        """Calculate total premiums (Medigap + Part D) for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Total annual premiums for the specified year (monthly premiums * 12)
        """
        monthly_medigap = self.calculate_medigap_premium(year)
        monthly_part_d = self.calculate_part_d_premium(year)
        return (monthly_medigap + monthly_part_d) * 12

    def calculate_total_deductibles(self, year: int) -> float:
        """Calculate total deductibles (Plan + Part B) for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Total deductibles for the specified year
        """
        return self.calculate_plan_deductible(year) + self.calculate_part_b_deductible(year)

    def calculate_annual_costs(self, year: int, is_sick: bool) -> float:
        """Calculate total annual costs for a given year and health status.
        
        Args:
            year: Year offset from start year (0 = start year)
            is_sick: Whether the person is sick (full utilization)
            
        Returns:
            Total annual costs including premiums and deductibles (if sick)
        """
        total_premiums = self.calculate_total_premiums(year)
        
        if is_sick:
            total_deductibles = self.calculate_total_deductibles(year)
            return total_premiums + total_deductibles
        else:
            return total_premiums

    def calculate_all_years_costs(self, utilization_pattern: List[bool]) -> List[float]:
        """Calculate costs for all years based on utilization pattern.
        
        Args:
            utilization_pattern: List of boolean values indicating sick/healthy for each year
            
        Returns:
            List of total costs for each year
            
        Raises:
            ValueError: If utilization pattern length doesn't match simulation years
        """
        if len(utilization_pattern) != self.params.simulation_years:
            raise ValueError(
                f"Utilization pattern length ({len(utilization_pattern)}) "
                f"must match simulation years ({self.params.simulation_years})"
            )
        
        costs = []
        for year, is_sick in enumerate(utilization_pattern):
            annual_cost = self.calculate_annual_costs(year, is_sick)
            costs.append(annual_cost)
        
        return costs
