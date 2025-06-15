#!/usr/bin/env python3
"""
CAPTCHA TESTING SCRIPT
Test only the CAPTCHA solving functionality to debug issues
"""

import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import requests
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

class CaptchaTest:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/captcha_test"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize OCR
        self.ocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.ocr_reader = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized")
            except:
                print("⚠️ EasyOCR initialization failed")
        
        self.driver = None
        self.wait = None

    def setup_firefox(self):
        """Setup Firefox for testing"""
        try:
            options = Options()
            # Visible browser
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            print("🦊 Firefox started for CAPTCHA testing")
            return True
        except Exception as e:
            print(f"❌ Firefox setup failed: {e}")
            return False

    def test_captcha_solving(self):
        """Test CAPTCHA solving functionality"""
        try:
            print("\n🧪 TESTING CAPTCHA SOLVING")
            print("=" * 50)
            
            # Load website
            print("🌐 Loading IGR website...")
            self.driver.get(self.base_url)
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
                print("❌ CAPTCHA not found - maybe page not loaded properly")
                return False
            
            # Download CAPTCHA image
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'test_captcha_{timestamp}.png')
            
            try:
                print("📥 Downloading CAPTCHA image...")
                response = requests.get(captcha_src, verify=False, timeout=10)
                if response.status_code == 200:
                    with open(captcha_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ CAPTCHA saved: {captcha_path}")
                else:
                    print(f"❌ Download failed: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Download failed: {e}")
                return False
            
            # Test OCR methods
            print("\n🔍 TESTING OCR METHODS")
            print("-" * 30)
            
            ocr_results = []
            
            # Test EasyOCR
            if self.ocr_reader:
                try:
                    print("🔍 Testing EasyOCR...")
                    results = self.ocr_reader.readtext(captcha_path)
                    for result in results:
                        text = result[1].strip().upper()
                        confidence = result[2]
                        clean_text = ''.join(c for c in text if c.isalnum())
                        if len(clean_text) >= 3:
                            ocr_results.append((clean_text, confidence, "EasyOCR"))
                            print(f"   📝 EasyOCR: '{clean_text}' (confidence: {confidence:.2f})")
                except Exception as e:
                    print(f"   ❌ EasyOCR failed: {e}")
            
            # Test Tesseract
            if TESSERACT_AVAILABLE:
                try:
                    print("🔍 Testing Tesseract...")
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
                            if len(clean_text) >= 3:
                                ocr_results.append((clean_text, 0.7, f"Tesseract-{i+1}"))
                                print(f"   📝 Tesseract-{i+1}: '{clean_text}'")
                        except Exception as e:
                            print(f"   ❌ Tesseract config {i+1} failed: {e}")
                            
                except Exception as e:
                    print(f"   ❌ Tesseract failed: {e}")
            
            # Show results
            print(f"\n📊 OCR RESULTS SUMMARY")
            print("-" * 30)
            
            if ocr_results:
                print(f"Found {len(ocr_results)} OCR results:")
                for i, (text, conf, method) in enumerate(ocr_results):
                    print(f"   {i+1}. '{text}' from {method} (confidence: {conf:.2f})")
                
                # Test manual input
                print(f"\n👀 Look at the Firefox browser to see the actual CAPTCHA")
                print(f"📁 CAPTCHA image saved at: {captcha_path}")
                
                while True:
                    print(f"\nOptions:")
                    for i, (text, conf, method) in enumerate(ocr_results):
                        print(f"   {i+1}. Use '{text}' from {method}")
                    print(f"   m. Enter manually")
                    print(f"   q. Quit test")
                    
                    choice = input(f"\nChoose option: ").strip().lower()
                    
                    if choice == 'q':
                        break
                    elif choice == 'm':
                        manual_text = input("Enter CAPTCHA manually: ").strip().upper()
                        if manual_text:
                            print(f"✅ Manual input: '{manual_text}'")
                            self.test_captcha_submission(manual_text)
                        break
                    elif choice.isdigit() and 1 <= int(choice) <= len(ocr_results):
                        selected = ocr_results[int(choice)-1]
                        print(f"✅ Selected: '{selected[0]}' from {selected[2]}")
                        self.test_captcha_submission(selected[0])
                        break
                    else:
                        print("❌ Invalid choice")
            else:
                print("❌ No OCR results found")
                manual_text = input("Enter CAPTCHA manually: ").strip().upper()
                if manual_text:
                    self.test_captcha_submission(manual_text)
            
            return True
            
        except Exception as e:
            print(f"❌ CAPTCHA test failed: {e}")
            return False

    def test_captcha_submission(self, captcha_text):
        """Test submitting the CAPTCHA"""
        try:
            print(f"\n🧪 TESTING CAPTCHA SUBMISSION: '{captcha_text}'")
            
            # Find CAPTCHA input field
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            
            # Verify input
            entered_value = captcha_input.get_attribute('value')
            print(f"📝 Entered: '{captcha_text}'")
            print(f"✅ Field shows: '{entered_value}'")
            
            if entered_value == captcha_text:
                print("✅ CAPTCHA input successful!")
                
                # Ask if user wants to submit
                submit = input("Submit form to test? (y/n): ").strip().lower()
                if submit == 'y':
                    try:
                        submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                        submit_button.click()
                        print("📤 Form submitted!")
                        
                        time.sleep(5)
                        
                        # Check result
                        page_source = self.driver.page_source.lower()
                        if "invalid captcha" in page_source or "captcha error" in page_source:
                            print("❌ CAPTCHA was incorrect")
                        elif "no data available" in page_source:
                            print("✅ CAPTCHA was correct! (No data found for search)")
                        elif "showing" in page_source:
                            print("✅ CAPTCHA was correct! (Found results)")
                        else:
                            print("⚠️ Unknown result")
                            
                    except Exception as e:
                        print(f"❌ Submit failed: {e}")
            else:
                print("❌ CAPTCHA input mismatch!")
                
        except Exception as e:
            print(f"❌ CAPTCHA submission test failed: {e}")

    def cleanup(self):
        """Clean up"""
        try:
            if self.driver:
                input("\nPress Enter to close browser...")
                self.driver.quit()
                print("🧹 Browser closed")
        except:
            pass

def main():
    print("🧪 CAPTCHA TESTING SCRIPT")
    print("This script tests only the CAPTCHA solving functionality")
    print("=" * 60)
    
    test = CaptchaTest()
    
    try:
        if not test.setup_firefox():
            print("❌ Failed to setup Firefox")
            return
        
        success = test.test_captcha_solving()
        
        if success:
            print("\n✅ CAPTCHA test completed!")
        else:
            print("\n❌ CAPTCHA test failed!")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        test.cleanup()

if __name__ == "__main__":
    main() 