#!/usr/bin/env python3
"""
Test script for the realistic VS Code screenshot generator using website output.
This script demonstrates how to use the create_realistic_vscode_screenshot function
with output that would be produced by the website.
"""

import os
import sys
from realistic_vscode_screenshot import create_realistic_vscode_screenshot

def main():
    """
    Main test function that generates a VS Code screenshot with website-like output
    """
    # Sample website output (similar to what would be produced by the website)
    website_output = """Hello, world!

This is a factorial calculation program.
Factorial of 5 is: 120

This is a prime number checker.
7 is a prime number.

This is a string reverser.
Reversed string: olleh

All tests completed successfully!
"""
    
    # Generate the screenshot with the website output
    print("Generating VS Code screenshot with website output...")
    screenshot_bytes = create_realistic_vscode_screenshot(
        output_text=website_output,
        user_name="THARAN",  # Using the actual username from the system
        document_terminal_path=None  # Will use default path from terminal_utils
    )
    
    # Save the screenshot to a file
    output_file = "website_output_screenshot.png"
    with open(output_file, "wb") as f:
        f.write(screenshot_bytes)
    
    # Print success message
    print(f"Screenshot saved as {output_file}")
    print(f"File size: {len(screenshot_bytes) / 1024:.2f} KB")
    
    # Check if file was created successfully
    if os.path.exists(output_file):
        print(f"✅ Screenshot created successfully at: {os.path.abspath(output_file)}")
    else:
        print("❌ Failed to create screenshot file")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)