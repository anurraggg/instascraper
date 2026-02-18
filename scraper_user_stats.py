"""
Instagram User Stats Scraper
Extracts: Username, Collaborators (Full Name), Followers, Following
Input: input/Instagram_URLS.csv
Output: output/instagram_user_stats.xlsx
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
from pathlib import Path
import urllib.parse

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

def get_full_username_from_link(element):
    """Extracts username from href, handling /username/ format."""
    try:
        href = element.get_attribute('href')
        if href:
            # Remove trailing slash and split
            parts = href.strip('/').split('/')
            # Usually the last part is the username, unless it's a special link
            # e.g. instagram.com/username
            return parts[-1]
    except:
        pass
    return None

print("\n" + "="*60)
print("INSTAGRAM USER STATS SCRAPER")
print("="*60)

# Load URLs
try:
    df = pd.read_csv('input/Instagram_URLS.csv')
    # Assuming the first column contains URLs
    urls = df.iloc[:, 0].dropna().tolist()
    # Clean URLs
    urls = [url.strip() for url in urls if isinstance(url, str) and url.strip().startswith('http')]
    print(f"\n✓ Loaded {len(urls)} URLs")
except Exception as e:
    print(f"✗ Error loading URLs: {e}")
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

print("\n✅ Starting scraping...")

results = []

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] Processing: {url[:60]}...")
    
    data = {
        'url': url,
        'username': '',
        'collaborators': '',
        'followers': 0,
        'following': 0,
        'status': 'Pending',
        'error': ''
    }
    
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8)) # Wait for load
        
        # 1. Identify Username & Collaborators from Post Header
        # Strategy: Look for the header links before the timestamp or "Follow" button
        usernames_found = []
        
        try:
            # Try to find the header element. It usually contains the profile pic and username.
            # We can look for all 'a' tags that link to a profile (no /p/, /reel/, /explore/, etc.)
            # and are located at the top of the content.
            
            # Get all links on the page
            links = driver.find_elements(By.TAG_NAME, "a")
            
            # Filter for potential profile links in the "header" area
            # We assume the header is roughly the first part of the page or the article
            # A good heuristic for the post header is finding the link that contains the profile picture or name
            # adjacent to "Follow" text or the timestamp.
            
            potential_users = []
            for link in links:
                href = link.get_attribute('href')
                if not href or 'instagram.com' not in href:
                    continue
                
                # Exclude non-profile links
                if any(x in href for x in ['/p/', '/reel/', '/explore/', '/direct/', '/stories/', '/legal/', '/about/']):
                    continue
                
                # Extract username
                u_name = get_full_username_from_link(link)
                if u_name and u_name not in potential_users:
                    # Check if this link is "visible" and likely in the header
                    # (This is hard to do perfectly without complex logic, so we'll collect candidates)
                    
                    # Heuristic: If the link text matches the username (case insensitive), it's a strong candidate
                    # Or if the link contains an image (profile pic)
                    potential_users.append(u_name)
            
            # The first user found is usually the owner.
            # If there are "collaborators", they appear as "User1 and User2" or "User1 with User2"
            
            # Let's try to parse the "title" or text of the header container if possible.
            # But relying on the 'potential_users' list found at the top is safer for "full names".
            
            # Let's refine: The post header usually has a specific structure.
            # We can look for the text "and" or "with" between links.
            
            # SIMPLER APPROACH:
            # 1. Get the page title. It often says "User (@username) on Instagram..." or "User and Collab (@collab) on Instagram"
            page_title = driver.title
            
            # 2. Extract from the visible header on the post
            # Find the <header> inside the <article> if possible
            try:
                article = driver.find_element(By.TAG_NAME, "article")
                header = article.find_element(By.TAG_NAME, "header")
                header_links = header.find_elements(By.TAG_NAME, "a")
                
                header_usernames = []
                for hl in header_links:
                    un = get_full_username_from_link(hl)
                    if un and un not in header_usernames:
                        header_usernames.append(un)
                
                if header_usernames:
                    data['username'] = header_usernames[0]
                    if len(header_usernames) > 1:
                        data['collaborators'] = ", ".join(header_usernames[1:])
                        print(f"  ✓ Found Collaborators (Header): {data['collaborators']}")
            except:
                # Fallback if no article/header found (e.g. some layouts)
                pass

        except Exception as e:
            print(f"  ⚠ Error finding usernames: {e}")

        # 2. Go to Profile for Stats (Followers/Following)
        # If we found a username, go to their profile.
        # If we have collaborators, we might want to go to the MAIN user's profile.
        
        target_username = data['username']
        if not target_username:
            # Try to extract from URL if we failed to find it on page
            # e.g. instagram.com/username/p/id
            # But the input is a post URL, so we can't always know.
            pass

        if target_username:
            print(f"  👤 Main Username: {target_username}")
            
            # Navigate to profile
            profile_url = f"https://www.instagram.com/{target_username}/"
            driver.get(profile_url)
            time.sleep(random.uniform(3, 5))
            
            # Extract Stats
            try:
                # Look for "followers" and "following" in text
                # Usually in <ul class="..."> or similar
                # We can search the whole body text for "X followers"
                
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Followers
                f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', page_text, re.I)
                if f_match:
                    data['followers'] = extract_number(f_match.group(1))
                
                # Following
                fol_match = re.search(r'([\d,\.]+[KMB]?)\s+following', page_text, re.I)
                if fol_match:
                    data['following'] = extract_number(fol_match.group(1))
                    
                print(f"  ✓ Stats: {data['followers']:,} Followers | {data['following']:,} Following")
                
            except Exception as e:
                print(f"  ⚠ Error extracting stats: {e}")
        else:
            print("  ⚠ Could not identify username to fetch stats.")
            data['error'] = "Username not found"

        data['status'] = 'Success'
        
    except Exception as e:
        print(f"  ✗ Error processing URL: {e}")
        data['status'] = 'Error'
        data['error'] = str(e)
    
    results.append(data)
    
    # Save incrementally
    if i % 5 == 0:
        pd.DataFrame(results).to_excel('output/instagram_user_stats.xlsx', index=False)
        print("  (Saved progress)")

driver.quit()

# Final Save
Path('output').mkdir(exist_ok=True)
df_results = pd.DataFrame(results)
df_results.to_excel('output/instagram_user_stats.xlsx', index=False)
print(f"\n✅ Completed! Saved to: output/instagram_user_stats.xlsx")
