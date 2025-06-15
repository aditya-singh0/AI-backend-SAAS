#!/usr/bin/env python3
"""
HTML to PDF Converter for Agreement Documents
Converts existing HTML documents to PDF format
"""

import os
import sys
import glob
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from bs4 import BeautifulSoup

def convert_html_to_pdf():
    """Convert HTML documents to PDF format"""
    print("📄 HTML to PDF Converter for Agreement Documents")
    print("=" * 60)
    print("This tool converts existing HTML documents to PDF format")
    print("Features:")
    print("✅ Converts all HTML documents to PDF")
    print("✅ Professional PDF formatting")
    print("✅ Preserves document information")
    print("✅ Organized PDF storage")
    print("✅ File size reporting")
    print("=" * 60)
    
    # Setup directories
    html_dir = 'data/documents'
    pdf_dir = 'data/pdf_documents'
    os.makedirs(pdf_dir, exist_ok=True)
    
    print(f"\n📁 Source HTML files: {os.path.abspath(html_dir)}")
    print(f"📁 Target PDF files: {os.path.abspath(pdf_dir)}")
    
    # Find HTML files
    html_files = glob.glob(os.path.join(html_dir, '*.html'))
    print(f"\n📄 Found {len(html_files)} HTML files to convert")
    
    if not html_files:
        print("❌ No HTML files found to convert")
        return 0
    
    converted = 0
    
    try:
        for html_file in html_files:
            try:
                # Read HTML content
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse HTML
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract document information
                doc_id = "Unknown"
                title_text = "Agreement Document"
                
                for p in soup.find_all('p'):
                    text = p.get_text()
                    if 'Document ID:' in text:
                        doc_id = text.split('Document ID:')[1].strip()
                        break
                
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text()
                
                # Create PDF filename
                base_name = os.path.basename(html_file).replace('.html', '')
                pdf_filename = f"{base_name}.pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                
                print(f"🔄 Converting: {base_name}")
                
                # Create PDF using ReportLab
                c = canvas.Canvas(pdf_path, pagesize=A4)
                width, height = A4
                
                # Header
                c.setFont("Helvetica-Bold", 18)
                title_text = "Agreement to Sale Document"
                text_width = c.stringWidth(title_text, "Helvetica-Bold", 18)
                c.drawString((width - text_width) / 2, height-60, title_text)
                
                c.setFont("Helvetica", 14)
                subtitle_text = "Maharashtra Income and Registration Department"
                subtitle_width = c.stringWidth(subtitle_text, "Helvetica", 14)
                c.drawString((width - subtitle_width) / 2, height-90, subtitle_text)
                
                # Document info
                y = height - 140
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Document Information:")
                
                y -= 25
                c.setFont("Helvetica", 10)
                c.drawString(70, y, f"Document ID: {doc_id}")
                y -= 20
                c.drawString(70, y, f"Title: {title_text}")
                y -= 20
                c.drawString(70, y, f"Converted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                y -= 20
                c.drawString(70, y, f"Source: {os.path.basename(html_file)}")
                
                # Content
                y -= 40
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, "Document Content:")
                
                y -= 25
                c.setFont("Helvetica", 9)
                
                # Add text content
                text_content = soup.get_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                for line in lines:
                    if y < 50:
                        c.showPage()
                        y = height - 50
                        c.setFont("Helvetica", 9)
                    
                    if len(line) > 85:
                        line = line[:82] + "..."
                    
                    c.drawString(50, y, line)
                    y -= 12
                
                # Footer
                c.setFont("Helvetica", 8)
                footer_text = "Generated by IGR PDF Converter"
                footer_width = c.stringWidth(footer_text, "Helvetica", 8)
                c.drawString((width - footer_width) / 2, 30, footer_text)
                
                c.save()
                
                file_size = os.path.getsize(pdf_path)
                print(f"✅ Converted: {pdf_filename} ({file_size:,} bytes)")
                converted += 1
                
            except Exception as e:
                print(f"❌ Failed to convert {os.path.basename(html_file)}: {e}")
        
        print(f"\n🎉 Successfully converted {converted}/{len(html_files)} documents!")
        
        # Show final statistics
        print(f"\n📊 Conversion Statistics:")
        print(f"   📄 Total converted: {converted}")
        print(f"   📁 PDF folder: {os.path.abspath(pdf_dir)}")
        
        # List converted files
        if converted > 0:
            pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
            print(f"\n📄 Converted PDF files ({len(pdf_files)}):")
            for i, pdf_file in enumerate(pdf_files, 1):
                file_size = os.path.getsize(pdf_file)
                print(f"   {i:2d}. {os.path.basename(pdf_file)} ({file_size:,} bytes)")
                if i >= 10:  # Show first 10
                    remaining = len(pdf_files) - 10
                    if remaining > 0:
                        print(f"   ... and {remaining} more files")
                    break
        
        return converted
        
    except KeyboardInterrupt:
        print("\n\n👋 Conversion interrupted by user")
        return converted
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return converted

if __name__ == "__main__":
    try:
        count = convert_html_to_pdf()
        print(f"\n✅ PDF conversion completed with {count} documents!")
        print("📂 Check the 'data/pdf_documents' folder for your PDF files")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 