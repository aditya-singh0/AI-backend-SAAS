#!/usr/bin/env python3

import sys
import os
import time

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from captcha_helper_scraper import CAPTCHAHelperScraper
from bs4 import BeautifulSoup

class MumbaiCAPTCHAScraper(CAPTCHAHelperScraper):
    def __init__(self, year="2024", proxy_manager=None):
        super().__init__(proxy_manager)
        self.year = year
        
        # Mumbai parameters in Marathi
        self.mumbai_params = {
            'district_text': 'मुंबई',  # Mumbai in Marathi
            'district_text_alt': 'mumbai',  # Alternative text
            'article_text': 'अॅग्रीमेंट टू सेल',  # Agreement to Sale in Marathi
            'article_text_alt': 'agreement',  # Alternative text
            'area_text': 'अंधेरी',  # Andheri in Marathi
        }
        
    def find_and_select_option(self, soup, select_id, search_texts):
        """Find and return the value for an option containing any of the search texts"""
        select_elem = soup.select_one(f'select#{select_id}')
        if select_elem:
            options = select_elem.find_all('option')
            for option in options:
                option_text = option.get_text(strip=True)
                option_value = option.get('value', '')
                
                # Check if any search text matches
                for search_text in search_texts:
                    if search_text.lower() in option_text.lower():
                        print(f"✅ Found {select_id}: {option_text} (value={option_value})")
                        return option_value
        return None
        
    def fill_mumbai_form(self, soup, form_data):
        """Fill form with Mumbai-specific data"""
        print("\n📝 Filling Mumbai-specific form data...")
        
        # Find and set district (Mumbai)
        district_value = self.find_and_select_option(
            soup, 
            'district_id',
            [self.mumbai_params['district_text'], self.mumbai_params['district_text_alt']]
        )
        if district_value:
            form_data['district_id'] = district_value
            
        # Find and set article type (Agreement for Sale)
        article_value = self.find_and_select_option(
            soup,
            'article_id', 
            [self.mumbai_params['article_text'], self.mumbai_params['article_text_alt']]
        )
        if article_value:
            form_data['article_id'] = article_value
            
        # Find and set year
        year_value = self.find_and_select_option(
            soup,
            'dbselect',
            [str(self.year)]
        )
        if year_value:
            form_data['dbselect'] = year_value
            form_data['yearsel'] = self.year
            
        return form_data
        
    def mumbai_search_with_captcha(self):
        """Mumbai search with proper form filling and CAPTCHA handling"""
        print("🏙️ Mumbai IGR Scraper with CAPTCHA Helper")
        print("=" * 70)
        print(f"📍 District: {self.mumbai_params['district_text']} (Mumbai)")
        print(f"📄 Article: {self.mumbai_params['article_text']} (Agreement for Sale)")
        print(f"📅 Year: {self.year}")
        print("=" * 70)
        
        igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        
        try:
            # Load the page
            print("\n🌐 Loading IGR website...")
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
            
            # Fill Mumbai-specific data
            form_data = self.fill_mumbai_form(soup, form_data)
            
            # First submission attempt (this will likely trigger CAPTCHA)
            print(f"\n🚀 Submitting form to trigger CAPTCHA...")
            
            response = self.session.post(
                igr_url,
                data=form_data,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if CAPTCHA is now required
            if self.detect_igr_captcha(soup):
                print(f"\n🚨 CAPTCHA detected! Starting enhanced CAPTCHA handler...")
                
                # Update form data with new CSRF token
                new_form_data = self.get_form_data(soup)
                form_data['_csrfToken'] = new_form_data.get('_csrfToken', form_data.get('_csrfToken'))
                
                # Fill Mumbai data again
                form_data = self.fill_mumbai_form(soup, form_data)
                
                # Handle CAPTCHA
                captcha_success = self.enhanced_captcha_handling(soup, igr_url, form_data)
                
                if captcha_success:
                    print(f"\n✅ CAPTCHA solved successfully!")
                    print(f"🎯 Processing search results...")
                    
                    # Parse results
                    results = self.scrape_qr_codes_from_soup(soup, igr_url)
                    
                    if results:
                        print(f"\n🎉 Found {len(results)} QR codes!")
                        for i, result in enumerate(results, 1):
                            print(f"\n📱 QR Code #{i}:")
                            print(f"   🔗 Image URL: {result['image_url']}")
                            for j, content in enumerate(result['qr_contents']):
                                print(f"   📄 Content #{j+1}: {content}")
                    else:
                        print(f"\n❌ No QR codes found in results")
                else:
                    print(f"\n❌ Could not solve CAPTCHA after multiple attempts")
            else:
                # Check if we got results without CAPTCHA
                results = self.scrape_qr_codes_from_soup(soup, igr_url)
                if results:
                    print(f"\n🎉 Found {len(results)} QR codes (no CAPTCHA required)!")
                    for i, result in enumerate(results, 1):
                        print(f"\n📱 QR Code #{i}:")
                        print(f"   🔗 Image URL: {result['image_url']}")
                        for j, content in enumerate(result['qr_contents']):
                            print(f"   📄 Content #{j+1}: {content}")
                else:
                    print("\n❓ No CAPTCHA detected, but also no results found")
                    print("Form may require additional parameters")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    # Get year from command line or use default
    year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    print(f"🚀 Starting Mumbai CAPTCHA scraper with year: {year}")
    
    scraper = MumbaiCAPTCHAScraper(year=year)
    scraper.mumbai_search_with_captcha()

if __name__ == "__main__":
    main() 