import instaloader
import re

TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def extract_shortcode(url):
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def test_instaloader():
    print(f"Testing Instaloader on {TARGET_URL}...")
    
    L = instaloader.Instaloader()
    
    shortcode = extract_shortcode(TARGET_URL)
    if not shortcode:
        print("❌ Invalid URL")
        return

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"✅ Post Loaded!")
        print(f"  Type: {'Video' if post.is_video else 'Image'}")
        print(f"  Views: {post.video_view_count}")
        print(f"  Likes: {post.likes}")
        print(f"  Comments: {post.comments}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_instaloader()
