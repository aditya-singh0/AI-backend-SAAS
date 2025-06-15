#!/usr/bin/env python3
"""
Firefox Diagnostic IGR Scraper
This script inspects the form elements to understand the year dropdown issue.
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

class FirefoxDiagnosticScraper:
    def __init__(self):
        self.YEAR = '2024'
        self.DISTRICT_ID = '1'
        self.ARTICLE_ID = '43'
        self.base_url = 'https://pay2igr.igrmaharashtra.gov.in'
        self.search_url = f'{self.base_url}/eDisplay/Propertydetails/index'
        
        print("🔍 Firefox Diagnostic IGR Scraper")
        print("=" * 60)
        print("This script will inspect form elements to diagnose issues.")
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

    def inspect_dropdown(self, driver, select_id, name):
        """Inspect a dropdown and show all available options."""
        try:
            print(f"\n🔍 Inspecting {name} dropdown (#{select_id})...")
            element = driver.find_element(By.ID, select_id)
            select = Select(element)
            options = select.options
            
            print(f"   Found {len(options)} options:")
            for i, option in enumerate(options):
                value = option.get_attribute('value')
                text = option.text.strip()
                print(f"   {i+1}. Value: '{value}' | Text: '{text}'")
            
            return True
        except Exception as e:
            print(f"   ❌ Could not inspect {name}: {e}")
            return False

    def run(self):
        driver = self.setup_driver()
        try:
            print("\n--- Starting Diagnostic ---")
            driver.get(self.search_url)
            time.sleep(3)
            print("✅ Page loaded.")

            # Inspect initial state
            print("\n=== INITIAL STATE ===")
            self.inspect_dropdown(driver, "dbselect", "Database")
            self.inspect_dropdown(driver, "district_id", "District")
            self.inspect_dropdown(driver, "article_id", "Article")
            self.inspect_dropdown(driver, "year", "Year")

            # Select database and see what changes
            print("\n=== AFTER SELECTING DATABASE ===")
            if self.safe_select(driver, "dbselect", "3"):
                print("✅ Database selected")
                time.sleep(2)  # Wait for any dynamic updates
                self.inspect_dropdown(driver, "district_id", "District")
                self.inspect_dropdown(driver, "article_id", "Article")
                self.inspect_dropdown(driver, "year", "Year")
            
            # Select district and see what changes
            print("\n=== AFTER SELECTING DISTRICT ===")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"#district_id option[value='{self.DISTRICT_ID}']"))
            )
            if self.safe_select(driver, "district_id", self.DISTRICT_ID):
                print("✅ District selected")
                time.sleep(2)  # Wait for any dynamic updates
                self.inspect_dropdown(driver, "article_id", "Article")
                self.inspect_dropdown(driver, "year", "Year")
            
            # Select article and see what changes
            print("\n=== AFTER SELECTING ARTICLE ===")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))
            if self.safe_select(driver, "article_id", self.ARTICLE_ID):
                print("✅ Article selected")
                time.sleep(2)  # Wait for any dynamic updates
                self.inspect_dropdown(driver, "year", "Year")
                
                # Try to find the correct year option
                print(f"\n🎯 Looking for year '{self.YEAR}'...")
                try:
                    element = driver.find_element(By.ID, "year")
                    select = Select(element)
                    
                    # Try different methods to find 2024
                    found_2024 = False
                    for option in select.options:
                        if '2024' in option.text or option.get_attribute('value') == '2024':
                            print(f"   ✅ Found 2024: Value='{option.get_attribute('value')}', Text='{option.text}'")
                            found_2024 = True
                            break
                    
                    if not found_2024:
                        print("   ❌ 2024 not found in year options")
                        
                except Exception as e:
                    print(f"   ❌ Error inspecting year: {e}")

            print("\n=== DIAGNOSTIC COMPLETE ===")
            print("You can now manually interact with the form to test.")
            input("Press Enter to close the browser...")

        finally:
            driver.quit()

if __name__ == '__main__':
    scraper = FirefoxDiagnosticScraper()
    scraper.run()