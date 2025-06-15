#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.enhanced_qr_scraper import EnhancedQRScraper

def test_igr_with_captcha_handling():
    """Test scraping QR codes from the Maharashtra IGR website with CAPTCHA handling"""
    print("🔍 Enhanced Maharashtra IGR Website QR Code Scraper")
    print("=" * 70)
    
    # The website URL provided by user
    igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
    
    print(f"Website: {igr_url}")
    
    # Create enhanced scraper
    scraper = EnhancedQRScraper()
    
    # Ask user for custom CAPTCHA selectors
    print("\n🔧 CAPTCHA Configuration")
    print("=" * 30)
    print("If you know the CAPTCHA selector on this website, provide it below.")
    print("Examples:")
    print("- img[src*='captcha']")
    print("- .captcha-image")
    print("- #captcha_img")
    print("- input[name='captcha']")
    
    custom_selector = input("\nEnter custom CAPTCHA selector (or press Enter to skip): ").strip()
    
    if custom_selector:
        scraper.add_custom_captcha_selector(custom_selector)
        print(f"✅ Added custom CAPTCHA selector: {custom_selector}")
    
    print(f"\n🌐 Starting to scrape: {igr_url}")
    print("=" * 70)
    
    try:
        # Scrape QR codes from the webpage
        results = scraper.scrape_qr_codes_from_webpage(igr_url)
        
        print("\n" + "=" * 70)
        
        if results:
            print(f"🎉 SUCCESS! Found QR codes in {len(results)} image(s):")
            print("=" * 70)
            
            for i, result in enumerate(results, 1):
                print(f"\n📷 QR Code #{i}:")
                print(f"   Image URL: {result['image_url']}")
                print(f"   QR Content: {result['qr_contents']}")
                
                # Show additional details for each QR code
                for j, qr_content in enumerate(result['qr_contents']):
                    print(f"\n   QR Data #{j+1}:")
                    print(f"     Content: {qr_content}")
                    print(f"     Type: {'URL' if qr_content.startswith(('http://', 'https://')) else 'Text'}")
                    print(f"     Length: {len(qr_content)} characters")
                    
                    # If it looks like property data, provide more context
                    if any(keyword in qr_content.lower() for keyword in ['property', 'registration', 'document', 'igr']):
                        print(f"     🏠 Appears to be property-related data")
                
        else:
            print("❌ No QR codes found on the webpage")
            print("\n🔍 Troubleshooting suggestions:")
            print("1. The QR codes might be generated dynamically after user interaction")
            print("2. You might need to navigate to a specific property page first")
            print("3. The website might require form submission to show QR codes")
            print("4. QR codes might be in a different format or location")
            
            # Offer to try alternative approaches
            print("\n🛠️ Would you like to try:")
            print("1. Access a specific property page URL")
            print("2. Use multi-step navigation")
            print("3. Manual browser session (open in browser first)")
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        print(f"\nDetailed error:\n{traceback.format_exc()}")

def test_specific_property_page():
    """Allow testing of a specific property page if user has one"""
    print("\n🏠 Test Specific Property Page")
    print("=" * 40)
    
    specific_url = input("Enter a specific property page URL (or press Enter to skip): ").strip()
    
    if specific_url:
        print(f"\n🔍 Testing specific page: {specific_url}")
        
        scraper = EnhancedQRScraper()
        results = scraper.scrape_qr_codes_from_webpage(specific_url)
        
        if results:
            print(f"✅ Found QR codes in {len(results)} image(s) on the specific page!")
            for i, result in enumerate(results, 1):
                print(f"\nQR Code #{i}: {result['qr_contents']}")
        else:
            print("❌ No QR codes found on the specific page")

def main():
    """Main function to run the enhanced test"""
    try:
        test_igr_with_captcha_handling()
        test_specific_property_page()
        
        print("\n" + "=" * 70)
        print("✅ Enhanced testing completed!")
        print("\n💡 Tips for government websites:")
        print("- Many require user interaction before showing QR codes")
        print("- Property QR codes often appear only after searching")
        print("- Some websites generate QR codes client-side with JavaScript")
        print("- Consider using browser automation (Selenium) for complex workflows")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    main() 