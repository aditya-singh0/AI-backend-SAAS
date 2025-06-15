#!/usr/bin/env python3
"""
Complete IGR Automation - Everything automated
Form filling + CAPTCHA solving + Document downloading
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

class CompleteAutomation:
    def __init__(self):
        # Confirmed selectors
        self.DATABASE_VALUE = '3'
        self.MUMBAI_DISTRICT = '31'
        self.AGREEMENT_ARTICLE = '42'
        
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        
        # Data folders
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'automated_docs')
        self.captcha_dir = os.path.join(self.data_dir, 'captchas')
        
        for directory in [self.docs_dir, self.captcha_dir]:
            os.makedirs(directory, exist_ok=True)
        
        self.download_count = 0
        print("🚀 COMPLETE IGR AUTOMATION")
        print("=" * 50)
        print(f"📁 Documents: {os.path.abspath(self.docs_dir)}")
        print(f"🖼️  CAPTCHAs: {os.path.abspath(self.captcha_dir)}")
        print("=" * 50)

    def setup_driver(self):
        options = webdriver.FirefoxOptions()
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_window_size(1280, 1024)
        return driver

    def safe_select(self, driver, select_id, value):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, select_id))
            )
            select = Select(element)
            select.select_by_value(value)
            print(f"   ✅ Selected {select_id}: {value}")
            return True
        except Exception as e:
            print(f"   ❌ Failed {select_id}: {e}")
            return False

    def download_captcha(self, driver):
        try:
            captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha']")
            captcha_url = captcha_img.get_attribute('src')
            
            if not captcha_url.startswith('http'):
                captcha_url = f"{self.base_url}{captcha_url}"
            
            response = requests.get(captcha_url)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.captcha_dir, f'captcha_{timestamp}.png')
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"   📷 CAPTCHA saved")
            return filepath
        except Exception as e:
            print(f"   ❌ CAPTCHA download failed: {e}")
            return None

    def solve_captcha(self, image_path):
        try:
            # Preprocess image
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # OCR
            image = Image.fromarray(thresh)
            configs = [
                '--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 7',
                '--psm 6'
            ]
            
            for config in configs:
                try:
                    text = pytesseract.image_to_string(image, config=config).strip()
                    text = ''.join(c for c in text if c.isalnum())
                    if text and len(text) >= 3:
                        print(f"   🔍 CAPTCHA solved: '{text}'")
                        return text
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"   ❌ CAPTCHA solving failed: {e}")
            return None

    def automate_form(self, driver):
        print("\n🤖 AUTOMATING FORM...")
        
        try:
            # Database
            print("[1/6] Database...")
            if not self.safe_select(driver, "dbselect", self.DATABASE_VALUE):
                return False
            time.sleep(2)
            
            # District
            print("[2/6] District...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"#district_id option[value='{self.MUMBAI_DISTRICT}']"))
            )
            if not self.safe_select(driver, "district_id", self.MUMBAI_DISTRICT):
                return False
            time.sleep(2)
            
            # Taluka
            print("[3/6] Taluka...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
                taluka_element = driver.find_element(By.ID, "taluka_id")
                taluka_select = Select(taluka_element)
                if len(taluka_select.options) > 1:
                    taluka_select.select_by_index(1)  # Select first non-empty option
                    print("   ✅ Taluka selected")
                time.sleep(2)
            except:
                print("   ⚠️ Taluka not available")
            
            # Village
            print("[4/6] Village...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                village_element = driver.find_element(By.ID, "village_id")
                village_select = Select(village_element)
                if len(village_select.options) > 1:
                    village_select.select_by_index(1)  # Select first non-empty option
                    print("   ✅ Village selected")
                time.sleep(2)
            except:
                print("   ⚠️ Village not available")
            
            # Article
            print("[5/6] Article...")
            if not self.safe_select(driver, "article_id", self.AGREEMENT_ARTICLE):
                return False
            time.sleep(2)
            
            # CAPTCHA
            print("[6/6] CAPTCHA...")
            captcha_path = self.download_captcha(driver)
            if captcha_path:
                captcha_solution = self.solve_captcha(captcha_path)
                if captcha_solution:
                    try:
                        captcha_input = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha'], input[id*='captcha']")
                        captcha_input.clear()
                        captcha_input.send_keys(captcha_solution)
                        print("   ✅ CAPTCHA entered")
                    except Exception as e:
                        print(f"   ❌ CAPTCHA input failed: {e}")
                        return False
                else:
                    print("   ❌ CAPTCHA solving failed")
                    return False
            
            # Submit
            print("📤 Submitting form...")
            submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            submit_btn.click()
            time.sleep(5)
            
            print("✅ Form automation completed!")
            return True
            
        except Exception as e:
            print(f"❌ Form automation failed: {e}")
            return False

    def download_documents(self, driver):
        print("\n📥 DOWNLOADING DOCUMENTS...")
        
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find document links
            links = soup.select("table a[href*='indexii']")
            if not links:
                links = soup.select("a[href*='view']")
            if not links:
                links = soup.select("a[href*='document']")
            
            if not links:
                print("❌ No document links found")
                # Save page for debugging
                with open(os.path.join(self.docs_dir, 'results.html'), 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("📄 Results page saved for inspection")
                return 0
            
            print(f"📄 Found {len(links)} documents")
            
            # Download each document
            for i, link in enumerate(links):
                print(f"📥 Document {i+1}/{len(links)}...")
                
                href = link.get('href', '')
                doc_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    filename = f"Doc_{i+1:03d}_{datetime.now().strftime('%H%M%S')}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(doc_driver.page_source)
                    
                    self.download_count += 1
                    print(f"   ✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                finally:
                    doc_driver.quit()
                
                time.sleep(1)
            
            return self.download_count
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return 0

    def run(self):
        print("🚀 STARTING COMPLETE AUTOMATION")
        
        driver = self.setup_driver()
        try:
            print("\n🌐 Loading website...")
            driver.get(self.search_url)
            time.sleep(3)
            
            if self.automate_form(driver):
                downloaded = self.download_documents(driver)
                
                print("\n" + "=" * 50)
                print("🎉 AUTOMATION COMPLETE!")
                print(f"📊 Downloaded: {downloaded} documents")
                print(f"📁 Location: {os.path.abspath(self.docs_dir)}")
                print("=" * 50)
            else:
                print("❌ Automation failed")
                
        finally:
            driver.quit()

if __name__ == '__main__':
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR available")
    except:
        print("⚠️ Tesseract OCR not found - install for CAPTCHA solving")
    
    automation = CompleteAutomation()
    automation.run()