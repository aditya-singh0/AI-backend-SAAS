#!/usr/bin/env python3
"""
HEADLESS BROWSER AUTOMATION WITH PDF DOWNLOADS
Enhanced version that tries more search parameters and downloads PDFs when found
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

try:
    import pytesseract
    TESSERACT_OK = True
    print("✅ Tesseract available")
except:
    TESSERACT_OK = False
    print("⚠️ Tesseract not available")

class HeadlessWithDownloads:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/headless_downloads"
        self.pdf_dir = "data/downloaded_pdfs"
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
        
        # Expanded search parameters - trying more combinations to find documents
        self.searches = [
            # Recent years with popular areas
            {"year_db": 3, "reg_year": 2024, "village": "Andheri", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2024, "village": "Bandra", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2024, "village": "Borivali", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2024, "village": "Malad", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2024, "village": "Powai", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2024, "village": "Goregaon", "taluka": "Mumbai"},
            
            # 2023 searches
            {"year_db": 3, "reg_year": 2023, "village": "Andheri", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2023, "village": "Bandra", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2023, "village": "Kandivali", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2023, "village": "Thane", "taluka": "Mumbai"},
            
            # 2022 searches
            {"year_db": 3, "reg_year": 2022, "village": "Andheri", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2022, "village": "Juhu", "taluka": "Mumbai"},
            {"year_db": 3, "reg_year": 2022, "village": "Versova", "taluka": "Mumbai"},
            
            # Older years with different database
            {"year_db": 2, "reg_year": 2021, "village": "Andheri", "taluka": "Mumbai"},
            {"year_db": 2, "reg_year": 2020, "village": "Bandra", "taluka": "Mumbai"},
            {"year_db": 2, "reg_year": 2019, "village": "Malad", "taluka": "Mumbai"},
        ]

    def start_headless_browser(self):
        """Start headless Firefox with download preferences"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(1)
            
            options = Options()
            
            # HEADLESS MODE
            options.add_argument('--headless')
            
            # Download preferences
            download_dir = os.path.abspath(self.pdf_dir)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.download.dir", download_dir)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf,application/octet-stream")
            options.set_preference("pdfjs.disabled", True)  # Disable PDF viewer
            
            # Performance optimizations
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Disable images for faster loading
            options.set_preference("permissions.default.image", 2)
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print("🤖 Headless Firefox with download support started")
            return True
            
        except Exception as e:
            print(f"❌ Headless browser failed: {e}")
            return False

    def download_captcha_headless(self):
        """Download CAPTCHA in headless mode"""
        try:
            print("📥 Downloading CAPTCHA (headless)...")
            
            # Load website
            self.driver.get(self.url)
            time.sleep(3)
            
            # Find CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            
            try:
                # Direct download
                response = requests.get(captcha_src, verify=False, timeout=10)
                if response.status_code == 200:
                    with open(captcha_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ CAPTCHA downloaded: {captcha_path}")
                else:
                    raise Exception(f"HTTP {response.status_code}")
            except:
                # Screenshot fallback
                captcha_screenshot = captcha_img.screenshot_as_png
                with open(captcha_path, 'wb') as f:
                    f.write(captcha_screenshot)
                print(f"✅ CAPTCHA screenshot: {captcha_path}")
            
            return captcha_path
            
        except Exception as e:
            print(f"❌ CAPTCHA download failed: {e}")
            return None

    def solve_captcha_automatically(self, captcha_path):
        """Solve CAPTCHA automatically using enhanced OCR methods"""
        try:
            print("🤖 Solving CAPTCHA automatically...")
            
            solutions = []
            
            # Method 1: EasyOCR
            if self.ocr:
                try:
                    results = self.ocr.readtext(captcha_path)
                    for result in results:
                        text = result[1].strip().upper()
                        confidence = result[2]
                        if len(text) >= 4 and len(text) <= 8 and confidence > 0.4:
                            clean_text = ''.join(c for c in text if c.isalnum())
                            if len(clean_text) >= 4:
                                solutions.append((clean_text, confidence, "EasyOCR"))
                                print(f"   🔍 EasyOCR: '{clean_text}' (confidence: {confidence:.2f})")
                except Exception as e:
                    print(f"   ⚠️ EasyOCR failed: {e}")
            
            # Method 2: Enhanced Tesseract
            if TESSERACT_OK:
                try:
                    import cv2
                    
                    img = cv2.imread(captcha_path)
                    if img is not None:
                        # Enhanced preprocessing
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        
                        # Multiple preprocessing approaches
                        preprocessed_images = []
                        
                        # Approach 1: Simple threshold
                        _, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                        preprocessed_images.append(thresh1)
                        
                        # Approach 2: OTSU threshold
                        _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        preprocessed_images.append(thresh2)
                        
                        # Approach 3: Gaussian blur + threshold
                        blur = cv2.GaussianBlur(gray, (3, 3), 0)
                        _, thresh3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        preprocessed_images.append(thresh3)
                        
                        # Try different Tesseract configs
                        configs = [
                            '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                            '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                            '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        ]
                        
                        for i, processed_img in enumerate(preprocessed_images):
                            for j, config in enumerate(configs):
                                try:
                                    text = pytesseract.image_to_string(processed_img, config=config).strip().upper()
                                    clean_text = ''.join(c for c in text if c.isalnum())
                                    if len(clean_text) >= 4 and len(clean_text) <= 8:
                                        solutions.append((clean_text, 0.6, f"Tesseract-{i+1}-{j+1}"))
                                        print(f"   🔍 Tesseract-{i+1}-{j+1}: '{clean_text}'")
                                except:
                                    continue
                                
                except Exception as e:
                    print(f"   ⚠️ Tesseract failed: {e}")
            
            # Choose best solution
            if solutions:
                # Sort by confidence
                solutions.sort(key=lambda x: x[1], reverse=True)
                best_solution = solutions[0]
                
                print(f"   🎯 Best solution: '{best_solution[0]}' from {best_solution[2]} (confidence: {best_solution[1]:.2f})")
                
                # Auto-select high confidence results
                if best_solution[1] > 0.75:
                    print(f"   ✅ Auto-selected high confidence result")
                    return best_solution[0]
                
                # If multiple solutions agree, use the common one
                texts = [sol[0] for sol in solutions]
                text_counts = {}
                for text in texts:
                    text_counts[text] = text_counts.get(text, 0) + 1
                
                # Find most common solution
                most_common = max(text_counts.items(), key=lambda x: x[1])
                if most_common[1] > 1:  # At least 2 methods agree
                    print(f"   ✅ Multiple methods agree on: '{most_common[0]}'")
                    return most_common[0]
                
                # Auto-select best if confidence is reasonable
                if best_solution[1] > 0.5:
                    print(f"   🎯 Auto-selecting best result: '{best_solution[0]}'")
                    return best_solution[0]
                
                # Use best guess
                print(f"   🤖 Using best guess: '{best_solution[0]}'")
                return best_solution[0]
            else:
                print("   ❌ No OCR solutions found")
                return None
            
        except Exception as e:
            print(f"❌ CAPTCHA solving failed: {e}")
            return None

    def fill_form_headless(self, year_db, reg_year, village, captcha_solution):
        """Fill form in headless mode"""
        try:
            print(f"📝 Filling form (headless): Mumbai {village} - {reg_year}")
            print(f"🔤 Using CAPTCHA: '{captcha_solution}'")
            
            # 1. Database selection
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            print(f"   ✅ Database: {year_db}")
            time.sleep(2)
            
            # 2. Mumbai district
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value("31")
            print("   ✅ District: Mumbai (31)")
            time.sleep(2)
            
            # 3. Mumbai taluka
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                print("   ✅ Taluka: Mumbai")
                time.sleep(2)
            
            # 4. Village selection - try to find exact match or use first available
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            
            village_found = False
            selected_village = ""
            
            # Try exact match first
            for option in village_options:
                option_text = option.text.lower()
                if village.lower() in option_text or option_text in village.lower():
                    village_select.select_by_value(option.get_attribute('value'))
                    village_found = True
                    selected_village = option.text
                    print(f"   ✅ Village: {selected_village}")
                    break
            
            # If no match, use first available village
            if not village_found and len(village_options) > 1:
                village_select.select_by_value(village_options[1].get_attribute('value'))
                selected_village = village_options[1].text
                print(f"   ✅ Village (fallback): {selected_village}")
            
            time.sleep(1)
            
            # 5. Agreement to Sale
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value("42")
            print("   ✅ Article: Agreement to Sale (42)")
            time.sleep(1)
            
            # 6. Registration year
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            print(f"   ✅ Registration Year: {reg_year}")
            
            # 7. CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            time.sleep(0.5)
            captcha_input.send_keys(captcha_solution)
            print(f"   ✅ CAPTCHA entered: '{captcha_solution}'")
            
            print("✅ Form filled successfully!")
            return True, selected_village
                
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False, ""

    def submit_and_check_for_downloads(self):
        """Submit form and check for downloadable documents"""
        try:
            print("🚀 Submitting form (headless)...")
            
            # Submit
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            print("   📤 Form submitted!")
            
            # Wait for results
            time.sleep(6)
            
            # Check results
            page_source = self.driver.page_source.lower()
            
            if any(error in page_source for error in ['invalid captcha', 'captcha error', 'wrong captcha']):
                print("   ❌ CAPTCHA was incorrect")
                return False, 0, []
            elif "no data available" in page_source:
                print("   ❌ No documents found")
                return False, 0, []
            elif "showing" in page_source and "entries" in page_source:
                print("   ✅ FOUND RESULTS!")
                
                # Look for download links
                download_links = []
                try:
                    # Find all rows in the results table
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    doc_count = 0
                    
                    for row in rows:
                        if row.get_attribute('innerHTML').strip():
                            doc_count += 1
                            
                            # Look for download links in this row
                            links = row.find_elements(By.CSS_SELECTOR, "a[href*='pdf'], a[href*='download'], a[href*='view']")
                            for link in links:
                                href = link.get_attribute('href')
                                if href and ('pdf' in href.lower() or 'download' in href.lower()):
                                    download_links.append({
                                        'url': href,
                                        'text': link.text.strip(),
                                        'row_data': row.text.strip()
                                    })
                    
                    if doc_count > 0:
                        print(f"   📊 Found {doc_count} documents!")
                        if download_links:
                            print(f"   🔗 Found {len(download_links)} download links!")
                        return True, doc_count, download_links
                    
                except Exception as e:
                    print(f"   ⚠️ Error parsing results: {e}")
                
                print("   ✅ Documents found (count unknown)")
                return True, 1, download_links
            else:
                print("   ⚠️ Unknown result")
                return False, 0, []
                
        except Exception as e:
            print(f"❌ Submit failed: {e}")
            return False, 0, []

    def download_pdfs(self, download_links, search_params):
        """Download PDF files from the results"""
        downloaded_files = []
        
        if not download_links:
            print("   ℹ️ No download links found")
            return downloaded_files
        
        print(f"📥 Downloading {len(download_links)} PDF files...")
        
        for i, link_info in enumerate(download_links, 1):
            try:
                url = link_info['url']
                print(f"   📄 Downloading PDF {i}/{len(download_links)}: {link_info['text']}")
                
                # Generate filename
                timestamp = datetime.now().strftime('%H%M%S')
                filename = f"agreement_{search_params['village']}_{search_params['reg_year']}_{i}_{timestamp}.pdf"
                filepath = os.path.join(self.pdf_dir, filename)
                
                # Download the PDF
                response = requests.get(url, verify=False, timeout=30)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = len(response.content)
                    print(f"   ✅ Downloaded: {filename} ({file_size} bytes)")
                    downloaded_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_size,
                        'url': url,
                        'row_data': link_info['row_data']
                    })
                else:
                    print(f"   ❌ Download failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Download error: {e}")
        
        return downloaded_files

    def save_debug_info(self, params, success=False, doc_count=0, downloads=None):
        """Save debug information"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            status = "SUCCESS" if success else "FAILED"
            download_count = len(downloads) if downloads else 0
            filename = f'{status}_{params["village"]}_{params["reg_year"]}_{doc_count}docs_{download_count}pdfs_{timestamp}.html'
            debug_file = os.path.join(self.data_dir, filename)
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Search: {params} -->\n")
                f.write(f"<!-- Documents: {doc_count} -->\n")
                f.write(f"<!-- Downloads: {download_count} -->\n")
                if downloads:
                    f.write(f"<!-- Downloaded Files: {[d['filename'] for d in downloads]} -->\n")
                f.write(self.driver.page_source)
            
            print(f"📄 Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")

    def run_enhanced_automation(self):
        """Run enhanced headless automation with PDF downloads"""
        print("🚀 HEADLESS BROWSER AUTOMATION WITH PDF DOWNLOADS")
        print("=" * 70)
        print("🤖 ENHANCED FEATURES:")
        print("   🔍 Headless browser - no visible windows")
        print("   📥 Automatic CAPTCHA download & solving")
        print("   📝 Automatic form filling with expanded search")
        print("   🔗 PDF download link detection")
        print("   📄 Automatic PDF downloads")
        print("   🚀 Fast execution")
        print("=" * 70)
        
        total_documents = 0
        total_downloads = 0
        successful_searches = []
        all_downloaded_files = []
        
        for i, params in enumerate(self.searches, 1):
            print(f"\n🚀 SEARCH {i}/{len(self.searches)}")
            print(f"🔄 Mumbai {params['village']} - Year {params['reg_year']}")
            
            try:
                # Start headless browser
                if not self.start_headless_browser():
                    print("❌ Failed to start headless browser")
                    continue
                
                # Download and solve CAPTCHA
                captcha_path = self.download_captcha_headless()
                if not captcha_path:
                    print("❌ CAPTCHA download failed")
                    continue
                
                captcha_solution = self.solve_captcha_automatically(captcha_path)
                if not captcha_solution:
                    print("❌ CAPTCHA solving failed")
                    continue
                
                # Fill form
                form_success, selected_village = self.fill_form_headless(params["year_db"], params["reg_year"], params["village"], captcha_solution)
                if not form_success:
                    print("❌ Form filling failed")
                    self.save_debug_info(params, False, 0)
                    continue
                
                # Submit and check for downloads
                found_docs, doc_count, download_links = self.submit_and_check_for_downloads()
                
                if found_docs:
                    print(f"🎉 SUCCESS! Found {doc_count} documents")
                    
                    # Download PDFs if available
                    downloaded_files = self.download_pdfs(download_links, params)
                    
                    search_result = {
                        **params, 
                        "doc_count": doc_count, 
                        "download_count": len(downloaded_files),
                        "selected_village": selected_village,
                        "downloaded_files": downloaded_files
                    }
                    successful_searches.append(search_result)
                    total_documents += doc_count
                    total_downloads += len(downloaded_files)
                    all_downloaded_files.extend(downloaded_files)
                    
                    self.save_debug_info(params, True, doc_count, downloaded_files)
                    
                    if downloaded_files:
                        print(f"📄 Downloaded {len(downloaded_files)} PDF files!")
                        # Ask if user wants to continue
                        continue_search = input(f"\n✅ Found {doc_count} documents and downloaded {len(downloaded_files)} PDFs! Continue? (y/n, default y): ").strip().lower()
                        if continue_search == 'n':
                            break
                    else:
                        print("ℹ️ No downloadable PDFs found in results")
                else:
                    print("❌ No documents found")
                    self.save_debug_info(params, False, 0)
                
                # Brief pause between searches
                if i < len(self.searches):
                    print("⏳ Waiting 3s before next search...")
                    time.sleep(3)
                
            except Exception as e:
                print(f"❌ Search {i} failed: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 ENHANCED AUTOMATION SUMMARY")
        print("=" * 70)
        
        if successful_searches:
            print(f"🎉 SUCCESS! Found documents in {len(successful_searches)} searches:")
            for result in successful_searches:
                print(f"   🏘️ {result['selected_village']} - Year {result['reg_year']} - {result['doc_count']} docs - {result['download_count']} PDFs")
            
            print(f"\n📊 TOTALS:")
            print(f"   📄 Documents Found: {total_documents}")
            print(f"   📥 PDFs Downloaded: {total_downloads}")
            
            if all_downloaded_files:
                print(f"\n📁 DOWNLOADED FILES:")
                for file_info in all_downloaded_files:
                    print(f"   📄 {file_info['filename']} ({file_info['size']} bytes)")
        else:
            print("❌ No documents found in any search")
        
        print(f"\n📁 All files saved in:")
        print(f"   🗂️ Debug files: {os.path.abspath(self.data_dir)}")
        print(f"   📄 PDF files: {os.path.abspath(self.pdf_dir)}")
        
        return successful_searches, all_downloaded_files

    def cleanup(self):
        """Clean up headless browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Headless browser closed")
        except:
            pass

def main():
    print("🚀 HEADLESS BROWSER AUTOMATION WITH PDF DOWNLOADS")
    print("📄 Enhanced version that finds and downloads Agreement to Sale PDFs!")
    print("🤖 Fast, automated, completely invisible!")
    
    automation = HeadlessWithDownloads()
    
    try:
        successful_results, downloaded_files = automation.run_enhanced_automation()
        
        if successful_results:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print(f"Found documents in {len(successful_results)} searches")
            if downloaded_files:
                print(f"Downloaded {len(downloaded_files)} PDF files!")
            else:
                print("No PDFs were available for download")
        else:
            print("\n😔 No documents found")
            
    except KeyboardInterrupt:
        print("\n👋 Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 