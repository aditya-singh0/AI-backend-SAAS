#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.qr_scraper import QRScraper

def main():
    print("🔍 Simple QR Code Test")
    print("=" * 40)
    
    scraper = QRScraper()
    
    # Test with a direct QR code image
    qr_image_url = "https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg"
    
    print(f"Testing QR code from: {qr_image_url}")
    
    try:
        qr_data = scraper.extract_qr_from_image_url(qr_image_url)
        
        if qr_data:
            print("✅ SUCCESS! Found QR codes:")
            for i, data in enumerate(qr_data, 1):
                print(f"  {i}. {data}")
        else:
            print("❌ No QR codes found in the image")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Test with a simple PNG QR code
    print("\n" + "=" * 40)
    png_qr_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/256px-QR_code_for_mobile_English_Wikipedia.svg.png"
    print(f"Testing PNG QR code from: {png_qr_url}")
    
    try:
        qr_data = scraper.extract_qr_from_image_url(png_qr_url)
        
        if qr_data:
            print("✅ SUCCESS! Found QR codes:")
            for i, data in enumerate(qr_data, 1):
                print(f"  {i}. {data}")
        else:
            print("❌ No QR codes found in the PNG image")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 