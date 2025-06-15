#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.qr_scraper import QRScraper

def demo_single_qr_image():
    """Demonstrate extracting QR code from a single image"""
    print("🔍 Demo 1: Single QR Code Image")
    print("=" * 50)
    
    scraper = QRScraper()
    
    # Use QR Server API to generate a test QR code
    test_urls = [
        "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=Hello%20World",
        "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://www.example.com",
        "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=This%20is%20a%20test%20QR%20code"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}: {url}")
        qr_data = scraper.extract_qr_from_image_url(url)
        
        if qr_data:
            print(f"✅ Found QR code(s): {qr_data}")
        else:
            print("❌ No QR codes found")

def demo_custom_url():
    """Allow user to test with their own URL"""
    print("\n🔍 Demo 2: Your Custom URL")
    print("=" * 50)
    
    print("You can test with:")
    print("1. A direct image URL (ending in .png, .jpg, etc.)")
    print("2. A webpage URL that contains images with QR codes")
    print("3. Press Enter to skip")
    
    url = input("\nEnter a URL: ").strip()
    
    if not url:
        print("Skipped.")
        return
    
    scraper = QRScraper()
    
    # Check if it's likely an image URL
    if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
        print(f"\nTreating as image URL: {url}")
        qr_data = scraper.extract_qr_from_image_url(url)
        
        if qr_data:
            print(f"✅ Found QR code(s): {qr_data}")
        else:
            print("❌ No QR codes found in image")
    else:
        print(f"\nTreating as webpage URL: {url}")
        results = scraper.scrape_qr_codes_from_webpage(url)
        
        if results:
            print(f"✅ Found QR codes in {len(results)} image(s):")
            for i, result in enumerate(results, 1):
                print(f"\n  Image {i}: {result['image_url']}")
                print(f"  QR Content: {result['qr_contents']}")
        else:
            print("❌ No QR codes found on webpage")

def main():
    print("🚀 QR Code Scraper - Working Examples")
    print("=" * 60)
    
    try:
        demo_single_qr_image()
        demo_custom_url()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed!")
        print("\nTo use in your own code:")
        print("```python")
        print("from src.qr_scraper import QRScraper")
        print("scraper = QRScraper()")
        print("qr_data = scraper.extract_qr_from_image_url('your_image_url')")
        print("results = scraper.scrape_qr_codes_from_webpage('your_webpage_url')")
        print("```")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 