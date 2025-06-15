#!/usr/bin/env python3

import sys
import os
import requests
from PIL import Image
from pyzbar.pyzbar import decode
import io

def test_qr_debug():
    print("🔍 QR Code Debug Test")
    print("=" * 40)
    
    # Test URL
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/256px-QR_code_for_mobile_English_Wikipedia.svg.png"
    print(f"Testing URL: {url}")
    
    try:
        # Download image
        print("Downloading image...")
        response = requests.get(url)
        response.raise_for_status()
        print(f"✅ Downloaded {len(response.content)} bytes")
        
        # Open with PIL
        print("Opening image with PIL...")
        image = Image.open(io.BytesIO(response.content))
        print(f"✅ Image opened: {image.format}, {image.size}, {image.mode}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            print(f"Converting from {image.mode} to RGB...")
            image = image.convert('RGB')
        
        # Try to decode
        print("Attempting to decode QR codes...")
        decoded_objects = decode(image)
        print(f"Found {len(decoded_objects)} decoded objects")
        
        if decoded_objects:
            for i, obj in enumerate(decoded_objects):
                print(f"  QR {i+1}: {obj.data.decode('utf-8')}")
                print(f"    Type: {obj.type}")
                print(f"    Rect: {obj.rect}")
        else:
            print("❌ No QR codes detected")
            
            # Try with a simpler approach - save and reload
            print("\nTrying alternative approach...")
            image.save("/tmp/test_qr.png")
            reloaded = Image.open("/tmp/test_qr.png")
            decoded_again = decode(reloaded)
            print(f"Reloaded attempt found {len(decoded_again)} objects")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_with_known_qr():
    print("\n" + "=" * 40)
    print("Testing with a different known QR code...")
    
    # This is a simple QR code that says "Hello World"
    url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=Hello%20World"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"✅ Downloaded {len(response.content)} bytes")
        
        image = Image.open(io.BytesIO(response.content))
        print(f"✅ Image opened: {image.format}, {image.size}, {image.mode}")
        
        decoded_objects = decode(image)
        print(f"Found {len(decoded_objects)} decoded objects")
        
        if decoded_objects:
            for i, obj in enumerate(decoded_objects):
                print(f"  ✅ QR {i+1}: {obj.data.decode('utf-8')}")
        else:
            print("❌ No QR codes detected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_qr_debug()
    test_with_known_qr() 