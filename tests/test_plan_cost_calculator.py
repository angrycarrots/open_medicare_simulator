"""Tests for the PlanCostCalculator class."""

import pytest
from src.medigap.models.plans import PlanG, PlanHDG
from src.medigap.simulation.plan_cost_calculator import PlanCostCalculator


class TestPlanCostCalculator:
    """Test cases for the PlanCostCalculator class."""
    
    def test_calculator_initialization(self):
        """Test that PlanCostCalculator initializes correctly."""
        plan = PlanG()
        calculator = PlanCostCalculator(plan)
        
        assert calculator.plan == plan

    def test_calculate_premium(self):
        """Test premium calculation through calculator."""
        plan = PlanG()
        calculator = PlanCostCalculator(plan)
        
        # Year 0
        assert calculator.calculate_premium(0) == 155.0
        
        # Year 1 (7% growth)
        expected = 155.0 * 1.07
        assert abs(calculator.calculate_premium(1) - expected) < 0.01

    def test_calculate_plan_deductible(self):
        """Test plan deductible calculation through calculator."""
        plan = PlanG()
        calculator = PlanCostCalculator(plan)
        
        # Year 0
        assert calculator.calculate_plan_deductible(0) == 257.0
        
        # Year 1 (6% growth)
        expected = 257.0 * 1.06
        assert abs(calculator.calculate_plan_deductible(1) - expected) < 0.01

    def test_calculate_total_premiums(self):
        """Test total premiums calculation."""
        plan = PlanG()
        calculator = PlanCostCalculator(plan)
        
        # Year 0: (155 + 49) * 12 = 2448
        expected = (155.0 + 49.0) * 12
        assert abs(calculator.calculate_total_premiums(0) - expected) < 0.01

    def test_calculate_total_deductibles(self):
        """Test total deductibles calculation."""
        plan = PlanG()
        calculator = PlanCostCalculator(plan)
        
        # Year 0: 257 + 210 = 467
        expected = 257.0 + 210.0
        assert abs(calculator.calculate_total_deductibles(0) - expected) < 0.01

    def test_calculate_annual_costs(self):
        """Test annual costs calculation."""
        plan = PlanG()
        calculator = PlanCostCalculator(plan)
        
        # Healthy scenario
        healthy_cost = calculator.calculate_annual_costs(0, False)
        expected_healthy = (155.0 + 49.0) * 12  # 2448
        assert abs(healthy_cost - expected_healthy) < 0.01
        
        # Sick scenario
        sick_cost = calculator.calculate_annual_costs(0, True)
        expected_sick = (155.0 + 49.0) * 12 + 257.0 + 210.0  # 2448 + 467 = 2915
        assert abs(sick_cost - expected_sick) < 0.01

    def test_calculate_all_years_costs(self):
        """Test calculation of costs for all years."""
        plan = PlanG(simulation_years=3)
        calculator = PlanCostCalculator(plan)
        
        # Create a utilization pattern: sick in year 0, healthy in years 1-2
        utilization_pattern = [True, False, False]
        
        costs = calculator.calculate_all_years_costs(utilization_pattern)
        
        assert len(costs) == 3
        
        # Year 0: sick (premiums + deductibles)
        expected_year_0 = (155.0 + 49.0) * 12 + 257.0 + 210.0
        assert abs(costs[0] - expected_year_0) < 0.01
        
        # Year 1: healthy (premiums only)
        expected_year_1 = (155.0 * 1.07 + 49.0 * 1.06) * 12
        assert abs(costs[1] - expected_year_1) < 0.01
        
        # Year 2: healthy (premiums only)
        expected_year_2 = (155.0 * (1.07 ** 2) + 49.0 * (1.06 ** 2)) * 12
        assert abs(costs[2] - expected_year_2) < 0.01

    def test_calculate_all_years_costs_wrong_length(self):
        """Test that calculate_all_years_costs raises error for wrong pattern length."""
        plan = PlanG(simulation_years=3)
        calculator = PlanCostCalculator(plan)
        
        # Wrong length utilization pattern
        utilization_pattern = [True, False]  # Only 2 years, should be 3
        
        with pytest.raises(ValueError, match="Utilization pattern length"):
            calculator.calculate_all_years_costs(utilization_pattern)

    def test_get_plan_summary(self):
        """Test getting plan summary."""
        plan = PlanHDG()
        calculator = PlanCostCalculator(plan)
        
        summary = calculator.get_plan_summary()
        
        assert summary['name'] == 'Plan-HDG'
        assert summary['premium_2026'] == 40.0
        assert summary['premium_growth_rate'] == 0.07
        assert summary['plan_deductible_2026'] == 2800.0
        assert summary['plan_deductible_growth_rate'] == 0.06
        assert summary['part_d_premium_2026'] == 49.0
        assert summary['part_d_premium_growth_rate'] == 0.06
        assert summary['part_b_deductible_2026'] == 210.0
        assert summary['part_b_deductible_growth_rate'] == 0.06
        assert summary['percent_sick'] == 0.20
        assert summary['simulation_years'] == 25
        assert summary['start_year'] == 2026

