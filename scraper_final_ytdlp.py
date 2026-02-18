import pandas as pd
import subprocess
import json
import time
import random
import os
from datetime import datetime
from pathlib import Path

# Configuration
INPUT_FILE = "input/INSTAURL.xlsx"
OUTPUT_FILE = "output/instagram_final_results.xlsx"

def get_ytdlp_data(url):
    """Run yt-dlp to get metadata."""
    try:
        # Use --cookies-from-browser to leverage existing sessions if possible, 
        # or just try without first as it's faster.
        cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download", url]
        
        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return None, f"Error: {result.stderr.strip()}"
            
        data = json.loads(result.stdout)
        return data, None
        
    except Exception as e:
        return None, str(e)

def main():
    print("="*60)
    print("INSTAGRAM FINAL DATA EXTRACTION (YT-DLP)")
    print("="*60)
    
    # 1. Load URLs
    try:
        df = pd.read_excel(INPUT_FILE)
        # Get the first column
        urls = df.iloc[:, 0].dropna().tolist()
        urls = [url.strip() for url in urls if isinstance(url, str) and url.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs from {INPUT_FILE}")
    except Exception as e:
        print(f"✗ Error loading input file: {e}")
        return

    results = []
    Path("output").mkdir(exist_ok=True)
    
    print("\n🚀 Starting extraction...")
    print("This method is efficient and will try to get views, likes, and comments.")
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        # Skip YouTube URLs if accidentally included in the list for Instagram scraping
        if "youtube.com" in url or "youtu.be" in url:
            print("  ⚠️ Skipping YouTube URL in Instagram scraper.")
            continue

        data, error = get_ytdlp_data(url)
        
        entry = {
            'url': url,
            'status': 'Failed',
            'likes': 0,
            'comments': 0,
            'views': 0,
            'username': '',
            'upload_date': '',
            'description': '',
            'error': ''
        }
        
        if data:
            entry['status'] = 'Success'
            entry['views'] = data.get('view_count', 0)
            entry['likes'] = data.get('like_count', 0)
            entry['comments'] = data.get('comment_count', 0)
            entry['username'] = data.get('uploader', '')
            entry['upload_date'] = data.get('upload_date', '')
            entry['description'] = data.get('description', '')[:500] if data.get('description') else ''
            
            print(f"  ✅ SUCCESS: {entry['views']:,} Views | {entry['likes']:,} Likes | {entry['comments']:,} Comments")
        else:
            entry['error'] = error
            print(f"  ❌ FAILED: {error[:100]}...")
            
        results.append(entry)
        
        # Periodic Save
        if i % 5 == 0:
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            
        # Small random delay to avoid rate limiting
        time.sleep(random.uniform(0.5, 1.5))

    # Final Save
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ COMPLETE! Results saved to: {OUTPUT_FILE}")
    
    # Summary
    success_count = sum(1 for r in results if r['status'] == 'Success')
    print(f"Total: {len(results)} | Success: {success_count} | Failed: {len(results)-success_count}")

if __name__ == "__main__":
    main()
