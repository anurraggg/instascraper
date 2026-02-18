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

# Configuration
INPUT_FILE = "input/redourls.xlsx"
OUTPUT_FILE = "output/instagram_profiles.xlsx"

def get_username_from_ytdlp(url):
    """Get username using yt-dlp (reliable)."""
    try:
        cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download", url]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Prefer channel (handle) over uploader (display name)
            return data.get('channel') or data.get('uploader')
    except: pass
    return None

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
            print("  ⚠️ No cookies.pkl found. Please run setup_session.py first.")
    except Exception as e:
        print(f"  ❌ Error loading cookies: {e}")
        
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

def main():
    print("="*60)
    print("INSTAGRAM PROFILE SCRAPER")
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

    driver = setup_driver()
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        username = ''
        post_count = 0
        bio = ''
        status = 'Failed'
        error = ''
        
        try:
            # 1. Get Username
            username = get_username_from_ytdlp(url)
            
            # Fallback: If no username from yt-dlp, we MUST visit the URL
            if not username or username == 'www.instagram.com' or username == 'instagram.com':
                print("  ⚠️ Could not determine username from yt-dlp. Visiting URL...")
                driver.get(url)
                time.sleep(5)
                
                # Strategy 1: Check Page Title
                # Title format: "Name (@username) on Instagram: ..."
                try:
                    title = driver.title
                    m = re.search(r'\(@([^\)]+)\)', title)
                    if m:
                        username = m.group(1)
                        print(f"  ✅ Found username from title: {username}")
                except: pass
                
                # Strategy 2: Check Meta Tags
                if not username:
                    try:
                        meta_title = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
                        m = re.search(r'\(@([^\)]+)\)', meta_title)
                        if m:
                            username = m.group(1)
                            print(f"  ✅ Found username from meta tag: {username}")
                    except: pass

                # Strategy 3: Link Search (with exclusion)
                if not username:
                    try:
                        links = driver.find_elements(By.XPATH, "//a")
                        for link in links:
                            href = link.get_attribute("href")
                            if href and 'instagram.com/' in href:
                                parts = href.strip('/').split('/')
                                if len(parts) >= 3:
                                    possible_user = parts[-1]
                                    # Exclude common pages and logged-in user
                                    if possible_user not in ['reels', 'explore', 'direct', 'home', os.environ.get('IG_USERNAME', '')] and len(possible_user) > 1:
                                        # Heuristic: Author link is usually early but AFTER nav
                                        # Let's try to be more specific: Author link usually contains the username text
                                        if link.text and link.text.strip() == possible_user:
                                            username = possible_user
                                            break
                    except: pass
                
            if not username or username == os.environ.get('IG_USERNAME', ''):
                print("  ❌ Could not find username (or found self).")
                error = "Username not found"
            else:
                print(f"  👤 Username: {username}")
                
                # 2. Visit Profile
                profile_url = f"https://www.instagram.com/{username}/"
                if driver.current_url != profile_url:
                    driver.get(profile_url)
                    time.sleep(5)
                
                # 3. Extract Post Count
                try:
                    # Look for "X posts" in header list
                    posts_elem = driver.find_element(By.XPATH, "//header//ul//li[1]")
                    post_text = posts_elem.text
                    post_count = extract_number(post_text)
                    print(f"  📝 Posts: {post_count} ({post_text})")
                except:
                    print("  ⚠️ Post count element not found")
                    
                # 4. Extract Bio & Fallback Post Count
                try:
                    header = driver.find_element(By.TAG_NAME, "header")
                    header_text = header.text
                    
                    # Fallback for post count if 0
                    if post_count == 0:
                        m = re.search(r'([\d,\.]+[KMB]?)\s*posts', header_text, re.I)
                        if m:
                            post_count = extract_number(m.group(1))
                            print(f"  📝 Posts (from header): {post_count}")
                    
                    # Try to find specific bio div
                    try:
                        # Bio is often in a div with class _aa_c or just text in the header
                        # Let's try to find the element that contains the text but isn't the stats
                        bio_elem = driver.find_element(By.XPATH, "//h1/../../following-sibling::div")
                        bio = bio_elem.text
                    except:
                        # Fallback: Use full header text but try to strip stats
                        bio = header_text
                        
                    print(f"  📖 Bio found: {bio[:50]}...")
                    
                except:
                    print("  ⚠️ Header not found")

                status = 'Success'

        except Exception as e:
            print(f"  ❌ Error: {e}")
            error = str(e)
            
        results.append({
            'url': url,
            'username': username,
            'post_count': post_count,
            'bio': bio,
            'status': status,
            'error': error
        })
        
        # Save every 5
        if i % 5 == 0:
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            print(f"  💾 Saved progress to {OUTPUT_FILE}")

    driver.quit()
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
