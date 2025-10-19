#!/usr/bin/env python3
"""
Test Firebase configuration
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_firebase_config():
    api_key = os.getenv('FIREBASE_API_KEY')
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    
    print(f"🔥 Testing Firebase Configuration")
    print(f"📱 Project ID: {project_id}")
    print(f"🔑 API Key: {api_key[:20]}..." if api_key else "❌ API Key not found")
    
    if not api_key or not project_id:
        print("❌ Firebase configuration incomplete")
        return False
    
    # Test Firebase Auth API
    try:
        # Test with a simple lookup request (should fail gracefully but return proper Firebase error)
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup"
        params = {"key": api_key}
        payload = {"idToken": "test"}
        
        response = requests.post(url, json=payload, params=params, timeout=10)
        
        print(f"🌐 Firebase API Response Status: {response.status_code}")
        
        if response.status_code in [400, 401, 403]:
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    print("✅ Firebase API is reachable and working")
                    print(f"📋 Response: {error_data['error']['message']}")
                    return True
            except:
                pass
        
        print("⚠️ Unexpected response from Firebase")
        print(f"Response: {response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Error connecting to Firebase: {e}")
        return False

if __name__ == "__main__":
    test_firebase_config()
