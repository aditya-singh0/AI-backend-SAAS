#!/usr/bin/env python3
"""
Real Agreement to Sale Scraper
Actually searches and downloads different Agreement to Sale documents
"""

import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
import requests
from bs4 import BeautifulSoup

class RealAgreementScraper:
    def __init__(self):
        self.data_dir = 'data'
        self.documents_dir = os.path.join(self.data_dir, 'real_agreements')
        self.metadata_dir = os.path.join(self.data_dir, 'real_metadata')
        
        # Create directories
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        self.download_count = 0
        
        print("🏛️  Real Agreement to Sale Scraper")
        print("=" * 50)
        print(f"📁 Documents: {os.path.abspath(self.documents_dir)}")
        print(f"📋 Metadata: {os.path.abspath(self.metadata_dir)}")
        print("=" * 50)
    
    def setup_driver(self):
        """Setup Chrome WebDriver with proper options"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Don't use headless mode so we can see what's happening
        # chrome_options.add_argument('--headless')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def wait_for_page_load(self, driver, timeout=10):
        """Wait for page to fully load"""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional wait for dynamic content
            return True
        except:
            return False
    
    def fill_search_form(self, driver):
        """Fill the search form with Agreement to Sale parameters"""
        try:
            print("📝 Filling search form...")
            
            # Wait for form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Select District - Mumbai
            try:
                district_select = Select(driver.find_element(By.ID, "district_id"))
                # Try different Mumbai options
                for option in district_select.options:
                    if 'mumbai' in option.text.lower() or 'मुंबई' in option.text:
                        district_select.select_by_visible_text(option.text)
                        print(f"✅ Selected District: {option.text}")
                        break
                else:
                    district_select.select_by_index(1)  # Fallback to first option
                    print("✅ Selected District: First available")
            except Exception as e:
                print(f"⚠️  District selection failed: {e}")
            
            # Select Article - Agreement to Sale
            try:
                article_select = Select(driver.find_element(By.ID, "article_id"))
                for option in article_select.options:
                    text = option.text.lower()
                    if any(term in text for term in ['agreement', 'sale', 'करार', 'विक्री']):
                        article_select.select_by_visible_text(option.text)
                        print(f"✅ Selected Article: {option.text}")
                        break
                else:
                    # Try by value if text doesn't work
                    for option in article_select.options:
                        if option.get_attribute('value') in ['31', '42', '43']:
                            article_select.select_by_value(option.get_attribute('value'))
                            print(f"✅ Selected Article by value: {option.get_attribute('value')}")
                            break
            except Exception as e:
                print(f"⚠️  Article selection failed: {e}")
            
            # Select Year - 2024
            try:
                year_select = Select(driver.find_element(By.ID, "year") or driver.find_element(By.NAME, "year"))
                year_select.select_by_visible_text("2024")
                print("✅ Selected Year: 2024")
            except Exception as e:
                print(f"⚠️  Year selection failed: {e}")
            
            # Fill any other required fields
            try:
                # Look for database selection
                db_select = driver.find_element(By.ID, "dbselect")
                if db_select:
                    Select(db_select).select_by_value("3")  # Recent years
                    print("✅ Selected Database: Recent years")
            except:
                pass
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False
    
    def handle_captcha(self, driver):
        """Handle CAPTCHA if present"""
        try:
            # Look for CAPTCHA
            captcha_img = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha')]")
            
            if captcha_img:
                print("🤖 CAPTCHA detected!")
                print("👀 Please solve the CAPTCHA manually in the browser window")
                print("⏳ Waiting for you to solve it...")
                
                # Wait for user to solve CAPTCHA
                input("Press Enter after solving the CAPTCHA...")
                return True
            
            return True
            
        except Exception as e:
            print(f"⚠️  CAPTCHA handling failed: {e}")
            return True
    
    def submit_search(self, driver):
        """Submit the search form"""
        try:
            # Handle CAPTCHA first
            if not self.handle_captcha(driver):
                return False
            
            print("📤 Submitting search...")
            
            # Find and click search button
            search_buttons = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button']")
            search_buttons.extend(driver.find_elements(By.XPATH, "//button[@type='submit']"))
            
            for button in search_buttons:
                if any(term in button.get_attribute('value', '').lower() for term in ['search', 'submit', 'go']):
                    button.click()
                    print("✅ Search submitted")
                    time.sleep(3)
                    return True
            
            # Fallback - try any submit button
            if search_buttons:
                search_buttons[0].click()
                print("✅ Search submitted (fallback)")
                time.sleep(3)
                return True
            
            print("❌ No search button found")
            return False
            
        except Exception as e:
            print(f"❌ Search submission failed: {e}")
            return False
    
    def extract_document_links(self, driver):
        """Extract document links from search results"""
        try:
            print("🔍 Extracting document links...")
            
            # Wait for results to load
            time.sleep(5)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            documents = []
            
            # Look for document links in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    links = row.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Check if it's a document link
                        if any(term in href.lower() for term in ['view', 'display', 'document', 'indexii']):
                            full_url = href if href.startswith('http') else f"https://pay2igr.igrmaharashtra.gov.in{href}"
                            documents.append({
                                'url': full_url,
                                'text': text,
                                'row_data': row.get_text(strip=True)
                            })
            
            # Also look for direct links
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(term in href.lower() for term in ['propertydetails', 'indexii', 'view']):
                    full_url = href if href.startswith('http') else f"https://pay2igr.igrmaharashtra.gov.in{href}"
                    if not any(doc['url'] == full_url for doc in documents):
                        documents.append({
                            'url': full_url,
                            'text': text,
                            'row_data': text
                        })
            
            print(f"📄 Found {len(documents)} document links")
            return documents
            
        except Exception as e:
            print(f"❌ Link extraction failed: {e}")
            return []
    
    def download_document(self, doc_info, index):
        """Download a single document"""
        try:
            print(f"📥 Downloading document {index}: {doc_info['text'][:50]}...")
            
            # Setup new driver for this document
            driver = self.setup_driver()
            
            try:
                # Load the document page
                driver.get(doc_info['url'])
                self.wait_for_page_load(driver)
                
                # Get the page content
                content = driver.page_source
                
                # Save HTML file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"Agreement_{index:04d}_{timestamp}.html"
                filepath = os.path.join(self.documents_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Save metadata
                metadata = {
                    'filename': filename,
                    'url': doc_info['url'],
                    'text': doc_info['text'],
                    'row_data': doc_info['row_data'],
                    'downloaded_at': datetime.now().isoformat(),
                    'file_size': len(content),
                    'document_index': index
                }
                
                meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                self.download_count += 1
                print(f"✅ Saved: {filename} ({len(content):,} characters)")
                
                return True
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ Download failed for document {index}: {e}")
            return False
    
    def run_scraper(self, max_documents=10):
        """Run the complete scraper"""
        print(f"🚀 Starting Real Agreement Scraper for {max_documents} documents")
        
        driver = self.setup_driver()
        
        try:
            # Navigate to search page
            print("🌐 Loading IGR search page...")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            if not self.wait_for_page_load(driver):
                print("❌ Page load timeout")
                return 0
            
            # Fill search form
            if not self.fill_search_form(driver):
                print("❌ Form filling failed")
                return 0
            
            # Submit search
            if not self.submit_search(driver):
                print("❌ Search submission failed")
                return 0
            
            # Extract document links
            documents = self.extract_document_links(driver)
            
            if not documents:
                print("❌ No documents found")
                return 0
            
            # Limit to requested number
            documents = documents[:max_documents]
            
            print(f"📥 Starting download of {len(documents)} documents...")
            
            # Download each document
            for i, doc in enumerate(documents, 1):
                success = self.download_document(doc, i)
                if success:
                    print(f"✅ Downloaded {i}/{len(documents)}")
                else:
                    print(f"❌ Failed {i}/{len(documents)}")
                
                # Wait between downloads
                time.sleep(2)
            
            return self.download_count
            
        except Exception as e:
            print(f"❌ Scraper failed: {e}")
            return 0
            
        finally:
            driver.quit()

def main():
    scraper = RealAgreementScraper()
    
    try:
        max_docs = int(input("How many documents to download? (default 10): ") or "10")
    except ValueError:
        max_docs = 10
    
    print(f"\n🎯 Starting scraper for {max_docs} documents")
    print("👀 Browser window will open - you may need to solve CAPTCHAs manually")
    print("=" * 50)
    
    count = scraper.run_scraper(max_documents=max_docs)
    
    print("\n" + "=" * 50)
    print(f"🎉 Scraping complete!")
    print(f"📊 Successfully downloaded: {count} documents")
    print(f"📁 Saved to: {os.path.abspath(scraper.documents_dir)}")

if __name__ == "__main__":
    main()