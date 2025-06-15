#!/usr/bin/env python3
"""
CAPTCHA FIRST AUTOMATION SCRIPT
Downloads and solves CAPTCHA first, then fills the form
Better approach: CAPTCHA → Form → Submit
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

class CaptchaFirstAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/captcha_first_automation"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Thordata proxy configuration
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
        """Setup Chrome browser for Thordata proxy requests"""
        try:
            if self.chrome_driver:
                self.chrome_driver.quit()
                time.sleep(1)
            
            chrome_options = ChromeOptions()
            
            # Thordata proxy setup
            proxy_host = self.proxy_config['host']
            proxy_port = self.proxy_config['port']
            full_username = f"{self.proxy_config['username']}-sessid-{session_id}"
            proxy_password = self.proxy_config['password']
            
            proxy_url = f"http://{full_username}:{proxy_password}@{proxy_host}:{proxy_port}"
            chrome_options.add_argument(f'--proxy-server={proxy_url}')
            
            # Chrome settings
            chrome_options.add_argument('--headless')
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
        """Setup Firefox browser for website automation"""
        try:
            if self.firefox_driver:
                self.firefox_driver.quit()
                time.sleep(2)
            
            firefox_options = FirefoxOptions()
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            
            self.firefox_driver = webdriver.Firefox(options=firefox_options)
            self.wait = WebDriverWait(self.firefox_driver, 20)
            
            print("🦊 Firefox setup for website automation")
            return True
            
        except Exception as e:
            print(f"❌ Firefox setup failed: {e}")
            return False

    def setup_dual_browsers(self):
        """Setup both browsers"""
        try:
            self.session_counter += 1
            session_id = f"captcha-first-{self.session_counter}-{datetime.now().strftime('%H%M%S')}"
            
            print(f"\n🔄 SETTING UP BROWSERS (Session: {session_id})")
            
            if not self.setup_chrome_for_thordata(session_id):
                return None
            
            if not self.setup_firefox_for_website():
                return None
            
            print("✅ Both browsers ready!")
            return session_id
            
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            return None

    def download_and_solve_captcha_first(self, session_id):
        """STEP 1: Download and solve CAPTCHA before filling form"""
        try:
            print("\n🎯 STEP 1: DOWNLOAD AND SOLVE CAPTCHA FIRST")
            print("=" * 50)
            
            # Load website in Firefox to get CAPTCHA
            print("🌐 Loading IGR website to get CAPTCHA...")
            self.firefox_driver.get(self.base_url)
            time.sleep(5)
            
            # Find CAPTCHA image
            print("🔍 Looking for CAPTCHA...")
            try:
                captcha_img = self.wait.until(
                    EC.presence_of_element_located((By.ID, "captcha-img"))
                )
                captcha_src = captcha_img.get_attribute("src")
                print(f"✅ CAPTCHA found: {captcha_src}")
            except:
                print("❌ CAPTCHA not found")
                return None
            
            # Download CAPTCHA using Chrome + Thordata proxy
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            try:
                print("🚗 Downloading CAPTCHA via Chrome + Thordata...")
                full_username = f"{self.proxy_config['username']}-sessid-{session_id}"
                proxy_url = f"http://{full_username}:{self.proxy_config['password']}@{self.proxy_config['host']}:{self.proxy_config['port']}"
                proxies = {"http": proxy_url, "https": proxy_url}
                
                response = requests.get(captcha_src, proxies=proxies, verify=False, timeout=15)
                
                if response.status_code == 200:
                    with open(captcha_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ CAPTCHA downloaded: {captcha_path}")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Direct download failed: {e}")
                print("🚗 Trying Chrome screenshot...")
                
                try:
                    self.chrome_driver.get(captcha_src)
                    time.sleep(2)
                    self.chrome_driver.save_screenshot(captcha_path)
                    print(f"✅ Chrome screenshot saved: {captcha_path}")
                except Exception as e2:
                    print(f"❌ Chrome screenshot failed: {e2}")
                    return None
            
            # Solve CAPTCHA using OCR
            print("\n🤖 SOLVING CAPTCHA WITH OCR...")
            captcha_solution = self.solve_captcha_with_ocr(captcha_path)
            
            if captcha_solution:
                print(f"✅ CAPTCHA SOLVED: '{captcha_solution}'")
                return captcha_solution
            else:
                print("❌ CAPTCHA solving failed")
                return None
                
        except Exception as e:
            print(f"❌ CAPTCHA download/solve failed: {e}")
            return None

    def solve_captcha_with_ocr(self, captcha_path):
        """Solve CAPTCHA using multiple OCR methods"""
        try:
            print(f"📁 Processing CAPTCHA: {captcha_path}")
            
            ocr_results = []
            
            # Method 1: EasyOCR
            if self.ocr_reader:
                try:
                    print("🔍 Trying EasyOCR...")
                    results = self.ocr_reader.readtext(captcha_path)
                    for result in results:
                        text = result[1].strip().upper()
                        confidence = result[2]
                        if len(text) >= 4 and len(text) <= 8 and confidence > 0.5:
                            clean_text = ''.join(c for c in text if c.isalnum())
                            if len(clean_text) >= 4:
                                ocr_results.append((clean_text, confidence, "EasyOCR"))
                                print(f"   📝 EasyOCR: '{clean_text}' (confidence: {confidence:.2f})")
                except Exception as e:
                    print(f"   ⚠️ EasyOCR failed: {e}")
            
            # Method 2: Tesseract
            if TESSERACT_AVAILABLE:
                try:
                    print("🔍 Trying Tesseract...")
                    import cv2
                    
                    img = cv2.imread(captcha_path)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                    
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
                                print(f"   📝 Tesseract-{i+1}: '{clean_text}'")
                        except:
                            continue
                            
                except Exception as e:
                    print(f"   ⚠️ Tesseract failed: {e}")
            
            # Choose best solution
            if ocr_results:
                print(f"\n📊 Found {len(ocr_results)} OCR results:")
                for i, (text, conf, method) in enumerate(ocr_results):
                    print(f"   {i+1}. '{text}' from {method} (confidence: {conf:.2f})")
                
                # Auto-select high confidence result
                best_result = max(ocr_results, key=lambda x: x[1])
                if best_result[1] > 0.8:
                    print(f"\n🎯 Auto-selecting high confidence result: '{best_result[0]}'")
                    return best_result[0]
                
                # Show options
                print(f"\n👀 Check Firefox browser to see the actual CAPTCHA")
                print(f"📁 CAPTCHA image: {captcha_path}")
                
                while True:
                    choice = input(f"\nChoose: (1-{len(ocr_results)}) or 'm' for manual: ").strip().lower()
                    
                    if choice == 'm':
                        manual_input = input("Enter CAPTCHA manually: ").strip().upper()
                        if manual_input:
                            clean_manual = ''.join(c for c in manual_input if c.isalnum())
                            print(f"✅ Manual input: '{clean_manual}'")
                            return clean_manual
                    elif choice.isdigit() and 1 <= int(choice) <= len(ocr_results):
                        selected = ocr_results[int(choice)-1]
                        print(f"✅ Selected: '{selected[0]}'")
                        return selected[0]
                    else:
                        print("❌ Invalid choice")
            else:
                print("❌ No OCR results found")
                manual_input = input("Enter CAPTCHA manually: ").strip().upper()
                if manual_input:
                    clean_manual = ''.join(c for c in manual_input if c.isalnum())
                    return clean_manual
            
            return None
            
        except Exception as e:
            print(f"❌ OCR solving failed: {e}")
            return None

    def fill_form_with_solved_captcha(self, year_db, reg_year, village, captcha_solution):
        """STEP 2: Fill form with pre-solved CAPTCHA"""
        try:
            print(f"\n🎯 STEP 2: FILL FORM WITH SOLVED CAPTCHA")
            print("=" * 50)
            print(f"🤖 Form: Mumbai {village} - Year {reg_year}")
            print(f"🔤 CAPTCHA: '{captcha_solution}'")
            
            # 1. Select database
            print("📅 Selecting database...")
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            print(f"✅ Database: {year_db}")
            time.sleep(3)
            
            # 2. Select Mumbai district
            print("📍 Selecting Mumbai district...")
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value("31")
            print("✅ District: Mumbai (31)")
            time.sleep(3)
            
            # 3. Select Mumbai taluka
            print("🏘️ Selecting Mumbai taluka...")
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                print("✅ Taluka: Mumbai")
                time.sleep(3)
            
            # 4. Select village
            print(f"🏘️ Selecting village: {village}...")
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            
            village_found = False
            for option in village_options:
                if village.lower() in option.text.lower():
                    village_select.select_by_value(option.get_attribute('value'))
                    village_found = True
                    print(f"✅ Village: {option.text}")
                    break
            
            if not village_found and len(village_options) > 1:
                village_select.select_by_value(village_options[1].get_attribute('value'))
                print(f"✅ Village: {village_options[1].text}")
            
            time.sleep(2)
            
            # 5. Select Agreement to Sale
            print("📄 Selecting Agreement to Sale...")
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            print("✅ Article: Agreement to Sale (42)")
            time.sleep(2)
            
            # 6. Enter registration year
            print(f"📝 Entering registration year: {reg_year}...")
            free_text_input = self.firefox_driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            print(f"✅ Registration Year: {reg_year}")
            
            # 7. Enter pre-solved CAPTCHA
            print(f"🔤 Entering pre-solved CAPTCHA: '{captcha_solution}'...")
            captcha_input = self.firefox_driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            time.sleep(1)
            captcha_input.send_keys(captcha_solution)
            time.sleep(1)
            
            # Verify CAPTCHA was entered
            entered_value = captcha_input.get_attribute('value')
            print(f"✅ CAPTCHA entered: '{entered_value}'")
            
            if entered_value == captcha_solution:
                print("✅ FORM COMPLETELY FILLED WITH CAPTCHA!")
                return True
            else:
                print(f"⚠️ CAPTCHA mismatch: expected '{captcha_solution}', got '{entered_value}'")
                return False
                
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False

    def submit_and_check_results(self):
        """STEP 3: Submit form and check results"""
        try:
            print(f"\n🎯 STEP 3: SUBMIT FORM AND CHECK RESULTS")
            print("=" * 50)
            
            # Submit form
            try:
                submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                submit_button.click()
                print("📤 Form submitted!")
            except:
                print("❌ Could not find submit button")
                return False, 0
            
            # Wait for results
            print("⏳ Waiting for results...")
            time.sleep(8)
            
            # Check results
            try:
                page_source = self.firefox_driver.page_source.lower()
                
                # Check for CAPTCHA errors
                if any(error in page_source for error in ['invalid captcha', 'captcha error', 'wrong captcha']):
                    print("❌ CAPTCHA was incorrect!")
                    return False, 0
                
                # Check for no data
                if "no data available" in page_source:
                    print("❌ No documents found for this search")
                    return False, 0
                
                # Check for results
                if "showing" in page_source and "entries" in page_source:
                    print("✅ FOUND RESULTS!")
                    
                    try:
                        rows = self.firefox_driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                        doc_count = len([row for row in rows if row.get_attribute('innerHTML').strip()])
                        if doc_count > 0:
                            print(f"📊 Found {doc_count} documents!")
                            return True, doc_count
                    except:
                        pass
                    
                    print("✅ Documents found (count unknown)")
                    return True, 1
                
                print("⚠️ Unknown result")
                return False, 0
                
            except Exception as e:
                print(f"❌ Error checking results: {e}")
                return False, 0
                
        except Exception as e:
            print(f"❌ Submit failed: {e}")
            return False, 0

    def save_debug_info(self, params, success=False, doc_count=0):
        """Save debug information"""
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

    def run_captcha_first_automation(self):
        """Run automation with CAPTCHA-first approach"""
        print("🚀 CAPTCHA FIRST AUTOMATION")
        print("=" * 60)
        print("🎯 NEW APPROACH:")
        print("   1️⃣ Download and solve CAPTCHA first")
        print("   2️⃣ Fill form with solved CAPTCHA")
        print("   3️⃣ Submit and check results")
        print("   🚗 Chrome for Thordata proxy")
        print("   🦊 Firefox for website automation")
        print("=" * 60)
        
        total_documents = 0
        successful_searches = []
        
        for i, params in enumerate(self.search_params, 1):
            print(f"\n🚀 SEARCH {i}/{len(self.search_params)}")
            print(f"🔄 Mumbai {params['village']} - Year {params['reg_year']}")
            
            try:
                # Setup browsers
                session_id = self.setup_dual_browsers()
                if not session_id:
                    print("❌ Failed to setup browsers")
                    continue
                
                # STEP 1: Download and solve CAPTCHA first
                captcha_solution = self.download_and_solve_captcha_first(session_id)
                if not captcha_solution:
                    print("❌ CAPTCHA solving failed")
                    continue
                
                # STEP 2: Fill form with solved CAPTCHA
                if not self.fill_form_with_solved_captcha(params["year_db"], params["reg_year"], params["village"], captcha_solution):
                    print("❌ Form filling failed")
                    self.save_debug_info(params, False, 0)
                    continue
                
                # STEP 3: Submit and check results
                found_docs, doc_count = self.submit_and_check_results()
                
                if found_docs:
                    print(f"🎉 SUCCESS! Found {doc_count} documents")
                    successful_searches.append({**params, "doc_count": doc_count})
                    total_documents += doc_count
                    
                    self.save_debug_info(params, True, doc_count)
                    
                    continue_search = input(f"\n✅ Found {doc_count} documents! Continue? (y/n, default y): ").strip().lower()
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
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CAPTCHA FIRST AUTOMATION SUMMARY")
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
        """Clean up browsers"""
        try:
            if self.firefox_driver or self.chrome_driver:
                input("\nPress Enter to close browsers...")
                
                if self.firefox_driver:
                    self.firefox_driver.quit()
                    print("🧹 Firefox closed")
                    
                if self.chrome_driver:
                    self.chrome_driver.quit()
                    print("🧹 Chrome closed")
        except:
            pass

def main():
    print("🚀 CAPTCHA FIRST AUTOMATION SCRIPT")
    print("🎯 Better approach: CAPTCHA → Form → Submit")
    print("🚗 Chrome for Thordata proxy + 🦊 Firefox for website")
    
    automation = CaptchaFirstAutomation()
    
    try:
        successful_results = automation.run_captcha_first_automation()
        
        if successful_results:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print(f"Found documents in {len(successful_results)} searches")
        else:
            print("\n😔 No documents found")
            
    except KeyboardInterrupt:
        print("\n👋 Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 