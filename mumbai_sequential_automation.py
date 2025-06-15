#!/usr/bin/env python3
"""
Mumbai Sequential IGR Automation with IP Switching
Fixed: District=Mumbai, Taluka=Mumbai, Article=Agreement to Sale
Variable: Year, Village, Registration Year
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
import easyocr
import urllib3
urllib3.disable_warnings()

# Proxy configuration
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'iyHxHphyuy3i'
}

class MumbaiSequentialAutomation:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/mumbai_sequential"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize OCR
        try:
            self.ocr_reader = easyocr.Reader(['en'])
            print("✅ EasyOCR initialized")
        except:
            self.ocr_reader = None
            print("⚠️ EasyOCR not available")
        
        self.driver = None
        self.wait = None
        self.session_counter = 0
        
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
            {"year_db": 2, "reg_year": 2020},
        ]
        
        self.mumbai_villages = [
            {"value": "1", "name": "Andheri"},
            {"value": "2", "name": "Bandra"},
            {"value": "3", "name": "Borivali"},
            {"value": "4", "name": "Malad"},
            {"value": "5", "name": "Kandivali"},
            {"value": "6", "name": "Goregaon"},
            {"value": "7", "name": "Jogeshwari"},
            {"value": "8", "name": "Vile Parle"},
            {"value": "9", "name": "Santacruz"},
            {"value": "10", "name": "Khar"},
        ]
        
    def generate_session_id(self):
        """Generate unique session ID for IP rotation"""
        self.session_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"mumbai-seq-{self.session_counter}-{random_id}-{timestamp}"
    
    def get_proxy_config(self, session_id):
        """Get proxy configuration with unique session"""
        full_username = f"{PROXY_CONFIG['username']}-sessid-{session_id}"
        proxy_url = f"http://{full_username}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def setup_driver_with_proxy(self, session_id):
        """Setup Firefox driver with proxy"""
        try:
            # Close existing driver if any
            if self.driver:
                self.driver.quit()
                time.sleep(2)
            
            options = Options()
            
            # Proxy configuration
            proxy_host = PROXY_CONFIG['host']
            proxy_port = int(PROXY_CONFIG['port'])
            
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxy_host)
            options.set_preference("network.proxy.http_port", proxy_port)
            options.set_preference("network.proxy.ssl", proxy_host)
            options.set_preference("network.proxy.ssl_port", proxy_port)
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            
            # Visible browser for debugging
            # options.add_argument('--headless')  # Comment out for visible browser
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print(f"🦊 Firefox setup with proxy session: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Driver setup failed: {e}")
            return False

    def solve_captcha(self, session_id):
        """Solve CAPTCHA using EasyOCR"""
        try:
            # Find CAPTCHA image
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.ID, "captcha-img"))
            )
            
            # Get CAPTCHA image source
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA image with proxy
            proxy_config = self.get_proxy_config(session_id)
            response = requests.get(captcha_src, proxies=proxy_config, verify=False, timeout=10)
            
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
            print(f"   ❌ CAPTCHA solving failed: {e}")
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

    def fill_form(self, year_db, village_info, reg_year):
        """Fill the search form with Mumbai-specific parameters"""
        try:
            print(f"🤖 Form automation: Mumbai {village_info['name']} - Year {reg_year}")
            
            # Select database (year)
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            print(f"   ✅ Database: {year_db}")
            time.sleep(1)
            
            # Select Mumbai district (FIXED)
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value(self.DISTRICT_ID)
            print(f"   ✅ District: Mumbai ({self.DISTRICT_ID})")
            time.sleep(2)
            
            # Select Mumbai taluka (FIXED - first available)
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                print(f"   ✅ Taluka: Mumbai")
                time.sleep(2)
            
            # Select specific village (VARIABLE)
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_select.select_by_value(village_info['value'])
            print(f"   ✅ Village: {village_info['name']}")
            time.sleep(1)
            
            # Select Agreement to Sale (FIXED)
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value(self.ARTICLE_ID)
            print(f"   ✅ Article: Agreement to Sale ({self.ARTICLE_ID})")
            time.sleep(1)
            
            # Add registration year (VARIABLE - same as selected year)
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            print(f"   ✅ Registration Year: {reg_year}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Form filling failed: {e}")
            return False

    def submit_form(self, session_id):
        """Solve CAPTCHA and submit form"""
        try:
            print("🤖 Starting CAPTCHA solving...")
            
            # Solve CAPTCHA
            captcha_solution = self.solve_captcha(session_id)
            
            # Enter CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_solution)
            print(f"   ✅ CAPTCHA entered: '{captcha_solution}'")
            
            # Submit form
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            print("   📤 Form submitted")
            
            # Wait for results to load
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"   ❌ Form submission failed: {e}")
            return False

    def check_results(self):
        """Check if any documents were found"""
        try:
            time.sleep(3)
            page_source = self.driver.page_source
            
            if "No data available in table" in page_source:
                print("❌ No documents found")
                return False
            elif "Showing" in page_source and "entries" in page_source:
                print("✅ DOCUMENTS FOUND!")
                return True
            else:
                print("⚠️ Results unclear")
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
            print(f"\n🔍 TRYING: Mumbai {village_info['name']} - Year {reg_year}")
            
            # Generate new session for IP rotation
            session_id = self.generate_session_id()
            
            # Setup driver with new proxy session
            if not self.setup_driver_with_proxy(session_id):
                return False
            
            # Load the website
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Fill form
            if not self.fill_form(year_db, village_info, reg_year):
                return False
            
            # Submit form
            if not self.submit_form(session_id):
                return False
            
            # Check results
            found_documents = self.check_results()
            
            # Save debug info
            self.save_debug_info(village_info, reg_year, found_documents)
            
            if found_documents:
                print(f"🎉 SUCCESS! Found documents for Mumbai {village_info['name']} - {reg_year}")
                return {
                    "village": village_info['name'],
                    "year": reg_year,
                    "year_db": year_db,
                    "session_id": session_id
                }
            
            return False
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    def run_mumbai_search(self):
        """Run Mumbai-focused sequential search"""
        print("🚀 MUMBAI SEQUENTIAL IGR AUTOMATION")
        print("=" * 60)
        print("🏙️ FIXED PARAMETERS:")
        print("   📍 District: Mumbai (31)")
        print("   🏘️ Taluka: Mumbai")
        print("   📄 Article: Agreement to Sale (42)")
        print("\n🔄 VARIABLE PARAMETERS:")
        print("   📅 Years: 2020-2025")
        print("   🏘️ Villages: Andheri, Bandra, Borivali, Malad, etc.")
        print("   📝 Registration Year = Selected Year")
        print("   🔄 IP rotation: New session for each search")
        print("=" * 60)
        
        successful_results = []
        total_combinations = len(self.year_combinations) * len(self.mumbai_villages)
        current_combination = 0
        
        # Try all combinations sequentially
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
                    print(f"✅ FOUND DOCUMENTS! Continuing search...")
                else:
                    print("❌ No documents found, trying next combination...")
                
                # Wait between attempts for IP rotation
                if current_combination < total_combinations:
                    wait_time = 3
                    print(f"⏳ Waiting {wait_time}s for IP rotation...")
                    time.sleep(wait_time)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MUMBAI SEARCH SUMMARY")
        print("=" * 60)
        
        if successful_results:
            print(f"🎉 SUCCESS! Found Mumbai Agreement to Sale documents in {len(successful_results)} combinations:")
            for result in successful_results:
                print(f"   🏘️ Mumbai {result['village']} - Year {result['year']}")
                print(f"      📅 Database: {result['year_db']}, Session: {result['session_id']}")
        else:
            print("❌ No Mumbai Agreement to Sale documents found")
            print("💡 Possible reasons:")
            print("   - CAPTCHA solutions were incorrect")
            print("   - No Agreement to Sale documents in Mumbai for these years/villages")
            print("   - Website access restrictions")
        
        print(f"\n📊 Statistics:")
        print(f"   ✅ Successful: {len(successful_results)}")
        print(f"   ❌ Failed: {total_combinations - len(successful_results)}")
        print(f"   📁 Debug files saved in: {os.path.abspath(self.data_dir)}")
        
        return successful_results

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Browser closed")
        except:
            pass

def main():
    automation = MumbaiSequentialAutomation()
    
    try:
        successful_results = automation.run_mumbai_search()
        
        if successful_results:
            print(f"\n🎉 MUMBAI MISSION ACCOMPLISHED! Found {len(successful_results)} working combinations")
            print("🔥 You can now use these successful Mumbai combinations for bulk downloading!")
        else:
            print("\n😔 No Mumbai Agreement to Sale documents found")
            print("💡 Try running again - different CAPTCHA solutions might work")
            
    except KeyboardInterrupt:
        print("\n\n👋 Mumbai search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 