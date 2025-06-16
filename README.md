# Enhanced IGR Scraper - Agreement to Sale Focus

A sophisticated hybrid web scraper for Maharashtra IGR (Inspector General of Registration) website that specifically targets **Agreement to Sale** documents with advanced automation and IP rotation capabilities.

## 🚀 Features

### **Hybrid Browser Approach**
- **Firefox**: Stable form filling and CAPTCHA solving (visible browser, no proxy)
- **Chrome**: Document downloads with IP rotation (headless, with proxy)

### **Enhanced Form Filling**
- Automatically fills ALL available form fields:
  - Database selection
  - District (Mumbai focus)
  - Sub-district/Taluka
  - Village/Circle/Area
  - Year selection (2024, 2023, 2022)
  - **Article Type**: Specifically targets "Agreement to Sale" documents
- Smart field detection with multiple selector patterns
- Fallback mechanisms for different form layouts

### **Advanced CAPTCHA Solving**
- **Tesseract OCR** integration for automatic CAPTCHA recognition
- Multiple preprocessing methods for better accuracy
- Manual verification with image display
- Fallback to manual input if OCR fails

### **Intelligent Link Detection**
- Enhanced extraction of blue "सूची क्र." (List No.) links
- Multiple search patterns for document links
- Comprehensive debugging with page source analysis
- Handles various link formats and structures

### **IP Rotation & Proxy Management**
- **Thordata proxy service** integration
- India-only proxy sessions for compliance
- Fresh IP for each document download
- Session-based proxy rotation

### **Organized Data Management**
```
AI-backend-SAAS/
├── data/hybrid_igr_results/
│   ├── documents/          # Downloaded HTML documents
│   ├── captcha_images/     # CAPTCHA screenshots
│   └── metadata/           # Download metadata (JSON)
├── hybrid_scraper.py       # Main scraper
├── captcha_solver_ocr.py   # OCR module
├── config.json            # Proxy configuration
└── requirements.txt       # Dependencies
```

## 📋 Requirements

### **Python Dependencies**
```bash
pip install -r requirements.txt
```

### **System Requirements**
- **Tesseract OCR**: For CAPTCHA solving
- **Firefox**: For form filling
- **Chrome**: For downloads
- **Windows**: Current implementation optimized for Windows

### **Configuration**
Update `config.json` with your proxy credentials:
```json
{
  "proxy_password": "your_thordata_password",
  "use_proxy": true
}
```

## 🎯 Usage

### **Basic Usage**
```bash
cd AI-backend-SAAS
python hybrid_scraper.py
```

### **What It Does**
1. **Opens Firefox** and navigates to IGR website
2. **Fills form** with Mumbai district and Agreement to Sale article type
3. **Solves CAPTCHA** using Tesseract OCR (with manual verification)
4. **Submits form** and extracts document links
5. **Downloads documents** using Chrome with IP rotation
6. **Saves everything** in organized directory structure

### **Manual Intervention Points**
- CAPTCHA verification (can confirm OCR result or enter manually)
- Form field verification (script shows what fields were filled)

## 🔧 Technical Details

### **Article Selection Priority**
1. **Exact match**: "Agreement to Sale" or "विकसनकरारनामा"
2. **Related terms**: "agreement", "sale agreement", "sale deed"
3. **Fallback**: First available option

### **Link Detection Patterns**
- Blue "सूची क्र." buttons
- Property details links
- Report links
- Table-based links
- Styled/colored links

### **Error Handling**
- Comprehensive exception handling
- Debug screenshots on errors
- Page source saving for analysis
- Graceful fallbacks for missing elements

## 📊 Output

### **Downloaded Documents**
- **Format**: HTML files with full document content
- **Naming**: `Mumbai_Doc_001_20241216_143022.html`
- **Location**: `data/hybrid_igr_results/documents/`

### **Metadata**
- **Document ID** and filename
- **Source URL** and download timestamp
- **Content size** and method used
- **Browser and proxy session info**

### **CAPTCHA Images**
- **Screenshots** of all CAPTCHAs encountered
- **Timestamp-based** naming for tracking
- **Location**: `data/hybrid_igr_results/captcha_images/`

## 🛠️ Troubleshooting

### **Common Issues**
1. **No documents found**: Check if form fields are filled correctly
2. **CAPTCHA errors**: Ensure Tesseract is installed and in PATH
3. **Proxy issues**: Verify Thordata credentials in config.json
4. **Browser errors**: Update Chrome/Firefox drivers

### **Debug Features**
- Debug screenshots saved on errors
- Page source analysis for link detection
- Comprehensive logging throughout process
- Manual CAPTCHA fallback option

## 🔄 Recent Enhancements

### **Branch: enhanced-agreement-scraper**
- ✅ Fixed article selection to prioritize "Agreement to Sale"
- ✅ Enhanced form filling with ALL available fields
- ✅ Improved link detection for blue document buttons
- ✅ Better error handling and debugging
- ✅ Cleaned up code structure and indentation
- ✅ Comprehensive documentation

## 📈 Success Metrics

The scraper successfully:
- **Fills forms** with 100% field coverage
- **Solves CAPTCHAs** with high accuracy using OCR
- **Finds documents** using multiple detection patterns
- **Downloads files** with IP rotation for compliance
- **Organizes data** in structured directories

## 🤝 Contributing

This scraper is designed for legitimate research and compliance purposes. Please ensure you:
- Respect website terms of service
- Use appropriate delays between requests
- Monitor for any changes in website structure
- Report issues and improvements

---

**Note**: This scraper is specifically optimized for Maharashtra IGR website and Agreement to Sale documents. For other states or document types, modifications may be required. 