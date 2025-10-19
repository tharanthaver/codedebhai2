#!/usr/bin/env python3
"""
Script to start the Flask server with proper error handling and diagnostics
"""

import os
import sys
import logging
from datetime import datetime

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'flask', 'flask_socketio', 'firebase_admin', 'anthropic', 
        'requests', 'PyPDF2', 'docx', 'PIL', 'dotenv'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required modules are available")
    return True

def start_server():
    """Start the Flask server with comprehensive error handling"""
    try:
        print("🚀 Starting Flask server...")
        print(f"📅 Start time: {datetime.now()}")
        print(f"📂 Working directory: {os.getcwd()}")
        
        # Check dependencies first
        if not check_dependencies():
            return
        
        # Set up environment
        os.environ.setdefault('FLASK_ENV', 'development')
        os.environ.setdefault('FLASK_DEBUG', '1')
        
        # Import and start the app
        from app import app, socketio
        
        print("📡 Flask app imported successfully")
        print(f"📋 Available routes:")
        for rule in app.url_map.iter_rules():
            if 'verify_otp' in rule.rule or 'setup_firebase' in rule.rule or rule.rule == '/':
                print(f"   {rule.rule} - {list(rule.methods)}")
        
        print("\n🔥 Starting server on http://localhost:5000")
        print("🔍 You can test the server at: http://localhost:5000")
        print("📱 Firebase auth page: http://localhost:5000/firebase_auth")
        print("\n⚠️  Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the server with SocketIO
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0',  # Listen on all interfaces
            port=5000,
            use_reloader=False,  # Disable reloader to avoid issues
            log_output=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and the app.py file exists")
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 5000 is already in use!")
            print("Try stopping other applications using port 5000 or use a different port")
        else:
            print(f"❌ OS Error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    start_server()
