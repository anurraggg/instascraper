"""
Instagram Scraper - ENRICH DATA
Enriches existing data with Username, Collaborators, Followers, and Following counts.
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
print("INSTAGRAM SCRAPER - ENRICH DATA")
print("="*60)

# Load Input File
input_file = 'final_output/Instagram_Final_Updated_114.xlsx'
output_file = 'final_output/Instagram_Enriched_Complete.xlsx'

try:
    df = pd.read_excel(input_file)
    urls = df['url'].tolist()
    print(f"✓ Loaded {len(urls)} URLs to enrich")
except Exception as e:
    print(f"✗ Error loading input file: {e}")
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

print("\n✅ Starting enrichment...")

results = []
# Load existing results if resuming
if os.path.exists(output_file):
    try:
        existing_df = pd.read_excel(output_file)
        results = existing_df.to_dict('records')
        processed_urls = set(existing_df['url'].tolist())
        print(f"✓ Resuming from {len(results)} already processed items")
    except: pass
else:
    processed_urls = set()

for i, url in enumerate(urls, 1):
    if url in processed_urls:
        continue

    print(f"[{i}/{len(urls)}] Processing: {url[:50]}...")
    
    # Preserve existing data for this row
    row_data = df[df['url'] == url].iloc[0].to_dict()
    
    # Initialize new fields
    row_data['username'] = ''
    row_data['collaborators'] = ''
    row_data['followers_count'] = 0
    row_data['following_count'] = 0
    row_data['enrich_status'] = 'Failed'
    
    try:
        driver.get(url)
        time.sleep(random.uniform(4, 6))
        
        # 1. Extract Username & Collaborators
        username = ''
        collaborators = []
        
        # Strategy: Look at the header links
        try:
            # This selector finds links in the header (usually username + collaborators)
            # Adjust selector based on actual DOM structure if needed
            header_links = driver.find_elements(By.XPATH, "//header//h2//a")
            if not header_links:
                 header_links = driver.find_elements(By.XPATH, "//header//div[contains(@class, '_aaqt')]//a") # Fallback

            if header_links:
                usernames_found = [link.text.strip() for link in header_links if link.text.strip()]
                if usernames_found:
                    username = usernames_found[0]
                    if len(usernames_found) > 1:
                        collaborators = usernames_found[1:]
        except Exception as e:
            print(f"  ⚠ Error extracting header info: {e}")

        # Fallback for username if not found
        if not username:
             try:
                meta_url = driver.find_element(By.XPATH, "//meta[@property='og:url']").get_attribute("content")
                if 'instagram.com/' in meta_url:
                    parts = meta_url.split('instagram.com/')[-1].split('/')
                    if len(parts) > 0: username = parts[0]
             except: pass

        if username:
            print(f"  👤 Username: {username}")
            row_data['username'] = username
            if collaborators:
                print(f"  👥 Collaborators: {', '.join(collaborators)}")
                row_data['collaborators'] = ', '.join(collaborators)
            
            # 2. Go to Profile for Stats
            # Open new tab to keep flow clean or just navigate
            print(f"  ➡️ Navigating to profile: {username}")
            driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(random.uniform(3, 5))
            
            try:
                # Extract Followers
                # Look for links with 'followers' in href or text
                followers_elem = driver.find_elements(By.XPATH, "//a[contains(@href, '/followers/')]//span")
                if not followers_elem:
                     followers_elem = driver.find_elements(By.XPATH, "//ul//li[2]//span") # Fallback by position
                
                if followers_elem:
                    followers_text = followers_elem[0].get_attribute("title") # Often in title attribute for full number
                    if not followers_text: followers_text = followers_elem[0].text
                    followers_count = extract_number(followers_text)
                    print(f"  To Followers: {followers_count}")
                    row_data['followers_count'] = followers_count

                # Extract Following
                following_elem = driver.find_elements(By.XPATH, "//a[contains(@href, '/following/')]//span")
                if not following_elem:
                     following_elem = driver.find_elements(By.XPATH, "//ul//li[3]//span") # Fallback by position

                if following_elem:
                    following_text = following_elem[0].text
                    following_count = extract_number(following_text)
                    print(f"  To Following: {following_count}")
                    row_data['following_count'] = following_count
                
                row_data['enrich_status'] = 'Success'

            except Exception as e:
                print(f"  ⚠ Error extracting profile stats: {e}")
                
        else:
            print("  ⚠ Could not find username")

    except Exception as e:
        print(f"  ✗ Error processing URL: {e}")
    
    results.append(row_data)
    
    # Periodic Save
    if i % 5 == 0:
        pd.DataFrame(results).to_excel(output_file, index=False)
        print(f"  💾 Saved progress to {output_file}")

driver.quit()

# Final Save
pd.DataFrame(results).to_excel(output_file, index=False)
print(f"\n✅ Final results saved to {output_file}")
