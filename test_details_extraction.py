import pandas as pd
import time
import os
import pickle
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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
    print(f"Testing URL: {url}")
    try:
        driver.get(url)
        time.sleep(5)
        
        # Extract from Meta Tags
        try:
            meta_desc = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
            print(f"  📄 Meta Description: {meta_desc}")
            
            # Parse Description
            # Format: "224 likes, 5 comments - friesandvogue on August 3, 2025: \"Because some bonds...\""
            
            # 1. Date
            date_match = re.search(r'on\s+(.*?):\s+"', meta_desc)
            date_posted = date_match.group(1) if date_match else "Unknown"
            print(f"  📅 Date: {date_posted}")
            
            # 2. Caption
            caption_match = re.search(r':\s+"(.*)"', meta_desc, re.DOTALL)
            caption = caption_match.group(1) if caption_match else ""
            print(f"  📝 Caption: {caption[:100]}...")
            
            # 3. Hashtags
            hashtags = re.findall(r'#\w+', caption)
            print(f"  🏷 Tags: {hashtags}")
            
            return {
                'url': url,
                'date': date_posted,
                'caption': caption,
                'hashtags': ", ".join(hashtags)
            }
            
        except Exception as e:
            print(f"  ❌ Meta extraction error: {e}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def test_extraction():
    # Load first 3 URLs
    df = pd.read_excel('input/redourls.xlsx')
    urls = df['URL'].head(3).tolist()
    
    driver = setup_driver()
    
    for url in urls:
        extract_details(driver, url)
        print("-" * 50)
        
    driver.quit()

if __name__ == "__main__":
    test_extraction()
