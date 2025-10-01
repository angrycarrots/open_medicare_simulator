"""Tests for the Plan base class."""

import pytest
from src.medigap.models.plan import Plan


class TestPlan(Plan):
    """Test implementation of Plan for testing purposes."""
    
    def __init__(self, **kwargs):
        # Set default values
        defaults = {
            'name': "Test-Plan",
            'premium_2026': 100.0,
            'premium_growth_rate': 0.05,
            'plan_deductible_2026': 500.0,
            'plan_deductible_growth_rate': 0.04,
        }
        # Update defaults with any provided kwargs
        defaults.update(kwargs)
        super().__init__(**defaults)


class TestPlanClass:
    """Test cases for the Plan base class."""
    
    def test_plan_initialization(self):
        """Test that Plan initializes correctly with valid parameters."""
        plan = TestPlan()
        
        assert plan.name == "Test-Plan"
        assert plan.premium_2026 == 100.0
        assert plan.premium_growth_rate == 0.05
        assert plan.plan_deductible_2026 == 500.0
        assert plan.plan_deductible_growth_rate == 0.04
        assert plan.part_d_premium_2026 == 49.0
        assert plan.part_d_premium_growth_rate == 0.06
        assert plan.part_b_deductible_2026 == 210.0
        assert plan.part_b_deductible_growth_rate == 0.06
        assert plan.percent_sick == 0.20
        assert plan.simulation_years == 25
        assert plan.start_year == 2026

    def test_plan_validation_negative_premium(self):
        """Test that Plan raises ValueError for negative premium."""
        with pytest.raises(ValueError, match="Premium must be positive"):
            TestPlan(premium_2026=-100.0)

    def test_plan_validation_negative_growth_rate(self):
        """Test that Plan raises ValueError for negative growth rate."""
        with pytest.raises(ValueError, match="Premium growth rate must be non-negative"):
            TestPlan(premium_growth_rate=-0.05)

    def test_plan_validation_invalid_percent_sick(self):
        """Test that Plan raises ValueError for invalid percent_sick."""
        with pytest.raises(ValueError, match="Percent sick must be between 0 and 1"):
            TestPlan(percent_sick=1.5)

    def test_plan_validation_negative_simulation_years(self):
        """Test that Plan raises ValueError for negative simulation years."""
        with pytest.raises(ValueError, match="Simulation years must be positive"):
            TestPlan(simulation_years=-5)

    def test_calculate_premium(self):
        """Test premium calculation over time."""
        plan = TestPlan()
        
        # Year 0 (start year)
        assert plan.calculate_premium(0) == 100.0
        
        # Year 1 (5% growth)
        expected_year_1 = 100.0 * 1.05
        assert abs(plan.calculate_premium(1) - expected_year_1) < 0.01
        
        # Year 2 (5% growth compounded)
        expected_year_2 = 100.0 * (1.05 ** 2)
        assert abs(plan.calculate_premium(2) - expected_year_2) < 0.01

    def test_calculate_premium_negative_year(self):
        """Test that calculate_premium raises ValueError for negative year."""
        plan = TestPlan()
        
        with pytest.raises(ValueError, match="Year must be non-negative"):
            plan.calculate_premium(-1)

    def test_calculate_plan_deductible(self):
        """Test plan deductible calculation over time."""
        plan = TestPlan()
        
        # Year 0 (start year)
        assert plan.calculate_plan_deductible(0) == 500.0
        
        # Year 1 (4% growth)
        expected_year_1 = 500.0 * 1.04
        assert abs(plan.calculate_plan_deductible(1) - expected_year_1) < 0.01

    def test_calculate_total_premiums(self):
        """Test total premiums calculation (plan + Part D)."""
        plan = TestPlan()
        
        # Year 0: (100 + 49) * 12 = 1788
        expected_total = (100.0 + 49.0) * 12
        assert abs(plan.calculate_total_premiums(0) - expected_total) < 0.01

    def test_calculate_total_deductibles(self):
        """Test total deductibles calculation (plan + Part B)."""
        plan = TestPlan()
        
        # Year 0: 500 + 210 = 710
        expected_total = 500.0 + 210.0
        assert abs(plan.calculate_total_deductibles(0) - expected_total) < 0.01

    def test_calculate_annual_costs_healthy(self):
        """Test annual costs calculation when healthy (no deductibles)."""
        plan = TestPlan()
        
        # Year 0: only premiums, no deductibles
        expected_cost = (100.0 + 49.0) * 12  # 1788
        assert abs(plan.calculate_annual_costs(0, False) - expected_cost) < 0.01

    def test_calculate_annual_costs_sick(self):
        """Test annual costs calculation when sick (premiums + deductibles)."""
        plan = TestPlan()
        
        # Year 0: premiums + deductibles
        expected_cost = (100.0 + 49.0) * 12 + 500.0 + 210.0  # 1788 + 710 = 2498
        assert abs(plan.calculate_annual_costs(0, True) - expected_cost) < 0.01

    def test_string_representation(self):
        """Test string representation of the plan."""
        plan = TestPlan()
        
        expected_str = "Test-Plan: Premium $100.00, Deductible $500.00"
        assert str(plan) == expected_str

    def test_repr_representation(self):
        """Test detailed string representation of the plan."""
        plan = TestPlan()
        
        repr_str = repr(plan)
        assert "TestPlan" in repr_str
        assert "name='Test-Plan'" in repr_str
        assert "premium_2026=100.0" in repr_str
        assert "premium_growth_rate=0.05" in repr_str
