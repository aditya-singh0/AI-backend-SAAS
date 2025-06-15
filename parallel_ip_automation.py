#!/usr/bin/env python3
"""
Parallel IGR Automation with IP Switching
Runs multiple browser instances simultaneously with different IP sessions
"""

import time
import random
import threading
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

class ParallelIGRAutomation:
    def __init__(self, worker_id, proxy_session=None):
        self.worker_id = worker_id
        self.proxy_session = proxy_session or self.generate_session_id()
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = f"data/parallel_worker_{worker_id}"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize OCR (shared instance)
        if not hasattr(ParallelIGRAutomation, '_ocr_reader'):
            try:
                ParallelIGRAutomation._ocr_reader = easyocr.Reader(['en'])
                print(f"🤖 Worker {worker_id}: EasyOCR initialized")
            except:
                ParallelIGRAutomation._ocr_reader = None
                print(f"⚠️ Worker {worker_id}: EasyOCR not available")
        
        self.ocr_reader = ParallelIGRAutomation._ocr_reader
        self.driver = None
        self.wait = None
        
    def generate_session_id(self):
        """Generate unique session ID for IP rotation"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"worker{self.worker_id}-{random_id}-{timestamp}"
    
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

    def fill_form(self, search_params):
        """Fill the search form with given parameters"""
        try:
            print(f"🤖 Worker {self.worker_id}: Form automation for {search_params['district_name']} - {search_params['article_name']}")
            
            # Select database (recent years)
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value("3")
            time.sleep(1)
            
            # Select district
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value(search_params["district"])
            time.sleep(2)
            
            # Wait for taluka to load and select first available
            try:
                taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
                taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
                if taluka_options:
                    taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                    time.sleep(2)
            except:
                pass
            
            # Wait for village to load and select first available
            try:
                village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
                village_options = [opt for opt in village_select.options if opt.get_attribute('value')]
                if village_options:
                    village_select.select_by_value(village_options[0].get_attribute('value'))
                    time.sleep(1)
            except:
                pass
            
            # Select article type
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value(search_params["article"])
            time.sleep(1)
            
            # Add required document number (using current year)
            free_text_input = self.driver.find_element(By.ID, "free_text")
            current_year = datetime.now().year
            free_text_input.clear()
            free_text_input.send_keys(str(current_year))
            
            print(f"   ✅ Worker {self.worker_id}: Form filled successfully")
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

    def save_debug_info(self, search_params, success=False):
        """Save debug information"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            status = "SUCCESS" if success else "FAILED"
            debug_file = os.path.join(self.data_dir, f'{status}_{search_params["district_name"]}_{timestamp}.html')
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"📄 Worker {self.worker_id}: Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Worker {self.worker_id}: Debug save failed: {e}")

    def process_search_combination(self, search_params):
        """Process a single search combination"""
        try:
            print(f"\n🔍 Worker {self.worker_id}: TRYING {search_params['district_name']} - {search_params['article_name']}")
            
            # Setup driver with proxy
            if not self.setup_driver_with_proxy():
                return {"worker_id": self.worker_id, "success": False, "error": "Driver setup failed"}
            
            # Load the website
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Fill form
            if not self.fill_form(search_params):
                return {"worker_id": self.worker_id, "success": False, "error": "Form filling failed"}
            
            # Submit form
            if not self.submit_form():
                return {"worker_id": self.worker_id, "success": False, "error": "Form submission failed"}
            
            # Check results
            found_documents = self.check_results()
            
            # Save debug info
            self.save_debug_info(search_params, found_documents)
            
            if found_documents:
                print(f"🎉 Worker {self.worker_id}: SUCCESS! Found documents for {search_params['district_name']} - {search_params['article_name']}")
                return {
                    "worker_id": self.worker_id, 
                    "success": True, 
                    "search_params": search_params,
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

class ParallelSearchManager:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.search_combinations = [
            # Mumbai combinations
            {"district": "31", "district_name": "Mumbai", "article": "42", "article_name": "Agreement to Sale"},
            {"district": "31", "district_name": "Mumbai", "article": "31", "article_name": "Sale Deed"},
            {"district": "31", "district_name": "Mumbai", "article": "32", "article_name": "Gift Deed"},
            
            # Pune combinations
            {"district": "29", "district_name": "Pune", "article": "42", "article_name": "Agreement to Sale"},
            {"district": "29", "district_name": "Pune", "article": "31", "article_name": "Sale Deed"},
            
            # Thane combinations
            {"district": "33", "district_name": "Thane", "article": "42", "article_name": "Agreement to Sale"},
            {"district": "33", "district_name": "Thane", "article": "31", "article_name": "Sale Deed"},
            
            # Nashik combinations
            {"district": "21", "district_name": "Nashik", "article": "42", "article_name": "Agreement to Sale"},
            {"district": "21", "district_name": "Nashik", "article": "31", "article_name": "Sale Deed"},
            
            # Nagpur combinations
            {"district": "22", "district_name": "Nagpur", "article": "42", "article_name": "Agreement to Sale"},
            {"district": "22", "district_name": "Nagpur", "article": "31", "article_name": "Sale Deed"},
            
            # Aurangabad combinations
            {"district": "3", "district_name": "Aurangabad", "article": "42", "article_name": "Agreement to Sale"},
            {"district": "3", "district_name": "Aurangabad", "article": "31", "article_name": "Sale Deed"},
        ]

    def run_parallel_search(self):
        """Run parallel search with multiple workers"""
        print("🚀 PARALLEL IGR AUTOMATION WITH IP SWITCHING")
        print("=" * 70)
        print(f"🔄 Running {self.max_workers} parallel workers with different IP sessions")
        print(f"🔍 Testing {len(self.search_combinations)} search combinations")
        print("📍 Districts: Mumbai, Pune, Thane, Nashik, Nagpur, Aurangabad")
        print("📄 Documents: Agreement to Sale, Sale Deed, Gift Deed")
        print("=" * 70)
        
        successful_results = []
        failed_results = []
        
        # Create worker tasks
        tasks = []
        for i, search_params in enumerate(self.search_combinations):
            worker_id = i + 1
            proxy_session = f"parallel-{worker_id}-{datetime.now().strftime('%H%M%S')}"
            tasks.append((worker_id, proxy_session, search_params))
        
        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for worker_id, proxy_session, search_params in tasks:
                automation = ParallelIGRAutomation(worker_id, proxy_session)
                future = executor.submit(automation.process_search_combination, search_params)
                future_to_task[future] = (worker_id, search_params)
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                worker_id, search_params = future_to_task[future]
                try:
                    result = future.result()
                    if result["success"]:
                        successful_results.append(result)
                        print(f"✅ Worker {worker_id} FOUND DOCUMENTS!")
                    else:
                        failed_results.append(result)
                        print(f"❌ Worker {worker_id} failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ Worker {worker_id} exception: {e}")
                    failed_results.append({"worker_id": worker_id, "success": False, "error": str(e)})
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PARALLEL SEARCH SUMMARY")
        print("=" * 70)
        
        if successful_results:
            print(f"🎉 SUCCESS! Found documents in {len(successful_results)} combinations:")
            for result in successful_results:
                params = result["search_params"]
                print(f"   📍 Worker {result['worker_id']}: {params['district_name']} - {params['article_name']}")
                print(f"      🔗 Proxy session: {result['proxy_session']}")
        else:
            print("❌ No documents found in any combination")
            print("💡 Possible reasons:")
            print("   - All CAPTCHA solutions were incorrect")
            print("   - No documents match the search criteria")
            print("   - Website access restrictions")
            print("   - Proxy/IP blocking")
        
        print(f"\n📊 Statistics:")
        print(f"   ✅ Successful: {len(successful_results)}")
        print(f"   ❌ Failed: {len(failed_results)}")
        print(f"   📁 Debug files saved in: data/parallel_worker_* directories")
        
        return successful_results

def main():
    # Ask user for number of parallel workers
    try:
        max_workers = int(input("How many parallel workers? (default 5): ") or "5")
        max_workers = min(max_workers, 10)  # Limit to 10 workers
    except:
        max_workers = 5
    
    print(f"\n🚀 Starting {max_workers} parallel workers...")
    
    manager = ParallelSearchManager(max_workers=max_workers)
    
    try:
        successful_results = manager.run_parallel_search()
        
        if successful_results:
            print(f"\n🎉 MISSION ACCOMPLISHED! Found {len(successful_results)} working combinations")
            print("🔥 You can now use these successful combinations for bulk downloading!")
        else:
            print("\n😔 No documents found in any combination")
            print("💡 Try running again - different CAPTCHA solutions might work")
            
    except KeyboardInterrupt:
        print("\n\n👋 Parallel search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 