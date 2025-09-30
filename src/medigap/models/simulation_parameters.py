"""Simulation parameters configuration class."""

from typing import Optional


class SimulationParameters:
    """Configuration class for Medicare/Medigap simulation parameters.
    
    This class holds all the configuration parameters needed for the Monte Carlo
    simulation, including premium costs, growth rates, and simulation settings.
    """
    
    def __init__(
        self,
        medigap_premium_2026: float = 155.0,
        medigap_premium_growth_rate: float = 0.07,
        plan_deductible_2026: float = 257.0,
        plan_deductible_growth_rate: float = 0.06,
        part_d_premium_2026: float = 49.0,
        part_d_premium_growth_rate: float = 0.06,
        part_b_deductible_2026: float = 210.0,
        part_b_deductible_growth_rate: float = 0.06,
        percent_sick: float = 0.20,
        simulation_years: int = 25,
        start_year: int = 2026
    ) -> None:
        """Initialize simulation parameters with validation.
        
        Args:
            medigap_premium_2026: Base Medigap Plan N premium for 2026
            medigap_premium_growth_rate: Annual growth rate for Medigap premium
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
            medigap_premium_2026, medigap_premium_growth_rate,
            plan_deductible_2026, plan_deductible_growth_rate,
            part_d_premium_2026, part_d_premium_growth_rate,
            part_b_deductible_2026, part_b_deductible_growth_rate,
            percent_sick, simulation_years, start_year
        )
        
        self.medigap_premium_2026 = medigap_premium_2026
        self.medigap_premium_growth_rate = medigap_premium_growth_rate
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
        medigap_premium_2026: float,
        medigap_premium_growth_rate: float,
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
        """Validate all simulation parameters.
        
        Args:
            All parameters to validate
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate premiums (must be positive)
        for premium, name in [
            (medigap_premium_2026, "Medigap premium"),
            (plan_deductible_2026, "Plan deductible"),
            (part_d_premium_2026, "Part D premium"),
            (part_b_deductible_2026, "Part B deductible")
        ]:
            if premium <= 0:
                raise ValueError(f"{name} must be positive")
        
        # Validate growth rates (must be non-negative)
        for rate, name in [
            (medigap_premium_growth_rate, "Medigap premium growth rate"),
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
