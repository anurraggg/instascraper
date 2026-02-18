"""
Instagram Scraper - TEST ENRICHMENT
Runs enrichment on first 3 URLs only.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import random

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
print("TESTING ENRICHMENT LOGIC (3 URLs)")
print("="*60)

# Load Input File
input_file = 'final_output/Instagram_Final_Updated_114.xlsx'

try:
    df = pd.read_excel(input_file)
    urls = df['url'].tolist()[:3] # ONLY FIRST 3
    print(f"✓ Loaded {len(urls)} URLs for testing")
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

print("\n✅ Starting test...")

results = []

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] Processing: {url[:50]}...")
    
    row_data = {'url': url}
    
    try:
        driver.get(url)
        time.sleep(5)
        
        # 1. Extract Username & Collaborators
        username = ''
        collaborators = []
        
        try:
            # Try multiple selectors for username/collaborators in header
            header_links = driver.find_elements(By.XPATH, "//header//h2//a")
            if not header_links:
                 header_links = driver.find_elements(By.XPATH, "//header//div[contains(@class, '_aaqt')]//a")
            
            # Debug print
            # print(f"DEBUG: Found {len(header_links)} header links")
            
            if header_links:
                usernames_found = [link.text.strip() for link in header_links if link.text.strip()]
                if usernames_found:
                    username = usernames_found[0]
                    if len(usernames_found) > 1:
                        collaborators = usernames_found[1:]
        except Exception as e:
            print(f"  ⚠ Error extracting header info: {e}")

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
            
            # 2. Go to Profile
            print(f"  ➡️ Navigating to profile: {username}")
            driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(5)
            
            try:
                # Extract Followers
                followers_elem = driver.find_elements(By.XPATH, "//a[contains(@href, '/followers/')]//span")
                if not followers_elem:
                     followers_elem = driver.find_elements(By.XPATH, "//ul//li[2]//span")
                
                if followers_elem:
                    followers_text = followers_elem[0].get_attribute("title")
                    if not followers_text: followers_text = followers_elem[0].text
                    followers_count = extract_number(followers_text)
                    print(f"  To Followers: {followers_count}")
                    row_data['followers_count'] = followers_count

                # Extract Following
                following_elem = driver.find_elements(By.XPATH, "//a[contains(@href, '/following/')]//span")
                if not following_elem:
                     following_elem = driver.find_elements(By.XPATH, "//ul//li[3]//span")

                if following_elem:
                    following_text = following_elem[0].text
                    following_count = extract_number(following_text)
                    print(f"  To Following: {following_count}")
                    row_data['following_count'] = following_count
                
            except Exception as e:
                print(f"  ⚠ Error extracting profile stats: {e}")
                
        else:
            print("  ⚠ Could not find username")

    except Exception as e:
        print(f"  ✗ Error processing URL: {e}")
    
    results.append(row_data)

driver.quit()
print("\nTest Complete. Results:")
print(pd.DataFrame(results).to_string())
