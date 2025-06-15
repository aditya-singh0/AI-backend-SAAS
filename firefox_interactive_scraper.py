#!/usr/bin/env python3
"""
Firefox Interactive IGR Scraper
This script uses Firefox to bypass Chrome/Edge driver errors.
It automates form filling, lets the user solve the CAPTCHA,
and then automates the downloading of all results.
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

class FirefoxInteractiveScraper:
    def __init__(self):
        # --- Configuration ---
        self.YEAR = '2024'
        self.DISTRICT_ID = '1' # Mumbai City
        self.ARTICLE_ID = '43' # Agreement to Sale

        # --- Setup ---
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'firefox_interactive_docs')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        self.print_header()

    def print_header(self):
        print("🦊 Firefox Interactive IGR Scraper")
        print("=" * 60)
        print("This script uses Firefox (Gecko engine) to bypass driver issues.")
        print(f"📁 Documents will be saved in: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def setup_driver(self):
        """Configures and returns a visible Firefox WebDriver."""
        print("🚀 Setting up Firefox WebDriver...")
        options = webdriver.FirefoxOptions()
        # Firefox doesn't need as many stability flags
        try:
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_window_size(1280, 1024)
            print("✅ Firefox WebDriver is active.")
            return driver
        except Exception as e:
            print(f"❌ CRITICAL: Firefox WebDriver setup failed: {e}")
            print("   You may need to install Firefox browser first.")
            sys.exit(1)

    def run(self):
        """Main execution logic."""
        driver = self.setup_driver()
        try:
            print("\n--- Starting Automation on Firefox ---")
            driver.get(self.search_url)

            # 1. Automated Form Filling
            print("\n[Step 1/3] Automating form fill...")
            try:
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "dbselect")))
                Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")

                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#district_id option[value='{self.DISTRICT_ID}']")))
                Select(driver.find_element(By.ID, "district_id")).select_by_value(self.DISTRICT_ID)
                
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))
                Select(driver.find_element(By.ID, "article_id")).select_by_value(self.ARTICLE_ID)

                Select(WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "year")))).select_by_visible_text(self.YEAR)
                print("✅ Form filled automatically.")
            except Exception as e:
                print(f"❌ An error occurred during form filling: {e}")
                return

            # 2. Manual User Step
            print("\n" + "="*25 + " USER ACTION REQUIRED " + "="*25)
            print("The Firefox browser is ready for you.")
            print("1. Solve the CAPTCHA.")
            print("2. Click the 'Search' button.")
            input(">>> Press Enter here AFTER the search results have loaded...")
            
            # 3. Automated Downloading
            print("\n[Step 3/3] Resuming automation to download documents...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            
            if not links:
                print("❌ No document links found.")
                return

            doc_urls = [f"{self.base_url}{link['href']}" for link in links]
            print(f"📄 Found {len(doc_urls)} documents.")
            
            for i, url in enumerate(doc_urls):
                print(f"   -> Downloading document {i+1}/{len(doc_urls)}...")
                dl_driver = self.setup_driver()
                try:
                    dl_driver.get(url)
                    time.sleep(3) 
                    filename = f"Firefox_Doc_{i+1:03d}.html"
                    with open(os.path.join(self.docs_dir, filename), 'w', encoding='utf-8') as f:
                        f.write(dl_driver.page_source)
                    self.download_count += 1
                except Exception as e:
                    print(f"      - Error downloading document: {e}")
                finally:
                    dl_driver.quit()

            print(f"\n✅ Downloaded {self.download_count} documents.")

        finally:
            print("\n--- Process Finished ---")
            driver.quit()

if __name__ == '__main__':
    scraper = FirefoxInteractiveScraper()
    scraper.run()
    print(f"\n🎉 Process complete! Check the '{scraper.docs_dir}' directory.")