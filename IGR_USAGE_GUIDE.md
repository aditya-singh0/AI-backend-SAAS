# Maharashtra IGR QR Code Scraper - Usage Guide

## Overview
This specialized scraper is designed specifically for the Maharashtra IGR (Inspector General of Registration) website to extract QR codes from property documents and certificates.

## Features
✅ **CAPTCHA Handling**: Detects and downloads CAPTCHA images (`img#captcha-img`)  
✅ **Form Automation**: Handles all form fields (district, taluka, village, article, database)  
✅ **Interactive Input**: Guides you through the form filling process  
✅ **QR Detection**: Automatically finds and decodes QR codes from results  
✅ **Content Analysis**: Analyzes QR content for property-related information  

## Website Elements Handled
Based on your provided selectors:

- **CAPTCHA Image**: `img#captcha-img`
- **CAPTCHA Input**: `input#captchaTextBox`
- **District Dropdown**: `select#district_id`
- **Taluka Dropdown**: `select#taluka_id`
- **Village Dropdown**: `select#village_id`
- **Article Dropdown**: `select#article_id`
- **Database Selection**: `select#dbselect`

## How to Run

### Basic Usage
```bash
cd AI-backend-SAAS
python3 test_igr_final.py
```

### What Happens When You Run It

1. **Page Loading**: Connects to the IGR website
2. **Form Analysis**: Detects all form fields and options
3. **CAPTCHA Detection**: Downloads CAPTCHA image if present
4. **Interactive Input**: Prompts you to:
   - Solve the CAPTCHA (view `captcha_image.png`)
   - Select district, taluka, village, article
   - Choose database option
5. **Form Submission**: Submits the form with your inputs
6. **QR Scanning**: Searches all images in the results for QR codes
7. **Content Analysis**: Analyzes found QR codes for property information

## Step-by-Step Workflow

### Step 1: CAPTCHA Solving
When prompted:
1. The script downloads the CAPTCHA image as `captcha_image.png`
2. Open this image file to view the CAPTCHA
3. Enter the text you see in the image
4. Press Enter to continue

### Step 2: Form Filling
For each field, you can:
- **Skip**: Press Enter to leave field empty
- **Specify**: Enter the ID/value for that field

Example:
```
Enter District ID (or press Enter to skip): 12
Enter Taluka ID (or press Enter to skip): 5
Enter Village ID (or press Enter to skip): 
Enter Article ID (or press Enter to skip): 2
```

### Step 3: Results
The scraper will:
- Submit the form
- Scan all images on the result page
- Extract and decode any QR codes found
- Display detailed analysis of QR content

## Expected Output

### Success Case
```
🎉 SUCCESS! Found 2 QR code(s):

📱 QR Code #1:
   🔗 Image URL: https://pay2igr.igrmaharashtra.gov.in/images/qr123.png
   📄 QR Contents: ['PropertyReg/2023/MH/12345']

   📊 QR Data Analysis #1:
      Content: PropertyReg/2023/MH/12345
      Length: 23 characters
      Type: Text/Data
      🏠 Contains property-related information
      📜 Appears to be a document/certificate reference
```

### No Results Case
```
❌ No QR codes were found

🔍 Possible reasons:
- QR codes may only appear for specific property searches
- The search criteria may need to be more specific
```

## Tips for Success

### 1. Use Specific Search Criteria
- If you have specific property details, use them
- QR codes often appear only for exact matches

### 2. CAPTCHA Solving
- Make sure to view the downloaded `captcha_image.png` clearly
- Enter exactly what you see (case-sensitive)
- If CAPTCHA fails, restart the script for a new one

### 3. Form Field Values
- Check the displayed dropdown options for valid IDs
- Use numeric IDs that appear in the option lists
- Some fields may be required depending on the search type

### 4. Property Information
- If you're looking for a specific property, have details ready:
  - District name/ID
  - Taluka/Sub-district
  - Village name
  - Property/article type

## Troubleshooting

### CAPTCHA Issues
- **Image not downloading**: Check internet connection
- **Wrong CAPTCHA**: Try again with a fresh session
- **CAPTCHA not detected**: The website structure may have changed

### Form Submission Issues
- **Required fields**: Some combinations of fields may be required
- **Invalid selections**: Use only IDs that appear in the dropdown options
- **Timeout errors**: Government websites can be slow, try again

### No QR Codes Found
- **Wrong page**: QR codes may only appear on specific result pages
- **Different location**: Try searching for specific properties
- **Dynamic content**: Some QR codes are generated client-side

## Advanced Usage

### Using Specific Property URLs
If you have a direct property page URL:
```python
from src.igr_specialized_scraper import IGRSpecializedScraper

scraper = IGRSpecializedScraper()
results = scraper.scrape_qr_codes_from_soup(soup_object, base_url)
```

### Batch Processing
For multiple properties, you can modify the script to loop through property IDs.

## Files Created
- `captcha_image.png`: Downloaded CAPTCHA image for manual solving
- Log files: Error logs if debugging is enabled

## Security Notes
- ✅ SSL verification disabled for government sites with certificate issues
- ✅ Respectful delays between requests (0.5 seconds)
- ✅ Proper browser headers to avoid blocking
- ✅ Session management for cookie persistence

## Contact & Support
This scraper is specifically designed for the Maharashtra IGR website structure as of 2025. If the website structure changes, the selectors may need to be updated. 