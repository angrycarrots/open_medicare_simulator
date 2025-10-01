"""Cost calculation utilities for Medicare plans."""

import numpy as np
from typing import List
from ..models.plan import Plan


class PlanCostCalculator:
    """Calculator for Medicare plan costs with growth rates.
    
    This class handles all cost calculations including premiums, deductibles,
    and total annual costs based on a Plan object.
    """
    
    def __init__(self, plan: Plan) -> None:
        """Initialize the cost calculator with a plan.
        
        Args:
            plan: Plan object containing cost bases and growth rates
        """
        self.plan = plan

    def calculate_premium(self, year: int) -> float:
        """Calculate plan premium for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Monthly plan premium for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        return self.plan.calculate_premium(year)

    def calculate_plan_deductible(self, year: int) -> float:
        """Calculate plan deductible for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Plan deductible for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        return self.plan.calculate_plan_deductible(year)

    def calculate_part_d_premium(self, year: int) -> float:
        """Calculate Part D premium for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Monthly Part D premium for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        return self.plan.calculate_part_d_premium(year)

    def calculate_part_b_deductible(self, year: int) -> float:
        """Calculate Part B deductible for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Part B deductible for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        return self.plan.calculate_part_b_deductible(year)

    def calculate_total_premiums(self, year: int) -> float:
        """Calculate total premiums (Plan + Part D) for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Total annual premiums for the specified year (monthly premiums * 12)
        """
        return self.plan.calculate_total_premiums(year)

    def calculate_total_deductibles(self, year: int) -> float:
        """Calculate total deductibles (Plan + Part B) for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Total deductibles for the specified year
        """
        return self.plan.calculate_total_deductibles(year)

    def calculate_annual_costs(self, year: int, is_sick: bool) -> float:
        """Calculate total annual costs for a given year and health status.
        
        Args:
            year: Year offset from start year (0 = start year)
            is_sick: Whether the person is sick (full utilization)
            
        Returns:
            Total annual costs including premiums and deductibles (if sick)
        """
        return self.plan.calculate_annual_costs(year, is_sick)

    def calculate_all_years_costs(self, utilization_pattern: List[bool]) -> List[float]:
        """Calculate costs for all years based on utilization pattern.
        
        Args:
            utilization_pattern: List of boolean values indicating sick/healthy for each year
            
        Returns:
            List of total costs for each year
            
        Raises:
            ValueError: If utilization pattern length doesn't match simulation years
        """
        if len(utilization_pattern) != self.plan.simulation_years:
            raise ValueError(
                f"Utilization pattern length ({len(utilization_pattern)}) "
                f"must match simulation years ({self.plan.simulation_years})"
            )
        
        costs = []
        for year, is_sick in enumerate(utilization_pattern):
            annual_cost = self.calculate_annual_costs(year, is_sick)
            costs.append(annual_cost)
        
        return costs

    def get_plan_summary(self) -> dict:
        """Get a summary of the plan's key parameters.
        
        Returns:
            Dictionary containing plan summary information
        """
        return {
            "name": self.plan.name,
            "premium_2026": self.plan.premium_2026,
            "premium_growth_rate": self.plan.premium_growth_rate,
            "plan_deductible_2026": self.plan.plan_deductible_2026,
            "plan_deductible_growth_rate": self.plan.plan_deductible_growth_rate,
            "part_d_premium_2026": self.plan.part_d_premium_2026,
            "part_d_premium_growth_rate": self.plan.part_d_premium_growth_rate,
            "part_b_deductible_2026": self.plan.part_b_deductible_2026,
            "part_b_deductible_growth_rate": self.plan.part_b_deductible_growth_rate,
            "percent_sick": self.plan.percent_sick,
            "simulation_years": self.plan.simulation_years,
            "start_year": self.plan.start_year
        }

