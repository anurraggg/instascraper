from bs4 import BeautifulSoup
import re

def extract_username(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    username = ''
    
    print("--- Extraction Debug ---")
    
    # 1. Title
    title = soup.title.string if soup.title else ''
    print(f"Title: {title}")
    
    if '(@' in title and ')' in title:
        username = title.split('(@')[1].split(')')[0]
        print(f"  Matches (@): {username}")
    elif 'on Instagram' in title:
        username = title.split('on Instagram')[0].strip().replace('"', '').split(' ')[0]
        print(f"  Matches 'on Instagram': {username}")
    
    # Fallback: Meta Title
    if not username:
        try:
            meta_title = soup.find('meta', property='og:title')['content']
            print(f"Meta Title: {meta_title}")
            if '(@' in meta_title:
                username = meta_title.split('(@')[1].split(')')[0]
                print(f"  Matches (@): {username}")
        except: pass
    
    # Fallback: OG URL (Very Reliable)
    if not username:
        try:
            og_url = soup.find('meta', property='og:url')['content']
            print(f"OG URL: {og_url}")
            # https://www.instagram.com/username/reel/ID/
            if 'instagram.com/' in og_url:
                parts = og_url.split('instagram.com/')[1].split('/')
                if parts[0] in ['p', 'reel', 'tv']:
                    print("  Skipped (format /p/ or /reel/)")
                else:
                    username = parts[0]
                    print(f"  Matches OG URL: {username}")
        except: pass

    # Fallback: Meta Description
    if not username:
        try:
            meta_desc = soup.find('meta', attrs={'name':'description'})['content']
            print(f"Meta Desc: {meta_desc}")
            # "224 likes, 5 comments - username on..."
            match = re.search(r'-\s+([^\s]+)\s+on', meta_desc)
            if match:
                username = match.group(1)
                print(f"  Matches Meta Desc: {username}")
        except: pass
        
    return username

if __name__ == "__main__":
    with open('debug_missing.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    result = extract_username(html)
    print(f"\nFinal Result: '{result}'")
