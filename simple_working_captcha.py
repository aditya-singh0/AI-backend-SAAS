#!/usr/bin/env python3
"""
Simple Working CAPTCHA Solver with IP Switching
No problematic dependencies - uses manual CAPTCHA solving
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64

class SimpleCAPTCHASolver:
    def __init__(self, proxy_password=None):
        """Initialize simple CAPTCHA solver"""
        self.proxy_password = proxy_password
        self.session_count = 0
        
        print("🚀 SIMPLE WORKING CAPTCHA SOLVER")
        print("=" * 50)
        print("✅ Manual CAPTCHA solving (100% reliable)")
        print("🌐 IP switching with each search")
        print("📋 All Mumbai districts and villages")
        print("🎯 Agreement to Sale documents")
        print("=" * 50)
    
    def get_new_session(self):
        """Get new session ID for IP rotation"""
        self.session_count += 1
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        return f"mumbai-{timestamp}-{random_str}-{self.session_count}"
    
    def create_driver(self):
        """Create Chrome driver with proxy"""
        options = Options()
        
        if self.proxy_password:
            session_id = self.get_new_session()
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.proxy_password}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔄 New IP session: {session_id}")
        
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"❌ Driver creation failed: {e}")
            return None
    
    def manual_captcha_solve(self, driver):
        """Manual CAPTCHA solving - most reliable method"""
        try:
            print("\n🔍 Looking for CAPTCHA...")
            
            # Wait for page to load
            time.sleep(3)
            
            # Take screenshot for user to see
            screenshot_path = f"captcha_screenshot_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Try to open screenshot
            try:
                os.startfile(screenshot_path)
            except:
                print("📋 Please check the screenshot file")
            
            print("\n" + "="*60)
            print("🔤 MANUAL CAPTCHA SOLVING")
            print("="*60)
            print("1. Look at the browser window or screenshot")
            print("2. Find the CAPTCHA image")
            print("3. Enter what you see below")
            print("="*60)
            
            # Get CAPTCHA text from user
            captcha_text = input("Enter CAPTCHA text: ").strip()
            
            if not captcha_text:
                print("❌ No CAPTCHA text entered")
                return False
            
            # Find and fill CAPTCHA input
            captcha_inputs = driver.find_elements(By.XPATH, "//input[@type='text' and (contains(@name, 'captcha') or contains(@id, 'captcha') or contains(@placeholder, 'captcha'))]")
            
            if not captcha_inputs:
                # Try broader search
                captcha_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                if len(captcha_inputs) > 1:
                    captcha_inputs = captcha_inputs[-1:]  # Take the last text input
            
            if captcha_inputs:
                captcha_input = captcha_inputs[0]
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                print(f"✅ CAPTCHA entered: {captcha_text}")
                return True
            else:
                print("❌ Could not find CAPTCHA input field")
                return False
                
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return False
    
    def fill_mumbai_form(self, driver):
        """Fill form with Mumbai data"""
        try:
            print("📋 Filling Mumbai form...")
            
            # Wait for form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "select"))
            )
            
            # Get all select elements
            selects = driver.find_elements(By.TAG_NAME, "select")
            print(f"📋 Found {len(selects)} dropdown fields")
            
            # Fill dropdowns step by step
            for i, select_elem in enumerate(selects):
                try:
                    select = Select(select_elem)
                    options = [opt.text for opt in select.options if opt.value and opt.value != ""]
                    
                    if not options:
                        continue
                    
                    print(f"📋 Dropdown {i+1}: {len(options)} options")
                    
                    # Select based on field type
                    if i == 0:  # District
                        for opt in select.options:
                            if "मुंबई" in opt.text or "Mumbai" in opt.text:
                                select.select_by_value(opt.value)
                                print(f"✅ Selected district: {opt.text}")
                                break
                    elif i == 1:  # Sub-district/Taluka
                        for opt in select.options:
                            if "मुंबई" in opt.text or "Mumbai" in opt.text:
                                select.select_by_value(opt.value)
                                print(f"✅ Selected taluka: {opt.text}")
                                break
                    elif i == 2:  # Village
                        # Select first available village
                        if len(select.options) > 1:
                            select.select_by_index(1)
                            print(f"✅ Selected village: {select.options[1].text}")
                    elif "year" in select_elem.get_attribute("name").lower():
                        # Select 2024
                        for opt in select.options:
                            if "2024" in opt.text:
                                select.select_by_value(opt.value)
                                print(f"✅ Selected year: {opt.text}")
                                break
                    elif "article" in select_elem.get_attribute("name").lower():
                        # Select Agreement to Sale
                        for opt in select.options:
                            if "विकस" in opt.text or "Agreement" in opt.text.lower():
                                select.select_by_value(opt.value)
                                print(f"✅ Selected article: {opt.text}")
                                break
                    
                    time.sleep(1)  # Wait between selections
                    
                except Exception as e:
                    print(f"⚠️ Dropdown {i+1} failed: {e}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False
    
    def submit_form(self, driver):
        """Submit the form"""
        try:
            # Look for submit button
            submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit'] | //button[@type='submit'] | //button[contains(text(), 'Submit')] | //input[@value='Submit']")
            
            if submit_buttons:
                submit_button = submit_buttons[0]
                submit_button.click()
                print("✅ Form submitted")
                return True
            else:
                print("❌ Submit button not found")
                return False
                
        except Exception as e:
            print(f"❌ Form submission failed: {e}")
            return False
    
    def extract_documents(self, driver):
        """Extract document URLs"""
        try:
            # Wait for results
            time.sleep(5)
            
            documents = []
            
            # Look for document links
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails') or contains(@href, 'indexii')]")
            
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if href and ("propertydetails" in href or "indexii" in href):
                    documents.append({
                        "url": href,
                        "text": text
                    })
            
            print(f"📄 Found {len(documents)} document links")
            return documents
            
        except Exception as e:
            print(f"❌ Document extraction failed: {e}")
            return []
    
    def download_document(self, doc_url, index):
        """Download individual document"""
        try:
            driver = self.create_driver()
            if not driver:
                return False
            
            print(f"📥 Downloading document {index}...")
            driver.get(doc_url)
            time.sleep(3)
            
            # Save HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Mumbai_Agreement_{index:03d}_{timestamp}.html"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            print(f"💾 Saved: {filename}")
            
            driver.quit()
            return True
            
        except Exception as e:
            print(f"❌ Document download failed: {e}")
            return False
    
    def run_search(self, max_documents=10):
        """Run search with IP switching and CAPTCHA solving"""
        print(f"\n🚀 STARTING MUMBAI SEARCH")
        print(f"🎯 Target: {max_documents} Agreement to Sale documents")
        print("="*60)
        
        all_documents = []
        
        for attempt in range(5):  # Try up to 5 different searches
            if len(all_documents) >= max_documents:
                break
            
            print(f"\n🔍 Search attempt {attempt + 1}/5")
            
            driver = self.create_driver()
            if not driver:
                continue
            
            try:
                # Load IGR website
                print("🌐 Loading IGR website...")
                driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
                time.sleep(3)
                
                # Fill form
                if not self.fill_mumbai_form(driver):
                    driver.quit()
                    continue
                
                # Solve CAPTCHA
                if not self.manual_captcha_solve(driver):
                    driver.quit()
                    continue
                
                # Submit form
                if not self.submit_form(driver):
                    driver.quit()
                    continue
                
                # Extract documents
                documents = self.extract_documents(driver)
                
                # Add to collection
                for doc in documents:
                    if len(all_documents) < max_documents:
                        all_documents.append(doc)
                
                driver.quit()
                
                print(f"✅ Search {attempt + 1} completed: {len(documents)} documents found")
                time.sleep(3)  # Pause between searches
                
            except Exception as e:
                print(f"❌ Search {attempt + 1} failed: {e}")
                try:
                    driver.quit()
                except:
                    pass
                continue
        
        # Download documents
        print(f"\n📥 DOWNLOADING {len(all_documents)} DOCUMENTS")
        print("="*60)
        
        for i, doc in enumerate(all_documents, 1):
            success = self.download_document(doc["url"], i)
            if success:
                print(f"✅ Document {i}/{len(all_documents)} downloaded")
            else:
                print(f"❌ Document {i}/{len(all_documents)} failed")
            
            time.sleep(2)  # Pause between downloads
        
        print(f"\n🎉 COMPLETED!")
        print(f"📊 Total documents: {len(all_documents)}")
        print(f"📁 Files saved in current directory")
        
        return all_documents

def main():
    """Main function"""
    print("🔧 SIMPLE CAPTCHA SOLVER SETUP")
    print("="*40)
    
    # Get proxy password
    use_proxy = input("🌐 Use proxy for IP switching? (y/n): ").lower().startswith('y')
    
    proxy_password = None
    if use_proxy:
        proxy_password = input("🔐 Enter proxy password: ").strip()
        if not proxy_password:
            print("⚠️ No proxy password - running without proxy")
    
    # Get number of documents
    try:
        max_docs = int(input("📋 How many documents? (default 10): ") or "10")
    except:
        max_docs = 10
    
    # Run solver
    solver = SimpleCAPTCHASolver(proxy_password=proxy_password)
    documents = solver.run_search(max_documents=max_docs)
    
    print(f"\n✅ DONE! Found {len(documents)} documents")

if __name__ == "__main__":
    main() 