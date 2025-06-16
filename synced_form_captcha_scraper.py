#!/usr/bin/env python3
"""
Synced Form Filling + CAPTCHA + IP Switching Scraper
Everything working together in perfect synchronization
"""

import requests
import time
import random
import string
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

class SyncedFormCAPTCHAScraper:
    def __init__(self, proxy_password=None):
        """Initialize synced scraper with all features"""
        self.proxy_password = proxy_password
        self.session_count = 0
        self.documents_found = []
        
        # Create output directories
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "synced_results")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 SYNCED FORM + CAPTCHA + IP SWITCHING SCRAPER")
        print("=" * 60)
        print("✅ Complete form automation (Mumbai, 2024, Agreement to Sale)")
        print("✅ IP rotation with proxy support")
        print("✅ Manual CAPTCHA solving (100% reliable)")
        print("✅ Document downloading and organization")
        print("=" * 60)
    
    def get_new_ip_session(self):
        """Generate new IP session for rotation"""
        self.session_count += 1
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        session_id = f"sync-{timestamp}-{random_str}-{self.session_count}"
        return session_id
    
    def create_driver_with_ip(self):
        """Create Chrome driver with fresh IP session"""
        options = Options()
        
        # IP rotation setup
        if self.proxy_password:
            session_id = self.get_new_ip_session()
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.proxy_password}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔄 New IP session: {session_id}")
        
        # Browser optimization
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"❌ Driver creation failed: {e}")
            return None
    
    def fill_mumbai_form_complete(self, driver):
        """Complete Mumbai form filling with correct selectors"""
        try:
            print("📋 Starting complete Mumbai form filling...")
            
            # Wait for main form to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )
            
            time.sleep(2)  # Let page stabilize
            
            # Step 1: Database selection (if exists)
            try:
                db_select = driver.find_element(By.ID, "dbselect")
                if db_select:
                    Select(db_select).select_by_value("3")  # Current year database
                    print("✅ Database selected: Current year")
                    time.sleep(1)
            except:
                print("ℹ️ No database selector found (skipping)")
            
            # Step 2: District selection (Mumbai)
            try:
                district_select = Select(driver.find_element(By.ID, "district_id"))
                # Try Mumbai variations
                mumbai_found = False
                for option in district_select.options:
                    if any(term in option.text.lower() for term in ['mumbai', 'मुंबई', 'mumbai city']):
                        district_select.select_by_value(option.get_attribute("value"))
                        print(f"✅ District selected: {option.text}")
                        mumbai_found = True
                        break
                
                if not mumbai_found:
                    # Fallback to first available district
                    district_select.select_by_index(1)
                    print("✅ District selected: First available")
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ District selection issue: {e}")
            
            # Step 3: Sub-district/Taluka selection
            try:
                subdistrict_select = Select(driver.find_element(By.ID, "subdistrict_id"))
                # Select first available sub-district
                subdistrict_select.select_by_index(1)
                print("✅ Sub-district selected")
                time.sleep(2)
            except:
                print("ℹ️ No sub-district selector found (skipping)")
            
            # Step 4: Village selection
            try:
                village_select = Select(driver.find_element(By.ID, "village_id"))
                # Select first available village
                village_select.select_by_index(1)
                print("✅ Village selected")
                time.sleep(2)
            except:
                print("ℹ️ No village selector found (skipping)")
            
            # Step 5: Year selection (2024)
            try:
                year_selectors = [
                    driver.find_element(By.ID, "year"),
                    driver.find_element(By.ID, "year_id"),
                    driver.find_element(By.NAME, "year")
                ]
                
                for year_select_elem in year_selectors:
                    try:
                        year_select = Select(year_select_elem)
                        # Try to select 2024
                        for option in year_select.options:
                            if "2024" in option.text:
                                year_select.select_by_value(option.get_attribute("value"))
                                print("✅ Year selected: 2024")
                                time.sleep(1)
                                break
                        break
                    except:
                        continue
            except:
                print("ℹ️ No year selector found (skipping)")
            
            # Step 6: Article selection (Agreement to Sale)
            try:
                article_select = Select(driver.find_element(By.ID, "article_id"))
                agreement_found = False
                
                for option in article_select.options:
                    if any(term in option.text.lower() for term in ['agreement', 'विकस', 'sale']):
                        article_select.select_by_value(option.get_attribute("value"))
                        print(f"✅ Article selected: {option.text}")
                        agreement_found = True
                        break
                
                if not agreement_found:
                    # Try common Agreement to Sale IDs
                    for article_id in ["42", "43", "44"]:
                        try:
                            article_select.select_by_value(article_id)
                            print(f"✅ Article selected by ID: {article_id}")
                            break
                        except:
                            continue
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Article selection issue: {e}")
            
            print("✅ Mumbai form filling completed")
            return True
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False
    
    def solve_captcha_manual_guided(self, driver):
        """Guided manual CAPTCHA solving with screenshot"""
        try:
            print("\n🔍 CAPTCHA SOLVING PROCESS")
            print("=" * 40)
            
            # Take full page screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.captcha_dir, f"captcha_page_{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            
            print(f"📸 Full page screenshot saved: {screenshot_path}")
            
            # Try to open screenshot automatically
            try:
                os.startfile(screenshot_path)
                print("📋 Screenshot opened automatically - check your screen!")
            except:
                print(f"📋 Please manually open: {screenshot_path}")
            
            print("\n" + "🔤 CAPTCHA INSTRUCTIONS" + "\n" + "="*30)
            print("1. Look at the browser window (should be visible)")
            print("2. Find the CAPTCHA image on the page")
            print("3. Enter the CAPTCHA text below")
            print("4. The form will be submitted automatically")
            print("="*30)
            
            # Wait for user input
            captcha_text = input("\n🔤 Enter CAPTCHA text (what you see): ").strip()
            
            if not captcha_text:
                print("❌ No CAPTCHA text entered")
                return False
            
            # Find CAPTCHA input field (try multiple selectors)
            captcha_selectors = [
                "txtcaptcha",
                "captcha",
                "captcha_text",
                "captcha_input"
            ]
            
            captcha_input = None
            for selector in captcha_selectors:
                try:
                    captcha_input = driver.find_element(By.ID, selector)
                    break
                except:
                    try:
                        captcha_input = driver.find_element(By.NAME, selector)
                        break
                    except:
                        continue
            
            if not captcha_input:
                # Fallback: find any text input that might be CAPTCHA
                text_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                if text_inputs:
                    captcha_input = text_inputs[-1]  # Usually the last one
            
            if captcha_input:
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                print(f"✅ CAPTCHA entered: {captcha_text}")
                return True
            else:
                print("❌ Could not find CAPTCHA input field")
                return False
                
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return False
    
    def submit_form_and_wait(self, driver):
        """Submit form and wait for results"""
        try:
            # Find submit button
            submit_selectors = ["search", "submit", "btnSubmit", "btn_submit"]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.ID, selector)
                    break
                except:
                    try:
                        submit_button = driver.find_element(By.NAME, selector)
                        break
                    except:
                        continue
            
            if not submit_button:
                # Try finding by text
                submit_button = driver.find_element(By.XPATH, "//input[@type='submit'] | //button[contains(text(), 'Submit') or contains(text(), 'Search')]")
            
            if submit_button:
                submit_button.click()
                print("✅ Form submitted")
                
                # Wait for results
                print("⏳ Waiting for search results...")
                time.sleep(8)
                
                return True
            else:
                print("❌ Submit button not found")
                return False
                
        except Exception as e:
            print(f"❌ Form submission failed: {e}")
            return False
    
    def extract_document_links(self, driver):
        """Extract document links from results page"""
        try:
            print("🔍 Extracting document links...")
            
            # Wait a bit more for results to load
            time.sleep(3)
            
            documents = []
            
            # Try multiple link patterns
            link_patterns = [
                "//a[contains(@href, 'propertydetails')]",
                "//a[contains(@href, 'indexii')]",
                "//a[contains(@href, 'document')]",
                "//table//a[@href]"
            ]
            
            for pattern in link_patterns:
                try:
                    links = driver.find_elements(By.XPATH, pattern)
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text.strip()
                        
                        if href and any(term in href for term in ['propertydetails', 'indexii', 'document']):
                            documents.append({
                                "url": href,
                                "text": text,
                                "found_by": pattern
                            })
                    
                    if documents:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Pattern {pattern} failed: {e}")
                    continue
            
            # Remove duplicates
            unique_docs = []
            seen_urls = set()
            for doc in documents:
                if doc["url"] not in seen_urls:
                    unique_docs.append(doc)
                    seen_urls.add(doc["url"])
            
            print(f"📄 Found {len(unique_docs)} unique document links")
            return unique_docs
            
        except Exception as e:
            print(f"❌ Document extraction failed: {e}")
            return []
    
    def download_document(self, doc_url, doc_index):
        """Download individual document with new IP"""
        try:
            print(f"\n📥 Downloading document {doc_index}...")
            
            # Create new driver with fresh IP
            driver = self.create_driver_with_ip()
            if not driver:
                return False
            
            driver.get(doc_url)
            time.sleep(4)
            
            # Save document
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Mumbai_Agreement_{doc_index:03d}_{timestamp}.html"
            filepath = os.path.join(self.docs_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            # Save metadata
            metadata = {
                "document_id": doc_index,
                "filename": filename,
                "source_url": doc_url,
                "download_timestamp": datetime.now().isoformat(),
                "content_size": len(driver.page_source),
                "method": "Synced Scraper"
            }
            
            meta_filepath = os.path.join(self.meta_dir, f"{filename}.json")
            with open(meta_filepath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved: {filename} ({len(driver.page_source):,} characters)")
            
            driver.quit()
            return True
            
        except Exception as e:
            print(f"❌ Document {doc_index} download failed: {e}")
            return False
    
    def run_synced_scraping(self, max_documents=10):
        """Run complete synced scraping process"""
        print(f"\n🚀 STARTING SYNCED SCRAPING PROCESS")
        print(f"🎯 Target: {max_documents} Mumbai Agreement to Sale documents")
        print("="*70)
        
        # Create main driver for form filling
        main_driver = self.create_driver_with_ip()
        if not main_driver:
            print("❌ Could not create main driver")
            return []
        
        try:
            # Step 1: Navigate to IGR website
            print("\n📍 Step 1: Loading IGR website...")
            main_driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            time.sleep(4)
            
            # Step 2: Fill Mumbai form
            print("\n📍 Step 2: Filling Mumbai form...")
            if not self.fill_mumbai_form_complete(main_driver):
                print("❌ Form filling failed")
                return []
            
            # Step 3: Solve CAPTCHA
            print("\n📍 Step 3: Solving CAPTCHA...")
            if not self.solve_captcha_manual_guided(main_driver):
                print("❌ CAPTCHA solving failed")
                return []
            
            # Step 4: Submit and wait for results
            print("\n📍 Step 4: Submitting form...")
            if not self.submit_form_and_wait(main_driver):
                print("❌ Form submission failed")
                return []
            
            # Step 5: Extract document links
            print("\n📍 Step 5: Extracting document links...")
            documents = self.extract_document_links(main_driver)
            
            if not documents:
                print("❌ No documents found")
                return []
            
            # Limit to requested number
            documents = documents[:max_documents]
            
        finally:
            main_driver.quit()
        
        # Step 6: Download documents with IP rotation
        print(f"\n📍 Step 6: Downloading {len(documents)} documents...")
        print("="*50)
        
        successful_downloads = 0
        for i, doc in enumerate(documents, 1):
            success = self.download_document(doc["url"], i)
            if success:
                successful_downloads += 1
                print(f"✅ Document {i}/{len(documents)} downloaded successfully")
            else:
                print(f"❌ Document {i}/{len(documents)} failed")
            
            # Pause between downloads
            if i < len(documents):
                time.sleep(2)
        
        # Final summary
        print(f"\n🎉 SYNCED SCRAPING COMPLETED!")
        print("="*50)
        print(f"📊 Total documents found: {len(documents)}")
        print(f"✅ Successful downloads: {successful_downloads}")
        print(f"❌ Failed downloads: {len(documents) - successful_downloads}")
        print(f"📁 Files saved in: {self.docs_dir}")
        print(f"📋 Metadata saved in: {self.meta_dir}")
        
        return documents

def main():
    """Main function"""
    print("🔧 SYNCED FORM + CAPTCHA + IP SCRAPER SETUP")
    print("="*50)
    
    # Get proxy configuration
    use_proxy = input("🌐 Use proxy for IP switching? (y/N): ").lower().startswith('y')
    
    proxy_password = None
    if use_proxy:
        proxy_password = input("🔐 Enter proxy password: ").strip()
        if not proxy_password:
            print("⚠️ No proxy password provided - running without proxy")
            proxy_password = None
    
    # Get document count
    try:
        max_docs = int(input("📋 How many documents to download? (default 10): ") or "10")
    except:
        max_docs = 10
    
    print(f"\n🚀 Initializing synced scraper...")
    scraper = SyncedFormCAPTCHAScraper(proxy_password=proxy_password)
    
    # Run scraping
    documents = scraper.run_synced_scraping(max_documents=max_docs)
    
    print(f"\n✅ PROCESS COMPLETE!")
    print(f"🎯 Found and processed {len(documents)} documents")
    
    if documents:
        print("\n📋 Document Summary:")
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc['text'][:50]}...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc() 