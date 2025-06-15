#!/usr/bin/env python3

import sys
import os
import argparse

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.igr_specialized_scraper import IGRSpecializedScraper
from src.enhanced_proxy_manager import EnhancedProxyManager

def main():
    """Main function to run the IGR QR Code scraper with proxy support"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='IGR QR Code Scraper with Proxy Support')
    parser.add_argument('--no-proxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('--proxy-password', type=str, help='Proxy password (if not in env)')
    parser.add_argument('--test-proxy', action='store_true', help='Test proxy connection only')
    args = parser.parse_args()
    
    print("🏛️ Maharashtra IGR QR Code Scraper with IP Rotation")
    print("=" * 70)
    print("This scraper includes:")
    print("✅ Residential proxy support with IP rotation")
    print("✅ CAPTCHA detection and handling")
    print("✅ Form field interaction")
    print("✅ QR code extraction from results")
    print("=" * 70)
    
    # Configure proxy if needed
    if args.test_proxy:
        print("\n🔧 Testing Proxy Connection...")
        proxy_config = {
            'host': '42q6t9rp.pr.thordata.net',
            'port': '9999',
            'username': 'td-customer-hdXMhtuot8ni',
            'password': args.proxy_password or os.getenv('PROXY_PASSWORD', '')
        }
        
        proxy_manager = EnhancedProxyManager(proxy_config)
        
        # Test multiple IPs
        print("\n📊 Testing IP Rotation (3 different IPs):")
        for i in range(3):
            result = proxy_manager.test_proxy_connection(rotate_ip=True)
            if result['success']:
                print(f"   Test {i+1}: ✅ IP: {result['ip']}")
            else:
                print(f"   Test {i+1}: ❌ Error: {result['error']}")
        
        print("\n📊 Proxy Statistics:")
        stats = proxy_manager.get_proxy_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        return
    
    # The IGR website URL
    igr_url = "https://pay2igr.igrmaharashtra.gov.in/eDisplay/Propertydetails/index"
    
    try:
        # Create the specialized scraper with proxy support
        use_proxy = not args.no_proxy
        
        if use_proxy:
            print("\n🔄 Proxy Mode: ENABLED")
            print("   - IP rotation for each request")
            print("   - Sticky session for form submission")
            print("   - Anonymous browsing")
            
            # Set proxy password if provided
            if args.proxy_password:
                os.environ['PROXY_PASSWORD'] = args.proxy_password
        else:
            print("\n🔄 Proxy Mode: DISABLED")
            print("   - Direct connection will be used")
        
        scraper = IGRSpecializedScraper(use_proxy=use_proxy)
        
        print("\n🚀 Starting IGR workflow...")
        
        # Run the complete workflow
        results = scraper.full_igr_workflow(igr_url)
        
        # Display results
        print("\n" + "=" * 70)
        print("🎯 FINAL RESULTS")
        print("=" * 70)
        
        if results:
            print(f"🎉 SUCCESS! Found {len(results)} QR code(s):")
            
            for i, result in enumerate(results, 1):
                print(f"\n📱 QR Code #{i}:")
                print(f"   🔗 Image URL: {result['image_url']}")
                print(f"   📄 QR Contents: {result['qr_contents']}")
                
                # Analyze QR content
                for j, qr_content in enumerate(result['qr_contents']):
                    print(f"\n   📊 QR Data Analysis #{j+1}:")
                    print(f"      Content: {qr_content}")
                    print(f"      Length: {len(qr_content)} characters")
                    print(f"      Type: {'URL' if qr_content.startswith(('http://', 'https://')) else 'Text/Data'}")
                    
                    # Check for property-related keywords
                    property_keywords = ['property', 'registration', 'document', 'igr', 'survey', 'plot', 'land']
                    if any(keyword.lower() in qr_content.lower() for keyword in property_keywords):
                        print(f"      🏠 Contains property-related information")
                    
                    # Check for document/certificate keywords
                    doc_keywords = ['certificate', 'registration', 'deed', 'document']
                    if any(keyword.lower() in qr_content.lower() for keyword in doc_keywords):
                        print(f"      📜 Appears to be a document/certificate reference")
                        
        else:
            print("❌ No QR codes were found")
            print("\n🔍 Possible reasons:")
            print("- QR codes may only appear for specific property searches")
            print("- The search criteria may need to be more specific") 
            print("- QR codes might be generated after additional steps")
            
        # Show proxy statistics if used
        if use_proxy and hasattr(scraper, 'proxy_manager'):
            print("\n📊 Proxy Usage Statistics:")
            stats = scraper.proxy_manager.get_proxy_stats()
            print(f"   Total requests made: {stats.get('total_requests', 0)}")
            print(f"   Proxy endpoint: {stats.get('host')}:{stats.get('port')}")
        
        # Cleanup
        if os.path.exists('captcha_image.png'):
            print(f"\n🗑️  CAPTCHA image saved as 'captcha_image.png' for reference")
            
    except KeyboardInterrupt:
        print("\n\n👋 Scraping interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n" + "=" * 70)
        print("✅ IGR QR Code Scraping Session Complete")
        print("\n📚 Usage Summary:")
        print("- Run with --no-proxy to disable proxy")
        print("- Run with --test-proxy to test proxy connection")
        print("- Run with --proxy-password YOUR_PASSWORD to set proxy password")
        print("- Each request uses a different IP address")
        print("- Form submissions maintain the same IP (sticky session)")

if __name__ == "__main__":
    main() 