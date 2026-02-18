"""
Instagram Scraper - RETRY FAILURES
Retries the 53 failed URLs from output/instagram_data.xlsx
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
print("INSTAGRAM SCRAPER - RETRY FAILURES")
print("="*60)

# Load existing results
try:
    df = pd.read_excel('output/instagram_data.xlsx')
    print(f"✓ Loaded existing data: {len(df)} rows")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit()

# Filter for failures
failures_indices = df[df['status'] != 'Success'].index.tolist()
print(f"✓ Found {len(failures_indices)} failed URLs to retry")

if len(failures_indices) == 0:
    print("No failures to retry!")
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

for i, idx in enumerate(failures_indices, 1):
    url = df.loc[idx, 'url']
    print(f"[{i}/{len(failures_indices)}] Retrying: {url}")
    
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Check if it's a profile URL (no /p/ or /reel/)
        is_profile = '/p/' not in url and '/reel/' not in url and '/tv/' not in url
        
        if is_profile:
            print("  👤 Detected Profile URL")
            followers = 0
            following = 0
            
            # Extract Followers
            f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', page_text, re.I)
            if f_match:
                followers = extract_number(f_match.group(1))
                
            # Extract Following
            fol_match = re.search(r'([\d,\.]+[KMB]?)\s+following', page_text, re.I)
            if fol_match:
                following = extract_number(fol_match.group(1))
                
            if followers > 0 or following > 0:
                print(f"  ✓ Found Stats: {followers:,} Followers | {following:,} Following")
                df.loc[idx, 'followers'] = followers
                df.loc[idx, 'following'] = following
                df.loc[idx, 'status'] = 'Success'
                df.loc[idx, 'error'] = ''
            else:
                print("  ⚠ Could not find profile stats")
                df.loc[idx, 'error'] = 'Profile stats not found'
                
        else:
            # It's a Post URL
            print("  📹 Detected Post URL")
            
            likes = 0
            comments = 0
            views = 0
            collaborators = ''
            
            # Likes
            likes_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes', page_text, re.I)
            if not likes_match:
                likes_match = re.search(r'Liked by\s+[^\n]+\s+and\s+(\d[\d,\.]*[KMB]?)', page_text, re.I)
            if likes_match:
                likes = extract_number(likes_match.group(1))
                
            # Comments
            comments_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments', page_text, re.I)
            if comments_match:
                comments = extract_number(comments_match.group(1))
                
            # Views
            views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views', page_text, re.I)
            if not views_match:
                views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', page_text, re.I)
            if views_match:
                views = extract_number(views_match.group(1))
            
            # Collaborators
            collab_match = re.search(r'with\s+@?([a-zA-Z0-9._]+)', page_text, re.I)
            if collab_match:
                collaborators = collab_match.group(1)
                
            if likes > 0 or comments > 0 or views > 0:
                print(f"  ✓ Found Data: {likes:,} Likes | {views:,} Views")
                df.loc[idx, 'likes'] = likes
                df.loc[idx, 'comments'] = comments
                df.loc[idx, 'views'] = views
                df.loc[idx, 'collaborators'] = collaborators
                df.loc[idx, 'status'] = 'Success'
                df.loc[idx, 'error'] = ''
            else:
                print("  ⚠ No data found (Post might be deleted/private)")
                df.loc[idx, 'error'] = 'No data found on retry'

    except Exception as e:
        print(f"  ✗ Error: {e}")
        df.loc[idx, 'error'] = str(e)

driver.quit()

# Save updated results
output_file = 'output/instagram_data_v2.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')
print(f"\n✅ Updated results saved to: {output_file}")

# Summary
print("\n" + "="*60)
print("RETRY SUMMARY")
print("="*60)
success_count = len(df[df['status'] == 'Success'])
print(f"Total Rows: {len(df)}")
print(f"Success: {success_count}")
print(f"Failed: {len(df) - success_count}")
print("="*60)
