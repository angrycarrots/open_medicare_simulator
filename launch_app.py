#!/usr/bin/env python3
"""Launcher script for the Medicare Plan Simulator apps."""

import subprocess
import sys
import os


def main():
    """Main launcher function."""
    print("🏥 Medicare Plan Simulator")
    print("=" * 40)
    print("Choose an application to run:")
    print()
    print("1. Plan Selection & Simulation (app_updated.py)")
    print("   - Select from predefined plans (Plan-G, Plan-HDG)")
    print("   - Create custom plans")
    print("   - Run Monte Carlo simulations")
    print()
    print("2. Plan Comparison Tool (app_comparison.py)")
    print("   - Compare two plans side by side")
    print("   - Visual comparison charts")
    print("   - Statistical comparison")
    print()
    print("3. Original App (app.py)")
    print("   - Legacy version with manual parameter input")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\n🚀 Launching Plan Selection & Simulation...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app_updated.py"])
                break
            elif choice == "2":
                print("\n🚀 Launching Plan Comparison Tool...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app_comparison.py"])
                break
            elif choice == "3":
                print("\n🚀 Launching Original App...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()

