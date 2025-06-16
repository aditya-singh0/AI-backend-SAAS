#!/usr/bin/env python3
"""
Fully Automated Chrome-Only IGR Scraper with IP Switching

This script uses a single browser (Chrome) for the entire process:
1.  **IP Switching:** Uses a new proxy IP session for the initial search and
    for each subsequent document download.
2.  **Automated Form Filling:** Automatically fills the form for
    Mumbai / 2024 / Agreement to Sale.
3.  **Manual CAPTCHA:** The script will automatically open the CAPTCHA image
    and wait for the user to input the value.
4.  **Automated Downloads:** Downloads all found documents sequentially with
    a 4-second delay between each.

The script is fully automated and requires no y/n prompts.
"""

import time
import random
import string
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ChromeOnlyAutomatedScraper:
    def __init__(self):
        """Initializes the fully automated Chrome-only scraper."""
        # --- Configuration ---
        self.proxy_password = "Aditya@58"
        self.max_documents_to_download = 25
        self.delay_between_downloads = 4  # seconds

        # --- Internal State ---
        self.session_count = 0
        
        # --- Directory Setup ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "chrome_only_run")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 FULLY AUTOMATED CHROME-ONLY SCRAPER")
        print("=" * 60)
        print("✅ Chrome used for all operations.")
        print("✅ IP Switching for search and each download.")
        print(f"✅ Delay Between Downloads: {self.delay_between_downloads} seconds.")
        print("=" * 60)

    def _get_new_session_id(self):
        """Generates a new, unique session ID for proxy rotation."""
        self.session_count += 1
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"chrome-only-{timestamp}-{random_str}-{self.session_count}"

    def _create_driver_with_new_ip(self):
        """Creates a new Chrome WebDriver with a fresh proxy IP session."""
        options = ChromeOptions()
        session_id = self._get_new_session_id()
        
        if self.proxy_password:
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.proxy_password}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔄 Launching Chrome with new IP session: {session_id}")
        
        options.add_argument("--window-size=1280,800")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"❌ Failed to create Chrome driver: {e}")
            return None

    def _fill_search_form(self, driver):
        """Fills the IGR search form with explicit waits for stability."""
        try:
            print("📝 Filling search form...")
            # Use explicit waits for each dropdown to ensure it is clickable
            Select(WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "dbselect")))).select_by_value("3")
            
            dist_select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "district_id")))
            dist_select = Select(dist_select_element)
            for option in dist_select.options:
                if "mumbai" in option.text.lower() or "मुंबई" in option.text:
                    dist_select.select_by_value(option.get_attribute("value"))
                    break
            
            Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "subdistrict_id")))).select_by_index(1)
            Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "village_id")))).select_by_index(1)
            Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "year")))).select_by_visible_text("2024")
            
            article_select_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "article_id")))
            article_select = Select(article_select_element)
            for option in article_select.options:
                if "agreement" in option.text.lower() or "विकस" in option.text:
                    article_select.select_by_value(option.get_attribute("value"))
                    break
            
            print("✅ Form filled successfully.")
            return True
        except Exception as e:
            print(f"❌ Error during form fill: {e}")
            return False

    def _handle_manual_captcha(self, driver):
        """Handles the manual CAPTCHA entry process."""
        print("\n--- MANUAL CAPTCHA STEP ---")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.captcha_dir, f"captcha_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        
        try:
            os.startfile(screenshot_path)
            print(f"📸 CAPTCHA screenshot opened: {screenshot_path}")
        except:
            print(f"📸 Please open screenshot manually: {screenshot_path}")

        captcha_text = input("🔤 Please enter the CAPTCHA text you see: ").strip()
        if not captcha_text:
            print("❌ No CAPTCHA entered.")
            return False

        try:
            driver.find_element(By.ID, "txtcaptcha").send_keys(captcha_text)
            print("✅ CAPTCHA entered.")
            return True
        except NoSuchElementException:
            print("❌ Could not find CAPTCHA input box.")
            return False

    def _submit_and_extract_links(self, driver):
        """Submits the form and extracts the resulting document links."""
        try:
            driver.find_element(By.ID, "search").click()
            print("📤 Form submitted. Waiting for results...")
            
            # Wait for the results table to appear
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tbl")))
            
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails/indexii')]")
            if not links:
                print("❌ No document links found on the results page.")
                return []

            urls = [link.get_attribute("href") for link in links]
            print(f"📄 Found {len(urls)} document links.")
            return urls
        except TimeoutException:
            print("❌ Timed out waiting for search results. The page may have an error or CAPTCHA was incorrect.")
            return []
        except Exception as e:
            print(f"❌ Error submitting or extracting links: {e}")
            return []

    def _download_document(self, url, index):
        """Downloads a single document using a new browser instance for a fresh IP."""
        print(f"\n--- Downloading Document {index}/{self.max_documents_to_download} ---")
        driver = self._create_driver_with_new_ip()
        if not driver:
            print(f"❌ Skipping document {index} due to driver failure.")
            return

        try:
            print(f"🌐 Navigating to document URL...")
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            content = driver.page_source
            if len(content) < 1000:
                print("⚠️ Downloaded content is too small, likely an error page.")
                return

            self._save_document_content(index, url, content)
        except Exception as e:
            print(f"❌ An error occurred while downloading document {index}: {e}")
        finally:
            if driver:
                driver.quit()

    def _save_document_content(self, index, url, content):
        """Saves the document HTML and metadata."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"Chrome_Doc_{index:03d}_{timestamp}"
        
        html_path = os.path.join(self.docs_dir, f"{filename_base}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        meta_path = os.path.join(self.meta_dir, f"{filename_base}_meta.json")
        metadata = {
            "document_index": index,
            "source_url": url,
            "download_timestamp": datetime.now().isoformat(),
            "content_size_chars": len(content),
            "retrieval_method": "Chrome Only with IP Switching",
            "session_count": self.session_count,
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"✅ Document {index} saved successfully.")

    def run(self):
        """Executes the entire automated process."""
        # --- Phase 1: Search ---
        print("\n--- PHASE 1: SEARCHING FOR DOCUMENTS ---")
        search_driver = self._create_driver_with_new_ip()
        if not search_driver:
            print("❌ Cannot proceed without a browser. Aborting.")
            return

        document_urls = []
        try:
            print("🌐 Navigating to IGR website...")
            search_driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            if self._fill_search_form(search_driver):
                if self._handle_manual_captcha(search_driver):
                    document_urls = self._submit_and_extract_links(search_driver)
        finally:
            print("✅ Search phase finished.")
            search_driver.quit()

        # --- Phase 2: Download ---
        if not document_urls:
            print("\nNo documents found to download. Process finished.")
            return
            
        print(f"\n--- PHASE 2: DOWNLOADING DOCUMENTS ---")
        docs_to_download = document_urls[:self.max_documents_to_download]
        
        for i, url in enumerate(docs_to_download, 1):
            self._download_document(url, i)
            
            # Enforce delay between downloads
            if i < len(docs_to_download):
                print(f"⏳ Waiting for {self.delay_between_downloads} seconds...")
                time.sleep(self.delay_between_downloads)

        # --- Final Summary ---
        print("\n\n--- AUTOMATION COMPLETE ---")
        print(f"Attempted to download {len(docs_to_download)} documents.")
        print(f"📁 All files are saved in: {os.path.abspath(self.data_dir)}")
        print("🎉 Process finished.")


if __name__ == "__main__":
    try:
        scraper = ChromeOnlyAutomatedScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ A critical error occurred: {e}")
        import traceback
        traceback.print_exc() 