"""Visualization utilities for Medicare/Medigap simulation results."""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional


class Visualization:
    """Visualization class for creating charts and graphs from simulation results.
    
    This class provides methods to create various types of charts including
    expenditure projections, lifetime cost distributions, and utilization patterns.
    """
    
    def __init__(self) -> None:
        """Initialize the visualization class."""
        # Set default matplotlib style
        plt.style.use('default')
    
    def create_expenditure_chart(
        self,
        years: List[int],
        mean_costs: List[float],
        std_costs: List[float],
        title: str = "Medicare/Medigap Cost Projection (2026-2050)",
        save_path: Optional[str] = None
    ) -> None:
        """Create a line chart showing mean costs with confidence intervals.
        
        Args:
            years: List of years for the x-axis
            mean_costs: List of mean costs for each year
            std_costs: List of standard deviations for each year
            title: Chart title
            save_path: Optional path to save the chart
            
        Raises:
            ValueError: If years and costs lists have different lengths
        """
        if len(years) != len(mean_costs) or len(years) != len(std_costs):
            raise ValueError("Years and costs must have the same length")
        
        # Create the figure
        plt.figure(figsize=(12, 8))
        
        # Convert to numpy arrays for easier calculation
        years_array = np.array(years)
        mean_costs_array = np.array(mean_costs)
        std_costs_array = np.array(std_costs)
        
        # Plot mean costs
        plt.plot(years_array, mean_costs_array, 'b-', linewidth=2, label='Mean Costs')
        
        # Add confidence intervals (mean ± std)
        upper_bound = mean_costs_array + std_costs_array
        lower_bound = mean_costs_array - std_costs_array
        
        plt.fill_between(
            years_array, lower_bound, upper_bound,
            alpha=0.3, color='blue', label='±1 Standard Deviation'
        )
        
        # Customize the chart
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Annual Cost ($)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis to show currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save or show the chart
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    def create_lifetime_cost_histogram(
        self,
        lifetime_costs: List[float],
        title: str = "Distribution of Lifetime Medicare/Medigap Costs",
        save_path: Optional[str] = None
    ) -> None:
        """Create a histogram showing the distribution of lifetime costs.
        
        Args:
            lifetime_costs: List of total lifetime costs from simulations
            title: Chart title
            save_path: Optional path to save the chart
        """
        plt.figure(figsize=(10, 6))
        
        # Create histogram
        plt.hist(lifetime_costs, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        
        # Add statistics
        mean_cost = np.mean(lifetime_costs)
        median_cost = np.median(lifetime_costs)
        std_cost = np.std(lifetime_costs)
        
        # Add vertical lines for mean and median
        plt.axvline(mean_cost, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_cost:,.0f}')
        plt.axvline(median_cost, color='green', linestyle='--', linewidth=2, label=f'Median: ${median_cost:,.0f}')
        
        # Customize the chart
        plt.xlabel('Lifetime Cost ($)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis to show currency
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add text box with statistics
        stats_text = f'Mean: ${mean_cost:,.0f}\nMedian: ${median_cost:,.0f}\nStd Dev: ${std_cost:,.0f}'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Save or show the chart
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    def create_utilization_chart(
        self,
        years: List[int],
        utilization_rates: List[float],
        title: str = "Utilization Rate by Year",
        save_path: Optional[str] = None
    ) -> None:
        """Create a bar chart showing utilization rates by year.
        
        Args:
            years: List of years for the x-axis
            utilization_rates: List of utilization rates (0-1) for each year
            title: Chart title
            save_path: Optional path to save the chart
        """
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        bars = plt.bar(years, utilization_rates, alpha=0.7, color='orange', edgecolor='black')
        
        # Add value labels on top of bars
        for bar, rate in zip(bars, utilization_rates):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{rate:.1%}', ha='center', va='bottom')
        
        # Customize the chart
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Utilization Rate', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as percentage
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0%}'))
        
        # Set y-axis limits
        plt.ylim(0, max(utilization_rates) * 1.2)
        
        plt.tight_layout()
        
        # Save or show the chart
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    def create_comprehensive_dashboard(
        self,
        years: List[int],
        mean_costs: List[float],
        std_costs: List[float],
        lifetime_costs: List[float],
        utilization_rates: List[float],
        save_path: Optional[str] = None
    ) -> None:
        """Create a comprehensive dashboard with multiple charts.
        
        Args:
            years: List of years for the x-axis
            mean_costs: List of mean costs for each year
            std_costs: List of standard deviations for each year
            lifetime_costs: List of total lifetime costs from simulations
            utilization_rates: List of utilization rates for each year
            save_path: Optional path to save the dashboard
        """
        # Create a 2x2 subplot layout
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Chart 1: Expenditure projection
        ax1.plot(years, mean_costs, 'b-', linewidth=2, label='Mean Costs')
        upper_bound = np.array(mean_costs) + np.array(std_costs)
        lower_bound = np.array(mean_costs) - np.array(std_costs)
        ax1.fill_between(years, lower_bound, upper_bound, alpha=0.3, color='blue')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Annual Cost ($)')
        ax1.set_title('Cost Projection with Confidence Intervals')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Chart 2: Lifetime cost distribution
        ax2.hist(lifetime_costs, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        mean_cost = np.mean(lifetime_costs)
        median_cost = np.median(lifetime_costs)
        ax2.axvline(mean_cost, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_cost:,.0f}')
        ax2.axvline(median_cost, color='green', linestyle='--', linewidth=2, label=f'Median: ${median_cost:,.0f}')
        ax2.set_xlabel('Lifetime Cost ($)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Lifetime Cost Distribution')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Chart 3: Utilization rates
        bars = ax3.bar(years, utilization_rates, alpha=0.7, color='orange', edgecolor='black')
        for bar, rate in zip(bars, utilization_rates):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{rate:.1%}', ha='center', va='bottom')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Utilization Rate')
        ax3.set_title('Utilization Rate by Year')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0%}'))
        
        # Chart 4: Cumulative costs
        cumulative_costs = np.cumsum(mean_costs)
        ax4.plot(years, cumulative_costs, 'g-', linewidth=2, label='Cumulative Costs')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Cumulative Cost ($)')
        ax4.set_title('Cumulative Cost Projection')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Overall title
        fig.suptitle('Medicare/Medigap Cost Analysis Dashboard', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Save or show the dashboard
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
