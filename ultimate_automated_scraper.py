#!/usr/bin/env python3
"""
Ultimate Automated IGR Scraper
Complete automation: Form filling → CAPTCHA solving → Document downloading
Uses all selectors: Database → District → Taluka → Village → Article
"""
import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import cv2
import numpy as np
from datetime import datetime
import json

class UltimateAutomatedScraper:
    def __init__(self):
        # All confirmed selectors
        self.DATABASE_VALUE = '3'  # Recent years
        self.MUMBAI_DISTRICT = '31'  # Mumbai City
        self.AGREEMENT_ARTICLE = '42'  # विकसनकरारनामा (Agreement to Sale)
        
        # URLs
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        
        # Data organization
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'automated_documents')
        self.captcha_dir = os.path.join(self.data_dir, 'captchas')
        self.metadata_dir = os.path.join(self.data_dir, 'metadata')
        
        # Create directories
        for directory in [self.docs_dir, self.captcha_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
        
        self.download_count = 0
        self.captcha_attempts = 0
        self.max_captcha_attempts = 5
        
        self.print_header()

    def print_header(self):
        print("🚀 ULTIMATE AUTOMATED IGR SCRAPER")
        print("=" * 60)
        print("✅ Complete form automation (Database→District→Taluka→Village→Article)")
        print("🤖 Automatic CAPTCHA solving with OCR")
        print("📥 Bulk document downloading")
        print("💾 Organized data folder structure")
        print(f"📁 Documents: {os.path.abspath(self.docs_dir)}")
        print(f"🖼️  CAPTCHAs: {os.path.abspath(self.captcha_dir)}")
        print(f"📋 Metadata: {os.path.abspath(self.metadata_dir)}")
        print("=" * 60)

    def setup_driver(self):
        print("🚀 Setting up Firefox WebDriver...")
        options = webdriver.FirefoxOptions()
        # Add download preferences
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", os.path.abspath(self.docs_dir))
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf,text/html,application/octet-stream")
        
        try:
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_window_size(1280, 1024)
            print("✅ Firefox WebDriver active")
            return driver
        except Exception as e:
            print(f"❌ Firefox setup failed: {e}")
            sys.exit(1)

    def safe_select(self, driver, select_id, value, by_value=True, wait_time=10):
        """Safely select dropdown option with multiple fallback methods"""
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((By.ID, select_id))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            select = Select(element)
            
            if by_value:
                select.select_by_value(value)
            else:
                select.select_by_visible_text(value)
            
            print(f"   ✅ Selected {select_id}: {value}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to select {select_id}: {e}")
            return False

    def get_dropdown_options(self, driver, select_id, name=""):
        """Get all options from a dropdown"""
        try:
            element = driver.find_element(By.ID, select_id)
            select = Select(element)
            options = []
            
            for option in select.options:
                value = option.get_attribute('value')
                text = option.text.strip()
                if value:  # Skip empty values
                    options.append({'value': value, 'text': text})
            
            print(f"   📋 Found {len(options)} {name} options")
            return options
            
        except Exception as e:
            print(f"   ❌ Error getting {name} options: {e}")
            return []

    def download_captcha_image(self, driver):
        """Download CAPTCHA image for OCR processing"""
        try:
            # Find CAPTCHA image
            captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha'], img[alt*='captcha'], img[id*='captcha']")
            captcha_url = captcha_img.get_attribute('src')
            
            if not captcha_url.startswith('http'):
                captcha_url = f"{self.base_url}{captcha_url}"
            
            # Download image
            response = requests.get(captcha_url, stream=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'captcha_{timestamp}.png'
            filepath = os.path.join(self.captcha_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   📷 CAPTCHA saved: {filename}")
            return filepath
            
        except Exception as e:
            print(f"   ❌ CAPTCHA download failed: {e}")
            return None

    def preprocess_captcha(self, image_path):
        """Preprocess CAPTCHA image for better OCR accuracy"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get black and white image
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Remove noise
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Resize for better OCR
            height, width = cleaned.shape
            cleaned = cv2.resize(cleaned, (width*3, height*3), interpolation=cv2.INTER_CUBIC)
            
            # Save processed image
            processed_path = image_path.replace('.png', '_processed.png')
            cv2.imwrite(processed_path, cleaned)
            
            return processed_path
            
        except Exception as e:
            print(f"   ⚠️ Image preprocessing failed: {e}")
            return image_path

    def solve_captcha_ocr(self, image_path):
        """Solve CAPTCHA using OCR with multiple configurations"""
        try:
            # Preprocess image
            processed_path = self.preprocess_captcha(image_path)
            image = Image.open(processed_path)
            
            # Try different OCR configurations
            configs = [
                '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 13',
                '--psm 8',
                '--psm 7'
            ]
            
            for config in configs:
                try:
                    captcha_text = pytesseract.image_to_string(image, config=config).strip()
                    # Clean the text
                    captcha_text = ''.join(c for c in captcha_text if c.isalnum())
                    
                    if captcha_text and len(captcha_text) >= 3:
                        print(f"   🔍 CAPTCHA solved: '{captcha_text}' (config: {config[:10]}...)")
                        return captcha_text
                except:
                    continue
            
            print("   ❌ OCR failed to solve CAPTCHA")
            return None
            
        except Exception as e:
            print(f"   ❌ CAPTCHA solving error: {e}")
            return None

    def handle_captcha(self, driver):
        """Complete CAPTCHA handling workflow"""
        print("🤖 CAPTCHA detected - starting automatic solving...")
        
        self.captcha_attempts += 1
        if self.captcha_attempts > self.max_captcha_attempts:
            print(f"❌ Maximum CAPTCHA attempts ({self.max_captcha_attempts}) reached")
            return None
        
        # Download CAPTCHA image
        captcha_image_path = self.download_captcha_image(driver)
        if not captcha_image_path:
            return None
        
        # Solve using OCR
        captcha_solution = self.solve_captcha_ocr(captcha_image_path)
        if captcha_solution:
            # Enter CAPTCHA solution
            try:
                captcha_input = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha'], input[id*='captcha'], input[placeholder*='captcha']")
                captcha_input.clear()
                captcha_input.send_keys(captcha_solution)
                print(f"   ✅ CAPTCHA entered: {captcha_solution}")
                return captcha_solution
            except Exception as e:
                print(f"   ❌ Failed to enter CAPTCHA: {e}")
                return None
        
        return None

    def automate_form_filling(self, driver):
        """Complete form automation with all selectors"""
        print("\n🤖 STARTING COMPLETE FORM AUTOMATION")
        print("=" * 50)
        
        try:
            # Step 1: Select Database
            print("[1/6] Selecting database...")
            if not self.safe_select(driver, "dbselect", self.DATABASE_VALUE):
                return False
            time.sleep(2)
            
            # Step 2: Select District (Mumbai)
            print("[2/6] Selecting Mumbai district...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"#district_id option[value='{self.MUMBAI_DISTRICT}']"))
            )
            if not self.safe_select(driver, "district_id", self.MUMBAI_DISTRICT):
                return False
            time.sleep(2)
            
            # Step 3: Get and select Taluka options
            print("[3/6] Handling Taluka selection...")
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
            taluka_options = self.get_dropdown_options(driver, "taluka_id", "Taluka")
            
            if taluka_options:
                # Select first available taluka (or you can specify)
                first_taluka = taluka_options[0]['value']
                if self.safe_select(driver, "taluka_id", first_taluka):
                    print(f"   ✅ Selected Taluka: {taluka_options[0]['text']}")
                else:
                    print("   ⚠️ Continuing without Taluka selection")
                time.sleep(2)
            
            # Step 4: Get and select Village options
            print("[4/6] Handling Village selection...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                village_options = self.get_dropdown_options(driver, "village_id", "Village")
                
                if village_options:
                    # Select first available village
                    first_village = village_options[0]['value']
                    if self.safe_select(driver, "village_id", first_village):
                        print(f"   ✅ Selected Village: {village_options[0]['text']}")
                    else:
                        print("   ⚠️ Continuing without Village selection")
                    time.sleep(2)
            except:
                print("   ⚠️ Village selection not available or not required")
            
            # Step 5: Select Agreement Article
            print("[5/6] Selecting Agreement to Sale article...")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))
            if not self.safe_select(driver, "article_id", self.AGREEMENT_ARTICLE):
                return False
            time.sleep(2)
            
            # Step 6: Handle CAPTCHA
            print("[6/6] Handling CAPTCHA...")
            captcha_solution = self.handle_captcha(driver)
            if not captcha_solution:
                print("   ❌ CAPTCHA solving failed")
                return False
            
            # Submit form
            print("📤 Submitting search form...")
            submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], input[value*='Search'], button:contains('Search')")
            driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for results
            print("⏳ Waiting for search results...")
            time.sleep(5)
            
            print("✅ Form automation completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Form automation failed: {e}")
            return False

    def download_documents(self, driver):
        """Download all found documents"""
        print("\n📥 STARTING DOCUMENT DOWNLOAD")
        print("=" * 50)
        
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Look for document links with multiple selectors
            selectors = [
                "table a[href*='indexii']",
                "a[href*='view']",
                "a[href*='document']",
                "a[href*='pdf']",
                "table a[href*='/eDisplay/']"
            ]
            
            links = []
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    links.extend(found_links)
                    print(f"   📋 Found {len(found_links)} links with selector: {selector}")
            
            # Remove duplicates
            unique_links = []
            seen_hrefs = set()
            for link in links:
                href = link.get('href', '')
                if href and href not in seen_hrefs:
                    unique_links.append(link)
                    seen_hrefs.add(href)
            
            if not unique_links:
                print("❌ No document links found")
                # Save results page for debugging
                with open(os.path.join(self.docs_dir, 'search_results.html'), 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("📄 Saved search results page for inspection")
                return 0
            
            print(f"📄 Found {len(unique_links)} unique document links")
            
            # Download each document
            for i, link in enumerate(unique_links):
                print(f"\n📥 Downloading document {i+1}/{len(unique_links)}...")
                
                href = link.get('href', '')
                if not href.startswith('http'):
                    doc_url = f"{self.base_url}{href}"
                else:
                    doc_url = href
                
                # Create new driver instance for each download
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    # Generate filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"Agreement_Doc_{i+1:03d}_{timestamp}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    # Save document
                    with open(filepath, 'w', encoding='utf-8') as f:
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
                    
                    meta_file = os.path.join(self.metadata_dir, f"{filename}_metadata.json")
                    with open(meta_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    self.download_count += 1
                    print(f"   ✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error downloading document {i+1}: {e}")
                finally:
                    doc_driver.quit()
                
                # Small delay between downloads
                time.sleep(1)
            
            return self.download_count
            
        except Exception as e:
            print(f"❌ Document download failed: {e}")
            return 0

    def run(self):
        """Main execution workflow"""
        print("🚀 STARTING ULTIMATE AUTOMATION")
        
        driver = self.setup_driver()
        try:
            # Load the search page
            print(f"\n🌐 Loading IGR website...")
            driver.get(self.search_url)
            time.sleep(3)
            print("✅ Website loaded")
            
            # Automate form filling
            if not self.automate_form_filling(driver):
                print("❌ Form automation failed")
                return
            
            # Download documents
            downloaded = self.download_documents(driver)
            
            # Final summary
            print("\n" + "=" * 60)
            print("🎉 ULTIMATE AUTOMATION COMPLETE!")
            print(f"📊 Documents downloaded: {downloaded}")
            print(f"📁 Documents folder: {os.path.abspath(self.docs_dir)}")
            print(f"🖼️  CAPTCHAs folder: {os.path.abspath(self.captcha_dir)}")
            print(f"📋 Metadata folder: {os.path.abspath(self.metadata_dir)}")
            print("=" * 60)
            
        finally:
            driver.quit()

if __name__ == '__main__':
    # Setup OCR
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
    except:
        print("⚠️  Tesseract OCR not found - CAPTCHA solving may fail")
        print("💡 Install from: https://github.com/tesseract-ocr/tesseract")
    
    # Run the ultimate scraper
    scraper = UltimateAutomatedScraper()
    scraper.run()