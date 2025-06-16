#!/usr/bin/env python3
"""
Hybrid Scraper: Firefox Form Filling + Chrome Proxy Downloads
Firefox: Stable form filling and CAPTCHA (no proxy)
Chrome: Document downloads with IP switching (proxy rotation)
"""

import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException

# Assuming captcha_solver_ocr.py is in the same directory or accessible in the path
from captcha_solver_ocr import CaptchaSolver

class HybridIGRScraper:
    def __init__(self, config_path='config.json'):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = self.load_config(os.path.join(self.base_dir, config_path))
        
        self.data_dir = os.path.join(self.base_dir, "data", "hybrid_igr_results")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
            
        self.captcha_solver = CaptchaSolver()
        self.chrome_session_count = 0

    def load_config(self, path):
        with open(path, 'r') as f:
            return json.load(f)

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

    def create_chrome_with_proxy(self):
        """Create Chrome with proxy for downloads"""
        options = ChromeOptions()
        
        # IP rotation setup for Chrome
        if self.config.get("use_proxy"):
            session_id = f"chrome-{int(time.time())}-{self.chrome_session_count}"
            self.chrome_session_count += 1
            proxy_user = f"td-customer-hdXMhtuot8ni-country-in-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.config.get('proxy_password')}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔵 Chrome proxy session: {session_id}")
        
        # Chrome optimizations
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            return webdriver.Chrome(options=options)
        except Exception as e:
            print(f"❌ Chrome driver creation failed: {e}")
            return None

    def run(self):
        print("🚀 STARTING HYBRID FIREFOX + CHROME SCRAPER")
        print("🦊 Firefox: Form filling + CAPTCHA solving")
        print("🔵 Chrome: Downloads with IP switching")
        
        firefox_driver = self.create_firefox_stable()
        if not firefox_driver:
            return

        try:
            # Load the correct IGR website
            print("🌐 Loading IGR website...")
            firefox_driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails")
            time.sleep(5)
            
            # Wait for page to load completely
            WebDriverWait(firefox_driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )
            
            self.fill_mumbai_form(firefox_driver)
            
            captcha_text = self.solve_captcha_with_tesseract(firefox_driver)
            if not captcha_text:
                print("❌ OCR failed. Trying manual fallback...")
                # Show the CAPTCHA image for manual input
                try:
                    import subprocess
                    import os
                    latest_captcha = max([os.path.join(self.captcha_dir, f) for f in os.listdir(self.captcha_dir)], key=os.path.getctime)
                    subprocess.run(['start', latest_captcha], shell=True)  # Open image
                    captcha_text = input("🔍 Please enter CAPTCHA text manually: ").strip()
                    if not captcha_text:
                        print("❌ No CAPTCHA text provided.")
                        return
                except Exception as e:
                    print(f"❌ Manual fallback failed: {e}")
                    return

            self.enter_captcha(firefox_driver, captcha_text)
            
            documents = self.submit_and_extract_links(firefox_driver)
            if not documents:
                print("❌ No documents found to download.")
                return
            
            print(f"📄 Found {len(documents)} documents. Starting downloads...")
            self.download_documents_with_chrome(documents)
        
        except TimeoutException:
            print("❌ Timed out waiting for page to load. Saving screenshot for debugging.")
            firefox_driver.save_screenshot(os.path.join(self.base_dir, "debug_screenshot.png"))
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            firefox_driver.save_screenshot(os.path.join(self.base_dir, "error_screenshot.png"))

        finally:
            firefox_driver.quit()
            print("🎉 HYBRID SCRAPING COMPLETE!")

    def fill_mumbai_form(self, driver):
        """Fill the Mumbai IGR form"""
        print("📝 Filling Mumbai IGR form...")
        
        try:
            # Database selection
            try:
                db_select = driver.find_element(By.ID, "dbselect")
                Select(db_select).select_by_value("3")
                print("✅ Database selected")
                time.sleep(2)
            except:
                print("ℹ️ No database selector found")
            
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
            
            print("✅ Form filled successfully!")
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            raise

    def solve_captcha_with_tesseract(self, driver):
        """Solve CAPTCHA using Tesseract OCR"""
        print("🔍 Solving CAPTCHA with Tesseract OCR...")
        
        try:
            # Find CAPTCHA image
            captcha_selectors = ["captcha_img", "imgCaptcha", "captcha"]
            captcha_element = None
            
            for selector in captcha_selectors:
                try:
                    captcha_element = driver.find_element(By.ID, selector)
                    break
                except:
                    continue
            
            if not captcha_element:
                # Try by class or other attributes
                try:
                    captcha_element = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha') or contains(@id, 'captcha')]")
                except:
                    print("❌ CAPTCHA image not found")
                    return None
            
            # Take screenshot of CAPTCHA
            timestamp = int(time.time())
            screenshot_path = os.path.join(self.captcha_dir, f"captcha_{timestamp}.png")
            captcha_element.screenshot(screenshot_path)
            
            print(f"📸 CAPTCHA screenshot saved: {screenshot_path}")
            time.sleep(1)

            # Solve using Tesseract
            try:
                solution = self.captcha_solver.solve_captcha(screenshot_path)
                if solution:
                    print(f"✅ CAPTCHA solved: {solution}")
                    # Open the CAPTCHA image for verification
                    try:
                        import subprocess
                        subprocess.run(['start', screenshot_path], shell=True)
                        print(f"🖼️ CAPTCHA image opened for verification: {screenshot_path}")
                        
                        # Ask for confirmation
                        confirm = input(f"🔍 OCR result: '{solution}' - Is this correct? (y/n/manual): ").strip().lower()
                        if confirm == 'n':
                            manual_solution = input("🔍 Please enter correct CAPTCHA: ").strip()
                            return manual_solution if manual_solution else solution
                        elif confirm == 'manual':
                            manual_solution = input("🔍 Please enter CAPTCHA manually: ").strip()
                            return manual_solution if manual_solution else solution
                        else:
                            return solution
                    except:
                        return solution
                else:
                    print("❌ OCR returned empty result")
                    return None
            except Exception as e:
                print(f"❌ Tesseract OCR failed: {e}")
                return None
                
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return None

    def enter_captcha(self, driver, text):
        """Enter CAPTCHA text"""
        try:
            # Find CAPTCHA input field
            captcha_input = None
            input_selectors = ["txtcaptcha", "captcha", "captcha_text", "txtImg"]
            
            for selector in input_selectors:
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
                captcha_input.send_keys(text)
                print(f"✅ CAPTCHA entered: {text}")
            else:
                print("❌ CAPTCHA input field not found")
                
        except Exception as e:
            print(f"❌ Error entering CAPTCHA: {e}")

    def submit_and_extract_links(self, driver):
        """Submit form and extract document links"""
        try:
            # Submit form
            submit_button = None
            submit_selectors = ["search", "submit", "btnSubmit", "btnSearch"]
            
            for selector in submit_selectors:
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
                "//a[contains(@href, 'Report')]",
                "//table//a[@href]"
            ]
            
            for pattern in patterns:
                try:
                    links = driver.find_elements(By.XPATH, pattern)
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text.strip()
                        
                        if href and any(term in href for term in ['propertydetails', 'indexii', 'report']):
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
                if doc['url'] not in seen_urls:
                    unique_docs.append(doc)
                    seen_urls.add(doc['url'])
            
            print(f"✅ Found {len(unique_docs)} document links")
            return unique_docs
            
        except Exception as e:
            print(f"❌ Submit/extract failed: {e}")
            return []

    def download_documents_with_chrome(self, documents):
        """Download documents using Chrome with IP switching"""
        print(f"⬇️ Starting download of {len(documents)} documents with Chrome + IP switching...")
        
        successful = 0
        for i, doc in enumerate(documents, 1):
            try:
                print(f"🔵 Chrome download {i}/{len(documents)} (with IP rotation)...")
                
                # Create new Chrome with fresh proxy session
                chrome_driver = self.create_chrome_with_proxy()
                if not chrome_driver:
                    continue
                
                chrome_driver.get(doc["url"])
                time.sleep(4)
                
                # Check content
                content = chrome_driver.page_source
                if len(content) < 1000:
                    print(f"⚠️ Content too small for doc {i}, skipping...")
                    chrome_driver.quit()
                    continue
                
                # Save document
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Mumbai_Doc_{i:03d}_{timestamp}.html"
                filepath = os.path.join(self.docs_dir, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                
                # Save metadata
                metadata = {
                    "document_id": i,
                    "filename": filename,
                    "source_url": doc["url"],
                    "download_timestamp": datetime.now().isoformat(),
                    "content_size": len(content),
                    "method": "Firefox Form + Chrome Proxy",
                    "form_browser": "Firefox (no proxy)",
                    "download_browser": "Chrome (with IP rotation)",
                    "chrome_session": self.chrome_session_count
                }
                
                meta_path = os.path.join(self.meta_dir, f"{filename}.json")
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Downloaded: {filename} ({len(content):,} chars)")
                successful += 1
                
                chrome_driver.quit()
                
                # Pause between downloads for IP rotation
                if i < len(documents):
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Chrome download {i} failed: {e}")
                try:
                    chrome_driver.quit()
                except:
                    pass
        
        print(f"\n📊 DOWNLOAD SUMMARY:")
        print(f"✅ Successful: {successful}/{len(documents)}")
        print(f"📁 Documents saved to: {self.docs_dir}")
        print(f"📋 Metadata saved to: {self.meta_dir}")

if __name__ == "__main__":
    scraper = HybridIGRScraper()
    scraper.run()