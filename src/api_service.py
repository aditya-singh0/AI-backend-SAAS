from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from bs4.element import Tag  # Import Tag for type hinting
from src.proxy_manager import ProxyManager
from contextlib import asynccontextmanager
import os
from enum import Enum
# Playwright and OCR imports
from playwright.async_api import Playwright, async_playwright
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import tempfile
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('igr_scraper.log')
    ]
)
logger = logging.getLogger(__name__)

class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class SearchRequest(BaseModel):
    year: int = Field(..., ge=2000, le=2030, description="Year to search for")
    village: str = Field(..., min_length=1, max_length=100, description="Village name")
    district: Optional[str] = Field(default="Mumbai", description="District name")
    
    @validator('village')
    def validate_village(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Village name cannot be empty')
        return v.strip()

class SearchResponse(BaseModel):
    success: bool
    message: str
    properties: List[str] = []
    job_id: Optional[str] = None
    total_found: int = 0
    processed: int = 0

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    total_properties: int = 0
    processed_properties: int = 0
    created_at: datetime
    updated_at: datetime

# Global variables for job tracking
job_store: Dict[str, Dict[str, Any]] = {}

# Load OCR model and processor once
trocr_processor = None
trocr_model = None

def load_ocr_model():
    global trocr_processor, trocr_model
    if trocr_processor is None or trocr_model is None:
        logging.info("Loading TROCR model...")
        trocr_processor, _ = TrOCRProcessor.from_pretrained('microsoft/trocr-large-printed')
        trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-printed')
        logging.info("TROCR model loaded.")

class IGRSearcher:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.base_domain = "https://pay2igr.igrmaharashtra.gov.in"
        self.search_page_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
        load_ocr_model() # Ensure model is loaded

    def extract_property_urls(self, response_text: str) -> List[str]:
        """Extract property URLs from the response text"""
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            
            selectors = [
                'a.property-link',
                'a[href*="property"]',
                'a[href*="document"]',
                '.property-row a',
                '.result-item a'
            ]
            
            property_urls: List[str] = []
            for selector in selectors:
                links: List[Tag] = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if isinstance(href, str) and href:
                        if href.startswith('/'):
                            href = self.base_domain + href
                        property_urls.append(href)
                        
                if property_urls:
                    break
                    
            seen: set[str] = set()
            unique_urls: List[str] = []
            for url in property_urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)
                    
            logger.info(f"Extracted {len(unique_urls)} property URLs")
            return unique_urls
            
        except Exception as e:
            logger.error(f"Error extracting property URLs: {str(e)}")
            return []

    async def search_properties(self, district: str, village: str, year: int, max_retries: int = 3) -> List[str]:
        """Search for properties by village and year with retry logic using Playwright and CAPTCHA solving."""
        logging.info(f"Playwright search for District: {district}, Village: {village}, Year: {year} - To be implemented.")
        return []

    async def solve_and_submit_captcha_playwright(self, page, attempt_limit=5):
        logging.info("solve_and_submit_captcha_playwright - To be implemented.")
        for attempt in range(attempt_limit):
            try:
                logging.info(f"CAPTCHA attempt {attempt + 1}")
                captcha_image_element = page.locator("#captcha-img")
                screenshot_bytes = await captcha_image_element.screenshot()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    tmpfile.write(screenshot_bytes)
                    captcha_image_path = tmpfile.name

                img_pil = Image.open(captcha_image_path).convert("RGB")
                
                pixel_values = trocr_processor(images=img_pil, return_tensors="pt").pixel_values
                generated_ids = trocr_model.generate(pixel_values)
                raw_captcha_text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                captcha_text = re.sub(r'\W+', '', raw_captcha_text).strip()
                
                logging.info(f"Raw CAPTCHA: {raw_captcha_text} | Processed CAPTCHA: {captcha_text}")

                if not captcha_text:
                    logging.warning("OCR returned empty CAPTCHA text. Refreshing CAPTCHA.")
                    await page.locator("button.reloadbutton").click()
                    await page.wait_for_timeout(2000)
                    if os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                    continue

                await page.fill("#txtcaptcha", captcha_text)
                await page.click("#btnSearch")
                await page.wait_for_timeout(4000)

                if await page.locator("div.message.error:visible").count() > 0:
                    error_text = await page.locator("div.message.error").text_content()
                    logging.warning(f"CAPTCHA incorrect: {error_text}. Retrying...")
                    await page.locator("button.reloadbutton").click()
                    await page.wait_for_timeout(2000)
                else:
                    logging.info("CAPTCHA submitted successfully.")
                    if os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                    return True
            except Exception as e:
                logging.error(f"Error during CAPTCHA attempt {attempt + 1}: {e}", exc_info=True)
                if 'captcha_image_path' in locals() and os.path.exists(captcha_image_path): os.remove(captcha_image_path)
                if attempt == attempt_limit - 1:
                    logging.error(f"Failed to solve CAPTCHA after {attempt_limit} attempts.")
                    return False
                try:
                    await page.locator("button.reloadbutton").click()
                    await page.wait_for_timeout(2000)
                except: pass
            finally:
                 if 'captcha_image_path' in locals() and os.path.exists(captcha_image_path):
                     os.remove(captcha_image_path)
        return False

class IGRScraper:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        })

    async def scrape_property(self, url: str) -> Optional[str]:
        """Scrape a single property URL"""
        proxy = self.proxy_manager.get_proxy()

        try:
            if proxy:
                response = self.session.get(url, proxies=proxy, timeout=30)
            else:
                response = self.session.get(url, timeout=30)
                
            response.raise_for_status() # Raise HTTPError for bad responses
            self.logger.info(f"Successfully scraped {url}")
            return response.text
        except RequestException as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None

    async def process_batch(self, urls: List[str], job_id: str) -> tuple[int, int]:
        """Process a batch of property URLs and save locally"""
        success_count = 0
        fail_count = 0
        
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        for url in urls:
            html_content = await self.scrape_property(url)
            if html_content:
                try:
                    # Generate a unique filename based on URL or a hash
                    # For simplicity, using a part of the URL and timestamp
                    filename = f"{data_dir}/property_{job_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    self.logger.info(f"Saved {url} to {filename}")
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Error saving content for {url}: {e}")
                    fail_count += 1
            else:
                fail_count += 1
        
        return success_count, fail_count

# Job management functions
def create_job(job_id: str, total_properties: int) -> None:
    """Create a new job entry"""
    job_store[job_id] = {
        "status": JobStatus.PENDING,
        "message": "Job created",
        "total_properties": total_properties,
        "processed_properties": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

def update_job(job_id: str, status: Optional[JobStatus] = None, message: Optional[str] = None, processed: Optional[int] = None) -> None:
    """Update job status"""
    if job_id in job_store:
        job = job_store[job_id]
        if status is not None:
            job["status"] = status
        if message is not None:
            job["message"] = message
        if processed is not None:
            job["processed_properties"] = processed
        job["updated_at"] = datetime.now()

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job status"""
    return job_store.get(job_id)

# Background task for processing properties
async def process_properties_background(
    job_id: str,
    property_urls: List[str],
    scraper: IGRScraper # Changed type hint back to IGRScraper
):
    """Background task to process property URLs"""
    try:
        update_job(job_id, status=JobStatus.IN_PROGRESS, message="Processing properties")
        
        total_processed = 0
        total_failed = 0
        
        # Limit to first 1000 URLs
        urls_to_process = property_urls[:1000]

        if not urls_to_process:
             update_job(job_id, status=JobStatus.COMPLETED, message="No URLs to process")
             return

        success, fails = await scraper.process_batch(urls_to_process, job_id)
        
        total_processed += success
        total_failed += fails
        
        update_job(job_id, processed=total_processed)
        
        # Update final status
        if total_failed == 0:
            update_job(
                job_id, 
                status=JobStatus.COMPLETED, 
                message=f"Successfully processed all {total_processed} properties"
            )
        else:
            update_job(
                job_id, 
                status=JobStatus.COMPLETED, 
                message=f"Processed {total_processed} properties, {total_failed} failed"
            )
        
    except Exception as e:
        logger.error(f"Error in background processing for job {job_id}: {e}")
        update_job(job_id, status=JobStatus.FAILED, message=f"Background processing failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("IGR Property Scraper API started")
    yield
    # Shutdown
    logger.info("IGR Property Scraper API shutting down")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get IGRScraper instance
def get_scraper() -> IGRScraper:
    return IGRScraper()

@app.get("/")
async def root():
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_properties(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    scraper: IGRScraper = Depends(get_scraper) # Inject IGRScraper
):
    """Search for properties and start background processing"""
    try:
        # Initialize components
        searcher = IGRSearcher()
        
        # Log the request
        logging.info(f"Received search request for village: {request.village}, year: {request.year}")

        # Search for properties
        property_urls: List[str] = await searcher.search_properties(
            district=str(request.district),
            village=request.village,
            year=request.year
        )

        if not property_urls:
            return SearchResponse(
                success=False,
                message="No properties found",
                properties=[],
                job_id=None, # No job created if no properties found
                total_found=0,
                processed=0
            )

        # Generate job ID
        job_id: str = f"{request.village}_{request.year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logging.info(f"Generated job ID: {job_id}")

        # Create job entry
        create_job(job_id, len(property_urls))
        
        # Start background processing
        background_tasks.add_task(
            process_properties_background,
            job_id,
            property_urls,
            scraper
        )

        return SearchResponse(
            success=True,
            message=f"Found {len(property_urls)} properties. Processing started in background.",
            properties=property_urls[:10], # Return first 10 found URLs in response
            job_id=job_id,
            total_found=len(property_urls),
            processed=0 # Processing starts in background
        )

    except Exception as e:
        logging.error(f"Error processing search request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/v1/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status_endpoint(job_id: str):
    """Get job status by ID"""
    job_status = get_job_status(job_id)
    if job_status:
        return JobStatusResponse(
            job_id=job_id,
            status=job_status["status"],
            message=job_status["message"],
            total_properties=job_status["total_properties"],
            processed_properties=job_status["processed_properties"],
            created_at=job_status["created_at"],
            updated_at=job_status["updated_at"]
        )
    raise HTTPException(status_code=404, detail="Job not found")

@app.get("/api/v1/jobs", response_model=List[JobStatusResponse])
async def list_jobs():
    """List all jobs"""
    return [
        JobStatusResponse(
            job_id=job_id,
            status=job_data["status"],
            message=job_data["message"],
            total_properties=job_data["total_properties"],
            processed_properties=job_data["processed_properties"],
            created_at=job_data["created_at"],
            updated_at=job_data["updated_at"]
        )
        for job_id, job_data in job_store.items()
    ]