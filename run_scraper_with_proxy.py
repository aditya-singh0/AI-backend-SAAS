#!/usr/bin/env python3
"""
IGR Scraper with Proxy Support - No QR Dependencies
This version focuses on form automation and CAPTCHA handling
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import argparse
from urllib.parse import urljoin
import io
from PIL import Image

# Proxy configuration
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni'
}

class SimpleIGRScraper:
    def __init__(self, proxy_password=None):
        self.session = requests.Session()
        self.proxy_password = proxy_password
        self.session_id = None
        
        # Headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def get_proxy(self, new_ip=False):
        """Get proxy configuration"""
        if not self.proxy_password:
            return None
            
        # Generate or reuse session ID
        if new_ip or not self.session_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            self.session_id = f"igr-{timestamp}"
            print(f"🔄 New session ID: {self.session_id}")
        
        # Build proxy URL
        full_username = f"{PROXY_CONFIG['username']}-sessid-{self.session_id}"
        proxy_url = f"http://{full_username}:{self.proxy_password}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    def download_captcha(self, url):
        """Download and save CAPTCHA image"""
        try:
            print("📥 Downloading CAPTCHA image...")
            response = self.session.get(
                url,
                headers=self.headers,
                proxies=self.get_proxy(),
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            # Save CAPTCHA
            with open('captcha_image.png', 'wb') as f:
                f.write(response.content)
                
            print("✅ CAPTCHA saved as 'captcha_image.png'")
            
            # Show image info
            try:
                img = Image.open(io.BytesIO(response.content))
                print(f"📐 Image size: {img.size}")
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"❌ Error downloading CAPTCHA: {e}")
            return False
    
    def scrape_igr_website(self, url):
        """Main scraping workflow"""
        print("\n🏛️ Maharashtra IGR Website Scraper")
        print("=" * 60)
        
        try:
            # Try HTTP version first
            if url.startswith('https://'):
                http_url = url.replace('https://', 'http://')
                print(f"\n🔄 Trying HTTP version first: {http_url}")
            else:
                http_url = url
                
            # Step 1: Load page
            print(f"\n🌐 Loading page...")
            
            # Configure session for proxy
            self.session.trust_env = False  # Don't use system proxy settings
            
            try:
                # Try with HTTP first
                response = self.session.get(
                    http_url,
                    headers=self.headers,
                    proxies=self.get_proxy(new_ip=True),
                    verify=False,
                    timeout=30,
                    allow_redirects=True
                )
                response.raise_for_status()
            except:
                # If HTTP fails, try without proxy
                print("⚠️ Proxy connection failed, trying direct connection...")
                response = self.session.get(
                    url,
                    headers=self.headers,
                    verify=False,
                    timeout=30
                )
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✅ Page loaded successfully")
            
            # Step 2: Check for CAPTCHA
            captcha_img = soup.select_one('img#captcha-img')
            if captcha_img:
                print("\n🔍 CAPTCHA detected!")
                captcha_url = urljoin(url, captcha_img.get('src', ''))
                
                if self.download_captcha(captcha_url):
                    print("\n📝 Please solve the CAPTCHA:")
                    print("1. Open 'captcha_image.png' in your file explorer")
                    print("2. Enter the text you see below")
                    
                    captcha_text = input("\nEnter CAPTCHA text: ").strip()
                    print(f"✅ CAPTCHA entered: {captcha_text}")
            
            # Step 3: Show available form fields
            print("\n📋 Available form fields:")
            
            # Find all select dropdowns
            selects = soup.find_all('select')
            for select in selects:
                select_id = select.get('id', 'unknown')
                select_name = select.get('name', 'unknown')
                options = select.find_all('option')
                
                print(f"\n📌 {select_id or select_name}:")
                for i, option in enumerate(options[:5]):  # Show first 5 options
                    value = option.get('value', '')
                    text = option.get_text(strip=True)
                    print(f"   {value}: {text}")
                if len(options) > 5:
                    print(f"   ... and {len(options) - 5} more options")
            
            # Step 4: Find images (potential QR codes)
            images = soup.find_all('img')
            print(f"\n🖼️ Found {len(images)} images on the page")
            
            for i, img in enumerate(images[:10], 1):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    print(f"   Image {i}: {src[:50]}{'...' if len(src) > 50 else ''}")
                    if alt:
                        print(f"            Alt: {alt}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(description='IGR Scraper with Proxy Support')
    parser.add_argument('--password', '-p', type=str, help='Proxy password')
    parser.add_argument('--url', type=str, 
                       default='https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index',
                       help='IGR website URL')
    args = parser.parse_args()
    
    print("🔧 IGR Scraper with Proxy Support")
    print("=" * 60)
    
    # Get password if not provided
    proxy_password = args.password
    if not proxy_password:
        proxy_password = input("Enter proxy password (or press Enter to skip): ").strip()
    
    if proxy_password:
        print("\n✅ Proxy enabled with IP rotation")
        print(f"   Endpoint: {PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}")
    else:
        print("\n⚠️ Running without proxy (direct connection)")
    
    # Create scraper
    scraper = SimpleIGRScraper(proxy_password)
    
    # Run scraping
    success = scraper.scrape_igr_website(args.url)
    
    if success:
        print("\n✅ Scraping completed!")
    else:
        print("\n❌ Scraping failed!")
    
    print("\n" + "=" * 60)
    print("Session complete. CAPTCHA image saved if found.")

if __name__ == "__main__":
    try:
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings()
        
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 