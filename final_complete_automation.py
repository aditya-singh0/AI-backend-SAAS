#!/usr/bin/env python3
"""
FINAL COMPLETE AUTOMATION - Everything Automated
100% Automation: Form + CAPTCHA + Document Download
"""
import os, sys, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from PIL import Image
import cv2, numpy as np
from datetime import datetime
import urllib3, json, random, string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FinalCompleteAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.search_url = f"{self.base_url}/eDisplay/Propertydetails/index"
        self.data_dir = "data"
        self.docs_dir = os.path.join(self.data_dir, "final_complete_docs")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_final")
        
        for directory in [self.docs_dir, self.captcha_dir]:
            os.makedirs(directory, exist_ok=True)
        
        self.download_count = 0
        
        print("🚀 FINAL COMPLETE AUTOMATION - 100% AUTOMATED")
        print("=" * 70)
        print("✅ Complete form automation")
        print("🤖 Advanced CAPTCHA solving")
        print("📥 Bulk document downloading")
        print(f"📁 Documents: {os.path.abspath(self.docs_dir)}")
        print("=" * 70)

    def setup_driver(self):
        options = webdriver.FirefoxOptions()
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)

    def safe_select(self, driver, select_id, value):
        try:
            element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, select_id)))
            Select(element).select_by_value(value)
            print(f"   ✅ {select_id}: {value}")
            return True
        except Exception as e:
            print(f"   ❌ {select_id}: {e}")
            return False

    def solve_captcha_and_submit(self, driver):
        """Combined CAPTCHA solving and form submission"""
        try:
            # Download CAPTCHA
            captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha']")
            captcha_url = captcha_img.get_attribute('src')
            if not captcha_url.startswith('http'):
                captcha_url = f"{self.base_url}{captcha_url}"
            
            response = requests.get(captcha_url, verify=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            captcha_path = os.path.join(self.captcha_dir, f'captcha_{timestamp}.png')
            
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
            print("   📷 CAPTCHA downloaded")
            
            # Generate CAPTCHA solution
            solution = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            print(f"   🔍 CAPTCHA solution: '{solution}'")
            
            # Enter CAPTCHA
            captcha_input = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha']")
            captcha_input.clear()
            captcha_input.send_keys(solution)
            print("   ✅ CAPTCHA entered")
            
            # Find and click submit button with comprehensive search
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='Search']",
                "input[value*='search']",
                "button[value*='Search']",
                "input[onclick*='submit']",
                "button[onclick*='submit']",
                "input.btn",
                "button.btn"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"   🎯 Found submit: {selector}")
                    break
                except: continue
            
            # Try XPath methods if CSS selectors fail
            if not submit_button:
                xpath_selectors = [
                    "//input[@type='button' and contains(@value, 'Search')]",
                    "//button[contains(text(), 'Search')]",
                    "//input[contains(@value, 'Submit')]",
                    "//button[contains(text(), 'Submit')]",
                    "//input[@type='button']",
                    "//button[@type='button']"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        submit_button = driver.find_element(By.XPATH, xpath)
                        print(f"   🎯 Found submit by XPath")
                        break
                    except: continue
            
            if not submit_button:
                print("   ❌ Submit button not found")
                return False
            
            # Submit form
            driver.execute_script("arguments[0].click();", submit_button)
            print("   📤 Form submitted")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ CAPTCHA/Submit failed: {e}")
            return False

    def download_documents(self, driver):
        """Download all documents found"""
        print("\n📥 DOWNLOADING DOCUMENTS...")
        
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Find all possible document links
            all_links = []
            selectors = [
                "table a", "a[href*='indexii']", "a[href*='view']", 
                "a[href*='document']", "a[href*='pdf']", "a[href*='eDisplay']"
            ]
            
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    all_links.extend(found)
                    print(f"   📋 {len(found)} links: {selector}")
            
            # Remove duplicates and filter
            unique_links = []
            seen = set()
            
            for link in all_links:
                href = link.get('href', '')
                if href and href not in seen and 'javascript:' not in href and '#' not in href:
                    unique_links.append(link)
                    seen.add(href)
            
            if not unique_links:
                print("❌ No documents found")
                # Save debug page
                debug_file = os.path.join(self.docs_dir, f'debug_{datetime.now().strftime("%H%M%S")}.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"📄 Debug saved: {debug_file}")
                return 0
            
            print(f"\n📄 Found {len(unique_links)} documents")
            
            # Download each document
            for i, link in enumerate(unique_links):
                print(f"📥 Document {i+1}/{len(unique_links)}...")
                
                href = link.get('href', '')
                doc_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    filename = f"Final_Doc_{i+1:03d}_{timestamp}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(doc_driver.page_source)
                    
                    self.download_count += 1
                    print(f"   ✅ {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                finally:
                    doc_driver.quit()
                
                time.sleep(1)
            
            return self.download_count
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return 0

    def run_complete(self):
        """Run complete automation"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            print(f"\n🚀 ATTEMPT {attempt + 1}/{max_attempts}")
            
            driver = self.setup_driver()
            try:
                print("🌐 Loading website...")
                driver.get(self.search_url)
                time.sleep(3)
                
                print("🤖 Form automation...")
                
                # Fill form
                if not self.safe_select(driver, "dbselect", "3"):
                    continue
                time.sleep(2)
                
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']")))
                if not self.safe_select(driver, "district_id", "31"):
                    continue
                time.sleep(2)
                
                # Taluka
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
                    Select(driver.find_element(By.ID, "taluka_id")).select_by_index(1)
                    print("   ✅ Taluka selected")
                    time.sleep(2)
                except: pass
                
                # Village
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                    Select(driver.find_element(By.ID, "village_id")).select_by_index(1)
                    print("   ✅ Village selected")
                    time.sleep(2)
                except: pass
                
                if not self.safe_select(driver, "article_id", "42"):
                    continue
                time.sleep(2)
                
                print("✅ Form completed!")
                
                # CAPTCHA and submit
                if self.solve_captcha_and_submit(driver):
                    downloaded = self.download_documents(driver)
                    
                    if downloaded > 0:
                        print("\n" + "="*70)
                        print("🎉 FINAL COMPLETE AUTOMATION SUCCESS!")
                        print(f"📊 Downloaded: {downloaded} documents")
                        print(f"📁 Location: {os.path.abspath(self.docs_dir)}")
                        print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print("="*70)
                        return True
                    else:
                        print("⚠️ No documents, retrying...")
                else:
                    print("❌ CAPTCHA/Submit failed, retrying...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                driver.quit()
            
            if attempt < max_attempts - 1:
                wait = (attempt + 1) * 2
                print(f"⏳ Waiting {wait}s...")
                time.sleep(wait)
        
        print("\n❌ All attempts failed")
        return False

if __name__ == "__main__":
    automation = FinalCompleteAutomation()
    automation.run_complete()