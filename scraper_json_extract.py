"""
Instagram Scraper - JSON Direct Extraction
Extracts data from Instagram's embedded JSON (_sharedData)
Most reliable method - no HTML parsing needed!
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import json
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

def extract_from_json(json_data):
    """Extract all data from Instagram's JSON structure."""
    result = {
        'username': '',
        'followers': 0,
        'following': 0,
        'likes': 0,
        'comments': 0,
        'views': 0,
        'collaborators': ''
    }
    
    try:
        # Navigate through the JSON structure
        if 'entry_data' in json_data:
            # Try PostPage (for /p/ URLs)
            if 'PostPage' in json_data['entry_data']:
                media = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
                
                # Username
                result['username'] = media.get('owner', {}).get('username', '')
                
                # Likes
                edge_likes = media.get('edge_media_preview_like', {})
                result['likes'] = edge_likes.get('count', 0)
                
                # Comments
                edge_comments = media.get('edge_media_to_parent_comment', {}) or media.get('edge_media_to_comment', {})
                result['comments'] = edge_comments.get('count', 0)
                
                # Views (for videos/reels)
                result['views'] = media.get('video_view_count', 0)
                
                # Collaborators
                coauthors = media.get('coauthor_producers', [])
                if coauthors:
                    result['collaborators'] = ', '.join([c.get('username', '') for c in coauthors])
                
                # Get profile stats
                owner = media.get('owner', {})
                result['followers'] = owner.get('edge_followed_by', {}).get('count', 0)
                result['following'] = owner.get('edge_follow', {}).get('count', 0)
                
            # Try ProfilePage
            elif 'ProfilePage' in json_data['entry_data']:
                user = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
                result['username'] = user.get('username', '')
                result['followers'] = user.get('edge_followed_by', {}).get('count', 0)
                result['following'] = user.get('edge_follow', {}).get('count', 0)
                
    except Exception as e:
        print(f"    ⚠ JSON extraction error: {e}")
    
    return result

def main():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - JSON EXTRACTION METHOD")
    print("Most Reliable: Extracts from embedded JSON")
    print("="*60)

    # Load URLs
    try:
        df = pd.read_excel('input/redourls.xlsx')
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
    print("✅ Chrome ready")

    # Login
    print("\n🔐 Please log in to Instagram manually in the browser...")
    driver.get("https://www.instagram.com/")
    print("👉 Log in to Instagram in the browser window")
    print("👉 After logging in, press ENTER here to continue...")
    input()

    print("\n✅ Starting scraping...")

    # Scrape
    results = []
    Path('output').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"SCRAPING {len(urls)} URLS")
    print(f"{'='*60}\n")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url[:50]}...")
        
        try:
            driver.get(url)
            time.sleep(random.uniform(6, 8))
            
            # Extract JSON from page
            json_data = None
            try:
                json_script = driver.execute_script("""
                    return window._sharedData;
                """)
                
                if json_script:
                    json_data = json_script
                    # Save for debugging
                    with open(f'logs/url_{i}_json.json', 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, default=str)
                    print(f"  ✓ Extracted JSON data")
                else:
                    print(f"  ⚠ No _sharedData found")
            except Exception as e:
                print(f"  ⚠ JSON extraction failed: {e}")
            
            # Extract data from JSON
            if json_data:
                data = extract_from_json(json_data)
                
                print(f"  👤 User: {data['username']}")
                print(f"  ✓ Stats: {data['followers']:,} Followers | {data['following']:,} Following")
                print(f"  ✓ Engagement: {data['likes']:,} Likes | {data['comments']:,} Comments | {data['views']:,} Views")
                if data['collaborators']:
                    print(f"  ✓ Collaborators: {data['collaborators']}")
                
                status = 'Success' if (data['likes'] > 0 or data['views'] > 0 or data['followers'] > 0) else 'No Data'
                
                results.append({
                    'url': url,
                    'username': data['username'],
                    'followers': data['followers'],
                    'following': data['following'],
                    'likes': data['likes'],
                    'comments': data['comments'],
                    'views': data['views'],
                    'collaborators': data['collaborators'],
                    'status': status,
                    'error': ''
                })
            else:
                # Fallback: No JSON found
                results.append({
                    'url': url,
                    'username': '',
                    'followers': 0,
                    'following': 0,
                    'likes': 0,
                    'comments': 0,
                    'views': 0,
                    'collaborators': '',
                    'status': 'No JSON',
                    'error': 'Could not extract _sharedData'
                })
                
        except Exception as e:
            error_msg = str(e)
            if "invalid session id" in error_msg or "no such window" in error_msg:
                print(f"\n🛑 CRITICAL ERROR: Browser session lost. Exiting...")
                break
                
            results.append({
                'url': url,
                'username': '',
                'followers': 0,
                'following': 0,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Error',
                'error': error_msg
            })
            print(f"  ✗ Error: {e}")
        
        # Save incrementally
        if i % 10 == 0 or i == len(urls):
            df_results = pd.DataFrame(results)
            df_results.to_excel('output/instagram_json_extract.xlsx', index=False, engine='openpyxl')
            print(f"  💾 Saved progress ({i}/{len(urls)})")
        
        if i < len(urls):
            time.sleep(random.uniform(4, 7))

    driver.quit()

    # Final Save
    df_results = pd.DataFrame(results)
    df_results.to_excel('output/instagram_json_extract.xlsx', index=False, engine='openpyxl')
    print(f"\n✅ Saved to: output/instagram_json_extract.xlsx")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r['status'] == 'Success')
    print(f"Total: {len(results)} | Success: {successful} | Failed: {len(results)-successful}")
    print(f"Total Likes: {sum(r['likes'] for r in results):,}")
    print(f"Total Comments: {sum(r['comments'] for r in results):,}")
    print(f"Total Views: {sum(r['views'] for r in results):,}")
    print("="*60)

if __name__ == "__main__":
    main()
