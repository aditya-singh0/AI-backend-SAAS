# 🖥️ VM Setup Guide - IGR Scraper

## 🚀 Complete VM Setup for IGR Scraper

### Prerequisites
- Windows VM with internet access
- Admin privileges on the VM
- At least 4GB RAM and 20GB free disk space

## 📋 Step-by-Step Setup

### Step 1: Transfer Files to VM
1. Copy the entire `AI-backend-SAAS` folder to your VM
2. Place it in a directory like `C:\IGR-Scraper\`

### Step 2: Install Python (if not installed)
```powershell
# Check if Python is installed
python --version

# If not installed, download from python.org
# Or use chocolatey (recommended)
```

### Step 3: Install Chocolatey (Package Manager)
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Step 4: Install Python via Chocolatey
```powershell
# Install Python (if needed)
choco install python -y

# Refresh environment variables
refreshenv
```

### Step 5: Install Tesseract OCR
```powershell
# Navigate to the AI-backend-SAAS directory
cd C:\IGR-Scraper\AI-backend-SAAS

# Run the installer
.\install_tesseract.bat
```

### Step 6: Install Python Dependencies
```powershell
# Still in AI-backend-SAAS directory
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 7: Verify Installation
```powershell
# Test if everything is installed correctly
python -c "import cv2, pytesseract, requests, selenium; print('✅ All dependencies ready!')"

# Test Tesseract
tesseract --version
```

## 🎯 Running the Scraper

### Option 1: Easy Menu Interface (Recommended)
```powershell
cd C:\IGR-Scraper\AI-backend-SAAS
python run_scraper.py
```

### Option 2: Direct Script Execution
```powershell
# Interactive Mumbai scraper (best for manual control)
python mumbai_interactive_scraper.py

# Automated with proxy
python test_igr_with_proxy.py --proxy-password YOUR_PASSWORD

# Without proxy (direct connection)
python test_igr_with_proxy.py --no-proxy
```

### Option 3: Selenium-Based (Most Reliable)
```powershell
# Interactive selenium scraper
python selenium_bulk_igr_scraper.py

# Mumbai-specific scraper
python final_mumbai_scraper.py
```

## 🔧 VM-Specific Optimizations

### 1. Disable Windows Defender (Temporary)
```powershell
# Temporarily disable real-time protection
Set-MpPreference -DisableRealtimeMonitoring $true
```

### 2. Increase Virtual Memory
- Control Panel > System > Advanced System Settings
- Performance Settings > Advanced > Virtual Memory
- Set to 8GB+ if possible

### 3. Network Settings
```powershell
# Disable IPv6 if causing issues
netsh interface ipv6 set global randomizeidentifiers=disabled
```

## 📊 Expected Results on VM

### With Full Setup:
- ✅ Automatic CAPTCHA solving
- ✅ IP rotation with proxy
- ✅ 25+ documents downloaded per session
- ✅ PDF generation and organization

### Performance Expectations:
- **Setup time**: 15-20 minutes
- **Per document**: 30-60 seconds
- **Session duration**: 10-15 minutes for 25 documents
- **Success rate**: 85-95%

## 🛠️ Troubleshooting VM Issues

### Common VM Problems:

#### 1. Slow Performance
```powershell
# Use lighter version
python simple_agreement_downloader.py
```

#### 2. Network Timeouts
```powershell
# Use longer timeouts
python selenium_bulk_igr_scraper.py
```

#### 3. Memory Issues
```powershell
# Use minimal version
python simple_igr_test.py
```

#### 4. Display Issues
```powershell
# Use headless mode
python headless_automation.py
```

## 🚀 Quick Start Commands

### Test Setup
```powershell
cd C:\IGR-Scraper\AI-backend-SAAS
python debug_test.py
```

### Run Quick Test (2 documents)
```powershell
python simple_agreement_downloader.py
# When prompted, enter: 2
```

### Full Production Run (25 documents)
```powershell
python run_scraper.py
# Choose option 1 (with proxy)
# Enter your proxy password
```

## 📈 Performance Monitoring

### Monitor Resource Usage
```powershell
# In another PowerShell window
while ($true) { 
    Get-Process python | Select-Object Name, CPU, WorkingSet
    Start-Sleep 5
}
```

### Monitor Network Activity
```powershell
netstat -an | findstr :80
netstat -an | findstr :443
```

## 🔐 Security Notes for VM

1. **Isolated environment**: VM provides security isolation
2. **Snapshot capability**: Take snapshots before major runs
3. **Network isolation**: Consider using NAT networking
4. **Firewall settings**: Configure Windows Firewall appropriately

## 📞 VM-Specific Support

### If issues persist:
1. Check VM memory allocation (min 4GB)
2. Verify network connectivity
3. Ensure VM tools are installed
4. Check host system resources

### Emergency Fallback:
```powershell
# Simple manual version
python manual_form_scraper.py
```

## 🎯 Next Steps

1. **Test run**: Start with `python simple_test.py`
2. **Small batch**: Run `python simple_agreement_downloader.py` with 2-3 documents
3. **Full automation**: Use `python run_scraper.py` for production runs
4. **Scale up**: Multiple VMs can run in parallel for faster processing 