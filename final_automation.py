#!/usr/bin/env python3
"""FINAL COMPLETE IGR AUTOMATION - Manual CAPTCHA"""
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

class FinalAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.search_url = f"{self.base_url}/eDisplay/Propertydetails/index"
        self.data_dir = "data"
        self.docs_dir = os.path.join(self.data_dir, "final_documents")
        os.makedirs(self.docs_dir, exist_ok=True)
        print("🚀 FINAL COMPLETE IGR AUTOMATION")
        print("=" * 60)
        print("✅ Complete form automation (Database→District→Taluka→Village→Article)")
        print("👤 Manual CAPTCHA solving (most reliable)")
        print("📥 Automated bulk document downloading")
        print(f"📁 Documents: {os.path.abspath(self.docs_dir)}")
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
            
            # COMPLETE FORM AUTOMATION
            print("\n🤖 STARTING COMPLETE FORM AUTOMATION...")
            print("[1/5] Database selection...")
            if not self.safe_select(driver, "dbselect", "3"):
                return
            time.sleep(2)
            
            print("[2/5] Mumbai district selection...")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#district_id option[value='31']")))
            if not self.safe_select(driver, "district_id", "31"):
                return
            time.sleep(2)
            
            print("[3/5] Taluka selection...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "taluka_id")))
                taluka_select = Select(driver.find_element(By.ID, "taluka_id"))
                if len(taluka_select.options) > 1:
                    taluka_select.select_by_index(1)
                    print("   ✅ Taluka auto-selected")
                time.sleep(2)
            except:
                print("   ⚠️ Taluka not available")
            
            print("[4/5] Village selection...")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))
                village_select = Select(driver.find_element(By.ID, "village_id"))
                if len(village_select.options) > 1:
                    village_select.select_by_index(1)
                    print("   ✅ Village auto-selected")
                time.sleep(2)
            except:
                print("   ⚠️ Village not available")
            
            print("[5/5] Agreement to Sale article selection...")
            if not self.safe_select(driver, "article_id", "42"):
                return
            time.sleep(2)
            
            print("\n✅ FORM AUTOMATION COMPLETED!")
            print("🎯 All form fields filled automatically:")
            print("   📋 Database: Recent years (3)")
            print("   🏙️ District: Mumbai (31)")
            print("   🏘️ Taluka: Auto-selected first option")
            print("   🏠 Village: Auto-selected first option")
            print("   📄 Article: Agreement to Sale (42)")
            
            # MANUAL CAPTCHA STEP
            print("\n" + "="*25 + " USER ACTION REQUIRED " + "="*25)
            print("🎯 The form has been completely automated!")
            print("👤 Now please do the following in the Firefox browser:")
            print("1. 🔍 Look at the CAPTCHA image")
            print("2. ✍️ Type the CAPTCHA text in the input field")
            print("3. 🔍 Click the 'Search' button")
            print("4. ⏳ Wait for search results to load completely")
            print("="*76)
            
            input("\n>>> Press Enter here AFTER search results have loaded...")
            
            # AUTOMATED DOCUMENT DOWNLOADING
            print("\n📥 STARTING AUTOMATED BULK DOWNLOAD...")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Multiple selectors to find document links
            selectors = [
                "table a[href*='indexii']",
                "a[href*='view']", 
                "a[href*='document']",
                "table a[href*='/eDisplay/']",
                "a[href*='pdf']",
                "a[href*='download']"
            ]
            
            all_links = []
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    all_links.extend(found)
                    print(f"   📋 Found {len(found)} links with: {selector}")
            
            # Remove duplicates
            unique_links = []
            seen_hrefs = set()
            for link in all_links:
                href = link.get('href', '')
                if href and href not in seen_hrefs:
                    unique_links.append(link)
                    seen_hrefs.add(href)
            
            if not unique_links:
                print("❌ No document links found")
                # Save results for debugging
                debug_file = os.path.join(self.docs_dir, 'search_results_debug.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"📄 Results saved for debugging: {debug_file}")
                return
            
            print(f"\n📄 Found {len(unique_links)} unique documents to download")
            print("🚀 Starting automated bulk download...")
            
            download_count = 0
            for i, link in enumerate(unique_links):
                print(f"\n📥 Downloading document {i+1}/{len(unique_links)}...")
                
                href = link.get('href', '')
                doc_url = f"{self.base_url}{href}" if not href.startswith('http') else href
                
                # New driver instance for each document
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(doc_url)
                    time.sleep(3)
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
                    filename = f"Agreement_Doc_{i+1:03d}_{timestamp}.html"
                    filepath = os.path.join(self.docs_dir, filename)
                    
                    # Save document
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(doc_driver.page_source)
                    
                    download_count += 1
                    print(f"   ✅ Saved: {filename}")
                    
                except Exception as e:
                    print(f"   ❌ Error downloading document {i+1}: {e}")
                finally:
                    doc_driver.quit()
                
                # Brief pause between downloads
                time.sleep(1)
            
            # FINAL SUMMARY
            print("\n" + "="*60)
            print("🎉 FINAL AUTOMATION COMPLETE!")
            print(f"📊 Successfully downloaded: {download_count} documents")
            print(f"📁 Documents location: {os.path.abspath(self.docs_dir)}")
            print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("💡 All documents are saved as HTML files containing the full content")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Automation error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n👋 Closing main browser...")
            driver.quit()

if __name__ == "__main__":
    automation = FinalAutomation()
    automation.run()