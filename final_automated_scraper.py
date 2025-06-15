#!/usr/bin/env python3
"""
Final, Fully Automated IGR Scraper (Corrected)
This version includes all fixes and is designed for robust, one-click automation.
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

# --- Configuration ---
# Set the Tesseract command path explicitly to avoid PATH issues on Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Set the number of documents to download
DOCUMENTS_TO_DOWNLOAD = 10

class FinalIGRScraper:
    def __init__(self):
        self.max_documents = DOCUMENTS_TO_DOWNLOAD
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'final_automated_documents')
        self.captcha_dir = os.path.join(self.data_dir, 'final_automated_captchas')
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.captcha_dir, exist_ok=True)
        self.download_count = 0

        self.print_header()
        self.verify_tesseract()

    def print_header(self):
        print("🤖 Final, Fully Automated IGR Scraper (Corrected)")
        print("=" * 60)
        print("This will automate:")
        print("✅ Form Filling (Mumbai, 2024, Agreement to Sale)")
        print("✅ Advanced CAPTCHA Solving")
        print("✅ Robust Element Selection with Explicit Waits")
        print("✅ Document Downloading")
        print(f"📁 Saving {self.max_documents} documents to: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def verify_tesseract(self):
        """Verify that Tesseract OCR is correctly configured."""
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR is correctly configured.")
        except Exception:
            print("❌ CRITICAL: Tesseract OCR not found at the specified path.")
            print(f"   Please ensure it's installed at: '{pytesseract.pytesseract.tesseract_cmd}'")
            sys.exit(1)

    def setup_driver(self):
        """Configures and returns a visible Chrome WebDriver for debugging."""
        print("🚀 Setting up VISIBLE Chrome WebDriver for debugging...")
        options = Options()
        # options.add_argument("--headless") # Comment out for visibility
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")  # Suppress console noise
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ WebDriver setup complete.")
            return driver
        except Exception as e:
            print("❌ CRITICAL: WebDriver setup failed. Check network or firewall.")
            print(f"   Error: {e}")
            sys.exit(1)

    def solve_captcha(self, driver):
        """Fetches, processes, and solves the CAPTCHA image."""
        try:
            # Use a more flexible XPath to find the CAPTCHA image
            captcha_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@id, 'captcha')]"))
            )
            img_bytes = captcha_element.screenshot_as_png
            
            # Image processing for better OCR
            image = Image.open(io.BytesIO(img_bytes)).convert('L')
            np_image = np.array(image)
            _, thresh = cv2.threshold(np_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            config = '--psm 8 -c tessedit_char_whitelist=0123456789'
            captcha_text = pytesseract.image_to_string(Image.fromarray(thresh), config=config).strip()
            
            if captcha_text and len(captcha_text) >= 4:
                print(f"🤖 CAPTCHA solved: '{captcha_text}'")
                return captcha_text
        except Exception as e:
            print(f"⚠️  CAPTCHA solving failed: {e}")
        return None

    def run(self):
        """Main execution logic for the scraper."""
        driver = self.setup_driver()
        try:
            print("\n--- Starting Scraping Process ---")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            # --- 1. Fill Form ---
            print("\n[Step 1/4] Filling search form...")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "dbselect")))
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            Select(driver.find_element(By.ID, "district_id")).select_by_value("1")
            Select(driver.find_element(By.ID, "article_id")).select_by_value("43")
            
            # Robustly select the year
            year_select_el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "year")))
            Select(year_select_el).select_by_visible_text("2024")
            print("✅ Form filled successfully.")

            # --- 2. Solve CAPTCHA and Submit ---
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
                    else:
                        print(f"⚠️ Attempt {attempt+1}: Submission failed (No Record Found). Retrying...")
                else:
                     print(f"⚠️ Attempt {attempt+1}: Could not solve CAPTCHA. Refreshing...")
                
                driver.find_element(By.ID, "newcaptcha").click()
                time.sleep(2)
            else:
                print("❌ Failed to submit after multiple attempts. Exiting.")
                return

            # --- 3. Extract Links ---
            print("\n[Step 3/4] Extracting document links...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            if not links:
                print("❌ No document links found on the results page.")
                return
            
            doc_urls = [f"https://pay2igr.igrmaharashtra.gov.in{link['href']}" for link in links]
            print(f"📄 Found {len(doc_urls)} documents.")

            # --- 4. Download Documents ---
            print(f"\n[Step 4/4] Downloading up to {self.max_documents} documents...")
            for i, url in enumerate(doc_urls[:self.max_documents]):
                print(f"   -> Downloading document {i+1}...")
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(url)
                    html_content = doc_driver.page_source
                    
                    filename = f"Document_{i+1:03d}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
                    with open(os.path.join(self.docs_dir, filename), 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.download_count += 1
                finally:
                    doc_driver.quit()
            
            print(f"✅ Downloaded {self.download_count} documents.")

        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n--- Process Finished ---")
            driver.quit()

if __name__ == '__main__':
    scraper = FinalIGRScraper()
    scraper.run()
    print(f"\n🎉 Automation complete. Total documents downloaded: {scraper.download_count}")