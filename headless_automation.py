#!/usr/bin/env python3
"""
HEADLESS BROWSER AUTOMATION
Runs completely in background - no visible browser windows
Fast CAPTCHA solving and form filling
"""

import time
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import urllib3
urllib3.disable_warnings()

# Try OCR
try:
    import easyocr
    EASYOCR_OK = True
    print("✅ EasyOCR available")
except:
    EASYOCR_OK = False
    print("⚠️ EasyOCR not available")

try:
    import pytesseract
    TESSERACT_OK = True
    print("✅ Tesseract available")
except:
    TESSERACT_OK = False
    print("⚠️ Tesseract not available")

class HeadlessAutomation:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/headless_automation"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # OCR setup
        self.ocr = None
        if EASYOCR_OK:
            try:
                self.ocr = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized")
            except:
                print("⚠️ EasyOCR init failed")
        
        self.driver = None
        self.wait = None
        
        # Search parameters
        self.searches = [
            {"year_db": 3, "reg_year": 2024, "village": "Andheri"},
            {"year_db": 3, "reg_year": 2023, "village": "Bandra"},
            {"year_db": 3, "reg_year": 2022, "village": "Borivali"},
            {"year_db": 2, "reg_year": 2021, "village": "Malad"},
        ]

    def start_headless_browser(self):
        """Start headless Firefox"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(1)
            
            options = Options()
            
            # HEADLESS MODE - no visible browser
            options.add_argument('--headless')
            
            # Performance optimizations
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Disable images and CSS for faster loading
            options.set_preference("permissions.default.image", 2)
            options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("🤖 Headless Firefox started")
            return True
            
        except Exception as e:
            print(f"❌ Headless browser failed: {e}")
            return False

    def download_captcha_headless(self):
        """Download CAPTCHA in headless mode"""
        try:
            print("📥 Downloading CAPTCHA (headless)...")
            
            # Load website
            self.driver.get(self.url)
            time.sleep(3)
            
            # Find CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            try:
                # Direct download
                response = requests.get(captcha_src, verify=False, timeout=10)
                if response.status_code == 200:
                    with open(captcha_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ CAPTCHA downloaded: {captcha_path}")
                else:
                    raise Exception(f"HTTP {response.status_code}")
            except:
                # Screenshot fallback
                captcha_screenshot = captcha_img.screenshot_as_png
                with open(captcha_path, 'wb') as f:
                    f.write(captcha_screenshot)
                print(f"✅ CAPTCHA screenshot: {captcha_path}")
            
            return captcha_path
            
        except Exception as e:
            print(f"❌ CAPTCHA download failed: {e}")
            return None

    def solve_captcha_automatically(self, captcha_path):
        """Solve CAPTCHA automatically using multiple OCR methods"""
        try:
            print("🤖 Solving CAPTCHA automatically...")
            
            solutions = []
            
            # Method 1: EasyOCR
            if self.ocr:
                try:
                    results = self.ocr.readtext(captcha_path)
                    for result in results:
                        text = result[1].strip().upper()
                        confidence = result[2]
                        if len(text) >= 4 and len(text) <= 8 and confidence > 0.5:
                            clean_text = ''.join(c for c in text if c.isalnum())
                            if len(clean_text) >= 4:
                                solutions.append((clean_text, confidence, "EasyOCR"))
                                print(f"   🔍 EasyOCR: '{clean_text}' (confidence: {confidence:.2f})")
                except Exception as e:
                    print(f"   ⚠️ EasyOCR failed: {e}")
            
            # Method 2: Tesseract
            if TESSERACT_OK:
                try:
                    import cv2
                    
                    img = cv2.imread(captcha_path)
                    if img is not None:
                        # Preprocess image
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                        
                        # Try different Tesseract configs
                        configs = [
                            '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                            '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                            '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        ]
                        
                        for i, config in enumerate(configs):
                            try:
                                text = pytesseract.image_to_string(thresh, config=config).strip().upper()
                                clean_text = ''.join(c for c in text if c.isalnum())
                                if len(clean_text) >= 4 and len(clean_text) <= 8:
                                    solutions.append((clean_text, 0.7, f"Tesseract-{i+1}"))
                                    print(f"   🔍 Tesseract-{i+1}: '{clean_text}'")
                            except:
                                continue
                                
                except Exception as e:
                    print(f"   ⚠️ Tesseract failed: {e}")
            
            # Choose best solution
            if solutions:
                # Sort by confidence
                solutions.sort(key=lambda x: x[1], reverse=True)
                best_solution = solutions[0]
                
                print(f"   🎯 Best solution: '{best_solution[0]}' from {best_solution[2]} (confidence: {best_solution[1]:.2f})")
                
                # Auto-select high confidence results
                if best_solution[1] > 0.8:
                    print(f"   ✅ Auto-selected high confidence result")
                    return best_solution[0]
                
                # If multiple solutions agree, use the common one
                texts = [sol[0] for sol in solutions]
                if len(set(texts)) == 1:
                    print(f"   ✅ All OCR methods agree on: '{texts[0]}'")
                    return texts[0]
                
                # Auto-select best if confidence is reasonable
                if best_solution[1] > 0.6:
                    print(f"   🎯 Auto-selecting best result: '{best_solution[0]}'")
                    return best_solution[0]
                
                # If no high confidence, return best guess
                print(f"   🤖 Using best guess: '{best_solution[0]}'")
                return best_solution[0]
            else:
                print("   ❌ No OCR solutions found")
                return None
            
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return None

    def fill_form_headless(self, year_db, reg_year, village, captcha_solution):
        """Fill form in headless mode"""
        try:
            print(f"📝 Filling form (headless): Mumbai {village} - {reg_year}")
            print(f"🔤 Using CAPTCHA: '{captcha_solution}'")
            
            # 1. Database selection
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            print(f"   ✅ Database: {year_db}")
            time.sleep(2)
            
            # 2. Mumbai district
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value("31")
            print("   ✅ District: Mumbai (31)")
            time.sleep(2)
            
            # 3. Mumbai taluka
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                print("   ✅ Taluka: Mumbai")
                time.sleep(2)
            
            # 4. Village selection
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            
            village_found = False
            for option in village_options:
                if village.lower() in option.text.lower():
                    village_select.select_by_value(option.get_attribute('value'))
                    village_found = True
                    print(f"   ✅ Village: {option.text}")
                    break
            
            if not village_found and len(village_options) > 1:
                village_select.select_by_value(village_options[1].get_attribute('value'))
                print(f"   ✅ Village: {village_options[1].text}")
            
            time.sleep(1)
            
            # 5. Agreement to Sale
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            print("   ✅ Article: Agreement to Sale (42)")
            time.sleep(1)
            
            # 6. Registration year
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            print(f"   ✅ Registration Year: {reg_year}")
            
            # 7. CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            time.sleep(0.5)
            captcha_input.send_keys(captcha_solution)
            print(f"   ✅ CAPTCHA entered: '{captcha_solution}'")
            
            # Verify CAPTCHA was entered correctly
            entered_value = captcha_input.get_attribute('value')
            if entered_value == captcha_solution:
                print("✅ Form filled successfully!")
                return True
            else:
                print(f"⚠️ CAPTCHA mismatch: expected '{captcha_solution}', got '{entered_value}'")
                return False
                
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False

    def submit_and_check_headless(self):
        """Submit form and check results in headless mode"""
        try:
            print("🚀 Submitting form (headless)...")
            
            # Submit
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            print("   📤 Form submitted!")
            
            # Wait for results
            time.sleep(6)
            
            # Check results
            page_source = self.driver.page_source.lower()
            
            if any(error in page_source for error in ['invalid captcha', 'captcha error', 'wrong captcha']):
                print("   ❌ CAPTCHA was incorrect")
                return False, 0
            elif "no data available" in page_source:
                print("   ❌ No documents found")
                return False, 0
            elif "showing" in page_source and "entries" in page_source:
                print("   ✅ FOUND RESULTS!")
                
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    doc_count = len([row for row in rows if row.get_attribute('innerHTML').strip()])
                    if doc_count > 0:
                        print(f"   📊 Found {doc_count} documents!")
                        return True, doc_count
                except:
                    pass
                
                print("   ✅ Documents found (count unknown)")
                return True, 1
            else:
                print("   ⚠️ Unknown result")
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
                f.write(self.driver.page_source)
            
            print(f"📄 Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")

    def run_headless_automation(self):
        """Run complete headless automation"""
        print("🚀 HEADLESS BROWSER AUTOMATION")
        print("=" * 60)
        print("🤖 COMPLETELY AUTOMATED:")
        print("   🔍 Headless browser - no visible windows")
        print("   📥 Automatic CAPTCHA download")
        print("   🤖 Multi-method OCR solving")
        print("   📝 Automatic form filling")
        print("   🚀 Fast execution")
        print("=" * 60)
        
        total_documents = 0
        successful_searches = []
        
        for i, params in enumerate(self.searches, 1):
            print(f"\n🚀 SEARCH {i}/{len(self.searches)}")
            print(f"🔄 Mumbai {params['village']} - Year {params['reg_year']}")
            
            try:
                # Start headless browser
                if not self.start_headless_browser():
                    print("❌ Failed to start headless browser")
                    continue
                
                # Download and solve CAPTCHA
                captcha_path = self.download_captcha_headless()
                if not captcha_path:
                    print("❌ CAPTCHA download failed")
                    continue
                
                captcha_solution = self.solve_captcha_automatically(captcha_path)
                if not captcha_solution:
                    print("❌ CAPTCHA solving failed")
                    continue
                
                # Fill form
                if not self.fill_form_headless(params["year_db"], params["reg_year"], params["village"], captcha_solution):
                    print("❌ Form filling failed")
                    self.save_debug_info(params, False, 0)
                    continue
                
                # Submit and check
                found_docs, doc_count = self.submit_and_check_headless()
                
                if found_docs:
                    print(f"🎉 SUCCESS! Found {doc_count} documents")
                    successful_searches.append({**params, "doc_count": doc_count})
                    total_documents += doc_count
                    
                    self.save_debug_info(params, True, doc_count)
                    
                    # Ask if user wants to continue
                    continue_search = input(f"\n✅ Found {doc_count} documents! Continue? (y/n, default y): ").strip().lower()
                    if continue_search == 'n':
                        break
                else:
                    print("❌ No documents found")
                    self.save_debug_info(params, False, 0)
                
                # Brief pause between searches
                if i < len(self.searches):
                    print("⏳ Waiting 3s before next search...")
                    time.sleep(3)
                
            except Exception as e:
                print(f"❌ Search {i} failed: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 HEADLESS AUTOMATION SUMMARY")
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
        """Clean up headless browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Headless browser closed")
        except:
            pass

def main():
    print("🚀 HEADLESS BROWSER AUTOMATION")
    print("🤖 Fast, automated, no visible browser windows!")
    print("🔍 CAPTCHA solving + Form filling in background")
    
    automation = HeadlessAutomation()
    
    try:
        successful_results = automation.run_headless_automation()
        
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