"""
Instagram Scraper using Instaloader
Extracts: Username, Followers, Following, Collaborators, Likes, Comments, Views
"""

import instaloader
import pandas as pd
import re
import time
import random
from pathlib import Path
import os

def extract_shortcode(url):
    """Extract shortcode from Instagram URL."""
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None

def scrape_with_instaloader():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - INSTALOADER METHOD")
    print("Target: Profile Stats (Followers/Following) & Post Stats")
    print("="*60)
    
    # Load URLs
    # Load URLs
    try:
        # Read the no-header file we prepared
        df = pd.read_excel('input/INSTAURL.xlsx', header=None)
        urls = df.iloc[:, 0].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"\n✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return
    
    # Initialize Instaloader
    L = instaloader.Instaloader()
    
    # LOGIN / SESSION MANAGEMENT
    print("\n" + "="*60)
    print("LOGIN (Required for Profile Stats)")
    print("="*60)
    
    session_file = None
    # Check for existing session files
    files = [f for f in os.listdir('.') if f.startswith('session-')]
    if files:
        print(f"Found existing session: {files[0]}")
        use_saved = input("Use this session? (y/n): ").lower()
        if use_saved == 'y':
            session_file = files[0]
            try:
                L.load_session_from_file(session_file.replace('session-', ''))
                print("✅ Session loaded!")
            except Exception as e:
                print(f"⚠ Could not load session: {e}")
                session_file = None

    if not session_file:
        username = input("Enter Instagram username: ").strip()
        if username:
            try:
                L.interactive_login(username)
                L.save_session_to_file()
                print("✅ Login successful & Session saved!")
            except Exception as e:
                print(f"✗ Login failed: {e}")
                cont = input("Continue without login? (y/n): ").lower()
                if cont != 'y':
                    return
                print("⚠ Continuing without login (Rate limits may be stricter)")

        else:
            print("⚠ No username provided. Scraper will likely fail on profiles.")
            
    # Scrape
    results = []
    Path('output').mkdir(exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
        
        shortcode = extract_shortcode(url)
        if not shortcode:
            print(f"  ✗ Invalid URL format")
            continue
            
        try:
            # Get Post
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Get Profile
            profile = post.owner_profile
            username = profile.username
            followers = profile.followers
            following = profile.followees
            
            # Get Post Stats
            likes = post.likes
            comments = post.comments
            views = post.video_view_count if post.is_video else 0
            
            # Collaborators
            collaborators = []
            for tag in post.tagged_users:
                collaborators.append(tag.username)
            collab_str = ', '.join(collaborators)
            
            print(f"  👤 User: {username}")
            print(f"  ✓ Stats: {followers:,} Followers | {following:,} Following")
            print(f"  ✓ Post: {likes:,} Likes | {views:,} Views")
            
            results.append({
                'Original_URL': url,
                'Username': username,
                'Followers': followers,
                'Following': following,
                'Likes': likes,
                'Comments': comments,
                'Views': views,
                'Collaborators': collab_str,
                'Status': 'Success',
                'Error': ''
            })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'Original_URL': url,
                'Username': '',
                'Followers': 0,
                'Following': 0,
                'Likes': 0,
                'Comments': 0,
                'Views': 0,
                'Collaborators': '',
                'Status': 'Error',
                'Error': str(e)
            })
            
        # Rate Limit Delay
        time.sleep(random.uniform(10, 15))
        
        # Save incrementally
        if i % 5 == 0:
            pd.DataFrame(results).to_excel('output/instagram_instaloader.xlsx', index=False)
            print("  💾 Saved progress")

    # Final Save
    pd.DataFrame(results).to_excel('output/instagram_instaloader.xlsx', index=False)
    print(f"\n✅ Done! Saved to output/instagram_instaloader.xlsx")

if __name__ == "__main__":
    scrape_with_instaloader()
