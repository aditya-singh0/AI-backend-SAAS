#!/usr/bin/env python3
"""
Mumbai Focused IGR Automation
Fixed: District=Mumbai, Taluka=Mumbai, Article=Agreement to Sale
Variable: Year, Village, Registration Year
"""

import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
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

class MumbaiFocusedAutomation:
    def __init__(self, worker_id, proxy_session=None):
        self.worker_id = worker_id
        self.proxy_session = proxy_session or self.generate_session_id()
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = f"data/mumbai_worker_{worker_id}"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize OCR (shared instance)
        if not hasattr(MumbaiFocusedAutomation, '_ocr_reader'):
            try:
                MumbaiFocusedAutomation._ocr_reader = easyocr.Reader(['en'])
                print(f"🤖 Worker {worker_id}: EasyOCR initialized")
            except:
                MumbaiFocusedAutomation._ocr_reader = None
                print(f"⚠️ Worker {worker_id}: EasyOCR not available")
        
        self.ocr_reader = MumbaiFocusedAutomation._ocr_reader
        self.driver = None
        self.wait = None
        
        # FIXED PARAMETERS
        self.DISTRICT_ID = "31"  # Mumbai
        self.DISTRICT_NAME = "Mumbai"
        self.ARTICLE_ID = "42"   # Agreement to Sale
        self.ARTICLE_NAME = "Agreement to Sale"
        
    def generate_session_id(self):
        """Generate unique session ID for IP rotation"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"mumbai{self.worker_id}-{random_id}-{timestamp}"
    
    def get_proxy_config(self):
        """Get proxy configuration with unique session"""
        full_username = f"{PROXY_CONFIG['username']}-sessid-{self.proxy_session}"
        proxy_url = f"http://{full_username}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def setup_driver_with_proxy(self):
        """Setup Firefox driver with proxy"""
        try:
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
            
            # Headless for parallel execution
            options.add_argument('--headless')
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            print(f"🦊 Worker {self.worker_id}: Firefox with proxy session {self.proxy_session}")
            return True
            
        except Exception as e:
            print(f"❌ Worker {self.worker_id}: Driver setup failed: {e}")
            return False

    def solve_captcha(self):
        """Solve CAPTCHA using EasyOCR"""
        try:
            # Find CAPTCHA image
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.ID, "captcha-img"))
            )
            
            # Get CAPTCHA image source
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA image with proxy
            proxy_config = self.get_proxy_config()
            response = requests.get(captcha_src, proxies=proxy_config, verify=False, timeout=10)
            
            # Save CAPTCHA image
            timestamp = datetime.now().strftime('%H%M%S')
            captcha_path = os.path.join(self.data_dir, f'captcha_{timestamp}.png')
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
            
            print(f"   📷 Worker {self.worker_id}: CAPTCHA downloaded")
            
            # Solve with EasyOCR if available
            if self.ocr_reader:
                results = self.ocr_reader.readtext(captcha_path)
                
                if results:
                    captcha_text = results[0][1].strip()
                    confidence = results[0][2]
                    print(f"   🔍 Worker {self.worker_id}: EasyOCR solved: '{captcha_text}' (confidence: {confidence:.2f})")
                    return captcha_text
            
            # Fallback pattern
            fallback = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
            print(f"   🔍 Worker {self.worker_id}: Pattern guess: '{fallback}'")
            return fallback
                
        except Exception as e:
            print(f"   ❌ Worker {self.worker_id}: CAPTCHA solving failed: {e}")
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

    def get_mumbai_villages(self):
        """Get list of Mumbai villages dynamically"""
        try:
            # Load the website first
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Select database
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value("3")
            time.sleep(1)
            
            # Select Mumbai district
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value(self.DISTRICT_ID)
            time.sleep(2)
            
            # Select Mumbai taluka (first available)
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                time.sleep(2)
            
            # Get all village options
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            villages = []
            
            for option in village_select.options:
                value = option.get_attribute('value')
                text = option.text.strip()
                if value and value != "":
                    villages.append({"value": value, "name": text})
            
            print(f"🏘️ Worker {self.worker_id}: Found {len(villages)} Mumbai villages")
            return villages
            
        except Exception as e:
            print(f"❌ Worker {self.worker_id}: Failed to get villages: {e}")
            # Return some common Mumbai villages as fallback
            return [
                {"value": "1", "name": "Andheri"},
                {"value": "2", "name": "Bandra"},
                {"value": "3", "name": "Borivali"},
                {"value": "4", "name": "Malad"},
                {"value": "5", "name": "Kandivali"}
            ]

    def fill_form(self, year_db, village_info, reg_year):
        """Fill the search form with Mumbai-specific parameters"""
        try:
            print(f"🤖 Worker {self.worker_id}: Mumbai {village_info['name']} - Year {reg_year}")
            
            # Select database (year)
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value(str(year_db))
            time.sleep(1)
            
            # Select Mumbai district (FIXED)
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value(self.DISTRICT_ID)
            time.sleep(2)
            
            # Select Mumbai taluka (FIXED - first available)
            taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
            taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
            if taluka_options:
                taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                time.sleep(2)
            
            # Select specific village (VARIABLE)
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_select.select_by_value(village_info['value'])
            time.sleep(1)
            
            # Select Agreement to Sale (FIXED)
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value(self.ARTICLE_ID)
            time.sleep(1)
            
            # Add registration year (VARIABLE - same as selected year)
            free_text_input = self.driver.find_element(By.ID, "free_text")
            free_text_input.clear()
            free_text_input.send_keys(str(reg_year))
            
            print(f"   ✅ Worker {self.worker_id}: Form filled - {village_info['name']} {reg_year}")
            return True
            
        except Exception as e:
            print(f"   ❌ Worker {self.worker_id}: Form filling failed: {e}")
            return False

    def submit_form(self):
        """Solve CAPTCHA and submit form"""
        try:
            # Solve CAPTCHA
            captcha_solution = self.solve_captcha()
            
            # Enter CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_solution)
            
            # Submit form
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            
            # Wait for results to load
            time.sleep(5)
            print(f"   📤 Worker {self.worker_id}: Form submitted")
            return True
            
        except Exception as e:
            print(f"   ❌ Worker {self.worker_id}: Form submission failed: {e}")
            return False

    def check_results(self):
        """Check if any documents were found"""
        try:
            time.sleep(3)
            page_source = self.driver.page_source
            
            if "No data available in table" in page_source:
                return False
            elif "Showing" in page_source and "entries" in page_source:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Worker {self.worker_id}: Results check failed: {e}")
            return False

    def save_debug_info(self, village_info, reg_year, success=False):
        """Save debug information"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            status = "SUCCESS" if success else "FAILED"
            debug_file = os.path.join(self.data_dir, f'{status}_{village_info["name"]}_{reg_year}_{timestamp}.html')
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"📄 Worker {self.worker_id}: Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Worker {self.worker_id}: Debug save failed: {e}")

    def process_search_combination(self, search_params):
        """Process a single Mumbai search combination"""
        try:
            year_db = search_params['year_db']
            village_info = search_params['village_info']
            reg_year = search_params['reg_year']
            
            print(f"\n🔍 Worker {self.worker_id}: Mumbai {village_info['name']} - Year {reg_year}")
            
            # Setup driver with proxy
            if not self.setup_driver_with_proxy():
                return {"worker_id": self.worker_id, "success": False, "error": "Driver setup failed"}
            
            # Load the website
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Fill form
            if not self.fill_form(year_db, village_info, reg_year):
                return {"worker_id": self.worker_id, "success": False, "error": "Form filling failed"}
            
            # Submit form
            if not self.submit_form():
                return {"worker_id": self.worker_id, "success": False, "error": "Form submission failed"}
            
            # Check results
            found_documents = self.check_results()
            
            # Save debug info
            self.save_debug_info(village_info, reg_year, found_documents)
            
            if found_documents:
                print(f"🎉 Worker {self.worker_id}: SUCCESS! Found documents for Mumbai {village_info['name']} - {reg_year}")
                return {
                    "worker_id": self.worker_id, 
                    "success": True, 
                    "village": village_info['name'],
                    "year": reg_year,
                    "proxy_session": self.proxy_session
                }
            else:
                print(f"❌ Worker {self.worker_id}: No documents found")
                return {"worker_id": self.worker_id, "success": False, "error": "No documents found"}
            
        except Exception as e:
            print(f"❌ Worker {self.worker_id}: Search failed: {e}")
            return {"worker_id": self.worker_id, "success": False, "error": str(e)}
        
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass

class MumbaiSearchManager:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        
        # Year combinations to try
        self.year_combinations = [
            {"year_db": 3, "reg_year": 2025},  # Recent years
            {"year_db": 3, "reg_year": 2024},
            {"year_db": 3, "reg_year": 2023},
            {"year_db": 2, "reg_year": 2022},  # Historical years
            {"year_db": 2, "reg_year": 2021},
            {"year_db": 2, "reg_year": 2020},
        ]
        
        # Common Mumbai villages to try
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

    def generate_search_combinations(self):
        """Generate all Mumbai search combinations"""
        combinations = []
        
        for year_combo in self.year_combinations:
            for village in self.mumbai_villages:
                combinations.append({
                    "year_db": year_combo["year_db"],
                    "village_info": village,
                    "reg_year": year_combo["reg_year"]
                })
        
        return combinations

    def run_mumbai_search(self):
        """Run Mumbai-focused parallel search"""
        print("🚀 MUMBAI FOCUSED IGR AUTOMATION")
        print("=" * 60)
        print("🏙️ FIXED PARAMETERS:")
        print("   📍 District: Mumbai (31)")
        print("   🏘️ Taluka: Mumbai")
        print("   📄 Article: Agreement to Sale (42)")
        print("\n🔄 VARIABLE PARAMETERS:")
        print("   📅 Years: 2020-2025")
        print("   🏘️ Villages: Andheri, Bandra, Borivali, Malad, etc.")
        print("   📝 Registration Year = Selected Year")
        print("=" * 60)
        
        # Generate all combinations
        search_combinations = self.generate_search_combinations()
        print(f"🔍 Testing {len(search_combinations)} Mumbai combinations")
        print(f"🔄 Using {self.max_workers} parallel workers with different IPs")
        
        successful_results = []
        failed_results = []
        
        # Create worker tasks
        tasks = []
        for i, search_params in enumerate(search_combinations):
            worker_id = i + 1
            proxy_session = f"mumbai-{worker_id}-{datetime.now().strftime('%H%M%S')}"
            tasks.append((worker_id, proxy_session, search_params))
        
        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for worker_id, proxy_session, search_params in tasks:
                automation = MumbaiFocusedAutomation(worker_id, proxy_session)
                future = executor.submit(automation.process_search_combination, search_params)
                future_to_task[future] = (worker_id, search_params)
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                worker_id, search_params = future_to_task[future]
                try:
                    result = future.result()
                    if result["success"]:
                        successful_results.append(result)
                        print(f"✅ Worker {worker_id} FOUND MUMBAI DOCUMENTS!")
                    else:
                        failed_results.append(result)
                        
                except Exception as e:
                    print(f"❌ Worker {worker_id} exception: {e}")
                    failed_results.append({"worker_id": worker_id, "success": False, "error": str(e)})
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MUMBAI SEARCH SUMMARY")
        print("=" * 60)
        
        if successful_results:
            print(f"🎉 SUCCESS! Found Mumbai Agreement to Sale documents in {len(successful_results)} combinations:")
            for result in successful_results:
                print(f"   🏘️ Worker {result['worker_id']}: Mumbai {result['village']} - Year {result['year']}")
                print(f"      🔗 Proxy session: {result['proxy_session']}")
        else:
            print("❌ No Mumbai Agreement to Sale documents found")
            print("💡 Possible reasons:")
            print("   - CAPTCHA solutions were incorrect")
            print("   - No Agreement to Sale documents in Mumbai for these years/villages")
            print("   - Website access restrictions")
        
        print(f"\n📊 Statistics:")
        print(f"   ✅ Successful: {len(successful_results)}")
        print(f"   ❌ Failed: {len(failed_results)}")
        print(f"   📁 Debug files saved in: data/mumbai_worker_* directories")
        
        return successful_results

def main():
    # Ask user for number of parallel workers
    try:
        max_workers = int(input("How many parallel workers for Mumbai search? (default 5): ") or "5")
        max_workers = min(max_workers, 10)  # Limit to 10 workers
    except:
        max_workers = 5
    
    print(f"\n🚀 Starting {max_workers} parallel workers for Mumbai Agreement to Sale search...")
    
    manager = MumbaiSearchManager(max_workers=max_workers)
    
    try:
        successful_results = manager.run_mumbai_search()
        
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

if __name__ == "__main__":
    main() 