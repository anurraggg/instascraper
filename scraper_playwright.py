"""
Instagram Scraper - Playwright Version
Robust scraping using Playwright with persistent login state.
"""

from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random
import re
import os
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

def run():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - PLAYWRIGHT")
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

    with sync_playwright() as p:
        # Launch Browser
        print("\n🚀 Launching Browser...")
        browser = p.chromium.launch(headless=False)
        
        # Context with State (Login Persistence)
        state_file = "state.json"
        if os.path.exists(state_file):
            print(f"  ✓ Loading login state from {state_file}")
            context = browser.new_context(storage_state=state_file)
        else:
            print("  ℹ No login state found. Creating new context.")
            context = browser.new_context()

        page = context.new_page()
        
        # Check Login
        print("\n🔐 Checking Login Status...")
        page.goto("https://www.instagram.com/")
        time.sleep(5)
        
        # If login input is visible, we are not logged in
        if page.locator("input[name='username']").is_visible():
            print("\n⚠️ NOT LOGGED IN")
            print("👉 Please log in manually in the browser window.")
            print("👉 Press ENTER here once you are logged in...")
            input()
            
            # Save State
            context.storage_state(path=state_file)
            print(f"  💾 Login state saved to {state_file}")
        else:
            print("  ✅ Already logged in!")

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
                page.goto(url)
                # Wait for network idle (page fully loaded)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass # Continue anyway
                
                time.sleep(random.uniform(3, 5))
                
                # Check for "Unavailable"
                if "Sorry, this page isn't available" in page.content():
                    print("  ⚠️ Page unavailable")
                    status = 'Unavailable'
                else:
                    # 1. Get Username (Title Strategy)
                    title = page.title()
                    if ' on Instagram:' in title:
                        username = title.split(' on Instagram:')[0].strip()
                        print(f"  👤 Username (Title): {username}")
                        
                        # Navigate to Profile
                        page.goto(f"https://www.instagram.com/{username}/")
                        try:
                            page.wait_for_load_state("networkidle", timeout=10000)
                        except:
                            pass
                        time.sleep(random.uniform(3, 5))
                    
                    # 2. Extract Stats (Meta Strategy)
                    try:
                        meta_desc = page.locator("meta[property='og:description']").get_attribute("content")
                        if meta_desc:
                            print(f"  🔍 Meta: {meta_desc}")
                            f_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta_desc, re.I)
                            if f_match:
                                followers = extract_number(f_match.group(1))
                            fol_match = re.search(r'([\d,\.]+[KMB]?)\s+Following', meta_desc, re.I)
                            if fol_match:
                                following = extract_number(fol_match.group(1))
                            
                            print(f"  ✓ Stats: {followers:,} Followers | {following:,} Following")
                            status = 'Success'
                    except Exception as e:
                        print(f"  ⚠️ Meta extraction failed: {e}")
                        
                    # 3. Fallback: Visible Text Strategy
                    if followers == 0:
                        try:
                            # Try to find "followers" text on page
                            text_content = page.content()
                            f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', text_content, re.I)
                            if f_match:
                                followers = extract_number(f_match.group(1))
                                print(f"  ✓ Stats (Text): {followers:,} Followers")
                                status = 'Success'
                        except:
                            pass

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
                pd.DataFrame(results).to_excel('output/instagram_playwright.xlsx', index=False)
                print("  💾 Saved progress")
        
        browser.close()
        
        # Final Save
        pd.DataFrame(results).to_excel('output/instagram_playwright.xlsx', index=False)
        print(f"\n✅ Done! Saved to output/instagram_playwright.xlsx")

if __name__ == "__main__":
    run()
