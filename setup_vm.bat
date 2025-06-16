@echo off
title IGR Scraper - VM Setup Script
color 0A
echo.
echo ===================================================================
echo                    IGR Scraper - VM Setup Script
echo ===================================================================
echo.
echo This script will set up everything needed to run the IGR scraper
echo on your Virtual Machine.
echo.
echo What this script does:
echo  1. Install Python (if needed)
echo  2. Install Tesseract OCR for CAPTCHA solving
echo  3. Install all Python dependencies
echo  4. Test the installation
echo  5. Create desktop shortcuts
echo.
echo Prerequisites:
echo  - Internet connection
echo  - Administrator privileges
echo  - At least 4GB free disk space
echo.
pause
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo ✅ Running with administrator privileges
echo.

REM Check if chocolatey is installed
echo 📦 Checking for Chocolatey package manager...
choco version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Chocolatey
        echo Please install manually from https://chocolatey.org/install
        pause
        exit /b 1
    )
    echo ✅ Chocolatey installed successfully
) else (
    echo ✅ Chocolatey already installed
)
echo.

REM Refresh environment variables
echo 🔄 Refreshing environment variables...
call refreshenv

REM Check if Python is installed
echo 🐍 Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python...
    choco install python -y
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Python
        pause
        exit /b 1
    )
    echo ✅ Python installed successfully
    call refreshenv
) else (
    echo ✅ Python already installed
)
echo.

REM Check if Tesseract is installed
echo 🔍 Checking for Tesseract OCR...
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Tesseract OCR...
    choco install tesseract -y
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Tesseract
        pause
        exit /b 1
    )
    echo ✅ Tesseract installed successfully
    call refreshenv
) else (
    echo ✅ Tesseract already installed
)
echo.

REM Install Python dependencies
echo 📋 Installing Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    echo Trying verbose install...
    python -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Python dependencies installed successfully
echo.

REM Test the installation
echo 🧪 Testing installation...
python -c "import cv2, pytesseract, requests, beautifulsoup4; print('✅ All core dependencies working!')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Some dependencies failed to import
    echo Running diagnostic...
    python -c "
import sys
modules = ['cv2', 'pytesseract', 'requests', 'beautifulsoup4', 'selenium', 'pillow']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module} - OK')
    except ImportError as e:
        print(f'❌ {module} - FAILED: {e}')
"
    echo.
    echo Some modules failed. You may need to install them manually.
    pause
) else (
    echo ✅ All dependencies are working correctly!
)
echo.

REM Create desktop shortcuts
echo 🔗 Creating desktop shortcuts...
set DESKTOP=%USERPROFILE%\Desktop
set CURRENT_DIR=%CD%

REM Create shortcut for main scraper
echo @echo off > "%DESKTOP%\IGR Scraper.bat"
echo cd /d "%CURRENT_DIR%" >> "%DESKTOP%\IGR Scraper.bat"
echo python run_scraper.py >> "%DESKTOP%\IGR Scraper.bat"
echo pause >> "%DESKTOP%\IGR Scraper.bat"

REM Create shortcut for simple test
echo @echo off > "%DESKTOP%\IGR Test.bat"
echo cd /d "%CURRENT_DIR%" >> "%DESKTOP%\IGR Test.bat"
echo python simple_test.py >> "%DESKTOP%\IGR Test.bat"
echo pause >> "%DESKTOP%\IGR Test.bat"

REM Create shortcut for selenium scraper
echo @echo off > "%DESKTOP%\IGR Selenium.bat"
echo cd /d "%CURRENT_DIR%" >> "%DESKTOP%\IGR Selenium.bat"
echo python selenium_bulk_igr_scraper.py >> "%DESKTOP%\IGR Selenium.bat"
echo pause >> "%DESKTOP%\IGR Selenium.bat"

echo ✅ Desktop shortcuts created
echo.

REM Final test
echo 🎯 Running final test...
python simple_test.py
echo.

REM Setup complete
echo ===================================================================
echo                        SETUP COMPLETE! 
echo ===================================================================
echo.
echo 🎉 Your VM is now ready to run the IGR scraper!
echo.
echo Next steps:
echo  1. Check your desktop for IGR scraper shortcuts
echo  2. Run a quick test: Double-click "IGR Test" on desktop
echo  3. For full scraping: Double-click "IGR Scraper" on desktop
echo.
echo Available scripts:
echo  • run_scraper.py        - Main menu interface
echo  • simple_test.py        - Quick test (recommended first)
echo  • selenium_bulk_igr_scraper.py - Browser automation
echo  • mumbai_interactive_scraper.py - Interactive scraper
echo.
echo 📋 Usage notes:
echo  • Use proxy for best results (IP rotation)
echo  • Start with small batches (2-5 documents)
echo  • Check downloaded files in data/ folder
echo.
echo 🆘 If you encounter issues:
echo  • Check VM_SETUP_GUIDE.md for troubleshooting
echo  • Ensure VM has at least 4GB RAM allocated
echo  • Verify internet connection is stable
echo.
echo Press any key to exit...
pause >nul 