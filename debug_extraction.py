"""
Debug Extraction Script
Loads a URL and prints out potential data sources (Meta tags, JSON blobs).
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json
import time

def main():
    print("DEBUG EXTRACTION")
    url = input("Enter Instagram URL to debug: ").strip()
    if not url:
        url = "https://www.instagram.com/instagram/" # Default
        
    print(f"Loading {url}...")
    
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.instagram.com/")
        print("Please log in if needed, then press ENTER.")
        input()
        
        driver.get(url)
        time.sleep(5)
        
        page_source = driver.page_source
        
        print("\n--- META TAGS ---")
        try:
            og_title = re.search(r'<meta property="og:title" content="([^"]+)"', page_source)
            if og_title:
                print(f"og:title: {og_title.group(1)}")
                
            og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', page_source)
            if og_desc:
                print(f"og:description: {og_desc.group(1)}")
                
            desc = re.search(r'<meta name="description" content="([^"]+)"', page_source)
            if desc:
                print(f"description: {desc.group(1)}")
        except Exception as e:
            print(f"Error extracting meta: {e}")

        print("\n--- JSON DATA ---")
        # Look for sharedData
        shared_match = re.search(r'window\._sharedData\s*=\s*({.+?});', page_source)
        if shared_match:
            print("Found window._sharedData!")
            # print(shared_match.group(1)[:500] + "...")
        else:
            print("window._sharedData NOT found.")
            
        # Look for additionalData
        add_match = re.search(r'window\.__additionalData\s*=\s*({.+?});', page_source)
        if add_match:
            print("Found window.__additionalData!")
        else:
            print("window.__additionalData NOT found.")
            
        # Look for GraphQL
        graphql_match = re.search(r'window\.__graphql\s*=\s*({.+?});', page_source)
        if graphql_match:
            print("Found window.__graphql!")
        else:
            print("window.__graphql NOT found.")
            
        # Look for application/json scripts
        scripts = re.findall(r'<script type="application/json">(.+?)</script>', page_source)
        print(f"Found {len(scripts)} JSON scripts.")
        for i, s in enumerate(scripts):
            print(f"Script {i}: {s[:100]}...")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
