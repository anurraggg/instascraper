"""
Instagram Scraper - Stealth Mode
Uses advanced Chrome options to hide automation and bypass "Reel unavailable" errors.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import random
import os
import shutil
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

def main():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - STEALTH MODE")
    print("Bypassing detection with custom headers & options")
    print("="*60)

    # Load URLs
    try:
        df = pd.read_csv('input/Instagram_URLS.csv')
        urls = df.iloc[:, 0].dropna().tolist()[1:]
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"\n✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return

    # CLEAN SESSION (Optional: Remove old profile to force fresh login)
    # user_data_dir = os.path.join(os.getcwd(), "chrome_profile_stealth")
    # if os.path.exists(user_data_dir):
    #     try:
    #         shutil.rmtree(user_data_dir)
    #         print("✓ Cleared previous session data")
    #     except:
    #         pass

    # Setup Chrome with STEALTH options
    print("\n🚀 Starting Chrome (Stealth)...")
    options = Options()
    options.add_argument('--log-level=3')
    
    # 1. Disable Automation Flags
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 2. Real User Agent (Windows 10 / Chrome 120)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 3. Standard Stability
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    
    driver = webdriver.Chrome(options=options)
    
    # 4. Execute CDP command to prevent navigator.webdriver detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    # Login
    print("\n🔐 Please log in to Instagram manually in the browser...")
    driver.get("https://www.instagram.com/")
    print("👉 Log in to Instagram in the browser window")
    print("👉 After logging in, press ENTER here to continue...")
    input()
    
    print("\n✅ Starting scraping...")
    
    results = []
    Path('output').mkdir(exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        username = ''
        followers = 0
        following = 0
        status = 'Init'
        error_msg = ''
        
        try:
            driver.get(url)
            time.sleep(random.uniform(5, 8)) # Slower wait for stealth
            
            # Check for "Restricted" or "Unavailable"
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "Sorry, this page isn't available" in page_text or "Restricted profile" in page_text:
                print("  ⚠️ Page unavailable (Soft Ban or Invalid URL)")
                status = 'Unavailable'
            else:
                # Try to find username link (Click Flow Logic)
                clicked = False
                try:
                    # Look for username in header
                    header_username_elem = driver.find_element(By.XPATH, "//header//a[not(contains(@href, 'explore')) and string-length(text()) > 0]")
                    username = header_username_elem.text
                    print(f"  🎯 Found Username: {username}")
                    
                    header_username_elem.click()
                    clicked = True
                    print("  🖱️ Clicked username!")
                    time.sleep(random.uniform(4, 6))
                    
                except Exception as e:
                    # Fallback: Metadata extraction
                    try:
                        meta_title = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
                        match = re.search(r'\(@([a-zA-Z0-9._]+)\)', meta_title)
                        if match:
                            username = match.group(1)
                            print(f"  👤 Extracted Username (Meta): {username}")
                            driver.get(f"https://www.instagram.com/{username}/")
                            time.sleep(random.uniform(4, 6))
                            clicked = True
                    except:
                        pass

                # Strategy 3: Extract from Page Title (Reliable for Reels)
                if not username:
                    try:
                        page_title = driver.title
                        print(f"  📄 Page Title: {page_title}")
                        if ' on Instagram:' in page_title:
                            # Format: "Username on Instagram: 'Caption'"
                            username = page_title.split(' on Instagram:')[0].strip()
                            print(f"  👤 Extracted Username (Title): {username}")
                            driver.get(f"https://www.instagram.com/{username}/")
                            time.sleep(random.uniform(4, 6))
                            clicked = True
                    except Exception as e:
                        print(f"  ⚠️ Error extracting from title: {e}")

                # Ensure we are on the profile page
                is_profile = True
                if '/p/' in driver.current_url or '/reel/' in driver.current_url:
                    is_profile = False
                
                if clicked or is_profile:
                    # Extract Data
                    try:
                        meta_desc = ''
                        try:
                            meta_elem = driver.find_element(By.XPATH, "//meta[@property='og:description']")
                            meta_desc = meta_elem.get_attribute("content")
                        except:
                            pass
                        
                        if meta_desc:
                            print(f"  🔍 Meta Description Found: '{meta_desc}'")
                            f_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta_desc, re.I)
                            if f_match:
                                print(f"  ✓ Regex Match (Followers): {f_match.group(1)}")
                                followers = extract_number(f_match.group(1))
                            else:
                                print("  ⚠️ No 'Followers' pattern found in Meta Description")

                            fol_match = re.search(r'([\d,\.]+[KMB]?)\s+Following', meta_desc, re.I)
                            if fol_match:
                                following = extract_number(fol_match.group(1))
                                
                            if followers > 0 or following > 0:
                                print(f"  ✓ Found Stats: {followers:,} Followers | {following:,} Following")
                                status = 'Success'
                            else:
                                print("  ⚠️ Stats are 0. Meta description might be generic.")

                        else:
                            # Fallback Text
                             page_text = driver.find_element(By.TAG_NAME, "body").text
                             f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', page_text, re.I)
                             if f_match:
                                 followers = extract_number(f_match.group(1))
                                 status = 'Success'
                                 print(f"  ✓ Found Stats (Text): {followers:,}")

                    except Exception as e:
                        print(f"  ⚠️ Error extracting stats: {e}")
                        status = 'Data Error'
                else:
                    print("  ⚠️ Could not navigate to profile")
                    status = 'Nav Failed'

        except Exception as e:
            print(f"  ✗ Error: {e}")
            status = 'Error'
            error_msg = str(e)
            
        results.append({
            'Original_URL': url,
            'Username': username,
            'Followers': followers,
            'Following': following,
            'Status': status,
            'Error': error_msg
        })
        
        if i % 5 == 0:
            pd.DataFrame(results).to_excel('output/instagram_stealth.xlsx', index=False)
            print("  💾 Saved progress")
            
    driver.quit()
    pd.DataFrame(results).to_excel('output/instagram_stealth.xlsx', index=False)
    print(f"\n✅ Done! Saved to output/instagram_stealth.xlsx")

if __name__ == "__main__":
    main()
