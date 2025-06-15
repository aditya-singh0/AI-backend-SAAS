#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper

def main():
    """Main function to run the specialized IGR QR Code scraper"""
    print("🏛️ Maharashtra IGR Specialized QR Code Scraper")
    print("=" * 70)
    print("This scraper is specifically designed for the Maharashtra IGR website")
    print("with the following capabilities:")
    print("✅ CAPTCHA detection and handling (img#captcha-img)")
    print("✅ Form field interaction (district, taluka, village, article, db)")
    print("✅ Interactive CAPTCHA solving")
    print("✅ QR code extraction from results")
    print("=" * 70)
    
    # The IGR website URL
    igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
    
    try:
        # Create the specialized scraper
        scraper = IGRSpecializedScraper()
        
        print("\n🚀 Starting IGR workflow...")
        print("📋 The scraper will:")
        print("1. Load the IGR website")
        print("2. Detect and download CAPTCHA image")
        print("3. Allow you to solve the CAPTCHA")
        print("4. Let you fill in location/property details")
        print("5. Submit the form")
        print("6. Scan the results for QR codes")
        
        # Run the complete workflow
        results = scraper.full_igr_workflow(igr_url)
        
        # Display results
        print("\n" + "=" * 70)
        print("🎯 FINAL RESULTS")
        print("=" * 70)
        
        if results:
            print(f"🎉 SUCCESS! Found {len(results)} QR code(s):")
            
            for i, result in enumerate(results, 1):
                print(f"\n📱 QR Code #{i}:")
                print(f"   🔗 Image URL: {result['image_url']}")
                print(f"   📄 QR Contents: {result['qr_contents']}")
                
                # Analyze QR content
                for j, qr_content in enumerate(result['qr_contents']):
                    print(f"\n   📊 QR Data Analysis #{j+1}:")
                    print(f"      Content: {qr_content}")
                    print(f"      Length: {len(qr_content)} characters")
                    print(f"      Type: {'URL' if qr_content.startswith(('http://', 'https://')) else 'Text/Data'}")
                    
                    # Check for property-related keywords
                    property_keywords = ['property', 'registration', 'document', 'igr', 'survey', 'plot', 'land']
                    if any(keyword.lower() in qr_content.lower() for keyword in property_keywords):
                        print(f"      🏠 Contains property-related information")
                    
                    # Check for document/certificate keywords
                    doc_keywords = ['certificate', 'registration', 'deed', 'document']
                    if any(keyword.lower() in qr_content.lower() for keyword in doc_keywords):
                        print(f"      📜 Appears to be a document/certificate reference")
                        
        else:
            print("❌ No QR codes were found")
            print("\n🔍 Possible reasons:")
            print("- QR codes may only appear for specific property searches")
            print("- The search criteria may need to be more specific") 
            print("- QR codes might be generated after additional steps")
            print("- The website structure may have changed")
            
            print("\n💡 Suggestions:")
            print("1. Try with specific property details if you have them")
            print("2. Navigate to a known property page directly")
            print("3. Check if there are additional steps after form submission")
        
        # Cleanup
        if os.path.exists('captcha_image.png'):
            print(f"\n🗑️  CAPTCHA image saved as 'captcha_image.png' for reference")
            
    except KeyboardInterrupt:
        print("\n\n👋 Scraping interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n" + "=" * 70)
        print("✅ IGR QR Code Scraping Session Complete")
        print("\n📚 Usage Summary:")
        print("- This scraper handles the specific IGR website form structure")
        print("- CAPTCHA images are downloaded for manual solving")
        print("- Form fields can be filled interactively")
        print("- QR codes are automatically detected and decoded")
        print("- Results are analyzed for property-related content")

if __name__ == "__main__":
    main() 