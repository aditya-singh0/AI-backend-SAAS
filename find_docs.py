#!/usr/bin/env python3
import time
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

try:
    import easyocr
    EASYOCR_OK = True
except:
    EASYOCR_OK = False

class DocumentFinder:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/document_finder"
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.ocr = None
        if EASYOCR_OK:
            self.ocr = easyocr.Reader(['en'])
        
        self.driver = None
        self.wait = None

    def start_browser(self):
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(1)
            
            options = Options()
            options.add_argument('--headless')
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("🤖 Browser started")
            return True
        except Exception as e:
            print(f"❌ Browser failed: {e}")
            return False

    def solve_captcha(self, captcha_path):
        try:
            if self.ocr:
                results = self.ocr.readtext(captcha_path)
                for result in results:
                    text = result[1].strip().upper()
                    confidence = result[2]
                    if len(text) >= 4 and confidence > 0.4:
                        clean_text = ''.join(c for c in text if c.isalnum())
                        if len(clean_text) >= 4:
                            return clean_text
            return None
        except:
            return None

    def search_documents(self, year_db, reg_year, village_idx=1):
        try:
            self.driver.get(self.url)
            time.sleep(3)
            
            # CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            response = requests.get(captcha_src, verify=False, timeout=10)
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
            
            captcha_solution = self.solve_captcha(captcha_path)
            if not captcha_solution:
                return False, "CAPTCHA failed", ""
            
            # Form filling
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
            
            if len(village_options) > village_idx:
                village_select.select_by_value(village_options[village_idx].get_attribute('value'))
                selected_village = village_options[village_idx].text
            
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            time.sleep(1)
            
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            
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
                # Found results!
                results_file = os.path.join(self.data_dir, f'FOUND_{selected_village}_{reg_year}_{timestamp}.html')
                with open(results_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    doc_count = len([row for row in rows if row.get_attribute('innerHTML').strip()])
                except:
                    doc_count = 1
                
                return True, f"Found {doc_count} documents", selected_village
            else:
                return False, "Unknown result", selected_village
                
        except Exception as e:
            return False, f"Error: {e}", ""

    def run_search(self):
        print("🚀 SEARCHING FOR DOCUMENTS WITH DOWNLOAD LINKS")
        print("=" * 50)
        
        found_docs = []
        
        # Try different combinations
        for year_db in [3, 2]:
            for reg_year in [2024, 2023, 2022, 2021]:
                for village_idx in [1, 2, 3]:
                    print(f"\n🔍 DB={year_db}, Year={reg_year}, Village={village_idx}")
                    
                    try:
                        if not self.start_browser():
                            continue
                        
                        success, result, village = self.search_documents(year_db, reg_year, village_idx)
                        
                        if success:
                            print(f"🎉 SUCCESS! {village} - {result}")
                            found_docs.append({
                                'year_db': year_db,
                                'reg_year': reg_year,
                                'village': village,
                                'result': result
                            })
                            
                            # Ask to continue
                            cont = input("Continue searching? (y/n, default n): ").strip().lower()
                            if cont != 'y':
                                return found_docs
                        else:
                            print(f"❌ {village} - {result}")
                        
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"❌ Search failed: {e}")
                        continue
        
        return found_docs

    def cleanup(self):
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

def main():
    finder = DocumentFinder()
    try:
        found = finder.run_search()
        if found:
            print(f"\n🎉 Found {len(found)} searches with documents!")
        else:
            print("\n😔 No documents found")
    except KeyboardInterrupt:
        print("\n👋 Stopped")
    finally:
        finder.cleanup()

if __name__ == "__main__":
    main() 