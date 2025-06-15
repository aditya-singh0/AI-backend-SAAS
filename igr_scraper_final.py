#!/usr/bin/env python3
"""
Maharashtra IGR QR Code Scraper - Final Version
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

class IGRScraperFinal:
    def __init__(self, proxy_password=None):
        self.session = requests.Session()
        self.proxy_password = proxy_password
        self.session_id = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
    def run(self):
        """Main entry point"""
        url = 'https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index'
        print(f"\n🌐 Accessing IGR website...")
        print(f"Using proxy: {'Yes' if self.proxy_password else 'No'}")
        
        # Load page
        response = self.session.get(url, verify=False, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        print("✅ Page loaded")
        
        # Find CAPTCHA
        captcha = soup.find('img', {'id': 'captcha-img'})
        if captcha:
            print("\n🔍 CAPTCHA found!")
            captcha_url = urljoin(url, captcha.get('src', ''))
            
            # Download CAPTCHA
            print("📥 Downloading CAPTCHA...")
            img_response = self.session.get(captcha_url, verify=False)
            with open('captcha_image.png', 'wb') as f:
                f.write(img_response.content)
            print("✅ Saved as captcha_image.png")
            
            # Get user input
            print("\n📝 Please open captcha_image.png and solve it")
            captcha_text = input("Enter CAPTCHA text: ")
            print(f"You entered: {captcha_text}")
        
        print("\n✅ Process complete!")
        return True

def main():
    print("🏛️ Maharashtra IGR Scraper")
    print("=" * 50)
    
    password = input("Enter proxy password (or press Enter to skip): ").strip()
    
    scraper = IGRScraperFinal(password)
    scraper.run()

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main() 