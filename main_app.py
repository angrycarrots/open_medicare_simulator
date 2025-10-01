"""Main Streamlit application hub for the Open Medicare Simulator."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, Any


def create_navigation_sidebar():
    """Create navigation sidebar with links to different apps."""
    st.sidebar.title("🏥 Open Medicare Simulator")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("📱 Applications")
    
    # Navigation buttons
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.rerun()
    
    if st.sidebar.button("📊 Single Plan Simulator", use_container_width=True):
        st.switch_page("pages/1_Single_Plan_Simulator.py")
    
    if st.sidebar.button("⚖️ Plan Comparison Tool", use_container_width=True):
        st.switch_page("pages/2_Plan_Comparison.py")
    
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("ℹ️ About")
    st.sidebar.markdown("""
    This simulator uses Monte Carlo methods to project Medicare costs over time, 
    helping users understand the financial implications of different plan choices.
    """)


def display_welcome_section():
    """Display the main welcome section."""
    st.title("🏥 Open Medicare Simulator")
    st.markdown("### A Monte Carlo Simulation Platform for Medicare Plan Analysis")
    
    st.markdown("""
    Welcome to the Open Medicare Simulator! This platform helps you understand the long-term 
    financial implications of different Medicare plans using advanced Monte Carlo simulation techniques.
    """)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Single Plan Analysis**
        - Analyze individual Medicare plans
        - Customize plan parameters
        - View detailed cost projections
        """)
    
    with col2:
        st.markdown("""
        **⚖️ Plan Comparison**
        - Compare multiple plans side-by-side
        - Statistical analysis of differences
        - Risk assessment tools
        """)
    
    with col3:
        st.markdown("""
        **🎲 Monte Carlo Simulation**
        - Thousands of scenario simulations
        - Probability-based projections
        - Risk and uncertainty analysis
        """)


def explain_monte_carlo_algorithm():
    """Explain the Monte Carlo algorithm used in the simulator."""
    st.header("🎲 Understanding Monte Carlo Simulation")
    
    st.markdown("""
    The Monte Carlo method is a computational algorithm that uses random sampling to solve 
    mathematical problems. In our Medicare simulator, it helps predict future healthcare costs 
    by running thousands of simulations with different random outcomes.
    """)
    
    # Algorithm explanation with visual
    st.subheader("How It Works")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **1. Define Parameters:**
        - Plan premiums and deductibles
        - Growth rates for costs
        - Probability of being "sick" (high utilization)
        - Simulation timeframe (e.g., 25 years)
        
        **2. Run Simulations:**
        - For each year, randomly determine if you're "healthy" or "sick"
        - Calculate total costs based on your health status
        - Account for annual cost growth
        - Sum costs over the entire simulation period
        
        **3. Analyze Results:**
        - Run thousands of these simulations
        - Calculate statistics (mean, standard deviation, percentiles)
        - Create probability distributions
        - Identify risk scenarios
        """)
    
    with col2:
        # Create a simple visualization of the Monte Carlo process
        fig = go.Figure()
        
        # Simulate some data for visualization
        np.random.seed(42)
        years = list(range(2026, 2031))
        healthy_costs = [5000 + i*200 + np.random.normal(0, 500) for i in range(5)]
        sick_costs = [15000 + i*800 + np.random.normal(0, 2000) for i in range(5)]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=healthy_costs,
            mode='lines+markers',
            name='Healthy Scenario',
            line=dict(color='green', width=2),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=sick_costs,
            mode='lines+markers',
            name='Sick Scenario',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Example: 5-Year Cost Projection',
            xaxis_title='Year',
            yaxis_title='Annual Cost ($)',
            template='plotly_white',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Benefits section
    st.subheader("Why Monte Carlo Simulation?")
    
    benefits_col1, benefits_col2 = st.columns(2)
    
    with benefits_col1:
        st.markdown("""
        **🎯 Advantages:**
        - **Handles Uncertainty:** Accounts for unpredictable health events
        - **Risk Assessment:** Shows probability of different cost outcomes
        - **Comprehensive:** Considers thousands of possible scenarios
        - **Realistic:** Models real-world variability in healthcare costs
        """)
    
    with benefits_col2:
        st.markdown("""
        **📈 Key Insights:**
        - **Mean Cost:** Average expected lifetime cost
        - **Standard Deviation:** Measure of cost variability/risk
        - **Percentiles:** Cost ranges for different probability levels
        - **Risk Scenarios:** Best-case and worst-case outcomes
        """)


def create_algorithm_visualization():
    """Create an interactive visualization of the Monte Carlo algorithm."""
    st.subheader("🔬 Algorithm Visualization")
    
    # Parameters for the demo
    st.markdown("**Adjust parameters to see how they affect the simulation:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        percent_sick = st.slider(
            "Probability of Being Sick",
            min_value=0.1,
            max_value=0.5,
            value=0.2,
            step=0.05,
            help="Probability of high healthcare utilization in any given year"
        )
    
    with col2:
        num_simulations = st.slider(
            "Number of Simulations",
            min_value=100,
            max_value=2000,
            value=1000,
            step=100,
            help="More simulations = more accurate results"
        )
    
    with col3:
        simulation_years = st.slider(
            "Simulation Years",
            min_value=10,
            max_value=30,
            value=20,
            step=5,
            help="Number of years to project forward"
        )
    
    # Run a simplified simulation for demonstration
    if st.button("🎲 Run Demo Simulation", type="primary"):
        with st.spinner("Running Monte Carlo simulation..."):
            # Simplified simulation parameters
            base_premium = 200  # Monthly
            base_deductible = 2000  # Annual
            premium_growth = 0.07
            deductible_growth = 0.06
            
            # Run simulation
            np.random.seed(42)  # For reproducible results
            lifetime_costs = []
            
            for _ in range(num_simulations):
                total_cost = 0
                
                for year in range(simulation_years):
                    # Calculate costs for this year
                    premium = base_premium * (1 + premium_growth) ** year
                    deductible = base_deductible * (1 + deductible_growth) ** year
                    
                    # Determine if sick this year
                    is_sick = np.random.random() < percent_sick
                    
                    # Calculate annual cost
                    annual_premium = premium * 12
                    annual_deductible = deductible if is_sick else 0
                    annual_cost = annual_premium + annual_deductible
                    
                    total_cost += annual_cost
                
                lifetime_costs.append(total_cost)
            
            # Display results
            st.success(f"Simulation complete! Ran {num_simulations} scenarios over {simulation_years} years.")
            
            # Statistics
            mean_cost = np.mean(lifetime_costs)
            std_cost = np.std(lifetime_costs)
            min_cost = np.min(lifetime_costs)
            max_cost = np.max(lifetime_costs)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Mean Cost", f"${mean_cost:,.0f}")
            with col2:
                st.metric("Std Deviation", f"${std_cost:,.0f}")
            with col3:
                st.metric("Minimum Cost", f"${min_cost:,.0f}")
            with col4:
                st.metric("Maximum Cost", f"${max_cost:,.0f}")
            
            # Histogram
            fig = go.Figure(data=[
                go.Histogram(
                    x=lifetime_costs,
                    nbinsx=50,
                    marker_color='lightblue',
                    marker_line=dict(color='black', width=1)
                )
            ])
            
            fig.update_layout(
                title=f'Lifetime Cost Distribution ({num_simulations} simulations)',
                xaxis_title='Lifetime Cost ($)',
                yaxis_title='Frequency',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Percentile table
            percentiles = [5, 10, 25, 50, 75, 90, 95]
            percentile_values = [np.percentile(lifetime_costs, p) for p in percentiles]
            
            percentile_data = {
                'Percentile': [f"{p}%" for p in percentiles],
                'Lifetime Cost': [f"${v:,.0f}" for v in percentile_values]
            }
            
            percentile_df = pd.DataFrame(percentile_data)
            st.dataframe(percentile_df, use_container_width=True)


def display_application_links():
    """Display prominent links to the main applications."""
    st.header("🚀 Get Started")
    st.markdown("Choose an application to begin your Medicare plan analysis:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Single Plan Simulator
        
        Analyze individual Medicare plans with detailed cost projections and risk analysis.
        
        **Features:**
        - Plan-G and Plan-HDG analysis
        - Custom plan creation
        - Detailed cost breakdowns
        - Monte Carlo risk assessment
        """)
        
        if st.button("Launch Single Plan Simulator", type="primary", use_container_width=True):
            st.switch_page("pages/1_Single_Plan_Simulator.py")
    
    with col2:
        st.markdown("""
        ### ⚖️ Plan Comparison Tool
        
        Compare multiple Medicare plans side-by-side with statistical analysis.
        
        **Features:**
        - Head-to-head plan comparisons
        - Statistical significance testing
        - Risk-adjusted comparisons
        - Cost difference analysis
        """)
        
        if st.button("Launch Plan Comparison Tool", type="primary", use_container_width=True):
            st.switch_page("pages/2_Plan_Comparison.py")


def display_technical_details():
    """Display technical details about the implementation."""
    with st.expander("🔧 Technical Implementation Details"):
        st.markdown("""
        **Model Components:**
        
        - **Plan Models:** `PlanG`, `PlanHDG`, and custom `Plan` classes
        - **Simulation Engine:** `PlanMonteCarloSimulation` class
        - **Cost Calculations:** Annual cost projections with growth rates
        - **Statistical Analysis:** Mean, standard deviation, percentiles
        
        **Key Parameters:**
        
        - **Premium Growth Rate:** Annual increase in plan premiums
        - **Deductible Growth Rate:** Annual increase in plan deductibles
        - **Part B/D Growth Rates:** Medicare component cost increases
        - **Percent Sick:** Probability of high healthcare utilization
        
        **Simulation Process:**
        
        1. Initialize plan parameters and growth rates
        2. For each simulation iteration:
           - Generate random health status for each year
           - Calculate annual costs (premiums + deductibles if sick)
           - Apply growth rates to project future costs
           - Sum total lifetime costs
        3. Analyze results across all simulations
        4. Generate statistics and visualizations
        
        **Statistical Outputs:**
        
        - Mean lifetime cost and standard deviation
        - Cost percentiles (5th, 25th, 50th, 75th, 95th)
        - Probability distributions
        - Risk scenarios and confidence intervals
        """)


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Open Medicare Simulator - Home",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # Create navigation sidebar
    create_navigation_sidebar()
    
    # Main content
    display_welcome_section()
    
    st.markdown("---")
    
    display_application_links()
    
    st.markdown("---")
    
    explain_monte_carlo_algorithm()
    
    st.markdown("---")
    
    create_algorithm_visualization()
    
    st.markdown("---")
    
    display_technical_details()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Disclaimer:** This simulation is for educational and informational purposes only. 
    Actual Medicare costs may vary significantly based on location, health status, 
    provider networks, and other factors. Always consult with qualified professionals 
    when making healthcare decisions.
    """)


if __name__ == "__main__":
    main()