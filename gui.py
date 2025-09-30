"""GUI application for Medicare/Medigap Monte Carlo simulation with fallback to CLI."""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main() -> None:
    """Main function that provides GUI instructions and runs CLI."""
    print("=" * 60)
    print("MEDICARE/MEDIGAP SIMULATION")
    print("=" * 60)
    print()
    print("GUI INTERFACE NOT AVAILABLE")
    print("=" * 60)
    print()
    print("The tkinter GUI requires a display server (X11/Wayland) which")
    print("is not available in your current environment.")
    print()
    print("This commonly happens in:")
    print("  • WSL2 without X11 forwarding")
    print("  • Headless servers")
    print("  • Remote SSH sessions without display")
    print()
    print("SOLUTIONS:")
    print("  1. Use the command-line interface:")
    print("     python main.py")
    print()
    print("  2. Set up X11 forwarding (WSL2):")
    print("     • Install VcXsrv or Xming on Windows")
    print("     • Set DISPLAY=localhost:0.0")
    print("     • Run: export DISPLAY=localhost:0.0")
    print("     • Then run: python gui.py")
    print()
    print("  3. Use WSLg (Windows 11):")
    print("     • Update to Windows 11")
    print("     • WSLg provides native GUI support")
    print("     • Then run: python gui.py")
    print()
    print("  4. Use a different environment:")
    print("     • Run on a local machine with display")
    print("     • Use a cloud IDE with GUI support")
    print()
    print("Running command-line interface instead...")
    print("=" * 60)
    print()
    
    # Import and run the main command-line interface
    from main import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()