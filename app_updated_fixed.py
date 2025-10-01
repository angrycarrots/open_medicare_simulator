"""Streamlit application for Medicare/Medigap Monte Carlo simulation with plan selection."""

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

from medigap.models.plans import PlanG, PlanHDG
from medigap.simulation.plan_monte_carlo import PlanMonteCarloSimulation


def create_plan_selection() -> tuple:
    """Create plan selection interface and return selected plan and custom parameters."""
    st.sidebar.header("🏥 Medicare Plan Selection")
    
    # Plan selection
    plan_type = st.sidebar.selectbox(
        "Select Medicare Plan",
        ["Plan-G (Original Medigap Plan N)", "Plan-HDG (High Deductible Plan G)", "Custom Plan"],
        help="Choose between predefined plans or create a custom plan"
    )
    
    # Simulation settings
    st.sidebar.subheader("⚙️ Simulation Settings")
    
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
    
    # Create plan based on selection
    if plan_type == "Plan-G (Original Medigap Plan N)":
        plan = PlanG(
            percent_sick=percent_sick,
            simulation_years=simulation_years,
            start_year=start_year
        )
        show_plan_details = True
        
    elif plan_type == "Plan-HDG (High Deductible Plan G)":
        plan = PlanHDG(
            percent_sick=percent_sick,
            simulation_years=simulation_years,
            start_year=start_year
        )
        show_plan_details = True
        
    else:  # Custom Plan
        st.sidebar.subheader("💰 Custom Plan Parameters")
        
        premium_2026 = st.sidebar.number_input(
            "Premium (monthly)",
            min_value=10.0,
            max_value=1000.0,
            value=100.0,
            step=10.0,
            help="Base premium for 2026"
        )
        
        premium_growth_rate = st.sidebar.slider(
            "Premium Growth Rate",
            min_value=0.0,
            max_value=0.20,
            value=0.07,
            step=0.01,
            # format="%.1%",
            help="Annual growth rate for premium"
        )
        
        plan_deductible_2026 = st.sidebar.number_input(
            "Plan Deductible (annual)",
            min_value=100.0,
            max_value=10000.0,
            value=1000.0,
            step=100.0,
            help="Base plan deductible for 2026"
        )
        
        plan_deductible_growth_rate = st.sidebar.slider(
            "Deductible Growth Rate",
            min_value=0.0,
            max_value=0.20,
            value=0.06,
            step=0.01,
            # format="%.1%",
            help="Annual growth rate for plan deductible"
        )
        
        # Part D and Part B parameters
        st.sidebar.subheader("📋 Part D & Part B Parameters")
        
        part_d_premium_2026 = st.sidebar.number_input(
            "Part D Premium (monthly)",
            min_value=10.0,
            max_value=200.0,
            value=49.0,
            step=5.0,
            help="Base Part D premium for 2026"
        )
        
        part_d_premium_growth_rate = st.sidebar.slider(
            "Part D Growth Rate",
            min_value=0.0,
            max_value=0.20,
            value=0.06,
            step=0.01,
            # format="%.1%",
            help="Annual growth rate for Part D premium"
        )
        
        part_b_deductible_2026 = st.sidebar.number_input(
            "Part B Deductible (annual)",
            min_value=100.0,
            max_value=500.0,
            value=210.0,
            step=10.0,
            help="Base Part B deductible for 2026"
        )
        
        part_b_deductible_growth_rate = st.sidebar.slider(
            "Part B Growth Rate",
            min_value=0.0,
            max_value=0.20,
            value=0.06,
            step=0.01,
            # format="%.1%",
            help="Annual growth rate for Part B deductible"
        )
        
        # Create custom plan
        from medigap.models.plan import Plan
        plan = Plan(
            name="Custom Plan",
            premium_2026=premium_2026,
            premium_growth_rate=premium_growth_rate,
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
        show_plan_details = True
    
    return plan, num_simulations, show_plan_details


def display_plan_summary(plan):
    """Display a summary of the selected plan parameters."""
    st.subheader(f"📋 {plan.name} Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Premium Information:**")
        st.write(f"• Monthly Premium (2026): ${plan.premium_2026:.2f}")
        st.write(f"• Premium Growth Rate: {plan.premium_growth_rate:.1%}")
        st.write(f"• Part D Premium (2026): ${plan.part_d_premium_2026:.2f}")
        st.write(f"• Part D Growth Rate: {plan.part_d_premium_growth_rate:.1%}")
    
    with col2:
        st.markdown("**Deductible Information:**")
        st.write(f"• Plan Deductible (2026): ${plan.plan_deductible_2026:.2f}")
        st.write(f"• Deductible Growth Rate: {plan.plan_deductible_growth_rate:.1%}")
        st.write(f"• Part B Deductible (2026): ${plan.part_b_deductible_2026:.2f}")
        st.write(f"• Part B Growth Rate: {plan.part_b_deductible_growth_rate:.1%}")
    
    st.markdown("**Simulation Settings:**")
    st.write(f"• Percent Sick: {plan.percent_sick:.1%}")
    st.write(f"• Simulation Years: {plan.simulation_years}")
    st.write(f"• Start Year: {plan.start_year}")


def create_cost_projection_chart(years: list, mean_costs: list, std_costs: list, plan_name: str) -> go.Figure:
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
        title=f'{plan_name} - Annual Cost Projections',
        xaxis_title='Year',
        yaxis_title='Annual Cost ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_lifetime_cost_histogram(lifetime_costs: list, plan_name: str) -> go.Figure:
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
        title=f'{plan_name} - Lifetime Cost Distribution',
        xaxis_title='Lifetime Cost ($)',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    
    return fig


def create_cost_comparison_table(plan, years_to_show=5):
    """Create a table showing cost projections for the first few years."""
    st.subheader("📊 Cost Projections by Year")
    
    data = []
    for year in range(min(years_to_show, plan.simulation_years)):
        actual_year = plan.start_year + year
        
        # Calculate costs for this year
        premium = plan.calculate_premium(year)
        plan_deductible = plan.calculate_plan_deductible(year)
        part_d_premium = plan.calculate_part_d_premium(year)
        part_b_deductible = plan.calculate_part_b_deductible(year)
        
        # Calculate total costs
        total_premiums = (premium + part_d_premium) * 12
        total_deductibles = plan_deductible + part_b_deductible
        total_annual_healthy = total_premiums
        total_annual_sick = total_premiums + total_deductibles
        
        data.append({
            'Year': actual_year,
            'Premium (Monthly)': f"${premium:.2f}",
            'Plan Deductible': f"${plan_deductible:.2f}",
            'Part D Premium': f"${part_d_premium:.2f}",
            'Part B Deductible': f"${part_b_deductible:.2f}",
            'Healthy (Annual)': f"${total_annual_healthy:,.2f}",
            'Sick (Annual)': f"${total_annual_sick:,.2f}"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def run_simulation_and_display_results(plan, num_simulations):
    """Run Monte Carlo simulation and display results."""
    st.subheader("🎲 Monte Carlo Simulation Results")
    
    # Create simulation
    simulation = PlanMonteCarloSimulation(plan)
    
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
    years = list(range(plan.start_year, plan.start_year + plan.simulation_years))
    
    # Cost projection chart
    st.subheader("📈 Annual Cost Projections")
    cost_chart = create_cost_projection_chart(
        years, 
        statistics['mean_costs'], 
        statistics['std_costs'],
        plan.name
    )
    st.plotly_chart(cost_chart, use_container_width=True)
    
    # Lifetime cost histogram
    st.subheader("📊 Lifetime Cost Distribution")
    hist_chart = create_lifetime_cost_histogram(lifetime_costs, plan.name)
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
    st.markdown("Compare different Medicare plans and project costs over time using Monte Carlo simulation.")
    
    # Create plan selection interface
    plan, num_simulations, show_plan_details = create_plan_selection()
    
    if show_plan_details:
        # Display plan summary
        display_plan_summary(plan)
        
        # Create cost comparison table
        create_cost_comparison_table(plan)
        
        # Run simulation button
        if st.button("🚀 Run Monte Carlo Simulation", type="primary"):
            run_simulation_and_display_results(plan, num_simulations)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Note:** This simulation is for educational purposes only. "
        "Actual Medicare costs may vary based on location, health status, and other factors."
    )


if __name__ == "__main__":
    main()

