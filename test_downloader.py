#!/usr/bin/env python3
"""
Test script for Agreement Document Downloader
Runs without interactive input for testing
"""

import os
import sys
import urllib3

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Disable SSL warnings
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import the downloader
from download_agreements import AgreementDownloader

def test_downloader():
    """Test the downloader with a small number of documents"""
    print("🧪 Testing Agreement Document Downloader")
    print("=" * 50)
    
    # Create downloader instance
    downloader = AgreementDownloader()
    
    # Test with just 5 documents to verify functionality
    print("🔍 Testing with 5 documents...")
    
    try:
        count = downloader.run_bulk_download(
            max_documents=5,
            districts=['1', '2'],  # Test with just 2 districts
            years=['2024']  # Test with just current year
        )
        
        print(f"\n✅ Test completed! Downloaded {count} documents")
        
        # Show what was created
        print(f"\n📁 Data folder structure:")
        print(f"   📄 Documents: {downloader.documents_dir}")
        print(f"   📋 Metadata: {downloader.metadata_dir}")
        print(f"   🖼️  CAPTCHAs: {downloader.captcha_dir}")
        
        # List downloaded files
        if os.path.exists(downloader.documents_dir):
            docs = os.listdir(downloader.documents_dir)
            print(f"\n📄 Downloaded files ({len(docs)}):")
            for doc in docs[:5]:  # Show first 5
                print(f"   - {doc}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment for SSL
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    
    success = test_downloader()
    
    if success:
        print("\n🎉 Test successful! The downloader is working correctly.")
    else:
        print("\n❌ Test failed. Check the error messages above.") 