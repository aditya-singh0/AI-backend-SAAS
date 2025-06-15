#!/usr/bin/env python3
"""
Flexible IGR Document Search Automation
Tries multiple search combinations to find available documents
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

class FlexibleIGRAutomation:
    def __init__(self):
        self.setup_driver()
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/flexible_search"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize OCR
        try:
            self.ocr_reader = easyocr.Reader(['en'])
            print("✅ EasyOCR initialized")
        except:
            self.ocr_reader = None
            print("⚠️ EasyOCR not available")
        
        # Search combinations to try
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
        ]
        
    def setup_driver(self):
        """Setup Firefox driver"""
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        print("🦊 Firefox driver initialized")

    def solve_captcha(self):
        """Solve CAPTCHA using EasyOCR"""
        try:
            # Find CAPTCHA image
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.ID, "captcha-img"))
            )
            
            # Get CAPTCHA image source
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA image
            response = requests.get(captcha_src, verify=False)
            
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
            print(f"   🔍 Pattern guess: '{fallback}' (fallback method)")
            return fallback
                
        except Exception as e:
            print(f"   ❌ CAPTCHA solving failed: {e}")
            return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

    def fill_form(self, search_params):
        """Fill the search form with given parameters"""
        try:
            print(f"\n🤖 FORM AUTOMATION for {search_params['district_name']} - {search_params['article_name']}...")
            
            # Select database (recent years)
            dbselect = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "dbselect"))))
            dbselect.select_by_value("3")
            print("   ✅ dbselect: 3")
            time.sleep(1)
            
            # Select district
            district_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "district_id"))))
            district_select.select_by_value(search_params["district"])
            print(f"   ✅ district_id: {search_params['district']} ({search_params['district_name']})")
            time.sleep(2)
            
            # Wait for taluka to load and select first available
            try:
                taluka_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "taluka_id"))))
                taluka_options = [opt for opt in taluka_select.options if opt.get_attribute('value')]
                if taluka_options:
                    taluka_select.select_by_value(taluka_options[0].get_attribute('value'))
                    print("   ✅ Taluka selected")
                    time.sleep(2)
            except:
                print("   ⚠️ Taluka selection skipped")
            
            # Wait for village to load and select first available
            try:
                village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
                village_options = [opt for opt in village_select.options if opt.get_attribute('value')]
                if village_options:
                    village_select.select_by_value(village_options[0].get_attribute('value'))
                    print("   ✅ Village selected")
                    time.sleep(1)
            except:
                print("   ⚠️ Village selection skipped")
            
            # Select article type
            article_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "article_id"))))
            article_select.select_by_value(search_params["article"])
            print(f"   ✅ article_id: {search_params['article']} ({search_params['article_name']})")
            time.sleep(1)
            
            # Add required document number (using current year)
            free_text_input = self.driver.find_element(By.ID, "free_text")
            current_year = datetime.now().year
            free_text_input.clear()
            free_text_input.send_keys(str(current_year))
            print(f"   ✅ free_text: {current_year}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Form filling failed: {e}")
            return False

    def submit_form(self):
        """Solve CAPTCHA and submit form"""
        try:
            print("🤖 Starting automatic CAPTCHA solving...")
            
            # Solve CAPTCHA
            captcha_solution = self.solve_captcha()
            
            # Enter CAPTCHA
            captcha_input = self.driver.find_element(By.ID, "cpatchaTextBox")
            captcha_input.clear()
            captcha_input.send_keys(captcha_solution)
            print(f"   ✅ CAPTCHA entered: '{captcha_solution}'")
            
            # Submit form
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            print("   🎯 Found submit button")
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
            # Wait for results table
            time.sleep(3)
            
            # Check for "No data available" message
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

    def save_debug_info(self, search_params):
        """Save debug information"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            debug_file = os.path.join(self.data_dir, f'debug_{search_params["district_name"]}_{timestamp}.html')
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"📄 Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")

    def try_search_combination(self, search_params):
        """Try a single search combination"""
        try:
            print(f"\n🔍 TRYING: {search_params['district_name']} - {search_params['article_name']}")
            
            # Load the website
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Fill form
            if not self.fill_form(search_params):
                return False
            
            # Submit form
            if not self.submit_form():
                return False
            
            # Check results
            found_documents = self.check_results()
            
            # Save debug info
            self.save_debug_info(search_params)
            
            if found_documents:
                print(f"🎉 SUCCESS! Found documents for {search_params['district_name']} - {search_params['article_name']}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Search combination failed: {e}")
            return False

    def run_flexible_search(self):
        """Run flexible search trying multiple combinations"""
        print("🚀 FLEXIBLE IGR DOCUMENT SEARCH")
        print("=" * 60)
        print("🔍 Trying multiple districts and document types...")
        print("📍 Districts: Mumbai, Pune, Thane, Nashik")
        print("📄 Documents: Agreement to Sale, Sale Deed, Gift Deed")
        print("=" * 60)
        
        successful_combinations = []
        
        for i, search_params in enumerate(self.search_combinations, 1):
            print(f"\n🚀 ATTEMPT {i}/{len(self.search_combinations)}")
            
            try:
                success = self.try_search_combination(search_params)
                
                if success:
                    successful_combinations.append(search_params)
                    print(f"✅ FOUND DOCUMENTS! Continuing to find more...")
                else:
                    print("❌ No documents found, trying next combination...")
                
                # Wait between attempts
                if i < len(self.search_combinations):
                    wait_time = 3
                    print(f"⏳ Waiting {wait_time}s before next attempt...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"❌ Attempt {i} failed: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SEARCH SUMMARY")
        print("=" * 60)
        
        if successful_combinations:
            print(f"✅ Found documents in {len(successful_combinations)} combinations:")
            for combo in successful_combinations:
                print(f"   📍 {combo['district_name']} - {combo['article_name']}")
        else:
            print("❌ No documents found in any combination")
            print("💡 Possible reasons:")
            print("   - CAPTCHA solutions were incorrect")
            print("   - No documents match the search criteria")
            print("   - Website structure has changed")
            print("   - Access restrictions or rate limiting")
        
        print(f"\n📁 Debug files saved to: {os.path.abspath(self.data_dir)}")
        
        return successful_combinations

    def cleanup(self):
        """Clean up resources"""
        try:
            self.driver.quit()
            print("🧹 Browser closed")
        except:
            pass

def main():
    automation = FlexibleIGRAutomation()
    
    try:
        successful_combinations = automation.run_flexible_search()
        
        if successful_combinations:
            print(f"\n🎉 SUCCESS! Found {len(successful_combinations)} working combinations")
        else:
            print("\n😔 No documents found in any combination")
            
    except KeyboardInterrupt:
        print("\n\n👋 Search interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        automation.cleanup()

if __name__ == "__main__":
    main() 