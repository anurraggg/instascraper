import pandas as pd
import subprocess
import json
import time
import random
import os
from datetime import datetime

# Configuration
INPUT_FILE = "input/redourls.xlsx"
OUTPUT_FILE = "output/instagram_views_ytdlp.xlsx"

def get_ytdlp_data(url):
    """Run yt-dlp to get metadata."""
    try:
        # --dump-json: get metadata in JSON format
        # --no-warnings: suppress warnings
        # --skip-download: don't download the video
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
    print("INSTAGRAM VIEWS SCRAPER (YT-DLP)")
    print("="*60)
    
    # 1. Load URLs
    try:
        df = pd.read_excel(INPUT_FILE)
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs from {INPUT_FILE}")
    except Exception as e:
        print(f"✗ Error loading input file: {e}")
        return

    results = []
    os.makedirs("output", exist_ok=True)
    
    print("\n🚀 Starting extraction...")
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        data, error = get_ytdlp_data(url)
        
        entry = {
            'url': url,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Failed',
            'views': 0,
            'likes': 0,
            'comments': 0,
            'username': '',
            'upload_date': '',
            'title': '',
            'error': ''
        }
        
        if data:
            entry['status'] = 'Success'
            entry['views'] = data.get('view_count', 0)
            entry['likes'] = data.get('like_count', 0)
            entry['comments'] = data.get('comment_count', 0)
            entry['username'] = data.get('uploader', '')
            entry['upload_date'] = data.get('upload_date', '')
            entry['title'] = data.get('title', '')
            
            print(f"  ✅ Success! Views: {entry['views']:,} | Likes: {entry['likes']:,} | User: {entry['username']}")
        else:
            entry['error'] = error
            print(f"  ❌ Failed: {error[:100]}...")
            
        results.append(entry)
        
        # Save every 10
        if i % 10 == 0:
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            print(f"  💾 Saved progress to {OUTPUT_FILE}")
            
        # Small delay to be polite
        time.sleep(random.uniform(1, 2))

    # Final Save
    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Done! All results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
