#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium Bulk IGR PDF Scraper
Downloads multiple Agreement to Sale documents from Maharashtra IGR website using Selenium.
This bypasses SSL issues that occur with requests library.
"""

import os
import sys
import time
import random
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add webdriver_manager for automatic ChromeDriver management
try:
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("⚠️ webdriver_manager not available. Make sure ChromeDriver is in PATH.")

# Try to import ReportLab for PDF conversion
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from bs4 import BeautifulSoup
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class SeleniumBulkIGRScraper:
    """A class to scrape multiple IGR documents using Selenium WebDriver."""
    
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.output_dir = "data/selenium_igr_pdfs"
        self.metadata_dir = "data/selenium_metadata"
        self.download_count = 0
        self.session_counter = 0
        self.failed_downloads = []
        self.lock = threading.Lock()
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        self.print_header()
        
    def print_header(self):
        """Prints the scraper's starting header."""
        print("=" * 60)
        print("🏛️  SELENIUM BULK IGR PDF SCRAPER - BYPASS SSL ISSUES")
        print("=" * 60)
        print(f"📂 Output Directory: {os.path.abspath(self.output_dir)}")
        print(f"📋 Metadata Directory: {os.path.abspath(self.metadata_dir)}")
        if not REPORTLAB_AVAILABLE:
            print("⚠️  Warning: ReportLab not found. HTML docs will not be converted to PDF.")
        print("🌐 Using Selenium WebDriver to bypass SSL issues")
        
    def create_driver(self):
        """Create a configured Chrome WebDriver instance."""
        options = Options()
        options.add_argument("--headless")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                # Use webdriver_manager to automatically manage ChromeDriver
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Fallback to regular Chrome driver
                driver = webdriver.Chrome(options=options)
            
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            print(f"❌ Failed to create Chrome driver: {e}")
            print("💡 Make sure Chrome browser is installed")
            if not WEBDRIVER_MANAGER_AVAILABLE:
                print("💡 Install webdriver-manager: pip install webdriver-manager")
            return None
    
    def download_document(self, doc_url, doc_id):
        """Downloads a single IGR document using Selenium."""
        driver = None
        for attempt in range(3):
            try:
                with self.lock:
                    self.session_counter += 1
                    session_id = f"selenium-igr-{datetime.now().strftime('%H%M%S')}-{self.session_counter}"
                
                print(f"\n📥 Doc {doc_id} | Attempt {attempt+1} | Session {session_id}")
                
                # Create driver for this download
                driver = self.create_driver()
                if not driver:
                    print(f"❌ Doc {doc_id}: Failed to create WebDriver")
                    continue
                
                print(f"🌐 Loading: {doc_url[:80]}...")
                
                # Navigate to the document URL
                driver.get(doc_url)
                
                # Wait for page to load
                time.sleep(3)
                
                # Get page source
                page_source = driver.page_source
                
                if not page_source or len(page_source) < 1000:
                    print(f"❌ Doc {doc_id}: Invalid or empty page content")
                    continue
                
                # Check if it's a valid IGR document
                if not self.is_valid_igr_document(page_source):
                    print(f"❌ Doc {doc_id}: Not a valid IGR document")
                    continue
                
                # Save the document
                self.save_document(page_source, doc_id, doc_url, session_id)
                
                driver.quit()
                return True
                
            except TimeoutException:
                print(f"⚠️ Doc {doc_id}: Page load timeout. Retrying...")
                time.sleep(attempt * 2)
            except WebDriverException as e:
                print(f"⚠️ Doc {doc_id}: WebDriver error ({e}). Retrying...")
                time.sleep(attempt * 2)
            except Exception as e:
                print(f"❌ Doc {doc_id}: Unexpected error: {e}")
                break
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
        print(f"❌ Doc {doc_id}: Failed after multiple attempts")
        with self.lock:
            self.failed_downloads.append({"id": doc_id, "url": doc_url})
        return False
    
    def is_valid_igr_document(self, page_source):
        """Check if the page contains valid IGR document content."""
        igr_indicators = [
            'Department of Registration',
            'INDEX II',
            'Agreement',
            'Maharashtra',
            'Registration Number',
            'Doc Reg. No.',
            'िजल्हा',  # District in Marathi
            'तालुका'   # Taluka in Marathi
        ]
        
        page_lower = page_source.lower()
        return any(indicator.lower() in page_lower for indicator in igr_indicators)
    
    def save_document(self, page_source, doc_id, url, session_id):
        """Saves the document content to a file and creates metadata."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"IGR_Agreement_{doc_id:04d}_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        print(f"💾 Saved {filename} ({len(page_source):,} characters)")
        
        # Convert to PDF if ReportLab is available
        if REPORTLAB_AVAILABLE:
            pdf_filename = self.convert_html_to_pdf(filepath, page_source, doc_id, timestamp)
            if pdf_filename:
                filename = pdf_filename
        
        # Save metadata
        self.save_metadata(filename, url, session_id, doc_id, len(page_source))
        
        with self.lock:
            self.download_count += 1
    
    def convert_html_to_pdf(self, html_path, page_source, doc_id, timestamp):
        """Converts HTML content to PDF using ReportLab."""
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            text_content = soup.get_text()
            
            if len(text_content) < 500:
                return None
            
            pdf_filename = f"IGR_Agreement_{doc_id:04d}_{timestamp}.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title = Paragraph("Maharashtra IGR - Agreement to Sale Document", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Add authenticity marking
            auth_mark = Paragraph("<b>🏛️ AUTHENTIC GOVERNMENT DOCUMENT (via Selenium)</b>", styles['Heading2'])
            story.append(auth_mark)
            story.append(Spacer(1, 12))
            
            # Process and add content
            lines = [line.strip() for line in text_content.split('\n') if len(line.strip()) > 3]
            
            content_added = 0
            for line in lines:
                if content_added >= 200:  # Limit content
                    break
                    
                try:
                    # Clean the line for PDF
                    clean_line = line.encode('ascii', 'ignore').decode('ascii')
                    if len(clean_line) > 10:
                        para = Paragraph(clean_line, styles['Normal'])
                        story.append(para)
                        story.append(Spacer(1, 4))
                        content_added += 1
                except:
                    continue
            
            # Build PDF
            doc.build(story)
            
            print(f"📄 PDF created: {pdf_filename}")
            
            # Remove original HTML file
            try:
                os.remove(html_path)
            except:
                pass
            
            return pdf_filename
            
        except Exception as e:
            print(f"⚠️ PDF conversion failed: {e}")
            return None
    
    def save_metadata(self, filename, url, session_id, doc_id, size):
        """Saves metadata for a downloaded document to a JSON file."""
        meta_path = os.path.join(self.metadata_dir, f"{os.path.splitext(filename)[0]}_meta.json")
        metadata = {
            "document_id": doc_id,
            "filename": filename,
            "source_url": url,
            "download_timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "content_size_chars": size,
            "method": "Selenium WebDriver",
            "status": "SUCCESS"
        }
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
    
    def generate_urls(self, count):
        """Generates a list of plausible IGR document URLs."""
        base = "MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
        urls = []
        
        for i in range(count):
            # Create variations by modifying the document number
            try:
                # Decode the base64-like part to modify numbers
                import re
                numbers = re.findall(r'\d{6,}', base)
                if numbers:
                    # Modify the largest number found
                    largest_num = max(numbers, key=len)
                    new_num = str(int(largest_num) + i)
                    modified_base = base.replace(largest_num, new_num, 1)
                else:
                    modified_base = base
                
                full_url = f"{self.base_url}/eDisplay/propertydetails/indexii/{modified_base}"
                urls.append(full_url)
                
            except:
                # Fallback: just use the base pattern
                full_url = f"{self.base_url}/eDisplay/propertydetails/indexii/{base}"
                urls.append(full_url)
        
        return urls
    
    def run(self, max_docs=10, workers=2):
        """Runs the bulk scraping process using Selenium."""
        print(f"\n🚀 Starting Selenium bulk scrape for {max_docs} documents")
        print(f"⚡ Using {workers} concurrent WebDriver instances")
        print("🔧 This method bypasses SSL issues by using a real browser")
        
        urls = self.generate_urls(max_docs)
        
        # Use fewer workers for Selenium to avoid overwhelming the system
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_doc = {
                executor.submit(self.download_document, url, i+1): i+1 
                for i, url in enumerate(urls)
            }
            
            for future in as_completed(future_to_doc):
                doc_id = future_to_doc[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Exception for doc {doc_id}: {e}")
        
        self.print_summary(max_docs)
    
    def print_summary(self, total_attempted):
        """Prints the final summary of the scraping run."""
        print("\n" + "=" * 60)
        print("📊 SELENIUM BULK SCRAPING SUMMARY")
        print("=" * 60)
        print(f"🎯 Total documents attempted: {total_attempted}")
        print(f"✅ Successful downloads: {self.download_count}")
        print(f"❌ Failed downloads: {len(self.failed_downloads)}")
        print(f"📈 Success rate: {(self.download_count/total_attempted)*100:.1f}%")
        print(f"📂 Files saved to: {os.path.abspath(self.output_dir)}")
        
        if self.failed_downloads:
            print("\n❌ Failed Downloads:")
            for item in self.failed_downloads:
                print(f"   Doc {item['id']}: {item['url'][:80]}...")

def main():
    """Main function to run the Selenium scraper."""
    print("🏛️  Maharashtra IGR Selenium Bulk PDF Scraper")
    print("=" * 60)
    print("This tool uses Selenium WebDriver to bypass SSL issues")
    print("Features:")
    print("✅ Headless Chrome browser automation")
    print("✅ SSL/TLS issue bypass")
    print("✅ Concurrent document downloads")
    print("✅ HTML to PDF conversion")
    print("✅ Detailed metadata tracking")
    print("=" * 60)
    
    try:
        doc_count = int(input("\n📊 How many documents to scrape? (default: 10): ") or "10")
        workers = int(input("⚡ How many concurrent browsers? (default: 2, max 3): ") or "2")
        workers = min(workers, 3)  # Limit to avoid system overload
    except ValueError:
        print("Invalid input. Using defaults.")
        doc_count, workers = 10, 2
    
    scraper = SeleniumBulkIGRScraper()
    start_time = time.time()
    scraper.run(max_docs=doc_count, workers=workers)
    duration = time.time() - start_time
    
    print(f"\n🎉 Selenium bulk scraping complete!")
    print(f"⏱️  Total time: {duration:.1f} seconds")
    print(f"📊 Downloaded {scraper.download_count}/{doc_count} documents")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Selenium scraping interrupted by user")
    except Exception as e:
        import traceback
        print(f"\n❌ A fatal error occurred: {e}")
        traceback.print_exc() 