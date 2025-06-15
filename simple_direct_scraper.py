#!/usr/bin/env python3
"""
Simple Direct IGR Scraper
This is the most basic HTTP approach possible, bypassing all security checks.
"""
import os
import requests
import urllib3
from bs4 import BeautifulSoup
import warnings

# Disable all SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class SimpleDirectScraper:
    def __init__(self):
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'simple_direct_docs')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        
        # Create session with all security disabled
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print("🚀 Simple Direct IGR Scraper")
        print("=" * 60)
        print("This script attempts the most basic HTTP approach.")
        print(f"📁 Documents will be saved in: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def run(self):
        """Main execution logic."""
        try:
            print("\n🔍 Attempting to access the website...")
            response = self.session.get(self.search_url, timeout=15)
            print(f"✅ Website responded with status: {response.status_code}")
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find any form token
            token_input = soup.find('input', {'name': '__RequestVerificationToken'})
            if token_input:
                token = token_input.get('value', '')
                print(f"✅ Found verification token: {token[:20]}...")
            else:
                token = ''
                print("⚠️ No verification token found, proceeding without it.")
            
            # Prepare basic form data (without CAPTCHA)
            form_data = {
                '__RequestVerificationToken': token,
                'dbselect': '3',
                'district_id': '1',
                'article_id': '43',
                'year': '2024',
                'txtcaptcha': ''  # Empty CAPTCHA
            }
            
            print("\n📤 Submitting search form...")
            response = self.session.post(self.search_url, data=form_data, timeout=20)
            print(f"✅ Form submitted, status: {response.status_code}")
            
            # Look for any links in the response
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            print(f"\n📄 Found {len(all_links)} total links on the page.")
            
            # Filter for document-like links
            doc_links = []
            for link in all_links:
                href = link.get('href', '')
                if any(keyword in href.lower() for keyword in ['view', 'document', 'indexii', 'display']):
                    doc_links.append(href)
            
            if doc_links:
                print(f"📋 Found {len(doc_links)} potential document links.")
                
                # Download first few documents
                for i, link in enumerate(doc_links[:5]):  # Limit to 5 for testing
                    try:
                        if not link.startswith('http'):
                            url = f"{self.base_url}{link}"
                        else:
                            url = link
                        
                        print(f"   -> Downloading document {i+1}: {url[:50]}...")
                        doc_response = self.session.get(url, timeout=15)
                        
                        filename = f"Simple_Doc_{i+1:03d}.html"
                        filepath = os.path.join(self.docs_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(doc_response.text)
                        
                        self.download_count += 1
                        print(f"      ✅ Saved: {filename}")
                        
                    except Exception as e:
                        print(f"      ❌ Error downloading: {e}")
                
                print(f"\n✅ Downloaded {self.download_count} documents.")
            else:
                print("❌ No document links found. The server likely requires CAPTCHA.")
                print("   However, the basic connection worked!")
                
                # Save the response page for inspection
                with open(os.path.join(self.docs_dir, 'response_page.html'), 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("📄 Saved response page for inspection.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n--- Process Finished ---")

if __name__ == '__main__':
    scraper = SimpleDirectScraper()
    scraper.run()
    print(f"\n🎉 Check the '{scraper.docs_dir}' directory for results.") 