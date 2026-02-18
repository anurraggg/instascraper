import pandas as pd
import subprocess
import json
import time
import re
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pickle
import argparse


# Configuration
INPUT_FILE = "input/redourls.xlsx"
OUTPUT_FILE = "output/instagram_media.xlsx"
SNAPSHOT_DIR = "output/snapshots"

if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

def get_ytdlp_metadata(url):
    """Get metadata using yt-dlp."""
    try:
        cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--skip-download", url]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"  ❌ yt-dlp error: {e}")
    return None

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"  ❌ Download error: {e}")
    return False

def setup_driver():
    options = Options()
    options.add_argument('--log-level=3')
    # options.add_argument('--headless=new') # Optional: Run headless if desired
    driver = webdriver.Chrome(options=options)
    return driver

def main(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    print("="*60)
    print("INSTAGRAM MEDIA SCRAPER")
    print("="*60)
    
    # Load URLs
    try:
        df = pd.read_excel(input_file)
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs from {input_file}")
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return

    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        media_url = ''
        snapshot_url = ''
        snapshot_path = ''
        status = 'Failed'
        error = ''
        
        # Extract shortcode for filename
        shortcode = ''
        if '/reel/' in url:
            shortcode = url.split('/reel/')[-1].split('/')[0]
        elif '/p/' in url:
            shortcode = url.split('/p/')[-1].split('/')[0]
        
        if not shortcode:
            shortcode = f"unknown_{i}"

        # 1. Try yt-dlp
        meta = get_ytdlp_metadata(url)
        if meta:
            # Get Media URL
            media_url = meta.get('url', '')
            if not media_url and 'formats' in meta:
                # Try to find best video format
                best_format = None
                for fmt in meta['formats']:
                    if fmt.get('vcodec') != 'none':
                        best_format = fmt
                if best_format:
                    media_url = best_format.get('url', '')
            
            # Get Snapshot URL
            snapshot_url = meta.get('thumbnail', '')
            
            if media_url:
                print(f"  ✓ Found Media URL")
            if snapshot_url:
                print(f"  ✓ Found Snapshot URL")
                
                # Download Snapshot
                local_filename = f"{shortcode}.jpg"
                local_path = os.path.join(SNAPSHOT_DIR, local_filename)
                if download_image(snapshot_url, local_path):
                    snapshot_path = local_path
                    print(f"  ✓ Saved Snapshot: {local_path}")
                else:
                    print(f"  ⚠️ Failed to download snapshot")

            status = 'Success'
        else:
            print("  ⚠️ yt-dlp failed. (Selenium fallback not implemented yet for simplicity, relying on yt-dlp strength)")
            error = "yt-dlp failed"

        results.append({
            'url': url,
            'shortcode': shortcode,
            'media_url': media_url,
            'snapshot_url': snapshot_url,
            'snapshot_path': snapshot_path,
            'status': status,
            'error': error
        })
        
        # Save every 5
        if i % 5 == 0:
            pd.DataFrame(results).to_excel(output_file, index=False)
            print(f"  💾 Saved progress to {output_file}")

    pd.DataFrame(results).to_excel(output_file, index=False)
    print(f"\n✅ Done! Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instagram Media Scraper")
    parser.add_argument("--input", default=INPUT_FILE, help="Path to input Excel file")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Path to output Excel file")
    args = parser.parse_args()
    
    main(input_file=args.input, output_file=args.output)
