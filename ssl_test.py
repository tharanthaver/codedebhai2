#!/usr/bin/env python3
"""
SSL Connection Test Script
This script helps diagnose SSL/HTTPS connection issues with Supabase or other APIs
"""

import requests
import ssl
import socket
import urllib3
from urllib.parse import urlparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ssl_connection():
    """Test SSL connection to Supabase"""
    
    # Get Supabase URL from environment or use a test URL
    supabase_url = os.getenv('SUPABASE_URL')
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment variables")
        print("Please set SUPABASE_URL in your .env file or environment")
        return False
    
    print(f"🔍 Testing SSL connection to: {supabase_url}")
    print("-" * 50)
    
    # Parse URL
    parsed_url = urlparse(supabase_url)
    hostname = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    
    # Test 1: Basic socket connection
    print("1. Testing basic socket connection...")
    try:
        sock = socket.create_connection((hostname, port), timeout=10)
        print("✅ Socket connection successful")
        sock.close()
    except Exception as e:
        print(f"❌ Socket connection failed: {e}")
        return False
    
    # Test 2: SSL context and certificate
    print("\n2. Testing SSL context and certificate...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL handshake successful")
                print(f"   Certificate subject: {cert.get('subject', 'N/A')}")
                print(f"   Certificate issuer: {cert.get('issuer', 'N/A')}")
    except Exception as e:
        print(f"❌ SSL connection failed: {e}")
        return False
    
    # Test 3: Requests library with verification
    print("\n3. Testing requests library with SSL verification...")
    try:
        response = requests.get(f"{supabase_url}/rest/v1/", 
                              headers={'apikey': os.getenv('SUPABASE_ANON_KEY', 'test')},
                              timeout=10)
        print(f"✅ Requests with SSL verification successful")
        print(f"   Status code: {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error with requests: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Request completed but got error: {e}")
        print("   This might be expected if the API key is invalid")
    
    # Test 4: Requests library without verification (temporary test)
    print("\n4. Testing requests library WITHOUT SSL verification...")
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(f"{supabase_url}/rest/v1/", 
                              headers={'apikey': os.getenv('SUPABASE_ANON_KEY', 'test')},
                              verify=False, 
                              timeout=10)
        print(f"✅ Requests without SSL verification successful")
        print(f"   Status code: {response.status_code}")
        print("   ⚠️  This confirms the SSL issue is with certificate verification")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed even without SSL verification: {e}")
        return False
    
    return True

def print_environment_info():
    """Print relevant environment information"""
    print("\n" + "="*50)
    print("ENVIRONMENT INFORMATION")
    print("="*50)
    print(f"Python version: {sys.version}")
    print(f"Requests version: {requests.__version__}")
    print(f"urllib3 version: {urllib3.__version__}")
    print(f"SSL version: {ssl.OPENSSL_VERSION}")
    
    # Check for proxy settings
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        if os.getenv(var):
            print(f"⚠️  {var}: {os.getenv(var)}")
    
    # Check SSL-related environment variables
    ssl_vars = ['PYTHONHTTPSVERIFY', 'SSL_CERT_FILE', 'SSL_CERT_DIR']
    for var in ssl_vars:
        if os.getenv(var):
            print(f"📋 {var}: {os.getenv(var)}")

def main():
    """Main function to run all tests"""
    print("🚀 Starting SSL Connection Diagnostics")
    print("="*50)
    
    print_environment_info()
    
    print("\n" + "="*50)
    print("RUNNING SSL TESTS")
    print("="*50)
    
    success = test_ssl_connection()
    
    print("\n" + "="*50)
    print("RECOMMENDATIONS")
    print("="*50)
    
    if success:
        print("✅ All SSL tests passed!")
        print("Your SSL connection should work fine.")
    else:
        print("❌ Some SSL tests failed.")
        print("\nTry these solutions:")
        print("1. Update your certificates:")
        print("   pip install --upgrade certifi")
        print("\n2. Update networking libraries:")
        print("   pip install --upgrade requests urllib3 httpcore")
        print("\n3. Check if you're behind a corporate firewall/proxy")
        print("\n4. Try running your app with a different Python version")
        print("\n5. If all else fails, temporarily disable SSL verification")
        print("   (NOT recommended for production)")

if __name__ == "__main__":
    main()
