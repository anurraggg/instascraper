import instaloader
import pandas as pd
import re
import time
import random
import pickle
import os

# Configuration — set IG_USERNAME as an environment variable
USERNAME = os.environ.get("IG_USERNAME", "")
INPUT_FILE = "output/instagram_auto.xlsx"
OUTPUT_FILE = "output/instagram_auto_views_final.xlsx"

def extract_shortcode(url):
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def scrape_views_session():
    print("\n" + "="*60)
    print("INSTAGRAM VIEW SCRAPER - SESSION COOKIES")
    print("="*60)
    
    # Load Data
    try:
        df = pd.read_excel(INPUT_FILE)
        print(f"✓ Loaded {len(df)} rows")
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return

    # Initialize Instaloader
    L = instaloader.Instaloader()
    
    # Load Cookies
    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            L.context.session.cookies.set(cookie['name'], cookie['value'])
        print(f"✅ Loaded {len(cookies)} cookies into session")
        
        # Verify Session
        print(f"  Verifying session for {USERNAME}...")
        # We can't easily verify without making a request, so we'll just try to scrape
    except Exception as e:
        print(f"✗ Error loading cookies: {e}")
        return

    updated_count = 0
    
    for index, row in df.iterrows():
        url = row['url']
        current_views = row.get('views', 0)
        
        try:
            if int(float(current_views)) > 0:
                continue
        except: pass
            
        print(f"\n[{index+1}/{len(df)}] {url[:40]}...")
        
        shortcode = extract_shortcode(url)
        if not shortcode:
            print(f"  ✗ Invalid URL format")
            continue
            
        try:
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            if post.is_video:
                views = post.video_view_count
                print(f"  ✓ Found Views: {views:,}")
                df.at[index, 'views'] = views
                updated_count += 1
            else:
                print("  ℹ Post is not a video")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            if "429" in str(e) or "401" in str(e):
                print("  🛑 Critical error (Rate Limit / Auth). Stopping.")
                break
            
        # Rate Limit Delay
        time.sleep(random.uniform(5, 8))
        
        # Save every 5
        if updated_count > 0 and updated_count % 5 == 0:
            df.to_excel(OUTPUT_FILE, index=False)
            print("  💾 Saved progress")

    # Final Save
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Updated {updated_count} rows. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_views_session()
