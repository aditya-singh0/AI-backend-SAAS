#!/usr/bin/env python3
"""
SIMPLE FIREFOX AUTOMATION
CAPTCHA first approach - download, solve, then fill form
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

class SimpleFirefoxAutomation:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/simple_firefox"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # OCR
        self.ocr = None
        if EASYOCR_OK:
            try:
                self.ocr = easyocr.Reader(['en'])
                print("✅ EasyOCR ready")
            except:
                print("⚠️ EasyOCR failed")
        
        self.driver = None
        self.wait = None

    def start_firefox(self):
        """Start Firefox"""
        try:
            options = Options()
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            print("🦊 Firefox started")
            return True
        except Exception as e:
            print(f"❌ Firefox failed: {e}")
            return False

    def get_captcha(self):
        """Get and solve CAPTCHA"""
        try:
            print("\n🎯 GETTING CAPTCHA")
            
            # Load site
            print("🌐 Loading website...")
            self.driver.get(self.url)
            time.sleep(5)
            
            # Find CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            print("✅ CAPTCHA found")
            
            # Download
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            try:
                response = requests.get(captcha_src, verify=False, timeout=10)
                with open(captcha_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded: {captcha_path}")
            except:
                # Screenshot fallback
                captcha_screenshot = captcha_img.screenshot_as_png
                with open(captcha_path, 'wb') as f:
                    f.write(captcha_screenshot)
                print(f"✅ Screenshot: {captcha_path}")
            
            # Solve
            solution = self.solve_captcha(captcha_path)
            return solution
            
        except Exception as e:
            print(f"❌ CAPTCHA failed: {e}")
            return None

    def solve_captcha(self, path):
        """Solve CAPTCHA"""
        try:
            results = []
            
            # Try EasyOCR
            if self.ocr:
                try:
                    ocr_results = self.ocr.readtext(path)
                    for result in ocr_results:
                        text = result[1].strip().upper()
                        conf = result[2]
                        if len(text) >= 4 and conf > 0.5:
                            clean = ''.join(c for c in text if c.isalnum())
                            if len(clean) >= 4:
                                results.append((clean, conf))
                                print(f"🔍 EasyOCR: '{clean}' ({conf:.2f})")
                except Exception as e:
                    print(f"⚠️ EasyOCR error: {e}")
            
            # Choose solution
            if results:
                best = max(results, key=lambda x: x[1])
                if best[1] > 0.8:
                    print(f"🎯 Auto-select: '{best[0]}'")
                    return best[0]
                
                print(f"\n📊 OCR Results:")
                for i, (text, conf) in enumerate(results):
                    print(f"   {i+1}. '{text}' ({conf:.2f})")
                
                print("👀 Check Firefox browser to see CAPTCHA")
                while True:
                    choice = input(f"Choose 1-{len(results)} or 'm' for manual: ").strip()
                    if choice == 'm':
                        manual = input("Enter CAPTCHA: ").strip().upper()
                        return ''.join(c for c in manual if c.isalnum()) if manual else None
                    elif choice.isdigit() and 1 <= int(choice) <= len(results):
                        return results[int(choice)-1][0]
                    print("❌ Invalid choice")
            else:
                print("❌ No OCR results")
                manual = input("Enter CAPTCHA manually: ").strip().upper()
                return ''.join(c for c in manual if c.isalnum()) if manual else None
                
        except Exception as e:
            print(f"❌ Solve failed: {e}")
            return None

    def fill_form(self, captcha_text):
        """Fill form with CAPTCHA"""
        try:
            print(f"\n🎯 FILLING FORM")
            print(f"🔤 CAPTCHA: '{captcha_text}'")
            
            # Database
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value("3")
            print("✅ Database: 3")
            time.sleep(3)
            
            # District (Mumbai = 31)
            district = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district.select_by_value("31")
            print("✅ District: Mumbai")
            time.sleep(3)
            
            # Taluka
            taluka = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            options = [opt for opt in taluka.options if opt.get_attribute('value')]
            if options:
                taluka.select_by_value(options[0].get_attribute('value'))
                print("✅ Taluka: First available")
                time.sleep(3)
            
            # Village
            village = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            v_options = village.options
            if len(v_options) > 1:
                village.select_by_value(v_options[1].get_attribute('value'))
                print("✅ Village: First available")
                time.sleep(2)
            
            # Article (Agreement to Sale = 42)
            article = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article.select_by_value("42")
            print("✅ Article: Agreement to Sale")
            time.sleep(2)
            
            # Year
            year_input = self.driver.find_element(By.ID, "free_text")
            year_input.clear()
            year_input.send_keys("2024")
            print("✅ Year: 2024")
            
            # CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            time.sleep(1)
            captcha_input.send_keys(captcha_text)
            print(f"✅ CAPTCHA entered: '{captcha_text}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Form fill failed: {e}")
            return False

    def submit_form(self):
        """Submit and check results"""
        try:
            print(f"\n🎯 SUBMITTING")
            
            # Submit
            submit_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_btn.click()
            print("📤 Submitted!")
            
            # Wait
            time.sleep(8)
            
            # Check results
            page = self.driver.page_source.lower()
            
            if "invalid captcha" in page:
                print("❌ CAPTCHA wrong")
                return False
            elif "no data available" in page:
                print("❌ No documents")
                return False
            elif "showing" in page:
                print("✅ FOUND RESULTS!")
                return True
            else:
                print("⚠️ Unknown result")
                return False
                
        except Exception as e:
            print(f"❌ Submit failed: {e}")
            return False

    def run(self):
        """Run automation"""
        print("🚀 SIMPLE FIREFOX AUTOMATION")
        print("=" * 40)
        
        try:
            # Start
            if not self.start_firefox():
                return False
            
            # CAPTCHA
            captcha = self.get_captcha()
            if not captcha:
                print("❌ No CAPTCHA solution")
                return False
            
            # Form
            if not self.fill_form(captcha):
                print("❌ Form failed")
                return False
            
            # Submit
            success = self.submit_form()
            
            if success:
                print("🎉 SUCCESS!")
            else:
                print("❌ FAILED")
            
            return success
            
        except Exception as e:
            print(f"❌ Run failed: {e}")
            return False

    def cleanup(self):
        """Close browser"""
        try:
            if self.driver:
                input("\nPress Enter to close...")
                self.driver.quit()
                print("🧹 Closed")
        except:
            pass

def main():
    print("🚀 SIMPLE FIREFOX AUTOMATION")
    
    automation = SimpleFirefoxAutomation()
    
    try:
        success = automation.run()
        if success:
            print("\n🎉 COMPLETED SUCCESSFULLY!")
        else:
            print("\n😔 FAILED")
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 