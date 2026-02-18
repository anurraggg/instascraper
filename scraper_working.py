"""
Instagram Scraper - WORKING SELENIUM VERSION
Fully automated scraper for 462+ URLs
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import os
from pathlib import Path


def extract_number(text):
    """Extract number from text like '1.2K', '5M', '234'."""
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


def setup_driver():
    """Setup Chrome with anti-detection."""
    print("🚀 Setting up Chrome...")
    
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--log-level=3')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    print("✅ Chrome ready")
    return driver


def login(driver, username, password):
    """Login to Instagram."""
    print(f"\n🔐 Logging in as {username}...")
    
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(4)
    
    try:
        # Enter credentials
        driver.find_element(By.NAME, "username").send_keys(username)
        time.sleep(1)
        driver.find_element(By.NAME, "password").send_keys(password)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        print("⏳ Logging in...")
        time.sleep(10)
        
        # Handle popups
        try:
            driver.find_element(By.XPATH, "//button[contains(text(), 'Not now') or contains(text(), 'Not Now')]").click()
            time.sleep(2)
        except:
            pass
        
        try:
            driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Not now')]").click()
            time.sleep(2)
        except:
            pass
        
        print("✅ Logged in!")
        return True
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return False


def scrape_post(driver, url):
    """Scrape one post."""
    try:
        driver.get(url)
        time.sleep(6)  # Wait for page load
        
        # Scroll to load all content
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 400)")
            time.sleep(1)
        
        # Get page text
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Extract metrics using regex
        likes = 0
        comments = 0
        views = 0
        collaborators = ''
        
        # Likes
        likes_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes?', page_text, re.IGNORECASE)
        if likes_match:
            likes = extract_number(likes_match.group(1))
        
        # Comments
        comments_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments?', page_text, re.IGNORECASE)
        if not comments_match:
            comments_match = re.search(r'View all (\d[\d,\.]*[KMB]?)\s*comments?', page_text, re.IGNORECASE)
        if comments_match:
            comments = extract_number(comments_match.group(1))
        
        # Views
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views?', page_text, re.IGNORECASE)
        if views_match:
            views = extract_number(views_match.group(1))
        
        # Collaborators
        collab_match = re.search(r'with\s+@?([a-zA-Z0-9._]+)', page_text, re.IGNORECASE)
        if collab_match:
            collaborators = collab_match.group(1)
        
        status = 'Success' if (likes > 0 or comments > 0 or views > 0) else 'No Data'
        
        return {
            'url': url,
            'likes': likes,
            'comments': comments,
            'views': views,
            'collaborators': collaborators,
            'status': status,
            'error': '' if status == 'Success' else 'No metrics found'
        }
        
    except Exception as e:
        return {
            'url': url,
            'likes': 0,
            'comments': 0,
            'views': 0,
            'collaborators': '',
            'status': 'Error',
            'error': str(e)
        }


def main():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - SELENIUM (OPTIMIZED)")
    print("="*60)
    
    # Load URLs
    try:
        df = pd.read_csv('input/Instagram_URLS.csv')
        urls = df.iloc[:, 0].dropna().tolist()[1:]
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"\n✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Setup
    driver = setup_driver()
    
    if not login(driver, os.environ.get("IG_USERNAME", ""), os.environ.get("IG_PASSWORD", "")):
        driver.quit()
        return
    
    # Scrape
    results = []
    print(f"\n{'='*60}")
    print(f"SCRAPING {len(urls)} URLS")
    print(f"{'='*60}\n")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url[:60]}...")
        result = scrape_post(driver, url)
        results.append(result)
        
        print(f"  ✓ Likes: {result['likes']:,} | Comments: {result['comments']:,} | Views: {result['views']:,}")
        if result['collaborators']:
            print(f"  ✓ Collaborators: {result['collaborators']}")
        
        if i < len(urls):
            time.sleep(3)  # Rate limiting
    
    driver.quit()
    
    # Save
    Path('output').mkdir(exist_ok=True)
    df_results = pd.DataFrame(results)
    df_results.to_excel('output/instagram_data.xlsx', index=False, engine='openpyxl')
    print(f"\n✅ Saved to: output/instagram_data.xlsx")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r['status'] == 'Success')
    print(f"Total: {len(results)} | Success: {successful} | Failed: {len(results)-successful}")
    print(f"Likes: {sum(r['likes'] for r in results):,}")
    print(f"Comments: {sum(r['comments'] for r in results):,}")
    print(f"Views: {sum(r['views'] for r in results):,}")
    print("="*60)
    
    if successful > 0:
        print("\n✅ WORKING! Ready for all 462 URLs!")


if __name__ == "__main__":
    main()
