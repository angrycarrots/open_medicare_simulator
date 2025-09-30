"""Tests for SimulationParameters class."""

import pytest
from src.medigap.models.simulation_parameters import SimulationParameters


class TestSimulationParameters:
    """Test cases for SimulationParameters class."""

    def test_default_parameters(self) -> None:
        """Test that default parameters are set correctly."""
        params = SimulationParameters()
        
        assert params.medigap_premium_2026 == 155.0
        assert params.medigap_premium_growth_rate == 0.07
        assert params.plan_deductible_2026 == 257.0
        assert params.plan_deductible_growth_rate == 0.06
        assert params.part_d_premium_2026 == 49.0
        assert params.part_d_premium_growth_rate == 0.06
        assert params.part_b_deductible_2026 == 210.0
        assert params.part_b_deductible_growth_rate == 0.06
        assert params.percent_sick == 0.20
        assert params.simulation_years == 25
        assert params.start_year == 2026

    def test_custom_parameters(self) -> None:
        """Test that custom parameters can be set."""
        params = SimulationParameters(
            medigap_premium_2026=200.0,
            medigap_premium_growth_rate=0.05,
            percent_sick=0.15
        )
        
        assert params.medigap_premium_2026 == 200.0
        assert params.medigap_premium_growth_rate == 0.05
        assert params.percent_sick == 0.15
        # Other parameters should remain default
        assert params.plan_deductible_2026 == 257.0

    def test_parameter_validation(self) -> None:
        """Test that invalid parameters raise appropriate errors."""
        # Test negative premium
        with pytest.raises(ValueError, match="Medigap premium must be positive"):
            SimulationParameters(medigap_premium_2026=-100.0)
        
        # Test negative growth rate
        with pytest.raises(ValueError, match="Medigap premium growth rate must be non-negative"):
            SimulationParameters(medigap_premium_growth_rate=-0.05)
        
        # Test percent_sick out of range
        with pytest.raises(ValueError, match="Percent sick must be between 0 and 1"):
            SimulationParameters(percent_sick=1.5)
        
        with pytest.raises(ValueError, match="Percent sick must be between 0 and 1"):
            SimulationParameters(percent_sick=-0.1)

    def test_simulation_years_validation(self) -> None:
        """Test validation of simulation years."""
        with pytest.raises(ValueError, match="Simulation years must be positive"):
            SimulationParameters(simulation_years=0)
        
        with pytest.raises(ValueError, match="Simulation years must be positive"):
            SimulationParameters(simulation_years=-5)

    def test_start_year_validation(self) -> None:
        """Test validation of start year."""
        with pytest.raises(ValueError, match="Start year must be positive"):
            SimulationParameters(start_year=0)
        
        with pytest.raises(ValueError, match="Start year must be positive"):
            SimulationParameters(start_year=-2026)
