"""Tkinter GUI application for Medicare/Medigap Monte Carlo simulation."""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from medigap.models.plans import PlanG, PlanHDG, PlanN, Plan
from medigap.simulation.plan_monte_carlo import PlanMonteCarloSimulation
from medigap.visualization.charts import Visualization


class MedicareSimulatorGUI:
    """Main GUI application for Medicare/Medigap simulation."""
    
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the GUI application.
        
        Args:
            root: The main tkinter root window
        """
        self.root = root
        self.root.title("Open Medicare Simulator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize variables
        self.current_plan: Optional[Plan] = None
        self.simulation_results: Optional[Dict[str, Any]] = None
        self.visualization = Visualization()
        
        # Create the GUI
        self.create_widgets()
        self.create_status_bar()
        
    def create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_plan_selection_tab()
        self.create_simulation_tab()
        self.create_results_tab()
        self.create_comparison_tab()
    
    def create_status_bar(self) -> None:
        """Create the status bar at the bottom of the window."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar (initially hidden)
        self.status_progress = ttk.Progressbar(self.status_frame, mode='indeterminate', length=200)
        self.status_progress.pack(side=tk.RIGHT, padx=(5, 0))
        self.status_progress.pack_forget()  # Hide initially
    
    def update_status(self, message: str, show_progress: bool = False) -> None:
        """Update the status bar message.
        
        Args:
            message: Status message to display
            show_progress: Whether to show the progress bar
        """
        self.status_var.set(message)
        if show_progress:
            self.status_progress.pack(side=tk.RIGHT, padx=(5, 0))
            self.status_progress.start()
        else:
            self.status_progress.stop()
            self.status_progress.pack_forget()
        self.root.update_idletasks()
        
    def create_plan_selection_tab(self) -> None:
        """Create the plan selection tab."""
        self.plan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plan_frame, text="Plan Selection")
        
        # Title
        title_label = ttk.Label(self.plan_frame, text="Medicare Plan Selection", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Plan selection frame
        selection_frame = ttk.LabelFrame(self.plan_frame, text="Select Plan Type", padding=10)
        selection_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Plan type selection
        self.plan_type_var = tk.StringVar(value="Plan-G")
        plan_types = ["Plan-G (Original Medigap Plan N)", "Plan-HDG (High Deductible Plan G)", 
                     "Plan-N (New Plan with Specialist Visits)", "Custom Plan"]
        
        for plan_type in plan_types:
            ttk.Radiobutton(selection_frame, text=plan_type, variable=self.plan_type_var,
                           value=plan_type, command=self.on_plan_type_change).pack(anchor=tk.W, pady=2)
        
        # Custom plan parameters frame
        self.custom_frame = ttk.LabelFrame(self.plan_frame, text="Custom Plan Parameters", padding=10)
        self.custom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create custom plan input fields
        self.create_custom_plan_inputs()
        
        # Plan summary frame
        self.summary_frame = ttk.LabelFrame(self.plan_frame, text="Plan Summary", padding=10)
        self.summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.summary_text = tk.Text(self.summary_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load button
        load_button = ttk.Button(self.plan_frame, text="Load Selected Plan", 
                                command=self.load_plan)
        load_button.pack(pady=10)
        
        # Initialize with default plan
        self.on_plan_type_change()
        
    def create_custom_plan_inputs(self) -> None:
        """Create input fields for custom plan parameters."""
        # Clear existing widgets
        for widget in self.custom_frame.winfo_children():
            widget.destroy()
        
        # Create input fields
        fields = [
            ("Plan Name:", "name", "Custom Plan"),
            ("Premium 2026 ($/month):", "premium_2026", "155.0"),
            ("Premium Growth Rate (%):", "premium_growth_rate", "7.0"),
            ("Plan Deductible 2026 ($):", "plan_deductible_2026", "257.0"),
            ("Plan Deductible Growth Rate (%):", "plan_deductible_growth_rate", "6.0"),
            ("Part D Premium 2026 ($/month):", "part_d_premium_2026", "49.0"),
            ("Part D Premium Growth Rate (%):", "part_d_premium_growth_rate", "6.0"),
            ("Part B Deductible 2026 ($):", "part_b_deductible_2026", "210.0"),
            ("Part B Deductible Growth Rate (%):", "part_b_deductible_growth_rate", "6.0"),
            ("Specialist Visits/Year:", "specialist_visits_per_year", "0"),
            ("Specialist Copay 2026 ($):", "specialist_copay_2026", "0.0"),
            ("Specialist Copay Growth Rate (%):", "specialist_copay_growth_rate", "7.0")
        ]
        
        self.custom_vars = {}
        for i, (label_text, var_name, default_value) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(self.custom_frame, text=label_text).grid(row=row, column=col, 
                                                              sticky=tk.W, padx=5, pady=2)
            
            var = tk.StringVar(value=default_value)
            self.custom_vars[var_name] = var
            
            entry = ttk.Entry(self.custom_frame, textvariable=var, width=15)
            entry.grid(row=row, column=col+1, sticky=tk.W, padx=5, pady=2)
    
    def on_plan_type_change(self) -> None:
        """Handle plan type selection change."""
        plan_type = self.plan_type_var.get()
        
        if plan_type == "Custom Plan":
            self.custom_frame.pack(fill=tk.X, padx=20, pady=10)
        else:
            self.custom_frame.pack_forget()
        
        self.update_plan_summary()
    
    def update_plan_summary(self) -> None:
        """Update the plan summary display."""
        try:
            plan_type = self.plan_type_var.get()
            
            if plan_type == "Plan-G (Original Medigap Plan N)":
                plan = PlanG()
            elif plan_type == "Plan-HDG (High Deductible Plan G)":
                plan = PlanHDG()
            elif plan_type == "Plan-N (New Plan with Specialist Visits)":
                plan = PlanN()
            else:  # Custom Plan
                plan = self.create_custom_plan()
            
            # Display plan summary
            summary = f"Plan: {plan.name}\n"
            summary += f"Premium (2026): ${plan.premium_2026:.2f}/month\n"
            summary += f"Premium Growth Rate: {plan.premium_growth_rate:.1%}\n"
            summary += f"Plan Deductible (2026): ${plan.plan_deductible_2026:.2f}\n"
            summary += f"Plan Deductible Growth Rate: {plan.plan_deductible_growth_rate:.1%}\n"
            summary += f"Part D Premium (2026): ${plan.part_d_premium_2026:.2f}/month\n"
            summary += f"Part D Premium Growth Rate: {plan.part_d_premium_growth_rate:.1%}\n"
            summary += f"Part B Deductible (2026): ${plan.part_b_deductible_2026:.2f}\n"
            summary += f"Part B Deductible Growth Rate: {plan.part_b_deductible_growth_rate:.1%}\n"
            
            if plan.specialist_visits_per_year is not None:
                summary += f"Specialist Visits/Year: {plan.specialist_visits_per_year}\n"
                summary += f"Specialist Copay (2026): ${plan.specialist_copay_2026:.2f}\n"
                summary += f"Specialist Copay Growth Rate: {plan.specialist_copay_growth_rate:.1%}\n"
            
            summary += f"Simulation Years: {plan.simulation_years}\n"
            summary += f"Start Year: {plan.start_year}\n"
            summary += f"Percent Sick: {plan.percent_sick:.1%}\n"
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary)
            
        except Exception as e:
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, f"Error creating plan: {str(e)}")
    
    def create_custom_plan(self) -> Plan:
        """Create a custom plan from user inputs."""
        try:
            # Get values from custom inputs
            name = self.custom_vars["name"].get()
            premium_2026 = float(self.custom_vars["premium_2026"].get())
            premium_growth_rate = float(self.custom_vars["premium_growth_rate"].get()) / 100
            plan_deductible_2026 = float(self.custom_vars["plan_deductible_2026"].get())
            plan_deductible_growth_rate = float(self.custom_vars["plan_deductible_growth_rate"].get()) / 100
            part_d_premium_2026 = float(self.custom_vars["part_d_premium_2026"].get())
            part_d_premium_growth_rate = float(self.custom_vars["part_d_premium_growth_rate"].get()) / 100
            part_b_deductible_2026 = float(self.custom_vars["part_b_deductible_2026"].get())
            part_b_deductible_growth_rate = float(self.custom_vars["part_b_deductible_growth_rate"].get()) / 100
            
            # Specialist visit parameters
            specialist_visits = int(self.custom_vars["specialist_visits_per_year"].get())
            specialist_copay_2026 = float(self.custom_vars["specialist_copay_2026"].get())
            specialist_copay_growth_rate = float(self.custom_vars["specialist_copay_growth_rate"].get()) / 100
            
            # Create plan with specialist visits if specified
            if specialist_visits > 0:
                return Plan(
                    name=name,
                    premium_2026=premium_2026,
                    premium_growth_rate=premium_growth_rate,
                    plan_deductible_2026=plan_deductible_2026,
                    plan_deductible_growth_rate=plan_deductible_growth_rate,
                    part_d_premium_2026=part_d_premium_2026,
                    part_d_premium_growth_rate=part_d_premium_growth_rate,
                    part_b_deductible_2026=part_b_deductible_2026,
                    part_b_deductible_growth_rate=part_b_deductible_growth_rate,
                    specialist_visits_per_year=specialist_visits,
                    specialist_copay_2026=specialist_copay_2026,
                    specialist_copay_growth_rate=specialist_copay_growth_rate
                )
            else:
                return Plan(
                    name=name,
                    premium_2026=premium_2026,
                    premium_growth_rate=premium_growth_rate,
                    plan_deductible_2026=plan_deductible_2026,
                    plan_deductible_growth_rate=plan_deductible_growth_rate,
                    part_d_premium_2026=part_d_premium_2026,
                    part_d_premium_growth_rate=part_d_premium_growth_rate,
                    part_b_deductible_2026=part_b_deductible_2026,
                    part_b_deductible_growth_rate=part_b_deductible_growth_rate
                )
        except ValueError as e:
            raise ValueError(f"Invalid input values: {str(e)}")
    
    def load_plan(self) -> None:
        """Load the selected plan."""
        try:
            plan_type = self.plan_type_var.get()
            
            if plan_type == "Plan-G (Original Medigap Plan N)":
                self.current_plan = PlanG()
            elif plan_type == "Plan-HDG (High Deductible Plan G)":
                self.current_plan = PlanHDG()
            elif plan_type == "Plan-N (New Plan with Specialist Visits)":
                self.current_plan = PlanN()
            else:  # Custom Plan
                self.current_plan = self.create_custom_plan()
            
            self.update_status(f"Plan '{self.current_plan.name}' loaded successfully!")
            
            # Switch to simulation tab
            self.notebook.select(1)
            
        except Exception as e:
            self.update_status(f"Error: Failed to load plan - {str(e)}")
    
    def create_simulation_tab(self) -> None:
        """Create the simulation tab."""
        self.sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sim_frame, text="Simulation")
        
        # Title
        title_label = ttk.Label(self.sim_frame, text="Monte Carlo Simulation", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Simulation parameters frame
        params_frame = ttk.LabelFrame(self.sim_frame, text="Simulation Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Number of simulations
        ttk.Label(params_frame, text="Number of Simulations:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.num_simulations_var = tk.StringVar(value="1000")
        num_sim_entry = ttk.Entry(params_frame, textvariable=self.num_simulations_var, width=10)
        num_sim_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Percent sick slider
        ttk.Label(params_frame, text="Percent Sick (%):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.percent_sick_var = tk.DoubleVar(value=20.0)
        
        # Create slider frame
        slider_frame = ttk.Frame(params_frame)
        slider_frame.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        percent_sick_slider = tk.Scale(slider_frame, from_=0.0, to=100.0, 
                                      variable=self.percent_sick_var, orient=tk.HORIZONTAL, length=150,
                                      resolution=0.1, digits=3)
        percent_sick_slider.pack(side=tk.LEFT)
        
        # Percent sick value label
        self.percent_sick_label = ttk.Label(slider_frame, text="20.0%")
        self.percent_sick_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Update label when slider changes
        def update_percent_sick_label(*args):
            value = self.percent_sick_var.get()
            self.percent_sick_label.config(text=f"{value:.1f}%")
        
        self.percent_sick_var.trace_add('write', update_percent_sick_label)
        
        # Simulation years
        ttk.Label(params_frame, text="Simulation Years:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.simulation_years_var = tk.StringVar(value="25")
        sim_years_entry = ttk.Entry(params_frame, textvariable=self.simulation_years_var, width=10)
        sim_years_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Start year
        ttk.Label(params_frame, text="Start Year:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.start_year_var = tk.StringVar(value="2026")
        start_year_entry = ttk.Entry(params_frame, textvariable=self.start_year_var, width=10)
        start_year_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Run simulation button
        run_button = ttk.Button(self.sim_frame, text="Run Simulation", 
                               command=self.run_simulation)
        run_button.pack(pady=20)
        
        # Simulation info label
        self.sim_info_var = tk.StringVar(value="Ready to run simulation")
        sim_info_label = ttk.Label(self.sim_frame, textvariable=self.sim_info_var)
        sim_info_label.pack(pady=5)
    
    def run_simulation(self) -> None:
        """Run the Monte Carlo simulation."""
        if self.current_plan is None:
            self.update_status("Error: Please load a plan first!")
            return
        
        try:
            # Get simulation parameters
            num_simulations = int(self.num_simulations_var.get())
            percent_sick = self.percent_sick_var.get() / 100  # Slider already gives percentage
            simulation_years = int(self.simulation_years_var.get())
            start_year = int(self.start_year_var.get())
            
            # Update plan parameters
            self.current_plan.percent_sick = percent_sick
            self.current_plan.simulation_years = simulation_years
            self.current_plan.start_year = start_year
            
            # Start progress indication
            self.update_status("Running simulation...", show_progress=True)
            self.sim_info_var.set(f"Running {num_simulations} simulations...")
            self.root.update()
            
            # Run simulation
            simulation = PlanMonteCarloSimulation(self.current_plan)
            self.simulation_results = simulation.run_comprehensive_simulation(num_simulations)
            
            # Stop progress indication
            self.update_status(f"Simulation completed! Ran {num_simulations} simulations.")
            self.sim_info_var.set(f"Completed {num_simulations} simulations successfully.")
            
            # Switch to results tab and populate results
            self.populate_results()
            self.notebook.select(2)
            
        except Exception as e:
            self.update_status(f"Error: Simulation failed - {str(e)}")
            self.sim_info_var.set("Simulation failed")
    
    def create_results_tab(self) -> None:
        """Create the results tab."""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")
        
        # Title
        title_label = ttk.Label(self.results_frame, text="Simulation Results", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Create notebook for results sub-tabs
        self.results_notebook = ttk.Notebook(self.results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.stats_frame, text="Statistics")
        
        # Charts tab
        self.charts_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.charts_frame, text="Charts")
        
        # Export button
        export_button = ttk.Button(self.results_frame, text="Export Results", 
                                  command=self.export_results)
        export_button.pack(pady=10)
        
        # Initialize results display
        self.populate_results()
    
    def create_comparison_tab(self) -> None:
        """Create the plan comparison tab."""
        self.comp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comp_frame, text="Plan Comparison")
        
        # Title
        title_label = ttk.Label(self.comp_frame, text="Plan Comparison", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Comparison controls
        controls_frame = ttk.LabelFrame(self.comp_frame, text="Comparison Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Plan 1 selection
        ttk.Label(controls_frame, text="Plan 1:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.plan1_var = tk.StringVar(value="Plan-G")
        plan1_combo = ttk.Combobox(controls_frame, textvariable=self.plan1_var, 
                                  values=["Plan-G", "Plan-HDG", "Plan-N"], state="readonly")
        plan1_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Plan 2 selection
        ttk.Label(controls_frame, text="Plan 2:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.plan2_var = tk.StringVar(value="Plan-HDG")
        plan2_combo = ttk.Combobox(controls_frame, textvariable=self.plan2_var, 
                                  values=["Plan-G", "Plan-HDG", "Plan-N"], state="readonly")
        plan2_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Compare button
        compare_button = ttk.Button(controls_frame, text="Compare Plans", 
                                   command=self.compare_plans)
        compare_button.grid(row=1, column=0, columnspan=4, pady=10)
        
        # Comparison results
        self.comp_results_frame = ttk.LabelFrame(self.comp_frame, text="Comparison Results", padding=10)
        self.comp_results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.comp_results_text = tk.Text(self.comp_results_frame, wrap=tk.WORD)
        comp_scrollbar = ttk.Scrollbar(self.comp_results_frame, orient=tk.VERTICAL, 
                                      command=self.comp_results_text.yview)
        self.comp_results_text.configure(yscrollcommand=comp_scrollbar.set)
        
        self.comp_results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        comp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def compare_plans(self) -> None:
        """Compare two plans."""
        try:
            # Create plans
            plan1_name = self.plan1_var.get()
            plan2_name = self.plan2_var.get()
            
            if plan1_name == "Plan-G":
                plan1 = PlanG()
            elif plan1_name == "Plan-HDG":
                plan1 = PlanHDG()
            elif plan1_name == "Plan-N":
                plan1 = PlanN()
            
            if plan2_name == "Plan-G":
                plan2 = PlanG()
            elif plan2_name == "Plan-HDG":
                plan2 = PlanHDG()
            elif plan2_name == "Plan-N":
                plan2 = PlanN()
            
            # Run comparison
            simulation1 = PlanMonteCarloSimulation(plan1)
            comparison = simulation1.compare_plans(plan2, 1000)
            
            # Display results
            results = f"Plan Comparison Results\n"
            results += "=" * 50 + "\n\n"
            
            results += f"Plan 1: {comparison['plan_1']['name']}\n"
            results += f"  Mean Lifetime Cost: ${comparison['plan_1']['mean_lifetime_cost']:,.2f}\n"
            results += f"  Std Dev: ${comparison['plan_1']['std_lifetime_cost']:,.2f}\n"
            results += f"  Min Cost: ${comparison['plan_1']['min_lifetime_cost']:,.2f}\n"
            results += f"  Max Cost: ${comparison['plan_1']['max_lifetime_cost']:,.2f}\n\n"
            
            results += f"Plan 2: {comparison['plan_2']['name']}\n"
            results += f"  Mean Lifetime Cost: ${comparison['plan_2']['mean_lifetime_cost']:,.2f}\n"
            results += f"  Std Dev: ${comparison['plan_2']['std_lifetime_cost']:,.2f}\n"
            results += f"  Min Cost: ${comparison['plan_2']['min_lifetime_cost']:,.2f}\n"
            results += f"  Max Cost: ${comparison['plan_2']['max_lifetime_cost']:,.2f}\n\n"
            
            results += f"Difference (Plan 1 - Plan 2):\n"
            results += f"  Mean Difference: ${comparison['difference']['mean_difference']:,.2f}\n"
            results += f"  Std Dev of Difference: ${comparison['difference']['std_difference']:,.2f}\n"
            
            self.comp_results_text.delete(1.0, tk.END)
            self.comp_results_text.insert(1.0, results)
            self.update_status("Plan comparison completed successfully")
            
        except Exception as e:
            self.update_status(f"Error: Comparison failed - {str(e)}")
    
    def export_results(self) -> None:
        """Export simulation results to file."""
        if self.simulation_results is None:
            self.update_status("Error: No simulation results to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"Medicare Simulation Results\n")
                    f.write(f"Plan: {self.current_plan.name}\n")
                    f.write(f"Number of Simulations: {self.simulation_results['num_simulations']}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Write statistics
                    stats = self.simulation_results['statistics']
                    f.write("Year-by-Year Statistics:\n")
                    f.write("Year\tMean\tStd Dev\tMin\tMax\n")
                    
                    for year in range(len(stats['mean_costs'])):
                        f.write(f"{self.current_plan.start_year + year}\t"
                               f"{stats['mean_costs'][year]:.2f}\t"
                               f"{stats['std_costs'][year]:.2f}\t"
                               f"{stats['min_costs'][year]:.2f}\t"
                               f"{stats['max_costs'][year]:.2f}\n")
                    
                    # Write lifetime cost statistics
                    lifetime_costs = self.simulation_results['lifetime_costs']
                    f.write(f"\nLifetime Cost Statistics:\n")
                    f.write(f"Mean: ${np.mean(lifetime_costs):,.2f}\n")
                    f.write(f"Median: ${np.median(lifetime_costs):,.2f}\n")
                    f.write(f"Std Dev: ${np.std(lifetime_costs):,.2f}\n")
                    f.write(f"Min: ${np.min(lifetime_costs):,.2f}\n")
                    f.write(f"Max: ${np.max(lifetime_costs):,.2f}\n")
                
                self.update_status(f"Results exported successfully to {filename}")
                
            except Exception as e:
                self.update_status(f"Error: Failed to export results - {str(e)}")
    
    def populate_results(self) -> None:
        """Populate the results tabs with simulation data."""
        if self.simulation_results is None:
            # Show placeholder text
            self.populate_statistics_placeholder()
            self.populate_charts_placeholder()
            return
        
        self.populate_statistics()
        self.populate_charts()
    
    def populate_statistics_placeholder(self) -> None:
        """Show placeholder text in statistics tab."""
        # Clear existing widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        placeholder = ttk.Label(self.stats_frame, 
                               text="No simulation results available.\nPlease run a simulation first.",
                               font=("Arial", 12))
        placeholder.pack(expand=True)
    
    def populate_statistics(self) -> None:
        """Populate the statistics tab with simulation results."""
        # Clear existing widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Create statistics display
        stats_text = tk.Text(self.stats_frame, wrap=tk.WORD, font=("Courier", 10))
        stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, command=stats_text.yview)
        stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format statistics
        stats = self.simulation_results['statistics']
        lifetime_costs = self.simulation_results['lifetime_costs']
        
        # Header
        stats_text.insert(tk.END, f"Simulation Results for {self.current_plan.name}\n")
        stats_text.insert(tk.END, f"Number of Simulations: {self.simulation_results['num_simulations']}\n")
        stats_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Lifetime cost statistics
        stats_text.insert(tk.END, "Lifetime Cost Statistics:\n")
        stats_text.insert(tk.END, f"Mean: ${np.mean(lifetime_costs):,.2f}\n")
        stats_text.insert(tk.END, f"Median: ${np.median(lifetime_costs):,.2f}\n")
        stats_text.insert(tk.END, f"Standard Deviation: ${np.std(lifetime_costs):,.2f}\n")
        stats_text.insert(tk.END, f"Minimum: ${np.min(lifetime_costs):,.2f}\n")
        stats_text.insert(tk.END, f"Maximum: ${np.max(lifetime_costs):,.2f}\n\n")
        
        # Percentiles
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        stats_text.insert(tk.END, "Lifetime Cost Percentiles:\n")
        for p in percentiles:
            value = np.percentile(lifetime_costs, p)
            stats_text.insert(tk.END, f"{p:2d}th percentile: ${value:,.2f}\n")
        stats_text.insert(tk.END, "\n")
        
        # Year-by-year statistics
        stats_text.insert(tk.END, "Year-by-Year Statistics:\n")
        stats_text.insert(tk.END, "Year    Mean      Std Dev   Min       Max\n")
        stats_text.insert(tk.END, "-" * 50 + "\n")
        
        for year in range(len(stats['mean_costs'])):
            actual_year = self.current_plan.start_year + year
            stats_text.insert(tk.END, 
                f"{actual_year}  ${stats['mean_costs'][year]:8,.0f}  "
                f"${stats['std_costs'][year]:8,.0f}  "
                f"${stats['min_costs'][year]:8,.0f}  "
                f"${stats['max_costs'][year]:8,.0f}\n")
        
        stats_text.config(state=tk.DISABLED)
    
    def populate_charts_placeholder(self) -> None:
        """Show placeholder text in charts tab."""
        # Clear existing widgets
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        placeholder = ttk.Label(self.charts_frame, 
                               text="No simulation results available.\nPlease run a simulation first.",
                               font=("Arial", 12))
        placeholder.pack(expand=True)
    
    def populate_charts(self) -> None:
        """Populate the charts tab with visualization."""
        # Clear existing widgets
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Create chart controls
        controls_frame = ttk.Frame(self.charts_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Cost Projection Chart", 
                  command=self.show_cost_projection_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Lifetime Cost Distribution", 
                  command=self.show_lifetime_distribution_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Comprehensive Dashboard", 
                  command=self.show_comprehensive_dashboard).pack(side=tk.LEFT, padx=5)
        
        # Chart display area
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Show default chart
        self.show_cost_projection_chart()
    
    def show_cost_projection_chart(self) -> None:
        """Show the cost projection chart."""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if self.simulation_results is None:
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get data
        stats = self.simulation_results['statistics']
        years = list(range(self.current_plan.start_year, 
                          self.current_plan.start_year + len(stats['mean_costs'])))
        
        # Plot mean costs
        ax.plot(years, stats['mean_costs'], 'b-', linewidth=2, label='Mean Costs')
        
        # Add confidence intervals
        upper_bound = np.array(stats['mean_costs']) + np.array(stats['std_costs'])
        lower_bound = np.array(stats['mean_costs']) - np.array(stats['std_costs'])
        
        ax.fill_between(years, lower_bound, upper_bound, alpha=0.3, color='blue', 
                       label='±1 Standard Deviation')
        
        # Customize chart
        ax.set_xlabel('Year')
        ax.set_ylabel('Annual Cost ($)')
        ax.set_title(f'Cost Projection for {self.current_plan.name}')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_lifetime_distribution_chart(self) -> None:
        """Show the lifetime cost distribution chart."""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if self.simulation_results is None:
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get data
        lifetime_costs = self.simulation_results['lifetime_costs']
        
        # Create histogram
        ax.hist(lifetime_costs, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        
        # Add statistics lines
        mean_cost = np.mean(lifetime_costs)
        median_cost = np.median(lifetime_costs)
        
        ax.axvline(mean_cost, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: ${mean_cost:,.0f}')
        ax.axvline(median_cost, color='green', linestyle='--', linewidth=2, 
                  label=f'Median: ${median_cost:,.0f}')
        
        # Customize chart
        ax.set_xlabel('Lifetime Cost ($)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Lifetime Cost Distribution for {self.current_plan.name}')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_comprehensive_dashboard(self) -> None:
        """Show the comprehensive dashboard."""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if self.simulation_results is None:
            return
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Get data
        stats = self.simulation_results['statistics']
        lifetime_costs = self.simulation_results['lifetime_costs']
        years = list(range(self.current_plan.start_year, 
                          self.current_plan.start_year + len(stats['mean_costs'])))
        
        # Chart 1: Cost projection
        ax1.plot(years, stats['mean_costs'], 'b-', linewidth=2, label='Mean Costs')
        upper_bound = np.array(stats['mean_costs']) + np.array(stats['std_costs'])
        lower_bound = np.array(stats['mean_costs']) - np.array(stats['std_costs'])
        ax1.fill_between(years, lower_bound, upper_bound, alpha=0.3, color='blue')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Annual Cost ($)')
        ax1.set_title('Cost Projection')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Chart 2: Lifetime cost distribution
        ax2.hist(lifetime_costs, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        mean_cost = np.mean(lifetime_costs)
        median_cost = np.median(lifetime_costs)
        ax2.axvline(mean_cost, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: ${mean_cost:,.0f}')
        ax2.axvline(median_cost, color='green', linestyle='--', linewidth=2, 
                   label=f'Median: ${median_cost:,.0f}')
        ax2.set_xlabel('Lifetime Cost ($)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Lifetime Cost Distribution')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Chart 3: Cumulative costs
        cumulative_costs = np.cumsum(stats['mean_costs'])
        ax3.plot(years, cumulative_costs, 'g-', linewidth=2, label='Cumulative Costs')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Cumulative Cost ($)')
        ax3.set_title('Cumulative Cost Projection')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Chart 4: Cost components (example for first year)
        components = ['Premium', 'Deductible', 'Part D', 'Part B']
        first_year_costs = [
            self.current_plan.calculate_premium(0) * 12,
            self.current_plan.calculate_plan_deductible(0),
            self.current_plan.calculate_part_d_premium(0) * 12,
            self.current_plan.calculate_part_b_deductible(0)
        ]
        
        ax4.pie(first_year_costs, labels=components, autopct='%1.1f%%', startangle=90)
        ax4.set_title(f'Cost Components - {self.current_plan.start_year}')
        
        # Overall title
        fig.suptitle(f'Comprehensive Dashboard - {self.current_plan.name}', 
                    fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main() -> None:
    """Main function to run the GUI application."""
    try:
        root = tk.Tk()
        app = MedicareSimulatorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"GUI Error: {str(e)}")
        print("Falling back to command-line interface...")
        from main import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()