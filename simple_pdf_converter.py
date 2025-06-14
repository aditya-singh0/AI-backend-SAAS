import os
import glob
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from bs4 import BeautifulSoup

print("📄 Simple HTML to PDF Converter")
print("=" * 50)

# Create PDF directory
os.makedirs('data/pdf_documents', exist_ok=True)

# Find HTML files
html_files = glob.glob('data/documents/*.html')
print(f"Found {len(html_files)} HTML files to convert")

converted = 0
for html_file in html_files:
    try:
        # Read HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse HTML to extract info
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract document ID
        doc_id = "Unknown"
        for p in soup.find_all('p'):
            text = p.get_text()
            if 'Document ID:' in text:
                doc_id = text.split('Document ID:')[1].strip()
                break
        
        # Create PDF filename
        base_name = os.path.basename(html_file).replace('.html', '')
        pdf_path = f'data/pdf_documents/{base_name}.pdf'
        
        print(f"Converting: {base_name}")
        
        # Create PDF using ReportLab
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Title section
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredText(width/2, height-60, "Agreement to Sale Document")
        
        c.setFont("Helvetica", 14)
        c.drawCentredText(width/2, height-90, "Maharashtra Income and Registration Department")
        
        # Document information
        y_position = height - 140
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Document Information:")
        
        y_position -= 25
        c.setFont("Helvetica", 10)
        c.drawString(70, y_position, f"Document ID: {doc_id}")
        
        y_position -= 20
        c.drawString(70, y_position, f"Converted to PDF: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y_position -= 20
        c.drawString(70, y_position, f"Original Format: HTML")
        
        y_position -= 20
        c.drawString(70, y_position, f"Source File: {os.path.basename(html_file)}")
        
        # Content section
        y_position -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Document Content:")
        
        y_position -= 25
        c.setFont("Helvetica", 9)
        
        # Extract and add text content
        text_content = soup.get_text()
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        for line in lines:
            if y_position < 50:  # Start new page if needed
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 9)
            
            # Wrap long lines
            if len(line) > 90:
                line = line[:87] + "..."
            
            c.drawString(50, y_position, line)
            y_position -= 12
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredText(width/2, 30, f"Generated by IGR PDF Converter - Page 1")
        
        c.save()
        
        file_size = os.path.getsize(pdf_path)
        print(f"✅ Converted: {base_name}.pdf ({file_size:,} bytes)")
        converted += 1
        
    except Exception as e:
        print(f"❌ Failed to convert {os.path.basename(html_file)}: {e}")

print(f"\n✅ Successfully converted {converted}/{len(html_files)} files to PDF")
print(f"📁 PDF files saved to: {os.path.abspath('data/pdf_documents')}")

# List the converted files
if converted > 0:
    pdf_files = glob.glob('data/pdf_documents/*.pdf')
    print(f"\n📄 Converted PDF files ({len(pdf_files)}):")
    for i, pdf_file in enumerate(pdf_files[:10], 1):
        file_size = os.path.getsize(pdf_file)
        print(f"   {i:2d}. {os.path.basename(pdf_file)} ({file_size:,} bytes)")
    
    if len(pdf_files) > 10:
        print(f"   ... and {len(pdf_files) - 10} more files")

print("\n🎉 HTML to PDF conversion completed!")
print("📂 Check the 'data/pdf_documents' folder for your PDF files")
