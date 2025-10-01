"""Streamlit application for comparing Medicare plans side by side."""

import sys
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from medigap.models.plans import PlanG, PlanHDG, PlanN
from medigap.simulation.plan_monte_carlo import PlanMonteCarloSimulation


def create_plan_comparison_interface():
    """Create interface for comparing two plans."""
    # Navigation
    st.sidebar.title("🏥 Open Medicare Simulator")
    if st.sidebar.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("main_app.py")
    st.sidebar.markdown("---")
    
    st.sidebar.header("🏥 Plan Comparison")
    
    # Plan selection
    st.sidebar.subheader("📋 Select Plans to Compare")
    
    plan1_type = st.sidebar.selectbox(
        "Plan 1",
        ["Plan-G (Original Medigap Plan N)", "Plan-HDG (High Deductible Plan G)", "Plan-N (New Plan with Specialist Visits)"],
        help="First plan to compare"
    )
    
    plan2_type = st.sidebar.selectbox(
        "Plan 2", 
        ["Plan-HDG (High Deductible Plan G)", "Plan-G (Original Medigap Plan N)", "Plan-N (New Plan with Specialist Visits)"],
        help="Second plan to compare"
    )
    
    # Simulation settings
    st.sidebar.subheader("⚙️ Simulation Settings")
    
    percent_sick = st.sidebar.slider(
        "Percent Sick",
        min_value=0.0,
        max_value=1.0,
        value=0.20,
        step=0.05,
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
    
    # Create plans
    if plan1_type == "Plan-G (Original Medigap Plan N)":
        plan1 = PlanG(percent_sick=percent_sick, simulation_years=simulation_years, start_year=start_year)
    elif plan1_type == "Plan-HDG (High Deductible Plan G)":
        plan1 = PlanHDG(percent_sick=percent_sick, simulation_years=simulation_years, start_year=start_year)
    else:  # Plan-N
        plan1 = PlanN(percent_sick=percent_sick, simulation_years=simulation_years, start_year=start_year)
    
    if plan2_type == "Plan-G (Original Medigap Plan N)":
        plan2 = PlanG(percent_sick=percent_sick, simulation_years=simulation_years, start_year=start_year)
    elif plan2_type == "Plan-HDG (High Deductible Plan G)":
        plan2 = PlanHDG(percent_sick=percent_sick, simulation_years=simulation_years, start_year=start_year)
    else:  # Plan-N
        plan2 = PlanN(percent_sick=percent_sick, simulation_years=simulation_years, start_year=start_year)
    
    return plan1, plan2, num_simulations


def display_plan_comparison_table(plan1, plan2):
    """Display side-by-side comparison of plan parameters."""
    st.subheader("📊 Plan Comparison")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"**{plan1.name}**")
        st.write(f"Premium: ${plan1.premium_2026:.2f}/month")
        st.write(f"Premium Growth: {plan1.premium_growth_rate:.1%}")
        st.write(f"Deductible: ${plan1.plan_deductible_2026:.2f}/year")
        st.write(f"Deductible Growth: {plan1.plan_deductible_growth_rate:.1%}")
        st.write(f"Part D: ${plan1.part_d_premium_2026:.2f}/month")
        st.write(f"Part B: ${plan1.part_b_deductible_2026:.2f}/year")
        if plan1.specialist_visits_per_year is not None:
            st.write(f"Specialist Visits: {plan1.specialist_visits_per_year}/year")
            st.write(f"Specialist Copay: ${plan1.specialist_copay_2026:.2f}/visit")
    
    with col2:
        st.markdown(f"**{plan2.name}**")
        st.write(f"Premium: ${plan2.premium_2026:.2f}/month")
        st.write(f"Premium Growth: {plan2.premium_growth_rate:.1%}")
        st.write(f"Deductible: ${plan2.plan_deductible_2026:.2f}/year")
        st.write(f"Deductible Growth: {plan2.plan_deductible_growth_rate:.1%}")
        st.write(f"Part D: ${plan2.part_d_premium_2026:.2f}/month")
        st.write(f"Part B: ${plan2.part_b_deductible_2026:.2f}/year")
        if plan2.specialist_visits_per_year is not None:
            st.write(f"Specialist Visits: {plan2.specialist_visits_per_year}/year")
            st.write(f"Specialist Copay: ${plan2.specialist_copay_2026:.2f}/visit")
    
    with col3:
        st.markdown("**Difference**")
        premium_diff = plan2.premium_2026 - plan1.premium_2026
        deductible_diff = plan2.plan_deductible_2026 - plan1.plan_deductible_2026
        
        st.write(f"Premium: ${premium_diff:+.2f}/month")
        st.write(f"Deductible: ${deductible_diff:+.2f}/year")
        
        if premium_diff < 0:
            st.success(f"Plan 2 saves ${abs(premium_diff):.2f}/month on premiums")
        else:
            st.warning(f"Plan 2 costs ${premium_diff:.2f}/month more in premiums")
        
        if deductible_diff < 0:
            st.success(f"Plan 2 saves ${abs(deductible_diff):.2f}/year on deductibles")
        else:
            st.warning(f"Plan 2 costs ${deductible_diff:.2f}/year more in deductibles")


def create_comparison_chart(plan1, plan2, years_to_show=10):
    """Create a chart comparing costs over time."""
    st.subheader("📈 Cost Comparison Over Time")
    
    years = list(range(plan1.start_year, plan1.start_year + min(years_to_show, plan1.simulation_years)))
    
    # Calculate costs for each year
    plan1_healthy_costs = []
    plan1_sick_costs = []
    plan2_healthy_costs = []
    plan2_sick_costs = []
    
    for year_offset in range(len(years)):
        plan1_healthy = plan1.calculate_annual_costs(year_offset, False)
        plan1_sick = plan1.calculate_annual_costs(year_offset, True)
        plan2_healthy = plan2.calculate_annual_costs(year_offset, False)
        plan2_sick = plan2.calculate_annual_costs(year_offset, True)
        
        plan1_healthy_costs.append(plan1_healthy)
        plan1_sick_costs.append(plan1_sick)
        plan2_healthy_costs.append(plan2_healthy)
        plan2_sick_costs.append(plan2_sick)
    
    # Create the chart
    fig = go.Figure()
    
    # Plan 1 lines
    fig.add_trace(go.Scatter(
        x=years,
        y=plan1_healthy_costs,
        mode='lines+markers',
        name=f'{plan1.name} (Healthy)',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=plan1_sick_costs,
        mode='lines+markers',
        name=f'{plan1.name} (Sick)',
        line=dict(color='blue', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    # Plan 2 lines
    fig.add_trace(go.Scatter(
        x=years,
        y=plan2_healthy_costs,
        mode='lines+markers',
        name=f'{plan2.name} (Healthy)',
        line=dict(color='red', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=plan2_sick_costs,
        mode='lines+markers',
        name=f'{plan2.name} (Sick)',
        line=dict(color='red', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Annual Cost Comparison',
        xaxis_title='Year',
        yaxis_title='Annual Cost ($)',
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def run_comparison_simulation(plan1, plan2, num_simulations):
    """Run Monte Carlo simulations for both plans and compare results."""
    st.subheader("🎲 Monte Carlo Simulation Comparison")
    
    # Create simulations
    sim1 = PlanMonteCarloSimulation(plan1)
    sim2 = PlanMonteCarloSimulation(plan2)
    
    # Run simulations
    with st.spinner(f"Running {num_simulations} simulations for both plans..."):
        results1 = sim1.run_comprehensive_simulation(num_simulations)
        results2 = sim2.run_comprehensive_simulation(num_simulations)
    
    # Extract lifetime costs
    lifetime_costs1 = results1['lifetime_costs']
    lifetime_costs2 = results2['lifetime_costs']
    
    # Calculate comparison statistics
    mean1 = np.mean(lifetime_costs1)
    mean2 = np.mean(lifetime_costs2)
    std1 = np.std(lifetime_costs1)
    std2 = np.std(lifetime_costs2)
    
    difference = mean2 - mean1
    difference_std = np.std(np.array(lifetime_costs2) - np.array(lifetime_costs1))
    
    # Display comparison metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            f"{plan1.name} Mean",
            f"${mean1:,.0f}",
            delta=f"±${std1:,.0f}"
        )
    
    with col2:
        st.metric(
            f"{plan2.name} Mean",
            f"${mean2:,.0f}",
            delta=f"±${std2:,.0f}"
        )
    
    with col3:
        st.metric(
            "Difference",
            f"${difference:,.0f}",
            delta=f"±${difference_std:,.0f}"
        )
    
    with col4:
        if difference < 0:
            st.metric(
                "Savings",
                f"${abs(difference):,.0f}",
                delta="Plan 2 cheaper"
            )
        else:
            st.metric(
                "Extra Cost",
                f"${difference:,.0f}",
                delta="Plan 1 cheaper"
            )
    
    # Create comparison histogram
    st.subheader("📊 Lifetime Cost Distribution Comparison")
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=lifetime_costs1,
        name=plan1.name,
        opacity=0.7,
        nbinsx=50,
        marker_color='blue'
    ))
    
    fig.add_trace(go.Histogram(
        x=lifetime_costs2,
        name=plan2.name,
        opacity=0.7,
        nbinsx=50,
        marker_color='red'
    ))
    
    fig.update_layout(
        title='Lifetime Cost Distribution Comparison',
        xaxis_title='Lifetime Cost ($)',
        yaxis_title='Frequency',
        barmode='overlay',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Percentile comparison
    st.subheader("📊 Percentile Comparison")
    
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    
    comparison_data = {
        'Percentile': [f"{p}%" for p in percentiles],
        f'{plan1.name}': [f"${np.percentile(lifetime_costs1, p):,.0f}" for p in percentiles],
        f'{plan2.name}': [f"${np.percentile(lifetime_costs2, p):,.0f}" for p in percentiles],
        'Difference': [f"${np.percentile(lifetime_costs2, p) - np.percentile(lifetime_costs1, p):+,.0f}" for p in percentiles]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)


def main():
    """Main Streamlit application for plan comparison."""
    st.set_page_config(
        page_title="Medicare Plan Comparison",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("⚖️ Medicare Plan Comparison Tool")
    st.markdown("Compare different Medicare plans side by side using Monte Carlo simulation.")
    
    # Create comparison interface
    plan1, plan2, num_simulations = create_plan_comparison_interface()
    
    # Display plan comparison
    display_plan_comparison_table(plan1, plan2)
    
    # Create cost comparison chart
    create_comparison_chart(plan1, plan2)
    
    # Run comparison simulation button
    if st.button("🚀 Run Comparison Simulation", type="primary"):
        run_comparison_simulation(plan1, plan2, num_simulations)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Note:** This simulation is for educational purposes only. "
        "Actual Medicare costs may vary based on location, health status, and other factors."
    )


if __name__ == "__main__":
    main()


