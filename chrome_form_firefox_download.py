#!/usr/bin/env python3
"""
Fully Automated Hybrid Scraper: Chrome for Forms, Firefox for Downloads

This script uses two browsers for maximum stability and automation:
1.  Chrome (with Proxy IP Switching): Handles the initial form filling,
    CAPTCHA submission, and extraction of document links.
2.  Firefox (No Proxy): Handles the individual downloading of each document
    to avoid proxy issues with download servers.

The script is fully automated and requires no y/n prompts. Only the
CAPTCHA value needs to be entered manually.
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
from selenium.common.exceptions import TimeoutException

class HybridAutomatedScraper:
    def __init__(self):
        """Initializes the fully automated hybrid scraper."""
        # --- Configuration ---
        self.proxy_password = "Aditya@58"
        self.max_documents_to_download = 25
        self.delay_between_downloads = 4  # seconds

        # --- Internal State ---
        self.chrome_session_count = 0
        
        # --- Directory Setup ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "hybrid_automated_run")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 FULLY AUTOMATED HYBRID SCRAPER (CHROME + FIREFOX)")
        print("=" * 60)
        print("✅ Chrome: IP Switching, Form Filling, CAPTCHA")
        print("✅ Firefox: Stable Document Downloads")
        print(f"✅ Delay Between Downloads: {self.delay_between_downloads} seconds")
        print(f"🎯 Target Documents: {self.max_documents_to_download}")
        print("=" * 60)

    def _get_chrome_proxy_session_id(self):
        """Generates a new, unique session ID for Chrome's proxy."""
        self.chrome_session_count += 1
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f"chrome-auto-{timestamp}-{random_str}-{self.chrome_session_count}"

    def _create_chrome_driver_with_proxy(self):
        """Creates a new Chrome WebDriver instance with a fresh IP address."""
        options = ChromeOptions()
        session_id = self._get_chrome_proxy_session_id()
        
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

    def _create_firefox_driver_for_download(self):
        """Creates a clean Firefox WebDriver instance for downloading."""
        options = FirefoxOptions()
        options.add_argument("--headless")  # Downloads can run in the background
        
        try:
            driver = webdriver.Firefox(options=options)
            return driver
        except Exception as e:
            print(f"❌ Failed to create Firefox driver: {e}")
            return None

    def run_search_and_get_links(self):
        """
        Phase 1: Use Chrome with IP switching to fill the form, solve the
        CAPTCHA, and extract all document links.
        """
        print("\n--- PHASE 1: SEARCHING FOR DOCUMENTS WITH CHROME ---")
        driver = self._create_chrome_driver_with_proxy()
        if not driver:
            return []

        try:
            # 1. Navigate to the website
            print("🌐 Navigating to IGR website...")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "dbselect")))
            
            # 2. Fill the form automatically
            print("📝 Automatically filling form for Mumbai/2024/Agreement...")
            self._fill_search_form(driver)

            # 3. Handle CAPTCHA manually
            if not self._handle_manual_captcha(driver):
                print("❌ CAPTCHA process failed. Aborting.")
                return []
            
            # 4. Submit and extract links
            print("📤 Submitting form and extracting links...")
            document_links = self._submit_and_extract(driver)
            
            return document_links

        except Exception as e:
            print(f"❌ An error occurred during the Chrome search phase: {e}")
            return []
        finally:
            if driver:
                driver.quit()
                print("✅ Chrome browser closed.")

    def _fill_search_form(self, driver):
        """Fills the search form with predefined values."""
        try:
            # Select Database (Current Year)
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            time.sleep(1)
            
            # Select District (Mumbai)
            dist_select = Select(driver.find_element(By.ID, "district_id"))
            for option in dist_select.options:
                if "mumbai" in option.text.lower() or "मुंबई" in option.text:
                    dist_select.select_by_value(option.get_attribute("value"))
                    break
            time.sleep(2)

            # Select Taluka (Sub-district) and Village
            Select(driver.find_element(By.ID, "subdistrict_id")).select_by_index(1)
            time.sleep(2)
            Select(driver.find_element(By.ID, "village_id")).select_by_index(1)
            time.sleep(2)

            # Select Year (2024)
            Select(driver.find_element(By.ID, "year")).select_by_visible_text("2024")
            time.sleep(1)

            # Select Article (Agreement to Sale)
            article_select = Select(driver.find_element(By.ID, "article_id"))
            for option in article_select.options:
                if "agreement" in option.text.lower() or "विकस" in option.text:
                    article_select.select_by_value(option.get_attribute("value"))
                    break
            
            print("✅ Form filled successfully.")
        except Exception as e:
            print(f"⚠️ Warning: A field could not be set during form fill: {e}")

    def _handle_manual_captcha(self, driver):
        """Shows CAPTCHA to user and waits for input."""
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
            return False

        try:
            driver.find_element(By.ID, "txtcaptcha").send_keys(captcha_text)
            print("✅ CAPTCHA entered.")
            return True
        except NoSuchElementException:
            print("❌ Could not find CAPTCHA input box.")
            return False

    def _submit_and_extract(self, driver):
        """Submits the form and extracts all matching document links."""
        driver.find_element(By.ID, "search").click()
        print("⏳ Waiting for search results to load...")
        time.sleep(8)

        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails/indexii')]")
        if not links:
            print("❌ No document links found on the results page.")
            return []

        urls = [link.get_attribute("href") for link in links]
        print(f"📄 Found {len(urls)} document links to download.")
        return urls

    def download_all_documents(self, urls):
        """
        Phase 2: Use Firefox to download each document from the provided list
        of URLs, with a delay between each download.
        """
        if not urls:
            print("No documents to download. Skipping Phase 2.")
            return

        print(f"\n--- PHASE 2: DOWNLOADING {len(urls)} DOCUMENTS WITH FIREFOX ---")
        
        docs_to_process = urls[:self.max_documents_to_download]
        print(f"🎯 Capped to {len(docs_to_process)} documents based on configuration.")

        for i, url in enumerate(docs_to_process, 1):
            print(f"\n--- Downloading Document {i}/{len(docs_to_process)} ---")
            
            # --- Enforce delay between downloads ---
            if i > 1:
                print(f"⏳ Waiting for {self.delay_between_downloads} seconds...")
                time.sleep(self.delay_between_downloads)

            driver = self._create_firefox_driver_for_download()
            if not driver:
                print(f"❌ Skipping document {i} due to Firefox driver failure.")
                continue

            try:
                print(f"🦊 Firefox navigating to URL...")
                driver.get(url)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                content = driver.page_source
                if len(content) < 1000:
                    print("⚠️ Downloaded content is too small, likely an error page.")
                    continue

                # Save the document and its metadata
                self._save_document(i, url, content)

            except Exception as e:
                print(f"❌ An error occurred while downloading document {i}: {e}")
            finally:
                if driver:
                    driver.quit()
    
    def _save_document(self, index, url, content):
        """Saves the document content and metadata to files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"Document_{index:03d}_{timestamp}"
        
        # Save HTML file
        html_path = os.path.join(self.docs_dir, f"{filename_base}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save Metadata
        meta_path = os.path.join(self.meta_dir, f"{filename_base}_meta.json")
        metadata = {
            "document_index": index,
            "source_url": url,
            "download_timestamp": datetime.now().isoformat(),
            "content_size_chars": len(content),
            "retrieval_method": "Chrome (Search) + Firefox (Download)"
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"✅ Document {index} saved successfully to '{self.docs_dir}'")

    def run(self):
        """Executes the entire automated two-browser process."""
        # Phase 1: Search with Chrome
        document_urls = self.run_search_and_get_links()

        # Phase 2: Download with Firefox
        self.download_all_documents(document_urls)

        # Final Summary
        print("\n\n--- AUTOMATION COMPLETE ---")
        print(f"Searched for documents and attempted to download {min(len(document_urls), self.max_documents_to_download)}.")
        print(f"📁 All files are saved in: {os.path.abspath(self.data_dir)}")
        print("🎉 Process finished.")


if __name__ == "__main__":
    try:
        scraper = HybridAutomatedScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ A critical error occurred in the main process: {e}")
        import traceback
        traceback.print_exc() 