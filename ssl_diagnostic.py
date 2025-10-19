import ssl
import socket
from urllib.parse import urlparse
import certifi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase URL
supabase_url = os.getenv('SUPABASE_URL')
print(f'Testing SSL connection to: {supabase_url}')

# Parse URL
parsed = urlparse(supabase_url)
hostname = parsed.hostname
port = parsed.port or (443 if parsed.scheme == 'https' else 80)

print(f'Hostname: {hostname}')
print(f'Port: {port}')

try:
    # Create SSL context
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    
    # Connect to server
    with socket.create_connection((hostname, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print('SSL connection successful!')
            
            # Get certificate info
            cert = ssock.getpeercert()
            print(f'Certificate subject: {cert.get("subject", "Unknown")}')
            print(f'Certificate issuer: {cert.get("issuer", "Unknown")}')
            print(f'Certificate version: {cert.get("version", "Unknown")}')
            
            # Check if certificate is valid
            print('Certificate validation: PASSED')
            
except ssl.SSLError as e:
    print(f'SSL Error: {e}')
except socket.error as e:
    print(f'Socket Error: {e}')
except Exception as e:
    print(f'General Error: {e}')

# Test Python SSL module
print('\nPython SSL module info:')
print(f'SSL version: {ssl.OPENSSL_VERSION}')
print(f'SSL library: {ssl.OPENSSL_VERSION_INFO}')
print(f'Certificate file: {certifi.where()}')
