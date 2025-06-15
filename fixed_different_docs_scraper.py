#!/usr/bin/env python3
"""
Fixed Different Documents Scraper
This generates different document URLs by varying parameters to get unique documents
"""

import os
import time
import json
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random

class FixedDifferentDocsScraper:
    def __init__(self):
        self.data_dir = 'data'
        self.documents_dir = os.path.join(self.data_dir, 'different_agreements')
        self.metadata_dir = os.path.join(self.data_dir, 'different_metadata')
        
        # Create directories
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        self.download_count = 0
        
        print("🎯 Fixed Different Documents Scraper")
        print("=" * 50)
        print("This scraper generates different document URLs to get unique content")
        print(f"📁 Documents: {os.path.abspath(self.documents_dir)}")
        print(f"📋 Metadata: {os.path.abspath(self.metadata_dir)}")
        print("=" * 50)
    
    def generate_document_urls(self, count=25):
        """Generate different document URLs by varying parameters"""
        base_urls = [
            "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/",
            "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii2/",
            "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/view/",
            "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/display/"
        ]
        
        # Different encoded parameters
        parameters = []
        
        # Generate different base64 encoded parameters
        for i in range(1, count + 1):
            # Vary the numbers to get different documents
            for year in [2024, 2023, 2022]:
                for district in range(1, 15):  # Different districts
                    for doc_num in range(1000, 9999, 100):  # Different document numbers
                        # Create different parameter combinations
                        param_variations = [
                            f"{year}{district:02d}{doc_num}",
                            f"{doc_num}{year}",
                            f"{district:02d}{year}{doc_num}",
                            f"{year}{doc_num}{district:02d}",
                        ]
                        
                        for param in param_variations:
                            # Encode parameter in base64
                            encoded = base64.b64encode(param.encode()).decode()
                            parameters.append(encoded)
                            
                            # Also try URL encoding
                            url_encoded = param.replace('2024', 'MjAyNQ%3D%3D').replace('2023', 'MjAyMw%3D%3D')
                            parameters.append(url_encoded)
                            
                            if len(parameters) >= count * 4:  # Enough parameters
                                break
                        
                        if len(parameters) >= count * 4:
                            break
                    if len(parameters) >= count * 4:
                        break
                if len(parameters) >= count * 4:
                    break
        
        # Generate URLs
        urls = []
        for i in range(count):
            base_url = random.choice(base_urls)
            param = parameters[i % len(parameters)]
            
            # Try different URL patterns
            url_patterns = [
                f"{base_url}{param}",
                f"{base_url}{param}/view",
                f"{base_url}{param}/display",
                f"{base_url}MjAyNQ%3D%3D/{param}",
                f"{base_url}details/{param}",
            ]
            
            url = random.choice(url_patterns)
            urls.append({
                'url': url,
                'param': param,
                'pattern': base_url,
                'index': i + 1
            })
        
        return urls
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def download_document(self, doc_info):
        """Download a single document with unique URL"""
        driver = self.setup_driver()
        
        try:
            print(f"📥 Document {doc_info['index']}: Loading {doc_info['url'][:80]}...")
            
            # Load the page
            driver.get(doc_info['url'])
            time.sleep(3)  # Wait for content to load
            
            # Get page content
            content = driver.page_source
            
            # Check if we got different content
            content_size = len(content)
            
            # Skip if content is too small (likely error page)
            if content_size < 1000:
                print(f"⚠️  Document {doc_info['index']}: Content too small ({content_size} chars), trying next...")
                return False
            
            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"UniqueAgreement_{doc_info['index']:04d}_{timestamp}.html"
            filepath = os.path.join(self.documents_dir, filename)
            
            # Save content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Save metadata
            metadata = {
                'filename': filename,
                'url': doc_info['url'],
                'parameter': doc_info['param'],
                'pattern': doc_info['pattern'],
                'index': doc_info['index'],
                'downloaded_at': datetime.now().isoformat(),
                'file_size': content_size,
                'content_preview': content[:500] + '...' if len(content) > 500 else content
            }
            
            meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.download_count += 1
            print(f"✅ Document {doc_info['index']}: Saved {filename} ({content_size:,} chars)")
            
            return True
            
        except Exception as e:
            print(f"❌ Document {doc_info['index']}: Failed - {e}")
            return False
            
        finally:
            driver.quit()
    
    def run_scraper(self, max_documents=25):
        """Run the scraper with different URLs"""
        print(f"🚀 Starting scraper for {max_documents} DIFFERENT documents")
        print("🎯 Generating unique URLs with different parameters...")
        
        # Generate different document URLs
        document_urls = self.generate_document_urls(max_documents)
        
        print(f"📊 Generated {len(document_urls)} unique URLs")
        print("=" * 50)
        
        success_count = 0
        
        # Download each document
        for doc_info in document_urls:
            success = self.download_document(doc_info)
            if success:
                success_count += 1
            
            # Wait between downloads
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print(f"🎉 Scraping complete!")
        print(f"📊 Successfully downloaded: {success_count}/{max_documents} documents")
        print(f"📁 Saved to: {os.path.abspath(self.documents_dir)}")
        
        # Show file sizes to verify they're different
        print("\n📋 File sizes (to verify uniqueness):")
        for filename in os.listdir(self.documents_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(self.documents_dir, filename)
                size = os.path.getsize(filepath)
                print(f"   {filename}: {size:,} bytes")
        
        return success_count

def main():
    scraper = FixedDifferentDocsScraper()
    
    try:
        max_docs = int(input("How many DIFFERENT documents to download? (default 25): ") or "25")
    except ValueError:
        max_docs = 25
    
    print(f"\n🎯 This will generate {max_docs} different URLs to get unique documents")
    print("💡 Each document should have different content sizes")
    print("=" * 50)
    
    count = scraper.run_scraper(max_documents=max_docs)
    
    if count > 0:
        print(f"\n✅ SUCCESS: Downloaded {count} different documents!")
        print("🔍 Check file sizes above - they should be different if documents are unique")
    else:
        print("\n❌ No documents downloaded")

if __name__ == "__main__":
    main()