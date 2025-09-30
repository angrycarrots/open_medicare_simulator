"""Tests for Visualization class."""

import pytest
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
from src.medigap.visualization.charts import Visualization


class TestVisualization:
    """Test cases for Visualization class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.visualization = Visualization()

    def test_initialization(self) -> None:
        """Test Visualization initialization."""
        assert self.visualization is not None

    def test_create_expenditure_chart(self) -> None:
        """Test creation of expenditure chart."""
        # Mock data
        years = list(range(2026, 2031))  # 5 years
        mean_costs = [400.0, 420.0, 440.0, 460.0, 480.0]
        std_costs = [50.0, 55.0, 60.0, 65.0, 70.0]
        
        # Mock matplotlib to avoid actual plotting
        with patch('matplotlib.pyplot.figure') as mock_figure, \
             patch('matplotlib.pyplot.plot') as mock_plot, \
             patch('matplotlib.pyplot.fill_between') as mock_fill, \
             patch('matplotlib.pyplot.xlabel') as mock_xlabel, \
             patch('matplotlib.pyplot.ylabel') as mock_ylabel, \
             patch('matplotlib.pyplot.title') as mock_title, \
             patch('matplotlib.pyplot.grid') as mock_grid, \
             patch('matplotlib.pyplot.legend') as mock_legend, \
             patch('matplotlib.pyplot.show') as mock_show:
            
            self.visualization.create_expenditure_chart(years, mean_costs, std_costs)
            
            # Verify that plotting functions were called
            assert mock_figure.call_count >= 1
            mock_plot.assert_called()
            mock_fill.assert_called()
            mock_xlabel.assert_called_once()
            mock_ylabel.assert_called_once()
            mock_title.assert_called_once()
            mock_grid.assert_called_once()
            mock_legend.assert_called_once()

    def test_create_expenditure_chart_with_custom_title(self) -> None:
        """Test creation of expenditure chart with custom title."""
        years = list(range(2026, 2031))
        mean_costs = [400.0, 420.0, 440.0, 460.0, 480.0]
        std_costs = [50.0, 55.0, 60.0, 65.0, 70.0]
        custom_title = "Custom Medicare Cost Projection"
        
        with patch('matplotlib.pyplot.figure') as mock_figure, \
             patch('matplotlib.pyplot.plot') as mock_plot, \
             patch('matplotlib.pyplot.fill_between') as mock_fill, \
             patch('matplotlib.pyplot.xlabel') as mock_xlabel, \
             patch('matplotlib.pyplot.ylabel') as mock_ylabel, \
             patch('matplotlib.pyplot.title') as mock_title, \
             patch('matplotlib.pyplot.grid') as mock_grid, \
             patch('matplotlib.pyplot.legend') as mock_legend, \
             patch('matplotlib.pyplot.show') as mock_show:
            
            self.visualization.create_expenditure_chart(
                years, mean_costs, std_costs, title=custom_title
            )
            
            # Verify custom title was used (with additional formatting parameters)
            mock_title.assert_called()
            # Check that the title was called with the custom title as first argument
            assert mock_title.call_args[0][0] == custom_title

    def test_create_lifetime_cost_histogram(self) -> None:
        """Test creation of lifetime cost histogram."""
        lifetime_costs = [10000.0, 12000.0, 11000.0, 13000.0, 11500.0]
        
        with patch('matplotlib.pyplot.figure') as mock_figure, \
             patch('matplotlib.pyplot.hist') as mock_hist, \
             patch('matplotlib.pyplot.xlabel') as mock_xlabel, \
             patch('matplotlib.pyplot.ylabel') as mock_ylabel, \
             patch('matplotlib.pyplot.title') as mock_title, \
             patch('matplotlib.pyplot.grid') as mock_grid, \
             patch('matplotlib.pyplot.show') as mock_show:
            
            self.visualization.create_lifetime_cost_histogram(lifetime_costs)
            
            # Verify that plotting functions were called
            assert mock_figure.call_count >= 1
            mock_hist.assert_called_once()
            mock_xlabel.assert_called_once()
            mock_ylabel.assert_called_once()
            mock_title.assert_called_once()
            mock_grid.assert_called_once()

    def test_create_utilization_chart(self) -> None:
        """Test creation of utilization pattern chart."""
        years = list(range(2026, 2031))
        utilization_rates = [0.2, 0.25, 0.18, 0.22, 0.19]
        
        with patch('matplotlib.pyplot.figure') as mock_figure, \
             patch('matplotlib.pyplot.bar') as mock_bar, \
             patch('matplotlib.pyplot.xlabel') as mock_xlabel, \
             patch('matplotlib.pyplot.ylabel') as mock_ylabel, \
             patch('matplotlib.pyplot.title') as mock_title, \
             patch('matplotlib.pyplot.grid') as mock_grid, \
             patch('matplotlib.pyplot.show') as mock_show:
            
            self.visualization.create_utilization_chart(years, utilization_rates)
            
            # Verify that plotting functions were called
            assert mock_figure.call_count >= 1
            mock_bar.assert_called_once()
            mock_xlabel.assert_called_once()
            mock_ylabel.assert_called_once()
            mock_title.assert_called_once()
            mock_grid.assert_called_once()

    def test_save_chart(self) -> None:
        """Test saving chart to file."""
        years = list(range(2026, 2031))
        mean_costs = [400.0, 420.0, 440.0, 460.0, 480.0]
        std_costs = [50.0, 55.0, 60.0, 65.0, 70.0]
        
        with patch('matplotlib.pyplot.figure') as mock_figure, \
             patch('matplotlib.pyplot.plot') as mock_plot, \
             patch('matplotlib.pyplot.fill_between') as mock_fill, \
             patch('matplotlib.pyplot.xlabel') as mock_xlabel, \
             patch('matplotlib.pyplot.ylabel') as mock_ylabel, \
             patch('matplotlib.pyplot.title') as mock_title, \
             patch('matplotlib.pyplot.grid') as mock_grid, \
             patch('matplotlib.pyplot.legend') as mock_legend, \
             patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.close') as mock_close:
            
            self.visualization.create_expenditure_chart(
                years, mean_costs, std_costs, save_path="test_chart.png"
            )
            
            # Verify that savefig was called
            mock_savefig.assert_called_once_with("test_chart.png", dpi=300, bbox_inches='tight')
            mock_close.assert_called_once()

    def test_empty_data_handling(self) -> None:
        """Test handling of empty data."""
        # Test mismatched lengths - should raise error before any matplotlib calls
        with pytest.raises(ValueError, match="Years and costs must have the same length"):
            self.visualization.create_expenditure_chart([2026, 2027], [400.0], [50.0])
        
        # Test different mismatched lengths
        with pytest.raises(ValueError, match="Years and costs must have the same length"):
            self.visualization.create_expenditure_chart([2026], [400.0, 500.0], [50.0, 60.0])

    def test_negative_costs_handling(self) -> None:
        """Test handling of negative costs."""
        years = [2026, 2027]
        mean_costs = [-100.0, 200.0]  # Negative cost
        std_costs = [50.0, 60.0]
        
        # Should not raise an error, but should handle gracefully
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.fill_between'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.show'):
            
            # Should not raise an error
            self.visualization.create_expenditure_chart(years, mean_costs, std_costs)
