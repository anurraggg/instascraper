import pandas as pd
import time
import re
import os
import pickle
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

INPUT_FILE = "output/instagram_profiles.xlsx"

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

def retry_failed():
    print("Loading existing results...")
    df = pd.read_excel(INPUT_FILE)
    
    # Identify failed rows (empty username)
    failed_indices = df[df['username'].isna()].index.tolist()
    print(f"Found {len(failed_indices)} failed rows to retry.")
    
    if not failed_indices:
        print("No failed rows found!")
        return

    driver = setup_driver()
    
    for idx in failed_indices:
        url = df.at[idx, 'url']
        print(f"\nRetrying [{idx}]: {url}")
        
        username = ''
        post_count = 0
        bio = ''
        
        try:
            driver.get(url)
            time.sleep(8) # Increased wait
            
            # 1. Try Title
            try:
                title = driver.title
                print(f"  Title: {title}")
                m = re.search(r'\(@([^\)]+)\)', title)
                if m:
                    username = m.group(1)
                    print(f"  ✅ Found username from title: {username}")
            except: pass
            
            # 2. Try Meta
            if not username:
                try:
                    meta = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
                    m = re.search(r'\(@([^\)]+)\)', meta)
                    if m:
                        username = m.group(1)
                        print(f"  ✅ Found username from meta: {username}")
                except: pass
                
            # 3. Try Link Search
            if not username:
                try:
                    links = driver.find_elements(By.XPATH, "//a")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and 'instagram.com/' in href:
                            parts = href.strip('/').split('/')
                            if len(parts) >= 3:
                                possible = parts[-1]
                                if possible not in ['reels', 'explore', 'direct', 'home', os.environ.get('IG_USERNAME', '')] and len(possible) > 1:
                                    if link.text and link.text.strip() == possible:
                                        username = possible
                                        print(f"  ✅ Found username from link: {username}")
                                        break
                except: pass

            if username:
                # Visit Profile
                profile_url = f"https://www.instagram.com/{username}/"
                if driver.current_url != profile_url:
                    driver.get(profile_url)
                    time.sleep(5)
                
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
                
                # Update DataFrame
                df.at[idx, 'username'] = username
                df.at[idx, 'post_count'] = post_count
                df.at[idx, 'bio'] = bio
                df.at[idx, 'error'] = 'Recovered'
                
            else:
                print("  ❌ Still could not find username.")
                df.at[idx, 'error'] = 'Retry Failed'

        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        # Save incrementally
        df.to_excel(INPUT_FILE, index=False)

    driver.quit()
    print("\nRetry complete.")

if __name__ == "__main__":
    retry_failed()
