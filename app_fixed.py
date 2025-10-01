"""Streamlit application for Medicare/Medigap Monte Carlo simulation."""

import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from medigap.models.simulation_parameters import SimulationParameters
from medigap.simulation.monte_carlo import MonteCarloSimulation


def create_parameter_inputs() -> SimulationParameters:
    """Create interactive parameter input widgets and return SimulationParameters object."""
    st.sidebar.header("📊 Simulation Parameters")
    
    # Premium and cost inputs
    st.sidebar.subheader("💰 Base Costs (2026)")
    
    medigap_premium_2026 = st.sidebar.number_input(
        "Medigap Premium (monthly)",
        min_value=50.0,
        max_value=500.0,
        value=155.0,
        step=5.0,
        help="Base Medigap Plan N premium for 2026"
    )
    
    plan_deductible_2026 = st.sidebar.number_input(
        "Plan Deductible (annual)",
        min_value=100.0,
        max_value=1000.0,
        value=257.0,
        step=10.0,
        help="Base plan deductible for 2026"
    )
    
    part_d_premium_2026 = st.sidebar.number_input(
        "Part D Premium (monthly)",
        min_value=10.0,
        max_value=200.0,
        value=49.0,
        step=5.0,
        help="Base Part D premium for 2026"
    )
    
    part_b_deductible_2026 = st.sidebar.number_input(
        "Part B Deductible (annual)",
        min_value=100.0,
        max_value=500.0,
        value=210.0,
        step=10.0,
        help="Base Part B deductible for 2026"
    )
    
    # Growth rate inputs
    st.sidebar.subheader("📈 Growth Rates")
    
    medigap_premium_growth_rate = st.sidebar.slider(
        "Medigap Premium Growth Rate",
        min_value=0.0,
        max_value=0.20,
        value=0.07,
        step=0.01,
        # format="%.1%",
        help="Annual growth rate for Medigap premium"
    )
    
    plan_deductible_growth_rate = st.sidebar.slider(
        "Plan Deductible Growth Rate",
        min_value=0.0,
        max_value=0.20,
        value=0.06,
        step=0.01,
        # format="%.1%",
        help="Annual growth rate for plan deductible"
    )
    
    part_d_premium_growth_rate = st.sidebar.slider(
        "Part D Premium Growth Rate",
        min_value=0.0,
        max_value=0.20,
        value=0.06,
        step=0.01,
        # format="%.1%",
        help="Annual growth rate for Part D premium"
    )
    
    part_b_deductible_growth_rate = st.sidebar.slider(
        "Part B Deductible Growth Rate",
        min_value=0.0,
        max_value=0.20,
        value=0.06,
        step=0.01,
        # format="%.1%",
        help="Annual growth rate for Part B deductible"
    )
    
    # Simulation settings
    st.sidebar.subheader("⚙️ Simulation Setting")
    
    percent_sick = st.sidebar.slider(
        "Percent Sick",
        min_value=0.0,
        max_value=1.0,
        value=0.20,
        step=0.05,
        # format="%.1%",
        help="Probability of being 'sick' (full utilization) in any given year"
    )
    
    num_simulations = st.sidebar.number_input(
        "Number of Simulations",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100,
        help="Number of Monte Carlo simulations to run"
    )
    
    simulation_years = st.sidebar.number_input(
        "Simulation Years",
        min_value=10,
        max_value=50,
        value=25,
        step=5,
        help="Number of years to simulate"
    )
    
    start_year = st.sidebar.number_input(
        "Start Year",
        min_value=2020,
        max_value=2030,
        value=2026,
        step=1,
        help="Starting year for simulation"
    )
    
    return SimulationParameters(
        medigap_premium_2026=medigap_premium_2026,
        medigap_premium_growth_rate=medigap_premium_growth_rate,
        plan_deductible_2026=plan_deductible_2026,
        plan_deductible_growth_rate=plan_deductible_growth_rate,
        part_d_premium_2026=part_d_premium_2026,
        part_d_premium_growth_rate=part_d_premium_growth_rate,
        part_b_deductible_2026=part_b_deductible_2026,
        part_b_deductible_growth_rate=part_b_deductible_growth_rate,
        percent_sick=percent_sick,
        simulation_years=simulation_years,
        start_year=start_year
    )


def display_parameter_summary(params: SimulationParameters):
    """Display a summary of the simulation parameters."""
    st.subheader("📋 Simulation Parameters Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Base Costs (2026):**")
        st.write(f"• Medigap Premium: ${params.medigap_premium_2026:.2f}/month")
        st.write(f"• Plan Deductible: ${params.plan_deductible_2026:.2f}/year")
        st.write(f"• Part D Premium: ${params.part_d_premium_2026:.2f}/month")
        st.write(f"• Part B Deductible: ${params.part_b_deductible_2026:.2f}/year")
    
    with col2:
        st.markdown("**Growth Rates:**")
        st.write(f"• Medigap Premium: {params.medigap_premium_growth_rate:.1%}")
        st.write(f"• Plan Deductible: {params.plan_deductible_growth_rate:.1%}")
        st.write(f"• Part D Premium: {params.part_d_premium_growth_rate:.1%}")
        st.write(f"• Part B Deductible: {params.part_b_deductible_growth_rate:.1%}")
    
    st.markdown("**Simulation Settings:**")
    st.write(f"• Percent Sick: {params.percent_sick:.1%}")
    st.write(f"• Simulation Years: {params.simulation_years}")
    st.write(f"• Start Year: {params.start_year}")


def create_cost_projection_table(params: SimulationParameters, years_to_show=5):
    """Create a table showing cost projections for the first few years."""
    st.subheader("📊 Cost Projections by Year")
    
    from medigap.simulation.cost_calculator import CostCalculator
    calculator = CostCalculator(params)
    
    data = []
    for year in range(min(years_to_show, params.simulation_years)):
        actual_year = params.start_year + year
        
        # Calculate costs for this year
        medigap_premium = calculator.calculate_medigap_premium(year)
        plan_deductible = calculator.calculate_plan_deductible(year)
        part_d_premium = calculator.calculate_part_d_premium(year)
        part_b_deductible = calculator.calculate_part_b_deductible(year)
        
        # Calculate total costs
        total_premiums = (medigap_premium + part_d_premium) * 12
        total_deductibles = plan_deductible + part_b_deductible
        total_annual = total_premiums + total_deductibles
        
        data.append({
            'Year': actual_year,
            'Medigap Premium': f"${medigap_premium:.2f}",
            'Plan Deductible': f"${plan_deductible:.2f}",
            'Part D Premium': f"${part_d_premium:.2f}",
            'Part B Deductible': f"${part_b_deductible:.2f}",
            'Total Annual': f"${total_annual:,.2f}"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def create_cost_projection_chart(years: list, mean_costs: list, std_costs: list) -> go.Figure:
    """Create cost projection chart with confidence intervals."""
    fig = go.Figure()
    
    # Add mean cost line
    fig.add_trace(go.Scatter(
        x=years,
        y=mean_costs,
        mode='lines+markers',
        name='Mean Cost',
        line=dict(color='blue', width=3),
        marker=dict(size=6)
    ))
    
    # Add confidence interval
    upper_bound = [mean + std for mean, std in zip(mean_costs, std_costs)]
    lower_bound = [mean - std for mean, std in zip(mean_costs, std_costs)]
    
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='±1 Standard Deviation',
        showlegend=True
    ))
    
    fig.update_layout(
        title='Annual Cost Projections',
        xaxis_title='Year',
        yaxis_title='Annual Cost ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_lifetime_cost_histogram(lifetime_costs: list) -> go.Figure:
    """Create histogram of lifetime costs."""
    fig = go.Figure(data=[
        go.Histogram(
            x=lifetime_costs,
            nbinsx=50,
            marker_color='lightblue',
            marker_line=dict(color='black', width=1)
        )
    ])
    
    fig.update_layout(
        title='Lifetime Cost Distribution',
        xaxis_title='Lifetime Cost ($)',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    
    return fig


def run_simulation_and_display_results(params: SimulationParameters, num_simulations: int):
    """Run Monte Carlo simulation and display results."""
    st.subheader("🎲 Monte Carlo Simulation Results")
    
    # Create simulation
    simulation = MonteCarloSimulation(params)
    
    # Run simulation
    with st.spinner(f"Running {num_simulations} simulations..."):
        results = simulation.run_comprehensive_simulation(num_simulations)
    
    # Extract results
    lifetime_costs = results['lifetime_costs']
    statistics = results['statistics']
    
    # Display summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Mean Lifetime Cost",
            f"${np.mean(lifetime_costs):,.0f}"
        )
    
    with col2:
        st.metric(
            "Standard Deviation",
            f"${np.std(lifetime_costs):,.0f}"
        )
    
    with col3:
        st.metric(
            "Minimum Cost",
            f"${np.min(lifetime_costs):,.0f}"
        )
    
    with col4:
        st.metric(
            "Maximum Cost",
            f"${np.max(lifetime_costs):,.0f}"
        )
    
    # Create years list for charts
    years = list(range(params.start_year, params.start_year + params.simulation_years))
    
    # Cost projection chart
    st.subheader("📈 Annual Cost Projections")
    cost_chart = create_cost_projection_chart(
        years, 
        results['statistics']['mean_costs'], 
        results['statistics']['std_costs']
    )
    st.plotly_chart(cost_chart, use_container_width=True)
    
    # Lifetime cost histogram
    st.subheader("📊 Lifetime Cost Distribution")
    hist_chart = create_lifetime_cost_histogram(lifetime_costs)
    st.plotly_chart(hist_chart, use_container_width=True)
    
    # Percentile analysis
    st.subheader("📊 Cost Percentiles")
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    percentile_values = [np.percentile(lifetime_costs, p) for p in percentiles]
    
    percentile_data = {
        'Percentile': [f"{p}%" for p in percentiles],
        'Lifetime Cost': [f"${v:,.0f}" for v in percentile_values]
    }
    
    percentile_df = pd.DataFrame(percentile_data)
    st.dataframe(percentile_df, use_container_width=True)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Medicare Plan Simulator",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Medicare Plan Monte Carlo Simulator")
    st.markdown("Project Medicare costs over time using Monte Carlo simulation.")
    
    # Create parameter input interface
    params = create_parameter_inputs()
    
    # Display parameter summary
    display_parameter_summary(params)
    
    # Create cost projection table
    create_cost_projection_table(params)
    
    # Run simulation button
    if st.button("🚀 Run Monte Carlo Simulation", type="primary"):
        run_simulation_and_display_results(params, params.simulation_years)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Note:** This simulation is for educational purposes only. "
        "Actual Medicare costs may vary based on location, health status, and other factors."
    )


if __name__ == "__main__":
    main()

