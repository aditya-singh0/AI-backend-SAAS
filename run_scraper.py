#!/usr/bin/env python3
"""
Maharashtra IGR QR Code Scraper - Easy Runner
This script provides a simple interface to run the IGR scraper
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("  Maharashtra IGR QR Code Scraper - Easy Runner")
    print("=" * 60)
    print()

def check_python():
    """Check if Python is properly installed"""
    print("🔍 Checking Python installation...")
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is installed")
    print()

def install_requirements():
    """Install required packages"""
    print("📦 Installing/updating dependencies...")
    print("This may take a few minutes on first run...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
        
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Trying verbose install to see errors...")
        subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False

def test_proxy(password):
    """Test proxy connection"""
    print("\n🔧 Testing proxy connection...")
    cmd = [sys.executable, "test_igr_with_proxy.py", "--test-proxy"]
    if password:
        cmd.extend(["--proxy-password", password])
    
    subprocess.call(cmd)

def run_scraper_with_proxy(password):
    """Run scraper with proxy"""
    print("\n🚀 Starting scraper with proxy...")
    print("   - IP rotation enabled")
    print("   - Each request will use a different IP")
    print("   - Form submissions will maintain same IP (sticky session)")
    print()
    
    cmd = [sys.executable, "test_igr_with_proxy.py"]
    if password:
        cmd.extend(["--proxy-password", password])
    
    subprocess.call(cmd)

def run_scraper_without_proxy():
    """Run scraper without proxy"""
    print("\n🚀 Starting scraper without proxy...")
    print("   - Direct connection will be used")
    print("   - No IP rotation")
    print()
    
    subprocess.call([sys.executable, "test_igr_with_proxy.py", "--no-proxy"])

def get_menu_choice():
    """Display menu and get user choice"""
    print("\n" + "=" * 60)
    print("                    MAIN MENU")
    print("=" * 60)
    print()
    print("1. 🔄 Run scraper WITH proxy (IP rotation enabled)")
    print("2. 🌐 Run scraper WITHOUT proxy (direct connection)")
    print("3. 🔧 Test proxy connection")
    print("4. 📋 View proxy configuration")
    print("5. ❌ Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("Invalid choice! Please enter 1-5.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return '5'

def view_proxy_config():
    """Display proxy configuration"""
    print("\n📋 Proxy Configuration:")
    print("-" * 40)
    print(f"Host: 42q6t9rp.pr.thordata.net")
    print(f"Port: 9999")
    print(f"Username: td-customer-hdXMhtuot8ni")
    print(f"Type: Residential Rotating Proxy")
    print("-" * 40)
    print("\nFor IP rotation, session IDs are appended to username:")
    print("Example: td-customer-hdXMhtuot8ni-sessid-abc123xyz")
    print()

def main():
    """Main function"""
    print_banner()
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: Not in the AI-backend-SAAS directory")
        print("Please run this script from the AI-backend-SAAS folder")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    check_python()
    
    # Install requirements
    if not install_requirements():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Main loop
    while True:
        choice = get_menu_choice()
        
        if choice == '5':
            print("\n👋 Thank you for using IGR Scraper!")
            break
        
        elif choice == '4':
            view_proxy_config()
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            password = getpass.getpass("\n🔐 Enter your proxy password (hidden): ")
            test_proxy(password)
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            run_scraper_without_proxy()
            input("\nPress Enter to continue...")
        
        elif choice == '1':
            password = getpass.getpass("\n🔐 Enter your proxy password (hidden): ")
            run_scraper_with_proxy(password)
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...") 