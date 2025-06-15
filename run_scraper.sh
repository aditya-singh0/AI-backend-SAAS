#!/bin/bash

echo "===================================================="
echo "  Maharashtra IGR QR Code Scraper - Linux/WSL Runner"
echo "===================================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python3 is not installed"
    echo "Please install Python3:"
    echo "  sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python is installed"
python3 --version
echo

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[ERROR]${NC} Not in the AI-backend-SAAS directory"
    echo "Please run this script from the AI-backend-SAAS folder"
    exit 1
fi

# Install/upgrade pip
echo "[1/3] Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install requirements
echo "[2/3] Installing requirements..."
echo "This may take a few minutes on first run..."
python3 -m pip install -r requirements.txt --quiet

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to install requirements"
    echo "Trying verbose install to see errors..."
    python3 -m pip install -r requirements.txt
    exit 1
fi

echo
echo -e "${GREEN}[3/3] All dependencies installed successfully!${NC}"
echo
echo "===================================================="
echo "                 SCRAPER OPTIONS"
echo "===================================================="
echo
echo "Choose an option:"
echo "1. Run scraper WITH proxy (IP rotation enabled)"
echo "2. Run scraper WITHOUT proxy (direct connection)"
echo "3. Test proxy connection"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    4)
        exit 0
        ;;
    3)
        echo
        read -s -p "Enter your proxy password: " proxy_pass
        echo
        echo
        echo "Testing proxy connection..."
        python3 test_igr_with_proxy.py --test-proxy --proxy-password "$proxy_pass"
        ;;
    2)
        echo
        echo "Starting scraper without proxy..."
        python3 test_igr_with_proxy.py --no-proxy
        ;;
    1)
        echo
        read -s -p "Enter your proxy password: " proxy_pass
        echo
        echo
        echo "Starting scraper with proxy..."
        echo "- IP rotation will be enabled"
        echo "- Each request will use a different IP"
        echo
        python3 test_igr_with_proxy.py --proxy-password "$proxy_pass"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac 