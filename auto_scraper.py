#!/usr/bin/env python3
"""Complete IGR Automation"""
import os, sys, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract, cv2, numpy as np
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AutoScraper:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.search_url = f"{self.base_url}/eDisplay/Propertydetails/index"
        self.data_dir = "data"
        self.docs_dir = os.path.join(self.data_dir, "auto_docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        print(f"🚀 Auto Scraper - Docs: {os.path.abspath(self.docs_dir)}")

    def setup_driver(self):
        options = webdriver.FirefoxOptions()
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)

    def safe_select(self, driver, select_id, value):
        try:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, select_id)))
            Select(element).select_by_value(value)
            print(f"✅ {select_id}: {value}")
            return True
        except: 
            return False

    def solve_captcha(self, driver):
        try:
            img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha']")
            url = img.get_attribute("src")
            if not url.startswith("http"): 
                url = f"{self.base_url}{url}"
            
            resp = requests.get(url, verify=False)
            path = os.path.join(self.data_dir, "temp_captcha.png")
            with open(path, "wb") as f: 
                f.write(resp.content)
            
            cv_img = cv2.imread(path)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            pil_img = Image.fromarray(thresh)
            text = pytesseract.image_to_string(pil_img, config="--psm 8").strip()
            text = "".join(c for c in text if c.isalnum())
            
            if len(text) >= 3:
                inp = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha']")
                inp.clear()
                inp.send_keys(text)
                print(f"🔍 CAPTCHA: {text}")
                return True
        except Exception as e: 
            print(f"❌ CAPTCHA failed: {e}")
        return False

    def run(self):
        driver = self.setup_driver()
        try:
            driver.get(self.search_url)
            time.sleep(3)
            
            # Form automation
            print("🤖 Automating form...")
            self.safe_select(driver, "dbselect", "3")
            time.sleep(2)
            
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']")))
            self.safe_select(driver, "district_id", "31")
            time.sleep(2)
            
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
                Select(driver.find_element(By.ID, "taluka_id")).select_by_index(1)
                print("✅ Taluka selected")
                time.sleep(2)
            except: 
                pass
            
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                Select(driver.find_element(By.ID, "village_id")).select_by_index(1)
                print("✅ Village selected")
                time.sleep(2)
            except: 
                pass
            
            self.safe_select(driver, "article_id", "42")
            time.sleep(2)
            
            if self.solve_captcha(driver):
                driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
                time.sleep(5)
                
                # Download documents
                soup = BeautifulSoup(driver.page_source, "html.parser")
                links = soup.select("table a[href*='indexii']") or soup.select("a[href*='view']")
                
                print(f"📄 Found {len(links)} documents")
                for i, link in enumerate(links):
                    doc_driver = self.setup_driver()
                    try:
                        url = f"{self.base_url}{link['href']}"
                        doc_driver.get(url)
                        time.sleep(3)
                        
                        filename = f"Doc_{i+1:03d}.html"
                        with open(os.path.join(self.docs_dir, filename), "w", encoding="utf-8") as f:
                            f.write(doc_driver.page_source)
                        print(f"✅ {filename}")
                    except Exception as e: 
                        print(f"❌ Doc {i+1}: {e}")
                    finally: 
                        doc_driver.quit()
                
                print(f"🎉 Complete! Check: {self.docs_dir}")
        finally: 
            driver.quit()

if __name__ == "__main__":
    AutoScraper().run() 