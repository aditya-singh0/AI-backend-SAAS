#!/usr/bin/env python3

import sys
import os

# Copy the imports and class from the original file
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from captcha_helper_scraper import CAPTCHAHelperScraper
from bs4 import BeautifulSoup

class CLICAPTCHAHelperScraper(CAPTCHAHelperScraper):
    def __init__(self, year="2024", proxy_manager=None):
        super().__init__(proxy_manager)
        self.year = year
        
    def mumbai_search_with_captcha_helper(self):
        """Mumbai search with CLI year parameter"""
        print("🏙️ Mumbai IGR Scraper with CAPTCHA Helper (CLI Mode)")
        print("=" * 70)
        print("Features:")
        print("✅ OCR suggestions for CAPTCHA text")
        print("✅ Multiple retry attempts")  
        print("✅ Automatic success detection")
        print("✅ Saves all CAPTCHA images with timestamps")
        print("=" * 70)
        
        igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        
        try:
            # Load the page
            print("🌐 Loading IGR website...")
            response = self.session.get(
                igr_url,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✅ Page loaded successfully")
            
            # Get form data
            form_data = self.get_form_data(soup)
            
            # Use provided year
            print(f"\n📅 Using year: {self.year}")
            
            # Set up Mumbai search parameters
            print(f"\n🔍 Setting up Mumbai search parameters...")
            
            # Handle CAPTCHA with enhanced logic
            if self.detect_igr_captcha(soup):
                print(f"\n🚨 CAPTCHA detected! Starting enhanced CAPTCHA handler...")
                
                captcha_success = self.enhanced_captcha_handling(soup, igr_url, form_data)
                
                if captcha_success:
                    print(f"\n✅ CAPTCHA solved successfully!")
                    print(f"🎯 Proceeding with form submission...")
                    
                    # Now submit the actual search
                    results = self.submit_form_and_scrape(igr_url, form_data)
                    
                    if results:
                        print(f"\n🎉 Found {len(results)} QR codes!")
                        for result in results:
                            print(f"QR: {result['qr_contents']}")
                    else:
                        print(f"\n❌ No QR codes found in results")
                else:
                    print(f"\n❌ Could not solve CAPTCHA after multiple attempts")
                    
            else:
                print("No CAPTCHA detected, proceeding with search...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    # Get year from command line or use default
    year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    print(f"🚀 Starting scraper with year: {year}")
    
    scraper = CLICAPTCHAHelperScraper(year=year)
    scraper.mumbai_search_with_captcha_helper()

if __name__ == "__main__":
    main() 