#!/usr/bin/env python3
"""Launcher script for the Medicare Plan Simulator apps (fixed versions)."""

import subprocess
import sys
import os


def main():
    """Main launcher function."""
    print("🏥 Medicare Plan Simulator (Fixed Versions)")
    print("=" * 50)
    print("Choose an application to run:")
    print()
    print("1. Plan Selection & Simulation (app_updated_fixed.py)")
    print("   - Select from predefined plans (Plan-G, Plan-HDG)")
    print("   - Create custom plans")
    print("   - Run Monte Carlo simulations")
    print("   - ✅ Fixed Plotly deprecation warnings")
    print()
    print("2. Plan Comparison Tool (app_comparison_fixed.py)")
    print("   - Compare two plans side by side")
    print("   - Visual comparison charts")
    print("   - Statistical comparison")
    print("   - ✅ Fixed Plotly deprecation warnings")
    print()
    print("3. Original App (app_fixed.py)")
    print("   - Legacy version with manual parameter input")
    print("   - ✅ Fixed Plotly deprecation warnings")
    print()
    print("4. Original Apps (with warnings)")
    print("   - app_updated.py, app_comparison.py, app.py")
    print("   - ⚠️  May show deprecation warnings")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\n🚀 Launching Plan Selection & Simulation (Fixed)...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app_updated_fixed.py"])
                break
            elif choice == "2":
                print("\n🚀 Launching Plan Comparison Tool (Fixed)...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app_comparison_fixed.py"])
                break
            elif choice == "3":
                print("\n🚀 Launching Original App (Fixed)...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app_fixed.py"])
                break
            elif choice == "4":
                print("\n🚀 Launching Original Apps (with warnings)...")
                print("Choose which original app to run:")
                print("a) app_updated.py")
                print("b) app_comparison.py") 
                print("c) app.py")
                sub_choice = input("Enter sub-choice (a-c): ").strip().lower()
                
                if sub_choice == "a":
                    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_updated.py"])
                elif sub_choice == "b":
                    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_comparison.py"])
                elif sub_choice == "c":
                    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
                else:
                    print("Invalid sub-choice.")
                    continue
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()

