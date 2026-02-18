import requests
import pickle
import json
import time
import random

# Configuration
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"
API_URL = TARGET_URL.rstrip("/") + "/?__a=1&__d=dis"
COOKIES_FILE = "cookies.pkl"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def debug_requests():
    print(f"\n🚀 Testing Direct API Request: {API_URL}")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    
    # Load Cookies
    try:
        with open(COOKIES_FILE, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                # Requests expects simple dict or cookiejar
                # Selenium cookies have 'domain', 'path', etc.
                # We need to filter for relevant fields or just add them all
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
        print(f"  ✅ Loaded {len(cookies)} cookies from {COOKIES_FILE}")
    except Exception as e:
        print(f"  ❌ Error loading cookies: {e}")
        return

    # Make Request to Public Page
    try:
        print(f"  Sending request to {TARGET_URL}...")
        response = session.get(TARGET_URL, allow_redirects=True)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✅ Page Loaded!")
            html = response.text
            
            # Search for view count
            import re
            
            # 1. Search for "video_view_count":1234
            m = re.search(r'"video_view_count":(\d+)', html)
            if m:
                print(f"  ✅ Found View Count (JSON): {m.group(1)}")
            else:
                print("  ❌ 'video_view_count' not found in HTML.")
                
            # 2. Search for "play_count":1234
            m = re.search(r'"play_count":(\d+)', html)
            if m:
                print(f"  ✅ Found Play Count (JSON): {m.group(1)}")
                
            # 3. Search for text "7,550 views" etc (Ground Truth)
            if "7550" in html or "7551" in html:
                print("  ✅ Ground Truth (7550/7551) found in HTML!")
            else:
                print("  ❌ Ground Truth not found.")
                
            # Save for inspection
            with open("debug_requests.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("  💾 Saved debug_requests.html")
            
        else:
            print("  ❌ Request failed.")
            
    except Exception as e:
        print(f"  ❌ Request Error: {e}")

if __name__ == "__main__":
    debug_requests()
