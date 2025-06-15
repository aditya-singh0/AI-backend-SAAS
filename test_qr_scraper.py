#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.qr_scraper import QRScraper

def test_single_image():
    """Test extracting QR code from a single image URL"""
    print("=== Testing single QR code image ===")
    
    scraper = QRScraper()
    
    # Test with a known QR code image (this is a sample QR code image)
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/256px-QR_code_for_mobile_English_Wikipedia.svg.png"
    
    print(f"Testing image: {test_image_url}")
    qr_data = scraper.extract_qr_from_image_url(test_image_url)
    
    if qr_data:
        print(f"✅ Found QR codes: {qr_data}")
    else:
        print("❌ No QR codes found")

def test_webpage():
    """Test scraping QR codes from a webpage"""
    print("\n=== Testing webpage QR code scraping ===")
    
    scraper = QRScraper()
    
    # Test with a webpage that might contain QR codes
    test_url = "https://en.wikipedia.org/wiki/QR_code"
    
    print(f"Testing webpage: {test_url}")
    results = scraper.scrape_qr_codes_from_webpage(test_url)
    
    if results:
        print(f"✅ Found {len(results)} images with QR codes:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Image: {result['image_url']}")
            print(f"     QR Content: {result['qr_contents']}")
    else:
        print("❌ No QR codes found on the webpage")

def test_custom_url():
    """Allow user to test with their own URL"""
    print("\n=== Custom URL Test ===")
    
    url = input("Enter a URL to scrape for QR codes (or press Enter to skip): ").strip()
    
    if url:
        scraper = QRScraper()
        
        if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
            print(f"Testing image: {url}")
            qr_data = scraper.extract_qr_from_image_url(url)
            if qr_data:
                print(f"✅ Found QR codes: {qr_data}")
            else:
                print("❌ No QR codes found")
        else:
            print(f"Testing webpage: {url}")
            results = scraper.scrape_qr_codes_from_webpage(url)
            if results:
                print(f"✅ Found {len(results)} images with QR codes:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. Image: {result['image_url']}")
                    print(f"     QR Content: {result['qr_contents']}")
            else:
                print("❌ No QR codes found on the webpage")
    else:
        print("Skipping custom URL test")

if __name__ == "__main__":
    print("🔍 QR Code Scraper Test")
    print("=" * 50)
    
    try:
        test_single_image()
        test_webpage()
        test_custom_url()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 