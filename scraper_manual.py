# Instagram Manual Scraper
# This version lets you manually navigate while the script extracts data

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import pandas as pd
import re


def extract_number(text):
    """Extract number from text like '1.2K', '5M', '234'."""
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


def extract_data_from_page(page):
    """Extract data from current page."""
    try:
        result = page.evaluate("""
            (() => {
                const text = document.body.innerText;
                console.log("Page text length:", text.length);
                console.log("First 500 chars:", text.substring(0, 500));
                
                const likesMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*likes?/i);
                const commentsMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*comments?/i) || 
                                    text.match(/View all (\\d[\\d,\\.]*[KMB]?)\\s*comments?/i);
                const viewsMatch = text.match(/(\\d[\\d,\\.]*[KMB]?)\\s*views?/i);
                const collabMatch = text.match(/with\\s+@?([a-zA-Z0-9._]+)/i);
                
                console.log("Likes match:", likesMatch);
                console.log("Comments match:", commentsMatch);
                console.log("Views match:", viewsMatch);
                
                return {
                    likes: likesMatch ? likesMatch[1] : null,
                    comments: commentsMatch ? commentsMatch[1] : null,
                    views: viewsMatch ? viewsMatch[1] : null,
                    collaborator: collabMatch ? collabMatch[1] : null,
                    url: window.location.href
                };
            })()
        """)
        return result
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None


def main():
    print("\n" + "="*60)
    print("INSTAGRAM MANUAL SCRAPER")
    print("="*60)
    print("\nThis scraper lets YOU control the browser.")
    print("Navigate to each Instagram post/reel manually,")
    print("then press ENTER to extract the data.\n")
    
    # Load URLs
    try:
        df = pd.read_csv('input/Instagram_URLS.csv')
        urls = df.iloc[:, 0].dropna().tolist()[1:]
        urls = [url.strip() for url in urls if url.strip() and url.strip().startswith('http')]
        print(f"✓ Found {len(urls)} URLs to scrape\n")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    except Exception as e:
        print(f"Error loading URLs: {e}")
        return
    
    results = []
    
    with sync_playwright() as p:
        print("\n🚀 Launching browser...")
        browser = p.chromium.launch(headless=False)
        
        # Try to use saved session
        auth_file = "instagram_auth.json"
        if Path(auth_file).exists():
            print(f"✓ Using saved session from {auth_file}")
            context = browser.new_context(storage_state=auth_file)
        else:
            context = browser.new_context()
        
        page = context.new_page()
        page.goto("https://www.instagram.com/")
        
        print("\n" + "="*60)
        print("INSTRUCTIONS:")
        print("="*60)
        print("1. Log in to Instagram if needed")
        print("2. Navigate to each URL from the list above")
        print("3. Wait for the page to fully load")
        print("4. Press ENTER in this terminal to extract data")
        print("5. Repeat for all URLs")
        print("6. Type 'done' when finished")
        print("="*60 + "\n")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Next URL: {url}")
            print("👉 Navigate to this URL in the browser, then press ENTER...")
            
            user_input = input()
            if user_input.lower() == 'done':
                break
            
            # Wait a moment for page to settle
            time.sleep(2)
            
            # Extract data
            print("🔍 Extracting data...")
            data = extract_data_from_page(page)
            
            if data:
                result = {
                    'url': data['url'],
                    'likes': extract_number(data['likes']) if data['likes'] else 0,
                    'comments': extract_number(data['comments']) if data['comments'] else 0,
                    'views': extract_number(data['views']) if data['views'] else 0,
                    'collaborators': data['collaborator'] if data['collaborator'] else '',
                    'status': 'Success' if (data['likes'] or data['comments'] or data['views']) else 'No Data'
                }
                
                print(f"✓ Likes: {result['likes']:,}")
                print(f"✓ Comments: {result['comments']:,}")
                print(f"✓ Views: {result['views']:,}")
                if result['collaborators']:
                    print(f"✓ Collaborators: {result['collaborators']}")
                
                results.append(result)
            else:
                print("⚠ Could not extract data")
                results.append({
                    'url': url,
                    'likes': 0,
                    'comments': 0,
                    'views': 0,
                    'collaborators': '',
                    'status': 'Error'
                })
        
        browser.close()
    
    # Save results
    if results:
        df = pd.DataFrame(results)
        df.to_excel('output/instagram_data.xlsx', index=False, engine='openpyxl')
        print(f"\n✓ Results saved to: output/instagram_data.xlsx")
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total URLs processed: {len(results)}")
        print(f"Total Likes: {sum(r['likes'] for r in results):,}")
        print(f"Total Comments: {sum(r['comments'] for r in results):,}")
        print(f"Total Views: {sum(r['views'] for r in results):,}")
        print("="*60)


if __name__ == "__main__":
    main()
