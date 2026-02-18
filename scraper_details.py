import pandas as pd
import time
import os
import pickle
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

INPUT_FILE = 'input/redourls.xlsx'
OUTPUT_FILE = 'output/instagram_details.xlsx'

def setup_driver():
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    print("🔐 Loading session...")
    driver.get("https://www.instagram.com/")
    time.sleep(3)
    
    if os.path.exists("cookies.pkl"):
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
    return driver

def extract_details(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(4, 6))
        
        # Extract from Meta Tags
        try:
            meta_desc = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
            
            # Parse Description
            # Format: "224 likes, 5 comments - friesandvogue on August 3, 2025: \"Because some bonds...\""
            
            # 1. Date
            date_match = re.search(r'on\s+(.*?):\s+"', meta_desc)
            date_posted = date_match.group(1) if date_match else "Unknown"
            
            # 2. Caption
            caption_match = re.search(r':\s+"(.*)"', meta_desc, re.DOTALL)
            caption = caption_match.group(1) if caption_match else ""
            
            # 3. Hashtags
            hashtags = re.findall(r'#\w+', caption)
            
            return {
                'url': url,
                'date_posted': date_posted,
                'caption': caption,
                'hashtags': ", ".join(hashtags),
                'status': 'Success'
            }
            
        except Exception as e:
            print(f"  ❌ Meta extraction error: {e}")
            return {
                'url': url,
                'date_posted': '',
                'caption': '',
                'hashtags': '',
                'status': 'Error'
            }
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {
            'url': url,
            'date_posted': '',
            'caption': '',
            'hashtags': '',
            'status': 'Error'
        }

def main():
    print(f"🚀 Starting scraper for {INPUT_FILE}")
    
    try:
        df = pd.read_excel(INPUT_FILE)
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return

    driver = setup_driver()
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        data = extract_details(driver, url)
        results.append(data)
        
        if data['status'] == 'Success':
            print(f"  ✓ Date: {data['date_posted']} | Tags: {len(data['hashtags'].split(',')) if data['hashtags'] else 0}")
        
        # Save incrementally
        if i % 10 == 0:
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            print(f"  💾 Saved progress to {OUTPUT_FILE}")
            
    driver.quit()
    
    # Final Save
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Completed! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
