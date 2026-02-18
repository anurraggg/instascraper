from instascrape import Reel
import time

# Target URL
TARGET_URL = "https://www.instagram.com/reel/DM5F3Vzq6TN/"

def debug_instascrape():
    print(f"\n🚀 Testing instascrape: {TARGET_URL}")
    
    try:
        reel = Reel(TARGET_URL)
        print("  Scraping...")
        reel.scrape()
        
        print(f"  ✅ Success!")
        print(f"  Views: {reel.video_view_count}")
        print(f"  Likes: {reel.likes}")
        print(f"  Comments: {reel.comments}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    debug_instascrape()
