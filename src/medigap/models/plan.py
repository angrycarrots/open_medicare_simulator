"""Base Medicare plan class for different plan types."""

from abc import ABC, abstractmethod
from typing import Optional


class Plan(ABC):
    """Abstract base class for Medicare plans.
    
    This class defines the interface that all Medicare plans must implement,
    allowing for different plan types with varying parameters.
    """
    
    def __init__(
        self,
        name: str,
        premium_2026: float,
        premium_growth_rate: float,
        plan_deductible_2026: float,
        plan_deductible_growth_rate: float,
        part_d_premium_2026: float = 49.0,
        part_d_premium_growth_rate: float = 0.06,
        part_b_deductible_2026: float = 210.0,
        part_b_deductible_growth_rate: float = 0.06,
        percent_sick: float = 0.20,
        simulation_years: int = 25,
        start_year: int = 2026
    ) -> None:
        """Initialize plan parameters with validation.
        
        Args:
            name: Name of the plan (e.g., "Plan-G", "Plan-HDG")
            premium_2026: Base premium for 2026
            premium_growth_rate: Annual growth rate for premium
            plan_deductible_2026: Base plan deductible for 2026
            plan_deductible_growth_rate: Annual growth rate for plan deductible
            part_d_premium_2026: Base Part D premium for 2026
            part_d_premium_growth_rate: Annual growth rate for Part D premium
            part_b_deductible_2026: Base Part B deductible for 2026
            part_b_deductible_growth_rate: Annual growth rate for Part B deductible
            percent_sick: Probability of full utilization (0-1)
            simulation_years: Number of years to simulate
            start_year: Starting year for simulation
            
        Raises:
            ValueError: If any parameter is invalid
        """
        self._validate_parameters(
            premium_2026, premium_growth_rate,
            plan_deductible_2026, plan_deductible_growth_rate,
            part_d_premium_2026, part_d_premium_growth_rate,
            part_b_deductible_2026, part_b_deductible_growth_rate,
            percent_sick, simulation_years, start_year
        )
        
        self.name = name
        self.premium_2026 = premium_2026
        self.premium_growth_rate = premium_growth_rate
        self.plan_deductible_2026 = plan_deductible_2026
        self.plan_deductible_growth_rate = plan_deductible_growth_rate
        self.part_d_premium_2026 = part_d_premium_2026
        self.part_d_premium_growth_rate = part_d_premium_growth_rate
        self.part_b_deductible_2026 = part_b_deductible_2026
        self.part_b_deductible_growth_rate = part_b_deductible_growth_rate
        self.percent_sick = percent_sick
        self.simulation_years = simulation_years
        self.start_year = start_year

    def _validate_parameters(
        self,
        premium_2026: float,
        premium_growth_rate: float,
        plan_deductible_2026: float,
        plan_deductible_growth_rate: float,
        part_d_premium_2026: float,
        part_d_premium_growth_rate: float,
        part_b_deductible_2026: float,
        part_b_deductible_growth_rate: float,
        percent_sick: float,
        simulation_years: int,
        start_year: int
    ) -> None:
        """Validate all plan parameters.
        
        Args:
            All parameters to validate
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate premiums (must be positive)
        for premium, name in [
            (premium_2026, "Premium"),
            (plan_deductible_2026, "Plan deductible"),
            (part_d_premium_2026, "Part D premium"),
            (part_b_deductible_2026, "Part B deductible")
        ]:
            if premium <= 0:
                raise ValueError(f"{name} must be positive")
        
        # Validate growth rates (must be non-negative)
        for rate, name in [
            (premium_growth_rate, "Premium growth rate"),
            (plan_deductible_growth_rate, "Plan deductible growth rate"),
            (part_d_premium_growth_rate, "Part D premium growth rate"),
            (part_b_deductible_growth_rate, "Part B deductible growth rate")
        ]:
            if rate < 0:
                raise ValueError(f"{name} must be non-negative")
        
        # Validate percent_sick (must be between 0 and 1)
        if not 0 <= percent_sick <= 1:
            raise ValueError("Percent sick must be between 0 and 1")
        
        # Validate simulation_years (must be positive)
        if simulation_years <= 0:
            raise ValueError("Simulation years must be positive")
        
        # Validate start_year (must be positive)
        if start_year <= 0:
            raise ValueError("Start year must be positive")

    def calculate_premium(self, year: int) -> float:
        """Calculate premium for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Monthly premium for the specified year
            
        Raises:
            ValueError: If year is negative
        """
        if year < 0:
            raise ValueError("Year must be non-negative")
        
        return self.premium_2026 * (1 + self.premium_growth_rate) ** year

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
        
        return self.plan_deductible_2026 * (1 + self.plan_deductible_growth_rate) ** year

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
        
        return self.part_d_premium_2026 * (1 + self.part_d_premium_growth_rate) ** year

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
        
        return self.part_b_deductible_2026 * (1 + self.part_b_deductible_growth_rate) ** year

    def calculate_total_premiums(self, year: int) -> float:
        """Calculate total premiums (Plan + Part D) for a given year.
        
        Args:
            year: Year offset from start year (0 = start year)
            
        Returns:
            Total annual premiums for the specified year (monthly premiums * 12)
        """
        monthly_premium = self.calculate_premium(year)
        monthly_part_d = self.calculate_part_d_premium(year)
        return (monthly_premium + monthly_part_d) * 12

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

    def __str__(self) -> str:
        """Return string representation of the plan."""
        return f"{self.name}: Premium ${self.premium_2026:.2f}, Deductible ${self.plan_deductible_2026:.2f}"

    def __repr__(self) -> str:
        """Return detailed string representation of the plan."""
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"premium_2026={self.premium_2026}, "
                f"premium_growth_rate={self.premium_growth_rate}, "
                f"plan_deductible_2026={self.plan_deductible_2026}, "
                f"plan_deductible_growth_rate={self.plan_deductible_growth_rate})")

