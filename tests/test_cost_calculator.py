"""Tests for CostCalculator class."""

import pytest
import numpy as np
from src.medigap.models.simulation_parameters import SimulationParameters
from src.medigap.simulation.cost_calculator import CostCalculator


class TestCostCalculator:
    """Test cases for CostCalculator class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.params = SimulationParameters()
        self.calculator = CostCalculator(self.params)

    def test_initialization(self) -> None:
        """Test CostCalculator initialization."""
        assert self.calculator.params == self.params

    def test_calculate_medigap_premium(self) -> None:
        """Test Medigap premium calculation with growth."""
        # Year 0 (2026) should return base premium
        premium_2026 = self.calculator.calculate_medigap_premium(0)
        assert premium_2026 == 155.0
        
        # Year 1 (2027) should apply 7% growth
        premium_2027 = self.calculator.calculate_medigap_premium(1)
        expected_2027 = 155.0 * (1 + 0.07)
        assert abs(premium_2027 - expected_2027) < 0.01
        
        # Year 2 (2028) should apply compound growth
        premium_2028 = self.calculator.calculate_medigap_premium(2)
        expected_2028 = 155.0 * (1 + 0.07) ** 2
        assert abs(premium_2028 - expected_2028) < 0.01

    def test_calculate_plan_deductible(self) -> None:
        """Test plan deductible calculation with growth."""
        # Year 0 (2026) should return base deductible
        deductible_2026 = self.calculator.calculate_plan_deductible(0)
        assert deductible_2026 == 257.0
        
        # Year 1 (2027) should apply 6% growth
        deductible_2027 = self.calculator.calculate_plan_deductible(1)
        expected_2027 = 257.0 * (1 + 0.06)
        assert abs(deductible_2027 - expected_2027) < 0.01

    def test_calculate_part_d_premium(self) -> None:
        """Test Part D premium calculation with growth."""
        # Year 0 (2026) should return base premium
        premium_2026 = self.calculator.calculate_part_d_premium(0)
        assert premium_2026 == 49.0
        
        # Year 1 (2027) should apply 6% growth
        premium_2027 = self.calculator.calculate_part_d_premium(1)
        expected_2027 = 49.0 * (1 + 0.06)
        assert abs(premium_2027 - expected_2027) < 0.01

    def test_calculate_part_b_deductible(self) -> None:
        """Test Part B deductible calculation with growth."""
        # Year 0 (2026) should return base deductible
        deductible_2026 = self.calculator.calculate_part_b_deductible(0)
        assert deductible_2026 == 210.0
        
        # Year 1 (2027) should apply 6% growth
        deductible_2027 = self.calculator.calculate_part_b_deductible(1)
        expected_2027 = 210.0 * (1 + 0.06)
        assert abs(deductible_2027 - expected_2027) < 0.01

    def test_calculate_total_premiums(self) -> None:
        """Test total premiums calculation."""
        # Year 0 should be (Medigap + Part D monthly premiums) * 12
        total_2026 = self.calculator.calculate_total_premiums(0)
        expected_2026 = (155.0 + 49.0) * 12  # Monthly premiums * 12 months
        assert total_2026 == expected_2026

    def test_calculate_total_deductibles(self) -> None:
        """Test total deductibles calculation."""
        # Year 0 should be Plan + Part B deductibles
        total_2026 = self.calculator.calculate_total_deductibles(0)
        expected_2026 = 257.0 + 210.0
        assert total_2026 == expected_2026

    def test_calculate_annual_costs(self) -> None:
        """Test annual costs calculation for a single year."""
        # Test with utilization (sick)
        costs_sick = self.calculator.calculate_annual_costs(0, is_sick=True)
        expected_sick = (155.0 + 49.0) * 12 + (257.0 + 210.0)  # annual premiums + deductibles
        assert costs_sick == expected_sick
        
        # Test without utilization (healthy)
        costs_healthy = self.calculator.calculate_annual_costs(0, is_sick=False)
        expected_healthy = (155.0 + 49.0) * 12  # only annual premiums
        assert costs_healthy == expected_healthy

    def test_calculate_all_years_costs(self) -> None:
        """Test calculation of costs for all simulation years."""
        # Test with utilization pattern (25 years to match default simulation_years)
        utilization_pattern = [True, False, True, False, False] * 5  # 25 years
        costs = self.calculator.calculate_all_years_costs(utilization_pattern)
        
        assert len(costs) == 25
        
        # Check that sick years have higher costs than healthy years
        for i, is_sick in enumerate(utilization_pattern):
            if is_sick:
                # Should include deductibles - check that cost is reasonable
                assert costs[i] > 0
                # Should be higher than just premiums
                expected_premiums = (155.0 + 49.0) * 12 * (1 + 0.07) ** i
                assert costs[i] > expected_premiums
            else:
                # Should only include premiums - check that cost is reasonable
                assert costs[i] > 0
                # Should be close to just premiums (allow for some tolerance)
                expected_premiums = (155.0 + 49.0) * 12 * (1 + 0.07) ** i
                assert abs(costs[i] - expected_premiums) < expected_premiums * 0.1  # Within 10%

    def test_negative_year_raises_error(self) -> None:
        """Test that negative year raises ValueError."""
        with pytest.raises(ValueError, match="Year must be non-negative"):
            self.calculator.calculate_medigap_premium(-1)
