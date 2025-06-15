from src.qr_scraper import QRScraper

def main():
    # Create an instance of QRScraper
    scraper = QRScraper()
    
    # Example: Scrape QR codes from a webpage
    url = "https://example.com"  # Replace with the website URL you want to scrape
    print(f"\nScraping QR codes from: {url}")
    
    results = scraper.scrape_qr_codes_from_webpage(url)
    
    if results:
        print("\nFound QR codes:")
        for result in results:
            print(f"\nImage URL: {result['image_url']}")
            print(f"QR Contents: {result['qr_contents']}")
    else:
        print("\nNo QR codes found on the webpage")

if __name__ == "__main__":
    main() 