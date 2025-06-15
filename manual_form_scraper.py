#!/usr/bin/env python3
"""
Manual Form Scraper
You fill out the form and solve the CAPTCHA, then this script automates all the downloads.
"""

import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class ManualFormScraper:
    def __init__(self):
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'manual_form_documents')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        self.print_header()

    def print_header(self):
        print("👤 Manual Form IGR Scraper")
        print("=" * 60)
        print("This script will open the IGR page for you.")
        print("1. YOU fill out the form (District, Year, etc.).")
        print("2. YOU solve the CAPTCHA and click 'Search'.")
        print("3. The script will then AUTOMATICALLY download all results.")
        print("=" * 60)

    def setup_driver(self):
        """Configures a visible Chrome WebDriver."""
        print("🚀 Setting up browser...")
        options = Options()
        options.add_argument("--start-maximized")
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"❌ WebDriver setup failed: {e}")
            sys.exit(1)

    def run(self):
        driver = self.setup_driver()
        print("✅ Browser ready.")
        try:
            # 1. Navigate to the page
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            # 2. Pause for manual form filling, CAPTCHA, and submission
            print("\n[YOUR TURN]")
            print("Please perform the following actions in the browser window:")
            print("  1. Fill out the search form completely.")
            print("  2. Solve the CAPTCHA.")
            print("  3. Click the 'Search' button.")
            input("\n>>> Press Enter here in the terminal AFTER you see the search results on the website. <<<")
            
            # 3. Resume automation to download everything
            print("\n[AUTOMATION RESUMING]")
            print("Extracting and downloading all found documents...")
            time.sleep(3) # Wait for page to be settled
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            
            if not links:
                print("\n❌ No document links found! Please ensure you clicked 'Search' and the results loaded on the page.")
                return

            doc_urls = [f"https://pay2igr.igrmaharashtra.gov.in{link['href']}" for link in links]
            print(f"📄 Found {len(doc_urls)} documents to download.")

            for i, url in enumerate(doc_urls):
                print(f"   -> Downloading document {i+1}/{len(doc_urls)}...")
                # Use a new driver for each download to avoid session issues
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(url)
                    time.sleep(2)
                    filename = f"Manual_Search_Doc_{i+1:03d}.html"
                    with open(os.path.join(self.docs_dir, filename), 'w', encoding='utf-8') as f:
                        f.write(doc_driver.page_source)
                    self.download_count += 1
                finally:
                    doc_driver.quit()
            
            print(f"\n✅ Successfully downloaded {self.download_count} documents.")

        finally:
            print("\n--- Process Finished ---")
            input("Press Enter to close the browser.")
            driver.quit()

if __name__ == '__main__':
    scraper = ManualFormScraper()
    scraper.run()
    print(f"\n🎉 Task complete! Files are saved in: {os.path.abspath(scraper.docs_dir)}") 