#!/usr/bin/env python3
"""
Test script to check URL accessibility
"""
import requests

def test_url_access():
    """Test if Cashfree URLs are accessible"""
    
    # Test different Cashfree URLs
    test_urls = [
        "https://checkout.cashfree.com",
        "https://api.cashfree.com/pg",
        "https://payments.cashfree.com"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing {url}...")
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Accessible: ✅")
        except requests.exceptions.DNSError as e:
            print(f"  DNS Error: ❌ {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"  Connection Error: ❌ {e}")
        except requests.exceptions.Timeout as e:
            print(f"  Timeout Error: ❌ {e}")
        except Exception as e:
            print(f"  Other Error: ❌ {e}")
        print()

if __name__ == "__main__":
    test_url_access()
