#!/usr/bin/env python3
"""
Interactive Final Scraper
Automates form filling, lets you solve the CAPTCHA, then automates all downloads.
"""

import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class InteractiveFinalScraper:
    def __init__(self):
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'interactive_final_documents')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        self.print_header()

    def print_header(self):
        print("🤖 Interactive Final Scraper")
        print("=" * 60)
        print("This script will:")
        print("1. ✅ AUTOMATICALLY fill the search form.")
        print("2. 👤 PAUSE for YOU to solve the CAPTCHA and click 'Search'.")
        print("3. ✅ AUTOMATICALLY download all the search results.")
        print("=" * 60)

    def setup_driver(self):
        """Configures a visible Chrome WebDriver."""
        print("🚀 Setting up browser...")
        options = Options()
        options.add_argument("--start-maximized")
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Browser ready.")
            return driver
        except Exception as e:
            print(f"❌ WebDriver setup failed: {e}")
            sys.exit(1)

    def run(self):
        driver = self.setup_driver()
        try:
            print("\n--- Starting Interactive Process ---")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            # 1. Automated Form Filling
            print("\n[Step 1/3] Automatically filling the form...")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "dbselect")))
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            Select(driver.find_element(By.ID, "district_id")).select_by_value("1") # Mumbai City
            Select(driver.find_element(By.ID, "article_id")).select_by_value("43") # Agreement to Sale
            Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "year")))).select_by_visible_text("2024")
            print("✅ Form filled.")

            # 2. Pause for Manual CAPTCHA and Submission
            print("\n[Step 2/3] YOUR TURN: Please solve the CAPTCHA and click 'Search'.")
            input("   Press Enter here AFTER you have clicked 'Search' on the website...")
            
            # Wait for results to load after user submission
            print("\n   Waiting for search results to load...")
            time.sleep(5)

            # 3. Automated Download of All Results
            print("\n[Step 3/3] Automation resumes. Extracting and downloading all results...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            if not links:
                print("❌ No search result links found. Please ensure you clicked 'Search' and results appeared.")
                return

            doc_urls = [f"https://pay2igr.igrmaharashtra.gov.in{link['href']}" for link in links]
            print(f"📄 Found {len(doc_urls)} documents in the search results.")

            for i, url in enumerate(doc_urls):
                print(f"   -> Downloading document {i+1}/{len(doc_urls)}...")
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(url)
                    time.sleep(2)
                    filename = f"Final_Doc_{i+1:03d}.html"
                    with open(os.path.join(self.docs_dir, filename), 'w', encoding='utf-8') as f:
                        f.write(doc_driver.page_source)
                    self.download_count += 1
                finally:
                    doc_driver.quit()
            
            print(f"\n✅ Successfully downloaded {self.download_count} documents.")

        finally:
            print("\n--- Process Finished ---")
            # Keep the main browser window open until user is done
            input("Press Enter to close the browser and end the program...")
            driver.quit()

if __name__ == '__main__':
    scraper = InteractiveFinalScraper()
    scraper.run()
    print(f"\n🎉 Automation complete! All found documents have been downloaded.")
    print(f"📁 Files are saved in: {os.path.abspath(scraper.docs_dir)}")