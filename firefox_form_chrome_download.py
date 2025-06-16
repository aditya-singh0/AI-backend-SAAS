#!/usr/bin/env python3
"""
Hybrid Scraper: Firefox for Form Filling + Chrome for Downloads
Firefox handles form filling and IP switching (more stable)
Chrome handles document downloads (faster)
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
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

class HybridFirefoxChromeScraper:
    def __init__(self, proxy_password=None):
        """Initialize hybrid scraper with Firefox + Chrome"""
        self.proxy_password = proxy_password
        self.session_count = 0
        self.documents_found = []
        
        # Create output directories
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "hybrid_results")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 HYBRID FIREFOX + CHROME SCRAPER")
        print("=" * 60)
        print("🦊 Firefox: Form filling + IP switching (stable)")
        print("🔵 Chrome: Document downloads (fast)")
        print("✅ Mumbai 2024 Agreement to Sale automation")
        print("✅ Manual CAPTCHA solving (100% reliable)")
        print("=" * 60)
    
    def get_new_ip_session(self):
        """Generate new IP session for rotation"""
        self.session_count += 1
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        session_id = f"hybrid-{timestamp}-{random_str}-{self.session_count}"
        return session_id
    
    def create_firefox_with_proxy(self):
        """Create Firefox driver with proxy for form filling"""
        options = FirefoxOptions()
        
        # IP rotation setup for Firefox
        if self.proxy_password:
            session_id = self.get_new_ip_session()
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_host = "42q6t9rp.pr.thordata.net"
            proxy_port = "9999"
            
            # Firefox proxy configuration
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxy_host)
            options.set_preference("network.proxy.http_port", int(proxy_port))
            options.set_preference("network.proxy.ssl", proxy_host)
            options.set_preference("network.proxy.ssl_port", int(proxy_port))
            
            # Authentication (will need manual entry for Firefox)
            print(f"🦊 Firefox with proxy session: {session_id}")
            print(f"🔑 Proxy auth: {proxy_user}:{self.proxy_password}")
        
        # Firefox optimization for form filling
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0")
        
        # Keep browser visible for form filling
        # options.add_argument("--headless")  # Commented out to keep visible
        
        try:
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1200, 800)
            return driver
        except Exception as e:
            print(f"❌ Firefox driver creation failed: {e}")
            return None
    
    def create_chrome_for_download(self):
        """Create Chrome driver for fast document downloads"""
        options = ChromeOptions()
        
        # Chrome optimization for downloads
        options.add_argument("--headless")  # Hidden for downloads
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"❌ Chrome driver creation failed: {e}")
            return None
    
    def fill_mumbai_form_firefox(self, driver):
        """Complete Mumbai form filling using Firefox"""
        try:
            print("📋 Firefox: Starting Mumbai form filling...")
            
            # Wait for page to fully load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )
            
            print("✅ Page loaded, starting form filling...")
            time.sleep(3)  # Extra time for page stability
            
            # Step 1: Database selection
            try:
                db_select = driver.find_element(By.ID, "dbselect")
                Select(db_select).select_by_value("3")
                print("✅ Database selected")
                time.sleep(2)
            except:
                print("ℹ️ No database selector found")
            
            # Step 2: District selection (Mumbai)
            try:
                district_select = Select(driver.find_element(By.ID, "district_id"))
                mumbai_selected = False
                
                # Try to find Mumbai in options
                for option in district_select.options:
                    option_text = option.text.lower()
                    if any(term in option_text for term in ['mumbai', 'मुंबई']):
                        district_select.select_by_value(option.get_attribute("value"))
                        print(f"✅ District selected: {option.text}")
                        mumbai_selected = True
                        break
                
                if not mumbai_selected:
                    # Try by value (common Mumbai IDs)
                    for mumbai_id in ["1", "31", "32"]:
                        try:
                            district_select.select_by_value(mumbai_id)
                            print(f"✅ District selected by ID: {mumbai_id}")
                            mumbai_selected = True
                            break
                        except:
                            continue
                
                if not mumbai_selected:
                    district_select.select_by_index(1)
                    print("✅ District selected: First available")
                
                time.sleep(3)  # Wait for dependent dropdowns
            except Exception as e:
                print(f"⚠️ District selection issue: {e}")
            
            # Step 3: Sub-district/Taluka
            try:
                subdistrict_select = Select(driver.find_element(By.ID, "subdistrict_id"))
                subdistrict_select.select_by_index(1)
                print("✅ Sub-district selected")
                time.sleep(2)
            except:
                print("ℹ️ No sub-district selector")
            
            # Step 4: Village selection
            try:
                village_select = Select(driver.find_element(By.ID, "village_id"))
                village_select.select_by_index(1)
                print("✅ Village selected")
                time.sleep(2)
            except:
                print("ℹ️ No village selector")
            
            # Step 5: Year selection (2024)
            try:
                year_selectors = ["year", "year_id", "registration_year"]
                year_selected = False
                
                for year_id in year_selectors:
                    try:
                        year_element = driver.find_element(By.ID, year_id)
                        year_select = Select(year_element)
                        
                        # Try to select 2024
                        for option in year_select.options:
                            if "2024" in option.text:
                                year_select.select_by_value(option.get_attribute("value"))
                                print(f"✅ Year selected: 2024 (using {year_id})")
                                year_selected = True
                                break
                        
                        if year_selected:
                            break
                            
                    except:
                        continue
                
                if not year_selected:
                    print("ℹ️ No year selector found")
                else:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"⚠️ Year selection issue: {e}")
            
            # Step 6: Article selection (Agreement to Sale)
            try:
                article_select = Select(driver.find_element(By.ID, "article_id"))
                agreement_selected = False
                
                # Look for Agreement to Sale in options
                for option in article_select.options:
                    option_text = option.text.lower()
                    if any(term in option_text for term in ['agreement', 'विकस', 'sale']):
                        article_select.select_by_value(option.get_attribute("value"))
                        print(f"✅ Article selected: {option.text}")
                        agreement_selected = True
                        break
                
                if not agreement_selected:
                    # Try common Agreement IDs
                    for article_id in ["42", "43", "44"]:
                        try:
                            article_select.select_by_value(article_id)
                            print(f"✅ Article selected by ID: {article_id}")
                            agreement_selected = True
                            break
                        except:
                            continue
                
                if not agreement_selected:
                    print("⚠️ Could not find Agreement to Sale")
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Article selection issue: {e}")
            
            print("✅ Firefox form filling completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Firefox form filling failed: {e}")
            return False
    
    def solve_captcha_firefox(self, driver):
        """Solve CAPTCHA in Firefox with user interaction"""
        try:
            print("\n🔍 FIREFOX CAPTCHA SOLVING")
            print("=" * 40)
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.captcha_dir, f"firefox_captcha_{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Open screenshot
            try:
                os.startfile(screenshot_path)
                print("📋 Screenshot opened - check your screen!")
            except:
                print(f"📋 Please open: {screenshot_path}")
            
            # Show browser window
            print("\n🦊 FIREFOX CAPTCHA INSTRUCTIONS")
            print("="*35)
            print("1. Firefox browser window should be visible")
            print("2. Look for the CAPTCHA image on the page")
            print("3. Enter the CAPTCHA text below")
            print("="*35)
            
            captcha_text = input("\n🔤 Enter CAPTCHA text: ").strip()
            
            if not captcha_text:
                print("❌ No CAPTCHA text entered")
                return False
            
            # Find CAPTCHA input
            captcha_selectors = ["txtcaptcha", "captcha", "captcha_text"]
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
                # Find any text input (last one usually CAPTCHA)
                text_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                if text_inputs:
                    captcha_input = text_inputs[-1]
            
            if captcha_input:
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                print(f"✅ CAPTCHA entered in Firefox: {captcha_text}")
                return True
            else:
                print("❌ Could not find CAPTCHA input field")
                return False
                
        except Exception as e:
            print(f"❌ Firefox CAPTCHA solving failed: {e}")
            return False
    
    def submit_form_firefox(self, driver):
        """Submit form in Firefox"""
        try:
            # Find submit button
            submit_selectors = ["search", "submit", "btnSubmit"]
            
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.ID, selector)
                    submit_button.click()
                    print("✅ Form submitted in Firefox")
                    time.sleep(8)  # Wait for results
                    return True
                except:
                    continue
            
            # Try by xpath
            try:
                submit_button = driver.find_element(By.XPATH, "//input[@type='submit'] | //button[contains(text(), 'Submit')]")
                submit_button.click()
                print("✅ Form submitted in Firefox (xpath)")
                time.sleep(8)
                return True
            except:
                pass
            
            print("❌ Submit button not found")
            return False
            
        except Exception as e:
            print(f"❌ Firefox form submission failed: {e}")
            return False
    
    def extract_links_firefox(self, driver):
        """Extract document links from Firefox results"""
        try:
            print("🔍 Firefox: Extracting document links...")
            
            time.sleep(5)  # Extra wait for results
            
            documents = []
            
            # Multiple patterns to find links
            patterns = [
                "//a[contains(@href, 'propertydetails')]",
                "//a[contains(@href, 'indexii')]",
                "//table//a[@href]"
            ]
            
            for pattern in patterns:
                try:
                    links = driver.find_elements(By.XPATH, pattern)
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text.strip()
                        
                        if href and any(term in href for term in ['propertydetails', 'indexii']):
                            documents.append({
                                "url": href,
                                "text": text
                            })
                    
                    if documents:
                        break
                        
                except:
                    continue
            
            # Remove duplicates
            unique_docs = []
            seen_urls = set()
            for doc in documents:
                if doc["url"] not in seen_urls:
                    unique_docs.append(doc)
                    seen_urls.add(doc["url"])
            
            print(f"✅ Firefox found {len(unique_docs)} document links")
            return unique_docs
            
        except Exception as e:
            print(f"❌ Firefox link extraction failed: {e}")
            return []
    
    def download_with_chrome(self, doc_url, doc_index):
        """Download document using Chrome (fast and headless)"""
        try:
            print(f"🔵 Chrome: Downloading document {doc_index}...")
            
            # Create Chrome driver for this download
            chrome_driver = self.create_chrome_for_download()
            if not chrome_driver:
                return False
            
            chrome_driver.get(doc_url)
            time.sleep(3)
            
            # Save document
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Hybrid_Document_{doc_index:03d}_{timestamp}.html"
            filepath = os.path.join(self.docs_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(chrome_driver.page_source)
            
            # Save metadata
            metadata = {
                "document_id": doc_index,
                "filename": filename,
                "source_url": doc_url,
                "download_timestamp": datetime.now().isoformat(),
                "content_size": len(chrome_driver.page_source),
                "method": "Hybrid Firefox+Chrome",
                "form_browser": "Firefox",
                "download_browser": "Chrome"
            }
            
            meta_filepath = os.path.join(self.meta_dir, f"{filename}.json")
            with open(meta_filepath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Chrome saved: {filename} ({len(chrome_driver.page_source):,} chars)")
            
            chrome_driver.quit()
            return True
            
        except Exception as e:
            print(f"❌ Chrome download failed: {e}")
            return False
    
    def run_hybrid_scraping(self, max_documents=10):
        """Run hybrid Firefox+Chrome scraping"""
        print(f"\n🚀 STARTING HYBRID SCRAPING")
        print(f"🎯 Target: {max_documents} documents")
        print("🦊 Firefox: Form + CAPTCHA")
        print("🔵 Chrome: Downloads")
        print("="*50)
        
        # Phase 1: Firefox form filling
        print("\n📍 PHASE 1: FIREFOX FORM FILLING")
        print("="*40)
        
        firefox_driver = self.create_firefox_with_proxy()
        if not firefox_driver:
            print("❌ Could not create Firefox driver")
            return []
        
        try:
            # Step 1: Load page
            print("🌐 Firefox: Loading IGR website...")
            firefox_driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            time.sleep(5)
            
            # Step 2: Fill form
            if not self.fill_mumbai_form_firefox(firefox_driver):
                print("❌ Firefox form filling failed")
                return []
            
            # Step 3: Solve CAPTCHA
            if not self.solve_captcha_firefox(firefox_driver):
                print("❌ Firefox CAPTCHA failed")
                return []
            
            # Step 4: Submit form
            if not self.submit_form_firefox(firefox_driver):
                print("❌ Firefox form submission failed")
                return []
            
            # Step 5: Extract links
            documents = self.extract_links_firefox(firefox_driver)
            
            if not documents:
                print("❌ No documents found")
                return []
            
            # Limit to requested number
            documents = documents[:max_documents]
            
        finally:
            firefox_driver.quit()
            print("🦊 Firefox session closed")
        
        # Phase 2: Chrome downloads
        print(f"\n📍 PHASE 2: CHROME DOWNLOADS")
        print("="*40)
        
        successful_downloads = 0
        for i, doc in enumerate(documents, 1):
            success = self.download_with_chrome(doc["url"], i)
            if success:
                successful_downloads += 1
                print(f"✅ Document {i}/{len(documents)} completed")
            else:
                print(f"❌ Document {i}/{len(documents)} failed")
            
            time.sleep(1)  # Brief pause between downloads
        
        # Summary
        print(f"\n🎉 HYBRID SCRAPING COMPLETED!")
        print("="*40)
        print(f"🦊 Firefox: Form filling successful")
        print(f"🔵 Chrome: {successful_downloads}/{len(documents)} downloads successful")
        print(f"📁 Files saved in: {self.docs_dir}")
        
        return documents

def main():
    """Main function"""
    print("🔧 HYBRID FIREFOX + CHROME SCRAPER SETUP")
    print("="*50)
    
    # Get proxy info
    use_proxy = input("🌐 Use proxy for IP switching in Firefox? (y/N): ").lower().startswith('y')
    
    proxy_password = None
    if use_proxy:
        proxy_password = input("🔐 Enter proxy password: ").strip()
        if not proxy_password:
            print("⚠️ No proxy password - running without proxy")
    
    # Get document count
    try:
        max_docs = int(input("📋 How many documents? (default 10): ") or "10")
    except:
        max_docs = 10
    
    # Initialize scraper
    scraper = HybridFirefoxChromeScraper(proxy_password=proxy_password)
    
    # Run hybrid scraping
    documents = scraper.run_hybrid_scraping(max_documents=max_docs)
    
    print(f"\n✅ HYBRID PROCESS COMPLETE!")
    print(f"📊 Total documents processed: {len(documents)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc() 