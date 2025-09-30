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
        max_value=0.15,
        value=0.07,
        step=0.01,
        format="%.1%",
        help="Annual growth rate for Medigap premium"
    )
    
    plan_deductible_growth_rate = st.sidebar.slider(
        "Plan Deductible Growth Rate",
        min_value=0.0,
        max_value=0.15,
        value=0.06,
        step=0.01,
        format="%.1%",
        help="Annual growth rate for plan deductible"
    )
    
    part_d_premium_growth_rate = st.sidebar.slider(
        "Part D Premium Growth Rate",
        min_value=0.0,
        max_value=0.15,
        value=0.06,
        step=0.01,
        format="%.1%",
        help="Annual growth rate for Part D premium"
    )
    
    part_b_deductible_growth_rate = st.sidebar.slider(
        "Part B Deductible Growth Rate",
        min_value=0.0,
        max_value=0.15,
        value=0.06,
        step=0.01,
        format="%.1%",
        help="Annual growth rate for Part B deductible"
    )
    
    # Simulation settings
    st.sidebar.subheader("⚙️ Simulation Settings")
    
    percent_sick = st.sidebar.slider(
        "Probability of Full Utilization",
        min_value=0.0,
        max_value=1.0,
        value=0.20,
        step=0.05,
        format="%.1%",
        help="Probability of being 'sick' (full utilization) in any given year"
    )
    
    simulation_years = st.sidebar.slider(
        "Simulation Years",
        min_value=5,
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
    
    # Number of simulations
    num_simulations = st.sidebar.selectbox(
        "Number of Simulations",
        options=[100, 500, 1000, 2000, 5000],
        index=2,
        help="Number of Monte Carlo simulations to run"
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
    ), num_simulations


def display_cost_breakdown(params: SimulationParameters) -> None:
    """Display detailed cost breakdown table."""
    st.subheader("📋 Year-by-Year Cost Breakdown")
    
    # Create cost breakdown data
    years = list(range(params.start_year, params.start_year + params.simulation_years))
    data = []
    
    for year_num, year in enumerate(years):
        # Calculate individual components
        medigap_monthly = params.medigap_premium_2026 * (1 + params.medigap_premium_growth_rate) ** year_num
        medigap_annual = medigap_monthly * 12
        
        plan_deductible = params.plan_deductible_2026 * (1 + params.plan_deductible_growth_rate) ** year_num
        
        part_d_monthly = params.part_d_premium_2026 * (1 + params.part_d_premium_growth_rate) ** year_num
        part_d_annual = part_d_monthly * 12
        
        part_b_deductible = params.part_b_deductible_2026 * (1 + params.part_b_deductible_growth_rate) ** year_num
        
        # Total annual cost (premiums + deductibles)
        total_annual = medigap_annual + part_d_annual + plan_deductible + part_b_deductible
        
        data.append({
            'Year': year,
            'Medigap Monthly': f"${medigap_monthly:,.2f}",
            'Medigap Annual': f"${medigap_annual:,.2f}",
            'Plan Deductible': f"${plan_deductible:,.2f}",
            'Part D Monthly': f"${part_d_monthly:,.2f}",
            'Part D Annual': f"${part_d_annual:,.2f}",
            'Part B Deductible': f"${part_b_deductible:,.2f}",
            'Total Annual': f"${total_annual:,.2f}"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def create_cost_projection_chart(years: list, mean_costs: list, std_costs: list) -> go.Figure:
    """Create cost projection chart with confidence intervals."""
    fig = go.Figure()
    
    # Add mean line
    fig.add_trace(go.Scatter(
        x=years,
        y=mean_costs,
        mode='lines+markers',
        name='Mean Cost',
        line=dict(color='blue', width=3),
        marker=dict(size=6)
    ))
    
    # Add confidence interval (mean ± std)
    upper_bound = [mean + std for mean, std in zip(mean_costs, std_costs)]
    lower_bound = [mean - std for mean, std in zip(mean_costs, std_costs)]
    
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='tonexty',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='±1 Standard Deviation',
        hoverinfo="skip"
    ))
    
    fig.update_layout(
        title='Medicare/Medigap Cost Projections Over Time',
        xaxis_title='Year',
        yaxis_title='Annual Cost ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_lifetime_cost_histogram(lifetime_costs: list) -> go.Figure:
    """Create lifetime cost distribution histogram."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=lifetime_costs,
        nbinsx=50,
        name='Lifetime Cost Distribution',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    # Add mean line
    mean_cost = np.mean(lifetime_costs)
    fig.add_vline(
        x=mean_cost,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${mean_cost:,.0f}",
        annotation_position="top"
    )
    
    fig.update_layout(
        title='Distribution of Total Lifetime Costs',
        xaxis_title='Total Lifetime Cost ($)',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    
    return fig


def display_simulation_results(results: Dict[str, Any]) -> None:
    """Display comprehensive simulation results."""
    st.subheader("📊 Simulation Results")
    
    # Calculate key statistics
    lifetime_costs = results['lifetime_costs']
    mean_lifetime = np.mean(lifetime_costs)
    min_lifetime = np.min(lifetime_costs)
    max_lifetime = np.max(lifetime_costs)
    median_lifetime = np.median(lifetime_costs)
    std_lifetime = np.std(lifetime_costs)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Mean Lifetime Cost",
            value=f"${mean_lifetime:,.0f}",
            delta=f"±${std_lifetime:,.0f}"
        )
    
    with col2:
        st.metric(
            label="Median Lifetime Cost",
            value=f"${median_lifetime:,.0f}"
        )
    
    with col3:
        st.metric(
            label="Minimum Lifetime Cost",
            value=f"${min_lifetime:,.0f}"
        )
    
    with col4:
        st.metric(
            label="Maximum Lifetime Cost",
            value=f"${max_lifetime:,.0f}"
        )
    
    # Create charts
    years = list(range(results['parameters']['start_year'], 
                      results['parameters']['start_year'] + results['parameters']['simulation_years']))
    
    # Cost projection chart
    st.subheader("📈 Cost Projections Over Time")
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
        page_title="Medicare/Medigap Cost Simulator",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🏥 Medicare/Medigap Cost Simulator")
    st.markdown("""
    This application uses Monte Carlo simulation to project Medicare and Medigap costs over time.
    Adjust the parameters in the sidebar to explore different scenarios and see how they affect
    your long-term healthcare costs.
    """)
    
    # Create parameter inputs
    params, num_simulations = create_parameter_inputs()
    
    # Run simulation button
    if st.sidebar.button("🚀 Run Simulation", type="primary"):
        with st.spinner(f"Running {num_simulations:,} Monte Carlo simulations..."):
            # Create simulation engine
            simulation = MonteCarloSimulation(params)
            
            # Run comprehensive simulation
            results = simulation.run_comprehensive_simulation(num_simulations)
            
            # Store results in session state
            st.session_state.simulation_results = results
    
    # Display results if available
    if 'simulation_results' in st.session_state:
        results = st.session_state.simulation_results
        
        # Display cost breakdown
        display_cost_breakdown(params)
        
        st.divider()
        
        # Display simulation results
        display_simulation_results(results)
        
        # Download results
        st.subheader("💾 Download Results")
        
        # Create downloadable data
        years = list(range(params.start_year, params.start_year + params.simulation_years))
        results_data = {
            'Year': years,
            'Mean_Cost': results['statistics']['mean_costs'],
            'Std_Cost': results['statistics']['std_costs'],
            'Min_Cost': results['statistics']['min_costs'],
            'Max_Cost': results['statistics']['max_costs']
        }
        
        results_df = pd.DataFrame(results_data)
        csv = results_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Cost Projections (CSV)",
            data=csv,
            file_name=f"medicare_cost_projections_{params.start_year}_{params.start_year + params.simulation_years - 1}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.divider()
    st.markdown("""
    **About this simulation:**
    - Uses Monte Carlo methods to account for uncertainty in healthcare utilization
    - Projects costs based on current Medicare/Medigap pricing and growth rates
    - Results are for informational purposes only and should not be considered financial advice
    """)


if __name__ == "__main__":
    main()
