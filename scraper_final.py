"""
FINAL Instagram Scraper - Most Reliable Method
Uses instaloader with proper session management and rate limiting
"""

import instaloader
import pandas as pd
import re
import time
import os
from pathlib import Path


def extract_shortcode(url):
    """Extract shortcode from Instagram URL."""
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None


def main():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - FINAL VERSION")
    print("="*60)
    
    # Load URLs
    try:
        df = pd.read_csv('input/Instagram_URLS.csv')
        urls = df.iloc[:, 0].dropna().tolist()[1:]
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"\n✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return
    
    # Initialize Instaloader with settings to avoid rate limiting
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        max_connection_attempts=3
    )
    
    # Login
    session_file = Path("instagram_session")
    
    if session_file.exists():
        print("\n✓ Found saved session, loading...")
        try:
            L.load_session_from_file(os.environ.get("IG_USERNAME", ""), session_file)
            print("✅ Session loaded successfully!")
        except Exception as e:
            print(f"⚠ Could not load session: {e}")
            print("Will try to login...")
            session_file = None
    
    if not session_file or not session_file.exists():
        print("\n🔐 Logging in to Instagram...")
        ig_user = os.environ.get("IG_USERNAME", "")
        ig_pass = os.environ.get("IG_PASSWORD", "")
        print(f"Username: {ig_user}")
        
        try:
            L.login(ig_user, ig_pass)
            L.save_session_to_file(session_file)
            print("✅ Login successful! Session saved for future use.")
        except instaloader.exceptions.BadCredentialsException:
            print("✗ Login failed: Bad credentials")
            print("\n⚠ Instagram may be blocking login attempts.")
            print("Please try one of these:")
            print("1. Log in to Instagram on your browser first")
            print("2. Wait a few minutes and try again")
            print("3. Check if your account has 2FA enabled")
            return
        except instaloader.exceptions.ConnectionException as e:
            print(f"✗ Connection error: {e}")
            return
        except Exception as e:
            print(f"✗ Login error: {e}")
            return
    
    # Scrape each URL
    results = []
    
    print(f"\n{'='*60}")
    print(f"SCRAPING {len(urls)} URLS")
    print(f"{'='*60}\n")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        
        shortcode = extract_shortcode(url)
        if not shortcode:
            print(f"  ✗ Invalid URL")
            results.append({
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Invalid URL',
                'error': 'Could not extract shortcode'
            })
            continue
        
        try:
            # Get post
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Extract data
            likes = post.likes
            comments = post.comments
            views = post.video_view_count if post.is_video else 0
            
            # Get collaborators
            collaborators = []
            try:
                for tag in post.tagged_users:
                    collaborators.append(tag.username)
            except:
                pass
            
            collab_str = ', '.join(collaborators) if collaborators else ''
            
            print(f"  ✓ Likes: {likes:,} | Comments: {comments:,} | Views: {views:,}")
            if collab_str:
                print(f"  ✓ Collaborators: {collab_str}")
            
            results.append({
                'url': url,
                'likes': likes,
                'comments': comments,
                'views': views,
                'collaborators': collab_str,
                'status': 'Success',
                'error': ''
            })
            
            # Rate limiting - wait between requests
            if i < len(urls):
                wait_time = 2
                print(f"  ⏳ Waiting {wait_time}s...")
                time.sleep(wait_time)
            
        except instaloader.exceptions.QueryReturnedNotFoundException:
            print(f"  ✗ Post not found")
            results.append({
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Not Found',
                'error': 'Post not found'
            })
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Error: {error_msg}")
            results.append({
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Error',
                'error': error_msg
            })
    
    # Save results
    Path('output').mkdir(exist_ok=True)
    df_results = pd.DataFrame(results)
    df_results.to_excel('output/instagram_data.xlsx', index=False, engine='openpyxl')
    print(f"\n✅ Results saved to: output/instagram_data.xlsx")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r['status'] == 'Success')
    print(f"Total URLs processed: {len(results)}")
    print(f"Successful: {successful}/{len(results)}")
    print(f"Failed: {len(results) - successful}")
    print(f"\nTotal Likes: {sum(r['likes'] for r in results):,}")
    print(f"Total Comments: {sum(r['comments'] for r in results):,}")
    print(f"Total Views: {sum(r['views'] for r in results):,}")
    print("="*60)
    
    if successful > 0:
        print("\n✅ SUCCESS! The scraper is working!")
        print(f"📊 You can now process all 462 URLs by adding them to the CSV file.")
    else:
        print("\n⚠ No data was scraped. Instagram may be blocking access.")
        print("This is a known issue with Instagram's API restrictions.")


if __name__ == "__main__":
    main()
