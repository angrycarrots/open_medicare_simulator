"""Specific Medicare plan implementations."""

from .plan import Plan


class PlanG(Plan):
    """Medigap Plan G implementation.
    
    This represents the current default Medigap Plan N configuration
    with the original parameters from the simulation.
    """
    
    def __init__(
        self,
        percent_sick: float = 0.20,
        simulation_years: int = 25,
        start_year: int = 2026
    ) -> None:
        """Initialize Plan G with default parameters.
        
        Args:
            percent_sick: Probability of full utilization (0-1)
            simulation_years: Number of years to simulate
            start_year: Starting year for simulation
        """
        super().__init__(
            name="Plan-G",
            premium_2026=155.0,  # Original Medigap Plan N premium
            premium_growth_rate=0.07,  # 7% annual growth
            plan_deductible_2026=257.0,  # Original plan deductible
            plan_deductible_growth_rate=0.06,  # 6% annual growth
            part_d_premium_2026=49.0,  # Part D premium
            part_d_premium_growth_rate=0.06,  # 6% annual growth
            part_b_deductible_2026=210.0,  # Part B deductible
            part_b_deductible_growth_rate=0.06,  # 6% annual growth
            percent_sick=percent_sick,
            simulation_years=simulation_years,
            start_year=start_year
        )


class PlanHDG(Plan):
    """High Deductible Plan G implementation.
    
    This represents a high deductible version of Plan G with:
    - Lower premium ($40/month)
    - Higher deductible ($2800/year)
    - Same Part D and Part B parameters as Plan G
    """
    
    def __init__(
        self,
        percent_sick: float = 0.20,
        simulation_years: int = 25,
        start_year: int = 2026
    ) -> None:
        """Initialize Plan HDG with specified parameters.
        
        Args:
            percent_sick: Probability of full utilization (0-1)
            simulation_years: Number of years to simulate
            start_year: Starting year for simulation
        """
        super().__init__(
            name="Plan-HDG",
            premium_2026=40.0,  # Lower premium
            premium_growth_rate=0.07,  # 7% annual growth
            plan_deductible_2026=2800.0,  # Higher deductible
            plan_deductible_growth_rate=0.06,  # 6% annual growth
            part_d_premium_2026=49.0,  # Same Part D premium as Plan G
            part_d_premium_growth_rate=0.06,  # Same Part D growth rate
            part_b_deductible_2026=210.0,  # Same Part B deductible as Plan G
            part_b_deductible_growth_rate=0.06,  # Same Part B growth rate
            percent_sick=percent_sick,
            simulation_years=simulation_years,
            start_year=start_year
        )


class PlanN(Plan):
    """Plan N implementation.
    
    This represents Plan N with:
    - Premium: $118/month (2026)
    - Premium growth rate: 7%
    - Plan deductible: $257/year (2026)
    - Plan deductible growth rate: 6%
    - Same Part B and Part D parameters as other plans
    - Specialist visits: 12 per year with $20 copay (2026)
    - Specialist copay growth rate: same as premium growth rate (7%)
    """
    
    def __init__(
        self,
        percent_sick: float = 0.20,
        simulation_years: int = 25,
        start_year: int = 2026
    ) -> None:
        """Initialize Plan N with specified parameters.
        
        Args:
            percent_sick: Probability of full utilization (0-1)
            simulation_years: Number of years to simulate
            start_year: Starting year for simulation
        """
        super().__init__(
            name="Plan-N",
            premium_2026=118.0,  # $118/month premium
            premium_growth_rate=0.07,  # 7% annual growth
            plan_deductible_2026=257.0,  # $257/year deductible
            plan_deductible_growth_rate=0.06,  # 6% annual growth
            part_d_premium_2026=49.0,  # Same Part D premium as other plans
            part_d_premium_growth_rate=0.06,  # Same Part D growth rate
            part_b_deductible_2026=210.0,  # Same Part B deductible as other plans
            part_b_deductible_growth_rate=0.06,  # Same Part B growth rate
            percent_sick=percent_sick,
            simulation_years=simulation_years,
            start_year=start_year,
            # Specialist visit parameters
            specialist_visits_per_year=12,  # 12 specialist visits per year
            specialist_copay_2026=20.0,  # $20 copay per specialist visit
            specialist_copay_growth_rate=0.07  # Same as premium growth rate (7%)
        )


