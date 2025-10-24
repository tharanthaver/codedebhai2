#!/usr/bin/env python3
"""
Quick Payment System Test Runner
Runs the comprehensive payment system tests with proper environment setup
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the comprehensive payment system tests"""
    print("🔧 Payment System Test Runner")
    print("=" * 50)
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    test_script = script_dir / "comprehensive_payment_test.py"
    
    # Check if test script exists
    if not test_script.exists():
        print(f"❌ Test script not found: {test_script}")
        return False
    
    # Check for .env file
    env_file = script_dir / ".env"
    if not env_file.exists():
        print(f"⚠️ Warning: .env file not found at {env_file}")
        print("Make sure your environment variables are set properly.")
    
    print(f"📍 Running tests from: {script_dir}")
    print(f"🧪 Test script: {test_script}")
    
    try:
        # Change to the script directory
        os.chdir(script_dir)
        
        # Run the comprehensive test
        result = subprocess.run([
            sys.executable, 
            str(test_script)
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Test runner completed successfully!")
    else:
        print("\n❌ Test runner encountered issues.")
    sys.exit(0 if success else 1)