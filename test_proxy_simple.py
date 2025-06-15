#!/usr/bin/env python3
"""
Simple proxy connection tester for ThorData proxy
"""

import sys
import os
import requests
import argparse
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_proxy_connection(proxy_password=None):
    """Test proxy connection without dependencies"""
    
    print("🔧 ThorData Proxy Connection Test")
    print("=" * 50)
    
    # Proxy configuration
    proxy_host = "42q6t9rp.pr.thordata.net"
    proxy_port = "9999"
    proxy_username = "td-customer-hdXMhtuot8ni"
    
    if not proxy_password:
        proxy_password = input("Enter proxy password: ")
    
    print(f"\n📋 Proxy Configuration:")
    print(f"   Host: {proxy_host}")
    print(f"   Port: {proxy_port}")
    print(f"   Username: {proxy_username}")
    print()
    
    # Test multiple IPs
    print("🔄 Testing IP Rotation (3 different sessions):")
    print("-" * 50)
    
    for i in range(3):
        # Generate session ID for IP rotation
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        session_id = f"test{i}-{timestamp}"
        
        # Build proxy URL with session ID
        full_username = f"{proxy_username}-sessid-{session_id}"
        proxy_url = f"http://{full_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        try:
            # Test connection
            print(f"\nTest {i+1}:")
            print(f"   Session ID: {session_id}")
            
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                ip = data.get('origin', 'Unknown')
                print(f"   ✅ Success! IP: {ip}")
            else:
                print(f"   ❌ Failed with status: {response.status_code}")
                
        except requests.exceptions.ProxyError as e:
            print(f"   ❌ Proxy Error: Authentication failed or proxy unreachable")
            print(f"      Check your password and proxy settings")
            
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout: Connection took too long")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Proxy test complete!")
    print("\nNext steps:")
    print("1. If all tests passed, your proxy is working correctly")
    print("2. Each test should show a different IP address")
    print("3. You can use this proxy for the IGR scraper")

def main():
    parser = argparse.ArgumentParser(description='Test ThorData Proxy Connection')
    parser.add_argument('--password', '-p', type=str, help='Proxy password')
    args = parser.parse_args()
    
    try:
        test_proxy_connection(args.password)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 