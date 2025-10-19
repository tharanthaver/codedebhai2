#!/usr/bin/env python3
"""
Install new dependencies for real-time progress tracking
"""

import subprocess
import sys

def install_dependencies():
    """Install the new dependencies"""
    dependencies = [
        "Flask-SocketIO==5.4.1",
        "psycopg2-binary==2.9.9"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Successfully installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Installing real-time progress tracking dependencies...")
    
    if install_dependencies():
        print("\n✅ All dependencies installed successfully!")
        print("\n📋 Next steps:")
        print("1. Run the task tracking setup: python setup_task_tracking.py")
        print("2. Start your Flask application")
        print("3. The real-time progress tracking is now active!")
    else:
        print("\n❌ Some dependencies failed to install. Please check the errors above.")
