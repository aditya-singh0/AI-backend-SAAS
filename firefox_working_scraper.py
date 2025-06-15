#!/usr/bin/env python3
"""
Firefox Working Scraper - Uses confirmed selectors
Based on diagnostic results: District 31=Mumbai, Database 3=Recent years
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

class FirefoxWorkingScraper:
    def __init__(self):
        # Confirmed working selectors from diagnostic
        self.DATABASE_VALUE = '3'  # Recent years database
        self.MUMBAI_DISTRICT = '31'  # Mumbai City
        
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        self.data_dir = 'data'
        self.docs_dir = os.path.join(self.data_dir, 'firefox_working_docs')
        os.makedirs(self.docs_dir, exist_ok=True)
        self.download_count = 0
        
        print("🦊 Firefox Working Scraper")
        print("=" * 60)
        print("Using confirmed selectors from diagnostic results")
        print(f"📁 Documents will be saved in: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def setup_driver(self):
        print("🚀 Setting up Firefox WebDriver...")
        options = webdriver.FirefoxOptions()
        try:
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.set_window_size(1280, 1024)
            print("✅ Firefox WebDriver is active.")
            return driver
        except Exception as e:
            print(f"❌ Firefox WebDriver setup failed: {e}")
            sys.exit(1)

    def safe_select(self, driver, select_id, value, by_value=True):
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

    def find_agreement_article(self, driver):
        """Find Agreement to Sale article ID by searching through options"""
        try:
            print("🔍 Searching for Agreement to Sale article...")
            element = driver.find_element(By.ID, "article_id")
            select = Select(element)
            
            # Search terms for Agreement to Sale
            search_terms = [
                'agreement', 'sale', 'करार', 'विक्री', 'करारनामा', 
                'विक्रीकरार', 'agreement to sale', 'sale agreement'
            ]
            
            for option in select.options:
                value = option.get_attribute('value')
                text = option.text.strip().lower()
                
                for term in search_terms:
                    if term in text:
                        print(f"   ✅ Found: '{value}' | {option.text.strip()}")
                        return value
            
            # If not found, try common sale deed IDs
            common_ids = ['43', '31', '32', '33', '34', '35']
            for test_id in common_ids:
                for option in select.options:
                    if option.get_attribute('value') == test_id:
                        print(f"   🎯 Trying common ID: '{test_id}' | {option.text.strip()}")
                        return test_id
            
            print("   ❌ Could not find Agreement to Sale article")
            return None
            
        except Exception as e:
            print(f"   ❌ Error finding article: {e}")
            return None

    def run(self):
        driver = self.setup_driver()
        try:
            print("\n--- Starting Firefox Automation ---")
            driver.get(self.search_url)
            time.sleep(3)
            print("✅ Page loaded")

            # Step 1: Select Database
            print("\n[Step 1/5] Selecting database...")
            if self.safe_select(driver, "dbselect", self.DATABASE_VALUE):
                print("   ✅ Database selected (Recent years)")
            else:
                print("   ❌ Failed to select database")
                return

            # Wait for district options to load
            print("\n[Step 2/5] Waiting for district options...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"#district_id option[value='{self.MUMBAI_DISTRICT}']"))
            )

            # Step 2: Select Mumbai District
            print("\n[Step 3/5] Selecting Mumbai district...")
            if self.safe_select(driver, "district_id", self.MUMBAI_DISTRICT):
                print("   ✅ Mumbai district selected")
            else:
                print("   ❌ Failed to select district")
                return

            # Wait for article options to load
            print("\n[Step 4/5] Waiting for article options...")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))

            # Step 3: Find and select Agreement to Sale
            print("\n[Step 5/5] Finding Agreement to Sale article...")
            article_id = self.find_agreement_article(driver)
            if article_id:
                if self.safe_select(driver, "article_id", article_id):
                    print("   ✅ Agreement article selected")
                else:
                    print("   ❌ Failed to select article")
                    return
            else:
                print("   ❌ Could not find Agreement to Sale article")
                return

            # Step 4: Try to select year (if available)
            print("\n[Optional] Trying to select year...")
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "year")))
                # Try common year values
                year_values = ['2024', '2023', '2022']
                year_selected = False
                
                for year in year_values:
                    if self.safe_select(driver, "year", year, by_value=False):
                        print(f"   ✅ Year {year} selected")
                        year_selected = True
                        break
                
                if not year_selected:
                    print("   ⚠️ Could not select year, continuing anyway...")
                    
            except Exception as e:
                print(f"   ⚠️ Year selection not available: {e}")

            # Manual CAPTCHA step
            print("\n" + "="*25 + " USER ACTION REQUIRED " + "="*25)
            print("🎯 The form has been filled automatically!")
            print("📋 Database: Recent years")
            print("🏙️ District: Mumbai")
            print("📄 Article: Agreement to Sale (found automatically)")
            print("")
            print("👤 Please do the following in the Firefox browser:")
            print("1. ✅ Verify the form looks correct")
            print("2. 🔍 Solve the CAPTCHA")
            print("3. 🔍 Click the 'Search' button")
            print("4. ⏳ Wait for results to load")
            print("")
            input(">>> Press Enter here AFTER the search results have loaded...")

            # Automated downloading
            print("\n--- Resuming automation for downloading ---")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Look for document links
            links = soup.select("table a[href*='indexii']")
            if not links:
                # Try alternative selectors
                links = soup.select("a[href*='view']") or soup.select("a[href*='document']")
            
            if not links:
                print("❌ No document links found in results")
                # Save page for debugging
                with open(os.path.join(self.docs_dir, 'search_results.html'), 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("📄 Saved search results page for inspection")
                return

            print(f"📄 Found {len(links)} document links")
            
            # Download documents
            for i, link in enumerate(links):
                print(f"📥 Downloading document {i+1}/{len(links)}...")
                doc_url = f"{self.base_url}{link['href']}"
                
                # Open document in new driver instance
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    filename = f"Agreement_Doc_{i+1:03d}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(doc_driver.page_source)
                    
                    self.download_count += 1
                    print(f"   ✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error downloading document {i+1}: {e}")
                finally:
                    doc_driver.quit()

            print(f"\n🎉 Successfully downloaded {self.download_count} documents!")
            print(f"📁 Check folder: {os.path.abspath(self.docs_dir)}")

        finally:
            print("\n--- Process Complete ---")
            driver.quit()

if __name__ == '__main__':
    scraper = FirefoxWorkingScraper()
    scraper.run()