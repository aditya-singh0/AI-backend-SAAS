import requests
from bs4 import BeautifulSoup
from PIL import Image
from pyzbar.pyzbar import decode
import io
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from .proxy_manager import ProxyManager
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class EnhancedQRScraper:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager or ProxyManager()
        self.session = requests.Session()
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': '',
        }
        
        # CAPTCHA detection selectors (can be customized)
        self.captcha_selectors = [
            'input[name*="captcha"]',
            'img[src*="captcha"]',
            '.captcha',
            '#captcha',
            '.g-recaptcha',
            'iframe[src*="recaptcha"]'
        ]
        
    def detect_captcha(self, soup: BeautifulSoup) -> bool:
        """Detect if there's a CAPTCHA on the page"""
        for selector in self.captcha_selectors:
            if soup.select(selector):
                return True
        return False
    
    def add_custom_captcha_selector(self, selector: str):
        """Add a custom CAPTCHA selector"""
        if selector not in self.captcha_selectors:
            self.captcha_selectors.append(selector)
            logger.info(f"Added custom CAPTCHA selector: {selector}")
    
    def handle_captcha_page(self, url: str, soup: BeautifulSoup) -> bool:
        """Handle CAPTCHA detection and provide user guidance"""
        if self.detect_captcha(soup):
            print(f"\n🚨 CAPTCHA detected on {url}")
            print("=" * 50)
            print("The website has anti-bot protection (CAPTCHA).")
            print("\nOptions:")
            print("1. Open the website manually in a browser")
            print("2. Solve the CAPTCHA manually")
            print("3. Try accessing a different page")
            print("4. Use browser automation tools like Selenium")
            
            user_choice = input("\nDo you want to continue anyway? (y/n): ").lower().strip()
            if user_choice == 'y':
                print("Continuing despite CAPTCHA presence...")
                return True
            else:
                print("Stopping due to CAPTCHA.")
                return False
        return True
    
    def extract_qr_from_image_url(self, image_url: str) -> List[str]:
        """Extract QR code data from an image URL"""
        try:
            # Get proxy configuration if available
            proxies = self.proxy_manager.get_proxy()
            
            # Download the image with session for cookie persistence
            response = self.session.get(
                image_url, 
                proxies=proxies,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            # Open the image using PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary for better QR detection
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            # Decode QR codes
            decoded_objects = decode(image)
            
            # Extract and return QR code data
            qr_data = [obj.data.decode('utf-8') for obj in decoded_objects]
            
            if qr_data:
                logger.info(f"Found {len(qr_data)} QR codes in image: {image_url}")
            
            return qr_data
            
        except Exception as e:
            logger.error(f"Error extracting QR code from {image_url}: {str(e)}")
            return []

    def scrape_qr_codes_from_webpage(self, url: str, handle_captcha: bool = True) -> List[Dict[str, str]]:
        """Scrape all QR codes found in images on a webpage with CAPTCHA handling"""
        try:
            # Get proxy configuration if available
            proxies = self.proxy_manager.get_proxy()
            
            # Set referer
            self.headers['Referer'] = url
            
            print(f"🌐 Fetching webpage: {url}")
            
            # Fetch the webpage with session for cookie persistence
            response = self.session.get(
                url, 
                proxies=proxies,
                headers=self.headers,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            
            print(f"✅ Successfully fetched webpage (Status: {response.status_code})")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Handle CAPTCHA if detected
            if handle_captcha and not self.handle_captcha_page(url, soup):
                return []
            
            # Find all image tags
            images = soup.find_all('img')
            print(f"🔍 Found {len(images)} images on the page")
            
            results = []
            for i, img in enumerate(images, 1):
                img_url = img.get('src', '')
                
                if img_url:
                    # Use urljoin to properly handle relative URLs
                    full_img_url = urljoin(url, img_url)
                    
                    print(f"📷 Checking image {i}/{len(images)}: {full_img_url}")
                    
                    qr_data = self.extract_qr_from_image_url(full_img_url)
                    if qr_data:
                        results.append({
                            'image_url': full_img_url,
                            'qr_contents': qr_data
                        })
                        print(f"✅ Found QR code in image {i}!")
                    
                    # Small delay to be respectful to the server
                    time.sleep(0.5)
            
            logger.info(f"Found QR codes in {len(results)} images on {url}")
            return results
            
        except Exception as e:
            logger.error(f"Error scraping QR codes from {url}: {str(e)}")
            return []
    
    def scrape_with_session_management(self, base_url: str, navigation_steps: List[Dict] = None) -> List[Dict[str, str]]:
        """
        Advanced scraping with session management for multi-step navigation
        navigation_steps: List of dicts with 'url', 'method', 'data', etc.
        """
        try:
            if navigation_steps:
                print("🚀 Starting multi-step navigation...")
                
                for i, step in enumerate(navigation_steps, 1):
                    print(f"Step {i}: {step.get('description', 'Navigating...')}")
                    
                    if step.get('method', 'GET').upper() == 'POST':
                        response = self.session.post(
                            step['url'],
                            data=step.get('data', {}),
                            headers=self.headers,
                            verify=False,
                            timeout=30
                        )
                    else:
                        response = self.session.get(
                            step['url'],
                            headers=self.headers,
                            verify=False,
                            timeout=30
                        )
                    
                    response.raise_for_status()
                    print(f"✅ Step {i} completed (Status: {response.status_code})")
                    
                    # Small delay between steps
                    time.sleep(1)
            
            # Final scraping step
            return self.scrape_qr_codes_from_webpage(base_url, handle_captcha=True)
            
        except Exception as e:
            logger.error(f"Error in session management scraping: {str(e)}")
            return [] 