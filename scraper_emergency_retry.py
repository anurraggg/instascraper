"""
Instagram Scraper - EMERGENCY RETRY (First 200)
Retries the first 200 URLs which were reported as broken/0 views.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import random
from pathlib import Path

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text: multiplier = 1000; text = text.replace('K', '')
    elif 'M' in text: multiplier = 1000000; text = text.replace('M', '')
    elif 'B' in text: multiplier = 1000000000; text = text.replace('B', '')
    match = re.search(r'[\d.]+', text)
    if match:
        try: return int(float(match.group()) * multiplier)
        except: return 0
    return 0

print("\n" + "="*60)
print("INSTAGRAM SCRAPER - EMERGENCY RETRY (First 200)")
print("="*60)

# Load Final File
try:
    file_path = 'final_output/Instagram_Final_Complete.xlsx'
    df = pd.read_excel(file_path, sheet_name='Posts_Reels')
    
    # Filter first 200 AND 0 views
    subset = df.head(200)
    retry_indices = subset[subset['views'] == 0].index.tolist()
    
    print(f"✓ Found {len(retry_indices)} URLs in first 200 with 0 views")
except Exception as e:
    print(f"✗ Error loading file: {e}")
    exit()

if not retry_indices:
    print("No URLs to retry!")
    exit()

# Setup Chrome
print("\n🚀 Starting Chrome...")
options = Options()
options.add_argument('--log-level=3')
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# Login
print("\n🔐 Please log in to Instagram manually in the browser...")
driver.get("https://www.instagram.com/")
print("👉 Log in to Instagram in the browser window")
print("👉 After logging in, press ENTER here to continue...")
input()

print("\n✅ Starting retry...")

for i, idx in enumerate(retry_indices, 1):
    url = df.loc[idx, 'url']
    print(f"[{i}/{len(retry_indices)}] Retrying: {url[:50]}...")
    
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Check for Rate Limit / Login Wall
        if "Wait a few minutes" in page_text or "Log in" in driver.title:
            print("  🛑 RATE LIMIT DETECTED or LOGGED OUT!")
            print("  👉 Please resolve in browser (wait or log in).")
            print("  👉 Press ENTER here when ready to continue...")
            input()
            driver.refresh()
            time.sleep(5)
            page_text = driver.find_element(By.TAG_NAME, "body").text

        # 1. Try standard extraction
        views = 0
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views', page_text, re.I)
        if not views_match: views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', page_text, re.I)
        if views_match: views = extract_number(views_match.group(1))
            
        if views > 0:
            print(f"  ✓ Found views on page: {views:,}")
            df.loc[idx, 'views'] = views
            df.loc[idx, 'status'] = 'Success'
            continue
            
        # 2. PROFILE LOOKUP STRATEGY
        print("  🕵️ Going to profile page for views...")
        username = ''
        
        try:
            meta_url = driver.find_element(By.XPATH, "//meta[@property='og:url']").get_attribute("content")
            if 'instagram.com/' in meta_url:
                parts = meta_url.split('instagram.com/')[-1].split('/')
                if len(parts) > 0: username = parts[0]
        except: pass
            
        if not username:
            try:
                match = re.search(r'\(@([a-zA-Z0-9._]+)\)', driver.title)
                if match: username = match.group(1)
            except: pass

        if not username:
            try:
                header_link = driver.find_element(By.XPATH, "//header//a[contains(@href, '/')]")
                username = header_link.get_attribute("href").strip('/').split('/')[-1]
            except: pass
                
        if not username:
            print("  ⚠ Could not find username. Saving debug page...")
            with open(f"debug_failed_user_{i}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        
        if username:
            print(f"  👤 Username: {username}")
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(f"https://www.instagram.com/{username}/reels/")
            time.sleep(5)
            
            shortcode = ''
            if '/reel/' in url: shortcode = url.split('/reel/')[-1].split('/')[0].split('?')[0]
            elif '/p/' in url: shortcode = url.split('/p/')[-1].split('/')[0].split('?')[0]
            
            if shortcode:
                print(f"  🔍 Looking for shortcode: {shortcode}")
                found_reel = False
                for _ in range(100): # Increased from 20 to 100 as requested
                    try:
                        reel_link = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                        if reel_link:
                            container = reel_link[0]
                            container_text = container.text
                            inner_html = container.get_attribute("innerHTML")
                            view_match = re.search(r'(\d[\d,\.]*[KMB]?)', container_text)
                            if not view_match: view_match = re.search(r'>\s*(\d[\d,\.]*[KMB]?)\s*<', inner_html)
                            if view_match:
                                views = extract_number(view_match.group(1))
                                print(f"  ✓ Found views on profile: {views:,}")
                                df.loc[idx, 'views'] = views
                                df.loc[idx, 'status'] = 'Success'
                                found_reel = True
                                break
                        driver.execute_script("window.scrollBy(0, 1000)")
                        time.sleep(1)
                    except: break
                if not found_reel: print("  ⚠ Could not find reel on profile")
            
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            print("  ⚠ Could not find username")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except: pass
    
    # Periodic Save
    if i % 10 == 0:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Posts_Reels', index=False)
            # We need to preserve Profiles sheet, so load it and write it back
            try:
                p_df = pd.read_excel('final_output/Instagram_Data_Compiled.xlsx', sheet_name='Profiles')
                p_df.to_excel(writer, sheet_name='Profiles', index=False)
            except: pass

driver.quit()

# Final Save
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Posts_Reels', index=False)
    try:
        p_df = pd.read_excel('final_output/Instagram_Data_Compiled.xlsx', sheet_name='Profiles')
        p_df.to_excel(writer, sheet_name='Profiles', index=False)
    except: pass
    
print(f"\n✅ Updated {file_path}")
