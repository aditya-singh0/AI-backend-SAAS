@echo off
echo Installing Tesseract OCR for Windows...
echo.

REM Check if chocolatey is installed
choco version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Chocolatey found. Installing Tesseract...
    choco install tesseract -y
    echo.
    echo ✅ Tesseract installed successfully!
    echo Setting environment variable...
    setx PATH "%PATH%;C:\Program Files\Tesseract-OCR" /M
    echo.
    echo ✅ Setup complete! Please restart your command prompt.
    echo.
) else (
    echo ❌ Chocolatey not found. Please install Tesseract manually:
    echo.
    echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Run the installer
    echo 3. Add to PATH: C:\Program Files\Tesseract-OCR
    echo.
    echo OR install Chocolatey first:
    echo Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    echo.
)

pause 