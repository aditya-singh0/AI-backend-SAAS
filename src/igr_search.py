from typing import List
import logging
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from igr_scraper import IGRScraper
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add current directory to PYTHONPATH
# Define the IGRSearcher class directly if the module is not available
class IGRSearcher:
    def search_properties(self, district: str, village: str, year: int) -> List[str]:
        # Search for properties in the IGR system
        try:
            # TODO: Implement actual IGR property search logic
            # For now, return a mock URL
            return [f"https://example.com/{district}/{village}/{year}"]
        except Exception as e:
            logging.error(f"Error searching properties: {str(e)}")
            return []

class SearchRequest(BaseModel):
    year: int
    village: str
    district: Optional[str] = "Mumbai"

class SearchResponse(BaseModel):
    success: bool
    message: str
    properties: List[str] = []
    job_id: Optional[str] = None

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_properties(request: SearchRequest):
    try:
        # Initialize components
        searcher: IGRSearcher = IGRSearcher()
        scraper: IGRScraper = IGRScraper()

        # Generate job ID
        job_id: str = f"{request.village}_{request.year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logging.info(f"Generated job ID: {job_id}")

        # Log the request
        logging.info(f"Received search request for village: {request.village}, year: {request.year}")

        # Search for properties
        property_urls: List[str] = searcher.search_properties(
            district=str(request.district),
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
        scraper.run(property_urls)

        return SearchResponse(
            success=True,
            message=f"Found {len(property_urls)} properties. Scraper run completed.",
            properties=property_urls,
            job_id=job_id
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))