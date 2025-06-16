#!/usr/bin/env python3
"""
Final, Stable, Fully Automated Chrome-Only IGR Scraper

This script uses a single browser (Chrome) and incorporates robust waits
to handle timing issues during form filling.

-   **IP Switching:** A new IP is used for the initial search and for each
    subsequent document download.
-   **Automated Form Filling:** Uses explicit, robust waits to ensure
    the page is ready before interacting with elements.
-   **Manual CAPTCHA:** The only manual step.
-   **Automated Downloads:** Downloads documents with a 4-second delay.
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

class FinalStableScraper:
    def __init__(self):
        """Initializes the final, stable, automated scraper."""
        # --- Configuration ---
        self.proxy_password = "Aditya@58"
        self.max_documents_to_download = 25
        self.delay_between_downloads = 4

        # --- Internal State ---
        self.session_count = 0
        
        # --- Directory Setup ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "final_stable_run")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 FINAL STABLE CHROME-ONLY SCRAPER")
        print("=" * 60)
        print("✅ Using robust waits for maximum stability.")
        print("✅ IP Switching for search and each download.")
        print("=" * 60)

    def _get_new_session_id(self):
        self.session_count += 1
        timestamp = int(time.time())
        return f"final-stable-{timestamp}-{self.session_count}"

    def _create_driver_with_new_ip(self):
        """Creates a new Chrome WebDriver with a fresh proxy IP session."""
        options = ChromeOptions()
        session_id = self._get_new_session_id()
        
        if self.proxy_password:
            proxy_user = f"td-customer-hdXMhtuot8ni-sessid-{session_id}"
            proxy_url = f"http://{proxy_user}:{self.proxy_password}@42q6t9rp.pr.thordata.net:9999"
            options.add_argument(f"--proxy-server={proxy_url}")
            print(f"🔄 Launching Chrome with IP session: {session_id}")
        
        options.add_argument("--window-size=1280,800")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(5) # Add a small implicit wait
            return driver
        except Exception as e:
            print(f"❌ Failed to create Chrome driver: {e}")
            return None

    def _fill_search_form_robustly(self, driver):
        """Fills the search form using robust, explicit waits."""
        try:
            print("📝 Filling search form with robust waits...")
            
            # --- KEY FIX: Wait for a reliable element to be clickable ---
            # The 'district_id' dropdown is a good indicator the form is ready.
            wait = WebDriverWait(driver, 20)
            dist_select_element = wait.until(EC.element_to_be_clickable((By.ID, "district_id")))
            
            # Now that we know the form is ready, proceed with selections.
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            
            dist_select = Select(dist_select_element)
            for option in dist_select.options:
                if "mumbai" in option.text.lower() or "मुंबई" in option.text:
                    dist_select.select_by_value(option.get_attribute("value"))
                    break
            
            # Wait for subsequent dropdowns to populate
            subdist_element = wait.until(EC.element_to_be_clickable((By.ID, "subdistrict_id")))
            Select(subdist_element).select_by_index(1)
            
            village_element = wait.until(EC.element_to_be_clickable((By.ID, "village_id")))
            Select(village_element).select_by_index(1)
            
            Select(wait.until(EC.element_to_be_clickable((By.ID, "year")))).select_by_visible_text("2024")
            
            article_element = wait.until(EC.element_to_be_clickable((By.ID, "article_id")))
            article_select = Select(article_element)
            for option in article_select.options:
                if "agreement" in option.text.lower() or "विकस" in option.text:
                    article_select.select_by_value(option.get_attribute("value"))
                    break
            
            print("✅ Form filled successfully using robust method.")
            return True
        except TimeoutException:
            print("❌ Timed out waiting for form elements to become available. The page may be slow or unresponsive.")
            return False
        except Exception as e:
            print(f"❌ An unexpected error occurred during robust form fill: {e}")
            return False

    def _handle_manual_captcha(self, driver):
        """Handles the manual CAPTCHA entry process."""
        print("\n--- MANUAL CAPTCHA STEP ---")
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "captcha_image")))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.captcha_dir, f"captcha_{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            
            os.startfile(screenshot_path)
            print(f"📸 CAPTCHA screenshot opened: {screenshot_path}")
        except:
            print(f"⚠️ Could not take screenshot, please look at the browser window.")

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

    def _submit_and_extract_links(self, driver):
        """Submits the form and extracts the resulting document links."""
        try:
            driver.find_element(By.ID, "search").click()
            print("📤 Form submitted. Waiting for results...")
            
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tbl")))
            
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails/indexii')]")
            if not links:
                return []

            urls = [link.get_attribute("href") for link in links]
            print(f"📄 Found {len(urls)} document links.")
            return urls
        except TimeoutException:
            print("❌ Timed out waiting for search results. CAPTCHA may have been incorrect.")
            return []
        except Exception as e:
            print(f"❌ Error submitting or extracting links: {e}")
            return []

    def _download_document(self, url, index):
        """Downloads a single document using a new browser instance for a fresh IP."""
        print(f"\n--- Downloading Document {index}/{self.max_documents_to_download} ---")
        driver = self._create_driver_with_new_ip()
        if not driver:
            return

        try:
            print(f"🌐 Navigating to document URL...")
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self._save_document_content(index, url, driver.page_source)
        except Exception as e:
            print(f"❌ Error downloading document {index}: {e}")
        finally:
            if driver:
                driver.quit()

    def _save_document_content(self, index, url, content):
        """Saves the document HTML and metadata."""
        if len(content) < 1000:
            print("⚠️ Downloaded content is too small, likely an error page.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"Final_Doc_{index:03d}_{timestamp}"
        
        html_path = os.path.join(self.docs_dir, f"{filename_base}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        meta_path = os.path.join(self.meta_dir, f"{filename_base}_meta.json")
        metadata = { "document_index": index, "source_url": url, "download_timestamp": datetime.now().isoformat() }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"✅ Document {index} saved successfully.")

    def run(self):
        """Executes the entire automated process."""
        # Phase 1: Search
        print("\n--- PHASE 1: SEARCHING FOR DOCUMENTS ---")
        search_driver = self._create_driver_with_new_ip()
        if not search_driver:
            print("❌ Cannot proceed without a browser. Aborting.")
            return

        document_urls = []
        try:
            search_driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            if self._fill_search_form_robustly(search_driver):
                if self._handle_manual_captcha(search_driver):
                    document_urls = self._submit_and_extract_links(search_driver)
        finally:
            print("✅ Search phase finished.")
            search_driver.quit()

        # Phase 2: Download
        if not document_urls:
            print("\nNo documents found to download. Process finished.")
            return
            
        print(f"\n--- PHASE 2: DOWNLOADING DOCUMENTS ---")
        docs_to_download = document_urls[:self.max_documents_to_download]
        
        for i, url in enumerate(docs_to_download, 1):
            self._download_document(url, i)
            
            if i < len(docs_to_download):
                print(f"⏳ Waiting for {self.delay_between_downloads} seconds...")
                time.sleep(self.delay_between_downloads)

        print("\n\n--- AUTOMATION COMPLETE ---")
        print(f"Attempted to download {len(docs_to_download)} documents.")
        print(f"📁 All files are saved in: {os.path.abspath(self.data_dir)}")
        print("🎉 Process finished.")


if __name__ == "__main__":
    try:
        scraper = FinalStableScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ A critical error occurred: {e}")
        import traceback
        traceback.print_exc() 