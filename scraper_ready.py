"""
Instagram Scraper - FINAL WORKING VERSION
Ready for 462 URLs - Fully Automated
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import random
from pathlib import Path


def extract_number(text):
    """Extract number from text."""
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


def is_valid_username(username):
    if not username:
        return False
    ignored = ['home', 'explore', 'reels', 'direct', 'accounts', 'create', 'profile', 'stories', 'instagram', 'search', 'notifications', 'more', 'settings', 'messages']
    return username.lower() not in ignored and len(username) > 1


print("\n" + "="*60)
print("INSTAGRAM SCRAPER - READY FOR 462 URLS")
print("="*60)

# Load URLs
try:
    df = pd.read_excel('input/redourls.xlsx')
    urls = df['URL'].dropna().tolist()
    urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
    print(f"\n✓ Loaded {len(urls)} URLs")
except Exception as e:
    print(f"✗ Error: {e}")
    exit()

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
print(f"\n{'='*60}")
print(f"SCRAPING {len(urls)} URLS")
print(f"{'='*60}\n")

for i, url in enumerate(urls, 1):
    print(f"[{i}/{len(urls)}] {url[:50]}...")
    
    # RESUME LOGIC: Skip if already scraped AND valid (size > 500 bytes)
    log_filename = f"logs/url_{i}.txt"
    if Path(log_filename).exists():
        if Path(log_filename).stat().st_size > 500:
            print(f"  ✓ Already scraped (found {log_filename}). Skipping...")
            try:
                # Load existing data
                json_filename = f"logs/url_{i}_result.json"
                if Path(json_filename).exists():
                    import json
                    with open(json_filename, "r", encoding="utf-8") as f:
                        existing_result = json.load(f)
                        results.append(existing_result)
            except Exception as e:
                print(f"  ⚠ Could not load existing result: {e}")
            continue
        else:
            print(f"  ⚠ Found invalid log (size < 500b). Re-scraping...")

    try:
        driver.get(url)
        time.sleep(random.uniform(8, 12))
        
        # Check for 429 Rate Limit
        page_source = driver.page_source
        if "HTTP ERROR 429" in page_source or "This page isn’t working" in page_source:
            print(f"  🛑 HIT RATE LIMIT (429).")
            print("  👉 Please switch network or wait.")
            print("  👉 Press ENTER here when ready to retry...")
            input()
            driver.refresh()
            time.sleep(10)
        
        # --- PROFILE STATS (Followers/Following) ---
        followers = 0
        following = 0
        try:
            # Check if we are on a profile page (not a specific post)
            # Or if the page contains profile stats
            page_text_full = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for "X followers" and "Y following"
            # This works on both desktop and mobile views usually
            f_match = re.search(r'([\d,\.]+[KMB]?)\s+followers', page_text_full, re.I)
            if f_match:
                followers = extract_number(f_match.group(1))
                
            fol_match = re.search(r'([\d,\.]+[KMB]?)\s+following', page_text_full, re.I)
            if fol_match:
                following = extract_number(fol_match.group(1))
                
            if followers > 0 or following > 0:
                print(f"  ✓ Found Profile Stats: {followers:,} Followers | {following:,} Following")
        except Exception as e:
            pass # Ignore errors here, focus on main task
        
        # Scroll
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 400)")
            time.sleep(1)
        
        # Get text
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        # SAVE RAW TEXT LOG
        try:
            Path('logs').mkdir(exist_ok=True)
            log_filename = f"logs/url_{i}.txt"
            with open(log_filename, "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\n\n")
                f.write("--- TEXT CONTENT ---\n")
                f.write(page_text)
                f.write("\n\n--- ARIA LABELS ---\n")
                
                # Extract all aria-labels to find hidden data
                elements = driver.find_elements(By.XPATH, "//*[@aria-label]")
                for elem in elements:
                    label = elem.get_attribute("aria-label")
                    f.write(f"{label}\n")
                    
                    # Check if this label contains "plays" or "views"
                    if 'play' in label.lower() or 'view' in label.lower():
                        # Try to extract number
                        match = re.search(r'(\d[\d,\.]*[KMB]?)\s*(?:plays?|views?)', label, re.I)
                        if match:
                            views = extract_number(match.group(1))
                            
            print(f"  ✓ Saved raw text & aria-labels to {log_filename}")
            
            # SAVE JSON DATA (Nuclear Option)
            try:
                json_data = driver.execute_script("""
                    return {
                        sharedData: window._sharedData,
                        additionalData: window.__additionalData,
                        graphql: window.__graphql
                    };
                """)
                import json
                json_filename = f"logs/url_{i}_data.json"
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, default=str)
                print(f"  ✓ Saved JSON data to {json_filename}")
            except Exception as e:
                print(f"  ⚠ Could not save JSON data: {e}")
                
        except Exception as e:
            print(f"  ⚠ Could not save log: {e}")
        
        # Extract
        likes = 0
        comments = 0
        views = 0
        collaborators = ''
        
        # Likes - Try multiple patterns
        # 1. "498 likes"
        likes_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*likes', page_text, re.I)
        
        # 2. "Liked by user and 498 others"
        if not likes_match:
            likes_match = re.search(r'and\s+(\d[\d,\.]*[KMB]?)\s+others', page_text, re.I)
            
        # 3. "Liked by 498 people"
        if not likes_match:
            likes_match = re.search(r'Liked by\s+[^\n]+\s+and\s+(\d[\d,\.]*[KMB]?)', page_text, re.I)
            
        if likes_match:
            likes = extract_number(likes_match.group(1))
        
        # Comments
        comments_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*comments', page_text, re.I)
        if not comments_match:
            comments_match = re.search(r'View all (\d[\d,\.]*[KMB]?)\s*comments', page_text, re.I)
        if comments_match:
            comments = extract_number(comments_match.group(1))
        
        # Views
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*views', page_text, re.I)
        if not views_match:
            views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', page_text, re.I)
        if views_match:
            views = extract_number(views_match.group(1))
            
        # --- FALLBACK PARSER (For Reels with no labels) ---
        if likes == 0 and comments == 0:
            lines = page_text.split('\n')
            for idx, line in enumerate(lines):
                line = line.strip()
                
                # Case A: "Likes" \n "9"
                if line.lower() == 'likes' and idx + 1 < len(lines):
                    next_line = lines[idx+1].strip()
                    if re.match(r'^[\d,\.]+[KMB]?$', next_line):
                        likes = extract_number(next_line)
                        break  # STOP after finding first match
                        
                # Case B: "... more" \n "498" \n "17" (Reel format)
                if '… more' in line and idx + 1 < len(lines):
                    # Check next line for Likes
                    next_line = lines[idx+1].strip()
                    if re.match(r'^[\d,\.]+[KMB]?$', next_line):
                        likes = extract_number(next_line)
                        
                        # Check line after for Comments
                        if idx + 2 < len(lines):
                            next_next_line = lines[idx+2].strip()
                            if re.match(r'^[\d,\.]+[KMB]?$', next_next_line):
                                comments = extract_number(next_next_line)
                        
                        break  # STOP after finding first match
                        
        # --- PROFILE LOOKUP (Reliable View Count) ---
        if views == 0:
            try:
                print("  🕵️ Going to profile page for views...")
                


# ... inside the loop ...

                # Extract username
                username = ''
                
                # Strategy 1: Look for username in the Post/Reel header (most reliable)
                if not username:
                    try:
                        article_user_links = driver.find_elements(By.XPATH, "//article//header//a")
                        for link in article_user_links:
                            href = link.get_attribute("href")
                            if href:
                                candidate = href.strip('/').split('/')[-1]
                                if is_valid_username(candidate):
                                    username = candidate
                                    print(f"  ✓ Found username (Strategy 1 - Article): {username}")
                                    break
                    except:
                        pass

                # Strategy 2: Header link (Fallback)
                if not username:
                    try:
                        header_links = driver.find_elements(By.XPATH, "//header//a[contains(@href, '/')]")
                        for link in header_links:
                            candidate = link.get_attribute("href").strip('/').split('/')[-1]
                            if is_valid_username(candidate):
                                username = candidate
                                print(f"  ✓ Found username (Strategy 2 - Header): {username}")
                                break
                    except:
                        pass
                
                # Strategy 3: Regex with newlines (Profile view)
                if not username:
                    user_match = re.search(r'([a-zA-Z0-9._]+)\s*\n\s*•\s*\n\s*Follow', page_text)
                    if user_match:
                        candidate = user_match.group(1)
                        if is_valid_username(candidate):
                            username = candidate
                            print(f"  ✓ Found username (Strategy 3 - Regex): {username}")
                        
                # Strategy 4: Page Title
                if not username:
                    title = driver.title
                    if 'on Instagram' in title:
                        candidate = title.split('on Instagram')[0].strip().split(' ')[0]
                        if is_valid_username(candidate):
                            username = candidate
                            print(f"  ✓ Found username (Strategy 4 - Title): {username}")
                        
                # Strategy 5: First line of text
                if not username:
                    lines = page_text.split('\n')
                    if lines:
                        for line in lines[:5]: # Check first 5 lines
                            candidate = line.strip()
                            if ' ' not in candidate and len(candidate) > 2 and is_valid_username(candidate):
                                username = candidate
                                print(f"  ✓ Found username (Strategy 5 - Text): {username}")
                                break

                # Strategy 6: Search all links in main (Broad Search)
                if not username:
                    try:
                        print("  🔍 specific headers failed, searching all main links...")
                        all_links = driver.find_elements(By.XPATH, "//main//a")
                        for link in all_links[:20]: # Check first 20 links in main
                            href = link.get_attribute("href")
                            if href and '/p/' not in href and '/reel/' not in href:
                                candidate = href.strip('/').split('/')[-1]
                                if is_valid_username(candidate):
                                    username = candidate
                                    print(f"  ✓ Found username (Strategy 6 - Broad Link): {username}")
                                    break
                    except Exception as e:
                        print(f"  ⚠ Strategy 6 failed: {e}")
                
                if username:
                    print(f"  👤 Username: {username}")
                    
                    # Open new tab
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Go to Reels tab
                    driver.get(f"https://www.instagram.com/{username}/reels/")
                    time.sleep(6)
                    
                    # Scroll down a bit to ensure recent reels are loaded
                    driver.execute_script("window.scrollBy(0, 500)")
                    time.sleep(2)
                    
                    # Find the specific Reel
                    shortcode = ''
                    if '/reel/' in url:
                        shortcode = url.split('/reel/')[-1].split('/')[0].split('?')[0]
                    elif '/p/' in url:
                        shortcode = url.split('/p/')[-1].split('/')[0].split('?')[0]
                    elif '/share/reel/' in url:
                        shortcode = url.split('/share/reel/')[-1].split('/')[0].split('?')[0]
                    elif '/share/' in url:
                        # Could be /share/SHORTCODE or /share/reel/SHORTCODE
                        shortcode = url.split('/share/')[-1].split('/')[0].split('?')[0]
                    
                    if len(shortcode) < 5: # Safety check
                        print(f"  ⚠ Invalid shortcode extracted: {shortcode}")
                        continue
                        
                    print(f"  🔍 Looking for shortcode: {shortcode}")
                         
                    # Scroll and Search Loop
                    found_reel = False
                    for scroll_attempt in range(100): # Scroll up to 100 times (User requested more scrolling)
                        try:
                            # Look for the link containing the shortcode
                            reel_link = driver.find_elements(By.XPATH, f"//a[contains(@href, '{shortcode}')]")
                            
                            if reel_link:
                                print("  ✓ Found reel link on profile")
                                container = reel_link[0]
                                
                                # Method 1: direct text
                                container_text = container.text
                                print(f"  📄 Text: {container_text.replace(chr(10), ' ')}")
                                
                                # Method 2: innerHTML
                                inner_html = container.get_attribute("innerHTML")
                                
                                # Extract number
                                view_match = re.search(r'(\d[\d,\.]*[KMB]?)', container_text)
                                
                                if not view_match:
                                     view_match = re.search(r'>\s*(\d[\d,\.]*[KMB]?)\s*<', inner_html)
                                     
                                if view_match:
                                    views = extract_number(view_match.group(1))
                                    print(f"  ✓ Found views on profile: {views}")
                                    found_reel = True
                                    break # Stop scrolling
                            
                            # Scroll down if not found
                            driver.execute_script("window.scrollBy(0, 1000)")
                            time.sleep(1.5)
                            
                        except Exception as e:
                            print(f"  ⚠ Error during profile search: {e}")
                            break
                            
                    if not found_reel:
                        print(f"  ⚠ Reel link not found after scrolling")
                    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    print("  ⚠ Could not find username")
                
            except Exception as e:
                print(f"  ⚠ Profile lookup failed: {e}")
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass

        # Extract Data (Likes, Comments, Views)
        # CRITICAL: Only look within the specific Reel/Post container to avoid picking up "More like this" data
        
        # 1. Try to find the specific article/container first
        container = None
        try:
            # For Reels, it's often an article with a specific class or structure
            # For Posts, it's the main article
            container = driver.find_element(By.TAG_NAME, "article")
        except:
            pass
            
        if container:
            container_text = container.text
            container_html = container.get_attribute("innerHTML")
            print("  ✓ Found main article container")
        else:
            container_text = page_text # Fallback to full page (risky)
            container_html = driver.page_source
            print("  ⚠ Could not find main article, using full page text")

        # Likes
        likes = 0
        # Strategy 1: Aria-label on "Like" button (Most accurate)
        try:
            like_btns = driver.find_elements(By.XPATH, "//article//div[@role='button']//span[contains(@class, 'html-span')]")
            # This is tricky, often the number is just text.
            # Let's try looking for the specific "Like" or "Likes" text structure in the container
            
            # Regex on Container Text
            # 1. "Liked by user and 224 others"
            likes_match = re.search(r'and\s+(\d[\d,\.]*[KMB]?)\s+others', container_text, re.I)
            
            # 2. "224 likes"
            if not likes_match:
                likes_match = re.search(r'^(\d[\d,\.]*[KMB]?)\s*likes$', container_text, re.I | re.MULTILINE)
                
            if likes_match:
                likes = extract_number(likes_match.group(1))
        except:
            pass
            
        # Comments
        comments = 0
        comments_match = re.search(r'View all (\d[\d,\.]*[KMB]?)\s*comments', container_text, re.I)
        if not comments_match:
             comments_match = re.search(r'^(\d[\d,\.]*[KMB]?)\s*comments$', container_text, re.I | re.MULTILINE)
        if comments_match:
            comments = extract_number(comments_match.group(1))
            
        # Views (Reels)
        views = 0
        # Look for "Played by..." or just the number with "plays"
        views_match = re.search(r'(\d[\d,\.]*[KMB]?)\s*plays', container_text, re.I)
        if views_match:
            views = extract_number(views_match.group(1))

        # Collaborators - Look for "with user" or "and user"
        collab_match = re.search(r'with\s+@?([a-zA-Z0-9._]+)', container_text, re.I)
        if not collab_match:
             collab_match = re.search(r'and\s+@?([a-zA-Z0-9._]+)', container_text, re.I)
        if collab_match:
            collaborators = collab_match.group(1)
        
        status = 'Success' if (likes > 0 or comments > 0 or views > 0) else 'No Data'
        
        result = {
            'url': url,
            'likes': likes,
            'comments': comments,
            'views': views,
            'followers': followers,
            'following': following,
            'collaborators': collaborators,
            'status': status,
            'error': ''
        }
        
        print(f"  ✓ Likes: {likes:,} | Comments: {comments:,} | Views: {views:,}")
        if collaborators:
            print(f"  ✓ Collaborators: {collaborators}")
        
    except Exception as e:
        error_msg = str(e)
        if "invalid session id" in error_msg or "no such window" in error_msg:
            print(f"\n🛑 CRITICAL ERROR: Browser session lost (Closed/Crashed). Exiting...")
            break
            
        result = {
            'url': url,
            'likes': 0,
            'comments': 0,
            'views': 0,
            'followers': 0,
            'following': 0,
            'collaborators': '',
            'status': 'Error',
            'error': error_msg
        }
        print(f"  ✗ Error: {e}")
    
    # Save Result JSON
    try:
        import json
        result_filename = f"logs/url_{i}_result.json"
        with open(result_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
    except:
        pass

    results.append(result)
    
    if i < len(urls):
        time.sleep(random.uniform(5, 10))

driver.quit()

# Save
Path('output').mkdir(exist_ok=True)
df_results = pd.DataFrame(results)
df_results.to_excel('output/instagram_data.xlsx', index=False, engine='openpyxl')
print(f"\n✅ Saved to: output/instagram_data.xlsx")

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

if successful > 0:
    print("\n✅ SUCCESS! Scraper is working!")
    print("📊 Ready to process all 462 URLs!")
    print("\n💡 TIP: Add all 462 URLs to the CSV file and run again!")
