#!/usr/bin/env python3
"""
HEADLESS BROWSER AUTOMATION WITH IP SWITCHING
Combines headless browser + Thordata proxy IP rotation
Each search uses a different IP address
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

class HeadlessIPSwitching:
    def __init__(self):
        self.url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        self.data_dir = "data/headless_ip_switching"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Thordata proxy configuration with session-based authentication
        self.proxy_host = "42q6t9rp.pr.thordata.net"
        self.proxy_port = "9999"
        # Generate unique session ID for each run
        self.session_id = f"session-{int(time.time())}"
        self.proxy_url = f"http://{self.session_id}:password@{self.proxy_host}:{self.proxy_port}"
        
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
        self.current_ip = None
        
        # Search parameters - each will get a different IP
        self.searches = [
            {"year_db": 3, "reg_year": 2024, "village": "Andheri"},
            {"year_db": 3, "reg_year": 2023, "village": "Bandra"},
            {"year_db": 3, "reg_year": 2022, "village": "Borivali"},
            {"year_db": 2, "reg_year": 2021, "village": "Malad"},
            {"year_db": 3, "reg_year": 2024, "village": "Powai"},
            {"year_db": 2, "reg_year": 2020, "village": "Goregaon"},
        ]

    def get_new_ip_session(self):
        """Get a new IP session from Thordata proxy with authentication"""
        try:
            print("🔄 Requesting new IP session with authentication...")
            
            # Generate new session ID for IP rotation
            self.session_id = f"session-{int(time.time())}-{len(self.searches)}"
            self.proxy_url = f"http://{self.session_id}:password@{self.proxy_host}:{self.proxy_port}"
            
            print(f"🔑 Using session: {self.session_id}")
            
            # Create session with authenticated proxy
            session = requests.Session()
            session.proxies = {
                'http': self.proxy_url,
                'https': self.proxy_url
            }
            
            # Test IP and get new session
            try:
                response = session.get('http://httpbin.org/ip', timeout=15)
                if response.status_code == 200:
                    ip_info = response.json()
                    new_ip = ip_info.get('origin', 'Unknown')
                    
                    if new_ip != self.current_ip:
                        self.current_ip = new_ip
                        print(f"✅ New IP obtained: {new_ip}")
                        return True
                    else:
                        print(f"⚠️ Same IP returned: {new_ip}")
                        return True  # Still usable
                else:
                    print(f"❌ IP check failed: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ IP check error: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Proxy session failed: {e}")
            return False

    def start_headless_browser_with_proxy(self):
        """Start headless Firefox with authenticated Thordata proxy"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(2)
            
            options = Options()
            
            # HEADLESS MODE
            options.add_argument('--headless')
            
            # Proxy configuration with authentication
            proxy_parts = self.proxy_url.replace('http://', '').split('@')
            if len(proxy_parts) == 2:
                auth_part = proxy_parts[0]  # session-xxx:password
                host_port = proxy_parts[1]  # host:port
                
                options.set_preference("network.proxy.type", 1)  # Manual proxy
                options.set_preference("network.proxy.http", self.proxy_host)
                options.set_preference("network.proxy.http_port", int(self.proxy_port))
                options.set_preference("network.proxy.ssl", self.proxy_host)
                options.set_preference("network.proxy.ssl_port", int(self.proxy_port))
                options.set_preference("network.proxy.share_proxy_settings", True)
                
                # Set proxy authentication
                username, password = auth_part.split(':')
                options.set_preference("network.proxy.username", username)
                options.set_preference("network.proxy.password", password)
            
            # Performance optimizations
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Disable images for faster loading
            options.set_preference("permissions.default.image", 2)
            
            # Timeout settings
            options.set_preference("network.http.connection-timeout", 30)
            options.set_preference("network.http.response.timeout", 30)
            
            self.driver = webdriver.Firefox(options=options)
            self.wait = WebDriverWait(self.driver, 25)  # Longer timeout for proxy
            
            print("🤖 Headless Firefox with authenticated proxy started")
            return True
            
        except Exception as e:
            print(f"❌ Headless browser with proxy failed: {e}")
            return False

    def verify_ip_in_browser(self):
        """Verify the browser is using the proxy IP"""
        try:
            print("🔍 Verifying browser IP...")
            
            self.driver.get("http://httpbin.org/ip")
            time.sleep(3)
            
            page_source = self.driver.page_source
            if '"origin"' in page_source:
                # Extract IP from JSON response
                import json
                try:
                    # Find JSON in page source
                    start = page_source.find('{')
                    end = page_source.rfind('}') + 1
                    if start != -1 and end != -1:
                        json_str = page_source[start:end]
                        ip_data = json.loads(json_str)
                        browser_ip = ip_data.get('origin', 'Unknown')
                        
                        print(f"🌐 Browser IP: {browser_ip}")
                        
                        if browser_ip == self.current_ip:
                            print("✅ IP verification successful!")
                            return True
                        else:
                            print(f"⚠️ IP mismatch - Session: {self.current_ip}, Browser: {browser_ip}")
                            return True  # Still proceed
                except:
                    print("⚠️ Could not parse IP response")
                    return True  # Still proceed
            else:
                print("⚠️ Could not verify IP")
                return True  # Still proceed
                
        except Exception as e:
            print(f"⚠️ IP verification failed: {e}")
            return True  # Still proceed

    def download_captcha_with_proxy(self):
        """Download CAPTCHA using authenticated proxy"""
        try:
            print("📥 Downloading CAPTCHA (headless + proxy)...")
            
            # Load website through proxy
            self.driver.get(self.url)
            time.sleep(5)  # Extra time for proxy
            
            # Find CAPTCHA
            captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "captcha-img")))
            captcha_src = captcha_img.get_attribute("src")
            
            # Download CAPTCHA
            timestamp = datetime.now().strftime('%H%M%S')
            ip_suffix = self.current_ip.replace('.', '_') if self.current_ip else "unknown"
            captcha_path = os.path.join(self.data_dir, f'captcha_{ip_suffix}_{timestamp}.png')
            
            try:
                # Direct download through authenticated proxy
                proxies = {
                    'http': self.proxy_url,
                    'https': self.proxy_url
                }
                response = requests.get(captcha_src, proxies=proxies, verify=False, timeout=15)
                if response.status_code == 200:
                    with open(captcha_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ CAPTCHA downloaded via proxy: {captcha_path}")
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

    def fill_form_with_proxy(self, year_db, reg_year, village, captcha_solution):
        """Fill form using proxy connection"""
        try:
            print(f"📝 Filling form (headless + proxy): Mumbai {village} - {reg_year}")
            print(f"🔤 Using CAPTCHA: '{captcha_solution}'")
            print(f"🌐 Using IP: {self.current_ip}")
            
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
            
            # 4. Village selection
            village_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, "village_id"))))
            village_options = village_select.options
            
            village_found = False
            for option in village_options:
                if village.lower() in option.text.lower():
                    village_select.select_by_value(option.get_attribute('value'))
                    village_found = True
                    print(f"   ✅ Village: {option.text}")
                    break
            
            if not village_found and len(village_options) > 1:
                village_select.select_by_value(village_options[1].get_attribute('value'))
                print(f"   ✅ Village: {village_options[1].text}")
            
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
            
            print("✅ Form filled successfully with proxy!")
            return True
                
        except Exception as e:
            print(f"❌ Form filling failed: {e}")
            return False

    def submit_and_check_with_proxy(self):
        """Submit form and check results using proxy"""
        try:
            print("🚀 Submitting form (headless + proxy)...")
            
            # Submit
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            print("   📤 Form submitted via proxy!")
            
            # Wait for results (longer timeout for proxy)
            time.sleep(8)
            
            # Check results
            page_source = self.driver.page_source.lower()
            
            if any(error in page_source for error in ['invalid captcha', 'captcha error', 'wrong captcha']):
                print("   ❌ CAPTCHA was incorrect")
                return False, 0
            elif "no data available" in page_source:
                print("   ❌ No documents found")
                return False, 0
            elif "showing" in page_source and "entries" in page_source:
                print("   ✅ FOUND RESULTS!")
                
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                    doc_count = len([row for row in rows if row.get_attribute('innerHTML').strip()])
                    if doc_count > 0:
                        print(f"   📊 Found {doc_count} documents!")
                        return True, doc_count
                except:
                    pass
                
                print("   ✅ Documents found (count unknown)")
                return True, 1
            else:
                print("   ⚠️ Unknown result")
                return False, 0
                
        except Exception as e:
            print(f"❌ Submit failed: {e}")
            return False, 0

    def save_debug_info(self, params, success=False, doc_count=0):
        """Save debug information with IP info"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            status = "SUCCESS" if success else "FAILED"
            ip_suffix = self.current_ip.replace('.', '_') if self.current_ip else "unknown"
            filename = f'{status}_{params["village"]}_{params["reg_year"]}_{doc_count}docs_{ip_suffix}_{timestamp}.html'
            debug_file = os.path.join(self.data_dir, filename)
            
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- IP: {self.current_ip} -->\n")
                f.write(f"<!-- Session: {self.session_id} -->\n")
                f.write(f"<!-- Search: {params} -->\n")
                f.write(self.driver.page_source)
            
            print(f"📄 Debug saved: {debug_file}")
            
        except Exception as e:
            print(f"⚠️ Debug save failed: {e}")

    def run_ip_switching_automation(self):
        """Run complete headless automation with IP switching"""
        print("🚀 HEADLESS BROWSER AUTOMATION WITH IP SWITCHING")
        print("=" * 70)
        print("🤖 FEATURES:")
        print("   🔍 Headless browser - no visible windows")
        print("   🌐 IP switching with Thordata proxy + authentication")
        print("   📥 Automatic CAPTCHA download")
        print("   🤖 Enhanced multi-method OCR solving")
        print("   📝 Automatic form filling")
        print("   🚀 Fast execution with different IPs")
        print("=" * 70)
        
        total_documents = 0
        successful_searches = []
        ip_usage = {}
        
        for i, params in enumerate(self.searches, 1):
            print(f"\n🚀 SEARCH {i}/{len(self.searches)}")
            print(f"🔄 Mumbai {params['village']} - Year {params['reg_year']}")
            
            try:
                # Get new IP session with authentication
                if not self.get_new_ip_session():
                    print("❌ Failed to get new IP session")
                    continue
                
                # Track IP usage
                if self.current_ip in ip_usage:
                    ip_usage[self.current_ip] += 1
                else:
                    ip_usage[self.current_ip] = 1
                
                # Start headless browser with authenticated proxy
                if not self.start_headless_browser_with_proxy():
                    print("❌ Failed to start headless browser with proxy")
                    continue
                
                # Verify IP in browser
                if not self.verify_ip_in_browser():
                    print("⚠️ IP verification failed, but continuing...")
                
                # Download and solve CAPTCHA
                captcha_path = self.download_captcha_with_proxy()
                if not captcha_path:
                    print("❌ CAPTCHA download failed")
                    continue
                
                captcha_solution = self.solve_captcha_automatically(captcha_path)
                if not captcha_solution:
                    print("❌ CAPTCHA solving failed")
                    continue
                
                # Fill form
                if not self.fill_form_with_proxy(params["year_db"], params["reg_year"], params["village"], captcha_solution):
                    print("❌ Form filling failed")
                    self.save_debug_info(params, False, 0)
                    continue
                
                # Submit and check
                found_docs, doc_count = self.submit_and_check_with_proxy()
                
                if found_docs:
                    print(f"🎉 SUCCESS! Found {doc_count} documents using IP {self.current_ip}")
                    successful_searches.append({**params, "doc_count": doc_count, "ip": self.current_ip})
                    total_documents += doc_count
                    
                    self.save_debug_info(params, True, doc_count)
                    
                    # Ask if user wants to continue
                    continue_search = input(f"\n✅ Found {doc_count} documents! Continue? (y/n, default y): ").strip().lower()
                    if continue_search == 'n':
                        break
                else:
                    print(f"❌ No documents found using IP {self.current_ip}")
                    self.save_debug_info(params, False, 0)
                
                # Brief pause between searches
                if i < len(self.searches):
                    print("⏳ Waiting 5s before next search...")
                    time.sleep(5)
                
            except Exception as e:
                print(f"❌ Search {i} failed: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 HEADLESS IP SWITCHING AUTOMATION SUMMARY")
        print("=" * 70)
        
        if successful_searches:
            print(f"🎉 SUCCESS! Found documents in {len(successful_searches)} searches:")
            for result in successful_searches:
                print(f"   🏘️ Mumbai {result['village']} - Year {result['reg_year']} - {result['doc_count']} docs - IP: {result['ip']}")
            print(f"\n📊 TOTAL DOCUMENTS FOUND: {total_documents}")
        else:
            print("❌ No documents found in any search")
        
        print(f"\n🌐 IP USAGE SUMMARY:")
        for ip, count in ip_usage.items():
            print(f"   📍 {ip}: {count} searches")
        
        print(f"\n📁 All files saved in: {os.path.abspath(self.data_dir)}")
        
        return successful_searches

    def cleanup(self):
        """Clean up headless browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🧹 Headless browser closed")
        except:
            pass

def main():
    print("🚀 HEADLESS BROWSER AUTOMATION WITH IP SWITCHING")
    print("🌐 Each search uses a different IP via Thordata proxy!")
    print("🤖 Fast, automated, completely invisible!")
    
    automation = HeadlessIPSwitching()
    
    try:
        successful_results = automation.run_ip_switching_automation()
        
        if successful_results:
            print(f"\n🎉 MISSION ACCOMPLISHED!")
            print(f"Found documents in {len(successful_results)} searches using different IPs")
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