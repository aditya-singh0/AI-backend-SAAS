#!/usr/bin/env python3

import sys
import os
import time
from datetime import datetime

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import cv2
import numpy as np

class CAPTCHAHelperScraper(IGRSpecializedScraper):
    def __init__(self, proxy_manager=None):
        super().__init__(proxy_manager)
        self.captcha_attempts = 0
        self.max_attempts = 5
        
    def preprocess_captcha_image(self, image_path):
        """Preprocess CAPTCHA image for better OCR recognition"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get binary image
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Remove noise
            kernel = np.ones((2,2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Save preprocessed image
            preprocessed_path = 'captcha_preprocessed.png'
            cv2.imwrite(preprocessed_path, cleaned)
            
            return preprocessed_path
            
        except Exception as e:
            print(f"Error preprocessing CAPTCHA: {e}")
            return image_path
    
    def suggest_captcha_text(self, image_path):
        """Use OCR to suggest what the CAPTCHA text might be"""
        try:
            # Preprocess the image
            preprocessed_path = self.preprocess_captcha_image(image_path)
            
            # Configure tesseract for CAPTCHA
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            
            # Try OCR on original
            text1 = pytesseract.image_to_string(Image.open(image_path), config=custom_config).strip()
            
            # Try OCR on preprocessed
            text2 = pytesseract.image_to_string(Image.open(preprocessed_path), config=custom_config).strip()
            
            suggestions = []
            if text1:
                suggestions.append(text1)
            if text2 and text2 != text1:
                suggestions.append(text2)
                
            return suggestions
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return []
    
    def enhanced_captcha_handling(self, soup, base_url, form_data):
        """Enhanced CAPTCHA handling with retry logic and OCR suggestions"""
        max_retries = self.max_attempts
        
        for attempt in range(1, max_retries + 1):
            print(f"\n🔄 CAPTCHA Attempt #{attempt} of {max_retries}")
            print("=" * 50)
            
            # Get fresh CAPTCHA
            captcha_url = self.get_captcha_image_url(soup, base_url)
            if not captcha_url:
                print("❌ No CAPTCHA found")
                return False
                
            # Download CAPTCHA with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            captcha_filename = f'captcha_{timestamp}_attempt{attempt}.png'
            
            try:
                response = self.session.get(
                    captcha_url,
                    headers=self.headers,
                    verify=False,
                    timeout=30
                )
                response.raise_for_status()
                
                # Save CAPTCHA
                with open(captcha_filename, 'wb') as f:
                    f.write(response.content)
                
                # Also save as main captcha_image.png
                with open('captcha_image.png', 'wb') as f:
                    f.write(response.content)
                    
                print(f"✅ CAPTCHA saved as: {captcha_filename}")
                
                # Try OCR suggestions
                suggestions = self.suggest_captcha_text(captcha_filename)
                
                if suggestions:
                    print(f"\n🤖 OCR Suggestions:")
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"   {i}. {suggestion}")
                    print(f"\n💡 Note: OCR suggestions may not be accurate for distorted CAPTCHAs")
                else:
                    print(f"\n❌ OCR couldn't read the CAPTCHA clearly")
                
                # Show CAPTCHA info
                img = Image.open(captcha_filename)
                print(f"\n📷 CAPTCHA Image Info:")
                print(f"   Size: {img.size}")
                print(f"   Mode: {img.mode}")
                print(f"   Format: {img.format}")
                
                # Get user input
                print(f"\n📝 Please check '{captcha_filename}' and enter the CAPTCHA text")
                print(f"   (Or try one of the OCR suggestions above)")
                
                captcha_text = input("CAPTCHA text: ").strip()
                
                if not captcha_text:
                    print("❌ No CAPTCHA text entered")
                    continue
                    
                # Store CAPTCHA text
                form_data['captchaTextBox'] = captcha_text
                print(f"✅ Entered CAPTCHA: {captcha_text}")
                
                # Try to submit and check if CAPTCHA was correct
                print(f"\n🚀 Testing CAPTCHA...")
                
                # Submit form
                test_response = self.session.post(
                    base_url,
                    data=form_data,
                    headers=self.headers,
                    verify=False,
                    timeout=30
                )
                
                # Check if CAPTCHA was accepted
                if test_response.status_code == 200:
                    test_soup = BeautifulSoup(test_response.text, 'html.parser')
                    
                    # Check for CAPTCHA error messages
                    error_indicators = [
                        'incorrect captcha',
                        'wrong captcha',
                        'invalid captcha',
                        'कॅप्चा',
                        'चुकीचा',
                        'captcha error'
                    ]
                    
                    response_text = test_response.text.lower()
                    captcha_failed = any(error in response_text for error in error_indicators)
                    
                    # Also check if we're still on the same form page
                    still_on_form = test_soup.select_one('input#captchaTextBox') is not None
                    
                    if not captcha_failed and not still_on_form:
                        print(f"✅ CAPTCHA appears to be CORRECT!")
                        print(f"🎉 Successfully passed CAPTCHA on attempt #{attempt}")
                        
                        # Save successful CAPTCHA for reference
                        success_filename = f'captcha_SUCCESS_{timestamp}.png'
                        os.rename(captcha_filename, success_filename)
                        print(f"📁 Successful CAPTCHA saved as: {success_filename}")
                        
                        return True
                    else:
                        print(f"❌ CAPTCHA was INCORRECT")
                        if attempt < max_retries:
                            print(f"🔄 Refreshing for new CAPTCHA...")
                            time.sleep(2)  # Wait before retry
                            
                            # Reload page to get new CAPTCHA
                            response = self.session.get(
                                base_url,
                                headers=self.headers,
                                verify=False,
                                timeout=30
                            )
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # Update form data with new CSRF token
                            new_form_data = self.get_form_data(soup)
                            form_data['_csrfToken'] = new_form_data.get('_csrfToken', form_data.get('_csrfToken'))
                
            except Exception as e:
                print(f"❌ Error in CAPTCHA attempt {attempt}: {e}")
                continue
        
        print(f"\n❌ Failed to solve CAPTCHA after {max_retries} attempts")
        return False
    
    def mumbai_search_with_captcha_helper(self):
        """Mumbai search with enhanced CAPTCHA handling"""
        print("🏙️ Mumbai IGR Scraper with CAPTCHA Helper")
        print("=" * 70)
        print("Features:")
        print("✅ OCR suggestions for CAPTCHA text")
        print("✅ Multiple retry attempts")
        print("✅ Automatic success detection")
        print("✅ Saves all CAPTCHA images with timestamps")
        print("=" * 70)
        
        igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        
        try:
            # Load the page
            print("🌐 Loading IGR website...")
            response = self.session.get(
                igr_url,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✅ Page loaded successfully")
            
            # Get form data
            form_data = self.get_form_data(soup)
            
            # Get year
            year = input("\nEnter year (e.g., 2023, 2024): ").strip() or "2024"
            
            # Set up Mumbai search parameters
            print(f"\n🔍 Setting up Mumbai search parameters...")
            
            # You would set district_id, taluka_id, article_id here based on the dropdowns
            # For now, let's assume these are set
            
            # Handle CAPTCHA with enhanced logic
            if self.detect_igr_captcha(soup):
                print(f"\n🚨 CAPTCHA detected! Starting enhanced CAPTCHA handler...")
                
                captcha_success = self.enhanced_captcha_handling(soup, igr_url, form_data)
                
                if captcha_success:
                    print(f"\n✅ CAPTCHA solved successfully!")
                    print(f"🎯 Proceeding with form submission...")
                    
                    # Now submit the actual search
                    results = self.submit_form_and_scrape(igr_url, form_data)
                    
                    if results:
                        print(f"\n🎉 Found {len(results)} QR codes!")
                        for result in results:
                            print(f"QR: {result['qr_contents']}")
                    else:
                        print(f"\n❌ No QR codes found in results")
                else:
                    print(f"\n❌ Could not solve CAPTCHA after multiple attempts")
                    
            else:
                print("No CAPTCHA detected, proceeding with search...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def main():
    # Check if required libraries are installed
    try:
        import pytesseract
        import cv2
    except ImportError:
        print("❌ Missing required libraries for OCR!")
        print("Please install:")
        print("pip install pytesseract opencv-python")
        print("Also install tesseract-ocr system package")
        return
    
    scraper = CAPTCHAHelperScraper()
    scraper.mumbai_search_with_captcha_helper()

if __name__ == "__main__":
    main() 