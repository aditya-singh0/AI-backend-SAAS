import logging
from datetime import datetime
import os
# from igr_search import IGRSearcher  # No longer needed
from igr_scraper import IGRScraper
import json
import time
import requests  # Import the requests library

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        filename=f'logs/scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    
    # Initialize components
    # searcher = IGRSearcher()  # No longer needed
    scraper = IGRScraper()
    
    # Search parameters
    district = "Mumbai"  # Ensure this is used in the payload
    today = datetime.now()
    year = today.year  # Extract the year
    village = "ExampleVillage"  # Replace with a valid village name
    
    # API endpoint URL
    api_url = "http://127.0.0.1:8000/api/v1/search"  # Replace with your API URL
    
    # Prepare the request payload
    payload: dict[str, str | int] = {
        "year": year,
        "village": village,
        "district": district,  # Add district to the payload
        "district": district
    }
    
    # Search for properties via API
    logging.info(f"Searching properties for year {year}, village {village}")
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        search_results = response.json()
        property_urls = search_results.get("properties", [])
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return
    
    with open(f'data/urls_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
        json.dump(property_urls, f)
    
    # Process URLs in batches
    batch_size = 10
    for i in range(0, len(property_urls), batch_size):
        batch = property_urls[i:i + batch_size]
        success, fails = scraper.test_batch_download(batch)
        logging.info(f"Batch {i//batch_size + 1}: Success={success}, Fails={fails}")
        time.sleep(60)  # Wait between batches

if __name__ == "__main__":
    main()
