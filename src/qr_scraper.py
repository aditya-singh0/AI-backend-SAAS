import requests
from bs4 import BeautifulSoup
from PIL import Image
from pyzbar.pyzbar import decode
import io
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from .proxy_manager import ProxyManager
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class QRScraper:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager or ProxyManager()
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
    def extract_qr_from_image_url(self, image_url: str) -> List[str]:
        """
        Extract QR code data from an image URL
        Returns a list of decoded QR code contents
        """
        try:
            # Get proxy configuration if available
            proxies = self.proxy_manager.get_proxy()
            
            # Download the image with SSL verification disabled and headers
            response = requests.get(
                image_url, 
                proxies=proxies,
                headers=self.headers,
                verify=False,  # Disable SSL verification
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
            else:
                logger.info(f"No QR codes found in image: {image_url}")
                
            return qr_data
            
        except Exception as e:
            logger.error(f"Error extracting QR code from {image_url}: {str(e)}")
            return []

    def scrape_qr_codes_from_webpage(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape all QR codes found in images on a webpage
        Returns a list of dictionaries containing image URLs and their QR code contents
        """
        try:
            # Get proxy configuration if available
            proxies = self.proxy_manager.get_proxy()
            
            # Fetch the webpage with SSL verification disabled and headers
            response = requests.get(
                url, 
                proxies=proxies,
                headers=self.headers,
                verify=False,  # Disable SSL verification
                timeout=30
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all image tags
            images = soup.find_all('img')
            
            results = []
            for img in images:
                img_url = img.get('src', '')
                
                if img_url:
                    # Use urljoin to properly handle relative URLs
                    full_img_url = urljoin(url, img_url)
                    
                    qr_data = self.extract_qr_from_image_url(full_img_url)
                    if qr_data:
                        results.append({
                            'image_url': full_img_url,
                            'qr_contents': qr_data
                        })
            
            logger.info(f"Found QR codes in {len(results)} images on {url}")
            return results
            
        except Exception as e:
            logger.error(f"Error scraping QR codes from {url}: {str(e)}")
            return [] 