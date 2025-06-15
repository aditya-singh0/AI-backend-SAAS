#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper
from bs4 import BeautifulSoup

def andheri_mumbai_qr_search():
    """Andheri Mumbai specific QR search"""
    print("🏙️ Mumbai IGR - Andheri Agreement for Sale QR Scraper")
    print("=" * 70)
    print("Search Parameters:")
    print("📍 District: मुंबई (Mumbai)")
    print("📍 Taluka: मुंबई (Mumbai)")  
    print("📍 Area: अंधेरी (Andheri)")
    print("📄 Article: Agreement for Sale")
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
        
        # Handle CAPTCHA
        if scraper.detect_igr_captcha(soup):
            captcha_url = scraper.get_captcha_image_url(soup, igr_url)
            if captcha_url:
                print(f"\n🚨 CAPTCHA detected!")
                if scraper.download_and_show_captcha(captcha_url):
                    print("\n📝 CAPTCHA image saved as 'captcha_image.png'")
                    print("Enter the CAPTCHA text you see in the image:")
                    
                    captcha_text = input("CAPTCHA: ").strip()
                    if captcha_text:
                        form_data['captchaTextBox'] = captcha_text
                        print(f"✅ CAPTCHA entered: {captcha_text}")
                    else:
                        print("❌ No CAPTCHA provided")
                        return
        
        # Get year
        year = input("\nEnter year (e.g., 2023, 2024): ").strip()
        if not year:
            year = "2024"
        
        print(f"\n🔍 Setting up Andheri Mumbai search...")
        
        # Search for Mumbai District (मुंबई)
        district_select = soup.select_one('select#district_id')
        mumbai_found = False
        if district_select:
            district_options = district_select.find_all('option')
            
            for option in district_options:
                text = option.get_text(strip=True)
                if 'मुंबई' in text:
                    form_data['district_id'] = option.get('value', '')
                    print(f"✅ Found मुंबई District: {text} (ID: {option.get('value', '')})")
                    mumbai_found = True
                    break
            
            if not mumbai_found:
                print("❌ मुंबई district not found automatically")
                print("\n📋 Available Districts:")
                for i, option in enumerate(district_options):
                    if i >= 20:  # Show first 20
                        break
                    print(f"   {i}: {option.get('value', '')} - {option.get_text(strip=True)}")
                
                choice = input(f"\nSelect Mumbai district number: ").strip()
                if choice.isdigit() and 0 <= int(choice) < len(district_options):
                    chosen = district_options[int(choice)]
                    form_data['district_id'] = chosen.get('value', '')
                    print(f"✅ Selected: {chosen.get_text(strip=True)}")
        
        # Search for Mumbai Taluka (मुंबई)
        taluka_select = soup.select_one('select#taluka_id')
        if taluka_select:
            taluka_options = taluka_select.find_all('option')
            for option in taluka_options:
                text = option.get_text(strip=True)
                if 'मुंबई' in text:
                    form_data['taluka_id'] = option.get('value', '')
                    print(f"✅ Found मुंबई Taluka: {text} (ID: {option.get('value', '')})")
                    break
        
        # Search for Andheri Village (अंधेरी)
        village_select = soup.select_one('select#village_id')
        andheri_found = False
        if village_select:
            village_options = village_select.find_all('option')
            
            # Try to find Andheri in various forms
            andheri_terms = ['अंधेरी', 'andheri']
            
            for option in village_options:
                text = option.get_text(strip=True).lower()
                for term in andheri_terms:
                    if term.lower() in text:
                        form_data['village_id'] = option.get('value', '')
                        print(f"✅ Found Andheri: {option.get_text(strip=True)} (ID: {option.get('value', '')})")
                        andheri_found = True
                        break
                if andheri_found:
                    break
            
            if not andheri_found:
                print("❌ अंधेरी (Andheri) not found in village options")
                # Try manual entry
                andheri_manual = input("Enter Andheri village ID manually (or press Enter to skip): ").strip()
                if andheri_manual:
                    form_data['village_id'] = andheri_manual
                    print(f"✅ Manual Andheri ID: {andheri_manual}")
        
        # Search for Agreement for Sale Article
        article_select = soup.select_one('select#article_id')
        agreement_found = False
        if article_select:
            article_options = article_select.find_all('option')
            
            # Search terms for Agreement for Sale
            agreement_terms = ['अॅग्रीमेंट टू सेल', 'agreement', 'sale', 'करार']
            
            for option in article_options:
                text = option.get_text(strip=True).lower()
                for term in agreement_terms:
                    if term.lower() in text:
                        form_data['article_id'] = option.get('value', '')
                        print(f"✅ Found Agreement Article: {option.get_text(strip=True)} (ID: {option.get('value', '')})")
                        agreement_found = True
                        break
                if agreement_found:
                    break
            
            if not agreement_found:
                print("❌ Agreement for Sale not found automatically")
                print("Showing some article options:")
                for i, option in enumerate(article_options[:10]):
                    print(f"   {i}: {option.get('value', '')} - {option.get_text(strip=True)}")
                
                choice = input("Select agreement article number (or 92 if that's the correct one): ").strip()
                if choice.isdigit() and 0 <= int(choice) < len(article_options):
                    chosen = article_options[int(choice)]
                    form_data['article_id'] = chosen.get('value', '')
                    print(f"✅ Selected: {chosen.get_text(strip=True)}")
        
        # Set Year
        db_select = soup.select_one('select#dbselect')
        if db_select:
            db_options = db_select.find_all('option')
            year_found = False
            
            for option in db_options:
                if year in option.get_text():
                    form_data['dbselect'] = option.get('value', '')
                    print(f"✅ Found year {year}: {option.get_text(strip=True)} (ID: {option.get('value', '')})")
                    year_found = True
                    break
            
            if year_found:
                form_data['yearsel'] = year  # Also set doc year field
                print(f"✅ Set document year: {year}")
        
        # Display final form data
        print(f"\n📋 Andheri Mumbai Search Parameters:")
        for key, value in form_data.items():
            if key != '_csrfToken' and value:
                print(f"   {key}: {value}")
        
        # Confirm submission
        proceed = input(f"\n🚀 Submit Andheri Mumbai Agreement for Sale search? (y/n): ").strip().lower()
        
        if proceed == 'y':
            print(f"\n🏙️ Submitting Andheri Mumbai search...")
            results = scraper.submit_form_and_scrape(igr_url, form_data)
            
            # Display results
            print("\n" + "=" * 70)
            print("🎯 ANDHERI MUMBAI AGREEMENT FOR SALE QR RESULTS")
            print("=" * 70)
            
            if results:
                print(f"🎉 SUCCESS! Found {len(results)} QR code(s) for Andheri agreements:")
                
                for i, result in enumerate(results, 1):
                    print(f"\n📱 QR Code #{i}:")
                    print(f"   🔗 Image URL: {result['image_url']}")
                    print(f"   📄 QR Contents: {result['qr_contents']}")
                    
                    for j, qr_content in enumerate(result['qr_contents']):
                        print(f"\n   📊 Andheri Agreement Analysis #{j+1}:")
                        print(f"      Content: {qr_content}")
                        print(f"      Length: {len(qr_content)} characters")
                        
                        # Check for Andheri and Mumbai specific terms
                        andheri_keywords = ['andheri', 'अंधेरी', 'mumbai', 'मुंबई', 'agreement', 'sale']
                        found_keywords = [kw for kw in andheri_keywords if kw.lower() in qr_content.lower()]
                        if found_keywords:
                            print(f"      🏙️ Contains Andheri/Mumbai keywords: {found_keywords}")
                        
                        if year in qr_content:
                            print(f"      📅 Contains year: {year}")
                        
                        if any(term in qr_content.lower() for term in ['property', 'registration', 'document']):
                            print(f"      📜 Property registration document")
                            
            else:
                print("❌ No QR codes found for Andheri Mumbai Agreement for Sale")
                print(f"\n💡 Suggestions:")
                print("- Try different year")
                print("- Check if Andheri documents exist for this period")
                print("- Verify article selection (maybe try option 92)")
                print("- Try without village specification")
        else:
            print("Search cancelled")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    andheri_mumbai_qr_search() 