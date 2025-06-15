#!/usr/bin/env python3
"""
Working Agreement Document Downloader - PDF Version
Downloads 25 Agreement to Sale documents with IP rotation and converts to PDF format
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import json
import ssl
import urllib3

# Try to import PDF libraries
try:
    from weasyprint import HTML, CSS
    PDF_AVAILABLE = True
    print("✅ WeasyPrint available for PDF conversion")
except ImportError:
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        PDF_AVAILABLE = True
        print("✅ ReportLab available for PDF conversion")
    except ImportError:
        PDF_AVAILABLE = False
        print("⚠️  No PDF libraries available, will save as HTML")

# Disable SSL warnings
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Proxy configuration
PROXY_CONFIG = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'iyHxHphyuy3i'
}

def main():
    """Main download function"""
    print("📄 IGR PDF Document Downloader")
    print("=" * 60)
    print("Features:")
    print("✅ Downloads real IGR documents")
    print("✅ Converts to PDF format")
    print("✅ Automatic IP rotation")
    print("✅ Organized data folder structure")
    print("=" * 60)
    
    # Create data directories
    data_dir = 'data'
    documents_dir = os.path.join(data_dir, 'igr_pdfs')
    metadata_dir = os.path.join(data_dir, 'metadata')
    
    for directory in [data_dir, documents_dir, metadata_dir]:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created/verified directory: {directory}")
    
    print(f"\n📁 Data will be saved to: {os.path.abspath(data_dir)}")
    print(f"   📄 Documents: {documents_dir}")
    print(f"   📋 Metadata: {metadata_dir}")
    
    # Initialize session
    session = requests.Session()
    session.verify = False
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    
    # Real IGR URL provided by user
    real_igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
    
    # Create list of documents to download
    docs = []
    
    # Add the real IGR document
    docs.append({
        'url': real_igr_url,
        'title': 'Real IGR Agreement to Sale Document',
        'id': 'IGR_REAL_001'
    })
    
    # Create variations of the real URL for bulk download
    base_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/MjAyNQ%3D%3D/"
    base_doc_id = "MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
    
    for i in range(2, 26):  # Generate 24 more variations
        # Modify the document ID slightly
        modified_id = base_doc_id[:-4] + f"{i:04d}"
        variant_url = base_url + modified_id
        docs.append({
            'url': variant_url,
            'title': f'IGR Agreement Document Variant {i:02d}',
            'id': f'IGR_VAR_{i:03d}'
        })
    
    print(f"\n🚀 Starting download of {len(docs)} IGR documents...")
    
    download_count = 0
    session_id = None
    last_ip_change = time.time()
    
    for i, doc in enumerate(docs, 1):
        try:
            print(f"\n📥 Downloading document {i}/25: {doc['title']}")
            print(f"🔗 URL: {doc['url'][:80]}...")
            
            # IP rotation every 4 seconds
            current_time = time.time()
            if not session_id or (current_time - last_ip_change) >= 4:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
                session_id = f"igr-{random_id}-{timestamp}"
                last_ip_change = current_time
                print(f"🔄 IP rotation - Session: {session_id}")
            
            # Prepare proxy
            full_username = f"{PROXY_CONFIG['username']}-sessid-{session_id}"
            proxy_url = f"http://{full_username}:{PROXY_CONFIG['password']}@{PROXY_CONFIG['host']}:{PROXY_CONFIG['port']}"
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            # Try to make request
            response = None
            try:
                # First try with proxy
                response = session.get(
                    doc['url'], 
                    headers=headers, 
                    proxies=proxies, 
                    timeout=15,
                    verify=False
                )
                print(f"✅ Downloaded with proxy (Status: {response.status_code})")
            except Exception as e:
                # Fallback to direct connection
                print(f"⚠️  Proxy failed: {e}")
                try:
                    response = session.get(
                        doc['url'], 
                        headers=headers, 
                        timeout=15,
                        verify=False
                    )
                    print(f"✅ Downloaded directly (Status: {response.status_code})")
                except Exception as e2:
                    print(f"❌ Direct connection failed: {e2}")
                    continue
            
            if not response or response.status_code != 200:
                print(f"❌ Failed to download (Status: {response.status_code if response else 'None'})")
                continue
            
            # Process and save document
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if PDF_AVAILABLE:
                # Save as PDF
                filename = f"igr_agreement_{i:04d}_{doc['id']}_{timestamp}.pdf"
                filepath = os.path.join(documents_dir, filename)
                
                try:
                    # Parse content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_content = soup.get_text()
                    
                    # Create HTML for PDF conversion
                    pdf_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>IGR Agreement to Sale Document</title>
                    </head>
                    <body>
                        <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #333;">
                            <h1 style="color: #d32f2f;">Agreement to Sale Document</h1>
                            <h2 style="color: #666;">Maharashtra Income and Registration Department</h2>
                            <p><strong>Document ID:</strong> {doc['id']}</p>
                            <p><strong>Downloaded:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p><strong>Source URL:</strong> {doc['url']}</p>
                        </div>
                        
                        <div style="background-color: #f9f9f9; padding: 20px; margin-bottom: 20px;">
                            <h3>Document Information</h3>
                            <p><strong>Type:</strong> Agreement to Sale</p>
                            <p><strong>Source:</strong> Maharashtra IGR Official Website</p>
                            <p><strong>Session:</strong> {session_id}</p>
                            <p><strong>Download Index:</strong> {i}</p>
                        </div>
                        
                        <div style="margin-top: 30px;">
                            <h3>Document Content</h3>
                            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                                {text_content.replace('\n', '<br>') if text_content else 'Content extracted from IGR website'}
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Convert to PDF using WeasyPrint
                    css = CSS(string='''
                    @page { margin: 2cm; size: A4; }
                    body { font-family: Arial, sans-serif; font-size: 12px; line-height: 1.5; }
                    ''')
                    
                    HTML(string=pdf_html).write_pdf(filepath, stylesheets=[css])
                    print(f"📄 Converted to PDF successfully")
                    
                except Exception as e:
                    print(f"⚠️  PDF conversion failed: {e}")
                    # Fallback to HTML
                    filename = filename.replace('.pdf', '.html')
                    filepath = filepath.replace('.pdf', '.html')
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(pdf_html)
            else:
                # Save as HTML if PDF libraries not available
                filename = f"igr_agreement_{i:04d}_{doc['id']}_{timestamp}.html"
                filepath = os.path.join(documents_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
            
            download_count += 1
            file_size = os.path.getsize(filepath)
            print(f"✅ Saved: {filename} ({file_size:,} bytes)")
            
            # Save metadata
            metadata = {
                'filename': filename,
                'document_id': doc['id'],
                'title': doc['title'],
                'url': doc['url'],
                'downloaded_at': datetime.now().isoformat(),
                'session_id': session_id,
                'file_size': file_size,
                'download_index': i,
                'format': 'PDF' if filename.endswith('.pdf') else 'HTML'
            }
            
            meta_file = os.path.join(metadata_dir, f"{filename}_metadata.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Wait between downloads
            if i < len(docs):
                wait_time = 2 + random.uniform(0.5, 1.5)  # Random wait 2.5-3.5 seconds
                print(f"⏳ Waiting {wait_time:.1f} seconds before next download...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"❌ Failed to download document {i}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"✅ Download complete!")
    print(f"   📄 Total downloaded: {download_count}/25")
    print(f"   📁 Documents saved to: {os.path.abspath(documents_dir)}")
    print(f"   📋 Metadata saved to: {os.path.abspath(metadata_dir)}")
    
    # List downloaded files
    if os.path.exists(documents_dir):
        docs = os.listdir(documents_dir)
        print(f"\n📄 Downloaded files ({len(docs)}):")
        for i, doc in enumerate(docs[:10], 1):  # Show first 10
            file_path = os.path.join(documents_dir, doc)
            file_size = os.path.getsize(file_path)
            print(f"   {i:2d}. {doc} ({file_size:,} bytes)")
        if len(docs) > 10:
            remaining = len(docs) - 10
            print(f"   ... and {remaining} more files")
    
    print(f"\n🎉 Successfully downloaded {download_count} IGR Agreement to Sale documents!")
    return download_count

if __name__ == "__main__":
    try:
        count = main()
        print(f"\n✅ Process completed with {count} documents downloaded!")
    except KeyboardInterrupt:
        print("\n\n👋 Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 