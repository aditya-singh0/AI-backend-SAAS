#!/usr/bin/env python3
"""
SSL Certificate Generator for VM Deployment
Generates self-signed SSL certificates for HTTPS server deployment
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta

def check_openssl():
    """Check if OpenSSL is available"""
    try:
        result = subprocess.run(['openssl', 'version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ OpenSSL found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found. Please install OpenSSL first.")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("   Linux: sudo apt-get install openssl")
        print("   macOS: brew install openssl")
        return False

def generate_ssl_certificate(domain="localhost", ip="127.0.0.1", days=365):
    """Generate self-signed SSL certificate"""
    
    print(f"🔐 GENERATING SSL CERTIFICATE")
    print("=" * 50)
    print(f"Domain: {domain}")
    print(f"IP: {ip}")
    print(f"Valid for: {days} days")
    print("=" * 50)
    
    # Create ssl directory
    ssl_dir = "ssl_certificates"
    os.makedirs(ssl_dir, exist_ok=True)
    
    # File paths
    key_file = os.path.join(ssl_dir, "server.key")
    cert_file = os.path.join(ssl_dir, "server.crt")
    config_file = os.path.join(ssl_dir, "openssl.conf")
    
    # Create OpenSSL config file
    config_content = f"""[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = IN
ST = Maharashtra
L = Mumbai
O = IGR Scraper
OU = IT Department
CN = {domain}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = {domain}
DNS.2 = *.{domain}
IP.1 = {ip}
IP.2 = 127.0.0.1
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"📝 Created OpenSSL config: {config_file}")
    
    try:
        # Generate private key
        print("🔑 Generating private key...")
        subprocess.run([
            'openssl', 'genrsa', 
            '-out', key_file, 
            '2048'
        ], check=True)
        
        # Generate certificate
        print("📜 Generating certificate...")
        subprocess.run([
            'openssl', 'req',
            '-new', '-x509',
            '-key', key_file,
            '-out', cert_file,
            '-days', str(days),
            '-config', config_file,
            '-extensions', 'v3_req'
        ], check=True)
        
        print("\n✅ SSL CERTIFICATE GENERATED SUCCESSFULLY!")
        print("=" * 50)
        print(f"🔑 Private Key: {os.path.abspath(key_file)}")
        print(f"📜 Certificate: {os.path.abspath(cert_file)}")
        print(f"⚙️  Config File: {os.path.abspath(config_file)}")
        
        # Display certificate info
        print("\n📋 CERTIFICATE INFORMATION:")
        result = subprocess.run([
            'openssl', 'x509', '-in', cert_file, 
            '-text', '-noout'
        ], capture_output=True, text=True)
        
        # Extract key information
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Subject:' in line:
                print(f"   Subject: {line.split('Subject:')[1].strip()}")
            elif 'Not Before:' in line:
                print(f"   Valid From: {line.split('Not Before:')[1].strip()}")
            elif 'Not After:' in line:
                print(f"   Valid Until: {line.split('Not After:')[1].strip()}")
        
        return key_file, cert_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating certificate: {e}")
        return None, None

def create_https_server_example():
    """Create example HTTPS server code"""
    
    server_code = '''#!/usr/bin/env python3
"""
HTTPS Server Example for IGR Scraper
Run your scraper with SSL/TLS encryption
"""

import ssl
import http.server
import socketserver
import os
from pathlib import Path

class HTTPSServer:
    def __init__(self, port=8443, cert_file="ssl_certificates/server.crt", 
                 key_file="ssl_certificates/server.key"):
        self.port = port
        self.cert_file = cert_file
        self.key_file = key_file
        
    def start_server(self):
        """Start HTTPS server"""
        
        # Check if certificate files exist
        if not os.path.exists(self.cert_file):
            print(f"❌ Certificate file not found: {self.cert_file}")
            print("   Run generate_ssl_cert.py first!")
            return
            
        if not os.path.exists(self.key_file):
            print(f"❌ Key file not found: {self.key_file}")
            print("   Run generate_ssl_cert.py first!")
            return
        
        # Create HTTPS server
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"🚀 Starting HTTPS server on port {self.port}")
            print(f"🔐 Using certificate: {self.cert_file}")
            print(f"🔑 Using key: {self.key_file}")
            
            # Create SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.cert_file, self.key_file)
            
            # Wrap socket with SSL
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            
            print(f"✅ HTTPS Server running at: https://localhost:{self.port}")
            print("   Press Ctrl+C to stop")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\\n🛑 Server stopped")

if __name__ == "__main__":
    server = HTTPSServer()
    server.start_server()
'''
    
    with open("https_server_example.py", 'w') as f:
        f.write(server_code)
    
    print(f"📝 Created HTTPS server example: https_server_example.py")

def create_flask_https_example():
    """Create Flask HTTPS server example"""
    
    flask_code = '''#!/usr/bin/env python3
"""
Flask HTTPS Server for IGR Scraper API
Secure API endpoint for your scraper
"""

from flask import Flask, jsonify, request
import ssl
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "IGR Scraper API",
        "status": "running",
        "secure": True
    })

@app.route('/api/scrape', methods=['POST'])
def scrape_documents():
    """API endpoint for document scraping"""
    data = request.get_json()
    
    # Your scraper logic here
    return jsonify({
        "status": "success",
        "message": "Scraping initiated",
        "parameters": data
    })

@app.route('/api/status')
def get_status():
    """Get scraper status"""
    return jsonify({
        "status": "ready",
        "ssl_enabled": True,
        "version": "1.0"
    })

if __name__ == '__main__':
    # SSL Configuration
    cert_file = "ssl_certificates/server.crt"
    key_file = "ssl_certificates/server.key"
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("🚀 Starting Flask HTTPS server...")
        print("🔐 SSL/TLS encryption enabled")
        print("📡 API endpoints:")
        print("   GET  https://localhost:5000/")
        print("   POST https://localhost:5000/api/scrape")
        print("   GET  https://localhost:5000/api/status")
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(cert_file, key_file)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            ssl_context=context,
            debug=False
        )
    else:
        print("❌ SSL certificates not found!")
        print("   Run generate_ssl_cert.py first!")
'''
    
    with open("flask_https_server.py", 'w') as f:
        f.write(flask_code)
    
    print(f"📝 Created Flask HTTPS server: flask_https_server.py")

def main():
    """Main function"""
    print("🔐 SSL CERTIFICATE GENERATOR FOR VM DEPLOYMENT")
    print("=" * 60)
    
    if not check_openssl():
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
    key_file, cert_file = generate_ssl_certificate(domain, ip, days)
    
    if key_file and cert_file:
        # Create example servers
        create_https_server_example()
        create_flask_https_example()
        
        print("\n🚀 DEPLOYMENT INSTRUCTIONS:")
        print("=" * 60)
        print("1. Copy the ssl_certificates folder to your VM")
        print("2. Install required packages:")
        print("   pip install flask requests selenium")
        print("3. Run your scraper with HTTPS:")
        print("   python flask_https_server.py")
        print("4. Access via: https://your-vm-ip:5000")
        print("\n⚠️  SECURITY NOTES:")
        print("   - This is a self-signed certificate")
        print("   - Browsers will show security warnings")
        print("   - For production, use certificates from a CA")
        print("   - Keep private key secure!")
        
        print(f"\n📁 Files created in: {os.path.abspath('.')}")

if __name__ == "__main__":
    main() 