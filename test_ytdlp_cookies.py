import subprocess
import json
import shutil
import os

TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def test_ytdlp_cookies():
    print(f"Testing yt-dlp with cookies on {TARGET_URL}...")
    
    if not os.path.exists("cookies.txt"):
        print("❌ cookies.txt not found")
        return

    try:
        # Run yt-dlp with cookies
        cmd = ["yt-dlp", "--dump-json", "--no-warnings", "--cookies", "cookies.txt", TARGET_URL]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"❌ yt-dlp failed: {result.stderr}")
            return

        data = json.loads(result.stdout)
        
        print("\n--- Extracted Data (With Cookies) ---")
        print(f"view_count: {data.get('view_count')}")
        print(f"like_count: {data.get('like_count')}")
        
        # Check for other keys
        for k, v in data.items():
            if 'view' in k or 'play' in k:
                print(f"{k}: {v}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ytdlp_cookies()
