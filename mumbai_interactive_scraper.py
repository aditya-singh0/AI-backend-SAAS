#!/usr/bin/env python3

import sys
import os
import time
import json

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from captcha_helper_scraper import CAPTCHAHelperScraper
from bs4 import BeautifulSoup

class MumbaiInteractiveScraper(CAPTCHAHelperScraper):
    def __init__(self, year="2024", proxy_manager=None):
        super().__init__(proxy_manager)
        self.year = year
        
    def get_dropdown_options(self, soup, select_id):
        """Get all options from a dropdown"""
        options = []
        select_elem = soup.select_one(f'select#{select_id}')
        if select_elem:
            for option in select_elem.find_all('option'):
                value = option.get('value', '')
                text = option.get_text(strip=True)
                if value:  # Skip empty values
                    options.append({'value': value, 'text': text})
        return options
    
    def display_options(self, options, title):
        """Display options for user selection"""
        print(f"\n📋 {title}:")
        for i, opt in enumerate(options):
            print(f"   {i}: [{opt['value']}] {opt['text']}")
        return options
    
    def load_dependent_dropdowns(self, soup, base_url, form_data, district_id):
        """Load taluka options after selecting district"""
        print(f"\n🔄 Loading talukas for selected district...")
        
        # Add district to form data
        form_data['district_id'] = district_id
        
        # Submit form to get updated dropdowns
        response = self.session.post(
            base_url,
            data=form_data,
            headers=self.headers,
            verify=False,
            timeout=30
        )
        
        return BeautifulSoup(response.text, 'html.parser')
    
    def interactive_mumbai_search(self):
        """Interactive Mumbai search with step-by-step form filling"""
        print("🏙️ Mumbai IGR Interactive Scraper")
        print("=" * 70)
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
            
            # Step 1: Select District
            print("\n" + "="*50)
            print("STEP 1: SELECT DISTRICT")
            print("="*50)
            
            district_options = self.get_dropdown_options(soup, 'district_id')
            
            # Find Mumbai
            mumbai_idx = None
            for i, opt in enumerate(district_options):
                if 'मुंबई' in opt['text'] or 'mumbai' in opt['text'].lower():
                    mumbai_idx = i
                    print(f"✅ Found Mumbai at index {i}: {opt['text']}")
                    break
                    
            if mumbai_idx is None:
                # Show all options
                self.display_options(district_options[:10], "District options (first 10)")
                district_idx = input(f"\nSelect district (0-{len(district_options)-1}): ").strip()
                district_idx = int(district_idx) if district_idx.isdigit() else 0
            else:
                district_idx = mumbai_idx
                print(f"🏙️ Auto-selecting Mumbai")
                
            selected_district = district_options[district_idx]
            form_data['district_id'] = selected_district['value']
            print(f"✅ Selected: {selected_district['text']} (value={selected_district['value']})")
            
            # Load taluka options
            soup = self.load_dependent_dropdowns(soup, igr_url, form_data, selected_district['value'])
            
            # Step 2: Select Taluka
            print("\n" + "="*50)
            print("STEP 2: SELECT TALUKA")
            print("="*50)
            
            taluka_options = self.get_dropdown_options(soup, 'taluka_id')
            if taluka_options:
                self.display_options(taluka_options[:10], "Taluka options")
                taluka_idx = input(f"\nSelect taluka (0-{len(taluka_options)-1}), or Enter to skip: ").strip()
                if taluka_idx.isdigit():
                    selected_taluka = taluka_options[int(taluka_idx)]
                    form_data['taluka_id'] = selected_taluka['value']
                    print(f"✅ Selected: {selected_taluka['text']}")
            
            # Step 3: Select Article Type
            print("\n" + "="*50)
            print("STEP 3: SELECT ARTICLE TYPE")
            print("="*50)
            
            article_options = self.get_dropdown_options(soup, 'article_id')
            
            # Find Agreement for Sale
            agreement_idx = None
            for i, opt in enumerate(article_options):
                text_lower = opt['text'].lower()
                # Check for various spellings/formats
                if ('agreement' in text_lower and 'sale' in text_lower) or \
                   ('अॅग्रीमेंट' in opt['text'] and 'सेल' in opt['text']) or \
                   ('एग्रीमेंट' in opt['text']):
                    agreement_idx = i
                    print(f"✅ Found Agreement type at index {i}: {opt['text']}")
                    
            if agreement_idx is None:
                # Show relevant options
                print("\n🔍 Showing article options containing 'agreement' or similar:")
                relevant = []
                for i, opt in enumerate(article_options):
                    if any(word in opt['text'].lower() for word in ['agree', 'sale', 'अॅग्री', 'एग्री']):
                        print(f"   {i}: {opt['text']}")
                        relevant.append(i)
                        
                if not relevant:
                    self.display_options(article_options[:20], "First 20 article options")
                    
                article_idx = input(f"\nSelect article type (0-{len(article_options)-1}): ").strip()
                article_idx = int(article_idx) if article_idx.isdigit() else 0
            else:
                article_idx = agreement_idx
                print(f"📄 Auto-selecting Agreement for Sale")
                
            selected_article = article_options[article_idx]
            form_data['article_id'] = selected_article['value']
            print(f"✅ Selected: {selected_article['text']} (value={selected_article['value']})")
            
            # Step 4: Select Year
            print("\n" + "="*50)
            print("STEP 4: SELECT YEAR")
            print("="*50)
            
            year_options = self.get_dropdown_options(soup, 'dbselect')
            
            # Find specified year
            year_idx = None
            for i, opt in enumerate(year_options):
                if str(self.year) in opt['text']:
                    year_idx = i
                    break
                    
            if year_idx is not None:
                form_data['dbselect'] = year_options[year_idx]['value']
                print(f"✅ Selected year: {year_options[year_idx]['text']}")
            else:
                self.display_options(year_options[:10], "Year options")
                year_idx = input(f"\nSelect year (0-{len(year_options)-1}): ").strip()
                if year_idx.isdigit():
                    selected_year = year_options[int(year_idx)]
                    form_data['dbselect'] = selected_year['value']
                    print(f"✅ Selected: {selected_year['text']}")
            
            # Step 5: Submit form
            print("\n" + "="*50)
            print("STEP 5: SUBMIT SEARCH")
            print("="*50)
            
            print("\n📋 Final form data:")
            for key, value in form_data.items():
                if value and key not in ['_csrfToken']:
                    print(f"   {key}: {value}")
                    
            print(f"\n🚀 Submitting search form...")
            
            response = self.session.post(
                igr_url,
                data=form_data,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if CAPTCHA is required
            if self.detect_igr_captcha(soup):
                print(f"\n🚨 CAPTCHA detected! Starting enhanced CAPTCHA handler...")
                
                # Update form data with new CSRF token
                new_form_data = self.get_form_data(soup)
                form_data['_csrfToken'] = new_form_data.get('_csrfToken', form_data.get('_csrfToken'))
                
                # Handle CAPTCHA
                captcha_success = self.enhanced_captcha_handling(soup, igr_url, form_data)
                
                if captcha_success:
                    print(f"\n✅ CAPTCHA solved successfully!")
                    # Results should be in the current soup after successful CAPTCHA
            
            # Check for results
            print(f"\n🔍 Searching for QR codes...")
            results = self.scrape_qr_codes_from_soup(soup, igr_url)
            
            if results:
                print(f"\n🎉 Found {len(results)} QR codes!")
                for i, result in enumerate(results, 1):
                    print(f"\n📱 QR Code #{i}:")
                    print(f"   🔗 Image URL: {result['image_url']}")
                    for j, content in enumerate(result['qr_contents']):
                        print(f"   📄 Content #{j+1}: {content}")
                        
                # Save results
                with open('mumbai_qr_results.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Results saved to mumbai_qr_results.json")
            else:
                print(f"\n❌ No QR codes found")
                
                # Check for error messages
                error_msgs = soup.find_all(text=lambda text: text and any(word in text.lower() for word in ['error', 'no record', 'not found']))
                if error_msgs:
                    print("\n⚠️ Possible error messages found:")
                    for msg in error_msgs[:3]:
                        print(f"   - {msg.strip()}")
                        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    print(f"🚀 Starting Mumbai Interactive Scraper")
    
    scraper = MumbaiInteractiveScraper(year=year)
    scraper.interactive_mumbai_search()

if __name__ == "__main__":
    main() 