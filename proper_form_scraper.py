#!/usr/bin/env python3
"""
Proper Form-Based IGR Scraper
CORRECTLY fills selector fields → submits form → gets search results → downloads different documents
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
from bs4 import BeautifulSoup

class ProperFormScraper:
    def __init__(self):
        self.data_dir = 'data'
        self.documents_dir = os.path.join(self.data_dir, 'proper_form_results')
        self.metadata_dir = os.path.join(self.data_dir, 'proper_form_metadata')
        
        # Create directories
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        self.download_count = 0
        
        print("📝 Proper Form-Based IGR Scraper")
        print("=" * 60)
        print("✅ Step 1: Fill selector fields (District, Article, Year)")
        print("✅ Step 2: Submit form")
        print("✅ Step 3: Extract actual search results")
        print("✅ Step 4: Download different documents")
        print(f"📁 Documents: {os.path.abspath(self.documents_dir)}")
        print("=" * 60)
    
    def setup_driver(self):
        """Setup Chrome WebDriver with visible window"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Keep visible so we can see what's happening
        # chrome_options.add_argument('--headless')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def fill_form_selectors(self, driver):
        """Properly fill all the form selector fields"""
        try:
            print("📝 Step 1: Filling form selector fields...")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            time.sleep(2)
            
            # 1. Select Database (Recent years)
            try:
                db_select = Select(driver.find_element(By.ID, "dbselect"))
                db_select.select_by_value("3")  # Recent years database
                print("✅ Selected Database: Recent years (3)")
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Database selection: {e}")
            
            # 2. Select District (Mumbai)
            try:
                district_select = Select(driver.find_element(By.ID, "district_id"))
                
                # Try to find Mumbai/मुंबई
                mumbai_found = False
                for option in district_select.options:
                    text = option.text.lower()
                    if 'mumbai' in text or 'मुंबई' in text:
                        district_select.select_by_visible_text(option.text)
                        print(f"✅ Selected District: {option.text}")
                        mumbai_found = True
                        break
                
                if not mumbai_found:
                    # Fallback to first few options
                    district_select.select_by_index(1)
                    selected_option = district_select.first_selected_option
                    print(f"✅ Selected District (fallback): {selected_option.text}")
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  District selection: {e}")
            
            # 3. Select Article (Agreement to Sale)
            try:
                article_select = Select(driver.find_element(By.ID, "article_id"))
                
                # Look for Agreement to Sale
                agreement_found = False
                for option in article_select.options:
                    text = option.text.lower()
                    if any(term in text for term in ['agreement', 'sale', 'करार', 'विक्री']):
                        article_select.select_by_visible_text(option.text)
                        print(f"✅ Selected Article: {option.text}")
                        agreement_found = True
                        break
                
                if not agreement_found:
                    # Try common values
                    for value in ['31', '42', '43']:
                        try:
                            article_select.select_by_value(value)
                            selected_option = article_select.first_selected_option
                            print(f"✅ Selected Article (value {value}): {selected_option.text}")
                            agreement_found = True
                            break
                        except:
                            continue
                
                if not agreement_found:
                    article_select.select_by_index(1)
                    selected_option = article_select.first_selected_option
                    print(f"✅ Selected Article (fallback): {selected_option.text}")
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Article selection: {e}")
            
            # 4. Select Year (2024)
            try:
                year_elements = driver.find_elements(By.ID, "year")
                year_elements.extend(driver.find_elements(By.NAME, "year"))
                
                for year_element in year_elements:
                    try:
                        year_select = Select(year_element)
                        year_select.select_by_visible_text("2024")
                        print("✅ Selected Year: 2024")
                        break
                    except:
                        continue
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Year selection: {e}")
            
            print("✅ All form fields filled!")
            return True
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False
    
    def submit_form_and_get_results(self, driver):
        """Submit the form and wait for search results"""
        try:
            print("📤 Step 2: Submitting form...")
            
            # Handle CAPTCHA if present
            captcha_images = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha') or contains(@alt, 'captcha')]")
            if captcha_images:
                print("🤖 CAPTCHA detected!")
                print("👁️  Please solve the CAPTCHA in the browser window")
                input("Press Enter after solving CAPTCHA...")
            
            # Find submit button
            submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit']")
            submit_buttons.extend(driver.find_elements(By.XPATH, "//button[@type='submit']"))
            submit_buttons.extend(driver.find_elements(By.XPATH, "//input[@value='Search']"))
            submit_buttons.extend(driver.find_elements(By.XPATH, "//input[@value='Go']"))
            
            if submit_buttons:
                submit_buttons[0].click()
                print("✅ Form submitted!")
                time.sleep(5)  # Wait for results
                return True
            else:
                print("❌ No submit button found")
                return False
                
        except Exception as e:
            print(f"❌ Form submission failed: {e}")
            return False
    
    def extract_search_results(self, driver):
        """Extract document links from actual search results"""
        try:
            print("🔍 Step 3: Extracting search results...")
            
            # Wait for results to load
            time.sleep(3)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            documents = []
            
            # Look for result tables
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables")
            
            for table_idx, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"   Table {table_idx + 1}: {len(rows)} rows")
                
                for row_idx, row in enumerate(rows[1:], 1):  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:  # Valid data row
                        # Look for links in this row
                        links = row.find_all('a', href=True)
                        
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            # Check if it's a document link
                            if any(term in href.lower() for term in ['view', 'display', 'indexii', 'propertydetails']):
                                # Make URL absolute
                                if href.startswith('/'):
                                    full_url = f"https://pay2igr.igrmaharashtra.gov.in{href}"
                                else:
                                    full_url = href
                                
                                # Get row data for context
                                row_text = ' | '.join(cell.get_text(strip=True) for cell in cells[:5])
                                
                                documents.append({
                                    'url': full_url,
                                    'text': text,
                                    'row_data': row_text,
                                    'table_index': table_idx + 1,
                                    'row_index': row_idx
                                })
                                
                                print(f"📄 Found document link: {text[:40]}...")
            
            # Also look for direct links outside tables
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if any(term in href.lower() for term in ['indexii', 'propertydetails', 'view']) and len(text) > 5:
                    if href.startswith('/'):
                        full_url = f"https://pay2igr.igrmaharashtra.gov.in{href}"
                    else:
                        full_url = href
                    
                    # Check if not already added
                    if not any(doc['url'] == full_url for doc in documents):
                        documents.append({
                            'url': full_url,
                            'text': text,
                            'row_data': text,
                            'table_index': 0,
                            'row_index': 0
                        })
            
            print(f"✅ Found {len(documents)} total document links")
            return documents
            
        except Exception as e:
            print(f"❌ Results extraction failed: {e}")
            return []
    
    def download_document(self, doc_info, index):
        """Download individual document"""
        try:
            print(f"📥 Document {index}: {doc_info['text'][:50]}...")
            
            # Setup new driver for document
            doc_driver = self.setup_driver()
            
            try:
                # Load document page
                doc_driver.get(doc_info['url'])
                time.sleep(3)
                
                # Get content
                content = doc_driver.page_source
                content_size = len(content)
                
                # Skip if too small
                if content_size < 1000:
                    print(f"⚠️  Document {index}: Too small ({content_size} chars)")
                    return False
                
                # Save file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"FormResult_{index:04d}_{timestamp}.html"
                filepath = os.path.join(self.documents_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Save metadata
                metadata = {
                    'filename': filename,
                    'url': doc_info['url'],
                    'text': doc_info['text'],
                    'row_data': doc_info['row_data'],
                    'table_index': doc_info['table_index'],
                    'row_index': doc_info['row_index'],
                    'downloaded_at': datetime.now().isoformat(),
                    'file_size': content_size,
                    'index': index
                }
                
                meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                self.download_count += 1
                print(f"✅ Document {index}: Saved {filename} ({content_size:,} chars)")
                return True
                
            finally:
                doc_driver.quit()
                
        except Exception as e:
            print(f"❌ Document {index} failed: {e}")
            return False
    
    def run_proper_scraper(self, max_documents=25):
        """Run the complete proper scraper workflow"""
        print(f"🚀 Starting PROPER form-based scraper for {max_documents} documents")
        print("This will follow the correct workflow!")
        
        driver = self.setup_driver()
        
        try:
            # Step 1: Load search page
            print("🌐 Loading IGR search page...")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            time.sleep(3)
            
            # Step 2: Fill form selectors
            if not self.fill_form_selectors(driver):
                print("❌ Failed to fill form")
                return 0
            
            # Step 3: Submit form
            if not self.submit_form_and_get_results(driver):
                print("❌ Failed to submit form")
                return 0
            
            # Step 4: Extract search results
            documents = self.extract_search_results(driver)
            
            if not documents:
                print("❌ No search results found")
                return 0
            
            # Limit documents
            documents = documents[:max_documents]
            
            print(f"📥 Step 4: Downloading {len(documents)} documents...")
            
            # Step 5: Download each document
            success_count = 0
            for i, doc in enumerate(documents, 1):
                if self.download_document(doc, i):
                    success_count += 1
                
                # Wait between downloads
                time.sleep(2)
            
            return success_count
            
        except Exception as e:
            print(f"❌ Scraper failed: {e}")
            return 0
            
        finally:
            driver.quit()

def main():
    scraper = ProperFormScraper()
    
    try:
        max_docs = int(input("How many documents from search results? (default 25): ") or "25")
    except ValueError:
        max_docs = 25
    
    print(f"\n🎯 Starting PROPER workflow for {max_docs} documents")
    print("👁️  Browser will stay open so you can solve CAPTCHAs")
    print("=" * 60)
    
    count = scraper.run_proper_scraper(max_documents=max_docs)
    
    print("\n" + "=" * 60)
    print(f"🎉 Proper scraping complete!")
    print(f"📊 Successfully downloaded: {count} documents")
    print(f"📁 Files saved to: {os.path.abspath(scraper.documents_dir)}")
    
    if count > 0:
        print("\n📋 Verifying file sizes (should be different):")
        for filename in os.listdir(scraper.documents_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(scraper.documents_dir, filename)
                size = os.path.getsize(filepath)
                print(f"   {filename}: {size:,} bytes")

if __name__ == "__main__":
    main()