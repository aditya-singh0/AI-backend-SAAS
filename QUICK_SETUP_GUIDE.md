# 🚀 Quick Setup Guide - Fix IGR Scraper Issues

## Issues Found:
1. ❌ **SSL/TLS Errors**: `[SSL: WRONG_VERSION_NUMBER]`
2. ❌ **Missing Tesseract OCR**: Required for CAPTCHA solving
3. ❌ **Connection Resets**: Website blocking automated requests

## ✅ Solutions:

### **Option 1: Install Tesseract OCR (Recommended)**

#### Method A: Using Chocolatey (Easiest)
```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Tesseract
choco install tesseract -y
```

#### Method B: Manual Installation
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

#### Method C: Run our installer
```powershell
.\install_tesseract.bat
```

### **Option 2: Use Selenium Version (Works without OCR)**
```powershell
python selenium_bulk_igr_scraper.py
```

### **Option 3: Use Working Selenium Scripts**
```powershell
# Interactive Mumbai scraper (works best)
python mumbai_interactive_scraper.py

# Automated Mumbai scraper
python final_mumbai_scraper.py
```

## 🔧 **Recommended Steps:**

1. **Install Tesseract OCR** (5 minutes)
2. **Restart PowerShell** 
3. **Run**: `python download_agreements.py`

## 📋 **Test Commands:**
```powershell
# Test if Tesseract is installed
tesseract --version

# Test if all dependencies are installed
python -c "import cv2, pytesseract; print('✅ All dependencies ready!')"

# Run the main scraper
python download_agreements.py
```

## 🛠️ **Alternative: Use Selenium Scrapers**
If you prefer not to install OCR, use these working scrapers:

```powershell
# Best option - Interactive Mumbai scraper
python mumbai_interactive_scraper.py

# Automated option
python selenium_bulk_igr_scraper.py
```

## 📊 **Expected Results:**
- **With OCR**: Full automation, handles CAPTCHAs automatically
- **Without OCR**: Manual CAPTCHA solving required, but downloads work
- **Selenium**: Browser automation, most reliable for bypassing blocks

## 🎯 **Quick Test:**
```powershell
# Quick test with 2 documents
python simple_agreement_downloader.py
# Enter: 2
``` 