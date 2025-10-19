#!/usr/bin/env python3
"""
Demo script showing how to fix terminal path issues and take screenshots
"""

from terminal_utils import TerminalUtils, clean_terminal_path, take_screenshot, fix_terminal, suppress_extra_output
import sys

def main():
    """Main demonstration function"""
    print("=" * 60)
    print("Terminal Utilities Demo")
    print("=" * 60)
    
    # Initialize terminal utils
    utils = TerminalUtils()
    
    # 1. Show current terminal path issue (before fix)
    print("\n1. Current terminal state:")
    print("This is your normal program output...")
    print("20 30 30")  # Simulating your program output
    
    # 2. Generate clean terminal path
    print("\n2. Generating clean terminal path:")
    clean_path = clean_terminal_path()
    print(f"Clean path: {clean_path}")
    
    # 3. Fix terminal prompt display
    print("\n3. Fixing terminal prompt display:")
    fix_result = fix_terminal()
    print(f"Fix result: {fix_result}")
    
    # 4. Take a screenshot
    print("\n4. Taking terminal screenshot:")
    screenshot_result = take_screenshot("terminal_fixed.png")
    print(f"Screenshot: {screenshot_result}")
    
    # 5. Suppress extra terminal output
    print("\n5. Suppressing extra output...")
    suppress_extra_output()
    
    print("\n" + "=" * 60)
    print("Demo completed! Terminal should be clean now.")
    print("=" * 60)
    
    # This should NOT show extra prompt after this line
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        suppress_extra_output()
        sys.exit(1)
    except Exception as e:
        print(f"Error in demo: {e}")
        suppress_extra_output()
        sys.exit(1)
