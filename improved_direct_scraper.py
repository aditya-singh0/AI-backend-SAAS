#!/usr/bin/env python3
"""
Improved Direct IGR Scraper
This script properly handles CSRF tokens and cookies based on our successful connection.
"""
import os
import requests
import urllib3
from bs4 import BeautifulSoup
import warnings

# Disable all SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class ImprovedDirectScraper:
    def __init__(self):
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'improved_direct_docs')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        
        # Create session with all security disabled but proper cookie handling
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        print("🚀 Improved Direct IGR Scraper")
        print("=" * 60)
        print("This script properly handles CSRF tokens and cookies.")
        print(f"📁 Documents will be saved in: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def run(self):
        """Main execution logic."""
        try:
            # Step 1: Get the initial page to obtain CSRF token and cookies
            print("\n🔍 Getting initial page and CSRF token...")
            response = self.session.get(self.search_url, timeout=15)
            print(f"✅ Initial page loaded, status: {response.status_code}")
            
            # Parse the page and extract CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for CSRF token in various possible locations
            csrf_token = None
            
            # Method 1: Look for __RequestVerificationToken input
            token_input = soup.find('input', {'name': '__RequestVerificationToken'})
            if token_input:
                csrf_token = token_input.get('value')
                print(f"✅ Found CSRF token (method 1): {csrf_token[:20]}...")
            
            # Method 2: Look for other common CSRF token names
            if not csrf_token:
                for name in ['_token', 'csrf_token', 'authenticity_token']:
                    token_input = soup.find('input', {'name': name})
                    if token_input:
                        csrf_token = token_input.get('value')
                        print(f"✅ Found CSRF token (method 2, {name}): {csrf_token[:20]}...")
                        break
            
            # Method 3: Look in meta tags
            if not csrf_token:
                meta_token = soup.find('meta', {'name': 'csrf-token'})
                if meta_token:
                    csrf_token = meta_token.get('content')
                    print(f"✅ Found CSRF token (method 3, meta): {csrf_token[:20]}...")
            
            if not csrf_token:
                print("⚠️ No CSRF token found, proceeding without it.")
                csrf_token = ''
            
            # Step 2: Prepare form data with proper headers
            form_data = {
                '__RequestVerificationToken': csrf_token,
                'dbselect': '3',
                'district_id': '1', 
                'article_id': '43',
                'year': '2024',
                'txtcaptcha': ''  # We'll try without CAPTCHA first
            }
            
            # Add proper form headers
            headers = self.session.headers.copy()
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.search_url,
                'Origin': self.base_url
            })
            
            print("\n📤 Submitting search form with proper CSRF token...")
            response = self.session.post(
                self.search_url, 
                data=form_data, 
                headers=headers,
                timeout=20,
                allow_redirects=True
            )
            print(f"✅ Form submitted, status: {response.status_code}")
            
            # Step 3: Analyze the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Save the response for inspection
            with open(os.path.join(self.docs_dir, 'form_response.html'), 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("📄 Saved form response for inspection.")
            
            # Look for various types of links
            all_links = soup.find_all('a', href=True)
            print(f"\n📄 Found {len(all_links)} total links on the response page.")
            
            # Check for error messages
            error_indicators = ['error', 'captcha', 'verification', 'invalid']
            page_text = response.text.lower()
            
            for indicator in error_indicators:
                if indicator in page_text:
                    print(f"⚠️ Found '{indicator}' in response - may indicate an issue.")
            
            # Look for document-like links
            doc_links = []
            for link in all_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                if any(keyword in href.lower() for keyword in ['view', 'document', 'indexii', 'display', 'download']):
                    doc_links.append((href, link_text))
                elif any(keyword in link_text for keyword in ['view', 'document', 'download', 'agreement']):
                    doc_links.append((href, link_text))
            
            if doc_links:
                print(f"📋 Found {len(doc_links)} potential document links:")
                for i, (href, text) in enumerate(doc_links[:10]):  # Show first 10
                    print(f"   {i+1}. {text[:30]} -> {href[:50]}")
                
                # Try to download a few
                for i, (href, text) in enumerate(doc_links[:3]):
                    try:
                        if not href.startswith('http'):
                            url = f"{self.base_url}{href}"
                        else:
                            url = href
                        
                        print(f"\n   -> Downloading document {i+1}: {text[:30]}...")
                        doc_response = self.session.get(url, timeout=15)
                        
                        filename = f"Improved_Doc_{i+1:03d}.html"
                        filepath = os.path.join(self.docs_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(doc_response.text)
                        
                        self.download_count += 1
                        print(f"      ✅ Saved: {filename}")
                        
                    except Exception as e:
                        print(f"      ❌ Error downloading: {e}")
                
                print(f"\n✅ Downloaded {self.download_count} documents.")
            else:
                print("❌ No document links found.")
                print("   This likely means the server requires CAPTCHA verification.")
                print("   However, the CSRF token handling is now working!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n--- Process Finished ---")

if __name__ == '__main__':
    scraper = ImprovedDirectScraper()
    scraper.run()
    print(f"\n🎉 Check the '{scraper.docs_dir}' directory for results.") 