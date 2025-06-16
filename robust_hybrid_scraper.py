#!/usr/bin/env python3
"""
Fully Automated Hybrid Scraper (Robust Version)
- Chrome (Detached): For stable form filling with IP switching.
- Firefox: For reliable, headless document downloads.
- Delay between downloads is enforced.
- No user prompts except for CAPTCHA.
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
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class RobustHybridScraper:
    def __init__(self):
        """Initializes the robust, fully automated hybrid scraper."""
        # --- Configuration ---
        self.proxy_password = "Aditya@58"
        self.max_documents_to_download = 25
        self.delay_between_downloads = 4

        # --- Internal State ---
        self.chrome_session_count = 0
        
        # --- Directory Setup ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "robust_hybrid_run")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 ROBUST HYBRID SCRAPER (CHROME + FIREFOX)")
        print("=" * 60)
        print("✅ Chrome (Detached Mode): Stable IP Switching & Form Filling")
        print("✅ Firefox (Headless): Reliable Document Downloads")
        print(f"✅ Delay Between Downloads: {self.delay_between_downloads} seconds")
        print("=" * 60)

    def _get_chrome_proxy_session_id(self):
        self.chrome_session_count += 1
        timestamp = int(time.time())
        return f"chrome-robust-{timestamp}-{self.chrome_session_count}"

    def _create_robust_chrome_driver(self):
        """Creates a robust Chrome driver in detached mode with proxy."""
        options = ChromeOptions()
        session_id = self._get_chrome_proxy_session_id()
        
        if self.proxy_password:
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.proxy_password}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔄 Launching Chrome with new IP session: {session_id}")

        # --- Key Stability Improvement: Detached Mode ---
        options.add_experimental_option("detach", True)
        
        options.add_argument("--window-size=1280,850")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"❌ Failed to create robust Chrome driver: {e}")
            return None

    def _create_firefox_driver_for_download(self):
        """Creates a clean, headless Firefox driver for downloading."""
        options = FirefoxOptions()
        options.add_argument("--headless")
        
        try:
            driver = webdriver.Firefox(options=options)
            return driver
        except Exception as e:
            print(f"❌ Failed to create Firefox driver: {e}")
            return None

    def run_search_with_chrome(self):
        """Phase 1: Use a robust Chrome instance for form filling and CAPTCHA."""
        print("\n--- PHASE 1: SEARCHING FOR DOCUMENTS (CHROME) ---")
        driver = self._create_robust_chrome_driver()
        if not driver:
            return []

        try:
            # 1. Navigate
            print("🌐 Navigating to IGR website...")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "dbselect")))
            
            # 2. Fill form
            print("📝 Automatically filling form...")
            self._fill_search_form(driver)

            # 3. Handle CAPTCHA
            if not self._handle_manual_captcha(driver):
                print("❌ CAPTCHA process failed. Check the detached Chrome window.")
                return []
            
            # 4. Submit and Extract
            print("📤 Submitting form and extracting links...")
            document_links = self._submit_and_extract(driver)
            
            return document_links

        except Exception as e:
            print(f"❌ An error occurred during the Chrome phase: {e}")
            print("ℹ️ The Chrome browser window may still be open for inspection.")
            return []
        # NOTE: We do not call driver.quit() here because of detached mode.
        # The browser will remain open after the script finishes or fails.

    def _fill_search_form(self, driver):
        """Fills the search form with robust waits."""
        try:
            # Wrap each selection in a wait for better stability
            Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "dbselect")))).select_by_value("3")
            
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
        except Exception as e:
            print(f"⚠️ Warning: A field could not be set: {e}")

    def _handle_manual_captcha(self, driver):
        """Shows CAPTCHA and waits for user input."""
        print("\n--- MANUAL CAPTCHA STEP ---")
        # The browser is detached and visible, so screenshot is a backup
        print("ℹ️ Please look at the visible Chrome browser window for the CAPTCHA.")
        
        captcha_text = input("🔤 Enter the CAPTCHA text you see in the Chrome window: ").strip()
        if not captcha_text:
            return False

        try:
            driver.find_element(By.ID, "txtcaptcha").send_keys(captcha_text)
            print("✅ CAPTCHA entered.")
            return True
        except NoSuchElementException:
            print("❌ Could not find CAPTCHA input box.")
            return False

    def _submit_and_extract(self, driver):
        """Submits form and extracts document URLs."""
        driver.find_element(By.ID, "search").click()
        print("⏳ Waiting for search results...")
        
        # Wait for the results table to appear
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "tbl")))
        
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails/indexii')]")
        if not links:
            print("❌ No document links found on results page.")
            return []

        urls = [link.get_attribute("href") for link in links]
        print(f"📄 Found {len(urls)} document links.")
        return urls

    def download_all_documents(self, urls):
        """Phase 2: Use Firefox to download documents with delays."""
        if not urls:
            print("No documents to download. Aborting Phase 2.")
            return

        print(f"\n--- PHASE 2: DOWNLOADING {len(urls)} DOCUMENTS (FIREFOX) ---")
        
        docs_to_process = urls[:self.max_documents_to_download]
        print(f"🎯 Capped to {len(docs_to_process)} documents.")

        for i, url in enumerate(docs_to_process, 1):
            print(f"\n--- Downloading Document {i}/{len(docs_to_process)} ---")
            
            if i > 1:
                print(f"⏳ Waiting for {self.delay_between_downloads} seconds...")
                time.sleep(self.delay_between_downloads)

            driver = self._create_firefox_driver_for_download()
            if not driver:
                continue

            try:
                print(f"🦊 Firefox navigating to URL...")
                driver.get(url)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                self._save_document(i, url, driver.page_source)
            except Exception as e:
                print(f"❌ Error downloading document {i}: {e}")
            finally:
                if driver:
                    driver.quit()
    
    def _save_document(self, index, url, content):
        """Saves document content and metadata."""
        if len(content) < 1000:
            print("⚠️ Downloaded content is too small, likely an error page.")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"Robust_Doc_{index:03d}_{timestamp}"
        
        html_path = os.path.join(self.docs_dir, f"{filename_base}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        meta_path = os.path.join(self.meta_dir, f"{filename_base}_meta.json")
        metadata = {
            "document_index": index,
            "source_url": url,
            "download_timestamp": datetime.now().isoformat(),
            "content_size_chars": len(content),
            "retrieval_method": "Robust Chrome (Search) + Firefox (Download)"
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"✅ Document {index} saved successfully.")

    def run(self):
        """Executes the entire robust, automated process."""
        # Phase 1
        document_urls = self.run_search_with_chrome()

        # Phase 2
        self.download_all_documents(document_urls)

        print("\n\n--- AUTOMATION COMPLETE ---")
        print(f"Searched for documents and attempted to download {min(len(document_urls), self.max_documents_to_download)}.")
        print(f"📁 All files are in: {os.path.abspath(self.data_dir)}")
        print("ℹ️ A Chrome window may remain open for inspection. You can close it manually.")
        print("🎉 Process finished.")


if __name__ == "__main__":
    try:
        scraper = RobustHybridScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ A critical error occurred: {e}")
        import traceback
        traceback.print_exc() 