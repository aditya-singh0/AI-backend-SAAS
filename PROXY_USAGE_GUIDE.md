# Proxy IP Rotation Guide for IGR Scraper

## Overview
This guide explains how to use the residential proxy integration with the Maharashtra IGR QR Code Scraper for IP rotation and anonymous browsing.

## Features
✅ **IP Rotation**: Each request can use a different IP address  
✅ **Sticky Sessions**: Maintain same IP during form submission workflow  
✅ **Residential IPs**: Use real residential IP addresses for better success rates  
✅ **Session Management**: Automatic session ID generation for IP control  
✅ **Proxy Testing**: Built-in proxy connection testing  

## Quick Start

### 1. Install Python (if not already installed)
First, ensure Python is installed on your system.

### 2. Install Dependencies
```bash
cd AI-backend-SAAS
pip install -r requirements.txt
```

### 3. Configure Proxy Credentials
You have three options:

#### Option A: Command Line (Recommended for testing)
```bash
python test_igr_with_proxy.py --proxy-password YOUR_PASSWORD
```

#### Option B: Environment File
1. Copy the example config:
   ```bash
   copy proxy_config.env.example proxy_config.env
   ```
2. Edit `proxy_config.env` and add your password:
   ```
   PROXY_PASSWORD=your_actual_password
   ```

#### Option C: Environment Variable
```bash
set PROXY_PASSWORD=your_actual_password
python test_igr_with_proxy.py
```

## Usage Examples

### Test Proxy Connection
Test if your proxy is working and see IP rotation in action:
```bash
python test_igr_with_proxy.py --test-proxy --proxy-password YOUR_PASSWORD
```

Expected output:
```
📊 Testing IP Rotation (3 different IPs):
   Test 1: ✅ IP: 185.123.45.67
   Test 2: ✅ IP: 192.168.89.101
   Test 3: ✅ IP: 178.234.56.78
```

### Run Scraper with Proxy
```bash
python test_igr_with_proxy.py --proxy-password YOUR_PASSWORD
```

### Run Scraper without Proxy
```bash
python test_igr_with_proxy.py --no-proxy
```

## How IP Rotation Works

### 1. **Different IP for Each Request Type**
- Initial page load: New IP
- CAPTCHA download: Sticky session (same IP)
- Form submission: Same IP as CAPTCHA
- QR code images: New IP for each image

### 2. **Session ID Format**
The proxy uses session IDs to control IP addresses:
```
td-customer-hdXMhtuot8ni-sessid-abc123xyz-20250106120530
```

### 3. **Sticky Sessions**
During form workflows, the scraper maintains the same IP to avoid detection:
- CAPTCHA request → Session ID generated
- Form submission → Same session ID used
- Ensures consistency from the website's perspective

## Proxy Configuration Details

### Your ThorData Proxy Settings
- **Endpoint**: `42q6t9rp.pr.thordata.net:9999`
- **Username**: `td-customer-hdXMhtuot8ni`
- **Authentication**: Username + Password
- **Type**: Residential rotating proxy

### Session Rotation
To get a new IP, append a session ID to your username:
```
Username format: td-customer-hdXMhtuot8ni-sessid-[RANDOM_ID]
```

## Code Integration

### Using in Your Own Code
```python
from src.enhanced_proxy_manager import EnhancedProxyManager
from src.igr_specialized_scraper import IGRSpecializedScraper

# Configure proxy
proxy_config = {
    'host': '42q6t9rp.pr.thordata.net',
    'port': '9999',
    'username': 'td-customer-hdXMhtuot8ni',
    'password': 'your_password'
}

# Create scraper with proxy
scraper = IGRSpecializedScraper(use_proxy=True)

# Run workflow
results = scraper.full_igr_workflow(igr_url)
```

### Manual Proxy Testing
```python
from src.enhanced_proxy_manager import EnhancedProxyManager

proxy_manager = EnhancedProxyManager(proxy_config)

# Test connection
result = proxy_manager.test_proxy_connection()
print(f"IP: {result['ip']}")

# Get proxy for requests
proxy = proxy_manager.get_proxy(rotate_ip=True)
```

## Benefits of Using Proxy

1. **Avoid Rate Limiting**: Different IPs prevent blocking
2. **Anonymous Browsing**: Hide your real IP address
3. **Geographic Flexibility**: Access from different locations
4. **Better Success Rate**: Residential IPs are less likely to be blocked
5. **Session Control**: Maintain consistency when needed

## Troubleshooting

### Proxy Connection Failed
- Check your password is correct
- Ensure you have active proxy balance
- Verify internet connection

### Same IP Appearing
- This is intentional during form submission (sticky session)
- For new IPs, ensure `rotate_ip=True` is used

### Slow Performance
- Proxy adds latency (normal behavior)
- Residential proxies are slower than datacenter proxies
- This is a tradeoff for better success rates

## Advanced Configuration

### Custom Session Duration
Control how long to maintain the same IP:
```python
proxy_manager.sticky_session_id = "custom-session-123"
```

### Force New IP
```python
proxy_config = proxy_manager.get_proxy(rotate_ip=True)
```

### Use Specific Session
```python
proxy_config = proxy_manager.get_sticky_proxy("my-session-id")
```

## Security Notes
- Never commit your proxy password to version control
- Use environment variables for production
- Monitor your proxy usage/balance
- Respect website terms of service

## Performance Tips
- Use sticky sessions for related requests
- Rotate IPs only when necessary
- Cache results when possible
- Add delays between requests to appear more natural 