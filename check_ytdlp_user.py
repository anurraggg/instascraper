import subprocess
import json

def check_ytdlp_username():
    url = "https://www.instagram.com/reel/DM5F3Vzq6TN/"
    print(f"Checking {url}...")
    
    cmd = ["yt-dlp", "--dump-json", "--no-warnings", url]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode != 0:
        print("Error running yt-dlp")
        return

    try:
        data = json.loads(result.stdout)
        print(f"uploader: {data.get('uploader')}")
        print(f"uploader_id: {data.get('uploader_id')}")
        print(f"channel: {data.get('channel')}")
        print(f"channel_id: {data.get('channel_id')}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    check_ytdlp_username()
