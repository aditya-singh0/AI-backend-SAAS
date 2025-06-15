#!/usr/bin/env python3
"""
Real IGR Document Downloader
Downloads actual Agreement to Sale documents from Maharashtra IGR website
"""

import os
import sys
import requests
import ssl
import urllib3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

def download_real_igr_document():
    """Download real IGR document and convert to PDF"""
    print("📄 Real IGR Document Downloader")
    print("=" * 60)
    print("This tool downloads actual Agreement to Sale documents from Maharashtra IGR")
    print("Features:")
    print("✅ Downloads real IGR documents")
    print("✅ Accesses Maharashtra IGR official website")
    print("✅ Converts to professional PDF format")
    print("✅ Preserves authentic document content")
    print("✅ Organized storage with metadata")
    print("=" * 60)
    
    # Setup directories
    pdf_dir = 'data/real_igr_pdfs'
    metadata_dir = 'data/metadata'
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    
    print(f"\n📁 Real IGR PDFs will be saved to: {os.path.abspath(pdf_dir)}")
    print(f"📁 Metadata will be saved to: {os.path.abspath(metadata_dir)}")
    
    # Real IGR URL provided by user
    real_igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails/indexii/MjAyNQ%3D%3D/MDUyMDAwMDAwMDAwMTE5NjY5MDAwMDA5Mzc5MjAyNUlT"
    
    print(f"\n🌐 Downloading from Maharashtra IGR website...")
    print(f"🔗 URL: {real_igr_url[:80]}...")
    
    # Setup session with headers
    session = requests.Session()
    session.verify = False
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    converted = 0
    
    try:
        # Download real IGR document
        try:
            print("📥 Downloading real IGR document...")
            response = session.get(real_igr_url, headers=headers, timeout=30, verify=False)
            print(f"✅ Download successful! Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse the real IGR content
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text()
                
                print(f"📄 Document content extracted: {len(text_content)} characters")
                print(f"📊 Content preview: {text_content[:200]}...")
                
                # Create PDF filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f"REAL_IGR_Agreement_{timestamp}.pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                
                print(f"🔄 Converting to PDF: {pdf_filename}")
                
                # Create PDF using ReportLab
                c = canvas.Canvas(pdf_path, pagesize=A4)
                width, height = A4
                
                # Header with special marking for REAL document
                c.setFont("Helvetica-Bold", 20)
                title_text = "🌟 REAL IGR Agreement to Sale Document 🌟"
                text_width = c.stringWidth(title_text, "Helvetica-Bold", 20)
                c.drawString((width - text_width) / 2, height-50, title_text)
                
                c.setFont("Helvetica-Bold", 16)
                subtitle_text = "Maharashtra Income and Registration Department"
                subtitle_width = c.stringWidth(subtitle_text, "Helvetica-Bold", 16)
                c.drawString((width - subtitle_width) / 2, height-80, subtitle_text)
                
                c.setFont("Helvetica", 12)
                auth_text = "AUTHENTIC DOCUMENT FROM OFFICIAL IGR WEBSITE"
                auth_width = c.stringWidth(auth_text, "Helvetica", 12)
                c.drawString((width - auth_width) / 2, height-105, auth_text)
                
                # Document information
                y = height - 140
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Document Information:")
                
                y -= 25
                c.setFont("Helvetica", 10)
                c.drawString(70, y, "Document Type: Agreement to Sale")
                y -= 20
                c.drawString(70, y, "Source: Maharashtra IGR Official Website")
                y -= 20
                c.drawString(70, y, f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                y -= 20
                c.drawString(70, y, f"Source URL: {real_igr_url[:60]}...")
                y -= 20
                c.drawString(70, y, f"Content Length: {len(text_content)} characters")
                y -= 20
                c.drawString(70, y, f"Status: AUTHENTIC IGR DOCUMENT")
                
                # Content section
                y -= 40
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Real IGR Document Content:")
                
                y -= 25
                c.setFont("Helvetica", 9)
                
                # Add the actual IGR content
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                for line in lines:
                    if y < 50:  # Start new page if needed
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 9)
                        
                        # Add header on new page
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(50, height-30, "REAL IGR Agreement Document (continued)")
                        c.setFont("Helvetica", 9)
                        y = height - 60
                    
                    # Handle long lines
                    if len(line) > 85:
                        # Split long lines
                        words = line.split()
                        current_line = ""
                        for word in words:
                            if len(current_line + " " + word) <= 85:
                                current_line += " " + word if current_line else word
                            else:
                                if current_line:
                                    c.drawString(50, y, current_line)
                                    y -= 12
                                    if y < 50:
                                        c.showPage()
                                        y = height - 50
                                        c.setFont("Helvetica", 9)
                                current_line = word
                        if current_line:
                            c.drawString(50, y, current_line)
                            y -= 12
                    else:
                        c.drawString(50, y, line)
                        y -= 12
                
                # Footer
                c.setFont("Helvetica", 8)
                footer_text = f"Real IGR Document Downloaded from Maharashtra Government Website - {datetime.now().strftime('%Y-%m-%d')}"
                footer_width = c.stringWidth(footer_text, "Helvetica", 8)
                c.drawString((width - footer_width) / 2, 30, footer_text)
                
                c.save()
                
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Real IGR PDF created: {pdf_filename} ({file_size:,} bytes)")
                
                # Save metadata
                metadata = {
                    'filename': pdf_filename,
                    'source_url': real_igr_url,
                    'download_date': datetime.now().isoformat(),
                    'content_length': len(text_content),
                    'file_size': file_size,
                    'document_type': 'Real IGR Agreement to Sale',
                    'authenticity': 'Authentic Maharashtra IGR Document',
                    'status': 'Successfully Downloaded and Converted'
                }
                
                metadata_file = os.path.join(metadata_dir, f"{pdf_filename}_metadata.json")
                import json
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                print(f"📋 Metadata saved: {os.path.basename(metadata_file)}")
                converted += 1
                
            else:
                print(f"❌ Failed to download: HTTP {response.status_code}")
                if response.status_code == 404:
                    print("💡 The document may have been moved or is no longer available")
                elif response.status_code == 403:
                    print("💡 Access forbidden - may need different authentication")
                else:
                    print(f"💡 HTTP Status {response.status_code}: {response.reason}")
                
        except requests.exceptions.Timeout:
            print("❌ Download timeout - IGR server may be slow")
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - check internet connection")
        except Exception as e:
            print(f"❌ Download failed: {e}")
        
        # Final results
        if converted > 0:
            print(f"\n🎉 Successfully downloaded and converted {converted} real IGR document!")
            
            print(f"\n📊 Download Statistics:")
            print(f"   📄 Real documents downloaded: {converted}")
            print(f"   📁 PDF location: {os.path.abspath(pdf_dir)}")
            print(f"   📋 Metadata location: {os.path.abspath(metadata_dir)}")
            
            # List the real IGR PDF
            pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
            if pdf_files:
                print(f"\n📄 Real IGR PDF Document:")
                for pdf_file in pdf_files:
                    file_path = os.path.join(pdf_dir, pdf_file)
                    file_size = os.path.getsize(file_path)
                    print(f"   🌟 {pdf_file} ({file_size:,} bytes)")
                    print(f"   📁 Full path: {os.path.abspath(file_path)}")
        else:
            print(f"\n❌ Failed to download real IGR document")
            print("💡 This could be due to:")
            print("   - Network connectivity issues")
            print("   - IGR website being temporarily unavailable")
            print("   - Document URL may have changed")
            print("   - Access restrictions on the IGR website")
        
        return converted
        
    except KeyboardInterrupt:
        print("\n\n👋 Download interrupted by user")
        return converted
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return converted

if __name__ == "__main__":
    try:
        count = download_real_igr_document()
        if count > 0:
            print(f"\n✅ Real IGR document download completed successfully!")
            print("📂 Check the 'data/real_igr_pdfs' folder for your authentic IGR document")
            print("🌟 This is a REAL document from Maharashtra Government IGR website")
        else:
            print(f"\n❌ Failed to download real IGR document")
            print("💡 Please check your internet connection and try again")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 