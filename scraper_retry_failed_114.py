"""
Instagram Scraper - RETRY FAILED 114
Retries specific URLs from retry_failed_114.csv with INCREASED SCROLLING
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
print("INSTAGRAM SCRAPER - RETRY FAILED 114")
print("="*60)

# Load Retry List
try:
    retry_df = pd.read_csv('retry_failed_114.csv')
    urls = retry_df['url'].tolist()
    print(f"✓ Loaded {len(urls)} URLs to retry")
except Exception as e:
    print(f"✗ Error loading retry list: {e}")
    exit()

if not urls:
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

results = []

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] Retrying: {url[:50]}...")
    
    result = {'url': url, 'views': 0, 'status': 'Failed'}
    
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # 1. Try standard extraction
        views = 0
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views', page_text, re.I)
        if not views_match: views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', page_text, re.I)
        if views_match: views = extract_number(views_match.group(1))
            
        if views > 0:
            print(f"  ✓ Found views on page: {views:,}")
            result['views'] = views
            result['status'] = 'Success'
            results.append(result)
            continue
            
        # 2. PROFILE LOOKUP STRATEGY
        print("  🕵️ Going to profile page for views...")
        username = ''
        
        # Strategy 1: Meta og:url
        try:
            meta_url = driver.find_element(By.XPATH, "//meta[@property='og:url']").get_attribute("content")
            if 'instagram.com/' in meta_url:
                parts = meta_url.split('instagram.com/')[-1].split('/')
                if len(parts) > 0: username = parts[0]
        except: pass
            
        # Strategy 2: Title Regex
        if not username:
            try:
                match = re.search(r'\(@([a-zA-Z0-9._]+)\)', driver.title)
                if match: username = match.group(1)
            except: pass

        # Strategy 3: Header link
        if not username:
            try:
                header_link = driver.find_element(By.XPATH, "//header//a[contains(@href, '/')]")
                username = header_link.get_attribute("href").strip('/').split('/')[-1]
            except: pass
                
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
                
                # INCREASED SCROLLING TO 50
                for scroll_idx in range(50):
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
                                result['views'] = views
                                result['status'] = 'Success'
                                found_reel = True
                                break
                        
                        driver.execute_script("window.scrollBy(0, 1000)")
                        time.sleep(1.5) # Increased sleep slightly
                        if scroll_idx % 10 == 0:
                            print(f"    ...scrolling ({scroll_idx}/50)")
                            
                    except: break
                if not found_reel: print("  ⚠ Could not find reel on profile (after 50 scrolls)")
            
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
    
    results.append(result)
    
    # Periodic Save
    if i % 5 == 0:
        pd.DataFrame(results).to_csv('retry_failed_114_results.csv', index=False)

driver.quit()

# Final Save
pd.DataFrame(results).to_csv('retry_failed_114_results.csv', index=False)
print("\n✅ Saved results to retry_failed_114_results.csv")
