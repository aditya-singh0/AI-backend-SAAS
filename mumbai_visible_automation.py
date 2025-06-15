#!/usr/bin/env python3
"""
Mumbai Visible IGR Automation
Fixed: District=Mumbai, Taluka=Mumbai, Article=Agreement to Sale
Variable: Year, Village, Registration Year
VISIBLE BROWSER - You can see what's happening!
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import requests
import os
from datetime import datetime
import urllib3
urllib3.disable_warnings()

# Try to import EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

class MumbaiVisibleAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/mumbai_visible"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize OCR if available
        if EASYOCR_AVAILABLE:
            try:
                self.ocr_reader = easyocr.Reader(['en'])
                print("✅ EasyOCR initialized")
            except:
                self.ocr_reader = None
                print("⚠️ EasyOCR failed to initialize")
        else:
            self.ocr_reader = None
            print("⚠️ EasyOCR not available")
        
        self.driver = None
        self.wait = None
        
        # FIXED PARAMETERS
        self.DISTRICT_ID = "31"  # Mumbai
        self.DISTRICT_NAME = "Mumbai"
        self.ARTICLE_ID = "42"   # Agreement to Sale
        self.ARTICLE_NAME = "Agreement to Sale"
        
        # Search combinations
        self.year_combinations = [
            {"year_db": 3, "reg_year": 2025},  # Recent years
            {"year_db": 3, "reg_year": 2024},
            {"year_db": 3, "reg_year": 2023},
            {"year_db": 2, "reg_year": 2022},  # Historical years
            {"year_db": 2, "reg_year": 2021},
        ]
        
        self.mumbai_villages = [
            {"value": "1", "name": "Andheri"},
            {"value": "2", "name": "Bandra"},
            {"value": "3", "name": "Borivali"},
            {"value": "4", "name": "Malad"},
            {"value": "5", "name": "Kandivali"},
        ]

    def setup_visible_driver(self):
        """Setup Firefox driver - VISIBLE BROWSER"""
        try:
            options = Options()
            
            # VISIBLE BROWSER - No headless mode
            # options.add_argument('--headless')  # COMMENTED OUT
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            
            # Window size
            options.add_argument('--width=1200')
            options.add_argument('--height=800')
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("🦊 Firefox browser opened - YOU CAN SEE IT!")
            return True
            
        except Exception as e:
            print(f"❌ Driver setup failed: {e}")
            return False

    def solve_captcha_manual(self):
        """Manual CAPTCHA solving with user input"""
        try:
            print("\n🤖 CAPTCHA DETECTED!")
            print("👀 Look at the browser window and see the CAPTCHA image")
            
            # Wait for user to see the CAPTCHA
            time.sleep(2)
            
            # Get CAPTCHA solution from user
            captcha_solution = input("🔤 Please enter the CAPTCHA text you see: ").strip()
            
            if captcha_solution:
                print(f"✅ You entered: '{captcha_solution}'")
                return captcha_solution
            else:
                print("❌ No CAPTCHA entered")
                return None
                
        except Exception as e:
            print(f"❌ CAPTCHA handling failed: {e}")
            return None

    def solve_captcha_auto(self):
        """Automatic CAPTCHA solving with EasyOCR"""
        try:
            # Find CAPTCHA image
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.ID, "captcha-img"))
            )
            
            # Get CAPTCHA image source
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA image
            response = requests.get(captcha_src, verify=False, timeout=10)
            
            # Save CAPTCHA image
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
            
            print(f"   📷 CAPTCHA downloaded: {captcha_path}")
            
            # Solve with EasyOCR if available
            if self.ocr_reader:
                results = self.ocr_reader.readtext(captcha_path)
                
                if results:
                    captcha_text = results[0][1].strip()
                    confidence = results[0][2]
                    print(f"   🔍 EasyOCR solved: '{captcha_text}' (confidence: {confidence:.2f})")
                    return captcha_text
            
            # Fallback pattern
            fallback = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
            print(f"   🔍 Pattern guess: '{fallback}'")
            return fallback
                
        except Exception as e:
            print(f"   ❌ Auto CAPTCHA solving failed: {e}")
            return None

    def fill_form(self, year_db, village_info, reg_year):
        """Fill the search form with Mumbai-specific parameters"""
        try:
            print(f"\n🤖 FILLING FORM: Mumbai {village_info['name']} - Year {reg_year}")
            print("👀 Watch the browser window to see the form being filled!")
            
            # Select database (year)
            print("   📅 Selecting database...")
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            print(f"   ✅ Database: {year_db}")
            time.sleep(2)
            
            # Select Mumbai district (FIXED)
            print("   📍 Selecting Mumbai district...")
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value(self.DISTRICT_ID)
            print(f"   ✅ District: Mumbai ({self.DISTRICT_ID})")
            time.sleep(3)
            
            # Select Mumbai taluka (FIXED - first available)
            print("   🏘️ Selecting Mumbai taluka...")
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                print(f"   ✅ Taluka: Mumbai")
                time.sleep(3)
            
            # Select specific village (VARIABLE)
            print(f"   🏘️ Selecting village: {village_info['name']}...")
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_select.select_by_value(village_info['value'])
            print(f"   ✅ Village: {village_info['name']}")
            time.sleep(2)
            
            # Select Agreement to Sale (FIXED)
            print("   📄 Selecting Agreement to Sale...")
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value(self.ARTICLE_ID)
            print(f"   ✅ Article: Agreement to Sale ({self.ARTICLE_ID})")
            time.sleep(2)
            
            # Add registration year (VARIABLE - same as selected year)
            print(f"   📝 Entering registration year: {reg_year}...")
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            print(f"   ✅ Registration Year: {reg_year}")
            
            print("✅ FORM FILLED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            print(f"   ❌ Form filling failed: {e}")
            return False

    def submit_form(self):
        """Solve CAPTCHA and submit form"""
        try:
            print("\n🤖 SUBMITTING FORM...")
            print("👀 Look at the browser window!")
            
            # Ask user for CAPTCHA preference
            print("\nCAPTCHA Options:")
            print("1. Manual (you enter CAPTCHA)")
            print("2. Automatic (EasyOCR)")
            choice = input("Choose option (1 or 2, default 1): ").strip() or "1"
            
            if choice == "1":
                captcha_solution = self.solve_captcha_manual()
            else:
                captcha_solution = self.solve_captcha_auto()
            
            if not captcha_solution:
                print("❌ No CAPTCHA solution available")
                return False
            
            # Enter CAPTCHA
            print(f"   📝 Entering CAPTCHA: '{captcha_solution}'...")
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_solution)
            print(f"   ✅ CAPTCHA entered: '{captcha_solution}'")
            
            # Submit form
            print("   📤 Clicking submit button...")
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            print("   📤 Form submitted!")
            
            # Wait for results to load
            print("   ⏳ Waiting for results...")
            time.sleep(8)
            return True
            
        except Exception as e:
            print(f"   ❌ Form submission failed: {e}")
            return False

    def check_results(self):
        """Check if any documents were found"""
        try:
            print("\n🔍 CHECKING RESULTS...")
            print("👀 Look at the browser window to see the results!")
            
            time.sleep(3)
            page_source = self.driver.page_source
            
            if "No data available in table" in page_source:
                print("❌ No documents found")
                return False
            elif "Showing" in page_source and "entries" in page_source:
                print("✅ DOCUMENTS FOUND!")
                print("🎉 SUCCESS! Check the browser window to see the documents!")
                return True
            else:
                print("⚠️ Results unclear - check browser window")
                return False
                
        except Exception as e:
            print(f"❌ Results check failed: {e}")
            return False

    def save_debug_info(self, village_info, reg_year, success=False):
        """Save debug information"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            status = "SUCCESS" if success else "FAILED"
            debug_file = os.path.join(self.data_dir, f'{status}_{village_info["name"]}_{reg_year}_{timestamp}.html')
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"📄 Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")

    def process_search_combination(self, year_db, village_info, reg_year):
        """Process a single Mumbai search combination"""
        try:
            print(f"\n{'='*60}")
            print(f"🔍 TRYING: Mumbai {village_info['name']} - Year {reg_year}")
            print(f"{'='*60}")
            
            # Load the website
            print("🌐 Loading IGR website...")
            self.driver.get(self.base_url)
            time.sleep(5)
            
            # Fill form
            if not self.fill_form(year_db, village_info, reg_year):
                return False
            
            # Submit form
            if not self.submit_form():
                return False
            
            # Check results
            found_documents = self.check_results()
            
            # Save debug info
            self.save_debug_info(village_info, reg_year, found_documents)
            
            if found_documents:
                print(f"\n🎉 SUCCESS! Found documents for Mumbai {village_info['name']} - {reg_year}")
                print("🔥 Check the browser window to see the documents!")
                
                # Ask user if they want to continue
                continue_search = input("\nContinue searching for more documents? (y/n, default n): ").strip().lower()
                if continue_search != 'y':
                    return {
                        "village": village_info['name'],
                        "year": reg_year,
                        "year_db": year_db,
                        "stop_search": True
                    }
                
                return {
                    "village": village_info['name'],
                    "year": reg_year,
                    "year_db": year_db,
                    "stop_search": False
                }
            
            return False
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def run_mumbai_search(self):
        """Run Mumbai-focused visible search"""
        print("🚀 MUMBAI VISIBLE IGR AUTOMATION")
        print("=" * 60)
        print("🏙️ FIXED PARAMETERS:")
        print("   📍 District: Mumbai (31)")
        print("   🏘️ Taluka: Mumbai")
        print("   📄 Article: Agreement to Sale (42)")
        print("\n🔄 VARIABLE PARAMETERS:")
        print("   📅 Years: 2021-2025")
        print("   🏘️ Villages: Andheri, Bandra, Borivali, Malad, Kandivali")
        print("   📝 Registration Year = Selected Year")
        print("\n👀 VISIBLE BROWSER - You can see everything happening!")
        print("=" * 60)
        
        # Setup visible driver
        if not self.setup_visible_driver():
            print("❌ Failed to setup browser")
            return []
        
        successful_results = []
        total_combinations = len(self.year_combinations) * len(self.mumbai_villages)
        current_combination = 0
        
        try:
            # Try all combinations
            for year_combo in self.year_combinations:
                for village in self.mumbai_villages:
                    current_combination += 1
                    print(f"\n🚀 ATTEMPT {current_combination}/{total_combinations}")
                    
                    result = self.process_search_combination(
                        year_combo["year_db"], 
                        village, 
                        year_combo["reg_year"]
                    )
                    
                    if result:
                        successful_results.append(result)
                        if result.get("stop_search"):
                            print("🛑 Search stopped by user")
                            break
                    else:
                        print("❌ No documents found, trying next combination...")
                    
                    # Wait between attempts
                    if current_combination < total_combinations:
                        wait_time = 3
                        print(f"⏳ Waiting {wait_time}s before next attempt...")
                        time.sleep(wait_time)
                
                if result and result.get("stop_search"):
                    break
        
        except KeyboardInterrupt:
            print("\n👋 Search interrupted by user")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MUMBAI SEARCH SUMMARY")
        print("=" * 60)
        
        if successful_results:
            print(f"🎉 SUCCESS! Found Mumbai Agreement to Sale documents in {len(successful_results)} combinations:")
            for result in successful_results:
                print(f"   🏘️ Mumbai {result['village']} - Year {result['year']}")
        else:
            print("❌ No Mumbai Agreement to Sale documents found")
        
        print(f"\n📁 Debug files saved in: {os.path.abspath(self.data_dir)}")
        
        return successful_results

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                input("\nPress Enter to close the browser...")
                self.driver.quit()
                print("🧹 Browser closed")
        except:
            pass

def main():
    print("🚀 MUMBAI VISIBLE IGR AUTOMATION")
    print("👀 This will open a VISIBLE browser window!")
    print("🔍 You can see everything happening in real-time")
    
    automation = MumbaiVisibleAutomation()
    
    try:
        successful_results = automation.run_mumbai_search()
        
        if successful_results:
            print(f"\n🎉 MUMBAI MISSION ACCOMPLISHED! Found {len(successful_results)} working combinations")
        else:
            print("\n😔 No Mumbai Agreement to Sale documents found")
            
    except KeyboardInterrupt:
        print("\n\n👋 Mumbai search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 