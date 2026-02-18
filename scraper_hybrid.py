import pandas as pd
import subprocess
import json
import time
import random
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
INPUT_FILE = "input/redourls.xlsx"
OUTPUT_FILE = "output/instagram_hybrid.xlsx"
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")

def get_ytdlp_metadata(url):
    """Get metadata using yt-dlp."""
    try:
        cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download", url]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return json.loads(result.stdout)
    except: pass
    return None

def extract_number(text):
    if not text: return 0
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    if 'K' in text: multiplier = 1000; text = text.replace('K', '')
    elif 'M' in text: multiplier = 1000000; text = text.replace('M', '')
    match = re.search(r'[\d.]+', text)
    if match: return int(float(match.group()) * multiplier)
    return 0

import pickle

def setup_driver():
    options = Options()
    options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=options)
    
    # Load Cookies
    print("🔐 Loading session...")
    driver.get("https://www.instagram.com/")
    time.sleep(3)
    
    try:
        if os.path.exists("cookies.pkl"):
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            print("  ✅ Cookies loaded.")
            driver.refresh()
            time.sleep(5)
        else:
            print("  ⚠️ No cookies.pkl found. Logging in manually...")
            try:
                driver.find_element(By.NAME, "username").send_keys(USERNAME)
                driver.find_element(By.NAME, "password").send_keys(PASSWORD)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(10)
            except: pass
            
    except Exception as e:
        print(f"  ❌ Error loading cookies: {e}")
        
    return driver

def main():
    print("="*60)
    print("INSTAGRAM HYBRID SCRAPER")
    print("="*60)
    
    # Load URLs
    try:
        df = pd.read_excel(INPUT_FILE)
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return

    results = []
    driver = None
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        views = 0
        likes = 0
        comments = 0
        username = ''
        status = 'Failed'
        error = ''
        
        # 1. Try yt-dlp
        meta = get_ytdlp_metadata(url)
        if meta:
            # Prefer 'channel' (handle) over 'uploader' (display name)
            username = meta.get('channel', '')
            if not username:
                username = meta.get('uploader', '')
            
            # MANUAL OVERRIDE for specific URLs
            if "DM5F3Vzq6TN" in url:
                username = "friesandvogue"
                print(f"  ℹ️ Applied Manual Override: {username}")
                
            views = meta.get('view_count', 0)
            likes = meta.get('like_count', 0)
            comments = meta.get('comment_count', 0)
            print(f"  ✓ yt-dlp: User={username} | Views={views} | Likes={likes}")
            
        # 2. If views missing, try Direct Navigation (Desktop)
        if views == 0:
            print("  ⚠️ Views missing. Trying Direct Navigation...")
            if not driver: driver = setup_driver()
            
            try:
                driver.get(url)
                time.sleep(5)
                
                # Check for "10.5K plays" or "views" in text
                try:
                    # Look for "plays" text
                    # Often in "Liked by X and Y others" section or "X plays"
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    m = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', page_text, re.I)
                    if m:
                        views = extract_number(m.group(1))
                        print(f"  ✅ Found Views (Direct - Text): {views}")
                except: pass
                
                # Check metadata
                if views == 0:
                    try:
                        meta = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
                        # "224 likes, 5 comments - username..."
                        # Sometimes views are here? No, usually likes/comments.
                        pass
                    except: pass
                    
                # Check Aria Labels
                if views == 0:
                    try:
                        labels = driver.find_elements(By.XPATH, "//*[@aria-label]")
                        for elem in labels:
                            lbl = elem.get_attribute("aria-label")
                            if lbl and 'play' in lbl.lower():
                                m = re.search(r'(\d[\d,\.]*[KMB]?)', lbl)
                                if m:
                                    views = extract_number(m.group(1))
                                    print(f"  ✅ Found Views (Direct - Aria): {views}")
                                    break
                    except: pass
                    
            except Exception as e:
                print(f"  ❌ Direct Nav Error: {e}")

        # 3. If still missing, use Selenium Profile Lookup
        if views == 0 and username:
            print("  ⚠️ Views still missing. Using Selenium Profile Lookup...")
            
            try:
                driver.get(f"https://www.instagram.com/{username}/reels/")
                time.sleep(5)
                
                shortcode = ''
                if '/reel/' in url:
                    shortcode = url.split('/reel/')[-1].split('/')[0]
                elif '/p/' in url:
                    shortcode = url.split('/p/')[-1].split('/')[0]
                
                if not shortcode:
                    print(f"  ❌ Could not extract shortcode from {url}")
                    continue
                
                print(f"  🔍 Looking for shortcode: {shortcode}")
                
                found = False
                for scroll_i in range(500): # Scroll up to 500 times
                    try:
                        links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                        if links:
                            link = links[0]
                            # Try Text
                            m = re.search(r'([\d,\.]+[KMB]?)', link.text)
                            if m: 
                                views = extract_number(m.group(1))
                                print(f"  ✅ Found Views (Text): {views}")
                                found = True
                                break
                                
                            # Try HTML
                            html = link.get_attribute("innerHTML")
                            m = re.search(r'>\s*([\d,\.]+[KMB]?)\s*<', html)
                            if m:
                                views = extract_number(m.group(1))
                                print(f"  ✅ Found Views (HTML): {views}")
                                found = True
                                break
                    except: pass
                    
                    driver.execute_script("window.scrollBy(0, 1000)")
                    time.sleep(1.0) # Slightly faster scroll
                    if scroll_i % 20 == 0:
                        print(f"  ...scrolling ({scroll_i}/500)")
                    
                if not found:
                    print("  ⚠️ Reel not found in Reels tab. Checking Main Profile...")
                    driver.get(f"https://www.instagram.com/{username}/")
                    time.sleep(5)
                    
                    for scroll_i in range(500):
                        try:
                            links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                            if links:
                                link = links[0]
                                m = re.search(r'([\d,\.]+[KMB]?)', link.text)
                                if m: 
                                    views = extract_number(m.group(1))
                                    print(f"  ✅ Found Views (Main - Text): {views}")
                                    found = True
                                    break
                        except: pass
                        driver.execute_script("window.scrollBy(0, 1000)")
                        time.sleep(1.0)
                        if scroll_i % 20 == 0:
                            print(f"  ...scrolling main ({scroll_i}/500)")

                if not found:
                    print("  ❌ Reel not found in grid")
                    error = "Reel not found in grid"
                    driver.save_screenshot(f"debug_{shortcode}.png")
                    
            except Exception as e:
                print(f"  ❌ Selenium Error: {e}")
                error = str(e)
                # Restart driver if crashed
                if "no such window" in str(e):
                    driver.quit()
                    driver = None
        
        if views > 0 or likes > 0:
            status = 'Success'
            
        results.append({
            'url': url,
            'username': username,
            'views': views,
            'likes': likes,
            'comments': comments,
            'status': status,
            'error': error
        })
        
        # Save every 5
        if i % 5 == 0:
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            print(f"  💾 Saved progress to {OUTPUT_FILE}")

    if driver:
        driver.quit()
        
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
