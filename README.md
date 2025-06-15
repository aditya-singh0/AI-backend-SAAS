# Maharashtra IGR QR Code Scraper with Proxy Support

A specialized scraper for extracting QR codes from Maharashtra IGR property documents with residential proxy support and IP rotation.

## Features
- **QR Code Extraction**: Automatically detect and decode QR codes from property documents
- **CAPTCHA Handling**: Interactive CAPTCHA solving workflow
- **Form Automation**: Handle district, taluka, village, and article selection
- **Residential Proxy Support**: Built-in IP rotation using ThorData proxies
- **Session Management**: Sticky sessions for consistent form submissions

## Quick Start

### 1. Install Python
Download from [python.org](https://www.python.org/downloads/) or Microsoft Store

### 2. Install Dependencies
```bash
cd AI-backend-SAAS
pip install -r requirements.txt
```

### 3. Run with Proxy Support
```bash
python test_igr_with_proxy.py --proxy-password YOUR_PASSWORD
```

### 4. Test Proxy Connection
```bash
python test_igr_with_proxy.py --test-proxy --proxy-password YOUR_PASSWORD
```

## Documentation
- [IGR Usage Guide](IGR_USAGE_GUIDE.md) - Complete guide for IGR website scraping
- [Proxy Usage Guide](PROXY_USAGE_GUIDE.md) - How to use residential proxies with IP rotation

## Project Structure
- `src/`: Source code
  - `igr_specialized_scraper.py`: Main scraper implementation
  - `enhanced_proxy_manager.py`: Proxy management with IP rotation
  - `proxy_manager.py`: Basic proxy configuration
- `test_igr_final.py`: Basic scraper without proxy
- `test_igr_with_proxy.py`: Enhanced scraper with proxy support
- `proxy_config.env.example`: Example proxy configuration

## Requirements
- Python 3.7+
- ThorData proxy credentials (for IP rotation)
- Internet connection
