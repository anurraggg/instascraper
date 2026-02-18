"""
Instagram Scraper - Simple & Reliable
Uses meta tags + aria-labels for maximum reliability
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import random
from pathlib import Path

def extract_number(text):
    """Extract number from text (e.g. '1.2M' -> 1200000)."""
    if not text:
        return 0
    
    text = str(text).strip().upper().replace(',', '')
    multiplier = 1
    
    if 'K' in text:
        multiplier = 1000
        text = text.replace('K', '')
    elif 'M' in text:
        multiplier = 1000000
        text = text.replace('M', '')
    elif 'B' in text:
        multiplier = 1000000000
        text = text.replace('B', '')
    
    match = re.search(r'[\d.]+', text)
    if match:
        try:
            return int(float(match.group()) * multiplier)
        except:
            return 0
    return 0

def main():
    print("\n" + "="*60)
    print("INSTAGRAM SCRAPER - SIMPLE & RELIABLE")
    print("Uses Meta Tags + Aria-Labels")
    print("="*60)

    # Load URLs
    try:
        df = pd.read_excel('input/redourls.xlsx')
        urls = df['URL'].dropna().tolist()
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"\n✓ Loaded {len(urls)} URLs")
    except Exception as e:
        print(f"✗ Error loading URLs: {e}")
        return

    # Setup Chrome
    print("\n🚀 Starting Chrome...")
    options = Options()
    options.add_argument('--log-level=3')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    print("✅ Chrome ready")

    # Login
    print("\n🔐 Please log in to Instagram manually in the browser...")
    driver.get("https://www.instagram.com/")
    print("👉 Log in to Instagram in the browser window")
    print("👉 After logging in, press ENTER here to continue...")
    input()

    print("\n✅ Starting scraping...")

    # Scrape
    results = []
    Path('output').mkdir(exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"SCRAPING {len(urls)} URLS")
    print(f"{'='*60}\n")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url[:60]}...")
        
        username = ''
        followers = 0
        following = 0
        likes = 0
        comments = 0
        views = 0
        
        try:
            driver.get(url)
            time.sleep(random.uniform(5, 7))
            
            # Get page text for fallback
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # 1. Get Username from Title
            try:
                title = driver.title
                if '(@' in title and ')' in title:
                    username = title.split('(@')[1].split(')')[0]
                elif 'on Instagram' in title:
                    username = title.split('on Instagram')[0].strip().replace('"', '').split(' ')[0]
                print(f"  👤 Username: {username}")
            except:
                pass
            
            # 2. Try to get data from aria-labels (most reliable for post stats)
            try:
                aria_elements = driver.find_elements(By.XPATH, "//*[@aria-label]")
                for elem in aria_elements:
                    label = elem.get_attribute("aria-label")
                    if not label:
                        continue
                    
                    # Likes
                    if likes == 0:
                        like_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes?', label, re.I)
                        if like_match:
                            likes = extract_number(like_match.group(1))
                    
                    # Comments
                    if comments == 0:
                        comment_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments?', label, re.I)
                        if comment_match:
                            comments = extract_number(comment_match.group(1))
                    
                    # Views/Plays
                    if views == 0:
                        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:views?|plays?)', label, re.I)
                        if views_match:
                            views = extract_number(views_match.group(1))
            except Exception as e:
                print(f"  ⚠ Aria extraction error: {e}")
            
            # 3. Fallback to page text for post stats
            if likes == 0:
                like_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes?', page_text, re.I)
                if like_match:
                    likes = extract_number(like_match.group(1))
            
            if comments == 0:
                comment_match = re.search(r'(?:View all\s+)?(\d[\d,\.]*[KMB]?)\s*comments?', page_text, re.I)
                if comment_match:
                    comments = extract_number(comment_match.group(1))
            
            if views == 0:
                views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:views?|plays?)', page_text, re.I)
                if views_match:
                    views = extract_number(views_match.group(1))
            
            # 4. Get Profile Stats (navigate if we have username)
            if username:
                try:
                    # Open in new tab to preserve main tab
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    
                    driver.get(f"https://www.instagram.com/{username}/")
                    time.sleep(random.uniform(3, 4))
                    
                    # Try meta description first (most reliable)
                    try:
                        meta_desc = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
                        if meta_desc:
                            f_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', meta_desc, re.I)
                            if f_match:
                                followers = extract_number(f_match.group(1))
                            
                            fol_match = re.search(r'([\d,\.]+[KMB]?)\s+Following', meta_desc, re.I)
                            if fol_match:
                                following = extract_number(fol_match.group(1))
                    except:
                        pass
                    
                    # Fallback: page text
                    if followers == 0:
                        profile_text = driver.find_element(By.TAG_NAME, "body").text
                        f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', profile_text, re.I)
                        if f_match:
                            followers = extract_number(f_match.group(1))
                        
                        fol_match = re.search(r'([\d,\.]+[KMB]?)\s+following', profile_text, re.I)
                        if fol_match:
                            following = extract_number(fol_match.group(1))
                    
                    # Close tab and return to main
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                    print(f"  ✓ Profile: {followers:,} Followers | {following:,} Following")
                except Exception as e:
                    print(f"  ⚠ Profile lookup error: {e}")
                    try:
                        # Try to close tab and return
                        if len(driver.window_handles) > 1:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                    except:
                        pass
            
            print(f"  ✓ Post: {likes:,} Likes | {comments:,} Comments | {views:,} Views")
            
            status = 'Success' if (likes > 0 or views > 0 or followers > 0) else 'No Data'
            
            results.append({
                'url': url,
                'username': username,
                'followers': followers,
                'following': following,
                'likes': likes,
                'comments': comments,
                'views': views,
                'status': status,
                'error': ''
            })
            
        except Exception as e:
            error_msg = str(e)
            if "invalid session id" in error_msg or "no such window" in error_msg:
                print(f"\n🛑 CRITICAL ERROR: Browser session lost. Exiting...")
                break
                
            results.append({
                'url': url,
                'username': username,
                'followers': followers,
                'following': following,
                'likes': likes,
                'comments': comments,
                'views': views,
                'status': 'Error',
                'error': error_msg
            })
            print(f"  ✗ Error: {e}")
        
        # Save incrementally every 10 URLs
        if i % 10 == 0 or i == len(urls):
            df_results = pd.DataFrame(results)
            df_results.to_excel('output/instagram_simple.xlsx', index=False, engine='openpyxl')
            print(f"  💾 Saved progress ({i}/{len(urls)})")
        
        if i < len(urls):
            time.sleep(random.uniform(3, 5))

    driver.quit()

    # Final Save
    df_results = pd.DataFrame(results)
    df_results.to_excel('output/instagram_simple.xlsx', index=False, engine='openpyxl')
    print(f"\n✅ Saved to: output/instagram_simple.xlsx")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r['status'] == 'Success')
    print(f"Total: {len(results)} | Success: {successful} | Failed: {len(results)-successful}")
    print(f"Total Likes: {sum(r['likes'] for r in results):,}")
    print(f"Total Comments: {sum(r['comments'] for r in results):,}")
    print(f"Total Views: {sum(r['views'] for r in results):,}")
    print("="*60)

if __name__ == "__main__":
    main()
