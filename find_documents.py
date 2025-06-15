#!/usr/bin/env python3
"""
DOCUMENT FINDER - Enhanced Search for Agreement to Sale Documents
Tries many different search parameters to find actual documents with download links
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

class DocumentFinder:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/document_finder"
        self.pdf_dir = "data/found_pdfs"
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

    def start_headless_browser(self):
        """Start headless Firefox"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(1)
            
            options = Options()
            options.add_argument('--headless')
            
            # Download preferences
            download_dir = os.path.abspath(self.pdf_dir)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_dir)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)
            
            # Performance optimizations
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("🤖 Headless Firefox started")
            return True
            
        except Exception as e:
            print(f"❌ Browser failed: {e}")
            return False

    def solve_captcha_fast(self, captcha_path):
        """Fast CAPTCHA solving"""
        try:
            if self.ocr:
                results = self.ocr.readtext(captcha_path)
                for result in results:
                    text = result[1].strip().upper()
                    confidence = result[2]
                    if len(text) >= 4 and len(text) <= 8 and confidence > 0.4:
                        clean_text = ''.join(c for c in text if c.isalnum())
                        if len(clean_text) >= 4:
                            return clean_text
            return None
        except:
            return None

    def try_search_combination(self, year_db, reg_year, village_index=None):
        """Try a specific search combination"""
        try:
            # Load website
            self.driver.get(self.url)
            time.sleep(3)
            
            # Download and solve CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            response = requests.get(captcha_src, verify=False, timeout=10)
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
            
            captcha_solution = self.solve_captcha_fast(captcha_path)
            if not captcha_solution:
                return False, "CAPTCHA failed", ""
            
            # Fill form
            # 1. Database
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            time.sleep(2)
            
            # 2. District (Mumbai)
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value("31")
            time.sleep(2)
            
            # 3. Taluka
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                time.sleep(2)
            
            # 4. Village - try different villages
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            selected_village = "Unknown"
            
            if len(village_options) > 1:
                if village_index is None:
                    # Try first available village
                    village_select.select_by_value(village_options[1].get_attribute('value'))
                    selected_village = village_options[1].text
                else:
                    # Try specific village index
                    if village_index < len(village_options):
                        village_select.select_by_value(village_options[village_index].get_attribute('value'))
                        selected_village = village_options[village_index].text
            
            time.sleep(1)
            
            # 5. Agreement to Sale
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            time.sleep(1)
            
            # 6. Registration year
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            
            # 7. CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_solution)
            
            # Submit
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            time.sleep(6)
            
            # Check results
            page_source = self.driver.page_source.lower()
            
            if "no data available" in page_source:
                return False, "No data", selected_village
            elif "showing" in page_source and "entries" in page_source:
                # Found results! Save the page and look for download links
                results_file = os.path.join(self.data_dir, f'FOUND_RESULTS_{selected_village}_{reg_year}_{timestamp}.html')
                with open(results_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                
                # Count documents
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    doc_count = len([row for row in rows if row.get_attribute('innerHTML').strip()])
                except:
                    doc_count = 1
                
                # Look for download links
                download_links = []
                link_selectors = [
                    "a[href*='pdf']", "a[href*='download']", "a[href*='view']",
                    "a[title*='download']", "a[onclick*='download']", 
                    "button[onclick*='download']", "[onclick*='pdf']"
                ]
                
                for selector in link_selectors:
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for link in links:
                            href = link.get_attribute('href')
                            onclick = link.get_attribute('onclick')
                            text = link.text.strip()
                            
                            if href or onclick:
                                download_links.append({
                                    'url': href or onclick,
                                    'text': text,
                                    'type': 'href' if href else 'onclick'
                                })
                    except:
                        continue
                
                return True, f"Found {doc_count} docs, {len(download_links)} links", selected_village
            else:
                return False, "Unknown result", selected_village
                
        except Exception as e:
            return False, f"Error: {e}", ""

    def comprehensive_search(self):
        """Comprehensive search across multiple parameters"""
        print("🚀 COMPREHENSIVE DOCUMENT SEARCH")
        print("=" * 60)
        print("🔍 Trying multiple combinations to find actual documents...")
        print("=" * 60)
        
        # Search parameters to try
        year_databases = [3, 2, 1]  # Different database years
        registration_years = [2024, 2023, 2022, 2021, 2020, 2019]  # Different years
        village_indices = [1, 2, 3, 4, 5]  # Try first 5 villages
        
        found_documents = []
        search_count = 0
        
        for year_db in year_databases:
            for reg_year in registration_years:
                for village_idx in village_indices:
                    search_count += 1
                    
                    print(f"\n🔍 SEARCH {search_count}: DB={year_db}, Year={reg_year}, Village={village_idx}")
                    
                    try:
                        if not self.start_headless_browser():
                            continue
                        
                        success, result, village_name = self.try_search_combination(year_db, reg_year, village_idx)
                        
                        if success:
                            print(f"🎉 SUCCESS! {village_name} - {result}")
                            found_documents.append({
                                'year_db': year_db,
                                'reg_year': reg_year,
                                'village_idx': village_idx,
                                'village_name': village_name,
                                'result': result
                            })
                            
                            # Ask if user wants to continue searching
                            continue_search = input(f"\n✅ Found documents! Continue searching for more? (y/n, default n): ").strip().lower()
                            if continue_search != 'y':
                                break
                        else:
                            print(f"❌ {village_name} - {result}")
                        
                        # Brief pause
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"❌ Search failed: {e}")
                        continue
                
                # Break out of nested loops if user chose to stop
                if found_documents and continue_search != 'y':
                    break
            
            if found_documents and continue_search != 'y':
                break
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE SEARCH RESULTS")
        print("=" * 60)
        
        if found_documents:
            print(f"🎉 SUCCESS! Found documents in {len(found_documents)} searches:")
            for doc in found_documents:
                print(f"   📄 DB{doc['year_db']} - {doc['village_name']} - Year {doc['reg_year']} - {doc['result']}")
            
            print(f"\n📁 Result files saved in: {os.path.abspath(self.data_dir)}")
            print("🔍 Check the FOUND_RESULTS_*.html files for download links!")
        else:
            print("😔 No documents found in any search combination")
            print("💡 Try different search parameters or check if the website has data")
        
        return found_documents

    def cleanup(self):
        """Clean up browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Browser closed")
        except:
            pass

def main():
    print("🚀 COMPREHENSIVE DOCUMENT FINDER")
    print("🔍 Searching for Agreement to Sale documents with download links!")
    
    finder = DocumentFinder()
    
    try:
        found_documents = finder.comprehensive_search()
        
        if found_documents:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print(f"Found {len(found_documents)} searches with actual documents!")
            print("📄 Check the saved HTML files for download links!")
        else:
            print("\n😔 No documents found in comprehensive search")
            
    except KeyboardInterrupt:
        print("\n👋 Search stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        finder.cleanup()

if __name__ == "__main__":
    main() 