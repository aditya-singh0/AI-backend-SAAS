#!/usr/bin/env python3
"""
OCR Setup Script for CAPTCHA Reading
Helps install and configure Tesseract OCR
"""

import os
import sys
import subprocess
import platform

def check_tesseract():
    """Check if Tesseract is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Tesseract OCR is already installed!")
        print(f"Version: {result.stdout.split()[1]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract OCR not found")
        return False

def install_tesseract():
    """Install Tesseract OCR based on OS"""
    system = platform.system().lower()
    
    print(f"🔧 Installing Tesseract OCR for {system}...")
    
    if system == "windows":
        print("\n📝 For Windows:")
        print("1. Download Tesseract installer from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install it to default location (C:\\Program Files\\Tesseract-OCR)")
        print("3. Add to PATH: C:\\Program Files\\Tesseract-OCR")
        print("4. Restart your command prompt/terminal")
        
    elif system == "darwin":  # macOS
        print("\n📝 For macOS:")
        print("Run: brew install tesseract")
        try:
            subprocess.run(['brew', 'install', 'tesseract'], check=True)
            print("✅ Tesseract installed successfully!")
        except:
            print("❌ Homebrew not found. Install manually or install Homebrew first")
            
    elif system == "linux":
        print("\n📝 For Linux:")
        print("Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("CentOS/RHEL: sudo yum install tesseract")
        print("Arch: sudo pacman -S tesseract")
        
        # Try to install automatically for Ubuntu/Debian
        try:
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
            print("✅ Tesseract installed successfully!")
        except:
            print("⚠️  Please install manually using your package manager")
    
    else:
        print(f"❌ Unsupported OS: {system}")
        return False
    
    return True

def install_python_packages():
    """Install required Python packages"""
    packages = [
        'requests>=2.28.0',
        'beautifulsoup4>=4.11.0',
        'pillow>=9.0.0',
        'pytesseract>=0.3.10',
        'opencv-python>=4.6.0',
        'numpy>=1.21.0',
        'urllib3>=1.26.0',
        'lxml>=4.9.0'
    ]
    
    print("\n📦 Installing Python packages...")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All Python packages installed successfully!")
    return True

def test_setup():
    """Test the complete setup"""
    print("\n🧪 Testing setup...")
    
    try:
        import pytesseract
        from PIL import Image
        import cv2
        import numpy as np
        
        # Test Tesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ pytesseract working, Tesseract version: {version}")
        
        # Test image processing
        test_image = np.zeros((100, 200, 3), dtype=np.uint8)
        cv2.putText(test_image, 'TEST123', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Convert to PIL Image and test OCR
        pil_image = Image.fromarray(test_image)
        text = pytesseract.image_to_string(pil_image, config='--psm 8').strip()
        
        if text:
            print(f"✅ OCR test successful: '{text}'")
        else:
            print("⚠️  OCR test returned empty result (this might be normal)")
        
        print("✅ Setup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 OCR Setup for Agreement Document Downloader")
    print("=" * 60)
    
    # Check current status
    tesseract_installed = check_tesseract()
    
    if not tesseract_installed:
        install_tesseract()
    
    # Install Python packages
    if not install_python_packages():
        print("❌ Failed to install Python packages")
        return False
    
    # Test the setup
    if test_setup():
        print("\n🎉 Setup completed successfully!")
        print("✅ You can now run the document downloader with CAPTCHA support!")
    else:
        print("\n❌ Setup completed with issues")
        print("⚠️  CAPTCHA reading might not work properly")
    
    return True

if __name__ == "__main__":
    main() 