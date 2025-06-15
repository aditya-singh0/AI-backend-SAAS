#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Selenium IGR Scraper
Downloads IGR documents using Selenium to bypass SSL issues
"""

import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    """Create a Chrome driver with automatic ChromeDriver management"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    
    # Use webdriver_manager to automatically download and manage ChromeDriver
    print("🔧 Setting up ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ ChromeDriver ready")
    return driver

def download_igr_documents(count=10):
    """Download multiple IGR documents"""
    base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/"
    base_pattern = "MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
    
    # Create output directory
    output_dir = "data/selenium_igr_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📂 Output directory: {os.path.abspath(output_dir)}")
    print(f"🎯 Downloading {count} documents...\n")
    
    success_count = 0
    
    # Create one driver for all downloads
    driver = None
    try:
        driver = create_driver()
        
        for i in range(count):
            doc_id = i + 1
            print(f"\n📥 Downloading document {doc_id}/{count}...")
            
            # Modify URL for each document
            if i > 0:
                # Simple modification - change some numbers
                modified_pattern = base_pattern.replace("6969", f"{6969 + i:04d}")
                url = base_url + modified_pattern
            else:
                url = base_url + base_pattern
            
            try:
                print(f"🌐 Loading: {url[:80]}...")
                driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Get page source
                page_source = driver.page_source
                
                if len(page_source) > 1000:
                    # Save HTML file
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"IGR_Document_{doc_id:04d}_{timestamp}.html"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(page_source)
                    
                    print(f"✅ Saved: {filename} ({len(page_source):,} chars)")
                    success_count += 1
                    
                    # Save metadata
                    metadata = {
                        "doc_id": doc_id,
                        "url": url,
                        "filename": filename,
                        "timestamp": datetime.now().isoformat(),
                        "size_chars": len(page_source)
                    }
                    
                    meta_file = filepath.replace('.html', '_metadata.json')
                    with open(meta_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                else:
                    print(f"❌ Invalid content for document {doc_id}")
                    
            except Exception as e:
                print(f"❌ Error downloading document {doc_id}: {e}")
            
            # Small delay between downloads
            if i < count - 1:
                time.sleep(2)
    
    finally:
        if driver:
            driver.quit()
            print("\n🔧 ChromeDriver closed")
    
    print(f"\n✅ Downloaded {success_count}/{count} documents")
    print(f"📂 Files saved to: {os.path.abspath(output_dir)}")

def main():
    print("🏛️  Simple Selenium IGR Scraper")
    print("=" * 60)
    print("This tool downloads IGR documents using Selenium")
    print("It bypasses SSL issues by using a real browser")
    print("=" * 60)
    
    try:
        count = int(input("\n📊 How many documents to download? (default 10): ") or "10")
    except:
        count = 10
    
    start_time = time.time()
    download_igr_documents(count)
    print(f"\n⏱️  Total time: {time.time() - start_time:.1f} seconds")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 