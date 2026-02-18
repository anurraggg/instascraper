import instaloader
import re
import os

# Set IG_USERNAME and IG_PASSWORD as environment variables
USERNAME = os.environ.get("IG_USERNAME", "")
PASSWORD = os.environ.get("IG_PASSWORD", "")
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def extract_shortcode(url):
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def test_instaloader():
    print(f"Testing URL: {TARGET_URL}")
    shortcode = extract_shortcode(TARGET_URL)
    print(f"Shortcode: {shortcode}")
    
    L = instaloader.Instaloader()
    
    # 1. Try Anonymous
    print("\n--- Attempting Anonymous Access ---")
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"  ✅ Success!")
        print(f"  Views: {post.video_view_count}")
        print(f"  Likes: {post.likes}")
        return
    except Exception as e:
        print(f"  ✗ Anonymous failed: {e}")
        
    # 2. Try Login
    print("\n--- Attempting Login Access ---")
    try:
        L.login(USERNAME, PASSWORD)
        print("  ✅ Login successful!")
        
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"  ✅ Success!")
        print(f"  Views: {post.video_view_count}")
        print(f"  Likes: {post.likes}")
        
    except Exception as e:
        print(f"  ✗ Login failed: {e}")

if __name__ == "__main__":
    test_instaloader()
