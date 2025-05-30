import requests
import logging
from typing import List, Tuple, Dict, Any
import time
import os
from datetime import datetime
from proxy_manager import ProxyManager
from bs4 import BeautifulSoup
import json
import tempfile
from PIL import Image
import re

class IGRScraper:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.base_url = "https://pay2igr.igrmaharashtra.gov.in"
        self.session = requests.Session()
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        # At the module level or in IGRSearcher.__init__
        self.TROCR_PROCESSOR = TrOCRProcessor.from_pretrained('microsoft/trocr-large-printed')
        self.TROCR_MODEL = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-printed')
        
    def download_property(self, url: str) -> str | None:
        """Download property details with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    proxies=self.proxy_manager.get_proxy(),
                    timeout=30,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
                    }
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:  # Rate limit
                    wait_time = (attempt + 1) * self.retry_delay
                    logging.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed to fetch {url}. Status: {response.status_code}")
                    
            except Exception as e:
                logging.error(f"Error downloading {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
        return None

    def save_property_data(self, content: str, property_id: str):
        """Save property data to file"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        filename = f'data/property_{property_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Saved property data to {filename}")

    def test_batch_download(self, urls: List[str]) -> Tuple[int, int]:
        """Test downloading a batch of URLs"""
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(urls, 1):
            logging.info(f"Processing URL {i}/{len(urls)}: {url}")
            
            # Extract property ID from URL if possible
            property_id = url.split('/')[-1] if url else f"unknown_{i}"
            
            content = self.download_property(url)
            if content:
                success_count += 1
                self.save_property_data(content, property_id)
            else:
                fail_count += 1
                logging.error(f"Failed to download property {property_id}")
            
            # Add delay between requests to avoid overwhelming the server
            time.sleep(2)
        
        return success_count, fail_count

    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid IGR property URL"""
        return url.startswith(self.base_url) and 'propertydetails' in url

    def run(self, urls: List[str]) -> Tuple[int, int]:
        """
        Run the scraper for a list of URLs
        Args:
            urls: List of property URLs to scrape
        Returns:
            Tuple of (success_count, failure_count)
        """
        logging.info("Starting IGR property scraper...")
        
        # Filter and validate URLs
        valid_urls = [url for url in urls if self.validate_url(url)]
        logging.info(f"Found {len(valid_urls)} valid URLs to process.")
        
        # Test batch download
        success, failure = self.test_batch_download(valid_urls)
        logging.info(f"Batch download completed. Success: {success}, Failures: {failure}")
        
        return success, failure

    def extract_property_urls(self, response_text: str) -> List[str]:
        """
        Extract property URLs from the response text
        Args:
            response_text: HTML response as text
        Returns:
            List of property URLs
        """
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            links = soup.find_all('a', {'class': 'property-link'})
            return [link['href'] for link in links]
        except Exception as e:
            logging.error(f"Error extracting property URLs: {str(e)}")
            return []

    def search_properties(self, district: str, village: str, year: int) -> List[str]:
        """
        Search for properties by village and year
        Args:
            district: District name
            village: Village name
            year: Year to search for
        Returns:
            List of property URLs
        """
        try:
            # Format the search URL with parameters
            search_url = (
                f"{self.base_url}/eSearch/propertySearch"
                f"?district={district}"
                f"&village={village}"
                f"&year={year}"
            )
            
            # Perform the search using the proxy manager
            response = self.session.get(
                search_url,
                proxies=self.proxy_manager.get_proxy(),
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
                }
            )
            
            if response.status_code == 200:
                # Parse the response and extract property URLs
                property_urls = self.extract_property_urls(response.text)
                self.save_search_results(district, village, year, property_urls)
                return property_urls
            else:
                logging.error(f"Search failed with status code: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return []

    def save_search_results(self, district: str, village: str, year: int, property_urls: List[str]) -> None:
        """
        Save search results to a JSON file
        Args:
            district: District name
            village: Village name
            year: Year
            property_urls: List of property URLs
        """
        try:
            # Create data directory if it doesn't exist
            if not os.path.exists('data'):
                os.makedirs('data')
            
            # Prepare file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/search_results_{district}_{village}_{year}_{timestamp}.json"
            
            # Prepare data to save
            search_data: Dict[str, Any] = {
                "district": district,
                "village": village,
                "year": year,
                "timestamp": timestamp,
                "property_urls": property_urls
            }
            
            # Save data to JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, indent=4)
            
            logging.info(f"Search results saved to {filename}")
            
        except Exception as e:
            logging.error(f"Error saving search results: {str(e)}")

    async def solve_and_submit_captcha(self, page, attempt_limit=5):
        for attempt in range(attempt_limit):
            try:
                logging.info(f"CAPTCHA attempt {attempt + 1}")
                captcha_image_element = page.locator("#captcha-img") # Use actual selector
                screenshot_bytes = await captcha_image_element.screenshot()
                
                # Potentially use tempfile for image instead of writing to disk
                # Or pass bytes directly to PIL.Image.open if possible after conversion
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    tmpfile.write(screenshot_bytes)
                    captcha_image_path = tmpfile.name

                img_pil = Image.open(captcha_image_path).convert("RGB")
                # Apply contrast/preprocessing if needed (test this)
                # img_pil = change_contrast(img_pil, 100) 
                
                pixel_values = self.TROCR_PROCESSOR(images=img_pil, return_tensors="pt").pixel_values
                generated_ids = self.TROCR_MODEL.generate(pixel_values)
                raw_captcha_text = self.TROCR_PROCESSOR.batch_decode(generated_ids, skip_special_tokens=True)[0]
                captcha_text = re.sub(r'\W+', '', raw_captcha_text).strip() # Cleaned CAPTCHA
                
                logging.info(f"Raw CAPTCHA: {raw_captcha_text} | Processed CAPTCHA: {captcha_text}")

                if not captcha_text: # If OCR returns empty, retry with new image
                    logging.warning("OCR returned empty CAPTCHA text. Refreshing CAPTCHA.")
                    await page.locator("//button[contains(@class, 'reloadbutton')]").click() # Use actual refresh selector
                    await page.wait_for_timeout(2000) # Wait for new CAPTCHA
                    if os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                    continue

                await page.locator("#YOUR_CAPTCHA_INPUT_SELECTOR").fill(captcha_text) # Use actual selector
                await page.locator("#YOUR_SEARCH_BUTTON_SELECTOR").click() # Use actual selector
                
                await page.wait_for_timeout(3000) # Wait for page to potentially show error or results

                # Check for CAPTCHA error
                # Use the correct selector for the error message
                if await page.locator("#YOUR_CAPTCHA_ERROR_SELECTOR:visible").count() > 0:
                    error_text = await page.locator("#YOUR_CAPTCHA_ERROR_SELECTOR").text_content()
                    logging.warning(f"CAPTCHA incorrect: {error_text}. Retrying...")
                    # Click refresh/try another CAPTCHA button if available
                    try:
                        # Example: if there's a specific "Try Again" button after error
                        # await page.locator("button:has-text('Try Again')").click()
                        # Or just refresh the main CAPTCHA image
                        await page.locator("//button[contains(@class, 'reloadbutton')]").click() # Use actual refresh selector
                        await page.wait_for_timeout(2000)
                    except Exception as e_refresh:
                        logging.error(f"Could not click refresh CAPTCHA: {e_refresh}")
                        if os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                        # If refresh fails, maybe we break or raise after some attempts
                        if attempt == attempt_limit -1: raise Exception("Failed to solve CAPTCHA after multiple retries and failed refresh")
                else:
                    # No error visible, assume success or different page state
                    logging.info("CAPTCHA submitted. Checking for results or other errors.")
                    if os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                    return True # CAPTCHA likely passed

            except Exception as e:
                logging.error(f"Error during CAPTCHA attempt {attempt + 1}: {e}", exc_info=True)
                if os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                if attempt == attempt_limit - 1:
                    raise Exception(f"Failed to solve CAPTCHA after {attempt_limit} attempts: {e}")
                # Potentially refresh CAPTCHA here too if a general error occurred
                try:
                    await page.locator("//button[contains(@class, 'reloadbutton')]").click()
                    await page.wait_for_timeout(2000)
                except:
                    pass # Ignore if refresh fails during general error
            finally:
                 if 'captcha_image_path' in locals() and os.path.exists(captcha_image_path):
                     os.remove(captcha_image_path)


        raise Exception(f"Failed to solve CAPTCHA after {attempt_limit} attempts.")

# Additional code to handle requests and integrate with the scraper
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Request and response models
class SearchRequest(BaseModel):
    district: str
    village: str
    year: int

class SearchResponse(BaseModel):
    success: bool
    message: str
    properties: List[str]
    job_id: str

# Initialize scraper
scraper = IGRScraper()

@app.post("/search-properties", response_model=SearchResponse)
async def search_properties(request: SearchRequest):
    """
    Endpoint to search for properties and run the scraper
    """
    try:
        # Generate job ID
        job_id: str = f"{request.village}_{request.year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Log the request
        logging.info(f"Received search request for village: {request.village}, year: {request.year}")

        # Search for properties using the existing scraper instance
        property_urls: List[str] = scraper.search_properties(
            district=request.district,
            village=request.village,
            year=request.year
        )

        if not property_urls:
            return SearchResponse(
                success=False,
                message="No properties found",
                properties=[],
                job_id=job_id
            )

        # Run the scraper
        success, failure = scraper.run(property_urls)

        return SearchResponse(
            success=True,
            message=f"Found {len(property_urls)} properties. Downloaded {success} successfully, {failure} failed.",
            properties=property_urls,
            job_id=job_id
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))