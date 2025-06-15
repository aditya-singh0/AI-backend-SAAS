#!/usr/bin/env python3
"""
Run Agreement Document Downloader for 25 documents
Automated script without interactive input
"""

import os
import sys
import urllib3
import ssl

# Disable SSL warnings and verification
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables for better SSL compatibility
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import the downloader
from download_agreements import AgreementDownloader

def run_bulk_download():
    """Run bulk download of 25 documents"""
    print("📄 Enhanced Agreement to Sale Document Downloader")
    print("=" * 60)
    print("This tool downloads Agreement to Sale documents from Maharashtra IGR")
    print("Features:")
    print("✅ Automatic IP rotation every 4 seconds")
    print("✅ IP block detection and instant switching")
    print("✅ CAPTCHA detection and OCR solving")
    print("✅ Bulk download support")
    print("✅ Organized data folder structure")
    print("✅ Metadata tracking")
    print("=" * 60)
    
    # Create downloader instance
    downloader = AgreementDownloader()
    
    # Show data folder info
    print(f"\n📁 Data will be saved to: {os.path.abspath(downloader.data_dir)}")
    print(f"   📄 Documents: {downloader.documents_dir}")
    print(f"   📋 Metadata: {downloader.metadata_dir}")
    print(f"   🖼️  CAPTCHAs: {downloader.captcha_dir}")
    
    print(f"\n🚀 Starting download of 25 documents...")
    
    try:
        # Run the bulk download with 25 documents
        count = downloader.run_bulk_download(max_documents=25)
        
        print(f"\n🎉 Successfully downloaded {count} documents!")
        
        # Show final statistics
        print(f"\n📊 Final Statistics:")
        print(f"   📄 Total downloaded: {count}")
        print(f"   📁 Documents folder: {os.path.abspath(downloader.documents_dir)}")
        print(f"   📋 Metadata folder: {os.path.abspath(downloader.metadata_dir)}")
        print(f"   🖼️  CAPTCHAs folder: {os.path.abspath(downloader.captcha_dir)}")
        
        # List downloaded files
        if os.path.exists(downloader.documents_dir):
            docs = os.listdir(downloader.documents_dir)
            print(f"\n📄 Downloaded files ({len(docs)}):")
            for i, doc in enumerate(docs, 1):
                print(f"   {i:2d}. {doc}")
                if i >= 10:  # Show first 10
                    remaining = len(docs) - 10
                    if remaining > 0:
                        print(f"   ... and {remaining} more files")
                    break
        
        return count
        
    except KeyboardInterrupt:
        print("\n\n👋 Download interrupted by user")
        return downloader.download_count
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return downloader.download_count

if __name__ == "__main__":
    try:
        count = run_bulk_download()
        print(f"\n✅ Download session completed with {count} documents!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 