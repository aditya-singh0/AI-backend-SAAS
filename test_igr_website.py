#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.qr_scraper import QRScraper

def test_igr_website():
    """Test scraping QR codes from the Maharashtra IGR website"""
    print("🔍 Testing Maharashtra IGR Website for QR Codes")
    print("=" * 60)
    
    # The website URL provided by user
    igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
    
    print(f"Website: {igr_url}")
    print("Searching for QR codes on the webpage...")
    
    scraper = QRScraper()
    
    try:
        # Scrape QR codes from the webpage
        results = scraper.scrape_qr_codes_from_webpage(igr_url)
        
        if results:
            print(f"\n✅ SUCCESS! Found QR codes in {len(results)} image(s):")
            print("=" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"\n📷 Image {i}:")
                print(f"   URL: {result['image_url']}")
                print(f"   QR Content: {result['qr_contents']}")
                
                # If it's a single QR code, show more details
                if len(result['qr_contents']) == 1:
                    qr_content = result['qr_contents'][0]
                    print(f"   Content Type: {'URL' if qr_content.startswith(('http://', 'https://')) else 'Text'}")
                    print(f"   Length: {len(qr_content)} characters")
                
        else:
            print("\n❌ No QR codes found on the webpage")
            print("\nThis could mean:")
            print("- The website doesn't contain any QR codes")
            print("- QR codes are loaded dynamically with JavaScript")
            print("- QR codes are embedded in a way that's not easily detectable")
            print("- The images are in formats that aren't supported")
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\nPossible reasons:")
        print("- Network connectivity issues")
        print("- Website requires authentication")
        print("- Website blocks automated requests")
        print("- CAPTCHA or other anti-bot measures")
        
        import traceback
        print(f"\nDetailed error:\n{traceback.format_exc()}")

def main():
    """Main function to run the test"""
    test_igr_website()
    
    print("\n" + "=" * 60)
    print("💡 Tips:")
    print("1. If no QR codes were found, try accessing the website manually")
    print("2. Some government websites use dynamic content loading")
    print("3. You might need to navigate to specific property pages")
    print("4. QR codes might be generated after form submission")

if __name__ == "__main__":
    main() 