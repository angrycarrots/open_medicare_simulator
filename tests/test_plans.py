"""Tests for specific plan implementations."""

import pytest
from src.medigap.models.plans import PlanG, PlanHDG


class TestPlanG:
    """Test cases for Plan G implementation."""
    
    def test_plan_g_initialization(self):
        """Test that Plan G initializes with correct default parameters."""
        plan = PlanG()
        
        assert plan.name == "Plan-G"
        assert plan.premium_2026 == 155.0
        assert plan.premium_growth_rate == 0.07
        assert plan.plan_deductible_2026 == 257.0
        assert plan.plan_deductible_growth_rate == 0.06
        assert plan.part_d_premium_2026 == 49.0
        assert plan.part_d_premium_growth_rate == 0.06
        assert plan.part_b_deductible_2026 == 210.0
        assert plan.part_b_deductible_growth_rate == 0.06

    def test_plan_g_custom_parameters(self):
        """Test that Plan G can be initialized with custom parameters."""
        plan = PlanG(percent_sick=0.15, simulation_years=30, start_year=2025)
        
        assert plan.percent_sick == 0.15
        assert plan.simulation_years == 30
        assert plan.start_year == 2025

    def test_plan_g_calculations(self):
        """Test Plan G cost calculations."""
        plan = PlanG()
        
        # Test year 0 calculations
        assert plan.calculate_premium(0) == 155.0
        assert plan.calculate_plan_deductible(0) == 257.0
        
        # Test year 1 calculations (7% premium growth, 6% deductible growth)
        expected_premium_year_1 = 155.0 * 1.07
        expected_deductible_year_1 = 257.0 * 1.06
        
        assert abs(plan.calculate_premium(1) - expected_premium_year_1) < 0.01
        assert abs(plan.calculate_plan_deductible(1) - expected_deductible_year_1) < 0.01


class TestPlanHDG:
    """Test cases for Plan HDG implementation."""
    
    def test_plan_hdg_initialization(self):
        """Test that Plan HDG initializes with correct parameters."""
        plan = PlanHDG()
        
        assert plan.name == "Plan-HDG"
        assert plan.premium_2026 == 40.0
        assert plan.premium_growth_rate == 0.07
        assert plan.plan_deductible_2026 == 2800.0
        assert plan.plan_deductible_growth_rate == 0.06
        assert plan.part_d_premium_2026 == 49.0
        assert plan.part_d_premium_growth_rate == 0.06
        assert plan.part_b_deductible_2026 == 210.0
        assert plan.part_b_deductible_growth_rate == 0.06

    def test_plan_hdg_custom_parameters(self):
        """Test that Plan HDG can be initialized with custom parameters."""
        plan = PlanHDG(percent_sick=0.25, simulation_years=20, start_year=2027)
        
        assert plan.percent_sick == 0.25
        assert plan.simulation_years == 20
        assert plan.start_year == 2027

    def test_plan_hdg_calculations(self):
        """Test Plan HDG cost calculations."""
        plan = PlanHDG()
        
        # Test year 0 calculations
        assert plan.calculate_premium(0) == 40.0
        assert plan.calculate_plan_deductible(0) == 2800.0
        
        # Test year 1 calculations (7% premium growth, 6% deductible growth)
        expected_premium_year_1 = 40.0 * 1.07
        expected_deductible_year_1 = 2800.0 * 1.06
        
        assert abs(plan.calculate_premium(1) - expected_premium_year_1) < 0.01
        assert abs(plan.calculate_plan_deductible(1) - expected_deductible_year_1) < 0.01

    def test_plan_hdg_vs_plan_g_comparison(self):
        """Test comparison between Plan HDG and Plan G."""
        plan_g = PlanG()
        plan_hdg = PlanHDG()
        
        # Plan HDG should have lower premium but higher deductible
        assert plan_hdg.premium_2026 < plan_g.premium_2026
        assert plan_hdg.plan_deductible_2026 > plan_g.plan_deductible_2026
        
        # Part D and Part B should be the same
        assert plan_hdg.part_d_premium_2026 == plan_g.part_d_premium_2026
        assert plan_hdg.part_b_deductible_2026 == plan_g.part_b_deductible_2026

    def test_plan_hdg_healthy_vs_sick_costs(self):
        """Test Plan HDG costs for healthy vs sick scenarios."""
        plan = PlanHDG()
        
        # Healthy scenario (year 0): only premiums
        healthy_cost = plan.calculate_annual_costs(0, False)
        expected_healthy = (40.0 + 49.0) * 12  # 1068
        assert abs(healthy_cost - expected_healthy) < 0.01
        
        # Sick scenario (year 0): premiums + deductibles
        sick_cost = plan.calculate_annual_costs(0, True)
        expected_sick = (40.0 + 49.0) * 12 + 2800.0 + 210.0  # 1068 + 3010 = 4078
        assert abs(sick_cost - expected_sick) < 0.01

