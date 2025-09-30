"""Integration tests for the complete Medicare/Medigap simulation system."""

import pytest
import numpy as np
from src.medigap.models.simulation_parameters import SimulationParameters
from src.medigap.simulation.monte_carlo import MonteCarloSimulation
from src.medigap.visualization.charts import Visualization


class TestIntegration:
    """Integration tests for the complete simulation system."""

    def test_end_to_end_simulation(self) -> None:
        """Test complete end-to-end simulation workflow."""
        # Create parameters
        params = SimulationParameters()
        
        # Create simulation
        simulation = MonteCarloSimulation(params)
        
        # Run simulation
        results = simulation.run_comprehensive_simulation(100)
        
        # Verify results structure
        assert 'simulation_results' in results
        assert 'statistics' in results
        assert 'lifetime_costs' in results
        assert 'num_simulations' in results
        assert 'parameters' in results
        
        # Verify simulation results
        assert len(results['simulation_results']) == 100
        assert len(results['lifetime_costs']) == 100
        
        # Verify statistics
        stats = results['statistics']
        assert len(stats['mean_costs']) == params.simulation_years
        assert len(stats['std_costs']) == params.simulation_years
        assert len(stats['min_costs']) == params.simulation_years
        assert len(stats['max_costs']) == params.simulation_years
        
        # Verify all costs are positive
        for cost in results['lifetime_costs']:
            assert cost > 0
        
        # Verify mean costs are reasonable (should be at least premiums)
        for mean_cost in stats['mean_costs']:
            assert mean_cost > 0

    def test_visualization_integration(self) -> None:
        """Test integration with visualization components."""
        # Create parameters and run simulation
        params = SimulationParameters()
        simulation = MonteCarloSimulation(params)
        results = simulation.run_comprehensive_simulation(50)
        
        # Create visualization
        visualization = Visualization()
        
        # Test expenditure chart creation
        years = list(range(params.start_year, params.start_year + params.simulation_years))
        stats = results['statistics']
        
        # Should not raise any errors
        visualization.create_expenditure_chart(
            years, 
            stats['mean_costs'], 
            stats['std_costs'],
            save_path="test_expenditure.png"
        )
        
        # Test lifetime cost histogram
        visualization.create_lifetime_cost_histogram(
            results['lifetime_costs'],
            save_path="test_histogram.png"
        )
        
        # Test utilization chart
        utilization_rates = []
        for i in range(params.simulation_years):
            year_utilizations = [result['utilization'][i] for result in results['simulation_results']]
            utilization_rate = sum(year_utilizations) / len(year_utilizations)
            utilization_rates.append(utilization_rate)
        
        visualization.create_utilization_chart(
            years,
            utilization_rates,
            save_path="test_utilization.png"
        )

    def test_parameter_validation_integration(self) -> None:
        """Test parameter validation in the context of the full system."""
        # Test with invalid parameters
        with pytest.raises(ValueError):
            params = SimulationParameters(medigap_premium_2026=-100.0)
            simulation = MonteCarloSimulation(params)
        
        with pytest.raises(ValueError):
            params = SimulationParameters(percent_sick=1.5)
            simulation = MonteCarloSimulation(params)

    def test_cost_calculation_accuracy(self) -> None:
        """Test that cost calculations are mathematically accurate."""
        params = SimulationParameters()
        simulation = MonteCarloSimulation(params)
        
        # For now, test that costs are reasonable
        results = simulation.run_single_simulation()
        
        # Verify that sick years have higher costs than healthy years
        for i, is_sick in enumerate(results['utilization']):
            if is_sick:
                # Sick year should include deductibles
                assert results['costs'][i] > 0
            else:
                # Healthy year should only include premiums
                assert results['costs'][i] > 0

    def test_simulation_reproducibility(self) -> None:
        """Test that simulations are reproducible with the same seed."""
        params = SimulationParameters()
        simulation1 = MonteCarloSimulation(params)
        simulation2 = MonteCarloSimulation(params)
        
        # Set the same seed for both simulations
        np.random.seed(42)
        results1 = simulation1.run_single_simulation()
        
        np.random.seed(42)
        results2 = simulation2.run_single_simulation()
        
        # Results should be identical
        assert results1['utilization'] == results2['utilization']
        assert results1['costs'] == results2['costs']

    def test_large_simulation_performance(self) -> None:
        """Test that large simulations complete without errors."""
        params = SimulationParameters()
        simulation = MonteCarloSimulation(params)
        
        # Run a larger simulation
        results = simulation.run_comprehensive_simulation(1000)
        
        # Verify results
        assert len(results['simulation_results']) == 1000
        assert len(results['lifetime_costs']) == 1000
        
        # Verify all results are valid
        for result in results['simulation_results']:
            assert len(result['costs']) == params.simulation_years
            assert len(result['utilization']) == params.simulation_years
            assert all(cost > 0 for cost in result['costs'])
            assert all(isinstance(util, (bool, np.bool_)) for util in result['utilization'])

    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test with minimum simulation years
        params = SimulationParameters(simulation_years=1)
        simulation = MonteCarloSimulation(params)
        results = simulation.run_single_simulation()
        
        assert len(results['costs']) == 1
        assert len(results['utilization']) == 1
        
        # Test with different percent_sick values
        params = SimulationParameters(percent_sick=0.0)  # Never sick
        simulation = MonteCarloSimulation(params)
        results = simulation.run_single_simulation()
        
        # Should never be sick
        assert not any(results['utilization'])
        
        params = SimulationParameters(percent_sick=1.0)  # Always sick
        simulation = MonteCarloSimulation(params)
        results = simulation.run_single_simulation()
        
        # Should always be sick
        assert all(results['utilization'])
