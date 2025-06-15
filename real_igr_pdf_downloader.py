#!/usr/bin/env python3
"""
Real IGR Document Downloader (PDF Format)
Downloads actual Agreement to Sale documents from Maharashtra IGR website and saves as PDF
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
import base64
import re
from urllib.parse import urljoin, unquote
from weasyprint import HTML, CSS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# Disable SSL warnings
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Proxy configuration
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'iyHxHphyuy3i'
}

class RealIGRPDFDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Data directories
        self.data_dir = 'data'
        self.documents_dir = os.path.join(self.data_dir, 'documents_pdf')
        self.metadata_dir = os.path.join(self.data_dir, 'metadata')
        self.html_cache_dir = os.path.join(self.data_dir, 'html_cache')
        
        # Counters
        self.download_count = 0
        self.last_ip_change = time.time()
        self.session_id = None
        
        # Create directories
        self.create_directories()
        
    def create_directories(self):
        """Create necessary directories"""
        directories = [self.data_dir, self.documents_dir, self.metadata_dir, self.html_cache_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created/verified directory: {directory}")
    
    def get_new_session_id(self):
        """Generate new session ID for IP rotation"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"igr-{random_id}-{timestamp}"
    
    def get_proxy(self):
        """Get proxy configuration with IP rotation"""
        current_time = time.time()
        
        # Change IP every 4 seconds
        if not self.session_id or (current_time - self.last_ip_change) >= 4:
            self.session_id = self.get_new_session_id()
            self.last_ip_change = current_time
            print(f"🔄 IP rotation - Session: {self.session_id}")
        
        # Build proxy URL
        full_username = f"{PROXY_CONFIG['username']}-sessid-{self.session_id}"
        proxy_url = f"http://{full_username}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    def make_request(self, url, method='GET', **kwargs):
        """Make HTTP request with error handling and retries"""
        for attempt in range(3):
            try:
                # Try with proxy first
                kwargs['proxies'] = self.get_proxy()
                kwargs['verify'] = False
                kwargs['timeout'] = 15
                kwargs['headers'] = self.headers
                
                if method == 'GET':
                    response = self.session.get(url, **kwargs)
                else:
                    response = self.session.post(url, **kwargs)
                
                if response.status_code == 200:
                    return response
                    
            except Exception as e:
                print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
                    continue
        
        # Final attempt without proxy
        try:
            kwargs.pop('proxies', None)
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            else:
                response = self.session.post(url, **kwargs)
            return response
        except Exception as e:
            print(f"❌ All attempts failed: {e}")
            return None
    
    def search_real_documents(self, year='2025', district_id='052'):
        """Search for real IGR documents"""
        print(f"\n🔍 Searching real documents - Year: {year}, District: {district_id}")
        
        try:
            # Load the search page
            response = self.make_request(self.search_url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Prepare search form data (based on IGR website structure)
            form_data = {
                'dbselect': '3',  # Current year database
                'district_id': district_id,
                'article_id': '31',  # Sale deed
                'year': year,
            }
            
            # Extract any hidden fields or CSRF tokens
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for inp in hidden_inputs:
                name = inp.get('name')
                value = inp.get('value', '')
                if name and name not in form_data:
                    form_data[name] = value
            
            print("📤 Submitting search to IGR...")
            response = self.make_request(self.search_url, method='POST', data=form_data)
            
            if response:
                return self.extract_real_document_links(response.text)
            else:
                return []
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def extract_real_document_links(self, html):
        """Extract real document links from IGR search results"""
        soup = BeautifulSoup(html, 'html.parser')
        documents = []
        
        # Look for document links in tables (common IGR pattern)
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) > 2:
                    # Look for links in the row
                    links = row.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        if href and ('indexii' in href or 'property' in href.lower()):
                            doc_url = urljoin(self.base_url, href)
                            
                            # Extract document details from cells
                            doc_text = ' | '.join(cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True))
                            
                            documents.append({
                                'url': doc_url,
                                'text': doc_text[:200],  # Limit text length
                                'href': href,
                                'type': 'real_igr_doc'
                            })
        
        # Also look for direct links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if href and ('indexii' in href or 'propertydetails' in href):
                doc_url = urljoin(self.base_url, href)
                if doc_url not in [d['url'] for d in documents]:
                    documents.append({
                        'url': doc_url,
                        'text': link.get_text(strip=True)[:100],
                        'href': href,
                        'type': 'real_igr_doc'
                    })
        
        print(f"📄 Found {len(documents)} real IGR documents")
        return documents
    
    def download_real_document_as_pdf(self, doc_info, index):
        """Download a real IGR document and convert to PDF"""
        url = doc_info['url']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Extract document ID from URL if possible
        doc_id = self.extract_document_id(url)
        filename = f"igr_agreement_{index:04d}_{doc_id}_{timestamp}.pdf"
        pdf_filepath = os.path.join(self.documents_dir, filename)
        html_filepath = os.path.join(self.html_cache_dir, filename.replace('.pdf', '.html'))
        
        try:
            print(f"\n📥 Downloading real IGR document {index}: {doc_info['text'][:50]}...")
            print(f"🔗 URL: {url}")
            
            # Download the HTML content
            response = self.make_request(url)
            if not response:
                print(f"❌ Failed to download from {url}")
                return False
            
            # Save HTML for debugging
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Parse the content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Clean up the HTML for better PDF conversion
            cleaned_html = self.clean_html_for_pdf(soup, url)
            
            # Convert to PDF using multiple methods
            success = False
            
            # Method 1: Try WeasyPrint (best quality)
            try:
                print("📄 Converting to PDF using WeasyPrint...")
                
                # Create CSS for better formatting
                css_style = CSS(string='''
                    @page {
                        margin: 1cm;
                        size: A4;
                    }
                    body {
                        font-family: Arial, sans-serif;
                        font-size: 12px;
                        line-height: 1.4;
                        color: #333;
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        margin-bottom: 10px;
                    }
                    td, th {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 20px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                ''')
                
                HTML(string=cleaned_html).write_pdf(pdf_filepath, stylesheets=[css_style])
                success = True
                print("✅ PDF created successfully using WeasyPrint")
                
            except Exception as e:
                print(f"⚠️  WeasyPrint failed: {e}")
                
                # Method 2: Fallback to ReportLab
                try:
                    print("📄 Converting to PDF using ReportLab...")
                    self.create_pdf_with_reportlab(soup, pdf_filepath, doc_info, url)
                    success = True
                    print("✅ PDF created successfully using ReportLab")
                    
                except Exception as e:
                    print(f"❌ ReportLab also failed: {e}")
            
            if success:
                self.download_count += 1
                print(f"✅ Saved: {filename}")
                
                # Save metadata
                metadata = {
                    'filename': filename,
                    'document_id': doc_id,
                    'url': url,
                    'text': doc_info['text'],
                    'downloaded_at': datetime.now().isoformat(),
                    'session_id': self.session_id,
                    'file_size': os.path.getsize(pdf_filepath) if os.path.exists(pdf_filepath) else 0,
                    'download_index': index,
                    'conversion_method': 'WeasyPrint' if 'WeasyPrint' in str(success) else 'ReportLab'
                }
                
                meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Failed to download document {index}: {e}")
            return False
    
    def extract_document_id(self, url):
        """Extract document ID from IGR URL"""
        try:
            # IGR URLs often have encoded IDs
            parts = url.split('/')
            for part in parts:
                if len(part) > 20 and '=' in part:
                    # Try to decode base64 encoded parts
                    try:
                        decoded = base64.b64decode(part + '==').decode('utf-8')
                        if decoded.isdigit() or 'IGR' in decoded.upper():
                            return decoded.replace('/', '_')[:20]
                    except:
                        pass
                    return part[:20]  # Use first 20 chars if can't decode
            
            # Fallback: use timestamp
            return f"DOC{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        except:
            return f"DOC{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def clean_html_for_pdf(self, soup, url):
        """Clean HTML content for better PDF conversion"""
        # Remove scripts and styles that might interfere
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Add document header
        header = soup.new_tag('div', class_='header')
        header.string = f"Agreement to Sale Document - Downloaded from Maharashtra IGR\n{url}\nDownloaded on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if soup.body:
            soup.body.insert(0, header)
        
        # Ensure proper HTML structure
        if not soup.html:
            html_tag = soup.new_tag('html')
            html_tag.append(soup)
            soup = html_tag
        
        if not soup.head:
            head_tag = soup.new_tag('head')
            soup.html.insert(0, head_tag)
        
        # Add meta tags
        meta_charset = soup.new_tag('meta', charset='utf-8')
        soup.head.append(meta_charset)
        
        title_tag = soup.new_tag('title')
        title_tag.string = "Agreement to Sale Document"
        soup.head.append(title_tag)
        
        return str(soup)
    
    def create_pdf_with_reportlab(self, soup, pdf_filepath, doc_info, url):
        """Create PDF using ReportLab as fallback"""
        doc = SimpleDocTemplate(pdf_filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph("Agreement to Sale Document", title_style))
        story.append(Paragraph(f"Downloaded from Maharashtra IGR", styles['Normal']))
        story.append(Paragraph(f"URL: {url}", styles['Normal']))
        story.append(Paragraph(f"Downloaded on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Extract and add content
        text_content = soup.get_text()
        paragraphs = text_content.split('\n')
        
        for para in paragraphs:
            para = para.strip()
            if para:
                story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
    
    def run_download(self, max_documents=25):
        """Run the real IGR document download process"""
        print("📄 Real IGR Document Downloader (PDF Format)")
        print("=" * 60)
        print("Features:")
        print("✅ Downloads real Agreement to Sale documents from Maharashtra IGR")
        print("✅ Converts documents to PDF format")
        print("✅ Automatic IP rotation and proxy support")
        print("✅ Organized data folder structure")
        print("=" * 60)
        
        print(f"\n📁 Data will be saved to: {os.path.abspath(self.data_dir)}")
        print(f"   📄 PDF Documents: {self.documents_dir}")
        print(f"   📋 Metadata: {self.metadata_dir}")
        print(f"   🌐 HTML Cache: {self.html_cache_dir}")
        
        # Start with the provided URL for testing
        test_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
        
        documents = [{
            'url': test_url,
            'text': 'Sample IGR Agreement Document from provided URL',
            'href': '/eDisplay/propertydetails/indexii/MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT',
            'type': 'real_igr_doc'
        }]
        
        # Search for additional documents
        print(f"\n🔍 Searching for additional documents...")
        additional_docs = self.search_real_documents()
        documents.extend(additional_docs[:max_documents-1])  # Keep within limit
        
        print(f"\n🚀 Starting download of {min(len(documents), max_documents)} real IGR documents...")
        
        for i, doc in enumerate(documents[:max_documents], 1):
            success = self.download_real_document_as_pdf(doc, i)
            
            if i < len(documents):
                wait_time = 3 + random.uniform(1, 2)  # Wait 3-5 seconds
                print(f"⏳ Waiting {wait_time:.1f} seconds before next download...")
                time.sleep(wait_time)
        
        print("\n" + "=" * 60)
        print(f"✅ Download complete!")
        print(f"   📄 Total downloaded: {self.download_count}/{min(len(documents), max_documents)}")
        print(f"   📁 PDF documents saved to: {os.path.abspath(self.documents_dir)}")
        print(f"   📋 Metadata saved to: {os.path.abspath(self.metadata_dir)}")
        
        # List downloaded files
        if os.path.exists(self.documents_dir):
            docs = [f for f in os.listdir(self.documents_dir) if f.endswith('.pdf')]
            print(f"\n📄 Downloaded PDF files ({len(docs)}):")
            for i, doc in enumerate(docs[:10], 1):  # Show first 10
                print(f"   {i:2d}. {doc}")
            if len(docs) > 10:
                print(f"   ... and {len(docs) - 10} more files")
        
        return self.download_count

def main():
    """Main function"""
    print("🚀 Starting Real IGR PDF Document Downloader...")
    
    downloader = RealIGRPDFDownloader()
    count = downloader.run_download(max_documents=25)
    
    print(f"\n🎉 Successfully downloaded {count} real IGR documents as PDF files!")
    return count

if __name__ == "__main__":
    try:
        count = main()
        print(f"\n✅ Process completed with {count} PDF documents downloaded!")
    except KeyboardInterrupt:
        print("\n\n👋 Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 