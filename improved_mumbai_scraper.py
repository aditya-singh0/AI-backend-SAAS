#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper
from bs4 import BeautifulSoup

def find_option_by_text(options, search_terms):
    """Find option that contains any of the search terms"""
    for option in options:
        text = option.get_text(strip=True).lower()
        for term in search_terms:
            if term.lower() in text:
                return option
    return None

def display_options(options, title, max_display=20):
    """Display dropdown options in a formatted way"""
    print(f"\n📋 {title}:")
    for i, option in enumerate(options[:max_display]):
        value = option.get('value', '')
        text = option.get_text(strip=True)
        print(f"   {i}: {value} - {text}")
    
    if len(options) > max_display:
        print(f"   ... and {len(options) - max_display} more options")

def interactive_mumbai_search():
    """Interactive Mumbai IGR search with better option handling"""
    print("🏙️ Interactive Mumbai IGR - Agreement for Sale Search")
    print("=" * 70)
    
    scraper = IGRSpecializedScraper()
    igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
    
    try:
        # Load the page
        print("🌐 Loading IGR website...")
        response = scraper.session.get(
            igr_url,
            headers=scraper.headers,
            verify=False,
            timeout=30
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("✅ Page loaded successfully")
        
        # Get form data
        form_data = scraper.get_form_data(soup)
        
        # Handle CAPTCHA first
        if scraper.detect_igr_captcha(soup):
            captcha_url = scraper.get_captcha_image_url(soup, igr_url)
            if captcha_url:
                print(f"\n🚨 CAPTCHA detected!")
                if scraper.download_and_show_captcha(captcha_url):
                    print("\n📝 Please solve the CAPTCHA:")
                    print("1. Open 'captcha_image.png' to view the CAPTCHA")
                    print("2. Enter the CAPTCHA text below")
                    
                    captcha_text = input("\nEnter CAPTCHA text: ").strip()
                    if captcha_text:
                        form_data['captchaTextBox'] = captcha_text
                        print(f"✅ CAPTCHA entered: {captcha_text}")
                    else:
                        print("❌ No CAPTCHA text provided")
                        return
        
        # Get year
        year = input("\nEnter year to search (e.g., 2023): ").strip()
        if not year:
            year = "2023"
        
        # Find and select district (Mumbai)
        print(f"\n🔍 Searching for Mumbai district...")
        district_select = soup.select_one('select#district_id')
        if district_select:
            district_options = district_select.find_all('option')
            
            # Search for Mumbai variants
            mumbai_terms = ['mumbai', 'मुंबई', 'bombay', 'city']
            mumbai_district = find_option_by_text(district_options, mumbai_terms)
            
            if mumbai_district:
                form_data['district_id'] = mumbai_district.get('value', '')
                print(f"✅ Found Mumbai District: {mumbai_district.get_text(strip=True)} (ID: {mumbai_district.get('value', '')})")
            else:
                print("❌ Mumbai district not found automatically")
                display_options(district_options, "Available Districts")
                district_choice = input(f"\nEnter district number (0-{len(district_options)-1}): ").strip()
                if district_choice.isdigit() and 0 <= int(district_choice) < len(district_options):
                    chosen_district = district_options[int(district_choice)]
                    form_data['district_id'] = chosen_district.get('value', '')
                    print(f"✅ Selected: {chosen_district.get_text(strip=True)}")
        
        # Find and select article (Agreement for Sale)
        print(f"\n🔍 Searching for Agreement for Sale...")
        article_select = soup.select_one('select#article_id')
        if article_select:
            article_options = article_select.find_all('option')
            
            # Search for Agreement for Sale variants
            agreement_terms = ['agreement', 'sale', 'करार', 'विक्री', 'विक्रय']
            agreement_article = find_option_by_text(article_options, agreement_terms)
            
            if agreement_article:
                form_data['article_id'] = agreement_article.get('value', '')
                print(f"✅ Found Agreement for Sale: {agreement_article.get_text(strip=True)} (ID: {agreement_article.get('value', '')})")
            else:
                print("❌ Agreement for Sale not found automatically")
                display_options(article_options, "Available Articles")
                article_choice = input(f"\nEnter article number (0-{len(article_options)-1}): ").strip()
                if article_choice.isdigit() and 0 <= int(article_choice) < len(article_options):
                    chosen_article = article_options[int(article_choice)]
                    form_data['article_id'] = chosen_article.get('value', '')
                    print(f"✅ Selected: {chosen_article.get_text(strip=True)}")
        
        # Select year from database
        print(f"\n📅 Setting up year selection...")
        db_select = soup.select_one('select#dbselect')
        if db_select:
            db_options = db_select.find_all('option')
            
            # Find year option
            year_option = None
            for option in db_options:
                if year in option.get_text():
                    year_option = option
                    break
            
            if year_option:
                form_data['dbselect'] = year_option.get('value', '')
                print(f"✅ Found year {year}: {year_option.get_text(strip=True)} (ID: {year_option.get('value', '')})")
            else:
                display_options(db_options, f"Available Years")
                year_choice = input(f"\nEnter year option number (0-{len(db_options)-1}): ").strip()
                if year_choice.isdigit() and 0 <= int(year_choice) < len(db_options):
                    chosen_year = db_options[int(year_choice)]
                    form_data['dbselect'] = chosen_year.get('value', '')
                    print(f"✅ Selected: {chosen_year.get_text(strip=True)}")
        
        # Optional: Taluka and Village
        taluka_input = input(f"\nEnter Mumbai taluka ID (or press Enter to skip): ").strip()
        if taluka_input:
            form_data['taluka_id'] = taluka_input
        
        village_input = input(f"Enter Mumbai village/area ID (or press Enter to skip): ").strip()
        if village_input:
            form_data['village_id'] = village_input
        
        # Display final form data
        print(f"\n📋 Final Form Data:")
        for key, value in form_data.items():
            if key not in ['_csrfToken'] and value:  # Skip empty values and token
                print(f"   {key}: {value}")
        
        # Ask for confirmation
        proceed = input(f"\nProceed with search? (y/n): ").strip().lower()
        if proceed == 'y':
            print(f"\n🚀 Submitting search...")
            results = scraper.submit_form_and_scrape(igr_url, form_data)
            
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
                    
                    for j, qr_content in enumerate(result['qr_contents']):
                        print(f"\n   📊 QR Analysis #{j+1}:")
                        print(f"      Content: {qr_content}")
                        print(f"      Length: {len(qr_content)} characters")
                        
                        if any(word in qr_content.lower() for word in ['agreement', 'sale', 'mumbai', 'registration']):
                            print(f"      📜 Contains agreement/sale information")
                        
                        if year in qr_content:
                            print(f"      📅 Contains year: {year}")
            else:
                print("❌ No QR codes found")
                print(f"\n💡 This might mean:")
                print("- No Agreement for Sale documents for the specified criteria")
                print("- Wrong field selections")
                print("- Server error due to missing required fields")
                print("- Need to try different search parameters")
        else:
            print("Search cancelled")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    interactive_mumbai_search() 