#!/usr/bin/env python3
"""
Firefox Improved Interactive IGR Scraper
This script handles click interception issues and uses more robust interaction methods.
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

class FirefoxImprovedScraper:
    def __init__(self):
        # --- Configuration ---
        self.YEAR = '2024'
        self.DISTRICT_ID = '1' # Mumbai City
        self.ARTICLE_ID = '43' # Agreement to Sale

        # --- Setup ---
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'firefox_improved_docs')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        self.print_header()

    def print_header(self):
        print("🦊 Firefox Improved Interactive IGR Scraper")
        print("=" * 60)
        print("This script handles click interception and uses robust methods.")
        print(f"📁 Documents will be saved in: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def setup_driver(self):
        """Configures and returns a visible Firefox WebDriver."""
        print("🚀 Setting up Firefox WebDriver...")
        options = webdriver.FirefoxOptions()
        # Add some stability options
        options.add_argument("--width=1280")
        options.add_argument("--height=1024")
        try:
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_window_size(1280, 1024)
            print("✅ Firefox WebDriver is active.")
            return driver
        except Exception as e:
            print(f"❌ CRITICAL: Firefox WebDriver setup failed: {e}")
            sys.exit(1)

    def safe_click(self, driver, element):
        """Safely click an element with multiple fallback methods."""
        try:
            # Method 1: Scroll to element and click
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            return True
        except:
            try:
                # Method 2: Use ActionChains
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
                return True
            except:
                try:
                    # Method 3: JavaScript click
                    driver.execute_script("arguments[0].click();", element)
                    return True
                except:
                    return False

    def safe_select(self, driver, select_id, value, by_value=True):
        """Safely select an option with multiple methods."""
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, select_id))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            select = Select(element)
            if by_value:
                select.select_by_value(value)
            else:
                select.select_by_visible_text(value)
            return True
        except Exception as e:
            print(f"   ⚠️ Error selecting {select_id}: {e}")
            return False

    def run(self):
        """Main execution logic."""
        driver = self.setup_driver()
        try:
            print("\n--- Starting Automation on Firefox ---")
            driver.get(self.search_url)
            
            # Wait for page to fully load
            time.sleep(3)
            print("✅ Page loaded, waiting for elements...")

            # 1. Automated Form Filling with improved methods
            print("\n[Step 1/3] Automating form fill with robust methods...")
            try:
                # Select database
                print("   -> Selecting database...")
                if self.safe_select(driver, "dbselect", "3"):
                    print("   ✅ Database selected")
                else:
                    print("   ❌ Failed to select database")
                    return

                # Wait for district options to load
                print("   -> Waiting for district options...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"#district_id option[value='{self.DISTRICT_ID}']"))
                )
                
                # Select district
                print("   -> Selecting district...")
                if self.safe_select(driver, "district_id", self.DISTRICT_ID):
                    print("   ✅ District selected")
                else:
                    print("   ❌ Failed to select district")
                    return
                
                # Wait for article options to load
                print("   -> Waiting for article options...")
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))
                
                # Select article
                print("   -> Selecting article...")
                if self.safe_select(driver, "article_id", self.ARTICLE_ID):
                    print("   ✅ Article selected")
                else:
                    print("   ❌ Failed to select article")
                    return

                # Select year
                print("   -> Selecting year...")
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "year")))
                if self.safe_select(driver, "year", self.YEAR, by_value=False):
                    print("   ✅ Year selected")
                else:
                    print("   ❌ Failed to select year")
                    return
                
                print("✅ Form filled automatically.")
                
            except Exception as e:
                print(f"❌ An error occurred during form filling: {e}")
                return

            # 2. Manual User Step
            print("\n" + "="*25 + " USER ACTION REQUIRED " + "="*25)
            print("The Firefox browser is ready for you.")
            print("1. Solve the CAPTCHA in the browser.")
            print("2. Click the 'Search' button.")
            input(">>> Press Enter here AFTER the search results have loaded...")
            
            # 3. Automated Downloading
            print("\n[Step 3/3] Resuming automation to download documents...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            
            if not links:
                print("❌ No document links found.")
                # Save page for debugging
                with open(os.path.join(self.docs_dir, 'results_page.html'), 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("📄 Saved results page for inspection.")
                return

            doc_urls = [f"{self.base_url}{link['href']}" for link in links]
            print(f"📄 Found {len(doc_urls)} documents.")
            
            for i, url in enumerate(doc_urls):
                print(f"   -> Downloading document {i+1}/{len(doc_urls)}...")
                dl_driver = self.setup_driver()
                try:
                    dl_driver.get(url)
                    time.sleep(3) 
                    filename = f"Firefox_Improved_Doc_{i+1:03d}.html"
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
    scraper = FirefoxImprovedScraper()
    scraper.run()
    print(f"\n🎉 Process complete! Check the '{scraper.docs_dir}' directory.")