"""
Instagram Scraper using Instaloader with Session Import
This allows you to log in via browser and import the session
"""

import instaloader
import pandas as pd
import re
from pathlib import Path
import browser_cookie3


def extract_shortcode(url):
    """Extract shortcode from Instagram URL."""
    match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if match:
        return match.group(2)
    return None


def scrape_with_session():
    """Scrape Instagram posts using browser session."""
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - SESSION IMPORT METHOD")
    print("="*60)
    print("\nThis method uses your browser's Instagram session.")
    print("Make sure you're logged into Instagram in your browser!\n")
    
    # Load URLs
    try:
        df = pd.read_csv('input/Instagram_URLS.csv')
        urls = df.iloc[:, 0].dropna().tolist()[1:]
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return
    
    # Initialize Instaloader
    L = instaloader.Instaloader()
    
    # Try to import session from browser
    print("\n🔍 Attempting to import session from browser...")
    print("Trying Chrome first...")
    
    try:
        # Try Chrome
        cookies = browser_cookie3.chrome(domain_name='instagram.com')
        L.context._session.cookies.update(cookies)
        print("✅ Successfully imported session from Chrome!")
    except:
        try:
            # Try Firefox
            print("Chrome failed, trying Firefox...")
            cookies = browser_cookie3.firefox(domain_name='instagram.com')
            L.context._session.cookies.update(cookies)
            print("✅ Successfully imported session from Firefox!")
        except:
            try:
                # Try Edge
                print("Firefox failed, trying Edge...")
                cookies = browser_cookie3.edge(domain_name='instagram.com')
                L.context._session.cookies.update(cookies)
                print("✅ Successfully imported session from Edge!")
            except Exception as e:
                print(f"⚠ Could not import session from any browser: {e}")
                print("Please make sure you're logged into Instagram in your browser!")
                return
    
    # Test if session works
    print("\n🧪 Testing session...")
    try:
        # Try to get a test post
        test_post = instaloader.Post.from_shortcode(L.context, "C_8DhzNP8Zv")  # Random public post
        print("✅ Session is working!")
    except Exception as e:
        print(f"⚠ Session test failed: {e}")
        print("Continuing anyway...")
    
    # Scrape each URL
    results = []
    
    print(f"\n{'='*60}")
    print("STARTING SCRAPING")
    print(f"{'='*60}\n")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")
        
        shortcode = extract_shortcode(url)
        if not shortcode:
            print(f"✗ Could not extract shortcode from URL")
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
            # Get post by shortcode
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Extract data
            likes = post.likes
            comments = post.comments
            views = post.video_view_count if post.is_video else 0
            
            # Get collaborators (tagged users)
            collaborators = []
            try:
                for tag in post.tagged_users:
                    collaborators.append(tag.username)
            except:
                pass
            
            collab_str = ', '.join(collaborators) if collaborators else ''
            
            print(f"  ✓ Likes: {likes:,}")
            print(f"  ✓ Comments: {comments:,}")
            if views > 0:
                print(f"  ✓ Views: {views:,}")
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
            
        except instaloader.exceptions.LoginRequiredException:
            print("  ⚠ Login required for this post")
            results.append({
                'url': url,
                'likes': 0,
                'comments': 0,
                'views': 0,
                'collaborators': '',
                'status': 'Login Required',
                'error': 'Login required'
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
    print(f"\n✓ Results saved to: output/instagram_data.xlsx")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total URLs processed: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'Success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] != 'Success')}")
    print(f"\nTotal Likes: {sum(r['likes'] for r in results):,}")
    print(f"Total Comments: {sum(r['comments'] for r in results):,}")
    print(f"Total Views: {sum(r['views'] for r in results):,}")
    print("="*60)


if __name__ == "__main__":
    scrape_with_session()
