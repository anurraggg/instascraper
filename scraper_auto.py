"""
Instagram Scraper - Automated & Robust
Features:
1. Automated Login (reads IG_USERNAME / IG_PASSWORD from environment)
2. Robust Extraction (Meta Tags + Aria Labels)
3. Resume Capability
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import random
import os
from pathlib import Path

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
INPUT_FILE = "input/redourls.xlsx"
OUTPUT_FILE = "output/instagram_auto.xlsx"

def extract_number(text):
    """Extract number from text (e.g. '1.2M' -> 1200000)."""
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

def login(driver):
    print("\n🔐 Logging in as", USERNAME, "...")
    driver.get("https://www.instagram.com/")
    time.sleep(random.uniform(3, 5))
    
    try:
        # Check if already logged in
        if "login" not in driver.current_url and driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
            print("  ✅ Already logged in!")
            return True

        # Accept cookies if present
        try:
            driver.find_element(By.XPATH, "//button[text()='Allow all cookies']").click()
            time.sleep(2)
        except:
            pass

        # Enter Username
        user_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user_input.clear()
        user_input.send_keys(USERNAME)
        time.sleep(random.uniform(1, 2))
        
        # Enter Password
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        time.sleep(random.uniform(1, 2))
        
        # Click Login
        pass_input.send_keys(Keys.RETURN)
        time.sleep(random.uniform(5, 8))
        
        # Check for "Save Info" or "Not Now" (means success)
        if driver.find_elements(By.XPATH, "//div[text()='Not now']") or \
           driver.find_elements(By.XPATH, "//button[text()='Save Info']") or \
           driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
            print("  ✅ Login successful!")
            return True
            
        # Check for 2FA or Challenge
        if "challenge" in driver.current_url:
            print("  ⚠️ Security Challenge detected!")
            print("  👉 Please solve the challenge in the browser window.")
            print("  👉 Press ENTER here when done...")
            input()
            return True
            
        print("  ⚠️ Login verification needed. Please check browser.")
        time.sleep(5)
        return True
        
    except Exception as e:
        print(f"  ✗ Login failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - AUTOMATED")
    print("="*60)

    # Load URLs
    try:
        df = pd.read_excel(INPUT_FILE)
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"\n✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return

    # Setup Chrome
    print("\n🚀 Starting Chrome...")
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    # Login
    if not login(driver):
        print("🛑 Login failed. Exiting.")
        driver.quit()
        return

    print("\n✅ Starting scraping...")
    
    results = []
    Path('output').mkdir(exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url[:60]}...")
        
        username = ''
        followers = 0
        following = 0
        likes = 0
        comments = 0
        views = 0
        status = 'Init'
        error_msg = ''
        
        try:
            driver.get(url)
            time.sleep(random.uniform(5, 7))
            
            # Check for Page Unavailable
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "Sorry, this page isn't available" in page_text:
                print("  ⚠️ Page unavailable")
                status = 'Unavailable'
            else:
                # 0. Scroll to trigger lazy loading (helps with Views)
                driver.execute_script("window.scrollTo(0, 300);")
                time.sleep(2)

                # 1. Get Username
                try:
                    title = driver.title
                    if '(@' in title and ')' in title:
                        username = title.split('(@')[1].split(')')[0]
                    elif 'on Instagram' in title:
                        username = title.split('on Instagram')[0].strip().replace('"', '').split(' ')[0]
                    
                    # Fallback: Meta Title
                    if not username:
                        try:
                            meta_title = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
                            if '(@' in meta_title:
                                username = meta_title.split('(@')[1].split(')')[0]
                        except: pass
                    
                    # Fallback: OG URL (Very Reliable)
                    if not username:
                        try:
                            og_url = driver.find_element(By.XPATH, "//meta[@property='og:url']").get_attribute("content")
                            # https://www.instagram.com/username/reel/ID/
                            if 'instagram.com/' in og_url:
                                parts = og_url.split('instagram.com/')[1].split('/')
                                if parts[0] in ['p', 'reel', 'tv']:
                                    pass # URL format is /p/ID/, username not here usually
                                else:
                                    username = parts[0]
                        except: pass

                    # Fallback: Meta Description
                    if not username:
                        try:
                            meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
                            # "224 likes, 5 comments - username on..."
                            match = re.search(r'-\s+([^\s]+)\s+on', meta_desc)
                            if match:
                                username = match.group(1)
                        except: pass
                        
                    print(f"  👤 Username: {username}")
                except:
                    pass
                
                # 2. Get Stats from Meta Description (Most Reliable for Likes/Comments)
                try:
                    meta_desc = ""
                    try:
                        meta_desc = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
                    except:
                        try:
                            meta_desc = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
                        except: pass
                    
                    if meta_desc:
                        # Format: "224 likes, 5 comments - username..."
                        l_match = re.search(r'([\d,\.]+[KMB]?)\s+likes?', meta_desc, re.I)
                        if l_match: likes = extract_number(l_match.group(1))
                        
                        c_match = re.search(r'([\d,\.]+[KMB]?)\s+comments?', meta_desc, re.I)
                        if c_match: comments = extract_number(c_match.group(1))
                except:
                    pass

                # 3. Get Post Stats (Aria Labels - Backup & Views)
                try:
                    aria_elements = driver.find_elements(By.XPATH, "//*[@aria-label]")
                    for elem in aria_elements:
                        label = elem.get_attribute("aria-label")
                        if not label: continue
                        
                        if likes == 0:
                            m = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes?', label, re.I)
                            if m: likes = extract_number(m.group(1))
                        
                        if comments == 0:
                            m = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments?', label, re.I)
                            if m: comments = extract_number(m.group(1))
                            
                        if views == 0:
                            m = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:views?|plays?)', label, re.I)
                            if m: views = extract_number(m.group(1))
                except:
                    pass
                
                # 4. Fallback Post Stats (Text)
                if likes == 0:
                    m = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes?', page_text, re.I)
                    if m: likes = extract_number(m.group(1))
                
                if comments == 0:
                    m = re.search(r'(?:View all\s+)?(\d[\d,\.]*[KMB]?)\s*comments?', page_text, re.I)
                    if m: comments = extract_number(m.group(1))
                    
                if views == 0:
                    m = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:views?|plays?)', page_text, re.I)
                    if m: views = extract_number(m.group(1))
                
                # 5. Get Profile Stats
                if username:
                    try:
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(f"https://www.instagram.com/{username}/")
                        time.sleep(random.uniform(3, 5))
                        
                        # Meta Description
                        try:
                            meta = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
                            if meta:
                                m = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta, re.I)
                                if m: followers = extract_number(m.group(1))
                                m = re.search(r'([\d,\.]+[KMB]?)\s+Following', meta, re.I)
                                if m: following = extract_number(m.group(1))
                        except:
                            pass
                            
                        # Fallback Text
                        if followers == 0:
                            p_text = driver.find_element(By.TAG_NAME, "body").text
                            m = re.search(r'([\d,\.]+[KMB]?)\s+followers', p_text, re.I)
                            if m: followers = extract_number(m.group(1))
                            m = re.search(r'([\d,\.]+[KMB]?)\s+following', p_text, re.I)
                            if m: following = extract_number(m.group(1))
                            
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        print(f"  ✓ Profile: {followers:,} Followers | {following:,} Following")
                    except:
                        try:
                            if len(driver.window_handles) > 1:
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                        except: pass

                print(f"  ✓ Post: {likes:,} Likes | {comments:,} Comments | {views:,} Views")
                status = 'Success'
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            status = 'Error'
            error_msg = str(e)
            if "no such window" in str(e):
                break

        results.append({
            'url': url,
            'username': username,
            'followers': followers,
            'following': following,
            'likes': likes,
            'comments': comments,
            'views': views,
            'status': status,
            'error': error_msg
        })
        
        # Save every 5
        if i % 5 == 0:
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            print("  💾 Saved progress")
            
        time.sleep(random.uniform(2, 4))

    driver.quit()
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
