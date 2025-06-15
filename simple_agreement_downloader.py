#!/usr/bin/env python3
"""
Simplified Agreement to Sale Document Downloader
Downloads documents from Maharashtra IGR without OCR dependencies
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import json
import ssl
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy configuration
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'iyHxHphyuy3i'
}

class SimpleAgreementDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://pay2igr.igrmaharashtra.gov.in'
        }
        
        self.data_dir = 'data'
        self.documents_dir = os.path.join(self.data_dir, 'documents')
        self.metadata_dir = os.path.join(self.data_dir, 'metadata')
        self.download_count = 0
        self.session_id = None
        self.last_ip_change = time.time()
        
        # Create directories
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        print("✅ Simple Agreement Downloader initialized")
        print(f"📁 Documents folder: {os.path.abspath(self.documents_dir)}")
        print(f"📋 Metadata folder: {os.path.abspath(self.metadata_dir)}")
    
    def get_new_session_id(self):
        """Generate new session ID for IP rotation"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"simple-{random_id}-{timestamp}"
    
    def get_proxy(self):
        """Get proxy configuration with IP rotation"""
        current_time = time.time()
        
        # Change IP every 5 seconds
        if not self.session_id or (current_time - self.last_ip_change) >= 5:
            self.session_id = self.get_new_session_id()
            self.last_ip_change = current_time
            print(f"🔄 IP rotated - Session: {self.session_id}")
        
        # Build proxy URL
        full_username = f"{PROXY_CONFIG['username']}-sessid-{self.session_id}"
        proxy_url = f"http://{full_username}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    def make_request(self, url, method='GET', **kwargs):
        """Make HTTP request with proxy rotation"""
        try:
            # Add proxy and headers
            kwargs['proxies'] = self.get_proxy()
            kwargs['headers'] = self.headers
            kwargs['timeout'] = 15
            kwargs['verify'] = False
            
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            else:
                response = self.session.post(url, **kwargs)
            
            response.raise_for_status()
            return response
            
        except Exception as e:
            print(f"⚠️  Request failed: {e}")
            # Try without proxy
            kwargs.pop('proxies', None)
            
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            else:
                response = self.session.post(url, **kwargs)
            
            return response
    
    def search_documents(self, district_id='1', year='2024'):
        """Search for documents without CAPTCHA handling"""
        print(f"\n🔍 Searching documents for District: {district_id}, Year: {year}")
        
        try:
            # Load search page
            response = self.make_request(self.search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find Agreement to Sale article ID
            article_id = self.find_agreement_article_id(soup)
            if not article_id:
                print("⚠️  Could not find Agreement to Sale article ID, trying common ones...")
                article_id = '31'  # Common sale deed ID
            
            # Prepare form data
            form_data = {
                'dbselect': '3',  # Recent years database
                'district_id': district_id,
                'article_id': article_id,
                'year': year
            }
            
            # Add hidden form fields
            form = soup.find('form')
            if form:
                hidden_inputs = form.find_all('input', {'type': 'hidden'})
                for inp in hidden_inputs:
                    name = inp.get('name')
                    value = inp.get('value', '')
                    if name:
                        form_data[name] = value
            
            print(f"📤 Submitting search with Article ID: {article_id}")
            
            # Submit search (this might be blocked by CAPTCHA)
            response = self.make_request(self.search_url, method='POST', data=form_data)
            
            # Extract document links
            return self.extract_document_links(response.text)
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def find_agreement_article_id(self, soup):
        """Find Agreement to Sale article ID from dropdown"""
        select = soup.find('select', {'id': 'article_id'}) or soup.find('select', {'name': 'article_id'})
        if select:
            options = select.find_all('option')
            for option in options:
                text = option.get_text(strip=True).lower()
                value = option.get('value', '')
                
                if any(term in text for term in ['agreement', 'sale', 'करार', 'विक्री']):
                    print(f"📋 Found: {value} - {option.get_text(strip=True)}")
                    return value
        return None
    
    def extract_document_links(self, html):
        """Extract document links from search results"""
        soup = BeautifulSoup(html, 'html.parser')
        documents = []
        
        # Look for document links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it's a document link
            if any(term in href.lower() for term in ['view', 'download', 'document', 'indexii', 'propertydetails']):
                doc_url = urljoin(self.base_url, href)
                documents.append({
                    'url': doc_url,
                    'text': text,
                    'type': 'document_link'
                })
        
        # Also check tables for document rows
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                row_links = row.find_all('a', href=True)
                for link in row_links:
                    href = link.get('href', '')
                    if href:
                        doc_url = urljoin(self.base_url, href)
                        documents.append({
                            'url': doc_url,
                            'text': row.get_text(strip=True)[:100],
                            'type': 'table_row'
                        })
        
        print(f"📄 Found {len(documents)} potential documents")
        return documents
    
    def download_document(self, doc_info, index):
        """Download a single document"""
        url = doc_info['url']
        filename = f"agreement_{index:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.documents_dir, filename)
        
        try:
            print(f"📥 Downloading {index}: {doc_info['text'][:50]}...")
            
            response = self.make_request(url)
            
            # Save the content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.download_count += 1
            print(f"✅ Saved: {filename}")
            
            # Save metadata
            metadata = {
                'filename': filename,
                'url': url,
                'text': doc_info['text'],
                'downloaded_at': datetime.now().isoformat(),
                'session_id': self.session_id,
                'file_size': os.path.getsize(filepath),
                'content_type': response.headers.get('content-type', 'text/html')
            }
            
            meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def run_bulk_download(self, max_documents=10):
        """Run bulk download with basic parameters"""
        print("🚀 Starting Simple Agreement Download")
        print(f"   Max documents: {max_documents}")
        print(f"   IP rotation: Every 5 seconds")
        print("=" * 50)
        
        all_documents = []
        
        # Try different districts
        districts = ['1', '2', '3', '4', '5']
        years = ['2024', '2023']
        
        for district in districts:
            if len(all_documents) >= max_documents:
                break
            
            for year in years:
                if len(all_documents) >= max_documents:
                    break
                
                print(f"\n🔍 District: {district}, Year: {year}")
                
                # Search documents
                documents = self.search_documents(district_id=district, year=year)
                remaining = max_documents - len(all_documents)
                all_documents.extend(documents[:remaining])
                
                print(f"📊 Total found: {len(all_documents)}")
                
                # Wait between searches
                time.sleep(3)
        
        # Download documents
        print(f"\n📥 Starting download of {len(all_documents)} documents...")
        
        for i, doc in enumerate(all_documents, 1):
            if i > max_documents:
                break
            
            success = self.download_document(doc, i)
            
            # Wait between downloads
            if i < len(all_documents):
                time.sleep(2)
        
        print("\n" + "=" * 50)
        print(f"✅ Download complete!")
        print(f"   Downloaded: {self.download_count} documents")
        print(f"   Saved to: {os.path.abspath(self.documents_dir)}")
        
        return self.download_count

def main():
    """Main function"""
    print("📄 Simple Agreement to Sale Downloader")
    print("=" * 50)
    print("This is a simplified version that works without OCR")
    print("⚠️  May be limited by CAPTCHAs on the website")
    print("=" * 50)
    
    downloader = SimpleAgreementDownloader()
    
    # Get user input
    try:
        max_docs = int(input("\nHow many documents to download? (default 10): ") or "10")
    except ValueError:
        max_docs = 10
    
    # Run download
    count = downloader.run_bulk_download(max_documents=max_docs)
    
    print(f"\n🎉 Downloaded {count} documents successfully!")

if __name__ == "__main__":
    main()