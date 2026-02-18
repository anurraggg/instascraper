"""
Instagram Scraper - Profile Click Flow
Navigates to profile by CLICKING the username on the post/reel page.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pandas as pd
import time
import re
import random
from pathlib import Path

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

def main():
    print("\n" + "="*60)
    print("INSTAGRAM PROFILE SCRAPER - CLICK FLOW")
    print("Target: Click Username -> Profile -> Followers/Following")
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
    
    print("\n✅ Starting scraping...")
    
    results = []
    Path('output').mkdir(exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        username = ''
        followers = 0
        following = 0
        collaborators = []
        status = 'Init'
        error_msg = ''
        
        try:
            # 1. Go to Post URL
            driver.get(url)
            time.sleep(random.uniform(4, 6))
            
            # 2. Find and Click Username
            clicked = False
            
            # Strategy A: Try to find username text first to identify the element
            # This helps us know what we are looking for
            try:
                # Look for the username in the header (Post view)
                # Usually inside a header tag, first anchor
                header_username_elem = None
                
                # Try standard post header
                try:
                    header_username_elem = driver.find_element(By.XPATH, "//header//a[not(contains(@href, 'explore')) and string-length(text()) > 0]")
                except:
                    pass
                
                # Try Reel overlay (bottom left usually)
                if not header_username_elem:
                    try:
                        # Look for anchor with class containing 'User' or similar, or just by position
                        # Often reels have the username with an 'a' tag that has a specific structure
                        # Let's try finding by text if we can extract it from title first
                        title = driver.title
                        if 'on Instagram' in title:
                            possible_user = title.split('on Instagram')[0].strip().split(' ')[0]
                            if possible_user:
                                header_username_elem = driver.find_element(By.XPATH, f"//a[text()='{possible_user}']")
                    except:
                        pass

                if header_username_elem:
                    username = header_username_elem.text
                    print(f"  🎯 Found Username Link: {username}")
                    
                    # Scroll into view just in case
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header_username_elem)
                    time.sleep(1)
                    
                    # CLICK
                    try:
                        header_username_elem.click()
                        clicked = True
                        print("  🖱️ Clicked username!")
                    except ElementClickInterceptedException:
                        print("  ⚠️ Click intercepted, trying JS click...")
                        driver.execute_script("arguments[0].click();", header_username_elem)
                        clicked = True
                    
                    # Wait for navigation
                    time.sleep(random.uniform(3, 5))
                    
                    # Verify we are on profile page
                    if '/p/' not in driver.current_url and '/reel/' not in driver.current_url:
                        print(f"  ✓ Navigated to: {driver.current_url}")
                    else:
                        print("  ⚠️ Click might have failed, still on post page.")
                        clicked = False
                else:
                    print("  ⚠️ Could not find clickable username element.")
                    
            except Exception as e:
                print(f"  ⚠️ Error trying to click username: {e}")
            
            # Fallback: If click failed, try to construct URL if we have a username
            if not clicked:
                print("  🔄 Fallback: Trying to extract username and navigate directly...")
                if not username:
                    # Try to get username from metadata
                    try:
                        meta_title = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute("content")
                        match = re.search(r'\(@([a-zA-Z0-9._]+)\)', meta_title)
                        if match:
                            username = match.group(1)
                    except:
                        pass
                
                if username:
                    print(f"  👤 Extracted Username: {username}")
                    driver.get(f"https://www.instagram.com/{username}/")
                    time.sleep(random.uniform(3, 5))
                else:
                    print("  ❌ Could not determine username. Skipping.")
                    status = 'No Username'
                    raise Exception("Username not found")

            # 3. Extract Profile Data
            # Now we should be on the profile page
            
            # Double check we are on a profile page
            current_url = driver.current_url
            if 'instagram.com/p/' in current_url or 'instagram.com/reel/' in current_url:
                 print("  ❌ Still on post page. Aborting profile scrape.")
                 status = 'Nav Failed'
            else:
                # Extract Followers/Following
                try:
                    # Strategy 1: Meta Description (Reliable)
                    meta_desc = ''
                    try:
                        meta_elem = driver.find_element(By.XPATH, "//meta[@property='og:description']")
                        meta_desc = meta_elem.get_attribute("content")
                    except:
                        pass
                    
                    if meta_desc:
                        f_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta_desc, re.I)
                        if f_match:
                            followers = extract_number(f_match.group(1))
                            
                        fol_match = re.search(r'([\d,\.]+[KMB]?)\s+Following', meta_desc, re.I)
                        if fol_match:
                            following = extract_number(fol_match.group(1))
                            
                        print(f"  ✓ Found Stats (Meta): {followers:,} Followers | {following:,} Following")
                    
                    # Strategy 2: Page Text (Fallback)
                    if followers == 0:
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', page_text, re.I)
                        if f_match:
                            followers = extract_number(f_match.group(1))
                        fol_match = re.search(r'([\d,\.]+[KMB]?)\s+following', page_text, re.I)
                        if fol_match:
                            following = extract_number(fol_match.group(1))
                        
                        if followers > 0:
                            print(f"  ✓ Found Stats (Text): {followers:,} Followers | {following:,} Following")

                    status = 'Success'
                    
                except Exception as e:
                    print(f"  ⚠️ Error extracting stats: {e}")
                    status = 'Data Error'
                    error_msg = str(e)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            status = 'Error'
            error_msg = str(e)
            
        # Record Result
        results.append({
            'Original_URL': url,
            'Username': username,
            'Followers': followers,
            'Following': following,
            'Status': status,
            'Error': error_msg
        })
        
        # Save incrementally
        if i % 5 == 0:
            df_res = pd.DataFrame(results)
            df_res.to_excel('output/instagram_profiles_click.xlsx', index=False)
            print("  💾 Saved progress")
            
    driver.quit()
    
    # Final Save
    df_res = pd.DataFrame(results)
    df_res.to_excel('output/instagram_profiles_click.xlsx', index=False)
    print(f"\n✅ Done! Saved to output/instagram_profiles_click.xlsx")

if __name__ == "__main__":
    main()
