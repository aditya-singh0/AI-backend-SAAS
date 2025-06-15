import requests
from bs4 import BeautifulSoup
from PIL import Image
from pyzbar.pyzbar import decode
import io
import logging
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from .proxy_manager import ProxyManager
from .enhanced_proxy_manager import EnhancedProxyManager
import urllib3
import base64

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class IGRSpecializedScraper:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None, use_proxy: bool = True):
        # Use enhanced proxy manager for better IP rotation
        if use_proxy:
            self.proxy_manager = EnhancedProxyManager()
        else:
            self.proxy_manager = proxy_manager or ProxyManager()
        
        self.session = requests.Session()
        self.use_proxy = use_proxy
        self.sticky_session_id = None  # For maintaining same IP during form submission
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # IGR Website specific selectors based on user's screenshots
        self.igr_selectors = {
            'captcha_img': 'img#captcha-img',
            'captcha_input': 'input#captchaTextBox',
            'district_select': 'select#district_id',
            'taluka_select': 'select#taluka_id', 
            'village_select': 'select#village_id',
            'article_select': 'select#article_id',
            'db_select': 'select#dbselect',
            'form': 'form',
            'submit_button': 'input[type="submit"], button[type="submit"]'
        }
        
    def detect_igr_captcha(self, soup: BeautifulSoup) -> bool:
        """Detect if IGR CAPTCHA is present"""
        captcha_img = soup.select(self.igr_selectors['captcha_img'])
        captcha_input = soup.select(self.igr_selectors['captcha_input'])
        return bool(captcha_img and captcha_input)
    
    def get_captcha_image_url(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract CAPTCHA image URL"""
        captcha_img = soup.select_one(self.igr_selectors['captcha_img'])
        if captcha_img and captcha_img.get('src'):
            return urljoin(base_url, captcha_img['src'])
        return None
    
    def download_and_show_captcha(self, captcha_url: str) -> bool:
        """Download CAPTCHA image and save it for user to view"""
        try:
            # Get proxy configuration (use sticky session for captcha)
            proxy_config = None
            if self.use_proxy and hasattr(self.proxy_manager, 'get_sticky_proxy'):
                if not self.sticky_session_id:
                    self.sticky_session_id = self.proxy_manager.generate_session_id()
                proxy_config = self.proxy_manager.get_sticky_proxy(self.sticky_session_id)
                print(f"🔄 Using proxy with session: {self.sticky_session_id}")
            
            response = self.session.get(
                captcha_url,
                headers=self.headers,
                proxies=proxy_config,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            # Save CAPTCHA image
            with open('captcha_image.png', 'wb') as f:
                f.write(response.content)
            
            print(f"✅ CAPTCHA image saved as 'captcha_image.png'")
            print(f"📷 CAPTCHA URL: {captcha_url}")
            
            # Try to display dimensions and basic info
            try:
                img = Image.open(io.BytesIO(response.content))
                print(f"📐 Image size: {img.size}")
                print(f"🎨 Image mode: {img.mode}")
            except Exception as e:
                print(f"Could not analyze image: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading CAPTCHA: {e}")
            return False
    
    def get_form_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract form data and available options"""
        form_data = {}
        
        # Get all form inputs
        form = soup.select_one(self.igr_selectors['form'])
        if not form:
            print("❌ No form found on the page")
            return form_data
        
        # Extract hidden inputs
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        for inp in hidden_inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                form_data[name] = value
                print(f"🔒 Hidden field: {name} = {value}")
        
        # Extract dropdown options
        for selector_name, selector in self.igr_selectors.items():
            if 'select' in selector_name:
                select_elem = soup.select_one(selector)
                if select_elem:
                    options = select_elem.find_all('option')
                    if options:
                        print(f"\n📋 {selector_name.replace('_', ' ').title()} options:")
                        for option in options[:10]:  # Show first 10 options
                            value = option.get('value', '')
                            text = option.get_text(strip=True)
                            print(f"   - {value}: {text}")
                        if len(options) > 10:
                            print(f"   ... and {len(options) - 10} more options")
        
        return form_data
    
    def interactive_form_filling(self, soup: BeautifulSoup, base_url: str) -> Optional[Dict[str, str]]:
        """Interactive form filling with user input"""
        print("\n🔧 IGR Form Configuration")
        print("=" * 50)
        
        # Get base form data
        form_data = self.get_form_data(soup)
        
        # Handle CAPTCHA
        if self.detect_igr_captcha(soup):
            captcha_url = self.get_captcha_image_url(soup, base_url)
            if captcha_url:
                print(f"\n🚨 CAPTCHA detected!")
                if self.download_and_show_captcha(captcha_url):
                    print("\n📝 Please solve the CAPTCHA:")
                    print("1. Open 'captcha_image.png' to view the CAPTCHA")
                    print("2. Enter the CAPTCHA text below")
                    
                    captcha_text = input("\nEnter CAPTCHA text: ").strip()
                    if captcha_text:
                        form_data['captchaTextBox'] = captcha_text
                        print(f"✅ CAPTCHA entered: {captcha_text}")
                    else:
                        print("❌ No CAPTCHA text provided")
                        return None
        
        # Get dropdown selections
        print("\n📋 Form Field Selection:")
        print("You can either:")
        print("1. Skip field selection (press Enter)")
        print("2. Provide specific values")
        
        # District selection
        district_input = input("\nEnter District ID (or press Enter to skip): ").strip()
        if district_input:
            form_data['district_id'] = district_input
        
        # Taluka selection  
        taluka_input = input("Enter Taluka ID (or press Enter to skip): ").strip()
        if taluka_input:
            form_data['taluka_id'] = taluka_input
            
        # Village selection
        village_input = input("Enter Village ID (or press Enter to skip): ").strip()
        if village_input:
            form_data['village_id'] = village_input
            
        # Article selection
        article_input = input("Enter Article ID (or press Enter to skip): ").strip()
        if article_input:
            form_data['article_id'] = article_input
            
        # Database selection
        db_input = input("Enter Database selection (or press Enter to skip): ").strip()
        if db_input:
            form_data['dbselect'] = db_input
        
        return form_data
    
    def submit_form_and_scrape(self, base_url: str, form_data: Dict[str, str]) -> List[Dict[str, str]]:
        """Submit form and scrape resulting page for QR codes"""
        try:
            print(f"\n🚀 Submitting form to: {base_url}")
            print("Form data:", {k: v for k, v in form_data.items() if 'captcha' not in k.lower()})
            
            # Get proxy configuration (use sticky session for form submission)
            proxy_config = None
            if self.use_proxy and hasattr(self.proxy_manager, 'get_sticky_proxy'):
                if self.sticky_session_id:
                    proxy_config = self.proxy_manager.get_sticky_proxy(self.sticky_session_id)
                    print(f"🔄 Continuing with same IP session: {self.sticky_session_id}")
                else:
                    proxy_config = self.proxy_manager.get_proxy(rotate_ip=True)
                    print("🔄 Using new IP for form submission")
            
            # Submit form
            response = self.session.post(
                base_url,
                data=form_data,
                headers=self.headers,
                proxies=proxy_config,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            print(f"✅ Form submitted successfully (Status: {response.status_code})")
            
            # Parse response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for QR codes in the response
            return self.scrape_qr_codes_from_soup(soup, base_url)
            
        except Exception as e:
            print(f"❌ Error submitting form: {e}")
            return []
    
    def scrape_qr_codes_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Scrape QR codes from BeautifulSoup object"""
        images = soup.find_all('img')
        print(f"🔍 Found {len(images)} images in response")
        
        results = []
        for i, img in enumerate(images, 1):
            img_url = img.get('src', '')
            
            if img_url:
                full_img_url = urljoin(base_url, img_url)
                print(f"📷 Checking image {i}/{len(images)}: {full_img_url}")
                
                qr_data = self.extract_qr_from_image_url(full_img_url)
                if qr_data:
                    results.append({
                        'image_url': full_img_url,
                        'qr_contents': qr_data
                    })
                    print(f"✅ Found QR code in image {i}!")
                
                time.sleep(0.5)  # Be respectful
        
        return results
    
    def extract_qr_from_image_url(self, image_url: str) -> List[str]:
        """Extract QR code data from an image URL"""
        try:
            # Get proxy configuration (can rotate IP for each image)
            proxy_config = None
            if self.use_proxy and hasattr(self.proxy_manager, 'get_proxy'):
                proxy_config = self.proxy_manager.get_proxy(rotate_ip=True)
                print(f"🔄 Downloading image with rotated IP")
            
            response = self.session.get(
                image_url,
                headers=self.headers,
                proxies=proxy_config,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            decoded_objects = decode(image)
            qr_data = [obj.data.decode('utf-8') for obj in decoded_objects]
            
            return qr_data
            
        except Exception as e:
            logger.error(f"Error extracting QR code from {image_url}: {str(e)}")
            return []
    
    def full_igr_workflow(self, igr_url: str) -> List[Dict[str, str]]:
        """Complete IGR website workflow"""
        try:
            print("🔍 Maharashtra IGR QR Code Scraper") 
            print("=" * 60)
            
            # Test proxy connection if enabled
            if self.use_proxy and hasattr(self.proxy_manager, 'test_proxy_connection'):
                print("\n🔧 Testing proxy connection...")
                test_result = self.proxy_manager.test_proxy_connection()
                if test_result.get('success'):
                    print(f"✅ Proxy test successful! IP: {test_result.get('ip')}")
                else:
                    print(f"⚠️ Proxy test failed: {test_result.get('error')}")
            
            # Step 1: Load initial page
            print(f"\n🌐 Loading IGR website: {igr_url}")
            
            # Get proxy configuration for initial request
            proxy_config = None
            if self.use_proxy and hasattr(self.proxy_manager, 'get_proxy'):
                proxy_config = self.proxy_manager.get_proxy(rotate_ip=True)
                print("🔄 Using proxy for initial page load")
            
            response = self.session.get(
                igr_url,
                headers=self.headers,
                proxies=proxy_config,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"✅ Page loaded successfully")
            
            # Step 2: Interactive form filling
            form_data = self.interactive_form_filling(soup, igr_url)
            
            if not form_data:
                print("❌ Form filling cancelled or failed")
                return []
            
            # Step 3: Submit form and scrape results
            return self.submit_form_and_scrape(igr_url, form_data)
            
        except Exception as e:
            print(f"❌ Error in IGR workflow: {e}")
            import traceback
            traceback.print_exc()
            return [] 