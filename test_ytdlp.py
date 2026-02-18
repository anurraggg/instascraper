import subprocess
import json
import shutil

TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def test_ytdlp():
    print(f"Testing yt-dlp on {TARGET_URL}...")
    
    if not shutil.which("yt-dlp"):
        print("❌ yt-dlp not found in PATH")
        return

    try:
        # Run yt-dlp to dump JSON
        cmd = ["yt-dlp", "--dump-json", "--no-warnings", TARGET_URL]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"❌ yt-dlp failed: {result.stderr}")
            return

        data = json.loads(result.stdout)
        
        print("\n--- Extracted Data ---")
        print(f"view_count: {data.get('view_count')}")
        print(f"like_count: {data.get('like_count')}")
        print(f"comment_count: {data.get('comment_count')}")
        print(f"original_url: {data.get('original_url')}")
        
        print("\n--- All Keys containing 'count' ---")
        for k, v in data.items():
            if 'count' in k:
                print(f"{k}: {v}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ytdlp()
