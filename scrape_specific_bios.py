import pandas as pd
import time
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

USERNAMES = [
    "aashirvaad",
    "sunfeastwowzers",
    "rupankrita_kuki",
    "sfmomsmagic",
    "salonidaini_"
]

OUTPUT_FILE = "output/instagram_bios_specific_batch2.xlsx"

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

def scrape_specific():
    driver = setup_driver()
    results = []
    
    for username in USERNAMES:
        print(f"Processing: {username}")
        url = f"https://www.instagram.com/{username}/"
        bio = ''
        
        try:
            driver.get(url)
            time.sleep(5)
            
            # Extract Bio
            try:
                # Try to find the element that comes AFTER the stats ul
                # //header//ul/../following-sibling::div
                bio_elem = driver.find_element(By.XPATH, "//h1/../../following-sibling::div")
                bio = bio_elem.text
            except:
                # Fallback: just save full header text
                try:
                    bio = driver.find_element(By.TAG_NAME, "header").text
                except: pass
            
            print(f"  📖 Bio: {bio[:50]}...")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        results.append({
            'username': username,
            'url': url,
            'bio': bio
        })
        
    driver.quit()
    
    # Save
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Saved results to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_specific()
