#!/usr/bin/env python3
"""
Agreement to Sale Document Downloader
Downloads documents from Maharashtra IGR with IP rotation, CAPTCHA solving, and IP block detection
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import random
import json
import base64
from PIL import Image
import pytesseract
import io
import cv2
import numpy as np
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try to import httpx as fallback
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️  httpx not available, using requests only")

# Proxy configuration
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'iyHxHphyuy3i'
}

class AgreementDownloader:
    def __init__(self):
        # Force TLS 1.2 minimum
        self.setup_ssl_context()
        
        self.session = requests.Session()
        
        # Configure SSL adapter for better compatibility
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],  # Updated parameter name
            backoff_factor=1
        )
        
        # Create custom HTTPAdapter with TLS settings
        class TLSAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                ctx = ssl.create_default_context()
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')  # Lower security level for compatibility
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2  # Force TLS 1.2+
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                kwargs['ssl_context'] = ctx
                return super().init_poolmanager(*args, **kwargs)
        
        adapter = TLSAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Disable SSL verification globally for this session
        self.session.verify = False
        
        # Setup httpx client as fallback
        if HTTPX_AVAILABLE:
            self.setup_httpx_client()
        
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://pay2igr.igrmaharashtra.gov.in'
        }
        self.data_dir = 'data'
        self.captcha_dir = os.path.join(self.data_dir, 'captchas')
        self.documents_dir = os.path.join(self.data_dir, 'documents')
        self.metadata_dir = os.path.join(self.data_dir, 'metadata')
        self.download_count = 0
        self.last_ip_change = time.time()
        self.session_id = None
        self.blocked_ips = set()
        self.captcha_attempts = 0
        self.max_captcha_attempts = 5
        
        # Create all necessary directories
        self.create_directories()
        
        # Initialize OCR
        self.setup_ocr()
    
    def setup_ssl_context(self):
        """Setup SSL context for better TLS compatibility"""
        try:
            # Create a custom SSL context
            context = ssl.create_default_context()
            context.set_ciphers('DEFAULT@SECLEVEL=1')
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Apply globally
            ssl._create_default_https_context = lambda: context
            print("✅ SSL/TLS context configured (TLS 1.2+)")
            
        except Exception as e:
            print(f"⚠️  SSL setup warning: {e}")
    
    def setup_httpx_client(self):
        """Setup httpx client as fallback"""
        try:
            # Create httpx client with custom SSL settings
            self.httpx_client = httpx.Client(
                verify=False,
                timeout=15.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            print("✅ HTTPX client initialized as fallback")
        except Exception as e:
            print(f"⚠️  HTTPX setup warning: {e}")
            self.httpx_client = None
        
    def create_directories(self):
        """Create all necessary directories for data storage"""
        directories = [
            self.data_dir,
            self.captcha_dir,
            self.documents_dir,
            self.metadata_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created/verified directory: {directory}")
    
    def setup_ocr(self):
        """Setup OCR for CAPTCHA reading"""
        try:
            # Test if pytesseract is working
            pytesseract.get_tesseract_version()
            print("✅ OCR (Tesseract) initialized successfully")
        except Exception as e:
            print(f"⚠️  OCR setup warning: {e}")
            print("📝 Install Tesseract OCR for CAPTCHA reading: https://github.com/tesseract-ocr/tesseract")
        
    def get_new_session_id(self):
        """Generate new session ID for IP rotation"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"agr-{random_id}-{timestamp}"
    
    def force_ip_change(self):
        """Force immediate IP change"""
        old_session = self.session_id
        self.session_id = self.get_new_session_id()
        self.last_ip_change = time.time()
        
        if old_session:
            self.blocked_ips.add(old_session)
        
        print(f"🔄 FORCED IP change: {old_session} -> {self.session_id}")
        return self.session_id
    
    def get_proxy(self, force_new=False):
        """Get proxy configuration with IP rotation"""
        current_time = time.time()
        
        # Force new IP or change IP every 4 seconds
        if force_new or not self.session_id or (current_time - self.last_ip_change) >= 4:
            if not force_new:
                self.session_id = self.get_new_session_id()
                self.last_ip_change = current_time
                print(f"🔄 Scheduled IP rotation - Session: {self.session_id}")
            else:
                self.force_ip_change()
        
        # Build proxy URL
        full_username = f"{PROXY_CONFIG['username']}-sessid-{self.session_id}"
        proxy_url = f"http://{full_username}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    def is_ip_blocked(self, response_text):
        """Detect if IP is blocked based on response content"""
        blocked_indicators = [
            'blocked', 'banned', 'forbidden', 'access denied',
            'too many requests', 'rate limit', 'captcha required',
            '403', '429', 'please try again later'
        ]
        
        text_lower = response_text.lower()
        for indicator in blocked_indicators:
            if indicator in text_lower:
                return True
        return False
    
    def has_captcha(self, soup):
        """Check if page contains CAPTCHA"""
        captcha_indicators = [
            'captcha', 'verification', 'security code',
            'img[src*="captcha"]', 'input[name*="captcha"]'
        ]
        
        for indicator in captcha_indicators:
            if 'img[' in indicator or 'input[' in indicator:
                if soup.select(indicator):
                    return True
            else:
                if soup.find(text=lambda text: text and indicator.lower() in text.lower()):
                    return True
        
        return False
    
    def download_captcha_image(self, soup, captcha_url=None):
        """Download CAPTCHA image for processing"""
        if not captcha_url:
            # Find CAPTCHA image
            captcha_img = soup.find('img', src=lambda x: x and 'captcha' in x.lower()) or \
                         soup.find('img', alt=lambda x: x and 'captcha' in x.lower()) or \
                         soup.find('img', id=lambda x: x and 'captcha' in x.lower())
            
            if not captcha_img:
                return None
            
            captcha_url = captcha_img.get('src')
        
        if not captcha_url:
            return None
        
        # Make URL absolute
        if captcha_url.startswith('/'):
            captcha_url = urljoin(self.base_url, captcha_url)
        
        try:
            # Download CAPTCHA image
            response = self.make_request(captcha_url, stream=True)
            
            # Save CAPTCHA image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'captcha_{timestamp}.png'
            filepath = os.path.join(self.captcha_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"📷 CAPTCHA image saved: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to download CAPTCHA: {e}")
            return None
    
    def preprocess_captcha_image(self, image_path):
        """Preprocess CAPTCHA image for better OCR"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Remove noise
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Save preprocessed image
            processed_path = image_path.replace('.png', '_processed.png')
            cv2.imwrite(processed_path, cleaned)
            
            return processed_path
            
        except Exception as e:
            print(f"⚠️  Image preprocessing failed: {e}")
            return image_path
    
    def solve_captcha(self, image_path):
        """Solve CAPTCHA using OCR"""
        try:
            # Preprocess image
            processed_path = self.preprocess_captcha_image(image_path)
            
            # Read CAPTCHA with OCR
            image = Image.open(processed_path)
            
            # OCR with different configurations
            configs = [
                '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 6'
            ]
            
            for config in configs:
                try:
                    captcha_text = pytesseract.image_to_string(image, config=config).strip()
                    if captcha_text and len(captcha_text) >= 3:
                        print(f"🔍 CAPTCHA solved: '{captcha_text}'")
                        return captcha_text
                except:
                    continue
            
            print("❌ Could not solve CAPTCHA with OCR")
            return None
            
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return None
    
    def handle_captcha(self, soup):
        """Handle CAPTCHA challenge"""
        print("🤖 CAPTCHA detected, attempting to solve...")
        
        self.captcha_attempts += 1
        if self.captcha_attempts > self.max_captcha_attempts:
            print("❌ Maximum CAPTCHA attempts reached, changing IP...")
            self.force_ip_change()
            self.captcha_attempts = 0
            return None
        
        # Download CAPTCHA image
        captcha_image_path = self.download_captcha_image(soup)
        if not captcha_image_path:
            return None
        
        # Solve CAPTCHA
        captcha_solution = self.solve_captcha(captcha_image_path)
        if captcha_solution:
            print(f"✅ CAPTCHA solved: {captcha_solution}")
            return captcha_solution
        
        return None
    
    def make_request(self, url, method='GET', **kwargs):
        """Make request with automatic retry, proxy/direct fallback, and IP block detection"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Use proxy if not already failed
                if self.session_id not in self.blocked_ips:
                    kwargs['proxies'] = self.get_proxy()
                else:
                    kwargs.pop('proxies', None)  # Use direct connection
                
                # SSL/TLS configuration
                kwargs['verify'] = False
                kwargs['timeout'] = 15
                kwargs['headers'] = self.headers
                
                # Disable SSL warnings
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                if method == 'GET':
                    response = self.session.get(url, **kwargs)
                else:
                    response = self.session.post(url, **kwargs)
                
                # Check if IP is blocked
                if self.is_ip_blocked(response.text):
                    print(f"🚫 IP blocked detected, changing IP...")
                    self.force_ip_change()
                    continue
                
                # Check for CAPTCHA
                soup = BeautifulSoup(response.text, 'html.parser')
                if self.has_captcha(soup):
                    captcha_solution = self.handle_captcha(soup)
                    if captcha_solution:
                        # Retry request with CAPTCHA solution
                        if 'data' not in kwargs:
                            kwargs['data'] = {}
                        kwargs['data']['captcha'] = captcha_solution
                        
                        if method == 'GET':
                            response = self.session.get(url, **kwargs)
                        else:
                            response = self.session.post(url, **kwargs)
                
                response.raise_for_status()
                return response
                
            except (requests.exceptions.RequestException, ssl.SSLError) as e:
                print(f"⚠️  Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    # Force IP change on connection issues
                    self.force_ip_change()
                    time.sleep(2)
                    continue
                else:
                    # Final attempt with httpx if available
                    if HTTPX_AVAILABLE and hasattr(self, 'httpx_client') and self.httpx_client:
                        print("🔄 Trying with HTTPX fallback...")
                        return self.make_httpx_request(url, method, **kwargs)
                    else:
                        # Final attempt with direct connection
                        kwargs.pop('proxies', None)
                        
                        if method == 'GET':
                            response = self.session.get(url, **kwargs)
                        else:
                            response = self.session.post(url, **kwargs)
                        
                        return response
    
    def make_httpx_request(self, url, method='GET', **kwargs):
        """Make request using httpx as fallback"""
        try:
            # Remove requests-specific arguments
            kwargs.pop('stream', None)
            kwargs.pop('proxies', None)  # HTTPX handles proxies differently
            
            if method == 'GET':
                response = self.httpx_client.get(url, **kwargs)
            else:
                response = self.httpx_client.post(url, **kwargs)
            
            # Convert httpx response to requests-like response
            requests_response = requests.Response()
            requests_response.status_code = response.status_code
            requests_response.headers.update(response.headers)
            requests_response._content = response.content
            
            return requests_response
            
        except Exception as e:
            print(f"❌ HTTPX fallback failed: {e}")
            raise
    
    def get_agreement_article_id(self, soup):
        """Find the article ID for Agreement to Sale"""
        article_select = soup.find('select', {'id': 'article_id'})
        if article_select:
            options = article_select.find_all('option')
            for option in options:
                text = option.get_text(strip=True).lower()
                value = option.get('value', '')
                
                # Look for agreement/sale related terms
                if any(term in text for term in ['agreement', 'sale', 'विक्री करार', 'करारनामा']):
                    print(f"📋 Found Agreement type: {value} - {option.get_text(strip=True)}")
                    return value
                    
                # Also check common sale deed ID
                if value == '31':  # Sale deed ID
                    print(f"📋 Using Sale Deed: {value} - {option.get_text(strip=True)}")
                    return value
        
        return None

    def search_documents(self, district_id=None, year='2024', article_id=None):
        """Search for documents with given criteria"""
        print(f"\n🔍 Searching documents...")
        print(f"   Year: {year}")
        print(f"   District: {district_id or 'All'}")
        print(f"   Article: {article_id or 'Agreement to Sale'}")
        
        # Load the search page
        try:
            response = self.make_request(self.search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"❌ Failed to load search page: {e}")
            return []
        
        # Get article ID if not provided
        if not article_id:
            article_id = self.get_agreement_article_id(soup)
            if not article_id:
                print("❌ Could not find Agreement to Sale article ID")
                return []
        
        # Prepare form data
        form_data = {
            'dbselect': '3',  # Year database (3 for recent years)
            'article_id': article_id,
        }
        
        # Add district if specified
        if district_id:
            form_data['district_id'] = district_id
        
        # Extract hidden form fields
        form = soup.find('form')
        if form:
            hidden_inputs = form.find_all('input', {'type': 'hidden'})
            for inp in hidden_inputs:
                name = inp.get('name')
                value = inp.get('value', '')
                if name:
                    form_data[name] = value
        
        # Submit search
        print("📤 Submitting search...")
        try:
            response = self.make_request(
                self.search_url,
                method='POST',
                data=form_data
            )
            return self.extract_documents(response.text)
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def extract_documents(self, html):
        """Extract document links from search results"""
        soup = BeautifulSoup(html, 'html.parser')
        documents = []
        
        # Look for result links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            # Check if it's a document link
            if any(term in href.lower() for term in ['view', 'download', 'document', 'pdf']):
                doc_url = urljoin(self.base_url, href)
                documents.append({
                    'url': doc_url,
                    'text': link.get_text(strip=True),
                    'type': 'link'
                })
        
        # Also look for result rows/tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) > 2:  # Likely a data row
                    # Look for view/download links in the row
                    row_links = row.find_all('a', href=True)
                    for link in row_links:
                        href = link.get('href', '')
                        if href:
                            doc_url = urljoin(self.base_url, href)
                            documents.append({
                                'url': doc_url,
                                'text': ' '.join(cell.get_text(strip=True) for cell in cells[:3]),
                                'type': 'table_row'
                            })
        
        print(f"📄 Found {len(documents)} potential documents")
        return documents
    
    def download_document(self, doc_info, index):
        """Download a single document"""
        url = doc_info['url']
        filename = f"agreement_{index:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.documents_dir, filename)
        
        try:
            print(f"\n📥 Downloading document {index}: {doc_info['text'][:50]}...")
            
            response = self.make_request(url, stream=True)
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type:
                # Try to detect PDF from content
                first_chunk = next(response.iter_content(chunk_size=1024), b'')
                if not first_chunk.startswith(b'%PDF'):
                    print(f"⚠️  Not a PDF file, content-type: {content_type}")
                    # Save as HTML for debugging
                    filename = filename.replace('.pdf', '.html')
                    filepath = filepath.replace('.pdf', '.html')
            
            # Save the file
            with open(filepath, 'wb') as f:
                f.write(first_chunk)  # Write the first chunk we already read
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.download_count += 1
            print(f"✅ Saved: {filename}")
            
            # Save metadata
            metadata = {
                'filename': filename,
                'url': url,
                'text': doc_info['text'],
                'downloaded_at': datetime.now().isoformat(),
                'ip_session': self.session_id,
                'file_size': os.path.getsize(filepath),
                'content_type': content_type
            }
            
            meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download: {e}")
            return False
    
    def run_bulk_download(self, max_documents=50, districts=None, years=None):
        """Run bulk download with IP rotation and CAPTCHA handling"""
        print("🚀 Starting bulk Agreement to Sale download")
        print(f"   Max documents: {max_documents}")
        print(f"   IP rotation: Every 4 seconds + on blocks")
        print(f"   CAPTCHA solving: Enabled")
        print(f"   Data folder: {os.path.abspath(self.data_dir)}")
        print("=" * 60)
        
        # Default values
        if not years:
            years = ['2024', '2023', '2022']
        if not districts:
            districts = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
        
        all_documents = []
        
        # Search in different districts and years
        for year in years:
            for district in districts:
                if len(all_documents) >= max_documents:
                    break
                    
                print(f"\n🔍 Searching Year: {year}, District: {district}")
                
                # Wait for IP rotation if needed
                time_since_rotation = time.time() - self.last_ip_change
                if time_since_rotation < 4:
                    wait_time = 4 - time_since_rotation
                    print(f"⏳ Waiting {wait_time:.1f}s for IP rotation...")
                    time.sleep(wait_time)
                
                # Search documents
                documents = self.search_documents(district_id=district, year=year)
                remaining_slots = max_documents - len(all_documents)
                all_documents.extend(documents[:remaining_slots])
                
                print(f"📊 Total documents found so far: {len(all_documents)}")
                
                if len(all_documents) >= max_documents:
                    break
        
        # Download documents
        print(f"\n📥 Starting download of {len(all_documents)} documents...")
        
        for i, doc in enumerate(all_documents, 1):
            if i > max_documents:
                break
                
            # Download with IP rotation and error handling
            success = self.download_document(doc, i)
            
            # Wait between downloads
            if i < len(all_documents):
                wait_time = 3 if success else 5  # Wait longer if download failed
                print(f"⏳ Waiting {wait_time} seconds before next download...")
                time.sleep(wait_time)
        
        print("\n" + "=" * 60)
        print(f"✅ Download complete!")
        print(f"   Total downloaded: {self.download_count}")
        print(f"   Documents saved to: {os.path.abspath(self.documents_dir)}")
        print(f"   Metadata saved to: {os.path.abspath(self.metadata_dir)}")
        print(f"   CAPTCHAs saved to: {os.path.abspath(self.captcha_dir)}")
        
        return self.download_count

def main():
    """Main function"""
    print("📄 Enhanced Agreement to Sale Document Downloader")
    print("=" * 60)
    print("This tool downloads Agreement to Sale documents from Maharashtra IGR")
    print("Features:")
    print("✅ Automatic IP rotation every 4 seconds")
    print("✅ IP block detection and instant switching")
    print("✅ CAPTCHA detection and OCR solving")
    print("✅ Bulk download support")
    print("✅ Organized data folder structure")
    print("✅ Metadata tracking")
    print("=" * 60)
    
    downloader = AgreementDownloader()
    
    # You can customize these parameters
    max_docs = int(input("\nHow many documents to download? (default 25): ") or "25")
    
    # Show data folder info
    print(f"\n📁 Data will be saved to: {os.path.abspath(downloader.data_dir)}")
    print(f"   📄 Documents: {downloader.documents_dir}")
    print(f"   📋 Metadata: {downloader.metadata_dir}")
    print(f"   🖼️  CAPTCHAs: {downloader.captcha_dir}")
    
    # Run the bulk download
    count = downloader.run_bulk_download(max_documents=max_docs)
    
    print(f"\n🎉 Successfully downloaded {count} documents!")

if __name__ == "__main__":
    # Disable SSL warnings globally
    import urllib3
    urllib3.disable_warnings()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Disable SSL verification warnings
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Set environment variables for better SSL compatibility
    import os
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Download interrupted by user")
    except (ssl.SSLError, requests.exceptions.SSLError) as e:
        print(f"\n🔐 SSL/TLS Error: {e}")
        print("💡 Try running with different network or VPN connection")
    except requests.exceptions.ConnectionError as e:
        print(f"\n🌐 Connection Error: {e}")
        print("💡 Check your internet connection and try again")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 