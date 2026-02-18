"""
Instagram Scraper - NEW INPUT FILE
Processing input/INSTAURL.xlsx
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
print("INSTAGRAM SCRAPER - NEW INPUT FILE")
print("="*60)

# Load URLs
try:
    df = pd.read_excel('input/INSTAURL.xlsx')
    # Get the first column which is 'INSTAGRAM URL'
    urls = df.iloc[:, 0].dropna().tolist()
    urls = [url.strip() for url in urls if isinstance(url, str) and url.strip().startswith('http')]
    print(f"\n✓ Loaded {len(urls)} URLs from input/INSTAURL.xlsx")
except Exception as e:
    print(f"✗ Error: {e}")
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
print("👉 Log in to Instagram in the browser window")
print("👉 The script will automatically detect when you have logged in...")

# Wait for login
max_retries = 300  # 5 minutes
for _ in range(max_retries):
    try:
        # Check for indicators of being logged in
        if driver.find_elements(By.CSS_SELECTOR, "svg[aria-label='Home']") or \
           driver.find_elements(By.CSS_SELECTOR, "svg[aria-label='Search']") or \
           driver.find_elements(By.CSS_SELECTOR, "a[href='/'][role='link']"):
            print("\n✅ Login detected! Proceeding...")
            time.sleep(2)  # Give it a moment to settle
            break
    except:
        pass
    time.sleep(1)
else:
    print("\n⚠ Login not detected after 5 minutes. Continuing anyway (might fail)...")

print("\n✅ Starting scraping...")

results = []
Path('logs_new').mkdir(exist_ok=True)

print(f"\n{'='*60}")
print(f"SCRAPING {len(urls)} URLS")
print(f"{'='*60}\n")

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] {url[:50]}...")
    
    # Check for existing log
    log_filename = f"logs_new/url_{i}.txt"
    if Path(log_filename).exists() and Path(log_filename).stat().st_size > 500:
        print(f"  ✓ Already scraped (found {log_filename}). Skipping...")
        try:
            json_filename = f"logs_new/url_{i}_result.json"
            if Path(json_filename).exists():
                import json
                with open(json_filename, "r", encoding="utf-8") as f:
                    results.append(json.load(f))
        except:
            pass
        continue

    try:
        driver.get(url)
        time.sleep(random.uniform(6, 10))
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Save Log
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\n\n")
            f.write(page_text)
            
        # Determine Type
        is_profile = '/p/' not in url and '/reel/' not in url and '/tv/' not in url
        
        result = {
            'url': url,
            'likes': 0,
            'comments': 0,
            'views': 0,
            'followers': 0,
            'following': 0,
            'collaborators': '',
            'status': 'No Data',
            'error': ''
        }
        
        if is_profile:
            # --- PROFILE LOGIC ---
            followers = 0
            following = 0
            
            f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', page_text, re.I)
            if f_match:
                followers = extract_number(f_match.group(1))
                
            fol_match = re.search(r'([\d,\.]+[KMB]?)\s+following', page_text, re.I)
            if fol_match:
                following = extract_number(fol_match.group(1))
                
            result['followers'] = followers
            result['following'] = following
            
            if followers > 0 or following > 0:
                print(f"  👤 Profile: {followers:,} Followers | {following:,} Following")
                result['status'] = 'Success'
            else:
                print("  ⚠ Profile stats not found")
                
        else:
            # --- POST LOGIC ---
            likes = 0
            comments = 0
            views = 0
            collaborators = ''
            
            # NEW APPROACH: For reels/posts, Instagram shows likes and comments as
            # two consecutive standalone numbers right after the caption (after "... more")
            # This appears BEFORE any labeled "X likes" text from other posts in the feed
            
            lines = page_text.split('\n')
            found_engagement = False
            
            for j, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Look for "... more" or "Follow" which typically precedes engagement numbers
                if ('more' in line_stripped or 'Follow' in line_stripped) and j + 2 < len(lines):
                    # Check if next two lines are both numbers
                    next_line_1 = lines[j+1].strip()
                    next_line_2 = lines[j+2].strip()
                    
                    # Pattern: number followed by another number
                    if re.match(r'^[\d,\.]+[KMB]?$', next_line_1) and re.match(r'^[\d,\.]+[KMB]?$', next_line_2):
                        likes = extract_number(next_line_1)
                        comments = extract_number(next_line_2)
                        print(f"  📊 Engagement: {likes:,} likes, {comments:,} comments")
                        found_engagement = True
                        break
            
            # Fallback: Try standard labeled patterns (less reliable for reels)
            if not found_engagement:
                likes_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes', page_text, re.I)
                if not likes_match:
                    likes_match = re.search(r'Liked by\s+[^\n]+\s+and\s+(\d[\d,\.]*[KMB]?)', page_text, re.I)
                
                if likes_match:
                    likes = extract_number(likes_match.group(1))
                    
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
                
            result['likes'] = likes
            result['comments'] = comments
            result['views'] = views
            result['collaborators'] = collaborators
            
            if likes > 0 or comments > 0 or views > 0:
                print(f"  📹 Post: {likes:,} Likes | {views:,} Views")
                result['status'] = 'Success'
            else:
                print("  ⚠ No post data found")
        
        # Save Result JSON
        try:
            import json
            result_filename = f"logs_new/url_{i}_result.json"
            with open(result_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
        except:
            pass
            
        results.append(result)

    except Exception as e:
        print(f"  ✗ Error: {e}")
        results.append({
            'url': url,
            'status': 'Error',
            'error': str(e)
        })
    
    # Periodic Save
    if i % 10 == 0:
        df_results = pd.DataFrame(results)
        df_results.to_excel('output/instagram_data_new.xlsx', index=False, engine='openpyxl')

driver.quit()

# Final Save
Path('output').mkdir(exist_ok=True)
df_results = pd.DataFrame(results)
df_results.to_excel('output/instagram_data_new.xlsx', index=False, engine='openpyxl')
print(f"\n✅ Saved to: output/instagram_data_new.xlsx")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
successful = sum(1 for r in results if r.get('status') == 'Success')
print(f"Total: {len(results)} | Success: {successful} | Failed: {len(results)-successful}")
print("="*60)
