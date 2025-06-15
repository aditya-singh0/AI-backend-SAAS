#!/usr/bin/env python3

import sys
import subprocess

def main():
    year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    # Run the scraper with input
    process = subprocess.Popen(
        ['python3', 'captcha_helper_scraper.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Read output until we see the year prompt
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line, end='')
        
        # When we see the year prompt, send the year
        if "Enter year" in line:
            process.stdin.write(f"{year}\n")
            process.stdin.flush()
            print(f"Auto-entered year: {year}")
    
    # Wait for process to complete
    process.wait()

if __name__ == "__main__":
    main() 