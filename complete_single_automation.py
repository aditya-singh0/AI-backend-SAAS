#!/usr/bin/env python3
"""
COMPLETE SINGLE AUTOMATION SCRIPT - DUAL BROWSER VERSION
Everything automated in one script:
- Chrome for Thordata proxy requests (CAPTCHA downloads, etc.)
- Firefox for website automation (form filling, submission)
- IP switching for each search
- CAPTCHA solving with OCR
- Document downloading
"""

import time
import random
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import urllib3
urllib3.disable_warnings()

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✅ EasyOCR available")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR not available")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract available")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ Tesseract not available")

class DualBrowserAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/dual_browser_automation"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Thordata proxy configuration for Chrome requests
        self.proxy_config = {
            'host': '42q6t9rp.pr.thordata.net',
            'port': '9999',
            'username': 'td-customer-hdXMhtuot8ni',
            'password': 'iyHxHphyuy3i'
        }
        
        # Initialize OCR
        self.ocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.ocr_reader = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized")
            except:
                print("⚠️ EasyOCR initialization failed")
        
        # Browser instances
        self.firefox_driver = None  # For website automation
        self.chrome_driver = None   # For Thordata proxy requests
        self.wait = None
        self.session_counter = 0
        
        # Search parameters
        self.search_params = [
            {"year_db": 3, "reg_year": 2024, "village": "Andheri"},
            {"year_db": 3, "reg_year": 2023, "village": "Bandra"},
            {"year_db": 3, "reg_year": 2022, "village": "Borivali"},
            {"year_db": 2, "reg_year": 2021, "village": "Malad"},
            {"year_db": 2, "reg_year": 2020, "village": "Kandivali"},
        ]

    def setup_chrome_for_thordata(self, session_id):
        """Setup Chrome browser specifically for Thordata proxy requests"""
        try:
            # Close existing Chrome if any
            if self.chrome_driver:
                self.chrome_driver.quit()
                time.sleep(1)
            
            # Chrome options for Thordata proxy
            chrome_options = ChromeOptions()
            
            # Thordata proxy setup
            proxy_host = self.proxy_config['host']
            proxy_port = self.proxy_config['port']
            full_username = f"{self.proxy_config['username']}-sessid-{session_id}"
            proxy_password = self.proxy_config['password']
            
            # Configure proxy for Chrome
            proxy_url = f"http://{full_username}:{proxy_password}@{proxy_host}:{proxy_port}"
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
            
            # Chrome-specific settings
            chrome_options.add_argument('--headless')  # Chrome runs headless for proxy requests
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--silent')
            
            self.chrome_driver = webdriver.Chrome(options=chrome_options)
            print(f"🚗 Chrome setup for Thordata proxy (session: {session_id})")
            return True
            
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            return False

    def setup_firefox_for_website(self):
        """Setup Firefox browser for website automation (visible)"""
        try:
            # Close existing Firefox if any
            if self.firefox_driver:
                self.firefox_driver.quit()
                time.sleep(2)
            
            # Firefox options
            firefox_options = FirefoxOptions()
            
            # Anti-detection for Firefox
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            
            # Visible Firefox (you can see what's happening)
            # firefox_options.add_argument('--headless')  # Uncomment for headless
            
            self.firefox_driver = webdriver.Firefox(options=firefox_options)
            self.wait = WebDriverWait(self.firefox_driver, 20)
            
            print("🦊 Firefox setup for website automation (visible)")
            return True
            
        except Exception as e:
            print(f"❌ Firefox setup failed: {e}")
            return False

    def setup_dual_browsers(self):
        """Setup both browsers for the session"""
        try:
            # Generate session ID for IP rotation
            self.session_counter += 1
            session_id = f"dual-{self.session_counter}-{datetime.now().strftime('%H%M%S')}"
            
            print(f"\n🔄 SETTING UP DUAL BROWSERS (Session: {session_id})")
            
            # Setup Chrome for Thordata proxy requests
            if not self.setup_chrome_for_thordata(session_id):
                return None
            
            # Setup Firefox for website automation
            if not self.setup_firefox_for_website():
                return None
            
            print("✅ Both browsers ready!")
            return session_id
            
        except Exception as e:
            print(f"❌ Dual browser setup failed: {e}")
            return None

    def solve_captcha_with_chrome_thordata(self, session_id):
        """Solve CAPTCHA using Chrome with Thordata proxy - SIMPLIFIED & RELIABLE VERSION"""
        try:
            print("🤖 Solving CAPTCHA with simplified approach...")
            
            # Get CAPTCHA image URL from Firefox
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.ID, "captcha-img"))
            )
            captcha_src = captcha_img.get_attribute("src")
            print(f"   📷 CAPTCHA URL: {captcha_src}")
            
            # Download CAPTCHA image using requests with Thordata proxy
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            try:
                print("   🚗 Downloading CAPTCHA via Thordata proxy...")
                full_username = f"{self.proxy_config['username']}-sessid-{session_id}"
                proxy_url = f"http://{full_username}:{self.proxy_config['password']}@{self.proxy_config['host']}:{self.proxy_config['port']}"
                proxies = {"http": proxy_url, "https": proxy_url}
                
                response = requests.get(captcha_src, proxies=proxies, verify=False, timeout=15)
                
                if response.status_code == 200:
                    with open(captcha_path, 'wb') as f:
                        f.write(response.content)
                    print(f"   ✅ CAPTCHA downloaded: {captcha_path}")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️ Direct download failed: {e}")
                print("   🚗 Trying Chrome screenshot method...")
                
                try:
                    self.chrome_driver.get(captcha_src)
                    time.sleep(2)
                    self.chrome_driver.save_screenshot(captcha_path)
                    print(f"   ✅ Chrome screenshot saved: {captcha_path}")
                except Exception as e2:
                    print(f"   ❌ Chrome screenshot failed: {e2}")
                    return self.get_manual_captcha_input()
            
            # Show the CAPTCHA image path to user
            print(f"   📁 CAPTCHA saved at: {captcha_path}")
            
            # Try OCR methods
            ocr_results = []
            
            # Method 1: EasyOCR (if available)
            if self.ocr_reader:
                try:
                    print("   🔍 Trying EasyOCR...")
                    results = self.ocr_reader.readtext(captcha_path)
                    for result in results:
                        text = result[1].strip().upper()
                        confidence = result[2]
                        # Only consider results with reasonable length and confidence
                        if len(text) >= 4 and len(text) <= 8 and confidence > 0.5:
                            # Clean the text - remove special characters
                            clean_text = ''.join(c for c in text if c.isalnum())
                            if len(clean_text) >= 4:
                                ocr_results.append((clean_text, confidence, "EasyOCR"))
                                print(f"   🔍 EasyOCR: '{clean_text}' (confidence: {confidence:.2f})")
                except Exception as e:
                    print(f"   ⚠️ EasyOCR failed: {e}")
            
            # Method 2: Tesseract (if available)
            if TESSERACT_AVAILABLE:
                try:
                    print("   🔍 Trying Tesseract...")
                    import cv2
                    
                    # Load and preprocess image
                    img = cv2.imread(captcha_path)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Simple threshold
                    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                    
                    # Try different Tesseract configurations
                    configs = [
                        '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                        '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                    ]
                    
                    for i, config in enumerate(configs):
                        try:
                            text = pytesseract.image_to_string(thresh, config=config).strip().upper()
                            clean_text = ''.join(c for c in text if c.isalnum())
                            if len(clean_text) >= 4 and len(clean_text) <= 8:
                                ocr_results.append((clean_text, 0.7, f"Tesseract-{i+1}"))
                                print(f"   🔍 Tesseract-{i+1}: '{clean_text}'")
                        except:
                            continue
                            
                except Exception as e:
                    print(f"   ⚠️ Tesseract failed: {e}")
            
            # Analyze OCR results
            if ocr_results:
                print(f"\n   📊 Found {len(ocr_results)} OCR results:")
                for i, (text, conf, method) in enumerate(ocr_results):
                    print(f"      {i+1}. '{text}' from {method} (confidence: {conf:.2f})")
                
                # If we have a high-confidence result, offer it as default
                best_result = max(ocr_results, key=lambda x: x[1])
                if best_result[1] > 0.8:
                    print(f"\n   🎯 Best result: '{best_result[0]}' (confidence: {best_result[1]:.2f})")
                    use_ocr = input(f"   ✅ Use this result? (y/n, default y): ").strip().lower()
                    if use_ocr != 'n':
                        print(f"   ✅ Using OCR result: '{best_result[0]}'")
                        return best_result[0]
                
                # Show options to user
                print(f"\n   👀 Please check the Firefox browser to see the actual CAPTCHA")
                print(f"   📁 CAPTCHA image saved at: {captcha_path}")
                
                while True:
                    choice = input(f"   🔤 Choose OCR result (1-{len(ocr_results)}) or enter 'm' for manual: ").strip().lower()
                    
                    if choice == 'm':
                        return self.get_manual_captcha_input()
                    elif choice.isdigit() and 1 <= int(choice) <= len(ocr_results):
                        selected = ocr_results[int(choice)-1]
                        print(f"   ✅ Using selected result: '{selected[0]}'")
                        return selected[0]
                    else:
                        print(f"   ❌ Please enter 1-{len(ocr_results)} or 'm'")
            else:
                print("   ❌ No OCR results found")
                return self.get_manual_captcha_input()
                
        except Exception as e:
            print(f"   ❌ CAPTCHA solving failed: {e}")
            return self.get_manual_captcha_input()

    def get_manual_captcha_input(self):
        """Get CAPTCHA input manually from user - SIMPLIFIED"""
        print("\n   👀 MANUAL CAPTCHA INPUT REQUIRED")
        print("   🦊 Look at the Firefox browser window to see the CAPTCHA")
        print("   📷 CAPTCHA image has been saved in the data folder")
        print("   💡 The CAPTCHA is usually 5-6 characters (letters and numbers)")
        
        while True:
            manual_input = input("\n   🔤 Enter the CAPTCHA text: ").strip().upper()
            
            if not manual_input:
                print("   ❌ Please enter the CAPTCHA text")
                continue
            
            if len(manual_input) < 3:
                print("   ⚠️ CAPTCHA seems too short (usually 5-6 characters)")
                confirm = input("   Are you sure? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            if len(manual_input) > 10:
                print("   ⚠️ CAPTCHA seems too long (usually 5-6 characters)")
                confirm = input("   Are you sure? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            # Clean the input
            clean_input = ''.join(c for c in manual_input if c.isalnum())
            if clean_input != manual_input:
                print(f"   🔧 Cleaned input: '{manual_input}' → '{clean_input}'")
                confirm = input("   Use cleaned version? (y/n, default y): ").strip().lower()
                if confirm != 'n':
                    manual_input = clean_input
            
            print(f"   ✅ Using manual input: '{manual_input}'")
            return manual_input

    def fill_form_with_firefox(self, year_db, reg_year, village):
        """Fill the entire form using Firefox"""
        try:
            print(f"\n🤖 FILLING FORM WITH FIREFOX: Mumbai {village} - Year {reg_year}")
            
            # 1. Select database (year range)
            print("   📅 Selecting database...")
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            print(f"   ✅ Database: {year_db}")
            time.sleep(3)
            
            # 2. Select Mumbai district (ID: 31)
            print("   📍 Selecting Mumbai district...")
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value("31")
            print("   ✅ District: Mumbai (31)")
            time.sleep(3)
            
            # 3. Select Mumbai taluka (first available)
            print("   🏘️ Selecting Mumbai taluka...")
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                print("   ✅ Taluka: Mumbai")
                time.sleep(3)
            
            # 4. Select village
            print(f"   🏘️ Selecting village: {village}...")
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            
            # Try to find village by name
            village_found = False
            for option in village_options:
                if village.lower() in option.text.lower():
                    village_select.select_by_value(option.get_attribute('value'))
                    village_found = True
                    print(f"   ✅ Village: {option.text}")
                    break
            
            # Use first available if not found
            if not village_found and len(village_options) > 1:
                village_select.select_by_value(village_options[1].get_attribute('value'))
                print(f"   ✅ Village: {village_options[1].text}")
            
            time.sleep(2)
            
            # 5. Select Agreement to Sale (ID: 42)
            print("   📄 Selecting Agreement to Sale...")
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            print("   ✅ Article: Agreement to Sale (42)")
            time.sleep(2)
            
            # 6. Enter registration year
            print(f"   📝 Entering registration year: {reg_year}...")
            free_text_input = self.firefox_driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            print(f"   ✅ Registration Year: {reg_year}")
            
            print("✅ FORM COMPLETELY FILLED WITH FIREFOX!")
            return True
            
        except Exception as e:
            print(f"   ❌ Form filling failed: {e}")
            return False

    def submit_and_check_results(self, session_id):
        """Submit form using Firefox and check for results - SIMPLIFIED VERSION"""
        try:
            print("\n🚀 SUBMITTING FORM WITH FIREFOX...")
            
            # Solve CAPTCHA
            captcha_solution = self.solve_captcha_with_chrome_thordata(session_id)
            
            if not captcha_solution:
                print("   ❌ No CAPTCHA solution provided")
                return False, 0
            
            # Find CAPTCHA input field
            try:
                captcha_input = self.firefox_driver.find_element(By.ID, "cpatchaTextBox")
            except:
                print("   ❌ Could not find CAPTCHA input field")
                return False, 0
            
            # Clear and enter CAPTCHA
            captcha_input.clear()
            time.sleep(1)
            captcha_input.send_keys(captcha_solution)
            time.sleep(1)
            
            # Verify CAPTCHA was entered
            entered_value = captcha_input.get_attribute('value')
            print(f"   📝 CAPTCHA entered: '{captcha_solution}'")
            print(f"   ✅ Field value: '{entered_value}'")
            
            if entered_value != captcha_solution:
                print("   ⚠️ CAPTCHA mismatch - trying again...")
                captcha_input.clear()
                time.sleep(1)
                captcha_input.send_keys(captcha_solution)
                time.sleep(1)
            
            # Submit form
            try:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                submit_button.click()
                print("   📤 Form submitted!")
            except:
                print("   ❌ Could not find or click submit button")
                return False, 0
            
            # Wait for results
            print("   ⏳ Waiting for results...")
            time.sleep(8)
            
            # Check page content
            try:
                page_source = self.firefox_driver.page_source.lower()
                
                # Check for CAPTCHA errors
                if any(error in page_source for error in ['invalid captcha', 'captcha error', 'wrong captcha']):
                    print("   ❌ CAPTCHA was incorrect!")
                    print("   💡 The CAPTCHA will be solved again in the next attempt")
                    return False, 0
                
                # Check for no data
                if "no data available" in page_source:
                    print("   ❌ No documents found for this search")
                    return False, 0
                
                # Check for results
                if "showing" in page_source and "entries" in page_source:
                    print("   ✅ Found results!")
                    
                    # Try to count documents
                    try:
                        rows = self.firefox_driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                        doc_count = len([row for row in rows if row.get_attribute('innerHTML').strip()])
                        if doc_count > 0:
                            print(f"   📊 Found {doc_count} documents!")
                            return True, doc_count
                    except:
                        pass
                    
                    print("   ✅ Documents found (count unknown)")
                    return True, 1
                
                # Unknown result
                print("   ⚠️ Unknown result - check Firefox browser")
                save_debug = input("   💾 Save debug HTML? (y/n, default n): ").strip().lower()
                if save_debug == 'y':
                    debug_file = os.path.join(self.data_dir, f'debug_unknown_{datetime.now().strftime("%H%M%S")}.html')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(self.firefox_driver.page_source)
                    print(f"   📄 Debug saved: {debug_file}")
                
                return False, 0
                
            except Exception as e:
                print(f"   ❌ Error checking results: {e}")
                return False, 0
                
        except Exception as e:
            print(f"   ❌ Form submission failed: {e}")
            return False, 0

    def download_documents_with_firefox(self):
        """Download found documents using Firefox"""
        try:
            print("\n📥 DOWNLOADING DOCUMENTS WITH FIREFOX...")
            
            # Look for download links
            download_links = self.firefox_driver.find_elements(By.CSS_SELECTOR, "a[href*='download'], a[href*='pdf'], button[onclick*='download']")
            
            if not download_links:
                print("   ⚠️ No download links found")
                return 0
            
            downloaded = 0
            for i, link in enumerate(download_links[:5]):  # Limit to first 5
                try:
                    print(f"   📄 Downloading document {i+1}...")
                    link.click()
                    time.sleep(3)
                    downloaded += 1
                except:
                    print(f"   ⚠️ Failed to download document {i+1}")
            
            print(f"✅ Downloaded {downloaded} documents")
            return downloaded
            
        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return 0

    def save_debug_info(self, params, success=False, doc_count=0):
        """Save debug information from Firefox"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            status = "SUCCESS" if success else "FAILED"
            filename = f'{status}_{params["village"]}_{params["reg_year"]}_{doc_count}docs_{timestamp}.html'
            debug_file = os.path.join(self.data_dir, filename)
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.firefox_driver.page_source)
            
            print(f"📄 Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")

    def run_dual_browser_automation(self):
        """Run complete automation with dual browsers"""
        print("🚀 DUAL BROWSER AUTOMATION")
        print("=" * 60)
        print("🤖 DUAL BROWSER APPROACH:")
        print("   🚗 Chrome (headless) + Thordata proxy for CAPTCHA downloads")
        print("   🦊 Firefox (visible) for website automation")
        print("   🔄 IP switching for each search")
        print("   📝 Form filling (Mumbai + Agreement to Sale)")
        print("   🤖 CAPTCHA solving with OCR")
        print("   📥 Document downloading")
        print("=" * 60)
        
        total_documents = 0
        successful_searches = []
        
        for i, params in enumerate(self.search_params, 1):
            print(f"\n🚀 SEARCH {i}/{len(self.search_params)}")
            print(f"🔄 DUAL BROWSER + Mumbai {params['village']} - Year {params['reg_year']}")
            
            try:
                # Setup both browsers
                session_id = self.setup_dual_browsers()
                if not session_id:
                    print("❌ Failed to setup dual browsers")
                    continue
                
                # Load website in Firefox
                print("🌐 Loading IGR website in Firefox...")
                self.firefox_driver.get(self.base_url)
                time.sleep(5)
                
                # Fill form with Firefox
                if not self.fill_form_with_firefox(params["year_db"], params["reg_year"], params["village"]):
                    print("❌ Form filling failed")
                    self.save_debug_info(params, False, 0)
                    continue
                
                # Submit and check results (using both browsers)
                found_docs, doc_count = self.submit_and_check_results(session_id)
                
                if found_docs:
                    print(f"🎉 SUCCESS! Found {doc_count} documents")
                    successful_searches.append({**params, "doc_count": doc_count})
                    total_documents += doc_count
                    
                    # Try to download documents with Firefox
                    downloaded = self.download_documents_with_firefox()
                    
                    # Save success debug info
                    self.save_debug_info(params, True, doc_count)
                    
                    # Ask if user wants to continue
                    continue_search = input(f"\n✅ Found {doc_count} documents! Continue searching? (y/n, default y): ").strip().lower()
                    if continue_search == 'n':
                        break
                else:
                    print("❌ No documents found")
                    self.save_debug_info(params, False, 0)
                
                # Wait between searches
                if i < len(self.search_params):
                    print("⏳ Waiting 5s before next search...")
                    time.sleep(5)
                
            except Exception as e:
                print(f"❌ Search {i} failed: {e}")
                continue
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 DUAL BROWSER AUTOMATION SUMMARY")
        print("=" * 60)
        
        if successful_searches:
            print(f"🎉 SUCCESS! Found documents in {len(successful_searches)} searches:")
            for result in successful_searches:
                print(f"   🏘️ Mumbai {result['village']} - Year {result['reg_year']} - {result['doc_count']} docs")
            print(f"\n📊 TOTAL DOCUMENTS FOUND: {total_documents}")
        else:
            print("❌ No documents found in any search")
        
        print(f"\n📁 All files saved in: {os.path.abspath(self.data_dir)}")
        
        return successful_searches

    def cleanup(self):
        """Clean up both browsers"""
        try:
            if self.firefox_driver or self.chrome_driver:
                input("\nPress Enter to close both browsers...")
                
                if self.firefox_driver:
                    self.firefox_driver.quit()
                    print("🧹 Firefox closed")
                    
                if self.chrome_driver:
                    self.chrome_driver.quit()
                    print("🧹 Chrome closed")
        except:
            pass

def main():
    print("🚀 DUAL BROWSER AUTOMATION SCRIPT")
    print("🚗 Chrome (headless) + Thordata proxy for requests")
    print("🦊 Firefox (visible) for website automation")
    print("🤖 Best of both worlds!")
    
    automation = DualBrowserAutomation()
    
    try:
        successful_results = automation.run_dual_browser_automation()
        
        if successful_results:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print(f"Found documents in {len(successful_results)} different searches")
        else:
            print("\n😔 No documents found in any search")
            print("💡 Try different years or villages")
            
    except KeyboardInterrupt:
        print("\n\n👋 Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 