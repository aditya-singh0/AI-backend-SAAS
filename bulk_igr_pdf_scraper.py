#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk IGR PDF Scraper
Downloads multiple Agreement to Sale documents from Maharashtra IGR website.
"""

import os
import sys
import requests
import ssl
import urllib3
import time
import random
import json
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# --- Configuration ---
# Attempt to import ReportLab for PDF conversion
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Disable SSL warnings for simplicity
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Custom SSL Adapter as suggested
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

# Proxy configuration for IP rotation
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'iyHxHphyuy3i'
}

class BulkIGRScraper:
    """A class to scrape multiple IGR documents from the Maharashtra IGR website."""
    
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.output_dir = "data/bulk_igr_pdfs"
        self.metadata_dir = "data/bulk_metadata"
        self.download_count = 0
        self.session_counter = 0
        self.failed_downloads = []
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        self.print_header()
        
    def print_header(self):
        """Prints the scraper's starting header."""
        print("=" * 60)
        print("🏛️  BULK IGR PDF SCRAPER - AUTHENTIC DOCUMENTS")
        print("=" * 60)
        print(f"📂 Output Directory: {os.path.abspath(self.output_dir)}")
        print(f"📋 Metadata Directory: {os.path.abspath(self.metadata_dir)}")
        if not REPORTLAB_AVAILABLE:
            print("⚠️  Warning: ReportLab not found. HTML docs will not be converted to PDF.")
        
    def get_proxy_session(self):
        """Generates a new proxy session ID and proxy URL."""
        self.session_counter += 1
        session_id = f"bulk-igr-{datetime.now().strftime('%H%M%S')}-{self.session_counter}"
        proxy_user = f"{PROXY_CONFIG['username']}-sessid-{session_id}"
        proxy_url = f"http://{proxy_user}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        return session_id, {"http": proxy_url, "https": proxy_url}
    
    def create_session(self):
        """Create a configured requests session with the custom SSL adapter."""
        session = requests.Session()
        session.mount("https://", SSLAdapter()) # Mount the custom adapter

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        session.headers.update(headers)
        session.verify = False # Still good to keep for some edge cases
        return session

    def download_document(self, doc_url, doc_id):
        """Downloads a single IGR document with retries."""
        for attempt in range(3):
            session_id, proxies = self.get_proxy_session()
            try:
                print(f"\n📥 Doc {doc_id} | Attempt {attempt+1} | Session {session_id}")
                
                # Create a new session for each download to use the adapter
                session = self.create_session()

                with session.get(doc_url, proxies=proxies, timeout=45, verify=False, stream=True) as r:
                    r.raise_for_status()
                    content = r.content
                    content_type = r.headers.get('content-type', '').lower()

                if not content or len(content) < 1000:
                    print(f"❌ Doc {doc_id}: Invalid or empty content.")
                    continue

                self.save_document(content, content_type, doc_id, doc_url, session_id)
                return True

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Doc {doc_id}: Network error ({e}). Retrying...")
                time.sleep(attempt * 2)
            except Exception as e:
                print(f"❌ Doc {doc_id}: An unexpected error occurred: {e}")
                break
        
        print(f"❌ Doc {doc_id}: Failed after multiple attempts.")
        self.failed_downloads.append({"id": doc_id, "url": doc_url})
        return False

    def save_document(self, content, content_type, doc_id, url, session_id):
        """Saves the document content to a file and creates metadata."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = 'pdf' if 'pdf' in content_type else 'html'
        filename = f"IGR_Agreement_{doc_id:04d}_{timestamp}.{ext}"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(content)
        
        print(f"💾 Saved {filename} ({len(content):,} bytes)")

        if ext == 'html' and REPORTLAB_AVAILABLE:
            if self.convert_html_to_pdf(filepath):
                filename = filename.replace('.html', '.pdf')

        self.save_metadata(filename, url, session_id, doc_id, len(content))
        self.download_count += 1
    
    def convert_html_to_pdf(self, html_path):
        """Converts an HTML file to a PDF using ReportLab."""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            pdf_path = html_path.replace('.html', '.pdf')
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            story = [Paragraph("Maharashtra IGR Document", styles['Title'])]
            lines = [line.strip() for line in soup.get_text().split('\n') if len(line.strip()) > 3]
            for line in lines:
                story.append(Paragraph(line.encode('ascii', 'ignore').decode(), styles['Normal']))
                story.append(Spacer(1, 4))
            
            doc.build(story)
            print(f"📄 Converted {os.path.basename(html_path)} to PDF.")
            os.remove(html_path) # remove original html
            return True
        except Exception as e:
            print(f"⚠️ PDF conversion failed for {os.path.basename(html_path)}: {e}")
            return False

    def save_metadata(self, filename, url, session_id, doc_id, size):
        """Saves metadata for a downloaded document to a JSON file."""
        meta_path = os.path.join(self.metadata_dir, f"{os.path.splitext(filename)[0]}_meta.json")
        metadata = {
            "document_id": doc_id, "filename": filename, "source_url": url,
            "download_timestamp": datetime.now().isoformat(), "session_id": session_id,
            "file_size_bytes": size, "status": "SUCCESS"
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
    def generate_urls(self, count):
        """Generates a list of plausible IGR document URLs."""
        base = "MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
        urls = []
        for i in range(count):
            # Slightly change the long number in the URL to get different documents
            new_doc_id = str(11966900 + i)
            modified_base = base.replace("MTE5NjY5MDA", new_doc_id)
            urls.append(f"{self.base_url}/eDisplay/propertydetails/indexii/{modified_base}")
        return urls

    def run(self, max_docs=10, workers=3):
        """Runs the bulk scraping process."""
        print(f"\n🚀 Starting bulk scrape for {max_docs} documents with {workers} workers...")
        urls = self.generate_urls(max_docs)
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_doc = {executor.submit(self.download_document, url, i+1): i+1 for i, url in enumerate(urls)}
            for future in as_completed(future_to_doc):
                future.result() # We just need to wait for it to complete

        self.print_summary(max_docs)
        
    def print_summary(self, total_attempted):
        """Prints the final summary of the scraping run."""
        print("\n" + "=" * 60 + "\n📊 BULK SCRAPING SUMMARY\n" + "=" * 60)
        print(f"🎯 Total documents attempted: {total_attempted}")
        print(f"✅ Successful downloads: {self.download_count}")
        print(f"❌ Failed downloads: {len(self.failed_downloads)}")
        if self.failed_downloads:
            print("Failed URLs:", [item['url'] for item in self.failed_downloads])

def main():
    """Main function to run the scraper."""
    try:
        doc_count = int(input("\n📊 How many documents to scrape? (default: 10): ") or "10")
        workers = int(input("⚡ How many concurrent downloads? (default: 3): ") or "3")
    except ValueError:
        print("Invalid input. Using defaults.")
        doc_count, workers = 10, 3

    scraper = BulkIGRScraper()
    start_time = time.time()
    scraper.run(max_docs=doc_count, workers=workers)
    print(f"⏱️  Total time: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ A fatal error occurred: {e}")
        traceback.print_exc() 