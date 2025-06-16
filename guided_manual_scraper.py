#!/usr/bin/env python3
"""
Final Guided Manual Scraper

This script uses a fully manual, guided approach to bypass all browser
instability issues. The user performs the form filling and search, and
the script then takes over to automate the downloads.

-   **Step 1 (Manual):** The script opens Firefox.
-   **Step 2 (Manual):** The user fills the form and CAPTCHA.
-   **Step 3 (Manual):** The user clicks 'Search'.
-   **Step 4 (Automated):** The script extracts all links from the
    results page and downloads the documents.
"""

import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class GuidedManualScraper:
    def __init__(self):
        """Initializes the guided manual scraper."""
        self.max_documents_to_download = 25
        self.delay_between_downloads = 4
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data", "guided_manual_run")
        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.meta_dir = os.path.join(self.data_dir, "metadata")
        
        for directory in [self.docs_dir, self.meta_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 GUIDED MANUAL SCRAPER (MOST STABLE)")
        print("=" * 60)
        print("✅ You perform the form fill and search.")
        print("✅ The script automates the downloads.")
        print("=" * 60)

    def _create_firefox_driver(self):
        """Creates a standard Firefox WebDriver instance."""
        options = FirefoxOptions()
        options.add_argument("--window-size=1280,800")
        try:
            driver = webdriver.Firefox(options=options)
            return driver
        except Exception as e:
            print(f"❌ Failed to create Firefox driver: {e}")
            return None

    def _get_links_from_user_search(self, driver):
        """Waits for the user to search and then extracts links."""
        try:
            print("\n--- WAITING FOR YOUR SEARCH RESULTS ---")
            print("After you click 'Search', the script will detect the results.")
            
            # Wait for the results table to appear (long timeout)
            WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, "tbl")))
            
            print("✅ Search results detected!")
            time.sleep(2) # Allow page to settle
            
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'propertydetails/indexii')]")
            if not links:
                print("❌ No document links found on the page.")
                return []

            urls = [link.get_attribute("href") for link in links]
            print(f"📄 Found {len(urls)} document links to download.")
            return urls
        except TimeoutException:
            print("❌ Timed out waiting for search results. Please try running the script again.")
            return []
        except Exception as e:
            print(f"❌ Error extracting links: {e}")
            return []

    def _download_document(self, url, index, total):
        """Downloads a single document in a new tab."""
        print(f"\n--- Downloading Document {index}/{total} ---")
        # Use a new tab to avoid disturbing the results page
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self._save_document_content(index, url, self.driver.page_source)
        except Exception as e:
            print(f"❌ Error downloading document {index}: {e}")
        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def _save_document_content(self, index, url, content):
        """Saves the document content and metadata."""
        if len(content) < 1000:
            print("⚠️ Downloaded content is too small.")
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_base = f"Manual_Search_Doc_{index:03d}_{timestamp}"
        
        html_path = os.path.join(self.docs_dir, f"{filename_base}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        meta_path = os.path.join(self.meta_dir, f"{filename_base}_meta.json")
        metadata = { "document_index": index, "source_url": url, "download_timestamp": datetime.now().isoformat() }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"✅ Document {index} saved successfully.")

    def run(self):
        """Executes the guided manual process."""
        self.driver = self._create_firefox_driver()
        if not self.driver:
            return

        try:
            self.driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            
            print("\n--- MANUAL ACTION REQUIRED ---")
            print("="*40)
            print("A Firefox window has been opened. Please follow these steps:")
            print("\n1.  **Select Database:** Choose the most recent year's database (e.g., 'e-Registration')")
            print("2.  **Select District:** Choose 'मुंबई शहर' (Mumbai City) or 'मुंबई उपनगर' (Mumbai Suburban)")
            print("3.  **Select Taluka:** Choose a sub-district (e.g., 'Andheri')")
            print("4.  **Select Village:** Choose a village")
            print("5.  **Select Year:** Choose '2024'")
            print("6.  **Select Article:** Choose the article for 'Agreement to Sale' (usually contains 'विकसन करार' or similar)")
            print("7.  **Enter CAPTCHA:** Type the characters from the image into the box.")
            print("\n8.  **CLICK THE 'SEARCH' BUTTON**")
            print("\nIMPORTANT: The script will automatically continue after you click search.")
            print("="*40)

            document_urls = self._get_links_from_user_search(self.driver)
            
            if document_urls:
                docs_to_download = document_urls[:self.max_documents_to_download]
                print(f"\n--- Starting Automated Download of {len(docs_to_download)} Documents ---")
                
                for i, url in enumerate(docs_to_download, 1):
                    self._download_document(url, i, len(docs_to_download))
                    if i < len(docs_to_download):
                        print(f"⏳ Waiting for {self.delay_between_downloads} seconds...")
                        time.sleep(self.delay_between_downloads)

        finally:
            print("\n--- PROCESS FINISHED ---")
            self.driver.quit()
            print("✅ Firefox browser closed.")
            print(f"📁 All downloaded files are saved in: {os.path.abspath(self.data_dir)}")


if __name__ == "__main__":
    try:
        scraper = GuidedManualScraper()
        scraper.run()
    except KeyboardInterrupt:
        print("\n\n👋 Process interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ A critical error occurred: {e}")
        import traceback
        traceback.print_exc() 