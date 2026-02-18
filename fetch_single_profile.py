import pandas as pd
import time
import re
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

INPUT_FILE = "output/instagram_profiles.xlsx"
TARGET_USERNAME = "euphoria_covers"
TARGET_INDEX = 26

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

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text: multiplier = 1000; text = text.replace('K', '')
    elif 'M' in text: multiplier = 1000000; text = text.replace('M', '')
    match = re.search(r'[\d.]+', text)
    if match: return int(float(match.group()) * multiplier)
    return 0

def fetch_single():
    print(f"Fetching details for {TARGET_USERNAME}...")
    driver = setup_driver()
    
    try:
        driver.get(f"https://www.instagram.com/{TARGET_USERNAME}/")
        time.sleep(5)
        
        post_count = 0
        bio = ''
        
        # Extract Post Count
        try:
            header_text = driver.find_element(By.TAG_NAME, "header").text
            m = re.search(r'([\d,\.]+[KMB]?)\s*posts', header_text, re.I)
            if m:
                post_count = extract_number(m.group(1))
                print(f"  📝 Posts: {post_count}")
        except: pass
        
        # Extract Bio
        try:
            bio = driver.find_element(By.TAG_NAME, "header").text
        except: pass
        
        # Update Excel
        df = pd.read_excel(INPUT_FILE)
        df.at[TARGET_INDEX, 'post_count'] = post_count
        df.at[TARGET_INDEX, 'bio'] = bio
        df.at[TARGET_INDEX, 'error'] = 'Manual Fix'
        df.to_excel(INPUT_FILE, index=False)
        print("✅ Updated Excel.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_single()
