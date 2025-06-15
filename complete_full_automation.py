#!/usr/bin/env python3
"""
COMPLETE FULL AUTOMATION - Everything Automated Including CAPTCHA
100% Automation: Form + CAPTCHA + Document Download
"""
import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from datetime import datetime
import urllib3
import json
import base64
import io

# Try to import OCR libraries
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompleteFullAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.search_url = f"{self.base_url}/eDisplay/Propertydetails/index"
        self.data_dir = "data"
        self.docs_dir = os.path.join(self.data_dir, "complete_automation_docs")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_attempts")
        
        for directory in [self.docs_dir, self.captcha_dir]:
            os.makedirs(directory, exist_ok=True)
        
        self.captcha_attempts = 0
        self.max_captcha_attempts = 10
        self.download_count = 0
        
        # Initialize OCR engines
        self.setup_ocr()
        self.print_header()

    def print_header(self):
        print("🚀 COMPLETE FULL AUTOMATION - 100% AUTOMATED")
        print("=" * 60)
        print("✅ Complete form automation (Database→District→Taluka→Village→Article)")
        print("🤖 Automatic CAPTCHA solving with multiple OCR engines")
        print("📥 Automated bulk document downloading")
        print("🔄 Automatic retry with different techniques")
        print(f"📁 Documents: {os.path.abspath(self.docs_dir)}")
        print(f"🖼️  CAPTCHAs: {os.path.abspath(self.captcha_dir)}")
        print("=" * 60)

    def setup_ocr(self):
        """Setup multiple OCR engines for maximum success rate"""
        self.ocr_engines = []
        
        if TESSERACT_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
                self.ocr_engines.append("tesseract")
                print("✅ Tesseract OCR available")
            except:
                print("⚠️ Tesseract OCR not working")
        
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = easyocr.Reader(['en'])
                self.ocr_engines.append("easyocr")
                print("✅ EasyOCR available")
            except:
                print("⚠️ EasyOCR not working")
        
        if not self.ocr_engines:
            print("⚠️ No OCR engines available - will use basic image analysis")
            self.ocr_engines.append("basic")

    def setup_driver(self):
        options = webdriver.FirefoxOptions()
        # Add preferences for better automation
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        # Execute script to hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def safe_select(self, driver, select_id, value):
        try:
            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, select_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            select = Select(element)
            select.select_by_value(value)
            print(f"   ✅ {select_id}: {value}")
            return True
        except Exception as e:
            print(f"   ❌ Failed {select_id}: {e}")
            return False

    def download_captcha_image(self, driver):
        """Download CAPTCHA image with multiple methods"""
        try:
            # Method 1: Find by common CAPTCHA selectors
            selectors = [
                "img[src*='captcha']",
                "img[alt*='captcha']", 
                "img[id*='captcha']",
                "img[class*='captcha']",
                "img[src*='verification']",
                "img[src*='code']"
            ]
            
            captcha_img = None
            for selector in selectors:
                try:
                    captcha_img = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not captcha_img:
                print("   ❌ CAPTCHA image not found")
                return None
            
            # Get image URL
            captcha_url = captcha_img.get_attribute('src')
            if not captcha_url:
                print("   ❌ CAPTCHA URL not found")
                return None
            
            if not captcha_url.startswith('http'):
                captcha_url = f"{self.base_url}{captcha_url}"
            
            # Download image
            response = requests.get(captcha_url, verify=False, timeout=10)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f'captcha_{timestamp}.png'
            filepath = os.path.join(self.captcha_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"   📷 CAPTCHA downloaded: {filename}")
            return filepath
            
        except Exception as e:
            print(f"   ❌ CAPTCHA download failed: {e}")
            return None

    def preprocess_captcha_advanced(self, image_path):
        """Advanced image preprocessing for better OCR"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return image_path
            
            # Convert to PIL for advanced processing
            pil_img = Image.open(image_path)
            
            # Multiple preprocessing techniques
            processed_images = []
            
            # Technique 1: Basic threshold
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            processed_images.append(thresh1)
            
            # Technique 2: Adaptive threshold
            thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            processed_images.append(thresh2)
            
            # Technique 3: OTSU threshold
            _, thresh3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(thresh3)
            
            # Technique 4: Morphological operations
            kernel = np.ones((2,2), np.uint8)
            morph = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
            morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
            processed_images.append(morph)
            
            # Technique 5: PIL enhancements
            enhanced = pil_img.convert('L')  # Grayscale
            enhanced = ImageEnhance.Contrast(enhanced).enhance(2.0)  # Increase contrast
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)  # Increase sharpness
            enhanced_array = np.array(enhanced)
            processed_images.append(enhanced_array)
            
            # Save all processed versions
            processed_paths = []
            base_name = image_path.replace('.png', '')
            
            for i, processed in enumerate(processed_images):
                processed_path = f"{base_name}_processed_{i+1}.png"
                cv2.imwrite(processed_path, processed)
                processed_paths.append(processed_path)
            
            return processed_paths
            
        except Exception as e:
            print(f"   ⚠️ Advanced preprocessing failed: {e}")
            return [image_path]

    def solve_captcha_tesseract(self, image_paths):
        """Solve CAPTCHA using Tesseract with multiple configurations"""
        if not TESSERACT_AVAILABLE:
            return None
        
        configs = [
            '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            '--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            '--psm 13',
            '--psm 8',
            '--psm 7',
            '--psm 6',
            '--psm 10',
            '--psm 9'
        ]
        
        for image_path in image_paths:
            for config in configs:
                try:
                    image = Image.open(image_path)
                    text = pytesseract.image_to_string(image, config=config).strip()
                    text = ''.join(c for c in text if c.isalnum())
                    
                    if text and len(text) >= 3 and len(text) <= 8:
                        print(f"   🔍 Tesseract solved: '{text}' (config: {config[:15]}...)")
                        return text
                except:
                    continue
        
        return None

    def solve_captcha_easyocr(self, image_paths):
        """Solve CAPTCHA using EasyOCR"""
        if not EASYOCR_AVAILABLE:
            return None
        
        for image_path in image_paths:
            try:
                results = self.easyocr_reader.readtext(image_path)
                for (bbox, text, confidence) in results:
                    text = ''.join(c for c in text if c.isalnum())
                    if text and len(text) >= 3 and len(text) <= 8 and confidence > 0.5:
                        print(f"   🔍 EasyOCR solved: '{text}' (confidence: {confidence:.2f})")
                        return text
            except:
                continue
        
        return None

    def solve_captcha_basic(self, image_paths):
        """Basic CAPTCHA solving using simple techniques"""
        try:
            # This is a placeholder for basic pattern recognition
            # You could implement simple character recognition here
            print("   🔍 Using basic CAPTCHA analysis...")
            
            # For now, return a common pattern or None
            # In a real implementation, you'd analyze the image patterns
            return None
            
        except:
            return None

    def solve_captcha_complete(self, driver):
        """Complete CAPTCHA solving with all available methods"""
        print("🤖 Starting automatic CAPTCHA solving...")
        
        self.captcha_attempts += 1
        if self.captcha_attempts > self.max_captcha_attempts:
            print(f"❌ Maximum CAPTCHA attempts ({self.max_captcha_attempts}) reached")
            return False
        
        # Download CAPTCHA image
        captcha_path = self.download_captcha_image(driver)
        if not captcha_path:
            return False
        
        # Advanced preprocessing
        processed_paths = self.preprocess_captcha_advanced(captcha_path)
        
        # Try all OCR engines
        captcha_solution = None
        
        for engine in self.ocr_engines:
            if engine == "tesseract":
                captcha_solution = self.solve_captcha_tesseract(processed_paths)
            elif engine == "easyocr":
                captcha_solution = self.solve_captcha_easyocr(processed_paths)
            elif engine == "basic":
                captcha_solution = self.solve_captcha_basic(processed_paths)
            
            if captcha_solution:
                break
        
        if not captcha_solution:
            print(f"   ❌ All OCR methods failed (attempt {self.captcha_attempts})")
            return False
        
        # Enter CAPTCHA solution
        try:
            captcha_selectors = [
                "input[name*='captcha']",
                "input[id*='captcha']",
                "input[placeholder*='captcha']",
                "input[class*='captcha']",
                "input[type='text'][name*='code']",
                "input[type='text'][id*='code']"
            ]
            
            captcha_input = None
            for selector in captcha_selectors:
                try:
                    captcha_input = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not captcha_input:
                print("   ❌ CAPTCHA input field not found")
                return False
            
            # Clear and enter solution
            captcha_input.clear()
            time.sleep(0.5)
            captcha_input.send_keys(captcha_solution)
            time.sleep(0.5)
            
            print(f"   ✅ CAPTCHA entered: '{captcha_solution}'")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to enter CAPTCHA: {e}")
            return False

    def submit_form_and_wait(self, driver):
        """Submit form and wait for results"""
        try:
            # Find and click submit button
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='Search']",
                "button:contains('Search')",
                "input[value*='search']",
                "button:contains('search')"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not submit_button:
                print("   ❌ Submit button not found")
                return False
            
            # Click submit
            driver.execute_script("arguments[0].click();", submit_button)
            print("   📤 Form submitted")
            
            # Wait for results with multiple checks
            print("   ⏳ Waiting for search results...")
            
            # Wait for page to change/load
            time.sleep(3)
            
            # Check for results indicators
            result_indicators = [
                "table",
                ".result",
                "#result",
                "[class*='result']",
                "a[href*='indexii']",
                "a[href*='view']"
            ]
            
            for i in range(10):  # Wait up to 10 seconds
                for indicator in result_indicators:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                        if elements:
                            print(f"   ✅ Results loaded (found {len(elements)} elements)")
                            return True
                    except:
                        continue
                time.sleep(1)
            
            print("   ⚠️ Results may have loaded (timeout reached)")
            return True
            
        except Exception as e:
            print(f"   ❌ Form submission failed: {e}")
            return False

    def download_documents_advanced(self, driver):
        """Advanced document downloading with multiple strategies"""
        print("\n📥 STARTING ADVANCED DOCUMENT DOWNLOAD...")
        
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Comprehensive link selectors
            selectors = [
                "table a[href*='indexii']",
                "a[href*='view']",
                "a[href*='document']", 
                "a[href*='pdf']",
                "a[href*='download']",
                "table a[href*='/eDisplay/']",
                "a[href*='propertydetails']",
                "a[href*='details']",
                "table a",  # All table links as fallback
                "a[href*='id=']"  # Links with ID parameters
            ]
            
            all_links = []
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    all_links.extend(found)
                    print(f"   📋 Found {len(found)} links with: {selector}")
            
            # Filter and deduplicate links
            unique_links = []
            seen_hrefs = set()
            
            for link in all_links:
                href = link.get('href', '')
                if href and href not in seen_hrefs:
                    # Filter out obviously non-document links
                    if any(skip in href.lower() for skip in ['javascript:', 'mailto:', '#', 'css', 'js']):
                        continue
                    unique_links.append(link)
                    seen_hrefs.add(href)
            
            if not unique_links:
                print("❌ No document links found")
                # Save debug information
                debug_file = os.path.join(self.docs_dir, f'debug_results_{datetime.now().strftime("%H%M%S")}.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"📄 Debug file saved: {debug_file}")
                return 0
            
            print(f"\n📄 Found {len(unique_links)} unique document links")
            print("🚀 Starting automated bulk download...")
            
            # Download each document
            for i, link in enumerate(unique_links):
                print(f"\n📥 Downloading document {i+1}/{len(unique_links)}...")
                
                href = link.get('href', '')
                doc_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                
                # Create new driver for each document
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    link_text = link.get_text(strip=True)[:30] if link.get_text(strip=True) else "doc"
                    safe_text = ''.join(c for c in link_text if c.isalnum() or c in ' -_')
                    filename = f"Auto_Doc_{i+1:03d}_{safe_text}_{timestamp}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    # Save document
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(doc_driver.page_source)
                    
                    # Save metadata
                    metadata = {
                        'filename': filename,
                        'url': doc_url,
                        'link_text': link.get_text(strip=True),
                        'downloaded_at': datetime.now().isoformat(),
                        'document_number': i + 1,
                        'file_size': os.path.getsize(filepath)
                    }
                    
                    meta_file = os.path.join(self.docs_dir, f"{filename}_metadata.json")
                    with open(meta_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    self.download_count += 1
                    print(f"   ✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error downloading document {i+1}: {e}")
                finally:
                    doc_driver.quit()
                
                # Brief pause between downloads
                time.sleep(1)
            
            return self.download_count
            
        except Exception as e:
            print(f"❌ Document download failed: {e}")
            return 0

    def run_complete_automation(self):
        """Run complete automation with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            print(f"\n🚀 STARTING COMPLETE AUTOMATION (Attempt {attempt + 1}/{max_retries})")
            
            driver = self.setup_driver()
            try:
                # Load website
                print("\n🌐 Loading IGR website...")
                driver.get(self.search_url)
                time.sleep(3)
                
                # Form automation
                print("\n🤖 AUTOMATING COMPLETE FORM...")
                
                # Database
                print("[1/5] Database selection...")
                if not self.safe_select(driver, "dbselect", "3"):
                    continue
                time.sleep(2)
                
                # District
                print("[2/5] Mumbai district selection...")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']")))
                if not self.safe_select(driver, "district_id", "31"):
                    continue
                time.sleep(2)
                
                # Taluka
                print("[3/5] Taluka selection...")
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
                    taluka_select = Select(driver.find_element(By.ID, "taluka_id"))
                    if len(taluka_select.options) > 1:
                        taluka_select.select_by_index(1)
                        print("   ✅ Taluka auto-selected")
                    time.sleep(2)
                except:
                    print("   ⚠️ Taluka not available")
                
                # Village
                print("[4/5] Village selection...")
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                    village_select = Select(driver.find_element(By.ID, "village_id"))
                    if len(village_select.options) > 1:
                        village_select.select_by_index(1)
                        print("   ✅ Village auto-selected")
                    time.sleep(2)
                except:
                    print("   ⚠️ Village not available")
                
                # Article
                print("[5/5] Agreement to Sale article selection...")
                if not self.safe_select(driver, "article_id", "42"):
                    continue
                time.sleep(2)
                
                print("\n✅ FORM AUTOMATION COMPLETED!")
                
                # CAPTCHA solving
                if self.solve_captcha_complete(driver):
                    # Submit form
                    if self.submit_form_and_wait(driver):
                        # Download documents
                        downloaded = self.download_documents_advanced(driver)
                        
                        if downloaded > 0:
                            # SUCCESS!
                            print("\n" + "="*60)
                            print("🎉 COMPLETE AUTOMATION SUCCESS!")
                            print(f"📊 Successfully downloaded: {downloaded} documents")
                            print(f"📁 Documents location: {os.path.abspath(self.docs_dir)}")
                            print(f"🖼️ CAPTCHAs saved: {os.path.abspath(self.captcha_dir)}")
                            print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print("="*60)
                            return True
                        else:
                            print("⚠️ No documents found, retrying...")
                    else:
                        print("❌ Form submission failed, retrying...")
                else:
                    print("❌ CAPTCHA solving failed, retrying...")
                
            except Exception as e:
                print(f"❌ Automation error: {e}")
            finally:
                driver.quit()
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        print("\n❌ All automation attempts failed")
        return False

if __name__ == "__main__":
    print("🔧 Checking OCR dependencies...")
    
    if not TESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
        print("⚠️ No OCR engines available")
        print("💡 Install Tesseract: https://github.com/tesseract-ocr/tesseract")
        print("💡 Install EasyOCR: pip install easyocr")
        print("🚀 Continuing with basic methods...")
    
    automation = CompleteFullAutomation()
    automation.run_complete_automation()