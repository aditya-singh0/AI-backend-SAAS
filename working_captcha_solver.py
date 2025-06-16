#!/usr/bin/env python3
"""
Working CAPTCHA Solver with IP Switching
Handles CAPTCHA solving and form automation without problematic dependencies
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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64
from PIL import Image
import io

class WorkingCAPTCHASolver:
    def __init__(self, use_proxy=True, proxy_password=None):
        """Initialize the CAPTCHA solver"""
        self.use_proxy = use_proxy
        self.proxy_password = proxy_password
        self.session_id = None
        self.documents_found = []
        
        # Create directories
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "captcha_working")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.captcha_dir, exist_ok=True)
        
        # Mumbai districts and villages
        self.mumbai_config = {
            "districts": [
                ("1", "मुंबई"),
                ("2", "मुंबई उपनगर"),
            ],
            "villages": [
                ("1", "अंधेरी"),
                ("2", "बांद्रा"),
                ("3", "बोरीवली"),
                ("4", "मलाड"),
                ("5", "गोरेगांव"),
                ("6", "जुहू"),
                ("7", "विले पार्ले"),
                ("8", "सांताक्रूज"),
                ("9", "पवई"),
                ("10", "कांदिवली"),
            ]
        }
        
        print("🚀 WORKING CAPTCHA SOLVER WITH IP SWITCHING")
        print("=" * 60)
        print("✅ No problematic dependencies")
        print("🌐 IP rotation with proxy support")
        print("📥 Manual CAPTCHA solving (reliable)")
        print("📋 Automated form filling")
        print("=" * 60)
    
    def get_new_session_id(self):
        """Generate new session ID for IP rotation"""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.session_id = f"captcha-{timestamp}-{random_str}"
        return self.session_id
    
    def setup_chrome_driver(self):
        """Setup Chrome driver with proxy if needed"""
        chrome_options = Options()
        
        if self.use_proxy and self.proxy_password:
            # Setup proxy with authentication
            session_id = self.get_new_session_id()
            proxy_host = "42q6t9rp.pr.thordata.net"
            proxy_port = "9999"
            proxy_username = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            
            proxy_url = f"http://{proxy_username}:{self.proxy_password}@{proxy_host}:{proxy_port}"
            chrome_options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔄 Using proxy with session: {session_id}")
        
        # Other Chrome options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"❌ Chrome driver failed: {e}")
            return None
    
    def download_captcha_manual(self, driver):
        """Download CAPTCHA image for manual solving"""
        try:
            # Wait for CAPTCHA image to load
            captcha_img = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "captcha_image"))
            )
            
            # Get CAPTCHA image source
            captcha_src = captcha_img.get_attribute("src")
            
            if captcha_src.startswith("data:image"):
                # Handle base64 encoded image
                image_data = captcha_src.split(",")[1]
                image_bytes = base64.b64decode(image_data)
            else:
                # Download image from URL
                response = requests.get(captcha_src)
                image_bytes = response.content
            
            # Save CAPTCHA image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            captcha_path = os.path.join(self.captcha_dir, f"captcha_{timestamp}.png")
            
            with open(captcha_path, "wb") as f:
                f.write(image_bytes)
            
            print(f"📥 CAPTCHA saved: {captcha_path}")
            
            # Open image for user to see
            try:
                os.startfile(captcha_path)  # Windows
            except:
                print(f"📋 Please open and view: {captcha_path}")
            
            # Get manual input
            captcha_text = input("🔤 Enter CAPTCHA text (what you see in the image): ").strip()
            
            return captcha_text
            
        except Exception as e:
            print(f"❌ CAPTCHA download failed: {e}")
            return None
    
    def fill_form_mumbai(self, driver, district_id, village_id):
        """Fill form with Mumbai-specific data"""
        try:
            print(f"📋 Filling form - District: {district_id}, Village: {village_id}")
            
            # Wait for form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "district"))
            )
            
            # Select District
            district_select = Select(driver.find_element(By.ID, "district"))
            district_select.select_by_value(district_id)
            time.sleep(2)
            
            # Select Sub-District (Taluka) - usually same as district for Mumbai
            try:
                subdistrict_select = Select(driver.find_element(By.ID, "subdistrict"))
                subdistrict_select.select_by_value(district_id)
                time.sleep(2)
            except:
                print("⚠️ No sub-district field found")
            
            # Select Village
            village_select = Select(driver.find_element(By.ID, "village"))
            village_select.select_by_value(village_id)
            time.sleep(2)
            
            # Select Year (2024)
            year_select = Select(driver.find_element(By.ID, "year"))
            year_select.select_by_value("2024")
            time.sleep(1)
            
            # Select Registration Year (2024)
            try:
                reg_year_select = Select(driver.find_element(By.ID, "reg_year"))
                reg_year_select.select_by_value("2024")
                time.sleep(1)
            except:
                print("⚠️ No registration year field found")
            
            # Select Article (Agreement to Sale)
            article_select = Select(driver.find_element(By.ID, "article"))
            # Look for Agreement to Sale (usually value "42" or similar)
            for option in article_select.options:
                if "विकस" in option.text or "Agreement" in option.text:
                    article_select.select_by_value(option.get_attribute("value"))
                    break
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False
    
    def solve_captcha_and_submit(self, driver):
        """Solve CAPTCHA and submit form"""
        try:
            # Download and solve CAPTCHA manually
            captcha_text = self.download_captcha_manual(driver)
            
            if not captcha_text:
                return False
            
            # Enter CAPTCHA
            captcha_input = driver.find_element(By.ID, "captcha_input")
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            
            # Submit form
            submit_button = driver.find_element(By.ID, "submit_button")
            submit_button.click()
            
            # Wait for results
            time.sleep(5)
            
            # Check if submission was successful
            if "Invalid CAPTCHA" in driver.page_source or "गलत कॅप्चा" in driver.page_source:
                print("❌ Invalid CAPTCHA - try again")
                return False
            
            print("✅ CAPTCHA solved successfully!")
            return True
            
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return False
    
    def extract_documents(self, driver):
        """Extract document links from results"""
        try:
            documents = []
            
            # Look for document links
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails') or contains(@href, 'indexii')]")
            
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if href and ("propertydetails" in href or "indexii" in href):
                    documents.append({
                        "url": href,
                        "text": text,
                        "timestamp": datetime.now().isoformat()
                    })
            
            print(f"📄 Found {len(documents)} documents")
            return documents
            
        except Exception as e:
            print(f"❌ Document extraction failed: {e}")
            return []
    
    def download_document(self, doc_url, doc_index):
        """Download individual document"""
        try:
            print(f"📥 Downloading document {doc_index}...")
            
            driver = self.setup_chrome_driver()
            if not driver:
                return False
            
            driver.get(doc_url)
            time.sleep(3)
            
            # Save HTML content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"IGR_Document_{doc_index:04d}_{timestamp}.html"
            html_path = os.path.join(self.docs_dir, html_filename)
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            print(f"💾 Document saved: {html_filename}")
            
            driver.quit()
            return True
            
        except Exception as e:
            print(f"❌ Document download failed: {e}")
            return False
    
    def run_mumbai_search(self, max_documents=10):
        """Run Mumbai-specific search with IP switching"""
        print(f"\n🚀 STARTING MUMBAI SEARCH (Max: {max_documents} documents)")
        print("=" * 60)
        
        documents_collected = []
        
        for district_id, district_name in self.mumbai_config["districts"]:
            if len(documents_collected) >= max_documents:
                break
                
            for village_id, village_name in self.mumbai_config["villages"]:
                if len(documents_collected) >= max_documents:
                    break
                
                print(f"\n🔍 Searching: {district_name} - {village_name}")
                
                # Setup new driver with fresh IP
                driver = self.setup_chrome_driver()
                if not driver:
                    continue
                
                try:
                    # Load IGR website
                    driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
                    time.sleep(3)
                    
                    # Fill form
                    if not self.fill_form_mumbai(driver, district_id, village_id):
                        driver.quit()
                        continue
                    
                    # Solve CAPTCHA and submit
                    if not self.solve_captcha_and_submit(driver):
                        driver.quit()
                        continue
                    
                    # Extract documents
                    documents = self.extract_documents(driver)
                    
                    # Add to collection
                    for doc in documents:
                        if len(documents_collected) < max_documents:
                            doc["district"] = district_name
                            doc["village"] = village_name
                            documents_collected.append(doc)
                    
                    driver.quit()
                    
                    print(f"✅ Found {len(documents)} documents")
                    time.sleep(2)  # Pause between searches
                    
                except Exception as e:
                    print(f"❌ Search failed: {e}")
                    driver.quit()
                    continue
        
        # Download collected documents
        print(f"\n📥 DOWNLOADING {len(documents_collected)} DOCUMENTS")
        print("=" * 60)
        
        for i, doc in enumerate(documents_collected, 1):
            success = self.download_document(doc["url"], i)
            if success:
                print(f"✅ Document {i}/{len(documents_collected)} downloaded")
            else:
                print(f"❌ Document {i}/{len(documents_collected)} failed")
            
            time.sleep(1)  # Pause between downloads
        
        print(f"\n🎯 SEARCH COMPLETE!")
        print(f"📊 Total documents found: {len(documents_collected)}")
        print(f"📁 Files saved in: {self.docs_dir}")
        
        return documents_collected

def main():
    """Main function"""
    print("🔧 WORKING CAPTCHA SOLVER - SETUP")
    print("=" * 50)
    
    # Ask for proxy usage
    use_proxy = input("🌐 Use proxy for IP switching? (y/n): ").lower().startswith('y')
    
    proxy_password = None
    if use_proxy:
        proxy_password = input("🔐 Enter proxy password: ").strip()
    
    # Ask for number of documents
    try:
        max_docs = int(input("📋 How many documents to download? (default 10): ") or "10")
    except:
        max_docs = 10
    
    # Initialize solver
    solver = WorkingCAPTCHASolver(use_proxy=use_proxy, proxy_password=proxy_password)
    
    # Run search
    documents = solver.run_mumbai_search(max_documents=max_docs)
    
    print(f"\n✅ All done! Found {len(documents)} documents")

if __name__ == "__main__":
    main() 