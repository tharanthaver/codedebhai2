#!/usr/bin/env python3
"""
Local development startup script with ngrok tunnel
"""
import os
import sys
import subprocess
import time
import requests
import json
from threading import Thread

def start_flask_app():
    """Start the Flask application"""
    print("🚀 Starting Flask application...")
    try:
        # Start Flask app in a separate process
        return subprocess.Popen([sys.executable, "app.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        return None

def start_ngrok_tunnel():
    """Start ngrok tunnel"""
    print("🌐 Starting ngrok tunnel...")
    try:
        # Start ngrok tunnel for port 5000
        return subprocess.Popen(["./ngrok.exe", "http", "5000"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None

def get_ngrok_url():
    """Get the ngrok public URL"""
    try:
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get ngrok status
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get("tunnels", [])
            
            for tunnel in tunnels:
                if tunnel.get("proto") == "https":
                    return tunnel.get("public_url")
        
        return None
    except Exception as e:
        print(f"❌ Failed to get ngrok URL: {e}")
        return None

def update_env_file(ngrok_url):
    """Update .env file with ngrok URL"""
    try:
        # Read current .env file
        with open(".env", "r") as f:
            content = f.read()
        
        # Update URLs
        callback_url = f"{ngrok_url}/payment/callback"
        webhook_url = f"{ngrok_url}/payment/webhook"
        
        # Replace the URLs
        content = content.replace(
            "PAYMENT_RETURN_URL=https://codedebhai.com/payment/callback",
            f"PAYMENT_RETURN_URL={callback_url}"
        )
        content = content.replace(
            "PAYMENT_WEBHOOK_URL=https://codedebhai.com/payment/webhook",
            f"PAYMENT_WEBHOOK_URL={webhook_url}"
        )
        
        # Write back to .env file
        with open(".env", "w") as f:
            f.write(content)
        
        print(f"✅ Updated .env file with ngrok URLs:")
        print(f"   Return URL: {callback_url}")
        print(f"   Webhook URL: {webhook_url}")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")

def main():
    """Main function"""
    print("🔧 Local Development Setup with ngrok")
    print("=" * 50)
    
    # Start ngrok first
    ngrok_process = start_ngrok_tunnel()
    if not ngrok_process:
        return
    
    # Get ngrok URL
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ Failed to get ngrok URL")
        return
    
    print(f"✅ ngrok tunnel active: {ngrok_url}")
    
    # Update environment
    update_env_file(ngrok_url)
    
    print("\n🎉 Setup complete!")
    print(f"🌐 Your local app is now accessible at: {ngrok_url}")
    print(f"🔗 Payment callbacks will work with Cashfree production")
    print("\nℹ️  Now restart your Flask app to use the new URLs")
    print("Press Ctrl+C to stop ngrok tunnel")
    
    try:
        # Keep ngrok running
        ngrok_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping ngrok tunnel...")
        ngrok_process.terminate()

if __name__ == "__main__":
    main()
