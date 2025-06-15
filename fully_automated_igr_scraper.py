#!/usr/bin/env python3
"""
Fully Automated IGR Scraper
Automates everything: form filling, CAPTCHA solving, and document downloading.
"""

import os
import time
import json
import io
import cv2
import pytesseract
import numpy as np
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import sys

# Explicitly set the Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class FullyAutomatedIGRScraper:
    def __init__(self, max_docs=10):
        self.max_documents = max_docs
        self.data_dir = 'data'
        self.documents_dir = os.path.join(self.data_dir, 'fully_automated_results')
        self.metadata_dir = os.path.join(self.data_dir, 'fully_automated_metadata')
        self.captcha_dir = os.path.join(self.data_dir, 'automated_captchas')
        
        # Create all directories
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.captcha_dir, exist_ok=True)
        
        self.download_count = 0
        
        print("🤖 Fully Automated IGR Scraper")
        print("=" * 60)
        print("This will automate:")
        print("✅ 1. Form Filling (Mumbai, 2024, Agreement to Sale)")
        print("✅ 2. CAPTCHA Solving (using OCR)")
        print("✅ 3. Document Downloading")
        print(f"📁 Documents will be saved to: {os.path.abspath(self.documents_dir)}")
        print("=" * 60)

        # Verify Tesseract installation early - this is now more of a confirmation
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR found and ready.")
        except Exception as e:
            print("\n" + "="*60)
            print("❌ CRITICAL: Tesseract OCR is not installed or not in your system's PATH.")
            print("Please install it from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("Then, make sure the installation directory is in your PATH environment variable.")
            print("="*60)
            sys.exit(1) # Exit if Tesseract is not found

    def setup_driver(self):
        """Setup headless Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--ignore-certificate-errors")
        try:
            print("🚀 Setting up Chrome WebDriver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ WebDriver setup complete.")
            return driver
        except Exception as e:
            print("\n" + "="*60)
            print("❌ CRITICAL: Failed to setup Chrome WebDriver.")
            print("This might be due to a disconnected network or a firewall.")
            print(f"Error details: {e}")
            print("="*60)
            sys.exit(1)

    def preprocess_captcha(self, image_path):
        """Advanced preprocessing of the CAPTCHA image for better OCR."""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Invert the image
            inverted = cv2.bitwise_not(thresh)
            
            # Morphological operations to remove noise
            kernel = np.ones((1,1), np.uint8)
            opening = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)
            
            processed_path = image_path.replace('.png', '_processed.png')
            cv2.imwrite(processed_path, opening)
            return processed_path
        except Exception as e:
            print(f"⚠️  CAPTCHA preprocessing failed: {e}")
            return image_path

    def solve_captcha(self, driver):
        """Screenshots, preprocesses, and solves the CAPTCHA using Tesseract OCR."""
        try:
            # Find the CAPTCHA image element
            captcha_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'captcha')]"))
            )
            
            # Take a screenshot of the CAPTCHA element
            screenshot_bytes = captcha_element.screenshot_as_png
            
            # Save the CAPTCHA image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            img_path = os.path.join(self.captcha_dir, f'captcha_{timestamp}.png')
            with open(img_path, 'wb') as f:
                f.write(screenshot_bytes)

            # Preprocess for better accuracy
            processed_img_path = self.preprocess_captcha(img_path)

            # Use Tesseract to do OCR on the image
            image = Image.open(processed_img_path)
            
            # Try different OCR configurations
            configs = [
                '--psm 7 -c tessedit_char_whitelist=0123456789', # psm 7: Treat the image as a single text line.
                '--psm 8 -c tessedit_char_whitelist=0123456789', # psm 8: Treat the image as a single word.
                '--psm 13 -c tessedit_char_whitelist=0123456789'# psm 13: Raw line.
            ]

            for config in configs:
                captcha_text = pytesseract.image_to_string(image, config=config).strip()
                if captcha_text and len(captcha_text) >= 4 and captcha_text.isdigit(): # IGR Captchas are usually digits
                    print(f"🤖 OCR Result: '{captcha_text}' (using config: {config})")
                    return captcha_text

            print("❌ OCR failed to get a valid CAPTCHA.")
            return None

        except Exception as e:
            print(f"❌ Error during CAPTCHA solving: {e}")
            return None
            
    def run(self):
        """Executes the entire automated scraping process."""
        driver = self.setup_driver()
        try:
            # 1. Navigate to the page
            print("🌐 Navigating to IGR Website...")
            driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dbselect")))

            # 2. Fill the form
            print("📝 Filling out the search form...")
            Select(driver.find_element(By.ID, "dbselect")).select_by_value("3")
            time.sleep(1)
            Select(driver.find_element(By.ID, "district_id")).select_by_value("1") # Mumbai City
            time.sleep(1)
            Select(driver.find_element(By.ID, "article_id")).select_by_value("43") # Agreement to Sale
            
            # Add explicit wait for the 'year' dropdown to be clickable
            year_dropdown = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='year']"))
            )
            Select(year_dropdown).select_by_visible_text("2024")
            
            print("✅ Form filled.")

            # 3. Solve CAPTCHA and submit
            for attempt in range(5): # Try to solve and submit 5 times
                print(f"\n🔄 CAPTCHA Attempt {attempt + 1}...")
                captcha_solution = self.solve_captcha(driver)
                
                if captcha_solution:
                    # Input the solution
                    driver.find_element(By.ID, "txtcaptcha").send_keys(captcha_solution)
                    time.sleep(1)
                    # Submit
                    driver.find_element(By.ID, "search").click()
                    print("📤 Form submitted with CAPTCHA.")
                    time.sleep(5) # Wait for results page

                    # Check if submission was successful by looking for results table
                    if "No Record Found" not in driver.page_source and "tbl" in driver.page_source:
                        print("✅ Submission successful! Found search results.")
                        break
                    else:
                        print("⚠️ Submission failed or no records found. Retrying CAPTCHA...")
                        driver.find_element(By.ID, "txtcaptcha").clear()
                        # Refresh CAPTCHA if possible
                        try:
                            driver.find_element(By.ID, "newcaptcha").click()
                            time.sleep(1)
                        except:
                            pass
                else:
                    print("⚠️ Could not solve CAPTCHA. Refreshing and retrying...")
                    driver.refresh()
                    time.sleep(2)
            else:
                print("❌ Failed to solve CAPTCHA after multiple attempts. Exiting.")
                return

            # 4. Extract document links from results page
            print("\n🔍 Extracting document links from search results...")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = soup.select("table a[href*='indexii']")
            documents_to_download = []
            for link in links:
                full_url = f"https://pay2igr.igrmaharashtra.gov.in{link['href']}"
                documents_to_download.append(full_url)
            
            if not documents_to_download:
                print("❌ No document links found on the results page.")
                return

            print(f"📄 Found {len(documents_to_download)} documents to download.")

            # 5. Download the documents
            for i, url in enumerate(documents_to_download):
                if i >= self.max_documents:
                    print(f"\nReached max limit of {self.max_documents} documents.")
                    break
                
                print(f"\n📥 Downloading document {i+1}/{len(documents_to_download)}...")
                doc_driver = self.setup_driver()
                try:
                    doc_driver.get(url)
                    time.sleep(2)
                    content = doc_driver.page_source
                    
                    if len(content) < 1000:
                        print("⚠️  Downloaded content is too small, likely an error page.")
                        continue

                    # Save files
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"AutomatedDoc_{i+1:03d}_{timestamp}"
                    html_path = os.path.join(self.documents_dir, f"{filename}.html")
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Saved HTML: {html_path}")
                    
                    self.download_count += 1
                except Exception as e:
                    print(f"❌ Failed to download {url}: {e}")
                finally:
                    doc_driver.quit()

        finally:
            print("\nCleaning up and closing main driver.")
            driver.quit()

if __name__ == '__main__':
    try:
        # Hardcode document count for full automation
        docs_to_get = 25 
        print(f"🚀 Starting full automation to download {docs_to_get} documents...")
        scraper = FullyAutomatedIGRScraper(max_docs=docs_to_get)
        scraper.run()
        print("\n" + "=" * 60)
        print(f"🎉 Automation Complete! Downloaded {scraper.download_count} documents.")
        print("=" * 60)
    except ImportError:
        print("\n❌ Missing Dependencies!")
        print("Please install required packages: pip install selenium webdriver-manager opencv-python pytesseract pillow beautifulsoup4")
    except Exception as e:
        if "tesseract is not installed" in str(e).lower():
            print("\n❌ Tesseract OCR is not installed or not in your PATH!")
            print("Please install it from: https://github.com/UB-Mannheim/tesseract/wiki")
        else:
            print(f"\nAn unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()