#!/usr/bin/env python3
"""
Visible, Final, Fully Automated IGR Scraper
This version runs in a VISIBLE browser window for final debugging.
"""

import os
import time
import sys
import pytesseract
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from PIL import Image
import cv2
import numpy as np
import io

# --- Configuration ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
DOCUMENTS_TO_DOWNLOAD = 10

class VisibleIGRScraper:
    def __init__(self):
        self.max_documents = DOCUMENTS_TO_DOWNLOAD
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'visible_automated_documents')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        self.print_header()

    def print_header(self):
        print("🤖 Visible, Final, Fully Automated IGR Scraper")
        print("=" * 60)
        print("👁️ BROWSER WINDOW WILL BE VISIBLE FOR DEBUGGING 👁️")
        print(f"📁 Saving {self.max_documents} documents to: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def setup_driver(self):
        """Configures and returns a VISIBLE Chrome WebDriver."""
        print("🚀 Setting up VISIBLE Chrome WebDriver...")
        options = Options()
        # The next line is commented out to make the browser visible
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ WebDriver setup complete.")
            return driver
        except Exception as e:
            print(f"❌ CRITICAL: WebDriver setup failed: {e}")
            sys.exit(1)

    def solve_captcha(self, driver):
        """Solves the CAPTCHA from the visible browser page."""
        try:
            captcha_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@id, 'captcha')]"))
            )
            img_bytes = captcha_element.screenshot_as_png
            image = Image.open(io.BytesIO(img_bytes)).convert('L')
            np_image = np.array(image)
            _, thresh = cv2.threshold(np_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            config = '--psm 8 -c tessedit_char_whitelist=0123456789'
            captcha_text = pytesseract.image_to_string(Image.fromarray(thresh), config=config).strip()
            if captcha_text and len(captcha_text) >= 4:
                print(f"🤖 CAPTCHA solved: '{captcha_text}'")
                return captcha_text
        except Exception as e:
            print(f"⚠️ CAPTCHA solving failed: {e}")
        return None

    def run(self):
        driver = self.setup_driver()
        try:
            print("\n--- Starting Visible Scraping Process ---")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            print("\n[Step 1/4] Filling search form...")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "dbselect")))
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            Select(driver.find_element(By.ID, "district_id")).select_by_value("1")
            Select(driver.find_element(By.ID, "article_id")).select_by_value("43")
            Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "year")))).select_by_visible_text("2024")
            print("✅ Form filled successfully.")

            print("\n[Step 2/4] Solving CAPTCHA...")
            for attempt in range(5):
                solution = self.solve_captcha(driver)
                if solution:
                    driver.find_element(By.ID, "txtcaptcha").send_keys(solution)
                    driver.find_element(By.ID, "search").click()
                    time.sleep(3)
                    if "No Record Found" not in driver.page_source:
                        print("✅ Submission successful.")
                        break
                    print(f"⚠️ Attempt {attempt+1}: Submission failed. Retrying...")
                else:
                    print(f"⚠️ Attempt {attempt+1}: Could not solve CAPTcha. Refreshing...")
                driver.find_element(By.ID, "newcaptcha").click()
                time.sleep(2)
            else:
                print("❌ Failed to submit after multiple attempts.")
                return

            print("\n[Step 3/4] Extracting links...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            doc_urls = [f"https://pay2igr.igrmaharashtra.gov.in{link['href']}" for link in links][:self.max_documents]
            print(f"📄 Found {len(doc_urls)} documents.")

            print("\n[Step 4/4] Downloading documents...")
            for i, url in enumerate(doc_urls):
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(url)
                    with open(os.path.join(self.docs_dir, f"VisibleDoc_{i+1}.html"), 'w', encoding='utf-8') as f:
                        f.write(doc_driver.page_source)
                    self.download_count += 1
                finally:
                    doc_driver.quit()
            print(f"✅ Downloaded {self.download_count} documents.")

        finally:
            print("\n--- Process Finished ---")
            input("Press Enter to close the main browser window...")
            driver.quit()

if __name__ == '__main__':
    scraper = VisibleIGRScraper()
    scraper.run()
    print(f"\n🎉 Automation complete. Total documents downloaded: {scraper.download_count}")
