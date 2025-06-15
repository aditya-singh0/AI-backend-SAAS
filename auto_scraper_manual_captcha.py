#!/usr/bin/env python3
"""Complete IGR Automation with Manual CAPTCHA"""
import os, sys, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AutoScraperManualCaptcha:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.search_url = f"{self.base_url}/eDisplay/Propertydetails/index"
        self.data_dir = "data"
        self.docs_dir = os.path.join(self.data_dir, "auto_docs")
        os.makedirs(self.docs_dir, exist_ok=True)
        print("🚀 COMPLETE IGR AUTOMATION (Manual CAPTCHA)")
        print("=" * 60)
        print(f"📁 Documents will be saved to: {os.path.abspath(self.docs_dir)}")
        print("=" * 60)

    def setup_driver(self):
        options = webdriver.FirefoxOptions()
        service = Service(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)

    def safe_select(self, driver, select_id, value):
        try:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, select_id)))
            Select(element).select_by_value(value)
            print(f"   ✅ {select_id}: {value}")
            return True
        except Exception as e:
            print(f"   ❌ Failed {select_id}: {e}")
            return False

    def run(self):
        driver = self.setup_driver()
        try:
            print("\n🌐 Loading IGR website...")
            driver.get(self.search_url)
            time.sleep(3)
            
            # Complete form automation
            print("\n🤖 AUTOMATING COMPLETE FORM...")
            print("[1/5] Selecting database (Recent years)...")
            if not self.safe_select(driver, "dbselect", "3"):
                return
            time.sleep(2)
            
            print("[2/5] Selecting Mumbai district...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']")))
            if not self.safe_select(driver, "district_id", "31"):
                return
            time.sleep(2)
            
            print("[3/5] Selecting Taluka...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
                taluka_select = Select(driver.find_element(By.ID, "taluka_id"))
                if len(taluka_select.options) > 1:
                    taluka_select.select_by_index(1)
                    print("   ✅ Taluka selected")
                time.sleep(2)
            except:
                print("   ⚠️ Taluka not available")
            
            print("[4/5] Selecting Village...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                village_select = Select(driver.find_element(By.ID, "village_id"))
                if len(village_select.options) > 1:
                    village_select.select_by_index(1)
                    print("   ✅ Village selected")
                time.sleep(2)
            except:
                print("   ⚠️ Village not available")
            
            print("[5/5] Selecting Agreement to Sale article...")
            if not self.safe_select(driver, "article_id", "42"):
                return
            time.sleep(2)
            
            print("\n✅ FORM AUTOMATION COMPLETE!")
            print("🎯 All fields have been filled automatically:")
            print("   📋 Database: Recent years")
            print("   🏙️ District: Mumbai")
            print("   🏘️ Taluka: Auto-selected")
            print("   🏠 Village: Auto-selected")
            print("   📄 Article: Agreement to Sale")
            
            # Manual CAPTCHA step
            print("\n" + "="*25 + " USER ACTION REQUIRED " + "="*25)
            print("👤 Please do the following in the Firefox browser:")
            print("1. 🔍 Look at the CAPTCHA image")
            print("2. ✍️ Type the CAPTCHA text in the input field")
            print("3. 🔍 Click the 'Search' button")
            print("4. ⏳ Wait for search results to load")
            print("="*76)
            
            input("\n>>> Press Enter here AFTER you have solved CAPTCHA and search results are loaded...")
            
            # Automated document downloading
            print("\n📥 STARTING AUTOMATED DOCUMENT DOWNLOAD...")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Try multiple selectors to find document links
            selectors = [
                "table a[href*='indexii']",
                "a[href*='view']",
                "a[href*='document']",
                "table a[href*='/eDisplay/']",
                "a[href*='pdf']"
            ]
            
            links = []
            for selector in selectors:
                found_links = soup.select(selector)
                if found_links:
                    links.extend(found_links)
                    print(f"   📋 Found {len(found_links)} links with: {selector}")
            
            # Remove duplicates
            unique_links = []
            seen_hrefs = set()
            for link in links:
                href = link.get('href', '')
                if href and href not in seen_hrefs:
                    unique_links.append(link)
                    seen_hrefs.add(href)
            
            if not unique_links:
                print("❌ No document links found in search results")
                # Save results page for debugging
                with open(os.path.join(self.docs_dir, 'search_results.html'), 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("📄 Search results page saved for inspection")
                return
            
            print(f"\n📄 Found {len(unique_links)} unique document links")
            print("🚀 Starting bulk download...")
            
            download_count = 0
            for i, link in enumerate(unique_links):
                print(f"\n📥 Downloading document {i+1}/{len(unique_links)}...")
                
                href = link.get('href', '')
                doc_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                
                # Create new driver for each document
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"Agreement_Doc_{i+1:03d}_{timestamp}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    # Save document content
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(doc_driver.page_source)
                    
                    download_count += 1
                    print(f"   ✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error downloading document {i+1}: {e}")
                finally:
                    doc_driver.quit()
                
                # Small delay between downloads
                time.sleep(1)
            
            # Final summary
            print("\n" + "="*60)
            print("🎉 COMPLETE AUTOMATION FINISHED!")
            print(f"📊 Successfully downloaded: {download_count} documents")
            print(f"📁 Documents saved to: {os.path.abspath(self.docs_dir)}")
            print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Automation failed: {e}")
        finally:
            print("\n👋 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    scraper = AutoScraperManualCaptcha()
    scraper.run()