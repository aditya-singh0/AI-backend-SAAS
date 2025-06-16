#!/usr/bin/env python3
"""
Final, Most Stable, Firefox-Only Direct Scraper

This script prioritizes stability over all other features.
-   **No IP Switching:** Connects directly to the IGR website to prevent
    proxy-related browser crashes.
-   **Firefox Only:** Uses Firefox, which has proven more stable for this
    specific website's form.
-   **Automated Form Filling:** Fills the form for Mumbai / 2024 /
    Agreement to Sale using robust waits.
-   **Manual CAPTCHA & Automated Downloads:** The only manual step is the
    CAPTCHA entry. Downloads are fully automated with a 4-second delay.
"""

import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FirefoxStableDirectScraper:
    def __init__(self):
        """Initializes the stable, direct Firefox scraper."""
        # --- Configuration ---
        self.max_documents_to_download = 25
        self.delay_between_downloads = 4

        # --- Directory Setup ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "firefox_direct_run")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.captcha_dir = os.path.join(self.data_dir, "captcha_images")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.captcha_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 STABLE FIREFOX-ONLY DIRECT SCRAPER")
        print("=" * 60)
        print("✅ No IP Switching for maximum stability.")
        print("✅ Firefox used for all operations.")
        print("=" * 60)

    def _create_stable_firefox_driver(self):
        """Creates a stable Firefox WebDriver instance without a proxy."""
        options = FirefoxOptions()
        options.add_argument("--window-size=1280,800")
        
        try:
            driver = webdriver.Firefox(options=options)
            driver.implicitly_wait(5)
            return driver
        except Exception as e:
            print(f"❌ Failed to create Firefox driver: {e}")
            return None

    def _fill_search_form(self, driver):
        """Fills the search form with robust waits."""
        try:
            print("📝 Filling search form...")
            wait = WebDriverWait(driver, 20)
            
            # Wait for the main form element to be ready
            dist_select_element = wait.until(EC.element_to_be_clickable((By.ID, "district_id")))
            
            # Proceed with selections
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            
            dist_select = Select(dist_select_element)
            for option in dist_select.options:
                if "mumbai" in option.text.lower() or "मुंबई" in option.text:
                    dist_select.select_by_value(option.get_attribute("value"))
                    break
            
            # Wait for dependent dropdowns
            Select(wait.until(EC.element_to_be_clickable((By.ID, "subdistrict_id")))).select_by_index(1)
            Select(wait.until(EC.element_to_be_clickable((By.ID, "village_id")))).select_by_index(1)
            Select(wait.until(EC.element_to_be_clickable((By.ID, "year")))).select_by_visible_text("2024")
            
            article_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            for option in article_select.options:
                if "agreement" in option.text.lower() or "विकस" in option.text:
                    article_select.select_by_value(option.get_attribute("value"))
                    break
            
            print("✅ Form filled successfully.")
            return True
        except TimeoutException:
            print("❌ Timed out waiting for form elements. The page may be slow.")
            return False
        except Exception as e:
            print(f"❌ Error during form fill: {e}")
            return False

    def _handle_manual_captcha(self, driver):
        """Handles the manual CAPTCHA entry."""
        print("\n--- MANUAL CAPTCHA STEP ---")
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.ID, "captcha_image")))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.captcha_dir, f"captcha_{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            
            os.startfile(screenshot_path)
            print(f"📸 CAPTCHA screenshot opened: {screenshot_path}")
        except:
            print(f"⚠️ Could not take screenshot, please look at the Firefox window.")

        captcha_text = input("🔤 Please enter the CAPTCHA text: ").strip()
        if not captcha_text:
            return False

        try:
            driver.find_element(By.ID, "txtcaptcha").send_keys(captcha_text)
            print("✅ CAPTCHA entered.")
            return True
        except NoSuchElementException:
            print("❌ Could not find CAPTCHA input box.")
            return False

    def _submit_and_get_links(self, driver):
        """Submits the form and extracts document links."""
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

    def _download_document(self, url, index, total):
        """Downloads a single document using the same browser."""
        print(f"\n--- Downloading Document {index}/{total} ---")
        # Use a new tab to avoid losing the main page
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self._save_document_content(index, url, self.driver.page_source)
        except Exception as e:
            print(f"❌ Error downloading document {index}: {e}")
        finally:
            # Close the tab and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])


    def _save_document_content(self, index, url, content):
        """Saves the document content and metadata."""
        if len(content) < 1000:
            print("⚠️ Downloaded content is too small, likely an error page.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"Firefox_Doc_{index:03d}_{timestamp}"
        
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
        self.driver = self._create_stable_firefox_driver()
        if not self.driver:
            print("❌ Cannot proceed without a browser. Aborting.")
            return

        try:
            self.driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            if self._fill_search_form(self.driver):
                if self._handle_manual_captcha(self.driver):
                    document_urls = self._submit_and_get_links(self.driver)
                    
                    if document_urls:
                        docs_to_download = document_urls[:self.max_documents_to_download]
                        print(f"\n--- Starting Download of {len(docs_to_download)} Documents ---")
                        
                        for i, url in enumerate(docs_to_download, 1):
                            self._download_document(url, i, len(docs_to_download))
                            if i < len(docs_to_download):
                                print(f"⏳ Waiting for {self.delay_between_downloads} seconds...")
                                time.sleep(self.delay_between_downloads)

        finally:
            print("\n✅ Process finished.")
            self.driver.quit()
            print(f"📁 All files are saved in: {os.path.abspath(self.data_dir)}")


if __name__ == "__main__":
    try:
        scraper = FirefoxStableDirectScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ A critical error occurred: {e}")
        import traceback
        traceback.print_exc() 