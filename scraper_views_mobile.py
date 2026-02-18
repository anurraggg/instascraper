from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import re
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
INPUT_FILE = "output/instagram_auto.xlsx"
OUTPUT_FILE = "output/instagram_auto_views_mobile.xlsx"

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text:
        multiplier = 1000
        text = text.replace('K', '')
    elif 'M' in text:
        multiplier = 1000000
        text = text.replace('M', '')
    
    match = re.search(r'[\d.]+', text)
    if match:
        try:
            return int(float(match.group()) * multiplier)
        except: return 0
    return 0

def setup_driver():
    mobile_emulation = { "deviceName": "iPhone X" }
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument('--log-level=3')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login(driver):
    print("\n🔐 Logging in (Mobile Mode)...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(random.uniform(3, 5))
    
    try:
        # Accept cookies
        try:
            driver.find_element(By.XPATH, "//button[text()='Allow all cookies']").click()
            time.sleep(2)
        except: pass

        user_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        user_input.send_keys(USERNAME)
        time.sleep(1)
        
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.send_keys(PASSWORD)
        time.sleep(1)
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(random.uniform(5, 8))
        
        # Handle "Save Info"
        try:
            driver.find_element(By.XPATH, "//button[text()='Not Now']").click()
        except: pass
        
        print("✅ Login successful!")
        return True
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return False

def scrape_views_mobile():
    print("\n" + "="*60)
    print("INSTAGRAM VIEW SCRAPER - MOBILE EMULATION")
    print("="*60)
    
    try:
        df = pd.read_excel(INPUT_FILE)
        print(f"✓ Loaded {len(df)} rows")
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return

    driver = setup_driver()
    if not login(driver):
        driver.quit()
        return

    updated_count = 0
    
    for index, row in df.iterrows():
        url = row['url']
        current_views = row.get('views', 0)
        
        try:
            if int(float(current_views)) > 0:
                continue
        except: pass
            
        print(f"\n[{index+1}/{len(df)}] {url[:40]}...")
        
        try:
            driver.get(url)
            time.sleep(random.uniform(4, 6))
            
            views = 0
            
            # Strategy 1: Look for "Plays" text
            try:
                # On mobile, it often says "X plays" below the username or in the likes section
                body_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Regex for "10.5K plays"
                m = re.search(r'([\d,\.]+[KMB]?)\s*plays', body_text, re.I)
                if m:
                    views = extract_number(m.group(1))
                    print(f"  ✓ Found 'plays' text: {views:,}")
            except: pass
            
            # Strategy 2: Look for specific elements
            if views == 0:
                try:
                    # Sometimes it's just a number followed by "plays" in a span
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'plays')]")
                    for elem in elements:
                        txt = elem.text
                        m = re.search(r'([\d,\.]+[KMB]?)', txt)
                        if m:
                            views = extract_number(m.group(1))
                            print(f"  ✓ Found element with 'plays': {views:,}")
                            break
                except: pass

            if views > 0:
                df.at[index, 'views'] = views
                updated_count += 1
            else:
                print("  ⚠ Could not find views")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            
        time.sleep(random.uniform(2, 4))
        
        if updated_count > 0 and updated_count % 5 == 0:
            df.to_excel(OUTPUT_FILE, index=False)
            print("  💾 Saved progress")

    driver.quit()
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Updated {updated_count} rows. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_views_mobile()
