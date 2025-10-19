#!/usr/bin/env python3
"""
Solution script that prevents extra terminal path prompts
"""

import sys
import os

# Import our terminal utilities
try:
    from terminal_utils import suppress_extra_output, fix_terminal
    TERMINAL_UTILS_AVAILABLE = True
except ImportError:
    TERMINAL_UTILS_AVAILABLE = False

def main():
    """Main solution function"""
    try:
        # Your original program logic here
        print("10 20 30")  # Example output
        
        # Any other calculations or processing...
        result = 10 + 20 + 30
        
        # Clean exit without extra prompts
        if TERMINAL_UTILS_AVAILABLE:
            # Suppress any extra terminal output
            suppress_extra_output()
            
            # Fix terminal state
            fix_terminal()
        
        # Clean exit
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        
        # Clean up terminal even on error
        if TERMINAL_UTILS_AVAILABLE:
            suppress_extra_output()
        
        sys.exit(1)

def clean_exit():
    """Ensure clean exit without extra prompts"""
    if TERMINAL_UTILS_AVAILABLE:
        suppress_extra_output()
    sys.stdout.flush()
    sys.stderr.flush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clean_exit()
        sys.exit(1)
    finally:
        # Always clean up on exit
        clean_exit()
