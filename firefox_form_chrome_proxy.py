#!/usr/bin/env python3
"""
Hybrid Scraper: Firefox Form Filling + Chrome Proxy Downloads
Firefox: Stable form filling and CAPTCHA (no proxy)
Chrome: Document downloads with IP switching (proxy rotation)
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

class FirefoxFormChromeProxyScraper:
    def __init__(self, proxy_password=None):
        """Initialize hybrid scraper: Firefox for forms, Chrome for proxy downloads"""
        self.proxy_password = proxy_password
        self.chrome_session_count = 0
        self.documents_found = []
        
        # Create output directories
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "firefox_chrome_results")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 FIREFOX FORM + CHROME PROXY SCRAPER")
        print("=" * 60)
        print("🦊 Firefox: Form filling + CAPTCHA (stable, no proxy)")
        print("🔵 Chrome: Downloads with IP switching (proxy rotation)")
        print("✅ Mumbai 2024 Agreement to Sale automation")
        print("=" * 60)
    
    def create_firefox_stable(self):
        """Create stable Firefox for form filling (no proxy)"""
        options = FirefoxOptions()
        
        # Firefox optimizations for stability
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0")
        
        # Keep browser visible for form interaction
        options.set_preference("browser.tabs.remote.autostart", False)
        options.set_preference("browser.tabs.remote.autostart.2", False)
        
        try:
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1200, 800)
            print("🦊 Firefox driver created successfully (stable mode)")
            return driver
        except Exception as e:
            print(f"❌ Firefox driver creation failed: {e}")
            return None
    
    def get_chrome_proxy_session(self):
        """Generate new proxy session for Chrome"""
        self.chrome_session_count += 1
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        session_id = f"chrome-{timestamp}-{random_str}-{self.chrome_session_count}"
        return session_id
    
    def create_chrome_with_proxy(self):
        """Create Chrome with proxy for downloads"""
        options = ChromeOptions()
        
        # IP rotation setup for Chrome
        if self.proxy_password:
            session_id = self.get_chrome_proxy_session()
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.proxy_password}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔵 Chrome proxy session: {session_id}")
        
        # Chrome optimizations
        options.add_argument("--headless")  # Hidden for downloads
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"❌ Chrome driver creation failed: {e}")
            return None
    
    def fill_mumbai_form_firefox(self, driver):
        """Complete form filling in Firefox (stable)"""
        try:
            print("🦊 Firefox: Starting form filling...")
            
            # Wait for page load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )
            
            print("✅ Page loaded, filling form fields...")
            time.sleep(3)
            
            # Database selection
            try:
                db_select = driver.find_element(By.ID, "dbselect")
                Select(db_select).select_by_value("3")
                print("✅ Database selected")
                time.sleep(2)
            except:
                print("ℹ️ No database selector")
            
            # District (Mumbai)
            try:
                district_select = Select(driver.find_element(By.ID, "district_id"))
                mumbai_found = False
                
                # Look for Mumbai options
                for option in district_select.options:
                    if any(term in option.text.lower() for term in ['mumbai', 'मुंबई']):
                        district_select.select_by_value(option.get_attribute("value"))
                        print(f"✅ District: {option.text}")
                        mumbai_found = True
                        break
                
                if not mumbai_found:
                    # Try common Mumbai IDs
                    for mid in ["1", "31", "32"]:
                        try:
                            district_select.select_by_value(mid)
                            print(f"✅ District by ID: {mid}")
                            break
                        except:
                            continue
                
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ District selection: {e}")
            
            # Sub-district
            try:
                subdistrict_select = Select(driver.find_element(By.ID, "subdistrict_id"))
                subdistrict_select.select_by_index(1)
                print("✅ Sub-district selected")
                time.sleep(2)
            except:
                print("ℹ️ No sub-district field")
            
            # Village
            try:
                village_select = Select(driver.find_element(By.ID, "village_id"))
                village_select.select_by_index(1)
                print("✅ Village selected")
                time.sleep(2)
            except:
                print("ℹ️ No village field")
            
            # Year (2024)
            try:
                year_fields = ["year", "year_id", "registration_year"]
                for year_field in year_fields:
                    try:
                        year_select = Select(driver.find_element(By.ID, year_field))
                        for option in year_select.options:
                            if "2024" in option.text:
                                year_select.select_by_value(option.get_attribute("value"))
                                print(f"✅ Year 2024 selected")
                                time.sleep(2)
                                break
                        break
                    except:
                        continue
            except:
                print("ℹ️ Year field not found")
            
            # Article (Agreement to Sale)
            try:
                article_select = Select(driver.find_element(By.ID, "article_id"))
                agreement_found = False
                
                for option in article_select.options:
                    if any(term in option.text.lower() for term in ['agreement', 'विकस', 'sale']):
                        article_select.select_by_value(option.get_attribute("value"))
                        print(f"✅ Article: {option.text}")
                        agreement_found = True
                        break
                
                if not agreement_found:
                    # Try common Agreement IDs
                    for aid in ["42", "43", "44"]:
                        try:
                            article_select.select_by_value(aid)
                            print(f"✅ Article by ID: {aid}")
                            break
                        except:
                            continue
                
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Article selection: {e}")
            
            print("✅ Firefox form filling completed!")
            return True
            
        except Exception as e:
            print(f"❌ Firefox form filling failed: {e}")
            return False
    
    def solve_captcha_firefox(self, driver):
        """Solve CAPTCHA in visible Firefox browser"""
        try:
            print("\n🔍 FIREFOX CAPTCHA SOLVING")
            print("=" * 40)
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.captcha_dir, f"firefox_captcha_{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            
            print(f"📸 Screenshot: {screenshot_path}")
            
            # Open screenshot
            try:
                os.startfile(screenshot_path)
                print("📋 Screenshot opened!")
            except:
                print(f"📋 Please open: {screenshot_path}")
            
            print("\n🦊 CAPTCHA INSTRUCTIONS")
            print("="*30)
            print("1. Firefox window is visible")
            print("2. Look for CAPTCHA image")
            print("3. Enter the text below")
            print("="*30)
            
            captcha_text = input("\n🔤 Enter CAPTCHA: ").strip()
            
            if not captcha_text:
                return False
            
            # Find CAPTCHA input
            captcha_input = None
            for selector in ["txtcaptcha", "captcha", "captcha_text"]:
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
                # Last resort - find any text input
                inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                if inputs:
                    captcha_input = inputs[-1]
            
            if captcha_input:
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                print(f"✅ CAPTCHA entered: {captcha_text}")
                return True
            else:
                print("❌ CAPTCHA input not found")
                return False
                
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return False
    
    def submit_and_extract_firefox(self, driver):
        """Submit form and extract links in Firefox"""
        try:
            # Submit form
            submit_button = None
            for selector in ["search", "submit", "btnSubmit"]:
                try:
                    submit_button = driver.find_element(By.ID, selector)
                    break
                except:
                    continue
            
            if not submit_button:
                try:
                    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
                except:
                    print("❌ Submit button not found")
                    return []
            
            submit_button.click()
            print("✅ Form submitted")
            
            # Wait for results
            print("⏳ Waiting for results...")
            time.sleep(8)
            
            # Extract document links
            print("🔍 Extracting document links...")
            time.sleep(3)
            
            documents = []
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
            seen = set()
            for doc in documents:
                if doc["url"] not in seen:
                    unique_docs.append(doc)
                    seen.add(doc["url"])
            
            print(f"✅ Found {len(unique_docs)} document links")
            return unique_docs
            
        except Exception as e:
            print(f"❌ Submit/extract failed: {e}")
            return []
    
    def download_with_chrome_proxy(self, doc_url, doc_index):
        """Download document using Chrome with proxy rotation"""
        try:
            print(f"🔵 Chrome download {doc_index} (with IP rotation)...")
            
            # Create new Chrome with fresh proxy session
            chrome_driver = self.create_chrome_with_proxy()
            if not chrome_driver:
                return False
            
            chrome_driver.get(doc_url)
            time.sleep(4)
            
            # Check content
            content = chrome_driver.page_source
            if len(content) < 1000:
                print(f"⚠️ Content too small for doc {doc_index}")
                chrome_driver.quit()
                return False
            
            # Save document
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Mumbai_Doc_{doc_index:03d}_{timestamp}.html"
            filepath = os.path.join(self.docs_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Save metadata
            metadata = {
                "document_id": doc_index,
                "filename": filename,
                "source_url": doc_url,
                "download_timestamp": datetime.now().isoformat(),
                "content_size": len(content),
                "method": "Firefox Form + Chrome Proxy",
                "form_browser": "Firefox (no proxy)",
                "download_browser": "Chrome (with proxy rotation)",
                "chrome_session": self.chrome_session_count
            }
            
            meta_path = os.path.join(self.meta_dir, f"{filename}.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved: {filename} ({len(content):,} chars)")
            
            chrome_driver.quit()
            return True
            
        except Exception as e:
            print(f"❌ Chrome download {doc_index} failed: {e}")
            return False
    
    def run_hybrid_process(self, max_documents=10):
        """Run the complete hybrid process"""
        print(f"\n🚀 STARTING HYBRID FIREFOX + CHROME PROCESS")
        print(f"🎯 Target: {max_documents} documents")
        print("="*60)
        
        # PHASE 1: Firefox form filling
        print("\n📍 PHASE 1: FIREFOX FORM FILLING")
        print("="*40)
        
        firefox_driver = self.create_firefox_stable()
        if not firefox_driver:
            return []
        
        try:
            # Load page
            print("🌐 Loading IGR website...")
            firefox_driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            time.sleep(5)
            
            # Fill form
            if not self.fill_mumbai_form_firefox(firefox_driver):
                return []
            
            # Solve CAPTCHA
            if not self.solve_captcha_firefox(firefox_driver):
                return []
            
            # Submit and extract
            documents = self.submit_and_extract_firefox(firefox_driver)
            
            if not documents:
                print("❌ No documents found")
                return []
            
            # Limit documents
            documents = documents[:max_documents]
            print(f"🎯 Will download {len(documents)} documents")
            
        finally:
            firefox_driver.quit()
            print("🦊 Firefox session completed")
        
        # PHASE 2: Chrome proxy downloads
        print(f"\n📍 PHASE 2: CHROME PROXY DOWNLOADS")
        print("="*40)
        
        successful = 0
        for i, doc in enumerate(documents, 1):
            if self.download_with_chrome_proxy(doc["url"], i):
                successful += 1
                print(f"✅ Document {i}/{len(documents)} completed")
            else:
                print(f"❌ Document {i}/{len(documents)} failed")
            
            # Pause between downloads for IP rotation
            if i < len(documents):
                time.sleep(2)
        
        # Summary
        print(f"\n🎉 HYBRID PROCESS COMPLETED!")
        print("="*50)
        print(f"🦊 Firefox: Form filling successful")
        print(f"🔵 Chrome: {successful}/{len(documents)} downloads successful")
        print(f"📁 Documents: {self.docs_dir}")
        print(f"📋 Metadata: {self.meta_dir}")
        
        return documents

def main():
    """Main function"""
    print("🔧 FIREFOX FORM + CHROME PROXY SCRAPER SETUP")
    print("="*55)
    
    # Get proxy info for Chrome downloads
    use_proxy = input("🔵 Use proxy for Chrome downloads with IP rotation? (y/N): ").lower().startswith('y')
    
    proxy_password = None
    if use_proxy:
        proxy_password = input("🔐 Enter proxy password for Chrome: ").strip()
        if not proxy_password:
            print("⚠️ No proxy password - Chrome will run without proxy")
    
    # Get document count
    try:
        max_docs = int(input("📋 How many documents to download? (default 10): ") or "10")
    except:
        max_docs = 10
    
    print(f"\n🚀 Setup complete!")
    print(f"🦊 Firefox: Form filling (stable, no proxy)")
    print(f"🔵 Chrome: Downloads {'with IP rotation' if proxy_password else 'without proxy'}")
    
    # Initialize and run
    scraper = FirefoxFormChromeProxyScraper(proxy_password=proxy_password)
    documents = scraper.run_hybrid_process(max_documents=max_docs)
    
    print(f"\n✅ ALL DONE!")
    print(f"📊 Total documents processed: {len(documents)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc() 