#!/usr/bin/env python3
"""
PDF DOWNLOADER FOR AGREEMENT TO SALE DOCUMENTS
Detects and downloads PDFs from the results table
"""

import time
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import urllib3
urllib3.disable_warnings()

# Try OCR
try:
    import easyocr
    EASYOCR_OK = True
    print("✅ EasyOCR available")
except:
    EASYOCR_OK = False
    print("⚠️ EasyOCR not available")

class PDFDownloader:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/pdf_downloads"
        self.pdf_dir = "data/agreement_pdfs"
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        
        # OCR setup
        self.ocr = None
        if EASYOCR_OK:
            try:
                self.ocr = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized")
            except:
                print("⚠️ EasyOCR init failed")
        
        self.driver = None
        self.wait = None

    def start_browser_with_downloads(self):
        """Start Firefox with download support"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(1)
            
            options = Options()
            options.add_argument('--headless')
            
            # Download preferences
            download_dir = os.path.abspath(self.pdf_dir)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.download.dir", download_dir)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("🤖 Firefox with PDF download support started")
            return True
            
        except Exception as e:
            print(f"❌ Browser failed: {e}")
            return False

    def solve_captcha_quick(self, captcha_path):
        """Quick CAPTCHA solving"""
        try:
            if self.ocr:
                results = self.ocr.readtext(captcha_path)
                for result in results:
                    text = result[1].strip().upper()
                    confidence = result[2]
                    if len(text) >= 4 and len(text) <= 8 and confidence > 0.4:
                        clean_text = ''.join(c for c in text if c.isalnum())
                        if len(clean_text) >= 4:
                            print(f"🔍 CAPTCHA: '{clean_text}' (confidence: {confidence:.2f})")
                            return clean_text
            return None
        except:
            return None

    def search_and_download(self, year_db, reg_year):
        """Search for documents and download PDFs"""
        try:
            print(f"🔍 Searching: Database {year_db}, Year {reg_year}")
            
            # Load website
            self.driver.get(self.url)
            time.sleep(3)
            
            # Download CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            response = requests.get(captcha_src, verify=False, timeout=10)
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
            
            # Solve CAPTCHA
            captcha_solution = self.solve_captcha_quick(captcha_path)
            if not captcha_solution:
                print("❌ CAPTCHA solving failed")
                return []
            
            # Fill form
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            time.sleep(2)
            
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value("31")
            time.sleep(2)
            
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                time.sleep(2)
            
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            selected_village = "Unknown"
            
            if len(village_options) > 1:
                village_select.select_by_value(village_options[1].get_attribute('value'))
                selected_village = village_options[1].text
            
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            time.sleep(1)
            
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_solution)
            
            print(f"✅ Form filled: {selected_village}, Year {reg_year}")
            
            # Submit
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            time.sleep(6)
            
            # Check for results
            page_source = self.driver.page_source.lower()
            
            if "no data available" in page_source:
                print("❌ No documents found")
                return []
            elif "showing" in page_source and "entries" in page_source:
                print("✅ Found results! Looking for download links...")
                
                # Save the results page for inspection
                debug_file = os.path.join(self.data_dir, f'results_{selected_village}_{reg_year}_{timestamp}.html')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"📄 Results page saved: {debug_file}")
                
                # Look for download links
                download_links = []
                
                # Check for various types of download links
                link_selectors = [
                    "a[href*='pdf']",
                    "a[href*='download']", 
                    "a[href*='view']",
                    "a[title*='download']",
                    "a[onclick*='download']",
                    "button[onclick*='download']",
                    "[onclick*='pdf']"
                ]
                
                for selector in link_selectors:
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for link in links:
                            href = link.get_attribute('href')
                            onclick = link.get_attribute('onclick')
                            text = link.text.strip()
                            
                            if href:
                                download_links.append({
                                    'url': href,
                                    'text': text,
                                    'type': 'href'
                                })
                            elif onclick:
                                download_links.append({
                                    'url': onclick,
                                    'text': text,
                                    'type': 'onclick'
                                })
                    except:
                        continue
                
                if download_links:
                    print(f"🔗 Found {len(download_links)} potential download links!")
                    
                    # Try to download each link
                    downloaded_files = []
                    for i, link_info in enumerate(download_links, 1):
                        try:
                            print(f"📄 Trying download {i}: {link_info['text'][:50]}...")
                            
                            if link_info['type'] == 'onclick':
                                # Execute onclick
                                self.driver.execute_script(link_info['url'])
                                time.sleep(3)
                                print(f"   ✅ Onclick executed")
                            else:
                                # Direct download
                                url = link_info['url']
                                if not url.startswith('http'):
                                    url = "https://pay2igr.igrmaharashtra.gov.in" + url
                                
                                filename = f"agreement_{reg_year}_{i}_{timestamp}.pdf"
                                filepath = os.path.join(self.pdf_dir, filename)
                                
                                response = requests.get(url, verify=False, timeout=30)
                                if response.status_code == 200:
                                    with open(filepath, 'wb') as f:
                                        f.write(response.content)
                                    
                                    file_size = len(response.content)
                                    print(f"   ✅ Downloaded: {filename} ({file_size} bytes)")
                                    downloaded_files.append(filename)
                                else:
                                    print(f"   ❌ Download failed: HTTP {response.status_code}")
                        except Exception as e:
                            print(f"   ❌ Download error: {e}")
                    
                    return downloaded_files
                else:
                    print("ℹ️ Results found but no download links detected")
                    return []
            else:
                print("⚠️ Unknown result")
                return []
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []

    def run_download_search(self):
        """Main function to search and download PDFs"""
        print("🚀 PDF DOWNLOADER FOR AGREEMENT TO SALE DOCUMENTS")
        print("=" * 60)
        
        # Try different year/database combinations
        searches = [
            (3, 2024),
            (3, 2023), 
            (2, 2022),
            (2, 2021)
        ]
        
        all_downloads = []
        
        for i, (year_db, reg_year) in enumerate(searches, 1):
            print(f"\n🚀 SEARCH {i}/{len(searches)}")
            
            try:
                if not self.start_browser_with_downloads():
                    continue
                
                downloaded_files = self.search_and_download(year_db, reg_year)
                
                if downloaded_files:
                    print(f"🎉 Downloaded {len(downloaded_files)} files!")
                    all_downloads.extend(downloaded_files)
                    
                    # Ask if user wants to continue
                    continue_search = input(f"\n✅ Downloaded {len(downloaded_files)} PDFs! Continue? (y/n, default y): ").strip().lower()
                    if continue_search == 'n':
                        break
                
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Search {i} failed: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        
        if all_downloads:
            print(f"🎉 SUCCESS! Downloaded {len(all_downloads)} PDF files:")
            for filename in all_downloads:
                print(f"   📄 {filename}")
            print(f"\n📁 Files saved in: {os.path.abspath(self.pdf_dir)}")
        else:
            print("😔 No PDF files were downloaded")
        
        return all_downloads

    def cleanup(self):
        """Clean up browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Browser closed")
        except:
            pass

def main():
    downloader = PDFDownloader()
    
    try:
        downloaded_files = downloader.run_download_search()
        
        if downloaded_files:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print(f"Downloaded {len(downloaded_files)} Agreement to Sale PDF files!")
        else:
            print("\n😔 No PDF files found")
            
    except KeyboardInterrupt:
        print("\n👋 Download stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        downloader.cleanup()

if __name__ == "__main__":
    main() 