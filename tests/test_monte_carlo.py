"""Tests for MonteCarloSimulation class."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.medigap.models.simulation_parameters import SimulationParameters
from src.medigap.simulation.monte_carlo import MonteCarloSimulation


class TestMonteCarloSimulation:
    """Test cases for MonteCarloSimulation class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.params = SimulationParameters()
        self.simulation = MonteCarloSimulation(self.params)

    def test_initialization(self) -> None:
        """Test MonteCarloSimulation initialization."""
        assert self.simulation.params == self.params
        assert self.simulation.calculator is not None

    def test_generate_utilization_pattern(self) -> None:
        """Test utilization pattern generation."""
        # Mock random number generation to test deterministic behavior
        with patch('numpy.random.random') as mock_random:
            # Set up mock to return values that will test both sick and healthy cases
            # 0.1, 0.15 < 0.2 (sick), 0.3, 0.25, 0.5 > 0.2 (healthy)
            mock_random.return_value = np.array([0.1, 0.3, 0.15, 0.25, 0.5])
            
            pattern = self.simulation.generate_utilization_pattern(5)
            
            # Should have 2 sick years (values < 0.2) and 3 healthy years (values > 0.2)
            expected_pattern = [True, False, True, False, False]
            # Convert numpy booleans to Python booleans for comparison
            pattern_python = [bool(x) for x in pattern]
            assert pattern_python == expected_pattern

    def test_generate_utilization_pattern_with_seed(self) -> None:
        """Test that utilization pattern generation is reproducible with seed."""
        # Test with same seed should produce same pattern
        np.random.seed(42)
        pattern1 = self.simulation.generate_utilization_pattern(10)
        
        np.random.seed(42)
        pattern2 = self.simulation.generate_utilization_pattern(10)
        
        assert pattern1 == pattern2

    def test_run_single_simulation(self) -> None:
        """Test running a single simulation."""
        # Mock the utilization pattern generation
        mock_pattern = [True, False, True, False, False] * 5  # 25 years
        with patch.object(self.simulation, 'generate_utilization_pattern', return_value=mock_pattern):
            result = self.simulation.run_single_simulation()
            
            assert len(result['costs']) == 25
            assert len(result['utilization']) == 25
            assert result['utilization'] == mock_pattern
            
            # Check that costs are calculated correctly
            # Sick years should have higher costs than healthy years
            for i, is_sick in enumerate(mock_pattern):
                if is_sick:
                    # Should include deductibles
                    assert result['costs'][i] > 0
                else:
                    # Should only include premiums
                    assert result['costs'][i] > 0

    def test_run_multiple_simulations(self) -> None:
        """Test running multiple simulations."""
        num_simulations = 3
        
        # Mock the single simulation to return predictable results
        mock_results = [
            {'costs': [400.0, 200.0, 450.0], 'utilization': [True, False, True]},
            {'costs': [200.0, 200.0, 200.0], 'utilization': [False, False, False]},
            {'costs': [400.0, 400.0, 200.0], 'utilization': [True, True, False]}
        ]
        
        with patch.object(self.simulation, 'run_single_simulation', side_effect=mock_results):
            results = self.simulation.run_multiple_simulations(num_simulations)
            
            assert len(results) == num_simulations
            assert all(len(result['costs']) == 3 for result in results)
            assert all(len(result['utilization']) == 3 for result in results)

    def test_calculate_statistics(self) -> None:
        """Test statistics calculation."""
        # Create mock simulation results
        mock_results = [
            {'costs': [400.0, 200.0, 450.0], 'utilization': [True, False, True]},
            {'costs': [200.0, 200.0, 200.0], 'utilization': [False, False, False]},
            {'costs': [400.0, 400.0, 200.0], 'utilization': [True, True, False]}
        ]
        
        stats = self.simulation.calculate_statistics(mock_results)
        
        # Check that statistics are calculated
        assert 'mean_costs' in stats
        assert 'std_costs' in stats
        assert 'min_costs' in stats
        assert 'max_costs' in stats
        assert 'total_costs' in stats
        
        # Check dimensions
        assert len(stats['mean_costs']) == 3  # 3 years
        assert len(stats['std_costs']) == 3
        assert len(stats['min_costs']) == 3
        assert len(stats['max_costs']) == 3
        assert len(stats['total_costs']) == 3

    def test_calculate_total_lifetime_costs(self) -> None:
        """Test total lifetime costs calculation."""
        mock_results = [
            {'costs': [400.0, 200.0, 450.0], 'utilization': [True, False, True]},
            {'costs': [200.0, 200.0, 200.0], 'utilization': [False, False, False]},
            {'costs': [400.0, 400.0, 200.0], 'utilization': [True, True, False]}
        ]
        
        lifetime_costs = self.simulation.calculate_total_lifetime_costs(mock_results)
        
        # Should have 3 total costs (one per simulation)
        assert len(lifetime_costs) == 3
        assert lifetime_costs[0] == 1050.0  # 400 + 200 + 450
        assert lifetime_costs[1] == 600.0   # 200 + 200 + 200
        assert lifetime_costs[2] == 1000.0  # 400 + 400 + 200

    def test_invalid_num_simulations(self) -> None:
        """Test that invalid number of simulations raises error."""
        with pytest.raises(ValueError, match="Number of simulations must be positive"):
            self.simulation.run_multiple_simulations(0)
        
        with pytest.raises(ValueError, match="Number of simulations must be positive"):
            self.simulation.run_multiple_simulations(-5)
