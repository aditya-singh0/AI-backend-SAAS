#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper
from bs4 import BeautifulSoup

def final_mumbai_qr_search():
    """Final Mumbai QR search using exact Marathi terms from the website"""
    print("🏙️ Mumbai IGR - Agreement for Sale QR Scraper (Final Version)")
    print("=" * 70)
    print("Using exact terms: मुंबई district/taluka, अॅग्रीमेंट टू सेल article")
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
        
        # Get form data (including CSRF token and hidden fields)
        form_data = scraper.get_form_data(soup)
        
        # Handle CAPTCHA
        if scraper.detect_igr_captcha(soup):
            captcha_url = scraper.get_captcha_image_url(soup, igr_url)
            if captcha_url:
                print(f"\n🚨 CAPTCHA detected!")
                if scraper.download_and_show_captcha(captcha_url):
                    print("\n📝 Please solve the CAPTCHA:")
                    print("1. Open 'captcha_image.png' to view the CAPTCHA")
                    print("2. Enter the CAPTCHA text below")
                    print("   (From screenshot, it looks like: hwQdfL)")
                    
                    captcha_text = input("\nEnter CAPTCHA text: ").strip()
                    if captcha_text:
                        form_data['captchaTextBox'] = captcha_text
                        print(f"✅ CAPTCHA entered: {captcha_text}")
                    else:
                        print("❌ No CAPTCHA text provided")
                        return
        
        # Get year
        year = input("\nEnter year to search (e.g., 2023, 2024): ").strip()
        if not year:
            year = "2024"  # Default from screenshot
        
        print(f"\n🔍 Setting up form with exact Marathi terms...")
        
        # Find Mumbai District (मुंबई)
        district_select = soup.select_one('select#district_id')
        if district_select:
            district_options = district_select.find_all('option')
            mumbai_district = None
            
            for option in district_options:
                text = option.get_text(strip=True)
                if 'मुंबई' in text:  # Exact Marathi term
                    mumbai_district = option
                    break
            
            if mumbai_district:
                form_data['district_id'] = mumbai_district.get('value', '')
                print(f"✅ Found मुंबई District: {mumbai_district.get_text(strip=True)} (ID: {mumbai_district.get('value', '')})")
            else:
                print("❌ मुंबई district not found")
                # Show all options for manual selection
                print("\n📋 Available Districts:")
                for i, option in enumerate(district_options[:20]):
                    print(f"   {i}: {option.get('value', '')} - {option.get_text(strip=True)}")
                
                choice = input(f"\nEnter district number (0-{len(district_options)-1}): ").strip()
                if choice.isdigit() and 0 <= int(choice) < len(district_options):
                    chosen_district = district_options[int(choice)]
                    form_data['district_id'] = chosen_district.get('value', '')
                    print(f"✅ Selected: {chosen_district.get_text(strip=True)}")
        
        # Find Mumbai Taluka (मुंबई) 
        taluka_select = soup.select_one('select#taluka_id')
        if taluka_select:
            taluka_options = taluka_select.find_all('option')
            mumbai_taluka = None
            
            for option in taluka_options:
                text = option.get_text(strip=True)
                if 'मुंबई' in text:  # Exact Marathi term
                    mumbai_taluka = option
                    break
            
            if mumbai_taluka:
                form_data['taluka_id'] = mumbai_taluka.get('value', '')
                print(f"✅ Found मुंबई Taluka: {mumbai_taluka.get_text(strip=True)} (ID: {mumbai_taluka.get('value', '')})")
        
        # Find Agreement for Sale Article (अॅग्रीमेंट टू सेल)
        article_select = soup.select_one('select#article_id')
        if article_select:
            article_options = article_select.find_all('option')
            agreement_article = None
            
            # Look for exact Marathi term or English variants
            search_terms = ['अॅग्रीमेंट टू सेल', 'agreement', 'sale']
            
            for option in article_options:
                text = option.get_text(strip=True).lower()
                for term in search_terms:
                    if term.lower() in text:
                        agreement_article = option
                        break
                if agreement_article:
                    break
            
            if agreement_article:
                form_data['article_id'] = agreement_article.get('value', '')
                print(f"✅ Found Agreement Article: {agreement_article.get_text(strip=True)} (ID: {agreement_article.get('value', '')})")
            else:
                print("❌ Agreement for Sale article not found")
                # Show article options for manual selection
                print("\n📋 Available Articles (first 20):")
                for i, option in enumerate(article_options[:20]):
                    print(f"   {i}: {option.get('value', '')} - {option.get_text(strip=True)}")
                
                choice = input(f"\nEnter article number (0-{len(article_options)-1}): ").strip()
                if choice.isdigit() and 0 <= int(choice) < len(article_options):
                    chosen_article = article_options[int(choice)]
                    form_data['article_id'] = chosen_article.get('value', '')
                    print(f"✅ Selected: {chosen_article.get_text(strip=True)}")
        
        # Set Year (both Select Year dropdown and Doc Year field are same)
        db_select = soup.select_one('select#dbselect')
        if db_select:
            db_options = db_select.find_all('option')
            year_option = None
            
            for option in db_options:
                if year in option.get_text():
                    year_option = option
                    break
            
            if year_option:
                form_data['dbselect'] = year_option.get('value', '')
                print(f"✅ Found year {year}: {year_option.get_text(strip=True)} (ID: {year_option.get('value', '')})")
                
                # Also set the doc year field if it exists
                form_data['yearsel'] = year
                print(f"✅ Set doc year field: {year}")
        
        # Optional Village/Area
        village_input = input(f"\nEnter specific village/area in Mumbai (or press Enter to skip): ").strip()
        if village_input:
            form_data['village_id'] = village_input
        
        # Display final form data for confirmation
        print(f"\n📋 Final Form Data for Submission:")
        for key, value in form_data.items():
            if key != '_csrfToken' and value:  # Skip CSRF token and empty values
                print(f"   {key}: {value}")
        
        # Confirm submission
        proceed = input(f"\nSubmit search for Mumbai Agreement for Sale QR codes? (y/n): ").strip().lower()
        
        if proceed == 'y':
            print(f"\n🚀 Submitting Mumbai Agreement for Sale search...")
            results = scraper.submit_form_and_scrape(igr_url, form_data)
            
            # Display results
            print("\n" + "=" * 70)
            print("🎯 MUMBAI AGREEMENT FOR SALE QR CODE RESULTS")
            print("=" * 70)
            
            if results:
                print(f"🎉 SUCCESS! Found {len(results)} QR code(s):")
                
                for i, result in enumerate(results, 1):
                    print(f"\n📱 QR Code #{i}:")
                    print(f"   🔗 Image URL: {result['image_url']}")
                    print(f"   📄 QR Contents: {result['qr_contents']}")
                    
                    for j, qr_content in enumerate(result['qr_contents']):
                        print(f"\n   📊 Mumbai Agreement Analysis #{j+1}:")
                        print(f"      Content: {qr_content}")
                        print(f"      Length: {len(qr_content)} characters")
                        print(f"      Type: {'URL' if qr_content.startswith(('http://', 'https://')) else 'Text/Data'}")
                        
                        # Check for Mumbai-specific keywords
                        mumbai_keywords = ['mumbai', 'मुंबई', 'agreement', 'sale', 'registration', 'property']
                        found_keywords = [kw for kw in mumbai_keywords if kw.lower() in qr_content.lower()]
                        if found_keywords:
                            print(f"      🏙️ Contains Mumbai/Agreement keywords: {found_keywords}")
                        
                        # Check for year
                        if year in qr_content:
                            print(f"      📅 Contains year: {year}")
                        
                        # Check if it's a property registration
                        if any(term in qr_content.lower() for term in ['reg', 'registration', 'property', 'document']):
                            print(f"      📜 Appears to be property registration data")
                            
            else:
                print("❌ No QR codes found for Mumbai Agreement for Sale")
                print(f"\n💡 This might mean:")
                print("- No Agreement for Sale documents found for the specified criteria")
                print("- The search parameters need adjustment")
                print("- QR codes might be on a different page after successful search")
                print(f"- Try different year (currently: {year})")
                print("- Try with specific village/area details")
        else:
            print("Search cancelled by user")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_mumbai_qr_search() 