#!/usr/bin/env python3
"""
Test Other Districts - Maharashtra IGR Document Finder
Tests different districts to find Agreement to Sale documents
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import easyocr
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class DistrictTester:
    def __init__(self):
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eASR/Home/SearchDocument"
        self.reader = easyocr.Reader(['en'])
        self.data_dir = "data/district_test"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Test different districts (not just Mumbai)
        self.test_districts = [
            {"name": "Pune", "id": "32"},
            {"name": "Nashik", "id": "21"},
            {"name": "Nagpur", "id": "20"},
            {"name": "Aurangabad", "id": "2"},
            {"name": "Kolhapur", "id": "15"},
            {"name": "Solapur", "id": "33"},
            {"name": "Thane", "id": "34"},
            {"name": "Mumbai", "id": "31"},  # Keep Mumbai for comparison
        ]
        
    def setup_browser(self):
        """Setup headless Firefox browser"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_preference("network.http.connection-timeout", 30)
        options.set_preference("network.http.response.timeout", 30)
        
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(30)
        return driver
        
    def solve_captcha(self, driver):
        """Download and solve CAPTCHA"""
        try:
            # Find CAPTCHA image
            captcha_img = driver.find_element(By.ID, "imgCaptcha")
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA
            timestamp = int(time.time())
            captcha_path = f"{self.data_dir}/captcha_{timestamp}.png"
            
            response = requests.get(captcha_src, verify=False, timeout=10)
            with open(captcha_path, 'wb') as f:
                f.write(response.content)
                
            # Solve with EasyOCR
            results = self.reader.readtext(captcha_path)
            if results:
                captcha_text = results[0][1].upper().strip()
                confidence = results[0][2]
                return captcha_text, confidence
                
        except Exception as e:
            print(f"   ❌ CAPTCHA error: {e}")
            
        return None, 0
        
    def test_district(self, district_name, district_id, year=2024):
        """Test a specific district for documents"""
        print(f"\n🔍 Testing {district_name} (ID: {district_id}) - Year {year}")
        
        driver = None
        try:
            driver = self.setup_browser()
            driver.get(self.base_url)
            time.sleep(3)
            
            # Fill form
            # Database (3 for recent years)
            db_select = Select(driver.find_element(By.ID, "dbselect"))
            db_select.select_by_value("3")
            time.sleep(1)
            
            # District
            district_select = Select(driver.find_element(By.ID, "district_id"))
            district_select.select_by_value(district_id)
            time.sleep(2)
            
            # Article (42 = Agreement to Sale)
            article_select = Select(driver.find_element(By.ID, "article_id"))
            article_select.select_by_value("42")
            time.sleep(1)
            
            # Registration Year
            reg_year_input = driver.find_element(By.ID, "reg_year")
            reg_year_input.clear()
            reg_year_input.send_keys(str(year))
            time.sleep(1)
            
            # Solve CAPTCHA
            captcha_text, confidence = self.solve_captcha(driver)
            if not captcha_text:
                print(f"   ❌ CAPTCHA failed")
                return False
                
            print(f"   🔤 CAPTCHA: '{captcha_text}' (confidence: {confidence:.2f})")
            
            # Enter CAPTCHA
            captcha_input = driver.find_element(By.ID, "txtCaptcha")
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            
            # Submit form
            submit_btn = driver.find_element(By.ID, "btnSearch")
            submit_btn.click()
            time.sleep(5)
            
            # Check results
            try:
                # Look for results table
                table = driver.find_element(By.ID, "example")
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                
                if len(rows) > 0:
                    # Check if there's actual data (not "No data available")
                    first_row_text = rows[0].text.strip()
                    if "No data available" not in first_row_text and first_row_text:
                        print(f"   ✅ FOUND DOCUMENTS! ({len(rows)} rows)")
                        
                        # Save successful result
                        timestamp = int(time.time())
                        success_file = f"{self.data_dir}/SUCCESS_{district_name}_{year}_{len(rows)}docs_{timestamp}.html"
                        with open(success_file, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                            
                        return True
                    else:
                        print(f"   ❌ No documents found")
                else:
                    print(f"   ❌ No table rows found")
                    
            except Exception as e:
                print(f"   ❌ Error checking results: {e}")
                
        except Exception as e:
            print(f"   ❌ Error testing {district_name}: {e}")
            
        finally:
            if driver:
                driver.quit()
                
        return False
        
    def run_tests(self):
        """Run tests on all districts"""
        print("🚀 TESTING DIFFERENT DISTRICTS FOR AGREEMENT TO SALE DOCUMENTS")
        print("=" * 70)
        
        found_districts = []
        
        for district in self.test_districts:
            success = self.test_district(district["name"], district["id"])
            if success:
                found_districts.append(district["name"])
                
            time.sleep(2)  # Brief pause between tests
            
        print("\n" + "=" * 70)
        print("📊 DISTRICT TEST SUMMARY")
        print("=" * 70)
        
        if found_districts:
            print(f"✅ Districts with documents: {', '.join(found_districts)}")
        else:
            print("❌ No districts found with Agreement to Sale documents")
            print("💡 This might indicate:")
            print("   - Documents are not publicly available")
            print("   - Different search parameters needed")
            print("   - Website access restrictions")
            
        print(f"\n📁 Test files saved in: {os.path.abspath(self.data_dir)}")

if __name__ == "__main__":
    tester = DistrictTester()
    tester.run_tests() 