# 🚀 Quick Start Guide - IGR QR Code Scraper

## 📋 How to Run the Scraper

You have **3 ways** to run the scraper:

### Option 1: Windows (Easiest) 🪟
Double-click on `run_scraper.bat` or run in PowerShell:
```powershell
.\run_scraper.bat
```

### Option 2: Python Script (Cross-platform) 🐍
Run in terminal/command prompt:
```bash
py run_scraper.py
```
or
```bash
python run_scraper.py
```

### Option 3: Linux/WSL 🐧
First make the script executable:
```bash
chmod +x run_scraper.sh
./run_scraper.sh
```

## 🔑 What You'll Need

1. **Proxy Password** - Your ThorData proxy password for IP rotation
2. **Python Installed** - The scripts will check this automatically

## 📱 What the Scraper Does

1. **Connects** to Maharashtra IGR website
2. **Downloads** CAPTCHA image (you solve it)
3. **Fills** the property search form
4. **Searches** for QR codes in results
5. **Extracts** and decodes QR data

## ⚡ Quick Commands

### Test Proxy Connection
```bash
py test_igr_with_proxy.py --test-proxy --proxy-password YOUR_PASSWORD
```

### Run Without Menu
```bash
py test_igr_with_proxy.py --proxy-password YOUR_PASSWORD
```

### Run Without Proxy
```bash
py test_igr_with_proxy.py --no-proxy
```

## 🆘 Troubleshooting

- **Python not found**: Install from [python.org](https://python.org)
- **Dependencies fail**: Run `py -m pip install -r requirements.txt`
- **Proxy fails**: Check your password and internet connection

## 📞 Need Help?

Check the full documentation:
- [IGR Usage Guide](IGR_USAGE_GUIDE.md)
- [Proxy Usage Guide](PROXY_USAGE_GUIDE.md) 