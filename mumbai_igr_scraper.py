#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper
from bs4 import BeautifulSoup

class MumbaiIGRScraper(IGRSpecializedScraper):
    def __init__(self, proxy_manager=None):
        super().__init__(proxy_manager)
        
        # Mumbai-specific default values
        self.mumbai_defaults = {
            'district_name': 'Mumbai',
            'district_id': None,  # Will be determined from dropdown
            'taluka_name': 'Mumbai',
            'taluka_id': None,    # Will be determined from dropdown
            'article_name': 'Agreement for Sale',
            'article_id': None,   # Will be determined from dropdown
        }
    
    def find_mumbai_options(self, soup):
        """Find Mumbai-specific option values from dropdowns"""
        mumbai_options = {}
        
        # Find district dropdown and look for Mumbai
        district_select = soup.select_one(self.igr_selectors['district_select'])
        if district_select:
            options = district_select.find_all('option')
            for option in options:
                text = option.get_text(strip=True).lower()
                if 'mumbai' in text:
                    mumbai_options['district_id'] = option.get('value', '')
                    mumbai_options['district_name'] = option.get_text(strip=True)
                    print(f"🏙️ Found Mumbai District: ID={mumbai_options['district_id']}, Name={mumbai_options['district_name']}")
                    break
        
        # Find taluka dropdown and look for Mumbai
        taluka_select = soup.select_one(self.igr_selectors['taluka_select'])
        if taluka_select:
            options = taluka_select.find_all('option')
            for option in options:
                text = option.get_text(strip=True).lower()
                if 'mumbai' in text:
                    mumbai_options['taluka_id'] = option.get('value', '')
                    mumbai_options['taluka_name'] = option.get_text(strip=True)
                    print(f"🏙️ Found Mumbai Taluka: ID={mumbai_options['taluka_id']}, Name={mumbai_options['taluka_name']}")
                    break
        
        # Find article dropdown and look for Agreement for Sale
        article_select = soup.select_one(self.igr_selectors['article_select'])
        if article_select:
            options = article_select.find_all('option')
            for option in options:
                text = option.get_text(strip=True).lower()
                if 'agreement' in text and 'sale' in text:
                    mumbai_options['article_id'] = option.get('value', '')
                    mumbai_options['article_name'] = option.get_text(strip=True)
                    print(f"📄 Found Agreement for Sale: ID={mumbai_options['article_id']}, Name={mumbai_options['article_name']}")
                    break
        
        return mumbai_options
    
    def mumbai_form_filling(self, soup, base_url, year=None):
        """Simplified form filling for Mumbai Agreement for Sale searches"""
        print("\n🏙️ Mumbai IGR - Agreement for Sale Search")
        print("=" * 60)
        
        # Get base form data (hidden fields, etc.)
        form_data = self.get_form_data(soup)
        
        # Find Mumbai-specific options
        mumbai_options = self.find_mumbai_options(soup)
        
        # Handle CAPTCHA
        if self.detect_igr_captcha(soup):
            captcha_url = self.get_captcha_image_url(soup, base_url)
            if captcha_url:
                print(f"\n🚨 CAPTCHA detected!")
                if self.download_and_show_captcha(captcha_url):
                    print("\n📝 Please solve the CAPTCHA:")
                    print("1. Open 'captcha_image.png' to view the CAPTCHA")
                    print("2. Enter the CAPTCHA text below")
                    
                    captcha_text = input("\nEnter CAPTCHA text: ").strip()
                    if captcha_text:
                        form_data['captchaTextBox'] = captcha_text
                        print(f"✅ CAPTCHA entered: {captcha_text}")
                    else:
                        print("❌ No CAPTCHA text provided")
                        return None
        
        # Get year input
        if not year:
            year = input(f"\nEnter year for search (e.g., 2023): ").strip()
        
        if year:
            print(f"📅 Using year: {year}")
        
        # Set Mumbai-specific form data
        if mumbai_options.get('district_id'):
            form_data['district_id'] = mumbai_options['district_id']
            print(f"✅ Set District: {mumbai_options['district_name']} (ID: {mumbai_options['district_id']})")
        
        if mumbai_options.get('taluka_id'):
            form_data['taluka_id'] = mumbai_options['taluka_id']
            print(f"✅ Set Taluka: {mumbai_options['taluka_name']} (ID: {mumbai_options['taluka_id']})")
        
        if mumbai_options.get('article_id'):
            form_data['article_id'] = mumbai_options['article_id']
            print(f"✅ Set Article: {mumbai_options['article_name']} (ID: {mumbai_options['article_id']})")
        
        # Add year to form data if there's a year field
        if year:
            # Common year field names in government forms
            possible_year_fields = ['year', 'reg_year', 'registration_year', 'yr']
            for field in possible_year_fields:
                if field in [inp.get('name', '') for inp in soup.find_all('input')] or \
                   field in [sel.get('id', '') for sel in soup.find_all('select')]:
                    form_data[field] = year
                    print(f"✅ Set {field}: {year}")
                    break
        
        # Ask for any additional required fields
        print(f"\n🔧 Additional Options:")
        
        # Database selection
        db_select = soup.select_one(self.igr_selectors['db_select'])
        if db_select:
            options = db_select.find_all('option')
            if len(options) > 1:  # More than just the default option
                print(f"\n📋 Database options available:")
                for i, option in enumerate(options[:5]):  # Show first 5
                    value = option.get('value', '')
                    text = option.get_text(strip=True)
                    print(f"   {i}: {value} - {text}")
                
                db_choice = input(f"Select database option (0-{len(options)-1}, or press Enter for default): ").strip()
                if db_choice.isdigit() and 0 <= int(db_choice) < len(options):
                    chosen_option = options[int(db_choice)]
                    form_data['dbselect'] = chosen_option.get('value', '')
                    print(f"✅ Selected database: {chosen_option.get_text(strip=True)}")
        
        # Village selection (optional for Mumbai)
        village_input = input(f"\nEnter specific village/area in Mumbai (or press Enter to skip): ").strip()
        if village_input:
            form_data['village_id'] = village_input
            print(f"✅ Set Village/Area: {village_input}")
        
        return form_data
    
    def search_mumbai_agreements(self, year=None):
        """Complete workflow for Mumbai Agreement for Sale searches"""
        igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        
        try:
            print("🏙️ Mumbai IGR - Agreement for Sale QR Code Scraper")
            print("=" * 70)
            print("Searching for: Agreement for Sale documents in Mumbai")
            if year:
                print(f"Year: {year}")
            print("=" * 70)
            
            # Step 1: Load initial page
            print(f"🌐 Loading IGR website...")
            response = self.session.get(
                igr_url,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"✅ Page loaded successfully")
            
            # Step 2: Mumbai-specific form filling
            form_data = self.mumbai_form_filling(soup, igr_url, year)
            
            if not form_data:
                print("❌ Form filling cancelled or failed")
                return []
            
            # Step 3: Submit form and scrape results
            print(f"\n🚀 Submitting Mumbai Agreement for Sale search...")
            return self.submit_form_and_scrape(igr_url, form_data)
            
        except Exception as e:
            print(f"❌ Error in Mumbai IGR workflow: {e}")
            import traceback
            traceback.print_exc()
            return []

def main():
    """Main function for Mumbai-specific IGR QR Code scraping"""
    print("🏙️ Mumbai IGR Specialized Scraper")
    print("=" * 50)
    print("Optimized for: Agreement for Sale documents in Mumbai")
    print()
    
    # Get year from user
    year = input("Enter year to search (e.g., 2023): ").strip()
    if not year:
        year = "2023"  # Default to 2023
    
    try:
        scraper = MumbaiIGRScraper()
        results = scraper.search_mumbai_agreements(year)
        
        # Display results
        print("\n" + "=" * 70)
        print("🎯 SEARCH RESULTS")
        print("=" * 70)
        
        if results:
            print(f"🎉 SUCCESS! Found {len(results)} QR code(s):")
            
            for i, result in enumerate(results, 1):
                print(f"\n📱 QR Code #{i}:")
                print(f"   🔗 Image URL: {result['image_url']}")
                print(f"   📄 QR Contents: {result['qr_contents']}")
                
                # Analyze QR content for Mumbai agreements
                for j, qr_content in enumerate(result['qr_contents']):
                    print(f"\n   📊 Agreement Analysis #{j+1}:")
                    print(f"      Content: {qr_content}")
                    print(f"      Length: {len(qr_content)} characters")
                    
                    # Check for agreement-related keywords
                    if any(word in qr_content.lower() for word in ['agreement', 'sale', 'mumbai', 'registration']):
                        print(f"      📜 Contains agreement/sale information")
                    
                    # Check for year match
                    if year in qr_content:
                        print(f"      📅 Contains specified year: {year}")
                        
        else:
            print("❌ No QR codes found for Mumbai Agreement for Sale")
            print("\n💡 Try:")
            print(f"- Different year (currently: {year})")
            print("- Specific village/area in Mumbai")
            print("- Check if agreements exist for this time period")
        
    except KeyboardInterrupt:
        print("\n\n👋 Search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 