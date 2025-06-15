@echo off
echo ====================================================
echo   Maharashtra IGR QR Code Scraper - Windows Runner
echo ====================================================
echo.

REM Check if Python is installed
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
py --version
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo [ERROR] Not in the AI-backend-SAAS directory
    echo Please run this script from the AI-backend-SAAS folder
    pause
    exit /b 1
)

REM Install/upgrade pip
echo [1/3] Upgrading pip...
py -m pip install --upgrade pip --quiet

REM Install requirements
echo [2/3] Installing requirements...
echo This may take a few minutes on first run...
py -m pip install -r requirements.txt --quiet

REM Check if installation was successful
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements
    echo Trying verbose install to see errors...
    py -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [3/3] All dependencies installed successfully!
echo.
echo ====================================================
echo                  SCRAPER OPTIONS
echo ====================================================
echo.
echo Choose an option:
echo 1. Run scraper WITH proxy (IP rotation enabled)
echo 2. Run scraper WITHOUT proxy (direct connection)
echo 3. Test proxy connection
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="4" exit /b 0

if "%choice%"=="3" (
    echo.
    set /p proxy_pass="Enter your proxy password: "
    echo.
    echo Testing proxy connection...
    py test_igr_with_proxy.py --test-proxy --proxy-password "%proxy_pass%"
    pause
    exit /b 0
)

if "%choice%"=="2" (
    echo.
    echo Starting scraper without proxy...
    py test_igr_with_proxy.py --no-proxy
    pause
    exit /b 0
)

if "%choice%"=="1" (
    echo.
    set /p proxy_pass="Enter your proxy password: "
    echo.
    echo Starting scraper with proxy...
    echo - IP rotation will be enabled
    echo - Each request will use a different IP
    echo.
    py test_igr_with_proxy.py --proxy-password "%proxy_pass%"
    pause
    exit /b 0
)

echo Invalid choice!
pause 