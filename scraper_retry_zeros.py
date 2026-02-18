"""
Instagram Scraper - RETRY ZERO VIEWS
Retries URLs with 0 views using Profile Lookup strategy
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
    """Extract number from text."""
    if not text:
        return 0
    
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    
    if 'K' in text:
        multiplier = 1000
        text = text.replace('K', '')
    elif 'M' in text:
        multiplier = 1000000
        text = text.replace('M', '')
    elif 'B' in text:
        multiplier = 1000000000
        text = text.replace('B', '')
    
    match = re.search(r'[\d.]+', text)
    if match:
        try:
            return int(float(match.group()) * multiplier)
        except:
            return 0
    return 0

print("\n" + "="*60)
print("INSTAGRAM SCRAPER - RETRY ZERO VIEWS")
print("="*60)

# Load existing results
try:
    df = pd.read_excel('output/instagram_data_new.xlsx')
    print(f"✓ Loaded existing data: {len(df)} rows")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit()

# Filter for 0 views AND post URLs
# We assume if it has /p/ or /reel/ or /tv/ it is a post
post_mask = df['url'].str.contains('/p/|/reel/|/tv/', regex=True)
zero_views_mask = (df['views'] == 0)
retry_indices = df[post_mask & zero_views_mask].index.tolist()

print(f"✓ Found {len(retry_indices)} URLs with 0 views to retry")

if len(retry_indices) == 0:
    print("No URLs to retry!")
    exit()

# Setup Chrome
print("\n🚀 Starting Chrome...")
options = Options()
options.add_argument('--log-level=3')
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=options)
driver.maximize_window()
print("✅ Chrome ready")

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
        
        # 1. Try standard extraction first (just in case)
        views = 0
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views', page_text, re.I)
        if not views_match:
            views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', page_text, re.I)
        if views_match:
            views = extract_number(views_match.group(1))
            
        if views > 0:
            print(f"  ✓ Found views on page: {views:,}")
            df.loc[idx, 'views'] = views
            df.loc[idx, 'status'] = 'Success'
            continue
            
        # 2. PROFILE LOOKUP STRATEGY
        print("  🕵️ Going to profile page for views...")
        
        # Extract username
        username = ''
        
        # Strategy 1: Meta og:url (Most reliable)
        try:
            meta_url = driver.find_element(By.XPATH, "//meta[@property='og:url']").get_attribute("content")
            # Format: https://www.instagram.com/username/reel/ID/
            if 'instagram.com/' in meta_url:
                parts = meta_url.split('instagram.com/')[-1].split('/')
                if len(parts) > 0:
                    username = parts[0]
                    print(f"  ✓ Found username (meta): {username}")
        except:
            pass
            
        # Strategy 2: Page Title Regex (@username)
        if not username:
            try:
                title = driver.title
                # Format: "Name (@username) • Instagram reel"
                match = re.search(r'\(@([a-zA-Z0-9._]+)\)', title)
                if match:
                    username = match.group(1)
                    print(f"  ✓ Found username (title): {username}")
            except:
                pass

        # Strategy 3: Header link (Fallback)
        if not username:
            try:
                header_link = driver.find_element(By.XPATH, "//header//a[contains(@href, '/')]")
                username = header_link.get_attribute("href").strip('/').split('/')[-1]
                print(f"  ✓ Found username (header): {username}")
            except:
                pass
                
        # Strategy 4: Regex from body text (Last resort)
        if not username:
            user_match = re.search(r'([a-zA-Z0-9._]+)\s*\n\s*•\s*\n\s*Follow', page_text)
            if user_match:
                username = user_match.group(1)
                print(f"  ✓ Found username (text): {username}")

        if username:
            print(f"  👤 Username: {username}")
            
            # Open new tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            
            # Go to Reels tab
            driver.get(f"https://www.instagram.com/{username}/reels/")
            time.sleep(5)
            
            # Extract shortcode
            shortcode = ''
            if '/reel/' in url:
                shortcode = url.split('/reel/')[-1].split('/')[0].split('?')[0]
            elif '/p/' in url:
                shortcode = url.split('/p/')[-1].split('/')[0].split('?')[0]
            
            if shortcode:
                print(f"  🔍 Looking for shortcode: {shortcode}")
                found_reel = False
                
                # Scroll and Search
                for _ in range(20): # Scroll up to 20 times
                    try:
                        # Look for the link containing the shortcode
                        reel_link = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                        
                        if reel_link:
                            container = reel_link[0]
                            container_text = container.text
                            inner_html = container.get_attribute("innerHTML")
                            
                            # Extract number
                            view_match = re.search(r'(\d[\d,\.]*[KMB]?)', container_text)
                            if not view_match:
                                    view_match = re.search(r'>\s*(\d[\d,\.]*[KMB]?)\s*<', inner_html)
                                    
                            if view_match:
                                views = extract_number(view_match.group(1))
                                print(f"  ✓ Found views on profile: {views:,}")
                                df.loc[idx, 'views'] = views
                                df.loc[idx, 'status'] = 'Success'
                                found_reel = True
                                break
                        
                        driver.execute_script("window.scrollBy(0, 1000)")
                        time.sleep(1)
                    except:
                        break
                
                if not found_reel:
                    print("  ⚠ Could not find reel on profile")
            
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
        except:
            pass
            
    # Periodic Save
    if i % 5 == 0:
        df.to_excel('output/instagram_data_new_v3.xlsx', index=False, engine='openpyxl')

driver.quit()

# Final Save
df.to_excel('output/instagram_data_new_v3.xlsx', index=False, engine='openpyxl')
print(f"\n✅ Updated results saved to: output/instagram_data_new_v3.xlsx")

# Summary
print("\n" + "="*60)
print("RETRY SUMMARY")
print("="*60)
fixed_count = len(df[(df['views'] > 0) & (df.index.isin(retry_indices))])
print(f"Total Retried: {len(retry_indices)}")
print(f"Fixed: {fixed_count}")
print(f"Remaining 0: {len(retry_indices) - fixed_count}")
print("="*60)
