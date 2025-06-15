#!/usr/bin/env python3
"""
Python SSL Certificate Generator (No OpenSSL Required)
Generates self-signed SSL certificates using Python cryptography library
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

def install_cryptography():
    """Install cryptography library if not available"""
    try:
        import cryptography
        print("✅ Cryptography library available")
        return True
    except ImportError:
        print("📦 Installing cryptography library...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
            print("✅ Cryptography library installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install cryptography library")
            print("   Please run: pip install cryptography")
            return False

def generate_ssl_certificate_python(domain="localhost", ip="127.0.0.1", days=365):
    """Generate SSL certificate using Python cryptography library"""
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
    except ImportError:
        print("❌ Cryptography library not available")
        return None, None
    
    print(f"🔐 GENERATING SSL CERTIFICATE (Python Method)")
    print("=" * 50)
    print(f"Domain: {domain}")
    print(f"IP: {ip}")
    print(f"Valid for: {days} days")
    print("=" * 50)
    
    # Create ssl directory
    ssl_dir = Path("ssl_certificates")
    ssl_dir.mkdir(exist_ok=True)
    
    # File paths
    key_file = ssl_dir / "server.key"
    cert_file = ssl_dir / "server.crt"
    
    try:
        # Generate private key
        print("🔑 Generating private key...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate subject
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IGR Scraper"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IT Department"),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])
        
        # Create certificate
        print("📜 Generating certificate...")
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain),
                x509.DNSName(f"*.{domain}"),
                x509.IPAddress(ipaddress.ip_address(ip)),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("\n✅ SSL CERTIFICATE GENERATED SUCCESSFULLY!")
        print("=" * 50)
        print(f"🔑 Private Key: {key_file.absolute()}")
        print(f"📜 Certificate: {cert_file.absolute()}")
        
        # Display certificate info
        print("\n📋 CERTIFICATE INFORMATION:")
        print(f"   Subject: {cert.subject.rfc4514_string()}")
        print(f"   Valid From: {cert.not_valid_before}")
        print(f"   Valid Until: {cert.not_valid_after}")
        print(f"   Serial Number: {cert.serial_number}")
        
        return str(key_file), str(cert_file)
        
    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        return None, None

def create_flask_https_app():
    """Create Flask HTTPS application for the scraper"""
    
    flask_app_code = '''#!/usr/bin/env python3
"""
IGR Scraper HTTPS API Server
Secure Flask application for running the scraper on VM
"""

from flask import Flask, jsonify, request, render_template_string
import ssl
import os
import sys
from datetime import datetime
import threading
import time

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IGR Scraper API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .status { padding: 15px; border-radius: 5px; margin: 20px 0; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .form-group { margin: 20px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .endpoint { background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 IGR Scraper HTTPS API</h1>
            <p>Secure Maharashtra IGR Document Scraper</p>
        </div>
        
        <div class="status success">
            <strong>✅ SSL/TLS Encryption Active</strong><br>
            Server running securely with self-signed certificate
        </div>
        
        <div class="status info">
            <strong>📡 API Endpoints Available:</strong><br>
            <div class="endpoint">GET /api/status - Check scraper status</div>
            <div class="endpoint">POST /api/scrape - Start document scraping</div>
            <div class="endpoint">GET /api/results - Get scraping results</div>
        </div>
        
        <h3>🚀 Start Scraping</h3>
        <form id="scrapeForm">
            <div class="form-group">
                <label>District:</label>
                <select id="district" name="district">
                    <option value="31">Mumbai</option>
                    <option value="32">Pune</option>
                    <option value="21">Nashik</option>
                    <option value="20">Nagpur</option>
                </select>
            </div>
            <div class="form-group">
                <label>Year:</label>
                <input type="number" id="year" name="year" value="2024" min="2019" max="2024">
            </div>
            <div class="form-group">
                <label>Village/Area:</label>
                <input type="text" id="village" name="village" placeholder="e.g., Andheri, Bandra">
            </div>
            <button type="submit" class="btn">🔍 Start Scraping</button>
        </form>
        
        <div id="results" style="margin-top: 30px;"></div>
    </div>
    
    <script>
        document.getElementById('scrapeForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                district: document.getElementById('district').value,
                year: document.getElementById('year').value,
                village: document.getElementById('village').value
            };
            
            document.getElementById('results').innerHTML = '<div class="status info">🔄 Scraping in progress...</div>';
            
            fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('results').innerHTML = 
                    '<div class="status ' + (data.status === 'success' ? 'success' : 'info') + '">' +
                    '<strong>' + data.status.toUpperCase() + '</strong><br>' +
                    data.message + '</div>';
            })
            .catch(error => {
                document.getElementById('results').innerHTML = 
                    '<div class="status" style="background: #f8d7da; color: #721c24;">❌ Error: ' + error + '</div>';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """Get API status"""
    return jsonify({
        "status": "online",
        "ssl_enabled": True,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "endpoints": [
            "GET /api/status",
            "POST /api/scrape", 
            "GET /api/results"
        ]
    })

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """Start scraping process"""
    try:
        data = request.get_json()
        district = data.get('district', '31')
        year = data.get('year', '2024')
        village = data.get('village', 'Andheri')
        
        # Here you would integrate your scraper
        # For now, return a mock response
        
        return jsonify({
            "status": "success",
            "message": f"Scraping initiated for {village}, District {district}, Year {year}",
            "parameters": {
                "district": district,
                "year": year,
                "village": village
            },
            "job_id": f"job_{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/results')
def api_results():
    """Get scraping results"""
    return jsonify({
        "status": "completed",
        "documents_found": 0,
        "message": "No documents found for the specified parameters",
        "timestamp": datetime.now().isoformat()
    })

def run_https_server(host='0.0.0.0', port=5000):
    """Run the HTTPS server"""
    cert_file = "ssl_certificates/server.crt"
    key_file = "ssl_certificates/server.key"
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("❌ SSL certificates not found!")
        print("   Run python_ssl_generator.py first!")
        return
    
    print("🚀 IGR Scraper HTTPS API Server")
    print("=" * 40)
    print(f"🔐 SSL/TLS encryption: ENABLED")
    print(f"📡 Server address: https://{host}:{port}")
    print(f"🌐 Web interface: https://localhost:{port}")
    print(f"📋 API status: https://localhost:{port}/api/status")
    print("=" * 40)
    print("⚠️  Browser security warning is normal for self-signed certificates")
    print("   Click 'Advanced' → 'Proceed to localhost (unsafe)' to continue")
    print("=" * 40)
    
    try:
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        
        app.run(
            host=host,
            port=port,
            ssl_context=context,
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    run_https_server()
'''
    
    with open("igr_scraper_https_server.py", 'w', encoding='utf-8') as f:
        f.write(flask_app_code)
    
    print(f"📝 Created HTTPS Flask app: igr_scraper_https_server.py")

def create_deployment_guide():
    """Create deployment guide for VM"""
    
    guide_content = '''# 🚀 IGR Scraper VM Deployment Guide

## 📋 Prerequisites

1. **Python 3.7+** installed on VM
2. **pip** package manager
3. **Internet connection** for package installation

## 🔧 Installation Steps

### 1. Install Required Packages
```bash
pip install flask cryptography requests selenium easyocr
```

### 2. Generate SSL Certificates
```bash
python python_ssl_generator.py
```

### 3. Start HTTPS Server
```bash
python igr_scraper_https_server.py
```

## 🌐 Access Your Scraper

- **Web Interface**: https://your-vm-ip:5000
- **API Status**: https://your-vm-ip:5000/api/status
- **Start Scraping**: POST to https://your-vm-ip:5000/api/scrape

## 🔐 SSL Certificate Notes

- **Self-signed certificate** - browsers will show security warnings
- Click "Advanced" → "Proceed to [domain] (unsafe)" to continue
- For production, use certificates from a trusted CA

## 📡 API Usage Examples

### Check Status
```bash
curl -k https://your-vm-ip:5000/api/status
```

### Start Scraping
```bash
curl -k -X POST https://your-vm-ip:5000/api/scrape \\
  -H "Content-Type: application/json" \\
  -d '{"district": "31", "year": "2024", "village": "Andheri"}'
```

## 🛡️ Security Considerations

1. **Firewall**: Open port 5000 for HTTPS traffic
2. **Access Control**: Implement authentication for production
3. **Certificate**: Use proper CA-signed certificates for production
4. **Updates**: Keep packages updated regularly

## 🔧 Troubleshooting

### Certificate Issues
- Regenerate certificates: `python python_ssl_generator.py`
- Check file permissions on ssl_certificates folder

### Port Issues
- Change port in `igr_scraper_https_server.py` if 5000 is occupied
- Update firewall rules accordingly

### Browser Warnings
- Normal for self-signed certificates
- Add certificate to browser's trusted store to avoid warnings

## 📁 File Structure
```
your-project/
├── ssl_certificates/
│   ├── server.crt
│   └── server.key
├── python_ssl_generator.py
├── igr_scraper_https_server.py
└── your_scraper_files.py
```

## 🚀 Production Deployment

For production environments:
1. Use a proper domain name
2. Get SSL certificate from Let's Encrypt or commercial CA
3. Use a reverse proxy (nginx/Apache)
4. Implement proper authentication
5. Set up monitoring and logging
'''
    
    with open("VM_DEPLOYMENT_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"📖 Created deployment guide: VM_DEPLOYMENT_GUIDE.md")

def main():
    """Main function"""
    print("🔐 PYTHON SSL CERTIFICATE GENERATOR")
    print("=" * 50)
    print("🐍 No OpenSSL required - Pure Python solution!")
    print("=" * 50)
    
    # Install cryptography if needed
    if not install_cryptography():
        return
    
    # Get user input
    print("\n📝 Certificate Configuration:")
    domain = input("Enter domain name (default: localhost): ").strip() or "localhost"
    ip = input("Enter IP address (default: 127.0.0.1): ").strip() or "127.0.0.1"
    
    try:
        days = int(input("Certificate validity in days (default: 365): ").strip() or "365")
    except ValueError:
        days = 365
    
    # Generate certificate
    key_file, cert_file = generate_ssl_certificate_python(domain, ip, days)
    
    if key_file and cert_file:
        # Create Flask HTTPS app
        create_flask_https_app()
        create_deployment_guide()
        
        print("\n🚀 HTTPS SERVER READY!")
        print("=" * 50)
        print("📁 Files created:")
        print(f"   🔑 SSL Key: {key_file}")
        print(f"   📜 SSL Certificate: {cert_file}")
        print(f"   🌐 HTTPS Server: igr_scraper_https_server.py")
        print(f"   📖 Deployment Guide: VM_DEPLOYMENT_GUIDE.md")
        
        print("\n🚀 Quick Start:")
        print("1. pip install flask cryptography")
        print("2. python igr_scraper_https_server.py")
        print("3. Open https://localhost:5000")
        
        print("\n⚠️  Security Note:")
        print("   Browser will show security warning for self-signed certificate")
        print("   This is normal - click 'Advanced' → 'Proceed to localhost'")

if __name__ == "__main__":
    main() 