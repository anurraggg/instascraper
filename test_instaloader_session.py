import instaloader
import re
import pickle
import os

TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def extract_shortcode(url):
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def test_instaloader_session():
    print(f"Testing Instaloader with Session on {TARGET_URL}...")
    
    L = instaloader.Instaloader()
    
    # Try to find the session object
    session = None
    if hasattr(L.context, 'session'):
        session = L.context.session
    elif hasattr(L.context, '_session'):
        session = L.context._session
    else:
        print("❌ Could not find session object in L.context")
        print(dir(L.context))
        return

    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        print(f"✅ Loaded {len(cookies)} cookies")
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return

    shortcode = extract_shortcode(TARGET_URL)
    if not shortcode:
        print("❌ Invalid URL")
        return

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        print(f"✅ Post Loaded!")
        print(f"  Views: {post.video_view_count}")
        print(f"  Likes: {post.likes}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_instaloader_session()
