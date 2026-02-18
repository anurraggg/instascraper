import instaloader
import os
import re

# Configuration — set IG_USERNAME as an environment variable
USERNAME = os.environ.get("IG_USERNAME", "")
SESSION_FILE = "instagram_session"
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def extract_shortcode(url):
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def debug_session():
    print(f"\n🚀 Testing Session File: {SESSION_FILE}")
    
    if not os.path.exists(SESSION_FILE):
        print("  ❌ Session file not found!")
        return

    L = instaloader.Instaloader()
    
    try:
        print(f"  Loading session for {USERNAME}...")
        L.load_session_from_file(USERNAME, filename=SESSION_FILE)
        print("  ✅ Session loaded!")
    except Exception as e:
        print(f"  ❌ Failed to load session: {e}")
        return

    shortcode = extract_shortcode(TARGET_URL)
    print(f"  Fetching Post: {shortcode}")
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"  ✅ Success!")
        print(f"  Views: {post.video_view_count}")
        print(f"  Likes: {post.likes}")
        print(f"  Owner: {post.owner_username}")
    except Exception as e:
        print(f"  ❌ Error fetching post: {e}")

if __name__ == "__main__":
    debug_session()
