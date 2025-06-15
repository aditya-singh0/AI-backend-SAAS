from src.qr_scraper import QRScraper

# Create a QR scraper instance
scraper = QRScraper()

# Scrape QR codes from a single image
qr_data = scraper.extract_qr_from_image_url("https://example.com/image-with-qr.png")
print("QR codes found:", qr_data)

# Scrape all QR codes from a webpage
results = scraper.scrape_qr_codes_from_webpage("https://example.com/page-with-qr-codes")
for result in results:
    print(f"Image URL: {result['image_url']}")
    print(f"QR Contents: {result['qr_contents']}")