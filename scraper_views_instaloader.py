import instaloader
import pandas as pd
import re
import time
import random
import os

# Configuration — set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
INPUT_FILE = "output/instagram_auto.xlsx"
OUTPUT_FILE = "output/instagram_auto_views.xlsx"

def extract_shortcode(url):
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def scrape_views():
    print("\n" + "="*60)
    print("INSTAGRAM VIEW SCRAPER - INSTALOADER")
    print("="*60)
    
    # Load Data
    try:
        df = pd.read_excel(INPUT_FILE)
        print(f"✓ Loaded {len(df)} rows from {INPUT_FILE}")
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return

    # Initialize Instaloader
    L = instaloader.Instaloader()
    
    # Login
    print(f"\n🔐 Skipping Login (Anonymous Mode)...")
    # try:
    #     L.login(USERNAME, PASSWORD)
    #     print("✅ Login successful!")
    # except Exception as e:
    #     print(f"✗ Login failed: {e}")
    #     print("⚠ Attempting to scrape without login (Public posts only)...")

    updated_count = 0
    
    for index, row in df.iterrows():
        url = row['url']
        current_views = row.get('views', 0)
        
        # Skip if views already exist (and are > 0)
        try:
            if int(float(current_views)) > 0:
                continue
        except: pass
            
        print(f"\n[{index+1}/{len(df)}] Processing: {url[:60]}...")
        
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
                print("  ℹ Post is not a video (Image/Carousel)")
                # Optionally set views to 0 or leave as is
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            # If 429 (Rate Limit), wait longer
            if "429" in str(e):
                print("  ⏳ Rate limit hit. Sleeping for 60s...")
                time.sleep(60)
            
        # Rate Limit Delay
        time.sleep(random.uniform(5, 8))
        
        # Save every 10
        if updated_count > 0 and updated_count % 10 == 0:
            df.to_excel(OUTPUT_FILE, index=False)
            print("  💾 Saved progress")

    # Final Save
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! Updated {updated_count} rows. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_views()
