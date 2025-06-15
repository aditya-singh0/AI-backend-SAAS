#!/usr/bin/env python3
"""Simple IGR PDF Test"""

import requests
import os
import ssl
import urllib3
from datetime import datetime
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

print('📄 IGR PDF Downloader - Testing Real Document')
print('=' * 50)

# Create directories
os.makedirs('data/igr_pdfs', exist_ok=True)
print('📁 Created data/igr_pdfs directory')

# Real IGR URL
url = 'https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    print('📥 Downloading real IGR document...')
    print(f'🔗 URL: {url[:80]}...')
    
    response = requests.get(url, headers=headers, verify=False, timeout=15)
    print(f'✅ Downloaded (Status: {response.status_code})')
    
    if response.status_code == 200:
        # Parse content
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        
        print(f'📄 Content length: {len(text_content)} characters')
        
        # Create formatted HTML for PDF
        pdf_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>IGR Agreement to Sale Document</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 20px;">
    <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 20px;">
        <h1 style="color: #d32f2f; margin-bottom: 10px;">Agreement to Sale Document</h1>
        <h2 style="color: #666; margin-bottom: 15px;">Maharashtra Income and Registration Department</h2>
        <p><strong>Downloaded:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Source:</strong> Maharashtra IGR Official Website</p>
    </div>
    
    <div style="background-color: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
        <h3>Document Information</h3>
        <p><strong>Document Type:</strong> Agreement to Sale</p>
        <p><strong>Source URL:</strong> {url}</p>
        <p><strong>Status:</strong> Successfully Downloaded</p>
    </div>
    
    <div style="margin-top: 20px;">
        <h3>Document Content</h3>
        <div style="line-height: 1.6; border: 1px solid #ddd; padding: 15px; background-color: white;">
            {text_content.replace('\n', '<br>') if text_content else 'Content extracted from IGR website'}
        </div>
    </div>
</body>
</html>'''
        
        # Convert to PDF
        print('📄 Converting to PDF format...')
        filename = f'real_igr_agreement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        filepath = f'data/igr_pdfs/{filename}'
        
        # CSS for styling
        css = CSS(string='''
            @page {
                margin: 2cm;
                size: A4;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 11px;
                line-height: 1.5;
            }
            h1, h2, h3 {
                margin-top: 15px;
                margin-bottom: 10px;
            }
        ''')
        
        HTML(string=pdf_html).write_pdf(filepath, stylesheets=[css])
        
        file_size = os.path.getsize(filepath)
        print(f'✅ PDF saved: {filename}')
        print(f'📏 File size: {file_size:,} bytes')
        print(f'📁 Location: {os.path.abspath(filepath)}')
        print('\n🎉 SUCCESS! Real IGR document downloaded and converted to PDF!')
        
    else:
        print(f'❌ Failed to download document (Status: {response.status_code})')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 50)
print('Test completed!') 